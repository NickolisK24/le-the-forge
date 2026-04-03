"""
K10 — Chain Projectile Engine (Spatial)

Spatial chain logic: damage bounces between targets ordered by true 2D
Euclidean distance from the current hit position, rather than the 1-D
position_index used by the Phase I ChainEngine in damage/.

Each bounce reduces damage by a decay factor and jumps to the nearest
alive, un-hit target. Continues until max_bounces is reached or no
eligible candidates remain.
"""

from __future__ import annotations

from dataclasses import dataclass

from spatial.models.vector2 import Vector2
from targets.models.target_entity import TargetEntity


@dataclass(frozen=True)
class ChainBounce:
    """Record of one hop in the chain."""

    target_id:    str
    position:     Vector2
    damage_dealt: float
    hop_number:   int       # 0 = primary hit


@dataclass(frozen=True)
class SpatialChainResult:
    """Complete result of a spatial chain execution."""

    bounces:      list[ChainBounce]
    total_damage: float
    hops_executed: int       # includes primary hit


class SpatialChainEngine:
    """
    execute(base_damage, primary, primary_position, targets_with_positions,
            max_bounces, decay, max_chain_range)
        → SpatialChainResult

    base_damage             — damage on the primary (first) hit
    primary                 — first TargetEntity in the chain
    primary_position        — world-space position of the primary target
    targets_with_positions  — [(TargetEntity, Vector2)] full alive pool
    max_bounces             — maximum number of additional hops after primary (default 2)
    decay                   — damage multiplier per hop, in (0, 1] (default 0.7)
    max_chain_range         — maximum bounce distance in world-units (default: inf)
    """

    def execute(
        self,
        base_damage: float,
        primary: TargetEntity,
        primary_position: Vector2,
        targets_with_positions: list[tuple[TargetEntity, Vector2]],
        max_bounces: int = 2,
        decay: float = 0.7,
        max_chain_range: float = float("inf"),
    ) -> SpatialChainResult:
        if max_bounces < 0:
            raise ValueError("max_bounces must be >= 0")
        if not (0.0 < decay <= 1.0):
            raise ValueError("decay must be in (0, 1]")
        if max_chain_range <= 0:
            raise ValueError("max_chain_range must be > 0")

        bounces: list[ChainBounce] = []
        hit_ids: set[str] = {primary.target_id}
        current_damage = base_damage
        current_pos = primary_position

        # Primary hit
        pre_hp = primary.current_health
        actual = primary.apply_damage(current_damage)
        bounces.append(ChainBounce(
            target_id=primary.target_id,
            position=primary_position,
            damage_dealt=actual,
            hop_number=0,
        ))

        # Build position lookup
        pos_map: dict[str, tuple[TargetEntity, Vector2]] = {
            t.target_id: (t, pos)
            for t, pos in targets_with_positions
        }

        # Bounce loop
        hop = 1
        while hop <= max_bounces:
            # Find nearest alive, un-hit target within max_chain_range
            best_target: TargetEntity | None = None
            best_pos: Vector2 | None = None
            best_dist = float("inf")

            for tid, (t, pos) in pos_map.items():
                if tid in hit_ids or not t.is_alive:
                    continue
                dist = current_pos.distance_to(pos)
                if dist <= max_chain_range and dist < best_dist:
                    best_dist = dist
                    best_target = t
                    best_pos = pos

            if best_target is None:
                break

            current_damage *= decay
            pre_hp = best_target.current_health
            actual = best_target.apply_damage(current_damage)
            bounces.append(ChainBounce(
                target_id=best_target.target_id,
                position=best_pos,
                damage_dealt=actual,
                hop_number=hop,
            ))
            hit_ids.add(best_target.target_id)
            current_pos = best_pos
            hop += 1

        total = sum(b.damage_dealt for b in bounces)
        return SpatialChainResult(
            bounces=bounces,
            total_damage=total,
            hops_executed=len(bounces),
        )
