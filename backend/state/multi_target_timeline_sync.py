"""
I11 — Multi-Target Timeline Synchronization

Extends the single-target TimelineSynchronizer concept to operate over
a MultiTargetState. On each tick:
  1. Advance clock
  2. Expire per-target statuses via MultiTargetStatusManager
  3. Fire on_kill / remove dead via LifecycleManager
  4. Record tick snapshot
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from state.multi_target_state import MultiTargetState
from status.multi_target_status_manager import MultiTargetStatusManager
from targets.lifecycle_manager import LifecycleManager, KillRecord
from events.event_trigger import TriggerRegistry


@dataclass
class MultiTargetTickRecord:
    time:          float
    alive_count:   int
    kills:         list[str] = field(default_factory=list)   # target_ids killed this tick
    expired_statuses: dict[str, list[str]] = field(default_factory=dict)


class MultiTargetTimelineSynchronizer:
    """
    run(state, duration, status_mgr, lifecycle, registry, tick_size)
        → list[MultiTargetTickRecord]

    Advances *state* for *duration* seconds. Stops early if all targets die.
    """

    def __init__(self, tick_size: float = 0.1, record_snapshots: bool = True) -> None:
        if tick_size <= 0:
            raise ValueError("tick_size must be > 0")
        self.tick_size = tick_size
        self.record_snapshots = record_snapshots

    def run(
        self,
        state: MultiTargetState,
        duration: float,
        status_mgr: MultiTargetStatusManager | None = None,
        lifecycle: LifecycleManager | None = None,
        registry: TriggerRegistry | None = None,
    ) -> list[MultiTargetTickRecord]:
        if duration <= 0:
            raise ValueError("duration must be > 0")

        _registry  = registry  or TriggerRegistry()
        _lifecycle = lifecycle or LifecycleManager()
        records: list[MultiTargetTickRecord] = []

        n_ticks = math.ceil(duration / self.tick_size)
        for i in range(n_ticks):
            if state.is_cleared():
                break
            step = min(self.tick_size, duration - i * self.tick_size)
            if step <= 0:
                break
            state.advance_time(step)
            now = state.elapsed_time

            expired: dict[str, list[str]] = {}
            if status_mgr:
                expired = status_mgr.tick_all(now)

            kills = _lifecycle.process(state.manager, _registry, now)
            kill_ids = [k.target_id for k in kills]

            if self.record_snapshots:
                records.append(MultiTargetTickRecord(
                    time=round(now, 6),
                    alive_count=state.alive_count(),
                    kills=kill_ids,
                    expired_statuses=expired,
                ))

        return records
