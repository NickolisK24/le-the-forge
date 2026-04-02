"""
G4 — CooldownTracker

Tracks per-skill cooldown expiry times on a float simulation clock.

Usage
-----
    tracker = CooldownTracker()
    tracker.start(skill_id, current_time, cooldown_duration)
    tracker.is_ready(skill_id, current_time)  # True when expired
    tracker.time_remaining(skill_id, current_time)  # 0.0 when ready
"""

from __future__ import annotations


class CooldownTracker:
    """
    Tracks when each skill becomes available again.

    Internally stores {skill_id: ready_at_time}.  Skills that have never
    been put on cooldown are always considered ready.
    """

    def __init__(self) -> None:
        self._ready_at: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def start(self, skill_id: str, current_time: float, duration: float) -> None:
        """
        Place `skill_id` on cooldown for `duration` seconds starting
        at `current_time`.  A duration of 0 is a no-op.
        """
        if duration <= 0:
            return
        self._ready_at[skill_id] = current_time + duration

    def reset(self, skill_id: str) -> None:
        """Remove any active cooldown for `skill_id` immediately."""
        self._ready_at.pop(skill_id, None)

    def reset_all(self) -> None:
        """Clear all tracked cooldowns."""
        self._ready_at.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def is_ready(self, skill_id: str, current_time: float) -> bool:
        """Return True if the skill has no active cooldown at `current_time`."""
        ready_at = self._ready_at.get(skill_id)
        if ready_at is None:
            return True
        return current_time >= ready_at

    def time_remaining(self, skill_id: str, current_time: float) -> float:
        """Return seconds until the skill is ready (0.0 if already ready)."""
        ready_at = self._ready_at.get(skill_id)
        if ready_at is None:
            return 0.0
        return max(0.0, ready_at - current_time)

    def ready_skills(self, skill_ids: list[str], current_time: float) -> list[str]:
        """Return the subset of `skill_ids` that are currently ready."""
        return [sid for sid in skill_ids if self.is_ready(sid, current_time)]

    def all_ready_at(self) -> dict[str, float]:
        """Return a copy of the internal {skill_id: ready_at} map."""
        return dict(self._ready_at)
