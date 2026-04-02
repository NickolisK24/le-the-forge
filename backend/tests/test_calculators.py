"""
Deterministic tests for domain calculator functions.

Each test asserts exact numeric outputs for known inputs so that any change
to stacking formulas, pipeline order, or calculator logic causes an immediate
and obvious failure with a clear expected/actual diff.

Covered paths
─────────────
  Additive stacking   — combine_additive_percents
  Multiplicative stacking — apply_more_multiplier
  Percent application — apply_percent_bonus
  Full pipeline       — calculate_final_damage + DamageContext
"""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.domain.calculators.stat_calculator import apply_percent_bonus, combine_additive_percents
from app.domain.calculators.more_multiplier_calculator import apply_more_multiplier
from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
from app.domain.skill import SkillStatDef
from app.domain.calculators.skill_calculator import scale_skill_damage
from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.increased_damage_calculator import sum_increased_damage
from app.domain.calculators.ailment_calculator import ailment_stack_count, calc_ailment_dps
from app.domain.calculators.damage_type_router import source_type_for_ailment
from app.constants.combat import BLEED_BASE_RATIO, BLEED_DURATION, IGNITE_DPS_RATIO, IGNITE_DURATION, POISON_DPS_RATIO, POISON_DURATION
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ctx(base: float, increased: float, more: list[float]) -> DamageContext:
    """Shorthand DamageContext constructor for inline test clarity."""
    return DamageContext(base_damage=base, increased_damage=increased, more_damage=more)


# ---------------------------------------------------------------------------
# Additive stacking — combine_additive_percents
# ---------------------------------------------------------------------------

class TestCombineAdditivePercents(unittest.TestCase):
    def test_zero_sources_returns_zero(self):
        assert combine_additive_percents() == 0.0

    def test_single_source_identity(self):
        assert combine_additive_percents(75.0) == 75.0

    def test_two_sources_sum_linearly(self):
        # 50 + 50 = 100, not 50 × 50 = 125 (that would be multiplicative)
        assert combine_additive_percents(50.0, 50.0) == 100.0

    def test_three_sources_sum_linearly(self):
        assert combine_additive_percents(25.0, 10.0, 15.0) == 50.0

    def test_negative_contribution_subtracts(self):
        assert combine_additive_percents(100.0, -25.0) == 75.0

    def test_additive_is_not_multiplicative(self):
        # Two 50% sources MUST add (100%) not compound (125%).
        additive_result = combine_additive_percents(50.0, 50.0)
        multiplicative_result = 50.0 + 50.0 + (50.0 * 50.0) / 100  # compound formula
        assert additive_result == 100.0
        assert additive_result != multiplicative_result


# ---------------------------------------------------------------------------
# Percent application — apply_percent_bonus
# ---------------------------------------------------------------------------

class TestApplyPercentBonus(unittest.TestCase):
    def test_zero_bonus_is_identity(self):
        assert apply_percent_bonus(100.0, 0.0) == 100.0

    def test_100_pct_doubles(self):
        assert apply_percent_bonus(100.0, 100.0) == 200.0

    def test_50_pct_on_200_base(self):
        assert apply_percent_bonus(200.0, 50.0) == 300.0

    def test_150_pct_on_100_base(self):
        # 100 × (1 + 150/100) = 100 × 2.5 = 250
        assert apply_percent_bonus(100.0, 150.0) == 250.0

    def test_formula_matches_expected(self):
        base, pct = 250.0, 60.0
        assert apply_percent_bonus(base, pct) == base * (1 + pct / 100)


# ---------------------------------------------------------------------------
# Multiplicative stacking — apply_more_multiplier
# ---------------------------------------------------------------------------

class TestApplyMoreMultiplier(unittest.TestCase):
    def test_empty_list_is_identity(self):
        assert apply_more_multiplier(100.0, []) == 100.0

    def test_zero_pct_source_is_neutral(self):
        assert apply_more_multiplier(100.0, [0.0]) == 100.0

    def test_single_50_pct_more(self):
        assert apply_more_multiplier(100.0, [50.0]) == 150.0

    def test_two_sources_compound_not_add(self):
        # 50% more and 20% more:
        #   Correct (multiplicative): 100 × 1.5 × 1.2 = 180
        #   Wrong   (additive):       100 × 1.7       = 170
        assert apply_more_multiplier(100.0, [50.0, 20.0]) == 180.0
        assert apply_more_multiplier(100.0, [50.0, 20.0]) != 170.0

    def test_three_sources_compound(self):
        # 100 × 1.5 × 1.2 × 1.1 = 198.0
        result = apply_more_multiplier(100.0, [50.0, 20.0, 10.0])
        assert abs(result - 198.0) < 0.001

    def test_order_is_commutative(self):
        # Multiplication is order-independent; both orderings must be equal
        assert apply_more_multiplier(100.0, [50.0, 20.0]) == apply_more_multiplier(100.0, [20.0, 50.0])


