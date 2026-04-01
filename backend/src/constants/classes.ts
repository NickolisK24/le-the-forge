export const BASE_CLASSES = [
  "MAGE",
  "PRIMALIST",
  "SENTINEL",
  "ROGUE",
  "ACOLYTE"
] as const;

export type BaseClass =
  typeof BASE_CLASSES[number];



// Mastery definitions

export const CLASS_MASTERIES = {
  MAGE: [
    "SORCERER",
    "SPELLBLADE",
    "RUNEMASTER"
  ],

  PRIMALIST: [
    "BEASTMASTER",
    "SHAMAN",
    "DRUID"
  ],

  SENTINEL: [
    "PALADIN",
    "VOID_KNIGHT",
    "FORGE_GUARD"
  ],

  ROGUE: [
    "BLADEDANCER",
    "MARKSMAN",
    "FALCONER"
  ],

  ACOLYTE: [
    "LICH",
    "NECROMANCER",
    "WARLOCK"
  ]

} as const;



export type ClassMasteryMap =
  typeof CLASS_MASTERIES;

export type Mastery =
  ClassMasteryMap[BaseClass][number];