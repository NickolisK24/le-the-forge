"""
H13 — State-Encounter Integration

Bridges the conditional mechanics engine (Phase H) with the encounter
simulation layer. Given a list of ConditionalModifiers, a SimulationState,
and a base damage value, this service:

  1. Evaluates which conditional modifiers are active
  2. Aggregates stat deltas from active modifiers
  3. Returns an adjusted damage value and an audit trail

This is intentionally stateless — the caller owns the SimulationState
and passes it in.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from modifiers.conditional_modifier_engine import ConditionalModifierEngine
from modifiers.models.conditional_modifier import ConditionalModifier
from state.state_engine import SimulationState


@dataclass
class ConditionalEncounterResult:
    """
    Output of a single conditional damage evaluation.

    base_damage      — damage before conditional modifiers
    adjusted_damage  — damage after applying active modifiers
    active_modifier_ids — modifiers that were active this evaluation
    stat_deltas      — aggregated stat adjustments that were applied
    """
    base_damage:          float
    adjusted_damage:      float
    active_modifier_ids:  list[str] = field(default_factory=list)
    stat_deltas:          dict[str, float] = field(default_factory=dict)

    @property
    def damage_multiplier(self) -> float:
        if self.base_damage == 0:
            return 1.0
        return self.adjusted_damage / self.base_damage


class StateEncounterIntegration:
    """
    Applies conditional modifiers to a base damage value.

    evaluate_damage(base_damage, modifiers, state) → ConditionalEncounterResult
    """

    def __init__(self) -> None:
        self._engine = ConditionalModifierEngine()

    def evaluate_damage(
        self,
        base_damage: float,
        modifiers: list[ConditionalModifier],
        state: SimulationState,
    ) -> ConditionalEncounterResult:
        """
        Evaluate all *modifiers* against *state* and apply active ones
        to *base_damage*.

        Only 'additive' and 'multiplicative' modifier_types affect damage
        directly. Override modifiers are included in stat_deltas but do not
        compound on the base damage in this simplified model.
        """
        stat_deltas = self._engine.evaluate(modifiers, state)
        active = self._engine.active_modifiers(modifiers, state)
        active_ids = [m.modifier_id for m in active]

        # Apply damage-related deltas
        # "spell_damage_pct" / "damage_pct" are treated as % additive to multiplier
        damage_bonus_pct = (
            stat_deltas.get("spell_damage_pct", 0.0)
            + stat_deltas.get("damage_pct", 0.0)
            + stat_deltas.get("physical_damage_pct", 0.0)
        )
        multiplier = 1.0 + damage_bonus_pct / 100.0
        adjusted = base_damage * max(0.0, multiplier)

        return ConditionalEncounterResult(
            base_damage=base_damage,
            adjusted_damage=adjusted,
            active_modifier_ids=active_ids,
            stat_deltas=stat_deltas,
        )
