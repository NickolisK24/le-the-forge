"""
Combat Scenario — defines the parameters for a deterministic combat simulation.

A CombatScenario specifies:
  - Duration (how long the fight lasts)
  - Enemy target (what defenses apply)
  - Skill rotation (which skills fire and when)
  - Tick size (time resolution)
  - Mana configuration (max mana, regen rate)

This is a pure data object — no logic, no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domain.enemy import EnemyArchetype, EnemyInstance, EnemyStats
from app.domain.mana import ManaPool
from app.domain.skill import SkillStatDef
from app.domain.skill_modifiers import SkillModifiers


@dataclass(frozen=True)
class SkillRotationEntry:
    """A single skill in the combat rotation.

    Fields:
        skill_def:   Skill template (damage, speed, scaling).
        skill_name:  Human-readable label.
        level:       Skill level (1–20).
        skill_mods:  Per-skill spec-tree modifiers.
        priority:    Lower = higher priority when multiple skills are ready
                     at the same tick. Default 1.
        cooldown:    Seconds between casts. 0 = use skill's native attack_speed.
    """
    skill_def: SkillStatDef
    skill_name: str = ""
    level: int = 1
    skill_mods: SkillModifiers = field(default_factory=SkillModifiers)
    priority: int = 1
    cooldown: float = 0.0

    @property
    def effective_interval(self) -> float:
        """Seconds between casts — uses cooldown if set, else 1/attack_speed."""
        if self.cooldown > 0:
            return self.cooldown
        if self.skill_def.attack_speed > 0:
            return 1.0 / self.skill_def.attack_speed
        return 1.0


@dataclass(frozen=True)
class CombatScenario:
    """Full specification for a deterministic combat simulation.

    Usage::

        scenario = CombatScenario(
            duration_seconds=30.0,
            enemy=EnemyInstance.from_archetype(EnemyArchetype.BOSS),
            rotation=(fireball_entry, ice_bolt_entry),
        )
    """
    duration_seconds: float = 30.0
    enemy: Optional[EnemyInstance] = None
    rotation: tuple[SkillRotationEntry, ...] = ()
    tick_size: float = 0.1
    penetration: dict[str, float] = field(default_factory=dict)
    max_mana: float = 0.0
    mana_regen_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be > 0")
        if self.tick_size <= 0:
            raise ValueError("tick_size must be > 0")
        if not self.rotation:
            raise ValueError("rotation must contain at least one skill")

    def create_mana_pool(self) -> Optional[ManaPool]:
        """Create a fresh ManaPool from scenario config, or None if mana is disabled."""
        if self.max_mana <= 0:
            return None
        return ManaPool(
            max_mana=self.max_mana,
            current_mana=self.max_mana,
            mana_regeneration_rate=self.mana_regen_rate,
        )

    @classmethod
    def quick(
        cls,
        skill_def: SkillStatDef,
        duration: float = 30.0,
        level: int = 1,
        skill_name: str = "",
        archetype: EnemyArchetype = EnemyArchetype.TRAINING_DUMMY,
        skill_mods: SkillModifiers | None = None,
        max_mana: float = 0.0,
        mana_regen_rate: float = 0.0,
    ) -> "CombatScenario":
        """Create a single-skill scenario for quick testing."""
        entry = SkillRotationEntry(
            skill_def=skill_def,
            skill_name=skill_name,
            level=level,
            skill_mods=skill_mods or SkillModifiers(),
        )
        return cls(
            duration_seconds=duration,
            enemy=EnemyInstance.from_archetype(archetype),
            rotation=(entry,),
            max_mana=max_mana,
            mana_regen_rate=mana_regen_rate,
        )
