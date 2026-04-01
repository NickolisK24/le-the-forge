export const EQUIPMENT_SLOTS = [
  "body",
  "feet",
  "finger",
  "hands",
  "head",
  "idol",
  "neck",
  "offhand",
  "relic",
  "waist",
  "weapon",
] as const;

export type EquipmentSlot =
  typeof EQUIPMENT_SLOTS[number];
