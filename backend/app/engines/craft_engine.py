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


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PERFECT_ROLL_THRESHOLD = 95
TARGET_TIER = 4

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


def expected_instability_gain(action: str) -> float:
    """Expected (mean) instability gain accounting for 5% perfect rolls."""
    rules = load_fp_rules()
    gains = rules["instability_gains"].get(action, {"min": 3, "max": 8})
    lo, hi = gains["min"], gains["max"]
    if lo == hi:
        return float(lo)
    perfect_prob = 0.05
    normal_mean = (lo + hi) / 2.0
    return perfect_prob * lo + (1 - perfect_prob) * normal_mean


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
    # 1. Validate action
    if item.get("is_fractured", False):
        return {
            "success": False,
            "outcome": "error",
            "message": "Item is fractured.",
            "item": item
        }

    # 2. Roll FP cost
    cost = roll_fp_cost(action)
    if item["forge_potential"] < cost:
        return {
            "success": False,
            "outcome": "error",
            "message": f"Insufficient FP. Need {cost}, have {item['forge_potential']}.",
            "item": item
        }

    # 3. Apply craft effect
    roll = random.uniform(0, 100)
    _apply_craft_effect(item, action, affix_name, target_tier, roll)

    # 4. Reduce FP
    item["forge_potential"] -= cost

    # 5. Check FP remaining (crafting stops when FP = 0, but doesn't fracture)
    fp_remaining = item["forge_potential"]

    # 6. Return result
    outcome = "success"  # No risk mechanics in modern Last Epoch

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
) -> dict:
    """
    Monte Carlo simulation of a proposed action sequence for modern Last Epoch.
    No instability or fractures - just FP exhaustion and success rates.

    Returns:
      brick_chance (always 0.0), perfect_item_chance, step_survival_curve,
      step_fracture_rates (always []), n_simulations
    """
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

    return {
        "brick_chance": 0.0,  # No fractures in modern Last Epoch
        "perfect_item_chance": round(completed_all / n, 4),
        "step_survival_curve": step_survival,
        "step_fracture_rates": [],  # No fractures
        "n_simulations": n,
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
                "brick_chance": 0.0, "perfect_item_chance": 1.0,
                "expected_steps": 0, "expected_fp_cost": 0,
            })
            continue

        sim = simulate_sequence(forge_potential, steps, n_simulations=5_000)
        fp_cost_total = sum(FP_COSTS.get(s["action"], 4) for s in steps)
        results.append({
            "name": name,
            "description": description,
            "brick_chance": sim["brick_chance"],
            "perfect_item_chance": sim["perfect_item_chance"],
            "expected_steps": len(steps),
            "expected_fp_cost": fp_cost_total,
        })

    return results


