"""
Tests for Resistance Shred Mechanics (Step 5).

Validates:
  - apply_resistance_shred reduces resistance per type
  - Negative values (vulnerability) are allowed and clamped at -RES_CAP
  - Absent types default to 0.0 base before shred
  - Types absent from shred_map are unchanged
  - shred_damage_multiplier returns correct multipliers (>1 for vulnerable)
  - effective_shredded_resistance convenience function
"""

import pytest
from app.constants.defense import RES_CAP
from app.domain.resistance_shred import (
    apply_resistance_shred,
    shred_damage_multiplier,
    effective_shredded_resistance,
)


# ---------------------------------------------------------------------------
# apply_resistance_shred
# ---------------------------------------------------------------------------

class TestApplyResistanceShred:
    def test_basic_shred_reduces_resistance(self):
        resistances = {"fire": 50.0, "cold": 25.0}
        result = apply_resistance_shred(resistances, {"fire": 20.0})
        assert result["fire"] == pytest.approx(30.0)

    def test_unshredded_type_unchanged(self):
        resistances = {"fire": 50.0, "cold": 25.0}
        result = apply_resistance_shred(resistances, {"fire": 20.0})
        assert result["cold"] == pytest.approx(25.0)

    def test_shred_absent_type_starts_at_zero(self):
        resistances = {"fire": 50.0}
        result = apply_resistance_shred(resistances, {"void": 30.0})
        assert result["void"] == pytest.approx(-30.0)

    def test_shred_to_zero(self):
        resistances = {"fire": 25.0}
        result = apply_resistance_shred(resistances, {"fire": 25.0})
        assert result["fire"] == pytest.approx(0.0)

    def test_shred_into_negative_vulnerability(self):
        resistances = {"fire": 25.0}
        result = apply_resistance_shred(resistances, {"fire": 50.0})
        assert result["fire"] == pytest.approx(-25.0)

    def test_shred_clamped_at_negative_res_cap(self):
        resistances = {"fire": 0.0}
        result = apply_resistance_shred(resistances, {"fire": 200.0})
        assert result["fire"] == pytest.approx(-float(RES_CAP))

    def test_shred_high_base_also_clamped(self):
        resistances = {"fire": 10.0}
        result = apply_resistance_shred(resistances, {"fire": 1000.0})
        assert result["fire"] == pytest.approx(-float(RES_CAP))

    def test_empty_shred_map_unchanged(self):
        resistances = {"fire": 50.0, "cold": 30.0}
        result = apply_resistance_shred(resistances, {})
        assert result == resistances

    def test_empty_resistances_with_shred(self):
        result = apply_resistance_shred({}, {"fire": 20.0})
        assert result["fire"] == pytest.approx(-20.0)

    def test_original_dict_not_mutated(self):
        resistances = {"fire": 50.0}
        original_value = resistances["fire"]
        apply_resistance_shred(resistances, {"fire": 20.0})
        assert resistances["fire"] == original_value

    def test_multiple_types_shredded(self):
        resistances = {"fire": 60.0, "cold": 40.0, "void": 25.0}
        result = apply_resistance_shred(
            resistances, {"fire": 20.0, "cold": 40.0, "void": 10.0}
        )
        assert result["fire"] == pytest.approx(40.0)
        assert result["cold"] == pytest.approx(0.0)
        assert result["void"] == pytest.approx(15.0)

    def test_returns_new_dict(self):
        resistances = {"fire": 50.0}
        result = apply_resistance_shred(resistances, {"fire": 10.0})
        assert result is not resistances


# ---------------------------------------------------------------------------
# shred_damage_multiplier
# ---------------------------------------------------------------------------

class TestShredDamageMultiplier:
    def test_full_resistance_no_shred(self):
        # 75% resistance, no shred → multiplier = 1 - 0.75 = 0.25
        mult = shred_damage_multiplier(75.0, 0.0)
        assert mult == pytest.approx(0.25)

    def test_zero_resistance_no_shred(self):
        # 0% resistance → multiplier = 1.0
        mult = shred_damage_multiplier(0.0, 0.0)
        assert mult == pytest.approx(1.0)

    def test_partial_shred(self):
        # 50% resistance, 30 shred → eff=20% → multiplier=0.80
        mult = shred_damage_multiplier(50.0, 30.0)
        assert mult == pytest.approx(0.80)

    def test_shred_to_zero_gives_multiplier_one(self):
        mult = shred_damage_multiplier(25.0, 25.0)
        assert mult == pytest.approx(1.0)

    def test_shred_into_vulnerability(self):
        # 25% resistance, 50 shred → eff=-25% → multiplier=1.25
        mult = shred_damage_multiplier(25.0, 50.0)
        assert mult == pytest.approx(1.25)

    def test_shred_capped_vulnerability(self):
        # 0% resistance, 200 shred → eff=-75 (clamped) → multiplier=1.75
        mult = shred_damage_multiplier(0.0, 200.0)
        assert mult == pytest.approx(1.75)

    def test_multiplier_greater_than_one_when_vulnerable(self):
        mult = shred_damage_multiplier(10.0, 50.0)
        assert mult > 1.0

    def test_multiplier_at_most_1_75(self):
        # Maximum vulnerability = -RES_CAP = -75 → 1 - (-75/100) = 1.75
        mult = shred_damage_multiplier(0.0, 10000.0)
        assert mult == pytest.approx(1.75)


# ---------------------------------------------------------------------------
# effective_shredded_resistance
# ---------------------------------------------------------------------------

class TestEffectiveShreeddedResistance:
    def test_basic_lookup(self):
        resistances = {"fire": 50.0}
        eff = effective_shredded_resistance(resistances, {"fire": 20.0}, "fire")
        assert eff == pytest.approx(30.0)

    def test_type_not_in_resistances_defaults_zero_minus_shred(self):
        eff = effective_shredded_resistance({}, {"void": 30.0}, "void")
        assert eff == pytest.approx(-30.0)

    def test_type_not_shredded_returns_base(self):
        resistances = {"fire": 50.0, "cold": 25.0}
        eff = effective_shredded_resistance(resistances, {"fire": 10.0}, "cold")
        assert eff == pytest.approx(25.0)

    def test_type_absent_from_both_returns_zero(self):
        eff = effective_shredded_resistance({}, {}, "lightning")
        assert eff == pytest.approx(0.0)

    def test_vulnerability_value(self):
        resistances = {"fire": 10.0}
        eff = effective_shredded_resistance(resistances, {"fire": 40.0}, "fire")
        assert eff == pytest.approx(-30.0)
