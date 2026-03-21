"""
Item Engine — constructs validated item objects with resolved FP.

FP is primarily determined by rarity (from forging_potential_ranges.json).
Base type data (base_items.json) provides metadata (armor, implicit, etc.)
and will later contribute a FP modifier on top of the rarity range.
"""

from typing import Optional

from app.engines.base_engine import get_base
from app.engines.fp_engine import (
    generate_fp_by_rarity,
    validate_fp_by_rarity,
    get_fp_range_by_rarity,
)


def resolve_fp_for_item(
    rarity: str,
    item_level: int = 84,
    fp_mode: str = "random",
    manual_fp: Optional[int] = None,
) -> tuple[int, Optional[str]]:
    """
    Resolve FP for an item using rarity as the primary range source.

    Returns: (fp_value, error_or_None)
    """
    if fp_mode == "random":
        return generate_fp_by_rarity(rarity, item_level), None

    elif fp_mode == "manual":
        if manual_fp is None:
            return 0, "manual_fp is required when fp_mode is 'manual'"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        if not validate_fp_by_rarity(rarity, manual_fp, item_level):
            lo, hi = get_fp_range_by_rarity(rarity, item_level)
            return 0, f"manual_fp {manual_fp} out of range [{lo}, {hi}] for {rarity} item"
        return manual_fp, None

    elif fp_mode == "fixed":
        if manual_fp is None:
            return 0, "manual_fp value is required for fixed mode"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        return manual_fp, None

    else:
        return 0, f"Invalid fp_mode: {fp_mode!r}. Valid: 'random', 'manual', 'fixed'"


def create_item(
    base_type: str,
    rarity: str = "Rare",
    item_level: int = 84,
    fp_mode: str = "random",
    manual_fp: Optional[int] = None,
) -> dict:
    """
    Create a new item dict with FP resolved from rarity range.

    Args:
      base_type:   Item slot key (e.g. 'helmet', 'wand')
      rarity:      Item rarity ('Normal', 'Magic', 'Rare', 'Exalted')
      item_level:  Item level (used for Phase 2 tier scaling)
      fp_mode:     'random' | 'manual' | 'fixed'
      manual_fp:   Required for manual/fixed modes

    Returns:
      {"success": True, "item": {...}}
      {"success": False, "reason": "..."}
    """
    # Load base metadata
    try:
        base = get_base(base_type)
    except ValueError as e:
        return {"success": False, "reason": str(e)}

    # Resolve FP from rarity
    fp, error = resolve_fp_for_item(rarity, item_level, fp_mode, manual_fp)
    if error:
        return {"success": False, "reason": error}

    item = {
        "item_type": base_type,
        "rarity": rarity,
        "item_level": item_level,
        "prefixes": [],
        "suffixes": [],
        "sealed_affix": None,
        "forging_potential": fp,
        "history": [],
        "implicit": base.get("implicit"),
        "armor": base.get("armor", 0),
    }

    return {"success": True, "item": item}
