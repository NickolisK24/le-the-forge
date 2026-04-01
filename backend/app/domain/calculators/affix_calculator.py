"""
Affix Calculator — pure affix math with no side effects.

All functions accept plain inputs and return computed values.
No registry access. No Flask context. No I/O.
"""

from __future__ import annotations


def get_max_tier(affix: dict) -> int:
    """Return the highest tier number available for this affix."""
    tiers = affix.get("tiers", [])
    if not tiers:
        return 0
    return max(t["tier"] for t in tiers)
