"""
H6 — Status Manager

Tracks active status effect applications for a single simulation target.
Each application is recorded as (status_id, applied_at) so expiration can
be computed against elapsed_time.

The manager enforces stack_limit per StatusEffect definition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from status.models.status_effect import StatusEffect


@dataclass
class _Application:
    """One live application of a status effect."""
    status_id:  str
    applied_at: float


class StatusManager:
    """
    Manages status effect application, expiration, and stack counts
    for one simulation target.

    Usage::
        mgr = StatusManager()
        mgr.register(shock_effect)
        mgr.apply("shock", now=0.5)
        mgr.tick(now=2.0)           # expire stale applications
        count = mgr.stack_count("shock")
    """

    def __init__(self) -> None:
        self._definitions: dict[str, StatusEffect] = {}
        self._applications: list[_Application] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, effect: StatusEffect) -> None:
        """Register a StatusEffect definition so it can be applied."""
        self._definitions[effect.status_id] = effect

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    def apply(self, status_id: str, now: float) -> int:
        """
        Apply one stack of *status_id* at time *now*.
        Returns the new stack count.
        Respects stack_limit — excess applications are silently ignored.
        Raises KeyError if the effect has not been registered.
        """
        effect = self._definitions[status_id]
        current = self.stack_count(status_id)
        if effect.stack_limit is not None and current >= effect.stack_limit:
            return current
        self._applications.append(_Application(status_id=status_id, applied_at=now))
        return current + 1

    # ------------------------------------------------------------------
    # Expiration
    # ------------------------------------------------------------------

    def tick(self, now: float) -> list[str]:
        """
        Remove all applications whose duration has elapsed at *now*.
        Returns a list of status_ids that were removed (may contain duplicates).
        """
        expired: list[str] = []
        remaining: list[_Application] = []
        for app in self._applications:
            effect = self._definitions.get(app.status_id)
            if effect and effect.is_expired(app.applied_at, now):
                expired.append(app.status_id)
            else:
                remaining.append(app)
        self._applications = remaining
        return expired

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def stack_count(self, status_id: str) -> int:
        """Current number of active stacks for *status_id*."""
        return sum(1 for a in self._applications if a.status_id == status_id)

    def is_active(self, status_id: str) -> bool:
        return self.stack_count(status_id) > 0

    def active_status_ids(self) -> list[str]:
        """Sorted list of status_ids with at least one active stack."""
        return sorted({a.status_id for a in self._applications})

    def total_value(self, status_id: str) -> float:
        """
        Aggregate value for all active stacks of *status_id*.
        Returns 0 if the status is not registered or not active.
        """
        effect = self._definitions.get(status_id)
        if not effect:
            return 0.0
        return effect.value * self.stack_count(status_id)

    def clear(self) -> None:
        """Remove all active applications."""
        self._applications.clear()
