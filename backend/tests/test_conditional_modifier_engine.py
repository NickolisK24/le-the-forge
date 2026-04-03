"""H9 — Conditional Modifier Engine tests."""
import pytest
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from modifiers.conditional_modifier_engine import ConditionalModifierEngine
from state.state_engine import SimulationState


def _state(target_pct=1.0, player_pct=1.0, elapsed=0.0, buffs=None) -> SimulationState:
    s = SimulationState(
        player_health=player_pct, player_max_health=1.0,
        target_health=target_pct, target_max_health=1.0,
        elapsed_time=elapsed,
        active_buffs=set(buffs or []),
    )
    return s


def _mod(mid, stat, value, mtype, cond) -> ConditionalModifier:
    return ConditionalModifier(mid, stat, value, mtype, cond)


def _cond_target_lt(pct, cid="c") -> Condition:
    return Condition(cid, "target_health_pct", threshold_value=pct, comparison_operator="lt")


engine = ConditionalModifierEngine()


class TestModifierActivationTiming:
    def test_inactive_when_condition_false(self):
        m = _mod("m1", "spell_damage_pct", 20.0, "additive", _cond_target_lt(0.5))
        result = engine.evaluate([m], _state(target_pct=0.8))
        assert result == {}

    def test_active_when_condition_true(self):
        m = _mod("m1", "spell_damage_pct", 20.0, "additive", _cond_target_lt(0.5))
        result = engine.evaluate([m], _state(target_pct=0.3))
        assert result["spell_damage_pct"] == 20.0


class TestModifierRemovalTiming:
    def test_becomes_inactive_when_hp_rises(self):
        m = _mod("m1", "spell_damage_pct", 20.0, "additive", _cond_target_lt(0.5))
        assert engine.evaluate([m], _state(target_pct=0.3)) == {"spell_damage_pct": 20.0}
        assert engine.evaluate([m], _state(target_pct=0.7)) == {}


class TestMultipleModifiers:
    def test_additive_stack(self):
        c = _cond_target_lt(0.5)
        m1 = _mod("m1", "spell_damage_pct", 20.0, "additive", c)
        m2 = _mod("m2", "spell_damage_pct", 15.0, "additive", c)
        result = engine.evaluate([m1, m2], _state(target_pct=0.3))
        assert result["spell_damage_pct"] == 35.0

    def test_multiplicative_compounds(self):
        c = _cond_target_lt(0.5)
        m1 = _mod("m1", "spell_damage_pct", 20.0, "multiplicative", c)
        m2 = _mod("m2", "spell_damage_pct", 10.0, "multiplicative", c)
        result = engine.evaluate([m1, m2], _state(target_pct=0.3))
        # (1.2 * 1.1 - 1) * 100 = 32.0%
        assert abs(result["spell_damage_pct"] - 32.0) < 1e-6

    def test_override_wins(self):
        c = _cond_target_lt(0.5)
        m1 = _mod("m1", "spell_damage_pct", 20.0, "additive",  c)
        m2 = _mod("m2", "spell_damage_pct", 99.0, "override", c)
        result = engine.evaluate([m1, m2], _state(target_pct=0.3))
        assert result["spell_damage_pct"] == 99.0

    def test_active_modifiers_filter(self):
        c = _cond_target_lt(0.5)
        m1 = _mod("m1", "spell_damage_pct", 20.0, "additive", c)
        m2 = _mod("m2", "crit_chance",       5.0,  "additive", Condition("b", "buff_active"))
        state = _state(target_pct=0.3)
        active = engine.active_modifiers([m1, m2], state)
        assert len(active) == 1
        assert active[0].modifier_id == "m1"
