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
from app.domain.calculators.conversion_calculator import DamageConversion, apply_conversions
from app.domain.calculators.conditional_modifier_calculator import (
    Condition, ConditionContext, ConditionalModifier, evaluate_modifiers,
)
from app.domain.calculators.enemy_mitigation_calculator import (
    armor_mitigation, apply_armor,
    apply_penetration, effective_resistance,
    damage_multiplier as enemy_damage_multiplier,
    weighted_damage_multiplier,
    RES_CAP,
)
from app.domain.enemy import EnemyProfile
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
# Conditional modifiers — situational damage bonuses
# ---------------------------------------------------------------------------

class TestConditionalModifiers(unittest.TestCase):
    """
    Tests for evaluate_modifiers() against ConditionContext.

    Each test uses the minimal context that isolates one variable.
    """

    def test_empty_modifier_list_gives_zero(self):
        ctx = ConditionContext()
        assert evaluate_modifiers([], ctx) == 0.0

    def test_no_active_conditions_gives_zero(self):
        # All conditions inactive — no modifiers should fire.
        mods = [
            ConditionalModifier(Condition.ON_CRIT,        30.0),
            ConditionalModifier(Condition.TARGET_STUNNED, 20.0),
            ConditionalModifier(Condition.TARGET_FROZEN,  25.0),
        ]
        ctx = ConditionContext()  # defaults: no crit, full health, no statuses
        assert evaluate_modifiers(mods, ctx) == 0.0

    # --- ON_CRIT ---

    def test_on_crit_applies_when_crit(self):
        mod = ConditionalModifier(Condition.ON_CRIT, 30.0)
        ctx = ConditionContext(is_crit=True)
        assert math.isclose(evaluate_modifiers([mod], ctx), 30.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_on_crit_not_applied_when_not_crit(self):
        mod = ConditionalModifier(Condition.ON_CRIT, 30.0)
        ctx = ConditionContext(is_crit=False)
        assert evaluate_modifiers([mod], ctx) == 0.0

    # --- LOW_HEALTH ---

    def test_low_health_applies_below_threshold(self):
        mod = ConditionalModifier(Condition.LOW_HEALTH, 50.0, threshold=35.0)
        ctx = ConditionContext(target_health_pct=20.0)
        assert math.isclose(evaluate_modifiers([mod], ctx), 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_low_health_not_applied_above_threshold(self):
        mod = ConditionalModifier(Condition.LOW_HEALTH, 50.0, threshold=35.0)
        ctx = ConditionContext(target_health_pct=60.0)
        assert evaluate_modifiers([mod], ctx) == 0.0

    def test_low_health_applies_at_exact_threshold(self):
        # Threshold is inclusive (≤).
        mod = ConditionalModifier(Condition.LOW_HEALTH, 50.0, threshold=35.0)
        ctx = ConditionContext(target_health_pct=35.0)
        assert math.isclose(evaluate_modifiers([mod], ctx), 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_low_health_not_applied_one_above_threshold(self):
        mod = ConditionalModifier(Condition.LOW_HEALTH, 50.0, threshold=35.0)
        ctx = ConditionContext(target_health_pct=35.01)
        assert evaluate_modifiers([mod], ctx) == 0.0

    # --- Multiple conditions stacking ---

    def test_multiple_active_conditions_stack_additively(self):
        # Crit (30%) + stun (20%) both active → 50% total.
        mods = [
            ConditionalModifier(Condition.ON_CRIT,        30.0),
            ConditionalModifier(Condition.TARGET_STUNNED, 20.0),
        ]
        ctx = ConditionContext(is_crit=True, target_stunned=True)
        assert math.isclose(evaluate_modifiers(mods, ctx), 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_inactive_modifier_does_not_contribute(self):
        # Crit (30%) active, frozen (25%) inactive → only 30%.
        mods = [
            ConditionalModifier(Condition.ON_CRIT,       30.0),
            ConditionalModifier(Condition.TARGET_FROZEN, 25.0),
        ]
        ctx = ConditionContext(is_crit=True, target_frozen=False)
        assert math.isclose(evaluate_modifiers(mods, ctx), 30.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_same_condition_multiple_modifiers_stack(self):
        # Two separate ON_CRIT modifiers (e.g. from different gear pieces).
        mods = [
            ConditionalModifier(Condition.ON_CRIT, 20.0),
            ConditionalModifier(Condition.ON_CRIT, 15.0),
        ]
        ctx = ConditionContext(is_crit=True)
        assert math.isclose(evaluate_modifiers(mods, ctx), 35.0, rel_tol=1e-9, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# Status effect modifiers — stunned / frozen targets
# ---------------------------------------------------------------------------

class TestStatusEffectModifiers(unittest.TestCase):
    """
    Tests focused specifically on TARGET_STUNNED and TARGET_FROZEN conditions.

    Status bonuses must not leak across status types.
    """

    def test_stunned_applies_when_target_is_stunned(self):
        mod = ConditionalModifier(Condition.TARGET_STUNNED, 40.0)
        ctx = ConditionContext(target_stunned=True)
        assert math.isclose(evaluate_modifiers([mod], ctx), 40.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_stunned_not_applied_when_not_stunned(self):
        mod = ConditionalModifier(Condition.TARGET_STUNNED, 40.0)
        ctx = ConditionContext(target_stunned=False)
        assert evaluate_modifiers([mod], ctx) == 0.0

    def test_frozen_applies_when_target_is_frozen(self):
        mod = ConditionalModifier(Condition.TARGET_FROZEN, 35.0)
        ctx = ConditionContext(target_frozen=True)
        assert math.isclose(evaluate_modifiers([mod], ctx), 35.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_frozen_not_applied_when_not_frozen(self):
        mod = ConditionalModifier(Condition.TARGET_FROZEN, 35.0)
        ctx = ConditionContext(target_frozen=False)
        assert evaluate_modifiers([mod], ctx) == 0.0

    def test_stunned_bonus_does_not_apply_to_frozen_condition(self):
        # A STUNNED modifier must not fire when only frozen is active.
        mod = ConditionalModifier(Condition.TARGET_STUNNED, 40.0)
        ctx = ConditionContext(target_frozen=True, target_stunned=False)
        assert evaluate_modifiers([mod], ctx) == 0.0

    def test_frozen_bonus_does_not_apply_to_stunned_condition(self):
        mod = ConditionalModifier(Condition.TARGET_FROZEN, 35.0)
        ctx = ConditionContext(target_stunned=True, target_frozen=False)
        assert evaluate_modifiers([mod], ctx) == 0.0

    def test_both_statuses_stack_independently(self):
        # Stunned (40%) + frozen (35%) active at the same time → 75%.
        mods = [
            ConditionalModifier(Condition.TARGET_STUNNED, 40.0),
            ConditionalModifier(Condition.TARGET_FROZEN,  35.0),
        ]
        ctx = ConditionContext(target_stunned=True, target_frozen=True)
        assert math.isclose(evaluate_modifiers(mods, ctx), 75.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_full_context_all_statuses_and_crit(self):
        # All conditions active simultaneously — total is sum of all bonuses.
        mods = [
            ConditionalModifier(Condition.ON_CRIT,        30.0),
            ConditionalModifier(Condition.TARGET_STUNNED, 20.0),
            ConditionalModifier(Condition.TARGET_FROZEN,  15.0),
            ConditionalModifier(Condition.LOW_HEALTH,     25.0, threshold=35.0),
        ]
        ctx = ConditionContext(
            is_crit=True,
            target_stunned=True,
            target_frozen=True,
            target_health_pct=10.0,
        )
        expected = 30.0 + 20.0 + 15.0 + 25.0
        assert math.isclose(evaluate_modifiers(mods, ctx), expected, rel_tol=1e-9, abs_tol=1e-12)


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


# ---------------------------------------------------------------------------
# Damage conversion pipeline — apply_conversions
# ---------------------------------------------------------------------------

class TestApplyConversions(unittest.TestCase):
    """
    Deterministic tests for the conversion pipeline.

    Each test uses clean, hand-computable inputs so failures are unambiguous.
    """

    # --- No-ops ---

    def test_empty_conversions_returns_unchanged(self):
        scaled = {DamageType.PHYSICAL: 100.0}
        result = apply_conversions(scaled, [])
        assert result == {DamageType.PHYSICAL: 100.0}

    def test_self_conversion_is_ignored(self):
        # phys → phys should not change anything.
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.PHYSICAL, 50.0)
        result = apply_conversions(scaled, [conv])
        assert result == {DamageType.PHYSICAL: 100.0}

    def test_zero_pct_conversion_is_ignored(self):
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 0.0)
        result = apply_conversions(scaled, [conv])
        assert result == {DamageType.PHYSICAL: 100.0}

    def test_source_not_in_scaled_is_ignored(self):
        # Conversion references COLD, but scaled only has PHYSICAL.
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.COLD, DamageType.FIRE, 50.0)
        result = apply_conversions(scaled, [conv])
        assert result == {DamageType.PHYSICAL: 100.0}

    # --- Single conversion ---

    def test_full_conversion_removes_source_type(self):
        # 100% phys → fire: physical disappears, fire gains full amount.
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0)
        result = apply_conversions(scaled, [conv])
        assert DamageType.PHYSICAL not in result
        assert math.isclose(result[DamageType.FIRE], 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_partial_conversion_splits_correctly(self):
        # 50% phys → fire: 50 stays physical, 50 becomes fire.
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0)
        result = apply_conversions(scaled, [conv])
        assert math.isclose(result[DamageType.PHYSICAL], 50.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_conversion_adds_to_existing_target(self):
        # Skill already has FIRE damage; 50% phys → fire stacks on top.
        scaled = {DamageType.PHYSICAL: 100.0, DamageType.FIRE: 40.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0)
        result = apply_conversions(scaled, [conv])
        assert math.isclose(result[DamageType.PHYSICAL], 50.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     90.0, rel_tol=1e-9, abs_tol=1e-12)

    # --- Multi-target conversion ---

    def test_two_targets_within_cap(self):
        # 40% phys → fire, 30% phys → cold → total 70%, within 100%.
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 40.0),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD, 30.0),
        ]
        result = apply_conversions(scaled, convs)
        assert math.isclose(result[DamageType.PHYSICAL], 30.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     40.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.COLD],     30.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_over_cap_scales_proportionally(self):
        # 60% phys → fire, 60% phys → cold → total 120%, over cap.
        # Each should be scaled to 50% (100% total).
        # Physical should be fully consumed.
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 60.0),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD, 60.0),
        ]
        result = apply_conversions(scaled, convs)
        assert DamageType.PHYSICAL not in result
        assert math.isclose(result[DamageType.FIRE], 50.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.COLD], 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_total_damage_conserved(self):
        # The sum of all damage after conversion must equal the sum before.
        scaled = {DamageType.PHYSICAL: 80.0, DamageType.FIRE: 40.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD, 25.0),
        ]
        before = sum(scaled.values())
        result = apply_conversions(scaled, convs)
        after = sum(result.values())
        assert math.isclose(before, after, rel_tol=1e-9, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# Conversion priority ordering
# ---------------------------------------------------------------------------

class TestConversionPriority(unittest.TestCase):
    """
    Tests that priority controls the order conversions are applied and that
    higher-priority tiers feed their output into lower-priority tiers.

    Priority model: higher integer = runs first.
    Same-priority same-source entries are grouped and capped together (same
    as the no-priority tests above). Different priority levels are separate
    passes applied sequentially.
    """

    def test_default_priority_is_zero(self):
        # No priority argument → same result as priority=0.
        conv_default  = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0)
        conv_explicit = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0, priority=0)
        scaled = {DamageType.PHYSICAL: 100.0}
        assert apply_conversions(scaled, [conv_default]) == apply_conversions(scaled, [conv_explicit])

    def test_chain_phys_to_fire_to_cold(self):
        # phys→fire (priority=1) runs first; fire→cold (priority=0) runs second
        # and sees the fire produced by the first tier.
        # 100 phys → 100 fire (tier 1) → 100 cold (tier 0)
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0, priority=1),
            DamageConversion(DamageType.FIRE,     DamageType.COLD, 100.0, priority=0),
        ]
        result = apply_conversions(scaled, convs)
        assert DamageType.PHYSICAL not in result
        assert DamageType.FIRE     not in result
        assert math.isclose(result[DamageType.COLD], 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_wrong_priority_order_breaks_chain(self):
        # fire→cold (priority=1) runs before phys→fire (priority=0).
        # No fire exists yet when fire→cold runs → no cold produced.
        # After phys→fire (priority=0), we end up with fire only.
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.FIRE,     DamageType.COLD, 100.0, priority=1),
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 100.0, priority=0),
        ]
        result = apply_conversions(scaled, convs)
        assert DamageType.PHYSICAL not in result
        assert DamageType.COLD     not in result
        assert math.isclose(result[DamageType.FIRE], 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_partial_chain(self):
        # 50% phys → fire (priority=1); 50% fire → cold (priority=0).
        # Tier 1: 50 phys → fire. Result: {PHYSICAL: 50, FIRE: 50}
        # Tier 0: 50% of FIRE → cold. 50 × 0.5 = 25. Result: {PHYSICAL: 50, FIRE: 25, COLD: 25}
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0, priority=1),
            DamageConversion(DamageType.FIRE,     DamageType.COLD, 50.0, priority=0),
        ]
        result = apply_conversions(scaled, convs)
        assert math.isclose(result[DamageType.PHYSICAL], 50.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     25.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.COLD],     25.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_chain_total_damage_conserved(self):
        # Regardless of how many tiers fire, total damage must be unchanged.
        scaled = {DamageType.PHYSICAL: 120.0, DamageType.FIRE: 30.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 75.0, priority=2),
            DamageConversion(DamageType.FIRE,     DamageType.COLD, 50.0, priority=1),
            DamageConversion(DamageType.COLD,     DamageType.LIGHTNING, 40.0, priority=0),
        ]
        before = sum(scaled.values())
        result = apply_conversions(scaled, convs)
        after = sum(result.values())
        assert math.isclose(before, after, rel_tol=1e-9, abs_tol=1e-12)

    def test_same_priority_capping_still_works(self):
        # Two over-cap conversions at the same priority → existing cap behavior.
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 60.0, priority=1),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD, 60.0, priority=1),
        ]
        result = apply_conversions(scaled, convs)
        assert DamageType.PHYSICAL not in result
        assert math.isclose(result[DamageType.FIRE], 50.0, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.COLD], 50.0, rel_tol=1e-9, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# Partial conversion — fractional pct, remainder preservation
