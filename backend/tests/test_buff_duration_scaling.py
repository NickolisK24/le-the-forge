"""
Tests for Buff Duration Scaling (Step 56).

Validates:
  - Zero bonus returns base duration unchanged
  - Positive bonus extends duration proportionally
  - Negative bonus clamped to 0 (no reduction)
  - Zero base duration stays zero regardless of bonus
  - apply_buff_duration preserves all other BuffInstance fields
  - Stacking: additive bonus (e.g. two 50% sources → +100% total)
  - Invalid inputs raise ValueError
"""

import pytest
from app.domain.buff_duration_scaling import scale_buff_duration, apply_buff_duration
from app.domain.timeline import BuffInstance, BuffType


# ---------------------------------------------------------------------------
# scale_buff_duration
# ---------------------------------------------------------------------------

class TestScaleBuffDuration:
    def test_zero_bonus_unchanged(self):
        assert scale_buff_duration(5.0, 0.0) == pytest.approx(5.0)

    def test_100pct_doubles_duration(self):
        assert scale_buff_duration(4.0, 100.0) == pytest.approx(8.0)

    def test_50pct_increases_by_half(self):
        assert scale_buff_duration(4.0, 50.0) == pytest.approx(6.0)

    def test_200pct_triples_duration(self):
        assert scale_buff_duration(3.0, 200.0) == pytest.approx(9.0)

    def test_25pct_bonus(self):
        assert scale_buff_duration(8.0, 25.0) == pytest.approx(10.0)

    def test_negative_bonus_clamped_to_zero(self):
        # No penalty — negative values treated as 0
        assert scale_buff_duration(5.0, -50.0) == pytest.approx(5.0)

    def test_zero_base_duration_stays_zero(self):
        assert scale_buff_duration(0.0, 100.0) == pytest.approx(0.0)

    def test_fractional_bonus(self):
        # +33.33% of 3.0 = 4.0
        assert scale_buff_duration(3.0, 33.333333) == pytest.approx(4.0, rel=1e-4)

    def test_negative_base_duration_raises(self):
        with pytest.raises(ValueError, match="base_duration"):
            scale_buff_duration(-1.0, 0.0)

    def test_large_bonus(self):
        # 1000% → base * 11
        assert scale_buff_duration(2.0, 1000.0) == pytest.approx(22.0)


# ---------------------------------------------------------------------------
# apply_buff_duration — preserves BuffInstance fields
# ---------------------------------------------------------------------------

class TestApplyBuffDuration:
    def test_duration_scaled(self):
        buff = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0, source="passive")
        result = apply_buff_duration(buff, 100.0)
        assert result.duration == pytest.approx(10.0)

    def test_buff_type_preserved(self):
        buff = BuffInstance(BuffType.CAST_SPEED, 30.0, 3.0)
        result = apply_buff_duration(buff, 50.0)
        assert result.buff_type is BuffType.CAST_SPEED

    def test_value_preserved(self):
        buff = BuffInstance(BuffType.ATTACK_SPEED, 15.0, 2.0)
        result = apply_buff_duration(buff, 50.0)
        assert result.value == pytest.approx(15.0)

    def test_source_preserved(self):
        buff = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 10.0, 4.0, source="aura_skill")
        result = apply_buff_duration(buff, 25.0)
        assert result.source == "aura_skill"

    def test_zero_bonus_returns_equivalent_buff(self):
        buff = BuffInstance(BuffType.RESISTANCE_SHRED, 10.0, 6.0, source="debuff")
        result = apply_buff_duration(buff, 0.0)
        assert result.duration == pytest.approx(6.0)
        assert result.value == pytest.approx(10.0)

    def test_original_buff_unchanged(self):
        buff = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0)
        apply_buff_duration(buff, 100.0)
        assert buff.duration == pytest.approx(5.0)  # frozen, should not change


# ---------------------------------------------------------------------------
# Additive stacking — two sources
# ---------------------------------------------------------------------------

class TestAdditiveDurationStacking:
    def test_two_50pct_sources_add_to_100pct(self):
        # Two +50% sources pool additively → total +100% → duration * 2
        total_pct = 50.0 + 50.0   # 100%
        assert scale_buff_duration(4.0, total_pct) == pytest.approx(8.0)

    def test_additive_not_multiplicative(self):
        # Additive: base * (1 + 0.5 + 0.5) = base * 2.0
        # Multiplicative would be: base * 1.5 * 1.5 = base * 2.25
        additive = scale_buff_duration(4.0, 50.0 + 50.0)
        assert additive == pytest.approx(8.0)     # not 9.0

    def test_three_sources(self):
        # 30 + 20 + 50 = 100% → duration * 2
        assert scale_buff_duration(5.0, 100.0) == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Integration — TimelineEngine with scaled duration
# ---------------------------------------------------------------------------

class TestIntegrationWithTimeline:
    def test_scaled_buff_expires_later(self):
        from app.domain.timeline import TimelineEngine

        engine = TimelineEngine()
        # Base buff lasts 3s; +100% → 6s
        buff = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 3.0)
        scaled_buff = apply_buff_duration(buff, 100.0)
        engine.add_buff(scaled_buff)

        # After 5.9s, should still be active
        engine.tick(5.9)
        assert engine.has_any(BuffType.DAMAGE_MULTIPLIER)

        # After another 0.2s (total 6.1s), should be expired
        engine.tick(0.2)
        assert not engine.has_any(BuffType.DAMAGE_MULTIPLIER)

    def test_unscaled_vs_scaled_buff_duration(self):
        from app.domain.timeline import TimelineEngine

        base_buff   = BuffInstance(BuffType.CAST_SPEED, 10.0, 3.0)
        scaled_buff = apply_buff_duration(base_buff, 50.0)  # 3s → 4.5s

        engine = TimelineEngine()
        engine.add_buff(scaled_buff)

        engine.tick(3.5)   # unscaled would be expired; scaled still active
        assert engine.has_any(BuffType.CAST_SPEED)

        engine.tick(1.1)   # total 4.6s → scaled now expired
        assert not engine.has_any(BuffType.CAST_SPEED)
