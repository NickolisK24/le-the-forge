"""
Affix Calculator — pure affix math with no side effects.

All functions accept typed domain objects and return computed values.
No registry access. No Flask context. No I/O.
"""

from __future__ import annotations
from typing import Optional

from app.domain.item import AffixDefinition, AffixTier


def get_max_tier(affix_def: AffixDefinition) -> int:
    """Return the highest tier number available for this affix."""
    if not affix_def.tiers:
        return 0
    return max(t.tier for t in affix_def.tiers)


def is_max_tier(affix_def: AffixDefinition, tier: int) -> bool:
    """Return True if tier is at or beyond the affix's maximum tier count."""
    return tier >= len(affix_def.tiers)


def get_affix_tier_data(affix_def: AffixDefinition, tier: int) -> Optional[AffixTier]:
    """
    Return the AffixTier for the given tier number (1-indexed).

    Returns None if tier is out of range.
    """
    for t in affix_def.tiers:
        if t.tier == tier:
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
