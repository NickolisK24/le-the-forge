"""J8 — Enemy Template Model"""

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
    """

    enemy_id: str
    max_health: float
    resistances: dict = field(default_factory=dict)
    armor: float = 0.0

    def __post_init__(self) -> None:
        if not self.enemy_id:
            raise ValueError("enemy_id must not be empty")
        if self.max_health <= 0:
            raise ValueError("max_health must be > 0")
        if self.armor < 0:
            raise ValueError("armor must be >= 0")
        object.__setattr__(self, "resistances", dict(self.resistances))

    def resistance(self, damage_type: str) -> float:
        """Return the resistance for *damage_type* (default 0.0)."""
        return self.resistances.get(damage_type, 0.0)

    def to_dict(self) -> dict:
        return {
            "enemy_id": self.enemy_id,
            "max_health": self.max_health,
            "resistances": dict(self.resistances),
            "armor": self.armor,
        }
