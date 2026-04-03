"""
K5 — Collision Detection Engine

Geometric primitives for detecting projectile-to-target and shape-to-target
intersections. All operations are pure functions with no side effects.

Coordinate system: 2D Cartesian (x, y). All distances in world-units.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from projectiles.models.projectile import Projectile


@dataclass(frozen=True)
class CollisionResult:
    """Result of a single projectile-vs-target collision check."""
    hit:          bool
    target_id:    str
    distance:     float   # distance between projectile position and target center


class CollisionEngine:
    """
    Stateless collision detection utilities.

    check_point_circle      — is a point inside a circle?
    check_circle_circle     — do two circles overlap?
    check_projectile_target — does a projectile collide with a circular target?
    find_hits               — all targets hit by a projectile this tick
    find_first_hit          — nearest target hit (for non-piercing projectiles)
    """

    # ------------------------------------------------------------------
    # Geometric primitives
    # ------------------------------------------------------------------

    @staticmethod
    def check_point_circle(
        point: Vector2,
        center: Vector2,
        radius: float,
    ) -> bool:
        """True if *point* lies within the circle defined by *center* / *radius*."""
        if radius < 0:
            raise ValueError("radius must be >= 0")
        return point.distance_sq_to(center) <= radius * radius

    @staticmethod
    def check_circle_circle(
        center1: Vector2,
        radius1: float,
        center2: Vector2,
        radius2: float,
    ) -> bool:
        """True if two circles overlap (touching counts as a hit)."""
        if radius1 < 0 or radius2 < 0:
            raise ValueError("radii must be >= 0")
        combined = radius1 + radius2
        return center1.distance_sq_to(center2) <= combined * combined

    @staticmethod
    def check_segment_circle(
        segment_start: Vector2,
        segment_end: Vector2,
        circle_center: Vector2,
        circle_radius: float,
    ) -> bool:
        """
        True if the line segment from *segment_start* to *segment_end*
        passes through the circle.
        """
        d = segment_end - segment_start
        f = segment_start - circle_center
        a = d.dot(d)
        b = 2.0 * f.dot(d)
        c = f.dot(f) - circle_radius * circle_radius

        discriminant = b * b - 4.0 * a * c
        if discriminant < 0:
            return False
        import math
        discriminant = math.sqrt(discriminant)
        t1 = (-b - discriminant) / (2.0 * a) if a != 0 else float("inf")
        t2 = (-b + discriminant) / (2.0 * a) if a != 0 else float("inf")
        return (0.0 <= t1 <= 1.0) or (0.0 <= t2 <= 1.0)

    # ------------------------------------------------------------------
    # Projectile vs targets
    # ------------------------------------------------------------------

    def check_projectile_target(
        self,
        projectile: Projectile,
        target_center: Vector2,
        target_radius: float,
    ) -> bool:
        """
        True if the projectile's current position overlaps the target circle.
        Uses circle–circle test: projectile.radius vs target_radius.
        """
        return self.check_circle_circle(
            projectile.position,
            projectile.radius,
            target_center,
            target_radius,
        )

    def find_hits(
        self,
        projectile: Projectile,
        target_positions: dict[str, tuple[Vector2, float]],
    ) -> list[CollisionResult]:
        """
        Find all targets hit by *projectile* at its current position.

        target_positions: {target_id: (center, radius)}

        Skips targets the projectile has already hit.
        Returns CollisionResult list sorted by distance (nearest first).
        """
        results: list[CollisionResult] = []
        for target_id, (center, radius) in target_positions.items():
            if projectile.has_hit(target_id):
                continue
            dist = projectile.position.distance_to(center)
            hit = self.check_circle_circle(
                projectile.position, projectile.radius, center, radius
            )
            if hit:
                results.append(CollisionResult(hit=True, target_id=target_id, distance=dist))
        results.sort(key=lambda r: r.distance)
        return results

    def find_first_hit(
        self,
        projectile: Projectile,
        target_positions: dict[str, tuple[Vector2, float]],
    ) -> CollisionResult | None:
        """
        Return the nearest un-hit target the projectile collides with,
        or None if no collision.
        """
        hits = self.find_hits(projectile, target_positions)
        return hits[0] if hits else None
