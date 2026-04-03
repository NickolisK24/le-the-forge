"""
L5 — Random Movement Behavior

Simulates unpredictable motion by periodically choosing a new random
direction and moving for a fixed interval. Optionally bounded to a wander
radius from a center point.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior, BEHAVIOR_RANDOM


@dataclass
class RandomBehavior(BaseBehavior):
    """
    Wander in random directions, changing direction periodically.

    speed           — movement speed (uses state.max_speed if 0)
    change_interval — seconds between direction changes (> 0)
    wander_radius   — if > 0, entity returns toward origin when it strays too far
    seed            — RNG seed for determinism (None → non-deterministic)
    """

    speed:           float = 0.0
    change_interval: float = 1.0
    wander_radius:   float = 0.0
    seed:            int | None = None

    # Internal mutable state
    _rng:            random.Random = field(default=None, init=False, repr=False)  # type: ignore[assignment]
    _time_to_change: float         = field(default=0.0, init=False, repr=False)
    _direction:      Vector2       = field(default=None, init=False, repr=False)  # type: ignore[assignment]
    _origin:         Vector2 | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.change_interval <= 0:
            raise ValueError("change_interval must be > 0")
        if self.speed < 0:
            raise ValueError("speed must be >= 0")
        self._rng = random.Random(self.seed)
        self._direction = self._random_direction()
        self._time_to_change = self.change_interval

    def _random_direction(self) -> Vector2:
        angle = self._rng.uniform(0, 2 * math.pi)
        return Vector2(math.cos(angle), math.sin(angle))

    @property
    def behavior_type(self) -> str:
        return BEHAVIOR_RANDOM

    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        # Remember starting origin on first call
        if self._origin is None:
            self._origin = state.position

        # Tick down the direction-change timer
        self._time_to_change -= delta
        if self._time_to_change <= 0:
            self._direction = self._random_direction()
            self._time_to_change = self.change_interval

        move_speed = self.speed if self.speed > 0 else state.max_speed

        # If wander_radius active and entity is too far, steer back
        if self.wander_radius > 0 and self._origin is not None:
            dist_from_origin = state.position.distance_to(self._origin)
            if dist_from_origin > self.wander_radius:
                return_dir = (self._origin - state.position).normalize()
                return return_dir * move_speed

        return self._direction * move_speed
