"""
Item domain models — represent a single equipped item and its affixes.

Two distinct layers:
  - AffixDefinition / AffixTier : template data from affixes.json (what CAN exist)
  - Affix / Item                : instance data from a Build's gear list (what IS equipped)

AffixDefinition objects are held by AffixRegistry.
Affix / Item objects are constructed at the service boundary and passed to engines.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Template / definition layer  (from affixes.json)
# ---------------------------------------------------------------------------

@dataclass
class AffixTier:
    """A single tier range for an affix template."""

    tier: int
    min: float
    max: float

    @classmethod
    def from_dict(cls, d: dict) -> "AffixTier":
        return cls(
            tier=int(d.get("tier", 0)),
            min=float(d.get("min", 0.0)),
            max=float(d.get("max", 0.0)),
        )

    @property
    def midpoint(self) -> float:
        return math.floor((self.min + self.max) / 2)

    def to_dict(self) -> dict:
        return {"tier": self.tier, "min": self.min, "max": self.max}


@dataclass
class AffixDefinition:
    """
    An affix template — the canonical definition of what an affix is and where
    it can appear. Sourced from affixes.json and indexed by AffixRegistry.

    Do not confuse with Affix, which is an instance on a specific equipped item.
    """

    name: str
    stat_key: str
    affix_type: str           # "prefix" or "suffix"
    applicable_to: list[str]  # slot names, e.g. ["head", "body", "hands"]
    tiers: list[AffixTier]
    affix_id: Optional[int] = None
    data_version: str = "unknown"

    @classmethod
    def from_dict(cls, d: dict, *, data_version: str = "unknown") -> "AffixDefinition":
        raw_id = d.get("affix_id") or d.get("id")
        return cls(
            name=d.get("name", ""),
            stat_key=d.get("stat_key", d.get("id", "")),
            affix_type=d.get("type", ""),
            applicable_to=list(d.get("applicable_to", [])),
            tiers=[AffixTier.from_dict(t) for t in d.get("tiers", [])],
            affix_id=int(raw_id) if raw_id is not None else None,
            data_version=data_version,
        )

    def tier_midpoints(self) -> dict[str, float]:
        """Return {T1: mid, T2: mid, …} — matches the legacy affix_tier_midpoints shape."""
        return {f"T{t.tier}": t.midpoint for t in self.tiers}

    def to_dict(self) -> dict:
        """Serialize back to a raw dict (for backward-compat callers)."""
        d: dict = {
            "name": self.name,
            "stat_key": self.stat_key,
            "type": self.affix_type,
            "applicable_to": self.applicable_to,
            "tiers": [t.to_dict() for t in self.tiers],
        }
        if self.affix_id is not None:
            d["affix_id"] = self.affix_id
        return d


# ---------------------------------------------------------------------------
# Instance layer  (from a Build's gear list)
# ---------------------------------------------------------------------------

@dataclass
class Affix:
    """A single affix on an item — either a named tier affix or a unique stat."""

    name: str
    stat_key: str
    value: float
    tier: int = 0
    sealed: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Affix":
        return cls(
            name=d.get("name", ""),
            stat_key=d.get("stat_key", ""),
            value=float(d.get("value", 0.0)),
            tier=int(d.get("tier", 0)),
            sealed=bool(d.get("sealed", False)),
        )


@dataclass
class Item:
    """A single equipped item with its resolved affixes."""

    slot: str
    item_name: str
    rarity: str
    affixes: list[Affix] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Item":
        return cls(
            slot=d.get("slot", ""),
            item_name=d.get("item_name", d.get("name", "")),
            rarity=d.get("rarity", "Normal"),
            affixes=[Affix.from_dict(a) for a in d.get("affixes", [])],
        )
