"""
Enemy domain model — typed representation of enemy_profiles.json entries,
plus gameplay simulation types (EnemyStats, EnemyArchetype).
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field

from app.constants.defense import RES_CAP


# ---------------------------------------------------------------------------
# Gameplay simulation types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EnemyStats:
    """
    Runtime stats for a single enemy instance during simulation.

    Distinct from EnemyProfile (which is the data-pipeline model).
    resistances stores raw values; use capped_resistances for the
    effective values after the 75% hard cap is applied.
    """
    health: int = 0
    armor: int = 0
    resistances: dict[str, float] = field(default_factory=dict)
    status_effects: tuple[str, ...] = ()

    @property
    def capped_resistances(self) -> dict[str, float]:
        """Return resistances with the RES_CAP hard cap applied."""
        return {k: min(v, float(RES_CAP)) for k, v in self.resistances.items()}


class EnemyArchetype(enum.Enum):
    """
    Enemy tier categories with associated baseline stats.

    Tiers reflect Last Epoch enemy scaling:
      TRAINING_DUMMY — zero stats, used for raw damage benchmarking.
      NORMAL         — standard zone enemy.
      ELITE          — tougher rare/magic enemy.
      BOSS           — boss-tier with high health, armor, and resistances.
    """
    TRAINING_DUMMY = "training_dummy"
    NORMAL         = "normal"
    ELITE          = "elite"
    BOSS           = "boss"

    def base_stats(self) -> EnemyStats:
        """Return the default EnemyStats for this archetype tier."""
        _RESISTANCES_NORMAL = {
            "physical": 0.0, "fire": 25.0, "cold": 25.0,
            "lightning": 25.0, "void": 25.0, "necrotic": 25.0, "poison": 25.0,
        }
        _RESISTANCES_ELITE = {
            "physical": 10.0, "fire": 40.0, "cold": 40.0,
            "lightning": 40.0, "void": 40.0, "necrotic": 40.0, "poison": 40.0,
        }
        _RESISTANCES_BOSS = {
            "physical": 30.0, "fire": 60.0, "cold": 60.0,
            "lightning": 60.0, "void": 60.0, "necrotic": 60.0, "poison": 60.0,
        }
        if self is EnemyArchetype.TRAINING_DUMMY:
            return EnemyStats()
        if self is EnemyArchetype.NORMAL:
            return EnemyStats(health=1_000,  armor=200,  resistances=_RESISTANCES_NORMAL)
        if self is EnemyArchetype.ELITE:
            return EnemyStats(health=3_000,  armor=500,  resistances=_RESISTANCES_ELITE)
        # BOSS
        return EnemyStats(health=10_000, armor=1_000, resistances=_RESISTANCES_BOSS)



@dataclass(frozen=True)
class EnemyProfile:
    id: str
    name: str
    category: str
    data_version: str             # version of the data file this was loaded from
    description: str = ""
    health: int = 0
    armor: int = 0
    # resistances is a plain dict — the field reference is frozen but the dict
    # contents are technically mutable. Treat as read-only by convention.
    resistances: dict[str, float] = field(default_factory=dict)
    crit_chance: float = 0.0
    crit_multiplier: float = 1.0
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "name":            self.name,
            "category":        self.category,
            "description":     self.description,
            "health":          self.health,
            "armor":           self.armor,
            "resistances":     dict(self.resistances),
            "crit_chance":     self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
            "tags":            list(self.tags),
            "data_version":    self.data_version,
        }

    @classmethod
    def from_dict(cls, d: dict, *, data_version: str) -> "EnemyProfile":
        return cls(
            id=d["id"],
            name=d["name"],
            category=d.get("category", "normal"),
            data_version=data_version,
            description=d.get("description", ""),
            health=int(d.get("health", 0)),
            armor=int(d.get("armor", 0)),
            resistances=d.get("resistances", {}),
            crit_chance=float(d.get("crit_chance", 0.0)),
            crit_multiplier=float(d.get("crit_multiplier", 1.0)),
            tags=tuple(d.get("tags", [])),
        )
