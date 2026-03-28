"""
Passive Stat Resolver — reads PassiveNode rows from DB and accumulates
their stats into a flat additive dict + special_effects list.

The passive_nodes.stats column stores human-readable stat entries:
    [{"key": "Armor", "value": "+20"}, {"key": "Intelligence", "value": "+1"}]

This module parses those value strings, maps the key names to BuildStats
field names where possible, and sums everything up.

Stats that don't map to a known BuildStats field (niche mechanics, conditional
bonuses, etc.) are collected as special_effects — they can't be summed
numerically in a meaningful way.
"""

import re
from app.models import PassiveNode
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping: human-readable stat key → BuildStats field name
#
# Only common stats that map cleanly to BuildStats fields belong here.
# Everything else falls through to special_effects.
# ---------------------------------------------------------------------------

STAT_KEY_MAP: dict[str, str] = {
    # Attributes
    "Strength": "strength",
    "Intelligence": "intelligence",
    "Dexterity": "dexterity",
    "Vitality": "vitality",
    "Attunement": "attunement",
    "All Attributes": "_all_attributes",  # handled specially

    # Health / Mana
    "Health": "max_health",
    "Max Health": "max_health",
    "Increased Health": "health_pct",
    "Max Mana": "max_mana",
    "Mana": "max_mana",
    "Mana Regen": "mana_regen",
    "Mana Regeneration": "mana_regen",
    "Health Regen": "health_regen",
    "Health Regeneration": "health_regen",

    # Defense — armour / dodge / block
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

    # Defense — ward
    "Ward": "ward",
    "Ward Retention": "ward_retention_pct",
    "Ward Regen": "ward_regen",

    # Defense — resistances
    "Fire Resistance": "fire_res",
    "Cold Resistance": "cold_res",
    "Lightning Resistance": "lightning_res",
    "Void Resistance": "void_res",
    "Necrotic Resistance": "necrotic_res",
    "Poison Resistance": "poison_res",
    "Physical Resistance": "physical_res",
    "Elemental Resistance": "_elemental_res",  # handled specially

    # Offense — percentage damage
    "Increased Damage": "physical_damage_pct",  # generic damage → physical as default
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

    # Offense — speed / crit
    "Attack Speed": "attack_speed_pct",
    "Increased Attack Speed": "attack_speed_pct",
    "Cast Speed": "cast_speed",
    "Increased Cast Speed": "cast_speed",
    "Attack And Cast Speed": "_attack_and_cast_speed",  # handled specially
    "Critical Strike Chance": "crit_chance_pct",
    "Increased Critical Strike Chance": "crit_chance_pct",
    "Critical Strike Multiplier": "crit_multiplier_pct",
    "Increased Critical Strike Multiplier": "crit_multiplier_pct",

    # Offense — ailment chance
    "Poison Chance": "poison_chance_pct",
    "Bleed Chance": "bleed_chance_pct",
    "Ignite Chance": "ignite_chance_pct",
    "Shock Chance": "shock_chance_pct",
    "Chill Chance": "chill_chance_pct",

    # Offense — penetration
    "Physical Penetration": "physical_penetration",
    "Fire Penetration": "fire_penetration",
    "Cold Penetration": "cold_penetration",
    "Lightning Penetration": "lightning_penetration",
    "Void Penetration": "void_penetration",
    "Necrotic Penetration": "necrotic_penetration",

    # Offense — shred
    "Armour Shred Chance": "armour_shred_chance",
    "Fire Shred Chance": "fire_shred_chance",
    "Cold Shred Chance": "cold_shred_chance",
    "Lightning Shred Chance": "lightning_shred_chance",

    # Offense — minion
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

    # Sustain
    "Leech": "leech",
    "Health On Kill": "health_on_kill",
    "Mana On Kill": "mana_on_kill",
    "Ward On Kill": "ward_on_kill",
    "Health On Block": "health_on_block",
    "Healing Effectiveness": "healing_effectiveness_pct",

    # Utility
    "Movement Speed": "movement_speed",
    "Increased Movement Speed": "movement_speed",
    "Cooldown Recovery Speed": "cooldown_recovery_speed",
    "Increased Area": "area_pct",
}


# ---------------------------------------------------------------------------
# Value parser
# ---------------------------------------------------------------------------

_VALUE_RE = re.compile(r"^([+-]?)\s*(\d+(?:\.\d+)?)\s*(%?)$")


def _parse_value(raw: str) -> float | None:
    """
    Parse a stat value string into a float.

    Examples:
        "+20"   → 20.0
        "-50"   → -50.0
        "6%"    → 6.0
        "+5%"   → 5.0
        "+1"    → 1.0
        ""      → None  (empty / non-numeric → skip)
    """
    raw = raw.strip()
    if not raw:
        return None
    m = _VALUE_RE.match(raw)
    if not m:
        return None
    sign, digits, _pct = m.groups()
    value = float(digits)
    if sign == "-":
        value = -value
    return value


# ---------------------------------------------------------------------------
# Main resolver
# ---------------------------------------------------------------------------

def resolve_passive_stats(node_ids: list[str]) -> dict:
    """
    Load PassiveNode rows for the given IDs and accumulate their stats.

    Args:
        node_ids: list of namespaced node IDs, e.g. ["ac_0", "ac_1", "ac_5"]

    Returns:
        {
            "additive": {"armour": 40, "intelligence": 3, ...},
            "special_effects": [
                {"node_id": "ac_5", "node_name": "...", "key": "Summons A Revenant", "value": ""},
                ...
            ]
        }
    """
    if not node_ids:
        return {"additive": {}, "special_effects": []}

    # Batch-load all matching nodes
    nodes = PassiveNode.query.filter(PassiveNode.id.in_(node_ids)).all()
    found_ids = {n.id for n in nodes}

    # Log any IDs that weren't found (graceful skip)
    missing = set(node_ids) - found_ids
    if missing:
        log.warning("resolve_passive_stats: unknown node IDs skipped", ids=list(missing))

    additive: dict[str, float] = {}
    special_effects: list[dict] = []

    for node in nodes:
        for stat in (node.stats or []):
            key = stat.get("key", "")
            raw_value = str(stat.get("value", ""))

            mapped = STAT_KEY_MAP.get(key)
            parsed = _parse_value(raw_value)

            if mapped and parsed is not None:
                # Handle special composite mappings
                if mapped == "_all_attributes":
                    for attr in ("strength", "intelligence", "dexterity", "vitality", "attunement"):
                        additive[attr] = additive.get(attr, 0.0) + parsed
                elif mapped == "_elemental_res":
                    for res in ("fire_res", "cold_res", "lightning_res"):
                        additive[res] = additive.get(res, 0.0) + parsed
                elif mapped == "_attack_and_cast_speed":
                    additive["attack_speed_pct"] = additive.get("attack_speed_pct", 0.0) + parsed
                    additive["cast_speed"] = additive.get("cast_speed", 0.0) + parsed
                else:
                    additive[mapped] = additive.get(mapped, 0.0) + parsed
            else:
                # Unmapped or non-numeric → special effect
                special_effects.append({
                    "node_id": node.id,
                    "node_name": node.name,
                    "key": key,
                    "value": raw_value,
                })

    return {"additive": additive, "special_effects": special_effects}
