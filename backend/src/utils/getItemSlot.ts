import { ITEM_TYPE_TO_SLOT } from "../constants/itemTypeToSlot";
import { GAME_TYPE_TO_ITEM_TYPE_ID } from "../constants/gameTypeToItemTypeId";
import { SUBTYPE_ID_TO_ITEM_TYPE_ID } from "../constants/SUBTYPE_ID_TO_ITEM_TYPE_ID";
import type { EquipmentSlot } from "../constants/equipmentSlots";
import type { ItemTypeId } from "../constants/itemTypeIds";

/**
 * Resolve the equipment slot for an item given its raw game type string.
 *
 * @example
 *   getItemSlot("HELMET")      // → "head"
 *   getItemSlot("ONE_HANDED_AXE") // → "weapon"
 */
export function getItemSlot(gameType: string): EquipmentSlot | undefined {
  const itemTypeId = GAME_TYPE_TO_ITEM_TYPE_ID[gameType] as ItemTypeId | undefined;
  if (!itemTypeId) return undefined;
  return ITEM_TYPE_TO_SLOT[itemTypeId];
}

/**
 * Resolve the equipment slot for an item given its baseTypeID (globally unique
 * numeric ID from items.json equippable[].baseTypeID).
 *
 * @example
 *   getItemSlotByBaseTypeId(0)  // → "head"  (HELMET)
 *   getItemSlotByBaseTypeId(23) // → "weapon" (BOW)
 */
export function getItemSlotByBaseTypeId(baseTypeId: number): EquipmentSlot | undefined {
  const itemTypeId = SUBTYPE_ID_TO_ITEM_TYPE_ID[baseTypeId] as ItemTypeId | undefined;
  if (!itemTypeId) return undefined;
  return ITEM_TYPE_TO_SLOT[itemTypeId];
}
