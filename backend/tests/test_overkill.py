"""Tests for Damage Overkill Handling (Step 74)."""
import pytest
from app.domain.overkill import overkill_amount, apply_overkill_bonus


class TestOverkillAmount:
    def test_no_overkill(self):
        assert overkill_amount(50.0, 100.0) == pytest.approx(0.0)

    def test_exact_kill_no_overkill(self):
        assert overkill_amount(100.0, 100.0) == pytest.approx(0.0)

    def test_overkill(self):
        assert overkill_amount(150.0, 100.0) == pytest.approx(50.0)

    def test_zero_health_all_overkill(self):
        assert overkill_amount(100.0, 0.0) == pytest.approx(100.0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError):
            overkill_amount(-10.0, 100.0)

    def test_negative_health_raises(self):
        with pytest.raises(ValueError):
            overkill_amount(100.0, -1.0)


class TestApplyOverkillBonus:
    def test_zero_pct_no_bonus(self):
        assert apply_overkill_bonus(100.0, 0.0, 50.0) == pytest.approx(100.0)

    def test_100pct_adds_full_overkill(self):
        assert apply_overkill_bonus(100.0, 100.0, 50.0) == pytest.approx(150.0)

    def test_50pct_adds_half_overkill(self):
        assert apply_overkill_bonus(100.0, 50.0, 80.0) == pytest.approx(140.0)

    def test_zero_overkill_no_bonus(self):
        assert apply_overkill_bonus(100.0, 100.0, 0.0) == pytest.approx(100.0)

    def test_above_100pct_clamped(self):
        assert apply_overkill_bonus(100.0, 200.0, 50.0) == pytest.approx(150.0)

    def test_negative_base_raises(self):
        with pytest.raises(ValueError):
            apply_overkill_bonus(-10.0, 50.0, 20.0)
