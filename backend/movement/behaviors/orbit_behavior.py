"""
L8 — Orbiting Behavior

Circles an entity around a pivot point (e.g. the player or a boss) at a
fixed orbit radius and angular velocity. Uses direct angular integration
rather than steering so the orbit remains perfectly circular regardless
of delta size.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_ORBITING


@dataclass
class OrbitBehavior(BaseBehavior):
    """
    Orbit a pivot at a fixed radius and angular speed.

    orbit_radius   — distance from pivot to maintain (> 0)
    angular_speed  — radians per second (positive = counter-clockwise)
    initial_angle  — starting angle in radians (default: computed from entity position)
    """

    orbit_radius:  float = 5.0
    angular_speed: float = 1.0       # rad/s
    initial_angle: float | None = None

    _current_angle: float = field(default=None, init=False, repr=False)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.orbit_radius <= 0:
            raise ValueError("orbit_radius must be > 0")
        # _current_angle is initialised lazily on first update

    @property
    def behavior_type(self) -> str:
        return BEHAVIOR_ORBITING

    def _get_pivot(self, state: MovementState, context: dict) -> Vector2 | None:
        return (
            state.target_position
            or context.get("target_position")
            or context.get("player_position")
        )

    def _init_angle(self, state: MovementState, pivot: Vector2) -> None:
        if self.initial_angle is not None:
            self._current_angle = self.initial_angle
        else:
            delta_pos = state.position - pivot
            if delta_pos.magnitude_sq() == 0.0:
                self._current_angle = 0.0
            else:
                self._current_angle = math.atan2(delta_pos.y, delta_pos.x)

    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        pivot = self._get_pivot(state, context)
        if pivot is None:
            return Vector2.zero()

        # Lazy-initialize angle from current position
        if self._current_angle is None:
            self._init_angle(state, pivot)

        # Advance angle
        self._current_angle += self.angular_speed * delta

        # Desired position on the orbit circle
        desired_pos = Vector2(
            pivot.x + self.orbit_radius * math.cos(self._current_angle),
            pivot.y + self.orbit_radius * math.sin(self._current_angle),
        )

        # Velocity = displacement / delta (teleports to orbit, never overshoots)
        displacement = desired_pos - state.position
        return displacement / delta if delta > 0 else Vector2.zero()
