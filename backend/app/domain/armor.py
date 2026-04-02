"""
Armor & Mitigation System (Step 62).

Reduces physical damage based on armor values using the same formula
as Last Epoch:

    mitigation_pct = armor / (armor + K * raw_damage)
    effective_damage = raw_damage * (1 - mitigation_pct)

Where K is a scaling constant that controls how quickly armor loses
effectiveness against larger hits. The mitigation percentage is capped
at ARMOR_MITIGATION_CAP to prevent full physical immunity.

Constants:
    ARMOR_K = 10.0              — scaling constant (higher = armor less effective vs big hits)
    ARMOR_MITIGATION_CAP = 0.75 — maximum 75% reduction from armor alone

Only applies to physical damage. Non-physical damage types bypass armor
entirely and should instead use the resistance system (Step 61).

Public API:
    armor_mitigation_pct(armor, raw_damage) -> float
        Returns the mitigation fraction in [0, ARMOR_MITIGATION_CAP].

    apply_armor(raw_damage, armor) -> float
        Returns physical damage after armor mitigation.
"""

from __future__ import annotations

ARMOR_K: float = 10.0
ARMOR_MITIGATION_CAP: float = 0.75


def armor_mitigation_pct(armor: float, raw_damage: float) -> float:
    """
    Return the mitigation fraction (0.0–ARMOR_MITIGATION_CAP) for a hit.

        mitigation = armor / (armor + K * raw_damage)

    Special cases:
    - armor <= 0 → 0.0 (no mitigation)
    - raw_damage <= 0 → ARMOR_MITIGATION_CAP (full cap, damage is trivial)

    Raises ValueError if armor < 0.
    """
    if armor < 0:
        raise ValueError(f"armor must be >= 0, got {armor}")
    if armor == 0.0:
        return 0.0
    if raw_damage <= 0.0:
        return ARMOR_MITIGATION_CAP
    raw = armor / (armor + ARMOR_K * raw_damage)
    return min(raw, ARMOR_MITIGATION_CAP)


def apply_armor(raw_damage: float, armor: float) -> float:
    """
    Return physical damage after armor mitigation.

        effective = raw_damage * (1 - mitigation_pct)

    Raises ValueError if raw_damage < 0 or armor < 0.
    """
    if raw_damage < 0:
        raise ValueError(f"raw_damage must be >= 0, got {raw_damage}")
    mit = armor_mitigation_pct(armor, raw_damage)
    return raw_damage * (1.0 - mit)
