"""
Enemy Mitigation Calculator — armor and resistance reduction formulas.

Inputs:  EnemyProfile (typed domain object), hit damage types, penetration stats.
Outputs: individual mitigation factors and the combined damage multiplier.

Formulas (Last Epoch):
  Armor mitigation = armor / (armor + 10 × area_level)
    - Cap: 85% for physical, ~63.75% for non-physical (75% effectiveness)
  Effective res    = max(0, min(enemy_res, RES_CAP) − pen)  → pct [0, 75]
                   Cap applies to BASE resistance first; pen subtracts after.

Two multiplier functions:
  damage_multiplier(enemy, type_set, pen_map, area_level)
      Simple average — use when damage proportions are unknown.

  weighted_damage_multiplier(enemy, damage_by_type, pen_map, area_level)
      Proportion-weighted — use when DamageResult.damage_by_type is available.

All functions are pure: no registry access, no Flask context, no I/O.
"""

from __future__ import annotations

from app.constants.defense import (
    ARMOR_AREA_LEVEL_FACTOR,
    ARMOR_MITIGATION_CAP,
    ARMOR_NON_PHYSICAL_EFFECTIVENESS,
    DEFAULT_AREA_LEVEL,
)
from app.domain.calculators.damage_type_router import DamageType
from app.domain.enemy import EnemyProfile

RES_CAP: float = 75.0  # Hard cap on effective resistance (%)


def armor_mitigation(armor: int, area_level: int = DEFAULT_AREA_LEVEL, *, physical: bool = True) -> float:
    """
    Fraction of damage absorbed by armor.

    Formula: armor / (armor + 10 × area_level)
    Physical cap: 85%. Non-physical: armor at 75% effectiveness (cap ~63.75%).

    Returns a value in [0, cap). Zero or negative armor returns 0.0.
    """
    if armor <= 0:
        return 0.0
    if area_level <= 0:
        return ARMOR_MITIGATION_CAP if physical else ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS

    effective_armor = float(armor) if physical else float(armor) * ARMOR_NON_PHYSICAL_EFFECTIVENESS
    cap = ARMOR_MITIGATION_CAP if physical else ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS
    raw = effective_armor / (effective_armor + ARMOR_AREA_LEVEL_FACTOR * area_level)
    return min(raw, cap)


def apply_armor(damage: float, armor: int, area_level: int = DEFAULT_AREA_LEVEL, *, physical: bool = True) -> float:
    """
    Apply armor mitigation to a raw damage value.

    Returns the portion of damage that passes through after armor reduction.
    """
    return damage * (1.0 - armor_mitigation(armor, area_level, physical=physical))


def apply_penetration(capped_resistance: float, penetration: float) -> float:
    """
    Subtract penetration from an already-capped resistance value.

    Penetration reduces effective resistance but cannot push it below 0.
    """
    return max(0.0, capped_resistance - penetration)


def effective_resistance(
    enemy: EnemyProfile,
    damage_type: str,
    penetration: float = 0.0,
) -> float:
    """
    Effective resistance percentage for one damage type after cap and penetration.

    Order of operations:
      1. Cap to RES_CAP.
      2. Subtract penetration, floor at 0.
    """
    raw = float(enemy.resistances.get(damage_type, 0.0))
    capped = min(RES_CAP, raw)
    return apply_penetration(capped, penetration)


def damage_multiplier(
    enemy: EnemyProfile,
    damage_types: set[str],
    pen_map: dict[str, float] | None = None,
    area_level: int = DEFAULT_AREA_LEVEL,
) -> float:
    """
    Combined damage multiplier using equal-weight resistance averaging.

    Returns a value in (0, 1].
    """
    pen = pen_map or {}

    if not damage_types:
        return 1.0 - armor_mitigation(enemy.armor, area_level)  # physical by default

    # Determine if any type is physical for armor effectiveness
    has_physical = "physical" in damage_types
    armor_factor = 1.0 - armor_mitigation(enemy.armor, area_level, physical=has_physical)

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
    area_level: int = DEFAULT_AREA_LEVEL,
) -> float:
    """
    Proportion-weighted damage multiplier using actual per-type damage amounts.

    For each damage type, applies resistance only to that type's share of total
    damage, then sums the results.

    Falls back to armor-only if damage_by_type is empty or total is zero.
    Returns a value in (0, 1].
    """
    if not damage_by_type:
        return 1.0 - armor_mitigation(enemy.armor, area_level)

    total = sum(damage_by_type.values())
    if total <= 0:
        return 1.0 - armor_mitigation(enemy.armor, area_level)

    pen = pen_map or {}
    # Physical types get full armor, non-physical get 75% effectiveness
    has_physical = any(dt.value == "physical" for dt in damage_by_type)
    armor_factor = 1.0 - armor_mitigation(enemy.armor, area_level, physical=has_physical)

    res_factor = sum(
        (amount / total) * (1.0 - effective_resistance(enemy, dt.value, pen.get(dt.value, 0.0)) / 100.0)
        for dt, amount in damage_by_type.items()
    )
    return armor_factor * res_factor
