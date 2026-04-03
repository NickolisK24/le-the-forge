"""I9 — Multi-Target Status Manager tests."""
import pytest
from status.models.status_effect import StatusEffect
from status.multi_target_status_manager import MultiTargetStatusManager

shock  = StatusEffect("shock",  duration=2.0, stack_limit=3, effect_type="amplifier", value=10.0)
ignite = StatusEffect("ignite", duration=3.0, effect_type="dot", value=50.0)


def _mgr() -> MultiTargetStatusManager:
    m = MultiTargetStatusManager()
    m.register(shock)
    m.register(ignite)
    return m


class TestStatusIsolation:
    def test_status_on_t1_not_on_t2(self):
        mgr = _mgr()
        mgr.apply("t1", "shock", now=0.0)
        assert mgr.is_active("t1", "shock") is True
        assert mgr.is_active("t2", "shock") is False

    def test_different_stacks_per_target(self):
        mgr = _mgr()
        mgr.apply("t1", "shock", now=0.0)
        mgr.apply("t2", "shock", now=0.0)
        mgr.apply("t2", "shock", now=0.0)
        assert mgr.stack_count("t1", "shock") == 1
        assert mgr.stack_count("t2", "shock") == 2


class TestIndependentExpiration:
    def test_t1_expires_t2_remains(self):
        mgr = _mgr()
        mgr.apply("t1", "shock", now=0.0)
        mgr.apply("t2", "shock", now=1.5)   # applied later
        mgr.tick("t1", now=2.5)             # t1 shock expires (0+2<2.5)
        assert mgr.is_active("t1", "shock") is False
        assert mgr.is_active("t2", "shock") is True   # 1.5+2=3.5 > 2.5


class TestStackCorrectness:
    def test_stack_limit_respected_per_target(self):
        mgr = _mgr()
        for _ in range(5):
            mgr.apply("t1", "shock", now=0.0)
        assert mgr.stack_count("t1", "shock") == 3   # shock.stack_limit=3

    def test_total_value(self):
        mgr = _mgr()
        mgr.apply("t1", "shock", now=0.0)
        mgr.apply("t1", "shock", now=0.0)
        assert mgr.total_value("t1", "shock") == pytest.approx(20.0)

    def test_tick_all(self):
        mgr = _mgr()
        mgr.apply("t1", "shock", now=0.0)
        mgr.apply("t2", "ignite", now=0.0)
        expired = mgr.tick_all(now=4.0)   # both should expire
        assert "shock" in expired.get("t1", [])
        assert "ignite" in expired.get("t2", [])
