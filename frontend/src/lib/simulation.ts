/**
 * Build simulation engine — implements the formulas from engine_architecture.md
 *
 * DPS:
 *   HitDamage = BaseDamage * (1 + IncreasedDamage)
 *   AverageHit = (1 - CritChance) * HitDamage + CritChance * HitDamage * CritMultiplier
 *   DPS = AverageHit * AttackSpeed
 *
 * EHP:
 *   ArmorReduction = Armor / (Armor + 1000)
 *   ResistReduction = Resistance / 100  (capped at 75%)
 *   TotalReduction = 1 - (1 - ArmorReduction) * (1 - ResistReduction)
 *   EHP = Health / (1 - TotalReduction)
 */

import type { CharacterClass } from "@/types";
import {
  CLASS_BASE_STATS,
  AFFIX_DEFINITIONS,
  SKILL_STATS,
  ATTRIBUTE_SCALING,
  MASTERY_BONUSES,
  KEYSTONE_BONUSES,
  type PassiveNode,
  type GearItem,
} from "./gameData";

// ---------------------------------------------------------------------------
// Core stat accumulator
// ---------------------------------------------------------------------------

export interface BuildStats {
  // Offense
  base_damage: number;
  attack_speed: number;          // base attacks/s
  crit_chance: number;           // 0.0–1.0
  crit_multiplier: number;       // total multiplier, e.g. 2.0
  spell_damage_pct: number;      // additive % total
  physical_damage_pct: number;
  fire_damage_pct: number;
  cold_damage_pct: number;
  lightning_damage_pct: number;
  necrotic_damage_pct: number;
  void_damage_pct: number;
  poison_damage_pct: number;
  minion_damage_pct: number;
  attack_speed_pct: number;      // % bonus to attack_speed
  cast_speed: number;            // % bonus
  crit_chance_pct: number;       // % to add to crit_chance
  crit_multiplier_pct: number;   // % to add to crit_multiplier
  // Defense
  max_health: number;
  armour: number;
  dodge_rating: number;
  ward: number;
  ward_retention_pct: number;
  fire_res: number;
  cold_res: number;
  lightning_res: number;
  void_res: number;
  necrotic_res: number;
  poison_res: number;
  // Resources
  max_mana: number;
  mana_regen: number;
  health_regen: number;
  // Attributes
  strength: number;
  intelligence: number;
  dexterity: number;
  vitality: number;
  attunement: number;
}

function emptyStats(): BuildStats {
  return {
    base_damage: 0, attack_speed: 1.0, crit_chance: 0.05, crit_multiplier: 1.5,
    spell_damage_pct: 0, physical_damage_pct: 0, fire_damage_pct: 0,
    cold_damage_pct: 0, lightning_damage_pct: 0, necrotic_damage_pct: 0,
    void_damage_pct: 0, poison_damage_pct: 0, minion_damage_pct: 0,
    attack_speed_pct: 0, cast_speed: 0, crit_chance_pct: 0, crit_multiplier_pct: 0,
    max_health: 0, armour: 0, dodge_rating: 0, ward: 0, ward_retention_pct: 0,
    fire_res: 0, cold_res: 0, lightning_res: 0, void_res: 0, necrotic_res: 0, poison_res: 0,
    max_mana: 0, mana_regen: 0, health_regen: 0,
    strength: 0, intelligence: 0, dexterity: 0, vitality: 0, attunement: 0,
  };
}

// Stat keys that are additive % bonuses (accumulated as sums)
const PCT_BONUS_KEYS: Array<keyof BuildStats> = [
  "spell_damage_pct", "physical_damage_pct", "fire_damage_pct", "cold_damage_pct",
  "lightning_damage_pct", "necrotic_damage_pct", "void_damage_pct", "poison_damage_pct",
  "minion_damage_pct", "attack_speed_pct", "cast_speed", "crit_chance_pct",
  "crit_multiplier_pct", "ward_retention_pct",
];

// Stat keys that are flat additions
const FLAT_KEYS: Array<keyof BuildStats> = [
  "max_health", "armour", "dodge_rating", "ward", "max_mana", "mana_regen", "health_regen",
  "fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res", "poison_res",
  "strength", "intelligence", "dexterity", "vitality", "attunement",
];

function addPartial(stats: BuildStats, partial: Partial<Record<keyof BuildStats, number>>) {
  for (const key of [...PCT_BONUS_KEYS, ...FLAT_KEYS] as Array<keyof BuildStats>) {
    if (partial[key] !== undefined) {
      (stats[key] as number) += partial[key] as number;
    }
  }
}

// ---------------------------------------------------------------------------
// Passive node bonuses — deterministic from node id
// ---------------------------------------------------------------------------

