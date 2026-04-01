"""
Affix Calculator — pure affix math with no side effects.

All functions accept plain inputs and return computed values.
No registry access. No Flask context. No I/O.
"""

from __future__ import annotations
from typing import Optional

from app.domain.item import AffixDefinition


def get_max_tier(affix: dict) -> int:
    """Return the highest tier number available for this affix."""
    tiers = affix.get("tiers", [])
    if not tiers:
        return 0
    return max(t["tier"] for t in tiers)


def is_max_tier(affix: dict, tier: int) -> bool:
    """Return True if tier is at or beyond the affix's maximum tier count."""
    max_tier = len(affix["tiers"])
    return tier >= max_tier


def get_affix_tier_data(affix: dict, tier: int) -> Optional[dict]:
    """
    Return the tier data dict for the given tier number (1-indexed).

    Returns None if tier is out of range.
    """
    for t in affix.get("tiers", []):
        if t["tier"] == tier:
            return t
    return None


def calculate_affix_midpoint(affix_def: AffixDefinition, tier: int) -> float:
    """
    Return the midpoint value for the given tier on a typed AffixDefinition.

    Raises ValueError if the tier is not found.
    """
    for t in affix_def.tiers:
        if t.tier == tier:
            return t.midpoint
    raise ValueError(f"Tier {tier} not found on affix {affix_def.name!r}")