# ---------------------------------------------------------------------------
# Full damage pipeline — Base → Increased → More → Final
# ---------------------------------------------------------------------------

class TestDamagePipeline(unittest.TestCase):
    def test_base_only(self):
        # No bonuses → output equals input
        assert calculate_final_damage(ctx(100.0, 0.0, [])).total == 100.0

    def test_increased_only(self):
        # 100 × (1 + 100/100) = 200
        assert calculate_final_damage(ctx(100.0, 100.0, [])).total == 200.0

    def test_more_only(self):
        # 100 × 1.5 = 150
        assert calculate_final_damage(ctx(100.0, 0.0, [50.0])).total == 150.0

    def test_increased_then_more(self):
        # Base 100, 100% increased, 50% more:
        #   100 × (1 + 100/100) × (1 + 50/100) = 100 × 2.0 × 1.5 = 300
        assert calculate_final_damage(ctx(100.0, 100.0, [50.0])).total == 300.0

    def test_pipeline_order_not_additive_mixing(self):
        # If increased and more were naively added as a single pool:
        #   100 × (1 + (100 + 50)/100) = 100 × 2.5 = 250  ← WRONG
        # Correct separate-stage result is 300, not 250.
        result = calculate_final_damage(ctx(100.0, 100.0, [50.0])).total
        assert result == 300.0
        assert result != 250.0

    def test_multiple_more_sources_compound_after_increased(self):
        # Base 100, 100% increased, 50% more + 20% more:
        #   100 × 2.0 × 1.5 × 1.2 = 360
        assert calculate_final_damage(ctx(100.0, 100.0, [50.0, 20.0])).total == 360.0

    def test_additive_increased_pool_stacks_before_more(self):
        # Two 50% increased sources must combine additively to 100% total,
        # then a 50% more source applies multiplicatively.
        # Correct:  combine(50, 50) = 100% increased → 100 × 2.0 × 1.5 = 300
        # Wrong:    treat as two 1.5x more → 100 × 1.5 × 1.5 = 225
        total_increased = combine_additive_percents(50.0, 50.0)  # = 100.0
        result = calculate_final_damage(ctx(100.0, total_increased, [50.0])).total
        assert result == 300.0
        assert result != 225.0  # would be wrong if increased sources compounded

    def test_large_realistic_values(self):
        # Simulate a realistic high-investment build:
        # Base 500, 300% increased, two 40% more sources
        # 500 × (1 + 300/100) × 1.4 × 1.4 = 500 × 4.0 × 1.96 = 3920
        result = calculate_final_damage(ctx(500.0, 300.0, [40.0, 40.0])).total
        assert abs(result - 3920.0) < 0.01

    def test_zero_base_produces_zero(self):
        assert calculate_final_damage(ctx(0.0, 200.0, [50.0])).total == 0.0

    def test_debug_flag_does_not_change_result(self):
        c = ctx(100.0, 100.0, [50.0])
        assert calculate_final_damage(c, debug=True).total == calculate_final_damage(c, debug=False).total

# ---------------------------------------------------------------------------
# Damage scaling consistency — per-type routing
# ---------------------------------------------------------------------------

def _skill(damage_types: tuple, scaling_stats: tuple = (), **flags) -> SkillStatDef:
    """Minimal SkillStatDef for routing tests — exact damage_types, no level math."""
    return SkillStatDef(
        base_damage=100.0,
        level_scaling=0.10,
        attack_speed=1.0,
        scaling_stats=scaling_stats,
        data_version="test",
        damage_types=damage_types,
        **flags,
    )


