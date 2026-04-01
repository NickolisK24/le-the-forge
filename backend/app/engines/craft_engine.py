"""
Craft Engine — pure crafting math extracted from craft_service.py.

All functions here are stateless and have no DB or HTTP dependencies.
craft_service.py imports from here for its calculations.

FP costs are loaded from crafting_rules.json via fp_engine.
"""

import copy
import random
from typing import Optional

import numpy as np

from app.engines.fp_engine import (
    expected_fp_cost,
    fp_cost_range,
    roll_fp_cost,
    load_fp_rules,
)

from app.engines.affix_engine import (
    get_affix_by_name,
    can_add_affix,
    is_max_tier
)

from app.constants.crafting import PERFECT_ROLL_THRESHOLD, TARGET_TIER
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# Derived from rules file — used for planning and display only.
# Actual per-action costs are rolled randomly via fp_engine.roll_fp_cost().
def _build_fp_cost_table() -> dict:
    rules = load_fp_rules()
    return {k: int((v["min"] + v["max"]) / 2) for k, v in rules["fp_costs"].items()}

# Keep FP_COSTS as expected (mean) values for backward-compat imports
FP_COSTS = _build_fp_cost_table()


def fp_cost(action: str) -> int:
    """Expected FP cost for an action (mean of range). Used for path planning."""
    return FP_COSTS.get(action, 4)


# ---------------------------------------------------------------------------
# Pure math helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Unified Craft Pipeline
# ---------------------------------------------------------------------------

def apply_craft_action(item: dict, action: str, affix_name: Optional[str] = None,
                      target_tier: Optional[int] = None) -> dict:
    """
    Modern Last Epoch craft action pipeline (post-0.8.4).
    Items NEVER fracture. Crafting simply stops when FP runs out.

    Pipeline Order (MANDATORY):
    1. Validate action
    2. Roll FP cost
    3. Apply craft effect
    4. Reduce FP
    5. Check FP remaining
    6. Return result

    Item structure:
    {
        "forge_potential": int,
        "affixes": list[dict]  # [{name, tier, sealed}]
    }
    """
    # 1. Validate action — check FP first
    # 2. Roll FP cost
    cost = roll_fp_cost(action)
    if item["forge_potential"] < cost:
        log.warning(
            "craft_action.insufficient_fp",
            action=action,
            needed=cost,
            available=item["forge_potential"],
        )
        return {
            "success": False,
            "outcome": "error",
            "message": f"Insufficient FP. Need {cost}, have {item['forge_potential']}.",
            "item": item
        }

    log.info(
        "craft_action.apply",
        action=action,
        affix=affix_name,
        target_tier=target_tier,
        fp_before=item["forge_potential"],
        fp_cost=cost,
    )

    # 3. Apply craft effect
    roll = random.uniform(0, 100)
    _apply_craft_effect(item, action, affix_name, target_tier, roll)

    # 4. Reduce FP
    item["forge_potential"] -= cost

    # 5. Check FP remaining (crafting stops when FP = 0)
    fp_remaining = item["forge_potential"]

    # 6. Return result
    outcome = "success"  # No risk mechanics in modern Last Epoch

    log.info("craft_action.success", action=action, fp_remaining=fp_remaining)

    return {
        "success": True,
        "outcome": outcome,
        "roll": None,  # No rolls in FP-only system
        "fp_cost": cost,
        "fp_remaining": fp_remaining,
        "message": f"Craft successful. FP remaining: {fp_remaining}.",
        "item": item
    }