def simulate_crafting_path(
    instability: int,
    forge_potential: int,
    proposed_steps: list,
    n_simulations: int = 1_000,
) -> dict:
    """
    High-fidelity Monte Carlo simulation of a crafting path.

    Unlike simulate_sequence (which uses mean FP costs), this function rolls
    actual random FP costs and instability gains each iteration — giving
    accurate probability distributions of FP consumption, step completion,
    and fracture outcomes.

    Args:
      instability:     Starting instability (0–80).
      forge_potential: Starting FP.
      proposed_steps:  List of {"action": str, "sealed_count_at_step": int}.
      n_simulations:   Number of full runs (default 1 000; max recommended 50 000).

    Returns a dict with:
      brick_chance               — fraction of runs that fractured
      perfect_item_chance        — fraction of runs that completed all steps
      step_survival_curve        — cumulative survival after each step
      step_fracture_rates        — per-step fracture rate
      fp_consumed: {min, max, mean, p25, p50, p75}
      steps_completed: {min, max, mean, p50}
      final_instability: {min, max, mean, p50}
      fracture_severity: {minor, major, destructive}
      n_simulations
    """
    rules = load_fp_rules()
    n = n_simulations
    num_steps = len(proposed_steps)

    # Pre-extract per-step config so we don't re-hit dicts inside the hot loop
    step_cost_ranges = []
    step_risk_rates = []
    step_gain_ranges = []
    for step in proposed_steps:
        action = step.get("action", "upgrade_affix")
        sealed_ct = step.get("sealed_count_at_step", 0)
        cost_cfg = rules["fp_costs"].get(action, {"min": 2, "max": 6})
        gain_cfg = rules["instability_gains"].get(action, {"min": 3, "max": 8})
        step_cost_ranges.append((cost_cfg["min"], cost_cfg["max"]))
        step_gain_ranges.append((gain_cfg["min"], gain_cfg["max"]))
        step_risk_rates.append(sealed_ct)  # stored to compute risk per-inst

    # ---- Vectorized simulation using NumPy ----
    rng = np.random.default_rng()

    # State arrays — one entry per simulation run
    fp_arr  = np.full(n, forge_potential, dtype=np.float32)
    inst_arr = np.full(n, instability, dtype=np.float32)
    active   = np.ones(n, dtype=bool)    # runs still in progress
    fractured = np.zeros(n, dtype=bool)
    steps_done = np.zeros(n, dtype=np.int32)
    fp_spent = np.zeros(n, dtype=np.float32)

    # For severity breakdown — tracked as fractional rolls
    severity_minor = 0
    severity_major = 0
    severity_destructive = 0
    fracture_at_step = np.zeros(num_steps, dtype=np.int32)

    for step_idx, step in enumerate(proposed_steps):
        action = step.get("action", "upgrade_affix")
        sealed_ct = step.get("sealed_count_at_step", 0)

        cost_lo, cost_hi = step_cost_ranges[step_idx]
        gain_lo, gain_hi = step_gain_ranges[step_idx]

        # Only runs still active take this step
        mask = active.copy()
        if not mask.any():
            break

        # Roll FP costs for all active runs
        if cost_lo == cost_hi:
            costs = np.full(n, cost_lo, dtype=np.float32)
        else:
            costs = rng.integers(cost_lo, cost_hi + 1, size=n).astype(np.float32)

        # Runs that can't afford the cost stop (not a fracture)
        cant_afford = mask & (fp_arr < costs)
        active[cant_afford] = False
        mask = active & ~fractured

        if not mask.any():
            break

        # Compute fracture risk per run (depends on current instability)
        risk_arr = np.vectorize(lambda inst: fracture_risk(inst, sealed_ct))(inst_arr)

        # Roll fracture check
        fracture_rolls = rng.random(n)
        fractured_this_step = mask & (fracture_rolls < risk_arr)

        if fractured_this_step.any():
            fracture_at_step[step_idx] += int(fractured_this_step.sum())
            fractured |= fractured_this_step
            active[fractured_this_step] = False

            # Severity breakdown
            relative = np.where(
                risk_arr[fractured_this_step] > 0,
                fracture_rolls[fractured_this_step] / risk_arr[fractured_this_step],
                0.5,
            )
            severity_destructive += int((relative < 0.33).sum())
            severity_major += int(((relative >= 0.33) & (relative < 0.67)).sum())
            severity_minor += int((relative >= 0.67).sum())

            # Deduct FP for fractured runs too
            fp_spent[fractured_this_step] += costs[fractured_this_step]
            fp_arr[fractured_this_step] -= costs[fractured_this_step]

        # For runs that survived this step
        survived_step = mask & ~fractured_this_step
        if survived_step.any():
            fp_spent[survived_step] += costs[survived_step]
            fp_arr[survived_step] -= costs[survived_step]
            steps_done[survived_step] = step_idx + 1

            # Roll instability gain
            if gain_lo == gain_hi:
                gains = np.full(n, gain_lo, dtype=np.float32)
            else:
                gains = rng.integers(gain_lo, gain_hi + 1, size=n).astype(np.float32)
                # Perfect roll threshold: use minimum gain
                perfect = fracture_rolls > (PERFECT_ROLL_THRESHOLD / 100.0)
                gains = np.where(perfect, gain_lo, gains)

            inst_arr[survived_step] = np.minimum(
                MAX_INSTABILITY, inst_arr[survived_step] + gains[survived_step]
            )

    survived_all = int((~fractured).sum())

    # ---- Aggregate results ----
    fp_consumed = fp_spent
    steps_completed = np.where(fractured, steps_done, steps_done)  # same either way
    final_inst = inst_arr

    def _pct(arr, p):
        return int(np.percentile(arr, p))

    cumulative = 0
    step_survival = []
    for count in fracture_at_step:
        cumulative += int(count)
        step_survival.append(round(1.0 - cumulative / n, 4))

    return {
        "brick_chance": round(float(fractured.sum()) / n, 4),
        "perfect_item_chance": round(survived_all / n, 4),
        "step_survival_curve": step_survival,
        "step_fracture_rates": [round(int(f) / n, 4) for f in fracture_at_step],
        "fp_consumed": {
            "min": int(fp_consumed.min()),
            "max": int(fp_consumed.max()),
            "mean": round(float(fp_consumed.mean()), 2),
            "p25": _pct(fp_consumed, 25),
            "p50": _pct(fp_consumed, 50),
            "p75": _pct(fp_consumed, 75),
        },
        "steps_completed": {
            "min": int(steps_completed.min()),
            "max": int(steps_completed.max()),
            "mean": round(float(steps_completed.mean()), 2),
            "p50": _pct(steps_completed, 50),
        },
        "final_instability": {
            "min": int(final_inst.min()),
            "max": int(final_inst.max()),
            "mean": round(float(final_inst.mean()), 2),
            "p50": _pct(final_inst, 50),
        },
        "fracture_severity": {
            "minor_fracture_chance":       round(severity_minor / n, 4),
            "major_fracture_chance":       round(severity_major / n, 4),
            "destructive_fracture_chance": round(severity_destructive / n, 4),
        },
        "n_simulations": n,
    }


