"""
E2 — Stat Modifier Engine

Aggregates flat and percent modifiers from any source (gear, passives, buffs)
into a FinalModifierStack that can be applied to a BuildStats object.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ModifierType(str, Enum):
    FLAT    = "flat"
    PERCENT = "percent"


@dataclass
class StatModifier:
    """A single stat modifier from any source."""
    stat_key:      str
    value:         float
    modifier_type: ModifierType = ModifierType.FLAT

    def to_dict(self) -> dict:
        return {
            "stat_key":      self.stat_key,
            "value":         self.value,
            "modifier_type": self.modifier_type.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StatModifier":
        return cls(
            stat_key=d["stat_key"],
            value=float(d["value"]),
            modifier_type=ModifierType(d.get("modifier_type", "flat")),
        )


@dataclass
class FinalModifierStack:
    """
    Aggregated modifier totals, split by type.

    flat[stat_key]    = sum of all flat modifiers for that stat
    percent[stat_key] = sum of all percent modifiers for that stat
    """
    flat:    dict[str, float] = field(default_factory=dict)
    percent: dict[str, float] = field(default_factory=dict)

    def apply_to(self, stats_dict: dict) -> dict:
        """
        Return a copy of stats_dict with all modifiers applied.

        Flat modifiers are added directly.
        Percent modifiers increase the stat by that percentage:
            new_value = base * (1 + percent/100)
        """
        result = dict(stats_dict)
        for key, delta in self.flat.items():
            result[key] = result.get(key, 0.0) + delta
        for key, pct in self.percent.items():
            base = result.get(key, 0.0)
            result[key] = base * (1.0 + pct / 100.0)
        return result


class StatModifierEngine:
    """
    Collects StatModifier objects from multiple sources and computes
    a single FinalModifierStack.
    """

    def __init__(self) -> None:
        self._modifiers: list[StatModifier] = []

    def add_modifier(self, mod: StatModifier) -> None:
        self._modifiers.append(mod)

    def add_modifiers(self, mods: list[StatModifier]) -> None:
        self._modifiers.extend(mods)

    def reset(self) -> None:
        self._modifiers.clear()

    def compute(self) -> FinalModifierStack:
        """
        Aggregate all collected modifiers into a FinalModifierStack.
        Order of addition does not affect the totals (pure summation).
        """
        stack = FinalModifierStack()
        for mod in self._modifiers:
            if mod.modifier_type == ModifierType.FLAT:
                stack.flat[mod.stat_key] = stack.flat.get(mod.stat_key, 0.0) + mod.value
            else:
                stack.percent[mod.stat_key] = stack.percent.get(mod.stat_key, 0.0) + mod.value
        return stack

    def __len__(self) -> int:
        return len(self._modifiers)
