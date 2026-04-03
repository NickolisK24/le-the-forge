"""
I12 — Multi-Target Encounter Engine

Orchestrates a full multi-target encounter: routes damage events,
processes kills, and runs until all targets are dead or time expires.

Damage is applied each tick to targets selected by the TargetSelector.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from state.multi_target_state import MultiTargetState
from targets.target_selector import TargetSelector
from targets.lifecycle_manager import LifecycleManager, KillRecord
from damage.multi_target_distribution import MultiTargetDistribution
from events.event_trigger import TriggerRegistry
from metrics.multi_target_metrics import MultiTargetMetrics


@dataclass
class MultiTargetEncounterResult:
    time_to_clear:   float | None      # None if not all targets died
    total_kills:     int
    damage_events:   list[dict]        # lightweight log
    metrics:         dict
    cleared:         bool


class MultiTargetEncounterEngine:
    """
    run(state, base_damage, distribution, selection_mode,
        tick_size, max_duration, registry)
        → MultiTargetEncounterResult

    Applies *base_damage* per tick to targets selected by *selection_mode*
    and distributed via *distribution*. Runs until cleared or timeout.
    """

    def run(
        self,
        state: MultiTargetState,
        base_damage: float,
        distribution: str = "full_aoe",
        selection_mode: str = "all_targets",
        tick_size: float = 0.1,
        max_duration: float = 60.0,
        registry: TriggerRegistry | None = None,
    ) -> MultiTargetEncounterResult:

        _registry  = registry or TriggerRegistry()
        _selector  = TargetSelector()
        _dist      = MultiTargetDistribution()
        _lifecycle = LifecycleManager()
        _metrics   = MultiTargetMetrics()

        elapsed = 0.0
        damage_log: list[dict] = []

        while elapsed < max_duration and not state.is_cleared():
            step = min(tick_size, max_duration - elapsed)
            state.advance_time(step)
            elapsed += step
            now = state.elapsed_time

            alive = state.alive_targets()
            if not alive:
                break

            # Select primary target (for modes needing one)
            try:
                selected = _selector.select(selection_mode, alive)
                primary = selected[0]
            except ValueError:
                break

            # Distribute damage
            events = _dist.distribute(
                damage=base_damage * step,
                distribution=distribution,
                primary=primary,
                all_targets=alive,
            )
            for evt in events:
                _metrics.record_hit(evt.target_id, evt.damage_dealt, evt.overkill)
                if evt.killed:
                    _metrics.record_kill(evt.target_id, now)
                damage_log.append({
                    "time":       round(now, 4),
                    "target_id":  evt.target_id,
                    "damage":     round(evt.damage_dealt, 2),
                    "overkill":   round(evt.overkill, 2),
                    "killed":     evt.killed,
                })

            # Process deaths
            _lifecycle.process(state.manager, _registry, now)

        cleared      = state.is_cleared()
        time_to_clear = elapsed if cleared else None

        return MultiTargetEncounterResult(
            time_to_clear=time_to_clear,
            total_kills=_lifecycle.total_kills(),
            damage_events=damage_log,
            metrics=_metrics.summary(),
            cleared=cleared,
        )
