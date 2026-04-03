"""L1 — MovementVector tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.models.movement_vector import MovementVector


class TestConstruction:
    def test_default_stationary(self):
        mv = MovementVector()
        assert mv.speed == 0.0
        assert mv.is_moving is False

    def test_direction_normalized(self):
        mv = MovementVector(direction=Vector2(3, 4), speed=5.0)
        assert mv.direction.magnitude() == pytest.approx(1.0)

    def test_negative_speed_raises(self):
        with pytest.raises(ValueError):
            MovementVector(speed=-1.0)

    def test_zero_max_speed_raises(self):
        with pytest.raises(ValueError):
            MovementVector(max_speed=0.0)

    def test_velocity_property(self):
        mv = MovementVector(direction=Vector2(1, 0), speed=5.0)
        assert mv.velocity == Vector2(5, 0)

    def test_is_moving_false_when_zero_speed(self):
        mv = MovementVector(direction=Vector2(1, 0), speed=0.0)
        assert mv.is_moving is False

    def test_is_moving_false_when_zero_direction(self):
        mv = MovementVector(direction=Vector2(0, 0), speed=5.0)
        assert mv.is_moving is False


class TestMutation:
    def test_set_direction_normalizes(self):
        mv = MovementVector()
        mv.set_direction(Vector2(3, 4))
        assert mv.direction.magnitude() == pytest.approx(1.0)

    def test_set_direction_zero_clears(self):
        mv = MovementVector(direction=Vector2(1, 0), speed=5.0)
        mv.set_direction(Vector2(0, 0))
        assert mv.is_moving is False

    def test_apply_acceleration_increases_speed(self):
        mv = MovementVector(acceleration=2.0, max_speed=10.0)
        mv.apply_acceleration(1.0)
        assert mv.speed == pytest.approx(2.0)

    def test_apply_acceleration_clamped_to_max(self):
        mv = MovementVector(speed=9.0, acceleration=5.0, max_speed=10.0)
        mv.apply_acceleration(1.0)
        assert mv.speed == pytest.approx(10.0)

    def test_apply_negative_acceleration_slows(self):
        mv = MovementVector(speed=5.0, acceleration=-2.0)
        mv.apply_acceleration(1.0)
        assert mv.speed == pytest.approx(3.0)

    def test_stop_zeroes_speed(self):
        mv = MovementVector(direction=Vector2(1, 0), speed=5.0)
        mv.stop()
        assert mv.speed == 0.0

    def test_point_toward(self):
        mv = MovementVector()
        mv.point_toward(Vector2(0, 0), Vector2(1, 0))
        assert mv.direction == Vector2(1, 0)

    def test_to_dict_keys(self):
        d = MovementVector(direction=Vector2(1, 0), speed=3.0).to_dict()
        assert "direction" in d and "speed" in d and "velocity" in d

    def test_stationary_factory(self):
        mv = MovementVector.stationary()
        assert mv.is_moving is False

    def test_toward_factory(self):
        mv = MovementVector.toward(Vector2(0, 0), Vector2(4, 3), speed=5.0)
        assert mv.speed == pytest.approx(5.0)
        assert mv.direction.magnitude() == pytest.approx(1.0)
