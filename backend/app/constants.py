"""
Shared game constants — mirrors backend/src/constants/ for the Python layer.

These are the canonical lists used for request validation across all schemas
and routes. Update here when the game adds classes, masteries, or damage types.
"""

BASE_CLASSES: list[str] = [
    "Acolyte",
    "Mage",
    "Primalist",
    "Sentinel",
    "Rogue",
]

CLASS_MASTERIES: dict[str, list[str]] = {
    "Acolyte":   ["Necromancer", "Lich", "Warlock"],
    "Mage":      ["Runemaster", "Sorcerer", "Spellblade"],
    "Primalist": ["Beastmaster", "Shaman", "Druid"],
    "Sentinel":  ["Paladin", "Void Knight", "Forge Guard"],
    "Rogue":     ["Bladedancer", "Marksman", "Falconer"],
}

DAMAGE_TYPES: list[str] = [
    "physical",
    "fire",
    "cold",
    "lightning",
    "void",
    "necrotic",
    "poison",
]

EQUIPMENT_SLOTS: list[str] = [
    "helmet",
    "body",
    "gloves",
    "boots",
    "belt",
    "amulet",
    "ring",
    "weapon",
    "offhand",
    "relic",
]

ITEM_RARITIES: list[str] = [
    "Normal",
    "Magic",
    "Rare",
    "Exalted",
    "Unique",
    "Set",
    "Legendary",
]
