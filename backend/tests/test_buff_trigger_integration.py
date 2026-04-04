"""H8 — Buff Trigger Integration tests."""
import pytest
from state.state_engine import SimulationState
from buffs.buff_trigger_integration import BuffTriggerIntegration
from events.event_trigger import TriggerRegistry, EventTrigger


def _state():
    return SimulationState(
        player_health=1000.0, player_max_health=1000.0,
        target_health=1000.0, target_max_health=1000.0,
    )


class TestBuffActivation:
    def test_activate_adds_to_state(self):
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("power_surge", state, now=0.0, duration=5.0)
        assert "power_surge" in state.active_buffs

    def test_activate_tracks_internally(self):
        bti = BuffTriggerIntegration()
        bti.activate_buff("power_surge", _state(), now=0.0, duration=5.0)
        assert bti.is_tracked("power_surge")

    def test_refresh_resets_timer(self):
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("power_surge", state, now=0.0, duration=3.0)
        bti.activate_buff("power_surge", state, now=2.0, duration=3.0)
        # Should still be tracked with updated applied_at=2.0
        assert bti.is_tracked("power_surge")


class TestBuffExpiration:
    def test_tick_expires_buff(self):
        expired_log = []
        reg = TriggerRegistry()
        reg.register(EventTrigger(
            "exp_listener", "on_buff_expire",
            callback=lambda ctx: expired_log.append(ctx["buff_id"])
        ))
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("power_surge", state, now=0.0, duration=2.0)
        expired = bti.tick(state, now=3.0, registry=reg)
        assert "power_surge" in expired
        assert "power_surge" not in state.active_buffs
        assert "power_surge" in expired_log

    def test_permanent_buff_never_expires(self):
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("always_on", state, now=0.0, duration=None)
        expired = bti.tick(state, now=9999.0, registry=TriggerRegistry())
        assert expired == []
        assert "always_on" in state.active_buffs


class TestMultiBuffStacking:
    def test_two_buffs_tracked(self):
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("buff_a", state, now=0.0, duration=5.0)
        bti.activate_buff("buff_b", state, now=0.0, duration=3.0)
        assert set(bti.active_buff_ids()) == {"buff_a", "buff_b"}

    def test_one_expires_other_remains(self):
        bti = BuffTriggerIntegration()
        state = _state()
        bti.activate_buff("long",  state, now=0.0, duration=10.0)
        bti.activate_buff("short", state, now=0.0, duration=2.0)
        bti.tick(state, now=3.0, registry=TriggerRegistry())
        assert bti.is_tracked("long")
        assert not bti.is_tracked("short")
