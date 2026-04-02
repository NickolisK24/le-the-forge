"""Tests for Block Mechanics (Step 79)."""
import pytest
from app.domain.block import block_result, roll_block, BLOCK_CHANCE_CAP


class TestRollBlock:
    def test_zero_chance_never_blocks(self):
        assert roll_block(0.0, rng_roll=0.0) is False

    def test_above_cap_clamped(self):
        assert roll_block(1.0, rng_roll=0.5) is True   # clamped to cap

    def test_below_threshold_blocks(self):
        assert roll_block(0.5, rng_roll=0.4) is True

    def test_above_threshold_no_block(self):
        assert roll_block(0.5, rng_roll=0.6) is False


class TestBlockResult:
    def test_no_block_full_damage(self):
        dmg, blocked = block_result(100.0, 0.0, 0.5, rng_roll=0.5)
        assert dmg == pytest.approx(100.0)
        assert blocked is False

    def test_full_effectiveness_zero_damage(self):
        dmg, blocked = block_result(100.0, 0.8, 1.0, rng_roll=0.1)
        assert dmg == pytest.approx(0.0)
        assert blocked is True

    def test_partial_effectiveness_reduces_damage(self):
        dmg, blocked = block_result(100.0, 0.8, 0.5, rng_roll=0.1)
        assert dmg == pytest.approx(50.0)
        assert blocked is True

    def test_negative_incoming_raises(self):
        with pytest.raises(ValueError, match="incoming"):
            block_result(-10.0, 0.5, 0.5)

    def test_invalid_effectiveness_raises(self):
        with pytest.raises(ValueError, match="block_effectiveness"):
            block_result(100.0, 0.5, 1.5)

    def test_zero_damage_blocked(self):
        dmg, blocked = block_result(0.0, 0.8, 0.5, rng_roll=0.1)
        assert dmg == pytest.approx(0.0)
        assert blocked is True
