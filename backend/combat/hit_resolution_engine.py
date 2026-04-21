"""
K7 — Hit Resolution Engine

Translates a confirmed collision into concrete damage events. Handles:
  - Critical hit evaluation
  - Damage application to TargetEntity
  - AoE shape resolution with falloff
  - Result collection for metrics / logging
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from spatial.aoe.aoe_shapes import AoeShape
from targets.models.target_entity import TargetEntity


@dataclass(frozen=True)
class HitResult:
    """Result of resolving one projectile or AoE hit against one target."""

    target_id:    str
    damage_dealt: float
    raw_damage:   float       # before overkill cap
    overkill:     float       # excess damage beyond remaining HP
    is_critical:  bool
    killed:       bool
    position:     Vector2     # target position at time of hit


@dataclass(frozen=True)
class AoeHitResult:
    """Aggregated result of resolving an AoE shape against a target pool."""

    hits:         list[HitResult]
    targets_hit:  int
    total_damage: float
    shape_dict:   dict


class HitResolutionEngine:
    """
    Resolves collision notifications into damage events.

    resolve_projectile_hit(projectile_damage, target, position, crit_chance, crit_multiplier)
        → HitResult

    resolve_aoe(shape, targets_with_positions, base_damage, falloff, crit_chance, crit_multiplier)
        → AoeHitResult
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def resolve_projectile_hit(
        self,
        damage: float,
        target: TargetEntity,
        position: Vector2,
        crit_chance: float = 0.0,
        crit_multiplier: float = 2.0,  # verified: player base is 200%
    ) -> HitResult:
        """
        Apply *damage* to *target*, rolling for a crit.

        crit_chance      — 0.0–1.0 probability of a critical hit
        crit_multiplier  — damage multiplier on crit (>= 1.0)
        """
        if not (0.0 <= crit_chance <= 1.0):
            raise ValueError("crit_chance must be 0.0–1.0")
        if crit_multiplier < 1.0:
            raise ValueError("crit_multiplier must be >= 1.0")

        is_crit = self._rng.random() < crit_chance
        raw_damage = damage * crit_multiplier if is_crit else damage
        pre_hp = target.current_health
        actual = target.apply_damage(raw_damage)
        overkill = max(0.0, raw_damage - pre_hp)
        return HitResult(
            target_id=target.target_id,
            damage_dealt=actual,
            raw_damage=raw_damage,
            overkill=overkill,
            is_critical=is_crit,
            killed=not target.is_alive,
            position=position,
        )

    def resolve_aoe(
        self,
        shape: AoeShape,
        targets_with_positions: list[tuple[TargetEntity, Vector2]],
        base_damage: float,
        falloff: float = 0.0,
        crit_chance: float = 0.0,
        crit_multiplier: float = 2.0,  # verified: player base is 200%
    ) -> AoeHitResult:
        """
        Apply *base_damage* to all alive targets whose position is inside *shape*.

        falloff — damage reduction per unit distance from shape centre (0 = flat).
                  Only applies to CircleShape (distance to center); other shapes
                  use flat damage.
        """
        if base_damage < 0:
            raise ValueError("base_damage must be >= 0")
        if falloff < 0:
            raise ValueError("falloff must be >= 0")

        hits: list[HitResult] = []
        # Determine center for falloff calculation
        center = getattr(shape, "center", getattr(shape, "origin", None))

        for target, pos in targets_with_positions:
            if not target.is_alive:
                continue
            if not shape.contains(pos):
                continue

            # Compute falloff factor
            if falloff > 0 and center is not None:
                dist = pos.distance_to(center)
                factor = max(0.0, 1.0 - falloff * dist)
            else:
                factor = 1.0

            effective_damage = base_damage * factor
            if effective_damage <= 0:
                continue

            hit = self.resolve_projectile_hit(
                effective_damage, target, pos, crit_chance, crit_multiplier
            )
            hits.append(hit)

        total = sum(h.damage_dealt for h in hits)
        return AoeHitResult(
            hits=hits,
            targets_hit=len(hits),
            total_damage=total,
            shape_dict=shape.to_dict(),
        )
