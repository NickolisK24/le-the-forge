"""
buff_condition_evaluator — Condition gate for active buff stat application.

Evaluates each active buff's activation_condition against the current
SimulationState BEFORE stats are applied.  Buffs whose conditions fail
are suppressed: they remain in active_buffs (still ticking toward expiry)
but their stat modifiers must not be applied.

Evaluation rules:
  - activation_condition is None → always eligible (no gate)
  - activation_condition present → evaluated via ConditionEvaluator.evaluate()
  - All conditions are evaluated statelessly; no buff state is mutated

Public API:
    evaluate_buff_conditions(active_buffs, state) -> BuffConditionResult
    BuffConditionResult.eligible   — buffs whose conditions passed
    BuffConditionResult.suppressed — buffs whose conditions failed
"""

from __future__ import annotations

from dataclasses import dataclass

from conditions.condition_evaluator import ConditionEvaluator
from buffs.buff_instance import BuffInstance
from state.state_engine import SimulationState


_evaluator = ConditionEvaluator()


@dataclass(slots=True, frozen=True)
class BuffConditionResult:
    """Result of a condition evaluation pass over all active buffs.

    eligible   — buff_id → BuffInstance for buffs whose conditions passed.
                 Stat modifiers from these buffs should be applied.

    suppressed — buff_id → BuffInstance for buffs whose conditions failed.
                 Stat modifiers from these buffs must NOT be applied.
                 These buffs are still active and continue to tick.
    """
    eligible: dict[str, BuffInstance]
    suppressed: dict[str, BuffInstance]


def evaluate_buff_conditions(
    active_buffs: dict[str, BuffInstance],
    state: SimulationState,
) -> BuffConditionResult:
    """Evaluate each buff's activation_condition against *state*.

    Iterates over a snapshot of *active_buffs* so the input dict is never
    mutated and concurrent modification is safe.

    Args:
        active_buffs: current runtime buff state, keyed by buff_id.
        state:        current SimulationState used to resolve conditions.

    Returns:
        BuffConditionResult partitioning active_buffs into eligible and
        suppressed, based on each buff's activation_condition.
    """
    eligible: dict[str, BuffInstance] = {}
    suppressed: dict[str, BuffInstance] = {}

    for buff_id, instance in list(active_buffs.items()):
        condition = instance.definition.activation_condition

        if condition is None or _evaluator.evaluate(condition, state):
            eligible[buff_id] = instance
        else:
            suppressed[buff_id] = instance

    return BuffConditionResult(eligible=eligible, suppressed=suppressed)


def aggregate_eligible_modifiers(
    result: BuffConditionResult,
) -> dict[str, float]:
    """Aggregate stat modifiers from all eligible buffs.

    Calls BuffDefinition.aggregate_modifiers(stack_count) for each eligible
    buff and merges them additively into a flat stat_target → value dict.

    Only eligible buffs contribute.  Suppressed buffs are ignored entirely,
    enforcing the rule that conditions are evaluated before stat application.

    Args:
        result: output of evaluate_buff_conditions.

    Returns:
        Flat dict of stat_target → total modifier value across all eligible
        buffs and their current stack counts.
    """
    totals: dict[str, float] = {}

    for instance in result.eligible.values():
        modifiers = instance.definition.aggregate_modifiers(instance.stack_count)
        for stat_target, value in modifiers.items():
            totals[stat_target] = totals.get(stat_target, 0.0) + value

    return totals
