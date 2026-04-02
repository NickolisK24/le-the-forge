"""
Tests for Enemy Behavior Profiles (Step 8).

Validates:
  - EnemyBehaviorProfile: fields, cycle_duration, attack_uptime, validation
  - simulate_enemy_behavior: phase timing, full/partial cycles, uptime
  - Edge cases: zero duration, stationary, zero stun
"""

import pytest
from app.domain.enemy_behavior import (
    EnemyBehaviorProfile,
    BehaviorSummary,
    simulate_enemy_behavior,
)


# ---------------------------------------------------------------------------
# EnemyBehaviorProfile
# ---------------------------------------------------------------------------

class TestEnemyBehaviorProfile:
    def test_fields_stored(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0, stun_duration=0.5)
        assert p.attack_duration == pytest.approx(3.0)
        assert p.move_duration   == pytest.approx(1.0)
        assert p.stun_duration   == pytest.approx(0.5)

    def test_stun_duration_defaults_zero(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        assert p.stun_duration == pytest.approx(0.0)

    def test_is_stationary_defaults_false(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        assert p.is_stationary is False

    def test_is_frozen(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        with pytest.raises((AttributeError, TypeError)):
            p.attack_duration = 99.0  # type: ignore[misc]

    def test_cycle_duration_standard(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0, stun_duration=0.5)
        assert p.cycle_duration == pytest.approx(4.5)

    def test_cycle_duration_stationary(self):
        # Stationary: move phase omitted
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0, is_stationary=True)
        assert p.cycle_duration == pytest.approx(3.0)

    def test_cycle_duration_no_stun(self):
        p = EnemyBehaviorProfile(attack_duration=4.0, move_duration=2.0)
        assert p.cycle_duration == pytest.approx(6.0)

    def test_attack_uptime_calculation(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        assert p.attack_uptime == pytest.approx(0.75)

    def test_attack_uptime_stationary_full(self):
        p = EnemyBehaviorProfile(attack_duration=5.0, move_duration=2.0, is_stationary=True)
        assert p.attack_uptime == pytest.approx(1.0)

    def test_attack_uptime_zero_cycle(self):
        p = EnemyBehaviorProfile(attack_duration=0.0, move_duration=0.0)
        assert p.attack_uptime == pytest.approx(0.0)

    def test_negative_attack_duration_raises(self):
        with pytest.raises(ValueError, match="attack_duration"):
            EnemyBehaviorProfile(attack_duration=-1.0, move_duration=1.0)

    def test_negative_move_duration_raises(self):
        with pytest.raises(ValueError, match="move_duration"):
            EnemyBehaviorProfile(attack_duration=1.0, move_duration=-0.5)

    def test_negative_stun_duration_raises(self):
        with pytest.raises(ValueError, match="stun_duration"):
            EnemyBehaviorProfile(attack_duration=1.0, move_duration=1.0, stun_duration=-1.0)


# ---------------------------------------------------------------------------
# simulate_enemy_behavior — basic
# ---------------------------------------------------------------------------

class TestSimulateEnemyBehaviorBasic:
    def test_zero_duration(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 0.0)
        assert s.attack_time == pytest.approx(0.0)
        assert s.move_time   == pytest.approx(0.0)
        assert s.full_cycles == 0

    def test_negative_duration_raises(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        with pytest.raises(ValueError, match="fight_duration"):
            simulate_enemy_behavior(p, -1.0)

    def test_exact_one_cycle(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 4.0)
        assert s.full_cycles  == 1
        assert s.attack_time  == pytest.approx(3.0)
        assert s.move_time    == pytest.approx(1.0)
        assert s.partial_cycle == pytest.approx(0.0)

    def test_two_full_cycles(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 8.0)
        assert s.full_cycles == 2
        assert s.attack_time == pytest.approx(6.0)
        assert s.move_time   == pytest.approx(2.0)

    def test_total_time_conserved(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0, stun_duration=0.5)
        s = simulate_enemy_behavior(p, 10.0)
        assert s.attack_time + s.move_time + s.stun_time == pytest.approx(10.0)

    def test_attack_uptime_field(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 4.0)
        assert s.attack_uptime == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# simulate_enemy_behavior — partial cycles
# ---------------------------------------------------------------------------

class TestSimulatePartialCycle:
    def test_partial_cycle_in_attack_phase(self):
        # Cycle: 3s attack + 1s move. Fight: 5.0s = 1 full cycle + 1s partial (attack)
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 5.0)
        assert s.full_cycles  == 1
        assert s.attack_time  == pytest.approx(4.0)   # 3 + 1
        assert s.move_time    == pytest.approx(1.0)
        assert s.partial_cycle == pytest.approx(1.0)

    def test_partial_cycle_in_move_phase(self):
        # Cycle: 3s attack + 2s move. Fight: 4.5s = 1 full + 1.5s partial
        # 1.5s partial: 3s attack already consumed by full cycle, then 1.5s into move
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=2.0)
        s = simulate_enemy_behavior(p, 8.5)
        # full_cycles = 1 (5s), partial = 3.5s
        assert s.full_cycles == 1
        assert s.attack_time == pytest.approx(3.0 + 3.0)  # 1 full + full attack in partial
        assert s.move_time   == pytest.approx(2.0 + 0.5)   # 1 full + 0.5 into move

    def test_partial_cycle_in_stun_phase(self):
        # Cycle: 2s attack + 1s move + 1s stun. Fight: 3.5s = 0 full + 3.5s partial
        p = EnemyBehaviorProfile(attack_duration=2.0, move_duration=1.0, stun_duration=1.0)
        s = simulate_enemy_behavior(p, 3.5)
        assert s.full_cycles == 0
        assert s.attack_time == pytest.approx(2.0)
        assert s.move_time   == pytest.approx(1.0)
        assert s.stun_time   == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# simulate_enemy_behavior — stationary
# ---------------------------------------------------------------------------

class TestSimulateStationary:
    def test_stationary_no_move_time(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=2.0, is_stationary=True)
        s = simulate_enemy_behavior(p, 6.0)
        assert s.move_time == pytest.approx(0.0)

    def test_stationary_full_cycle(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=2.0, is_stationary=True)
        s = simulate_enemy_behavior(p, 6.0)
        assert s.full_cycles == 2
        assert s.attack_time == pytest.approx(6.0)

    def test_stationary_with_stun(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=0.0, stun_duration=1.0, is_stationary=True)
        s = simulate_enemy_behavior(p, 8.0)
        assert s.attack_time + s.stun_time == pytest.approx(8.0)
        assert s.move_time == pytest.approx(0.0)

    def test_stationary_uptime_with_stun(self):
        # 3s attack + 1s stun = 4s cycle. Uptime = 3/4 = 0.75
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=2.0, stun_duration=1.0, is_stationary=True)
        s = simulate_enemy_behavior(p, 4.0)
        assert s.attack_uptime == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# BehaviorSummary fields
# ---------------------------------------------------------------------------

class TestBehaviorSummary:
    def test_summary_is_frozen(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 4.0)
        with pytest.raises((AttributeError, TypeError)):
            s.attack_time = 99.0  # type: ignore[misc]

    def test_total_duration_stored(self):
        p = EnemyBehaviorProfile(attack_duration=3.0, move_duration=1.0)
        s = simulate_enemy_behavior(p, 7.5)
        assert s.total_duration == pytest.approx(7.5)
