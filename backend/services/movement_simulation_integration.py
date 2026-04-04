"""
L17 — Movement Simulation Integration

Top-level service that wires together the full movement simulation pipeline:
  1. Build MovementState per entity from a TargetManager
  2. Assign behaviors per entity
  3. Run the MovementTimelineSynchronizer
  4. Evaluate kiting for the player each tick
  5. Track distances and fire range events
  6. Collect metrics and log events

Single entry point for external callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from spatial.models.vector2 import Vector2
from movement.models.movement_state import MovementState
from movement.behaviors.base_behavior import BaseBehavior
from movement.behaviors.aggressive_behavior import AggressiveBehavior
from movement.timeline.movement_sync import MovementTimelineSynchronizer, MovementRecord
from movement.distance.distance_tracker import DistanceTracker, DistanceEvent
from movement.kiting.kiting_engine import KitingEngine, KiteResult
from metrics.movement_metrics import MovementMetrics
from debug.movement_logger import MovementLogger
from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager


@dataclass(frozen=True)
class EntityConfig:
    """Configuration for one entity in the simulation."""

    entity_id:     str
    start_pos:     Vector2
    max_speed:     float          = 5.0
    behavior:      BaseBehavior | None = None   # None → AggressiveBehavior()
    target_pos:    Vector2 | None = None
    track_with:    list[str]      = field(default_factory=list)  # entity_ids to track distance to
    range_threshold: float | None = None


@dataclass
class MovementSimulationResult:
    """Complete result of a movement simulation run."""

    tick_records:      list[MovementRecord]
    final_states:      list[dict]
    distance_events:   list[DistanceEvent]
    kite_results:      list[dict]
    metrics_summary:   dict
    log_entries:       list[dict]
    ticks_executed:    int
    duration:          float


class MovementSimulationIntegration:
    """
    Orchestrates a full movement simulation run.

    Usage:
        sim = MovementSimulationIntegration(tick_size=0.05)
        result = sim.run_simulation(
            entity_configs=[...],
            player_start=Vector2(0, 0),
            duration=10.0,
        )
    """

    def __init__(
        self,
        tick_size:        float = 0.05,
        avoidance_radius: float = 0.0,
        kite_min_range:   float = 5.0,
        kite_max_range:   float = 15.0,
        kite_speed:       float = 7.0,
        log_capacity:     int   = 500,
    ) -> None:
        self.tick_size        = tick_size
        self.avoidance_radius = avoidance_radius
        self.kite_engine      = KitingEngine(kite_min_range, kite_max_range, kite_speed)
        self.log_capacity     = log_capacity

    def run_simulation(
        self,
        entity_configs:  list[EntityConfig],
        player_start:    Vector2,
        duration:        float,
        player_max_speed: float = 7.0,
    ) -> MovementSimulationResult:
        """
        Run the simulation for *duration* seconds.
        The player is tracked separately from enemy entities.
        """
        # --- Build states and behaviors ---
        states: dict[str, MovementState] = {}
        behaviors: dict[str, BaseBehavior] = {}
        contexts: dict[str, dict] = {}

        for cfg in entity_configs:
            state = MovementState(
                entity_id=cfg.entity_id,
                position=cfg.start_pos,
                max_speed=cfg.max_speed,
                target_position=cfg.target_pos,
            )
            states[cfg.entity_id] = state
            behaviors[cfg.entity_id] = cfg.behavior or AggressiveBehavior()
            contexts[cfg.entity_id] = {"player_position": player_start}

        # --- Distance tracker setup ---
        tracker = DistanceTracker()
        for cfg in entity_configs:
            for other_id in cfg.track_with:
                tracker.track_pair(cfg.entity_id, other_id, cfg.range_threshold)
            # Always track distance to player
            tracker.track_pair(cfg.entity_id, "player", cfg.range_threshold)

        # --- Metrics and logger ---
        metrics = MovementMetrics()
        logger = MovementLogger(capacity=self.log_capacity)
        metrics.record_total_time(duration)

        # --- Run sync ---
        sync = MovementTimelineSynchronizer(
            tick_size=self.tick_size,
            record_snapshots=True,
            avoidance_radius=self.avoidance_radius,
        )

        # Update contexts each tick with player position
        import math
        n_ticks = math.ceil(duration / self.tick_size)
        all_records: list[MovementRecord] = []
        all_dist_events: list[DistanceEvent] = []
        kite_log: list[dict] = []
        player_pos = player_start
        elapsed = 0.0

        for i in range(n_ticks):
            step = min(self.tick_size, duration - i * self.tick_size)
            if step <= 0:
                break
            elapsed += step

            # Update player_position in each entity context
            for eid in states:
                contexts[eid]["player_position"] = player_pos

            # Run one tick of movement sync
            tick_records = sync.run(states, behaviors, contexts, duration=step)
            all_records.extend(tick_records)

            # Kiting: player repositions based on enemy positions
            enemy_positions = [s.position for s in states.values()]
            new_player_pos, kite_result = self.kite_engine.update_player_position(
                player_pos, enemy_positions, step
            )
            player_pos = new_player_pos
            if kite_result.is_kiting:
                metrics.record_kite_event(elapsed)
                logger.log_kite_event(player_pos, kite_result.closest_enemy_dist, elapsed)
            kite_log.append({
                "time":    round(elapsed, 6),
                "action":  kite_result.kite_action,
                "closest": round(kite_result.closest_enemy_dist, 4),
            })

            # Distance tracking
            all_positions = {eid: s.position for eid, s in states.items()}
            all_positions["player"] = player_pos
            dist_events = tracker.update(all_positions, now=elapsed)
            all_dist_events.extend(dist_events)
            for ev in dist_events:
                logger.log_range_event(ev.event_type, ev.entity_a, ev.entity_b, ev.distance, elapsed)

            # Record movement distances
            for rec in tick_records:
                metrics.record_movement(rec.entity_id, rec.distance_tick)

        return MovementSimulationResult(
            tick_records=all_records,
            final_states=[s.to_dict() for s in states.values()],
            distance_events=all_dist_events,
            kite_results=kite_log,
            metrics_summary=metrics.summary(),
            log_entries=logger.entries(),
            ticks_executed=n_ticks,
            duration=duration,
        )
