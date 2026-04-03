"""K12 — Spatial timeline synchronizer tests."""
import pytest
from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile
from projectiles.projectile_manager import ProjectileManager
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager
from targets.spatial_target_manager import SpatialTargetManager
from spatial.timeline.spatial_sync import SpatialTimelineSynchronizer, SpatialTickRecord


def _proj(pid: str = "p1", speed: float = 100.0, damage: float = 50.0, max_range: float = float("inf")) -> Projectile:
    p = Projectile(
        origin=Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=speed,
        damage=damage,
        skill_id="arrow",
        max_range=max_range,
    )
    object.__setattr__(p, "projectile_id", pid)
    return p


def _spatial_mgr(n: int = 3, hp: float = 10000.0, spacing: float = 5.0) -> SpatialTargetManager:
    mgr = TargetManager()
    for i in range(n):
        mgr.spawn(TargetEntity(target_id=f"t{i}", max_health=hp))
    sm = SpatialTargetManager(mgr)
    sm.layout_linear(spacing=spacing, origin=Vector2(200, 0))  # far away — won't be hit
    return sm


class TestTickCounting:
    def test_invalid_tick_size_raises(self):
        with pytest.raises(ValueError):
            SpatialTimelineSynchronizer(tick_size=0.0)

    def test_invalid_duration_raises(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr()
        with pytest.raises(ValueError):
            sync.run(proj_mgr, sm, duration=0.0)

    def test_exact_tick_count_no_float_drift(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr()
        records = sync.run(proj_mgr, sm, duration=1.0)
        assert len(records) == 10

    def test_no_records_when_disabled(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1, record_snapshots=False)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr()
        records = sync.run(proj_mgr, sm, duration=1.0)
        assert records == []

    def test_record_has_expected_fields(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.5)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr()
        records = sync.run(proj_mgr, sm, duration=0.5)
        r = records[0]
        assert hasattr(r, "time")
        assert hasattr(r, "active_projectiles")
        assert hasattr(r, "hits_this_tick")
        assert hasattr(r, "targets_alive")

    def test_first_tick_time_matches_tick_size(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.5)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr()
        records = sync.run(proj_mgr, sm, duration=1.0)
        assert records[0].time == pytest.approx(0.5)
        assert records[1].time == pytest.approx(1.0)


class TestHitDetection:
    def test_projectile_hits_target(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1, hit_radius=1.0)
        proj_mgr = ProjectileManager()

        # Target at x=5, projectile moving at 10 units/s will reach it in 0.5s
        mgr = TargetManager()
        mgr.spawn(TargetEntity(target_id="enemy", max_health=1000.0))
        sm = SpatialTargetManager(mgr)
        sm.set_position("enemy", Vector2(5, 0))

        p = Projectile(
            origin=Vector2(0, 0), direction=Vector2(1, 0),
            speed=10.0, damage=100.0, skill_id="arrow",
        )
        proj_mgr.spawn(p)

        records = sync.run(proj_mgr, sm, duration=2.0)
        total_hits = sum(r.hits_this_tick for r in records)
        assert total_hits >= 1

    def test_stops_when_all_cleared(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1)
        proj_mgr = ProjectileManager()
        mgr = TargetManager()
        mgr.spawn(TargetEntity(target_id="tiny", max_health=1.0))
        sm = SpatialTargetManager(mgr)
        sm.set_position("tiny", Vector2(0.1, 0))  # right in front

        p = Projectile(
            origin=Vector2(0, 0), direction=Vector2(1, 0),
            speed=10.0, damage=9999.0, skill_id="nuke",
        )
        proj_mgr.spawn(p)
        records = sync.run(proj_mgr, sm, duration=10.0)
        # Should stop well before 10s
        assert len(records) < 100


class TestProjectileExpiry:
    def test_expired_projectile_removed(self):
        sync = SpatialTimelineSynchronizer(tick_size=0.1)
        proj_mgr = ProjectileManager()
        sm = _spatial_mgr(n=0)  # no targets

        p = Projectile(
            origin=Vector2(0, 0), direction=Vector2(1, 0),
            speed=10.0, damage=50.0, skill_id="test",
            max_range=0.5,  # expires after 0.05s
        )
        proj_mgr.spawn(p)
        records = sync.run(proj_mgr, sm, duration=0.5)
        # After cleanup, inactive projectile is removed
        assert proj_mgr.active_count == 0
