// MIRRORS: backend/app/services/passive_stat_resolver.py STAT_KEY_MAP
//
// Human-readable passive-node stat keys → BuildStats field names.
// Every entry in this map must exactly match the backend mapping so the
// frontend passive-tree stat pipeline aggregates into the same field names
// the backend resolver uses.
//
// Composite keys that begin with an underscore ("_all_attributes",
// "_elemental_res", "_attack_and_cast_speed") are handled specially in
// extractNodeEffects() — they fan out to multiple BuildStats fields.

export const PASSIVE_STAT_KEY_MAP: Record<string, string> = {
  // Attributes
  "Strength": "strength",
  "Intelligence": "intelligence",
  "Dexterity": "dexterity",
  "Vitality": "vitality",
  "Attunement": "attunement",
  "All Attributes": "_all_attributes",

  // Health / Mana
  "Health": "max_health",
  "Max Health": "max_health",
  "Increased Health": "health_pct",
  "Max Mana": "max_mana",
  "Mana": "max_mana",
  "Mana Regen": "mana_regen",
  "Mana Regeneration": "mana_regen",
  "Health Regen": "health_regen",
  "Health Regeneration": "health_regen",

  // Defense — armour / dodge / block
  "Armor": "armour",
  "Armour": "armour",
  "Dodge Rating": "dodge_rating",
  "Block Chance": "block_chance",
  "Block Effectiveness": "block_effectiveness",
  "Endurance": "endurance",
  "Endurance Threshold": "endurance_threshold",
  "Stun Avoidance": "stun_avoidance",
  "Critical Strike Avoidance": "crit_avoidance",
  "Glancing Blow": "glancing_blow",

  // Defense — ward
  "Ward": "ward",
  "Ward Retention": "ward_retention_pct",
  "Ward Regen": "ward_regen",

  // Defense — resistances
  "Fire Resistance": "fire_res",
  "Cold Resistance": "cold_res",
  "Lightning Resistance": "lightning_res",
  "Void Resistance": "void_res",
  "Necrotic Resistance": "necrotic_res",
  "Poison Resistance": "poison_res",
  "Physical Resistance": "physical_res",
  "Elemental Resistance": "_elemental_res",

  // Offense — percentage damage
  "Increased Damage": "physical_damage_pct",
  "Increased Spell Damage": "spell_damage_pct",
  "Spell Damage": "spell_damage_pct",
  "Increased Physical Damage": "physical_damage_pct",
  "Increased Fire Damage": "fire_damage_pct",
  "Increased Cold Damage": "cold_damage_pct",
  "Increased Lightning Damage": "lightning_damage_pct",
  "Increased Necrotic Damage": "necrotic_damage_pct",
  "Increased Void Damage": "void_damage_pct",
  "Increased Poison Damage": "poison_damage_pct",
  "Increased Elemental Damage": "elemental_damage_pct",
  "Increased Melee Damage": "melee_damage_pct",
  "Increased Throwing Damage": "throwing_damage_pct",
  "Increased Bow Damage": "bow_damage_pct",
  "Increased Minion Damage": "minion_damage_pct",
  "Increased DoT Damage": "dot_damage_pct",
  "Increased Damage Over Time": "dot_damage_pct",

  // Offense — speed / crit
  "Attack Speed": "attack_speed_pct",
  "Increased Attack Speed": "attack_speed_pct",
  "Cast Speed": "cast_speed",
  "Increased Cast Speed": "cast_speed",
  "Attack And Cast Speed": "_attack_and_cast_speed",
  "Critical Strike Chance": "crit_chance_pct",
  "Increased Critical Strike Chance": "crit_chance_pct",
  "Critical Strike Multiplier": "crit_multiplier_pct",
  "Increased Critical Strike Multiplier": "crit_multiplier_pct",

  // Offense — ailment chance
  "Poison Chance": "poison_chance_pct",
  "Bleed Chance": "bleed_chance_pct",
  "Ignite Chance": "ignite_chance_pct",
  "Shock Chance": "shock_chance_pct",
  "Chill Chance": "chill_chance_pct",

  // Offense — penetration
  "Physical Penetration": "physical_penetration",
  "Fire Penetration": "fire_penetration",
  "Cold Penetration": "cold_penetration",
  "Lightning Penetration": "lightning_penetration",
  "Void Penetration": "void_penetration",
  "Necrotic Penetration": "necrotic_penetration",

  // Offense — shred
  "Armour Shred Chance": "armour_shred_chance",
  "Fire Shred Chance": "fire_shred_chance",
  "Cold Shred Chance": "cold_shred_chance",
  "Lightning Shred Chance": "lightning_shred_chance",

  // Offense — minion
  "Increased Minion Health": "minion_health_pct",
  "Minion Health": "minion_health_pct",
  "Increased Minion Speed": "minion_speed_pct",
  "Increased Minion Physical Damage": "minion_physical_damage_pct",
  "Increased Minion Spell Damage": "minion_spell_damage_pct",
  "Increased Minion Melee Damage": "minion_melee_damage_pct",
  "Companion Damage": "companion_damage_pct",
  "Companion Health": "companion_health_pct",
  "Totem Damage": "totem_damage_pct",
  "Totem Health": "totem_health_pct",

  // Sustain
  "Leech": "leech",
  "Health On Kill": "health_on_kill",
  "Mana On Kill": "mana_on_kill",
  "Ward On Kill": "ward_on_kill",
  "Health On Block": "health_on_block",
  "Healing Effectiveness": "healing_effectiveness_pct",

  // Utility
  "Movement Speed": "movement_speed",
  "Increased Movement Speed": "movement_speed",
  "Cooldown Recovery Speed": "cooldown_recovery_speed",
  "Increased Area": "area_pct",
};

// Composite fan-outs — when a key maps to one of these sentinel values,
// extractNodeEffects() emits one modifier per target field.
export const ALL_ATTRIBUTE_FIELDS = [
  "strength",
  "intelligence",
  "dexterity",
  "vitality",
  "attunement",
] as const;

export const ELEMENTAL_RES_FIELDS = [
  "fire_res",
  "cold_res",
  "lightning_res",
] as const;

export const ATTACK_AND_CAST_SPEED_FIELDS = [
  "attack_speed_pct",
  "cast_speed",
] as const;
