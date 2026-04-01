"""
Skill domain model — represents a single equipped skill slot.

Thin wrapper over the BuildSkill ORM data. Constructed at the service
boundary and passed to resolvers and engines.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SkillSpec:
    """A skill slot: which skill is equipped, at what level, and with what spec tree."""

    skill_name: str
    level: int = 1
    spec_tree: list[dict] = field(default_factory=list)  # [{"node_id": int, "points": int}, ...]
    hud_slot: int = 0                                     # 0–4 ordering in HUD

    @classmethod
    def from_dict(cls, d: dict) -> "SkillSpec":
        return cls(
            skill_name=d.get("skill_name", ""),
            level=int(d.get("level", 1)),
            spec_tree=d.get("spec_tree", []),
            hud_slot=int(d.get("hud_slot", d.get("slot_index", 0))),
        )
