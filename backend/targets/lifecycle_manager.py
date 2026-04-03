"""
I10 — Target Lifecycle Manager

Detects kill events after damage is applied, fires on_kill triggers
via TriggerRegistry, and removes dead targets from the TargetManager.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from targets.target_manager import TargetManager
from events.event_trigger import TriggerRegistry


@dataclass
class KillRecord:
    target_id:   str
    killed_at:   float     # elapsed_time when death was detected


class LifecycleManager:
    """
    process(manager, registry, now) → list[KillRecord]

    Scans all targets in *manager* for newly dead ones, fires an
    on_kill event for each, removes them from the manager, and
    returns a list of KillRecords describing what died.
    """

    def __init__(self) -> None:
        self._kill_log: list[KillRecord] = []

    def process(
        self,
        manager: TargetManager,
        registry: TriggerRegistry,
        now: float,
    ) -> list[KillRecord]:
        """
        Detect dead targets, fire on_kill events, remove from manager.
        Returns newly processed kills.
        """
        newly_killed: list[KillRecord] = []
        for target in manager.all_targets():
            if not target.is_alive:
                record = KillRecord(target_id=target.target_id, killed_at=now)
                registry.fire("on_kill", {
                    "target_id": target.target_id,
                    "time":      now,
                })
                newly_killed.append(record)
                self._kill_log.append(record)

        # Remove after iteration to avoid mutation-during-iteration
        for record in newly_killed:
            manager.remove(record.target_id)

        return newly_killed

    def kill_log(self) -> list[KillRecord]:
        return list(self._kill_log)

    def total_kills(self) -> int:
        return len(self._kill_log)

    def reset(self) -> None:
        self._kill_log.clear()
