"""
Tests for Cast Speed & Attack Speed Scaling (Step 53).

Validates:
  - Zero bonus returns base interval/rate unchanged
  - Positive speed shortens interval, increases rate
  - Minimum interval floor enforced
  - Cast and attack speed use the same formula but different stats
  - Multi-hit interval scales correctly
  - Negative speed values treated as 0 (no penalty)
  - Invalid inputs raise ValueError
"""

import pytest
from app.domain.speed_scaling import (
    effective_cast_interval,
    effective_attack_interval,
    effective_cast_rate,
    effective_attack_rate,
    scale_hit_interval,
    _MIN_INTERVAL,
)


# ---------------------------------------------------------------------------
# effective_cast_interval
# ---------------------------------------------------------------------------

class TestEffectiveCastInterval:
    def test_zero_bonus_unchanged(self):
        assert effective_cast_interval(1.0, 0.0) == pytest.approx(1.0)

    def test_100pct_speed_halves_interval(self):
        # +100% speed → interval / 2
        assert effective_cast_interval(2.0, 100.0) == pytest.approx(1.0)

    def test_50pct_speed_reduces_interval(self):
        # base=1.0, +50% → 1.0 / 1.5 ≈ 0.667
        assert effective_cast_interval(1.0, 50.0) == pytest.approx(1.0 / 1.5)

    def test_200pct_speed_divides_by_three(self):
        assert effective_cast_interval(3.0, 200.0) == pytest.approx(1.0)

    def test_min_interval_floor_applied(self):
        # Extreme speed should not go below _MIN_INTERVAL
        result = effective_cast_interval(1.0, 100000.0)
        assert result == pytest.approx(_MIN_INTERVAL)

    def test_negative_speed_treated_as_zero(self):
        # Speed penalties are not modelled — treated as 0
        assert effective_cast_interval(1.0, -50.0) == pytest.approx(1.0)

    def test_zero_base_interval_raises(self):
        with pytest.raises(ValueError, match="base_interval"):
            effective_cast_interval(0.0, 0.0)

    def test_negative_base_interval_raises(self):
        with pytest.raises(ValueError, match="base_interval"):
            effective_cast_interval(-1.0, 0.0)


# ---------------------------------------------------------------------------
# effective_attack_interval
# ---------------------------------------------------------------------------

class TestEffectiveAttackInterval:
    def test_zero_bonus_unchanged(self):
        assert effective_attack_interval(1.0, 0.0) == pytest.approx(1.0)

    def test_100pct_halves_interval(self):
        assert effective_attack_interval(2.0, 100.0) == pytest.approx(1.0)

    def test_min_floor_applied(self):
        result = effective_attack_interval(0.1, 100000.0)
        assert result == pytest.approx(_MIN_INTERVAL)


# ---------------------------------------------------------------------------
# effective_cast_rate
# ---------------------------------------------------------------------------

class TestEffectiveCastRate:
    def test_zero_bonus_unchanged(self):
        assert effective_cast_rate(2.0, 0.0) == pytest.approx(2.0)

    def test_100pct_doubles_rate(self):
        assert effective_cast_rate(1.0, 100.0) == pytest.approx(2.0)

    def test_50pct_increases_rate(self):
        assert effective_cast_rate(2.0, 50.0) == pytest.approx(3.0)

    def test_rate_faster_with_higher_bonus(self):
        slow = effective_cast_rate(1.0, 10.0)
        fast = effective_cast_rate(1.0, 50.0)
        assert fast > slow

    def test_zero_base_rate_raises(self):
        with pytest.raises(ValueError, match="base_rate"):
            effective_cast_rate(0.0, 50.0)


# ---------------------------------------------------------------------------
# effective_attack_rate
# ---------------------------------------------------------------------------

class TestEffectiveAttackRate:
    def test_zero_bonus_unchanged(self):
        assert effective_attack_rate(1.5, 0.0) == pytest.approx(1.5)

    def test_100pct_doubles_rate(self):
        assert effective_attack_rate(1.0, 100.0) == pytest.approx(2.0)

    def test_rate_is_inverse_of_interval(self):
        base = 1.0
        speed = 50.0
        rate     = effective_attack_rate(base, speed)
        interval = effective_attack_interval(base, speed)
        assert rate * interval == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# scale_hit_interval
# ---------------------------------------------------------------------------

class TestScaleHitInterval:
    def test_single_hit_equals_cast_interval(self):
        result = scale_hit_interval(1.0, 0.0, hit_count=1)
        assert result == pytest.approx(effective_cast_interval(1.0, 0.0))

    def test_two_hits_halves_interval(self):
        # cast window = 1.0s / 2 hits = 0.5s per hit
        result = scale_hit_interval(1.0, 0.0, hit_count=2)
        assert result == pytest.approx(0.5)

    def test_four_hits(self):
        result = scale_hit_interval(2.0, 0.0, hit_count=4)
        assert result == pytest.approx(0.5)

    def test_speed_applied_before_hit_division(self):
        # +100% speed → cast window = 2.0/2.0 = 1.0s → per hit = 0.5s
        result = scale_hit_interval(2.0, 100.0, hit_count=2)
        assert result == pytest.approx(0.5)

    def test_min_floor_applied(self):
        result = scale_hit_interval(0.1, 100000.0, hit_count=100)
        assert result == pytest.approx(_MIN_INTERVAL)

    def test_zero_hit_count_raises(self):
        with pytest.raises(ValueError, match="hit_count"):
            scale_hit_interval(1.0, 0.0, hit_count=0)

    def test_negative_hit_count_raises(self):
        with pytest.raises(ValueError, match="hit_count"):
            scale_hit_interval(1.0, 0.0, hit_count=-1)


# ---------------------------------------------------------------------------
# Cross-check: interval and rate are inverse
# ---------------------------------------------------------------------------

class TestIntervalRateInverse:
    def test_cast_interval_rate_inverse(self):
        for speed in [0.0, 25.0, 50.0, 100.0]:
            base = 1.0
            interval = effective_cast_interval(base, speed)
            rate     = effective_cast_rate(base, speed)
            assert interval * rate == pytest.approx(1.0), f"failed at speed={speed}"
