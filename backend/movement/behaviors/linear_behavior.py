"""
L4 — Linear Movement Behavior

Moves an entity in a straight line toward a target position at a constant
speed. Stops and clears velocity when within arrival_radius of the target.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_LINEAR


@dataclass
class LinearBehavior(BaseBehavior):
    """
    Move toward state.target_position at max_speed.

    speed          — units per second (uses state.max_speed if not set here)
    arrival_radius — distance at which the entity is considered to have arrived
    """

    speed:          float = 0.0        # 0 → use state.max_speed
    arrival_radius: float = 0.1

    def __post_init__(self) -> None:
        if self.speed < 0:
            raise ValueError("speed must be >= 0")
        if self.arrival_radius < 0:
            raise ValueError("arrival_radius must be >= 0")

    @property
    def behavior_type(self) -> str:
        return BEHAVIOR_LINEAR

    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        target = state.target_position or context.get("target_position")
        if target is None:
            return Vector2.zero()

        to_target = target - state.position
        dist = to_target.magnitude()

        if dist <= self.arrival_radius:
            return Vector2.zero()

        move_speed = self.speed if self.speed > 0 else state.max_speed
        direction = to_target / dist

        # Don't overshoot
        step = move_speed * delta
        if step >= dist:
            return direction * (dist / delta)

        return direction * move_speed
