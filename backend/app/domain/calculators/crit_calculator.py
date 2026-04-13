"""
Crit Calculator — pure crit mechanics math.

Last Epoch crit formula:
  Crit% = (BaseCrit + FlatAdded) × (1 + IncreasedCrit%)
  Cap: 100%

All functions accept primitive values and return computed values.
No registry access. No Flask context. No I/O.
"""

from __future__ import annotations

from app.constants.combat import CRIT_CHANCE_CAP


def effective_crit_chance(
    base: float,
    flat_bonus_pct: float = 0.0,
    increased_pct: float = 0.0,
) -> float:
    """
    Final crit chance using the verified 1.4.3 two-part formula, capped at 100%.

    VERIFIED: 1.4.3 spec §2.2 — Crit% = (base + flat) × (1 + increased%).

    base:            base crit chance as a fraction in [0, 1] (e.g. 0.05 = 5%).
    flat_bonus_pct:  flat additive crit chance in percent-points
                     (e.g. 10.0 = +10% added to base → +0.10 before multiplier).
    increased_pct:   total increased critical strike chance from all sources
                     as percent-points (e.g. 100.0 = +100% increased → ×2).

    Result is floored at 0 and capped at CRIT_CHANCE_CAP.
    """
    raw = (base + flat_bonus_pct / 100.0) * (1.0 + increased_pct / 100.0)
    return max(0.0, min(CRIT_CHANCE_CAP, raw))


def effective_crit_multiplier(base: float, bonus_pct: float = 0.0) -> float:
    """
    Final crit multiplier: base multiplier + bonus percent-points converted.

    VERIFIED: 1.4.3 spec §2.2 — crit multiplier cannot drop below 1.0 (a
    "crit" that deals less than a normal hit is impossible); floor at 1.0.

    bonus_pct: percent-point bonus (e.g. 50.0 = +50% → adds 0.5 to multiplier).
    """
    return max(1.0, base + bonus_pct / 100.0)


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
    Percentage of average hit attributable to the *bonus* portion of crits —
    i.e. the extra damage dealt above a non-crit hit.

    VERIFIED: 1.4.3 spec §2.2 — crit contribution is the uplift above the
    non-crit baseline, computed as `crit_chance × hit × (multi − 1) / avg_hit`.

    Returns 0 if average_hit is 0 to avoid division by zero.
    """
    if average_hit == 0:
        return 0
    crit_bonus = crit_chance * hit_damage * (crit_multiplier - 1.0)
    return round(crit_bonus / average_hit * 100)
