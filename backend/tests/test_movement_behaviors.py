"""L3-L8 — Movement behavior tests (base, linear, random, aggressive, defensive, orbit)."""
import math
import pytest
from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_LINEAR, BEHAVIOR_RANDOM, BEHAVIOR_AGGRESSIVE, BEHAVIOR_DEFENSIVE, BEHAVIOR_ORBITING
from movement.behaviors.linear_behavior import LinearBehavior
from movement.behaviors.random_behavior import RandomBehavior
from movement.behaviors.aggressive_behavior import AggressiveBehavior
from movement.behaviors.defensive_behavior import DefensiveBehavior
from movement.behaviors.orbit_behavior import OrbitBehavior


def _state(pos: Vector2 = None, target: Vector2 = None, max_speed: float = 5.0) -> MovementState:
    s = MovementState(entity_id="e1", position=pos or Vector2(0, 0), max_speed=max_speed)
    if target:
        s.set_target(target)
    return s


# ---------------------------------------------------------------------------
# L4 — LinearBehavior
# ---------------------------------------------------------------------------

class TestLinearBehavior:
    def test_behavior_type(self):
        assert LinearBehavior().behavior_type == BEHAVIOR_LINEAR

    def test_moves_toward_target(self):
        b = LinearBehavior(speed=5.0)
        s = _state(pos=Vector2(0, 0), target=Vector2(10, 0))
        v = b.compute_velocity(s, {}, delta=0.1)
        assert v.x > 0

    def test_stops_at_arrival_radius(self):
        b = LinearBehavior(speed=5.0, arrival_radius=1.0)
        s = _state(pos=Vector2(0.5, 0), target=Vector2(0, 0))
        v = b.compute_velocity(s, {}, delta=0.1)
        assert v.magnitude() == pytest.approx(0.0)

    def test_no_target_returns_zero(self):
        b = LinearBehavior()
        s = _state()
        v = b.compute_velocity(s, {}, delta=0.1)
        assert v == Vector2.zero()

    def test_context_target_used(self):
        b = LinearBehavior(speed=5.0)
        s = _state()
        v = b.compute_velocity(s, {"target_position": Vector2(10, 0)}, delta=0.1)
        assert v.x > 0

    def test_update_advances_position(self):
        b = LinearBehavior(speed=5.0)
        s = _state(pos=Vector2(0, 0), target=Vector2(10, 0))
        b.update(s, {}, delta=1.0)
        assert s.position.x > 0

    def test_invalid_speed_raises(self):
        with pytest.raises(ValueError):
            LinearBehavior(speed=-1.0)

    def test_does_not_overshoot(self):
        b = LinearBehavior(speed=10.0)
        s = _state(pos=Vector2(0, 0), target=Vector2(0.5, 0))
        b.update(s, {}, delta=1.0)
        # Should not go past target
        assert s.position.x <= 0.5 + 1e-6


# ---------------------------------------------------------------------------
# L5 — RandomBehavior
# ---------------------------------------------------------------------------

class TestRandomBehavior:
    def test_behavior_type(self):
        assert RandomBehavior(seed=0).behavior_type == BEHAVIOR_RANDOM

    def test_zero_interval_raises(self):
        with pytest.raises(ValueError):
            RandomBehavior(change_interval=0.0)

    def test_moves_somewhere(self):
        b = RandomBehavior(speed=3.0, seed=42)
        s = _state()
        b.update(s, {}, delta=1.0)
        assert s.position != Vector2(0, 0)

    def test_wander_radius_limits_travel(self):
        b = RandomBehavior(speed=10.0, wander_radius=5.0, seed=1)
        s = _state()
        for _ in range(200):
            b.update(s, {}, delta=0.1)
        # After many ticks, wander radius should pull it back
        assert s.position.magnitude() <= 20.0  # relaxed bound

    def test_deterministic_with_seed(self):
        b1 = RandomBehavior(speed=3.0, seed=99)
        b2 = RandomBehavior(speed=3.0, seed=99)
        s1 = _state()
        s2 = _state()
        for _ in range(10):
            b1.update(s1, {}, delta=0.1)
            b2.update(s2, {}, delta=0.1)
        assert s1.position.x == pytest.approx(s2.position.x)
        assert s1.position.y == pytest.approx(s2.position.y)


# ---------------------------------------------------------------------------
# L6 — AggressiveBehavior
# ---------------------------------------------------------------------------

