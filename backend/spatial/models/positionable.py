"""
K2 — Positionable Entity Model

Mixin dataclass that adds 2D position and velocity support to any entity.
Used as the base for SpatialTarget and Projectile-derived objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2


@dataclass
class Positionable:
    """
    Base class for entities with a 2D world position and velocity.

    position — current location in world-space (units)
    velocity — movement vector in units-per-second
    """

    position: Vector2 = field(default_factory=Vector2.zero)
    velocity: Vector2 = field(default_factory=Vector2.zero)

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, delta: float) -> None:
        """
        Advance position by velocity * delta seconds.
        Raises ValueError if delta <= 0.
        """
        if delta <= 0:
            raise ValueError("delta must be > 0")
        self.position = self.position + self.velocity * delta

    def set_position(self, position: Vector2) -> None:
        """Teleport to *position*."""
        self.position = position

    def set_velocity(self, velocity: Vector2) -> None:
        """Change velocity without moving."""
        self.velocity = velocity

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def distance_to(self, other: "Positionable") -> float:
        """Euclidean distance to another Positionable."""
        return self.position.distance_to(other.position)

    def distance_to_point(self, point: Vector2) -> float:
        """Euclidean distance to a world-space point."""
        return self.position.distance_to(point)

    def is_within_range(self, point: Vector2, radius: float) -> bool:
        """True if this entity's position is within *radius* of *point*."""
        return self.position.distance_sq_to(point) <= radius * radius

    def direction_to(self, target: Vector2) -> Vector2:
        """
        Normalized direction vector pointing from this entity toward *target*.
        Returns Vector2.zero() if already at target.
        """
        return (target - self.position).normalize()

    def speed(self) -> float:
        """Scalar speed (magnitude of velocity)."""
        return self.velocity.magnitude()

    def snapshot(self) -> dict:
        return {
            "position": self.position.to_tuple(),
            "velocity": self.velocity.to_tuple(),
            "speed":    round(self.speed(), 4),
        }
