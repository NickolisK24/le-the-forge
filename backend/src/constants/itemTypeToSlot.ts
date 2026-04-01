import type { EquipmentSlot } from "./equipmentSlots";
import type { ItemTypeId } from "./itemTypeIds";

export const ITEM_TYPE_TO_SLOT: Record<
  ItemTypeId,
  EquipmentSlot
> = {
  "amulet":   "neck",
  "axe":      "weapon",
  "belt":     "waist",
  "boots":    "feet",
  "bow":      "weapon",
  "catalyst": "offhand",
  "chest":    "body",
  "crossbow": "weapon",
  "dagger":   "weapon",
  "fist":     "weapon",
  "gloves":   "hands",
  "helm":     "head",
  "idol_1x1": "idol",
  "idol_1x2": "idol",
  "idol_1x3": "idol",
  "idol_1x4": "idol",
  "idol_2x1": "idol",
  "idol_2x2": "idol",
  "idol_3x1": "idol",
  "idol_4x1": "idol",
  "mace":     "weapon",
  "polearm":  "weapon",
  "quiver":   "offhand",
  "relic":    "relic",
  "ring":     "finger",
  "sceptre":  "weapon",
  "shield":   "offhand",
  "staff":    "weapon",
  "sword":    "weapon",
  "wand":     "weapon",
};
