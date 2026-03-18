"""
Stat Engine — aggregates all character stats into a single BuildStats dict.

Mirrors the logic in frontend/src/lib/simulation.ts:aggregateStats().
Sources: class base stats, mastery bonuses, passive nodes, gear affixes,
         attribute scaling.

This module is pure logic — no DB imports, no HTTP. Callers pass in
already-loaded data objects.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# BuildStats dataclass — mirrors BuildStats interface in simulation.ts
# ---------------------------------------------------------------------------

@dataclass
class BuildStats:
    # Offense
    base_damage: float = 0.0
    attack_speed: float = 1.0
    crit_chance: float = 0.05       # 0.0–1.0
    crit_multiplier: float = 1.5    # total multiplier e.g. 2.0
    spell_damage_pct: float = 0.0   # "increased" pool — additive with others
    physical_damage_pct: float = 0.0
    fire_damage_pct: float = 0.0
    cold_damage_pct: float = 0.0
    lightning_damage_pct: float = 0.0
    necrotic_damage_pct: float = 0.0
    void_damage_pct: float = 0.0
    poison_damage_pct: float = 0.0
    minion_damage_pct: float = 0.0
    attack_speed_pct: float = 0.0   # % bonus
    cast_speed: float = 0.0         # % bonus
    crit_chance_pct: float = 0.0    # % to add to crit_chance
    crit_multiplier_pct: float = 0.0
    more_damage_multiplier: float = 1.0  # "more" pool — multiplicative (default 1×)
    # Defense
    max_health: float = 0.0
    armour: float = 0.0
    dodge_rating: float = 0.0
    ward: float = 0.0
    ward_retention_pct: float = 0.0
    ward_regen: float = 0.0         # flat ward regenerated per second
    fire_res: float = 0.0
    cold_res: float = 0.0
    lightning_res: float = 0.0
    void_res: float = 0.0
    necrotic_res: float = 0.0
    poison_res: float = 0.0
    # Resources
    max_mana: float = 0.0
    mana_regen: float = 0.0
    health_regen: float = 0.0
    # Attributes
    strength: float = 0.0
    intelligence: float = 0.0
    dexterity: float = 0.0
    vitality: float = 0.0
    attunement: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Game constants — mirrored from frontend/src/lib/gameData.ts
# ---------------------------------------------------------------------------

CLASS_BASE_STATS: dict = {
    "Acolyte":   {"health": 380, "mana": 120, "strength": 5,  "intelligence": 15, "dexterity": 5,  "vitality": 8,  "attunement": 12, "base_damage": 80,  "crit_chance": 0.05, "crit_multiplier": 1.5, "attack_speed": 1.0},
    "Mage":      {"health": 340, "mana": 180, "strength": 3,  "intelligence": 20, "dexterity": 7,  "vitality": 6,  "attunement": 14, "base_damage": 100, "crit_chance": 0.05, "crit_multiplier": 1.5, "attack_speed": 1.0},
    "Primalist": {"health": 480, "mana": 80,  "strength": 18, "intelligence": 5,  "dexterity": 8,  "vitality": 14, "attunement": 5,  "base_damage": 90,  "crit_chance": 0.05, "crit_multiplier": 1.5, "attack_speed": 1.2},
    "Sentinel":  {"health": 520, "mana": 60,  "strength": 20, "intelligence": 5,  "dexterity": 5,  "vitality": 16, "attunement": 4,  "base_damage": 110, "crit_chance": 0.05, "crit_multiplier": 1.5, "attack_speed": 0.9},
    "Rogue":     {"health": 400, "mana": 100, "strength": 8,  "intelligence": 8,  "dexterity": 18, "vitality": 9,  "attunement": 7,  "base_damage": 85,  "crit_chance": 0.07, "crit_multiplier": 1.5, "attack_speed": 1.3},
}

MASTERY_BONUSES: dict = {
    "Paladin":       {"max_health": 200},
    "Necromancer":   {"minion_damage_pct": 15},
    "Runemaster":    {"spell_damage_pct": 10},
    "Sorcerer":      {"spell_damage_pct": 15, "cast_speed": 5},
    "Bladedancer":   {"physical_damage_pct": 15},
    "Marksman":      {"physical_damage_pct": 10, "attack_speed_pct": 5},
    "Warlock":       {"necrotic_damage_pct": 10, "void_damage_pct": 10},
    # Lich and Forge Guard handled per-point below
}

KEYSTONE_BONUSES: dict = {
    "Death's Door":         {"max_health": 200, "armour": -50},
    "Soul Aegis":           {"ward": 50, "ward_retention_pct": 15},
    "Forbidden Knowledge":  {"spell_damage_pct": 20, "crit_chance_pct": 5},
    "Grave Chill":          {"cold_damage_pct": 15, "necrotic_damage_pct": 10},
    "Stolen Vitality":      {"max_health": 150, "spell_damage_pct": 10},
    "Arcane Absorption":    {"spell_damage_pct": 20, "max_mana": 30},
    "Mana Starved Sorcery": {"spell_damage_pct": 40},
    "Runic Convergence":    {"spell_damage_pct": 25, "cast_speed": 10},
    "Spell Blade":          {"physical_damage_pct": 20, "spell_damage_pct": 15},
    "Natural Attunement":   {"cold_damage_pct": 10, "lightning_damage_pct": 10, "max_health": 20},
    "Ancient Power":        {"physical_damage_pct": 25},
    "Nature's Reach":       {"lightning_damage_pct": 15},
    "Primal Strength":      {"physical_damage_pct": 20, "max_health": 100},
    "Juggernaut":           {"armour": 200, "max_health": 100},
    "Forged in Fire":       {"fire_damage_pct": 30, "armour": 100},
    "Void Touched":         {"void_damage_pct": 30},
    "Sacred Aegis":         {"fire_res": 50, "cold_res": 50},
    "Shadow Daggers":       {"physical_damage_pct": 20, "crit_chance_pct": 5},
    "Expose Weakness":      {"physical_damage_pct": 30},
    "Acrobatics":           {"dodge_rating": 150},
    "Cheap Shot":           {"physical_damage_pct": 25, "crit_chance_pct": 3},
}

ATTRIBUTE_SCALING: dict = {
    "strength":     {"physical_damage_pct": 0.5, "armour": 2},
    "intelligence": {"spell_damage_pct": 0.5, "max_mana": 10},
    "dexterity":    {"attack_speed_pct": 0.3, "dodge_rating": 3},
    "vitality":     {"max_health": 10},
    "attunement":   {"cast_speed": 0.3},
}

# Passive node stat cycle — same as CORE_STAT_CYCLE in simulation.ts
CORE_STAT_CYCLE: list = [
    ("max_health", 8),
    ("spell_damage_pct", 1),
    ("physical_damage_pct", 1),
    ("armour", 10),
    ("fire_res", 2),
    ("cold_res", 2),
    ("lightning_res", 2),
    ("void_res", 2),
    ("necrotic_res", 2),
    ("cast_speed", 1),
]

NOTABLE_MULTIPLIER = 3

# Affix stat_key → midpoint value per tier
# Tier keys: "T1"=lowest/worst, "T5"=best/highest. Matches crafting system.
AFFIX_TIER_MIDPOINTS: dict = {
    "Spell Damage":               {"T1": 4,  "T2": 11, "T3": 20, "T4": 32, "T5": 47},
    "Necrotic Damage":            {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Fire Damage":                {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Cold Damage":                {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Lightning Damage":           {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Physical Damage":            {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Void Damage":                {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Poison Damage":              {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Minion Damage":              {"T1": 14, "T2": 27, "T3": 42, "T4": 59, "T5": 80},
    "Cast Speed":                 {"T1": 4,  "T2": 7,  "T3": 12, "T4": 17, "T5": 22},
    "Attack Speed":               {"T1": 4,  "T2": 7,  "T3": 12, "T4": 17, "T5": 22},
    "Health":                     {"T1": 27, "T2": 45, "T3": 68, "T4": 95, "T5": 130},
    "Armour":                     {"T1": 59, "T2": 104, "T3": 164, "T4": 249, "T5": 360},
    "Ward":                       {"T1": 9,  "T2": 22, "T3": 39, "T4": 64, "T5": 100},
    "Endurance":                  {"T1": 14, "T2": 27, "T3": 44, "T4": 67, "T5": 95},
    "Fire Resistance":            {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Cold Resistance":            {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Lightning Resistance":       {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Void Resistance":            {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Necrotic Resistance":        {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Poison Resistance":          {"T1": 15, "T2": 24, "T3": 34, "T4": 44, "T5": 55},
    "Ward Retention":             {"T1": 7,  "T2": 12, "T3": 17, "T4": 22, "T5": 27},
    "Dodge Rating":               {"T1": 37, "T2": 64, "T3": 99, "T4": 149, "T5": 220},
    "Critical Strike Chance":     {"T1": 1,  "T2": 3,  "T3": 5,  "T4": 7,  "T5": 10},
    "Critical Strike Multiplier": {"T1": 5,  "T2": 11, "T3": 19, "T4": 32, "T5": 50},
    "Strength":                   {"T1": 4,  "T2": 7,  "T3": 11, "T4": 15, "T5": 21},
    "Intelligence":               {"T1": 4,  "T2": 7,  "T3": 11, "T4": 15, "T5": 21},
    "Dexterity":                  {"T1": 4,  "T2": 7,  "T3": 11, "T4": 15, "T5": 21},
    "Vitality":                   {"T1": 4,  "T2": 7,  "T3": 11, "T4": 15, "T5": 21},
    "Attunement":                 {"T1": 4,  "T2": 7,  "T3": 11, "T4": 15, "T5": 21},
    "Mana":                       {"T1": 14, "T2": 27, "T3": 44, "T4": 67, "T5": 95},
    "Mana Regen":                 {"T1": 1,  "T2": 3,  "T3": 5,  "T4": 8,  "T5": 12},
    "Health Regen":               {"T1": 1,  "T2": 4,  "T3": 7,  "T4": 12, "T5": 20},
}

# Maps affix display name → BuildStats field name
AFFIX_STAT_KEYS: dict = {
    "Spell Damage":               "spell_damage_pct",
    "Necrotic Damage":            "necrotic_damage_pct",
    "Fire Damage":                "fire_damage_pct",
    "Cold Damage":                "cold_damage_pct",
    "Lightning Damage":           "lightning_damage_pct",
    "Physical Damage":            "physical_damage_pct",
    "Void Damage":                "void_damage_pct",
    "Poison Damage":              "poison_damage_pct",
    "Minion Damage":              "minion_damage_pct",
    "Cast Speed":                 "cast_speed",
    "Attack Speed":               "attack_speed_pct",
    "Health":                     "max_health",
    "Armour":                     "armour",
    "Ward":                       "ward",
    "Endurance":                  "max_health",
    "Fire Resistance":            "fire_res",
    "Cold Resistance":            "cold_res",
    "Lightning Resistance":       "lightning_res",
    "Void Resistance":            "void_res",
    "Necrotic Resistance":        "necrotic_res",
    "Poison Resistance":          "poison_res",
    "Ward Retention":             "ward_retention_pct",
    "Dodge Rating":               "dodge_rating",
    "Critical Strike Chance":     "crit_chance_pct",
    "Critical Strike Multiplier": "crit_multiplier_pct",
    "Strength":                   "strength",
    "Intelligence":               "intelligence",
    "Dexterity":                  "dexterity",
    "Vitality":                   "vitality",
    "Attunement":                 "attunement",
    "Mana":                       "max_mana",
    "Mana Regen":                 "mana_regen",
    "Health Regen":               "health_regen",
}


# ---------------------------------------------------------------------------
# Helper — add a partial stat dict to a BuildStats instance
# ---------------------------------------------------------------------------

def _add_partial(stats: BuildStats, partial: dict) -> None:
    for key, value in partial.items():
        if hasattr(stats, key):
            setattr(stats, key, getattr(stats, key) + value)


# ---------------------------------------------------------------------------
# Helper — passive node bonus (mirrors getNodeBonus in simulation.ts)
# ---------------------------------------------------------------------------

def _get_node_bonus(node_id: int, node_type: str, node_name: str) -> dict:
    if node_type == "mastery-gate":
        return {}
    if node_type == "keystone":
        return KEYSTONE_BONUSES.get(node_name, {"spell_damage_pct": 10, "max_health": 50})
    stat_key, base_amount = CORE_STAT_CYCLE[node_id % len(CORE_STAT_CYCLE)]
    amount = base_amount * NOTABLE_MULTIPLIER if node_type == "notable" else base_amount
    return {stat_key: amount}


# ---------------------------------------------------------------------------
# Helper — affix tier midpoint value
# ---------------------------------------------------------------------------

def get_affix_value(affix_name: str, tier: int) -> float:
    """Returns the midpoint stat value for an affix at the given tier (1=lowest, 5=best)."""
    tier_key = f"T{tier}"
    midpoints = AFFIX_TIER_MIDPOINTS.get(affix_name, {})
    return float(midpoints.get(tier_key, 0))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def aggregate_stats(
    character_class: str,
    mastery: str,
    allocated_node_ids: list[int],
    nodes: list[dict],        # list of {"id", "type", "name"}
    gear_affixes: list[dict], # list of {"name", "tier", "sealed"} — same as CraftAffix
) -> BuildStats:
    """
    Aggregate all character stats from every source.

    Args:
        character_class: e.g. "Mage"
        mastery: e.g. "Sorcerer"
        allocated_node_ids: list of passive node IDs the player has allocated
        nodes: all available passive nodes for the class (id, type, name)
        gear_affixes: flat list of affixes across all gear slots (name, tier)

    Returns:
        BuildStats with all values accumulated and derived stats applied.
    """
    stats = BuildStats()
    allocated_set = set(allocated_node_ids)

    # 1. Class base stats
    base = CLASS_BASE_STATS.get(character_class, CLASS_BASE_STATS["Sentinel"])
    stats.base_damage = base["base_damage"]
    stats.attack_speed = base["attack_speed"]
    stats.crit_chance = base["crit_chance"]
    stats.crit_multiplier = base["crit_multiplier"]
    stats.max_health = base["health"]
    stats.max_mana = base["mana"]
    stats.strength = base["strength"]
    stats.intelligence = base["intelligence"]
    stats.dexterity = base["dexterity"]
    stats.vitality = base["vitality"]
    stats.attunement = base["attunement"]

    # 2. Mastery flat bonuses
    mastery_bonus = MASTERY_BONUSES.get(mastery, {})
    _add_partial(stats, mastery_bonus)

    # Per-point mastery bonuses
    pts_used = len(allocated_node_ids)
    if mastery == "Lich":
        stats.ward += pts_used * 8
    elif mastery == "Forge Guard":
        stats.armour += pts_used * 15

    # 3. Passive node bonuses
    for node in nodes:
        if node["id"] not in allocated_set:
            continue
        bonus = _get_node_bonus(node["id"], node.get("type", "core"), node.get("name", ""))
        _add_partial(stats, bonus)

    # 4. Gear affix values (sealed affixes still contribute stats)
    for affix in gear_affixes:
        affix_name = affix.get("name", "")
        tier = int(affix.get("tier", 3))
        stat_key = AFFIX_STAT_KEYS.get(affix_name)
        if not stat_key:
            continue
        value = get_affix_value(affix_name, tier)
        if value and hasattr(stats, stat_key):
            setattr(stats, stat_key, getattr(stats, stat_key) + value)

    # 5. Attribute scaling
    stats.spell_damage_pct    += stats.intelligence * ATTRIBUTE_SCALING["intelligence"]["spell_damage_pct"]
    stats.max_mana            += stats.intelligence * ATTRIBUTE_SCALING["intelligence"]["max_mana"]
    stats.physical_damage_pct += stats.strength     * ATTRIBUTE_SCALING["strength"]["physical_damage_pct"]
    stats.armour              += stats.strength     * ATTRIBUTE_SCALING["strength"]["armour"]
    stats.attack_speed_pct    += stats.dexterity    * ATTRIBUTE_SCALING["dexterity"]["attack_speed_pct"]
    stats.dodge_rating        += stats.dexterity    * ATTRIBUTE_SCALING["dexterity"]["dodge_rating"]
    stats.max_health          += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["max_health"]
    stats.cast_speed          += stats.attunement   * ATTRIBUTE_SCALING["attunement"]["cast_speed"]

    # 6. Apply % bonuses to base values
    stats.crit_chance    = min(0.95, stats.crit_chance + stats.crit_chance_pct / 100)
    stats.crit_multiplier += stats.crit_multiplier_pct / 100
    stats.attack_speed   = stats.attack_speed * (1 + stats.attack_speed_pct / 100)

    return stats
