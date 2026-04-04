"""
Penetration & Resistance Shred (Step 64).

Two distinct mechanics that reduce effective enemy resistance:

  Penetration — bypasses resistance for the attacker's hits only; does NOT
                change the enemy's actual resistance stat. Applied per hit.
                  effective_res = enemy_res - penetration_pct

  Resistance Shred — permanently (for fight duration) reduces the enemy's
                resistance stat. Stacks additively up to a maximum shred.
                  new_enemy_res = enemy_res - total_shred

Both are applied before the resistance cap:
  final_res = clamp(enemy_res - shred - penetration, RES_MIN, RES_CAP)

Constants:
    MAX_SHRED_PER_TYPE = 100.0 — maximum total shred per resistance type

Public API:
    effective_resistance(enemy_res, penetration, shred) -> float
        Returns clamped effective resistance after both modifiers.

    apply_shred(current_shred, new_shred, max_shred=MAX_SHRED_PER_TYPE) -> float
        Accumulates shred additively up to max_shred.
"""

from __future__ import annotations

from app.domain.calculators.damage_type_router import DamageType
from app.domain.resistance import RES_CAP, RES_MIN

MAX_SHRED_PER_TYPE: float = 100.0


def effective_resistance(
    enemy_res: float,
    penetration: float = 0.0,
    shred: float = 0.0,
) -> float:
    """
    Return clamped effective resistance after penetration and shred.

        effective = clamp(enemy_res - shred - penetration, RES_MIN, RES_CAP)

    penetration and shred are both in percentage points (e.g. 20 = 20%).
    Negative values are ignored (clamped to 0).
    """
    total_reduction = max(0.0, penetration) + max(0.0, shred)
    raw = enemy_res - total_reduction
    return max(RES_MIN, min(RES_CAP, raw))


def apply_shred(
    current_shred: float,
    new_shred: float,
    max_shred: float = MAX_SHRED_PER_TYPE,
) -> float:
    """
    Return new cumulative shred after adding *new_shred* to *current_shred*.

    Capped at *max_shred*. Negative new_shred is ignored.
    Raises ValueError if current_shred < 0.
    """
    if current_shred < 0:
        raise ValueError(f"current_shred must be >= 0, got {current_shred}")
    return min(max_shred, current_shred + max(0.0, new_shred))


def apply_penetration_map(
    damage_map: dict[DamageType, float],
    resistance_map: dict[DamageType, float],
    penetration_map: dict[DamageType, float],
    shred_map: dict[DamageType, float] | None = None,
) -> dict[DamageType, float]:
    """
    Apply per-type penetration and shred to a damage map, then apply
    effective resistances. Returns a new damage map of post-resistance damage.

    Types absent from resistance_map default to 0 resistance.
    Types absent from penetration_map default to 0 penetration.
    Types absent from shred_map default to 0 shred.
    """
    from app.domain.resistance import apply_resistance

    if shred_map is None:
        shred_map = {}

    result: dict[DamageType, float] = {}
    for dt, raw in damage_map.items():
        res   = resistance_map.get(dt, 0.0)
        pen   = penetration_map.get(dt, 0.0)
        shred = shred_map.get(dt, 0.0)
        eff_res = effective_resistance(res, pen, shred)
        result[dt] = apply_resistance(raw, eff_res)
    return result
