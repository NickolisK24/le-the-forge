"""Tests for Conditional Enemy Behavior (Step 75)."""
import pytest
from app.domain.enemy_behavior import (
    BehaviorPhaseEntry,
    ConditionalBehavior,
    EnemyBehaviorProfile,
    select_behavior,
)

normal  = EnemyBehaviorProfile(attack_duration=2.0, move_duration=1.0)
enraged = EnemyBehaviorProfile(attack_duration=3.0, move_duration=0.5)
phase2  = EnemyBehaviorProfile(attack_duration=4.0, move_duration=0.2)


class TestBehaviorPhaseEntry:
    def test_valid_construction(self):
        e = BehaviorPhaseEntry(50.0, enraged)
        assert e.health_threshold == pytest.approx(50.0)

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            BehaviorPhaseEntry(150.0, enraged)

    def test_zero_threshold_allowed(self):
        e = BehaviorPhaseEntry(0.0, enraged)
        assert e.health_threshold == pytest.approx(0.0)


class TestSelectBehavior:
    def _cb(self) -> ConditionalBehavior:
        return ConditionalBehavior(
            phases=(BehaviorPhaseEntry(50.0, enraged),),
            default=normal,
        )

    def test_above_threshold_returns_default(self):
        assert select_behavior(self._cb(), 100.0) is normal

    def test_at_threshold_returns_phase(self):
        assert select_behavior(self._cb(), 50.0) is enraged

    def test_below_threshold_returns_phase(self):
        assert select_behavior(self._cb(), 25.0) is enraged

    def test_no_phases_always_default(self):
        cb = ConditionalBehavior(phases=(), default=normal)
        assert select_behavior(cb, 10.0) is normal

    def test_two_phase_thresholds(self):
        cb = ConditionalBehavior(
            phases=(
                BehaviorPhaseEntry(50.0, enraged),
                BehaviorPhaseEntry(25.0, phase2),
            ),
            default=normal,
        )
        assert select_behavior(cb, 75.0) is normal
        assert select_behavior(cb, 50.0) is enraged
        assert select_behavior(cb, 25.0) is phase2
        assert select_behavior(cb, 10.0) is phase2
