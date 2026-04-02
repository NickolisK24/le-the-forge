"""
E5 — Buff System

Handles temporary stat boosts applied to a build.
Buffs with duration=None are permanent for the duration of a fight.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Buff:
    """
    A single buff with optional duration and a set of stat modifiers.

    modifiers maps BuildStats field names to delta values:
        {"spell_damage_pct": 20.0, "crit_chance": 0.1}
    """
    buff_id: str
    modifiers: dict[str, float] = field(default_factory=dict)
    duration: float | None = None  # None = permanent / fight-long

    def is_active(self, elapsed: float) -> bool:
        """True if the buff is still active at the given elapsed time."""
        if self.duration is None:
            return True
        return elapsed < self.duration

    def to_dict(self) -> dict:
        return {
            "buff_id":   self.buff_id,
            "duration":  self.duration,
            "modifiers": dict(self.modifiers),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Buff":
        return cls(
            buff_id=d["buff_id"],
            modifiers=dict(d.get("modifiers", {})),
            duration=d.get("duration"),
        )


class BuffSystem:
    """Manages a collection of buffs and aggregates their stat modifiers."""

    def __init__(self, buffs: list[Buff] | None = None) -> None:
        self._buffs: dict[str, Buff] = {}
        for b in (buffs or []):
            self._buffs[b.buff_id] = b

    def add_buff(self, buff: Buff) -> None:
        self._buffs[buff.buff_id] = buff

    def remove_buff(self, buff_id: str) -> None:
        self._buffs.pop(buff_id, None)

    def get_active_buffs(self, elapsed: float = 0.0) -> list[Buff]:
        """Return all buffs still active at `elapsed` seconds."""
        return [b for b in self._buffs.values() if b.is_active(elapsed)]

    def aggregate_modifiers(self, elapsed: float = 0.0) -> dict[str, float]:
        """
        Sum all active buff modifiers into a flat stat_key → total dict.
        Multiple buffs with the same stat_key stack additively.
        """
        totals: dict[str, float] = {}
        for buff in self.get_active_buffs(elapsed):
            for stat_key, value in buff.modifiers.items():
                totals[stat_key] = totals.get(stat_key, 0.0) + value
        return totals

    def all_buffs(self) -> list[Buff]:
        return list(self._buffs.values())

    def __len__(self) -> int:
        return len(self._buffs)