def _apply_craft_effect(item: dict, action: str, affix_name: Optional[str],
                       target_tier: Optional[int], roll: float):
    """Apply the actual craft effect to the item."""
    affixes = item["affixes"]

    if action == "add_affix":
        if not affix_name:
            raise ValueError("affix_name required for add_affix")
        # Only unsealed affixes count toward prefix/suffix limits; sealed is a separate slot (max 1)
        prefix_count = sum(1 for a in affixes if a.get("type") == "prefix" and not a.get("sealed"))
        suffix_count = sum(1 for a in affixes if a.get("type") == "suffix" and not a.get("sealed"))
        active_count = sum(1 for a in affixes if not a.get("sealed"))
        # Get affix type from affix_engine
        affix_def = get_affix_by_name(affix_name)
        affix_type = affix_def.get("type") if affix_def else None
        if affix_type == "prefix" and prefix_count >= 2:
            raise ValueError("Prefix slots full (max 2 active prefixes).")
        if affix_type == "suffix" and suffix_count >= 2:
            raise ValueError("Suffix slots full (max 2 active suffixes).")
        if active_count >= 4:
            raise ValueError("Item already has 4 active affixes.")
        affixes.append({"name": affix_name, "tier": target_tier or 1, "sealed": False, "type": affix_type})

    elif action == "upgrade_affix":
        if not affix_name:
            raise ValueError("affix_name required for upgrade_affix")
        affix = next((a for a in affixes if a["name"] == affix_name), None)
        if not affix:
            raise ValueError(f"Affix {affix_name} not found")
        if affix.get("sealed"):
            raise ValueError("Cannot upgrade sealed affix")
        current_tier = affix.get("tier", 1)
        affix_def = get_affix_by_name(affix_name)
        if not affix_def:
            raise ValueError(f"Affix definition not found for {affix_name}")
        if is_max_tier(affix_def, current_tier):
            raise ValueError("Affix already at max tier")
        affix["tier"] = current_tier + 1

    elif action == "seal_affix":
        if not affix_name:
            raise ValueError("affix_name required for seal_affix")
        sealed_count = sum(1 for a in affixes if a.get("sealed"))
        if sealed_count >= 1:
            raise ValueError("Only 1 affix can be sealed at a time.")
        affix = next((a for a in affixes if a["name"] == affix_name), None)
        if not affix:
            raise ValueError(f"Affix {affix_name} not found")
        affix["sealed"] = True

    elif action == "unseal_affix":
        if not affix_name:
            raise ValueError("affix_name required for unseal_affix")
        affix = next((a for a in affixes if a["name"] == affix_name), None)
        if not affix:
            raise ValueError(f"Affix {affix_name} not found")
        if not affix.get("sealed"):
            raise ValueError("Affix not sealed")
        affix["sealed"] = False

    elif action == "remove_affix":
        if not affix_name:
            raise ValueError("affix_name required for remove_affix")
        item["affixes"] = [a for a in affixes if a["name"] != affix_name]


# ---------------------------------------------------------------------------
# Optimal path search
# ---------------------------------------------------------------------------

def optimal_path_search(affixes: list, forge_potential: int) -> list:
    """
    Finds the optimal crafting sequence for upgrading all unsealed affixes to T4.
    Modern Last Epoch: No instability or fractures, just FP management.

    Uses simple greedy approach: upgrade lowest tier affixes first, seal when beneficial.
    """
    steps = []
    fp = forge_potential
    current_affixes = copy.deepcopy(affixes)

    to_upgrade = [
        a for a in current_affixes
        if not a.get("sealed") and a.get("tier", 1) < TARGET_TIER
    ]

    if not to_upgrade:
        return steps

    # Sort by current tier (lowest first) to upgrade weakest affixes first
    to_upgrade.sort(key=lambda a: a.get("tier", 1))

    for target_affix in to_upgrade:
        while target_affix.get("tier", 1) < TARGET_TIER and fp >= FP_COSTS["upgrade_affix"]:
            new_tier = min(5, target_affix.get("tier", 1) + 1)
            target_affix["tier"] = new_tier

            steps.append({
                "action": "upgrade_affix",
                "affix": f"{target_affix['name']} → T{new_tier}",
                "risk_pct": 0.0,  # No risk in modern system
                "cumulative_survival_pct": 100.0,  # Always survives
                "sealed_count_at_step": sum(1 for a in current_affixes if a.get("sealed")),
                "note": f"Upgrade to T{new_tier}",
            })

            fp -= FP_COSTS["upgrade_affix"]

    return steps


# ---------------------------------------------------------------------------
# Monte Carlo simulation
# ---------------------------------------------------------------------------

def simulate_sequence(
    forge_potential: int,
    proposed_steps: list,
    n_simulations: int = 10_000,
    seed: Optional[int] = None,
) -> dict:
    """
    Monte Carlo simulation of a proposed action sequence for modern Last Epoch.
    No instability or fractures — just FP exhaustion and completion rates.

    Pass ``seed`` for a fully reproducible run — identical inputs + seed always
    produce identical output, which is required for regression testing and
    stable comparison between crafting strategies.

    Returns:
      completion_chance, step_survival_curve, n_simulations, seed
    """
    log.info(
        "simulate_sequence.start",
        forge_potential=forge_potential,
        steps=len(proposed_steps),
        n=n_simulations,
        seed=seed,
    )

    rng = random.Random(seed)
    n = n_simulations
    fp_exhausted_at_step = [0] * len(proposed_steps)
    completed_all = 0
    fp_remaining_distribution = []

    for _ in range(n):
        fp = forge_potential
        completed = True

        for step_idx, step in enumerate(proposed_steps):
            action = step.get("action", "upgrade_affix")
            cost = FP_COSTS.get(action, 4)

            if fp < cost:
                fp_exhausted_at_step[step_idx] += 1
                completed = False
                fp_remaining_distribution.append(fp)
                break

            fp -= cost

        if completed:
            completed_all += 1
            fp_remaining_distribution.append(fp)

    # Calculate survival curve (steps completed)
    cumulative_exhaustion = 0
    step_survival = []
    for count in fp_exhausted_at_step:
        cumulative_exhaustion += count
        step_survival.append(round(1.0 - cumulative_exhaustion / n, 4))

    completion_chance = round(completed_all / n, 4)
    log.info(
        "simulate_sequence.end",
        completion_chance=completion_chance,
        n=n,
        seed=seed,
    )

    return {
        "completion_chance": completion_chance,
        "step_survival_curve": step_survival,
        "n_simulations": n,
        "seed": seed,
    }


