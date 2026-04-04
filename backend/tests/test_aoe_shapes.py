"""K6 — AoE shape geometry tests."""
import math
import pytest
from spatial.models.vector2 import Vector2
from spatial.aoe.aoe_shapes import CircleShape, ConeShape, RectangleShape, RingShape


class TestCircleShape:
    def test_center_inside(self):
        c = CircleShape(center=Vector2(0, 0), radius=5.0)
        assert c.contains(Vector2(0, 0)) is True

    def test_point_on_edge(self):
        c = CircleShape(center=Vector2(0, 0), radius=5.0)
        assert c.contains(Vector2(5, 0)) is True

    def test_point_outside(self):
        c = CircleShape(center=Vector2(0, 0), radius=5.0)
        assert c.contains(Vector2(6, 0)) is False

    def test_area(self):
        c = CircleShape(center=Vector2(0, 0), radius=2.0)
        assert c.area() == pytest.approx(math.pi * 4)

    def test_intersects_overlapping_circle(self):
        c = CircleShape(center=Vector2(0, 0), radius=3.0)
        assert c.intersects_circle(Vector2(2, 0), 2.0) is True

    def test_intersects_non_overlapping(self):
        c = CircleShape(center=Vector2(0, 0), radius=1.0)
        assert c.intersects_circle(Vector2(5, 0), 1.0) is False

    def test_zero_radius_raises(self):
        with pytest.raises(ValueError):
            CircleShape(center=Vector2(0, 0), radius=0.0)

    def test_to_dict_shape_key(self):
        d = CircleShape(center=Vector2(0, 0), radius=1.0).to_dict()
        assert d["shape"] == "circle"


class TestConeShape:
    def test_point_in_cone(self):
        cone = ConeShape(
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            half_angle=math.pi / 4,
            length=10.0,
        )
        assert cone.contains(Vector2(5, 0)) is True

    def test_point_outside_angle(self):
        cone = ConeShape(
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            half_angle=math.pi / 6,  # 30 degrees
            length=10.0,
        )
        # 90 degrees off-axis — outside
        assert cone.contains(Vector2(0, 5)) is False

    def test_point_beyond_length(self):
        cone = ConeShape(
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            half_angle=math.pi / 4,
            length=3.0,
        )
        assert cone.contains(Vector2(5, 0)) is False

    def test_origin_inside(self):
        cone = ConeShape(
            origin=Vector2(0, 0),
            direction=Vector2(1, 0),
            half_angle=0.1,
            length=5.0,
        )
        assert cone.contains(Vector2(0, 0)) is True

    def test_invalid_half_angle_raises(self):
        with pytest.raises(ValueError):
            ConeShape(origin=Vector2(0, 0), direction=Vector2(1, 0), half_angle=0.0, length=5.0)

    def test_to_dict_shape_key(self):
        cone = ConeShape(origin=Vector2(0, 0), direction=Vector2(1, 0), half_angle=0.5, length=5.0)
        assert cone.to_dict()["shape"] == "cone"


class TestRectangleShape:
    def test_point_inside_axis_aligned(self):
        rect = RectangleShape(center=Vector2(0, 0), width=4.0, height=2.0)
        assert rect.contains(Vector2(1, 0.5)) is True

    def test_point_outside(self):
        rect = RectangleShape(center=Vector2(0, 0), width=4.0, height=2.0)
        assert rect.contains(Vector2(3, 0)) is False

    def test_point_on_corner(self):
        rect = RectangleShape(center=Vector2(0, 0), width=4.0, height=2.0)
        assert rect.contains(Vector2(2, 1)) is True

    def test_rotated_rectangle(self):
        rect = RectangleShape(
            center=Vector2(0, 0), width=4.0, height=2.0, rotation=math.pi / 2
        )
        # After 90° rotation, long axis is vertical
        assert rect.contains(Vector2(0, 1.5)) is True
        assert rect.contains(Vector2(1.5, 0)) is False

    def test_area(self):
        rect = RectangleShape(center=Vector2(0, 0), width=3.0, height=4.0)
        assert rect.area() == pytest.approx(12.0)

    def test_zero_width_raises(self):
        with pytest.raises(ValueError):
            RectangleShape(center=Vector2(0, 0), width=0.0, height=2.0)


class TestRingShape:
    def test_point_in_ring(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=2.0, outer_radius=5.0)
        assert ring.contains(Vector2(3, 0)) is True

    def test_point_inside_hole(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=2.0, outer_radius=5.0)
        assert ring.contains(Vector2(1, 0)) is False

    def test_point_outside_ring(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=2.0, outer_radius=5.0)
        assert ring.contains(Vector2(6, 0)) is False

    def test_point_on_outer_edge(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=1.0, outer_radius=3.0)
        assert ring.contains(Vector2(3, 0)) is True

    def test_invalid_inner_ge_outer_raises(self):
        with pytest.raises(ValueError):
            RingShape(center=Vector2(0, 0), inner_radius=5.0, outer_radius=3.0)

    def test_area(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=1.0, outer_radius=2.0)
        expected = math.pi * (4 - 1)
        assert ring.area() == pytest.approx(expected)

    def test_to_dict_shape_key(self):
        ring = RingShape(center=Vector2(0, 0), inner_radius=1.0, outer_radius=3.0)
        assert ring.to_dict()["shape"] == "ring"
