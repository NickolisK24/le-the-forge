export const ITEM_RARITIES = [
  "Normal",
  "Magic",
  "Rare",
  "Exalted",
  "Unique",
  "Set",
  "Legendary",
] as const;

export type ItemRarity = typeof ITEM_RARITIES[number];