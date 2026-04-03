"""H2 — Condition Evaluator tests."""
import pytest
from conditions.models.condition import Condition
from conditions.condition_evaluator import ConditionEvaluator
from state.state_engine import SimulationState


def _state(**kwargs) -> SimulationState:
    defaults = dict(
        player_health=800.0, player_max_health=1000.0,
        target_health=600.0, target_max_health=1000.0,
        elapsed_time=5.0,
    )
    defaults.update(kwargs)
    return SimulationState(**defaults)


ev = ConditionEvaluator()


class TestHealthEvaluation:
    def test_target_below_50pct_true(self):
        state = _state(target_health=400.0, target_max_health=1000.0)
        c = Condition("c", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        assert ev.evaluate(c, state) is True

    def test_target_below_50pct_false(self):
        state = _state(target_health=600.0, target_max_health=1000.0)
        c = Condition("c", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        assert ev.evaluate(c, state) is False

    def test_player_health_pct(self):
        state = _state(player_health=200.0, player_max_health=1000.0)
        c = Condition("c", "player_health_pct", threshold_value=0.3, comparison_operator="lt")
        assert ev.evaluate(c, state) is True


class TestStatusDetection:
    def test_status_present_true(self):
        state = _state()
        state.active_status_effects["shock"] = 2
        c = Condition("shock", "status_present")
        assert ev.evaluate(c, state) is True

    def test_status_present_false(self):
        state = _state()
        c = Condition("shock", "status_present")
        assert ev.evaluate(c, state) is False


class TestTimeEvaluation:
    def test_time_ge_true(self):
        state = _state(elapsed_time=10.0)
        c = Condition("c", "time_elapsed", threshold_value=5.0, comparison_operator="ge")
        assert ev.evaluate(c, state) is True

    def test_time_ge_false(self):
        state = _state(elapsed_time=3.0)
        c = Condition("c", "time_elapsed", threshold_value=5.0, comparison_operator="ge")
        assert ev.evaluate(c, state) is False


class TestCombinations:
    def test_evaluate_all_both_true(self):
        state = _state(target_health=300.0, target_max_health=1000.0, elapsed_time=10.0)
        state.active_buffs.add("power_surge")
        c1 = Condition("c1", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        c2 = Condition("power_surge", "buff_active")
        assert ev.evaluate_all([c1, c2], state) is True

    def test_evaluate_all_one_false(self):
        state = _state(target_health=700.0, target_max_health=1000.0)
        c1 = Condition("c1", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        c2 = Condition("power_surge", "buff_active")
        assert ev.evaluate_all([c1, c2], state) is False

    def test_evaluate_any(self):
        state = _state(target_health=700.0, target_max_health=1000.0)
        state.active_buffs.add("power_surge")
        c1 = Condition("c1", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
        c2 = Condition("power_surge", "buff_active")
        assert ev.evaluate_any([c1, c2], state) is True
