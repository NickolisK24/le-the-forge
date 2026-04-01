"""
Enemy domain model — typed representation of enemy_profiles.json entries.

Constructed by the data pipeline and held by the registry. Engines receive
EnemyProfile objects instead of raw dicts.
Frozen: fields are immutable after construction.
"""

from __future__ import annotations
from dataclasses import dataclass, field


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
