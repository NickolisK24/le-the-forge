"""K9 — Spatial splash engine tests."""
import pytest
from spatial.models.vector2 import Vector2
from spatial.splash.splash_engine import SpatialSplashEngine, SpatialSplashResult
from targets.models.target_entity import TargetEntity


def _target(tid: str = "t1", hp: float = 1000.0) -> TargetEntity:
    return TargetEntity(target_id=tid, max_health=hp)


class TestBasicSplash:
    def test_single_target_at_impact(self):
        eng = SpatialSplashEngine()
        t = _target()
        result = eng.execute(100.0, Vector2(0, 0), [(t, Vector2(0, 0))], radius=3.0, falloff=0.0)
        assert result.targets_hit == 1
        assert result.total_damage == pytest.approx(100.0)

    def test_target_outside_radius_not_hit(self):
        eng = SpatialSplashEngine()
        t = _target()
        result = eng.execute(100.0, Vector2(0, 0), [(t, Vector2(5, 0))], radius=3.0)
        assert result.targets_hit == 0

    def test_falloff_reduces_edge_damage(self):
        eng = SpatialSplashEngine()
        t = _target()
        # distance = 2, radius = 4, falloff = 1.0 → factor = 1 - 1*(2/4) = 0.5
        result = eng.execute(100.0, Vector2(0, 0), [(t, Vector2(2, 0))], radius=4.0, falloff=1.0)
        assert result.total_damage == pytest.approx(50.0)

    def test_zero_falloff_flat_damage(self):
        eng = SpatialSplashEngine()
        targets = [(TargetEntity(f"t{i}", 1000.0), Vector2(i, 0)) for i in range(3)]
        result = eng.execute(100.0, Vector2(1, 0), targets, radius=5.0, falloff=0.0)
        # All three within 5 units, all get 100 damage
        assert result.targets_hit == 3
        assert result.total_damage == pytest.approx(300.0)

    def test_dead_targets_skipped(self):
        eng = SpatialSplashEngine()
        dead = _target(hp=1.0)
        dead.apply_damage(1.0)
        result = eng.execute(100.0, Vector2(0, 0), [(dead, Vector2(0, 0))], radius=3.0)
        assert result.targets_hit == 0

    def test_multiple_targets_hit(self):
        eng = SpatialSplashEngine()
        targets = [(TargetEntity(f"mob{i}", 500.0), Vector2(i * 0.5, 0)) for i in range(5)]
        result = eng.execute(100.0, Vector2(0, 0), targets, radius=3.0, falloff=0.0)
        assert result.targets_hit == 5

    def test_invalid_radius_raises(self):
        eng = SpatialSplashEngine()
        with pytest.raises(ValueError):
            eng.execute(100.0, Vector2(0, 0), [], radius=0.0)

    def test_invalid_falloff_raises(self):
        eng = SpatialSplashEngine()
        with pytest.raises(ValueError):
            eng.execute(100.0, Vector2(0, 0), [], radius=1.0, falloff=1.5)

    def test_result_has_impact_point(self):
        eng = SpatialSplashEngine()
        impact = Vector2(3.0, 7.0)
        result = eng.execute(10.0, impact, [], radius=1.0)
        assert result.impact_point == impact

    def test_overkill_tracked(self):
        eng = SpatialSplashEngine()
        t = _target(hp=50.0)
        result = eng.execute(100.0, Vector2(0, 0), [(t, Vector2(0, 0))], radius=5.0, falloff=0.0)
        assert result.hits[0]["overkill"] == pytest.approx(50.0)
