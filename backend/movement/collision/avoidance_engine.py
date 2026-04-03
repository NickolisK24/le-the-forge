"""
L11 — Collision Avoidance System

Separation steering: when entities come within avoidance_radius of each other,
compute a repulsion velocity vector to push them apart. Uses a simple inverse-
distance weighting so nearby entities generate stronger separation forces.

Does not guarantee zero overlap in a single tick — it provides a velocity
nudge that, over multiple ticks, prevents sustained overlap.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2


@dataclass
class AvoidanceResult:
    """Separation forces computed for a set of entities."""
    forces: dict[str, Vector2]   # entity_id → separation velocity
    overlap_pairs: list[tuple[str, str]]  # pairs still overlapping after force


class AvoidanceEngine:
    """
    Stateless separation-steering engine.

    compute_separation(entity_id, pos, others, radius, strength)
        — single entity separation vector

    apply_separation_all(positions, radius, max_speed)
        — separation vectors for the whole group
    """

    def compute_separation(
        self,
        entity_id: str,
        entity_pos: Vector2,
        other_positions: dict[str, Vector2],
        avoidance_radius: float,
        strength: float = 1.0,
    ) -> Vector2:
        """
        Compute the separation velocity vector for one entity.

        Each nearby entity contributes a repulsion force inversely proportional
        to distance. The total is clamped to strength magnitude.
        """
        if avoidance_radius <= 0:
            raise ValueError("avoidance_radius must be > 0")
        if strength < 0:
            raise ValueError("strength must be >= 0")

        separation = Vector2.zero()
        for other_id, other_pos in other_positions.items():
            if other_id == entity_id:
                continue
            to_other = entity_pos - other_pos
            dist = to_other.magnitude()
            if dist == 0.0:
                # Perfectly overlapping — push in arbitrary direction
                separation = separation + Vector2(1.0, 0.0) * strength
                continue
            if dist < avoidance_radius:
                # Repulsion inversely proportional to proximity
                weight = (avoidance_radius - dist) / avoidance_radius
                separation = separation + to_other.normalize() * (weight * strength)

        return separation

    def apply_separation_all(
        self,
        positions: dict[str, Vector2],
        avoidance_radius: float,
        max_speed: float = 5.0,
    ) -> AvoidanceResult:
        """
        Compute separation vectors for every entity in *positions*.
        Returns a dict of {entity_id: velocity_nudge} and a list of
        overlapping pairs (distance < avoidance_radius / 2).
        """
        if avoidance_radius <= 0:
            raise ValueError("avoidance_radius must be > 0")

        forces: dict[str, Vector2] = {}
        overlap_pairs: list[tuple[str, str]] = []

        entity_ids = list(positions.keys())
        for i, eid in enumerate(entity_ids):
            sep = self.compute_separation(
                eid, positions[eid], positions, avoidance_radius, strength=max_speed
            )
            # Clamp to max_speed
            mag = sep.magnitude()
            if mag > max_speed:
                sep = sep * (max_speed / mag)
            forces[eid] = sep

        # Detect overlap pairs
        for i in range(len(entity_ids)):
            for j in range(i + 1, len(entity_ids)):
                a, b = entity_ids[i], entity_ids[j]
                dist = positions[a].distance_to(positions[b])
                if dist < avoidance_radius / 2.0:
                    overlap_pairs.append((a, b))

        return AvoidanceResult(forces=forces, overlap_pairs=overlap_pairs)
