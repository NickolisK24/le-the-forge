export const EQUIPMENT_SLOTS = [
  "HELM",
  "BODY_ARMOR",
  "GLOVES",
  "BOOTS",
  "BELT",
  "AMULET",
  "RING",
  "WEAPON",
  "OFFHAND",
  "RELIC"
] as const;

export type EquipmentSlot =
  typeof EQUIPMENT_SLOTS[number];