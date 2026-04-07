"""
EquipmentSet — aggregates all equipped Item instances and emits their
combined stat contributions into a StatPool.

Provides slot-based management (equip / unequip / lookup) and validates
that items are placed into recognised equipment slots.

This is a pure domain model — no DB, no HTTP, no Flask context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.domain.item import Item
from app.utils.logging import ForgeLogger

if TYPE_CHECKING:
    from app.engines.stat_engine import StatPool

log = ForgeLogger(__name__)

# Equipment slot whitelist — mirrors gear_system.VALID_SLOTS plus the
# domain/constants slot list.  Any slot recognised by either system is
# accepted to maximise backward compatibility.
VALID_EQUIPMENT_SLOTS: frozenset[str] = frozenset({
    # Standard gear slots (gear_system.py)
    "weapon", "offhand", "head", "body", "hands", "feet",
    "ring_1", "ring_2", "amulet", "waist", "relic",
    # Constants-layer aliases (equipment_slots.py)
    "finger", "neck", "idol",
})


@dataclass
class EquipmentSet:
    """A full set of equipped items, keyed by slot name.

    Usage::

        gear = EquipmentSet()
        gear.equip_item(Item(slot="head", ...))
        gear.equip_item(Item(slot="body", ...))
        gear.apply_to_stat_pool(pool)
    """

    items: dict[str, Item] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Slot management
    # ------------------------------------------------------------------

    def equip_item(self, item: Item) -> Item | None:
        """Place *item* in its declared slot, returning any displaced item.

        Raises ``ValueError`` if the item's slot is empty or unrecognised.
        """
        slot = item.slot
        if not slot:
            raise ValueError("Item has no slot defined")
        if slot not in VALID_EQUIPMENT_SLOTS:
            raise ValueError(
                f"Slot {slot!r} is not a valid equipment slot. "
                f"Valid: {sorted(VALID_EQUIPMENT_SLOTS)}"
            )
        previous = self.items.get(slot)
        self.items[slot] = item
        log.debug(
            "equipment.equip",
            slot=slot,
            item=item.item_name,
            replaced=previous.item_name if previous else None,
        )
        return previous

    def unequip(self, slot: str) -> Item | None:
        """Remove and return the item in *slot*, or ``None`` if empty."""
        removed = self.items.pop(slot, None)
        if removed:
            log.debug("equipment.unequip", slot=slot, item=removed.item_name)
        return removed

    def get_item(self, slot: str) -> Item | None:
        """Return the item in *slot* without removing it."""
        return self.items.get(slot)

    def list_items(self) -> list[Item]:
        """Return all equipped items in deterministic slot order."""
        return [self.items[s] for s in sorted(self.items)]

    @property
    def filled_slots(self) -> list[str]:
        return sorted(self.items.keys())

    @property
    def empty_slots(self) -> list[str]:
        return sorted(VALID_EQUIPMENT_SLOTS - set(self.items.keys()))

    def __len__(self) -> int:
        return len(self.items)

    # ------------------------------------------------------------------
    # Stat integration
    # ------------------------------------------------------------------

    def apply_to_stat_pool(self, pool: "StatPool") -> None:
        """Emit stat modifiers from every equipped item into *pool*.

        Iterates in deterministic slot order so that the resulting
        StatPool is reproducible across runs.
        """
        log.debug("equipment.apply_start", n_items=len(self.items))
        for slot in sorted(self.items):
            item = self.items[slot]
            item.apply_to_stat_pool(pool)
        log.debug("equipment.apply_done", n_items=len(self.items))

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            slot: {
                "slot": item.slot,
                "item_name": item.item_name,
                "rarity": item.rarity,
                "affixes": [
                    {
                        "name": a.name,
                        "stat_key": a.stat_key,
                        "value": a.value,
                        "tier": a.tier,
                        "sealed": a.sealed,
                    }
                    for a in item.affixes
                ],
                "implicit_stats": dict(item.implicit_stats),
            }
            for slot, item in sorted(self.items.items())
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EquipmentSet":
        items: dict[str, Item] = {}
        for slot, item_data in d.items():
            item_data.setdefault("slot", slot)
            items[slot] = Item.from_dict(item_data)
        return cls(items=items)

    @classmethod
    def from_item_list(cls, item_list: list[Item]) -> "EquipmentSet":
        """Build an EquipmentSet from a flat list of Item objects."""
        es = cls()
        for item in item_list:
            es.equip_item(item)
        return es
