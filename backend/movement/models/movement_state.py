"""
L2 — Movement State Model

Tracks the full kinematic state of a single entity across simulation ticks.
Each entity in the movement system owns one MovementState. The timeline
synchronizer reads state, behaviors mutate velocity, sync applies position.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2


@dataclass
class MovementState:
    """
    Mutable per-entity movement record.

    entity_id        — owning entity identifier
    position         — current world-space location
    velocity         — current movement vector (units/sec)
    acceleration     — current acceleration vector (units/sec²)
    target_position  — optional navigation goal
    max_speed        — velocity magnitude ceiling (units/sec)
    is_moving        — True when velocity magnitude > epsilon
    behavior_type    — label of the active behavior ("idle", "linear", …)
    distance_moved   — cumulative distance traveled this simulation run
    time_alive       — cumulative time this state has been updated (seconds)
    """

    entity_id:       str
    position:        Vector2

    velocity:        Vector2       = field(default_factory=Vector2.zero)
    acceleration:    Vector2       = field(default_factory=Vector2.zero)
    target_position: Vector2 | None = None
    max_speed:       float          = 5.0
    is_moving:       bool           = False
    behavior_type:   str            = "idle"
    distance_moved:  float          = 0.0
    time_alive:      float          = 0.0

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id must not be empty")
        if self.max_speed <= 0:
            raise ValueError("max_speed must be > 0")

    # ------------------------------------------------------------------
    # Integration
    # ------------------------------------------------------------------

    def apply_movement(self, delta: float) -> float:
        """
        Update position by velocity × delta.
        Returns distance moved this tick.
        """
        if delta <= 0:
            raise ValueError("delta must be > 0")
        step = self.velocity * delta
        dist = step.magnitude()
        self.position = self.position + step
        self.distance_moved += dist
        self.time_alive += delta
        self.is_moving = dist > 1e-9
        return dist

    def set_velocity(self, v: Vector2) -> None:
        """
        Set velocity, clamping its magnitude to max_speed.
        Automatically updates is_moving.
        """
        mag = v.magnitude()
        if mag > self.max_speed:
            v = v * (self.max_speed / mag)
        self.velocity = v
        self.is_moving = v.magnitude_sq() > 1e-12

    def stop(self) -> None:
        self.velocity = Vector2.zero()
        self.is_moving = False

    def set_target(self, target: Vector2 | None) -> None:
        self.target_position = target

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def distance_to_target(self) -> float | None:
        """Euclidean distance to target_position, or None if no target set."""
        if self.target_position is None:
            return None
        return self.position.distance_to(self.target_position)

    def has_reached_target(self, arrival_radius: float = 0.1) -> bool:
        """True if within arrival_radius of target_position."""
        dist = self.distance_to_target()
        if dist is None:
            return False
        return dist <= arrival_radius

    def speed(self) -> float:
        return self.velocity.magnitude()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "entity_id":      self.entity_id,
            "position":       self.position.to_tuple(),
            "velocity":       self.velocity.to_tuple(),
            "speed":          round(self.speed(), 4),
            "max_speed":      self.max_speed,
            "is_moving":      self.is_moving,
            "behavior_type":  self.behavior_type,
            "distance_moved": round(self.distance_moved, 4),
            "time_alive":     round(self.time_alive, 4),
            "target_position": self.target_position.to_tuple() if self.target_position else None,
        }
