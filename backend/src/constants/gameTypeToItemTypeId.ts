import type { ItemTypeId } from "./itemTypeIds";

/**
 * Maps raw game export type strings (from items.json `type` field) to
 * canonical ItemTypeId slugs used throughout the backend constants layer.
 *
 * Note: multiple game types can map to the same ItemTypeId (e.g. both
 * ONE_HANDED_AXE and TWO_HANDED_AXE → "axe") because the slot is the
 * same regardless of weapon hand count.
 *
 * Non-equipment types (BLESSING, *_LENS) are intentionally omitted.
 */
export const GAME_TYPE_TO_ITEM_TYPE_ID: Record<string, ItemTypeId> = {
  // Armor
  "HELMET":            "helm",
  "BODY_ARMOR":        "chest",
  "BELT":              "belt",
  "BOOTS":             "boots",
  "GLOVES":            "gloves",

  // Weapons — 1H
  "ONE_HANDED_AXE":    "axe",
  "ONE_HANDED_DAGGER": "dagger",
  "ONE_HANDED_FIST":   "fist",
  "ONE_HANDED_MACES":  "mace",
  "ONE_HANDED_SCEPTRE":"sceptre",
  "ONE_HANDED_SWORD":  "sword",
  "WAND":              "wand",

  // Weapons — 2H
  "TWO_HANDED_AXE":    "axe",
  "TWO_HANDED_MACE":   "mace",
  "TWO_HANDED_SPEAR":  "polearm",
  "TWO_HANDED_STAFF":  "staff",
  "TWO_HANDED_SWORD":  "sword",

  // Ranged
  "BOW":               "bow",
  "CROSSBOW":          "crossbow",

  // Off-hand
  "QUIVER":            "quiver",
  "SHIELD":            "shield",
  "CATALYST":          "catalyst",

  // Accessories
  "AMULET":            "amulet",
  "RING":              "ring",
  "RELIC":             "relic",

  // Idols
  "IDOL_1x1_ETERRA":   "idol_1x1",
  "IDOL_1x1_LAGON":    "idol_1x1",
  "IDOL_2x1":          "idol_2x1",
  "IDOL_1x2":          "idol_1x2",
  "IDOL_3x1":          "idol_3x1",
  "IDOL_1x3":          "idol_1x3",
  "IDOL_4x1":          "idol_4x1",
  "IDOL_1x4":          "idol_1x4",
  "IDOL_2x2":          "idol_2x2",
};

export type GameType = keyof typeof GAME_TYPE_TO_ITEM_TYPE_ID;
