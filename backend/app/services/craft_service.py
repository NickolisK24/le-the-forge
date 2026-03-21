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
    compare_strategies,
    MAX_INSTABILITY,
    PERFECT_ROLL_THRESHOLD,
    FP_COSTS,
)
from app.engines.fp_engine import roll_session_fp_cost
from app.utils.exceptions import ItemFracturedError, InsufficientForgePotentialError

import random


def create_session(data: dict, user_id: Optional[str] = None) -> CraftSession:
    import secrets
    slug = secrets.token_urlsafe(8)

    session = CraftSession(
        user_id=user_id,
        slug=slug,
        item_type=data["item_type"],
        item_name=data.get("item_name"),
        item_level=data.get("item_level", 84),
        rarity=data.get("rarity", "Exalted"),
        instability=data.get("instability", 0),
        forge_potential=data.get("forge_potential", 28),
        affixes=data.get("affixes", []),
    )
    db.session.add(session)
    db.session.commit()
    return session


def apply_action(session: CraftSession, action: str, affix_name: Optional[str] = None,
                 target_tier: Optional[int] = None) -> dict:
    """
    Apply a single forge action to a session. Mutates the session in-place
    and appends a CraftStep log entry.
    """
    if session.is_fractured:
        raise ItemFracturedError()

    cost = roll_session_fp_cost(action)
    if session.forge_potential < cost:
        raise InsufficientForgePotentialError(needed=cost, available=session.forge_potential)

    sealed_count = sum(1 for a in session.affixes if a.get("sealed"))
    risk = fracture_risk(session.instability, sealed_count)
    risk_pct = round(risk * 100, 1)

    roll = random.uniform(0, 100)
    fractured = (roll / 100) < risk

    if fractured:
        outcome = "fracture"
        inst_gain = 0
        session.is_fractured = True
    elif roll > PERFECT_ROLL_THRESHOLD:
        outcome = "perfect"
        inst_gain = instability_gain(action, roll)
    else:
        outcome = "success"
        inst_gain = instability_gain(action, roll)

    inst_before = session.instability
    fp_before = session.forge_potential
    session.instability = min(MAX_INSTABILITY, session.instability + inst_gain)
    session.forge_potential = max(0, session.forge_potential - cost)

    if not fractured:
        _apply_affix_mutation(session, action, affix_name, target_tier)

    step_number = len(list(session.steps)) + 1
    step = CraftStep(
        session_id=session.id,
        step_number=step_number,
        action=action,
        affix_name=affix_name,
        tier_before=None,
        tier_after=target_tier,
        instability_before=inst_before,
        instability_after=session.instability,
        fracture_risk_pct=risk_pct,
        roll=round(roll, 2),
        outcome=outcome,
        fp_before=fp_before,
        fp_after=session.forge_potential,
    )
    db.session.add(step)
    db.session.commit()

    messages = {
        "success": f"Craft successful. +{inst_gain} instability.",
        "perfect": f"Perfect craft! Minimal instability gain (+{inst_gain}).",
        "fracture": "Item fractured. The forge claims another victim.",
    }

    return {
        "success": outcome != "fracture",
        "outcome": outcome,
        "fracture_risk_pct": risk_pct,
        "roll": round(roll, 2),
        "instability": session.instability,
        "forge_potential": session.forge_potential,
        "is_fractured": session.is_fractured,
        "message": messages[outcome],
        "step_number": step_number,
    }


def _apply_affix_mutation(session: CraftSession, action: str,
                           affix_name: Optional[str], target_tier: Optional[int]):
    affixes = session.affixes or []

    if action == "add_affix" and affix_name:
        # Only unsealed affixes count toward prefix/suffix limits; sealed is a separate slot (max 1)
        prefix_count = sum(1 for a in affixes if a.get("type") == "prefix" and not a.get("sealed"))
        suffix_count = sum(1 for a in affixes if a.get("type") == "suffix" and not a.get("sealed"))
        active_count = sum(1 for a in affixes if not a.get("sealed"))
        affix_def = AffixDef.query.filter_by(name=affix_name).first()
        affix_type = affix_def.affix_type if affix_def else None
        if affix_type == "prefix" and prefix_count >= 2:
            raise ValueError("Prefix slots full (max 2 active prefixes).")
        if affix_type == "suffix" and suffix_count >= 2:
            raise ValueError("Suffix slots full (max 2 active suffixes).")
        if active_count >= 4:
            raise ValueError("Item already has 4 active affixes.")
        affixes.append({"name": affix_name, "tier": target_tier or 1, "sealed": False, "type": affix_type})

    elif action == "upgrade_affix" and affix_name:
        for a in affixes:
            if a["name"] == affix_name and not a.get("sealed"):
                a["tier"] = min(5, (a.get("tier") or 1) + 1)
                break

    elif action == "seal_affix" and affix_name:
        sealed_count = sum(1 for a in affixes if a.get("sealed"))
        if sealed_count >= 1:
            raise ValueError("Only 1 affix can be sealed at a time.")
        for a in affixes:
            if a["name"] == affix_name:
                a["sealed"] = True
                break

    elif action == "unseal_affix" and affix_name:
        for a in affixes:
            if a["name"] == affix_name:
                a["sealed"] = False
                break

    elif action == "remove_affix" and affix_name:
        session.affixes = [a for a in affixes if a["name"] != affix_name]
        return

    session.affixes = affixes


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
