/**
 * Simulation preset builds — quick-load archetypes for The Forge.
 *
 * Each preset maps to a BuildCreatePayload with pre-filled stats that
 * represent a typical endgame version of the archetype.
 */

import type { CharacterClass } from "@/types";

export interface SimPreset {
  id: string;
  label: string;
  description: string;
  character_class: CharacterClass;
  mastery: string;
  primary_skill: string;
  level: number;
  tags: {
    is_ssf?: boolean;
    is_hc?: boolean;
    is_ladder_viable?: boolean;
    is_budget?: boolean;
  };
}

export const PRESETS: SimPreset[] = [
  {
    id: "runemaster-glacier",
    label: "Glacier Runemaster",
    description: "High-burst cold Mage. Stacks cold damage, crit, and cast speed. Strong late-game scaler.",
    character_class: "Mage",
    mastery: "Runemaster",
    primary_skill: "Glacier",
    level: 90,
    tags: { is_ladder_viable: true },
  },
  {
    id: "necromancer-bones",
    label: "Bone Minion Necromancer",
    description: "Skeleton army with Summon Bone Golem. Off-screen clear and strong defensive layer from minions.",
    character_class: "Acolyte",
    mastery: "Necromancer",
    primary_skill: "Summon Skeleton",
    level: 90,
    tags: { is_budget: true, is_ladder_viable: true },
  },
  {
    id: "falconer-marksman",
    label: "Explosive Trap Falconer",
    description: "Rogue Falconer hybrid. Explosive traps for clear, falcon for boss damage. High ceiling.",
    character_class: "Rogue",
    mastery: "Falconer",
    primary_skill: "Puncture",
    level: 85,
    tags: { is_ladder_viable: true },
  },
  {
    id: "paladin-warpath",
    label: "Warpath Paladin",
    description: "Spinning melee Paladin. Tanky with endurance and resistances, good for hardcore.",
    character_class: "Sentinel",
    mastery: "Paladin",
    primary_skill: "Warpath",
    level: 90,
    tags: { is_hc: true, is_ladder_viable: true },
  },
  {
    id: "shaman-avalanche",
    label: "Avalanche Shaman",
    description: "Cold physical Primalist. Avalanche and ice synergies scale to very high DPS in endgame.",
    character_class: "Primalist",
    mastery: "Shaman",
    primary_skill: "Avalanche",
    level: 85,
    tags: { is_ssf: true },
  },
  {
    id: "bladedancer-shadow",
    label: "Shadow Cascade Bladedancer",
    description: "Fast melee Rogue. Shadow Cascade for clear, Shift for mobility. Budget-friendly early ladder.",
    character_class: "Rogue",
    mastery: "Bladedancer",
    primary_skill: "Shadow Cascade",
    level: 80,
    tags: { is_budget: true },
  },
  {
    id: "void-knight-warpath",
    label: "Void Knight Echo",
    description: "Void Knight Sentinel specialising in Volatile Reversal echoes. Strong single-target.",
    character_class: "Sentinel",
    mastery: "Void Knight",
    primary_skill: "Volatile Reversal",
    level: 88,
    tags: {},
  },
  {
    id: "lich-rip-blood",
    label: "Rip Blood Lich",
    description: "Lich spellcaster. Blood-based necrotic spells with high crit potential and ward stacking.",
    character_class: "Acolyte",
    mastery: "Lich",
    primary_skill: "Rip Blood",
    level: 90,
    tags: {},
  },
];
