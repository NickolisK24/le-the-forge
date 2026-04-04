"""
H9 — Conditional Modifier Engine

Evaluates a list of ConditionalModifiers against the current SimulationState
and produces an aggregated dict of active stat deltas. Modifiers whose
conditions are not met contribute nothing.

Additive modifiers sum their values per stat.
Multiplicative modifiers accumulate as compounding factors.
Override modifiers take the last registered value for that stat.
"""

from __future__ import annotations

from conditions.condition_evaluator import ConditionEvaluator
from modifiers.models.conditional_modifier import ConditionalModifier
from state.state_engine import SimulationState


class ConditionalModifierEngine:
    """
    evaluate(modifiers, state) → dict[stat_target, effective_value]

    Returns only stats that have at least one active modifier.
    Multiple additive modifiers on the same stat are summed.
    Multiple multiplicative modifiers on the same stat are chained:
        effective = (1 + v1/100) * (1 + v2/100) * … − 1  (as a percentage)
    Override: last modifier in list order wins.
    """

    def __init__(self) -> None:
        self._evaluator = ConditionEvaluator()

    def evaluate(
        self,
        modifiers: list[ConditionalModifier],
        state: SimulationState,
    ) -> dict[str, float]:
        """
        Return a dict of stat_target → effective delta for all active modifiers.
        """
        additive:       dict[str, float] = {}
        multiplicative: dict[str, float] = {}  # stored as cumulative (1+v/100) product
        override:       dict[str, float] = {}

        for mod in modifiers:
            if not self._evaluator.evaluate(mod.condition, state):
                continue

            st = mod.stat_target
            if mod.modifier_type == "additive":
                additive[st] = additive.get(st, 0.0) + mod.value
            elif mod.modifier_type == "multiplicative":
                factor = 1.0 + mod.value / 100.0
                multiplicative[st] = multiplicative.get(st, 1.0) * factor
            elif mod.modifier_type == "override":
                override[st] = mod.value

        result: dict[str, float] = {}

        # Merge additive
        for stat, val in additive.items():
            result[stat] = result.get(stat, 0.0) + val

        # Merge multiplicative — convert product back to percentage delta
        for stat, product in multiplicative.items():
            delta = (product - 1.0) * 100.0
            result[stat] = result.get(stat, 0.0) + delta

        # Override wins over everything
        result.update(override)

        return result

    def active_modifiers(
        self,
        modifiers: list[ConditionalModifier],
        state: SimulationState,
    ) -> list[ConditionalModifier]:
        """Return only the modifiers whose conditions are currently satisfied."""
        return [m for m in modifiers if self._evaluator.evaluate(m.condition, state)]
