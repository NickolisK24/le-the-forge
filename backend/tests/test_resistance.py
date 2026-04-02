"""
Tests for Resistance System (Step 61).
"""

import pytest
from app.domain.resistance import apply_resistance, apply_resistance_map, RES_CAP, RES_MIN
from app.domain.calculators.damage_type_router import DamageType


class TestApplyResistance:
    def test_zero_resistance_no_reduction(self):
        assert apply_resistance(100.0, 0.0) == pytest.approx(100.0)

    def test_50pct_resistance_halves_damage(self):
        assert apply_resistance(100.0, 50.0) == pytest.approx(50.0)

    def test_75pct_resistance_at_cap(self):
        assert apply_resistance(100.0, 75.0) == pytest.approx(25.0)

    def test_resistance_above_cap_clamped(self):
        assert apply_resistance(100.0, 100.0) == pytest.approx(25.0)

    def test_resistance_at_res_cap_constant(self):
        assert apply_resistance(200.0, RES_CAP) == pytest.approx(50.0)

    def test_negative_resistance_increases_damage(self):
        # -25% resistance → 125% damage taken
        assert apply_resistance(100.0, -25.0) == pytest.approx(125.0)

    def test_negative_resistance_clamped_at_min(self):
        # -200% clamped to -100% → 200% damage taken
        assert apply_resistance(100.0, -200.0) == pytest.approx(200.0)

    def test_res_min_boundary(self):
        assert apply_resistance(100.0, RES_MIN) == pytest.approx(200.0)

    def test_zero_damage_stays_zero(self):
        assert apply_resistance(0.0, 50.0) == pytest.approx(0.0)

    def test_negative_raw_damage_raises(self):
        with pytest.raises(ValueError, match="raw_damage"):
            apply_resistance(-1.0, 0.0)

    def test_25pct_resistance(self):
        assert apply_resistance(200.0, 25.0) == pytest.approx(150.0)

    def test_full_damage_at_zero_resistance(self):
        assert apply_resistance(500.0, 0.0) == pytest.approx(500.0)


class TestApplyResistanceMap:
    def test_single_type_no_resistance(self):
        dm = {DamageType.FIRE: 100.0}
        result = apply_resistance_map(dm, {})
        assert result[DamageType.FIRE] == pytest.approx(100.0)

    def test_single_type_with_resistance(self):
        dm  = {DamageType.FIRE: 100.0}
        rm  = {DamageType.FIRE: 50.0}
        result = apply_resistance_map(dm, rm)
        assert result[DamageType.FIRE] == pytest.approx(50.0)

    def test_multiple_types_independent(self):
        dm = {DamageType.FIRE: 100.0, DamageType.COLD: 80.0, DamageType.PHYSICAL: 60.0}
        rm = {DamageType.FIRE: 25.0, DamageType.COLD: 50.0, DamageType.PHYSICAL: 0.0}
        result = apply_resistance_map(dm, rm)
        assert result[DamageType.FIRE]     == pytest.approx(75.0)
        assert result[DamageType.COLD]     == pytest.approx(40.0)
        assert result[DamageType.PHYSICAL] == pytest.approx(60.0)

    def test_missing_type_treated_as_zero_resistance(self):
        dm = {DamageType.LIGHTNING: 100.0}
        result = apply_resistance_map(dm, {})
        assert result[DamageType.LIGHTNING] == pytest.approx(100.0)

    def test_original_maps_not_mutated(self):
        dm = {DamageType.FIRE: 100.0}
        rm = {DamageType.FIRE: 50.0}
        apply_resistance_map(dm, rm)
        assert dm[DamageType.FIRE] == pytest.approx(100.0)
        assert rm[DamageType.FIRE] == pytest.approx(50.0)

    def test_empty_damage_map_returns_empty(self):
        result = apply_resistance_map({}, {DamageType.FIRE: 75.0})
        assert result == {}

    def test_negative_resistance_in_map(self):
        dm = {DamageType.VOID: 100.0}
        rm = {DamageType.VOID: -50.0}
        result = apply_resistance_map(dm, rm)
        assert result[DamageType.VOID] == pytest.approx(150.0)
