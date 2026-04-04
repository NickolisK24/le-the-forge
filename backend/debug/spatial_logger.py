"""
K15 — Spatial Debug Logger

Ring-buffer event logger for spatial simulation events. Records projectile
spawns, collisions, kills, and AoE activations for post-run analysis and
visual debugging. Keeps only the last *capacity* entries to bound memory.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile


@dataclass(frozen=True)
class SpatialLogEntry:
    """A single recorded spatial event."""

    event_type:  str    # spawn | hit | miss | kill | aoe | expire
    time:        float
    payload:     dict


class SpatialLogger:
    """
    Bounded ring-buffer logger for spatial events.

    capacity  — maximum number of entries kept (oldest entries are discarded)

    Methods:
        log_projectile_spawn(projectile, time)
        log_hit(target_id, damage, position, is_critical, time)
        log_miss(projectile_id, position, time)
        log_target_killed(target_id, time)
        log_aoe(shape_dict, targets_hit, total_damage, time)
        log_expire(projectile_id, distance_traveled, time)
        entries()   → list[dict]   serialisable snapshot (oldest first)
        clear()
    """

    def __init__(self, capacity: int = 500) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._buffer: deque[SpatialLogEntry] = deque(maxlen=capacity)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_projectile_spawn(
        self,
        projectile: Projectile,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="spawn",
            time=time,
            payload={
                "projectile_id": projectile.projectile_id,
                "skill_id":      projectile.skill_id,
                "origin":        projectile.origin.to_tuple(),
                "direction":     projectile.direction.to_tuple(),
                "speed":         projectile.speed,
                "damage":        projectile.damage,
                "pierce_count":  projectile.pierce_count,
            },
        ))

    def log_hit(
        self,
        target_id: str,
        damage: float,
        position: Vector2,
        is_critical: bool = False,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="hit",
            time=time,
            payload={
                "target_id":   target_id,
                "damage":      round(damage, 4),
                "position":    position.to_tuple(),
                "is_critical": is_critical,
            },
        ))

    def log_miss(
        self,
        projectile_id: str,
        position: Vector2,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="miss",
            time=time,
            payload={
                "projectile_id": projectile_id,
                "position":      position.to_tuple(),
            },
        ))

    def log_target_killed(
        self,
        target_id: str,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="kill",
            time=time,
            payload={"target_id": target_id},
        ))

    def log_aoe(
        self,
        shape_dict: dict,
        targets_hit: int,
        total_damage: float,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="aoe",
            time=time,
            payload={
                "shape":        shape_dict,
                "targets_hit":  targets_hit,
                "total_damage": round(total_damage, 4),
            },
        ))

    def log_expire(
        self,
        projectile_id: str,
        distance_traveled: float,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(SpatialLogEntry(
            event_type="expire",
            time=time,
            payload={
                "projectile_id":     projectile_id,
                "distance_traveled": round(distance_traveled, 6),
            },
        ))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def entries(self) -> list[dict]:
        """Return all entries as serialisable dicts (oldest first)."""
        return [
            {
                "event_type": e.event_type,
                "time":       e.time,
                "payload":    e.payload,
            }
            for e in self._buffer
        ]

    def entries_by_type(self, event_type: str) -> list[dict]:
        """Return only entries matching *event_type*."""
        return [e for e in self.entries() if e["event_type"] == event_type]

    def clear(self) -> None:
        self._buffer.clear()

    @property
    def count(self) -> int:
        return len(self._buffer)

    @property
    def capacity(self) -> int:
        return self._capacity
