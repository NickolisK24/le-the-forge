"""
L18 — Movement Debug Logger

Ring-buffer event logger for movement simulation events. Records entity
movements, behavior changes, kite events, and range transitions for
post-run analysis and debugging. Shares the same capacity-bounded ring
pattern as K15's SpatialLogger.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from spatial.models.vector2 import Vector2


@dataclass(frozen=True)
class MovementLogEntry:
    """A single recorded movement event."""

    event_type: str   # move | behavior_change | kite | enter_range | leave_range | stop
    time:       float
    payload:    dict


class MovementLogger:
    """
    Ring-buffer logger for movement simulation events.

    capacity — maximum number of entries before oldest are evicted

    Methods:
        log_move(entity_id, from_pos, to_pos, distance, behavior, time)
        log_behavior_change(entity_id, old_behavior, new_behavior, time)
        log_kite_event(player_pos, closest_enemy_dist, time)
        log_range_event(event_type, entity_a, entity_b, distance, time)
        log_stop(entity_id, position, time)
        entries()  → list[dict]   serialisable (oldest first)
        clear()
    """

    def __init__(self, capacity: int = 500) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._buffer: deque[MovementLogEntry] = deque(maxlen=capacity)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_move(
        self,
        entity_id: str,
        from_pos: Vector2,
        to_pos: Vector2,
        distance: float,
        behavior: str = "unknown",
        time: float = 0.0,
    ) -> None:
        self._buffer.append(MovementLogEntry(
            event_type="move",
            time=time,
            payload={
                "entity_id": entity_id,
                "from":      from_pos.to_tuple(),
                "to":        to_pos.to_tuple(),
                "distance":  round(distance, 6),
                "behavior":  behavior,
            },
        ))

    def log_behavior_change(
        self,
        entity_id: str,
        old_behavior: str,
        new_behavior: str,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(MovementLogEntry(
            event_type="behavior_change",
            time=time,
            payload={
                "entity_id":    entity_id,
                "old_behavior": old_behavior,
                "new_behavior": new_behavior,
            },
        ))

    def log_kite_event(
        self,
        player_pos: Vector2,
        closest_enemy_dist: float,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(MovementLogEntry(
            event_type="kite",
            time=time,
            payload={
                "player_pos":           player_pos.to_tuple(),
                "closest_enemy_dist":   round(closest_enemy_dist, 4),
            },
        ))

    def log_range_event(
        self,
        event_type: str,   # "enter_range" or "leave_range"
        entity_a: str,
        entity_b: str,
        distance: float,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(MovementLogEntry(
            event_type=event_type,
            time=time,
            payload={
                "entity_a": entity_a,
                "entity_b": entity_b,
                "distance": round(distance, 4),
            },
        ))

    def log_stop(
        self,
        entity_id: str,
        position: Vector2,
        time: float = 0.0,
    ) -> None:
        self._buffer.append(MovementLogEntry(
            event_type="stop",
            time=time,
            payload={
                "entity_id": entity_id,
                "position":  position.to_tuple(),
            },
        ))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def entries(self) -> list[dict]:
        return [
            {"event_type": e.event_type, "time": e.time, "payload": e.payload}
            for e in self._buffer
        ]

    def entries_by_type(self, event_type: str) -> list[dict]:
        return [e for e in self.entries() if e["event_type"] == event_type]

    def clear(self) -> None:
        self._buffer.clear()

    @property
    def count(self) -> int:
        return len(self._buffer)

    @property
    def capacity(self) -> int:
        return self._capacity
