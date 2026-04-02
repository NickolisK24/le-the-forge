"""
Build Assembly Layer (Step 92).

Creates a unified Build object from all stat sources:
  - Passive tree nodes  (via passive_aggregator)
  - Equipped gear       (via gear_aggregator)
  - Skill list          (attached as-is)

  BuildSkill   — a skill entry in the build (name, tags, base_damage)
  Build        — the assembled build object exposing merged stat_pool
                 and scaled damage per skill via damage_for(skill)

Stat merging:
  Passive and gear stats are summed additively into a single stat_pool.
  The same stat key present in both sources stacks together.

Skill damage:
  Build.damage_for(skill) applies skill_scaling to the skill's base_damage
  using the merged stat_pool and the skill's declared tags.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.item import Item
from build.gear_aggregator import aggregate_gear
from build.passive_aggregator import PassiveNode, aggregate_passives
from build.skill_scaling import scale_skill


@dataclass(frozen=True)
class BuildSkill:
    """
    A skill entry in the build.

    name        — unique identifier
    tags        — scaling tag list (e.g. ["fire", "spell"])
    base_damage — raw damage before stat scaling
    """
    name:        str
    tags:        tuple[str, ...]
    base_damage: float = 0.0

    def __post_init__(self) -> None:
        if self.base_damage < 0:
            raise ValueError(f"BuildSkill '{self.name}': base_damage must be >= 0")


@dataclass
class Build:
    """
    Assembled build object.

    Merges passive and gear stats into a single stat_pool, and provides
    damage_for() to compute the scaled damage for any skill in the build.

    Attributes:
        skills    — ordered list of skills in the build
        stat_pool — merged flat stat dict (passive + gear, additively stacked)
    """
    skills:    list[BuildSkill]
    stat_pool: dict[str, float]

    @classmethod
    def assemble(
        cls,
        passives: list[PassiveNode],
        gear:     list[Item],
        skills:   list[BuildSkill],
    ) -> "Build":
        """
        Aggregate passives and gear stats, then return a fully assembled Build.

        Args:
            passives — passive tree nodes
            gear     — equipped items
            skills   — skill list for this build

        Returns:
            Build with merged stat_pool and skill list attached.
        """
        passive_stats = aggregate_passives(passives)
        gear_stats    = aggregate_gear(gear)

        # Additive merge of both stat sources
        merged: dict[str, float] = dict(passive_stats)
        for key, value in gear_stats.items():
            merged[key] = merged.get(key, 0.0) + value

        return cls(skills=list(skills), stat_pool=merged)

    def damage_for(self, skill: BuildSkill) -> float:
        """
        Return the scaled damage for *skill* using this build's stat_pool.

        Applies scale_skill() with the skill's tags and the merged stat_pool.
        """
        return scale_skill(skill.base_damage, list(skill.tags), self.stat_pool)

    def stat(self, key: str, default: float = 0.0) -> float:
        """Return the value of *key* from the merged stat_pool, or *default*."""
        return self.stat_pool.get(key, default)
