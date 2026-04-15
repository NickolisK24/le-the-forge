"""
Craft Engine — pure crafting math extracted from craft_service.py.

All functions here are stateless and have no DB or HTTP dependencies.
craft_service.py imports from here for its calculations.

FP costs are loaded from crafting_rules.json via fp_engine.
"""

import copy
import json
import os
import random
from functools import lru_cache
from typing import Any, Optional

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

_CONSTANTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


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
                      target_tier: Optional[int] = None,
                      rng: Optional[random.Random] = None) -> dict:
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

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state —
    preserving the historical behaviour of this function for callers that
    don't need determinism.

    Item structure:
    {
        "forge_potential": int,
        "affixes": list[dict]  # [{name, tier, sealed}]
    }
    """
    # 1. Validate action — check FP first
    # 2. Roll FP cost
    cost = roll_fp_cost(action, rng=rng)
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

    # 3. Apply craft effect — ValueError means the action is invalid for this item
    try:
        _apply_craft_effect(item, action, affix_name, target_tier)
    except ValueError as e:
        return {
            "success": False,
            "outcome": "invalid",
            "message": str(e),
            "item": item,
        }

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
                       target_tier: Optional[int]):
    """Apply the actual craft effect to the item."""
    affixes = item["affixes"]

    if action == "add_affix":
        if not affix_name:
            raise ValueError("affix_name required for add_affix")
        max_pfx = _const("crafting", "max_prefixes", 3)
        max_sfx = _const("crafting", "max_suffixes", 3)
        # Only unsealed affixes count toward prefix/suffix limits; sealed is a separate slot (max 1)
        prefix_count = sum(1 for a in affixes if a.get("type") == "prefix" and not a.get("sealed"))
        suffix_count = sum(1 for a in affixes if a.get("type") == "suffix" and not a.get("sealed"))
        active_count = sum(1 for a in affixes if not a.get("sealed"))
        # Get affix type from affix_engine
        affix_def = get_affix_by_name(affix_name)
        # affix_def may be an AffixDefinition dataclass or a dict depending on loader version
        if affix_def is None:
            affix_type = None
        elif isinstance(affix_def, dict):
            affix_type = affix_def.get("type")
        else:
            affix_type = getattr(affix_def, "type", None)
        if affix_type == "prefix" and prefix_count >= max_pfx:
            raise ValueError(f"Prefix slots full (max {max_pfx} active prefixes).")
        if affix_type == "suffix" and suffix_count >= max_sfx:
            raise ValueError(f"Suffix slots full (max {max_sfx} active suffixes).")
        if active_count >= max_pfx + max_sfx:
            raise ValueError(f"Item already has {max_pfx + max_sfx} active affixes.")
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






def add_affix(item, affix_name, tier, rng: Optional[random.Random] = None):
    """Add an affix to an item. Returns structured {success, reason} response.

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state.
    """
    affix = get_affix_by_name(affix_name)
    if affix is None:
        return {"success": False, "reason": "Affix not found"}

    affix_type = affix["type"]
    if not can_add_affix(item, affix_type):
        return {"success": False, "reason": "Slot limit reached"}

    cost = roll_fp_cost("add_affix", rng=rng)
    if item["forging_potential"] < cost:
        return {"success": False, "reason": "Not enough FP"}

    item["forging_potential"] -= cost
    affix_data = {"name": affix_name, "tier": tier}
    if affix_type == "prefix":
        item["prefixes"].append(affix_data)
    else:
        item["suffixes"].append(affix_data)

    return {"success": True, "reason": "Affix added"}


def upgrade_affix(item, affix_name, rng: Optional[random.Random] = None):
    """Upgrade an affix tier by 1. Returns structured {success, reason} response.

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state.
    """
    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                affix_data = get_affix_by_name(affix_name)
                if is_max_tier(affix_data, affix["tier"]):
                    return {"success": False, "reason": "Already at max tier"}

                cost = roll_fp_cost("upgrade_affix", rng=rng)
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                affix["tier"] += 1
                return {"success": True, "reason": "Affix upgraded"}

    return {"success": False, "reason": "Affix not found"}


def remove_affix(item, affix_name, rng: Optional[random.Random] = None):
    """Remove an affix from an item. Returns structured {success, reason} response.

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state.
    """
    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                cost = roll_fp_cost("remove_affix", rng=rng)
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                affix_list.remove(affix)
                return {"success": True, "reason": "Affix removed"}

    return {"success": False, "reason": "Affix not found"}


def unseal_affix(item, rng: Optional[random.Random] = None):
    """Return the sealed affix back to its prefix/suffix slot.
    Returns structured {success, reason} response.

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state.
    """
    if item["sealed_affix"] is None:
        return {"success": False, "reason": "No sealed affix"}

    cost = roll_fp_cost("unseal_affix", rng=rng)
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


def seal_affix(item, affix_name, rng: Optional[random.Random] = None):
    """Seal an affix (max 1 sealed). Returns structured {success, reason} response.

    Pass an isolated ``rng`` instance for deterministic/seeded simulations.
    When omitted, falls back to the module-level global random state.
    """
    if item["sealed_affix"]:
        return {"success": False, "reason": "Already has sealed affix"}

    for affix_list in [item["prefixes"], item["suffixes"]]:
        for affix in affix_list:
            if affix["name"] == affix_name:
                cost = roll_fp_cost("seal_affix", rng=rng)
                if item["forging_potential"] < cost:
                    return {"success": False, "reason": "Not enough FP"}

                item["forging_potential"] -= cost
                item["sealed_affix"] = affix
                affix_list.remove(affix)
                return {"success": True, "reason": "Affix sealed"}

    return {"success": False, "reason": "Affix not found"}


# ---------------------------------------------------------------------------
# Architecture-plan required functions (probability foundation)
# ---------------------------------------------------------------------------

def calculate_success_probability(
    item: dict,
    action: str,
    target_tier: int | None = None,
) -> float:
    """Return the probability (0.0–1.0) that the given craft *action* succeeds.

    This is the canonical interface from architecture_implementation_plan.md.

    Rules:
    - ``add_affix``: 1.0 if FP ≥ expected cost and a prefix/suffix slot is open,
      otherwise 0.0.
    - ``upgrade_affix``: 1.0 if FP ≥ expected cost and the target affix exists
      and is not already at max tier, otherwise 0.0.
    - ``remove_affix``: 1.0 if FP ≥ expected cost and any affix is present,
      otherwise 0.0.
    - ``seal_affix``: 1.0 if FP ≥ expected cost and no sealed slot is occupied,
      otherwise 0.0.
    - Any other action: 0.0.

    Args:
        item: Craft item dict with ``forging_potential``, ``prefixes``,
              ``suffixes``, and ``sealed_affix`` keys.
        action: One of ``add_affix``, ``upgrade_affix``, ``remove_affix``,
                ``seal_affix``.
        target_tier: Required for ``upgrade_affix`` — the tier being targeted.

    Returns:
        Probability as a float in [0.0, 1.0].
    """
    fp = item.get("forging_potential", item.get("forge_potential", 0))
    expected = fp_cost(action)

    if fp < expected:
        return 0.0

    if action == "add_affix":
        prefix_full = len(item.get("prefixes", [])) >= 3
        suffix_full = len(item.get("suffixes", [])) >= 3
        return 0.0 if (prefix_full and suffix_full) else 1.0

    if action == "upgrade_affix":
        all_affixes = item.get("prefixes", []) + item.get("suffixes", [])
        if not all_affixes:
            return 0.0
        if target_tier is not None:
            upgradeable = [a for a in all_affixes if a.get("tier", 1) < target_tier]
            return 1.0 if upgradeable else 0.0
        # No specific target — any non-max-tier affix is upgradeable
        upgradeable = [a for a in all_affixes if not is_max_tier(a.get("name", ""), a.get("tier", 1))]
        return 1.0 if upgradeable else 0.0

    if action == "remove_affix":
        has_affixes = bool(item.get("prefixes") or item.get("suffixes"))
        return 1.0 if has_affixes else 0.0

    if action == "seal_affix":
        already_sealed = item.get("sealed_affix") is not None
        has_affixes = bool(item.get("prefixes") or item.get("suffixes"))
        return 0.0 if already_sealed else (1.0 if has_affixes else 0.0)

    return 0.0


def calculate_fracture_probability(item: dict) -> float:
    """Return the probability (0.0–1.0) that the next craft attempt fractures the item.

    Fracture risk is determined by remaining forging potential — the lower the FP,
    the higher the risk.  Formula:

        base_rate = 0.05 (5% baseline when FP ≥ 20)
        For every FP below 20: add 1% (capped at 50%)

    This is the architecture-plan canonical function for fracture probability.

    Args:
        item: Craft item dict with a ``forging_potential`` key.

    Returns:
        Fracture probability in [0.0, 0.50].
    """
    fp = max(0, item.get("forging_potential", 0))
    base_rate = 0.05
    if fp >= 20:
        return base_rate
    # Each missing FP below 20 adds 1% risk, capped at 50%
    extra = (20 - fp) * 0.01
    return min(0.50, base_rate + extra)


def _get_fp(item: dict) -> int:
    """Return FP from an item that may use either key name."""
    return int(item.get("forging_potential", item.get("forge_potential", 0)))


def _to_pipeline_item(item: dict) -> dict:
    """Convert a plan-format item (forging_potential + prefixes/suffixes/sealed_affix)
    into the modern pipeline format (forge_potential + affixes list).

    This allows simulate_craft_attempt to accept both item schemas.
    """
    fp = _get_fp(item)
    # Merge prefixes and suffixes into flat affixes list; mark sealed separately
    prefixes = item.get("prefixes", [])
    suffixes = item.get("suffixes", [])
    sealed  = item.get("sealed_affix")
    affixes = list(prefixes) + list(suffixes)
    if sealed:
        sealed_copy = dict(sealed)
        sealed_copy["sealed"] = True
        affixes.append(sealed_copy)
    return {
        "forge_potential": fp,
        "item_type": item.get("item_type", ""),
        "affixes": affixes,
        # Keep original keys for traceability
        "_original": item,
    }


def simulate_craft_attempt(
    item: dict,
    action: str,
    affix_name: str | None = None,
    target_tier: int | None = None,
    seed: int | None = None,
) -> dict:
    """Execute a single deterministic craft attempt, returning a full result dict.

    This is the architecture-plan canonical function for craft simulation.
    Unlike :func:`apply_craft_action` (which mutates in place), this function
    works on a deep copy and always returns a structured result regardless of
    success or failure.

    Accepts items in **either** format:
    - Plan format:    ``forging_potential`` + ``prefixes``/``suffixes``/``sealed_affix``
    - Pipeline format: ``forge_potential`` + ``affixes``

    The optional *seed* parameter makes the attempt fully deterministic for
    testing and reproducibility.

    Args:
        item: Current craft item dict (will not be mutated).
        action: Craft action to attempt.
        affix_name: Affix to add/upgrade/remove/seal (required for most actions).
        target_tier: Target tier for upgrade actions.
        seed: Optional RNG seed for deterministic output.

    Returns:
        Dict with keys:
        - ``success`` (bool)
        - ``action`` (str)
        - ``fracture_probability`` (float)
        - ``fractured`` (bool)
        - ``fp_spent`` (int)
        - ``fp_remaining`` (int)
        - ``item_before`` (dict)
        - ``item_after`` (dict)
        - ``reason`` (str)
    """
    rng = random.Random(seed)

    fp_before = _get_fp(item)
    item_before = copy.deepcopy(item)

    fracture_prob = calculate_fracture_probability(item)
    fractured = rng.random() < fracture_prob

    if fractured:
        item_after = copy.deepcopy(item)
        item_after["fractured"] = True
        return {
            "success": False,
            "action": action,
            "fracture_probability": round(fracture_prob, 4),
            "fractured": True,
            "fp_spent": 0,
            "fp_remaining": fp_before,
            "item_before": item_before,
            "item_after": item_after,
            "reason": f"Item fractured (probability was {fracture_prob:.1%})",
        }

    # Normalise to pipeline format for apply_craft_action.
    # Thread the local rng through so the FP-cost roll inside
    # apply_craft_action uses this same seeded RNG rather than the global
    # random module. Without this, the result depends on whatever global
    # random state preceding code happens to leave behind, and the seed
    # parameter only controls the fracture check — not the FP roll.
    pipeline_item = _to_pipeline_item(item)
    result = apply_craft_action(
        pipeline_item, action, affix_name, target_tier, rng=rng,
    )
    success = result.get("success", False)
    reason  = result.get("reason", result.get("message", ""))
    fp_after = int(pipeline_item.get("forge_potential", fp_before))
    fp_spent = max(0, fp_before - fp_after)

    # Return with the original item schema
    item_after = copy.deepcopy(item)
    if "forging_potential" in item_after:
        item_after["forging_potential"] = fp_after
    else:
        item_after["forge_potential"] = fp_after

    return {
        "success": success,
        "action": action,
        "fracture_probability": round(fracture_prob, 4),
        "fractured": False,
        "fp_spent": fp_spent,
        "fp_remaining": fp_after,
        "item_before": item_before,
        "item_after": item_after,
        "reason": reason,
    }
