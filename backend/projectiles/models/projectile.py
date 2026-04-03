"""
K3 — Projectile Model

Represents a single moving damage object in flight. A Projectile is spawned
from a skill activation, travels along a direction vector at a fixed speed,
and becomes inactive when it hits a target, exceeds its range, or exhausts
pierce stacks.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2


@dataclass
class Projectile:
    """
    Mutable record for an in-flight projectile.

    projectile_id    — unique identifier (auto-generated if not given)
    origin           — spawn position in world-space
    direction        — unit vector defining travel direction
    speed            — world-units per second
    damage           — base damage on impact
    skill_id         — id of the skill that spawned this
    max_range        — maximum travel distance before expiry (default: inf)
    pierce_count     — number of additional targets this can hit after first (0 = no pierce)
    radius           — collision detection radius for hit tests
    is_active        — False once expired or destroyed
    position         — current world-space position (advances with travel)
    distance_traveled — total distance moved since spawn
    targets_hit      — set of target_ids already struck this flight
    spawn_time       — simulation time at spawn (for age calculation)
    """

    origin:     Vector2
    direction:  Vector2
    speed:      float
    damage:     float
    skill_id:   str

    projectile_id:     str   = field(default_factory=lambda: str(uuid.uuid4())[:8])
    max_range:         float = float("inf")
    pierce_count:      int   = 0
    radius:            float = 0.5
    spawn_time:        float = 0.0

    # Mutable flight state — not constructor args, set in __post_init__
    is_active:         bool           = field(default=True,   init=False)
    position:          Vector2        = field(default=None,   init=False)  # type: ignore[assignment]
    distance_traveled: float          = field(default=0.0,    init=False)
    targets_hit:       set[str]       = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        if self.speed <= 0:
            raise ValueError("speed must be > 0")
        if self.damage < 0:
            raise ValueError("damage must be >= 0")
        if self.max_range <= 0:
            raise ValueError("max_range must be > 0")
        if self.pierce_count < 0:
            raise ValueError("pierce_count must be >= 0")
        if self.radius <= 0:
            raise ValueError("radius must be > 0")
        # Normalize direction
        norm = self.direction.normalize()
        if norm.magnitude_sq() == 0.0:
            raise ValueError("direction must not be a zero vector")
        object.__setattr__(self, "direction", norm)
        # Start at origin
        object.__setattr__(self, "position", self.origin)

    # ------------------------------------------------------------------
    # Travel
    # ------------------------------------------------------------------

    def advance(self, delta: float) -> None:
        """
        Move the projectile forward by *delta* seconds.
        Deactivates automatically when max_range is exceeded.
        """
        if not self.is_active:
            return
        if delta <= 0:
            raise ValueError("delta must be > 0")
        step = self.speed * delta
        new_pos = self.position + self.direction * step
        new_dist = self.distance_traveled + step
        object.__setattr__(self, "position", new_pos)
        object.__setattr__(self, "distance_traveled", new_dist)
        if new_dist >= self.max_range:
            object.__setattr__(self, "is_active", False)

    # ------------------------------------------------------------------
    # Hit tracking
    # ------------------------------------------------------------------

    def record_hit(self, target_id: str) -> None:
        """Mark *target_id* as struck. Decrements pierce_count; deactivates if exhausted."""
        self.targets_hit.add(target_id)
        remaining = self.pierce_count - 1
        object.__setattr__(self, "pierce_count", remaining)
        if remaining < 0:
            object.__setattr__(self, "is_active", False)

    def has_hit(self, target_id: str) -> bool:
        return target_id in self.targets_hit

    def deactivate(self) -> None:
        object.__setattr__(self, "is_active", False)

    # ------------------------------------------------------------------
    # Age
    # ------------------------------------------------------------------

    def age(self, now: float) -> float:
        """Seconds elapsed since spawn."""
        return max(0.0, now - self.spawn_time)

    def range_remaining(self) -> float:
        return max(0.0, self.max_range - self.distance_traveled)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "projectile_id":     self.projectile_id,
            "skill_id":          self.skill_id,
            "position":          self.position.to_tuple(),
            "direction":         self.direction.to_tuple(),
            "speed":             self.speed,
            "damage":            self.damage,
            "distance_traveled": round(self.distance_traveled, 6),
            "max_range":         self.max_range,
            "pierce_count":      self.pierce_count,
            "is_active":         self.is_active,
            "targets_hit":       sorted(self.targets_hit),
        }
