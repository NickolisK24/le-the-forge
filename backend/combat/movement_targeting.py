"""
L14 — Movement-Based Target Selection

Selects combat targets based on their 2D positions relative to the player.
Provides multiple selection strategies driven by current movement state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity


@dataclass(frozen=True)
class TargetingResult:
    """Outcome of a target selection query."""

    primary:   TargetEntity | None
    secondary: list[TargetEntity]
    strategy:  str
    count:     int


class MovementTargeting:
    """
    Position-aware target selection.

    nearest_to_player(player_pos, targets_with_pos)
    farthest_from_player(player_pos, targets_with_pos)
    targets_in_range(center, radius, targets_with_pos)
    targets_in_cone(origin, direction, half_angle, range, targets_with_pos)
    most_isolated(targets_with_pos, isolation_radius)
    closest_n(player_pos, targets_with_pos, n)
    """

    # ------------------------------------------------------------------
    # Single-target strategies
    # ------------------------------------------------------------------

    @staticmethod
    def nearest_to_player(
        player_pos: Vector2,
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
    ) -> TargetingResult:
        """Select the alive target nearest to the player."""
        alive = [(t, p) for t, p in targets_with_pos if t.is_alive]
        if not alive:
            return TargetingResult(None, [], "nearest", 0)
        best = min(alive, key=lambda tp: player_pos.distance_sq_to(tp[1]))
        rest = [t for t, _ in alive if t.target_id != best[0].target_id]
        return TargetingResult(best[0], rest, "nearest", len(alive))

    @staticmethod
    def farthest_from_player(
        player_pos: Vector2,
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
    ) -> TargetingResult:
        """Select the alive target farthest from the player."""
        alive = [(t, p) for t, p in targets_with_pos if t.is_alive]
        if not alive:
            return TargetingResult(None, [], "farthest", 0)
        best = max(alive, key=lambda tp: player_pos.distance_sq_to(tp[1]))
        rest = [t for t, _ in alive if t.target_id != best[0].target_id]
        return TargetingResult(best[0], rest, "farthest", len(alive))

    # ------------------------------------------------------------------
    # Multi-target strategies
    # ------------------------------------------------------------------

    @staticmethod
    def targets_in_range(
        center: Vector2,
        radius: float,
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
    ) -> TargetingResult:
        """All alive targets within *radius* of *center*."""
        if radius <= 0:
            raise ValueError("radius must be > 0")
        r_sq = radius * radius
        in_range = [
            t for t, p in targets_with_pos
            if t.is_alive and center.distance_sq_to(p) <= r_sq
        ]
        primary = in_range[0] if in_range else None
        return TargetingResult(primary, in_range[1:], "in_range", len(in_range))

    @staticmethod
    def targets_in_cone(
        origin: Vector2,
        direction: Vector2,
        half_angle: float,
        cone_range: float,
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
    ) -> TargetingResult:
        """All alive targets inside a cone defined by origin/direction/half_angle/range."""
        if half_angle <= 0 or half_angle > math.pi:
            raise ValueError("half_angle must be in (0, π]")
        if cone_range <= 0:
            raise ValueError("cone_range must be > 0")

        dir_norm = direction.normalize()
        results: list[TargetEntity] = []

        for target, pos in targets_with_pos:
            if not target.is_alive:
                continue
            to_target = pos - origin
            dist = to_target.magnitude()
            if dist > cone_range:
                continue
            if dist == 0.0:
                results.append(target)
                continue
            angle = dir_norm.angle_to(to_target)
            if angle <= half_angle:
                results.append(target)

        primary = results[0] if results else None
        return TargetingResult(primary, results[1:], "cone", len(results))

    @staticmethod
    def most_isolated(
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
        isolation_radius: float = 5.0,
    ) -> TargetingResult:
        """
        Find the alive target with fewest neighbors within isolation_radius.
        Returns the most isolated target as primary.
        """
        if isolation_radius <= 0:
            raise ValueError("isolation_radius must be > 0")
        alive = [(t, p) for t, p in targets_with_pos if t.is_alive]
        if not alive:
            return TargetingResult(None, [], "most_isolated", 0)

        r_sq = isolation_radius * isolation_radius
        scores: list[tuple[int, TargetEntity]] = []
        for t, p in alive:
            neighbor_count = sum(
                1 for other_t, other_p in alive
                if other_t.target_id != t.target_id
                and p.distance_sq_to(other_p) <= r_sq
            )
            scores.append((neighbor_count, t))

        scores.sort(key=lambda s: s[0])
        primary = scores[0][1]
        rest = [s[1] for s in scores[1:]]
        return TargetingResult(primary, rest, "most_isolated", len(alive))

    @staticmethod
    def closest_n(
        player_pos: Vector2,
        targets_with_pos: list[tuple[TargetEntity, Vector2]],
        n: int,
    ) -> TargetingResult:
        """Return the *n* closest alive targets to *player_pos*."""
        if n <= 0:
            raise ValueError("n must be > 0")
        alive = [(t, p) for t, p in targets_with_pos if t.is_alive]
        alive.sort(key=lambda tp: player_pos.distance_sq_to(tp[1]))
        selected = [t for t, _ in alive[:n]]
        primary = selected[0] if selected else None
        return TargetingResult(primary, selected[1:], "closest_n", len(selected))
