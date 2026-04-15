"""
Tests for Armor & Mitigation System.

Last Epoch formula: DR% = Armor / (Armor + 10 × AreaLevel)
Physical cap: 85%. Non-physical: armor at 75% effectiveness (cap ~63.75%).
"""

import pytest
from app.domain.armor import (
    apply_armor,
    armor_mitigation_pct,
    ARMOR_K,
    ARMOR_MITIGATION_CAP,
)
from app.constants.defense import ARMOR_NON_PHYSICAL_EFFECTIVENESS


class TestArmorMitigationPct:
    def test_zero_armor_no_mitigation(self):
        assert armor_mitigation_pct(0.0, 100) == pytest.approx(0.0)

    def test_positive_armor_area_level_100(self):
        # armor=1000, area_level=100 → 1000 / (1000 + 10*100) = 1000/2000 = 0.5
        result = armor_mitigation_pct(1000.0, 100)
        assert result == pytest.approx(0.5)

    def test_mitigation_capped_at_85pct(self):
        # Very high armor → should cap at 0.85
        assert armor_mitigation_pct(1_000_000.0, 100) == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_mitigation_never_exceeds_cap(self):
        assert armor_mitigation_pct(999_999.0, 1) <= ARMOR_MITIGATION_CAP

    def test_zero_area_level_returns_cap(self):
        assert armor_mitigation_pct(500.0, 0) == pytest.approx(ARMOR_MITIGATION_CAP)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError, match="armor"):
            armor_mitigation_pct(-1.0, 100)

    def test_higher_area_level_reduces_mitigation(self):
        # Same armor, higher area level → lower mitigation
        low_level = armor_mitigation_pct(500.0, 50)
        high_level = armor_mitigation_pct(500.0, 200)
        assert low_level > high_level

    def test_higher_armor_increases_mitigation(self):
        low = armor_mitigation_pct(100.0, 100)
        high = armor_mitigation_pct(500.0, 100)
        assert high > low

    def test_formula_exact(self):
        # armor=500, area_level=50 → 500/(500+500) = 0.5
        assert armor_mitigation_pct(500.0, 50) == pytest.approx(0.5)

    def test_non_physical_70pct_effectiveness(self):
        # VERIFIED: 1.4.3 spec §3.1 — armour is 70% effective vs non-physical
        # Non-physical: effective_armor = 1000 * 0.70 = 700
        # 700 / (700 + 1000) = 700/1700 ≈ 0.4118
        result = armor_mitigation_pct(1000.0, 100, physical=False)
        expected = 700.0 / (700.0 + 1000.0)
        assert result == pytest.approx(expected)

    def test_non_physical_cap_is_lower(self):
        # Non-physical cap = 85% × 70% = 59.5%
        result = armor_mitigation_pct(1_000_000.0, 100, physical=False)
        assert result == pytest.approx(ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS)

    def test_armor_1000_area_100_is_50pct(self):
        """Canonical benchmark: 1000 armor at area level 100 = 50% DR."""
        assert armor_mitigation_pct(1000.0, 100) == pytest.approx(0.5)


class TestApplyArmor:
    def test_zero_armor_no_reduction(self):
        assert apply_armor(100.0, 0.0) == pytest.approx(100.0)

    def test_high_armor_reduces_damage(self):
        result = apply_armor(100.0, 500.0)
        assert result < 100.0

    def test_damage_floored_above_15pct(self):
        # Extreme armor can't reduce below 15% of raw (cap=85%)
        result = apply_armor(100.0, 1_000_000.0)
        assert result == pytest.approx(15.0)

    def test_zero_damage_stays_zero(self):
        assert apply_armor(0.0, 500.0) == pytest.approx(0.0)

    def test_negative_raw_damage_raises(self):
        with pytest.raises(ValueError, match="raw_damage"):
            apply_armor(-10.0, 100.0)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError, match="armor"):
            apply_armor(100.0, -50.0)

    def test_exact_formula(self):
        # armor=1000, area_level=100: mit=1000/(1000+1000)=0.5 → effective=50.0
        assert apply_armor(100.0, 1000.0) == pytest.approx(50.0)

    def test_small_armor_low_mitigation(self):
        # armor=10, area_level=100: mit=10/(10+1000)≈0.0099
        result = apply_armor(1000.0, 10.0)
        expected = 1000.0 * (1 - 10.0 / (10.0 + 10.0 * 100.0))
        assert result == pytest.approx(expected)
