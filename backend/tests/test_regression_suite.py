"""
Full regression validation suite.

Three layers:
  Deterministic — exact formula verification with synthetic inputs; no
                  running the full engine, just calculator primitives.
  Snapshot      — pinned output values from the live engine. Any change
                  here means a formula, data, or pipeline change occurred.
                  Update pinned values deliberately and document the reason.
  Edge          — boundary conditions: zero, extreme, and degenerate inputs
                  that must never crash or produce nonsense.

Run with:
    pytest tests/test_regression_suite.py -v
"""

import math
import pytest

from app.engines.stat_engine import aggregate_stats, BuildStats
from app.engines.combat_engine import (
    calculate_dps,
    monte_carlo_dps,
    calculate_dps_vs_enemy,
)
from app.domain.calculators.conversion_calculator import DamageConversion, apply_conversions
from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.enemy_mitigation_calculator import (
    armor_mitigation,
    effective_resistance,
    weighted_damage_multiplier,
    RES_CAP,
)
from app.domain.calculators.crit_calculator import effective_crit_chance
from app.domain.enemy import EnemyProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mage() -> BuildStats:
    return aggregate_stats("Mage", "Sorcerer", [], [], [])


def _paladin() -> BuildStats:
    return aggregate_stats("Sentinel", "Paladin", [], [], [])


def _enemy(**overrides) -> EnemyProfile:
    defaults = dict(
        id="test", name="Test", category="normal", data_version="test",
        health=1000, armor=0, resistances={},
    )
    defaults.update(overrides)
    return EnemyProfile(**defaults)


# ---------------------------------------------------------------------------
# Layer 1 — Deterministic formula verification
# ---------------------------------------------------------------------------

