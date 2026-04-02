"""
Resistance System (Step 61).

Applies percentage-based damage reduction per damage type. Each damage
type has an independent resistance value on the enemy. Resistance reduces
incoming damage by that percentage before it is applied to the enemy's
health pool.

Formula:
    effective_damage = raw_damage * (1 - clamped_resistance / 100)

Where clamped_resistance = clamp(resistance, RES_MIN, RES_CAP).

Constants:
    RES_CAP = 75.0  — maximum effective resistance (can be reduced by shred/penetration)
    RES_MIN = -100.0 — minimum resistance (negative = increased damage taken)

Public API:
    apply_resistance(raw_damage, resistance_pct) -> float
        Pure function; returns damage after resistance reduction.

    apply_resistance_map(damage_map, resistance_map) -> dict[DamageType, float]
        Applies per-type resistances to a full damage map.
"""

from __future__ import annotations

from app.domain.calculators.damage_type_router import DamageType


RES_CAP: float = 75.0     # maximum effective resistance percentage
RES_MIN: float = -100.0   # minimum resistance (negative = more damage taken)


def _clamp_resistance(resistance_pct: float) -> float:
    """Clamp resistance to the valid [RES_MIN, RES_CAP] range."""
    return max(RES_MIN, min(RES_CAP, resistance_pct))


def apply_resistance(raw_damage: float, resistance_pct: float) -> float:
    """
    Return damage after applying resistance reduction.

        effective = raw_damage * (1 - clamped_resistance / 100)

    Resistance is clamped to [RES_MIN, RES_CAP] before calculation.
    Negative resistance increases damage taken (vulnerability).
    Raises ValueError if raw_damage < 0.
    """
    if raw_damage < 0:
        raise ValueError(f"raw_damage must be >= 0, got {raw_damage}")
    clamped = _clamp_resistance(resistance_pct)
    return raw_damage * (1.0 - clamped / 100.0)


def apply_resistance_map(
    damage_map: dict[DamageType, float],
    resistance_map: dict[DamageType, float],
) -> dict[DamageType, float]:
    """
    Apply per-type resistances to a full damage map.

    Types present in damage_map but absent from resistance_map are treated
    as 0% resistance (no reduction). Returns a new dict; inputs not mutated.
    """
    result: dict[DamageType, float] = {}
    for dt, raw in damage_map.items():
        res = resistance_map.get(dt, 0.0)
        result[dt] = apply_resistance(raw, res)
    return result
