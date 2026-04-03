"""
L1 — Movement Vector System

Represents the motion state of an entity: a direction vector, a speed
magnitude, and an instantaneous acceleration. The resulting velocity is
direction * speed; acceleration is the rate at which speed changes.

Distinct from Vector2 (pure geometry): MovementVector models kinematic intent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from spatial.models.vector2 import Vector2


@dataclass
class MovementVector:
    """
    Kinematic description of an entity's motion.

    direction    — normalized unit vector (zero → stationary)
    speed        — scalar speed in world-units per second (>= 0)
    acceleration — signed rate of speed change in units/s² (may be negative)
    max_speed    — hard ceiling for speed after acceleration (> 0)
    """

    direction:    Vector2 = None  # type: ignore[assignment]
    speed:        float   = 0.0
    acceleration: float   = 0.0
    max_speed:    float   = 10.0

    def __post_init__(self) -> None:
        if self.direction is None:
            object.__setattr__(self, "direction", Vector2.zero())
        if self.speed < 0:
            raise ValueError("speed must be >= 0")
        if self.max_speed <= 0:
            raise ValueError("max_speed must be > 0")
        # Normalize direction if non-zero
        if self.direction.magnitude_sq() > 0.0:
            self.direction = self.direction.normalize()

    # ------------------------------------------------------------------
    # Derived
    # ------------------------------------------------------------------

    @property
    def velocity(self) -> Vector2:
        """Current velocity vector: direction × speed."""
        return self.direction * self.speed

    @property
    def is_moving(self) -> bool:
        return self.speed > 0.0 and self.direction.magnitude_sq() > 0.0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def set_direction(self, direction: Vector2) -> None:
        """Set and normalize the direction vector."""
        mag = direction.magnitude()
        if mag == 0.0:
            self.direction = Vector2.zero()
        else:
            self.direction = direction / mag

    def apply_acceleration(self, delta: float) -> None:
        """Update speed by acceleration * delta, clamped to [0, max_speed]."""
        if delta <= 0:
            raise ValueError("delta must be > 0")
        self.speed = max(0.0, min(self.max_speed, self.speed + self.acceleration * delta))

    def stop(self) -> None:
        self.speed = 0.0

    def point_toward(self, current: Vector2, target: Vector2) -> None:
        """Reorient direction to face *target* from *current*."""
        self.set_direction(target - current)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "direction":    self.direction.to_tuple(),
            "speed":        round(self.speed, 6),
            "acceleration": self.acceleration,
            "max_speed":    self.max_speed,
            "velocity":     self.velocity.to_tuple(),
            "is_moving":    self.is_moving,
        }

    @classmethod
    def stationary(cls, max_speed: float = 10.0) -> "MovementVector":
        return cls(direction=Vector2.zero(), speed=0.0, max_speed=max_speed)

    @classmethod
    def toward(
        cls,
        current: Vector2,
        target: Vector2,
        speed: float,
        max_speed: float = 10.0,
    ) -> "MovementVector":
        """Create a MovementVector pointing from *current* toward *target*."""
        direction = (target - current).normalize()
        return cls(direction=direction, speed=speed, max_speed=max_speed)