# ---------------------------------------------------------------------------

class TestPartialConversion(unittest.TestCase):
    """
    Tests that fractional (non-integer) pct values are handled correctly and
    that the unconverted remainder is not dropped or distorted.

    Acceptance: remaining = source * (1 - pct/100) to float precision.
    """

    def test_one_third_conversion_preserves_remainder(self):
        # pct = 100/3 ≈ 33.333...%
        # converted  = 100 * (1/3) ≈ 33.333...
        # remaining  = 100 * (2/3) ≈ 66.666...
        pct = 100.0 / 3.0
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, pct)
        result = apply_conversions(scaled, [conv])
        expected_remaining = 100.0 * (1.0 - pct / 100.0)
        expected_converted = 100.0 * pct / 100.0
        assert math.isclose(result[DamageType.PHYSICAL], expected_remaining, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     expected_converted, rel_tol=1e-9, abs_tol=1e-12)

    def test_three_way_fractional_split_exhausts_source(self):
        # Three equal thirds (each 100/3 %) — together they sum to 100%.
        # The source should be fully consumed (remainder ≈ 0, dropped by filter).
        pct = 100.0 / 3.0
        scaled = {DamageType.PHYSICAL: 100.0}
        convs = [
            DamageConversion(DamageType.PHYSICAL, DamageType.FIRE,      pct),
            DamageConversion(DamageType.PHYSICAL, DamageType.COLD,      pct),
            DamageConversion(DamageType.PHYSICAL, DamageType.LIGHTNING, pct),
        ]
        result = apply_conversions(scaled, convs)
        # Source should be absent (exhausted within float tolerance).
        assert DamageType.PHYSICAL not in result
        # Each target should receive approximately 1/3 of 100.
        for dt in (DamageType.FIRE, DamageType.COLD, DamageType.LIGHTNING):
            assert math.isclose(result[dt], 100.0 / 3.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_fractional_pct_total_conservation(self):
        # sum(result.values()) == sum(scaled.values()) for any fractional pct.
        pct = 7.77  # arbitrary non-round percentage
        scaled = {DamageType.PHYSICAL: 173.5, DamageType.FIRE: 26.5}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.COLD, pct)
        before = sum(scaled.values())
        result = apply_conversions(scaled, [conv])
        after = sum(result.values())
        assert math.isclose(before, after, rel_tol=1e-9, abs_tol=1e-12)

    def test_small_pct_remainder_not_dropped(self):
        # 0.5% conversion — almost all damage stays as source.
        # The remainder (99.5%) must survive the post-conversion filter.
        scaled = {DamageType.PHYSICAL: 100.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 0.5)
        result = apply_conversions(scaled, [conv])
        assert DamageType.PHYSICAL in result, "remainder was incorrectly dropped"
        assert math.isclose(result[DamageType.PHYSICAL], 99.5, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],      0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_multi_type_base_partial_conversion(self):
        # Skill base is already split: 50 physical + 50 fire (from scale_skill_damage).
        # 33.33% of physical → cold. Fire stays untouched.
        pct = 100.0 / 3.0
        scaled = {DamageType.PHYSICAL: 50.0, DamageType.FIRE: 50.0}
        conv = DamageConversion(DamageType.PHYSICAL, DamageType.COLD, pct)
        result = apply_conversions(scaled, [conv])
        expected_phys = 50.0 * (1.0 - pct / 100.0)
        expected_cold = 50.0 * pct / 100.0
        assert math.isclose(result[DamageType.PHYSICAL], expected_phys, rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.FIRE],     50.0,          rel_tol=1e-9, abs_tol=1e-12)
        assert math.isclose(result[DamageType.COLD],     expected_cold, rel_tol=1e-9, abs_tol=1e-12)

    def test_remainder_matches_complement_formula(self):
        # For any pct, remaining should equal source_amount * (100 - pct) / 100
        # within float precision — not just "approximately correct".
        for pct in (10.0, 25.0, 100.0 / 7.0, 99.9, 0.1):
            source = 200.0
            scaled = {DamageType.PHYSICAL: source}
            conv = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, pct)
            result = apply_conversions(scaled, [conv])
            expected_remaining = source * (100.0 - pct) / 100.0
            if expected_remaining > 1e-9:
                assert math.isclose(
                    result.get(DamageType.PHYSICAL, 0.0),
                    expected_remaining,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                ), f"pct={pct}: expected remaining {expected_remaining}, got {result.get(DamageType.PHYSICAL, 0.0)}"


