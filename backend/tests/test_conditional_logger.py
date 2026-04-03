"""H15 — Conditional Debug Logger tests."""
import pytest
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier
from state.state_engine import SimulationState
from debug.conditional_logger import ConditionalLogger


def _state(target_pct=0.3):
    return SimulationState(
        player_health=1.0, player_max_health=1.0,
        target_health=target_pct, target_max_health=1.0,
    )


def _mod():
    cond = Condition("c", "target_health_pct", threshold_value=0.5, comparison_operator="lt")
    return ConditionalModifier("m1", "spell_damage_pct", 30.0, "additive", cond)


class TestLogCreation:
    def test_record_adds_entry(self):
        clog = ConditionalLogger(enabled=True)
        clog.record(1.0, _state(), [_mod()], {"spell_damage_pct": 30.0}, 1000.0, 1300.0, ["m1"])
        assert len(clog.entries()) == 1

    def test_disabled_does_not_record(self):
        clog = ConditionalLogger(enabled=False)
        clog.record(1.0, _state(), [_mod()], {}, 1000.0, 1000.0)
        assert len(clog.entries()) == 0

    def test_clear_empties_log(self):
        clog = ConditionalLogger()
        clog.record(1.0, _state(), [], {}, 500.0, 500.0)
        clog.clear()
        assert len(clog.entries()) == 0

    def test_max_entries_respected(self):
        clog = ConditionalLogger(max_entries=3)
        for i in range(5):
            clog.record(float(i), _state(), [], {}, 100.0, 100.0)
        assert len(clog.entries()) == 3


class TestLogAccuracy:
    def test_entry_values_correct(self):
        clog = ConditionalLogger()
        clog.record(2.5, _state(0.3), [_mod()], {"spell_damage_pct": 30.0}, 1000.0, 1300.0, ["m1"])
        e = clog.entries()[0]
        assert e.tick_time == 2.5
        assert e.base_damage == 1000.0
        assert e.adjusted_damage == 1300.0
        assert e.stat_deltas == {"spell_damage_pct": 30.0}

    def test_to_list_serialises(self):
        clog = ConditionalLogger()
        clog.record(1.0, _state(), [_mod()], {"spell_damage_pct": 20.0}, 500.0, 600.0, ["m1"])
        lst = clog.to_list()
        assert len(lst) == 1
        assert lst[0]["base_damage"] == 500.0
        assert lst[0]["adjusted_damage"] == 600.0

    def test_summary_string(self):
        clog = ConditionalLogger()
        clog.record(3.0, _state(), [_mod()], {"spell_damage_pct": 30.0}, 1000.0, 1300.0, ["m1"])
        summary = clog.entries()[0].summary()
        assert "1000" in summary
        assert "1300" in summary
