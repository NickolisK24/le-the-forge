"""
I13 — Multi-Target Metrics Engine

Tracks performance statistics across all targets in a simulation run.

Metrics tracked:
    total_kills        — number of targets that died
    time_to_clear      — set externally when all targets are dead
    damage_per_target  — {target_id: total_damage_dealt}
    overkill_waste     — {target_id: total_overkill}
    kill_times         — {target_id: time_of_death}
"""

from __future__ import annotations

from dataclasses import dataclass, field


class MultiTargetMetrics:
    def __init__(self) -> None:
        self._kills:            list[tuple[str, float]] = []     # (target_id, time)
        self._damage:           dict[str, float] = {}
        self._overkill:         dict[str, float] = {}

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_hit(self, target_id: str, damage: float, overkill: float = 0.0) -> None:
        self._damage[target_id]   = self._damage.get(target_id, 0.0)   + damage
        self._overkill[target_id] = self._overkill.get(target_id, 0.0) + overkill

    def record_kill(self, target_id: str, time: float) -> None:
        self._kills.append((target_id, time))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def total_kills(self) -> int:
        return len(self._kills)

    def damage_per_target(self) -> dict[str, float]:
        return dict(self._damage)

    def overkill_waste(self) -> dict[str, float]:
        return dict(self._overkill)

    def kill_times(self) -> dict[str, float]:
        return {tid: t for tid, t in self._kills}

    def time_to_clear(self) -> float | None:
        """Time of last kill, or None if no kills recorded."""
        if not self._kills:
            return None
        return max(t for _, t in self._kills)

    def summary(self) -> dict:
        return {
            "total_kills":       self.total_kills,
            "time_to_clear":     self.time_to_clear(),
            "damage_per_target": self.damage_per_target(),
            "overkill_waste":    self.overkill_waste(),
            "kill_times":        self.kill_times(),
        }
