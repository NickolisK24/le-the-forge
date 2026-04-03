"""K11 — Spatial target manager tests."""
import math
import pytest
from spatial.models.vector2 import Vector2
from spatial.aoe.aoe_shapes import CircleShape
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager
from targets.spatial_target_manager import SpatialTargetManager


def _mgr_with_targets(n: int = 3, hp: float = 1000.0) -> SpatialTargetManager:
    mgr = TargetManager()
    for i in range(n):
        mgr.spawn(TargetEntity(target_id=f"t{i}", max_health=hp, position_index=i))
    return SpatialTargetManager(mgr)


class TestPositionManagement:
    def test_default_position_is_zero(self):
        sm = _mgr_with_targets(1)
        assert sm.get_position("t0") == Vector2(0, 0)

    def test_set_and_get_position(self):
        sm = _mgr_with_targets(1)
        sm.set_position("t0", Vector2(5.0, 3.0))
        assert sm.get_position("t0") == Vector2(5.0, 3.0)

    def test_set_position_unknown_target_raises(self):
        sm = _mgr_with_targets(1)
        with pytest.raises(KeyError):
            sm.set_position("unknown", Vector2(1, 1))

    def test_move_target_alias(self):
        sm = _mgr_with_targets(1)
        sm.move_target("t0", Vector2(2, 2))
        assert sm.get_position("t0") == Vector2(2, 2)


class TestSpatialQueries:
    def test_targets_in_radius_finds_nearby(self):
        sm = _mgr_with_targets(3)
        sm.set_position("t0", Vector2(1, 0))
        sm.set_position("t1", Vector2(5, 0))
        sm.set_position("t2", Vector2(10, 0))
        found = sm.targets_in_radius(Vector2(0, 0), radius=3.0)
        ids = {t.target_id for t in found}
        assert "t0" in ids
        assert "t1" not in ids
        assert "t2" not in ids

    def test_targets_in_radius_negative_raises(self):
        sm = _mgr_with_targets(1)
        with pytest.raises(ValueError):
            sm.targets_in_radius(Vector2(0, 0), radius=-1.0)

    def test_targets_in_shape(self):
        sm = _mgr_with_targets(3)
        sm.set_position("t0", Vector2(1, 0))
        sm.set_position("t1", Vector2(10, 0))
        sm.set_position("t2", Vector2(0, 1))
        shape = CircleShape(center=Vector2(0, 0), radius=2.0)
        found = sm.targets_in_shape(shape)
        ids = {t.target_id for t in found}
        assert "t0" in ids and "t2" in ids
        assert "t1" not in ids

    def test_nearest_to(self):
        sm = _mgr_with_targets(3)
        sm.set_position("t0", Vector2(10, 0))
        sm.set_position("t1", Vector2(1, 0))
        sm.set_position("t2", Vector2(5, 0))
        nearest = sm.nearest_to(Vector2(0, 0))
        assert nearest.target_id == "t1"

    def test_nearest_to_excludes_ids(self):
        sm = _mgr_with_targets(3)
        sm.set_position("t0", Vector2(1, 0))
        sm.set_position("t1", Vector2(2, 0))
        sm.set_position("t2", Vector2(5, 0))
        nearest = sm.nearest_to(Vector2(0, 0), exclude_ids={"t0"})
        assert nearest.target_id == "t1"

    def test_nearest_no_targets_returns_none(self):
        sm = _mgr_with_targets(0)
        assert sm.nearest_to(Vector2(0, 0)) is None


class TestLayouts:
    def test_layout_linear_spacing(self):
        sm = _mgr_with_targets(3)
        sm.layout_linear(spacing=5.0)
        pos_0 = sm.get_position("t0")
        pos_1 = sm.get_position("t1")
        assert pos_0.distance_to(pos_1) == pytest.approx(5.0)

    def test_layout_circle_equidistant(self):
        sm = _mgr_with_targets(4)
        sm.layout_circle(radius=5.0)
        # All targets should be at distance 5 from center
        for i in range(4):
            pos = sm.get_position(f"t{i}")
            assert pos.magnitude() == pytest.approx(5.0, abs=1e-9)

    def test_layout_linear_invalid_spacing_raises(self):
        sm = _mgr_with_targets(2)
        with pytest.raises(ValueError):
            sm.layout_linear(spacing=0.0)

    def test_layout_circle_invalid_radius_raises(self):
        sm = _mgr_with_targets(2)
        with pytest.raises(ValueError):
            sm.layout_circle(radius=0.0)

    def test_position_map_has_all_alive(self):
        sm = _mgr_with_targets(3)
        pmap = sm.position_map()
        assert set(pmap.keys()) == {"t0", "t1", "t2"}


class TestDelegation:
    def test_spawn_with_position(self):
        sm = SpatialTargetManager(TargetManager())
        t = TargetEntity("boss", max_health=5000.0)
        sm.spawn(t, position=Vector2(10, 5))
        assert sm.get_position("boss") == Vector2(10, 5)

    def test_is_cleared_after_kill(self):
        sm = _mgr_with_targets(1)
        sm.manager.get("t0").apply_damage(1000.0)
        sm.manager.remove_dead()
        assert sm.is_cleared() is True

    def test_snapshot_includes_position(self):
        sm = _mgr_with_targets(1)
        sm.set_position("t0", Vector2(3.0, 4.0))
        snap = sm.snapshot()
        assert snap[0]["position"] == (3.0, 4.0)
