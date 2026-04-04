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
    fp_cost,
    optimal_path_search,
    simulate_sequence,
    compare_strategies,
    FP_COSTS,
)
from app.engines.fp_engine import roll_session_fp_cost
from app.engines.item_engine import create_item
from app.utils.exceptions import InsufficientForgePotentialError

import random


# ---------------------------------------------------------------------------
# Craft Session Engine
# ---------------------------------------------------------------------------

class CraftSessionManager:
    """
    Runtime craft session manager. Maintains item state, applies actions,
    tracks history, and allows undo operations.

    Responsibilities:
    - Maintain item state (FP, affixes)
    - Apply craft actions using unified pipeline
    - Track full action history
    - Allow undo of last action
    - Provide current state snapshots
    """

    def __init__(self, initial_item: dict):
        """
        Initialize with item dict:
        {
            "forge_potential": int,
            "affixes": list[dict]
        }
        """
        self.current_item = initial_item.copy()
        self.history: list[dict] = []  # List of action results
        self.undo_stack: list[dict] = []  # Stack of previous item states for undo

    def apply(self, action: str, affix_name: Optional[str] = None,
              target_tier: Optional[int] = None) -> dict:
        """
        Apply a craft action to the current item.

        Returns the action result dict from apply_craft_action.
        """
        # Save current state for undo
        self.undo_stack.append(self.current_item.copy())

        # Apply the action
        result = apply_craft_action(
            self.current_item,
            action,
            affix_name,
            target_tier
        )

        # If action failed, restore state and don't add to history
        if not result["success"]:
            self.current_item = self.undo_stack.pop()
            return result

        # Add to history
        self.history.append(result)

        return result

    def undo(self) -> bool:
        """
        Undo the last action. Restores the previous item state.

        Returns True if undo was successful, False if no actions to undo.
        """
        if not self.undo_stack:
            return False

        # Restore previous state
        self.current_item = self.undo_stack.pop()

        # Remove last history entry
        if self.history:
            self.history.pop()

        return True

    def get_state(self) -> dict:
        """
        Get current item state plus history.
        """
        return {
            "item": self.current_item.copy(),
            "history": self.history.copy(),
            "can_undo": len(self.undo_stack) > 0
        }

    def get_item(self) -> dict:
        """Get current item state."""
        return self.current_item.copy()

    def get_history(self) -> list[dict]:
        """Get action history."""
        return self.history.copy()


# ---------------------------------------------------------------------------
# Undo System
# ---------------------------------------------------------------------------

def undo_last_action(item: dict, history: list[dict]) -> dict:
    """
    Undo the last craft action on an item.

    Required Behavior:
    - Restore previous FP
    - Restore previous affix state
    - Remove last history entry

    Returns updated item dict.
    """
    if not history:
        return item  # No actions to undo

    last_action = history[-1]

    # Reverse the changes from the last action
    item["forge_potential"] += last_action.get("fp_cost", 0)

    # For affixes, we need to reverse the specific action
    # This is simplified - in practice, we'd need to track exact changes
    action = last_action.get("action")
    affix_name = last_action.get("affix_name")

    if action == "add_affix" and affix_name:
        # Remove the added affix
        item["affixes"] = [a for a in item["affixes"] if a["name"] != affix_name]
    elif action == "upgrade_affix" and affix_name:
        # Downgrade the tier
        for a in item["affixes"]:
            if a["name"] == affix_name:
                a["tier"] = max(1, a.get("tier", 1) - 1)
                break
    elif action == "seal_affix" and affix_name:
        # Unseal
        for a in item["affixes"]:
            if a["name"] == affix_name:
                a["sealed"] = False
                break
    elif action == "unseal_affix" and affix_name:
        # Reseal
        for a in item["affixes"]:
            if a["name"] == affix_name:
                a["sealed"] = True
                break
    elif action == "remove_affix" and affix_name:
        # Re-add the removed affix (simplified - assume tier 1)
        item["affixes"].append({"name": affix_name, "tier": 1, "sealed": False})

    # Remove from history
    history.pop()

    return item


def create_session(data: dict, user_id: Optional[str] = None) -> CraftSession:
    import secrets
    slug = secrets.token_urlsafe(8)

    fp_mode = data.get("fp_mode", "random")
    manual_fp = data.get("manual_fp")
    item_type = data["item_type"]
    rarity = data.get("rarity", "Rare")
    item_level = data.get("item_level", 84)

    # If caller supplied forge_potential directly, treat as manual override
    if data.get("forge_potential") is not None and fp_mode == "random":
        fp_mode = "manual"
        manual_fp = data["forge_potential"]

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
    affixes_before = session.affixes or []
    item = {
        "forge_potential": session.forge_potential,
        "affixes": affixes_before.copy()
    }

    # Apply the unified craft action
    result = apply_craft_action(item, action, affix_name, target_tier)

    if not result["success"]:
        # Restore FP if failed
        session.forge_potential = item["forge_potential"] + result.get("fp_cost", 0)
        raise InsufficientForgePotentialError(needed=result.get("fp_cost", 0), available=session.forge_potential)

    # Update session from result
    session.forge_potential = result["item"]["forge_potential"]
    session.affixes = result["item"]["affixes"]

    # Log the step
    step_number = len(list(session.steps)) + 1
    step = CraftStep(
        session_id=session.id,
        step_number=step_number,
        action=action,
        affix_name=affix_name,
        tier_before=next((a["tier"] for a in affixes_before if a.get("name") == affix_name), None),
        tier_after=target_tier,
        roll=result["roll"],
        outcome=result["outcome"],
        fp_before=result["item"]["forge_potential"] + result["fp_cost"],
        fp_after=result["item"]["forge_potential"],
        affixes_before=affixes_before,
    )
    db.session.add(step)
    db.session.commit()

    return {
        "success": result["success"],
        "outcome": result["outcome"],
        "roll": result["roll"],
        "forge_potential": session.forge_potential,
        "message": result["message"],
        "step_number": step_number,
    }


def get_session_summary(session: CraftSession) -> dict:
    """Return aggregate stats + optimal path + Monte Carlo simulation."""
    steps = list(session.steps)
    total = len(steps)
    successes = sum(1 for s in steps if s.outcome == "success")
    perfects = sum(1 for s in steps if s.outcome == "perfect")

    path = optimal_path_search(
        session.affixes or [],
        session.forge_potential,
    )

    sim_steps = [
        {"action": s["action"], "sealed_count_at_step": s["sealed_count_at_step"]}
        for s in path
    ]
    sim_result = simulate_sequence(
        session.forge_potential,
        sim_steps,
        n_simulations=10_000,
    ) if sim_steps else {
        "completion_chance": 1.0,
        "step_survival_curve": [],
        "n_simulations": 0,
    }

    strategies = compare_strategies(
        session.affixes or [],
        session.forge_potential,
    )

    return {
        "total_actions": total,
        "successes": successes,
        "perfects": perfects,
        "fp_spent": sum(fp_cost(s.action) for s in steps),
        "optimal_path": path,
        "simulation_result": sim_result,
        "strategy_comparison": strategies,
    }
