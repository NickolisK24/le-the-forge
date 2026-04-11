"""
Dodge Mechanics.

Dodge provides a chance to avoid incoming damage entirely (not just reduce it).
Unlike resistance, a successful dodge negates the full hit.
DoTs CANNOT be dodged.

Formula: Dodge% = DodgeRating / (DodgeRating + 10 × AreaLevel)

  dodge_chance(dodge_rating, area_level=100) -> float
      Returns dodge chance in [0, DODGE_CAP].

  DODGE_CAP = 0.85  — maximum 85% dodge chance

Dexterity grants 4 Dodge Rating per point (handled by stat engine).
"""

from __future__ import annotations

from app.constants.defense import (
    DODGE_AREA_LEVEL_FACTOR,
    DODGE_CAP as _DODGE_CAP_CONST,
    DEFAULT_AREA_LEVEL,
)

DODGE_CAP: float = _DODGE_CAP_CONST


def dodge_chance(dodge_rating: float, area_level: int = DEFAULT_AREA_LEVEL) -> float:
    """
    Return dodge chance in [0, DODGE_CAP].

        chance = dodge_rating / (dodge_rating + 10 × area_level)

    Raises ValueError if dodge_rating < 0.
    """
    if dodge_rating < 0:
        raise ValueError(f"dodge_rating must be >= 0, got {dodge_rating}")
    if dodge_rating == 0.0:
        return 0.0
    if area_level <= 0:
        return min(DODGE_CAP, 1.0)
    denom = dodge_rating + DODGE_AREA_LEVEL_FACTOR * area_level
    raw = dodge_rating / denom
    return min(DODGE_CAP, raw)


def roll_dodge(chance: float, rng_roll: float | None = None) -> bool:
    """Return True if the dodge succeeds (hit is avoided entirely)."""
    if rng_roll is None:
        rng_roll = 0.0
    return rng_roll < chance
