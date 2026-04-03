from __future__ import annotations

from dataclasses import dataclass, field

from bis.models.item_slot import ItemSlot, SlotType, SlotPool


@dataclass
class ItemCandidate:
    candidate_id: str
    item_class: str
    slot_type: str
    base_name: str
    forging_potential: int
    implicit_affixes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


# Built-in base items per class (simplified LE-inspired data)
BASE_ITEMS: dict[str, list[tuple[str, str, int]]] = {
    "helm": [
        ("iron_helm", "Iron Helm", 60),
        ("void_carapace_helm", "Void Carapace", 80),
        ("royal_helm", "Royal Helm", 100),
    ],
    "chest": [
        ("iron_chest", "Iron Chest", 55),
        ("lacquered_armour", "Lacquered Armour", 75),
        ("ornate_chestplate", "Ornate Chestplate", 95),
    ],
    "gloves": [
        ("iron_gauntlets", "Iron Gauntlets", 50),
        ("silk_gloves", "Silk Gloves", 70),
        ("void_touched_gloves", "Void-Touched Gloves", 90),
    ],
    "boots": [
        ("iron_boots", "Iron Boots", 50),
        ("silk_slippers", "Silk Slippers", 65),
        ("woven_boots", "Woven Boots", 85),
    ],
    "weapon1": [
        ("broad_sword", "Broad Sword", 60),
        ("runed_staff", "Runed Staff", 80),
        ("void_blade", "Void Blade", 100),
    ],
    "ring1": [
        ("copper_ring", "Copper Ring", 45),
        ("sapphire_ring", "Sapphire Ring", 65),
        ("eternity_band", "Eternity Band", 85),
    ],
    "ring2": [
        ("copper_ring", "Copper Ring", 45),
        ("sapphire_ring", "Sapphire Ring", 65),
        ("eternity_band", "Eternity Band", 85),
    ],
    "amulet": [
        ("simple_amulet", "Simple Amulet", 50),
        ("jade_amulet", "Jade Amulet", 70),
        ("herald_of_the_void", "Herald of the Void", 90),
    ],
}


class ItemCandidateGenerator:
    def generate(self, slot: ItemSlot, limit: int | None = None) -> list[ItemCandidate]:
        slot_str = slot.slot_type.value
        bases = BASE_ITEMS.get(slot_str, BASE_ITEMS.get("helm"))
        if limit:
            bases = bases[:limit]
        return [
            ItemCandidate(
                candidate_id=f"{slot_str}_{base_id}",
                item_class=slot_str,
                slot_type=slot_str,
                base_name=base_name,
                forging_potential=fp,
            )
            for base_id, base_name, fp in bases
        ]

    def generate_all(
        self, slot_pool: SlotPool, limit_per_slot: int | None = None
    ) -> dict[str, list[ItemCandidate]]:
        return {
            s.slot_type.value: self.generate(s, limit_per_slot)
            for s in slot_pool.enabled_slots()
        }
