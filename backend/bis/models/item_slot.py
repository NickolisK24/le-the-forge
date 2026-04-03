from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class SlotType(Enum):
    HELM = "helm"
    CHEST = "chest"
    GLOVES = "gloves"
    BOOTS = "boots"
    BELT = "belt"
    RING1 = "ring1"
    RING2 = "ring2"
    AMULET = "amulet"
    WEAPON1 = "weapon1"
    WEAPON2 = "weapon2"
    OFFHAND = "offhand"


ALL_SLOTS = [s.value for s in SlotType]


@dataclass
class ItemSlot:
    slot_type: SlotType
    is_enabled: bool = True
    max_affixes: int = 4
    allowed_item_classes: list[str] = field(default_factory=list)  # empty = any


@dataclass
class SlotPool:
    slots: list[ItemSlot]

    @classmethod
    def all_slots(cls) -> SlotPool:
        return cls([ItemSlot(s) for s in SlotType])

    @classmethod
    def from_slot_types(cls, types: list[str]) -> SlotPool:
        return cls([ItemSlot(SlotType(t)) for t in types])

    def enabled_slots(self) -> list[ItemSlot]:
        return [s for s in self.slots if s.is_enabled]

    def disable(self, slot_type: str) -> None:
        for s in self.slots:
            if s.slot_type.value == slot_type:
                s.is_enabled = False
