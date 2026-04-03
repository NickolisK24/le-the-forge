"""H5 — Status Effect Model tests."""
import pytest
from status.models.status_effect import StatusEffect


class TestStatusCreation:
    def test_valid_dot(self):
        s = StatusEffect("ignite", duration=3.0, effect_type="dot", value=50.0)
        assert s.status_id == "ignite"
        assert s.duration == 3.0

    def test_zero_duration_raises(self):
        with pytest.raises(ValueError, match="duration"):
            StatusEffect("x", duration=0.0)

    def test_negative_stack_limit_raises(self):
        with pytest.raises(ValueError, match="stack_limit"):
            StatusEffect("x", duration=1.0, stack_limit=0)

    def test_invalid_effect_type_raises(self):
        with pytest.raises(ValueError, match="Invalid effect_type"):
            StatusEffect("x", duration=1.0, effect_type="unknown")


class TestStackBehavior:
    def test_stack_limit_none_means_unlimited(self):
        s = StatusEffect("shock", duration=2.0, stack_limit=None)
        assert s.stack_limit is None

    def test_stack_limit_enforced(self):
        s = StatusEffect("chill", duration=5.0, stack_limit=3)
        assert s.stack_limit == 3


class TestExpirationTiming:
    def test_not_expired_within_duration(self):
        s = StatusEffect("ignite", duration=3.0)
        assert s.is_expired(applied_at=0.0, now=2.9) is False

    def test_expired_at_boundary(self):
        s = StatusEffect("ignite", duration=3.0)
        assert s.is_expired(applied_at=0.0, now=3.0) is True

    def test_expired_past_boundary(self):
        s = StatusEffect("ignite", duration=3.0)
        assert s.is_expired(applied_at=1.0, now=5.0) is True


class TestSerialization:
    def test_round_trip(self):
        s = StatusEffect("shock", duration=2.0, stack_limit=5, effect_type="amplifier", value=25.0)
        assert StatusEffect.from_dict(s.to_dict()).status_id == s.status_id
        assert StatusEffect.from_dict(s.to_dict()).duration == s.duration
