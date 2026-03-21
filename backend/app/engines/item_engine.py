"""
Item Engine — constructs validated item objects with resolved FP.

Sits above base_engine and fp_engine. Provides the canonical create_item()
function used by craft_service when starting a new craft session.
"""

from typing import Optional

from app.engines.base_engine import get_base, resolve_fp


def create_item(
    base_type: str,
    fp_mode: str = "random",
    manual_fp: Optional[int] = None,
) -> dict:
    """
    Create a new item dict with validated FP.

    Args:
      base_type:  Item slot/type key (e.g. 'helmet', 'wand')
      fp_mode:    'random' | 'manual' | 'fixed'
      manual_fp:  Required for manual/fixed modes

    Returns:
      {"success": True, "item": {...}}
      {"success": False, "reason": "..."}
    """
    # Validate base type exists
    try:
        base = get_base(base_type)
    except ValueError as e:
        return {"success": False, "reason": str(e)}

    # Resolve FP
    fp, error = resolve_fp(base_type, fp_mode, manual_fp)
    if error:
        return {"success": False, "reason": error}

    item = {
        "base": base_type,
        "prefixes": [],
        "suffixes": [],
        "sealed": None,
        "forge_potential": fp,
        "history": [],
        "implicit": base.get("implicit"),
        "armor": base.get("armor", 0),
    }

    return {"success": True, "item": item}
