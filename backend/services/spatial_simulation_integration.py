"""
K14 — Spatial Simulation Integration

Top-level service that wires together the complete spatial combat pipeline:
  1. Accept a target layout and skill configuration
  2. Spawn projectiles from skill activations
  3. Run the spatial timeline synchronizer
  4. Collect and return metrics + tick records

This is the single entry point for external callers (API routes, tests)
that want to run a full spatially-aware combat simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile
from projectiles.projectile_manager import ProjectileManager
from targets.target_manager import TargetManager
from targets.spatial_target_manager import SpatialTargetManager
from spatial.timeline.spatial_sync import SpatialTimelineSynchronizer, SpatialTickRecord
from combat.hit_resolution_engine import HitResolutionEngine
from metrics.spatial_metrics import SpatialMetrics
from debug.spatial_logger import SpatialLogger


@dataclass(frozen=True)
class ProjectileSpec:
    """Configuration for one projectile to spawn at simulation start."""

    origin:      Vector2
    direction:   Vector2
    speed:       float
    damage:      float
    skill_id:    str
    max_range:   float = float("inf")
    pierce_count: int  = 0
    radius:      float = 0.5


@dataclass
class SpatialSimulationResult:
    """Complete result returned by run_simulation."""

    tick_records:   list[SpatialTickRecord]
    metrics_summary: dict
    target_snapshots: list[dict]
    log_entries:    list[dict]
    ticks_executed: int
    duration:       float


class SpatialSimulationIntegration:
    """
    Orchestrates a full spatial simulation run.

    Usage:
        integration = SpatialSimulationIntegration()
        result = integration.run_simulation(
            target_manager=mgr,
            target_positions={"boss": Vector2(10, 0)},
            projectile_specs=[ProjectileSpec(...)],
            duration=5.0,
        )
    """

    def __init__(
        self,
        tick_size: float = 0.05,
        crit_chance: float = 0.0,
        crit_multiplier: float = 1.5,
        log_capacity: int = 200,
    ) -> None:
        self.tick_size = tick_size
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.log_capacity = log_capacity

    def run_simulation(
        self,
        target_manager: TargetManager,
        projectile_specs: list[ProjectileSpec],
        duration: float,
        target_positions: dict[str, Vector2] | None = None,
        layout: str = "linear",
        layout_spacing: float = 2.0,
    ) -> SpatialSimulationResult:
        """
        Run a complete spatial simulation and return results.

        target_manager     — pre-populated TargetManager
        projectile_specs   — list of projectiles to spawn at t=0
        duration           — simulation length in seconds
        target_positions   — explicit 2D positions for targets (overrides layout)
        layout             — auto-layout when target_positions is None:
                             "linear" | "circle"
        layout_spacing     — spacing parameter for linear layout
        """
        # --- Build spatial manager ---
        spatial_mgr = SpatialTargetManager(target_manager)

        if target_positions:
            for tid, pos in target_positions.items():
                spatial_mgr.set_position(tid, pos)
        elif layout == "circle":
            spatial_mgr.layout_circle(radius=layout_spacing)
        else:
            spatial_mgr.layout_linear(spacing=layout_spacing)

        # --- Build projectile manager ---
        proj_mgr = ProjectileManager()
        metrics = SpatialMetrics()
        logger = SpatialLogger(capacity=self.log_capacity)

        for spec in projectile_specs:
            proj = Projectile(
                origin=spec.origin,
                direction=spec.direction,
                speed=spec.speed,
                damage=spec.damage,
                skill_id=spec.skill_id,
                max_range=spec.max_range,
                pierce_count=spec.pierce_count,
                radius=spec.radius,
            )
            proj_mgr.spawn(proj)
            metrics.record_projectile_spawn()
            logger.log_projectile_spawn(proj)

        # --- Run synchronizer ---
        resolver = HitResolutionEngine()
        sync = SpatialTimelineSynchronizer(
            tick_size=self.tick_size,
            record_snapshots=True,
        )
        records = sync.run(
            projectile_mgr=proj_mgr,
            spatial_mgr=spatial_mgr,
            duration=duration,
            resolution=resolver,
            crit_chance=self.crit_chance,
            crit_multiplier=self.crit_multiplier,
        )

        # --- Harvest hit data from records into metrics ---
        for record in records:
            for hit in record.hit_log:
                metrics.record_hit(
                    damage=hit["damage"],
                    is_critical=hit["is_critical"],
                )
                if hit["killed"]:
                    logger.log_target_killed(hit["target_id"], record.time)

        # Record expired projectiles
        for proj in proj_mgr.all_projectiles():
            if not proj.is_active:
                metrics.record_projectile_expired(proj.distance_traveled)

        return SpatialSimulationResult(
            tick_records=records,
            metrics_summary=metrics.summary(),
            target_snapshots=spatial_mgr.snapshot(),
            log_entries=logger.entries(),
            ticks_executed=len(records),
            duration=duration,
        )