// Cycle through these stats for core/notable nodes
const CORE_STAT_CYCLE: Array<[keyof BuildStats, number]> = [
  ["max_health", 8],
  ["spell_damage_pct", 1],
  ["physical_damage_pct", 1],
  ["armour", 10],
  ["fire_res", 2],
  ["cold_res", 2],
  ["lightning_res", 2],
  ["void_res", 2],
  ["necrotic_res", 2],
  ["cast_speed", 1],
];

const NOTABLE_MULTIPLIER = 3;

function getNodeBonus(node: PassiveNode): Partial<Record<keyof BuildStats, number>> {
  if (node.type === "mastery-gate") return {};

  if (node.type === "keystone") {
    return KEYSTONE_BONUSES[node.name] ?? { spell_damage_pct: 10, max_health: 50 };
  }

  const [statKey, baseAmount] = CORE_STAT_CYCLE[node.id % CORE_STAT_CYCLE.length];
  const amount = node.type === "notable" ? baseAmount * NOTABLE_MULTIPLIER : baseAmount;
  return { [statKey]: amount };
}

// ---------------------------------------------------------------------------
// Aggregate stats from all sources
// ---------------------------------------------------------------------------

export function aggregateStats(
  cls: CharacterClass,
  mastery: string,
  allocatedIds: number[],
  nodes: PassiveNode[],
  gear: GearItem[],
): BuildStats {
  const stats = emptyStats();
  const allocated = new Set(allocatedIds);

  // 1. Class base stats
  const base = CLASS_BASE_STATS[cls];
  stats.base_damage = base.base_damage;
  stats.attack_speed = base.attack_speed;
  stats.crit_chance = base.crit_chance;
  stats.crit_multiplier = base.crit_multiplier;
  stats.max_health = base.health;
  stats.max_mana = base.mana;
  stats.strength = base.strength;
  stats.intelligence = base.intelligence;
  stats.dexterity = base.dexterity;
  stats.vitality = base.vitality;
  stats.attunement = base.attunement;

  // 2. Mastery bonuses
  const masteryBonus = MASTERY_BONUSES[mastery];
  if (masteryBonus) addPartial(stats, masteryBonus as Partial<Record<keyof BuildStats, number>>);

  // Special mastery per-point bonuses (applied after node count is known)
  const ptsUsed = allocatedIds.length;
  if (mastery === "Lich") stats.ward += ptsUsed * 8;
  if (mastery === "Forge Guard") stats.armour += ptsUsed * 15;
  if (mastery === "Paladin") stats.max_health += 200; // already in MASTERY_BONUSES

  // 3. Passive node bonuses
  for (const node of nodes) {
    if (!allocated.has(node.id)) continue;
    addPartial(stats, getNodeBonus(node));
  }

  // 4. Gear affix values
  for (const item of gear) {
    for (const affix of item.affixes) {
      if (!affix.value || affix.value === 0) continue;
      const def = AFFIX_DEFINITIONS.find((d) => d.name === affix.name);
      if (!def) continue;
      addPartial(stats, { [def.stat_key]: affix.value } as Partial<Record<keyof BuildStats, number>>);
    }
  }

  // 5. Apply attribute scaling
  stats.spell_damage_pct   += stats.intelligence * ATTRIBUTE_SCALING.intelligence.spell_damage_pct;
  stats.max_mana           += stats.intelligence * ATTRIBUTE_SCALING.intelligence.max_mana;
  stats.physical_damage_pct += stats.strength   * ATTRIBUTE_SCALING.strength.physical_damage_pct;
  stats.armour             += stats.strength    * ATTRIBUTE_SCALING.strength.armour;
  stats.attack_speed_pct   += stats.dexterity   * ATTRIBUTE_SCALING.dexterity.attack_speed_pct;
  stats.dodge_rating       += stats.dexterity   * ATTRIBUTE_SCALING.dexterity.dodge_rating;
  stats.max_health         += stats.vitality    * ATTRIBUTE_SCALING.vitality.max_health;
  stats.cast_speed         += stats.attunement  * ATTRIBUTE_SCALING.attunement.cast_speed;

  // 6. Apply % bonuses to base values
  stats.crit_chance   = Math.min(0.95, stats.crit_chance + stats.crit_chance_pct / 100);
  stats.crit_multiplier += stats.crit_multiplier_pct / 100;
  stats.attack_speed  = stats.attack_speed * (1 + stats.attack_speed_pct / 100);

  return stats;
}

// ---------------------------------------------------------------------------
// DPS calculation
// ---------------------------------------------------------------------------