class TestDamageScalingConsistency(unittest.TestCase):
    """
    Deterministic tests for per-type increased damage routing.

    Each test asserts the exact output of sum_increased_damage so that any
    change to elemental routing, type→stat mapping, or the additive pool
    immediately surfaces as a numeric diff.
    """

    # --- Single type ---

    def test_single_fire_routes_elemental(self):
        # FIRE damage: fire_damage_pct and elemental_damage_pct both apply.
        # fire(100) + elemental(50) = 150
        skill = _skill((DamageType.FIRE,), ("fire_damage_pct",))
        stats = BuildStats(fire_damage_pct=100.0, elemental_damage_pct=50.0)
        assert sum_increased_damage(stats, skill) == 150.0

    def test_single_cold_routes_elemental(self):
        # COLD damage: same pattern — cold and elemental stack additively.
        # cold(80) + elemental(40) = 120
        skill = _skill((DamageType.COLD,), ("cold_damage_pct",))
        stats = BuildStats(cold_damage_pct=80.0, elemental_damage_pct=40.0)
        assert sum_increased_damage(stats, skill) == 120.0

    def test_single_lightning_routes_elemental(self):
        # LIGHTNING damage: lightning and elemental stack additively.
        # lightning(60) + elemental(30) = 90
        skill = _skill((DamageType.LIGHTNING,), ("lightning_damage_pct",))
        stats = BuildStats(lightning_damage_pct=60.0, elemental_damage_pct=30.0)
        assert sum_increased_damage(stats, skill) == 90.0

    # --- Mixed type ---

    def test_mixed_fire_physical_elemental_in_shared_pool(self):
        # FIRE + PHYSICAL: FIRE pulls elemental_damage_pct into the combined
        # increased pool for the whole skill.
        # fire(100) + physical(50) + elemental(30) = 180
        skill = _skill(
            (DamageType.FIRE, DamageType.PHYSICAL),
            ("fire_damage_pct", "physical_damage_pct"),
        )
        stats = BuildStats(fire_damage_pct=100.0, physical_damage_pct=50.0, elemental_damage_pct=30.0)
        assert sum_increased_damage(stats, skill) == 180.0

    # --- Elemental stacking ---

    def test_elemental_excluded_for_non_elemental_type(self):
        # NECROTIC damage: elemental_damage_pct must NOT be included.
        # necrotic(50) only; elemental(30) is excluded.
        skill = _skill((DamageType.NECROTIC,), ("necrotic_damage_pct",))
        stats = BuildStats(necrotic_damage_pct=50.0, elemental_damage_pct=30.0)
        assert sum_increased_damage(stats, skill) == 50.0

    def test_elemental_excluded_for_void(self):
        # VOID damage: same exclusion applies.
        # void(70) only; elemental(40) is excluded.
        skill = _skill((DamageType.VOID,), ("void_damage_pct",))
        stats = BuildStats(void_damage_pct=70.0, elemental_damage_pct=40.0)
        assert sum_increased_damage(stats, skill) == 70.0

    def test_elemental_zero_does_not_affect_result(self):
        # elemental_damage_pct=0 is neutral — routing it in must not change the total.
        # fire(100) + elemental(0) = 100
        skill = _skill((DamageType.FIRE,), ("fire_damage_pct",))
        stats = BuildStats(fire_damage_pct=100.0, elemental_damage_pct=0.0)
        assert sum_increased_damage(stats, skill) == 100.0


# ---------------------------------------------------------------------------
# SkillStatDef — damage_types derivation
# ---------------------------------------------------------------------------

class TestSkillStatDefDamageTypes(unittest.TestCase):

    def test_spell_only_skill_has_no_damage_types(self):
        # spell_damage_pct is a SkillTag (delivery modifier), not a DamageType channel.
        # Until skills.json adds explicit damage_types, this skill has none.
        # UPDATE THIS TEST INTENTIONALLY when JSON is updated — not as a side effect.
        skill = SkillStatDef.from_dict({
            "name": "TestSpell",
            "scaling_stats": ["spell_damage_pct"],
        })
        assert skill.damage_types == ()


# ---------------------------------------------------------------------------
# scale_skill_damage — multi-type distribution
# ---------------------------------------------------------------------------

