"""
L7 — Defensive Movement Behavior

Maintain a preferred distance band from a threat (e.g. the player or a
dangerous enemy). If the threat is closer than min_range, back away. If
farther than max_range, approach. Within the band, stay still.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_DEFENSIVE


@dataclass
class DefensiveBehavior(BaseBehavior):
    """
    Maintain separation from a threat within [min_range, max_range].

    min_range   — flee threshold: if threat is closer, back away
    max_range   — engage threshold: if threat is farther, approach
    speed       — movement speed (0 → state.max_speed)
    """

    min_range: float = 3.0
    max_range: float = 8.0
    speed:     float = 0.0

    def __post_init__(self) -> None:
        if self.min_range < 0:
            raise ValueError("min_range must be >= 0")
        if self.max_range <= self.min_range:
            raise ValueError("max_range must be > min_range")
        if self.speed < 0:
            raise ValueError("speed must be >= 0")

    @property
    def behavior_type(self) -> str:
        return BEHAVIOR_DEFENSIVE

    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        threat = (
            state.target_position
            or context.get("player_position")
            or context.get("threat_position")
            or context.get("target_position")
        )
        if threat is None:
            return Vector2.zero()

        to_threat = threat - state.position
        dist = to_threat.magnitude()

        if dist == 0.0:
            # Exactly on top of threat — escape in arbitrary direction
            return Vector2(1.0, 0.0) * (self.speed or state.max_speed)

        move_speed = self.speed or state.max_speed
        direction_to_threat = to_threat / dist

        if dist < self.min_range:
            # Too close — retreat directly away
            return -direction_to_threat * move_speed

        if dist > self.max_range:
            # Too far — approach
            step = move_speed * delta
            if step >= (dist - self.max_range):
                # Would overshoot desired max_range — stop at band edge
                return direction_to_threat * ((dist - self.max_range) / delta)
            return direction_to_threat * move_speed

        # In the safe band — stay still
        return Vector2.zero()
