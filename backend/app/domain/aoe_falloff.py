"""
Area Damage Falloff (Step 76).

Damage dealt to targets outside the primary AoE radius is reduced by
a falloff curve. Targets within the inner radius take full damage;
targets beyond the outer radius take minimum damage.

  linear_falloff(distance, inner_radius, outer_radius, min_pct) -> float
      Returns the damage multiplier [min_pct/100, 1.0] for a given distance.

  apply_aoe_damage(base_damage, distance, inner_radius, outer_radius, min_pct) -> float
"""

from __future__ import annotations


def linear_falloff(
    distance: float,
    inner_radius: float,
    outer_radius: float,
    min_pct: float = 0.0,
) -> float:
    """
    Return damage multiplier based on linear falloff between radii.

    - distance <= inner_radius  → 1.0 (full damage)
    - distance >= outer_radius  → min_pct / 100
    - between radii             → linear interpolation

    Raises ValueError if inner_radius < 0, outer_radius <= inner_radius,
    distance < 0, or min_pct not in [0, 100].
    """
    if inner_radius < 0:
        raise ValueError(f"inner_radius must be >= 0, got {inner_radius}")
    if outer_radius <= inner_radius:
        raise ValueError(f"outer_radius must be > inner_radius, got {outer_radius} <= {inner_radius}")
    if distance < 0:
        raise ValueError(f"distance must be >= 0, got {distance}")
    if not (0.0 <= min_pct <= 100.0):
        raise ValueError(f"min_pct must be in [0, 100], got {min_pct}")

    if distance <= inner_radius:
        return 1.0
    if distance >= outer_radius:
        return min_pct / 100.0

    # Linear interpolation from 1.0 at inner to min_pct/100 at outer
    t = (distance - inner_radius) / (outer_radius - inner_radius)
    return 1.0 - t * (1.0 - min_pct / 100.0)


def apply_aoe_damage(
    base_damage: float,
    distance: float,
    inner_radius: float,
    outer_radius: float,
    min_pct: float = 0.0,
) -> float:
    """Return base_damage scaled by the falloff multiplier at *distance*."""
    if base_damage < 0:
        raise ValueError(f"base_damage must be >= 0, got {base_damage}")
    multiplier = linear_falloff(distance, inner_radius, outer_radius, min_pct)
    return base_damage * multiplier
