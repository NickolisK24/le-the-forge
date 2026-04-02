"""Tests for Dodge Mechanics (Step 78)."""
import pytest
from app.domain.dodge import dodge_chance, roll_dodge, DODGE_CAP


class TestDodgeChance:
    def test_zero_rating_no_dodge(self):
        assert dodge_chance(0.0) == pytest.approx(0.0)

    def test_positive_rating_positive_chance(self):
        assert dodge_chance(1000.0) > 0.0

    def test_very_high_rating_capped(self):
        assert dodge_chance(10_000_000.0) == pytest.approx(DODGE_CAP)

    def test_level_penalty_reduces_chance(self):
        base  = dodge_chance(500.0, level_penalty=0.0)
        penalised = dodge_chance(500.0, level_penalty=1.0)
        assert penalised < base

    def test_negative_rating_raises(self):
        with pytest.raises(ValueError):
            dodge_chance(-10.0)

    def test_result_in_valid_range(self):
        chance = dodge_chance(500.0)
        assert 0.0 <= chance <= DODGE_CAP


class TestRollDodge:
    def test_zero_chance_never_dodges(self):
        assert roll_dodge(0.0) is False

    def test_full_cap_dodges_below_threshold(self):
        assert roll_dodge(DODGE_CAP, rng_roll=0.5) is True

    def test_above_threshold_no_dodge(self):
        assert roll_dodge(0.3, rng_roll=0.5) is False

    def test_none_roll_always_dodges_when_positive(self):
        assert roll_dodge(0.01, rng_roll=None) is True