class TestDeterministic:
    """Exact math on calculator primitives — no engine, no data files."""

    def test_armor_formula_zero(self):
        assert armor_mitigation(0) == 0.0

    def test_armor_formula_1000(self):
        # 1000 / (1000 + 1000) = 0.5
        assert math.isclose(armor_mitigation(1000), 0.5, rel_tol=1e-9)

    def test_armor_formula_500(self):
        # 500 / 1500 = 1/3
        assert math.isclose(armor_mitigation(500), 1 / 3, rel_tol=1e-9)

    def test_armor_never_reaches_one(self):
        assert armor_mitigation(10_000_000) < 1.0

    def test_resistance_capped_at_res_cap(self):
        enemy = _enemy(resistances={"fire": 90.0})
        assert effective_resistance(enemy, "fire") == RES_CAP

    def test_resistance_pen_applied_after_cap(self):
        # 90% raw → capped at 75 → minus 20 pen = 55
        enemy = _enemy(resistances={"fire": 90.0})
        assert math.isclose(effective_resistance(enemy, "fire", 20.0), 55.0, rel_tol=1e-9)

    def test_missing_resistance_defaults_zero(self):
        enemy = _enemy()
        assert effective_resistance(enemy, "fire") == 0.0

    def test_conversion_60pct_splits_correctly(self):
        base = {DamageType.PHYSICAL: 100.0}
        result = apply_conversions(base, [DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 60.0)])
        assert math.isclose(result[DamageType.PHYSICAL], 40.0, rel_tol=1e-9)
        assert math.isclose(result[DamageType.FIRE],     60.0, rel_tol=1e-9)

    def test_conversion_100pct_removes_source(self):
        base = {DamageType.PHYSICAL: 100.0}
        result = apply_conversions(base, [DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0)])
        assert DamageType.PHYSICAL not in result
        assert math.isclose(result[DamageType.FIRE], 100.0, rel_tol=1e-9)

    def test_crit_chance_capped_at_100pct(self):
        assert math.isclose(effective_crit_chance(1.0, 0), 1.0, rel_tol=1e-9)
        assert math.isclose(effective_crit_chance(2.0, 0), 1.0, rel_tol=1e-9)

    def test_weighted_multiplier_formula(self):
        # armor=500 → factor = 1000/1500 = 2/3
        # fire 75% res (capped), weight 0.8 → contribution 0.8 * 0.25 = 0.20
        # phys 30% res,          weight 0.2 → contribution 0.2 * 0.70 = 0.14
        # res_factor = 0.34,  total = (2/3) * 0.34 ≈ 0.22667
        enemy = _enemy(armor=500, resistances={"fire": 75.0, "physical": 30.0})
        mult = weighted_damage_multiplier(
            enemy,
            {DamageType.FIRE: 80.0, DamageType.PHYSICAL: 20.0},
        )
        assert math.isclose(mult, 2 / 3 * 0.34, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# Layer 2 — Snapshot tests (pinned live-engine output)
# ---------------------------------------------------------------------------

class TestDPSSnapshots:
    """
    Pinned calculate_dps outputs for the default Mage and Paladin builds.

    If any of these values change, a formula, data, or pipeline change occurred.
    Verify the change is intentional before updating the expected values.
    """

    def test_fireball_l20_dps(self):
        # updated: verified in-game data — Intelligence no longer grants
        # +0.5% spell_damage_pct per point (removed from ATTRIBUTE_SCALING).
        assert calculate_dps(_mage(), "Fireball", 20).dps == 549

    def test_fireball_l20_hit_damage(self):
        # updated: verified in-game data — see note above.
        assert calculate_dps(_mage(), "Fireball", 20).hit_damage == 415

    def test_fireball_l20_average_hit(self):
        # updated: verified in-game data — see note above.
        assert calculate_dps(_mage(), "Fireball", 20).average_hit == 436

    def test_fireball_l20_total_dps_equals_dps_no_ailments(self):
        r = calculate_dps(_mage(), "Fireball", 20)
        assert r.total_dps == r.dps  # no ailment chance on base build

    def test_fireball_damage_type_is_fire(self):
        r = calculate_dps(_mage(), "Fireball", 20)
        assert set(r.damage_by_type.keys()) == {"fire"}

    def test_rive_l20_dps(self):
        # updated: verified in-game data — Strength no longer grants direct
        # physical_damage_pct (removed from ATTRIBUTE_SCALING).
        assert calculate_dps(_paladin(), "Rive", 20).dps == 620

    def test_rive_l20_ailment_snapshot(self):
        stats = _paladin()
        stats.bleed_chance_pct  = 100
        stats.ignite_chance_pct = 100
        r = calculate_dps(stats, "Rive", 20)
        # updated: verified in-game data — ailment DPS derives from hit
        # damage, which is now lower without strength's phys-damage scaling.
        assert r.bleed_dps   == 310
        assert r.ignite_dps  == 216
        assert r.total_dps   == 1146

    def test_level_scaling_monotone(self):
        stats = _mage()
        # updated: verified in-game data — Intelligence no longer adds
        # spell_damage_pct, so DPS-at-L1 and DPS-at-L20 both drop, but
        # monotonicity is preserved.
        assert calculate_dps(stats, "Fireball",  1).dps == 167
        assert calculate_dps(stats, "Fireball", 20).dps == 549

    def test_conversion_flows_through_pipeline(self):
        # 100% phys → fire: damage_by_type must show fire, not physical
        convs = [DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0)]
        r = calculate_dps(_paladin(), "Rive", 20, conversions=convs)
        assert "fire" in r.damage_by_type
        assert "physical" not in r.damage_by_type
        # Pipeline now derives the increased-damage pool from the
        # post-conversion types (fire + elemental + melee), so the
        # Paladin's physical_damage_pct no longer scales the converted
        # fire hit. 328.0 is the correct value under that routing.
        assert math.isclose(r.damage_by_type["fire"], 328.0, rel_tol=1e-6)

        # Invariant: pumping physical_damage_pct must NOT increase the
        # converted fire damage. If it did, physical scaling would still
        # be leaking into the post-conversion fire pool — exactly the
        # bug the post_conversion_types fix removes.
        boosted = _paladin()
        boosted.physical_damage_pct += 100
        r_boosted = calculate_dps(boosted, "Rive", 20, conversions=convs)
        assert r_boosted.damage_by_type["fire"] == r.damage_by_type["fire"]

    def test_training_dummy_passes_through_unmodified(self):
        r = calculate_dps_vs_enemy(_mage(), "Fireball", 20, "training_dummy")
        assert r.raw_dps == r.effective_dps
        assert r.armor_reduction_pct  == 0.0
        assert r.avg_res_reduction_pct == 0.0


