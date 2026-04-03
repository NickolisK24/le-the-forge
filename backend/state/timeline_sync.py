"""
H12 — Timeline State Synchronization

TimelineSynchronizer advances SimulationState through a series of discrete
time ticks. On each tick it:
  1. Advances the simulation clock
  2. Expires status effects (via StatusManager)
  3. Expires buffs (via BuffTriggerIntegration)
  4. Fires health threshold callbacks
  5. Records a state snapshot at each tick (for debugging / replay)

This provides the integration glue between the time-aware subsystems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from state.state_engine import SimulationState
from state.health_thresholds import HealthThresholdTracker
from status.status_manager import StatusManager
from buffs.buff_trigger_integration import BuffTriggerIntegration
from events.event_trigger import TriggerRegistry


@dataclass
class TickRecord:
    """Snapshot captured at one simulation tick."""
    time:       float
    state:      dict   # SimulationState.snapshot()
    expired_statuses: list[str] = field(default_factory=list)
    expired_buffs:    list[str] = field(default_factory=list)
    threshold_fires:  list[float] = field(default_factory=list)


class TimelineSynchronizer:
    """
    Drives a simulation forward tick-by-tick.

    __init__(tick_size, record_snapshots)
        tick_size         — seconds per tick (default 0.1)
        record_snapshots  — if True, store a TickRecord for every tick

    run(state, duration, status_mgr, buff_integration, threshold_tracker, registry)
        → list[TickRecord]
        Advances *state* for *duration* seconds and returns all records.
    """

    def __init__(
        self,
        tick_size: float = 0.1,
        record_snapshots: bool = True,
    ) -> None:
        if tick_size <= 0:
            raise ValueError("tick_size must be > 0")
        self.tick_size = tick_size
        self.record_snapshots = record_snapshots

    def run(
        self,
        state: SimulationState,
        duration: float,
        status_mgr: StatusManager | None = None,
        buff_integration: BuffTriggerIntegration | None = None,
        threshold_tracker: HealthThresholdTracker | None = None,
        registry: TriggerRegistry | None = None,
    ) -> list[TickRecord]:
        """
        Advance *state* for *duration* seconds in steps of self.tick_size.
        Returns recorded tick history (empty list if record_snapshots=False).
        """
        if duration <= 0:
            raise ValueError("duration must be > 0")

        _registry = registry or TriggerRegistry()
        records: list[TickRecord] = []

        n_ticks = math.ceil(duration / self.tick_size)
        for i in range(n_ticks):
            step = min(self.tick_size, duration - i * self.tick_size)
            if step <= 0:
                break
            state.advance_time(step)
            now = state.elapsed_time

            expired_statuses: list[str] = []
            expired_buffs: list[str] = []
            threshold_fires: list[float] = []

            if status_mgr:
                expired_statuses = status_mgr.tick(now)
                # Sync status effects back into state
                for sid in status_mgr.active_status_ids():
                    state.active_status_effects[sid] = status_mgr.stack_count(sid)
                # Remove expired from state
                for sid in expired_statuses:
                    if status_mgr.stack_count(sid) == 0:
                        state.remove_status(sid)

            if buff_integration:
                expired_buffs = buff_integration.tick(state, now, _registry)

            if threshold_tracker:
                threshold_fires = threshold_tracker.update(state.target_health_pct)

            if self.record_snapshots:
                records.append(TickRecord(
                    time=round(now, 6),
                    state=state.snapshot(),
                    expired_statuses=expired_statuses,
                    expired_buffs=expired_buffs,
                    threshold_fires=threshold_fires,
                ))

        return records
