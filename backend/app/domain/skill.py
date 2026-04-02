"""
Skill domain models — two distinct layers.

  - SkillStatDef : template data from skills.json (what a skill IS — damage, speed, etc.)
  - SkillSpec    : instance data from a Build's skill slots (what IS equipped, at what level)

SkillStatDef objects are held by SkillRegistry.
SkillSpec objects are constructed at the service boundary and passed to engines.

Multi-hit support (Step 6):
  hit_count    — number of distinct hits produced per cast/activation (default 1)
  hit_interval — seconds between successive hits within one cast (0 = simultaneous)
  calculate_multi_hit_dps() — DPS accounting for hit count and attack speed
"""

from __future__ import annotations
from dataclasses import dataclass, field
from app.domain.calculators.damage_type_router import DamageType, damage_types_for_stats


# ---------------------------------------------------------------------------
# Template / definition layer  (from skills.json)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SkillStatDef:
    """
    Static per-skill tuning values. Sourced from skills.json and indexed by
    SkillRegistry. Mirrors SKILL_STATS in frontend/src/lib/gameData.ts.
    Frozen: fields are immutable after construction.

    Multi-hit fields:
      hit_count    — hits produced per cast (e.g. 3 for a 3-hit melee flurry)
      hit_interval — seconds between hits within one cast (0 = simultaneous)
    """

    base_damage: float
    level_scaling: float          # damage multiplier per level above 1
    attack_speed: float           # base casts/attacks per second
    scaling_stats: tuple[str, ...]  # BuildStats field names for % damage bonus
    data_version: str             # version of the data file this was loaded from
    is_spell: bool = False
    is_melee: bool = False
    is_throwing: bool = False
    is_bow: bool = False
    damage_types: tuple[DamageType, ...] = ()  # explicit damage channels this skill deals
    hit_count:    int   = 1    # hits per cast activation
    hit_interval: float = 0.0  # seconds between hits (0 = simultaneous)

    @classmethod
    def from_dict(cls, d: dict, *, data_version: str = "") -> "SkillStatDef":
        scaling = tuple(d.get("scaling_stats", []))
        # Accept explicit damage_types from JSON; fall back to deriving from scaling_stats.
        if "damage_types" in d:
            dtypes = tuple(DamageType(v) for v in d["damage_types"] if v in DamageType._value2member_map_)
        else:
            dtypes = tuple(damage_types_for_stats(scaling))
        return cls(
            base_damage=float(d.get("base_damage", 0.0)),
            level_scaling=float(d.get("level_scaling", 0.0)),
            attack_speed=float(d.get("attack_speed", 1.0)),
            scaling_stats=scaling,
            is_spell=bool(d.get("is_spell", False)),
            is_melee=bool(d.get("is_melee", False)),
            is_throwing=bool(d.get("is_throwing", False)),
            is_bow=bool(d.get("is_bow", False)),
            data_version=data_version,
            damage_types=dtypes,
            hit_count=int(d.get("hit_count", 1)),
            hit_interval=float(d.get("hit_interval", 0.0)),
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


# ---------------------------------------------------------------------------
# Multi-hit DPS helper
# ---------------------------------------------------------------------------

def calculate_multi_hit_dps(
    skill: SkillStatDef,
    per_hit_damage: float,
) -> float:
    """
    Compute DPS for a multi-hit skill given the damage dealt per individual hit.

    Formula:
        total_damage_per_cast = per_hit_damage * hit_count
        dps = total_damage_per_cast * attack_speed

    ``per_hit_damage`` is the fully-computed damage for one hit (after all
    modifiers, resistances, etc.). ``attack_speed`` is casts per second.

    hit_interval is informational (used by timeline scheduling) and does not
    affect steady-state DPS — all hits within a cast still occur once per cast.

    Raises ValueError if hit_count < 1 or attack_speed <= 0.
    """
    if skill.hit_count < 1:
        raise ValueError(f"hit_count must be >= 1, got {skill.hit_count}")
    if skill.attack_speed <= 0:
        raise ValueError(f"attack_speed must be > 0, got {skill.attack_speed}")
    return per_hit_damage * skill.hit_count * skill.attack_speed
