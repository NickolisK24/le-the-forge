"""
K1 — 2D Vector Math Utilities

Immutable 2D vector with standard arithmetic operations, distance helpers,
and interpolation. Used throughout the spatial and projectile systems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vector2:
    """
    Immutable 2D coordinate / direction vector.

    All arithmetic operators return new Vector2 instances.
    """

    x: float = 0.0
    y: float = 0.0

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector2":
        if scalar == 0.0:
            raise ZeroDivisionError("Cannot divide Vector2 by zero")
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> "Vector2":
        return Vector2(-self.x, -self.y)

    # ------------------------------------------------------------------
    # Magnitude & distance
    # ------------------------------------------------------------------

    def magnitude(self) -> float:
        """Euclidean length of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def magnitude_sq(self) -> float:
        """Squared length — cheaper than magnitude when only comparing."""
        return self.x * self.x + self.y * self.y

    def distance_to(self, other: "Vector2") -> float:
        """Euclidean distance to *other*."""
        return (self - other).magnitude()

    def distance_sq_to(self, other: "Vector2") -> float:
        """Squared distance to *other* (no sqrt)."""
        return (self - other).magnitude_sq()

    # ------------------------------------------------------------------
    # Direction helpers
    # ------------------------------------------------------------------

    def normalize(self) -> "Vector2":
        """
        Return unit vector in the same direction.
        Returns Vector2(0, 0) for a zero vector.
        """
        m = self.magnitude()
        if m == 0.0:
            return Vector2(0.0, 0.0)
        return Vector2(self.x / m, self.y / m)

    def dot(self, other: "Vector2") -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def angle_to(self, other: "Vector2") -> float:
        """
        Angle in radians between this vector and *other*.
        Returns value in [0, π].
        """
        mag_product = self.magnitude() * other.magnitude()
        if mag_product == 0.0:
            return 0.0
        cos_a = max(-1.0, min(1.0, self.dot(other) / mag_product))
        return math.acos(cos_a)

    def rotate(self, angle_radians: float) -> "Vector2":
        """Rotate the vector counter-clockwise by *angle_radians*."""
        cos_a = math.cos(angle_radians)
        sin_a = math.sin(angle_radians)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )

    # ------------------------------------------------------------------
    # Interpolation
    # ------------------------------------------------------------------

    def lerp(self, other: "Vector2", t: float) -> "Vector2":
        """
        Linear interpolation towards *other*.
        t=0 → self, t=1 → other. t is not clamped.
        """
        return self + (other - self) * t

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> "Vector2":
        return cls(float(t[0]), float(t[1]))

    @classmethod
    def zero(cls) -> "Vector2":
        return cls(0.0, 0.0)

    @classmethod
    def unit_x(cls) -> "Vector2":
        return cls(1.0, 0.0)

    @classmethod
    def unit_y(cls) -> "Vector2":
        return cls(0.0, 1.0)

    def __repr__(self) -> str:
        return f"Vector2({self.x:.4f}, {self.y:.4f})"
