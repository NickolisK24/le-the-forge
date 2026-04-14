/**
 * Human-readable labels for every raw stat key surfaced by the simulation
 * engine. All user-facing stat text on the simulation page should route
 * through `statLabel()` so that snake_case keys never leak into the UI.
 */

export const STAT_LABELS: Record<string, string> = {
  // Offense
  dps: "Total DPS",
  total_dps: "Total DPS",
  hit_dps: "Hit DPS",
  ailment_dps: "Ailment DPS",
  average_hit: "Average Hit",
  hit_damage: "Hit Damage",
  effective_attack_speed: "Attacks Per Second",
  crit_chance: "Critical Strike Chance",
  crit_multiplier: "Critical Strike Multiplier",
  crit_contribution_pct: "Crit Contribution to DPS",
  flat_damage_added: "Flat Added Damage",
  bleed_dps: "Bleed DPS",
  ignite_dps: "Ignite DPS",
  poison_dps: "Poison DPS",
  // Defense
  max_health: "Maximum Health",
  effective_hp: "Effective Health Pool",
  total_ehp: "Total Effective HP (with Ward)",
  ward_buffer: "Ward Buffer",
  armour: "Armor",
  armor_reduction_pct: "Armor Damage Reduction",
  avg_resistance: "Average Resistance",
  fire_res: "Fire Resistance",
  cold_res: "Cold Resistance",
  lightning_res: "Lightning Resistance",
  void_res: "Void Resistance",
  necrotic_res: "Necrotic Resistance",
  physical_res: "Physical Resistance",
  poison_res: "Poison Resistance",
  dodge_chance_pct: "Dodge Chance",
  block_chance: "Block Chance",
  endurance: "Endurance",
  endurance_threshold: "Endurance Threshold",
  survivability_score: "Survivability Rating",
  // Upgrades
  dps_gain_pct: "DPS Improvement",
  ehp_gain_pct: "Survivability Improvement",
  fp_cost: "Forge Potential Cost",
};

export function statLabel(key: string): string {
  return (
    STAT_LABELS[key] ??
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}
