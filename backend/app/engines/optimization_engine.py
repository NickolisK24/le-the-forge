"""
Optimization Engine — identifies which stat upgrades provide the largest gains.

Mirrors the logic in frontend/src/lib/simulation.ts:getStatUpgrades().

Workflow:
  1. Compute baseline DPS and EHP from current stats.
  2. For each candidate stat increment, apply the delta and recompute.
  3. Rank by DPS gain %. Include EHP gain % for defensive context.

Pure module — no DB, no HTTP.
"""

from dataclasses import dataclass, asdict

from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_defense


@dataclass
class StatUpgrade:
    stat: str
    label: str
    dps_gain_pct: float
    ehp_gain_pct: float

    def to_dict(self) -> dict:
        return asdict(self)


# Candidate increments — comprehensive stat testing
STAT_TEST_INCREMENTS: list = [
    # Offense — damage %
    {"key": "crit_multiplier_pct", "label": "+40% Crit Multiplier",       "delta": 40},
    {"key": "crit_chance_pct",     "label": "+7% Crit Chance",            "delta": 7},
    {"key": "attack_speed_pct",    "label": "+10% Attack Speed",          "delta": 10},
    {"key": "spell_damage_pct",    "label": "+40% Spell Damage",          "delta": 40},
    {"key": "physical_damage_pct", "label": "+40% Physical Damage",       "delta": 40},
    {"key": "fire_damage_pct",     "label": "+40% Fire Damage",           "delta": 40},
    {"key": "cold_damage_pct",     "label": "+40% Cold Damage",           "delta": 40},
    {"key": "lightning_damage_pct","label": "+40% Lightning Damage",      "delta": 40},
    {"key": "necrotic_damage_pct", "label": "+40% Necrotic Damage",       "delta": 40},
    {"key": "void_damage_pct",     "label": "+40% Void Damage",           "delta": 40},
    {"key": "poison_damage_pct",   "label": "+40% Poison Damage",         "delta": 40},
    {"key": "cast_speed",          "label": "+10% Cast Speed",            "delta": 10},
    {"key": "melee_damage_pct",    "label": "+40% Melee Damage",          "delta": 40},
    {"key": "throwing_damage_pct", "label": "+40% Throwing Damage",       "delta": 40},
    {"key": "bow_damage_pct",      "label": "+40% Bow Damage",            "delta": 40},
    {"key": "elemental_damage_pct","label": "+40% Elemental Damage",      "delta": 40},
    {"key": "dot_damage_pct",      "label": "+40% DoT Damage",            "delta": 40},
    {"key": "minion_damage_pct",   "label": "+40% Minion Damage",         "delta": 40},
    # Offense — flat added damage
    {"key": "added_spell_damage",  "label": "+15 Flat Spell Damage",      "delta": 15},
    {"key": "added_melee_physical","label": "+18 Flat Melee Physical",    "delta": 18},
    # Offense — ailments
    {"key": "bleed_chance_pct",    "label": "+30% Bleed Chance",          "delta": 30},
    {"key": "ignite_chance_pct",   "label": "+30% Ignite Chance",         "delta": 30},
    {"key": "poison_chance_pct",   "label": "+30% Poison Chance",         "delta": 30},
    {"key": "bleed_damage_pct",    "label": "+40% Bleed Damage",          "delta": 40},
    {"key": "ignite_damage_pct",   "label": "+40% Ignite Damage",         "delta": 40},
    # Defense — health / armour
    {"key": "max_health",          "label": "+300 Health",                "delta": 300},
    {"key": "armour",              "label": "+200 Armour",                "delta": 200},
    {"key": "dodge_rating",        "label": "+150 Dodge Rating",          "delta": 150},
    {"key": "block_chance",        "label": "+20% Block Chance",          "delta": 20},
    {"key": "block_effectiveness", "label": "+200 Block Effectiveness",   "delta": 200},
    {"key": "endurance",           "label": "+20% Endurance",             "delta": 20},
    {"key": "crit_avoidance",      "label": "+40% Crit Avoidance",        "delta": 40},
    {"key": "glancing_blow",       "label": "+20% Glancing Blow",         "delta": 20},
    # Defense — resistances
    {"key": "fire_res",            "label": "+20% Fire Resistance",       "delta": 20},
    {"key": "cold_res",            "label": "+20% Cold Resistance",       "delta": 20},
    {"key": "lightning_res",       "label": "+20% Lightning Resistance",  "delta": 20},
    {"key": "void_res",            "label": "+20% Void Resistance",       "delta": 20},
    {"key": "necrotic_res",        "label": "+20% Necrotic Resistance",   "delta": 20},
    {"key": "physical_res",        "label": "+10% Physical Resistance",   "delta": 10},
    # Sustain
    {"key": "leech",               "label": "+5% Leech",                  "delta": 5},
    {"key": "health_regen",        "label": "+15 Health Regen",           "delta": 15},
]


def get_stat_upgrades(
    stats: BuildStats,
    primary_skill: str,
    skill_level: int = 20,
    top_n: int = 5,
) -> list[StatUpgrade]:
    """
    Test each stat increment and rank by DPS gain.

    Args:
        stats: current aggregated BuildStats
        primary_skill: the skill to use as DPS reference (e.g. "Fireball")
        skill_level: the level of that skill
        top_n: how many top upgrades to return

    Returns:
        List of StatUpgrade sorted by dps_gain_pct descending, length top_n.
    """
    base_dps = calculate_dps(stats, primary_skill, skill_level).dps
    base_ehp = calculate_defense(stats).effective_hp

    results = []

    for increment in STAT_TEST_INCREMENTS:
        key = increment["key"]
        delta = increment["delta"]
        label = increment["label"]

        # Clone stats and apply delta
        from copy import copy as _copy
        modified = _copy(stats)
        current_val = getattr(modified, key, 0.0)
        setattr(modified, key, current_val + delta)

        # Re-derive dependent stats for crit
        if key == "crit_chance_pct":
            base_crit = stats.crit_chance - stats.crit_chance_pct / 100
            modified.crit_chance = min(0.95, base_crit + modified.crit_chance_pct / 100)
        elif key == "crit_multiplier_pct":
            base_mult = stats.crit_multiplier - stats.crit_multiplier_pct / 100
            modified.crit_multiplier = base_mult + modified.crit_multiplier_pct / 100

        new_dps = calculate_dps(modified, primary_skill, skill_level).dps
        new_ehp = calculate_defense(modified).effective_hp

        dps_gain = ((new_dps - base_dps) / base_dps * 100) if base_dps > 0 else 0.0
        ehp_gain = ((new_ehp - base_ehp) / base_ehp * 100) if base_ehp > 0 else 0.0

        results.append(StatUpgrade(
            stat=key,
            label=label,
            dps_gain_pct=round(dps_gain * 10) / 10,
            ehp_gain_pct=round(ehp_gain * 10) / 10,
        ))

    # Sort by DPS gain descending, return top N
    results.sort(key=lambda r: r.dps_gain_pct, reverse=True)
    return results[:top_n]
