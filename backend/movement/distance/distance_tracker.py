"""
L13 — Distance Tracking Engine

Maintains real-time distance measurements between registered entity pairs
across simulation ticks. Fires range-transition events when a pair crosses
a configured distance threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2


@dataclass(frozen=True)
class DistanceEvent:
    """Fired when a tracked pair crosses a range threshold."""

    event_type:  str    # "enter_range" | "leave_range" | "update"
    entity_a:    str
    entity_b:    str
    distance:    float
    time:        float


class DistanceTracker:
    """
    Tracks pairwise distances and emits events at range boundaries.

    Usage:
        tracker = DistanceTracker()
        tracker.track_pair("player", "enemy_1", threshold=10.0)
        events = tracker.update(positions, now=elapsed_time)
    """

    def __init__(self) -> None:
        self._pairs: dict[tuple[str, str], float | None] = {}  # pair → threshold (or None)
        self._current_distances: dict[tuple[str, str], float] = {}
        self._in_range: dict[tuple[str, str], bool] = {}
        self._history: dict[tuple[str, str], list[tuple[float, float]]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def track_pair(
        self,
        entity_a: str,
        entity_b: str,
        threshold: float | None = None,
    ) -> None:
        """
        Register a pair for tracking. *threshold* is the distance boundary
        that triggers enter_range / leave_range events (None → events disabled).
        """
        key = self._key(entity_a, entity_b)
        self._pairs[key] = threshold
        self._in_range[key] = False
        self._history[key] = []

    def untrack_pair(self, entity_a: str, entity_b: str) -> None:
        key = self._key(entity_a, entity_b)
        self._pairs.pop(key, None)
        self._current_distances.pop(key, None)
        self._in_range.pop(key, None)
        self._history.pop(key, None)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        positions: dict[str, Vector2],
        now: float = 0.0,
    ) -> list[DistanceEvent]:
        """
        Compute current distances for all tracked pairs.
        Returns a list of DistanceEvent objects for threshold crossings.
        """
        events: list[DistanceEvent] = []

        for (a, b), threshold in self._pairs.items():
            pos_a = positions.get(a)
            pos_b = positions.get(b)
            if pos_a is None or pos_b is None:
                continue

            dist = pos_a.distance_to(pos_b)
            self._current_distances[(a, b)] = dist
            self._history[(a, b)].append((now, dist))

            if threshold is not None:
                was_in = self._in_range.get((a, b), False)
                now_in = dist <= threshold
                if now_in and not was_in:
                    events.append(DistanceEvent("enter_range", a, b, dist, now))
                elif not now_in and was_in:
                    events.append(DistanceEvent("leave_range", a, b, dist, now))
                self._in_range[(a, b)] = now_in

        return events

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def current_distance(self, entity_a: str, entity_b: str) -> float | None:
        """Return the last computed distance for the pair, or None."""
        return self._current_distances.get(self._key(entity_a, entity_b))

    def is_in_range(self, entity_a: str, entity_b: str) -> bool:
        return self._in_range.get(self._key(entity_a, entity_b), False)

    def distance_history(
        self,
        entity_a: str,
        entity_b: str,
    ) -> list[tuple[float, float]]:
        """Return [(time, distance)] history list for the pair."""
        return list(self._history.get(self._key(entity_a, entity_b), []))

    def all_current_distances(self) -> dict[tuple[str, str], float]:
        return dict(self._current_distances)

    def tracked_pairs(self) -> list[tuple[str, str]]:
        return list(self._pairs.keys())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _key(a: str, b: str) -> tuple[str, str]:
        """Canonical ordering ensures (a,b) and (b,a) map to the same key."""
        return (a, b) if a <= b else (b, a)
