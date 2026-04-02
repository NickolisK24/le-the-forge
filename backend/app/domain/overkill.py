"""
Damage Overkill Handling (Step 74).

When a hit exceeds an enemy's remaining health, the excess damage is
"overkill". Some mechanics scale with overkill (e.g. overkill damage
bonuses, explode on death). This module computes overkill amounts and
applies overkill damage bonuses.

  overkill_amount(damage, current_health) -> float
  apply_overkill_bonus(base_damage, overkill_pct, overkill_amount) -> float
      Returns additional bonus damage based on overkill.
"""

from __future__ import annotations


def overkill_amount(damage: float, current_health: float) -> float:
    """
    Return the overkill (excess damage beyond current health).

        overkill = max(0, damage - current_health)

    Raises ValueError if damage < 0 or current_health < 0.
    """
    if damage < 0:
        raise ValueError(f"damage must be >= 0, got {damage}")
    if current_health < 0:
        raise ValueError(f"current_health must be >= 0, got {current_health}")
    return max(0.0, damage - current_health)


def apply_overkill_bonus(
    base_damage: float,
    overkill_pct: float,
    overkill: float,
) -> float:
    """
    Return bonus damage scaled from the overkill amount.

        bonus = overkill * clamp(overkill_pct, 0, 100) / 100

    base_damage is returned unchanged; caller adds the bonus on top.
    Raises ValueError if base_damage < 0 or overkill < 0.
    """
    if base_damage < 0:
        raise ValueError(f"base_damage must be >= 0, got {base_damage}")
    if overkill < 0:
        raise ValueError(f"overkill must be >= 0, got {overkill}")
    pct   = max(0.0, min(100.0, overkill_pct))
    bonus = overkill * pct / 100.0
    return base_damage + bonus
