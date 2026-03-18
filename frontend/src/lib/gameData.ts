/**
 * Last Epoch game data — single source of truth for the frontend.
 *
 * Sources:
 *   - lastepoch.fandom.com/wiki/Skills
 *   - lastepoch.fandom.com/wiki/Acolyte / Mage / Primalist / Sentinel / Rogue
 *   - maxroll.gg/last-epoch/resources/passives-and-skills
 *   - In-game data from patch 1.2.x
 *
 * Notes:
 *   - Skills max at level 20 by default; +skill level from gear can push beyond
 *   - Each class has a full skill pool; player picks any 5 to specialize
 *   - Passive tree has 4 sections per class: base class + 3 masteries
 *   - Points: max 113 total. Up to 25 in each non-chosen mastery half-tree
 */

import type { CharacterClass } from "@/types";

// ---------------------------------------------------------------------------
// Class colors
// ---------------------------------------------------------------------------

export const CLASS_COLORS: Record<CharacterClass, string> = {
  Acolyte:  "#b870ff",
  Mage:     "#00d4f5",
  Primalist:"#3dca74",
  Sentinel: "#f0a020",
  Rogue:    "#ff5050",
};

// ---------------------------------------------------------------------------
// Masteries
// ---------------------------------------------------------------------------

export const MASTERIES: Record<CharacterClass, string[]> = {
  Acolyte:   ["Necromancer", "Lich", "Warlock"],
  Mage:      ["Runemaster", "Sorcerer", "Spellblade"],
  Primalist: ["Druid", "Beastmaster", "Shaman"],
  Sentinel:  ["Forge Guard", "Paladin", "Void Knight"],
  Rogue:     ["Bladedancer", "Marksman", "Falconer"],
};

// ---------------------------------------------------------------------------
// Skills — full pool per class
// Players pick any 5 to specialize. Mastery-exclusive skills are tagged.
// ---------------------------------------------------------------------------

export interface SkillDef {
  name: string;
  mastery?: string;   // undefined = base class skill, available to all masteries
  tags: string[];     // e.g. ["Spell", "Necrotic", "DoT"]
  icon: string;       // emoji stand-in until real icons are wired
}

