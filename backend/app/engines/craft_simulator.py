"""
Crafting Monte Carlo Predictor — Upgrade 3

Simulates multi-step crafting sequences via seeded Monte Carlo iteration.
Each iteration executes the full action sequence on a deep copy of the item,
tracking success rates, fracture events, FP consumption, and affix tier
outcomes.

Rules enforced:
- Deterministic: seeded RNG, identical inputs → identical outputs
- No mutation of input item
- No magic numbers: all limits from constants.json
- Telemetry: execution_time and iterations exposed on every result
"""

from __future__ import annotations

import copy
import json
import math
import os
import random as _random_module
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.engines.craft_engine import (
    calculate_fracture_probability,
    calculate_success_probability,
    apply_craft_action as _apply_action,
    fp_cost,
)
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONSTANTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CraftSimulationResult:
    """Full Monte Carlo crafting simulation output."""
    success_rate:           float   # fraction of paths that completed without fracture
    fracture_rate:          float   # fraction of paths that fractured
    average_fp_remaining:   float   # mean FP at end of sequence
    median_fp_remaining:    float
    expected_affix_tiers:   dict    # affix_name → average tier achieved
    actions_completed_avg:  float   # average number of actions completed before stop
    fp_spent_avg:           float   # average total FP spent
    iterations:             int
    execution_time:         float

    def to_dict(self) -> dict:
        return {
            "success_rate":          round(self.success_rate, 4),
            "fracture_rate":         round(self.fracture_rate, 4),
            "average_fp_remaining":  round(self.average_fp_remaining, 2),
            "median_fp_remaining":   round(self.median_fp_remaining, 2),
            "expected_affix_tiers":  {k: round(v, 2) for k, v in self.expected_affix_tiers.items()},
            "actions_completed_avg": round(self.actions_completed_avg, 2),
            "fp_spent_avg":          round(self.fp_spent_avg, 2),
            "iterations":            self.iterations,
            "execution_time":        round(self.execution_time, 4),
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_fp(item: dict) -> int:
    """Read FP from either schema (forge_potential or forging_potential)."""
    return int(item.get("forging_potential", item.get("forge_potential", 0)))


def _set_fp(item: dict, value: int) -> None:
    if "forging_potential" in item:
        item["forging_potential"] = value
    else:
        item["forge_potential"] = value


def _to_pipeline_item(item: dict) -> dict:
    """Convert plan-format item to the modern apply_craft_action format.

    Supports both item schemas:
    - Plan format: ``forging_potential`` / ``prefixes`` / ``suffixes``
    - Pipeline format: ``forge_potential`` / ``affixes``
    """
    fp     = _get_fp(item)
    sealed = item.get("sealed_affix")
    # Prefer explicit affixes list; fall back to prefixes + suffixes
    if "affixes" in item:
        affixes = [dict(a) for a in item["affixes"] if not a.get("sealed")]
    else:
        prefixes = item.get("prefixes", [])
        suffixes = item.get("suffixes", [])
        affixes  = [dict(a) for a in list(prefixes) + list(suffixes)]
    if sealed:
        sc = dict(sealed)
        sc["sealed"] = True
        affixes.append(sc)
    return {"forge_potential": fp, "item_type": item.get("item_type", ""), "affixes": affixes}


def _get_affix_tiers(item: dict) -> dict[str, int]:
    """Return {affix_name → current tier} from any item schema."""
    result: dict[str, int] = {}
    for a in item.get("affixes", []):
        result[a.get("name", "")] = a.get("tier", 1)
    for a in item.get("prefixes", []) + item.get("suffixes", []):
        result[a.get("name", "")] = a.get("tier", 1)
    if item.get("sealed_affix"):
        sa = item["sealed_affix"]
        result[sa.get("name", "")] = sa.get("tier", 1)
    return result


# ---------------------------------------------------------------------------
# Single-iteration simulation
# ---------------------------------------------------------------------------

def _simulate_one_path(
    rng: _random_module.Random,
    item: dict,
    actions: list[dict],
    fracture_enabled: bool,
) -> tuple[bool, int, int, dict[str, int]]:
    """Execute one crafting path iteration.

    Returns:
        (completed_without_fracture, fp_remaining, actions_completed, affix_tiers)
    """
    item_copy = copy.deepcopy(item)
    fractured = False
    actions_done = 0

    for step in actions:
        action    = step.get("action", "")
        affix     = step.get("affix", step.get("affix_name"))
        target_t  = step.get("target_tier")

        fp = _get_fp(item_copy)
        expected_cost = fp_cost(action)
        if fp < expected_cost:
            break  # out of FP

        # Fracture check
        if fracture_enabled:
            frac_prob = calculate_fracture_probability(item_copy)
            if rng.random() < frac_prob:
                fractured = True
                break

        # Try the action via pipeline
        pipeline_item = _to_pipeline_item(item_copy)
        result = _apply_action(pipeline_item, action, affix, target_t)
        if not result.get("success", False):
            # Action failed (e.g. slots full) — skip and continue
            pass
        else:
            # Update FP from pipeline result
            new_fp = int(pipeline_item.get("forge_potential", fp))
            _set_fp(item_copy, new_fp)
            # Sync affixes back to plan-format item
            if "affixes" in pipeline_item:
                item_copy["affixes"] = pipeline_item["affixes"]
            actions_done += 1

    affix_tiers = _get_affix_tiers(item_copy)
    fp_remaining = _get_fp(item_copy)
    return not fractured, fp_remaining, actions_done, affix_tiers


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def simulate_crafting_path(
    item: dict,
    actions: list[dict],
    iterations: int = 5_000,
    seed: int = 42,
    fracture_enabled: bool = True,
) -> CraftSimulationResult:
    """Simulate a multi-step crafting sequence via Monte Carlo.

    This is the architecture-plan canonical function for craft prediction.

    Args:
        item: Craft item dict (will never be mutated).  Supports both item
            schemas (``forging_potential``/``prefixes``/``suffixes`` or
            ``forge_potential``/``affixes``).
        actions: Ordered list of craft steps, each a dict with:
            - ``action`` (str): "add_affix", "upgrade_affix", "remove_affix",
              "seal_affix" (or legacy: "upgrade", "add", "remove", "seal")
            - ``affix`` / ``affix_name`` (str): target affix name
            - ``target_tier`` (int, optional): tier cap for upgrade_affix
        iterations: Number of Monte Carlo iterations (default 5,000).
        seed: RNG seed for determinism (default 42).
        fracture_enabled: Whether fracture probability is applied each step
            (default True; set False for a deterministic "best case" path).

    Returns:
        :class:`CraftSimulationResult` with success_rate, fracture_rate,
        average_fp_remaining, expected_affix_tiers, and telemetry.
    """
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    if not actions:
        raise ValueError("actions list must not be empty")

    # Normalise legacy action names
    _ACTION_ALIASES = {
        "upgrade": "upgrade_affix",
        "add":     "add_affix",
        "remove":  "remove_affix",
        "seal":    "seal_affix",
    }
    norm_actions = [
        {**step, "action": _ACTION_ALIASES.get(step.get("action", ""), step.get("action", ""))}
        for step in actions
    ]

    log.info(
        "craft_simulation.start",
        iterations=iterations,
        seed=seed,
        n_actions=len(norm_actions),
        fracture_enabled=fracture_enabled,
    )

    t_start = time.perf_counter()
    rng = _random_module.Random(seed)

    successes: int = 0
    fractures: int = 0
    fp_remaining_list: list[float] = []
    actions_done_list: list[float] = []
    fp_spent_list:     list[float] = []
    affix_tier_totals: dict[str, float] = {}
    affix_tier_counts: dict[str, int]   = {}
    initial_fp = _get_fp(item)

    for _ in range(iterations):
        ok, fp_rem, n_done, tiers = _simulate_one_path(rng, item, norm_actions, fracture_enabled)
        if ok:
            successes += 1
        else:
            fractures += 1
        fp_remaining_list.append(float(fp_rem))
        actions_done_list.append(float(n_done))
        fp_spent_list.append(float(max(0, initial_fp - fp_rem)))
        for name, tier in tiers.items():
            affix_tier_totals[name] = affix_tier_totals.get(name, 0.0) + tier
            affix_tier_counts[name] = affix_tier_counts.get(name, 0) + 1

    elapsed = time.perf_counter() - t_start
    n = iterations

    fp_remaining_list.sort()
    avg_fp  = sum(fp_remaining_list) / n
    med_fp  = fp_remaining_list[n // 2]
    avg_act = sum(actions_done_list) / n
    avg_fp_spent = sum(fp_spent_list) / n

    expected_tiers = {
        name: affix_tier_totals[name] / affix_tier_counts[name]
        for name in affix_tier_totals
    }

    result = CraftSimulationResult(
        success_rate          = successes / n,
        fracture_rate         = fractures / n,
        average_fp_remaining  = avg_fp,
        median_fp_remaining   = med_fp,
        expected_affix_tiers  = expected_tiers,
        actions_completed_avg = avg_act,
        fp_spent_avg          = avg_fp_spent,
        iterations            = n,
        execution_time        = round(elapsed, 4),
    )
    log.info(
        "craft_simulation.done",
        success_rate=result.success_rate,
        fracture_rate=result.fracture_rate,
        elapsed=result.execution_time,
    )
    return result
