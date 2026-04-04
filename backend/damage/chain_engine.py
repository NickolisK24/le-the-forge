"""
I7 — Chain Damage Engine

Executes chain-hit logic: damage bounces from target to target,
reducing by a multiplier each hop, stopping when the bounce limit
is reached or no alive targets remain.

Chain starts at a designated primary target; subsequent targets are
chosen by lowest position_index among alive targets not yet hit this chain.
"""

from __future__ import annotations

from dataclasses import dataclass

from targets.models.target_entity import TargetEntity
from damage.multi_target_distribution import DamageEvent, MultiTargetDistribution


@dataclass(frozen=True)
class ChainResult:
    events:        list[DamageEvent]
    bounces:       int       # number of hops actually executed
    final_damage:  float     # damage value on the last hit


class ChainEngine:
    """
    execute(base_damage, targets, primary, max_bounces, decay)
        → ChainResult

    base_damage  — damage on the first hit
    targets      — full alive pool (primary must be in the list)
    primary      — first target in the chain
    max_bounces  — maximum number of additional hops after primary hit (default 2)
    decay        — damage multiplier per bounce (0.0–1.0, default 0.7)
    """

    def execute(
        self,
        base_damage: float,
        targets: list[TargetEntity],
        primary: TargetEntity,
        max_bounces: int = 2,
        decay: float = 0.7,
    ) -> ChainResult:
        if max_bounces < 0:
            raise ValueError("max_bounces must be >= 0")
        if not (0.0 < decay <= 1.0):
            raise ValueError("decay must be in (0, 1]")

        _dist = MultiTargetDistribution()
        events: list[DamageEvent] = []
        hit_ids: set[str] = set()

        # First hit
        current_damage = base_damage
        evt = _dist._hit(primary, current_damage)
        events.append(evt)
        hit_ids.add(primary.target_id)

        # Bounce loop
        bounces = 0
        while bounces < max_bounces:
            # Next candidate: alive target not yet hit, lowest position_index
            candidates = [
                t for t in targets
                if t.is_alive and t.target_id not in hit_ids
            ]
            if not candidates:
                break
            next_target = min(candidates, key=lambda t: t.position_index)
            current_damage *= decay
            evt = _dist._hit(next_target, current_damage)
            events.append(evt)
            hit_ids.add(next_target.target_id)
            bounces += 1

        return ChainResult(
            events=events,
            bounces=bounces,
            final_damage=current_damage,
        )