# ---------------------------------------------------------------------------
# EnemyProfile domain model
# ---------------------------------------------------------------------------

def _make_enemy(**overrides) -> EnemyProfile:
    """Minimal valid EnemyProfile for tests."""
    defaults = {
        "id": "test_enemy",
        "name": "Test Enemy",
        "category": "normal",
        "data_version": "test",
        "health": 1000,
        "armor": 0,
        "resistances": {
            "physical": 0.0,
            "fire": 0.0,
            "cold": 0.0,
            "lightning": 0.0,
        },
    }
    defaults.update(overrides)
    return EnemyProfile(**defaults)


class TestEnemyProfileModel(unittest.TestCase):
    """Verify EnemyProfile construction and serialization."""

    def test_from_dict_populates_required_fields(self):
        d = {
            "id": "boss_1",
            "name": "Lagon",
            "category": "boss",
            "health": 50000,
            "armor": 800,
            "resistances": {"fire": 40.0, "cold": 25.0},
        }
        ep = EnemyProfile.from_dict(d, data_version="1.0")
        assert ep.id == "boss_1"
        assert ep.name == "Lagon"
        assert ep.health == 50000
        assert ep.armor == 800
        assert ep.resistances["fire"] == 40.0

    def test_from_dict_defaults_optional_fields(self):
        ep = EnemyProfile.from_dict({"id": "x", "name": "X"}, data_version="1.0")
        assert ep.health == 0
        assert ep.armor == 0
        assert ep.resistances == {}
        assert ep.crit_chance == 0.0
        assert ep.crit_multiplier == 1.0
        assert ep.tags == ()

    def test_to_dict_round_trips(self):
        d = {
            "id": "goblin",
            "name": "Goblin",
            "category": "normal",
            "health": 500,
            "armor": 100,
            "resistances": {"physical": 10.0},
        }
        ep = EnemyProfile.from_dict(d, data_version="2.0")
        out = ep.to_dict()
        assert out["id"] == "goblin"
        assert out["armor"] == 100
        assert out["resistances"] == {"physical": 10.0}
        assert out["data_version"] == "2.0"

    def test_frozen_prevents_mutation(self):
        ep = _make_enemy()
        with self.assertRaises((AttributeError, TypeError)):
            ep.armor = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Enemy mitigation calculator
