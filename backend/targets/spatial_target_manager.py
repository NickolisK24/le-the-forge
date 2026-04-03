"""
K11 — Target Spatial Manager

Wraps a TargetManager and layers 2D world-space positions (Vector2) on top
of each target. TargetEntity itself retains position_index for backwards
compatibility; SpatialTargetManager maintains a parallel position map.

Layout helpers (layout_linear, layout_circle) can automatically assign
positions based on target count and spacing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager


class SpatialTargetManager:
    """
    Adds 2D spatial positions to a TargetManager's entities.

    set_position(target_id, position)   — assign a world position
    get_position(target_id)             — retrieve position (default: Vector2.zero)
    move_target(target_id, position)    — alias for set_position
    positions_for_alive()               — [(TargetEntity, Vector2)] alive only
    positions_for_all()                 — [(TargetEntity, Vector2)] all targets
    targets_in_radius(center, radius)   — alive targets within distance
    targets_in_shape(shape)             — alive targets inside an AoE shape
    nearest_to(point, exclude_ids)      — alive target nearest to a point
    layout_linear(spacing, origin)      — arrange targets in a row
    layout_circle(radius, center)       — arrange targets in a circle
    """

    def __init__(self, manager: TargetManager) -> None:
        self._manager = manager
        self._positions: dict[str, Vector2] = {}

    @property
    def manager(self) -> TargetManager:
        return self._manager

    # ------------------------------------------------------------------
    # Position management
    # ------------------------------------------------------------------

    def set_position(self, target_id: str, position: Vector2) -> None:
        """Assign *position* to *target_id*. Raises KeyError if target missing."""
        _ = self._manager.get(target_id)  # validates existence
        self._positions[target_id] = position

    def get_position(self, target_id: str) -> Vector2:
        """Return the 2D position for *target_id* (default: Vector2.zero)."""
        return self._positions.get(target_id, Vector2.zero())

    def move_target(self, target_id: str, position: Vector2) -> None:
        """Alias for set_position."""
        self.set_position(target_id, position)

    # ------------------------------------------------------------------
    # Pair accessors
    # ------------------------------------------------------------------

    def positions_for_alive(self) -> list[tuple[TargetEntity, Vector2]]:
        """Return [(target, position)] for all alive targets."""
        return [
            (t, self.get_position(t.target_id))
            for t in self._manager.alive_targets()
        ]

    def positions_for_all(self) -> list[tuple[TargetEntity, Vector2]]:
        """Return [(target, position)] for every registered target."""
        return [
            (t, self.get_position(t.target_id))
            for t in self._manager.all_targets()
        ]

    # ------------------------------------------------------------------
    # Spatial queries
    # ------------------------------------------------------------------

    def targets_in_radius(
        self,
        center: Vector2,
        radius: float,
    ) -> list[TargetEntity]:
        """Return alive targets whose position is within *radius* of *center*."""
        if radius < 0:
            raise ValueError("radius must be >= 0")
        r_sq = radius * radius
        result: list[TargetEntity] = []
        for target in self._manager.alive_targets():
            pos = self.get_position(target.target_id)
            if center.distance_sq_to(pos) <= r_sq:
                result.append(target)
        return result

    def targets_in_shape(self, shape) -> list[TargetEntity]:
        """
        Return alive targets whose position is inside *shape*.
        Shape must implement contains(Vector2) → bool.
        """
        result: list[TargetEntity] = []
        for target in self._manager.alive_targets():
            pos = self.get_position(target.target_id)
            if shape.contains(pos):
                result.append(target)
        return result

    def nearest_to(
        self,
        point: Vector2,
        exclude_ids: set[str] | None = None,
    ) -> TargetEntity | None:
        """
        Return the alive target nearest to *point*, excluding any ids in
        *exclude_ids*. Returns None if no eligible targets exist.
        """
        exclude = exclude_ids or set()
        best: TargetEntity | None = None
        best_dist_sq = float("inf")
        for target in self._manager.alive_targets():
            if target.target_id in exclude:
                continue
            pos = self.get_position(target.target_id)
            dist_sq = point.distance_sq_to(pos)
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best = target
        return best

    def position_map(self, alive_only: bool = True) -> dict[str, tuple[Vector2, float]]:
        """
        Build a {target_id: (center, radius)} dict for CollisionEngine.
        *radius* is a fixed 0.5 unit collision box (override if needed).
        """
        targets = (
            self._manager.alive_targets()
            if alive_only
            else self._manager.all_targets()
        )
        return {
            t.target_id: (self.get_position(t.target_id), 0.5)
            for t in targets
        }

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def layout_linear(
        self,
        spacing: float = 2.0,
        origin: Vector2 | None = None,
        axis: Vector2 | None = None,
    ) -> None:
        """
        Place targets in a straight line along *axis* (default: +X) from *origin*.
        Targets are ordered by position_index ascending.
        """
        if spacing <= 0:
            raise ValueError("spacing must be > 0")
        start = origin or Vector2.zero()
        direction = (axis or Vector2(1.0, 0.0)).normalize()
        targets = sorted(self._manager.all_targets(), key=lambda t: t.position_index)
        for i, target in enumerate(targets):
            self._positions[target.target_id] = start + direction * (spacing * i)

    def layout_circle(
        self,
        radius: float = 5.0,
        center: Vector2 | None = None,
    ) -> None:
        """
        Place targets evenly around a circle of *radius* centred at *center*.
        """
        if radius <= 0:
            raise ValueError("radius must be > 0")
        c = center or Vector2.zero()
        targets = self._manager.all_targets()
        n = len(targets)
        if n == 0:
            return
        angle_step = 2.0 * math.pi / n
        for i, target in enumerate(targets):
            angle = angle_step * i
            pos = Vector2(
                c.x + radius * math.cos(angle),
                c.y + radius * math.sin(angle),
            )
            self._positions[target.target_id] = pos

    # ------------------------------------------------------------------
    # Delegation
    # ------------------------------------------------------------------

    def spawn(self, target: TargetEntity, position: Vector2 | None = None) -> None:
        """Spawn a target and optionally set its position."""
        self._manager.spawn(target)
        if position is not None:
            self._positions[target.target_id] = position

    def alive_count(self) -> int:
        return self._manager.alive_count

    def is_cleared(self) -> bool:
        return self._manager.is_cleared()

    def snapshot(self) -> list[dict]:
        result = []
        for t in self._manager.all_targets():
            d = t.to_dict()
            d["position"] = self.get_position(t.target_id).to_tuple()
            result.append(d)
        return result
