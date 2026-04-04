"""
Tests for Long-Fight Stability Hardening (Step 70).
"""

import pytest
from app.domain.stability import (
    SimStats,
    accumulate,
    clamp,
    normalise_pct,
    safe_subtract,
    safe_tick,
    stable_divide,
)


class TestClamp:
    def test_within_range(self):
        assert clamp(50.0, 0.0, 100.0) == pytest.approx(50.0)

    def test_below_lo_clamped(self):
        assert clamp(-10.0, 0.0, 100.0) == pytest.approx(0.0)

    def test_above_hi_clamped(self):
        assert clamp(200.0, 0.0, 100.0) == pytest.approx(100.0)

    def test_lo_equals_hi(self):
        assert clamp(50.0, 30.0, 30.0) == pytest.approx(30.0)

    def test_lo_greater_than_hi_raises(self):
        with pytest.raises(ValueError):
            clamp(50.0, 100.0, 0.0)


class TestSafeSubtract:
    def test_normal_subtraction(self):
        assert safe_subtract(10.0, 3.0) == pytest.approx(7.0)

    def test_floored_at_zero(self):
        assert safe_subtract(3.0, 10.0) == pytest.approx(0.0)

    def test_exact_zero_result(self):
        assert safe_subtract(5.0, 5.0) == pytest.approx(0.0)

    def test_floating_point_near_zero(self):
        result = safe_subtract(1.0, 1.0 + 1e-15)
        assert result == pytest.approx(0.0)


class TestSafeTick:
    def test_normal_decrement(self):
        assert safe_tick(5.0, 1.0) == pytest.approx(4.0)

    def test_floored_at_zero(self):
        assert safe_tick(0.5, 2.0) == pytest.approx(0.0)

    def test_zero_delta_no_change(self):
        assert safe_tick(3.0, 0.0) == pytest.approx(3.0)

    def test_negative_delta_raises(self):
        with pytest.raises(ValueError, match="delta"):
            safe_tick(5.0, -1.0)


class TestAccumulate:
    def test_adds_positive_amount(self):
        assert accumulate(100.0, 50.0) == pytest.approx(150.0)

    def test_ignores_negative_amount(self):
        assert accumulate(100.0, -10.0) == pytest.approx(100.0)

    def test_zero_amount_no_change(self):
        assert accumulate(100.0, 0.0) == pytest.approx(100.0)

    def test_accumulates_from_zero(self):
        total = 0.0
        for i in range(100):
            total = accumulate(total, 10.0)
        assert total == pytest.approx(1000.0)


class TestNormalisePct:
    def test_within_range(self):
        assert normalise_pct(55.0) == pytest.approx(55.0)

    def test_below_zero_clamped(self):
        assert normalise_pct(-5.0) == pytest.approx(0.0)

    def test_above_100_clamped(self):
        assert normalise_pct(150.0) == pytest.approx(100.0)

    def test_boundaries(self):
        assert normalise_pct(0.0) == pytest.approx(0.0)
        assert normalise_pct(100.0) == pytest.approx(100.0)


class TestStableDivide:
    def test_normal_division(self):
        assert stable_divide(10.0, 2.0) == pytest.approx(5.0)

    def test_zero_denominator_returns_fallback(self):
        assert stable_divide(10.0, 0.0) == pytest.approx(0.0)

    def test_custom_fallback(self):
        assert stable_divide(10.0, 0.0, fallback=99.0) == pytest.approx(99.0)

    def test_near_zero_denominator_uses_fallback(self):
        assert stable_divide(10.0, 1e-15) == pytest.approx(0.0)

    def test_negative_denominator(self):
        assert stable_divide(10.0, -2.0) == pytest.approx(-5.0)


class TestSimStats:
    def test_empty_stats(self):
        s = SimStats()
        assert s.count == 0
        assert s.total == pytest.approx(0.0)
        assert s.mean == pytest.approx(0.0)
        assert s.min_value == pytest.approx(0.0)
        assert s.max_value == pytest.approx(0.0)

    def test_single_observation(self):
        s = SimStats()
        s.record(50.0)
        assert s.count == 1
        assert s.mean == pytest.approx(50.0)
        assert s.min_value == pytest.approx(50.0)
        assert s.max_value == pytest.approx(50.0)

    def test_multiple_observations(self):
        s = SimStats()
        for v in [10.0, 20.0, 30.0]:
            s.record(v)
        assert s.count == 3
        assert s.total == pytest.approx(60.0)
        assert s.mean == pytest.approx(20.0)

    def test_min_max_tracking(self):
        s = SimStats()
        for v in [5.0, 50.0, 25.0]:
            s.record(v)
        assert s.min_value == pytest.approx(5.0)
        assert s.max_value == pytest.approx(50.0)

    def test_negative_values_ignored(self):
        s = SimStats()
        s.record(-10.0)
        s.record(20.0)
        assert s.count == 1
        assert s.total == pytest.approx(20.0)

    def test_nan_ignored(self):
        s = SimStats()
        s.record(float("nan"))
        s.record(10.0)
        assert s.count == 1

    def test_is_stable_constant_values(self):
        s = SimStats()
        for _ in range(100):
            s.record(10.0)
        assert s.is_stable() is True

    def test_is_stable_large_spike_unstable(self):
        s = SimStats()
        for _ in range(99):
            s.record(10.0)
        s.record(1000.0)   # massive spike
        assert s.is_stable() is False

    def test_is_stable_empty_returns_true(self):
        assert SimStats().is_stable() is True

    def test_range_value(self):
        s = SimStats()
        s.record(10.0)
        s.record(20.0)
        assert s.range_value == pytest.approx(10.0)
