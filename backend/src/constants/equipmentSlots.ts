export const EQUIPMENT_SLOTS = [
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
] as const;

export type EquipmentSlot = typeof EQUIPMENT_SLOTS[number];