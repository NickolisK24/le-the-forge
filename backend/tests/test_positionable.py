"""K2 — Positionable entity model tests."""
import pytest
from spatial.models.vector2 import Vector2
from spatial.models.positionable import Positionable


class TestMovement:
    def test_default_position_is_zero(self):
        p = Positionable()
        assert p.position == Vector2(0.0, 0.0)

    def test_move_advances_position(self):
        p = Positionable(position=Vector2(0, 0), velocity=Vector2(2.0, 0.0))
        p.move(1.0)
        assert p.position == Vector2(2.0, 0.0)

    def test_move_delta_zero_raises(self):
        p = Positionable()
        with pytest.raises(ValueError):
            p.move(0.0)

    def test_move_negative_delta_raises(self):
        p = Positionable()
        with pytest.raises(ValueError):
            p.move(-0.5)

    def test_move_multiple_ticks(self):
        p = Positionable(velocity=Vector2(1.0, 1.0))
        p.move(0.5)
        p.move(0.5)
        assert p.position.x == pytest.approx(1.0)
        assert p.position.y == pytest.approx(1.0)

    def test_set_position(self):
        p = Positionable()
        p.set_position(Vector2(5.0, 7.0))
        assert p.position == Vector2(5.0, 7.0)

    def test_set_velocity(self):
        p = Positionable()
        p.set_velocity(Vector2(3.0, 0.0))
        assert p.velocity == Vector2(3.0, 0.0)


class TestSpatialQueries:
    def test_distance_to_other(self):
        a = Positionable(position=Vector2(0, 0))
        b = Positionable(position=Vector2(3, 4))
        assert a.distance_to(b) == pytest.approx(5.0)

    def test_distance_to_point(self):
        p = Positionable(position=Vector2(0, 0))
        assert p.distance_to_point(Vector2(3, 4)) == pytest.approx(5.0)

    def test_within_range_true(self):
        p = Positionable(position=Vector2(0, 0))
        assert p.is_within_range(Vector2(3, 4), radius=5.0) is True

    def test_within_range_false(self):
        p = Positionable(position=Vector2(0, 0))
        assert p.is_within_range(Vector2(3, 4), radius=4.9) is False

    def test_direction_to(self):
        p = Positionable(position=Vector2(0, 0))
        d = p.direction_to(Vector2(3, 0))
        assert d.x == pytest.approx(1.0)
        assert d.y == pytest.approx(0.0)

    def test_speed_from_velocity(self):
        p = Positionable(velocity=Vector2(3.0, 4.0))
        assert p.speed() == pytest.approx(5.0)

    def test_snapshot_keys(self):
        p = Positionable(position=Vector2(1, 2), velocity=Vector2(0.5, 0.5))
        snap = p.snapshot()
        assert "position" in snap and "velocity" in snap and "speed" in snap
