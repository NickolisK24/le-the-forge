export const DAMAGE_TYPES = [
  "PHYSICAL",
  "FIRE",
  "COLD",
  "LIGHTNING",
  "VOID",
  "NECROTIC",
  "POISON"
] as const;

export type DamageType =
  typeof DAMAGE_TYPES[number];