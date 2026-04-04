"""H6 — Status Manager tests."""
import pytest
from status.models.status_effect import StatusEffect
from status.status_manager import StatusManager


def _mgr_with(*effects: StatusEffect) -> StatusManager:
    mgr = StatusManager()
    for e in effects:
        mgr.register(e)
    return mgr


shock  = StatusEffect("shock",  duration=2.0, stack_limit=3,    effect_type="amplifier", value=10.0)
ignite = StatusEffect("ignite", duration=3.0, stack_limit=None, effect_type="dot",       value=50.0)


class TestStatusStacking:
    def test_apply_adds_stack(self):
        mgr = _mgr_with(shock)
        assert mgr.apply("shock", now=0.0) == 1
        assert mgr.stack_count("shock") == 1

    def test_apply_stacks(self):
        mgr = _mgr_with(shock)
        mgr.apply("shock", now=0.0)
        mgr.apply("shock", now=0.0)
        assert mgr.stack_count("shock") == 2

    def test_stack_limit_enforced(self):
        mgr = _mgr_with(shock)
        for _ in range(5):
            mgr.apply("shock", now=0.0)
        assert mgr.stack_count("shock") == 3  # capped at stack_limit=3

    def test_unlimited_stacks(self):
        mgr = _mgr_with(ignite)
        for _ in range(10):
            mgr.apply("ignite", now=0.0)
        assert mgr.stack_count("ignite") == 10

    def test_unregistered_raises(self):
        mgr = StatusManager()
        with pytest.raises(KeyError):
            mgr.apply("nonexistent", now=0.0)


class TestStatusExpiration:
    def test_tick_removes_expired(self):
        mgr = _mgr_with(shock)
        mgr.apply("shock", now=0.0)
        expired = mgr.tick(now=3.0)  # shock.duration=2.0
        assert "shock" in expired
        assert mgr.stack_count("shock") == 0

    def test_tick_keeps_fresh(self):
        mgr = _mgr_with(shock)
        mgr.apply("shock", now=1.0)
        expired = mgr.tick(now=2.0)   # 2.0 < 1.0+2.0=3.0 — not expired
        assert "shock" not in expired
        assert mgr.stack_count("shock") == 1


class TestMultipleStatuses:
    def test_two_statuses_tracked_independently(self):
        mgr = _mgr_with(shock, ignite)
        mgr.apply("shock", now=0.0)
        mgr.apply("ignite", now=0.0)
        assert mgr.stack_count("shock") == 1
        assert mgr.stack_count("ignite") == 1

    def test_total_value(self):
        mgr = _mgr_with(shock)
        mgr.apply("shock", now=0.0)
        mgr.apply("shock", now=0.0)
        assert mgr.total_value("shock") == 20.0  # 2 stacks × 10.0

    def test_active_status_ids(self):
        mgr = _mgr_with(shock, ignite)
        mgr.apply("ignite", now=0.0)
        assert mgr.active_status_ids() == ["ignite"]