export const CLASS_SKILLS: Record<CharacterClass, SkillDef[]> = {
  Acolyte: [
    // Base skills
    { name: "Rip Blood",           tags: ["Spell","Physical","Self-Cast"],     icon: "🩸" },
    { name: "Bone Curse",          tags: ["Spell","Necrotic","Curse","DoT"],   icon: "🦴" },
    { name: "Transplant",          tags: ["Spell","Physical","Movement"],      icon: "⚗️" },
    { name: "Marrow Shards",       tags: ["Spell","Physical","Projectile"],    icon: "🔮" },
    { name: "Hungering Souls",     tags: ["Spell","Necrotic","Projectile"],    icon: "👻" },
    { name: "Harvest",             tags: ["Spell","Physical","Melee"],         icon: "⚔️" },
    { name: "Infernal Shade",      tags: ["Spell","Fire","DoT","Debuff"],      icon: "🔥" },
    { name: "Mark for Death",      tags: ["Debuff","Necrotic"],                icon: "🎯" },
    { name: "Spirit Plague",       tags: ["Spell","Necrotic","DoT","Curse"],   icon: "💀" },
    { name: "Summon Skeleton",     tags: ["Minion","Spell"],                   icon: "💀" },
    { name: "Summon Bone Golem",   tags: ["Minion","Spell"],                   icon: "🗿" },
    { name: "Summon Volatile Zombie", tags: ["Minion","Spell","Fire"],         icon: "🧟" },
    { name: "Wandering Spirits",   tags: ["Spell","Necrotic","DoT"],           icon: "👻" },
    // Necromancer exclusive
    { name: "Summon Skeletal Mage",  mastery: "Necromancer", tags: ["Minion","Spell"], icon: "🧙" },
    { name: "Dread Shade",           mastery: "Necromancer", tags: ["Minion","Aura","Necrotic"], icon: "🌑" },
    { name: "Assemble Abomination",  mastery: "Necromancer", tags: ["Minion","Spell"], icon: "🧟" },
    { name: "Summon Wraith",         mastery: "Necromancer", tags: ["Minion","Spell","Necrotic"], icon: "👁️" },
    // Lich exclusive
    { name: "Reaper Form",    mastery: "Lich", tags: ["Transformation","Necrotic"],   icon: "💀" },
    { name: "Death Seal",     mastery: "Lich", tags: ["Spell","Necrotic","Self-Cast"], icon: "🔒" },
    { name: "Drain Life",     mastery: "Lich", tags: ["Spell","Necrotic","Channel","Leech"], icon: "🩸" },
    { name: "Aura of Decay",  mastery: "Lich", tags: ["Aura","Necrotic","Poison","DoT"], icon: "☠️" },
    // Warlock exclusive
    { name: "Chthonic Fissure", mastery: "Warlock", tags: ["Spell","Void","Necrotic"], icon: "🌑" },
    { name: "Soul Feast",       mastery: "Warlock", tags: ["Spell","Necrotic","Leech"], icon: "👁️" },
    { name: "Profane Veil",     mastery: "Warlock", tags: ["Spell","Curse","Ward"],    icon: "🌀" },
    { name: "Chaos Bolts",      mastery: "Warlock", tags: ["Spell","Fire","Necrotic","Projectile"], icon: "🔴" },
  ],

  Mage: [
    // Base skills
    { name: "Glacier",          tags: ["Spell","Cold","AoE"],              icon: "❄️" },
    { name: "Fireball",         tags: ["Spell","Fire","Projectile"],       icon: "🔥" },
    { name: "Lightning Blast",  tags: ["Spell","Lightning","Projectile"],  icon: "⚡" },
    { name: "Mana Strike",      tags: ["Melee","Spell","Lightning"],       icon: "✨" },
    { name: "Teleport",         tags: ["Movement","Spell"],                icon: "🌀" },
    { name: "Surge",            tags: ["Melee","Lightning","Movement"],    icon: "⚡" },
    { name: "Frost Claw",       tags: ["Spell","Cold","Projectile"],       icon: "❄️" },
    { name: "Static Orb",       tags: ["Spell","Lightning","AoE"],        icon: "🔵" },
    { name: "Volcanic Orb",     tags: ["Spell","Fire","AoE"],             icon: "🟠" },
    { name: "Disintegrate",     tags: ["Spell","Fire","Lightning","Channel"], icon: "🔆" },
    // Sorcerer exclusive
    { name: "Shatter Strike",   mastery: "Sorcerer", tags: ["Melee","Cold"],          icon: "🔷" },
    { name: "Flame Ward",       mastery: "Sorcerer", tags: ["Spell","Fire","Ward","Defense"], icon: "🛡️" },
    { name: "Meteor",           mastery: "Sorcerer", tags: ["Spell","Fire","AoE"],   icon: "☄️" },
    { name: "Nova",             mastery: "Sorcerer", tags: ["Spell","Cold","Lightning","AoE"], icon: "💥" },
    // Spellblade exclusive
    { name: "Shatter Strike",   mastery: "Spellblade", tags: ["Melee","Cold"],        icon: "🔷" },
    { name: "Enchant Weapon",   mastery: "Spellblade", tags: ["Buff","Melee","Fire"], icon: "🗡️" },
    { name: "Mana Strike",      mastery: "Spellblade", tags: ["Melee","Lightning"],   icon: "✨" },
    { name: "Snap Freeze",      mastery: "Spellblade", tags: ["Spell","Cold","AoE","Freeze"], icon: "🧊" },
    // Runemaster exclusive
    { name: "Rune of Winter",   mastery: "Runemaster", tags: ["Spell","Cold","Rune"], icon: "❄️" },
    { name: "Runic Invocation", mastery: "Runemaster", tags: ["Spell","Rune"],        icon: "🔮" },
    { name: "Runic Bolt",       mastery: "Runemaster", tags: ["Spell","Rune","Projectile"], icon: "🔵" },
  ],

  Primalist: [
    // Base skills
    { name: "Summon Wolf",       tags: ["Minion","Companion"],              icon: "🐺" },
    { name: "Warcry",            tags: ["Buff","Melee","AoE"],              icon: "📯" },
    { name: "Entangling Roots",  tags: ["Spell","Physical","DoT","AoE"],   icon: "🌿" },
    { name: "Fury Leap",         tags: ["Movement","Melee","Physical"],     icon: "🦘" },
    { name: "Maelstrom",         tags: ["Spell","Lightning","AoE","DoT"],   icon: "🌪️" },
    { name: "Avalanche",         tags: ["Spell","Physical","Cold","AoE"],   icon: "🏔️" },
    { name: "Ice Thorns",        tags: ["Spell","Cold","AoE"],              icon: "❄️" },
    { name: "Tornado",           tags: ["Spell","Lightning","AoE"],         icon: "🌪️" },
    { name: "Serpent Strike",    tags: ["Melee","Physical","Poison"],       icon: "🐍" },
    { name: "Gathering Storm",   tags: ["Spell","Lightning","DoT"],         icon: "⛈️" },
    // Druid exclusive
    { name: "Werebear Form",    mastery: "Druid", tags: ["Transformation","Physical","Cold"], icon: "🐻" },
    { name: "Spriggan Form",    mastery: "Druid", tags: ["Transformation","Physical","Poison"], icon: "🌱" },
    { name: "Swipe",            mastery: "Druid", tags: ["Melee","Physical","Cold"],          icon: "🐾" },
    { name: "Thorn Totem",      mastery: "Druid", tags: ["Totem","Physical","Poison"],        icon: "🌵" },
    // Beastmaster exclusive
    { name: "Summon Raptor",    mastery: "Beastmaster", tags: ["Companion","Minion"],        icon: "🦖" },
    { name: "Summon Bear",      mastery: "Beastmaster", tags: ["Companion","Minion"],        icon: "🐻" },
    { name: "Summon Sabertooth",mastery: "Beastmaster", tags: ["Companion","Minion"],        icon: "🐱" },
    { name: "Scorpion Aspect",  mastery: "Beastmaster", tags: ["Buff","Poison","Companion"], icon: "🦂" },
    // Shaman exclusive
    { name: "Summon Storm Totem", mastery: "Shaman", tags: ["Totem","Lightning"],    icon: "⚡" },
    { name: "Summon Thorn Totem", mastery: "Shaman", tags: ["Totem","Physical"],     icon: "🌿" },
    { name: "Earthquake",         mastery: "Shaman", tags: ["Spell","Physical","AoE"], icon: "💥" },
    { name: "Vessel of Chaos",    mastery: "Shaman", tags: ["Minion","Totem"],        icon: "🫙" },
  ],

  Sentinel: [
    // Base skills
    { name: "Lunge",              tags: ["Movement","Melee","Physical"],    icon: "⚔️" },
    { name: "Rive",               tags: ["Melee","Physical","AoE"],         icon: "🗡️" },
    { name: "Warpath",            tags: ["Melee","Physical","Movement","Channel"], icon: "🌪️" },
    { name: "Shield Rush",        tags: ["Movement","Melee","Physical"],    icon: "🛡️" },
    { name: "Javelin",            tags: ["Melee","Physical","Throwing","Lightning"], icon: "🏹" },
    { name: "Smite",              tags: ["Spell","Lightning","Fire","Melee"], icon: "⚡" },
    { name: "Ring of Shields",    tags: ["Minion","Physical","Defense"],    icon: "🔵" },
    { name: "Smelter's Wrath",    tags: ["Melee","Fire","Physical"],        icon: "🔥" },
    { name: "Healing Hands",      tags: ["Spell","Healing","Lightning"],    icon: "🤲" },
    // Forge Guard exclusive
    { name: "Manifest Armor",    mastery: "Forge Guard", tags: ["Minion","Physical","Defense"], icon: "🛡️" },
    { name: "Forge Strike",      mastery: "Forge Guard", tags: ["Melee","Fire","Physical"],     icon: "🔨" },
    { name: "Shield Throw",      mastery: "Forge Guard", tags: ["Throwing","Physical"],         icon: "🛡️" },
    // Paladin exclusive
    { name: "Volatile Reversal", mastery: "Paladin", tags: ["Spell","Void","Movement"],         icon: "⏪" },
    { name: "Holy Aura",         mastery: "Paladin", tags: ["Aura","Lightning","Healing"],      icon: "✨" },
    { name: "Judgement",         mastery: "Paladin", tags: ["Spell","Lightning","Fire","AoE"],  icon: "⚖️" },
    { name: "Consecrated Ground",mastery: "Paladin", tags: ["Spell","Fire","Lightning","AoE"],  icon: "🌟" },
    // Void Knight exclusive
    { name: "Anomaly",           mastery: "Void Knight", tags: ["Spell","Void","AoE"],          icon: "🌀" },
    { name: "Devouring Orb",     mastery: "Void Knight", tags: ["Spell","Void","Projectile"],   icon: "⚫" },
    { name: "Erasing Strike",    mastery: "Void Knight", tags: ["Melee","Void"],                icon: "💨" },
    { name: "Void Cleave",       mastery: "Void Knight", tags: ["Melee","Void","AoE"],          icon: "🌑" },
  ],

  Rogue: [
    // Base skills
    { name: "Shift",             tags: ["Movement","Spell"],                 icon: "👤" },
    { name: "Flurry",            tags: ["Melee","Physical","Bow","Dexterity"], icon: "💨" },
    { name: "Puncture",          tags: ["Melee","Physical","DoT","Poison"],  icon: "🎯" },
    { name: "Smoke Bomb",        tags: ["Spell","AoE","Debuff"],             icon: "💣" },
    { name: "Acid Flask",        tags: ["Throwing","Poison","DoT","AoE"],    icon: "⚗️" },
    { name: "Arrow Barrage",     tags: ["Bow","Physical","AoE"],             icon: "🏹" },
    { name: "Detonating Arrow",  tags: ["Bow","Fire","AoE","DoT"],           icon: "💥" },
    { name: "Explosive Trap",    tags: ["Trap","Fire","AoE"],                icon: "💣" },
    { name: "Flurry",            tags: ["Melee","Physical"],                 icon: "💨" },
    { name: "Shurikens",         tags: ["Throwing","Physical","Dexterity"],  icon: "⭐" },
    // Bladedancer exclusive
    { name: "Shadow Cascade",  mastery: "Bladedancer", tags: ["Melee","Physical","Void","AoE"], icon: "🌑" },
    { name: "Dancing Strikes", mastery: "Bladedancer", tags: ["Melee","Physical","Movement"],   icon: "⚔️" },
    { name: "Blade Flurry",    mastery: "Bladedancer", tags: ["Melee","Physical","AoE"],        icon: "🗡️" },
    { name: "Synchronized Strike", mastery: "Bladedancer", tags: ["Melee","Physical","Void"],  icon: "✦" },
    // Marksman exclusive
    { name: "Multishot",       mastery: "Marksman", tags: ["Bow","Physical","AoE"],             icon: "🏹" },
    { name: "Ballista",        mastery: "Marksman", tags: ["Totem","Bow","Physical"],            icon: "🎯" },
    { name: "Rain of Arrows",  mastery: "Marksman", tags: ["Bow","Physical","AoE","DoT"],       icon: "🌧️" },
    { name: "Hail of Arrows",  mastery: "Marksman", tags: ["Bow","Physical","Cold"],             icon: "❄️" },
    // Falconer exclusive
    { name: "Falcon Strikes",  mastery: "Falconer", tags: ["Companion","Physical"],              icon: "🦅" },
    { name: "Net",             mastery: "Falconer", tags: ["Trap","Physical","Debuff"],           icon: "🕸️" },
    { name: "Aerial Assault",  mastery: "Falconer", tags: ["Companion","Physical","Movement"],   icon: "🦅" },
    { name: "Dive Bomb",       mastery: "Falconer", tags: ["Companion","Physical","AoE"],        icon: "💥" },
  ],
};

