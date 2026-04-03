"""I4 — Multi-Target State tests."""
import pytest
from targets.target_templates import elite_pack, single_boss
from state.multi_target_state import MultiTargetState


def _state(count=3, hp=1000.0) -> MultiTargetState:
    return MultiTargetState(manager=elite_pack(count, hp))


class TestStateInitialization:
    def test_alive_count(self):
        s = _state(3)
        assert s.alive_count() == 3

    def test_not_cleared(self):
        s = _state(3)
        assert s.is_cleared() is False

    def test_invalid_player_max_health_raises(self):
        with pytest.raises(ValueError):
            MultiTargetState(manager=elite_pack(), player_max_health=0.0)


class TestMultiTargetHealthUpdates:
    def test_damage_one_target(self):
        s = _state()
        s.apply_damage("elite_0", 400.0)
        assert s.target_health_pct("elite_0") == pytest.approx(0.6)

    def test_kill_one_target(self):
        s = _state()
        s.apply_damage("elite_0", 1000.0)
        assert s.is_target_alive("elite_0") is False
        assert s.alive_count() == 2   # dead target excluded from alive count

    def test_unknown_target_raises(self):
        s = _state()
        with pytest.raises(KeyError):
            s.apply_damage("nonexistent", 100.0)


class TestTimelineSynchronization:
    def test_advance_time(self):
        s = _state()
        s.advance_time(2.5)
        assert s.elapsed_time == pytest.approx(2.5)

    def test_simulation_state_bridge(self):
        s = _state(1, 1000.0)
        s.apply_damage("elite_0", 300.0)
        sim = s.as_simulation_state("elite_0")
        assert sim.target_health_pct == pytest.approx(0.7)

    def test_simulation_state_all_dead_zeroed(self):
        s = _state(1, 500.0)
        s.apply_damage("elite_0", 500.0)
        s.manager.remove_dead()
        sim = s.as_simulation_state()
        assert sim.target_health == 0.0
