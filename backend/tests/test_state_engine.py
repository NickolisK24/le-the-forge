"""H4 — State Tracking Engine tests."""
import pytest
from state.state_engine import SimulationState


def _state(**kw) -> SimulationState:
    defaults = dict(
        player_health=1000.0, player_max_health=1000.0,
        target_health=1000.0, target_max_health=1000.0,
    )
    defaults.update(kw)
    return SimulationState(**defaults)


class TestStateCreation:
    def test_defaults(self):
        s = _state()
        assert s.player_health_pct == 1.0
        assert s.target_health_pct == 1.0
        assert s.elapsed_time == 0.0

    def test_zero_max_health_raises(self):
        with pytest.raises(ValueError):
            SimulationState(player_max_health=0.0)

    def test_negative_health_raises(self):
        with pytest.raises(ValueError):
            _state(player_health=-1.0)

    def test_negative_elapsed_raises(self):
        with pytest.raises(ValueError):
            _state(elapsed_time=-0.1)


class TestHealthTransitions:
    def test_damage_reduces_health(self):
        s = _state()
        s.apply_damage_to_target(300.0)
        assert s.target_health == 700.0
        assert abs(s.target_health_pct - 0.7) < 1e-9

    def test_damage_floors_at_zero(self):
        s = _state()
        s.apply_damage_to_target(9999.0)
        assert s.target_health == 0.0

    def test_heal_restores(self):
        s = _state(player_health=500.0)
        s.heal_player(300.0)
        assert s.player_health == 800.0

    def test_heal_caps_at_max(self):
        s = _state(player_health=900.0)
        s.heal_player(500.0)
        assert s.player_health == 1000.0


class TestStatusApplication:
    def test_apply_status(self):
        s = _state()
        s.apply_status("shock", stacks=2)
        assert s.active_status_effects["shock"] == 2

    def test_remove_status(self):
        s = _state()
        s.apply_status("shock")
        s.remove_status("shock")
        assert "shock" not in s.active_status_effects


class TestTimeAdvance:
    def test_advance_time(self):
        s = _state()
        s.advance_time(1.5)
        assert abs(s.elapsed_time - 1.5) < 1e-9

    def test_zero_delta_raises(self):
        s = _state()
        with pytest.raises(ValueError):
            s.advance_time(0.0)


class TestSnapshot:
    def test_snapshot_keys(self):
        s = _state()
        snap = s.snapshot()
        assert "player_health_pct" in snap
        assert "target_health_pct" in snap
        assert "elapsed_time" in snap
