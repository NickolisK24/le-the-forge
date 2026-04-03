"""L11 — Collision avoidance engine tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.collision.avoidance_engine import AvoidanceEngine, AvoidanceResult


class TestSingleEntitySeparation:
    def test_no_nearby_entities_zero_force(self):
        eng = AvoidanceEngine()
        force = eng.compute_separation("a", Vector2(0, 0), {"b": Vector2(20, 0)}, avoidance_radius=2.0)
        assert force == Vector2.zero()

    def test_nearby_entity_creates_force(self):
        eng = AvoidanceEngine()
        force = eng.compute_separation("a", Vector2(0, 0), {"b": Vector2(1, 0)}, avoidance_radius=2.0)
        # Force should push away from b (negative x)
        assert force.x < 0

    def test_overlapping_entities_nonzero_force(self):
        eng = AvoidanceEngine()
        force = eng.compute_separation("a", Vector2(0, 0), {"b": Vector2(0, 0)}, avoidance_radius=1.0)
        assert force.magnitude() > 0

    def test_self_excluded(self):
        eng = AvoidanceEngine()
        pos = {"a": Vector2(0, 0), "b": Vector2(1, 0)}
        force = eng.compute_separation("a", Vector2(0, 0), pos, avoidance_radius=2.0)
        # Only b pushes a — force should be non-zero
        assert force != Vector2.zero()

    def test_invalid_radius_raises(self):
        eng = AvoidanceEngine()
        with pytest.raises(ValueError):
            eng.compute_separation("a", Vector2(0, 0), {}, avoidance_radius=0.0)

    def test_negative_strength_raises(self):
        eng = AvoidanceEngine()
        with pytest.raises(ValueError):
            eng.compute_separation("a", Vector2(0, 0), {}, avoidance_radius=1.0, strength=-1.0)


class TestGroupSeparation:
    def test_all_entities_have_force_entry(self):
        eng = AvoidanceEngine()
        positions = {
            "a": Vector2(0, 0),
            "b": Vector2(0.5, 0),
            "c": Vector2(5, 0),
        }
        result = eng.apply_separation_all(positions, avoidance_radius=2.0, max_speed=5.0)
        assert set(result.forces.keys()) == {"a", "b", "c"}

    def test_overlap_pairs_detected(self):
        eng = AvoidanceEngine()
        positions = {
            "a": Vector2(0, 0),
            "b": Vector2(0.2, 0),  # very close
        }
        result = eng.apply_separation_all(positions, avoidance_radius=2.0)
        assert len(result.overlap_pairs) > 0

    def test_no_overlap_pairs_when_spread_out(self):
        eng = AvoidanceEngine()
        positions = {
            "a": Vector2(0, 0),
            "b": Vector2(10, 0),
        }
        result = eng.apply_separation_all(positions, avoidance_radius=1.0)
        assert result.overlap_pairs == []

    def test_forces_clamped_to_max_speed(self):
        eng = AvoidanceEngine()
        positions = {"a": Vector2(0, 0), "b": Vector2(0.01, 0)}
        result = eng.apply_separation_all(positions, avoidance_radius=5.0, max_speed=3.0)
        for force in result.forces.values():
            assert force.magnitude() <= 3.0 + 1e-9

    def test_invalid_radius_raises(self):
        eng = AvoidanceEngine()
        with pytest.raises(ValueError):
            eng.apply_separation_all({}, avoidance_radius=0.0)
