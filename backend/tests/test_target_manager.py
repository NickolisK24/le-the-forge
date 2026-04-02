"""Tests for encounter target manager (Step 98)."""

import pytest

from encounter.enemy import EncounterEnemy
from encounter.target_manager import TargetManager


def _enemy(health=100.0, name="e") -> EncounterEnemy:
    return EncounterEnemy(max_health=health, current_health=health,
                          armor=0.0, name=name)


def _dead(health=100.0, name="dead") -> EncounterEnemy:
    e = _enemy(health=health, name=name)
    e.apply_damage(health)
    return e


class TestConstruction:
    def test_empty_init(self):
        mgr = TargetManager()
        assert mgr.target_count == 0
        assert mgr.select_primary() is None

    def test_init_with_enemies(self):
        mgr = TargetManager([_enemy(name="a"), _enemy(name="b")])
        assert mgr.target_count == 2

    def test_default_primary_index_zero(self):
        mgr = TargetManager([_enemy(name="a"), _enemy(name="b")])
        assert mgr.primary_target_index == 0


class TestAddTarget:
    def test_add_increases_count(self):
        mgr = TargetManager()
        mgr.add_target(_enemy(name="x"))
        assert mgr.target_count == 1

    def test_add_multiple(self):
        mgr = TargetManager()
        for i in range(5):
            mgr.add_target(_enemy(name=f"e{i}"))
        assert mgr.target_count == 5


class TestSelectPrimary:
    def test_returns_first_by_default(self):
        a, b = _enemy(name="a"), _enemy(name="b")
        mgr = TargetManager([a, b])
        assert mgr.select_primary() is a

    def test_no_targets_returns_none(self):
        assert TargetManager().select_primary() is None


class TestSwitchTarget:
    def test_switch_to_second(self):
        a, b = _enemy(name="a"), _enemy(name="b")
        mgr = TargetManager([a, b])
        mgr.switch_target(1)
        assert mgr.select_primary() is b

    def test_switch_out_of_range_raises(self):
        mgr = TargetManager([_enemy(name="a")])
        with pytest.raises(IndexError):
            mgr.switch_target(5)

    def test_switch_negative_raises(self):
        mgr = TargetManager([_enemy(name="a")])
        with pytest.raises(IndexError):
            mgr.switch_target(-1)

    def test_switch_empty_raises(self):
        with pytest.raises(IndexError):
            TargetManager().switch_target(0)


class TestRemoveDeadTargets:
    def test_removes_dead_enemy(self):
        a = _enemy(name="a")
        b = _dead(name="b")
        mgr = TargetManager([a, b])
        removed = mgr.remove_dead_targets()
        assert mgr.target_count == 1
        assert len(removed) == 1
        assert removed[0] is b

    def test_keeps_alive_enemies(self):
        a, b = _enemy(name="a"), _enemy(name="b")
        mgr = TargetManager([a, b])
        mgr.remove_dead_targets()
        assert mgr.target_count == 2

    def test_all_dead_clears_list(self):
        mgr = TargetManager([_dead(name="a"), _dead(name="b")])
        mgr.remove_dead_targets()
        assert mgr.target_count == 0
        assert mgr.select_primary() is None

    def test_index_clamped_after_removal(self):
        a = _enemy(name="a")
        b = _dead(name="b")
        c = _enemy(name="c")
        mgr = TargetManager([a, b, c])
        mgr.switch_target(2)
        mgr.remove_dead_targets()
        assert mgr.primary_target_index <= mgr.target_count - 1

    def test_returns_empty_when_no_dead(self):
        mgr = TargetManager([_enemy(name="a")])
        assert mgr.remove_dead_targets() == []


class TestSwitchHelpers:
    def test_switch_to_lowest_health(self):
        a = EncounterEnemy(max_health=100.0, current_health=80.0, armor=0.0, name="a")
        b = EncounterEnemy(max_health=100.0, current_health=30.0, armor=0.0, name="b")
        c = EncounterEnemy(max_health=100.0, current_health=60.0, armor=0.0, name="c")
        mgr = TargetManager([a, b, c])
        mgr.switch_to_lowest_health()
        assert mgr.select_primary() is b

    def test_switch_to_highest_health(self):
        a = EncounterEnemy(max_health=100.0, current_health=80.0, armor=0.0, name="a")
        b = EncounterEnemy(max_health=100.0, current_health=30.0, armor=0.0, name="b")
        mgr = TargetManager([a, b])
        mgr.switch_to_highest_health()
        assert mgr.select_primary() is a

    def test_helpers_no_op_on_empty(self):
        mgr = TargetManager()
        mgr.switch_to_lowest_health()
        mgr.switch_to_highest_health()


class TestStateQueries:
    def test_alive_count(self):
        mgr = TargetManager([_enemy(name="a"), _dead(name="b"), _enemy(name="c")])
        assert mgr.alive_count == 2

    def test_all_dead_true(self):
        mgr = TargetManager([_dead(name="a"), _dead(name="b")])
        assert mgr.all_dead is True

    def test_all_dead_false(self):
        mgr = TargetManager([_enemy(name="a"), _dead(name="b")])
        assert mgr.all_dead is False

    def test_all_dead_empty_is_true(self):
        assert TargetManager().all_dead is True

    def test_active_targets_is_copy(self):
        mgr = TargetManager([_enemy(name="a")])
        snapshot = mgr.active_targets
        mgr.add_target(_enemy(name="b"))
        assert len(snapshot) == 1