class TestMonteCarloSnapshots:
    """
    Pinned seeded simulation outputs. Identical seed + n must always
    produce identical results — any change breaks reproducibility.
    """

    def test_fireball_seed1_n1000_mean(self):
        stats = BuildStats()
        stats.base_damage      = 120.0
        stats.crit_chance      = 0.25
        stats.crit_multiplier  = 2.0
        stats.spell_damage_pct = 80.0
        stats.fire_damage_pct  = 60.0
        stats.cast_speed       = 20.0
        mc = monte_carlo_dps(stats, "Fireball", 20, n=1_000, seed=1)
        # VERIFIED: 1.4.3 spec §2.1 + §2.2 — ±25% hit variance + 2.0× crit multi
        assert mc.mean_dps       == 1522
        assert mc.min_dps        == 936
        assert mc.max_dps        == 3110
        assert mc.std_dev        == 565.3
        assert mc.percentile_25  == 1132
        assert mc.percentile_75  == 1543
        assert mc.n_simulations  == 1_000

    def test_same_seed_always_identical(self):
        stats = _mage()
        r1 = monte_carlo_dps(stats, "Fireball", 20, n=500, seed=42)
        r2 = monte_carlo_dps(stats, "Fireball", 20, n=500, seed=42)
        assert r1.mean_dps == r2.mean_dps
        assert r1.std_dev  == r2.std_dev

    def test_different_seeds_differ(self):
        stats = _mage()
        r1 = monte_carlo_dps(stats, "Fireball", 20, n=1_000, seed=1)
        r2 = monte_carlo_dps(stats, "Fireball", 20, n=1_000, seed=9999)
        assert r1.mean_dps != r2.mean_dps or r1.std_dev != r2.std_dev


# ---------------------------------------------------------------------------
# Layer 3 — Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Boundary conditions that must never crash or produce nonsense."""

    # --- zero / identity inputs ---

    def test_zero_crit_chance_hit_variance_only(self):
        # VERIFIED: 1.4.3 spec §2.1 — hits always have ±25% variance; with 0%
        # crit chance, the only variance source is the ±25% uniform hit roll.
        stats = _mage()
        stats.crit_chance = 0.0
        mc = monte_carlo_dps(stats, "Fireball", 20, n=500, seed=7)
        # All samples bracket within the ±25% hit variance band.
        assert 0.70 * mc.mean_dps <= mc.min_dps <= mc.mean_dps
        assert mc.mean_dps <= mc.max_dps <= 1.30 * mc.mean_dps

    def test_unknown_skill_zeros_all_fields(self):
        r = calculate_dps(_mage(), "NoSuchSkill_XYZ", 20)
        assert r.dps == r.hit_damage == r.average_hit == r.total_dps == 0

    def test_unknown_skill_mc_zeros(self):
        mc = monte_carlo_dps(_mage(), "NoSuchSkill_XYZ", 20, n=100, seed=0)
        assert mc.mean_dps == mc.min_dps == mc.max_dps == 0

    # --- n boundary ---

    def test_n_equals_1(self):
        mc = monte_carlo_dps(_mage(), "Fireball", 20, n=1, seed=0)
        assert mc.n_simulations == 1
        assert mc.min_dps == mc.max_dps == mc.mean_dps

    def test_workers_greater_than_n(self):
        # 3 samples across 10 workers: 7 workers get 0 samples, 3 get 1 each
        mc = monte_carlo_dps(_mage(), "Fireball", 20, n=3, seed=0, workers=10)
        assert mc.n_simulations == 3

    def test_prime_n_preserved(self):
        mc = monte_carlo_dps(_mage(), "Fireball", 20, n=997, seed=3, workers=4)
        assert mc.n_simulations == 997

    # --- workers validation ---

    def test_workers_zero_raises(self):
        with pytest.raises(ValueError):
            monte_carlo_dps(_mage(), "Fireball", 20, n=10, workers=0)

    def test_workers_negative_raises(self):
        with pytest.raises(ValueError):
            monte_carlo_dps(_mage(), "Fireball", 20, n=10, workers=-5)

    # --- resistance / armor extremes ---

    def test_full_resistance_cap_limits_effective_res(self):
        enemy = _enemy(resistances={"fire": 200.0})
        assert effective_resistance(enemy, "fire") == RES_CAP

    def test_negative_resistance_is_floored_to_zero(self):
        # apply_penetration floors at 0: min(-50, 75)=-50 → max(0, -50)=0.
        # Negative raw resistance does not create a vulnerability — it is
        # treated as zero effective resistance (no bonus damage to the enemy).
        enemy = _enemy(resistances={"fire": -50.0})
        assert effective_resistance(enemy, "fire") == 0.0

    def test_extreme_armor_mitigation_capped_at_85pct(self):
        assert armor_mitigation(10_000_000) == pytest.approx(0.85)
        assert armor_mitigation(10_000_000) < 1.0

    # --- conversion extremes ---

    def test_no_conversions_preserves_base(self):
        base = {DamageType.PHYSICAL: 100.0}
        result = apply_conversions(base, [])
        assert math.isclose(result[DamageType.PHYSICAL], 100.0, rel_tol=1e-9)

    def test_overcapped_conversion_clamped_to_100pct(self):
        # Two 80% phys→fire conversions: total 160%, clamped to 100% of source
        base = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE,  80.0),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD,  80.0),
        ]
        result = apply_conversions(base, convs)
        total = sum(result.values())
        assert math.isclose(total, 100.0, rel_tol=1e-9)
        assert DamageType.PHYSICAL not in result


