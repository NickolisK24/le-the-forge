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

from app.constants.combat import BASE_CRIT_CHANCE, BASE_CRIT_MULTIPLIER
from app.domain.calculators.stat_calculator import apply_percent_bonus, combine_additive_percents
from app.domain.calculators.crit_calculator import effective_crit_chance, effective_crit_multiplier
from app.game_data.game_data_loader import (
    get_affix_tier_midpoints,
    get_affix_stat_keys,
    get_affix_types,
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
    more_damage_pct: float = 0.0
    more_damage_multiplier: float = 1.0  # product of all "more" damage multipliers (starts at 1×)

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
    ailment_damage_pct: float = 0.0      # increased damage for ALL ailment types
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
    # Strength grants 4% Increased Armor per point — accumulated here and
    # applied multiplicatively to armour in the mitigation calculator.
    armour_pct: float = 0.0
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
    buff_duration_pct: float = 0.0       # increased duration for all buffs
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

# VERIFIED: in-game character sheet at level 1 with no gear and no passives.
# All classes share the same survivability floor (110 HP, 51 mana, 6 HP regen,
# 8 mana regen, 255 stun avoidance, 20.0 endurance, 22 endurance threshold)
# and 2.0× crit multiplier. Only attribute allocation and (for Primalist/Acolyte)
# base mana or endurance threshold differ.
CLASS_BASE_STATS: dict = {
    "Sentinel":  {
        "health": 110, "mana": 51, "health_regen": 6, "mana_regen": 8,
        "strength": 2, "intelligence": 0, "dexterity": 0,
        "vitality": 1, "attunement": 0,
        "attack_speed": 1.0, "crit_chance": 0.05, "crit_multiplier": 2.0,
        "stun_avoidance": 255, "endurance": 20.0, "endurance_threshold": 22,
    },
    "Rogue":     {
        "health": 110, "mana": 51, "health_regen": 6, "mana_regen": 8,
        "strength": 0, "intelligence": 0, "dexterity": 3,
        "vitality": 0, "attunement": 0,
        "attack_speed": 1.0, "crit_chance": 0.05, "crit_multiplier": 2.0,
        "stun_avoidance": 255, "endurance": 20.0, "endurance_threshold": 22,
    },
    "Mage":      {
        "health": 110, "mana": 51, "health_regen": 6, "mana_regen": 8,
        "strength": 0, "intelligence": 3, "dexterity": 0,
        "vitality": 0, "attunement": 0,
        "attack_speed": 1.0, "crit_chance": 0.05, "crit_multiplier": 2.0,
        "stun_avoidance": 255, "endurance": 20.0, "endurance_threshold": 22,
    },
    "Primalist": {
        "health": 110, "mana": 51, "health_regen": 6, "mana_regen": 8,
        "strength": 2, "intelligence": 0, "dexterity": 0,
        "vitality": 0, "attunement": 1,
        "attack_speed": 1.0, "crit_chance": 0.05, "crit_multiplier": 2.0,
        "stun_avoidance": 255, "endurance": 20.0, "endurance_threshold": 22,
    },
    "Acolyte":   {
        "health": 110, "mana": 51, "health_regen": 6, "mana_regen": 8,
        "strength": 0, "intelligence": 2, "dexterity": 0,
        "vitality": 1, "attunement": 0,
        "attack_speed": 1.0, "crit_chance": 0.05, "crit_multiplier": 2.0,
        "stun_avoidance": 255, "endurance": 20.0, "endurance_threshold": 22,
    },
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

# VERIFIED: in-game attribute tooltip descriptions + level-1 sheet math.
# Per-point direct grants (attributes also scale specific skills at the skill
# layer — that's not handled here):
#   Strength     → 4% Increased Armor (multiplicative on current armour)
#   Dexterity    → 4 Dodge Rating  (Rogue DEX 3 = 12 dodge)
#   Intelligence → 2% Ward Retention  (Mage INT 3 = 6% ward)
#   Attunement   → 2 Mana  (Primalist ATT 1 = 53 mana)
#   Vitality     → 6 Health + 1 Endurance Threshold + 1% Poison Resistance
#                  + 1% Necrotic Resistance  (VIT 1 classes show 116 HP, 1%
#                  poison, 1% necrotic, ET 23; VIT 0 shows 110, 0%, 0%, 22)
ATTRIBUTE_SCALING: dict = {
    "strength":     {"armour_pct": 4.0},
    "dexterity":    {"dodge_rating": 4},
    "intelligence": {"ward_retention_pct": 2.0},
    "vitality":     {"max_health": 6, "endurance_threshold": 1,
                     "poison_res": 1.0, "necrotic_res": 1.0},
    "attunement":   {"max_mana": 2},
}

# Passive node stat cycle — generic fallback when real passive data is unavailable.
# Class-specific cycles give more realistic stat distributions per class archetype.
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

CLASS_STAT_CYCLES: dict[str, list] = {
    "Rogue": [
        ("dexterity", 2),
        ("physical_damage_pct", 2),
        ("crit_chance_pct", 1),
        ("dodge_rating", 15),
        ("max_health", 6),
        ("attack_speed_pct", 1),
        ("physical_damage_pct", 1),
        ("void_res", 2),
        ("cold_res", 2),
        ("dexterity", 1),
    ],
    "Mage": [
        ("intelligence", 2),
        ("spell_damage_pct", 2),
        ("max_mana", 8),
        ("ward", 10),
        ("max_health", 6),
        ("cast_speed", 1),
        ("elemental_damage_pct", 1),
        ("fire_res", 2),
        ("lightning_res", 2),
        ("cold_res", 2),
    ],
    "Sentinel": [
        ("strength", 2),
        ("physical_damage_pct", 2),
        ("armour", 20),
        ("max_health", 10),
        ("block_chance", 2),
        ("fire_res", 3),
        ("void_res", 2),
        ("physical_damage_pct", 1),
        ("vitality", 1),
        ("necrotic_res", 2),
    ],
    "Primalist": [
        ("strength", 2),
        ("physical_damage_pct", 2),
        ("max_health", 10),
        ("attunement", 1),
        ("armour", 10),
        ("cold_res", 2),
        ("lightning_res", 2),
        ("minion_damage_pct", 1),
        ("vitality", 1),
        ("dodge_rating", 10),
    ],
    "Acolyte": [
        ("intelligence", 2),
        ("necrotic_damage_pct", 2),
        ("max_health", 8),
        ("ward", 8),
        ("vitality", 1),
        ("spell_damage_pct", 1),
        ("void_damage_pct", 1),
        ("necrotic_res", 3),
        ("void_res", 2),
        ("minion_damage_pct", 1),
    ],
}

NOTABLE_MULTIPLIER = 3

# Affix lookups — loaded from canonical affixes.json via game_data_loader
AFFIX_TIER_MIDPOINTS: dict = get_affix_tier_midpoints()
AFFIX_STAT_KEYS: dict = get_affix_stat_keys()
AFFIX_TYPES: dict = get_affix_types()


# ---------------------------------------------------------------------------
# Stat Pool — flat / increased / more bucket system
# ---------------------------------------------------------------------------

class StatPool:
    """Accumulates stat modifiers in separate buckets by modifier type.

    flat        — additive base values (e.g. +40 Health, +12 Fire Resistance)
    increased   — additive % modifiers (e.g. +25% Spell Damage, +10% Attack Speed)
    more        — multiplicative modifiers (e.g. ×1.20 More Damage)
    multipliers — additional named multipliers applied after more (e.g. double-dip sources)

    Final damage = (base + flat) * (1 + sum(increased)/100) * product(more) * product(multipliers)
    """
    __slots__ = ("flat", "increased", "more", "multipliers")

    def __init__(self) -> None:
        self.flat: dict[str, float] = {}
        self.increased: dict[str, float] = {}
        self.more: dict[str, float] = {}
        self.multipliers: dict[str, float] = {}

    def add_flat(self, stat: str, value: float) -> None:
        self.flat[stat] = self.flat.get(stat, 0.0) + value

    def add_increased(self, stat: str, value: float) -> None:
        self.increased[stat] = self.increased.get(stat, 0.0) + value

    def add_more(self, stat: str, value: float) -> None:
        current = self.more.get(stat, 1.0)
        self.more[stat] = current * (1 + value / 100)

    def add_multiplier(self, stat: str, value: float) -> None:
        """Add a named multiplicative scalar (value is already a multiplier, e.g. 1.15)."""
        current = self.multipliers.get(stat, 1.0)
        self.multipliers[stat] = current * value

    def resolve_to(self, stats: "BuildStats") -> None:
        """Apply all accumulated pool values to a BuildStats instance."""
        for stat, value in self.flat.items():
            if hasattr(stats, stat):
                setattr(stats, stat, getattr(stats, stat) + value)
        for stat, value in self.increased.items():
            if hasattr(stats, stat):
                setattr(stats, stat, getattr(stats, stat) + value)
        for stat, value in self.more.items():
            if stat == "damage":
                stats.more_damage_multiplier *= value
        for stat, value in self.multipliers.items():
            if stat == "damage":
                stats.more_damage_multiplier *= value
            elif hasattr(stats, stat):
                setattr(stats, stat, getattr(stats, stat) * value)

    def to_dict(self) -> dict:
        """Serialise all buckets for debugging and deterministic validation."""
        return {
            "flat": dict(self.flat),
            "increased": dict(self.increased),
            "more": dict(self.more),
            "multipliers": dict(self.multipliers),
        }


def create_empty_stat_pool() -> StatPool:
    """Return a fresh, empty StatPool with all four buckets initialised.

    This is the canonical factory function for the plan's data layer.
    Callers should use this rather than constructing StatPool() directly
    so that future bucket additions are picked up automatically.
    """
    return StatPool()


# ---------------------------------------------------------------------------
# apply_affix — routes an affix value into the correct stat bucket
# ---------------------------------------------------------------------------

def apply_affix(pool: StatPool, affix_name: str, tier: int) -> None:
    """Apply a single affix at a given tier into the appropriate stat bucket.

    Modifier-type routing is inferred from the stat key convention because
    AFFIX_TYPES stores the slot type (prefix/suffix/idol), not the modifier type:

    - Stat keys ending in ``_pct``               → ``increased`` bucket
    - Stat keys starting with ``more_`` or equal to ``"more_damage_multiplier"``
                                                  → ``more`` bucket
    - Everything else                             → ``flat`` bucket
    """
    stat_key = AFFIX_STAT_KEYS.get(affix_name)
    if not stat_key:
        return
    value = get_affix_value(affix_name, tier)
    if not value:
        return
    if stat_key.endswith("_pct"):
        pool.add_increased(stat_key, value)
    elif stat_key.startswith("more_") or stat_key == "more_damage_multiplier":
        pool.add_more(stat_key, value)
    else:
        pool.add_flat(stat_key, value)


# ---------------------------------------------------------------------------
# Helper — add a partial stat dict to a BuildStats instance
# ---------------------------------------------------------------------------

def _add_partial(stats: BuildStats, partial: dict) -> None:
    for key, value in partial.items():
        if not hasattr(stats, key):
            continue
        if key.endswith("_pct"):
            setattr(stats, key, combine_additive_percents(getattr(stats, key), value))
        else:
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
        stats.attack_speed_pct = combine_additive_percents(stats.attack_speed_pct, value)
        stats.cast_speed += value
    elif hasattr(stats, stat_key):
        if stat_key.endswith("_pct"):
            setattr(stats, stat_key, combine_additive_percents(getattr(stats, stat_key), value))
        else:
            setattr(stats, stat_key, getattr(stats, stat_key) + value)


# ---------------------------------------------------------------------------
# Helper — passive node bonus (mirrors getNodeBonus in simulation.ts)
# ---------------------------------------------------------------------------

def _get_node_bonus(node_id: int, node_type: str, node_name: str, character_class: str = "") -> dict:
    if node_type == "mastery-gate":
        return {}
    if node_type == "keystone":
        return KEYSTONE_BONUSES.get(node_name, {"spell_damage_pct": 10, "max_health": 50})
    cycle = CLASS_STAT_CYCLES.get(character_class, CORE_STAT_CYCLE)
    stat_key, base_amount = cycle[node_id % len(cycle)]
    amount = base_amount * NOTABLE_MULTIPLIER if node_type == "notable" else base_amount
    return {stat_key: amount}


# ---------------------------------------------------------------------------
# Helper — affix tier midpoint value
# ---------------------------------------------------------------------------

# Stat keys whose affix tier values are stored at 100× game scale in the data
# files (sync_game_data.py multiplies raw floats by 100, which is correct for
# percentage-point stats but inflates flat stats by 100×).  Percentage stats
# (ending in _pct) are already at the correct scale after the ×100 conversion.
_FLAT_SCALE_STAT_KEYS: frozenset[str] = frozenset({
    "added_melee_physical", "added_melee_fire", "added_melee_cold",
    "added_melee_lightning", "added_melee_void", "added_melee_necrotic",
    "added_spell_damage", "added_spell_fire", "added_spell_cold",
    "added_spell_lightning", "added_spell_necrotic", "added_spell_void",
    "added_throw_physical", "added_throw_fire", "added_throw_cold",
    "added_bow_physical", "added_bow_fire",
    "max_health", "hybrid_health", "max_mana",
    "armour", "dodge_rating", "ward",
    "health_regen", "mana_regen", "ward_regen",
    "stun_avoidance", "block_effectiveness",
    "health_on_block", "health_on_kill", "ward_on_kill", "ward_on_potion",
    "strength", "intelligence", "dexterity", "vitality", "attunement",
    "thorns",
})


def get_affix_value(affix_name: str, tier: int) -> float:
    """Returns the midpoint stat value for an affix at the given tier (1=lowest, 7=best).

    Applies a /100 normalization for flat stat values that are stored at 100×
    scale in the data files (see sync_game_data.py tier conversion comment).
    Only applies to affixes whose stat_key is in _FLAT_SCALE_STAT_KEYS AND
    whose tier midpoint exceeds a threshold indicating ×100 inflation (> 100
    at T1 rules out percentage-scale stats that share the same stat_key).
    """
    tier_key = f"T{tier}"
    midpoints = AFFIX_TIER_MIDPOINTS.get(affix_name, {})
    raw = float(midpoints.get(tier_key, 0))
    if raw == 0:
        return 0.0
    stat_key = AFFIX_STAT_KEYS.get(affix_name, "")
    if stat_key in _FLAT_SCALE_STAT_KEYS:
        # Only correct if T1 midpoint indicates ×100 scale (>100).
        # Affixes like "Increased Armor" (T1=11) share stat_key "armour" but
        # are already at correct scale — don't divide those.
        t1_raw = float(midpoints.get("T1", 0))
        if t1_raw > 100:
            return raw / 100.0
    return raw


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
    blessing_stats: Optional[list[dict]] = None,  # output of resolve_blessing_stats()
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
        blessing_stats: resolved Monolith blessing effects from
            ``resolve_blessing_stats()`` — a list of
            ``{"stat_key", "value", "stat_type"}`` dicts.  Applied after the
            passive merge step.  Unknown stat keys are skipped silently.

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
    stats.attack_speed        = base["attack_speed"]
    stats.crit_chance         = base["crit_chance"]
    stats.crit_multiplier     = base["crit_multiplier"]
    stats.max_health          = base["health"]
    stats.max_mana            = base["mana"]
    stats.health_regen        = base["health_regen"]
    stats.mana_regen          = base["mana_regen"]
    stats.strength            = base["strength"]
    stats.intelligence        = base["intelligence"]
    stats.dexterity           = base["dexterity"]
    stats.vitality            = base["vitality"]
    stats.attunement          = base["attunement"]
    stats.stun_avoidance      = base["stun_avoidance"]
    stats.endurance           = base["endurance"]
    stats.endurance_threshold = base["endurance_threshold"]

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
        bonus = _get_node_bonus(node["id"], node_type, node_name, character_class)
        _add_partial(stats, bonus)

    # 4. Gear affix values — route through StatPool for proper type bucketing
    pool = StatPool()
    for affix in gear_affixes:
        # Format b: synthetic unique item stats injected by build_analysis_service
        if "stat_key" in affix:
            _apply_stat_key(stats, affix["stat_key"], float(affix.get("value", 0)))
            continue

        # Format a: normal gear affix by name + tier
        affix_name = affix.get("name", "")
        tier = int(affix.get("tier", 3))
        apply_affix(pool, affix_name, tier)
    pool.resolve_to(stats)

    # 5. Resolved passive tree stats (from passive_stat_resolver)
    if passive_stats:
        _add_partial(stats, passive_stats.get("additive", {}))

    # 5b. Monolith blessings — applied after passives, before attribute scaling
    for entry in (blessing_stats or []):
        stat_key = entry["stat_key"]
        value = entry["value"]
        if not hasattr(stats, stat_key):
            continue
        if entry.get("stat_type") == "increased" or stat_key.endswith("_pct"):
            setattr(
                stats,
                stat_key,
                combine_additive_percents(getattr(stats, stat_key), value),
            )
        else:
            setattr(stats, stat_key, getattr(stats, stat_key) + value)

    # 6. Attribute scaling
    # Direct per-point bonuses — verified from in-game tooltips and
    # level 1 character sheet data with no gear and no passives.
    # Note: attributes also scale specific skills at the skill level
    # (e.g. Strength scales Warpath) — that is handled in skill calc,
    # not here.
    stats.armour_pct          += stats.strength     * ATTRIBUTE_SCALING["strength"]["armour_pct"]
    stats.dodge_rating        += stats.dexterity    * ATTRIBUTE_SCALING["dexterity"]["dodge_rating"]
    stats.ward_retention_pct  += stats.intelligence * ATTRIBUTE_SCALING["intelligence"]["ward_retention_pct"]
    stats.max_health          += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["max_health"]
    stats.endurance_threshold += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["endurance_threshold"]
    stats.poison_res          += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["poison_res"]
    stats.necrotic_res        += stats.vitality     * ATTRIBUTE_SCALING["vitality"]["necrotic_res"]
    stats.max_mana            += stats.attunement   * ATTRIBUTE_SCALING["attunement"]["max_mana"]

    # 7. Apply percentage health bonuses
    stats.max_health = apply_percent_bonus(stats.max_health, stats.health_pct) + stats.hybrid_health

    # 8. Apply % bonuses to base values
    # VERIFIED: 1.4.3 spec §2.2 — stats.crit_chance_pct is the resolved
    # "increased" pool from affixes and passives (e.g. "+15% Increased Critical
    # Strike Chance"), applied multiplicatively on the base+flat crit chance.
    stats.crit_chance = effective_crit_chance(stats.crit_chance, increased_pct=stats.crit_chance_pct)
    stats.crit_multiplier = effective_crit_multiplier(stats.crit_multiplier, stats.crit_multiplier_pct)
    stats.attack_speed   = apply_percent_bonus(stats.attack_speed, stats.attack_speed_pct)

    log.info(
        "aggregate_stats.end",
        base_damage=stats.base_damage,
        max_health=stats.max_health,
        crit_chance=round(stats.crit_chance, 4),
    )

    return stats