class TestAggressiveBehavior:
    def test_behavior_type(self):
        assert AggressiveBehavior().behavior_type == BEHAVIOR_AGGRESSIVE

    def test_moves_toward_player(self):
        b = AggressiveBehavior(speed=5.0)
        s = _state(pos=Vector2(0, 0))
        v = b.compute_velocity(s, {"player_position": Vector2(10, 0)}, delta=0.1)
        assert v.x > 0

    def test_stops_within_arrival_radius(self):
        b = AggressiveBehavior(speed=5.0, arrival_radius=1.0)
        s = _state(pos=Vector2(0.5, 0))
        v = b.compute_velocity(s, {"player_position": Vector2(0, 0)}, delta=0.1)
        assert v.magnitude() == pytest.approx(0.0)

    def test_no_target_stays_still(self):
        b = AggressiveBehavior()
        s = _state()
        assert b.compute_velocity(s, {}, 0.1) == Vector2.zero()

    def test_does_not_overshoot(self):
        b = AggressiveBehavior(speed=20.0)
        s = _state(pos=Vector2(0, 0))
        s.set_target(Vector2(0.1, 0))
        b.update(s, {}, delta=1.0)
        assert s.position.x <= 0.1 + 1e-6


# ---------------------------------------------------------------------------
# L7 — DefensiveBehavior
# ---------------------------------------------------------------------------

class TestDefensiveBehavior:
    def test_behavior_type(self):
        assert DefensiveBehavior().behavior_type == BEHAVIOR_DEFENSIVE

    def test_retreats_when_too_close(self):
        b = DefensiveBehavior(min_range=5.0, max_range=10.0, speed=3.0)
        s = _state(pos=Vector2(2, 0))  # threat at origin → dist 2 < min_range=5
        v = b.compute_velocity(s, {"player_position": Vector2(0, 0)}, delta=0.1)
        # Should move away from origin (positive x)
        assert v.x > 0

    def test_advances_when_too_far(self):
        b = DefensiveBehavior(min_range=3.0, max_range=6.0, speed=3.0)
        s = _state(pos=Vector2(20, 0))  # threat at origin → dist 20 > max_range=6
        v = b.compute_velocity(s, {"player_position": Vector2(0, 0)}, delta=0.1)
        assert v.x < 0  # moving toward origin

    def test_holds_in_safe_band(self):
        b = DefensiveBehavior(min_range=3.0, max_range=10.0, speed=3.0)
        s = _state(pos=Vector2(5, 0))  # threat at origin → dist 5, in [3,10]
        v = b.compute_velocity(s, {"player_position": Vector2(0, 0)}, delta=0.1)
        assert v == Vector2.zero()

    def test_invalid_range_raises(self):
        with pytest.raises(ValueError):
            DefensiveBehavior(min_range=10.0, max_range=5.0)

    def test_no_threat_stays_still(self):
        b = DefensiveBehavior()
        s = _state()
        assert b.compute_velocity(s, {}, 0.1) == Vector2.zero()


# ---------------------------------------------------------------------------
# L8 — OrbitBehavior
# ---------------------------------------------------------------------------

class TestOrbitBehavior:
    def test_behavior_type(self):
        assert OrbitBehavior().behavior_type == BEHAVIOR_ORBITING

    def test_orbits_at_correct_radius(self):
        b = OrbitBehavior(orbit_radius=5.0, angular_speed=1.0, initial_angle=0.0)
        s = _state(pos=Vector2(5, 0))
        pivot = Vector2(0, 0)
        # Run for a full orbit
        for _ in range(200):
            b.update(s, {"target_position": pivot}, delta=0.1)
        dist = s.position.distance_to(pivot)
        assert dist == pytest.approx(5.0, abs=0.2)

    def test_zero_orbit_radius_raises(self):
        with pytest.raises(ValueError):
            OrbitBehavior(orbit_radius=0.0)

    def test_no_pivot_stays_still(self):
        b = OrbitBehavior()
        s = _state()
        b.update(s, {}, 0.1)
        # With no pivot, velocity should be zero → no movement (or tiny due to floating point)
        assert s.distance_moved == pytest.approx(0.0, abs=1e-6)

    def test_advances_angle(self):
        b = OrbitBehavior(orbit_radius=5.0, angular_speed=math.pi, initial_angle=0.0)
        # Use high max_speed so the velocity-based teleport can reach the orbit position
        s = _state(pos=Vector2(5, 0), max_speed=1000.0)
        b.update(s, {"target_position": Vector2(0, 0)}, delta=1.0)
        # After π rad (180°), should be near (-5, 0)
        assert s.position.x == pytest.approx(-5.0, abs=0.5)
