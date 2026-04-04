"""
E1 — Build Definition Object

The central data container for a player's build.
Holds all inputs that drive encounter simulation:
  skill, gear, passives, buffs, and metadata.

No DB imports — works as pure Python anywhere.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from builds.gear_system    import GearItem
from builds.buff_system    import Buff
from builds.passive_system import PassiveNode


@dataclass
class BuildMetadata:
    name:    str = "Untitled Build"
    version: str = "1.0"

    def to_dict(self) -> dict:
        return {"name": self.name, "version": self.version}

    @classmethod
    def from_dict(cls, d: dict) -> "BuildMetadata":
        return cls(name=d.get("name", "Untitled Build"), version=d.get("version", "1.0"))


@dataclass
class BuildDefinition:
    """
    Full build configuration.

    character_class / mastery:
        Drives base stats and mastery bonuses (passed to stat_engine).

    skill_id / skill_level:
        Selects which skill's base_damage and attack_speed are used.

    gear:
        List of GearItem objects (one per slot).  Adding a new item to an
        occupied slot replaces the existing one.

    passive_ids:
        Ordered list of allocated passive node IDs.

    buffs:
        Active Buff objects.  Duplicates (same buff_id) are replaced.

    metadata:
        Human-readable name and schema version.
    """

    character_class: str
    mastery:         str
    skill_id:        str            = "Rip Blood"
    skill_level:     int            = 20
    gear:            list[GearItem] = field(default_factory=list)
    passive_ids:     list[int]      = field(default_factory=list)
    buffs:           list[Buff]     = field(default_factory=list)
    metadata:        BuildMetadata  = field(default_factory=BuildMetadata)

    # ------------------------------------------------------------------
    # Gear helpers
    # ------------------------------------------------------------------

    def add_gear(self, item: GearItem) -> None:
        """Add or replace a gear item in the given slot."""
        self.gear = [g for g in self.gear if g.slot != item.slot]
        self.gear.append(item)

    def remove_gear(self, slot: str) -> GearItem | None:
        """Remove and return the item in `slot`, or None if empty."""
        for i, g in enumerate(self.gear):
            if g.slot == slot:
                return self.gear.pop(i)
        return None

    def get_gear(self, slot: str) -> GearItem | None:
        for g in self.gear:
            if g.slot == slot:
                return g
        return None

    # ------------------------------------------------------------------
    # Passive helpers
    # ------------------------------------------------------------------

    def add_passive(self, node_id: int) -> None:
        if node_id not in self.passive_ids:
            self.passive_ids.append(node_id)

    def remove_passive(self, node_id: int) -> None:
        if node_id in self.passive_ids:
            self.passive_ids.remove(node_id)

    # ------------------------------------------------------------------
    # Buff helpers
    # ------------------------------------------------------------------

    def add_buff(self, buff: Buff) -> None:
        """Add or replace a buff with the same buff_id."""
        self.buffs = [b for b in self.buffs if b.buff_id != buff.buff_id]
        self.buffs.append(buff)

    def remove_buff(self, buff_id: str) -> None:
        self.buffs = [b for b in self.buffs if b.buff_id != buff_id]

    # ------------------------------------------------------------------
    # Aggregation helpers (used by BuildStatsEngine)
    # ------------------------------------------------------------------

    def all_gear_affixes(self) -> list[dict]:
        """Flatten all gear affixes into the stat_engine-compatible format."""
        result = []
        for item in self.gear:
            result.extend(item.to_affix_dicts())
        return result

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "character_class": self.character_class,
            "mastery":         self.mastery,
            "skill_id":        self.skill_id,
            "skill_level":     self.skill_level,
            "gear":            [g.to_dict() for g in self.gear],
            "passive_ids":     list(self.passive_ids),
            "buffs":           [b.to_dict() for b in self.buffs],
            "metadata":        self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BuildDefinition":
        return cls(
            character_class=d["character_class"],
            mastery=d["mastery"],
            skill_id=d.get("skill_id", "Rip Blood"),
            skill_level=d.get("skill_level", 20),
            gear=[GearItem.from_dict(g) for g in d.get("gear", [])],
            passive_ids=list(d.get("passive_ids", [])),
            buffs=[Buff.from_dict(b) for b in d.get("buffs", [])],
            metadata=BuildMetadata.from_dict(d.get("metadata", {})),
        )
