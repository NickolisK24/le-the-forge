"""
K9 — Spatial Splash Damage Engine

2D splash damage using true Euclidean distance (Vector2) rather than the
1-D position_index proxy used by the Phase I SplashEngine in damage/.

Given an impact point and a radius, all targets within range take
falloff-adjusted damage based on their distance from the impact center.

    damage(d) = base_damage * max(0, 1 - falloff * d / radius)

A target exactly at the impact point (d=0) takes full base_damage.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity


@dataclass(frozen=True)
class SpatialSplashResult:
    """Outcome of one splash application."""

    impact_point: Vector2
    radius:       float
    hits:         list[dict]      # [{target_id, distance, damage_dealt, killed}]
    targets_hit:  int
    total_damage: float


class SpatialSplashEngine:
    """
    execute(base_damage, impact_point, targets_with_positions, radius, falloff)
        → SpatialSplashResult

    base_damage            — full damage at the impact point (d=0)
    impact_point           — 2D world-space epicentre
    targets_with_positions — [(TargetEntity, Vector2)] pool
    radius                 — blast radius in world-units
    falloff                — damage reduction fraction (0 = flat damage, 1 = linear to zero at edge)
    """

    def execute(
        self,
        base_damage: float,
        impact_point: Vector2,
        targets_with_positions: list[tuple[TargetEntity, Vector2]],
        radius: float = 2.0,
        falloff: float = 0.5,
    ) -> SpatialSplashResult:
        if radius <= 0:
            raise ValueError("radius must be > 0")
        if not (0.0 <= falloff <= 1.0):
            raise ValueError("falloff must be 0.0–1.0")
        if base_damage < 0:
            raise ValueError("base_damage must be >= 0")

        hits: list[dict] = []

        for target, pos in targets_with_positions:
            if not target.is_alive:
                continue
            dist = impact_point.distance_to(pos)
            if dist > radius:
                continue
            factor = max(0.0, 1.0 - falloff * (dist / radius))
            dmg = base_damage * factor
            if dmg <= 0:
                continue
            pre_hp = target.current_health
            actual = target.apply_damage(dmg)
            overkill = max(0.0, dmg - pre_hp)
            hits.append({
                "target_id":    target.target_id,
                "distance":     round(dist, 6),
                "damage_dealt": round(actual, 6),
                "overkill":     round(overkill, 6),
                "killed":       not target.is_alive,
            })

        total = sum(h["damage_dealt"] for h in hits)
        return SpatialSplashResult(
            impact_point=impact_point,
            radius=radius,
            hits=hits,
            targets_hit=len(hits),
            total_damage=total,
        )