// ---------------------------------------------------------------------------
// Passive tree region definitions
// Used to draw distinct zones on the canvas
// ---------------------------------------------------------------------------

export interface PassiveRegion {
  id: string;
  label: string;
  color: string;
  yStart: number;  // 0.0 - 1.0 as fraction of canvas height
  yEnd: number;
  isBase: boolean;
}

export const PASSIVE_REGIONS: Record<CharacterClass, PassiveRegion[]> = {
  Acolyte: [
    { id: "base",        label: "Acolyte",      color: "#6a4a9a", yStart: 0.0,  yEnd: 0.28, isBase: true  },
    { id: "necromancer", label: "Necromancer",   color: "#4a3a7a", yStart: 0.28, yEnd: 0.52, isBase: false },
    { id: "lich",        label: "Lich",          color: "#7a3a5a", yStart: 0.52, yEnd: 0.76, isBase: false },
    { id: "warlock",     label: "Warlock",       color: "#5a2a6a", yStart: 0.76, yEnd: 1.0,  isBase: false },
  ],
  Mage: [
    { id: "base",        label: "Mage",          color: "#2a5a8a", yStart: 0.0,  yEnd: 0.28, isBase: true  },
    { id: "runemaster",  label: "Runemaster",    color: "#1a4a7a", yStart: 0.28, yEnd: 0.52, isBase: false },
    { id: "sorcerer",    label: "Sorcerer",      color: "#2a3a8a", yStart: 0.52, yEnd: 0.76, isBase: false },
    { id: "spellblade",  label: "Spellblade",    color: "#3a4a8a", yStart: 0.76, yEnd: 1.0,  isBase: false },
  ],
  Primalist: [
    { id: "base",        label: "Primalist",     color: "#2a6a2a", yStart: 0.0,  yEnd: 0.28, isBase: true  },
    { id: "druid",       label: "Druid",         color: "#1a5a3a", yStart: 0.28, yEnd: 0.52, isBase: false },
    { id: "beastmaster", label: "Beastmaster",   color: "#4a5a1a", yStart: 0.52, yEnd: 0.76, isBase: false },
    { id: "shaman",      label: "Shaman",        color: "#2a4a5a", yStart: 0.76, yEnd: 1.0,  isBase: false },
  ],
  Sentinel: [
    { id: "base",        label: "Sentinel",      color: "#7a4a1a", yStart: 0.0,  yEnd: 0.28, isBase: true  },
    { id: "forge-guard", label: "Forge Guard",   color: "#6a3a1a", yStart: 0.28, yEnd: 0.52, isBase: false },
    { id: "paladin",     label: "Paladin",       color: "#7a5a1a", yStart: 0.52, yEnd: 0.76, isBase: false },
    { id: "void-knight", label: "Void Knight",   color: "#3a2a5a", yStart: 0.76, yEnd: 1.0,  isBase: false },
  ],
  Rogue: [
    { id: "base",        label: "Rogue",         color: "#7a2a2a", yStart: 0.0,  yEnd: 0.28, isBase: true  },
    { id: "bladedancer", label: "Bladedancer",   color: "#6a1a3a", yStart: 0.28, yEnd: 0.52, isBase: false },
    { id: "marksman",    label: "Marksman",      color: "#5a3a2a", yStart: 0.52, yEnd: 0.76, isBase: false },
    { id: "falconer",    label: "Falconer",      color: "#4a4a2a", yStart: 0.76, yEnd: 1.0,  isBase: false },
  ],
};

