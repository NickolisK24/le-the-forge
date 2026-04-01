export const ITEM_RARITIES = [
  "NORMAL",
  "MAGIC",
  "RARE",
  "EXALTED",
  "UNIQUE",
  "SET",
  "LEGENDARY"
] as const;

export type ItemRarity =
  typeof ITEM_RARITIES[number];