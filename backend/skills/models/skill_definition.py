"""
G1 — SkillDefinition Model

Represents a single skill as used in rotation simulation.
Intentionally DB-free — pure Python dataclass.

Fields
------
skill_id:       Unique string identifier (e.g. "rip_blood", "fireball").
base_damage:    Flat damage per cast before any stat scaling.
cast_time:      Time (seconds) the cast takes; 0 = instant.
cooldown:       Minimum seconds between uses; 0 = no cooldown.
resource_cost:  Resource (mana/rage/etc.) consumed per cast; 0 = free.
tags:           Arbitrary tag strings used for scaling lookups
                (e.g. ["spell", "fire", "dot"]).
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SkillDefinition:
    skill_id:      str
    base_damage:   float          = 0.0
    cast_time:     float          = 0.0   # seconds
    cooldown:      float          = 0.0   # seconds
    resource_cost: float          = 0.0
    tags:          list[str]      = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.skill_id:
            raise ValueError("skill_id must be a non-empty string")
        if self.cast_time < 0:
            raise ValueError(f"cast_time must be >= 0, got {self.cast_time}")
        if self.cooldown < 0:
            raise ValueError(f"cooldown must be >= 0, got {self.cooldown}")
        if self.resource_cost < 0:
            raise ValueError(f"resource_cost must be >= 0, got {self.resource_cost}")
        # Normalise tags to lowercase strings
        self.tags = [str(t).lower() for t in self.tags]

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "skill_id":      self.skill_id,
            "base_damage":   self.base_damage,
            "cast_time":     self.cast_time,
            "cooldown":      self.cooldown,
            "resource_cost": self.resource_cost,
            "tags":          list(self.tags),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SkillDefinition":
        return cls(
            skill_id      = d["skill_id"],
            base_damage   = float(d.get("base_damage",   0.0)),
            cast_time     = float(d.get("cast_time",     0.0)),
            cooldown      = float(d.get("cooldown",      0.0)),
            resource_cost = float(d.get("resource_cost", 0.0)),
            tags          = list(d.get("tags", [])),
        )
