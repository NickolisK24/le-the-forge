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

from app.constants.combat import BASE_CRIT_CHANCE, BASE_CRIT_MULTIPLIER, CRIT_CHANCE_CAP
from app.game_data.game_data_loader import (
    get_affix_tier_midpoints,
    get_affix_stat_keys,
)
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# BuildStats dataclass — mirrors BuildStats interface in simulation.ts
# ---------------------------------------------------------------------------

@dataclass
class BuildStats:
    # Offense — base
    base_damage: float = 0.0
    attack_speed: float = 1.0
    crit_chance: float = BASE_CRIT_CHANCE       # 0.0–1.0
    crit_multiplier: float = BASE_CRIT_MULTIPLIER    # total multiplier e.g. 2.0

    # Offense — percentage increased damage pools
    spell_damage_pct: float = 0.0
    physical_damage_pct: float = 0.0
    fire_damage_pct: float = 0.0
    cold_damage_pct: float = 0.0
    lightning_damage_pct: float = 0.0
    necrotic_damage_pct: float = 0.0
    void_damage_pct: float = 0.0
    poison_damage_pct: float = 0.0
    minion_damage_pct: float = 0.0
    melee_damage_pct: float = 0.0
    throwing_damage_pct: float = 0.0
    bow_damage_pct: float = 0.0
    elemental_damage_pct: float = 0.0
    dot_damage_pct: float = 0.0

    # Offense — percentage speed / crit
    attack_speed_pct: float = 0.0
    cast_speed: float = 0.0
    throwing_attack_speed: float = 0.0
    crit_chance_pct: float = 0.0
    crit_multiplier_pct: float = 0.0
    more_damage_multiplier: float = 1.0

    # Offense — flat added damage
    added_melee_physical: float = 0.0
    added_melee_fire: float = 0.0
    added_melee_cold: float = 0.0
    added_melee_lightning: float = 0.0
    added_melee_void: float = 0.0
    added_melee_necrotic: float = 0.0
    added_spell_damage: float = 0.0
    added_spell_fire: float = 0.0
    added_spell_cold: float = 0.0
    added_spell_lightning: float = 0.0
    added_spell_necrotic: float = 0.0
    added_spell_void: float = 0.0
    added_throw_physical: float = 0.0
    added_throw_fire: float = 0.0
    added_throw_cold: float = 0.0
    added_bow_physical: float = 0.0
    added_bow_fire: float = 0.0

    # Offense — ailment chance
    poison_chance_pct: float = 0.0
    bleed_chance_pct: float = 0.0
    ignite_chance_pct: float = 0.0
    shock_chance_pct: float = 0.0
    chill_chance_pct: float = 0.0
    slow_chance_pct: float = 0.0

    # Offense — ailment / DoT damage
    bleed_damage_pct: float = 0.0
    ignite_damage_pct: float = 0.0
    poison_dot_damage_pct: float = 0.0

    # Offense — minion
    minion_health_pct: float = 0.0
    minion_speed_pct: float = 0.0
    minion_physical_damage_pct: float = 0.0
    minion_spell_damage_pct: float = 0.0
    minion_melee_damage_pct: float = 0.0

    # Defense — health / armour
    max_health: float = 0.0
    health_pct: float = 0.0
    hybrid_health: float = 0.0
    armour: float = 0.0
    dodge_rating: float = 0.0
    block_chance: float = 0.0
    block_effectiveness: float = 0.0
    endurance: float = 0.0
    endurance_threshold: float = 0.0
    stun_avoidance: float = 0.0
    crit_avoidance: float = 0.0
    glancing_blow: float = 0.0

    # Defense — ward
    ward: float = 0.0
    ward_retention_pct: float = 0.0
    ward_regen: float = 0.0
    mana_to_ward_pct: float = 0.0      # % of mana spent converted to ward

    # Defense — resistances
    fire_res: float = 0.0
    cold_res: float = 0.0
    lightning_res: float = 0.0
    void_res: float = 0.0
    necrotic_res: float = 0.0
    poison_res: float = 0.0
    physical_res: float = 0.0

    # Offense — penetration (bypasses enemy resistance)
    physical_penetration: float = 0.0
    fire_penetration: float = 0.0
    cold_penetration: float = 0.0
    lightning_penetration: float = 0.0
    void_penetration: float = 0.0
    necrotic_penetration: float = 0.0
    poison_penetration: float = 0.0

    # Offense — debuff application chances
    armour_shred_chance: float = 0.0
    fire_shred_chance: float = 0.0
    cold_shred_chance: float = 0.0
    lightning_shred_chance: float = 0.0

    # Offense — channelling
    channelling_damage_pct: float = 0.0

    # Offense — specific damage types
    shadow_damage_pct: float = 0.0
    dagger_damage_pct: float = 0.0
    overkill_damage_pct: float = 0.0

    # Offense — minion/companion/totem
    minion_crit_chance_pct: float = 0.0
    companion_damage_pct: float = 0.0
    companion_health_pct: float = 0.0
    totem_damage_pct: float = 0.0
    totem_health_pct: float = 0.0

    # Resources
    max_mana: float = 0.0
    mana_regen: float = 0.0
    health_regen: float = 0.0
    mana_efficiency_pct: float = 0.0

    # Sustain
    leech: float = 0.0
    health_on_kill: float = 0.0
    mana_on_kill: float = 0.0
    ward_on_kill: float = 0.0
    health_on_block: float = 0.0
    health_on_potion: float = 0.0
    ward_on_potion: float = 0.0
    healing_effectiveness_pct: float = 0.0

    # Utility
    movement_speed: float = 0.0
    cooldown_recovery_speed: float = 0.0
    channelling_cost_reduction: float = 0.0
    area_pct: float = 0.0
    stun_duration_pct: float = 0.0
    buff_effect_pct: float = 0.0
    ailment_effect_pct: float = 0.0
    ailment_duration_pct: float = 0.0

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

