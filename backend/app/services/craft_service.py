"""
Craft Service — orchestrates DB operations for CraftSession and CraftStep.

Pure crafting math now lives in app.engines.craft_engine. This service
handles: session creation, applying actions, persisting audit steps, and
assembling the session summary.
"""

from typing import Optional

from app import db
from app.models import CraftSession, CraftStep, AffixDef
from app.engines.craft_engine import (
    fracture_risk,
    fracture_risk_pct,
    instability_gain,
    fp_cost,
    optimal_path_search,
    simulate_sequence,
    simulate_crafting_path,
    compare_strategies,
    MAX_INSTABILITY,
    PERFECT_ROLL_THRESHOLD,
    FP_COSTS,
)
from app.engines.fp_engine import roll_session_fp_cost
from app.engines.item_engine import create_item
from app.utils.exceptions import ItemFracturedError, InsufficientForgePotentialError

import random


def create_session(data: dict, user_id: Optional[str] = None) -> CraftSession:
    import secrets
    slug = secrets.token_urlsafe(8)

    fp_mode = data.get("fp_mode", "random")
    manual_fp = data.get("manual_fp")
    item_type = data["item_type"]
    rarity = data.get("rarity", "Rare")
    item_level = data.get("item_level", 84)

    # If caller supplied an explicit forging_potential, treat as manual override
    if "forging_potential" in data and fp_mode == "random":
        fp_mode = "manual"
        manual_fp = data["forging_potential"]

    result = create_item(item_type.lower(), rarity=rarity, item_level=item_level,
                         fp_mode=fp_mode, manual_fp=manual_fp)
    if not result["success"]:
        raise ValueError(result["reason"])

    forging_potential = result["item"]["forging_potential"]

    session = CraftSession(
        user_id=user_id,
        slug=slug,
        item_type=item_type,
        item_name=data.get("item_name"),
        item_level=item_level,
        rarity=rarity,
        instability=data.get("instability", 0),
        forge_potential=forging_potential,
        affixes=data.get("affixes", []),
    )
    db.session.add(session)
    db.session.commit()
    return session


from app.engines.craft_engine import apply_craft_action


def apply_action(session: CraftSession, action: str, affix_name: Optional[str] = None,
                 target_tier: Optional[int] = None) -> dict:
    """
    Apply a single forge action to a session using the unified craft pipeline.
    Mutates the session in-place and appends a CraftStep log entry.
    """
    # Create item dict from session
    item = {
        "forge_potential": session.forge_potential,
        "instability": session.instability,
        "is_fractured": session.is_fractured,
        "affixes": session.affixes or []
    }

    # Apply the unified craft action
    result = apply_craft_action(item, action, affix_name, target_tier)

    if not result["success"]:
        # Restore FP if failed
        session.forge_potential = item["forge_potential"] + result.get("fp_cost", 0)
        raise ItemFracturedError() if result["outcome"] == "error" and "fractured" in result["message"].lower() else InsufficientForgePotentialError(needed=result.get("fp_cost", 0), available=session.forge_potential)

    # Update session from result
    session.forge_potential = result["item"]["forge_potential"]
    session.instability = result["item"]["instability"]
    session.is_fractured = result["item"]["is_fractured"]
    session.affixes = result["item"]["affixes"]

    # Log the step
    step_number = len(list(session.steps)) + 1
    step = CraftStep(
        session_id=session.id,
        step_number=step_number,
        action=action,
        affix_name=affix_name,
        tier_before=None,  # TODO: track tier before
        tier_after=target_tier,
        instability_before=result["item"]["instability"] - result["instability_gain"],
        instability_after=result["item"]["instability"],
        fracture_risk_pct=result["fracture_risk_pct"],
        roll=result["roll"],
        outcome=result["outcome"],
        fp_before=result["item"]["forge_potential"] + result["fp_cost"],
        fp_after=result["item"]["forge_potential"],
    )
    db.session.add(step)
    db.session.commit()

    return {
        "success": result["success"],
        "outcome": result["outcome"],
        "fracture_risk_pct": result["fracture_risk_pct"],
        "roll": result["roll"],
        "instability": session.instability,
        "forge_potential": session.forge_potential,
        "is_fractured": session.is_fractured,
        "message": result["message"],
        "step_number": step_number,
    }


def get_session_summary(session: CraftSession) -> dict:
    """Return aggregate stats + optimal path + Monte Carlo simulation."""
    steps = list(session.steps)
    total = len(steps)
    successes = sum(1 for s in steps if s.outcome == "success")
    perfects = sum(1 for s in steps if s.outcome == "perfect")
    sealed_count = sum(1 for a in (session.affixes or []) if a.get("sealed"))

    path = optimal_path_search(
        session.instability,
        session.affixes or [],
        session.forge_potential,
    )

    sim_steps = [
        {"action": s["action"], "sealed_count_at_step": s["sealed_count_at_step"]}
        for s in path
    ]
    sim_result = simulate_sequence(
        session.instability,
        session.forge_potential,
        sim_steps,
        n_simulations=10_000,
    ) if sim_steps else {
        "brick_chance": 0.0,
        "perfect_item_chance": 1.0,
        "step_survival_curve": [],
        "step_fracture_rates": [],
        "median_instability": session.instability,
        "n_simulations": 0,
    }

    strategies = compare_strategies(
        session.instability,
        session.affixes or [],
        session.forge_potential,
    )

    return {
        "total_actions": total,
        "successes": successes,
        "perfects": perfects,
        "fractures": 1 if session.is_fractured else 0,
        "fp_spent": sum(fp_cost(s.action) for s in steps),
        "current_risk_pct": fracture_risk_pct(session.instability, sealed_count),
        "optimal_path": path,
        "simulation_result": sim_result,
        "strategy_comparison": strategies,
    }
