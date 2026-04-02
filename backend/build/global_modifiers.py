"""
Global Modifier Routing (Step 91).

Routes global stat modifiers into the correct combat layer category.

Each stat belongs to exactly one layer category. The routing table maps
stat_key patterns to a ModifierLayer. The build assembly layer uses this
to know which engine subsystem should consume a given modifier.

  ModifierLayer    — enum of combat layer categories
  ROUTING_TABLE    — dict[str, ModifierLayer] mapping stat_key -> layer
  route_modifier   — classify a single stat_key
  route_stat_pool  — classify an entire stat pool, return grouped dict

Layer categories:
  DAMAGE_INCREASED  — additive % damage bonuses (e.g. fire_damage_pct)
  DAMAGE_MORE       — multiplicative 'more' damage (e.g. more_damage_pct)
  CRIT              — crit chance and multiplier modifiers
  SPEED             — cast/attack/movement speed
  DEFENSE           — armor, resistance, dodge, block, health, shield
  RESOURCE          — mana/health regen and pool size
  AILMENT           — ailment damage, duration, chance
  UTILITY           — everything else (unrouted stats)
"""

from __future__ import annotations

import enum


class ModifierLayer(enum.Enum):
    DAMAGE_INCREASED = "damage_increased"
    DAMAGE_MORE      = "damage_more"
    CRIT             = "crit"
    SPEED            = "speed"
    DEFENSE          = "defense"
    RESOURCE         = "resource"
    AILMENT          = "ailment"
    UTILITY          = "utility"


# ---------------------------------------------------------------------------
# Routing table — exact stat_key matches take priority over prefix rules
# ---------------------------------------------------------------------------

_EXACT: dict[str, ModifierLayer] = {
    # More damage
    "more_damage_pct":                ModifierLayer.DAMAGE_MORE,
    # Crit
    "crit_chance_pct":                ModifierLayer.CRIT,
    "crit_multiplier_pct":            ModifierLayer.CRIT,
    "crit_chance_bonus_pct":          ModifierLayer.CRIT,
    "increased_crit_multiplier_pct":  ModifierLayer.CRIT,
    # Speed
    "cast_speed_pct":                 ModifierLayer.SPEED,
    "attack_speed_pct":               ModifierLayer.SPEED,
    "movement_speed_pct":             ModifierLayer.SPEED,
    # Defense — resistance
    "fire_resistance_pct":            ModifierLayer.DEFENSE,
    "cold_resistance_pct":            ModifierLayer.DEFENSE,
    "lightning_resistance_pct":       ModifierLayer.DEFENSE,
    "void_resistance_pct":            ModifierLayer.DEFENSE,
    "physical_resistance_pct":        ModifierLayer.DEFENSE,
    "necrotic_resistance_pct":        ModifierLayer.DEFENSE,
    "poison_resistance_pct":          ModifierLayer.DEFENSE,
    "all_resistance_pct":             ModifierLayer.DEFENSE,
    # Defense — other
    "armor_flat":                     ModifierLayer.DEFENSE,
    "armor_pct":                      ModifierLayer.DEFENSE,
    "dodge_rating":                   ModifierLayer.DEFENSE,
    "block_chance_pct":               ModifierLayer.DEFENSE,
    "block_effectiveness_pct":        ModifierLayer.DEFENSE,
    "max_health_flat":                ModifierLayer.DEFENSE,
    "max_health_pct":                 ModifierLayer.DEFENSE,
    "max_ward_flat":                  ModifierLayer.DEFENSE,
    # Resource
    "max_mana_flat":                  ModifierLayer.RESOURCE,
    "max_mana_pct":                   ModifierLayer.RESOURCE,
    "mana_regen_flat":                ModifierLayer.RESOURCE,
    "mana_regen_pct":                 ModifierLayer.RESOURCE,
    "health_regen_flat":              ModifierLayer.RESOURCE,
    "health_regen_pct":               ModifierLayer.RESOURCE,
    "leech_pct":                      ModifierLayer.RESOURCE,
    # Ailment
    "ailment_damage_pct":             ModifierLayer.AILMENT,
    "ailment_duration_pct":           ModifierLayer.AILMENT,
    "bleed_damage_pct":               ModifierLayer.AILMENT,
    "bleed_duration_pct":             ModifierLayer.AILMENT,
    "ignite_damage_pct":              ModifierLayer.AILMENT,
    "ignite_duration_pct":            ModifierLayer.AILMENT,
    "poison_damage_pct":              ModifierLayer.AILMENT,
    "poison_dot_damage_pct":          ModifierLayer.AILMENT,
    "frostbite_damage_pct":           ModifierLayer.AILMENT,
    "chill_effect_pct":               ModifierLayer.AILMENT,
}

# Suffix-based fallback rules (applied when no exact match found)
_SUFFIX_RULES: list[tuple[str, ModifierLayer]] = [
    ("_damage_pct", ModifierLayer.DAMAGE_INCREASED),
    ("_resistance_pct", ModifierLayer.DEFENSE),
    ("_regen_flat", ModifierLayer.RESOURCE),
    ("_regen_pct", ModifierLayer.RESOURCE),
    ("_duration_pct", ModifierLayer.AILMENT),
    ("_speed_pct", ModifierLayer.SPEED),
]


def route_modifier(stat_key: str) -> ModifierLayer:
    """
    Return the ModifierLayer for a given stat_key.

    Exact matches take priority. Falls back to suffix rules.
    Returns ModifierLayer.UTILITY for unknown keys.
    """
    if stat_key in _EXACT:
        return _EXACT[stat_key]
    for suffix, layer in _SUFFIX_RULES:
        if stat_key.endswith(suffix):
            return layer
    return ModifierLayer.UTILITY


def route_stat_pool(
    stat_pool: dict[str, float],
) -> dict[ModifierLayer, dict[str, float]]:
    """
    Classify every entry in *stat_pool* by its ModifierLayer.

    Returns a dict keyed by ModifierLayer. Each value is a sub-dict of
    {stat_key: value} for all stats assigned to that layer.

    Layers with no matching stats are omitted from the output.
    """
    result: dict[ModifierLayer, dict[str, float]] = {}
    for key, value in stat_pool.items():
        layer = route_modifier(key)
        if layer not in result:
            result[layer] = {}
        result[layer][key] = value
    return result
