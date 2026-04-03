"""
I8 — Splash Damage Engine

Applies splash (radial) damage around a primary target. Targets within
*radius* positions of the primary receive *falloff*-reduced damage.

position_index is used as a 1-D distance proxy:
    distance = abs(target.position_index - primary.position_index)
    hits when distance <= radius
    damage = base_damage * max(0, 1 - falloff * distance / radius)
"""

from __future__ import annotations

from dataclasses import dataclass

from targets.models.target_entity import TargetEntity
from damage.multi_target_distribution import DamageEvent, MultiTargetDistribution


@dataclass(frozen=True)
class SplashResult:
    events: list[DamageEvent]
    targets_hit: int


class SplashEngine:
    """
    execute(base_damage, targets, primary, radius, falloff)
        → SplashResult

    base_damage  — full damage at distance 0 (primary hit)
    targets      — full alive pool
    primary      — the impact epicentre
    radius       — max position_index distance for splash (default 2)
    falloff      — damage reduction fraction per unit distance (default 0.5)
                   damage at distance d = base * max(0, 1 - falloff*(d/radius))
    """

    def execute(
        self,
        base_damage: float,
        targets: list[TargetEntity],
        primary: TargetEntity,
        radius: int = 2,
        falloff: float = 0.5,
    ) -> SplashResult:
        if radius < 0:
            raise ValueError("radius must be >= 0")
        if not (0.0 <= falloff <= 1.0):
            raise ValueError("falloff must be 0.0–1.0")

        _dist = MultiTargetDistribution()
        events: list[DamageEvent] = []
        alive = [t for t in targets if t.is_alive]

        for t in alive:
            distance = abs(t.position_index - primary.position_index)
            if distance > radius:
                continue
            dmg_factor = max(0.0, 1.0 - falloff * (distance / radius if radius > 0 else 0.0))
            hit_damage = base_damage * dmg_factor
            if hit_damage > 0:
                events.append(_dist._hit(t, hit_damage))

        return SplashResult(events=events, targets_hit=len(events))
