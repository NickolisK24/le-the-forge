"""
H4 — State Tracking Engine

SimulationState is the single source of truth for all runtime variables
during a conditional simulation tick. It is passed to the ConditionEvaluator,
ConditionalModifierEngine, StatusManager, and HealthThresholds.

All health values are stored as absolute HP; the *_pct properties normalise
them to 0.0–1.0 for condition evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimulationState:
    """
    Mutable runtime state for one simulation run.

    player_health / player_max_health   — current / max player HP
    target_health / target_max_health   — current / max target HP
    active_buffs                        — set of buff_ids currently applied
    active_status_effects               — dict of status_id → stack_count
    elapsed_time                        — simulation clock in seconds
    """
    player_health:     float = 1.0
    player_max_health: float = 1.0
    target_health:     float = 1.0
    target_max_health: float = 1.0
    elapsed_time:      float = 0.0

    active_buffs:           set[str]        = field(default_factory=set)
    active_status_effects:  dict[str, int]  = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.player_max_health <= 0:
            raise ValueError("player_max_health must be > 0")
        if self.target_max_health <= 0:
            raise ValueError("target_max_health must be > 0")
        if self.player_health < 0:
            raise ValueError("player_health must be >= 0")
        if self.target_health < 0:
            raise ValueError("target_health must be >= 0")
        if self.elapsed_time < 0:
            raise ValueError("elapsed_time must be >= 0")

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def player_health_pct(self) -> float:
        """Player HP as a fraction 0.0–1.0."""
        return self.player_health / self.player_max_health

    @property
    def target_health_pct(self) -> float:
        """Target HP as a fraction 0.0–1.0."""
        return self.target_health / self.target_max_health

    @property
    def player_is_alive(self) -> bool:
        return self.player_health > 0

    @property
    def target_is_alive(self) -> bool:
        return self.target_health > 0

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def advance_time(self, delta: float) -> None:
        """Increment elapsed_time by *delta* seconds (delta must be > 0)."""
        if delta <= 0:
            raise ValueError("delta must be > 0")
        self.elapsed_time += delta

    def apply_damage_to_player(self, amount: float) -> None:
        """Reduce player_health by *amount*, floored at 0."""
        self.player_health = max(0.0, self.player_health - amount)

    def apply_damage_to_target(self, amount: float) -> None:
        """Reduce target_health by *amount*, floored at 0."""
        self.target_health = max(0.0, self.target_health - amount)

    def heal_player(self, amount: float) -> None:
        """Restore player_health by *amount*, capped at player_max_health."""
        self.player_health = min(self.player_max_health, self.player_health + amount)

    def add_buff(self, buff_id: str) -> None:
        self.active_buffs.add(buff_id)

    def remove_buff(self, buff_id: str) -> None:
        self.active_buffs.discard(buff_id)

    def apply_status(self, status_id: str, stacks: int = 1) -> int:
        """
        Add *stacks* of a status. Returns new stack count.
        Does not enforce a cap — StatusManager owns cap logic.
        """
        current = self.active_status_effects.get(status_id, 0)
        self.active_status_effects[status_id] = current + stacks
        return self.active_status_effects[status_id]

    def remove_status(self, status_id: str) -> None:
        self.active_status_effects.pop(status_id, None)

    def snapshot(self) -> dict:
        """Return an immutable snapshot dict for logging / debugging."""
        return {
            "player_health":     self.player_health,
            "player_max_health": self.player_max_health,
            "player_health_pct": round(self.player_health_pct, 4),
            "target_health":     self.target_health,
            "target_max_health": self.target_max_health,
            "target_health_pct": round(self.target_health_pct, 4),
            "elapsed_time":      self.elapsed_time,
            "active_buffs":      sorted(self.active_buffs),
            "active_status_effects": dict(self.active_status_effects),
        }