class TestScaleSkillDamage(unittest.TestCase):

    def test_single_type_returns_full_value(self):
        # Single type: the full scaled total maps to one key.
        # 100 × (1 + 0.10 × 9) = 190.0
        result = scale_skill_damage(100.0, 0.10, 10, (DamageType.FIRE,))
        self.assertEqual(result, {DamageType.FIRE: 190.0})

    def test_multi_type_splits_evenly(self):
        # FIRE + PHYSICAL: each gets base/2.
        # 100 × (1 + 0.10 × 9) = 190.0 → 95.0 each
        result = scale_skill_damage(100.0, 0.10, 10, (DamageType.FIRE, DamageType.PHYSICAL))
        self.assertAlmostEqual(result[DamageType.FIRE],     95.0, places=9)
        self.assertAlmostEqual(result[DamageType.PHYSICAL], 95.0, places=9)

    def test_multi_type_sum_equals_total_scaled_damage(self):
        # The sum of all per-type values must equal the untyped total.
        # 100 × (1 + 0.10 × 9) = 190.0
        result = scale_skill_damage(100.0, 0.10, 10, (DamageType.FIRE, DamageType.PHYSICAL))
        self.assertAlmostEqual(sum(result.values()), 190.0, places=9)

    def test_multi_type_rounding_stability(self):
        # base=100, scaling=0.15, level=7 → 190.0 / 3 = 63.333...
        # Non-round per-type values; sum must equal expected total within float precision.
        result = scale_skill_damage(
            base=100,
            scaling=0.15,
            level=7,
            damage_types=(DamageType.FIRE, DamageType.PHYSICAL, DamageType.COLD),
        )
        total = sum(result.values())
        expected = 100 * (1 + 0.15 * (7 - 1))
        assert math.isclose(total, expected, rel_tol=1e-9, abs_tol=1e-12)

    def test_empty_damage_types_returns_empty_dict(self):
        result = scale_skill_damage(100.0, 0.10, 10, ())
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# Ailment routing — source_type_for_ailment
# ---------------------------------------------------------------------------

class TestAilmentRouting(unittest.TestCase):
    """
    Deterministic tests for ailment → source hit-type mapping.

    The table is the single source of truth; these tests lock it.
    Update intentionally if LE changes the trigger mechanic.
    """

    def test_bleed_source_is_physical(self):
        assert source_type_for_ailment(DamageType.BLEED) == DamageType.PHYSICAL

    def test_ignite_source_is_fire(self):
        assert source_type_for_ailment(DamageType.IGNITE) == DamageType.FIRE

    def test_poison_source_is_poison(self):
        assert source_type_for_ailment(DamageType.POISON) == DamageType.POISON

    def test_non_ailment_raises(self):
        # FIRE is not an ailment type; the lookup must fail rather than silently return.
        with self.assertRaises(KeyError):
            source_type_for_ailment(DamageType.FIRE)

    def test_physical_raises(self):
        # PHYSICAL is a hit type, not an ailment type.
        with self.assertRaises(KeyError):
            source_type_for_ailment(DamageType.PHYSICAL)


# ---------------------------------------------------------------------------
# Ailment stack modeling — ailment_stack_count + calc_ailment_dps
# ---------------------------------------------------------------------------

class TestAilmentStackCount(unittest.TestCase):
    """
    Deterministic tests for steady-state ailment stack math.

    Formula: stacks = effective_as × chance × duration
    """

    def test_unit_values_equal_duration(self):
        # as=1, chance=1.0 → stacks = 1 × 1 × duration
        assert ailment_stack_count(1.0, 1.0, BLEED_DURATION) == BLEED_DURATION

    def test_half_chance_halves_stacks(self):
        # as=2, chance=0.5 → proc_rate=1.0 → same stacks as as=1, chance=1.0
        assert ailment_stack_count(2.0, 0.5, 3.0) == ailment_stack_count(1.0, 1.0, 3.0)

    def test_zero_chance_gives_zero_stacks(self):
        assert ailment_stack_count(2.0, 0.0, 3.0) == 0.0

    def test_zero_as_gives_zero_stacks(self):
        assert ailment_stack_count(0.0, 1.0, 3.0) == 0.0

    def test_proportional_to_attack_speed(self):
        # Doubling attack speed doubles stacks.
        assert ailment_stack_count(2.0, 0.5, 4.0) == 2 * ailment_stack_count(1.0, 0.5, 4.0)

    def test_proportional_to_duration(self):
        # Doubling duration doubles stacks.
        assert ailment_stack_count(1.5, 0.4, 6.0) == 2 * ailment_stack_count(1.5, 0.4, 3.0)

    def test_exact_numeric(self):
        # 1.5 as × 0.4 chance × 3.0 duration = 1.8
        assert math.isclose(ailment_stack_count(1.5, 0.4, 3.0), 1.8, rel_tol=1e-9, abs_tol=1e-12)