# ---------------------------------------------------------------------------
# Strategy comparison
# ---------------------------------------------------------------------------

def compare_strategies(affixes: list, forge_potential: int) -> list:
    """
    Evaluate crafting strategies for modern Last Epoch (no instability/fractures).
    Since there's no risk, strategies differ only in FP efficiency and completion rates.
    """
    unsealed = [
        a for a in affixes
        if not a.get("sealed") and a.get("tier", 1) < TARGET_TIER
    ]

    if not unsealed:
        return []

    # Calculate upgrade steps needed
    total_upgrades_needed = sum(TARGET_TIER - a.get("tier", 1) for a in unsealed)

    # Strategy 1: Direct upgrades (most FP efficient)
    direct_steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0} for _ in range(total_upgrades_needed)]

    # Strategy 2: Seal then upgrade (uses more FP but allows more control)
    seal_steps = [{"action": "seal_affix", "sealed_count_at_step": i} for i in range(len(unsealed))]
    seal_then_upgrade_steps = seal_steps + [{"action": "upgrade_affix", "sealed_count_at_step": len(unsealed)} for _ in range(total_upgrades_needed)]

    strategies = [
        ("Direct Upgrade", "Upgrade affixes directly — most FP efficient", direct_steps),
        ("Seal First", "Seal all affixes first, then upgrade — more FP cost but maximum control", seal_then_upgrade_steps),
    ]

    results = []
    for name, description, steps in strategies:
        if not steps:
            results.append({
                "name": name, "description": description,
                "expected_steps": 0, "expected_fp_cost": 0,
                "completion_chance": 1.0,
            })
            continue

        sim = simulate_sequence(forge_potential, steps, n_simulations=5_000)
        fp_cost_total = sum(FP_COSTS.get(s["action"], 4) for s in steps)
        results.append({
            "name": name,
            "description": description,
            "completion_chance": sim["completion_chance"],
            "expected_steps": len(steps),
            "expected_fp_cost": fp_cost_total,
        })

    return results






def add_affix(item, affix_name, tier):
    """Add an affix to an item. Returns structured {success, reason} response."""
    affix = get_affix_by_name(affix_name)
    if affix is None:
        return {"success": False, "reason": "Affix not found"}

    affix_type = affix["type"]
    if not can_add_affix(item, affix_type):
        return {"success": False, "reason": "Slot limit reached"}

    cost = roll_fp_cost("add_affix")
    if item["forging_potential"] < cost:
        return {"success": False, "reason": "Not enough FP"}

    item["forging_potential"] -= cost
    affix_data = {"name": affix_name, "tier": tier}
    if affix_type == "prefix":
        item["prefixes"].append(affix_data)
    else:
        item["suffixes"].append(affix_data)

    return {"success": True, "reason": "Affix added"}


def upgrade_affix(item, affix_name):
    """Upgrade an affix tier by 1. Returns structured {success, reason} response."""
    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                affix_data = get_affix_by_name(affix_name)
                if is_max_tier(affix_data, affix["tier"]):
                    return {"success": False, "reason": "Already at max tier"}

                cost = roll_fp_cost("upgrade_affix")
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                affix["tier"] += 1
                return {"success": True, "reason": "Affix upgraded"}

    return {"success": False, "reason": "Affix not found"}


def remove_affix(item, affix_name):
    """Remove an affix from an item. Returns structured {success, reason} response."""
    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                cost = roll_fp_cost("remove_affix")
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                affix_list.remove(affix)
                return {"success": True, "reason": "Affix removed"}

    return {"success": False, "reason": "Affix not found"}


def unseal_affix(item):
    """Return the sealed affix back to its prefix/suffix slot.
    Returns structured {success, reason} response."""
    if item["sealed_affix"] is None:
        return {"success": False, "reason": "No sealed affix"}

    cost = roll_fp_cost("unseal_affix")
    if item["forging_potential"] < cost:
        return {"success": False, "reason": "Not enough FP"}

    item["forging_potential"] -= cost
    affix = item["sealed_affix"]
    item["sealed_affix"] = None

    affix_data = get_affix_by_name(affix["name"])
    if affix_data and affix_data["type"] == "prefix":
        item["prefixes"].append(affix)
    else:
        item["suffixes"].append(affix)

    return {"success": True, "reason": "Affix unsealed"}


def seal_affix(item, affix_name):
    """Seal an affix (max 1 sealed). Returns structured {success, reason} response."""
    if item["sealed_affix"]:
        return {"success": False, "reason": "Already has sealed affix"}

    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                cost = roll_fp_cost("seal_affix")
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                item["sealed_affix"] = affix
                affix_list.remove(affix)
                return {"success": True, "reason": "Affix sealed"}

    return {"success": False, "reason": "Affix not found"}