def fracture_item(item):
    """
    Apply a fracture to an item dict.

    A fractured item is permanently damaged — no further crafting actions can
    be applied. One random unsealed affix is destroyed as part of the fracture.
    The item is marked with is_fractured=True.

    Returns:
      True on success.
      {"success": False, "reason": ...} if item is already fractured or has no affixes.
    """
    if item.get("is_fractured"):
        return {"success": False, "reason": "Item is already fractured"}

    all_affixes = item.get("prefixes", []) + item.get("suffixes", [])
    unsealed = [a for a in all_affixes if not a.get("sealed")]

    if not unsealed:
        return {"success": False, "reason": "No affixes to fracture"}

    destroyed = random.choice(unsealed)

    item["prefixes"] = [a for a in item.get("prefixes", []) if a is not destroyed]
    item["suffixes"] = [a for a in item.get("suffixes", []) if a is not destroyed]
    item["is_fractured"] = True

    return {"success": True, "destroyed_affix": destroyed["name"]}


def add_affix(
    item,
    affix_name,
    tier
):

    affix = get_affix_by_name(
        affix_name
    )

    if affix is None:
        return {
            "success": False,
            "reason": "Affix not found"
        }

    affix_type = affix["type"]

    if not can_add_affix(
        item,
        affix_type
    ):
        return {
            "success": False,
            "reason": "Slot limit reached"
        }

    fp_cost = roll_fp_cost("add_affix")

    if item["forging_potential"] < fp_cost:
        return {
            "success": False,
            "reason": "Not enough FP"
        }

    item["forging_potential"] -= fp_cost

    affix_data = {

        "name": affix_name,
        "tier": tier

    }

    if affix_type == "prefix":

        item["prefixes"].append(
            affix_data
        )

    else:

        item["suffixes"].append(
            affix_data
        )

    return True


def upgrade_affix(
    item,
    affix_name
):

    for affix_list in [

        item["prefixes"],
        item["suffixes"]

    ]:

        for affix in affix_list:

            if affix["name"] == affix_name:

                affix_data = get_affix_by_name(
                    affix_name
                )

                if is_max_tier(
                    affix_data,
                    affix["tier"]
                ):
                    return {
                        "success": False,
                        "reason": "Already at max tier"
                    }

                fp_cost = roll_fp_cost("upgrade_affix")

                if (
                    item["forging_potential"]
                    < fp_cost
                ):
                    return {
                        "success": False,
                        "reason": "Not enough FP"
                    }

                item[
                    "forging_potential"
                ] -= fp_cost

                affix["tier"] += 1

                return True

    return {
        "success": False,
        "reason": "Affix not found"
    }


def remove_affix(
    item,
    affix_name
):

    for affix_list in [

        item["prefixes"],
        item["suffixes"]

    ]:

        for affix in affix_list:

            if affix["name"] == affix_name:

                fp_cost = roll_fp_cost("remove_affix")

                if (
                    item["forging_potential"]
                    < fp_cost
                ):
                    return {
                        "success": False,
                        "reason": "Not enough FP"
                    }

                item[
                    "forging_potential"
                ] -= fp_cost

                affix_list.remove(
                    affix
                )

                return True

    return {
        "success": False,
        "reason": "Affix not found"
    }


def unseal_affix(item):
    """
    Return the sealed affix back to its prefix/suffix slot.

    Deducts FP cost. Fails if there is no sealed affix or not enough FP.
    """
    if item["sealed_affix"] is None:
        return {"success": False, "reason": "No sealed affix"}

    fp_cost = roll_fp_cost("unseal_affix")

    if item["forging_potential"] < fp_cost:
        return {"success": False, "reason": "Not enough FP"}

    item["forging_potential"] -= fp_cost

    affix = item["sealed_affix"]
    item["sealed_affix"] = None

    affix_data = get_affix_by_name(affix["name"])
    if affix_data and affix_data["type"] == "prefix":
        item["prefixes"].append(affix)
    else:
        item["suffixes"].append(affix)

    return True


def seal_affix(
    item,
    affix_name
):

    if item["sealed_affix"]:

        return {
            "success": False,
            "reason": "Already has sealed affix"
        }

    for affix_list in [

        item["prefixes"],
        item["suffixes"]

    ]:

        for affix in affix_list:

            if affix["name"] == affix_name:

                fp_cost = roll_fp_cost("seal_affix")

                if (
                    item["forging_potential"]
                    < fp_cost
                ):
                    return {
                        "success": False,
                        "reason": "Not enough FP"
                    }

                item[
                    "forging_potential"
                ] -= fp_cost

                item[
                    "sealed_affix"
                ] = affix

                affix_list.remove(
                    affix
                )

                return True

    return {
        "success": False,
        "reason": "Affix not found"
    }
