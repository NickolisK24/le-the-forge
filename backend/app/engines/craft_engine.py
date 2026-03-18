"""
Craft Engine — pure crafting math extracted from craft_service.py.

All functions here are stateless and have no DB or HTTP dependencies.
craft_service.py imports from here for its calculations.
"""

import copy
import random
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_INSTABILITY = 80
FP_COSTS = {
    "add_affix": 4,
    "upgrade_affix": 5,
    "seal_affix": 8,
    "unseal_affix": 2,
    "remove_affix": 3,
}
INSTABILITY_GAINS = {
    "add_affix": (3, 7),
    "upgrade_affix": (4, 10),
    "seal_affix": (0, 0),
    "unseal_affix": (1, 3),
    "remove_affix": (2, 5),
}
PERFECT_ROLL_THRESHOLD = 95
SEAL_RISK_THRESHOLD = 0.20
TARGET_TIER = 4


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
    lo, hi = INSTABILITY_GAINS.get(action, (3, 8))
    if lo == hi:
        return lo
    if roll and roll > PERFECT_ROLL_THRESHOLD:
        return lo
    return random.randint(lo, hi)


def expected_instability_gain(action: str) -> float:
    """Expected (mean) instability gain accounting for 5% perfect rolls."""
    lo, hi = INSTABILITY_GAINS.get(action, (3, 8))
    if lo == hi:
        return float(lo)
    perfect_prob = 0.05
    normal_mean = (lo + hi) / 2.0
    return perfect_prob * lo + (1 - perfect_prob) * normal_mean


def fp_cost(action: str) -> int:
    return FP_COSTS.get(action, 4)


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

            lo, hi = INSTABILITY_GAINS.get(action, (3, 8))
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
