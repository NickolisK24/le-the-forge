"""Character classes and masteries."""

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