class TestCalcAilmentDps(unittest.TestCase):
    """
    Deterministic tests for calc_ailment_dps output.

    Expected values derived from the stack model:
        stacks       = effective_as × chance × duration
        per_stack_dps = hit_damage × ratio [/ duration for bleed]
        base_dps     = per_stack_dps × stacks
        final_dps    = round(base_dps × (1 + increased_pct / 100))
    """

    def test_bleed_only_no_bonuses(self):
        # hit=100, as=1.0, bleed_chance=100% → chance=1.0
        # stacks = 1.0 × 1.0 × BLEED_DURATION = BLEED_DURATION
        # per_stack = 100 × BLEED_BASE_RATIO / BLEED_DURATION
        # base = per_stack × BLEED_DURATION = 100 × BLEED_BASE_RATIO = 70
        # increased = 0 → final = 70
        stats = BuildStats(bleed_chance_pct=100.0)
        bleed, ignite, poison = calc_ailment_dps(100.0, 1.0, stats)
        expected = round(100.0 * BLEED_BASE_RATIO)
        assert bleed == expected
        assert ignite == 0
        assert poison == 0

    def test_ignite_only_no_bonuses(self):
        # hit=100, as=1.0, ignite_chance=100%
        # stacks = 1.0 × 1.0 × IGNITE_DURATION
        # per_stack = 100 × IGNITE_DPS_RATIO = 20
        # base = 20 × IGNITE_DURATION = 60
        # final = 60
        stats = BuildStats(ignite_chance_pct=100.0)
        bleed, ignite, poison = calc_ailment_dps(100.0, 1.0, stats)
        expected = round(100.0 * IGNITE_DPS_RATIO * IGNITE_DURATION)
        assert bleed == 0
        assert ignite == expected
        assert poison == 0

    def test_poison_only_no_bonuses(self):
        # hit=100, as=1.0, poison_chance=100%
        # base = 100 × POISON_DPS_RATIO × POISON_DURATION = 90
        stats = BuildStats(poison_chance_pct=100.0)
        bleed, ignite, poison = calc_ailment_dps(100.0, 1.0, stats)
        expected = round(100.0 * POISON_DPS_RATIO * POISON_DURATION)
        assert bleed == 0
        assert ignite == 0
        assert poison == expected

    def test_bleed_chance_capped_at_100pct(self):
        # 150% chance is capped to 1.0 — same result as 100%.
        stats_100 = BuildStats(bleed_chance_pct=100.0)
        stats_150 = BuildStats(bleed_chance_pct=150.0)
        b100, _, _ = calc_ailment_dps(100.0, 1.0, stats_100)
        b150, _, _ = calc_ailment_dps(100.0, 1.0, stats_150)
        assert b100 == b150

    def test_bleed_scales_with_attack_speed(self):
        # Doubling effective_as doubles bleed DPS (linearly via stack count).
        stats = BuildStats(bleed_chance_pct=50.0)
        b1, _, _ = calc_ailment_dps(100.0, 1.0, stats)
        b2, _, _ = calc_ailment_dps(100.0, 2.0, stats)
        assert b2 == b1 * 2

    def test_increased_bleed_applies(self):
        # bleed_damage_pct=100 doubles bleed DPS.
        stats_base = BuildStats(bleed_chance_pct=100.0)
        stats_inc  = BuildStats(bleed_chance_pct=100.0, bleed_damage_pct=100.0)
        b_base, _, _ = calc_ailment_dps(100.0, 1.0, stats_base)
        b_inc,  _, _ = calc_ailment_dps(100.0, 1.0, stats_inc)
        assert b_inc == b_base * 2

    def test_zero_chance_produces_zero(self):
        # No proc chance → all ailment DPS is zero regardless of other stats.
        stats = BuildStats(bleed_damage_pct=200.0, ignite_damage_pct=200.0)
        bleed, ignite, poison = calc_ailment_dps(500.0, 2.0, stats)
        assert bleed == 0
        assert ignite == 0
        assert poison == 0


if __name__ == '__main__':
    unittest.main()
