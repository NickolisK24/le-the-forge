"""
Item domain models — represent a single equipped item and its affixes.

These are constructed at the service boundary from the raw gear list stored
in Build.gear (JSON array), then passed to engines as typed objects.
"""

from __future__ import annotations
from dataclasses import dataclass, field


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
