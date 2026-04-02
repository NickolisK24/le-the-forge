"""
Enemy Mitigation Calculator — armor and resistance reduction formulas.

Inputs:  EnemyProfile (typed domain object), hit damage types, penetration stats.
Outputs: individual mitigation factors and the combined damage multiplier.

Formulas (Last Epoch):
  Armor mitigation = armor / (armor + 1000)   → fraction [0, 1)
  Effective res    = clamp(enemy_res − pen, 0, RES_CAP)  → pct [0, 75]
  Hit multiplier   = (1 − armor_mitigation) × (1 − avg_effective_res / 100)

All functions are pure: no registry access, no Flask context, no I/O.
"""

from __future__ import annotations

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
    Combined effective damage multiplier after armor and average resistance.

    Resistance is averaged across all damage types the hit deals.
    Penetration is applied per-type via pen_map (damage_type_str → pen_value).

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
