"""
Tests for Armor & Mitigation System (Step 62).
"""

import pytest
from app.domain.armor import (
    apply_armor,
    armor_mitigation_pct,
    ARMOR_K,
    ARMOR_MITIGATION_CAP,
)


class TestArmorMitigationPct:
    def test_zero_armor_no_mitigation(self):
        assert armor_mitigation_pct(0.0, 100.0) == pytest.approx(0.0)

    def test_positive_armor_positive_damage(self):
        # armor=100, dmg=10, K=10 → 100 / (100 + 100) = 0.5
        result = armor_mitigation_pct(100.0, 10.0)
        assert result == pytest.approx(100.0 / (100.0 + ARMOR_K * 10.0))

    def test_mitigation_capped_at_75pct(self):
        # Very high armor relative to damage → should cap at 0.75
        assert armor_mitigation_pct(1_000_000.0, 1.0) == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_mitigation_never_exceeds_cap(self):
        assert armor_mitigation_pct(999_999.0, 0.001) <= ARMOR_MITIGATION_CAP

    def test_zero_damage_returns_cap(self):
        assert armor_mitigation_pct(500.0, 0.0) == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_negative_damage_returns_cap(self):
        assert armor_mitigation_pct(500.0, -10.0) == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError, match="armor"):
            armor_mitigation_pct(-1.0, 100.0)

    def test_higher_damage_reduces_mitigation(self):
        # Same armor, larger hit → lower mitigation %
        low  = armor_mitigation_pct(200.0, 10.0)
        high = armor_mitigation_pct(200.0, 1000.0)
        assert low > high

    def test_higher_armor_increases_mitigation(self):
        low  = armor_mitigation_pct(100.0, 100.0)
        high = armor_mitigation_pct(500.0, 100.0)
        assert high > low

    def test_formula_exact(self):
        # armor=200, dmg=20, K=10 → 200/(200+200)=0.5
        assert armor_mitigation_pct(200.0, 20.0) == pytest.approx(0.5)


class TestApplyArmor:
    def test_zero_armor_no_reduction(self):
        assert apply_armor(100.0, 0.0) == pytest.approx(100.0)

    def test_high_armor_reduces_damage(self):
        result = apply_armor(100.0, 500.0)
        assert result < 100.0

    def test_damage_floored_above_zero(self):
        # Even extreme armor can't reduce below 25% of raw (cap=75%)
        result = apply_armor(100.0, 1_000_000.0)
        assert result == pytest.approx(25.0)

    def test_zero_damage_stays_zero(self):
        assert apply_armor(0.0, 500.0) == pytest.approx(0.0)

    def test_negative_raw_damage_raises(self):
        with pytest.raises(ValueError, match="raw_damage"):
            apply_armor(-10.0, 100.0)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError, match="armor"):
            apply_armor(100.0, -50.0)

    def test_exact_formula(self):
        # armor=100, dmg=10: mit=100/(100+100)=0.5 → effective=5.0
        assert apply_armor(10.0, 100.0) == pytest.approx(5.0)

    def test_large_hit_small_armor_low_mitigation(self):
        # armor=10, dmg=10000: mit≈10/(10+100000)≈0.0001 → nearly full damage
        result = apply_armor(10000.0, 10.0)
        assert result == pytest.approx(10000.0 * (1 - 10.0 / (10.0 + ARMOR_K * 10000.0)))
