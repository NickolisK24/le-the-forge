"""
Skill domain models — two distinct layers.

  - SkillStatDef : template data from skills.json (what a skill IS — damage, speed, etc.)
  - SkillSpec    : instance data from a Build's skill slots (what IS equipped, at what level)

SkillStatDef objects are held by SkillRegistry.
SkillSpec objects are constructed at the service boundary and passed to engines.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Template / definition layer  (from skills.json)
# ---------------------------------------------------------------------------

@dataclass
class SkillStatDef:
    """
    Static per-skill tuning values. Sourced from skills.json and indexed by
    SkillRegistry. Mirrors SKILL_STATS in frontend/src/lib/gameData.ts.
    """

    base_damage: float
    level_scaling: float    # damage multiplier per level above 1
    attack_speed: float     # base casts/attacks per second
    scaling_stats: list     # list of BuildStats field names for % damage bonus
    data_version: str         # version of the data file this was loaded from
    is_spell: bool = False
    is_melee: bool = False
    is_throwing: bool = False
    is_bow: bool = False

    @classmethod
    def from_dict(cls, name: str, d: dict, *, data_version: str) -> "SkillStatDef":
        return cls(
            base_damage=float(d["base_damage"]),
            level_scaling=float(d["level_scaling"]),
            attack_speed=float(d["attack_speed"]),
            scaling_stats=list(d.get("scaling_stats", [])),
            is_spell=bool(d.get("is_spell", False)),
            is_melee=bool(d.get("is_melee", False)),
            is_throwing=bool(d.get("is_throwing", False)),
            is_bow=bool(d.get("is_bow", False)),
            data_version=data_version,
        )


# ---------------------------------------------------------------------------
# Instance layer  (from a Build's skill slots)
# ---------------------------------------------------------------------------

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
