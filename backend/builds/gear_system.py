"""
E4 — Gear System

Represents equipped items with stat-modifying affixes.
Each item occupies exactly one slot; two ring slots allow dual rings.
"""

from __future__ import annotations
from dataclasses import dataclass, field

# Slot identifiers used by BuildDefinition
VALID_SLOTS: tuple[str, ...] = (
    "weapon",
    "offhand",
    "head",
    "body",
    "hands",
    "feet",
    "ring_1",
    "ring_2",
    "amulet",
    "waist",
    "relic",
)

RARITY_VALUES = ("normal", "magic", "rare", "exalted")


@dataclass
class GearAffix:
    """A single affix on a gear item."""
    name: str
    tier: int = 1

    def to_dict(self) -> dict:
        return {"name": self.name, "tier": self.tier}


@dataclass
class GearItem:
    """
    One equipped item in a specific slot.

    affixes holds GearAffix objects; to_affix_dicts() converts them to
    the {"name": str, "tier": int} format expected by stat_engine.aggregate_stats().
    """
    slot: str
    affixes: list[GearAffix] = field(default_factory=list)
    rarity: str = "magic"

    def __post_init__(self) -> None:
        if self.slot not in VALID_SLOTS:
            raise ValueError(f"Invalid slot '{self.slot}'. Must be one of: {VALID_SLOTS}")
        if self.rarity not in RARITY_VALUES:
            raise ValueError(f"Invalid rarity '{self.rarity}'. Must be one of: {RARITY_VALUES}")

    def add_affix(self, affix: GearAffix) -> None:
        self.affixes.append(affix)

    def to_affix_dicts(self) -> list[dict]:
        """Return affixes as plain dicts for stat_engine compatibility."""
        return [a.to_dict() for a in self.affixes]

    def to_dict(self) -> dict:
        return {
            "slot":    self.slot,
            "affixes": [a.to_dict() for a in self.affixes],
            "rarity":  self.rarity,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GearItem":
        return cls(
            slot=d["slot"],
            affixes=[GearAffix(name=a["name"], tier=a.get("tier", 1)) for a in d.get("affixes", [])],
            rarity=d.get("rarity", "magic"),
        )
