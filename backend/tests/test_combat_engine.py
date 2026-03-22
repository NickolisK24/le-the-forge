"""Tests for the combat / DPS engine."""

import pytest
from app.engines.stat_engine import aggregate_stats, BuildStats
from app.engines.combat_engine import (
    calculate_dps,
    monte_carlo_dps,
    DPSResult,
    MonteCarloDPS,
    SKILL_STATS,
)


def _base_mage_stats() -> BuildStats:
    return aggregate_stats("Mage", "Sorcerer", [], [], [])


class TestCalculateDPS:
    def test_returns_dps_result(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Fireball")
        assert isinstance(result, DPSResult)

    def test_unknown_skill_returns_zeros(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Nonexistent Skill XYZ")
        assert result.dps == 0
        assert result.hit_damage == 0
        assert result.average_hit == 0

    def test_dps_is_positive_for_known_skill(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Fireball", 20)
        assert result.dps > 0
        assert result.hit_damage > 0
        assert result.average_hit > 0

    def test_average_hit_equals_formula(self):
        """AverageHit = (1-crit)*hit + crit*hit*mult"""
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Fireball", 1)
        hit = result.hit_damage
        expected = (1 - stats.crit_chance) * hit + stats.crit_chance * hit * stats.crit_multiplier
        assert result.average_hit == pytest.approx(round(expected), abs=1)

    def test_higher_level_has_higher_dps(self):
        stats = _base_mage_stats()
        low_level = calculate_dps(stats, "Fireball", 1)
        high_level = calculate_dps(stats, "Fireball", 20)
        assert high_level.dps > low_level.dps

    def test_spell_damage_increases_dps(self):
        base_stats = _base_mage_stats()
        boosted_stats = aggregate_stats("Mage", "Sorcerer", [], [], [{"name": "Spell Damage", "tier": 1}])
        base_dps = calculate_dps(base_stats, "Fireball", 20)
        boost_dps = calculate_dps(boosted_stats, "Fireball", 20)
        assert boost_dps.dps > base_dps.dps

    def test_crit_contribution_is_percentage(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Fireball", 20)
        assert 0 <= result.crit_contribution_pct <= 100

    def test_attack_speed_affects_dps(self):
        base = _base_mage_stats()
        fast = aggregate_stats("Mage", "Sorcerer", [], [], [{"name": "Cast Speed", "tier": 1}])
        base_dps = calculate_dps(base, "Fireball", 20)
        fast_dps = calculate_dps(fast, "Fireball", 20)
        assert fast_dps.dps > base_dps.dps

    def test_effective_attack_speed_is_positive(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Glacier", 20)
        assert result.effective_attack_speed > 0

    def test_melee_skill_uses_attack_speed_pct(self):
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        faster = aggregate_stats("Sentinel", "Paladin", [], [], [{"name": "Attack Speed", "tier": 1}])
        base_dps = calculate_dps(base, "Rive", 20)
        fast_dps = calculate_dps(faster, "Rive", 20)
        assert fast_dps.dps > base_dps.dps

    def test_spell_does_not_benefit_from_attack_speed_affix(self):
        base = aggregate_stats("Mage", "Sorcerer", [], [], [])
        # Attack speed affix should not affect Fireball (it's a spell)
        with_atk = aggregate_stats("Mage", "Sorcerer", [], [], [{"name": "Attack Speed", "tier": 1}])
        assert calculate_dps(base, "Fireball", 20).dps == calculate_dps(with_atk, "Fireball", 20).dps

    def test_all_known_skills_have_positive_dps(self):
        stats = _base_mage_stats()
        for skill_name in list(SKILL_STATS.keys())[:10]:
            result = calculate_dps(stats, skill_name, 20)
            assert result.dps >= 0, f"Negative DPS for skill: {skill_name}"

    def test_more_damage_multiplier_scales_dps(self):
        """'more' multiplier stacks multiplicatively — 1.5× more should give ~1.5× DPS."""
        base = _base_mage_stats()
        more = _base_mage_stats()
        more.more_damage_multiplier = 1.5
        base_dps = calculate_dps(base, "Fireball", 20)
        more_dps = calculate_dps(more, "Fireball", 20)
        ratio = more_dps.dps / base_dps.dps
        assert abs(ratio - 1.5) < 0.01

    def test_more_multiplier_one_is_neutral(self):
        """Default more_damage_multiplier=1.0 should produce same DPS as not setting it."""
        stats = _base_mage_stats()
        stats.more_damage_multiplier = 1.0
        r1 = calculate_dps(stats, "Fireball", 20)
        r2 = calculate_dps(_base_mage_stats(), "Fireball", 20)
        assert r1.dps == r2.dps


class TestMonteCarloDPS:
    def test_returns_monte_carlo_result(self):
        stats = _base_mage_stats()
        result = monte_carlo_dps(stats, "Fireball", 20, n=500)
        assert isinstance(result, MonteCarloDPS)

    def test_mean_dps_close_to_calculated_dps(self):
        stats = _base_mage_stats()
        expected = calculate_dps(stats, "Fireball", 20).dps
        mc = monte_carlo_dps(stats, "Fireball", 20, n=5_000)
        # Monte Carlo mean should be within 10% of deterministic
        assert abs(mc.mean_dps - expected) / expected < 0.1

    def test_max_is_gte_mean(self):
        stats = _base_mage_stats()
        mc = monte_carlo_dps(stats, "Fireball", 20, n=500)
        assert mc.max_dps >= mc.mean_dps

    def test_min_is_lte_mean(self):
        stats = _base_mage_stats()
        mc = monte_carlo_dps(stats, "Fireball", 20, n=500)
        assert mc.min_dps <= mc.mean_dps

    def test_high_crit_chance_raises_mean(self):
        low_crit = aggregate_stats("Mage", "Sorcerer", [], [], [])
        high_crit = aggregate_stats("Mage", "Sorcerer", [], [], [{"name": "Critical Strike Chance", "tier": 1}])
        mc_low = monte_carlo_dps(low_crit, "Fireball", 20, n=10_000)
        mc_high = monte_carlo_dps(high_crit, "Fireball", 20, n=10_000)
        assert mc_high.mean_dps > mc_low.mean_dps

    def test_unknown_skill_returns_zeros(self):
        stats = _base_mage_stats()
        mc = monte_carlo_dps(stats, "FakeSkill", 20, n=100)
        assert mc.mean_dps == 0

    def test_n_simulations_matches_requested(self):
        stats = _base_mage_stats()
        mc = monte_carlo_dps(stats, "Fireball", 20, n=777)
        assert mc.n_simulations == 777


class TestFlatAddedDamage:
    def test_flat_spell_damage_increases_dps(self):
        base = _base_mage_stats()
        boosted = _base_mage_stats()
        boosted.added_spell_damage = 50
        assert calculate_dps(boosted, "Fireball", 20).dps > calculate_dps(base, "Fireball", 20).dps

    def test_flat_melee_damage_increases_melee_dps(self):
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.added_melee_physical = 50
        assert calculate_dps(boosted, "Rive", 20).dps > calculate_dps(base, "Rive", 20).dps

    def test_flat_spell_damage_does_not_affect_melee_only(self):
        """Flat spell damage should not boost a pure melee skill like Rive."""
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.added_spell_damage = 100
        assert calculate_dps(boosted, "Rive", 20).dps == calculate_dps(base, "Rive", 20).dps

    def test_flat_damage_added_field_populated(self):
        stats = _base_mage_stats()
        stats.added_spell_fire = 20
        result = calculate_dps(stats, "Fireball", 20)
        assert result.flat_damage_added > 0

    def test_flat_throw_damage_boosts_shurikens(self):
        base = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        boosted = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        boosted.added_throw_physical = 30
        assert calculate_dps(boosted, "Shurikens", 20).dps > calculate_dps(base, "Shurikens", 20).dps

    def test_flat_bow_damage_boosts_multishot(self):
        base = aggregate_stats("Rogue", "Marksman", [], [], [])
        boosted = aggregate_stats("Rogue", "Marksman", [], [], [])
        boosted.added_bow_physical = 30
        assert calculate_dps(boosted, "Multishot", 20).dps > calculate_dps(base, "Multishot", 20).dps


class TestWeaponTypeBonuses:
    def test_melee_damage_pct_boosts_rive(self):
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.melee_damage_pct = 40
        assert calculate_dps(boosted, "Rive", 20).dps > calculate_dps(base, "Rive", 20).dps

    def test_throwing_damage_pct_boosts_javelin(self):
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.throwing_damage_pct = 40
        assert calculate_dps(boosted, "Javelin", 20).dps > calculate_dps(base, "Javelin", 20).dps

    def test_bow_damage_pct_boosts_arrow_barrage(self):
        base = aggregate_stats("Rogue", "Marksman", [], [], [])
        boosted = aggregate_stats("Rogue", "Marksman", [], [], [])
        boosted.bow_damage_pct = 40
        assert calculate_dps(boosted, "Arrow Barrage", 20).dps > calculate_dps(base, "Arrow Barrage", 20).dps

    def test_elemental_damage_pct_boosts_fireball(self):
        base = _base_mage_stats()
        boosted = _base_mage_stats()
        boosted.elemental_damage_pct = 40
        assert calculate_dps(boosted, "Fireball", 20).dps > calculate_dps(base, "Fireball", 20).dps

    def test_elemental_damage_pct_does_not_boost_physical_only(self):
        """Rive scales with physical only — elemental_damage_pct should not help."""
        base = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.elemental_damage_pct = 100
        assert calculate_dps(boosted, "Rive", 20).dps == calculate_dps(base, "Rive", 20).dps

    def test_throwing_attack_speed_boosts_shurikens(self):
        base = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        boosted = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        boosted.throwing_attack_speed = 20
        assert calculate_dps(boosted, "Shurikens", 20).dps > calculate_dps(base, "Shurikens", 20).dps


class TestAilmentDPS:
    def test_zero_ailment_chance_gives_zero_ailment_dps(self):
        stats = _base_mage_stats()
        result = calculate_dps(stats, "Fireball", 20)
        assert result.bleed_dps == 0
        assert result.ignite_dps == 0
        assert result.poison_dps == 0
        assert result.ailment_dps == 0

    def test_bleed_chance_produces_bleed_dps(self):
        stats = aggregate_stats("Sentinel", "Paladin", [], [], [])
        stats.bleed_chance_pct = 50
        result = calculate_dps(stats, "Rive", 20)
        assert result.bleed_dps > 0
        assert result.ailment_dps > 0
        assert result.total_dps > result.dps

    def test_ignite_chance_produces_ignite_dps(self):
        stats = _base_mage_stats()
        stats.ignite_chance_pct = 50
        result = calculate_dps(stats, "Fireball", 20)
        assert result.ignite_dps > 0

    def test_poison_chance_produces_poison_dps(self):
        stats = aggregate_stats("Rogue", "Bladedancer", [], [], [])
        stats.poison_chance_pct = 80
        result = calculate_dps(stats, "Puncture", 20)
        assert result.poison_dps > 0

    def test_total_dps_is_hit_plus_ailment(self):
        stats = _base_mage_stats()
        stats.ignite_chance_pct = 30
        result = calculate_dps(stats, "Fireball", 20)
        assert result.total_dps == result.dps + result.ailment_dps

    def test_bleed_damage_pct_increases_bleed_dps(self):
        stats = aggregate_stats("Sentinel", "Paladin", [], [], [])
        stats.bleed_chance_pct = 50
        base_result = calculate_dps(stats, "Rive", 20)

        boosted = aggregate_stats("Sentinel", "Paladin", [], [], [])
        boosted.bleed_chance_pct = 50
        boosted.bleed_damage_pct = 80
        boosted_result = calculate_dps(boosted, "Rive", 20)
        assert boosted_result.bleed_dps > base_result.bleed_dps

    def test_dot_damage_pct_increases_all_ailments(self):
        stats = _base_mage_stats()
        stats.ignite_chance_pct = 50
        stats.poison_chance_pct = 50
        base_result = calculate_dps(stats, "Fireball", 20)

        boosted = _base_mage_stats()
        boosted.ignite_chance_pct = 50
        boosted.poison_chance_pct = 50
        boosted.dot_damage_pct = 60
        boosted_result = calculate_dps(boosted, "Fireball", 20)
        assert boosted_result.ignite_dps > base_result.ignite_dps
        assert boosted_result.poison_dps > base_result.poison_dps

    def test_ailment_chance_capped_at_100(self):
        """200% bleed chance should not produce more ailment DPS than 100%."""
        stats = aggregate_stats("Sentinel", "Paladin", [], [], [])
        stats.bleed_chance_pct = 100
        r100 = calculate_dps(stats, "Rive", 20)

        stats.bleed_chance_pct = 200
        r200 = calculate_dps(stats, "Rive", 20)
        assert r100.bleed_dps == r200.bleed_dps
