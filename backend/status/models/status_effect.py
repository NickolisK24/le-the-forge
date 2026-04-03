"""
H5 — Status Effect Model

A StatusEffect describes a persistent effect that can be applied to a
target (or the player) and tracked by the StatusManager (H6).

effect_type values:
    dot        — damage-over-time (deals damage each tick)
    debuff     — reduces a target stat
    cc         — crowd-control (stun, freeze, etc.)
    amplifier  — increases incoming damage
"""

from __future__ import annotations

from dataclasses import dataclass, field

VALID_EFFECT_TYPES = frozenset({"dot", "debuff", "cc", "amplifier"})


@dataclass
class StatusEffect:
    """
    Descriptor for one type of status effect.

    status_id    — unique identifier (e.g. "shock", "ignite")
    duration     — how many seconds each application lasts (>0)
    stack_limit  — maximum concurrent stacks; None = unlimited
    effect_type  — one of VALID_EFFECT_TYPES
    value        — magnitude per stack (e.g. DPS for dot, % reduction for debuff)
    """
    status_id:   str
    duration:    float
    stack_limit: int | None = None
    effect_type: str        = "dot"
    value:       float      = 0.0

    def __post_init__(self) -> None:
        if not self.status_id:
            raise ValueError("status_id must not be empty")
        if self.duration <= 0:
            raise ValueError("duration must be > 0")
        if self.stack_limit is not None and self.stack_limit < 1:
            raise ValueError("stack_limit must be >= 1 when specified")
        if self.effect_type not in VALID_EFFECT_TYPES:
            raise ValueError(
                f"Invalid effect_type {self.effect_type!r}. "
                f"Must be one of: {sorted(VALID_EFFECT_TYPES)}"
            )

    def is_expired(self, applied_at: float, now: float) -> bool:
        """True when the application at *applied_at* has passed its duration."""
        return now >= applied_at + self.duration

    def to_dict(self) -> dict:
        return {
            "status_id":   self.status_id,
            "duration":    self.duration,
            "stack_limit": self.stack_limit,
            "effect_type": self.effect_type,
            "value":       self.value,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StatusEffect":
        return cls(
            status_id=d["status_id"],
            duration=d["duration"],
            stack_limit=d.get("stack_limit"),
            effect_type=d.get("effect_type", "dot"),
            value=d.get("value", 0.0),
        )
