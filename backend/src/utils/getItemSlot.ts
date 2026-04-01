import { ITEM_TYPE_TO_SLOT } from "../constants/itemTypeToSlot";
import { GAME_TYPE_TO_ITEM_TYPE_ID } from "../constants/gameTypeToItemTypeId";

export function getItemSlot(
  gameType: keyof typeof GAME_TYPE_TO_ITEM_TYPE_ID
) {
  const itemTypeId =
    GAME_TYPE_TO_ITEM_TYPE_ID[
      gameType
    ] as keyof typeof ITEM_TYPE_TO_SLOT;

  return ITEM_TYPE_TO_SLOT[itemTypeId];
}

console.log(
  getItemSlot("ONE_HANDED_AXE")
);