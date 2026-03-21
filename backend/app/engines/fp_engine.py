"""
FP Engine — Forge Potential core logic.

Single source of truth for all FP cost rolling, validation, and event logging.
Costs are loaded from /data/crafting_rules.json — never hardcoded.

Design rules:
  - All RNG lives here, nowhere else.
  - Backend craft_service uses apply_fp() as the entry point.
  - Logs every FP event to item["history"] for replay/analytics.
"""

import os
import json
import random
from typing import Optional

# ---------------------------------------------------------------------------
# Load rules
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(BASE_DIR, "..", "..", "..", "data", "crafting_rules.json")

_rules_cache: Optional[dict] = None


def load_fp_rules() -> dict:
    """Load and cache crafting rules from disk."""
    global _rules_cache
    if _rules_cache is None:
        with open(RULES_PATH) as f:
            _rules_cache = json.load(f)
    return _rules_cache


def reload_fp_rules() -> dict:
    """Force reload — useful after a rules file update."""
    global _rules_cache
    _rules_cache = None
    return load_fp_rules()


# ---------------------------------------------------------------------------
# Core FP functions
# ---------------------------------------------------------------------------

def roll_fp_cost(action_type: str) -> int:
    """
    Roll a random FP cost for the given action.
    Range is defined in crafting_rules.json — never hardcoded.
    """
    rules = load_fp_rules()
    action = rules["fp_costs"].get(action_type)
    if action is None:
        raise ValueError(f"Unknown action type: {action_type!r}")
    return random.randint(action["min"], action["max"])


def fp_cost_range(action_type: str) -> tuple[int, int]:
    """Return (min, max) FP cost for an action — useful for UI display."""
    rules = load_fp_rules()
    action = rules["fp_costs"].get(action_type)
    if action is None:
        raise ValueError(f"Unknown action type: {action_type!r}")
    return action["min"], action["max"]


def expected_fp_cost(action_type: str) -> float:
    """Expected (mean) FP cost for planning and path search."""
    lo, hi = fp_cost_range(action_type)
    return (lo + hi) / 2.0


def roll_instability_gain(action_type: str, is_perfect: bool = False) -> int:
    """
    Roll instability gained for an action.
    Perfect rolls use the minimum gain.
    """
    rules = load_fp_rules()
    gains = rules["instability_gains"].get(action_type, {"min": 3, "max": 8})
    lo, hi = gains["min"], gains["max"]
    if lo == hi:
        return lo
    return lo if is_perfect else random.randint(lo, hi)


def roll_base_fp(item_type: str) -> int:
    """Roll the starting FP for a new item of the given type."""
    rules = load_fp_rules()
    base_fp = rules.get("base_item_fp", {})
    slot = base_fp.get(item_type.lower(), base_fp.get("default", {"min": 16, "max": 24}))
    return random.randint(slot["min"], slot["max"])


# ---------------------------------------------------------------------------
# Consume + Log
# ---------------------------------------------------------------------------

def consume_fp(item: dict, action_type: str) -> dict:
    """
    Roll an FP cost, validate the item has enough, and deduct it.

    Returns:
      {"success": True, "cost": int, "remaining_fp": int}
      {"success": False, "reason": str, "cost": int}
    """
    cost = roll_fp_cost(action_type)

    if item.get("forge_potential", 0) < cost:
        return {
            "success": False,
            "reason": "Not enough Forge Potential",
            "cost": cost,
        }

    item["forge_potential"] -= cost
    return {
        "success": True,
        "cost": cost,
        "remaining_fp": item["forge_potential"],
    }


def log_fp_event(item: dict, action_type: str, cost: int) -> None:
    """Append an FP event to item["history"]. Every FP change must be logged."""
    if "history" not in item:
        item["history"] = []
    item["history"].append({
        "action": action_type,
        "fp_cost": cost,
        "remaining_fp": item["forge_potential"],
    })


def apply_fp(item: dict, action_type: str) -> dict:
    """
    Main entry point: consume FP, log the event, return result.
    Returns a result dict — caller checks result["success"] before applying craft.
    """
    result = consume_fp(item, action_type)
    if result["success"]:
        log_fp_event(item, action_type, result["cost"])
    return result


# ---------------------------------------------------------------------------
# Session-model helpers (for craft_service which uses SQLAlchemy models)
# ---------------------------------------------------------------------------

def roll_session_fp_cost(action_type: str) -> int:
    """Alias for craft_service — same as roll_fp_cost."""
    return roll_fp_cost(action_type)


def get_crafting_rules() -> dict:
    """Return the full rules dict — for the /api/ref/crafting-rules endpoint."""
    return load_fp_rules()
