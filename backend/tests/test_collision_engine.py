"""K5 — Collision detection engine tests."""
import pytest
from spatial.models.vector2 import Vector2
from spatial.collision.collision_engine import CollisionEngine, CollisionResult
from projectiles.models.projectile import Projectile


def _proj(pos: Vector2 = None, radius: float = 0.5) -> Projectile:
    p = Projectile(
        origin=pos or Vector2(0, 0),
        direction=Vector2(1, 0),
        speed=1.0,
        damage=10.0,
        skill_id="test",
        radius=radius,
    )
    return p


class TestPointCircle:
    def test_point_inside_circle(self):
        eng = CollisionEngine()
        assert eng.check_point_circle(Vector2(0, 0), Vector2(0, 0), 1.0) is True

    def test_point_on_boundary(self):
        eng = CollisionEngine()
        assert eng.check_point_circle(Vector2(1, 0), Vector2(0, 0), 1.0) is True

    def test_point_outside_circle(self):
        eng = CollisionEngine()
        assert eng.check_point_circle(Vector2(2, 0), Vector2(0, 0), 1.0) is False

    def test_negative_radius_raises(self):
        eng = CollisionEngine()
        with pytest.raises(ValueError):
            eng.check_point_circle(Vector2(0, 0), Vector2(0, 0), -1.0)


class TestCircleCircle:
    def test_overlapping_circles(self):
        eng = CollisionEngine()
        assert eng.check_circle_circle(Vector2(0, 0), 1.0, Vector2(1, 0), 1.0) is True

    def test_touching_circles(self):
        eng = CollisionEngine()
        assert eng.check_circle_circle(Vector2(0, 0), 1.0, Vector2(2, 0), 1.0) is True

    def test_separated_circles(self):
        eng = CollisionEngine()
        assert eng.check_circle_circle(Vector2(0, 0), 1.0, Vector2(3, 0), 1.0) is False

    def test_negative_radius_raises(self):
        eng = CollisionEngine()
        with pytest.raises(ValueError):
            eng.check_circle_circle(Vector2(0, 0), -1.0, Vector2(1, 0), 1.0)


class TestSegmentCircle:
    def test_segment_passes_through(self):
        eng = CollisionEngine()
        result = eng.check_segment_circle(
            Vector2(-5, 0), Vector2(5, 0), Vector2(0, 0), 1.0
        )
        assert result is True

    def test_segment_misses(self):
        eng = CollisionEngine()
        result = eng.check_segment_circle(
            Vector2(-5, 5), Vector2(5, 5), Vector2(0, 0), 1.0
        )
        assert result is False


class TestProjectileVsTargets:
    def test_projectile_hits_target(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0), radius=0.5)
        targets = {"t1": (Vector2(0.5, 0), 0.5)}
        results = eng.find_hits(p, targets)
        assert len(results) == 1
        assert results[0].target_id == "t1"

    def test_projectile_misses_target(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0), radius=0.5)
        targets = {"t1": (Vector2(10, 0), 0.5)}
        results = eng.find_hits(p, targets)
        assert results == []

    def test_already_hit_target_skipped(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0), radius=1.0)
        p.record_hit("t1")
        targets = {"t1": (Vector2(0.5, 0), 1.0)}
        assert eng.find_hits(p, targets) == []

    def test_find_first_hit_nearest(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0), radius=1.0)
        targets = {
            "near": (Vector2(0.5, 0), 1.0),
            "far":  (Vector2(0.8, 0), 1.0),
        }
        result = eng.find_first_hit(p, targets)
        assert result is not None
        assert result.target_id == "near"

    def test_find_first_hit_no_targets(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0))
        assert eng.find_first_hit(p, {}) is None

    def test_results_sorted_by_distance(self):
        eng = CollisionEngine()
        p = _proj(Vector2(0, 0), radius=2.0)
        targets = {
            "far":  (Vector2(1.5, 0), 1.0),
            "near": (Vector2(0.3, 0), 1.0),
        }
        results = eng.find_hits(p, targets)
        assert results[0].target_id == "near"
        assert results[1].target_id == "far"
