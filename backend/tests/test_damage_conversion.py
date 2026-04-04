"""
Tests for Damage Type Conversion System (Step 58).

Validates:
  - ConversionRule construction and validation
  - No rules leaves damage map unchanged
  - Partial conversion splits source correctly
  - Full 100% conversion moves all damage to target
  - Multiple rules on different sources are independent
  - Two rules on the same source are additive (cap at 100%)
  - Over-100% total from same source is scaled proportionally
  - Converted amount adds to existing target damage
  - Zero-amount source is ignored
  - Rule order does not affect result
  - Negative conversion_pct raises ValueError
  - Source == target raises ValueError
"""

import pytest
from app.domain.damage_conversion import ConversionRule, apply_conversions
from app.domain.calculators.damage_type_router import DamageType

P = DamageType.PHYSICAL
F = DamageType.FIRE
C = DamageType.COLD
L = DamageType.LIGHTNING


# ---------------------------------------------------------------------------
# ConversionRule construction
# ---------------------------------------------------------------------------

class TestConversionRuleConstruction:
    def test_basic_rule(self):
        r = ConversionRule(P, F, 30.0)
        assert r.source is P
        assert r.target is F
        assert r.conversion_pct == pytest.approx(30.0)

    def test_negative_pct_raises(self):
        with pytest.raises(ValueError, match="conversion_pct"):
            ConversionRule(P, F, -1.0)

    def test_zero_pct_allowed(self):
        r = ConversionRule(P, F, 0.0)
        assert r.conversion_pct == pytest.approx(0.0)

    def test_100_pct_allowed(self):
        r = ConversionRule(P, F, 100.0)
        assert r.conversion_pct == pytest.approx(100.0)

    def test_above_100_pct_allowed_in_rule(self):
        # Over-100 is clamped during apply, not at construction
        r = ConversionRule(P, F, 150.0)
        assert r.conversion_pct == pytest.approx(150.0)

    def test_source_equals_target_raises(self):
        with pytest.raises(ValueError, match="source and target"):
            ConversionRule(P, P, 50.0)


# ---------------------------------------------------------------------------
# apply_conversions — basic behaviour
# ---------------------------------------------------------------------------

class TestApplyConversionsBasic:
    def test_no_rules_returns_same_map(self):
        damage = {P: 100.0}
        result = apply_conversions(damage, [])
        assert result[P] == pytest.approx(100.0)
        assert len(result) == 1

    def test_original_map_not_mutated(self):
        damage = {P: 100.0}
        apply_conversions(damage, [ConversionRule(P, F, 30.0)])
        assert damage[P] == pytest.approx(100.0)

    def test_partial_conversion(self):
        # 30% of 100 physical → 30 fire, 70 physical remain
        result = apply_conversions({P: 100.0}, [ConversionRule(P, F, 30.0)])
        assert result[P] == pytest.approx(70.0)
        assert result[F] == pytest.approx(30.0)

    def test_full_100pct_conversion(self):
        # 100% physical → fire; physical entry removed
        result = apply_conversions({P: 100.0}, [ConversionRule(P, F, 100.0)])
        assert P not in result
        assert result[F] == pytest.approx(100.0)

    def test_zero_pct_rule_no_change(self):
        result = apply_conversions({P: 100.0}, [ConversionRule(P, F, 0.0)])
        assert result[P] == pytest.approx(100.0)
        assert F not in result

    def test_source_not_in_map_ignored(self):
        # Rule references PHYSICAL but map has only FIRE
        result = apply_conversions({F: 80.0}, [ConversionRule(P, C, 50.0)])
        assert result[F] == pytest.approx(80.0)
        assert C not in result

    def test_converted_amount_added_to_existing_target(self):
        # 50 base fire, plus 30% of 100 physical → fire = 50 + 30 = 80
        damage = {P: 100.0, F: 50.0}
        result = apply_conversions(damage, [ConversionRule(P, F, 30.0)])
        assert result[P] == pytest.approx(70.0)
        assert result[F] == pytest.approx(80.0)