export interface DPSResult {
  hit_damage: number;
  average_hit: number;
  dps: number;
  effective_attack_speed: number;
  crit_contribution_pct: number;   // % of DPS from crits
}

export function calculateSkillDPS(
  skillName: string,
  level: number,
  stats: BuildStats,
): DPSResult {
  const skillDef = SKILL_STATS[skillName];
  if (!skillDef) {
    return { hit_damage: 0, average_hit: 0, dps: 0, effective_attack_speed: 1, crit_contribution_pct: 0 };
  }

  // Base damage scaled by level
  const scaledBase = skillDef.baseDamage * (1 + skillDef.levelScaling * (level - 1));

  // Gather all relevant % damage bonuses for this skill
  let totalDamagePct = 0;
  for (const scalingStat of skillDef.scalingStats) {
    totalDamagePct += (stats[scalingStat as keyof BuildStats] as number) ?? 0;
  }

  // HitDamage = BaseDamage * (1 + IncreasedDamage)
  const hitDamage = scaledBase * (1 + totalDamagePct / 100);

  // AverageHit = (1 - crit) * hit + crit * hit * critMult
  const nonCritDPS = (1 - stats.crit_chance) * hitDamage;
  const critDPS    = stats.crit_chance * hitDamage * stats.crit_multiplier;
  const averageHit = nonCritDPS + critDPS;

  // Effective attack speed — use skill's base AS, modified by stats
  const castSpeedBonus = skillDef.isSpell ? stats.cast_speed / 100 : 0;
  const attackSpeedBonus = !skillDef.isSpell ? stats.attack_speed_pct / 100 : 0;
  const effectiveAS = skillDef.attackSpeed * (1 + castSpeedBonus + attackSpeedBonus);

  const dps = averageHit * effectiveAS;
  const critContrib = dps > 0 ? (critDPS * effectiveAS) / dps * 100 : 0;

  return {
    hit_damage: Math.round(hitDamage),
    average_hit: Math.round(averageHit),
    dps: Math.round(dps),
    effective_attack_speed: Math.round(effectiveAS * 100) / 100,
    crit_contribution_pct: Math.round(critContrib),
  };
}

// ---------------------------------------------------------------------------
// Defense / EHP calculation
// ---------------------------------------------------------------------------

export interface DefenseResult {
  max_health: number;
  effective_hp: number;
  armor_reduction_pct: number;
  avg_resistance: number;
  fire_res: number;
  cold_res: number;
  lightning_res: number;
  void_res: number;
  necrotic_res: number;
  survivability_score: number;   // 0–100 composite
  weaknesses: string[];
  strengths: string[];
}

const RES_CAP = 75;

export function calculateDefense(stats: BuildStats): DefenseResult {
  // ArmorReduction = Armor / (Armor + 1000)
  const armorReduction = stats.armour / (stats.armour + 1000);

  // Cap resistances at 75%
  const fireRes   = Math.min(RES_CAP, stats.fire_res);
  const coldRes   = Math.min(RES_CAP, stats.cold_res);
  const lightRes  = Math.min(RES_CAP, stats.lightning_res);
  const voidRes   = Math.min(RES_CAP, stats.void_res);
  const necroRes  = Math.min(RES_CAP, stats.necrotic_res);

  const avgRes = (fireRes + coldRes + lightRes + voidRes + necroRes) / 5;

  // TotalReduction = 1 - (1 - ArmorReduction) * (1 - ResistReduction)
  const avgResDecimal = avgRes / 100;
  const totalReduction = 1 - (1 - armorReduction) * (1 - avgResDecimal);

  // EHP = Health / (1 - TotalReduction)
  const denom = Math.max(0.01, 1 - totalReduction);
  const effectiveHP = Math.round(stats.max_health / denom);

  // Survivability score: weighted composite
  const healthScore   = Math.min(100, stats.max_health / 30);     // 3000 hp = 100
  const resistScore   = avgRes / RES_CAP * 100;                    // 75% avg = 100
  const armorScore    = Math.min(100, armorReduction * 200);       // 50% reduction = 100
  const score = Math.round(healthScore * 0.4 + resistScore * 0.4 + armorScore * 0.2);

  const weaknesses: string[] = [];
  const strengths: string[] = [];
  if (stats.fire_res < 40)   weaknesses.push(`Fire res ${stats.fire_res}% (uncapped)`);
  if (stats.cold_res < 40)   weaknesses.push(`Cold res ${stats.cold_res}% (uncapped)`);
  if (stats.lightning_res < 40) weaknesses.push(`Lightning res ${stats.lightning_res}% (uncapped)`);
  if (stats.void_res < 40)   weaknesses.push(`Void res ${stats.void_res}% (uncapped)`);
  if (stats.necrotic_res < 40) weaknesses.push(`Necrotic res ${stats.necrotic_res}% (uncapped)`);
  if (stats.armour < 500)    weaknesses.push("Low armour — vulnerable to physical hits");
  if (stats.max_health < 1500) weaknesses.push("Low health pool");
  if (stats.fire_res >= 70)  strengths.push("Fire capped");
  if (stats.cold_res >= 70)  strengths.push("Cold capped");
  if (stats.lightning_res >= 70) strengths.push("Lightning capped");
  if (armorReduction > 0.4)  strengths.push("Strong armour mitigation");
  if (stats.max_health > 2500) strengths.push("Large health pool");
  if (stats.ward > 200)      strengths.push("Ward absorption layer");

  return {
    max_health: Math.round(stats.max_health),
    effective_hp: effectiveHP,
    armor_reduction_pct: Math.round(armorReduction * 100),
    avg_resistance: Math.round(avgRes),
    fire_res: Math.round(fireRes),
    cold_res: Math.round(coldRes),
    lightning_res: Math.round(lightRes),
    void_res: Math.round(voidRes),
    necrotic_res: Math.round(necroRes),
    survivability_score: Math.min(100, score),
    weaknesses,
    strengths,
  };
}

