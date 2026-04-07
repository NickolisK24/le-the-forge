"""
BuffDefinition — Typed buff template integrated into the stat resolution system.

Uses existing StatModifier and Condition infrastructure:
  - ConditionalModifier from modifiers.models for stat effects
  - Condition from conditions.models for activation gates
  - Integrates with BuildStats for stat application

Supports:
  - Duration-based expiry (None = permanent)
  - Stacking with configurable behavior (REFRESH, INDEPENDENT, MAX_ONLY)
  - Conditional activation using the existing Condition system
  - Validation on construction (no invalid buffs can exist)
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional

from conditions.models.condition import Condition


# ---------------------------------------------------------------------------
# Stack behavior
# ---------------------------------------------------------------------------

class StackBehavior(enum.Enum):
    """How a buff handles re-application while already active."""

    REFRESH = "refresh"
    """Re-applying resets duration. Stack count stays at 1."""

    INDEPENDENT = "independent"
    """Each application creates a separate instance with its own timer."""

    MAX_ONLY = "max_only"
    """Only the highest-value instance is kept. Duration refreshed."""


# ---------------------------------------------------------------------------
# Stat modifier (reuses existing naming conventions)
# ---------------------------------------------------------------------------

VALID_MODIFIER_TYPES = frozenset({"additive", "multiplicative", "override"})


@dataclass(frozen=True, slots=True)
class StatModifier:
    """A single stat modification applied per stack of a buff.

    stat_target   — BuildStats field name (e.g. "spell_damage_pct", "crit_chance")
    value         — magnitude per stack
    modifier_type — how this modifier combines with the stat pool
    """
    stat_target: str
    value: float
    modifier_type: str = "additive"

    def __post_init__(self) -> None:
        if not self.stat_target:
            raise ValueError("stat_target must not be empty")
        if self.modifier_type not in VALID_MODIFIER_TYPES:
            raise ValueError(
                f"Invalid modifier_type {self.modifier_type!r}. "
                f"Must be one of: {sorted(VALID_MODIFIER_TYPES)}"
            )

    def scaled(self, stacks: int) -> float:
        """Return the effective value for the given stack count."""
        return self.value * stacks

    def to_dict(self) -> dict:
        return {
            "stat_target": self.stat_target,
            "value": self.value,
            "modifier_type": self.modifier_type,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StatModifier":
        return cls(
            stat_target=d["stat_target"],
            value=float(d["value"]),
            modifier_type=d.get("modifier_type", "additive"),
        )


# ---------------------------------------------------------------------------
# Buff definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class BuffDefinition:
    """Immutable buff template — the canonical definition of what a buff does.

    Validated on construction: no invalid BuffDefinition can exist.

    Fields:
        buff_id           — unique identifier (e.g. "berserk", "frenzy_charge")
        name              — display name
        stat_modifiers    — list of stat effects applied per stack
        duration_seconds  — time before expiry; None = permanent
        max_stacks        — maximum simultaneous stacks (≥ 1)
        stack_behavior    — how re-application is handled
        activation_condition — optional Condition that must be met for the buff to apply
        tags              — categorization tags (e.g. ["melee", "self_buff"])
        is_debuff         — True if this is a negative effect
        description       — human-readable description
    """
    buff_id: str
    name: str
    stat_modifiers: tuple[StatModifier, ...]
    duration_seconds: Optional[float] = None
    max_stacks: int = 1
    stack_behavior: StackBehavior = StackBehavior.REFRESH
    activation_condition: Optional[Condition] = None
    tags: tuple[str, ...] = ()
    is_debuff: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not self.buff_id:
            raise ValueError("buff_id must not be empty")
        if not self.name:
            raise ValueError("name must not be empty")
        if not self.stat_modifiers:
            raise ValueError("stat_modifiers must not be empty")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError(
                f"duration_seconds must be >= 0 or None (permanent), got {self.duration_seconds}"
            )
        if self.max_stacks < 1:
            raise ValueError(f"max_stacks must be >= 1, got {self.max_stacks}")

    @property
    def is_permanent(self) -> bool:
        """True if this buff has no duration limit."""
        return self.duration_seconds is None

    def aggregate_modifiers(self, stacks: int = 1) -> dict[str, float]:
        """Sum all stat modifiers scaled by stack count.

        Returns a flat dict: stat_target → total value.
        Compatible with BuildStats application.
        """
        clamped_stacks = min(max(stacks, 0), self.max_stacks)
        totals: dict[str, float] = {}
        for mod in self.stat_modifiers:
            totals[mod.stat_target] = totals.get(mod.stat_target, 0.0) + mod.scaled(clamped_stacks)
        return totals

    def to_dict(self) -> dict:
        return {
            "buff_id": self.buff_id,
            "name": self.name,
            "stat_modifiers": [m.to_dict() for m in self.stat_modifiers],
            "duration_seconds": self.duration_seconds,
            "max_stacks": self.max_stacks,
            "stack_behavior": self.stack_behavior.value,
            "activation_condition": self.activation_condition.to_dict() if self.activation_condition else None,
            "tags": list(self.tags),
            "is_debuff": self.is_debuff,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BuffDefinition":
        return cls(
            buff_id=d["buff_id"],
            name=d["name"],
            stat_modifiers=tuple(StatModifier.from_dict(m) for m in d["stat_modifiers"]),
            duration_seconds=d.get("duration_seconds"),
            max_stacks=d.get("max_stacks", 1),
            stack_behavior=StackBehavior(d.get("stack_behavior", "refresh")),
            activation_condition=Condition.from_dict(d["activation_condition"]) if d.get("activation_condition") else None,
            tags=tuple(d.get("tags", [])),
            is_debuff=d.get("is_debuff", False),
            description=d.get("description", ""),
        )
