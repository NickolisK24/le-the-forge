"""J3 — Skill Data Model"""

from dataclasses import dataclass, field

__all__ = ["SkillModel"]


@dataclass(frozen=True)
class SkillModel:
    """
    Immutable representation of a skill definition.

    Attributes
    ----------
    skill_id:
        Unique identifier for the skill (e.g. ``"rip_blood"``).
    base_damage:
        Base damage value before any scaling.
    cooldown:
        Cooldown duration in seconds (0 = no cooldown).
    mana_cost:
        Mana cost per use.
    tags:
        Tuple of tag strings (e.g. ``("spell", "cold")``).
    """

    skill_id: str
    base_damage: float
    cooldown: float
    mana_cost: float
    tags: tuple = field(default_factory=tuple)
    attack_speed: float = 1.0
    level_scaling: float = 0.0
    scaling_stats: tuple = field(default_factory=tuple)
    is_spell: bool = False
    is_melee: bool = False

    def __post_init__(self) -> None:
        if not self.skill_id:
            raise ValueError("skill_id must not be empty")
        if self.base_damage < 0:
            raise ValueError("base_damage must be >= 0")
        if self.cooldown < 0:
            raise ValueError("cooldown must be >= 0")
        if self.mana_cost < 0:
            raise ValueError("mana_cost must be >= 0")
        if self.attack_speed <= 0:
            raise ValueError("attack_speed must be > 0")
        # Normalise tags to a tuple of strings
        object.__setattr__(self, "tags", tuple(str(t) for t in self.tags))
        object.__setattr__(self, "scaling_stats", tuple(str(s) for s in self.scaling_stats))

    def has_tag(self, tag: str) -> bool:
        """Return True if *tag* is present."""
        return tag in self.tags

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "base_damage": self.base_damage,
            "cooldown": self.cooldown,
            "mana_cost": self.mana_cost,
            "tags": list(self.tags),
            "attack_speed": self.attack_speed,
            "level_scaling": self.level_scaling,
            "scaling_stats": list(self.scaling_stats),
            "is_spell": self.is_spell,
            "is_melee": self.is_melee,
        }
