"""Tests for Hit Accuracy & Avoidance (Step 77)."""
import pytest
from app.domain.accuracy import calculate_hit_chance, roll_hit, HIT_CHANCE_MIN, HIT_CHANCE_MAX


class TestCalculateHitChance:
    def test_no_evasion_max_hit_chance(self):
        assert calculate_hit_chance(1000.0, 0.0) == pytest.approx(HIT_CHANCE_MAX)

    def test_equal_accuracy_evasion(self):
        assert calculate_hit_chance(500.0, 500.0) == pytest.approx(0.5)

    def test_zero_accuracy_min_hit_chance(self):
        assert calculate_hit_chance(0.0, 1000.0) == pytest.approx(HIT_CHANCE_MIN)

    def test_both_zero_max_hit_chance(self):
        assert calculate_hit_chance(0.0, 0.0) == pytest.approx(HIT_CHANCE_MAX)

    def test_very_high_accuracy_capped(self):
        assert calculate_hit_chance(1_000_000.0, 1.0) == pytest.approx(HIT_CHANCE_MAX)

    def test_very_high_evasion_floored(self):
        assert calculate_hit_chance(1.0, 1_000_000.0) == pytest.approx(HIT_CHANCE_MIN)

    def test_negative_accuracy_raises(self):
        with pytest.raises(ValueError):
            calculate_hit_chance(-1.0, 100.0)

    def test_negative_evasion_raises(self):
        with pytest.raises(ValueError):
            calculate_hit_chance(100.0, -1.0)


class TestRollHit:
    def test_none_roll_always_hits(self):
        assert roll_hit(0.5, rng_roll=None) is True

    def test_below_threshold_hits(self):
        assert roll_hit(0.6, rng_roll=0.5) is True

    def test_above_threshold_misses(self):
        assert roll_hit(0.6, rng_roll=0.7) is False

    def test_zero_chance_never_hits(self):
        assert roll_hit(0.0, rng_roll=0.0) is False
