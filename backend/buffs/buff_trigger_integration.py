"""
H8 — Buff Trigger Integration

BuffTriggerIntegration wires the TriggerRegistry (H7) and SimulationState
(H4) together so that game events automatically apply or expire buffs.

Buff activations are stored as (buff_id, applied_at, duration) entries.
On each tick() call, expired buffs are removed from state and an
on_buff_expire event is fired for each one.
"""

from __future__ import annotations

from dataclasses import dataclass

from events.event_trigger import TriggerRegistry
from state.state_engine import SimulationState


@dataclass
class _ActiveBuff:
    buff_id:    str
    applied_at: float
    duration:   float | None  # None = permanent until explicitly removed


class BuffTriggerIntegration:
    """
    Manages buff lifecycle in conjunction with event triggers.

    activate_buff(buff_id, state, now, duration)
        — adds buff_id to state.active_buffs and records expiry
    tick(state, now, registry)
        — expires overdue buffs, fires on_buff_expire events
    deactivate_buff(buff_id, state, registry, now)
        — manually remove a buff and fire on_buff_expire
    """

    def __init__(self) -> None:
        self._active: dict[str, _ActiveBuff] = {}

    def activate_buff(
        self,
        buff_id: str,
        state: SimulationState,
        now: float,
        duration: float | None = None,
    ) -> None:
        """
        Apply *buff_id* to *state* at time *now* with optional *duration*.
        If the buff is already active it is refreshed (timer reset).
        """
        state.add_buff(buff_id)
        self._active[buff_id] = _ActiveBuff(
            buff_id=buff_id, applied_at=now, duration=duration
        )

    def tick(
        self,
        state: SimulationState,
        now: float,
        registry: TriggerRegistry,
    ) -> list[str]:
        """
        Check all active buffs for expiry at *now*.
        Removes expired buffs from *state* and fires on_buff_expire.
        Returns list of expired buff_ids.
        """
        expired: list[str] = []
        for buff_id, entry in list(self._active.items()):
            if entry.duration is not None and now >= entry.applied_at + entry.duration:
                state.remove_buff(buff_id)
                del self._active[buff_id]
                registry.fire("on_buff_expire", {"buff_id": buff_id, "time": now})
                expired.append(buff_id)
        return expired

    def deactivate_buff(
        self,
        buff_id: str,
        state: SimulationState,
        registry: TriggerRegistry,
        now: float,
    ) -> None:
        """Manually remove *buff_id* and fire on_buff_expire."""
        state.remove_buff(buff_id)
        self._active.pop(buff_id, None)
        registry.fire("on_buff_expire", {"buff_id": buff_id, "time": now})

    def is_tracked(self, buff_id: str) -> bool:
        return buff_id in self._active

    def active_buff_ids(self) -> list[str]:
        return sorted(self._active.keys())
