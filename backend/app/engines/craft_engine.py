"""
Craft Engine — pure crafting math extracted from craft_service.py.

All functions here are stateless and have no DB or HTTP dependencies.
craft_service.py imports from here for its calculations.

FP costs and instability gains are loaded from crafting_rules.json via fp_engine.
"""

import copy
import random
from typing import Optional

import numpy as np

from app.engines.fp_engine import (
    expected_fp_cost,
    fp_cost_range,
    roll_fp_cost,
    roll_instability_gain,
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

MAX_INSTABILITY = 80
PERFECT_ROLL_THRESHOLD = 95
SEAL_RISK_THRESHOLD = 0.20
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

def fracture_risk(instability: int, sealed_count: int = 0) -> float:
    """
    Returns fracture probability (0.0–1.0).

    Formula: (effective_instability / MAX_INSTABILITY)²
    Each sealed affix reduces effective instability by 12.
    """
    effective = max(0, instability - (sealed_count * 12))
    base = (effective / MAX_INSTABILITY) ** 2
    return min(base, 1.0)


def fracture_risk_pct(instability: int, sealed_count: int = 0) -> float:
    """Same as fracture_risk but returns 0–100 float rounded to 1 decimal."""
    return round(fracture_risk(instability, sealed_count) * 100, 1)


def instability_gain(action: str, roll: Optional[float] = None) -> int:
    """Returns instability gained for an action."""
    is_perfect = bool(roll and roll > PERFECT_ROLL_THRESHOLD)
    return roll_instability_gain(action, is_perfect=is_perfect)


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
# Optimal path search
# ---------------------------------------------------------------------------

def optimal_path_search(instability: int, affixes: list, forge_potential: int) -> list:
    """
    Finds the optimal crafting sequence for upgrading all unsealed affixes to T4.

    Uses iterative lookahead with expected-value instability tracking.
    Seals an affix when fracture risk exceeds SEAL_RISK_THRESHOLD (20%).
    """
    steps = []
    inst = float(instability)
    fp = forge_potential
    current_affixes = copy.deepcopy(affixes)
    sealed_count = sum(1 for a in current_affixes if a.get("sealed"))
    cumulative_survival = 1.0

    to_upgrade = [
        a for a in current_affixes
        if not a.get("sealed") and a.get("tier", 1) < TARGET_TIER
    ]

    if not to_upgrade:
        return steps

    for target_affix in to_upgrade:
        current_risk = fracture_risk(int(inst), sealed_count)

        if current_risk > SEAL_RISK_THRESHOLD:
            candidates = [
                a for a in current_affixes
                if not a.get("sealed") and a["name"] != target_affix["name"]
            ]
            if candidates and fp >= FP_COSTS["seal_affix"]:
                to_seal = max(candidates, key=lambda a: a.get("tier", 0))
                steps.append({
                    "action": "seal_affix",
                    "affix": to_seal["name"],
                    "risk_pct": 0.0,
                    "cumulative_survival_pct": round(cumulative_survival * 100, 1),
                    "sealed_count_at_step": sealed_count,
                    "note": (
                        f"Seal \"{to_seal['name']}\" (T{to_seal['tier']}) — "
                        f"risk at {fracture_risk_pct(int(inst), sealed_count):.1f}%, "
                        f"drops to {fracture_risk_pct(int(inst), sealed_count + 1):.1f}% after seal"
                    ),
                })
                to_seal["sealed"] = True
                sealed_count += 1
                fp -= FP_COSTS["seal_affix"]

        while target_affix.get("tier", 1) < TARGET_TIER and fp >= FP_COSTS["upgrade_affix"]:
            current_risk = fracture_risk(int(inst), sealed_count)

            if current_risk > SEAL_RISK_THRESHOLD:
                candidates = [
                    a for a in current_affixes
                    if not a.get("sealed") and a["name"] != target_affix["name"]
                ]
                if candidates and fp >= FP_COSTS["seal_affix"]:
                    to_seal = max(candidates, key=lambda a: a.get("tier", 0))
                    steps.append({
                        "action": "seal_affix",
                        "affix": to_seal["name"],
                        "risk_pct": 0.0,
                        "cumulative_survival_pct": round(cumulative_survival * 100, 1),
                        "sealed_count_at_step": sealed_count,
                        "note": (
                            f"Seal \"{to_seal['name']}\" — instability climbing, "
                            f"protect T{to_seal['tier']} gains before continuing"
                        ),
                    })
                    to_seal["sealed"] = True
                    sealed_count += 1
                    fp -= FP_COSTS["seal_affix"]
                    current_risk = fracture_risk(int(inst), sealed_count)

            cumulative_survival *= (1.0 - current_risk)
            new_tier = min(5, target_affix.get("tier", 1) + 1)
            target_affix["tier"] = new_tier

            steps.append({
                "action": "upgrade_affix",
                "affix": f"{target_affix['name']} → T{new_tier}",
                "risk_pct": round(current_risk * 100, 1),
                "cumulative_survival_pct": round(cumulative_survival * 100, 1),
                "sealed_count_at_step": sealed_count,
                "note": (
                    f"Upgrade to T{new_tier} — "
                    f"{round(current_risk * 100, 1)}% fracture risk at this step"
                ),
            })

            inst = min(MAX_INSTABILITY, inst + expected_instability_gain("upgrade_affix"))
            fp -= FP_COSTS["upgrade_affix"]

    return steps


# ---------------------------------------------------------------------------
# Monte Carlo simulation
# ---------------------------------------------------------------------------

def simulate_sequence(
    instability: int,
    forge_potential: int,
    proposed_steps: list,
    n_simulations: int = 10_000,
) -> dict:
    """
    Monte Carlo simulation of a proposed action sequence.

    Returns:
      brick_chance, perfect_item_chance, step_survival_curve,
      step_fracture_rates, median_instability, n_simulations
    """
    n = n_simulations
    fracture_at_step = [0] * len(proposed_steps)
    survived_all = 0
    final_instabilities = []
    # Severity counters — fraction of fracture events per type
    # Minor: roll in top third of risk window (barely fractured)
    # Major: roll in middle third
    # Destructive: roll in bottom third (worst outcome)
    severity_minor = 0
    severity_major = 0
    severity_destructive = 0

    for _ in range(n):
        inst = instability
        fp = forge_potential
        fractured = False

        for step_idx, step in enumerate(proposed_steps):
            action = step.get("action", "upgrade_affix")
            sealed_ct = step.get("sealed_count_at_step", 0)
            cost = FP_COSTS.get(action, 4)

            if fp < cost:
                break

            risk = fracture_risk(inst, sealed_ct)
            roll = random.random()

            if roll < risk:
                fracture_at_step[step_idx] += 1
                fractured = True
                # Classify severity by roll position within the fracture window:
                # roll near 0 → worst (destructive), roll near risk boundary → best (minor)
                relative = roll / risk if risk > 0 else 0
                if relative < 0.33:
                    severity_destructive += 1
                elif relative < 0.67:
                    severity_major += 1
                else:
                    severity_minor += 1
                break

            _gains = load_fp_rules()["instability_gains"].get(action, {"min": 3, "max": 8})
            lo, hi = _gains["min"], _gains["max"]
            if lo == hi:
                gain = lo
            elif roll > (PERFECT_ROLL_THRESHOLD / 100.0):
                gain = lo
            else:
                gain = random.randint(lo, hi)

            inst = min(MAX_INSTABILITY, inst + gain)
            fp -= cost

        if not fractured:
            survived_all += 1
            final_instabilities.append(inst)

    cumulative_fractures = 0
    step_survival = []
    for count in fracture_at_step:
        cumulative_fractures += count
        step_survival.append(round(1.0 - cumulative_fractures / n, 4))

    total_fractures = sum(fracture_at_step)
    sorted_finals = sorted(final_instabilities)
    median_inst = sorted_finals[len(sorted_finals) // 2] if sorted_finals else instability

    return {
        "brick_chance": round(total_fractures / n, 4),
        "perfect_item_chance": round(survived_all / n, 4),
        "step_survival_curve": step_survival,
        "step_fracture_rates": [round(f / n, 4) for f in fracture_at_step],
        "median_instability": median_inst,
        "n_simulations": n,
        "fracture_severity": {
            "minor_fracture_chance":       round(severity_minor / n, 4),
            "major_fracture_chance":       round(severity_major / n, 4),
            "destructive_fracture_chance": round(severity_destructive / n, 4),
        },
    }


# ---------------------------------------------------------------------------
# Strategy comparison
# ---------------------------------------------------------------------------

def compare_strategies(instability: int, affixes: list, forge_potential: int) -> list:
    """
    Evaluate three crafting strategies via Monte Carlo:
      Aggressive:   Upgrade without sealing
      Balanced:     Seal when risk > 20% (optimal path)
      Conservative: Seal all before any upgrade
    """
    unsealed = [
        a for a in affixes
        if not a.get("sealed") and a.get("tier", 1) < TARGET_TIER
    ]
    existing_sealed_count = sum(1 for a in affixes if a.get("sealed"))

    # Aggressive
    aggressive_steps = []
    running_inst = float(instability)
    for affix in unsealed:
        tier = affix.get("tier", 1)
        while tier < TARGET_TIER:
            aggressive_steps.append({
                "action": "upgrade_affix",
                "sealed_count_at_step": existing_sealed_count,
            })
            running_inst = min(MAX_INSTABILITY, running_inst + expected_instability_gain("upgrade_affix"))
            tier += 1

    # Balanced
    balanced_raw = optimal_path_search(instability, copy.deepcopy(affixes), forge_potential)
    balanced_steps = [
        {"action": s["action"], "sealed_count_at_step": s["sealed_count_at_step"]}
        for s in balanced_raw
    ]

    # Conservative
    conservative_steps = []
    cons_sealed = existing_sealed_count
    for affix in unsealed:
        conservative_steps.append({
            "action": "seal_affix",
            "sealed_count_at_step": cons_sealed,
        })
        cons_sealed += 1
    for affix in unsealed:
        tier = affix.get("tier", 1)
        while tier < TARGET_TIER:
            conservative_steps.append({
                "action": "upgrade_affix",
                "sealed_count_at_step": cons_sealed,
            })
            tier += 1

    strategies = [
        ("Aggressive",   "Upgrade without sealing — high risk, no FP spent on seals",   aggressive_steps),
        ("Balanced",     "Seal strategically when fracture risk exceeds 20%",            balanced_steps),
        ("Conservative", "Seal all affixes before any upgrade — maximum protection",     conservative_steps),
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

        sim = simulate_sequence(instability, forge_potential, steps, n_simulations=5_000)
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
