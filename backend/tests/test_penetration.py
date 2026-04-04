"""
Tests for Penetration & Resistance Shred (Step 64).
"""

import pytest
from app.domain.penetration import (
    apply_penetration_map,
    apply_shred,
    effective_resistance,
    MAX_SHRED_PER_TYPE,
)
from app.domain.resistance import RES_CAP, RES_MIN
from app.domain.calculators.damage_type_router import DamageType


class TestEffectiveResistance:
    def test_no_modifiers_returns_enemy_res(self):
        assert effective_resistance(50.0) == pytest.approx(50.0)

    def test_penetration_reduces_effective_res(self):
        assert effective_resistance(50.0, penetration=20.0) == pytest.approx(30.0)

    def test_shred_reduces_effective_res(self):
        assert effective_resistance(50.0, shred=15.0) == pytest.approx(35.0)

    def test_penetration_and_shred_additive(self):
        assert effective_resistance(75.0, penetration=20.0, shred=10.0) == pytest.approx(45.0)

    def test_result_clamped_at_res_cap(self):
        # Enemy has 80 res, no modifiers → clamped to 75
        assert effective_resistance(80.0) == pytest.approx(RES_CAP)

    def test_result_clamped_at_res_min(self):
        # 0 res, 200 pen → clamped to -100
        assert effective_resistance(0.0, penetration=200.0) == pytest.approx(RES_MIN)

    def test_negative_penetration_ignored(self):
        assert effective_resistance(50.0, penetration=-20.0) == pytest.approx(50.0)

    def test_negative_shred_ignored(self):
        assert effective_resistance(50.0, shred=-20.0) == pytest.approx(50.0)

    def test_zero_resistance_with_penetration(self):
        # Pen pushes to negative (vulnerability)
        assert effective_resistance(0.0, penetration=25.0) == pytest.approx(-25.0)

    def test_penetration_reduces_below_cap(self):
        # Enemy at cap (75), pen=30 → 45
        assert effective_resistance(75.0, penetration=30.0) == pytest.approx(45.0)


class TestApplyShred:
    def test_zero_plus_shred(self):
        assert apply_shred(0.0, 20.0) == pytest.approx(20.0)

    def test_accumulates_additively(self):
        shred = apply_shred(0.0, 20.0)
        shred = apply_shred(shred, 15.0)
        assert shred == pytest.approx(35.0)

    def test_capped_at_max(self):
        assert apply_shred(90.0, 50.0) == pytest.approx(MAX_SHRED_PER_TYPE)

    def test_exactly_at_max(self):
        assert apply_shred(MAX_SHRED_PER_TYPE, 10.0) == pytest.approx(MAX_SHRED_PER_TYPE)

    def test_negative_new_shred_ignored(self):
        assert apply_shred(30.0, -10.0) == pytest.approx(30.0)

    def test_negative_current_shred_raises(self):
        with pytest.raises(ValueError, match="current_shred"):
            apply_shred(-5.0, 10.0)

    def test_custom_max_shred(self):
        assert apply_shred(0.0, 200.0, max_shred=50.0) == pytest.approx(50.0)

    def test_zero_new_shred_no_change(self):
        assert apply_shred(25.0, 0.0) == pytest.approx(25.0)


class TestApplyPenetrationMap:
    def test_single_type_with_pen(self):
        result = apply_penetration_map(
            {DamageType.FIRE: 100.0},
            {DamageType.FIRE: 50.0},
            {DamageType.FIRE: 20.0},
        )
        # effective_res = 50 - 20 = 30 → damage = 100 * 0.7 = 70
        assert result[DamageType.FIRE] == pytest.approx(70.0)

    def test_single_type_with_shred(self):
        result = apply_penetration_map(
            {DamageType.COLD: 100.0},
            {DamageType.COLD: 60.0},
            {},
            shred_map={DamageType.COLD: 10.0},
        )
        # effective_res = 60 - 10 = 50 → damage = 100 * 0.5 = 50
        assert result[DamageType.COLD] == pytest.approx(50.0)

    def test_pen_and_shred_combined(self):
        result = apply_penetration_map(
            {DamageType.LIGHTNING: 100.0},
            {DamageType.LIGHTNING: 75.0},
            {DamageType.LIGHTNING: 25.0},
            shred_map={DamageType.LIGHTNING: 10.0},
        )
        # effective_res = 75 - 25 - 10 = 40 → damage = 100 * 0.6 = 60
        assert result[DamageType.LIGHTNING] == pytest.approx(60.0)

    def test_missing_pen_defaults_to_zero(self):
        result = apply_penetration_map(
            {DamageType.PHYSICAL: 100.0},
            {DamageType.PHYSICAL: 50.0},
            {},
        )
        assert result[DamageType.PHYSICAL] == pytest.approx(50.0)

    def test_missing_resistance_defaults_to_zero(self):
        result = apply_penetration_map(
            {DamageType.VOID: 100.0},
            {},
            {},
        )
        assert result[DamageType.VOID] == pytest.approx(100.0)

    def test_multiple_types_independent(self):
        result = apply_penetration_map(
            {DamageType.FIRE: 100.0, DamageType.COLD: 80.0},
            {DamageType.FIRE: 50.0, DamageType.COLD: 25.0},
            {DamageType.FIRE: 10.0},
        )
        assert result[DamageType.FIRE] == pytest.approx(60.0)   # (50-10)=40 res
        assert result[DamageType.COLD] == pytest.approx(60.0)   # 25 res