# ---------------------------------------------------------------------------
# Layer 4 — System integration
# ---------------------------------------------------------------------------

class TestSystemIntegration:
    """Cross-module pipeline tests: multiple calculators working together."""

    def test_mc_mean_close_to_analytical_dps(self):
        # Monte Carlo mean must converge to the analytical DPS within 10%.
        stats = _mage()
        analytical = calculate_dps(stats, "Fireball", 20).dps
        mc = monte_carlo_dps(stats, "Fireball", 20, n=5_000)
        assert abs(mc.mean_dps - analytical) / analytical < 0.10

    def test_parallel_mean_close_to_serial(self):
        stats = _mage()
        serial   = monte_carlo_dps(stats, "Fireball", 20, n=10_000, seed=42, workers=1)
        parallel = monte_carlo_dps(stats, "Fireball", 20, n=10_000, seed=42, workers=4)
        rel = abs(serial.mean_dps - parallel.mean_dps) / serial.mean_dps
        assert rel < 0.02, (
            f"Relative drift too large: "
            f"serial={serial.mean_dps:.3f}, "
            f"parallel={parallel.mean_dps:.3f}, "
            f"rel={rel:.4%}"
        )

    def test_higher_resistance_lowers_effective_dps(self):
        low_res  = _enemy(resistances={"fire": 20.0})
        high_res = _enemy(resistances={"fire": 60.0})
        dmg = {DamageType.FIRE: 100.0}
        assert weighted_damage_multiplier(high_res, dmg) < weighted_damage_multiplier(low_res, dmg)

    def test_penetration_increases_effective_multiplier(self):
        enemy = _enemy(resistances={"fire": 60.0})
        dmg   = {DamageType.FIRE: 100.0}
        without_pen = weighted_damage_multiplier(enemy, dmg)
        with_pen    = weighted_damage_multiplier(enemy, dmg, pen_map={"fire": 20.0})
        assert with_pen > without_pen

    def test_conversion_changes_damage_type_against_resistant_enemy(self):
        # Rive is physical. Convert to fire; enemy resists fire more than phys.
        # Effective DPS should drop when fire-resistant.
        # conversion preserves base damage quantity but reroutes the
        # increased pool — hit damage only matches unconverted when
        # source and target scaling are equal.
        convs = [DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0)]

        # Case 1: source scaling present, no target scaling. Strength no
        # longer adds physical_damage_pct directly — so we give the build
        # an explicit physical_damage_pct pool to create the asymmetric
        # scaling needed for the test.
        # updated: verified in-game data — previously leaned on Strength's
        # implicit 0.5%/pt physical scaling which has been removed.
        stats = _paladin()
        stats.physical_damage_pct = 50.0  # explicit source pool
        assert stats.physical_damage_pct > 0
        assert stats.fire_damage_pct == 0
        r_plain = calculate_dps(stats, "Rive", 20)
        r_conv = calculate_dps(stats, "Rive", 20, conversions=convs)
        assert r_conv.hit_damage < r_plain.hit_damage

        # Case 2: equal source and target scaling. With symmetric pools
        # the rerouted increased% matches the original, so base damage
        # quantity (which conversion preserves) carries through and
        # hit damage is ~unchanged. Allow 1 integer of rounding slack.
        sym = _paladin()
        sym.fire_damage_pct = sym.physical_damage_pct
        r_sym_plain = calculate_dps(sym, "Rive", 20)
        r_sym_conv = calculate_dps(sym, "Rive", 20, conversions=convs)
        assert abs(r_sym_conv.hit_damage - r_sym_plain.hit_damage) <= 1

    def test_ailment_dps_adds_to_total(self):
        stats = _mage()
        stats.ignite_chance_pct = 100
        r = calculate_dps(stats, "Fireball", 20)
        assert r.total_dps == r.dps + r.ailment_dps
        assert r.ailment_dps > 0
