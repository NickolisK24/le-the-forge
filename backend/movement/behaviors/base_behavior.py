"""
L3 — Movement Behavior Base Class

Abstract base for all movement behaviors. Each concrete behavior implements
compute_velocity() to return the desired velocity vector for the current tick.
The MovementTimelineSynchronizer calls update() which applies velocity to state.

Context dict keys (populated by caller):
    "target_position"  : Vector2 | None  — primary movement goal
    "player_position"  : Vector2 | None  — player world position (for enemy AI)
    "other_entities"   : list[(id, Vector2)] — peer positions for avoidance
    "elapsed_time"     : float — total simulation time
    "delta"            : float �� current tick size
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState

# Canonical behavior-type names
BEHAVIOR_IDLE       = "idle"
BEHAVIOR_LINEAR     = "linear"
BEHAVIOR_RANDOM     = "random"
BEHAVIOR_AGGRESSIVE = "aggressive"
BEHAVIOR_DEFENSIVE  = "defensive"
BEHAVIOR_ORBITING   = "orbiting"


class BaseBehavior(ABC):
    """
    Abstract movement behavior.

    All behaviors expose:
        behavior_type   : str  (read-only identifier)
        compute_velocity(state, context, delta) → Vector2
        update(state, context, delta) → None   (calls compute_velocity then applies)
    """

    @property
    @abstractmethod
    def behavior_type(self) -> str:
        """Canonical string identifier for this behavior."""
        ...

    @abstractmethod
    def compute_velocity(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> Vector2:
        """
        Compute the desired velocity for this tick.
        Must not modify *state* directly.
        Returns a Vector2 (may be zero if the entity should not move).
        """
        ...

    def update(
        self,
        state: MovementState,
        context: dict,
        delta: float,
    ) -> None:
        """
        Compute velocity and apply it to *state*.
        Updates state.velocity, state.behavior_type, and calls apply_movement.
        """
        v = self.compute_velocity(state, context, delta)
        state.behavior_type = self.behavior_type
        state.set_velocity(v)
        state.apply_movement(delta)
