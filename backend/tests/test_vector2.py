"""K1 — Vector2 tests."""
import math
import pytest
from spatial.models.vector2 import Vector2


class TestConstruction:
    def test_default_zero(self):
        v = Vector2()
        assert v.x == 0.0 and v.y == 0.0

    def test_explicit_values(self):
        v = Vector2(3.0, 4.0)
        assert v.x == 3.0 and v.y == 4.0

    def test_frozen_immutable(self):
        v = Vector2(1.0, 2.0)
        with pytest.raises((AttributeError, TypeError)):
            v.x = 5.0

    def test_zero_classmethod(self):
        assert Vector2.zero() == Vector2(0.0, 0.0)

    def test_unit_x(self):
        assert Vector2.unit_x() == Vector2(1.0, 0.0)

    def test_unit_y(self):
        assert Vector2.unit_y() == Vector2(0.0, 1.0)

    def test_from_tuple(self):
        v = Vector2.from_tuple((3.0, -1.5))
        assert v.x == 3.0 and v.y == -1.5

    def test_to_tuple(self):
        assert Vector2(2.0, 7.0).to_tuple() == (2.0, 7.0)


class TestArithmetic:
    def test_add(self):
        assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)

    def test_sub(self):
        assert Vector2(5, 3) - Vector2(2, 1) == Vector2(3, 2)

    def test_mul_scalar(self):
        assert Vector2(2, 3) * 3 == Vector2(6, 9)

    def test_rmul_scalar(self):
        assert 3 * Vector2(2, 3) == Vector2(6, 9)

    def test_truediv(self):
        assert Vector2(6, 4) / 2 == Vector2(3, 2)

    def test_truediv_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            Vector2(1, 2) / 0.0

    def test_neg(self):
        assert -Vector2(1, -2) == Vector2(-1, 2)


class TestMagnitudeDistance:
    def test_magnitude_3_4_is_5(self):
        assert Vector2(3, 4).magnitude() == pytest.approx(5.0)

    def test_magnitude_sq(self):
        assert Vector2(3, 4).magnitude_sq() == pytest.approx(25.0)

    def test_distance_to(self):
        a, b = Vector2(0, 0), Vector2(3, 4)
        assert a.distance_to(b) == pytest.approx(5.0)

    def test_distance_sq_to(self):
        a, b = Vector2(0, 0), Vector2(3, 4)
        assert a.distance_sq_to(b) == pytest.approx(25.0)


class TestDirectionHelpers:
    def test_normalize_gives_unit(self):
        v = Vector2(3, 4).normalize()
        assert v.magnitude() == pytest.approx(1.0)

    def test_normalize_zero_vector(self):
        assert Vector2(0, 0).normalize() == Vector2(0, 0)

    def test_dot_product(self):
        assert Vector2(1, 0).dot(Vector2(0, 1)) == pytest.approx(0.0)
        assert Vector2(1, 0).dot(Vector2(1, 0)) == pytest.approx(1.0)

    def test_angle_to_perpendicular(self):
        angle = Vector2(1, 0).angle_to(Vector2(0, 1))
        assert angle == pytest.approx(math.pi / 2)

    def test_rotate_90_degrees(self):
        rotated = Vector2(1, 0).rotate(math.pi / 2)
        assert rotated.x == pytest.approx(0.0, abs=1e-9)
        assert rotated.y == pytest.approx(1.0)

    def test_lerp_midpoint(self):
        a, b = Vector2(0, 0), Vector2(2, 4)
        mid = a.lerp(b, 0.5)
        assert mid == Vector2(1.0, 2.0)

    def test_lerp_t0_gives_self(self):
        a, b = Vector2(1, 2), Vector2(5, 6)
        assert a.lerp(b, 0.0) == a

    def test_lerp_t1_gives_other(self):
        a, b = Vector2(1, 2), Vector2(5, 6)
        assert a.lerp(b, 1.0) == b
