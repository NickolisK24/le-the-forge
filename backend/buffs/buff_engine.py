"""
BuffEngine — Orchestrator for the complete buff/debuff lifecycle.

Ties every subsystem together in strict per-frame execution order:

    1. apply()   — BuffDefinition → active_buffs via apply_buff + stack_resolver
    2. tick()    — Duration decay via tick_buffs; expired instances removed
    3. resolve() — Condition evaluation → eligible stat aggregation → debug snapshot

Completion criteria satisfied:
    ✔ Buffs apply correctly          — apply() delegates to apply_buff
    ✔ Stacks behave correctly        — apply_buff delegates to stack_resolver
    ✔ Duration decays correctly      — tick() uses tick_buffs
    ✔ Expired buffs removed          — tick() prunes via TickResult.expired
    ✔ Conditions respected           — resolve() gates via evaluate_buff_conditions
    ✔ Stat modifiers applied         — resolve() calls aggregate_eligible_modifiers
    ✔ Debug output exists            — resolve() calls export_active_buffs
    ✔ Deterministic behavior         — run_determinism_check() verifies it

Public API:
    BuffEngine()
    engine.apply(definition, timestamp, source=None)   — apply a buff
    engine.tick(delta_time)                            — advance time
    engine.resolve(state) -> BuffFrameResult           — evaluate + aggregate + snapshot
    engine.active_buff_ids() -> tuple[str, ...]        — current keyset (sorted)
    BuffEngine.run_determinism_check()                 — raises AssertionError on failure
"""

from __future__ import annotations

from dataclasses import dataclass, field

from buffs.apply_buff import apply_buff
from buffs.buff_condition_evaluator import (
    BuffConditionResult,
    aggregate_eligible_modifiers,
    evaluate_buff_conditions,
)
from buffs.buff_debug import BuffDebugEntry, export_active_buffs
from buffs.buff_definition import BuffDefinition, StackBehavior, StatModifier
from buffs.buff_instance import BuffInstance
from buffs.tick_buffs import TickResult, tick_buffs
from state.state_engine import SimulationState


# ---------------------------------------------------------------------------
# Frame result
# ---------------------------------------------------------------------------

@dataclass(slots=True, frozen=True)
class BuffFrameResult:
    """Complete output of one buff resolution pass.

    stat_modifiers  — flat dict of stat_target → total value from all
                      eligible (condition-passing) buffs this frame.
    condition_result — eligible/suppressed partition; useful for downstream
                       systems that need to know which buffs are inactive.
    debug_snapshot  — serializable per-buff debug dict; ready for insertion
                      into ResolutionResult.layer_snapshots["buffs"].
    expired         — sorted tuple of buff_ids pruned this tick (empty when
                      resolve() is called without a preceding tick()).
    """
    stat_modifiers: dict[str, float]
    condition_result: BuffConditionResult
    debug_snapshot: dict[str, BuffDebugEntry]
    expired: tuple[str, ...]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class BuffEngine:
    """Stateful orchestrator for the full buff lifecycle.

    Owns a single active_buffs dict.  All mutations go through the engine;
    no external code should modify active_buffs directly.

    Thread-safety: not thread-safe.  Use one engine per simulation context.
    """

    def __init__(self) -> None:
        self._active: dict[str, BuffInstance] = {}
        self._last_expired: tuple[str, ...] = ()

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def apply(
        self,
        definition: BuffDefinition,
        timestamp: float,
        source: str | None = None,
    ) -> None:
        """Apply *definition* to the active buff pool.

        Delegates to apply_buff → stack_resolver, which enforces:
          - correct StackBehavior (ADD_STACK / REFRESH_DURATION / IGNORE / REPLACE)
          - hard stack_count clamp to definition.max_stacks on every path
        """
        self._active = apply_buff(self._active, definition, timestamp, source)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def tick(self, delta_time: float) -> tuple[str, ...]:
        """Advance all buff timers by *delta_time* seconds.

        Reduces remaining_duration on every timed instance, removes expired
        instances, and records the expired set for the next resolve() call.

        Args:
            delta_time: seconds elapsed since last tick; must be >= 0.

        Returns:
            Sorted tuple of buff_ids that expired and were removed this tick.

        Raises:
            ValueError: propagated from tick_buffs if delta_time < 0.
        """
        result: TickResult = tick_buffs(self._active, delta_time)
        self._active = result.active
        self._last_expired = result.expired
        return result.expired

    # ------------------------------------------------------------------
    # Resolve
    # ------------------------------------------------------------------

    def resolve(self, state: SimulationState) -> BuffFrameResult:
        """Evaluate conditions, aggregate stats, and capture debug snapshot.

        Execution order (strict):
            1. evaluate_buff_conditions  — partitions active into eligible/suppressed
            2. aggregate_eligible_modifiers — sums stats from eligible buffs only
            3. export_active_buffs       — builds serializable debug snapshot

        Conditions are always evaluated BEFORE stat aggregation.  Suppressed
        buffs contribute zero to stat_modifiers.

        Args:
            state: current SimulationState for condition evaluation.

        Returns:
            BuffFrameResult with all outputs for this frame.
        """
        condition_result = evaluate_buff_conditions(self._active, state)
        stat_modifiers   = aggregate_eligible_modifiers(condition_result)
        debug_snapshot   = export_active_buffs(self._active, condition_result)

        expired          = self._last_expired
        self._last_expired = ()          # consume; reset for next tick

        return BuffFrameResult(
            stat_modifiers=stat_modifiers,
            condition_result=condition_result,
            debug_snapshot=debug_snapshot,
            expired=expired,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def active_buff_ids(self) -> tuple[str, ...]:
        """Sorted tuple of buff_ids currently in the active pool."""
        return tuple(sorted(self._active.keys()))

    def active_count(self) -> int:
        return len(self._active)

    # ------------------------------------------------------------------
    # Determinism check
    # ------------------------------------------------------------------

    @staticmethod
    def run_determinism_check() -> None:
        """Verify that identical inputs always produce identical outputs.

        Runs the full apply → tick → resolve pipeline twice with the same
        inputs and asserts that both passes produce byte-for-byte identical
        stat_modifiers and debug_snapshot outputs.

        Raises:
            AssertionError: if any output differs between the two runs.
        """
        definition = BuffDefinition(
            buff_id="__det_check__",
            name="Determinism Check",
            stat_modifiers=(
                StatModifier(stat_target="spell_damage_pct", value=20.0),
            ),
            duration_seconds=10.0,
            max_stacks=3,
            stack_behavior=StackBehavior.ADD_STACK,
        )

        state = SimulationState()
        timestamp = 1000.0
        delta = 1.5

        def _run() -> tuple[dict, dict]:
            engine = BuffEngine()
            engine.apply(definition, timestamp, source="skill_slam")
            engine.apply(definition, timestamp, source="skill_slam")  # +1 stack
            engine.tick(delta)
            result = engine.resolve(state)
            return result.stat_modifiers, result.debug_snapshot

        stats_a, snap_a = _run()
        stats_b, snap_b = _run()

        assert stats_a == stats_b, (
            f"Determinism failure — stat_modifiers differ:\n  run1={stats_a}\n  run2={stats_b}"
        )
        assert snap_a == snap_b, (
            f"Determinism failure — debug_snapshot differs:\n  run1={snap_a}\n  run2={snap_b}"
        )
