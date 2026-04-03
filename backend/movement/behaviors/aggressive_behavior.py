"""
L6 — Aggressive Targeting Behavior

Moves toward the player position (or a designated target) as fast as possible.
Charges directly at the nearest valid target each tick, updating direction
dynamically so it tracks moving targets.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_AGGRESSIVE


@dataclass
class AggressiveBehavior(BaseBehavior):
    """
    Charge directly toward the player / target at max speed.

    speed          — override speed (0 → state.max_speed)
    arrival_radius — stop within this distance (default 0.5 — melee range)
    charge_speed   — optional burst speed on initial approach (0 → use speed)
    """

    speed:          float = 0.0
    arrival_radius: float = 0.5
    charge_speed:   float = 0.0

    def __post_init__(self) -> None:
        if self.speed < 0:
            raise ValueError("speed must be >= 0")

    @property
    def behavior_type(self) -> str:
        return BEHAVIOR_AGGRESSIVE

    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        # Prefer explicit target_position on state; fall back to context
        target = state.target_position or context.get("player_position") or context.get("target_position")
        if target is None:
            return Vector2.zero()

        to_target = target - state.position
        dist = to_target.magnitude()

        if dist <= self.arrival_radius:
            return Vector2.zero()

        move_speed = self.charge_speed or self.speed or state.max_speed
        direction = to_target / dist

        # Don't overshoot
        step = move_speed * delta
        if step >= dist:
            return direction * (dist / delta)

        return direction * move_speed
