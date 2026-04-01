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
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.domain.calculators.stat_calculator import apply_percent_bonus, combine_additive_percents
from app.domain.calculators.more_multiplier_calculator import apply_more_multiplier
from app.domain.calculators.final_damage_calculator import DamageContext, calculate_final_damage
from app.domain.skill import SkillStatDef
from app.domain.calculators.skill_calculator import scale_skill_damage
from app.domain.calculators.damage_type_router import DamageType


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
        assert calculate_final_damage(ctx(100.0, 0.0, [])) == 100.0

    def test_increased_only(self):
        # 100 × (1 + 100/100) = 200
        assert calculate_final_damage(ctx(100.0, 100.0, [])) == 200.0

    def test_more_only(self):
        # 100 × 1.5 = 150
        assert calculate_final_damage(ctx(100.0, 0.0, [50.0])) == 150.0

    def test_increased_then_more(self):
        # Base 100, 100% increased, 50% more:
        #   100 × (1 + 100/100) × (1 + 50/100) = 100 × 2.0 × 1.5 = 300
        assert calculate_final_damage(ctx(100.0, 100.0, [50.0])) == 300.0

    def test_pipeline_order_not_additive_mixing(self):
        # If increased and more were naively added as a single pool:
        #   100 × (1 + (100 + 50)/100) = 100 × 2.5 = 250  ← WRONG
        # Correct separate-stage result is 300, not 250.
        result = calculate_final_damage(ctx(100.0, 100.0, [50.0]))
        assert result == 300.0
        assert result != 250.0

    def test_multiple_more_sources_compound_after_increased(self):
        # Base 100, 100% increased, 50% more + 20% more:
        #   100 × 2.0 × 1.5 × 1.2 = 360
        assert calculate_final_damage(ctx(100.0, 100.0, [50.0, 20.0])) == 360.0

    def test_additive_increased_pool_stacks_before_more(self):
        # Two 50% increased sources must combine additively to 100% total,
        # then a 50% more source applies multiplicatively.
        # Correct:  combine(50, 50) = 100% increased → 100 × 2.0 × 1.5 = 300
        # Wrong:    treat as two 1.5x more → 100 × 1.5 × 1.5 = 225
        total_increased = combine_additive_percents(50.0, 50.0)  # = 100.0
        result = calculate_final_damage(ctx(100.0, total_increased, [50.0]))
        assert result == 300.0
        assert result != 225.0  # would be wrong if increased sources compounded

    def test_large_realistic_values(self):
        # Simulate a realistic high-investment build:
        # Base 500, 300% increased, two 40% more sources
        # 500 × (1 + 300/100) × 1.4 × 1.4 = 500 × 4.0 × 1.96 = 3920
        result = calculate_final_damage(ctx(500.0, 300.0, [40.0, 40.0]))
        assert abs(result - 3920.0) < 0.01

    def test_zero_base_produces_zero(self):
        assert calculate_final_damage(ctx(0.0, 200.0, [50.0])) == 0.0

    def test_debug_flag_does_not_change_result(self):
        c = ctx(100.0, 100.0, [50.0])
        assert calculate_final_damage(c, debug=True) == calculate_final_damage(c, debug=False)

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

    def test_empty_damage_types_returns_empty_dict(self):
        result = scale_skill_damage(100.0, 0.10, 10, ())
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
