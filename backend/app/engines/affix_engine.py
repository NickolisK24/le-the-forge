"""
Affix Engine — centralized affix management.

Responsibilities:
  - Load affixes.json (single source of truth)
  - Filter affixes by item type and prefix/suffix
  - Validate prefix/suffix slot limits
  - Provide tier data access
  - Validate affix compatibility with item type

Does NOT: craft items, calculate stats, modify FP, or run combat.

Note: affixes.json uses 'applicable_to' for item type filtering and
      'id' as the canonical identifier alongside 'name'.
"""

import json
import os
from typing import Optional

from app.constants.crafting import MAX_PREFIXES, MAX_SUFFIXES
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AFFIX_PATH = os.path.join(BASE_DIR, "..", "..", "..", "data", "items", "affixes.json")


def load_affix_data() -> list[dict]:
    with open(AFFIX_PATH) as f:
        return json.load(f)


def _affix_data() -> list[dict]:
    """
    Return the affix list. Uses the app-context AffixRegistry when available
    (populated from the pipeline at startup), otherwise falls back to the
    direct file load so tests and scripts keep working.
    """
    try:
        from flask import current_app
        registry = current_app.extensions.get("affix_registry")
        if registry is not None:
            return registry.all()
    except RuntimeError:
        pass
    global _affix_cache
    if _affix_cache is None:
        _affix_cache = load_affix_data()
    return _affix_cache


_affix_cache: list[dict] | None = None


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def get_affixes_by_type(item_type: str, affix_type: str) -> list[dict]:
    """
    Return all affixes valid for the given item_type and affix_type (prefix/suffix).

    Args:
      item_type:   e.g. 'helmet', 'wand', 'boots'
      affix_type:  'prefix' or 'suffix'
    """
    return [
        a for a in _affix_data()
        if a["type"] == affix_type and item_type in a.get("applicable_to", [])
    ]


def get_prefixes(item_type: str) -> list[dict]:
    return get_affixes_by_type(item_type, "prefix")


def get_suffixes(item_type: str) -> list[dict]:
    return get_affixes_by_type(item_type, "suffix")


def get_affix_pool(item_type: str) -> dict:
    """Return both prefix and suffix pools for an item type."""
    return {
        "prefixes": get_prefixes(item_type),
        "suffixes": get_suffixes(item_type),
    }


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def get_affix_by_name(name: str) -> Optional[dict]:
    """Look up an affix by its display name."""
    try:
        from flask import current_app
        registry = current_app.extensions.get("affix_registry")
        if registry is not None and name in registry:
            return registry.get_by_name(name)
    except RuntimeError:
        pass
    for affix in _affix_data():
        if affix["name"] == name:
            return affix
    return None


def get_affix_by_id(affix_id: str) -> Optional[dict]:
    """Look up an affix by its canonical id."""
    for affix in _affix_data():
        if affix["id"] == affix_id:
            return affix
    return None


# ---------------------------------------------------------------------------
# Tier access
# ---------------------------------------------------------------------------

def get_affix_tier_data(affix: dict, tier: int) -> Optional[dict]:
    """
    Return the tier data dict for the given tier number (1-indexed).

    Returns None if tier is out of range.
    """
    tiers = affix.get("tiers", [])
    for t in tiers:
        if t["tier"] == tier:
            return t
    return None


def get_max_tier(affix: dict) -> int:
    """Return the highest tier available for this affix."""
    tiers = affix.get("tiers", [])
    if not tiers:
        return 0
    return max(t["tier"] for t in tiers)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def is_affix_valid_for_item(item_type: str, affix: dict) -> bool:
    """Return True if this affix can be placed on the given item type."""
    return item_type in affix.get("applicable_to", [])


def validate_affix_slots(item: dict) -> bool:
    """
    Return True if the item's affix counts are within legal limits.

    Sealed affixes (item['sealed']) do NOT count toward prefix/suffix limits.
    """
    prefix_count = sum(
        1 for a in item.get("prefixes", [])
        if not a.get("sealed", False)
    )
    suffix_count = sum(
        1 for a in item.get("suffixes", [])
        if not a.get("sealed", False)
    )
    return prefix_count <= MAX_PREFIXES and suffix_count <= MAX_SUFFIXES


def can_add_affix(item, affix_type):
    if affix_type == "prefix":
        if len(item["prefixes"]) >= 2:
            return False
    if affix_type == "suffix":
        if len(item["suffixes"]) >= 2:
            return False
    return True


def can_seal_affix(item):
    if item["sealed_affix"] is not None:
        return False
    return True


# ---------------------------------------------------------------------------
# Counting
# ---------------------------------------------------------------------------

def count_affix_types(item: dict) -> dict:
    """Return counts of active prefixes and suffixes (sealed excluded)."""
    prefix_count = sum(1 for a in item.get("prefixes", []) if not a.get("sealed", False))
    suffix_count = sum(1 for a in item.get("suffixes", []) if not a.get("sealed", False))
    return {
        "prefixes": prefix_count,
        "suffixes": suffix_count,
        "sealed": 1 if item.get("sealed") else 0,
    }


def is_max_tier(
    affix,
    tier
):

    max_tier = len(
        affix["tiers"]
    )

    return tier >= max_tier