# Affix lookups — loaded from canonical affixes.json via game_data_loader
AFFIX_TIER_MIDPOINTS: dict = get_affix_tier_midpoints()
AFFIX_STAT_KEYS: dict = get_affix_stat_keys()


# ---------------------------------------------------------------------------
# Helper — add a partial stat dict to a BuildStats instance
# ---------------------------------------------------------------------------

def _add_partial(stats: BuildStats, partial: dict) -> None:
    for key, value in partial.items():
        if hasattr(stats, key):
            setattr(stats, key, getattr(stats, key) + value)


# ---------------------------------------------------------------------------
# Helper — apply a single stat_key (direct or composite) to BuildStats
# ---------------------------------------------------------------------------

def _apply_stat_key(stats: BuildStats, stat_key: str, value: float) -> None:
    """
    Apply a stat_key value to BuildStats.  Handles both simple field names
    and special composite keys that distribute to multiple fields:
      _all_attributes      → strength, intelligence, dexterity, vitality, attunement
      _all_res / _all_resistances → fire_res, cold_res, lightning_res, void_res, necrotic_res, poison_res
      _elemental_res       → fire_res, cold_res, lightning_res
      _attack_and_cast_speed → attack_speed_pct, cast_speed
    """
    if value == 0:
        return
    if stat_key == "_all_attributes":
        for attr in ("strength", "intelligence", "dexterity", "vitality", "attunement"):
            setattr(stats, attr, getattr(stats, attr) + value)
    elif stat_key in ("_all_res", "_all_resistances"):
        for res in ("fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res", "poison_res"):
            setattr(stats, res, getattr(stats, res) + value)
    elif stat_key == "_elemental_res":
        for res in ("fire_res", "cold_res", "lightning_res"):
            setattr(stats, res, getattr(stats, res) + value)
    elif stat_key == "_attack_and_cast_speed":
        stats.attack_speed_pct += value
        stats.cast_speed += value
    elif hasattr(stats, stat_key):
        setattr(stats, stat_key, getattr(stats, stat_key) + value)


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
    """Returns the midpoint stat value for an affix at the given tier (1=lowest, 7=best)."""
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
    passive_stats: Optional[dict] = None,  # output of resolve_passive_stats()
) -> BuildStats:
    """
    Aggregate all character stats from every source.

    Args:
        character_class: e.g. "Mage"
        mastery: e.g. "Sorcerer"
        allocated_node_ids: list of passive node IDs the player has allocated
        nodes: all available passive nodes for the class (id, type, name)
        gear_affixes: flat list of affixes across all gear slots (name, tier)
        passive_stats: resolved passive tree stats from passive_stat_resolver
            ({"additive": {...}, "special_effects": [...]}). When provided,
            the additive values are merged into the stat totals.

    Returns:
        BuildStats with all values accumulated and derived stats applied.
    """
    log.info(
        "aggregate_stats.start",
        character_class=character_class,
        mastery=mastery,
        nodes=len(allocated_node_ids),
        gear_affixes=len(gear_affixes),
        has_passive_stats=passive_stats is not None,
    )

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
    # Nodes dict now has "id" = raw_node_id (int) so set comparison works correctly.
    # When real passive_stats are available from the DB resolver, only apply keystones
    # here (their effects aren't in the DB stats column). For regular/notable nodes the
    # resolver data is authoritative and we skip the modulo fallback to avoid double-counting.
    has_real_passive_data = bool(passive_stats and passive_stats.get("additive"))
    for node in nodes:
        if node["id"] not in allocated_set:
            continue
        node_type = node.get("type", "core")
        node_name = node.get("name", "")
        if has_real_passive_data and node_type != "keystone":
            # Real data from passive_stat_resolver covers this node; skip modulo fallback.
            continue
        bonus = _get_node_bonus(node["id"], node_type, node_name)
        _add_partial(stats, bonus)

    # 4. Gear affix values (sealed affixes still contribute stats)
    # Accepts two formats:
    #   a) Normal crafted affixes: {"name": str, "tier": int} — looked up via AFFIX_STAT_KEYS
    #   b) Synthetic unique stats: {"stat_key": str, "value": float} — applied directly
    for affix in gear_affixes:
        # Format b: synthetic unique item stats injected by build_analysis_service
        if "stat_key" in affix:
            _apply_stat_key(stats, affix["stat_key"], float(affix.get("value", 0)))
            continue

        # Format a: normal gear affix by name + tier
        affix_name = affix.get("name", "")
        tier = int(affix.get("tier", 3))
        stat_key = AFFIX_STAT_KEYS.get(affix_name)
        if not stat_key:
            continue
        value = get_affix_value(affix_name, tier)
        if value:
            _apply_stat_key(stats, stat_key, value)

    # 5. Resolved passive tree stats (from passive_stat_resolver)
    if passive_stats:
        _add_partial(stats, passive_stats.get("additive", {}))

    # 6. Attribute scaling
    stats.spell_damage_pct    += stats.intelligence * ATTRIBUTE_SCALING["intelligence"]["spell_damage_pct"]
    stats.max_mana            += stats.intelligence * ATTRIBUTE_SCALING["intelligence"]["max_mana"]
    stats.physical_damage_pct += stats.strength     * ATTRIBUTE_SCALING["strength"]["physical_damage_pct"]
    stats.armour              += stats.strength     * ATTRIBUTE_SCALING["strength"]["armour"]
    stats.attack_speed_pct    += stats.dexterity    * ATTRIBUTE_SCALING["dexterity"]["attack_speed_pct"]
    stats.dodge_rating        += stats.dexterity    * ATTRIBUTE_SCALING["dexterity"]["dodge_rating"]
    stats.max_health          += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["max_health"]
    stats.cast_speed          += stats.attunement   * ATTRIBUTE_SCALING["attunement"]["cast_speed"]

    # 7. Apply percentage health bonuses
    stats.max_health = stats.max_health * (1 + stats.health_pct / 100) + stats.hybrid_health

    # 8. Apply % bonuses to base values
    stats.crit_chance    = min(CRIT_CHANCE_CAP, stats.crit_chance + stats.crit_chance_pct / 100)
    stats.crit_multiplier += stats.crit_multiplier_pct / 100
    stats.attack_speed   = stats.attack_speed * (1 + stats.attack_speed_pct / 100)

    log.info(
        "aggregate_stats.end",
        base_damage=stats.base_damage,
        max_health=stats.max_health,
        crit_chance=round(stats.crit_chance, 4),
    )

    return stats
