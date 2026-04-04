export const DAMAGE_TYPES = [
  "physical",
  "fire",
  "cold",
  "lightning",
  "void",
  "necrotic",
  "poison",
] as const;

export type DamageType = typeof DAMAGE_TYPES[number];