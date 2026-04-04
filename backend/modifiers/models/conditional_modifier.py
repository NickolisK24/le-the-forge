"""
H3 — Conditional Modifier Model

A ConditionalModifier pairs a stat delta with a Condition that gates
whether the modifier is currently active. The modifier is inactive (value
= 0) when its condition evaluates to False.

modifier_type values:
    additive        — add value directly to the stat
    multiplicative  — multiply the stat by (1 + value/100)
    override        — replace the stat with value entirely
"""

from __future__ import annotations

from dataclasses import dataclass

from conditions.models.condition import Condition

VALID_MODIFIER_TYPES = frozenset({"additive", "multiplicative", "override"})


@dataclass(frozen=True)
class ConditionalModifier:
    """
    A stat modifier that only applies when its linked Condition is met.

    modifier_id   — unique identifier
    stat_target   — the stat field name this modifier affects
                    (e.g. "spell_damage_pct", "crit_chance")
    value         — delta magnitude
    modifier_type — "additive" | "multiplicative" | "override"
    condition     — the Condition that must evaluate True for this to apply
    """
    modifier_id:   str
    stat_target:   str
    value:         float
    modifier_type: str
    condition:     Condition

    def __post_init__(self) -> None:
        if not self.modifier_id:
            raise ValueError("modifier_id must not be empty")
        if not self.stat_target:
            raise ValueError("stat_target must not be empty")
        if self.modifier_type not in VALID_MODIFIER_TYPES:
            raise ValueError(
                f"Invalid modifier_type {self.modifier_type!r}. "
                f"Must be one of: {sorted(VALID_MODIFIER_TYPES)}"
            )

    def to_dict(self) -> dict:
        return {
            "modifier_id":   self.modifier_id,
            "stat_target":   self.stat_target,
            "value":         self.value,
            "modifier_type": self.modifier_type,
            "condition":     self.condition.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ConditionalModifier":
        return cls(
            modifier_id=d["modifier_id"],
            stat_target=d["stat_target"],
            value=d["value"],
            modifier_type=d["modifier_type"],
            condition=Condition.from_dict(d["condition"]),
        )
