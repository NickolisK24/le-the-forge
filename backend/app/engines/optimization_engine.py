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


# Candidate increments — mirrors STAT_TEST_INCREMENTS in simulation.ts
STAT_TEST_INCREMENTS: list = [
    {"key": "crit_multiplier_pct", "label": "+40% Crit Multiplier",       "delta": 40},
    {"key": "crit_chance_pct",     "label": "+7% Crit Chance",            "delta": 7},
    {"key": "attack_speed_pct",    "label": "+10% Attack Speed",          "delta": 10},
    {"key": "spell_damage_pct",    "label": "+40% Spell Damage",          "delta": 40},
    {"key": "physical_damage_pct", "label": "+40% Physical Damage",       "delta": 40},
    {"key": "fire_damage_pct",     "label": "+40% Fire Damage",           "delta": 40},
    {"key": "cold_damage_pct",     "label": "+40% Cold Damage",           "delta": 40},
    {"key": "lightning_damage_pct","label": "+40% Lightning Damage",      "delta": 40},
    {"key": "necrotic_damage_pct", "label": "+40% Necrotic Damage",       "delta": 40},
    {"key": "cast_speed",          "label": "+10% Cast Speed",            "delta": 10},
    {"key": "max_health",          "label": "+300 Health",                "delta": 300},
    {"key": "armour",              "label": "+200 Armour",                "delta": 200},
    {"key": "fire_res",            "label": "+20% Fire Resistance",       "delta": 20},
    {"key": "cold_res",            "label": "+20% Cold Resistance",       "delta": 20},
    {"key": "lightning_res",       "label": "+20% Lightning Resistance",  "delta": 20},
    {"key": "void_res",            "label": "+20% Void Resistance",       "delta": 20},
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
