"""J8 — Enemy Template Model"""

import warnings
from dataclasses import dataclass, field

__all__ = ["EnemyModel"]


@dataclass(frozen=True)
class EnemyModel:
    """
    Immutable representation of an enemy template.

    Attributes
    ----------
    enemy_id:
        Unique enemy identifier (e.g. ``"training_dummy"``).
    max_health:
        Maximum hit-point pool.
    resistances:
        Dict mapping damage type → resistance percentage (0–100).
    armor:
        Flat armor value used for physical damage reduction.
    name:
        Human-readable display name for the enemy.
    category:
        Enemy category string (e.g. ``"beast"``, ``"undead"``).
    crit_chance:
        Probability (0.0–1.0) that the enemy lands a critical hit.
    crit_multiplier:
        Damage multiplier applied on a critical hit (>= 1.0).
    """

    enemy_id: str
    max_health: float
    resistances: dict = field(default_factory=dict)
    armor: float = 0.0
    name: str = ""
    category: str = ""
    crit_chance: float = 0.0
    crit_multiplier: float = 1.5

    def __post_init__(self) -> None:
        if not self.enemy_id:
            raise ValueError("enemy_id must not be empty")
        if self.max_health <= 0:
            raise ValueError("max_health must be > 0")
        if self.armor < 0:
            raise ValueError("armor must be >= 0")
        if not (0.0 <= self.crit_chance <= 1.0):
            raise ValueError("crit_chance must be between 0.0 and 1.0")
        if self.crit_multiplier < 1.0:
            raise ValueError("crit_multiplier must be >= 1.0")
        # Validate resistances — warn if any value exceeds 100
        clamped = {}
        for dtype, val in self.resistances.items():
            if val > 100:
                warnings.warn(
                    f"Resistance for '{dtype}' is {val}, which exceeds 100%. Clamping to 100.",
                    UserWarning,
                    stacklevel=3,
                )
                clamped[dtype] = 100.0
            else:
                clamped[dtype] = val
        object.__setattr__(self, "resistances", clamped)

    def resistance(self, damage_type: str) -> float:
        """Return the resistance for *damage_type* (default 0.0)."""
        return self.resistances.get(damage_type, 0.0)

    def to_dict(self) -> dict:
        return {
            "enemy_id": self.enemy_id,
            "max_health": self.max_health,
            "resistances": dict(self.resistances),
            "armor": self.armor,
            "name": self.name,
            "category": self.category,
            "crit_chance": self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
        }
