"""
Conditional Modifier Calculator — situational damage bonuses.

Conditional modifiers apply additional bonuses only when specific game-state
conditions are satisfied at the time of the hit. They are evaluated against
a ConditionContext that captures the relevant state for that hit.

Supported conditions:
  ON_CRIT        — active when the hit is a critical strike
  LOW_HEALTH     — active when the target's health % is at or below a threshold
  TARGET_STUNNED — active when the target has the Stunned status effect
  TARGET_FROZEN  — active when the target has the Frozen status effect

Usage in the damage pipeline:
  active_bonus = evaluate_modifiers(modifiers, ctx)
  # Treat as additional increased% — add to the increased_damage pool:
  increased = existing_increased + active_bonus
  # Or, for more-type bonuses, pass each active modifier's bonus_pct
  # individually to the more_damage list in DamageContext.

All functions are pure: no registry access, no Flask context, no I/O.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Sequence


class Condition(enum.Enum):
    ON_CRIT        = "on_crit"
    LOW_HEALTH     = "low_health"
    TARGET_STUNNED = "target_stunned"
    TARGET_FROZEN  = "target_frozen"


@dataclass(frozen=True)
class ConditionContext:
    """Describes the hit-time state relevant to conditional modifier evaluation."""

    target_health_pct: float = 100.0  # Target's current health as % of max (0–100)
    is_crit:           bool  = False  # Whether this hit is a critical strike
    target_stunned:    bool  = False  # Target has the Stunned status effect
    target_frozen:     bool  = False  # Target has the Frozen status effect


@dataclass(frozen=True)
class ConditionalModifier:
    """A damage bonus that applies only when its condition is active."""

    condition: Condition
    bonus_pct: float     # Bonus magnitude in percentage points (e.g. 30.0 = +30%)
    threshold: float = 35.0  # LOW_HEALTH only: health% threshold (inclusive)


def _is_active(mod: ConditionalModifier, ctx: ConditionContext) -> bool:
    """Return True if the modifier's condition is satisfied by the context."""
    if mod.condition == Condition.ON_CRIT:
        return ctx.is_crit
    if mod.condition == Condition.LOW_HEALTH:
        return ctx.target_health_pct <= mod.threshold
    if mod.condition == Condition.TARGET_STUNNED:
        return ctx.target_stunned
    if mod.condition == Condition.TARGET_FROZEN:
        return ctx.target_frozen
    return False


def evaluate_modifiers(
    modifiers: Sequence[ConditionalModifier],
    ctx: ConditionContext,
) -> float:
    """
    Sum the bonus_pct of all modifiers whose conditions are active.

    Multiple active modifiers stack additively. Returns 0.0 when no
    conditions are met or the modifier list is empty.
    """
    return sum(mod.bonus_pct for mod in modifiers if _is_active(mod, ctx))
