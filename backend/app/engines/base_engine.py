"""
Base Engine — loads base item data and provides FP generation/validation.

Source of truth: /data/base_items.json
Never hardcode FP ranges — always load from that file.
"""

import os
import json
import random
from typing import Optional

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Load base item data
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.join(BASE_DIR, "..", "..", "..", "data", "base_items.json")

_base_cache: Optional[dict] = None


def load_base_data() -> dict:
    """Load and cache base_items.json."""
    global _base_cache
    if _base_cache is None:
        with open(BASE_PATH) as f:
            _base_cache = json.load(f)
    return _base_cache


def get_base(base_type: str) -> dict:
    """
    Return base item data for the given type.
    Raises ValueError if the base type is not found.
    """
    data = load_base_data()
    key = base_type.lower()
    if key not in data:
        raise ValueError(f"Unknown base type: {base_type!r}. Valid: {sorted(data.keys())}")
    return data[key]


def get_fp_range(base_type: str) -> tuple[int, int]:
    """Return (min_fp, max_fp) for the given base type."""
    base = get_base(base_type)
    return base["min_fp"], base["max_fp"]


# ---------------------------------------------------------------------------
# FP Modes
# ---------------------------------------------------------------------------

def generate_fp(base_type: str) -> int:
    """
    MODE 1 — RANDOM: Roll FP within the base item's valid range.
    Default behavior for normal crafting simulation.
    """
    lo, hi = get_fp_range(base_type)
    return random.randint(lo, hi)


def validate_fp(base_type: str, user_fp: int) -> bool:
    """
    MODE 2 — MANUAL: Validate that a user-supplied FP value is within range.

    Rules:
      - Must be an integer
      - Must be within [min_fp, max_fp] for the base type
    """
    if not isinstance(user_fp, int) or isinstance(user_fp, bool):
        return False
    lo, hi = get_fp_range(base_type)
    return lo <= user_fp <= hi


def fixed_fp(value: int) -> int:
    """
    MODE 3 — FIXED: Return a specific FP value directly.
    Used for debugging, testing, and reproducible optimizer runs.
    """
    return value


def resolve_fp(base_type: str, fp_mode: str = "random",
               manual_fp: Optional[int] = None) -> tuple[int, Optional[str]]:
    """
    Resolve final FP value from the requested mode.

    Returns: (fp_value, error_message_or_None)
    """
    if fp_mode == "random":
        return generate_fp(base_type), None

    elif fp_mode == "manual":
        if manual_fp is None:
            return 0, "manual_fp is required when fp_mode is 'manual'"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        if not validate_fp(base_type, manual_fp):
            lo, hi = get_fp_range(base_type)
            return 0, f"manual_fp {manual_fp} is out of range [{lo}, {hi}] for {base_type}"
        return manual_fp, None

    elif fp_mode == "fixed":
        if manual_fp is None:
            return 0, "manual_fp value is required for fixed mode"
        if not isinstance(manual_fp, int) or isinstance(manual_fp, bool):
            return 0, "manual_fp must be an integer"
        return fixed_fp(manual_fp), None

    else:
        return 0, f"Invalid fp_mode: {fp_mode!r}. Valid: 'random', 'manual', 'fixed'"


def get_all_bases() -> dict:
    """Return full base_items.json — for the /api/ref/base-items endpoint."""
    return load_base_data()
