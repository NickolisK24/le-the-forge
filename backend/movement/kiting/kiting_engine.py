"""
L15 — Kiting Simulation Engine

Models a player kiting strategy: maintain a preferred engagement range while
dealing damage. When enemies close to min_range, the player retreats; when
all enemies are beyond max_range, the player advances; within the band the
player stays stationary (or strafes).

The engine outputs the recommended player velocity vector each tick. Callers
combine this with their own damage/skill logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2


@dataclass(frozen=True)
class KiteResult:
    """Outcome of one kite evaluation tick."""

    recommended_velocity: Vector2
    kite_action:          str      # "retreat" | "advance" | "hold" | "strafe"
    closest_enemy_dist:   float
    is_kiting:            bool     # True when retreating


class KitingEngine:
    """
    Computes player movement recommendations to maintain a safe engagement range.

    min_range      — flee threshold (enemy closer than this → retreat)
    max_range      — advance threshold (all enemies farther than this → advance)
    kite_speed     — player retreat/advance speed (units/sec)
    strafe_speed   — lateral movement speed when holding (0 → stay still)
    """

    def __init__(
        self,
        min_range:    float = 5.0,
        max_range:    float = 15.0,
        kite_speed:   float = 7.0,
        strafe_speed: float = 0.0,
    ) -> None:
        if min_range < 0:
            raise ValueError("min_range must be >= 0")
        if max_range <= min_range:
            raise ValueError("max_range must be > min_range")
        if kite_speed <= 0:
            raise ValueError("kite_speed must be > 0")

        self.min_range   = min_range
        self.max_range   = max_range
        self.kite_speed  = kite_speed
        self.strafe_speed = strafe_speed

    def evaluate(
        self,
        player_pos:      Vector2,
        enemy_positions: list[Vector2],
    ) -> KiteResult:
        """
        Compute the recommended player velocity for the current frame.

        player_pos      — current player world position
        enemy_positions — list of enemy world positions (may be empty)
        """
        if not enemy_positions:
            return KiteResult(
                recommended_velocity=Vector2.zero(),
                kite_action="hold",
                closest_enemy_dist=float("inf"),
                is_kiting=False,
            )

        # Find the nearest enemy
        dists = [player_pos.distance_to(ep) for ep in enemy_positions]
        closest_dist = min(dists)
        closest_idx = dists.index(closest_dist)
        closest_pos = enemy_positions[closest_idx]

        away_dir = (player_pos - closest_pos).normalize()
        toward_dir = -away_dir

        if closest_dist < self.min_range:
            # Retreat directly away from the nearest enemy
            return KiteResult(
                recommended_velocity=away_dir * self.kite_speed,
                kite_action="retreat",
                closest_enemy_dist=closest_dist,
                is_kiting=True,
            )

        if closest_dist > self.max_range:
            # All enemies beyond max_range — advance toward nearest
            return KiteResult(
                recommended_velocity=toward_dir * self.kite_speed,
                kite_action="advance",
                closest_enemy_dist=closest_dist,
                is_kiting=False,
            )

        # In safe band — strafe laterally or hold
        if self.strafe_speed > 0:
            # Perpendicular to toward_dir (90° rotation)
            strafe_dir = Vector2(-toward_dir.y, toward_dir.x)
            return KiteResult(
                recommended_velocity=strafe_dir * self.strafe_speed,
                kite_action="strafe",
                closest_enemy_dist=closest_dist,
                is_kiting=False,
            )

        return KiteResult(
            recommended_velocity=Vector2.zero(),
            kite_action="hold",
            closest_enemy_dist=closest_dist,
            is_kiting=False,
        )

    def update_player_position(
        self,
        player_pos: Vector2,
        enemy_positions: list[Vector2],
        delta: float,
    ) -> tuple[Vector2, KiteResult]:
        """
        Evaluate kite and return (new_player_position, KiteResult).
        Convenience wrapper that integrates velocity × delta.
        """
        result = self.evaluate(player_pos, enemy_positions)
        new_pos = player_pos + result.recommended_velocity * delta
        return new_pos, result
