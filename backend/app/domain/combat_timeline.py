"""
Combat Timeline Integration (Step 9).

CombatTimeline is the integration layer that ties together:
  - Tick-based ailment advancement (ailments.py + ailment_stacking.py)
  - Buff/debuff timeline management (timeline.py)
  - Status effect interactions (status_interactions.py)
  - Enemy behavior phases (enemy_behavior.py)

It advances a fight state tick-by-tick and accumulates damage.

Public API:
  CombatState     — mutable snapshot of all combat variables at a point in time
  CombatTimeline  — stateful manager; call advance() to step through time
  CombatResult    — final summary returned after simulation ends
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.ailments import AilmentInstance, AilmentType, apply_ailment, tick_ailments
from app.domain.ailment_stacking import apply_ailment_with_limit
from app.domain.timeline import BuffInstance, BuffType, TimelineEngine
from app.domain.status_interactions import apply_interaction_multiplier
from app.domain.enemy_behavior import EnemyBehaviorProfile, simulate_enemy_behavior


# ---------------------------------------------------------------------------
# State and result types
# ---------------------------------------------------------------------------

@dataclass
class CombatState:
    """
    Mutable snapshot of the fight at the current simulation time.

    elapsed          — seconds simulated so far
    active_ailments  — all current ailment stacks on the enemy
    buff_engine      — manages active buffs/debuffs
    total_damage     — accumulated damage across all ticks
    """
    elapsed:         float = 0.0
    active_ailments: list[AilmentInstance] = field(default_factory=list)
    buff_engine:     TimelineEngine = field(default_factory=TimelineEngine)
    total_damage:    float = 0.0


@dataclass(frozen=True)
class CombatResult:
    """
    Final summary after a full combat simulation.

    total_damage     — total damage dealt over the fight
    fight_duration   — total simulated seconds
    average_dps      — total_damage / fight_duration (0 if duration == 0)
    ticks_simulated  — number of discrete time steps processed
    damage_by_ailment — damage contributed per AilmentType
    """
    total_damage:      float
    fight_duration:    float
    average_dps:       float
    ticks_simulated:   int
    damage_by_ailment: dict[str, float]


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

class CombatTimeline:
    """
    Stateful tick-based combat simulator.

    Usage::

        timeline = CombatTimeline(tick_size=0.1)
        timeline.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=4.0)
        timeline.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 3.0))
        timeline.advance(10.0)
        result = timeline.get_result()

    The timeline respects:
      - Ailment stack limits (via apply_ailment_with_limit)
      - Buff/debuff expiry
      - Status effect interactions when computing tick damage
      - Enemy behavior uptime if a BehaviorProfile is provided
    """

    def __init__(
        self,
        tick_size: float = 0.1,
        behavior_profile: EnemyBehaviorProfile | None = None,
    ) -> None:
        if tick_size <= 0:
            raise ValueError(f"tick_size must be > 0, got {tick_size}")
        self._tick_size       = tick_size
        self._behavior        = behavior_profile
        self._state           = CombatState()
        self._ticks           = 0
        self._damage_by_type: dict[AilmentType, float] = {}

    # ------------------------------------------------------------------
    # Mutation: add ailments and buffs
    # ------------------------------------------------------------------

    def apply_ailment(
        self,
        ailment_type: AilmentType,
        damage_per_tick: float,
        duration: float,
    ) -> None:
        """Apply a new ailment stack (respects stack limits)."""
        self._state.active_ailments = apply_ailment_with_limit(
            self._state.active_ailments,
            ailment_type,
            damage_per_tick,
            duration,
        )

    def add_buff(self, buff: BuffInstance) -> None:
        """Add a buff or debuff to the timeline."""
        self._state.buff_engine.add_buff(buff)

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def advance(self, duration: float) -> None:
        """
        Advance the simulation by ``duration`` seconds in tick_size steps.

        Tick ordering: COMPUTE DAMAGE FIRST, then advance time (intentional).
        A buff or ailment that is still active at the START of a tick
        contributes its full damage for that tick, even if it expires
        partway through. This matches the Last Epoch feel: if a buff was
        active when the hit landed, you get the benefit. The alternative
        (advance-then-compute) would silently drop the last partial tick of
        every expiring buff, producing counterintuitive under-counting.

        Each tick:
          1. Compute damage from current ailment/buff state.
          2. Expire ailments whose duration reached zero.
          3. Expire buffs whose duration reached zero.
        """
        if duration < 0:
            raise ValueError(f"duration must be >= 0, got {duration}")

        # Determine attack uptime fraction for this advance window
        uptime = 1.0
        if self._behavior is not None:
            summary = simulate_enemy_behavior(self._behavior, duration)
            uptime = summary.attack_uptime

        elapsed = 0.0
        tick = self._tick_size

        while elapsed < duration:
            actual_tick = min(tick, duration - elapsed)

            # 1. Tick ailments — collect raw damage and remove expired
            remaining, _ = tick_ailments(self._state.active_ailments, actual_tick)

            # 2. Per-type damage with interactions
            tick_total = 0.0
            for inst in self._state.active_ailments:
                raw = inst.damage_per_tick * actual_tick
                # Apply interaction multiplier for this ailment type
                boosted = apply_interaction_multiplier(
                    raw, self._state.active_ailments, inst.ailment_type
                )
                # Apply DAMAGE_MULTIPLIER buff
                dmg_bonus = self._state.buff_engine.total_modifier(BuffType.DAMAGE_MULTIPLIER)
                boosted *= 1.0 + dmg_bonus / 100.0
                # Apply enemy behavior uptime
                boosted *= uptime
                tick_total += boosted
                self._damage_by_type[inst.ailment_type] = (
                    self._damage_by_type.get(inst.ailment_type, 0.0) + boosted
                )

            self._state.active_ailments = remaining
            self._state.total_damage   += tick_total

            # 4. Advance buffs
            self._state.buff_engine.tick(actual_tick)

            self._state.elapsed += actual_tick
            self._ticks         += 1
            elapsed             += actual_tick

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def get_result(self) -> CombatResult:
        """Return a CombatResult summarising the simulation so far."""
        duration = self._state.elapsed
        avg_dps = self._state.total_damage / duration if duration > 0 else 0.0
        return CombatResult(
            total_damage=self._state.total_damage,
            fight_duration=duration,
            average_dps=avg_dps,
            ticks_simulated=self._ticks,
            damage_by_ailment={
                t.value: v for t, v in self._damage_by_type.items()
            },
        )

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> CombatState:
        """Current mutable combat state."""
        return self._state

    @property
    def elapsed(self) -> float:
        return self._state.elapsed