// ---------------------------------------------------------------------------
// PassiveNode type — shared between BuildPlannerPage and simulation engine
// ---------------------------------------------------------------------------

export type NodeType = "core" | "notable" | "keystone" | "mastery-gate";

export interface PassiveNode {
  id: number;
  x: number;
  y: number;
  type: NodeType;
  name: string;
  regionId: string;
  /** Maximum points that can be invested in this node (1 for keystone/toggle, 2-5 for notable, 1-8 for core) */
  maxPoints?: number;
  /** Parent node ID — required connection for prerequisite enforcement */
  parentId?: number;
}

// ---------------------------------------------------------------------------
// Gear types for simulation
// ---------------------------------------------------------------------------

export interface GearAffix {
  name: string;
  tier: number;   // 1 = best (T1), 5 = worst (T5) in Last Epoch
  value: number;  // midpoint of tier range
}

export interface GearItem {
  slot: string;
  item_type?: string;
  rarity: "normal" | "magic" | "rare" | "exalted";
  affixes: GearAffix[];
}

// ---------------------------------------------------------------------------
// Class base stats — seed values for the simulation engine
// ---------------------------------------------------------------------------

export const CLASS_BASE_STATS: Record<CharacterClass, {
  health: number; mana: number;
  strength: number; intelligence: number; dexterity: number; vitality: number; attunement: number;
  base_damage: number; crit_chance: number; crit_multiplier: number; attack_speed: number;
}> = {
  Acolyte:   { health: 380, mana: 120, strength: 5,  intelligence: 15, dexterity: 5,  vitality: 8,  attunement: 12, base_damage: 80,  crit_chance: 0.05, crit_multiplier: 1.5, attack_speed: 1.0 },
  Mage:      { health: 340, mana: 180, strength: 3,  intelligence: 20, dexterity: 7,  vitality: 6,  attunement: 14, base_damage: 100, crit_chance: 0.05, crit_multiplier: 1.5, attack_speed: 1.0 },
  Primalist: { health: 480, mana: 80,  strength: 18, intelligence: 5,  dexterity: 8,  vitality: 14, attunement: 5,  base_damage: 90,  crit_chance: 0.05, crit_multiplier: 1.5, attack_speed: 1.2 },
  Sentinel:  { health: 520, mana: 60,  strength: 20, intelligence: 5,  dexterity: 5,  vitality: 16, attunement: 4,  base_damage: 110, crit_chance: 0.05, crit_multiplier: 1.5, attack_speed: 0.9 },
  Rogue:     { health: 400, mana: 100, strength: 8,  intelligence: 8,  dexterity: 18, vitality: 9,  attunement: 7,  base_damage: 85,  crit_chance: 0.07, crit_multiplier: 1.5, attack_speed: 1.3 },
};

// ---------------------------------------------------------------------------
// Mastery bonuses applied on top of class base stats
// ---------------------------------------------------------------------------

export const MASTERY_BONUSES: Partial<Record<string, Record<string, number>>> = {
  Paladin:     { max_health: 200 },
  Necromancer: { minion_damage_pct: 15 },
  Runemaster:  { spell_damage_pct: 10 },
  Sorcerer:    { spell_damage_pct: 15, cast_speed: 5 },
  Bladedancer: { physical_damage_pct: 15 },
  Marksman:    { physical_damage_pct: 10, attack_speed_pct: 5 },
  Warlock:     { necrotic_damage_pct: 10, void_damage_pct: 10 },
  Lich:        {},  // handled with per-point bonuses in simulation.ts
  "Forge Guard": {},  // handled with per-point bonuses in simulation.ts
};

// ---------------------------------------------------------------------------
// Keystone passive bonuses — by keystone name
// ---------------------------------------------------------------------------

export const KEYSTONE_BONUSES: Record<string, Record<string, number>> = {
  // Acolyte keystones
  "Death's Door":         { max_health: 200, armour: -50 },
  "Soul Aegis":           { ward: 50, ward_retention_pct: 15 },
  "Forbidden Knowledge":  { spell_damage_pct: 20, crit_chance_pct: 5 },
  "Grave Chill":          { cold_damage_pct: 15, necrotic_damage_pct: 10 },
  "Stolen Vitality":      { max_health: 150, spell_damage_pct: 10 },
  // Mage keystones
  "Arcane Absorption":    { spell_damage_pct: 20, max_mana: 30 },
  "Mana Starved Sorcery": { spell_damage_pct: 40 },
  "Runic Convergence":    { spell_damage_pct: 25, cast_speed: 10 },
  "Spell Blade":          { physical_damage_pct: 20, spell_damage_pct: 15 },
  // Primalist keystones
  "Natural Attunement":   { cold_damage_pct: 10, lightning_damage_pct: 10, max_health: 20 },
  "Ancient Power":        { physical_damage_pct: 25 },
  "Nature's Reach":       { lightning_damage_pct: 15 },
  "Primal Strength":      { physical_damage_pct: 20, max_health: 100 },
  // Sentinel keystones
  "Juggernaut":           { armour: 200, max_health: 100 },
  "Forged in Fire":       { fire_damage_pct: 30, armour: 100 },
  "Void Touched":         { void_damage_pct: 30 },
  "Sacred Aegis":         { fire_res: 50, cold_res: 50 },
  // Rogue keystones
  "Shadow Daggers":       { physical_damage_pct: 20, crit_chance_pct: 5 },
  "Expose Weakness":      { physical_damage_pct: 30 },
  "Acrobatics":           { dodge_rating: 150 },
  "Cheap Shot":           { physical_damage_pct: 25, crit_chance_pct: 3 },
};

