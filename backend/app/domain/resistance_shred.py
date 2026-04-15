"""
Resistance Shred Mechanics (Step 5).

Resistance shred is a debuff applied to an enemy that permanently reduces
their resistance for the duration of the shred effect. Unlike penetration
(which is per-hit and floors at 0), shred modifies the enemy's effective
resistance directly and CAN push it negative — resulting in a vulnerability
multiplier (the enemy takes more damage).

Public API:
  apply_resistance_shred(resistances, shred_map) -> dict[str, float]
      Returns a new resistance dict with shred subtracted per type.
      Values below -RES_CAP are clamped at -RES_CAP (prevents infinite
      vulnerability; game convention: max vulnerability mirrors max resistance).

  shred_damage_multiplier(base_resistance, shred) -> float
      Returns the damage multiplier for a single type after shred is applied.
      Values above 1.0 mean the target is vulnerable.

  effective_shredded_resistance(resistances, shred_map, damage_type) -> float
      Convenience: resolve one damage type's effective resistance after shred.
"""

from __future__ import annotations

from app.constants.defense import RES_CAP

# VERIFIED: 1.4.3 spec §4.3 — resistance shred per-stack values
# Each stack of resistance shred reduces enemy resistance by 5% (2% vs bosses).
# Stacks persist for 4 seconds; max 10 stacks per element against a single target.
SHRED_PER_STACK: float = 5.0            # percentage points per shred stack
SHRED_PER_STACK_BOSS: float = 2.0       # percentage points per shred stack vs bosses
MAX_STACKS_PER_TYPE: int = 10           # maximum concurrent stacks per damage type
STACK_DURATION: float = 4.0             # seconds before a stack expires


# ---------------------------------------------------------------------------
# Core shred function
# ---------------------------------------------------------------------------

def apply_resistance_shred(
    resistances: dict[str, float],
    shred_map: dict[str, float],
) -> dict[str, float]:
    """
    Return a new resistance dict with shred values subtracted per type.

    For types present in shred_map:
        effective = max(-RES_CAP, resistance - shred)

    Types absent from shred_map are returned unchanged.
    Types present in shred_map but absent from resistances start at 0.0.
    The result can include negative values (vulnerability).
    """
    result = dict(resistances)
    for damage_type, shred_amount in shred_map.items():
        base = result.get(damage_type, 0.0)
        shredded = base - shred_amount
        # Clamp at -RES_CAP — mirrors the positive RES_CAP hard cap
        result[damage_type] = max(-float(RES_CAP), shredded)
    return result


# ---------------------------------------------------------------------------
# Single-type helpers
# ---------------------------------------------------------------------------

def shred_damage_multiplier(base_resistance: float, shred: float) -> float:
    """
    Damage multiplier for a single damage type after shred is applied.

    ``base_resistance`` — raw (pre-cap) resistance, e.g. 50.0 for 50%
    ``shred``           — flat reduction from shred debuffs, e.g. 30.0

    Effective resistance after shred:
        eff = max(-RES_CAP, base_resistance - shred)

    Damage multiplier:
        multiplier = 1.0 - eff / 100.0

    Examples:
        50% resistance, 30 shred  →  eff=20   →  multiplier=0.80  (20% absorbed)
        25% resistance, 50 shred  →  eff=-25  →  multiplier=1.25  (25% vulnerable)
        0%  resistance, 100 shred →  eff=-75  →  multiplier=1.75  (capped vulnerability)
    """
    eff = max(-float(RES_CAP), base_resistance - shred)
    return 1.0 - eff / 100.0


def effective_shredded_resistance(
    resistances: dict[str, float],
    shred_map: dict[str, float],
    damage_type: str,
) -> float:
    """
    Effective resistance for one damage type after shred is applied.

    Combines apply_resistance_shred and look-up in one call.
    Returns the clamped effective value in [-RES_CAP, max_raw].
    Note: does NOT apply the positive RES_CAP — shred operates on base
    resistance without first capping it (shred is applied before the cap).
    """
    shredded = apply_resistance_shred(resistances, shred_map)
    return shredded.get(damage_type, 0.0)
