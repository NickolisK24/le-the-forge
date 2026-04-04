"""
I9 — Multi-Target Status Manager

Wraps one StatusManager per target, providing isolated status tracking
so that e.g. "shock" on target A is independent of "shock" on target B.
"""

from __future__ import annotations

from status.models.status_effect import StatusEffect
from status.status_manager import StatusManager


class MultiTargetStatusManager:
    """
    Manages independent StatusManagers keyed by target_id.

    register(effect)          — register a StatusEffect for all targets
    apply(target_id, sid, now) — apply one stack to a specific target
    tick(target_id, now)       — expire stacks for a target, return expired ids
    tick_all(now)              — expire stacks for all targets
    stack_count(target_id, sid) — active stacks on one target
    is_active(target_id, sid)   — bool
    total_value(target_id, sid) — aggregate value for stacks on one target
    """

    def __init__(self) -> None:
        self._definitions: dict[str, StatusEffect] = {}
        self._managers: dict[str, StatusManager] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, effect: StatusEffect) -> None:
        """Register effect globally so it can be applied to any target."""
        self._definitions[effect.status_id] = effect
        # Propagate to any existing per-target managers
        for mgr in self._managers.values():
            mgr.register(effect)

    def _get_or_create(self, target_id: str) -> StatusManager:
        if target_id not in self._managers:
            mgr = StatusManager()
            for effect in self._definitions.values():
                mgr.register(effect)
            self._managers[target_id] = mgr
        return self._managers[target_id]

    # ------------------------------------------------------------------
    # Per-target operations
    # ------------------------------------------------------------------

    def apply(self, target_id: str, status_id: str, now: float) -> int:
        return self._get_or_create(target_id).apply(status_id, now)

    def tick(self, target_id: str, now: float) -> list[str]:
        if target_id not in self._managers:
            return []
        return self._managers[target_id].tick(now)

    def tick_all(self, now: float) -> dict[str, list[str]]:
        """Expire statuses for all tracked targets. Returns {target_id: [expired_ids]}."""
        return {
            tid: mgr.tick(now)
            for tid, mgr in self._managers.items()
        }

    def stack_count(self, target_id: str, status_id: str) -> int:
        mgr = self._managers.get(target_id)
        return mgr.stack_count(status_id) if mgr else 0

    def is_active(self, target_id: str, status_id: str) -> bool:
        return self.stack_count(target_id, status_id) > 0

    def total_value(self, target_id: str, status_id: str) -> float:
        mgr = self._managers.get(target_id)
        return mgr.total_value(status_id) if mgr else 0.0

    def active_status_ids(self, target_id: str) -> list[str]:
        mgr = self._managers.get(target_id)
        return mgr.active_status_ids() if mgr else []

    def clear_target(self, target_id: str) -> None:
        if target_id in self._managers:
            self._managers[target_id].clear()

    def clear_all(self) -> None:
        for mgr in self._managers.values():
            mgr.clear()
