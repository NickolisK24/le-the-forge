export const BASE_CLASSES = [
  "Acolyte",
  "Mage",
  "Primalist",
  "Sentinel",
  "Rogue",
] as const;

export type BaseClass = typeof BASE_CLASSES[number];

// Mastery definitions

export const CLASS_MASTERIES: Record<BaseClass, readonly string[]> = {
  Acolyte:   ["Necromancer", "Lich", "Warlock"],
  Mage:      ["Runemaster", "Sorcerer", "Spellblade"],
  Primalist: ["Beastmaster", "Shaman", "Druid"],
  Sentinel:  ["Paladin", "Void Knight", "Forge Guard"],
  Rogue:     ["Bladedancer", "Marksman", "Falconer"],
} as const;

export type ClassMasteryMap = typeof CLASS_MASTERIES;
export type Mastery = ClassMasteryMap[BaseClass][number];