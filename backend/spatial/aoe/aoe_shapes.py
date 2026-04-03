"""
K6 — Area-of-Effect Geometry

Defines the four AoE shapes used by spells and ground effects:
  - CircleShape    (radial blast)
  - ConeShape      (directional sweep)
  - RectangleShape (beam / ground slam)
  - RingShape      (donut / hollow circle)

All shapes expose:
  contains(point)  → bool          — point-in-shape test
  area()           → float         — approximate 2D area
  to_dict()        → dict          — serialisable snapshot
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from spatial.models.vector2 import Vector2


# ---------------------------------------------------------------------------
# Circle
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CircleShape:
    """Filled circle centred at *center* with given *radius*."""

    center: Vector2
    radius: float

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("radius must be > 0")

    def contains(self, point: Vector2) -> bool:
        """True if *point* lies inside or on the boundary."""
        return self.center.distance_sq_to(point) <= self.radius * self.radius

    def intersects_circle(self, other_center: Vector2, other_radius: float) -> bool:
        """True if this circle overlaps another circle."""
        combined = self.radius + other_radius
        return self.center.distance_sq_to(other_center) <= combined * combined

    def area(self) -> float:
        return math.pi * self.radius * self.radius

    def to_dict(self) -> dict:
        return {
            "shape": "circle",
            "center": self.center.to_tuple(),
            "radius": self.radius,
            "area":   round(self.area(), 4),
        }


# ---------------------------------------------------------------------------
# Cone
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConeShape:
    """
    Cone originating at *origin* pointing in *direction*.

    half_angle — half the opening angle in radians (full angle = 2 * half_angle)
    length     — reach of the cone along *direction*
    """

    origin:     Vector2
    direction:  Vector2
    half_angle: float
    length:     float

    def __post_init__(self) -> None:
        if not (0.0 < self.half_angle <= math.pi):
            raise ValueError("half_angle must be in (0, π]")
        if self.length <= 0:
            raise ValueError("length must be > 0")
        norm = self.direction.normalize()
        if norm.magnitude_sq() == 0.0:
            raise ValueError("direction must not be a zero vector")
        object.__setattr__(self, "direction", norm)

    def contains(self, point: Vector2) -> bool:
        """True if *point* is within the cone sector."""
        to_point = point - self.origin
        dist = to_point.magnitude()
        if dist > self.length:
            return False
        if dist == 0.0:
            return True
        angle = self.direction.angle_to(to_point)
        return angle <= self.half_angle

    def area(self) -> float:
        """Area of the circular sector."""
        return self.half_angle * self.length * self.length

    def to_dict(self) -> dict:
        return {
            "shape":      "cone",
            "origin":     self.origin.to_tuple(),
            "direction":  self.direction.to_tuple(),
            "half_angle": round(self.half_angle, 6),
            "length":     self.length,
            "area":       round(self.area(), 4),
        }


# ---------------------------------------------------------------------------
# Rectangle
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RectangleShape:
    """
    Axis-aligned rectangle centred at *center*, optionally rotated.

    width    — full extent along local X axis
    height   — full extent along local Y axis
    rotation — counter-clockwise rotation in radians (0 = axis-aligned)
    """

    center:   Vector2
    width:    float
    height:   float
    rotation: float = 0.0

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError("width must be > 0")
        if self.height <= 0:
            raise ValueError("height must be > 0")

    def contains(self, point: Vector2) -> bool:
        """True if *point* is within the (possibly rotated) rectangle."""
        # Translate to rectangle-local space
        local = point - self.center
        # Rotate back by -rotation to align with axes
        cos_r = math.cos(-self.rotation)
        sin_r = math.sin(-self.rotation)
        lx = local.x * cos_r - local.y * sin_r
        ly = local.x * sin_r + local.y * cos_r
        half_w = self.width / 2.0
        half_h = self.height / 2.0
        return (-half_w <= lx <= half_w) and (-half_h <= ly <= half_h)

    def area(self) -> float:
        return self.width * self.height

    def to_dict(self) -> dict:
        return {
            "shape":    "rectangle",
            "center":   self.center.to_tuple(),
            "width":    self.width,
            "height":   self.height,
            "rotation": round(self.rotation, 6),
            "area":     round(self.area(), 4),
        }


# ---------------------------------------------------------------------------
# Ring
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RingShape:
    """
    Hollow ring (annulus) centred at *center*.

    inner_radius — inside edge (exclusive)
    outer_radius — outside edge (inclusive)
    """

    center:       Vector2
    inner_radius: float
    outer_radius: float

    def __post_init__(self) -> None:
        if self.inner_radius < 0:
            raise ValueError("inner_radius must be >= 0")
        if self.outer_radius <= 0:
            raise ValueError("outer_radius must be > 0")
        if self.inner_radius >= self.outer_radius:
            raise ValueError("inner_radius must be < outer_radius")

    def contains(self, point: Vector2) -> bool:
        """True if *point* is in the annular band."""
        dist_sq = self.center.distance_sq_to(point)
        return (
            dist_sq > self.inner_radius * self.inner_radius
            and dist_sq <= self.outer_radius * self.outer_radius
        )

    def area(self) -> float:
        return math.pi * (self.outer_radius ** 2 - self.inner_radius ** 2)

    def to_dict(self) -> dict:
        return {
            "shape":        "ring",
            "center":       self.center.to_tuple(),
            "inner_radius": self.inner_radius,
            "outer_radius": self.outer_radius,
            "area":         round(self.area(), 4),
        }


# ---------------------------------------------------------------------------
# Union type hint
# ---------------------------------------------------------------------------

AoeShape = CircleShape | ConeShape | RectangleShape | RingShape

__all__ = [
    "CircleShape",
    "ConeShape",
    "RectangleShape",
    "RingShape",
    "AoeShape",
]
