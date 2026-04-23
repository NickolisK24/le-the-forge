/**
 * Human-readable labels for every raw stat key surfaced by the simulation
 * engine. All user-facing stat text on the simulation page should route
 * through `statLabel()` so that snake_case keys never leak into the UI.
 *
 * The mapping is exhaustive for every field the analysis response currently
 * returns (see `BuildSimulationResult`, `DPSResult`, `DefenseResult`,
 * `StatUpgrade` in `frontend/src/lib/api.ts`). When a new stat is added to
 * the engine, add the mapping here before exposing the stat in a panel.
 *
 * The covered-keys export + the exhaustive test in
 * `__tests__/constants/stat-labels.test.ts` enforce that contract.
 */

export const STAT_LABELS: Record<string, string> = {
  // ---------------------------------------------------------------------
  // Offense — DPSResult.
  //
  // Labels here are shortened where necessary so they fit in the narrow
  // offense/defense card on the pinned-320-px analysis rail at lg without
  // truncating to "Total D...", "Critic...", etc. The phase-3 prompt's
  // exact label strings (e.g. "Critical Strike Chance") are documented in
  // docs/unified-planner-phase3-notes.md §2; the shortened form is the
  // one rendered.
  // ---------------------------------------------------------------------
  dps:                      "Total DPS",
  total_dps:                "Total DPS",
  hit_dps:                  "Hit DPS",
  ailment_dps:              "Ailment DPS",
  bleed_dps:                "Bleed DPS",
  ignite_dps:               "Ignite DPS",
  poison_dps:               "Poison DPS",
  average_hit:              "Average Hit",
  hit_damage:               "Hit Damage",
  effective_attack_speed:   "Attacks Per Second",
  crit_chance:              "Crit Chance",
  crit_multiplier:          "Crit Multiplier",
  crit_contribution_pct:    "Crit Contribution to DPS",
  flat_damage_added:        "Flat Added Damage",

  // ---------------------------------------------------------------------
  // Defense — DefenseResult
  // ---------------------------------------------------------------------
  max_health:               "Max Health",
  effective_hp:             "Effective Health Pool",
  total_ehp:                "Total Effective HP",
  ward_buffer:              "Ward Buffer",
  ward_regen_per_second:    "Ward Regen / Sec",
  ward_decay_per_second:    "Ward Decay / Sec",
  net_ward_per_second:      "Net Ward / Sec",
  armour:                   "Armor",
  armor_reduction_pct:      "Armor Damage Reduction",
  // Kept for forward compatibility: engine tuning discussions in
  // docs/unified-planner-phase3-notes.md propose "armor_mitigation_pct" as
  // a clearer name. Both keys resolve to the same label so we do not need
  // a migration when the engine renames the field.
  armor_mitigation_pct:     "Armor Damage Reduction",
  avg_resistance:           "Avg Elemental Res",
  fire_res:                 "Fire Resistance",
  cold_res:                 "Cold Resistance",
  lightning_res:            "Lightning Resistance",
  void_res:                 "Void Resistance",
  necrotic_res:             "Necrotic Resistance",
  physical_res:             "Physical Resistance",
  poison_res:               "Poison Resistance",
  dodge_chance_pct:         "Dodge Chance",
  block_chance:             "Block Chance",
  block_chance_pct:         "Block Chance",
  block_mitigation_pct:     "Block Mitigation",
  endurance:                "Endurance",
  endurance_pct:            "Endurance",
  endurance_threshold:      "Endurance Threshold",
  endurance_threshold_pct:  "Endurance Threshold",
  crit_avoidance_pct:       "Critical Strike Avoidance",
  glancing_blow_pct:        "Glancing Blow Chance",
  stun_avoidance_pct:       "Stun Avoidance",
  survivability_score:      "Survivability Rating",
  sustain_score:            "Sustain Rating",
  leech_pct:                "Leech",
  health_on_kill:           "Health On Kill",
  mana_on_kill:             "Mana On Kill",
  ward_on_kill:             "Ward On Kill",
  health_regen:             "Health Regen / Sec",
  mana_regen:               "Mana Regen / Sec",

  // ---------------------------------------------------------------------
  // Upgrades — StatUpgrade
  // ---------------------------------------------------------------------
  dps_gain_pct:             "DPS Improvement",
  ehp_gain_pct:             "Survivability Improvement",
  fp_cost:                  "Forge Potential Cost",
};

/**
 * Every analysis-response field that must have a label before it reaches
 * the UI. Consumed by the exhaustiveness test — not by runtime code.
 * Keep in sync with the TypeScript response interfaces.
 */
export const COVERED_STAT_KEYS: readonly string[] = [
  // DPSResult
  "hit_damage", "average_hit", "dps", "effective_attack_speed",
  "crit_contribution_pct", "flat_damage_added",
  "bleed_dps", "ignite_dps", "poison_dps", "ailment_dps", "total_dps",
  // DefenseResult
  "max_health", "effective_hp", "armor_reduction_pct", "avg_resistance",
  "fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res",
  "physical_res", "poison_res",
  "dodge_chance_pct", "block_chance_pct", "block_mitigation_pct",
  "endurance_pct", "endurance_threshold_pct",
  "crit_avoidance_pct", "glancing_blow_pct", "stun_avoidance_pct",
  "ward_buffer", "total_ehp",
  "ward_regen_per_second", "ward_decay_per_second", "net_ward_per_second",
  "leech_pct", "health_on_kill", "mana_on_kill", "ward_on_kill",
  "health_regen", "mana_regen",
  "survivability_score", "sustain_score",
  // StatUpgrade
  "dps_gain_pct", "ehp_gain_pct", "fp_cost",
] as const;

export function statLabel(key: string): string {
  return (
    STAT_LABELS[key] ??
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}
