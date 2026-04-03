"""H7 — Event Trigger System tests."""
import pytest
from events.event_trigger import EventTrigger, TriggerRegistry, VALID_EVENTS


class TestTriggerCreation:
    def test_valid_trigger(self):
        t = EventTrigger("t1", "on_hit", callback=lambda ctx: None)
        assert t.trigger_id == "t1"

    def test_invalid_event_raises(self):
        with pytest.raises(ValueError, match="Invalid event"):
            EventTrigger("t1", "on_fly", callback=lambda ctx: None)

    def test_priority_below_1_raises(self):
        with pytest.raises(ValueError, match="priority"):
            EventTrigger("t1", "on_hit", callback=lambda ctx: None, priority=0)


class TestTriggerFiring:
    def test_fire_invokes_callback(self):
        log = []
        reg = TriggerRegistry()
        reg.register(EventTrigger("t1", "on_hit", callback=lambda ctx: log.append(ctx)))
        reg.fire("on_hit", {"damage": 100})
        assert len(log) == 1
        assert log[0]["damage"] == 100

    def test_fire_returns_fired_ids(self):
        reg = TriggerRegistry()
        reg.register(EventTrigger("t1", "on_crit", callback=lambda ctx: None))
        reg.register(EventTrigger("t2", "on_crit", callback=lambda ctx: None))
        fired = reg.fire("on_crit")
        assert set(fired) == {"t1", "t2"}

    def test_unregistered_event_not_fired(self):
        log = []
        reg = TriggerRegistry()
        reg.register(EventTrigger("t1", "on_hit", callback=lambda ctx: log.append(1)))
        reg.fire("on_kill")
        assert log == []

    def test_unknown_event_raises(self):
        reg = TriggerRegistry()
        with pytest.raises(ValueError):
            reg.fire("on_fly")


class TestEventSequencing:
    def test_priority_order(self):
        order = []
        reg = TriggerRegistry()
        reg.register(EventTrigger("high", "on_hit", callback=lambda ctx: order.append("high"), priority=1))
        reg.register(EventTrigger("low",  "on_hit", callback=lambda ctx: order.append("low"),  priority=5))
        reg.fire("on_hit")
        assert order == ["high", "low"]

    def test_unregister_removes_trigger(self):
        log = []
        reg = TriggerRegistry()
        reg.register(EventTrigger("t1", "on_kill", callback=lambda ctx: log.append(1)))
        reg.unregister("t1")
        reg.fire("on_kill")
        assert log == []