# ---------------------------------------------------------------------------

class TestArmorMitigation(unittest.TestCase):

    def test_zero_armor_gives_zero_mitigation(self):
        assert armor_mitigation(0) == 0.0

    def test_negative_armor_gives_zero_mitigation(self):
        assert armor_mitigation(-50) == 0.0

    def test_formula_1000_armor(self):
        # 1000 / (1000 + 1000) = 0.5
        assert math.isclose(armor_mitigation(1000), 0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_formula_500_armor(self):
        # 500 / (500 + 1000) = 1/3
        assert math.isclose(armor_mitigation(500), 1.0 / 3.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_higher_armor_gives_higher_mitigation(self):
        assert armor_mitigation(2000) > armor_mitigation(1000) > armor_mitigation(0)

    def test_mitigation_below_one(self):
        # Armor can never fully absorb damage
        assert armor_mitigation(999_999) < 1.0

    def test_extreme_armor_approaches_one(self):
        # Asymptotic saturation: 1_000_000 / (1_000_000 + 1000) ≈ 0.999001
        # Must be < 1.0 (never full absorption) and > 0.999 (saturating).
        mit = armor_mitigation(1_000_000)
        assert mit < 1.0
        assert mit > 0.999

    def test_formula_2000_armor(self):
        # 2000 / (2000 + 1000) = 2/3
        assert math.isclose(armor_mitigation(2000), 2.0 / 3.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_formula_3000_armor(self):
        # 3000 / (3000 + 1000) = 3/4 = 0.75
        assert math.isclose(armor_mitigation(3000), 0.75, rel_tol=1e-9, abs_tol=1e-12)

    def test_formula_general(self):
        # For any armor a > 0: mitigation = a / (a + 1000)
        for a in (100, 250, 750, 1500, 4000):
            expected = a / (a + 1000)
            assert math.isclose(armor_mitigation(a), expected, rel_tol=1e-9, abs_tol=1e-12)


class TestApplyArmor(unittest.TestCase):
    """
    Deterministic tests for apply_armor(damage, armor).

    Each case uses a round damage value and a breakpoint armor value so the
    expected post-armor damage is exactly computable.
    """

    def test_zero_armor_passes_full_damage(self):
        assert apply_armor(100.0, 0) == 100.0

    def test_1000_armor_halves_damage(self):
        # mitigation = 0.5 → 100 × 0.5 = 50
        assert math.isclose(apply_armor(100.0, 1000), 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_2000_armor_reduces_to_one_third(self):
        # mitigation = 2/3 → 300 × (1 - 2/3) = 100
        assert math.isclose(apply_armor(300.0, 2000), 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_3000_armor_reduces_to_one_quarter(self):
        # mitigation = 3/4 → 200 × 0.25 = 50
        assert math.isclose(apply_armor(200.0, 3000), 50.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_500_armor_reduces_to_two_thirds(self):
        # mitigation = 1/3 → 150 × (2/3) = 100
        assert math.isclose(apply_armor(150.0, 500), 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_negative_armor_is_same_as_zero(self):
        # Negative armor treated as 0 — no buff to damage.
        assert math.isclose(apply_armor(100.0, -200), 100.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_result_never_exceeds_input(self):
        # Post-armor damage is always ≤ raw damage.
        for armor in (0, 100, 500, 1000, 5000):
            assert apply_armor(100.0, armor) <= 100.0

    def test_result_always_positive(self):
        # Even extreme armor cannot produce zero or negative damage.
        assert apply_armor(1.0, 1_000_000) > 0.0

    def test_extreme_armor_never_reaches_full_block(self):
        # 1_000_000 armor: mitigation = 1_000_000 / 1_001_000 ≈ 0.999001
        # Remaining damage ≈ 0.0999 — well above zero, well below 0.1% of input.
        # Guards against overflow/rounding causing full absorption in Monte Carlo.
        damage = 100.0
        result = apply_armor(damage, 1_000_000)
        assert result > 0
        assert result < damage * 0.001


class TestPenetrationMechanics(unittest.TestCase):
    """
    Deterministic tests for penetration logic.

    Penetration subtracts from the enemy's CAPPED resistance.
    It cannot push effective resistance below 0 (no damage amplification).
    """

    # --- apply_penetration (pure function) ---

    def test_partial_penetration_reduces_resistance(self):
        assert math.isclose(apply_penetration(40.0, 15.0), 25.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_full_penetration_reaches_zero(self):
        assert apply_penetration(30.0, 30.0) == 0.0

    def test_over_penetration_floors_at_zero(self):
        # More pen than resistance → 0%, not negative (no damage bonus).
        assert apply_penetration(20.0, 50.0) == 0.0

    def test_penetration_on_zero_resistance(self):
        # 0% base res + any pen → still 0%.
        assert apply_penetration(0.0, 25.0) == 0.0

    def test_zero_penetration_leaves_resistance_unchanged(self):
        assert apply_penetration(55.0, 0.0) == 55.0

    # --- effective_resistance — ordering: cap THEN pen ---

    def test_cap_applies_before_penetration(self):
        # 90% raw res → capped to 75% first → 20% pen → 55% effective.
        # Wrong order (pen first): min(75, 90−20) = 70.
        enemy = _make_enemy(resistances={"fire": 90.0})
        eff = effective_resistance(enemy, "fire", penetration=20.0)
        assert math.isclose(eff, 55.0, rel_tol=1e-9, abs_tol=1e-12)
        # Explicitly confirm the wrong answer is not returned.
        assert not math.isclose(eff, 70.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_pen_on_uncapped_resistance(self):
        # 40% raw res (below cap), 15% pen → 25% effective.
        enemy = _make_enemy(resistances={"cold": 40.0})
        assert math.isclose(effective_resistance(enemy, "cold", 15.0), 25.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_pen_exceeds_capped_resistance(self):
        # 90% raw res → 75% capped; 90% pen → max(0, 75−90) = 0.
        enemy = _make_enemy(resistances={"fire": 90.0})
        assert effective_resistance(enemy, "fire", penetration=90.0) == 0.0

    def test_pen_on_missing_resistance_stays_zero(self):
        enemy = _make_enemy(resistances={})
        assert effective_resistance(enemy, "void", penetration=30.0) == 0.0

    # --- Integration: penetration through damage_multiplier ---

    def test_pen_increases_damage_multiplier(self):
        enemy = _make_enemy(armor=0, resistances={"fire": 50.0})
        without = enemy_damage_multiplier(enemy, {"fire"})
        with_pen = enemy_damage_multiplier(enemy, {"fire"}, pen_map={"fire": 25.0})
        assert with_pen > without

    def test_full_pen_gives_multiplier_one(self):
        # 0 armor, 40% fire res, 40% pen → effective res=0 → multiplier=1.0
        enemy = _make_enemy(armor=0, resistances={"fire": 40.0})
        mult = enemy_damage_multiplier(enemy, {"fire"}, pen_map={"fire": 40.0})
        assert math.isclose(mult, 1.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_pen_in_weighted_multiplier(self):
        # 100% fire, 60% fire res, 30% pen → eff res=30 → mult=0.7
        enemy = _make_enemy(armor=0, resistances={"fire": 60.0})
        damage_by_type = {DamageType.FIRE: 100.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type, pen_map={"fire": 30.0})
        assert math.isclose(mult, 0.70, rel_tol=1e-9, abs_tol=1e-12)

    def test_penetration_equals_cap(self):
        # 75% fire res (exactly at RES_CAP), 75% pen → eff res = max(0, 75-75) = 0.
        # Multiplier must be exactly 1.0 — boundary subtraction must not round.
        enemy = _make_enemy(armor=0, resistances={"fire": 75.0})
        damage_by_type = {DamageType.FIRE: 100.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type, pen_map={"fire": 75.0})
        assert math.isclose(mult, 1.0, rel_tol=1e-9, abs_tol=1e-12)


class TestEffectiveResistance(unittest.TestCase):

    def test_zero_resistance_zero_pen(self):
        ep = _make_enemy(resistances={"fire": 0.0})
        assert effective_resistance(ep, "fire") == 0.0

    def test_base_resistance_no_pen(self):
        ep = _make_enemy(resistances={"fire": 40.0})
        assert math.isclose(effective_resistance(ep, "fire"), 40.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_penetration_reduces_resistance(self):
        ep = _make_enemy(resistances={"fire": 40.0})
        assert math.isclose(effective_resistance(ep, "fire", penetration=15.0), 25.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_resistance_capped_at_res_cap(self):
        ep = _make_enemy(resistances={"fire": 90.0})
        assert math.isclose(effective_resistance(ep, "fire"), RES_CAP, rel_tol=1e-9, abs_tol=1e-12)

    def test_penetration_cannot_go_below_zero(self):
        ep = _make_enemy(resistances={"fire": 10.0})
        # More penetration than resistance → clamp to 0
        assert effective_resistance(ep, "fire", penetration=50.0) == 0.0

    def test_unknown_damage_type_defaults_zero(self):
        ep = _make_enemy(resistances={})
        assert effective_resistance(ep, "void") == 0.0


class TestEnemyDamageMultiplier(unittest.TestCase):

    def test_training_dummy_multiplier_is_one(self):
        # 0 armor, 0 resistance → full damage passes through
        dummy = _make_enemy(armor=0, resistances={"fire": 0.0})
        mult = enemy_damage_multiplier(dummy, {"fire"})
        assert math.isclose(mult, 1.0, rel_tol=1e-9, abs_tol=1e-12)

    def test_armor_only_reduces_multiplier(self):
        # 1000 armor → 50% mitigation → multiplier = 0.5
        enemy = _make_enemy(armor=1000, resistances={"physical": 0.0})
        mult = enemy_damage_multiplier(enemy, {"physical"})
        assert math.isclose(mult, 0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_resistance_only_reduces_multiplier(self):
        # 0 armor, 50% fire res → multiplier = 0.5
        enemy = _make_enemy(armor=0, resistances={"fire": 50.0})
        mult = enemy_damage_multiplier(enemy, {"fire"})
        assert math.isclose(mult, 0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_armor_and_resistance_stack_multiplicatively(self):
        # 1000 armor (50% mit) × 50% fire res → 0.5 × 0.5 = 0.25
        enemy = _make_enemy(armor=1000, resistances={"fire": 50.0})
        mult = enemy_damage_multiplier(enemy, {"fire"})
        assert math.isclose(mult, 0.25, rel_tol=1e-9, abs_tol=1e-12)

    def test_penetration_improves_multiplier(self):
        enemy = _make_enemy(armor=0, resistances={"fire": 40.0})
        without_pen = enemy_damage_multiplier(enemy, {"fire"})
        with_pen    = enemy_damage_multiplier(enemy, {"fire"}, pen_map={"fire": 20.0})
        assert with_pen > without_pen

    def test_empty_damage_types_uses_armor_only(self):
        enemy = _make_enemy(armor=1000, resistances={"fire": 50.0})
        mult = enemy_damage_multiplier(enemy, set())
        # No resistance applied — only armor
        assert math.isclose(mult, 0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_multi_type_resistance_is_averaged(self):
        # fire=0%, cold=100% (capped to 75%) → avg = 37.5% → mult = 0.625
        enemy = _make_enemy(armor=0, resistances={"fire": 0.0, "cold": 100.0})
        mult = enemy_damage_multiplier(enemy, {"fire", "cold"})
        expected_avg_res = (0.0 + 75.0) / 2.0   # 37.5%
        expected_mult = 1.0 - expected_avg_res / 100.0
        assert math.isclose(mult, expected_mult, rel_tol=1e-9, abs_tol=1e-12)


class TestWeightedDamageMultiplier(unittest.TestCase):
    """
    Tests for weighted_damage_multiplier — resistance applied proportionally
    to actual per-type damage amounts rather than equally across all types.
    """

    def test_equal_split_matches_unweighted(self):
        # When both types contribute equally, weighted == unweighted.
        enemy = _make_enemy(armor=0, resistances={"physical": 0.0, "fire": 40.0})
        damage_by_type = {DamageType.PHYSICAL: 50.0, DamageType.FIRE: 50.0}
        weighted = weighted_damage_multiplier(enemy, damage_by_type)
        unweighted = enemy_damage_multiplier(enemy, {"physical", "fire"})
        assert math.isclose(weighted, unweighted, rel_tol=1e-9, abs_tol=1e-12)

    def test_unequal_split_differs_from_unweighted(self):
        # 90% physical (0% res), 10% fire (75% res).
        # Weighted: 0.9×1.0 + 0.1×0.25 = 0.925
        # Unweighted average: (0 + 75)/2 = 37.5% → 0.625
        enemy = _make_enemy(armor=0, resistances={"physical": 0.0, "fire": 75.0})
        damage_by_type = {DamageType.PHYSICAL: 90.0, DamageType.FIRE: 10.0}
        weighted = weighted_damage_multiplier(enemy, damage_by_type)
        assert math.isclose(weighted, 0.925, rel_tol=1e-9, abs_tol=1e-12)

    def test_unequal_split_exact_formula(self):
        # p=phys amount, f=fire amount, total=p+f
        # res_factor = (p/total)×(1-phys_res/100) + (f/total)×(1-fire_res/100)
        enemy = _make_enemy(armor=0, resistances={"physical": 20.0, "fire": 60.0})
        p, f = 60.0, 40.0
        total = p + f
        damage_by_type = {DamageType.PHYSICAL: p, DamageType.FIRE: f}
        weighted = weighted_damage_multiplier(enemy, damage_by_type)
        expected = (p / total) * (1 - 20.0 / 100.0) + (f / total) * (1 - 60.0 / 100.0)
        assert math.isclose(weighted, expected, rel_tol=1e-9, abs_tol=1e-12)

    def test_single_type_matches_direct_resistance(self):
        # Single type: weighted == 1 - eff_res/100
        enemy = _make_enemy(armor=0, resistances={"cold": 30.0})
        damage_by_type = {DamageType.COLD: 100.0}
        weighted = weighted_damage_multiplier(enemy, damage_by_type)
        assert math.isclose(weighted, 0.70, rel_tol=1e-9, abs_tol=1e-12)

    def test_armor_applies_regardless_of_weighting(self):
        # 1000 armor (50% mit), 0% resistance on all types.
        enemy = _make_enemy(armor=1000, resistances={"fire": 0.0})
        damage_by_type = {DamageType.FIRE: 100.0}
        weighted = weighted_damage_multiplier(enemy, damage_by_type)
        assert math.isclose(weighted, 0.5, rel_tol=1e-9, abs_tol=1e-12)

    def test_empty_damage_by_type_returns_armor_only(self):
        # No per-type data → fall back to armor factor only.
        enemy = _make_enemy(armor=1000, resistances={"fire": 50.0})
        weighted = weighted_damage_multiplier(enemy, {})
        expected = 1.0 - armor_mitigation(1000)
        assert math.isclose(weighted, expected, rel_tol=1e-9, abs_tol=1e-12)

    def test_total_damage_conservation_with_high_res(self):
        # Total effective damage = raw × weighted_multiplier.
        # Verify the multiplier is in (0, 1] and damage is always reduced.
        enemy = _make_enemy(armor=200, resistances={"fire": 50.0, "cold": 30.0})
        damage_by_type = {DamageType.FIRE: 70.0, DamageType.COLD: 30.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type)
        assert 0 < mult <= 1.0
        # Should be less than 1 (some mitigation present)
        assert mult < 1.0

    def test_full_resistant_minor_type(self):
        # 90% physical (0% res) + 10% fire (75% res).
        # Weighted: 0.9×1.0 + 0.1×0.25 = 0.925 — minor fire doesn't drag total.
        # Naive average would give (0+75)/2 = 37.5% avg res → 0.625 (wrong).
        enemy = _make_enemy(armor=0, resistances={"physical": 0.0, "fire": 75.0})
        damage_by_type = {DamageType.PHYSICAL: 900.0, DamageType.FIRE: 100.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type, pen_map={})
        assert mult > 0.9
        # Also pin the exact value so regressions are obvious
        assert math.isclose(mult, 0.925, rel_tol=1e-9, abs_tol=1e-12)

    def test_weighted_multiplier_never_exceeds_one(self):
        # Zero armor + zero resistance = full damage, multiplier exactly 1.0.
        # No combination of zero mitigation should accidentally amplify damage.
        # (Resistance keys are strings; DamageType enum values are the string ids.)
        enemy = _make_enemy(
            armor=0,
            resistances={"fire": 0.0, "cold": 0.0},
        )
        damage_by_type = {DamageType.FIRE: 100.0, DamageType.COLD: 50.0}
        mult = weighted_damage_multiplier(enemy, damage_by_type, pen_map={})
        assert mult <= 1.0
        # With zero mitigation the multiplier should be exactly 1.0
        assert math.isclose(mult, 1.0, rel_tol=1e-9, abs_tol=1e-12)


if __name__ == '__main__':
    unittest.main()
