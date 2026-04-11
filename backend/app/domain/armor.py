"""
Armor & Mitigation System.

Reduces damage based on armor values using the Last Epoch formula:

    mitigation_pct = armor / (armor + 10 × area_level)

The mitigation percentage is capped at ARMOR_MITIGATION_CAP (85% for physical).
Non-physical damage types use armor at 75% effectiveness, giving an
effective cap of ~63.75%.

Constants:
    ARMOR_AREA_LEVEL_FACTOR = 10.0
    ARMOR_MITIGATION_CAP = 0.85  — maximum 85% reduction for physical
    ARMOR_NON_PHYSICAL_EFFECTIVENESS = 0.75

Armor mitigates HITS only, not DoTs (exception: "Armor mitigates DoT" affix).

Public API:
    armor_mitigation_pct(armor, area_level, physical=True) -> float
    apply_armor(raw_damage, armor, area_level, physical=True) -> float
"""

from __future__ import annotations

from app.constants.defense import (
    ARMOR_AREA_LEVEL_FACTOR,
    ARMOR_MITIGATION_CAP,
    ARMOR_NON_PHYSICAL_EFFECTIVENESS,
    DEFAULT_AREA_LEVEL,
)

# Re-export for backward compatibility with derived_stats.py
ARMOR_K: float = ARMOR_AREA_LEVEL_FACTOR


def armor_mitigation_pct(
    armor: float,
    area_level: int = DEFAULT_AREA_LEVEL,
    *,
    physical: bool = True,
) -> float:
    """
    Return the mitigation fraction for a hit.

        mitigation = armor / (armor + 10 × area_level)

    For non-physical damage, armor is 75% as effective.
    Cap: 85% for physical, ~63.75% for non-physical.

    Raises ValueError if armor < 0.
    """
    if armor < 0:
        raise ValueError(f"armor must be >= 0, got {armor}")
    if armor == 0.0:
        return 0.0
    if area_level <= 0:
        return min(ARMOR_MITIGATION_CAP, 1.0)

    effective_armor = armor if physical else armor * ARMOR_NON_PHYSICAL_EFFECTIVENESS
    cap = ARMOR_MITIGATION_CAP if physical else ARMOR_MITIGATION_CAP * ARMOR_NON_PHYSICAL_EFFECTIVENESS
    raw = effective_armor / (effective_armor + ARMOR_AREA_LEVEL_FACTOR * area_level)
    return min(raw, cap)


def apply_armor(
    raw_damage: float,
    armor: float,
    area_level: int = DEFAULT_AREA_LEVEL,
    *,
    physical: bool = True,
) -> float:
    """
    Return damage after armor mitigation.

        effective = raw_damage × (1 - mitigation_pct)

    Raises ValueError if raw_damage < 0 or armor < 0.
    """
    if raw_damage < 0:
        raise ValueError(f"raw_damage must be >= 0, got {raw_damage}")
    mit = armor_mitigation_pct(armor, area_level, physical=physical)
    return raw_damage * (1.0 - mit)
