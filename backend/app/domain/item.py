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
from typing import TYPE_CHECKING, Optional

from app.utils.logging import ForgeLogger

if TYPE_CHECKING:
    from app.engines.stat_engine import StatPool

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Template / definition layer  (from affixes.json)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
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


@dataclass(frozen=True)
class AffixDefinition:
    """
    An affix template — the canonical definition of what an affix is and where
    it can appear. Sourced from affixes.json and indexed by AffixRegistry.

    Do not confuse with Affix, which is an instance on a specific equipped item.
    Frozen: fields are immutable after construction.
    """

    name: str
    stat_key: str
    affix_type: str                 # "prefix" or "suffix"
    applicable_to: tuple[str, ...]  # slot names, e.g. ("head", "body", "hands")
    tiers: tuple[AffixTier, ...]
    data_version: str               # version of the data file this was loaded from
    affix_id: Optional[int] = None

    @classmethod
    def from_dict(cls, d: dict, *, data_version: str) -> "AffixDefinition":
        raw_id = d["affix_id"] if "affix_id" in d and d["affix_id"] is not None else d.get("id")
        return cls(
            name=d.get("name", ""),
            stat_key=d.get("stat_key", d.get("id", "")),
            affix_type=d.get("type", ""),
            applicable_to=tuple(d.get("applicable_to", [])),
            tiers=tuple(AffixTier.from_dict(t) for t in d.get("tiers", [])),
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
            "applicable_to": list(self.applicable_to),
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
    implicit_stats: dict[str, float] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Stat integration
    # ------------------------------------------------------------------

    def apply_to_stat_pool(self, pool: "StatPool") -> None:
        """Emit all stat modifiers from this item into the given StatPool.

        Processes:
          1. Each affix → flat modifier via stat_key + value
          2. Each implicit stat → flat modifier

        Sealed affixes are included (their value is already resolved).
        Modifier-type routing (flat vs increased vs more) is determined by
        stat_key convention — same rules as stat_engine.apply_affix:
          - ``_pct`` suffix  → ``increased`` bucket
          - ``more_`` prefix → ``more`` bucket
          - everything else  → ``flat`` bucket
        """
        for affix in self.affixes:
            if not affix.stat_key or affix.value == 0.0:
                continue
            self._route_to_pool(pool, affix.stat_key, affix.value)
            log.debug(
                "item.apply_affix",
                item=self.item_name,
                slot=self.slot,
                affix=affix.name,
                stat_key=affix.stat_key,
                value=affix.value,
            )

        for stat_key, value in self.implicit_stats.items():
            if value == 0.0:
                continue
            self._route_to_pool(pool, stat_key, value)
            log.debug(
                "item.apply_implicit",
                item=self.item_name,
                slot=self.slot,
                stat_key=stat_key,
                value=value,
            )

    @staticmethod
    def _route_to_pool(pool: "StatPool", stat_key: str, value: float) -> None:
        """Route a stat value into the correct StatPool bucket."""
        if stat_key.endswith("_pct"):
            pool.add_increased(stat_key, value)
        elif stat_key.startswith("more_") or stat_key == "more_damage_multiplier":
            pool.add_more(stat_key, value)
        else:
            pool.add_flat(stat_key, value)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: dict) -> "Item":
        raw_implicits = d.get("implicit_stats", {})
        implicits = {
            k: float(v) for k, v in raw_implicits.items()
            if isinstance(v, (int, float))
        }
        return cls(
            slot=d.get("slot", ""),
            item_name=d.get("item_name", d.get("name", "")),
            rarity=d.get("rarity", "Normal"),
            affixes=[Affix.from_dict(a) for a in d.get("affixes", [])],
            implicit_stats=implicits,
        )
