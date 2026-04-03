"""K4 — Projectile manager tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile
from projectiles.projectile_manager import ProjectileManager


def _proj(pid: str = "p1", speed: float = 10.0, max_range: float = float("inf")) -> Projectile:
    p = Projectile(
        origin=Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=speed,
        damage=50.0,
        skill_id="arrow",
        max_range=max_range,
    )
    object.__setattr__(p, "projectile_id", pid)
    return p


class TestSpawnAndGet:
    def test_spawn_and_get(self):
        mgr = ProjectileManager()
        p = _proj("p1")
        mgr.spawn(p)
        assert mgr.get("p1") is p

    def test_duplicate_id_raises(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        with pytest.raises(ValueError):
            mgr.spawn(_proj("p1"))

    def test_get_missing_raises(self):
        mgr = ProjectileManager()
        with pytest.raises(KeyError):
            mgr.get("nope")

    def test_total_count(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.spawn(_proj("p2"))
        assert mgr.total_count == 2

    def test_active_count(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.spawn(_proj("p2"))
        assert mgr.active_count == 2


class TestAdvanceAndCleanup:
    def test_advance_all_moves_projectiles(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1", speed=10.0))
        mgr.advance_all(1.0)
        assert mgr.get("p1").distance_traveled == pytest.approx(10.0)

    def test_advance_skips_inactive(self):
        mgr = ProjectileManager()
        p = _proj("p1")
        mgr.spawn(p)
        mgr.deactivate("p1")
        mgr.advance_all(1.0)
        assert mgr.get("p1").distance_traveled == pytest.approx(0.0)

    def test_deactivate_sets_inactive(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.deactivate("p1")
        assert mgr.get("p1").is_active is False

    def test_clear_inactive_removes_and_returns_count(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1", max_range=1.0, speed=10.0))  # will expire on advance
        mgr.spawn(_proj("p2"))
        mgr.advance_all(1.0)  # p1 expires (10 units > 1 unit range)
        removed = mgr.clear_inactive()
        assert removed == 1
        assert mgr.total_count == 1

    def test_reset_clears_all(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.reset()
        assert mgr.total_count == 0

    def test_active_projectiles_returns_active_only(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.spawn(_proj("p2"))
        mgr.deactivate("p1")
        active = mgr.active_projectiles()
        assert len(active) == 1
        assert active[0].projectile_id == "p2"

    def test_snapshot_only_active(self):
        mgr = ProjectileManager()
        mgr.spawn(_proj("p1"))
        mgr.spawn(_proj("p2"))
        mgr.deactivate("p1")
        snap = mgr.snapshot()
        assert len(snap) == 1
