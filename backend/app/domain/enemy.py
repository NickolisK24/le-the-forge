"""
Enemy domain model — typed representation of enemy_profiles.json entries.

Constructed by the data pipeline and held by the registry. Engines receive
EnemyProfile objects instead of raw dicts.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class EnemyProfile:
    id: str
    name: str
    category: str
    description: str = ""
    health: int = 0
    armor: int = 0
    resistances: dict[str, float] = field(default_factory=dict)
    crit_chance: float = 0.0
    crit_multiplier: float = 1.0
    data_version: str         # version of the data file this was loaded from
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict, *, data_version: str) -> "EnemyProfile":
        return cls(
            id=d["id"],
            name=d["name"],
            category=d.get("category", "normal"),
            description=d.get("description", ""),
            health=int(d.get("health", 0)),
            armor=int(d.get("armor", 0)),
            resistances=d.get("resistances", {}),
            crit_chance=float(d.get("crit_chance", 0.0)),
            crit_multiplier=float(d.get("crit_multiplier", 1.0)),
            data_version=data_version,
            tags=d.get("tags", []),
        )
