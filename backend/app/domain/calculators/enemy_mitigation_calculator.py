"""
Enemy Mitigation Calculator — armor and resistance reduction formulas.

Inputs:  EnemyProfile (typed domain object), hit damage types, penetration stats.
Outputs: individual mitigation factors and the combined damage multiplier.

Formulas (Last Epoch):
  Armor mitigation = armor / (armor + 1000)   → fraction [0, 1)
  Effective res    = clamp(enemy_res − pen, 0, RES_CAP)  → pct [0, 75]

Two multiplier functions:
  damage_multiplier(enemy, type_set, pen_map)
      Simple average — use when damage proportions are unknown.
      Assumes every type in the set contributes equally.

  weighted_damage_multiplier(enemy, damage_by_type, pen_map)
      Proportion-weighted — use when DamageResult.damage_by_type is available.
      Applies each type's resistance only to the fraction of damage it represents.
      Correct for multi-type skills after conversion.

All functions are pure: no registry access, no Flask context, no I/O.
"""

from __future__ import annotations

from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyProfile

RES_CAP: float = 75.0  # Hard cap on effective resistance (%)


def armor_mitigation(armor: int) -> float:
    """
    Fraction of damage absorbed by armor.

    Returns a value in [0, 1). Zero or negative armor returns 0.0.
    """
    if armor <= 0:
        return 0.0
    return armor / (armor + 1000)


def effective_resistance(
    enemy: EnemyProfile,
    damage_type: str,
    penetration: float = 0.0,
) -> float:
    """
    Effective resistance percentage for one damage type after penetration and cap.

    Returns a value in [0, RES_CAP].
    Unknown damage types default to 0 resistance.
    """
    raw = float(enemy.resistances.get(damage_type, 0.0))
    return max(0.0, min(RES_CAP, raw - penetration))


def damage_multiplier(
    enemy: EnemyProfile,
    damage_types: set[str],
    pen_map: dict[str, float] | None = None,
) -> float:
    """
    Combined damage multiplier using equal-weight resistance averaging.

    Use this when the exact per-type damage proportions are not known.
    For more accurate results when DamageResult.damage_by_type is available,
    use weighted_damage_multiplier() instead.

    Returns a value in (0, 1].
    """
    pen = pen_map or {}
    armor_factor = 1.0 - armor_mitigation(enemy.armor)

    if not damage_types:
        return armor_factor

    res_values = [
        effective_resistance(enemy, dt, pen.get(dt, 0.0))
        for dt in damage_types
    ]
    avg_res = sum(res_values) / len(res_values)
    return armor_factor * (1.0 - avg_res / 100.0)


def weighted_damage_multiplier(
    enemy: EnemyProfile,
    damage_by_type: dict[DamageType, float],
    pen_map: dict[str, float] | None = None,
) -> float:
    """
    Proportion-weighted damage multiplier using actual per-type damage amounts.

    For each damage type, applies resistance only to that type's share of total
    damage, then sums the results. More accurate than simple averaging when
    damage is distributed unevenly across types (e.g. after conversion).

    Formula:
        armor_factor = 1 − armor_mitigation(enemy.armor)
        res_factor   = Σ (amount[dt] / total) × (1 − eff_res[dt] / 100)
        multiplier   = armor_factor × res_factor

    Falls back to armor-only if damage_by_type is empty or total is zero.
    Returns a value in (0, 1].
    """
    if not damage_by_type:
        return 1.0 - armor_mitigation(enemy.armor)

    total = sum(damage_by_type.values())
    if total <= 0:
        return 1.0 - armor_mitigation(enemy.armor)

    pen = pen_map or {}
    armor_factor = 1.0 - armor_mitigation(enemy.armor)

    res_factor = sum(
        (amount / total) * (1.0 - effective_resistance(enemy, dt.value, pen.get(dt.value, 0.0)) / 100.0)
        for dt, amount in damage_by_type.items()
    )
    return armor_factor * res_factor
