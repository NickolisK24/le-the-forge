"""Tests for Leech Mechanics (Step 73)."""
import pytest
from app.domain.leech import calculate_leech, apply_leech_to_pool


class TestCalculateLeech:
    def test_zero_pct_no_leech(self):
        assert calculate_leech(100.0, 0.0) == pytest.approx(0.0)

    def test_10pct_leech(self):
        assert calculate_leech(200.0, 10.0) == pytest.approx(20.0)

    def test_100pct_leech(self):
        assert calculate_leech(100.0, 100.0) == pytest.approx(100.0)

    def test_above_100pct_clamped(self):
        assert calculate_leech(100.0, 150.0) == pytest.approx(100.0)

    def test_negative_pct_returns_zero(self):
        assert calculate_leech(100.0, -10.0) == pytest.approx(0.0)

    def test_max_per_hit_caps_result(self):
        assert calculate_leech(1000.0, 50.0, max_per_hit=30.0) == pytest.approx(30.0)

    def test_max_per_hit_not_exceeded_when_below(self):
        assert calculate_leech(100.0, 10.0, max_per_hit=50.0) == pytest.approx(10.0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError, match="damage"):
            calculate_leech(-10.0, 5.0)


class TestApplyLeechToPool:
    def test_restores_resource(self):
        assert apply_leech_to_pool(50.0, 100.0, 20.0) == pytest.approx(70.0)

    def test_caps_at_maximum(self):
        assert apply_leech_to_pool(90.0, 100.0, 50.0) == pytest.approx(100.0)

    def test_zero_leech_no_change(self):
        assert apply_leech_to_pool(60.0, 100.0, 0.0) == pytest.approx(60.0)

    def test_negative_leech_ignored(self):
        assert apply_leech_to_pool(60.0, 100.0, -10.0) == pytest.approx(60.0)

    def test_negative_current_raises(self):
        with pytest.raises(ValueError):
            apply_leech_to_pool(-1.0, 100.0, 10.0)

    def test_zero_maximum_raises(self):
        with pytest.raises(ValueError):
            apply_leech_to_pool(0.0, 0.0, 10.0)
