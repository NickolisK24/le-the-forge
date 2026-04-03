"""K14 — Spatial simulation integration tests."""
import pytest
from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager
from services.spatial_simulation_integration import (
    SpatialSimulationIntegration,
    SpatialSimulationResult,
    ProjectileSpec,
)


def _mgr(n: int = 3, hp: float = 10000.0) -> TargetManager:
    mgr = TargetManager()
    for i in range(n):
        mgr.spawn(TargetEntity(target_id=f"enemy_{i}", max_health=hp))
    return mgr


def _spec(origin: Vector2 = None, speed: float = 50.0, damage: float = 100.0) -> ProjectileSpec:
    return ProjectileSpec(
        origin=origin or Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=speed,
        damage=damage,
        skill_id="arrow",
        max_range=200.0,
    )


class TestIntegrationRun:
    def test_returns_result_object(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(1)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[_spec()],
            duration=1.0,
        )
        assert isinstance(result, SpatialSimulationResult)

    def test_tick_records_count(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(1, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[],  # no projectiles, won't stop early
            duration=1.0,
        )
        assert result.ticks_executed == 10

    def test_metrics_summary_present(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(1)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[_spec()],
            duration=1.0,
        )
        assert "hits" in result.metrics_summary
        assert "projectiles_spawned" in result.metrics_summary

    def test_spawn_recorded_in_metrics(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(1, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[_spec(), _spec()],
            duration=0.1,
        )
        assert result.metrics_summary["projectiles_spawned"] == 2

    def test_explicit_target_positions(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(2, hp=1e9)
        # Place targets far away to avoid accidental hits
        positions = {"enemy_0": Vector2(1000, 0), "enemy_1": Vector2(2000, 0)}
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[],
            duration=0.5,
            target_positions=positions,
        )
        assert result.ticks_executed == 5

    def test_linear_layout(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(3, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[],
            duration=0.5,
            layout="linear",
            layout_spacing=3.0,
        )
        assert result.ticks_executed == 5

    def test_circle_layout(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(4, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[],
            duration=0.5,
            layout="circle",
        )
        assert result.ticks_executed == 5

    def test_target_snapshots_in_result(self):
        integration = SpatialSimulationIntegration(tick_size=0.5)
        mgr = _mgr(2, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[],
            duration=0.5,
        )
        assert len(result.target_snapshots) == 2

    def test_log_entries_present(self):
        integration = SpatialSimulationIntegration(tick_size=0.1)
        mgr = _mgr(1, hp=1e9)
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[_spec()],
            duration=0.1,
        )
        # At least one spawn event logged
        assert any(e["event_type"] == "spawn" for e in result.log_entries)

    def test_projectile_with_pierce(self):
        integration = SpatialSimulationIntegration(tick_size=0.05)
        mgr = _mgr(3, hp=1e9)
        spec = ProjectileSpec(
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            speed=10.0,
            damage=50.0,
            skill_id="pierce_arrow",
            max_range=1000.0,
            pierce_count=2,
        )
        result = integration.run_simulation(
            target_manager=mgr,
            projectile_specs=[spec],
            duration=1.0,
            target_positions={
                "enemy_0": Vector2(200, 0),
                "enemy_1": Vector2(400, 0),
                "enemy_2": Vector2(600, 0),
            },
        )
        assert isinstance(result, SpatialSimulationResult)
