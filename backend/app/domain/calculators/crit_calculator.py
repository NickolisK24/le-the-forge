"""
Crit Calculator — pure crit mechanics math.

All functions accept primitive values and return computed values.
No registry access. No Flask context. No I/O.
"""

from __future__ import annotations

from app.constants.combat import CRIT_CHANCE_CAP


def effective_crit_chance(base: float, bonus_pct: float = 0.0) -> float:
    """
    Final crit chance: base + bonus percent-points converted to 0-1, capped.

    bonus_pct: percent-point bonus (e.g. 5.0 = +5% crit chance → +0.05).
    """
    return min(CRIT_CHANCE_CAP, base + bonus_pct / 100)


def effective_crit_multiplier(base: float, bonus_pct: float = 0.0) -> float:
    """
    Final crit multiplier: base multiplier + bonus percent-points converted.

    bonus_pct: percent-point bonus (e.g. 50.0 = +50% → adds 0.5 to multiplier).
    """
    return base + bonus_pct / 100


def calculate_average_hit(hit_damage: float, crit_chance: float, crit_multiplier: float) -> float:
    """
    Expected average hit weighted by crit probability.

    AverageHit = (1 − CritChance) × HitDamage + CritChance × HitDamage × CritMultiplier
    """
    return (1 - crit_chance) * hit_damage + crit_chance * hit_damage * crit_multiplier


def crit_contribution_pct(
    hit_damage: float,
    crit_chance: float,
    crit_multiplier: float,
    average_hit: float,
) -> int:
    """
    Percentage of average hit that comes from crits.

    Returns 0 if average_hit is 0 to avoid division by zero.
    """
    if average_hit == 0:
        return 0
    crit_hit = crit_chance * hit_damage * crit_multiplier
    return round(crit_hit / average_hit * 100)
