"""I2 — Target Manager tests."""
import pytest
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager


def _t(tid="t1", hp=1000.0) -> TargetEntity:
    return TargetEntity(tid, max_health=hp)


class TestTargetSpawning:
    def test_spawn_adds_target(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        assert mgr.total_count == 1

    def test_duplicate_id_raises(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        with pytest.raises(ValueError):
            mgr.spawn(_t("t1"))

    def test_get_returns_target(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        assert mgr.get("t1").target_id == "t1"

    def test_get_missing_raises(self):
        mgr = TargetManager()
        with pytest.raises(KeyError):
            mgr.get("missing")


class TestRemovalOnDeath:
    def test_remove_dead_clears_dead_targets(self):
        mgr = TargetManager()
        t = _t("t1")
        mgr.spawn(t)
        t.apply_damage(1000.0)
        removed = mgr.remove_dead()
        assert "t1" in removed
        assert mgr.total_count == 0

    def test_remove_dead_keeps_alive(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        mgr.spawn(_t("t2"))
        mgr.get("t1").apply_damage(1000.0)
        mgr.remove_dead()
        assert mgr.total_count == 1
        assert mgr.get("t2").is_alive


class TestAliveTracking:
    def test_alive_count(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        mgr.spawn(_t("t2"))
        mgr.get("t1").apply_damage(1000.0)
        assert mgr.alive_count == 1

    def test_alive_targets_filters_dead(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        mgr.spawn(_t("t2"))
        mgr.get("t2").apply_damage(1000.0)
        alive = mgr.alive_targets()
        assert len(alive) == 1
        assert alive[0].target_id == "t1"

    def test_is_cleared_when_all_dead(self):
        mgr = TargetManager()
        t = _t("t1")
        mgr.spawn(t)
        t.apply_damage(1000.0)
        assert mgr.is_cleared() is True


class TestManagerReset:
    def test_reset_empties_all(self):
        mgr = TargetManager()
        mgr.spawn(_t("t1"))
        mgr.spawn(_t("t2"))
        mgr.reset()
        assert mgr.total_count == 0
