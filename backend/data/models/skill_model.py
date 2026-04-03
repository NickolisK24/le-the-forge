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

    def __post_init__(self) -> None:
        if not self.skill_id:
            raise ValueError("skill_id must not be empty")
        if self.base_damage < 0:
            raise ValueError("base_damage must be >= 0")
        if self.cooldown < 0:
            raise ValueError("cooldown must be >= 0")
        if self.mana_cost < 0:
            raise ValueError("mana_cost must be >= 0")
        # Normalise tags to a tuple of strings
        object.__setattr__(self, "tags", tuple(str(t) for t in self.tags))

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
        }
