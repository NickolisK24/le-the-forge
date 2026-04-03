"""
L16 — Movement Metrics Collector

Tracks aggregate movement statistics for entities across a simulation run.
Metrics: total distance, time in/out of range, reposition count, kite events,
movement efficiency, per-entity breakdowns.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class MovementMetrics:
    """
    Mutable movement metrics collector.

    record_movement(entity_id, distance)
    record_time_in_range(entity_id, target_id, duration)
    record_time_out_of_range(entity_id, target_id, duration)
    record_reposition(entity_id, time)
    record_kite_event(time)
    record_behavior_change(entity_id, old, new, time)
    summary() → dict
    """

    def __init__(self) -> None:
        self._distance:         dict[str, float] = {}
        self._time_in_range:    dict[str, float] = {}   # key = f"{a}:{b}"
        self._time_out_range:   dict[str, float] = {}
        self._repositions:      dict[str, list[float]] = {}   # entity_id → [times]
        self._kite_events:      list[float] = []
        self._behavior_changes: list[dict] = []
        self._total_time:       float = 0.0

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_movement(self, entity_id: str, distance: float) -> None:
        self._distance[entity_id] = self._distance.get(entity_id, 0.0) + distance

    def record_time_in_range(
        self,
        entity_id: str,
        target_id: str,
        duration: float,
    ) -> None:
        key = f"{entity_id}:{target_id}"
        self._time_in_range[key] = self._time_in_range.get(key, 0.0) + duration

    def record_time_out_of_range(
        self,
        entity_id: str,
        target_id: str,
        duration: float,
    ) -> None:
        key = f"{entity_id}:{target_id}"
        self._time_out_range[key] = self._time_out_range.get(key, 0.0) + duration

    def record_reposition(self, entity_id: str, time: float) -> None:
        self._repositions.setdefault(entity_id, []).append(time)

    def record_kite_event(self, time: float) -> None:
        self._kite_events.append(time)

    def record_behavior_change(
        self,
        entity_id: str,
        old_behavior: str,
        new_behavior: str,
        time: float,
    ) -> None:
        self._behavior_changes.append({
            "entity_id": entity_id,
            "from":      old_behavior,
            "to":        new_behavior,
            "time":      time,
        })

    def record_total_time(self, duration: float) -> None:
        self._total_time += duration

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def total_distance(self, entity_id: str | None = None) -> float:
        if entity_id is not None:
            return self._distance.get(entity_id, 0.0)
        return sum(self._distance.values())

    def time_in_range(self, entity_id: str, target_id: str) -> float:
        return self._time_in_range.get(f"{entity_id}:{target_id}", 0.0)

    def time_out_of_range(self, entity_id: str, target_id: str) -> float:
        return self._time_out_range.get(f"{entity_id}:{target_id}", 0.0)

    def reposition_count(self, entity_id: str | None = None) -> int:
        if entity_id is not None:
            return len(self._repositions.get(entity_id, []))
        return sum(len(v) for v in self._repositions.values())

    def kite_count(self) -> int:
        return len(self._kite_events)

    def movement_efficiency(self, entity_id: str) -> float:
        """
        Distance traveled divided by total simulation time.
        Returns 0.0 if total_time is 0.
        """
        if self._total_time <= 0:
            return 0.0
        return self._distance.get(entity_id, 0.0) / self._total_time

    def all_entities(self) -> list[str]:
        return list(self._distance.keys())

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "total_distance_all":  round(self.total_distance(), 4),
            "distance_per_entity": {
                eid: round(d, 4) for eid, d in self._distance.items()
            },
            "repositions":         {
                eid: len(ts) for eid, ts in self._repositions.items()
            },
            "total_repositions":   self.reposition_count(),
            "kite_events":         self.kite_count(),
            "behavior_changes":    len(self._behavior_changes),
            "total_time":          round(self._total_time, 4),
        }

    def reset(self) -> None:
        self.__init__()  # type: ignore[misc]