// ---------------------------------------------------------------------------
// Skill stats — base damage + scaling for DPS calculation
// ---------------------------------------------------------------------------

export interface SkillStatDef {
  baseDamage: number;       // at level 1
  levelScaling: number;     // damage multiplier per level (e.g. 0.12 = +12% per level)
  attackSpeed: number;      // base casts/attacks per second
  damageType: string;
  scalingStats: string[];   // keys in BuildStats that add % damage
  isSpell?: boolean;
  isMelee?: boolean;
}

export const SKILL_STATS: Record<string, SkillStatDef> = {
  // --- Acolyte ---
  "Rip Blood":              { baseDamage: 80,  levelScaling: 0.12, attackSpeed: 1.8, damageType: "Physical",  scalingStats: ["spell_damage_pct"], isSpell: true },
  "Bone Curse":             { baseDamage: 60,  levelScaling: 0.10, attackSpeed: 1.2, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Transplant":             { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["spell_damage_pct"], isSpell: true },
  "Marrow Shards":          { baseDamage: 70,  levelScaling: 0.11, attackSpeed: 2.0, damageType: "Physical",  scalingStats: ["spell_damage_pct"], isSpell: true },
  "Hungering Souls":        { baseDamage: 90,  levelScaling: 0.13, attackSpeed: 1.5, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Harvest":                { baseDamage: 100, levelScaling: 0.14, attackSpeed: 1.0, damageType: "Physical",  scalingStats: ["spell_damage_pct"], isSpell: true, isMelee: true },
  "Infernal Shade":         { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct"], isSpell: true },
  "Mark for Death":         { baseDamage: 20,  levelScaling: 0.06, attackSpeed: 0.4, damageType: "Necrotic",  scalingStats: ["necrotic_damage_pct"], isSpell: true },
  "Spirit Plague":          { baseDamage: 30,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Summon Skeleton":        { baseDamage: 60,  levelScaling: 0.10, attackSpeed: 1.0, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  "Summon Bone Golem":      { baseDamage: 120, levelScaling: 0.12, attackSpeed: 0.8, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  "Summon Volatile Zombie": { baseDamage: 200, levelScaling: 0.15, attackSpeed: 0.3, damageType: "Fire",      scalingStats: ["minion_damage_pct", "fire_damage_pct"] },
  "Wandering Spirits":      { baseDamage: 50,  levelScaling: 0.09, attackSpeed: 0.8, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Summon Skeletal Mage":   { baseDamage: 80,  levelScaling: 0.11, attackSpeed: 1.0, damageType: "Necrotic",  scalingStats: ["minion_damage_pct", "necrotic_damage_pct"] },
  "Dread Shade":            { baseDamage: 35,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Necrotic",  scalingStats: ["minion_damage_pct", "necrotic_damage_pct"] },
  "Assemble Abomination":   { baseDamage: 180, levelScaling: 0.14, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  "Summon Wraith":          { baseDamage: 70,  levelScaling: 0.10, attackSpeed: 1.2, damageType: "Necrotic",  scalingStats: ["minion_damage_pct", "necrotic_damage_pct"] },
  "Reaper Form":            { baseDamage: 120, levelScaling: 0.15, attackSpeed: 1.4, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Death Seal":             { baseDamage: 150, levelScaling: 0.14, attackSpeed: 0.4, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Drain Life":             { baseDamage: 45,  levelScaling: 0.09, attackSpeed: 1.0, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Aura of Decay":          { baseDamage: 25,  levelScaling: 0.07, attackSpeed: 0.5, damageType: "Poison",    scalingStats: ["poison_damage_pct"], isSpell: true },
  "Chthonic Fissure":       { baseDamage: 150, levelScaling: 0.14, attackSpeed: 0.8, damageType: "Void",      scalingStats: ["spell_damage_pct", "void_damage_pct"], isSpell: true },
  "Soul Feast":             { baseDamage: 80,  levelScaling: 0.11, attackSpeed: 1.2, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Profane Veil":           { baseDamage: 30,  levelScaling: 0.07, attackSpeed: 0.4, damageType: "Necrotic",  scalingStats: ["spell_damage_pct", "necrotic_damage_pct"], isSpell: true },
  "Chaos Bolts":            { baseDamage: 100, levelScaling: 0.12, attackSpeed: 1.8, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct", "necrotic_damage_pct"], isSpell: true },
  // --- Mage ---
  "Glacier":                { baseDamage: 120, levelScaling: 0.13, attackSpeed: 0.9, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isSpell: true },
  "Fireball":               { baseDamage: 110, levelScaling: 0.12, attackSpeed: 1.2, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct"], isSpell: true },
  "Lightning Blast":        { baseDamage: 95,  levelScaling: 0.11, attackSpeed: 1.5, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Mana Strike":            { baseDamage: 80,  levelScaling: 0.10, attackSpeed: 2.0, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isMelee: true, isSpell: true },
  "Teleport":               { baseDamage: 50,  levelScaling: 0.09, attackSpeed: 0.5, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Surge":                  { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 1.6, damageType: "Lightning", scalingStats: ["lightning_damage_pct"], isMelee: true },
  "Frost Claw":             { baseDamage: 85,  levelScaling: 0.11, attackSpeed: 1.8, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isSpell: true },
  "Static Orb":             { baseDamage: 100, levelScaling: 0.12, attackSpeed: 1.0, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Volcanic Orb":           { baseDamage: 130, levelScaling: 0.13, attackSpeed: 0.8, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct"], isSpell: true },
  "Disintegrate":           { baseDamage: 60,  levelScaling: 0.09, attackSpeed: 1.0, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Shatter Strike":         { baseDamage: 130, levelScaling: 0.12, attackSpeed: 1.3, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isMelee: true },
  "Flame Ward":             { baseDamage: 50,  levelScaling: 0.08, attackSpeed: 0.3, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct"], isSpell: true },
  "Meteor":                 { baseDamage: 300, levelScaling: 0.16, attackSpeed: 0.4, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct"], isSpell: true },
  "Nova":                   { baseDamage: 180, levelScaling: 0.14, attackSpeed: 0.7, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Enchant Weapon":         { baseDamage: 80,  levelScaling: 0.10, attackSpeed: 1.0, damageType: "Fire",      scalingStats: ["fire_damage_pct"], isSpell: true },
  "Snap Freeze":            { baseDamage: 160, levelScaling: 0.14, attackSpeed: 0.7, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isSpell: true },
  "Rune of Winter":         { baseDamage: 140, levelScaling: 0.13, attackSpeed: 0.9, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isSpell: true },
  "Runic Invocation":       { baseDamage: 200, levelScaling: 0.15, attackSpeed: 0.6, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct", "fire_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Runic Bolt":             { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 1.6, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  // --- Primalist ---
  "Summon Wolf":            { baseDamage: 75,  levelScaling: 0.10, attackSpeed: 1.5, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Warcry":                 { baseDamage: 30,  levelScaling: 0.06, attackSpeed: 0.3, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Entangling Roots":       { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["spell_damage_pct"], isSpell: true },
  "Fury Leap":              { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Maelstrom":              { baseDamage: 55,  levelScaling: 0.09, attackSpeed: 0.8, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Avalanche":              { baseDamage: 180, levelScaling: 0.14, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["spell_damage_pct", "physical_damage_pct", "cold_damage_pct"], isSpell: true },
  "Ice Thorns":             { baseDamage: 65,  levelScaling: 0.10, attackSpeed: 1.2, damageType: "Cold",      scalingStats: ["spell_damage_pct", "cold_damage_pct"], isSpell: true },
  "Tornado":                { baseDamage: 65,  levelScaling: 0.10, attackSpeed: 0.6, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Serpent Strike":         { baseDamage: 70,  levelScaling: 0.11, attackSpeed: 2.2, damageType: "Physical",  scalingStats: ["physical_damage_pct", "poison_damage_pct"], isMelee: true },
  "Gathering Storm":        { baseDamage: 45,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Werebear Form":          { baseDamage: 130, levelScaling: 0.13, attackSpeed: 1.3, damageType: "Physical",  scalingStats: ["physical_damage_pct", "cold_damage_pct"], isMelee: true },
  "Spriggan Form":          { baseDamage: 80,  levelScaling: 0.10, attackSpeed: 1.0, damageType: "Physical",  scalingStats: ["physical_damage_pct", "poison_damage_pct"], isMelee: true },
  "Swipe":                  { baseDamage: 110, levelScaling: 0.12, attackSpeed: 1.4, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Thorn Totem":            { baseDamage: 55,  levelScaling: 0.09, attackSpeed: 1.0, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct", "poison_damage_pct"] },
  "Summon Raptor":          { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 1.8, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Summon Bear":            { baseDamage: 150, levelScaling: 0.13, attackSpeed: 0.9, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  "Summon Sabertooth":      { baseDamage: 110, levelScaling: 0.12, attackSpeed: 1.5, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Scorpion Aspect":        { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Poison",    scalingStats: ["poison_damage_pct", "minion_damage_pct"] },
  "Summon Storm Totem":     { baseDamage: 85,  levelScaling: 0.11, attackSpeed: 1.2, damageType: "Lightning", scalingStats: ["minion_damage_pct", "lightning_damage_pct"] },
  "Summon Thorn Totem":     { baseDamage: 60,  levelScaling: 0.10, attackSpeed: 1.2, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Earthquake":             { baseDamage: 250, levelScaling: 0.15, attackSpeed: 0.4, damageType: "Physical",  scalingStats: ["spell_damage_pct", "physical_damage_pct"], isSpell: true },
  "Vessel of Chaos":        { baseDamage: 100, levelScaling: 0.12, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  // --- Sentinel ---
  "Lunge":                  { baseDamage: 80,  levelScaling: 0.11, attackSpeed: 0.8, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Rive":                   { baseDamage: 100, levelScaling: 0.12, attackSpeed: 1.8, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Warpath":                { baseDamage: 85,  levelScaling: 0.11, attackSpeed: 1.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Shield Rush":            { baseDamage: 70,  levelScaling: 0.10, attackSpeed: 0.7, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Javelin":                { baseDamage: 130, levelScaling: 0.12, attackSpeed: 1.4, damageType: "Physical",  scalingStats: ["physical_damage_pct", "lightning_damage_pct"] },
  "Smite":                  { baseDamage: 120, levelScaling: 0.13, attackSpeed: 1.2, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], isSpell: true, isMelee: true },
  "Ring of Shields":        { baseDamage: 50,  levelScaling: 0.09, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Smelter's Wrath":        { baseDamage: 110, levelScaling: 0.12, attackSpeed: 1.2, damageType: "Fire",      scalingStats: ["fire_damage_pct"], isMelee: true },
  "Healing Hands":          { baseDamage: 60,  levelScaling: 0.09, attackSpeed: 0.8, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Manifest Armor":         { baseDamage: 80,  levelScaling: 0.10, attackSpeed: 0.8, damageType: "Physical",  scalingStats: ["minion_damage_pct"] },
  "Forge Strike":           { baseDamage: 140, levelScaling: 0.13, attackSpeed: 1.0, damageType: "Fire",      scalingStats: ["fire_damage_pct", "physical_damage_pct"], isMelee: true },
  "Shield Throw":           { baseDamage: 110, levelScaling: 0.12, attackSpeed: 1.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Volatile Reversal":      { baseDamage: 100, levelScaling: 0.12, attackSpeed: 0.6, damageType: "Void",      scalingStats: ["void_damage_pct"], isSpell: true },
  "Holy Aura":              { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.3, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Judgement":              { baseDamage: 200, levelScaling: 0.15, attackSpeed: 0.6, damageType: "Lightning", scalingStats: ["spell_damage_pct", "lightning_damage_pct", "fire_damage_pct"], isSpell: true },
  "Consecrated Ground":     { baseDamage: 60,  levelScaling: 0.09, attackSpeed: 0.4, damageType: "Fire",      scalingStats: ["spell_damage_pct", "fire_damage_pct", "lightning_damage_pct"], isSpell: true },
  "Anomaly":                { baseDamage: 160, levelScaling: 0.14, attackSpeed: 0.5, damageType: "Void",      scalingStats: ["spell_damage_pct", "void_damage_pct"], isSpell: true },
  "Devouring Orb":          { baseDamage: 100, levelScaling: 0.12, attackSpeed: 1.0, damageType: "Void",      scalingStats: ["spell_damage_pct", "void_damage_pct"], isSpell: true },
  "Erasing Strike":         { baseDamage: 180, levelScaling: 0.14, attackSpeed: 0.9, damageType: "Void",      scalingStats: ["void_damage_pct"], isMelee: true },
  "Void Cleave":            { baseDamage: 160, levelScaling: 0.13, attackSpeed: 1.1, damageType: "Void",      scalingStats: ["void_damage_pct"], isMelee: true },
  // --- Rogue ---
  "Shift":                  { baseDamage: 50,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isSpell: true },
  "Flurry":                 { baseDamage: 65,  levelScaling: 0.10, attackSpeed: 3.0, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Puncture":               { baseDamage: 80,  levelScaling: 0.11, attackSpeed: 2.0, damageType: "Physical",  scalingStats: ["physical_damage_pct", "poison_damage_pct"], isMelee: true },
  "Smoke Bomb":             { baseDamage: 30,  levelScaling: 0.07, attackSpeed: 0.4, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Acid Flask":             { baseDamage: 35,  levelScaling: 0.07, attackSpeed: 0.6, damageType: "Poison",    scalingStats: ["poison_damage_pct"] },
  "Arrow Barrage":          { baseDamage: 70,  levelScaling: 0.10, attackSpeed: 2.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Detonating Arrow":       { baseDamage: 130, levelScaling: 0.13, attackSpeed: 1.2, damageType: "Fire",      scalingStats: ["fire_damage_pct", "physical_damage_pct"] },
  "Explosive Trap":         { baseDamage: 120, levelScaling: 0.12, attackSpeed: 0.5, damageType: "Fire",      scalingStats: ["fire_damage_pct"] },
  "Shurikens":              { baseDamage: 55,  levelScaling: 0.09, attackSpeed: 3.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Shadow Cascade":         { baseDamage: 120, levelScaling: 0.13, attackSpeed: 1.6, damageType: "Physical",  scalingStats: ["physical_damage_pct", "void_damage_pct"], isMelee: true },
  "Dancing Strikes":        { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 2.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Blade Flurry":           { baseDamage: 100, levelScaling: 0.12, attackSpeed: 2.2, damageType: "Physical",  scalingStats: ["physical_damage_pct"], isMelee: true },
  "Synchronized Strike":    { baseDamage: 150, levelScaling: 0.13, attackSpeed: 0.8, damageType: "Physical",  scalingStats: ["physical_damage_pct", "void_damage_pct"], isMelee: true },
  "Multishot":              { baseDamage: 85,  levelScaling: 0.11, attackSpeed: 1.8, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Ballista":               { baseDamage: 70,  levelScaling: 0.10, attackSpeed: 2.0, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Rain of Arrows":         { baseDamage: 45,  levelScaling: 0.08, attackSpeed: 0.8, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Hail of Arrows":         { baseDamage: 60,  levelScaling: 0.09, attackSpeed: 1.0, damageType: "Physical",  scalingStats: ["physical_damage_pct", "cold_damage_pct"] },
  "Falcon Strikes":         { baseDamage: 90,  levelScaling: 0.11, attackSpeed: 2.0, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Net":                    { baseDamage: 40,  levelScaling: 0.08, attackSpeed: 0.5, damageType: "Physical",  scalingStats: ["physical_damage_pct"] },
  "Aerial Assault":         { baseDamage: 130, levelScaling: 0.13, attackSpeed: 0.6, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
  "Dive Bomb":              { baseDamage: 200, levelScaling: 0.15, attackSpeed: 0.4, damageType: "Physical",  scalingStats: ["minion_damage_pct", "physical_damage_pct"] },
};

// ---------------------------------------------------------------------------
// Full affix definitions — stat_key + tier ranges for simulation
// T1 = best tier in Last Epoch (highest value)
// ---------------------------------------------------------------------------

export interface AffixDefinition {
  name: string;
  type: "prefix" | "suffix";
  stat_key: string;   // matches BuildStats key in simulation.ts
  tiers: Record<string, [number, number]>;
  applicable: string[];
}

export const AFFIX_DEFINITIONS: AffixDefinition[] = [
  // --- Damage prefixes ---
  { name: "Spell Damage",         type: "prefix", stat_key: "spell_damage_pct",
    tiers: { T1: [39,55], T2: [26,38], T3: [16,25], T4: [8,15], T5: [1,7] },
    applicable: ["Wand","Staff","Helm","Chest"] },
  { name: "Necrotic Damage",      type: "prefix", stat_key: "necrotic_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Amulet"] },
  { name: "Fire Damage",          type: "prefix", stat_key: "fire_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Amulet"] },
  { name: "Cold Damage",          type: "prefix", stat_key: "cold_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Amulet"] },
  { name: "Lightning Damage",     type: "prefix", stat_key: "lightning_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Amulet"] },
  { name: "Physical Damage",      type: "prefix", stat_key: "physical_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Axe","Sword","Mace","Dagger","Bow","Amulet"] },
  { name: "Void Damage",          type: "prefix", stat_key: "void_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Amulet"] },
  { name: "Poison Damage",        type: "prefix", stat_key: "poison_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Dagger","Bow","Amulet"] },
  { name: "Minion Damage",        type: "prefix", stat_key: "minion_damage_pct",
    tiers: { T1: [70,90], T2: [50,69], T3: [35,49], T4: [20,34], T5: [10,19] },
    applicable: ["Wand","Staff","Helm","Amulet"] },
  // --- Speed prefixes ---
  { name: "Cast Speed",           type: "prefix", stat_key: "cast_speed",
    tiers: { T1: [20,25], T2: [15,19], T3: [10,14], T4: [6,9], T5: [3,5] },
    applicable: ["Wand","Staff","Sceptre"] },
  { name: "Attack Speed",         type: "prefix", stat_key: "attack_speed_pct",
    tiers: { T1: [20,25], T2: [15,19], T3: [10,14], T4: [6,9], T5: [3,5] },
    applicable: ["Axe","Sword","Dagger","Bow","Gloves"] },
  // --- Defense prefixes ---
  { name: "Health",               type: "prefix", stat_key: "max_health",
    tiers: { T1: [111,150], T2: [81,110], T3: [56,80], T4: [36,55], T5: [20,35] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet"] },
  { name: "Armour",               type: "prefix", stat_key: "armour",
    tiers: { T1: [300,420], T2: [200,299], T3: [130,199], T4: [80,129], T5: [40,79] },
    applicable: ["Helm","Chest","Gloves","Boots","Shield"] },
  { name: "Ward",                 type: "prefix", stat_key: "ward",
    tiers: { T1: [80,120], T2: [50,79], T3: [30,49], T4: [15,29], T5: [5,14] },
    applicable: ["Helm","Chest","Amulet","Ring"] },
  { name: "Endurance",            type: "prefix", stat_key: "max_health",
    tiers: { T1: [80,110], T2: [55,79], T3: [35,54], T4: [20,34], T5: [10,19] },
    applicable: ["Belt","Boots"] },
  // --- Resistance suffixes ---
  { name: "Fire Resistance",      type: "suffix", stat_key: "fire_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  { name: "Cold Resistance",      type: "suffix", stat_key: "cold_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  { name: "Lightning Resistance", type: "suffix", stat_key: "lightning_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  { name: "Void Resistance",      type: "suffix", stat_key: "void_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  { name: "Necrotic Resistance",  type: "suffix", stat_key: "necrotic_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  { name: "Poison Resistance",    type: "suffix", stat_key: "poison_res",
    tiers: { T1: [50,60], T2: [40,49], T3: [30,39], T4: [20,29], T5: [12,19] },
    applicable: ["Helm","Chest","Gloves","Boots","Belt","Ring","Amulet","Shield"] },
  // --- Defense suffixes ---
  { name: "Ward Retention",       type: "suffix", stat_key: "ward_retention_pct",
    tiers: { T1: [25,30], T2: [20,24], T3: [15,19], T4: [10,14], T5: [5,9] },
    applicable: ["Helm","Chest","Ring","Amulet"] },
  { name: "Dodge Rating",         type: "suffix", stat_key: "dodge_rating",
    tiers: { T1: [180,260], T2: [120,179], T3: [80,119], T4: [50,79], T5: [25,49] },
    applicable: ["Helm","Chest","Gloves","Boots"] },
  // --- Crit suffixes ---
  { name: "Critical Strike Chance",     type: "suffix", stat_key: "crit_chance_pct",
    tiers: { T1: [9,12], T2: [7,8], T3: [5,6], T4: [3,4], T5: [1,2] },
    applicable: ["Wand","Dagger","Sword","Axe","Ring","Amulet"] },
  { name: "Critical Strike Multiplier", type: "suffix", stat_key: "crit_multiplier_pct",
    tiers: { T1: [40,60], T2: [25,39], T3: [15,24], T4: [8,14], T5: [3,7] },
    applicable: ["Ring","Amulet","Gloves"] },
  // --- Attribute suffixes ---
  { name: "Strength",     type: "suffix", stat_key: "strength",
    tiers: { T1: [18,24], T2: [14,17], T3: [10,13], T4: [6,9], T5: [3,5] },
    applicable: ["Helm","Gloves","Ring","Amulet","Belt"] },
  { name: "Intelligence", type: "suffix", stat_key: "intelligence",
    tiers: { T1: [18,24], T2: [14,17], T3: [10,13], T4: [6,9], T5: [3,5] },
    applicable: ["Helm","Gloves","Ring","Amulet","Belt"] },
  { name: "Dexterity",    type: "suffix", stat_key: "dexterity",
    tiers: { T1: [18,24], T2: [14,17], T3: [10,13], T4: [6,9], T5: [3,5] },
    applicable: ["Helm","Gloves","Ring","Amulet","Belt"] },
  { name: "Vitality",     type: "suffix", stat_key: "vitality",
    tiers: { T1: [18,24], T2: [14,17], T3: [10,13], T4: [6,9], T5: [3,5] },
    applicable: ["Helm","Gloves","Ring","Amulet","Belt"] },
  { name: "Attunement",   type: "suffix", stat_key: "attunement",
    tiers: { T1: [18,24], T2: [14,17], T3: [10,13], T4: [6,9], T5: [3,5] },
    applicable: ["Helm","Gloves","Ring","Amulet","Belt"] },
  // --- Resource suffixes ---
  { name: "Mana",         type: "suffix", stat_key: "max_mana",
    tiers: { T1: [80,110], T2: [55,79], T3: [35,54], T4: [20,34], T5: [10,19] },
    applicable: ["Helm","Amulet","Ring","Belt"] },
  { name: "Mana Regen",   type: "suffix", stat_key: "mana_regen",
    tiers: { T1: [10,15], T2: [7,9], T3: [5,6], T4: [3,4], T5: [1,2] },
    applicable: ["Helm","Amulet","Ring","Belt"] },
  { name: "Health Regen", type: "suffix", stat_key: "health_regen",
    tiers: { T1: [15,25], T2: [10,14], T3: [6,9], T4: [3,5], T5: [1,2] },
    applicable: ["Helm","Chest","Belt","Amulet"] },
];

/** Returns the midpoint of a tier range for use in simulation. */
export function getAffixValue(affixName: string, tier: number): number {
  const tierKey = `T${tier}`;
  const def = AFFIX_DEFINITIONS.find((d) => d.name === affixName);
  if (!def || !def.tiers[tierKey]) return 0;
  const [lo, hi] = def.tiers[tierKey];
  return Math.round((lo + hi) / 2);
}

// Attribute scaling constants
export const ATTRIBUTE_SCALING = {
  strength:     { physical_damage_pct: 0.5, armour: 2 },
  intelligence: { spell_damage_pct: 0.5, max_mana: 10 },
  dexterity:    { attack_speed_pct: 0.3, dodge_rating: 3 },
  vitality:     { max_health: 10 },
  attunement:   { cast_speed: 0.3 },
};