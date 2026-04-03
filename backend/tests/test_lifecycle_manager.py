"""I10 — Lifecycle Manager tests."""
import pytest
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager
from targets.lifecycle_manager import LifecycleManager
from events.event_trigger import EventTrigger, TriggerRegistry


def _mgr_with(*tids) -> TargetManager:
    mgr = TargetManager()
    for tid in tids:
        mgr.spawn(TargetEntity(tid, max_health=1000.0))
    return mgr


class TestKillDetection:
    def test_dead_target_detected(self):
        tmgr = _mgr_with("t1", "t2")
        tmgr.get("t1").apply_damage(1000.0)
        lm = LifecycleManager()
        kills = lm.process(tmgr, TriggerRegistry(), now=5.0)
        assert len(kills) == 1
        assert kills[0].target_id == "t1"

    def test_alive_target_not_detected(self):
        tmgr = _mgr_with("t1")
        lm = LifecycleManager()
        kills = lm.process(tmgr, TriggerRegistry(), now=1.0)
        assert kills == []


class TestEventFiring:
    def test_on_kill_fired(self):
        fired = []
        reg = TriggerRegistry()
        reg.register(EventTrigger("kl", "on_kill", callback=lambda ctx: fired.append(ctx["target_id"])))
        tmgr = _mgr_with("t1")
        tmgr.get("t1").apply_damage(1000.0)
        lm = LifecycleManager()
        lm.process(tmgr, reg, now=2.0)
        assert "t1" in fired


class TestTargetRemovalTiming:
    def test_dead_removed_after_process(self):
        tmgr = _mgr_with("t1", "t2")
        tmgr.get("t1").apply_damage(1000.0)
        lm = LifecycleManager()
        lm.process(tmgr, TriggerRegistry(), now=1.0)
        assert tmgr.total_count == 1
        assert tmgr.get("t2").is_alive

    def test_kill_log_accumulates(self):
        tmgr = _mgr_with("t1", "t2", "t3")
        for tid in ["t1", "t2"]:
            tmgr.get(tid).apply_damage(1000.0)
        lm = LifecycleManager()
        lm.process(tmgr, TriggerRegistry(), now=1.0)
        assert lm.total_kills() == 2
