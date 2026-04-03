"""L2 — MovementState tests."""
import pytest
from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState


def _state(**kw) -> MovementState:
    defaults = dict(entity_id="e1", position=Vector2(0, 0))
    defaults.update(kw)
    return MovementState(**defaults)


class TestConstruction:
    def test_basic_construction(self):
        s = _state()
        assert s.entity_id == "e1"
        assert s.position == Vector2(0, 0)

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            MovementState(entity_id="", position=Vector2(0, 0))

    def test_zero_max_speed_raises(self):
        with pytest.raises(ValueError):
            _state(max_speed=0.0)

    def test_default_not_moving(self):
        assert _state().is_moving is False


class TestApplyMovement:
    def test_advances_position(self):
        s = _state(velocity=Vector2(5, 0))
        s.apply_movement(1.0)
        assert s.position == Vector2(5, 0)

    def test_accumulates_distance(self):
        s = _state(velocity=Vector2(3, 4))
        s.apply_movement(1.0)
        assert s.distance_moved == pytest.approx(5.0)

    def test_advances_time_alive(self):
        s = _state()
        s.apply_movement(0.5)
        assert s.time_alive == pytest.approx(0.5)

    def test_zero_delta_raises(self):
        s = _state()
        with pytest.raises(ValueError):
            s.apply_movement(0.0)

    def test_is_moving_true_when_velocity_nonzero(self):
        s = _state(velocity=Vector2(1, 0))
        s.apply_movement(0.1)
        assert s.is_moving is True

    def test_is_moving_false_when_stopped(self):
        s = _state()
        s.apply_movement(0.1)
        assert s.is_moving is False


class TestSetVelocity:
    def test_clamps_to_max_speed(self):
        s = _state(max_speed=5.0)
        s.set_velocity(Vector2(10, 0))
        assert s.velocity.magnitude() == pytest.approx(5.0)

    def test_sets_is_moving(self):
        s = _state()
        s.set_velocity(Vector2(1, 0))
        assert s.is_moving is True

    def test_zero_velocity_not_moving(self):
        s = _state()
        s.set_velocity(Vector2(0, 0))
        assert s.is_moving is False

    def test_stop_clears_velocity(self):
        s = _state(velocity=Vector2(5, 0))
        s.stop()
        assert s.velocity == Vector2.zero()
        assert s.is_moving is False


class TestTargetTracking:
    def test_set_target(self):
        s = _state()
        s.set_target(Vector2(10, 0))
        assert s.target_position == Vector2(10, 0)

    def test_distance_to_target(self):
        s = _state()
        s.set_target(Vector2(3, 4))
        assert s.distance_to_target() == pytest.approx(5.0)

    def test_no_target_returns_none(self):
        s = _state()
        assert s.distance_to_target() is None

    def test_has_reached_target_true(self):
        s = _state()
        s.set_target(Vector2(0.05, 0))
        assert s.has_reached_target(arrival_radius=0.1) is True

    def test_has_reached_target_false(self):
        s = _state()
        s.set_target(Vector2(5, 0))
        assert s.has_reached_target(arrival_radius=0.1) is False

    def test_to_dict_has_expected_keys(self):
        d = _state().to_dict()
        assert "entity_id" in d and "position" in d and "behavior_type" in d
