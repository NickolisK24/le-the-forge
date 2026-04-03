"""L17 — MovementSimulationIntegration end-to-end tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.behaviors.aggressive_behavior import AggressiveBehavior
from movement.behaviors.defensive_behavior import DefensiveBehavior
from movement.behaviors.orbit_behavior import OrbitBehavior
from services.movement_simulation_integration import (
    MovementSimulationIntegration,
    MovementSimulationResult,
    EntityConfig,
)


def _config(eid: str, pos: Vector2, **kw) -> EntityConfig:
    return EntityConfig(entity_id=eid, start_pos=pos, **kw)


class TestBasicRun:
    def test_returns_result_object(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(10, 0))],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert isinstance(result, MovementSimulationResult)

    def test_ticks_executed(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(5, 0))],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert result.ticks_executed == 10

    def test_duration_in_result(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[],
            player_start=Vector2(0, 0),
            duration=2.0,
        )
        assert result.duration == 2.0

    def test_final_states_length(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        configs = [_config(f"e{i}", Vector2(i * 5, 0)) for i in range(3)]
        result = sim.run_simulation(
            entity_configs=configs,
            player_start=Vector2(0, 0),
            duration=0.5,
        )
        assert len(result.final_states) == 3

    def test_metrics_summary_present(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(10, 0))],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert "total_distance_all" in result.metrics_summary
        assert "kite_events" in result.metrics_summary


class TestBehaviors:
    def test_aggressive_enemies_approach_player(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(50, 0), behavior=AggressiveBehavior(speed=5.0))],
            player_start=Vector2(0, 0),
            duration=2.0,
        )
        final_pos_x = result.final_states[0]["position"][0]
        assert final_pos_x < 50  # moved toward player

    def test_defensive_enemies_maintain_range(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[
                _config("e1", Vector2(2, 0), behavior=DefensiveBehavior(min_range=5.0, max_range=10.0, speed=5.0))
            ],
            player_start=Vector2(0, 0),
            duration=2.0,
        )
        final_x = result.final_states[0]["position"][0]
        # Should have retreated from player at origin
        assert final_x > 2

    def test_orbit_behavior(self):
        sim = MovementSimulationIntegration(tick_size=0.05)
        result = sim.run_simulation(
            entity_configs=[
                _config("e1", Vector2(5, 0), behavior=OrbitBehavior(orbit_radius=5.0))
            ],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert isinstance(result, MovementSimulationResult)


class TestKiting:
    def test_kite_events_when_enemy_close(self):
        sim = MovementSimulationIntegration(
            tick_size=0.1,
            kite_min_range=10.0,
            kite_max_range=20.0,
            kite_speed=5.0,
        )
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(3, 0))],  # 3 < min_range=10
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert result.metrics_summary["kite_events"] >= 1

    def test_kite_log_has_entries(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(3, 0))],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert len(result.kite_results) > 0


class TestDistanceTracking:
    def test_distance_events_tracked(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[
                _config("e1", Vector2(20, 0), track_with=[], range_threshold=5.0)
            ],
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        # Just ensure no crash and result has structure
        assert isinstance(result.distance_events, list)

    def test_log_entries_present(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        result = sim.run_simulation(
            entity_configs=[_config("e1", Vector2(5, 0))],
            player_start=Vector2(0, 0),
            duration=0.5,
        )
        assert isinstance(result.log_entries, list)


class TestMultipleEntities:
    def test_ten_entities_run(self):
        sim = MovementSimulationIntegration(tick_size=0.1)
        configs = [
            _config(f"e{i}", Vector2(i * 3, 0), behavior=AggressiveBehavior(speed=3.0))
            for i in range(10)
        ]
        result = sim.run_simulation(
            entity_configs=configs,
            player_start=Vector2(0, 0),
            duration=1.0,
        )
        assert result.ticks_executed == 10
        assert len(result.final_states) == 10
