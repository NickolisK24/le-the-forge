"""Tests for phase system framework (Step 100)."""

import pytest
from encounter.phases import (EncounterPhase, PhaseController,
                               PhaseModifiers, PhaseTransitionType)


def _health_phase(pid, threshold, **mods):
    return EncounterPhase(pid, PhaseTransitionType.HEALTH_BELOW, threshold,
                          PhaseModifiers(**mods) if mods else PhaseModifiers())

def _time_phase(pid, threshold, **mods):
    return EncounterPhase(pid, PhaseTransitionType.TIME_ELAPSED, threshold,
                          PhaseModifiers(**mods) if mods else PhaseModifiers())


class TestEncounterPhase:
    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError):
            EncounterPhase("p1", PhaseTransitionType.HEALTH_BELOW, -1.0)

    def test_valid_construction(self):
        p = _health_phase("rage", 50.0, damage_bonus_pct=20.0)
        assert p.phase_id == "rage"
        assert p.threshold == pytest.approx(50.0)
        assert p.modifiers.damage_bonus_pct == pytest.approx(20.0)


class TestPhaseController:
    def test_no_active_phase_initially(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        assert ctrl.active_phase is None

    def test_health_phase_triggers(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        assert ctrl.evaluate(health_pct=49.0, elapsed_time=0.0) is True
        assert ctrl.active_phase is not None
        assert ctrl.active_phase.phase_id == "rage"

    def test_health_phase_not_triggered_above_threshold(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        assert ctrl.evaluate(health_pct=51.0, elapsed_time=0.0) is False

    def test_health_phase_at_exact_threshold(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        assert ctrl.evaluate(health_pct=50.0, elapsed_time=0.0) is True

    def test_time_phase_triggers(self):
        ctrl = PhaseController([_time_phase("enrage", 30.0)])
        assert ctrl.evaluate(health_pct=100.0, elapsed_time=30.0) is True

    def test_time_phase_not_triggered_before(self):
        ctrl = PhaseController([_time_phase("enrage", 30.0)])
        assert ctrl.evaluate(health_pct=100.0, elapsed_time=29.9) is False

    def test_phase_fires_only_once(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        ctrl.evaluate(health_pct=40.0, elapsed_time=0.0)
        assert ctrl.evaluate(health_pct=30.0, elapsed_time=0.0) is False

    def test_multiple_phases_fire_in_order(self):
        phases = [
            _health_phase("p2", 50.0, damage_bonus_pct=10.0),
            _health_phase("p3", 25.0, damage_bonus_pct=20.0),
        ]
        ctrl = PhaseController(phases)
        ctrl.evaluate(health_pct=45.0, elapsed_time=0.0)
        assert ctrl.active_phase.phase_id == "p2"
        ctrl.evaluate(health_pct=20.0, elapsed_time=0.0)
        assert ctrl.active_phase.phase_id == "p3"

    def test_active_modifiers_default_when_no_phase(self):
        ctrl = PhaseController([])
        m = ctrl.active_modifiers
        assert m.damage_bonus_pct == pytest.approx(0.0)

    def test_active_modifiers_from_phase(self):
        ctrl = PhaseController([_health_phase("rage", 50.0, damage_bonus_pct=30.0)])
        ctrl.evaluate(health_pct=40.0, elapsed_time=0.0)
        assert ctrl.active_modifiers.damage_bonus_pct == pytest.approx(30.0)

    def test_phase_elapsed(self):
        ctrl = PhaseController([_time_phase("p1", 10.0)])
        ctrl.evaluate(health_pct=100.0, elapsed_time=10.0)
        assert ctrl.phase_elapsed(15.0) == pytest.approx(5.0)

    def test_phase_expired(self):
        p = EncounterPhase("short", PhaseTransitionType.TIME_ELAPSED, 5.0,
                           max_duration=10.0)
        ctrl = PhaseController([p])
        ctrl.evaluate(health_pct=100.0, elapsed_time=5.0)
        assert ctrl.is_phase_expired(14.9) is False
        assert ctrl.is_phase_expired(15.0) is True

    def test_unlimited_phase_never_expires(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        ctrl.evaluate(health_pct=40.0, elapsed_time=0.0)
        assert ctrl.is_phase_expired(999.0) is False

    def test_reset_clears_state(self):
        ctrl = PhaseController([_health_phase("rage", 50.0)])
        ctrl.evaluate(health_pct=40.0, elapsed_time=0.0)
        ctrl.reset()
        assert ctrl.active_phase is None
        assert ctrl.evaluate(health_pct=40.0, elapsed_time=0.0) is True
