"""
I4 — Multi-Target State Integration

MultiTargetState wraps a TargetManager and provides a SimulationState-
compatible view of the overall encounter, forwarding per-target
health/status queries to the correct TargetEntity.

For backwards-compatibility with Phase H condition evaluation, the
*active target* (default: target at index 0) is used when building
a SimulationState snapshot for the ConditionEvaluator.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from targets.target_manager import TargetManager
from targets.models.target_entity import TargetEntity
from state.state_engine import SimulationState


@dataclass
class MultiTargetState:
    """
    Encounter-level state container for multi-target simulations.

    manager            — owns the TargetEntity collection
    player_health      — player's current HP
    player_max_health  — player's max HP
    elapsed_time       — simulation clock in seconds
    active_buffs       — player-side active buffs
    """
    manager:           TargetManager
    player_health:     float = 1.0
    player_max_health: float = 1.0
    elapsed_time:      float = 0.0
    active_buffs:      set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.player_max_health <= 0:
            raise ValueError("player_max_health must be > 0")
        if self.player_health < 0:
            raise ValueError("player_health must be >= 0")

    # ------------------------------------------------------------------
    # Time
    # ------------------------------------------------------------------

    def advance_time(self, delta: float) -> None:
        if delta <= 0:
            raise ValueError("delta must be > 0")
        self.elapsed_time += delta

    # ------------------------------------------------------------------
    # Per-target access
    # ------------------------------------------------------------------

    def apply_damage(self, target_id: str, amount: float) -> float:
        """Deal *amount* to target. Returns actual damage dealt."""
        return self.manager.get(target_id).apply_damage(amount)

    def target_health_pct(self, target_id: str) -> float:
        return self.manager.get(target_id).health_pct

    def is_target_alive(self, target_id: str) -> bool:
        return self.manager.get(target_id).is_alive

    def alive_targets(self) -> list[TargetEntity]:
        return self.manager.alive_targets()

    def alive_count(self) -> int:
        return self.manager.alive_count

    def is_cleared(self) -> bool:
        return self.manager.is_cleared()

    # ------------------------------------------------------------------
    # SimulationState bridge (for Phase H condition evaluators)
    # ------------------------------------------------------------------

    def as_simulation_state(self, target_id: str | None = None) -> SimulationState:
        """
        Return a SimulationState snapshot scoped to one target.
        If *target_id* is None, uses the first alive target.
        """
        alive = self.manager.alive_targets()
        if target_id is not None:
            target = self.manager.get(target_id)
        elif alive:
            target = alive[0]
        else:
            # All dead — return zeroed state
            return SimulationState(
                player_health=self.player_health,
                player_max_health=self.player_max_health,
                target_health=0.0,
                target_max_health=1.0,
                elapsed_time=self.elapsed_time,
                active_buffs=set(self.active_buffs),
            )
        return SimulationState(
            player_health=self.player_health,
            player_max_health=self.player_max_health,
            target_health=target.current_health,
            target_max_health=target.max_health,
            elapsed_time=self.elapsed_time,
            active_buffs=set(self.active_buffs),
            active_status_effects={
                sid: 1 for sid in target.status_list
            },
        )

    def snapshot(self) -> dict:
        return {
            "elapsed_time":    self.elapsed_time,
            "player_health":   self.player_health,
            "alive_count":     self.alive_count(),
            "targets":         [t.to_dict() for t in self.manager.all_targets()],
        }
