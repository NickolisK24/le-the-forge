"""
H16 — Conditional Mechanics Regression Suite

Protects against regressions in four core conditional scenarios:
  1. Shock damage bonus  — amplifier status boosts incoming damage
  2. Crit-trigger buff   — on_crit event activates a timed damage buff
  3. Health threshold bonus — extra damage below 50 % HP
  4. Status stacking effects — stacked DoTs accumulate correctly
"""
import pytest
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from modifiers.conditional_modifier_engine import ConditionalModifierEngine
from state.state_engine import SimulationState
from status.models.status_effect import StatusEffect
from status.status_manager import StatusManager
from events.event_trigger import EventTrigger, TriggerRegistry
from buffs.buff_trigger_integration import BuffTriggerIntegration
from app.services.state_encounter_integration import StateEncounterIntegration


# ---------------------------------------------------------------------------
# 1. Shock damage bonus
# ---------------------------------------------------------------------------
class TestShockDamageBonus:
    """
    Shock (status) should increase incoming spell_damage_pct by 20 % per stack.
    Modifier is conditioned on status_present("shock").
    """

    def test_shock_active_boosts_damage(self):
        state = SimulationState(
            player_health=1.0, player_max_health=1.0,
            target_health=0.8, target_max_health=1.0,
            active_status_effects={"shock": 1},
        )
        cond = Condition("shock", "status_present")
        mod  = ConditionalModifier("shock_amp", "spell_damage_pct", 20.0, "additive", cond)
        result = StateEncounterIntegration().evaluate_damage(1000.0, [mod], state)
        assert result.adjusted_damage == pytest.approx(1200.0)

    def test_shock_absent_no_boost(self):
        state = SimulationState(
            player_health=1.0, player_max_health=1.0,
            target_health=0.8, target_max_health=1.0,
        )
        cond = Condition("shock", "status_present")
        mod  = ConditionalModifier("shock_amp", "spell_damage_pct", 20.0, "additive", cond)
        result = StateEncounterIntegration().evaluate_damage(1000.0, [mod], state)
        assert result.adjusted_damage == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# 2. Crit-trigger buff
# ---------------------------------------------------------------------------
class TestCritTriggerBuff:
    """
    An on_crit trigger activates 'crit_buff' for 3 seconds.
    After the buff expires, on_buff_expire fires.
    """

    def test_crit_activates_buff(self):
        state = SimulationState(
            player_health=1.0, player_max_health=1.0,
            target_health=1.0, target_max_health=1.0,
        )
        bti = BuffTriggerIntegration()
        reg = TriggerRegistry()
        reg.register(EventTrigger(
            "crit_to_buff", "on_crit",
            callback=lambda ctx: bti.activate_buff("crit_buff", state, ctx["time"], duration=3.0)
        ))
        reg.fire("on_crit", {"time": 1.0})
        assert "crit_buff" in state.active_buffs

    def test_buff_expires_fires_event(self):
        fired = []
        state = SimulationState(
            player_health=1.0, player_max_health=1.0,
            target_health=1.0, target_max_health=1.0,
        )
        bti = BuffTriggerIntegration()
        reg = TriggerRegistry()
        reg.register(EventTrigger(
            "exp_listener", "on_buff_expire",
            callback=lambda ctx: fired.append(ctx["buff_id"])
        ))
        bti.activate_buff("crit_buff", state, now=0.0, duration=3.0)
        bti.tick(state, now=4.0, registry=reg)
        assert "crit_buff" in fired


# ---------------------------------------------------------------------------
# 3. Health threshold bonus
# ---------------------------------------------------------------------------
class TestHealthThresholdBonus:
    """
    At < 50 % target HP, spell_damage_pct increases by 40 %.
    At >= 50 % HP, no modifier applies.
    """

    def _eval(self, target_pct: float) -> float:
        state = SimulationState(
            player_health=1.0, player_max_health=1.0,
            target_health=target_pct, target_max_health=1.0,
        )
        cond = Condition("c", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        mod  = ConditionalModifier("hp_bonus", "spell_damage_pct", 40.0, "additive", cond)
        return StateEncounterIntegration().evaluate_damage(1000.0, [mod], state).adjusted_damage

    def test_below_threshold_bonus_applies(self):
        assert self._eval(0.3) == pytest.approx(1400.0)

    def test_above_threshold_no_bonus(self):
        assert self._eval(0.7) == pytest.approx(1000.0)

    def test_at_exact_boundary_no_bonus(self):
        # condition is "lt" 0.5, so exactly 0.5 does NOT trigger
        assert self._eval(0.5) == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# 4. Status stacking effects
# ---------------------------------------------------------------------------
class TestStatusStackingEffects:
    """
    Ignite stacks up to 5. Each stack adds 50 DPS.
    Stacks expire after 3 s each.
    """

    def test_five_stacks_correct_value(self):
        ignite = StatusEffect("ignite", duration=3.0, stack_limit=5, effect_type="dot", value=50.0)
        mgr = StatusManager()
        mgr.register(ignite)
        for _ in range(5):
            mgr.apply("ignite", now=0.0)
        assert mgr.total_value("ignite") == pytest.approx(250.0)

    def test_stacks_capped_at_limit(self):
        ignite = StatusEffect("ignite", duration=3.0, stack_limit=5, effect_type="dot", value=50.0)
        mgr = StatusManager()
        mgr.register(ignite)
        for _ in range(10):
            mgr.apply("ignite", now=0.0)
        assert mgr.stack_count("ignite") == 5

    def test_expired_stacks_reduce_value(self):
        ignite = StatusEffect("ignite", duration=2.0, stack_limit=5, effect_type="dot", value=50.0)
        mgr = StatusManager()
        mgr.register(ignite)
        mgr.apply("ignite", now=0.0)
        mgr.apply("ignite", now=0.0)
        mgr.apply("ignite", now=3.0)  # fresh stack applied later
        mgr.tick(now=2.5)             # first two should expire (0+2 < 2.5 → expired)
        assert mgr.stack_count("ignite") == 1
        assert mgr.total_value("ignite") == pytest.approx(50.0)
