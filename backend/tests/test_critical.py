"""
Tests for Critical Strike System.

Last Epoch crit formula:
  Crit% = base × (1 + increased_pct / 100), capped at 100%
  Base crit multiplier: 150% (1.5×)
"""

import pytest
from app.domain.critical import (
    apply_crit,
    effective_crit_chance,
    effective_crit_multiplier,
    roll_crit,
    BASE_CRIT_MULTIPLIER,
    CRIT_CAP,
)


class TestEffectiveCritChance:
    def test_zero_base_zero_bonus(self):
        assert effective_crit_chance(0.0, 0.0) == pytest.approx(0.0)

    def test_base_only_no_bonus(self):
        assert effective_crit_chance(0.05, 0.0) == pytest.approx(0.05)

    def test_increased_multiplies_base(self):
        # 5% base × (1 + 100/100) = 5% × 2.0 = 10%
        assert effective_crit_chance(0.05, 100.0) == pytest.approx(0.10)

    def test_200pct_increased_triples_base(self):
        # 5% base × (1 + 200/100) = 5% × 3.0 = 15%
        assert effective_crit_chance(0.05, 200.0) == pytest.approx(0.15)

    def test_capped_at_100pct(self):
        assert effective_crit_chance(0.5, 200.0) == pytest.approx(CRIT_CAP)

    def test_above_cap_clamped(self):
        assert effective_crit_chance(1.0, 50.0) == pytest.approx(CRIT_CAP)

    def test_negative_increased_reduces_chance(self):
        # 5% base × (1 + (-50)/100) = 5% × 0.5 = 2.5%
        assert effective_crit_chance(0.05, -50.0) == pytest.approx(0.025)

    def test_negative_increased_clamped_at_zero(self):
        # 5% base × (1 + (-200)/100) = 5% × (-1.0) = -5% → clamped to 0
        assert effective_crit_chance(0.05, -200.0) == pytest.approx(0.0)

    def test_negative_base_raises(self):
        with pytest.raises(ValueError, match="base_chance"):
            effective_crit_chance(-0.1, 0.0)

    def test_large_increased_still_capped(self):
        # 50% base × (1 + 5000/100) = 50% × 51 → capped at 1.0
        assert effective_crit_chance(0.5, 5000.0) == pytest.approx(CRIT_CAP)


class TestEffectiveCritMultiplier:
    def test_base_only_no_bonus(self):
        assert effective_crit_multiplier(1.5, 0.0) == pytest.approx(1.5)

    def test_50pct_bonus_adds_half(self):
        # 1.5 + 50/100 = 2.0
        assert effective_crit_multiplier(1.5, 50.0) == pytest.approx(2.0)

    def test_100pct_bonus_adds_1(self):
        assert effective_crit_multiplier(1.5, 100.0) == pytest.approx(2.5)

    def test_negative_bonus_clamped_to_zero(self):
        assert effective_crit_multiplier(1.5, -50.0) == pytest.approx(1.5)

    def test_base_below_1_raises(self):
        with pytest.raises(ValueError, match="base_multiplier"):
            effective_crit_multiplier(0.5, 0.0)

    def test_base_exactly_1_allowed(self):
        assert effective_crit_multiplier(1.0, 0.0) == pytest.approx(1.0)

    def test_default_base_multiplier_constant(self):
        """Base crit multiplier is 200% (2.0×) per verified 1.4.3 game data."""
        # VERIFIED: 1.4.3 spec §2.2
        assert BASE_CRIT_MULTIPLIER == pytest.approx(2.0)


class TestApplyCrit:
    def test_non_crit_returns_raw(self):
        assert apply_crit(100.0, is_crit=False, crit_multiplier=2.0) == pytest.approx(100.0)

    def test_crit_doubles_damage_at_2x(self):
        assert apply_crit(100.0, is_crit=True, crit_multiplier=2.0) == pytest.approx(200.0)

    def test_crit_with_custom_multiplier(self):
        assert apply_crit(100.0, is_crit=True, crit_multiplier=3.5) == pytest.approx(350.0)

    def test_zero_damage_stays_zero(self):
        assert apply_crit(0.0, is_crit=True, crit_multiplier=2.0) == pytest.approx(0.0)

    def test_negative_raw_damage_raises(self):
        with pytest.raises(ValueError, match="raw_damage"):
            apply_crit(-10.0, is_crit=True, crit_multiplier=2.0)

    def test_multiplier_below_1_raises(self):
        with pytest.raises(ValueError, match="crit_multiplier"):
            apply_crit(100.0, is_crit=True, crit_multiplier=0.5)

    def test_multiplier_exactly_1_no_bonus(self):
        assert apply_crit(100.0, is_crit=True, crit_multiplier=1.0) == pytest.approx(100.0)


class TestRollCrit:
    def test_zero_chance_never_crits(self):
        assert roll_crit(0.0, rng_roll=0.0) is False

    def test_100pct_chance_always_crits(self):
        assert roll_crit(1.0, rng_roll=99.9) is True

    def test_roll_below_threshold_crits(self):
        assert roll_crit(0.5, rng_roll=49.9) is True

    def test_roll_at_threshold_no_crit(self):
        assert roll_crit(0.5, rng_roll=50.0) is False

    def test_roll_above_threshold_no_crit(self):
        assert roll_crit(0.5, rng_roll=75.0) is False

    def test_none_roll_treated_as_zero(self):
        assert roll_crit(0.01, rng_roll=None) is True

    def test_none_roll_zero_chance_no_crit(self):
        assert roll_crit(0.0, rng_roll=None) is False
