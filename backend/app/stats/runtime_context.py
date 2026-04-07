"""
RuntimeContext — build-planning context for conditional stat evaluation.

Translates high-level build-planning state (is_moving, has_ward,
enemy_frozen, against_boss) into a SimulationState that the existing
ConditionEvaluator and ConditionalModifierEngine can consume.

This bridges the gap between:
  - Build planning (static "what if" scenarios)
  - Combat simulation (tick-by-tick state tracking)

The context is passed to Layer 8 of the stat resolution pipeline so
conditional modifiers can activate based on assumed runtime conditions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from state.state_engine import SimulationState
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


@dataclass(frozen=True)
class RuntimeContext:
    """Immutable snapshot of assumed runtime conditions for build planning.

    Each boolean flag maps to a buff or status in SimulationState so the
    existing ConditionEvaluator can evaluate them.

    Usage::

        ctx = RuntimeContext(is_moving=True, has_ward=True)
        sim_state = ctx.to_simulation_state(max_health=2000)
    """

    # Movement state
    is_moving: bool = False
    is_channeling: bool = False

    # Player state
    has_ward: bool = False
    player_health_pct: float = 1.0   # 0.0–1.0 fraction

    # Enemy state
    enemy_frozen: bool = False
    enemy_stunned: bool = False
    enemy_health_pct: float = 1.0    # 0.0–1.0 fraction

    # Environment state
    against_boss: bool = False
    elapsed_time: float = 0.0

    # Extra buff/status IDs the user wants to assume are active
    assumed_buffs: tuple[str, ...] = ()
    assumed_statuses: tuple[str, ...] = ()

    def to_simulation_state(self, max_health: float = 1000.0) -> SimulationState:
        """Convert to a SimulationState for the ConditionEvaluator.

        Boolean flags are encoded as buff_ids or status_ids so that
        Condition objects with condition_type="buff_active" or
        "status_present" can match them.

        Naming convention for synthetic buff/status IDs:
          - ``"is_moving"`` → buff_active
          - ``"is_channeling"`` → buff_active
          - ``"has_ward"`` → buff_active
          - ``"against_boss"`` → buff_active
          - ``"frozen"`` → status_present (on target)
          - ``"stunned"`` → status_present (on target)
        """
        buffs: set[str] = set(self.assumed_buffs)
        statuses: dict[str, int] = {s: 1 for s in self.assumed_statuses}

        if self.is_moving:
            buffs.add("is_moving")
        if self.is_channeling:
            buffs.add("is_channeling")
        if self.has_ward:
            buffs.add("has_ward")
        if self.against_boss:
            buffs.add("against_boss")

        if self.enemy_frozen:
            statuses["frozen"] = 1
        if self.enemy_stunned:
            statuses["stunned"] = 1

        return SimulationState(
            player_health=max_health * self.player_health_pct,
            player_max_health=max_health,
            target_health=max_health * self.enemy_health_pct,
            target_max_health=max_health,
            elapsed_time=self.elapsed_time,
            active_buffs=buffs,
            active_status_effects=statuses,
        )

    def to_dict(self) -> dict:
        return {
            "is_moving": self.is_moving,
            "is_channeling": self.is_channeling,
            "has_ward": self.has_ward,
            "player_health_pct": self.player_health_pct,
            "enemy_frozen": self.enemy_frozen,
            "enemy_stunned": self.enemy_stunned,
            "enemy_health_pct": self.enemy_health_pct,
            "against_boss": self.against_boss,
            "elapsed_time": self.elapsed_time,
            "assumed_buffs": list(self.assumed_buffs),
            "assumed_statuses": list(self.assumed_statuses),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RuntimeContext":
        return cls(
            is_moving=d.get("is_moving", False),
            is_channeling=d.get("is_channeling", False),
            has_ward=d.get("has_ward", False),
            player_health_pct=d.get("player_health_pct", 1.0),
            enemy_frozen=d.get("enemy_frozen", False),
            enemy_stunned=d.get("enemy_stunned", False),
            enemy_health_pct=d.get("enemy_health_pct", 1.0),
            against_boss=d.get("against_boss", False),
            elapsed_time=d.get("elapsed_time", 0.0),
            assumed_buffs=tuple(d.get("assumed_buffs", ())),
            assumed_statuses=tuple(d.get("assumed_statuses", ())),
        )


# Default context — no conditions active (all bonuses inactive)
DEFAULT_CONTEXT = RuntimeContext()
