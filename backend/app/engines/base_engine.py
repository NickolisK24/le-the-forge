"""
Base Engine — loads base item data and provides FP generation/validation.

Source of truth: /data/items/base_items.json

base_items.json is keyed by slot category (e.g. "helmet"), each value is a list
of named base items:
  { "name": str, "level_req": int, "min_fp": int, "max_fp": int,
    "armor": int, "implicit": str|null, "tags": [str] }

Public API
----------
get_base(name_or_slot)       dict — single item dict; slot key → first item in slot
get_bases_for_slot(slot)     list  — all named bases for a slot
get_fp_range(name_or_slot)   (min_fp, max_fp)
get_all_bases()              dict  — full file (slot → list)
generate_fp(name_or_slot)    int
validate_fp(name_or_slot, fp) bool
resolve_fp(name_or_slot, mode, manual_fp)  (int, error|None)
"""

import os
import json
import random
from typing import Optional

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(BASE_DIR, "..", "..", "..", "data", "items", "base_items.json")

_base_cache: Optional[dict] = None
# Secondary lookup: item_name.lower() → item dict
_name_cache: Optional[dict] = None


def load_base_data() -> dict:
    """Load and cache base_items.json."""
    global _base_cache, _name_cache
    if _base_cache is None:
        with open(BASE_PATH) as f:
            _base_cache = json.load(f)
        # Build name → item dict for O(1) lookup
        _name_cache = {}
        for slot_items in _base_cache.values():
            if isinstance(slot_items, list):
                for item in slot_items:
                    _name_cache[item["name"].lower()] = item
    return _base_cache


def _find_item(name_or_slot: str) -> Optional[dict]:
    """
    Find an item dict by slot key OR item name.
    Slot key → returns first item in that slot (backward compat).
    Item name → exact match (case-insensitive).
    Returns None if not found.
    """
    data = load_base_data()
    key = name_or_slot.lower()

    # Slot category match → return first item
    if key in data:
        slot_items = data[key]
        if isinstance(slot_items, list) and slot_items:
            return slot_items[0]

    # Named item match
    if _name_cache and key in _name_cache:
        return _name_cache[key]

    return None


def get_base(name_or_slot: str) -> dict:
    """
    Return base item data dict.
    Accepts a slot category key (returns representative/first item) or
    an exact item name.
    Raises ValueError if not found.
    """
    item = _find_item(name_or_slot)
    if item is None:
        raise ValueError(f"Unknown base type: {name_or_slot!r}")
    return item


def get_bases_for_slot(slot: str) -> list:
    """Return all named base items for a slot category. [] if slot not found."""
    data = load_base_data()
    slot_items = data.get(slot.lower(), [])
    return slot_items if isinstance(slot_items, list) else []


def get_all_bases() -> dict:
    """Return full base_items.json — for the /api/ref/base-items endpoint."""
    return load_base_data()


def get_fp_range(name_or_slot: str) -> tuple[int, int]:
    """
    Return (min_fp, max_fp) for a named base item or slot category.
    For a slot category, returns the range of the first item (representative).
    """
    item = _find_item(name_or_slot)
    if item is None:
        raise ValueError(f"Unknown base type: {name_or_slot!r}")
    return item["min_fp"], item["max_fp"]


# ---------------------------------------------------------------------------
# FP Modes
# ---------------------------------------------------------------------------

def generate_fp(name_or_slot: str) -> int:
    """MODE 1 — RANDOM: Roll FP within the base item's valid range."""
    lo, hi = get_fp_range(name_or_slot)
    return random.randint(lo, hi)


def validate_fp(name_or_slot: str, user_fp: int) -> bool:
    """MODE 2 — MANUAL: Validate that a user-supplied FP value is within range."""
    if not isinstance(user_fp, int) or isinstance(user_fp, bool):
        return False
    lo, hi = get_fp_range(name_or_slot)
    return lo <= user_fp <= hi


def fixed_fp(value: int) -> int:
    """MODE 3 — FIXED: Return a specific FP value directly."""
    return value


def resolve_fp(name_or_slot: str, fp_mode: str = "random",
               manual_fp: Optional[int] = None) -> tuple[int, Optional[str]]:
    """
    Resolve final FP value from the requested mode.
    Returns: (fp_value, error_message_or_None)
    """
    if fp_mode == "random":
        return generate_fp(name_or_slot), None

    elif fp_mode == "manual":
        if manual_fp is None:
            return 0, "manual_fp is required when fp_mode is 'manual'"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        if not validate_fp(name_or_slot, manual_fp):
            lo, hi = get_fp_range(name_or_slot)
            return 0, f"manual_fp {manual_fp} is out of range [{lo}, {hi}] for {name_or_slot}"
        return manual_fp, None

    elif fp_mode == "fixed":
        if manual_fp is None:
            return 0, "manual_fp value is required for fixed mode"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        return fixed_fp(manual_fp), None

    else:
        return 0, f"Invalid fp_mode: {fp_mode!r}. Valid: 'random', 'manual', 'fixed'"
