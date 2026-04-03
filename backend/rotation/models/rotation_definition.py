"""
G3 — RotationDefinition

An ordered list of RotationSteps that the executor cycles through.

Fields
------
rotation_id:  Unique name for this rotation (e.g. "acolyte_basic").
steps:        Ordered list of RotationStep objects.
loop:         If True the executor restarts from step 0 after completing
              the last step. Default True.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from rotation.models.rotation_step import RotationStep


@dataclass
class RotationDefinition:
    rotation_id: str
    steps:       list[RotationStep] = field(default_factory=list)
    loop:        bool               = True

    def __post_init__(self) -> None:
        if not self.rotation_id:
            raise ValueError("rotation_id must be non-empty")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_step(self, step: RotationStep) -> None:
        self.steps.append(step)

    def skill_ids(self) -> list[str]:
        """Ordered list of skill IDs referenced by this rotation."""
        return [s.skill_id for s in self.steps]

    def unique_skill_ids(self) -> set[str]:
        return set(self.skill_ids())

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "rotation_id": self.rotation_id,
            "steps":       [s.to_dict() for s in self.steps],
            "loop":        self.loop,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RotationDefinition":
        return cls(
            rotation_id = d["rotation_id"],
            steps       = [RotationStep.from_dict(s) for s in d.get("steps", [])],
            loop        = bool(d.get("loop", True)),
        )
