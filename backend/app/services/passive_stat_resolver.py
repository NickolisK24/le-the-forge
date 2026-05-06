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
from app.domain.passive import PassiveStats, SpecialEffect
from app.models import PassiveNode
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping: human-readable stat key → BuildStats field name
#
# Coverage (measured against data/classes/passives.json by
# scripts/verify_passive_coverage.py):
#   • Overall entries mapped: 39.2% (555 / 1416) — pass 1 was 31.8%.
#   • freq≥2 keys mapped:     79.8% (485 / 608) — pass 1 was 69.7%.
# The remaining unmapped entries are either conditional mechanics
# ("while Dual Wielding", "per Stack of Perfection", "with a Shield"),
# proc triggers ("Chance To Cast X"), shared-with-minions composites,
# or non-numeric flag effects ("Can Equip Swords in Offhand"). They
# fall through to special_effects so callers can inspect them without
# the resolver silently over- or under-scaling the additive pool.
#
# Pass 2 additions prioritised meta-build DPS/EHP stats:
#   - High-frequency universals: Increased Mana Regen (freq 12),
#     Increased Dodge Rating (6), Increased Health Regen (6),
#     Increased Mana (4), Increased Leech Rate (3) — all backed by
#     new BuildStats fields so they stop polluting special_effects.
#   - Minion specialisation stats relevant to Acolyte/Necromancer
#     and Primalist Beastmaster builds: cold/necrotic damage,
#     attack/cast speed, armour, crit multiplier.
#   - Frequent aliases where the key was a simple case/plural
#     variation of an already-mapped concept (Bow Damage, Ward per
#     second, Elemental Resistances, Melee Damage, etc.).
#   - Type-scoped ailment/crit chance aliases (Melee Bleed Chance,
#     Melee Crit Chance, Spell Poison Chance, etc.) route to the
#     generic chance pool; BuildStats doesn't distinguish hit-source
#     for ailment chances so conflating them matches the existing
#     "Increased Melee Attack Speed" → attack_speed_pct pattern.
#
# Special composite keys (prefixed with underscore) fan out to multiple
# BuildStats fields inside resolve_passive_stats().
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
    "Increased Mana": "mana_pct",               # pass 2: freq 4 — pct of max mana
    "Mana Regen": "mana_regen",
    "Mana Regeneration": "mana_regen",
    "Increased Mana Regen": "mana_regen_pct",   # pass 2: freq 12 — highest unmapped
    "Increased Mana Regeneration": "mana_regen_pct",
    "Health Regen": "health_regen",
    "Health Regeneration": "health_regen",
    "Increased Health Regen": "health_regen_pct",        # pass 2: freq 6
    "Increased Health Regeneration": "health_regen_pct",

    # Defense — armour / dodge / block
    "Armor": "armour",
    "Armour": "armour",
    "Increased Armor": "armour_pct",
    "Increased Armour": "armour_pct",
    "Dodge Rating": "dodge_rating",
    "Increased Dodge Rating": "dodge_rating_pct",   # pass 2: freq 6 — meta Rogue/Falconer
    "Block Chance": "block_chance",
    "Block Effectiveness": "block_effectiveness",
    "Endurance": "endurance",
    "Endurance Threshold": "endurance_threshold",
    "Stun Avoidance": "stun_avoidance",
    "Critical Strike Avoidance": "crit_avoidance",
    "Crit Avoidance": "crit_avoidance",
    "Critical Avoidance": "crit_avoidance",
    "Glancing Blow": "glancing_blow",
    "Glancing Blow Chance": "glancing_blow",

    # Defense — ward
    "Ward": "ward",
    "Ward Retention": "ward_retention_pct",
    "Increased Ward Retention": "ward_retention_pct",
    "Ward Regen": "ward_regen",
    "Ward Per Second": "ward_regen",
    "Ward per Second": "ward_regen",            # pass 2: case alias
    "Ward per second": "ward_regen",            # pass 2: case alias
    "Ward Regeneration": "ward_regen",
    "Ward Decay Threshold": "ward_decay_threshold",  # pass 2: freq 2 — flat threshold

    # Defense — resistances
    "Fire Resistance": "fire_res",
    "Cold Resistance": "cold_res",
    "Lightning Resistance": "lightning_res",
    "Void Resistance": "void_res",
    "Necrotic Resistance": "necrotic_res",
    "Poison Resistance": "poison_res",
    "Physical Resistance": "physical_res",
    "Elemental Resistance": "_elemental_res",   # handled specially
    "Elemental Resistances": "_elemental_res",  # pass 2: plural alias
    "All Resistances": "_all_resistances",      # handled specially

    # Offense — percentage damage
    "Increased Damage": "physical_damage_pct",  # generic damage → physical as default
    "Increased Spell Damage": "spell_damage_pct",
    "Spell Damage": "spell_damage_pct",
    "Increased Physical Damage": "physical_damage_pct",
    "Physical Damage": "physical_damage_pct",        # pass 2: alias (base-tree node)
    "Increased Fire Damage": "fire_damage_pct",
    "Fire Damage": "fire_damage_pct",                # pass 2: alias
    "Increased Cold Damage": "cold_damage_pct",
    "Cold Damage": "cold_damage_pct",                # pass 2: alias
    "Increased Lightning Damage": "lightning_damage_pct",
    "Global Increased Lightning Damage": "lightning_damage_pct",  # pass 2: alias
    "Increased Necrotic Damage": "necrotic_damage_pct",
    "Necrotic Damage": "necrotic_damage_pct",        # pass 2: alias
    "Increased Void Damage": "void_damage_pct",
    "Void Damage": "void_damage_pct",                # pass 2: alias
    "Increased Poison Damage": "poison_damage_pct",
    "Increased Elemental Damage": "elemental_damage_pct",
    "Elemental Damage": "elemental_damage_pct",      # pass 2: alias
    "Increased Melee Damage": "melee_damage_pct",
    "Melee Damage": "melee_damage_pct",              # pass 2: alias
    "Increased Throwing Damage": "throwing_damage_pct",
    "Throwing Damage": "throwing_damage_pct",        # pass 2: alias
    "Throwing Attack Damage": "throwing_damage_pct",
    "Increased Throwing Attack Damage": "throwing_damage_pct",
    "Increased Bow Damage": "bow_damage_pct",
    "Bow Damage": "bow_damage_pct",                  # pass 2: freq 2 — alias
    "Increased Minion Damage": "minion_damage_pct",
    "Increased DoT Damage": "dot_damage_pct",
    "Increased Damage Over Time": "dot_damage_pct",
    "Damage Over Time": "dot_damage_pct",            # pass 2: alias
    "Global Damage Over Time": "dot_damage_pct",     # pass 2: alias
    "Increased Shadow Damage": "shadow_damage_pct",
    "Shadow Damage": "shadow_damage_pct",

    # Offense — flat added melee damage
    "Melee Physical Damage": "added_melee_physical",
    "Melee Fire Damage": "added_melee_fire",
    "Melee Cold Damage": "added_melee_cold",
    "Melee Lightning Damage": "added_melee_lightning",
    "Melee Void Damage": "added_melee_void",
    "Melee Necrotic Damage": "added_melee_necrotic",

    # Offense — flat added spell damage
    "Spell Fire Damage": "added_spell_fire",
    "Spell Cold Damage": "added_spell_cold",
    "Spell Lightning Damage": "added_spell_lightning",
    "Spell Necrotic Damage": "added_spell_necrotic",
    "Spell Void Damage": "added_spell_void",

    # Offense — flat added throwing / bow damage
    "Throwing Physical Damage": "added_throw_physical",
    "Throwing Fire Damage": "added_throw_fire",
    "Throwing Cold Damage": "added_throw_cold",
    "Bow Physical Damage": "added_bow_physical",
    "Bow Fire Damage": "added_bow_fire",

    # Offense — speed / crit
    "Attack Speed": "attack_speed_pct",
    "Increased Attack Speed": "attack_speed_pct",
    "Increased Melee Attack Speed": "attack_speed_pct",
    "Melee Attack Speed": "attack_speed_pct",        # pass 2: alias
    "Increased Bow Attack Speed": "attack_speed_pct",  # pass 2: bow attacks are attacks
    "Cast Speed": "cast_speed",
    "Increased Cast Speed": "cast_speed",
    "Increased Throwing Attack Speed": "throwing_attack_speed",  # pass 2
    "Throwing Attack Speed": "throwing_attack_speed",            # pass 2
    "Attack And Cast Speed": "_attack_and_cast_speed",  # handled specially
    "Critical Strike Chance": "crit_chance_pct",
    "Increased Critical Strike Chance": "crit_chance_pct",
    "Increased Melee Critical Strike Chance": "crit_chance_pct",  # pass 2: alias
    "Critical Chance": "crit_chance_pct",
    "Increased Critical Chance": "crit_chance_pct",
    "Increased Crit Chance": "crit_chance_pct",
    "Critical Strike Multiplier": "crit_multiplier_pct",
    "Increased Critical Strike Multiplier": "crit_multiplier_pct",
    "Critical Multiplier": "crit_multiplier_pct",
    "Crit Multiplier": "crit_multiplier_pct",

    # Offense — ailment chance
    "Poison Chance": "poison_chance_pct",
    "Melee Poison Chance": "poison_chance_pct",      # pass 2: type-scoped alias
    "Spell Poison Chance": "poison_chance_pct",      # pass 2: type-scoped alias
    "Bleed Chance": "bleed_chance_pct",
    "Melee Bleed Chance": "bleed_chance_pct",        # pass 2: freq 3 — type-scoped alias
    "Throwing Bleed Chance": "bleed_chance_pct",     # pass 2: type-scoped alias
    "Throwing Attack Bleed Chance": "bleed_chance_pct",  # pass 2: type-scoped alias
    "Ignite Chance": "ignite_chance_pct",
    "Melee Ignite Chance": "ignite_chance_pct",      # pass 2: type-scoped alias
    "Shock Chance": "shock_chance_pct",
    "Electrify Chance": "shock_chance_pct",     # Electrify is LE's legacy name for Shock
    "Chill Chance": "chill_chance_pct",
    "Slow Chance": "slow_chance_pct",                # pass 2: alias (field exists)

    # Offense — ailment / DoT duration (generic buckets via ailment_duration_pct)
    "Ignite Duration": "ailment_duration_pct",       # pass 2
    "Chill Duration": "ailment_duration_pct",        # pass 2
    "Shock Duration": "ailment_duration_pct",        # pass 2
    "Electrify Duration": "ailment_duration_pct",    # pass 2: Electrify == Shock
    "Poison Duration": "ailment_duration_pct",       # pass 2
    "Increased Poison Duration": "ailment_duration_pct",  # pass 2
    "Increased Slow Duration": "ailment_duration_pct",    # pass 2

    # Utility — buff duration
    "Buff Duration": "buff_duration_pct",            # pass 2: field already exists

    # Offense — penetration
    "Physical Penetration": "physical_penetration",
    "Fire Penetration": "fire_penetration",
    "Cold Penetration": "cold_penetration",
    "Lightning Penetration": "lightning_penetration",
    "Void Penetration": "void_penetration",
    "Necrotic Penetration": "necrotic_penetration",
    "Poison Penetration": "poison_penetration",

    # Offense — shred
    "Armour Shred Chance": "armour_shred_chance",
    "Armor Shred Chance": "armour_shred_chance",
    "Throwing Armor Shred Chance": "armour_shred_chance",   # pass 2: alias
    "Throwing Armour Shred Chance": "armour_shred_chance",  # pass 2: alias
    "Fire Shred Chance": "fire_shred_chance",
    "Cold Shred Chance": "cold_shred_chance",
    "Lightning Shred Chance": "lightning_shred_chance",
    "Lightning Res Shred Chance": "lightning_shred_chance",  # pass 2: alias

    # Offense — minion
    "Increased Minion Health": "minion_health_pct",
    "Minion Health": "minion_health_pct",
    "Increased Minion Speed": "minion_speed_pct",
    "Increased Minion Movement Speed": "minion_speed_pct",   # pass 2: alias
    "Minion Movespeed": "minion_speed_pct",                  # pass 2: alias
    "Increased Minion Physical Damage": "minion_physical_damage_pct",
    "Increased Minion Spell Damage": "minion_spell_damage_pct",
    "Increased Minion Melee Damage": "minion_melee_damage_pct",
    "Increased Minion Cold Damage": "minion_cold_damage_pct",      # pass 2: freq 4
    "Minion Cold Damage": "minion_cold_damage_pct",                # pass 2: alias
    "Minion Increased Cold Damage": "minion_cold_damage_pct",      # pass 2: alias
    "Increased Minion Necrotic Damage": "minion_necrotic_damage_pct",  # pass 2: freq 2
    "Minion Necrotic Damage": "minion_necrotic_damage_pct",        # pass 2: alias
    "Increased Minion Attack Speed": "minion_attack_speed_pct",    # pass 2: freq 3
    "Minion Attack Speed": "minion_attack_speed_pct",              # pass 2: alias
    "Increased Minion Cast Speed": "minion_cast_speed_pct",        # pass 2: freq 3
    "Minion Increased Cast Speed": "minion_cast_speed_pct",        # pass 2: alias
    "Minion Cast Speed": "minion_cast_speed_pct",                  # pass 2: alias
    "Minion Armor": "minion_armour",                               # pass 2: freq 3
    "Minion Armour": "minion_armour",                              # pass 2: alias
    "Increased Minion Armor": "minion_armour",                     # pass 2: alias
    "Increased Minion Armour": "minion_armour",                    # pass 2: alias
    "Minion Critical Multiplier": "minion_crit_multiplier_pct",    # pass 2: freq 2
    "Companion Damage": "companion_damage_pct",
    "Companion Health": "companion_health_pct",
    "Increased Companion Health": "companion_health_pct",
    "Totem Damage": "totem_damage_pct",
    "Increased Totem Damage": "totem_damage_pct",
    "Totem Health": "totem_health_pct",
    "Increased Totem Health": "totem_health_pct",

    # Sustain
    "Leech": "leech",
    "Health Leech": "leech",
    "Increased Health Leech": "leech",               # pass 2: alias
    "Damage Leeched As Health": "leech",
    "Damage Leeched as Health on Hit": "leech",      # pass 2: alias
    "Melee Damage Leeched as Health": "leech",
    "Increased Leech Rate": "leech_rate_pct",        # pass 2: freq 3 — distinct field
    "Health On Kill": "health_on_kill",
    "Mana On Kill": "mana_on_kill",
    "Ward On Kill": "ward_on_kill",
    "Health On Block": "health_on_block",
    "Health Gained On Block": "health_on_block",     # pass 2: alias
    "Health Gained on Block": "health_on_block",     # pass 2: alias
    "Healing Effectiveness": "healing_effectiveness_pct",
    "Increased Healing Effectiveness": "healing_effectiveness_pct",
    "Increased Healing": "healing_effectiveness_pct",
    "Healing": "healing_effectiveness_pct",          # pass 2: alias

    # Utility
    "Movement Speed": "movement_speed",
    "Increased Movement Speed": "movement_speed",
    "Movespeed": "movement_speed",
    "Increased Movespeed": "movement_speed",
    "Cooldown Recovery Speed": "cooldown_recovery_speed",
    "Increased Cooldown Recovery Speed": "cooldown_recovery_speed",
    "Increased Area": "area_pct",
    "Increased Area For Area Skills": "area_pct",
    "Increased Area for Area Skills": "area_pct",
    "Area For Area Spells": "area_pct",
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

def resolve_passive_stats(node_ids: list[str]) -> PassiveStats:
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
                elif mapped == "_all_resistances":
                    for res in ("fire_res", "cold_res", "lightning_res",
                                "void_res", "necrotic_res", "poison_res",
                                "physical_res"):
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
