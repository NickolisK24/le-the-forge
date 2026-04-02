"""
Damage Reflection System (Step 71).

When an enemy hits the player, a percentage of that damage is reflected
back to the attacker. Reflected damage bypasses the reflector's own
defenses but may be reduced by the attacker's own resistances.

  reflect_damage(incoming, reflect_pct) -> float
      Returns the flat amount reflected back.

  REFLECT_CAP = 100.0   — maximum reflection percentage
"""

from __future__ import annotations

REFLECT_CAP: float = 100.0


def reflect_damage(incoming: float, reflect_pct: float) -> float:
    """
    Return the amount of damage reflected to the attacker.

        reflected = incoming * clamp(reflect_pct, 0, REFLECT_CAP) / 100

    Raises ValueError if incoming < 0.
    """
    if incoming < 0:
        raise ValueError(f"incoming must be >= 0, got {incoming}")
    clamped = max(0.0, min(REFLECT_CAP, reflect_pct))
    return incoming * clamped / 100.0


def apply_reflection(
    incoming: float,
    reflect_pct: float,
    attacker_resistance: float = 0.0,
) -> tuple[float, float]:
    """
    Compute damage taken by the defender and reflected back to the attacker.

    attacker_resistance reduces the reflected amount before it hits the attacker.
    Returns (damage_taken_by_defender, damage_taken_by_attacker).

    The defender still takes the full *incoming* amount; reflection is
    additional damage to the attacker, not a reduction for the defender.
    """
    from app.domain.resistance import apply_resistance
    raw_reflected = reflect_damage(incoming, reflect_pct)
    attacker_damage = apply_resistance(raw_reflected, attacker_resistance)
    return incoming, attacker_damage
