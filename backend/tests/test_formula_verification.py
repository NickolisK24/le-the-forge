"""
Formula Verification Tests — verified Last Epoch game mechanics.

Each test uses known inputs and expected outputs derived from the verified
game formulas. These tests serve as the authoritative specification for
how every damage and defensive formula must behave.

Sections:
  1. Armor mitigation (area-level-based, 85% cap, non-physical effectiveness)
  2. Dodge chance (area-level-based, 85% cap)
  3. Critical strikes (multiplicative increased, 100% cap, 1.5x base multiplier)
  4. Ward decay (retention-based divisor formula)
  5. Ailment system (flat base DPS, multi-stack, boss reduction)
  6. Damage pipeline (increased additive, more multiplicative, added effectiveness)
  7. DPS benchmark (Rogue Bladedancer Umbral Blades scenario)
"""

import math
import pytest

from app.domain.armor import armor_mitigation_pct, apply_armor, ARMOR_K
from app.domain.dodge import dodge_chance, DODGE_CAP
from app.domain.critical import (
    effective_crit_chance,
    effective_crit_multiplier,
    apply_crit,
    BASE_CRIT_MULTIPLIER,
    CRIT_CAP,
)
from app.domain.ward import ward_decay_per_second, effective_ward_retention
from app.domain.calculators.ailment_calculator import (
    ailment_stack_count,
    ailment_stacks_per_hit,
    calc_ailment_dps,
)
from app.domain.calculators.crit_calculator import (
    effective_crit_chance as calc_crit_chance,
    calculate_average_hit,
)
from app.domain.calculators.enemy_mitigation_calculator import (
    armor_mitigation,
    apply_penetration,
    effective_resistance,
    weighted_damage_multiplier,
)
from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyProfile
from app.constants.combat import (
    BLEED_BASE_DPS,
    IGNITE_BASE_DPS,
    POISON_BASE_DPS,
    BOSS_AILMENT_REDUCTION,
)
from app.constants.defense import (
    ARMOR_MITIGATION_CAP,
    ARMOR_NON_PHYSICAL_EFFECTIVENESS,
    DEFAULT_AREA_LEVEL,
    WARD_BASE_DECAY_RATE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _enemy(**overrides) -> EnemyProfile:
    defaults = dict(
        id="test", name="Test", category="normal", data_version="test",
        health=1000, armor=0, resistances={},
    )
    defaults.update(overrides)
    return EnemyProfile(**defaults)


# ===========================================================================
# 1. Armor Mitigation
# ===========================================================================

class TestArmorFormula:
    """Armor / (Armor + 10 x AreaLevel), cap 85% physical, 75% eff non-phys."""

    def test_canonical_benchmark(self):
        """1000 armor at area level 100 = 50% DR."""
        assert armor_mitigation_pct(1000.0, 100) == pytest.approx(0.5)

    def test_500_armor_area_50(self):
        """500 / (500 + 500) = 50%."""
        assert armor_mitigation_pct(500.0, 50) == pytest.approx(0.5)

    def test_2000_armor_area_100(self):
        """2000 / (2000 + 1000) = 66.67%."""
        assert armor_mitigation_pct(2000.0, 100) == pytest.approx(2000 / 3000)

    def test_physical_cap_85pct(self):
        assert armor_mitigation_pct(1_000_000.0, 100) == pytest.approx(0.85)

    def test_non_physical_70pct_effectiveness(self):
        """VERIFIED: 1.4.3 spec §3.1 — armour 70% effective vs non-physical.
        effective_armor = 1000*0.70 = 700, mit = 700/1700."""
        result = armor_mitigation_pct(1000.0, 100, physical=False)
        assert result == pytest.approx(700.0 / 1700.0)

    def test_non_physical_cap(self):
        """Non-physical cap = 85% * 70% = 59.5%."""
        result = armor_mitigation_pct(1_000_000.0, 100, physical=False)
        assert result == pytest.approx(0.85 * 0.70)

    def test_apply_armor_damage_reduction(self):
        """100 damage, 1000 armor, area 100 → 50% mit → 50 passes through."""
        assert apply_armor(100.0, 1000.0, 100) == pytest.approx(50.0)

    def test_apply_armor_extreme_cap(self):
        """Extreme armor → min 15% damage passes through."""
        assert apply_armor(100.0, 1_000_000.0, 100) == pytest.approx(15.0)

    def test_zero_armor_no_reduction(self):
        assert armor_mitigation_pct(0.0, 100) == pytest.approx(0.0)

    def test_higher_area_level_reduces_mitigation(self):
        low = armor_mitigation_pct(500.0, 50)
        high = armor_mitigation_pct(500.0, 200)
        assert low > high

    def test_enemy_armor_mitigation_same_formula(self):
        """Enemy mitigation calculator uses same formula."""
        assert armor_mitigation(1000, 100) == pytest.approx(0.5)
        assert armor_mitigation(10_000_000, 100) == pytest.approx(0.85)


# ===========================================================================
# 2. Dodge Chance
# ===========================================================================

class TestDodgeFormula:
    """DodgeRating / (DodgeRating + 10 x AreaLevel), cap 85%."""

    def test_canonical(self):
        """1000 rating, area 100 → 1000/2000 = 50%."""
        assert dodge_chance(1000.0, area_level=100) == pytest.approx(0.5)

    def test_cap_85pct(self):
        assert dodge_chance(1_000_000.0) == pytest.approx(DODGE_CAP)
        assert DODGE_CAP == pytest.approx(0.85)

    def test_zero_rating(self):
        assert dodge_chance(0.0) == pytest.approx(0.0)

    def test_higher_area_reduces_dodge(self):
        base = dodge_chance(500.0, area_level=50)
        harder = dodge_chance(500.0, area_level=200)
        assert harder < base

    def test_exact_formula(self):
        """500 / (500 + 10*100) = 500/1500 = 1/3."""
        assert dodge_chance(500.0, area_level=100) == pytest.approx(1 / 3)


# ===========================================================================
# 3. Critical Strikes
# ===========================================================================

class TestCritFormula:
    """Crit% = base x (1 + increased_pct/100), cap 100%. Base mult 2.0x (1.4.3)."""

    def test_base_crit_multiplier_200pct(self):
        # VERIFIED: 1.4.3 spec §2.2 — base crit multiplier is 200% (2.0×)
        assert BASE_CRIT_MULTIPLIER == pytest.approx(2.0)

    def test_crit_cap_100pct(self):
        assert CRIT_CAP == pytest.approx(1.0)

    def test_multiplicative_formula(self):
        """5% base, 100% increased → 5% x 2.0 = 10%."""
        assert effective_crit_chance(0.05, 100.0) == pytest.approx(0.10)

    def test_200pct_increased_triples(self):
        """5% base, 200% increased → 5% x 3.0 = 15%."""
        assert effective_crit_chance(0.05, 200.0) == pytest.approx(0.15)

    def test_crit_chance_capped_at_100(self):
        assert effective_crit_chance(0.5, 200.0) == pytest.approx(1.0)

    def test_effective_multiplier_with_bonus(self):
        """1.5 base + 50%/100 = 2.0 total multiplier."""
        assert effective_crit_multiplier(1.5, 50.0) == pytest.approx(2.0)

    def test_apply_crit_doubles_at_2x(self):
        assert apply_crit(100.0, is_crit=True, crit_multiplier=2.0) == pytest.approx(200.0)

    def test_apply_crit_no_crit_returns_raw(self):
        assert apply_crit(100.0, is_crit=False, crit_multiplier=2.0) == pytest.approx(100.0)

    def test_average_hit_formula(self):
        """average = hit x (1 + crit_chance x (crit_mult - 1))."""
        avg = calculate_average_hit(100.0, 0.5, 2.0)
        assert avg == pytest.approx(150.0)

    def test_calculator_crit_chance_matches_domain(self):
        """Calculator module uses same multiplicative formula."""
        assert calc_crit_chance(0.05, 100.0) == pytest.approx(0.10)


# ===========================================================================
# 4. Ward Decay
# ===========================================================================

class TestWardDecayFormula:
    """Ward_Lost/sec = 0.4 x (Ward - Threshold) / (1 + 0.5 x Retention/100)."""

    def test_base_decay_rate_04(self):
        assert WARD_BASE_DECAY_RATE == pytest.approx(0.4)

    def test_no_retention(self):
        """400 ward, 0 retention → 0.4 * 400 / 1.0 = 160."""
        assert ward_decay_per_second(400.0) == pytest.approx(160.0)

    def test_100pct_retention(self):
        """400 ward, 100% retention → 0.4 * 400 / 1.5 ≈ 106.67."""
        result = ward_decay_per_second(400.0, ward_retention=100.0)
        assert result == pytest.approx(160.0 / 1.5)

    def test_200pct_retention(self):
        """400 ward, 200% retention → 0.4 * 400 / 2.0 = 80."""
        result = ward_decay_per_second(400.0, ward_retention=200.0)
        assert result == pytest.approx(80.0)

    def test_threshold_reduces_decaying_ward(self):
        """1000 ward, threshold 500 → decay on 500 only."""
        result = ward_decay_per_second(1000.0, threshold=500.0)
        assert result == pytest.approx(0.4 * 500.0)

    def test_ward_at_threshold_no_decay(self):
        assert ward_decay_per_second(100.0, threshold=100.0) == pytest.approx(0.0)

    def test_intelligence_ward_retention(self):
        """10 intelligence → 10 * 4 = 40% extra retention."""
        assert effective_ward_retention(0.0, intelligence=10.0) == pytest.approx(40.0)


# ===========================================================================
# 5. Ailment System
# ===========================================================================

class TestAilmentFormula:
    """Flat base DPS per stack; >100% chance grants extra stacks; boss -60%."""

    def test_flat_base_dps_constants(self):
        assert BLEED_BASE_DPS == pytest.approx(43.0)
        assert IGNITE_BASE_DPS == pytest.approx(40.0)
        assert POISON_BASE_DPS == pytest.approx(28.0)

    def test_boss_reduction_60pct(self):
        assert BOSS_AILMENT_REDUCTION == pytest.approx(0.60)

    def test_stacks_per_hit_100pct(self):
        """100% chance = exactly 1 stack per hit."""
        assert ailment_stacks_per_hit(100.0) == pytest.approx(1.0)

    def test_stacks_per_hit_235pct(self):
        """235% chance = 2 guaranteed + 35% for 3rd = 2.35 stacks."""
        assert ailment_stacks_per_hit(235.0) == pytest.approx(2.35)

    def test_stacks_per_hit_50pct(self):
        """50% chance = 0.5 stacks per hit."""
        assert ailment_stacks_per_hit(50.0) == pytest.approx(0.5)

    def test_stacks_per_hit_0pct(self):
        """0% chance = no stacks."""
        assert ailment_stacks_per_hit(0.0) == pytest.approx(0.0)

    def test_stack_count_formula(self):
        """stacks = effective_as x stacks_per_hit x duration."""
        # 2.0 as, 100% chance (1 stack/hit), 4s duration → 8 stacks
        count = ailment_stack_count(2.0, 100.0, 4.0)
        assert count == pytest.approx(8.0)

    def test_stack_count_partial_chance(self):
        """2.0 as, 50% chance (0.5 stack/hit), 4s → 4 stacks."""
        count = ailment_stack_count(2.0, 50.0, 4.0)
        assert count == pytest.approx(4.0)


# ===========================================================================
# 6. Damage Pipeline
# ===========================================================================

class TestDamagePipeline:
    """(Base + Added*Eff) x (1 + sum_increased) x prod(1+more_i)."""

    def test_increased_is_additive(self):
        """Two 50% increased sources = 100% total = 2.0x."""
        ctx = DamageContext(base_damage=100.0, increased_damage=100.0)
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(200.0)

    def test_more_is_multiplicative(self):
        """Two 50% more sources = 1.5 x 1.5 = 2.25x."""
        ctx = DamageContext(base_damage=100.0, increased_damage=0.0, more_damage=[50.0, 50.0])
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(225.0)

    def test_increased_and_more_combined(self):
        """100 base, 100% increased, 50% more → 100 x 2.0 x 1.5 = 300."""
        ctx = DamageContext(base_damage=100.0, increased_damage=100.0, more_damage=[50.0])
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(300.0)

    def test_penetration_after_cap(self):
        """90% raw res → capped to 75% → 20% pen → 55% effective."""
        enemy = _enemy(resistances={"fire": 90.0})
        eff = effective_resistance(enemy, "fire", penetration=20.0)
        assert eff == pytest.approx(55.0)

    def test_penetration_cannot_go_negative(self):
        assert apply_penetration(20.0, 50.0) == pytest.approx(0.0)

    def test_weighted_multiplier_physical(self):
        """1000 armor, physical only → 50% mitigation → 0.5 multiplier."""
        enemy = _enemy(armor=1000)
        damage_by_type = {DamageType.PHYSICAL: 100.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type)
        assert mult == pytest.approx(0.5)


# ===========================================================================
# 7. DPS Benchmark — Rogue Bladedancer Umbral Blades
# ===========================================================================

class TestDPSBenchmark:
    """
    Rogue Bladedancer scenario:
      - Umbral Blades, 5 hits/cast, base 80
      - 200% added damage effectiveness
      - 150% increased physical, 50% more (one source)
      - 45% crit chance, 250% crit multiplier
      - 1.33 attacks/sec, no enemy armor/resistance
      - Verify engine result within 10% of manual calculation

    Uses the hardcoded SKILL_STATS directly to avoid registry interference
    from Flask app contexts created by other tests.
    """

    def _run_benchmark(self):
        """Run the benchmark using hardcoded skill data directly."""
        from app.engines.stat_engine import BuildStats
        from app.engines.combat_engine import calculate_dps, SKILL_STATS
        from app.domain.skill_modifiers import SkillModifiers
        from app.domain.calculators.skill_calculator import scale_skill_damage, sum_flat_damage
        from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
        from app.domain.calculators.increased_damage_calculator import sum_increased_damage
        from app.domain.calculators.speed_calculator import effective_attack_speed

        stats = BuildStats()
        stats.crit_chance = 0.45
        stats.crit_multiplier = 2.5
        stats.physical_damage_pct = 150.0
        stats.more_damage_pct = 50.0

        sm = SkillModifiers(added_hits_per_cast=4)  # 1 + 4 = 5 hits/cast
        skill_def = SKILL_STATS["Umbral Blades"]

        # Reproduce the engine pipeline manually with the hardcoded skill
        flat_added = sum_flat_damage(stats, skill_def) * skill_def.added_damage_effectiveness
        scaled = scale_skill_damage(skill_def.base_damage, skill_def.level_scaling, 20, skill_def.damage_types)
        scaled_total = sum(scaled.values())
        effective_base = scaled_total + flat_added

        damage = calculate_final_damage(DamageContext.from_build(effective_base, stats, skill_def, sm.more_damage_pct, scaled=scaled))
        hit_damage = damage.total

        eff_crit_chance = calc_crit_chance(stats.crit_chance, sm.crit_chance_pct)
        eff_crit_mult = effective_crit_multiplier(stats.crit_multiplier, sm.crit_multiplier_pct)
        average_hit = calculate_average_hit(hit_damage, eff_crit_chance, eff_crit_mult)

        eff_as = effective_attack_speed(skill_def, stats, sm)
        hpc = 5  # 1 + 4 added

        dps = average_hit * eff_as * hpc

        return hit_damage, average_hit, round(dps), eff_as, scaled_total

    def test_rogue_bladedancer_dps_within_10pct(self):
        hit_damage, average_hit, dps, eff_as, scaled_total = self._run_benchmark()

        # Manual calculation from verified game formula:
        # Scaled base: 80 * (1 + 0.08 * 19) = 201.6
        # Hit damage: 201.6 * (1 + 150/100) * (1 + 50/100) = 756.0
        # Average hit: 756.0 * (1 + 0.45 * (2.5 - 1)) = 1266.3
        # DPS: 1266.3 * 1.33 * 5 = 8420.9
        manual_scaled = 80 * (1 + 0.08 * 19)
        manual_hit = manual_scaled * 2.5 * 1.5
        manual_avg = manual_hit * (1 + 0.45 * 1.5)
        manual_dps = manual_avg * 1.33 * 5

        assert manual_dps == pytest.approx(8420.9, rel=0.01)

        # Engine result must be within 10% of manual
        assert dps == pytest.approx(manual_dps, rel=0.10), (
            f"Engine DPS {dps} not within 10% of manual {manual_dps:.1f}"
        )

    def test_benchmark_hit_damage(self):
        """Verify hit damage component: base * increased * more."""
        hit_damage, _, _, _, _ = self._run_benchmark()
        assert hit_damage == pytest.approx(756, abs=1)

    def test_benchmark_average_hit(self):
        """Verify average hit including crit: hit * (1 + 0.45 * 1.5)."""
        _, average_hit, _, _, _ = self._run_benchmark()
        assert average_hit == pytest.approx(1266.3, abs=2)

    def test_benchmark_attack_speed(self):
        """Verify effective attack speed matches skill data."""
        _, _, _, eff_as, _ = self._run_benchmark()
        assert eff_as == pytest.approx(1.33, abs=0.01)