// ---------------------------------------------------------------------------
// Stat optimizer — which stat gives the best DPS gain?
// ---------------------------------------------------------------------------

export interface StatUpgrade {
  stat: string;
  label: string;
  dps_gain_pct: number;
  ehp_gain_pct: number;
}

const STAT_TEST_INCREMENTS: Array<{ key: keyof BuildStats; label: string; delta: number }> = [
  { key: "crit_multiplier_pct", label: "+40% Crit Multiplier",    delta: 40 },
  { key: "crit_chance_pct",     label: "+7% Crit Chance",         delta: 7  },
  { key: "attack_speed_pct",    label: "+10% Attack Speed",       delta: 10 },
  { key: "spell_damage_pct",    label: "+40% Spell Damage",       delta: 40 },
  { key: "physical_damage_pct", label: "+40% Physical Damage",    delta: 40 },
  { key: "fire_damage_pct",     label: "+40% Fire Damage",        delta: 40 },
  { key: "cold_damage_pct",     label: "+40% Cold Damage",        delta: 40 },
  { key: "lightning_damage_pct",label: "+40% Lightning Damage",   delta: 40 },
  { key: "necrotic_damage_pct", label: "+40% Necrotic Damage",    delta: 40 },
  { key: "cast_speed",          label: "+10% Cast Speed",         delta: 10 },
  { key: "max_health",          label: "+300 Health",             delta: 300 },
  { key: "armour",              label: "+200 Armour",             delta: 200 },
  { key: "fire_res",            label: "+20% Fire Resistance",    delta: 20  },
  { key: "cold_res",            label: "+20% Cold Resistance",    delta: 20  },
  { key: "lightning_res",       label: "+20% Lightning Resistance", delta: 20 },
  { key: "void_res",            label: "+20% Void Resistance",    delta: 20  },
];

export function getStatUpgrades(
  stats: BuildStats,
  primarySkillName: string,
  primarySkillLevel: number,
  topN = 5,
): StatUpgrade[] {
  const baseDPS = calculateSkillDPS(primarySkillName, primarySkillLevel, stats).dps;
  const baseEHP = calculateDefense(stats).effective_hp;

  const results: StatUpgrade[] = [];

  for (const { key, label, delta } of STAT_TEST_INCREMENTS) {
    const modified = { ...stats, [key]: (stats[key] as number) + delta };

    // Re-apply derived stats
    modified.crit_chance   = Math.min(0.95, stats.crit_chance - stats.crit_chance_pct / 100 + modified.crit_chance_pct / 100);
    modified.crit_multiplier = stats.crit_multiplier - stats.crit_multiplier_pct / 100 + modified.crit_multiplier_pct / 100;

    const newDPS = calculateSkillDPS(primarySkillName, primarySkillLevel, modified).dps;
    const newEHP = calculateDefense(modified).effective_hp;

    const dpsGain = baseDPS > 0 ? ((newDPS - baseDPS) / baseDPS) * 100 : 0;
    const ehpGain = baseEHP > 0 ? ((newEHP - baseEHP) / baseEHP) * 100 : 0;

    results.push({
      stat: String(key),
      label,
      dps_gain_pct: Math.round(dpsGain * 10) / 10,
      ehp_gain_pct: Math.round(ehpGain * 10) / 10,
    });
  }

  // Sort by DPS gain descending
  return results.sort((a, b) => b.dps_gain_pct - a.dps_gain_pct).slice(0, topN);
}
