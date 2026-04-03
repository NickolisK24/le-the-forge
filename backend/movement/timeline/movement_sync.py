"""
L12 — Movement Timeline Synchronizer

Drives a group of entities forward in fixed-size ticks using their assigned
behaviors. Uses integer tick counting (same pattern as H12, I11, K12) to
eliminate float accumulation drift.

Each tick:
  1. Build contexts for each entity
  2. Call behavior.update(state, context, delta) per entity
  3. Optionally apply avoidance forces (additive velocity nudge)
  4. Record a snapshot
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior
from movement.collision.avoidance_engine import AvoidanceEngine
from spatial.models.vector2 import Vector2


@dataclass(frozen=True)
class MovementRecord:
    """Per-tick snapshot for one entity."""

    time:           float
    entity_id:      str
    position:       tuple[float, float]
    velocity:       tuple[float, float]
    speed:          float
    behavior_type:  str
    distance_tick:  float   # distance moved this tick


@dataclass
class MovementTimelineSynchronizer:
    """
    Runs a multi-entity movement simulation for *duration* seconds.

    tick_size        — seconds per tick (must be > 0)
    record_snapshots — if False, returns empty list (zero memory overhead)
    avoidance_radius — separation radius for avoidance engine (0 → disabled)
    """

    tick_size:        float = 0.05
    record_snapshots: bool  = True
    avoidance_radius: float = 0.0

    def __post_init__(self) -> None:
        if self.tick_size <= 0:
            raise ValueError("tick_size must be > 0")

    def run(
        self,
        states: dict[str, MovementState],
        behaviors: dict[str, BaseBehavior],
        contexts: dict[str, dict] | None = None,
        duration: float = 1.0,
    ) -> list[MovementRecord]:
        """
        Run the simulation for *duration* seconds.

        states    — {entity_id: MovementState}  (mutated in place)
        behaviors — {entity_id: BaseBehavior}    (one per state entry)
        contexts  — {entity_id: context dict}    (None → empty dicts)
        duration  — total simulation length in seconds (> 0)

        Returns list[MovementRecord] (one per entity per tick when record_snapshots=True).
        """
        if duration <= 0:
            raise ValueError("duration must be > 0")

        ctx = contexts or {}
        avoidance = AvoidanceEngine() if self.avoidance_radius > 0 else None

        n_ticks = math.ceil(duration / self.tick_size)
        records: list[MovementRecord] = []
        elapsed = 0.0

        for i in range(n_ticks):
            step = min(self.tick_size, duration - i * self.tick_size)
            if step <= 0:
                break
            elapsed += step

            # Build shared position map for avoidance
            if avoidance is not None:
                positions = {eid: s.position for eid, s in states.items()}
                av_result = avoidance.apply_separation_all(
                    positions, self.avoidance_radius, max_speed=5.0
                )
            else:
                av_result = None

            for entity_id, state in states.items():
                behavior = behaviors.get(entity_id)
                if behavior is None:
                    continue

                entity_ctx = dict(ctx.get(entity_id, {}))
                entity_ctx["elapsed_time"] = elapsed
                entity_ctx["delta"] = step

                # Behaviors update velocity + apply movement
                pre_pos = state.position
                behavior.update(state, entity_ctx, step)

                # Additive avoidance nudge (applied after behavior)
                if av_result is not None:
                    sep = av_result.forces.get(entity_id, Vector2.zero())
                    if sep.magnitude_sq() > 0:
                        nudge = sep * step
                        state.position = state.position + nudge

                dist_tick = state.position.distance_to(pre_pos)

                if self.record_snapshots:
                    records.append(MovementRecord(
                        time=round(elapsed, 9),
                        entity_id=entity_id,
                        position=state.position.to_tuple(),
                        velocity=state.velocity.to_tuple(),
                        speed=round(state.speed(), 4),
                        behavior_type=state.behavior_type,
                        distance_tick=round(dist_tick, 6),
                    ))

        return records
