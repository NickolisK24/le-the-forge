"""
G2 — RotationStep Model

One entry in a rotation sequence.

Fields
------
skill_id:        Matches a SkillDefinition.skill_id.
delay_after_cast: Extra seconds of intentional pause after the cast resolves
                  before the executor may cast the next skill.
priority:        Lower value = higher priority when multiple skills are ready
                  simultaneously. Default 0.
repeat_count:    How many times this step repeats consecutively before
                  the rotation advances. 1 = cast once (default).
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RotationStep:
    skill_id:         str
    delay_after_cast: float = 0.0
    priority:         int   = 0
    repeat_count:     int   = 1

    def __post_init__(self) -> None:
        if not self.skill_id:
            raise ValueError("skill_id must be non-empty")
        if self.delay_after_cast < 0:
            raise ValueError(
                f"delay_after_cast must be >= 0, got {self.delay_after_cast}"
            )
        if self.repeat_count < 1:
            raise ValueError(
                f"repeat_count must be >= 1, got {self.repeat_count}"
            )

    def to_dict(self) -> dict:
        return {
            "skill_id":         self.skill_id,
            "delay_after_cast": self.delay_after_cast,
            "priority":         self.priority,
            "repeat_count":     self.repeat_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RotationStep":
        return cls(
            skill_id         = d["skill_id"],
            delay_after_cast = float(d.get("delay_after_cast", 0.0)),
            priority         = int(d.get("priority", 0)),
            repeat_count     = int(d.get("repeat_count", 1)),
        )
