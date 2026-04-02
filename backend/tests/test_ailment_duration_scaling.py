"""
Tests for Status Duration Scaling (Step 59).

Validates:
  - Zero bonus returns base duration unchanged
  - Positive bonus extends duration proportionally
  - Negative bonus clamped to 0 (no reduction)
  - Zero base duration stays zero regardless of bonus
  - Large bonuses work correctly
  - Additive stacking: two sources sum before multiplying
  - Invalid inputs raise ValueError
"""

import pytest
from app.domain.ailment_duration_scaling import scale_ailment_duration


class TestScaleAilmentDuration:
    def test_zero_bonus_unchanged(self):
        assert scale_ailment_duration(5.0, 0.0) == pytest.approx(5.0)

    def test_100pct_doubles_duration(self):
        assert scale_ailment_duration(4.0, 100.0) == pytest.approx(8.0)

    def test_50pct_increases_by_half(self):
        assert scale_ailment_duration(4.0, 50.0) == pytest.approx(6.0)

    def test_200pct_triples_duration(self):
        assert scale_ailment_duration(3.0, 200.0) == pytest.approx(9.0)

    def test_25pct_bonus(self):
        assert scale_ailment_duration(8.0, 25.0) == pytest.approx(10.0)

    def test_negative_bonus_clamped_to_zero(self):
        # No penalty — negative values treated as 0
        assert scale_ailment_duration(5.0, -50.0) == pytest.approx(5.0)

    def test_zero_base_duration_stays_zero(self):
        assert scale_ailment_duration(0.0, 100.0) == pytest.approx(0.0)

    def test_large_bonus(self):
        # +1000% → base * 11
        assert scale_ailment_duration(2.0, 1000.0) == pytest.approx(22.0)

    def test_fractional_bonus(self):
        assert scale_ailment_duration(3.0, 33.333333) == pytest.approx(4.0, rel=1e-4)

    def test_negative_base_raises(self):
        with pytest.raises(ValueError, match="base_duration"):
            scale_ailment_duration(-1.0, 0.0)


class TestAdditiveDurationStacking:
    def test_two_sources_sum_before_multiply(self):
        # Two +50% sources → +100% total → duration * 2
        total_pct = 50.0 + 50.0
        assert scale_ailment_duration(4.0, total_pct) == pytest.approx(8.0)

    def test_additive_not_multiplicative(self):
        # Additive: 4 * (1 + 1.0) = 8.0
        # Multiplicative would be: 4 * 1.5 * 1.5 = 9.0
        assert scale_ailment_duration(4.0, 100.0) == pytest.approx(8.0)

    def test_multiple_small_bonuses(self):
        # 20 + 30 + 50 = 100% → duration * 2
        assert scale_ailment_duration(5.0, 100.0) == pytest.approx(10.0)


class TestCommonAilmentDurations:
    """Spot-check against realistic ailment base durations."""

    def test_bleed_3s_with_50pct(self):
        assert scale_ailment_duration(3.0, 50.0) == pytest.approx(4.5)

    def test_ignite_4s_with_100pct(self):
        assert scale_ailment_duration(4.0, 100.0) == pytest.approx(8.0)

    def test_poison_6s_with_33pct(self):
        assert scale_ailment_duration(6.0, 33.333333) == pytest.approx(8.0, rel=1e-4)

    def test_shock_2s_zero_bonus(self):
        assert scale_ailment_duration(2.0, 0.0) == pytest.approx(2.0)
