"""
Leech Mechanics (Step 73).

Life/mana leech restores resources proportional to damage dealt.
Leech is applied as a percentage of damage, capped at a maximum
per-hit value to prevent single-hit full restoration.

  calculate_leech(damage, leech_pct, max_leech=None) -> float
  apply_leech_to_pool(current, maximum, leech_amount) -> float
      Returns new resource value after leech (capped at maximum).
"""

from __future__ import annotations

LEECH_CAP_PCT: float = 10.0   # default max leech per hit as % of max resource


def calculate_leech(
    damage: float,
    leech_pct: float,
    max_per_hit: float | None = None,
) -> float:
    """
    Return the raw leech amount from a hit.

        leech = damage * clamp(leech_pct, 0, 100) / 100

    If max_per_hit is provided, the result is capped at that value.
    Raises ValueError if damage < 0.
    """
    if damage < 0:
        raise ValueError(f"damage must be >= 0, got {damage}")
    pct    = max(0.0, min(100.0, leech_pct))
    amount = damage * pct / 100.0
    if max_per_hit is not None:
        amount = min(amount, max(0.0, max_per_hit))
    return amount


def apply_leech_to_pool(current: float, maximum: float, leech_amount: float) -> float:
    """
    Add *leech_amount* to *current*, capped at *maximum*.

    Returns new resource value. Ignores negative leech_amount.
    Raises ValueError if current < 0, maximum <= 0, or current > maximum.
    """
    if maximum <= 0:
        raise ValueError(f"maximum must be > 0, got {maximum}")
    if current < 0:
        raise ValueError(f"current must be >= 0, got {current}")
    return min(maximum, current + max(0.0, leech_amount))
