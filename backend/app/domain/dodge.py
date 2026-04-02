"""
Dodge Mechanics (Step 78).

Dodge provides a chance to avoid incoming damage entirely (not just reduce it).
Unlike resistance, a successful dodge negates the full hit.

  dodge_chance(dodge_rating, level_penalty=0) -> float
      Returns dodge chance in [0, DODGE_CAP].

  DODGE_CAP = 0.75  — maximum 75% dodge chance
"""

from __future__ import annotations

DODGE_CAP: float = 0.75
_DODGE_RATING_SCALE: float = 2000.0  # rating needed to approach cap


def dodge_chance(dodge_rating: float, level_penalty: float = 0.0) -> float:
    """
    Return dodge chance in [0, DODGE_CAP].

        chance = dodge_rating / (dodge_rating + SCALE * (1 + level_penalty))

    level_penalty accounts for enemy level scaling (higher = harder to dodge).
    Raises ValueError if dodge_rating < 0.
    """
    if dodge_rating < 0:
        raise ValueError(f"dodge_rating must be >= 0, got {dodge_rating}")
    if dodge_rating == 0.0:
        return 0.0
    denom = dodge_rating + _DODGE_RATING_SCALE * (1.0 + max(0.0, level_penalty))
    raw   = dodge_rating / denom
    return min(DODGE_CAP, raw)


def roll_dodge(chance: float, rng_roll: float | None = None) -> bool:
    """Return True if the dodge succeeds (hit is avoided entirely)."""
    if rng_roll is None:
        rng_roll = 0.0
    return rng_roll < chance
