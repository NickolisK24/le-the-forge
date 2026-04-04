"""H13 — State-Encounter Integration tests."""
import pytest
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from state.state_engine import SimulationState
from app.services.state_encounter_integration import StateEncounterIntegration


def _state(target_pct=1.0):
    return SimulationState(
        player_health=1.0, player_max_health=1.0,
        target_health=target_pct, target_max_health=1.0,
    )


def _mod(mid, value, mtype="additive", target_pct=0.5) -> ConditionalModifier:
    cond = Condition(mid + "_c", "target_health_pct",
                     threshold_value=target_pct, comparison_operator="lt")
    return ConditionalModifier(mid, "spell_damage_pct", value, mtype, cond)


svc = StateEncounterIntegration()


class TestConditionalDamageValidation:
    def test_no_modifier_no_change(self):
        result = svc.evaluate_damage(1000.0, [], _state(0.3))
        assert result.base_damage == 1000.0
        assert result.adjusted_damage == 1000.0
        assert result.damage_multiplier == pytest.approx(1.0)

    def test_active_modifier_boosts_damage(self):
        m = _mod("m1", 50.0)
        result = svc.evaluate_damage(1000.0, [m], _state(0.3))
        assert result.adjusted_damage == pytest.approx(1500.0)
        assert result.damage_multiplier == pytest.approx(1.5)

    def test_inactive_modifier_no_boost(self):
        m = _mod("m1", 50.0)
        result = svc.evaluate_damage(1000.0, [m], _state(0.8))
        assert result.adjusted_damage == pytest.approx(1000.0)


class TestStatusAwareResults:
    def test_active_modifier_ids_populated(self):
        m = _mod("shock_amp", 30.0)
        result = svc.evaluate_damage(500.0, [m], _state(0.3))
        assert "shock_amp" in result.active_modifier_ids

    def test_no_active_ids_when_inactive(self):
        m = _mod("shock_amp", 30.0)
        result = svc.evaluate_damage(500.0, [m], _state(0.9))
        assert result.active_modifier_ids == []

    def test_stat_deltas_returned(self):
        m = _mod("m1", 40.0)
        result = svc.evaluate_damage(1000.0, [m], _state(0.2))
        assert "spell_damage_pct" in result.stat_deltas
