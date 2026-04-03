"""
K12 — Spatial Timeline Synchronizer

Drives a spatial simulation forward in fixed-size ticks, updating projectile
positions, checking collisions, and applying damage each tick. Uses integer
tick counting (same approach as Phase H/I) to eliminate float accumulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from projectiles.projectile_manager import ProjectileManager
from spatial.collision.collision_engine import CollisionEngine
from targets.spatial_target_manager import SpatialTargetManager
from combat.hit_resolution_engine import HitResolutionEngine, HitResult
from projectiles.pierce_logic import PierceLogic


@dataclass(frozen=True)
class SpatialTickRecord:
    """Snapshot recorded after each tick."""

    time:              float
    active_projectiles: int
    hits_this_tick:    int
    targets_alive:     int
    hit_log:           list[dict]    # serialisable hit summaries


@dataclass
class SpatialTimelineSynchronizer:
    """
    Runs a spatial combat simulation over a fixed duration.

    tick_size        — seconds per tick (default 0.05 s)
    record_snapshots — if False, returns an empty list (no memory overhead)
    hit_radius       — default target collision radius (world-units)
    """

    tick_size:        float = 0.05
    record_snapshots: bool  = True
    hit_radius:       float = 0.5

    def __post_init__(self) -> None:
        if self.tick_size <= 0:
            raise ValueError("tick_size must be > 0")

    def run(
        self,
        projectile_mgr: ProjectileManager,
        spatial_mgr: SpatialTargetManager,
        duration: float,
        resolution: HitResolutionEngine | None = None,
        crit_chance: float = 0.0,
        crit_multiplier: float = 1.5,
    ) -> list[SpatialTickRecord]:
        """
        Advance *projectile_mgr* and *spatial_mgr* for *duration* seconds.

        Each tick:
          1. advance_all projectiles by tick_size
          2. run collision detection for each active projectile
          3. resolve hits (damage + pierce)
          4. remove dead targets from spatial_mgr (via manager.remove_dead)
          5. optionally record a snapshot

        Returns list of SpatialTickRecord (one per tick).
        """
        if duration <= 0:
            raise ValueError("duration must be > 0")

        engine = CollisionEngine()
        pierce = PierceLogic()
        resolver = resolution or HitResolutionEngine()

        n_ticks = math.ceil(duration / self.tick_size)
        records: list[SpatialTickRecord] = []
        elapsed = 0.0

        for i in range(n_ticks):
            step = min(self.tick_size, duration - i * self.tick_size)
            if step <= 0:
                break

            elapsed += step
            projectile_mgr.advance_all(step)

            hits_this_tick: list[HitResult] = []
            target_pos_map = spatial_mgr.position_map(alive_only=True)

            for proj in projectile_mgr.active_projectiles():
                results = engine.find_hits(proj, target_pos_map)
                for collision in results:
                    if not pierce.can_hit(proj, collision.target_id):
                        continue
                    target = spatial_mgr.manager.get(collision.target_id)
                    if not target.is_alive:
                        continue
                    pos = spatial_mgr.get_position(collision.target_id)
                    hit = resolver.resolve_projectile_hit(
                        proj.damage, target, pos, crit_chance, crit_multiplier
                    )
                    hits_this_tick.append(hit)
                    pierce.apply(proj, collision.target_id)
                    # Refresh position map after potential kill
                    target_pos_map = spatial_mgr.position_map(alive_only=True)

            # Cleanup
            projectile_mgr.clear_inactive()
            spatial_mgr.manager.remove_dead()

            if self.record_snapshots:
                records.append(SpatialTickRecord(
                    time=round(elapsed, 9),
                    active_projectiles=projectile_mgr.active_count,
                    hits_this_tick=len(hits_this_tick),
                    targets_alive=spatial_mgr.alive_count(),
                    hit_log=[
                        {
                            "target_id":    h.target_id,
                            "damage":       round(h.damage_dealt, 4),
                            "is_critical":  h.is_critical,
                            "killed":       h.killed,
                        }
                        for h in hits_this_tick
                    ],
                ))

            if spatial_mgr.is_cleared():
                break

        return records
