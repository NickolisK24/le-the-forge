"""
H17 — Conditional Mechanics Performance Benchmarks

Measures that key operations complete within acceptable time bounds.
All benchmarks run without any external I/O or DB access.
"""
import time
import pytest

from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from modifiers.conditional_modifier_engine import ConditionalModifierEngine
from state.state_engine import SimulationState
from status.models.status_effect import StatusEffect
from status.status_manager import StatusManager
from events.event_trigger import EventTrigger, TriggerRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _state(target_pct=0.3):
    return SimulationState(
        player_health=1.0, player_max_health=1.0,
        target_health=target_pct, target_max_health=1.0,
    )


def _mod(n: int) -> ConditionalModifier:
    cond = Condition(f"c{n}", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
    return ConditionalModifier(f"m{n}", "spell_damage_pct", float(n), "additive", cond)


def _elapsed(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


# ---------------------------------------------------------------------------
# H17.1 — Condition evaluation scaling
# ---------------------------------------------------------------------------

class TestConditionEvaluationScaling:
    def test_1000_modifiers_evaluated_fast(self):
        mods = [_mod(i) for i in range(1000)]
        engine = ConditionalModifierEngine()
        state = _state()

        elapsed = _elapsed(lambda: engine.evaluate(mods, state))
        assert elapsed < 0.1, f"1000-modifier evaluation took {elapsed:.3f}s (limit 0.1s)"

    def test_10000_evaluations_per_second(self):
        mods = [_mod(i) for i in range(10)]
        engine = ConditionalModifierEngine()
        state = _state()
        N = 10_000

        elapsed = _elapsed(lambda: [engine.evaluate(mods, state) for _ in range(N)])
        rate = N / elapsed
        assert rate > 5_000, f"Rate {rate:.0f}/s < 5000/s"


# ---------------------------------------------------------------------------
# H17.2 — Status stacking overhead
# ---------------------------------------------------------------------------

class TestStatusStackingOverhead:
    def test_1000_status_applies_fast(self):
        shock = StatusEffect("shock", duration=10.0, stack_limit=None)
        mgr = StatusManager()
        mgr.register(shock)

        elapsed = _elapsed(lambda: [mgr.apply("shock", now=0.0) for _ in range(1000)])
        assert elapsed < 0.05, f"1000 status applies took {elapsed:.3f}s (limit 0.05s)"

    def test_tick_1000_expirations_fast(self):
        shock = StatusEffect("shock", duration=1.0, stack_limit=None)
        mgr = StatusManager()
        mgr.register(shock)
        for _ in range(1000):
            mgr.apply("shock", now=0.0)

        elapsed = _elapsed(lambda: mgr.tick(now=2.0))
        assert elapsed < 0.05, f"1000-expiration tick took {elapsed:.3f}s (limit 0.05s)"


# ---------------------------------------------------------------------------
# H17.3 — Trigger performance
# ---------------------------------------------------------------------------

class TestTriggerPerformance:
    def test_100_triggers_fire_fast(self):
        reg = TriggerRegistry()
        fired = []
        for i in range(100):
            reg.register(EventTrigger(f"t{i}", "on_hit", callback=lambda ctx: fired.append(1)))

        elapsed = _elapsed(lambda: reg.fire("on_hit", {}))
        assert elapsed < 0.02, f"100 triggers took {elapsed:.3f}s (limit 0.02s)"

    def test_1000_fire_calls_fast(self):
        reg = TriggerRegistry()
        reg.register(EventTrigger("t1", "on_crit", callback=lambda ctx: None))

        elapsed = _elapsed(lambda: [reg.fire("on_crit", {}) for _ in range(1000)])
        assert elapsed < 0.1, f"1000 fire calls took {elapsed:.3f}s (limit 0.1s)"