# ---------------------------------------------------------------------------
# apply_conversions — multiple sources
# ---------------------------------------------------------------------------

class TestApplyConversionsMultipleSources:
    def test_two_different_sources_independent(self):
        damage = {P: 100.0, C: 80.0}
        rules = [ConversionRule(P, F, 50.0), ConversionRule(C, L, 25.0)]
        result = apply_conversions(damage, rules)
        assert result[P] == pytest.approx(50.0)
        assert result[F] == pytest.approx(50.0)
        assert result[C] == pytest.approx(60.0)
        assert result[L] == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# apply_conversions — same source, multiple rules
# ---------------------------------------------------------------------------

class TestSameSourceMultipleRules:
    def test_two_rules_additive_under_100(self):
        # 30% → fire + 20% → cold = 50% total; 50% physical remains
        damage = {P: 100.0}
        rules = [ConversionRule(P, F, 30.0), ConversionRule(P, C, 20.0)]
        result = apply_conversions(damage, rules)
        assert result[P] == pytest.approx(50.0)
        assert result[F] == pytest.approx(30.0)
        assert result[C] == pytest.approx(20.0)

    def test_two_rules_exactly_100(self):
        # 60% → fire + 40% → cold = 100%; nothing remains
        damage = {P: 100.0}
        rules = [ConversionRule(P, F, 60.0), ConversionRule(P, C, 40.0)]
        result = apply_conversions(damage, rules)
        assert P not in result
        assert result[F] == pytest.approx(60.0)
        assert result[C] == pytest.approx(40.0)

    def test_over_100_pct_total_scaled_proportionally(self):
        # 60% → fire + 60% → cold = 120% total → scaled to 50% each
        # fire = 100 * 0.5 = 50; cold = 100 * 0.5 = 50; physical = 0
        damage = {P: 100.0}
        rules = [ConversionRule(P, F, 60.0), ConversionRule(P, C, 60.0)]
        result = apply_conversions(damage, rules)
        assert result.get(P, 0.0) == pytest.approx(0.0, abs=1e-9)
        assert result[F] == pytest.approx(50.0)
        assert result[C] == pytest.approx(50.0)

    def test_single_rule_over_100_clamped_to_100(self):
        # A single rule of 150% is treated as 100%
        damage = {P: 100.0}
        result = apply_conversions(damage, [ConversionRule(P, F, 150.0)])
        assert P not in result
        assert result[F] == pytest.approx(100.0)

    def test_over_100_three_rules_proportional(self):
        # 50 + 50 + 50 = 150% → scale each to 33.33%
        damage = {P: 300.0}
        rules = [
            ConversionRule(P, F, 50.0),
            ConversionRule(P, C, 50.0),
            ConversionRule(P, L, 50.0),
        ]
        result = apply_conversions(damage, rules)
        assert result.get(P, 0.0) == pytest.approx(0.0, abs=1e-6)
        assert result[F] == pytest.approx(100.0, rel=1e-4)
        assert result[C] == pytest.approx(100.0, rel=1e-4)
        assert result[L] == pytest.approx(100.0, rel=1e-4)


# ---------------------------------------------------------------------------
# Rule order independence
# ---------------------------------------------------------------------------

class TestRuleOrderIndependence:
    def test_two_rules_same_result_regardless_of_order(self):
        damage = {P: 100.0}
        rules_ab = [ConversionRule(P, F, 30.0), ConversionRule(P, C, 20.0)]
        rules_ba = [ConversionRule(P, C, 20.0), ConversionRule(P, F, 30.0)]
        result_ab = apply_conversions(damage, rules_ab)
        result_ba = apply_conversions(damage, rules_ba)
        assert result_ab[P] == pytest.approx(result_ba[P])
        assert result_ab[F] == pytest.approx(result_ba[F])
        assert result_ab[C] == pytest.approx(result_ba[C])
