"""
H2 — Condition Evaluator

Evaluates a Condition against a SimulationState snapshot.
Returns True when the condition is satisfied, False otherwise.

Numeric types (target_health_pct, player_health_pct, time_elapsed) are
evaluated by comparing the relevant state field against threshold_value
using the condition's comparison_operator.

Presence types (buff_active, status_present) check membership in the
state's active_buffs / active_status_effects collections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from conditions.models.condition import Condition

if TYPE_CHECKING:
    from state.state_engine import SimulationState


class ConditionEvaluator:
    """
    Stateless evaluator — construct once, call evaluate() many times.

    evaluate(condition, state) → bool
    evaluate_all(conditions, state) → bool   (all must be True)
    evaluate_any(conditions, state) → bool   (at least one must be True)
    """

    def evaluate(self, condition: Condition, state: "SimulationState") -> bool:
        """Return True when *condition* is satisfied by *state*."""
        ct = condition.condition_type

        if ct == "target_health_pct":
            actual = state.target_health_pct
            return condition.evaluate_numeric(actual)

        if ct == "player_health_pct":
            actual = state.player_health_pct
            return condition.evaluate_numeric(actual)

        if ct == "time_elapsed":
            return condition.evaluate_numeric(state.elapsed_time)

        if ct == "buff_active":
            return condition.condition_id in state.active_buffs

        if ct == "status_present":
            return condition.condition_id in state.active_status_effects

        raise ValueError(f"Unhandled condition_type: {ct!r}")

    def evaluate_all(
        self,
        conditions: list[Condition],
        state: "SimulationState",
    ) -> bool:
        """Return True only when every condition in *conditions* is satisfied."""
        return all(self.evaluate(c, state) for c in conditions)

    def evaluate_any(
        self,
        conditions: list[Condition],
        state: "SimulationState",
    ) -> bool:
        """Return True when at least one condition in *conditions* is satisfied."""
        return any(self.evaluate(c, state) for c in conditions)
