"""
Encounter State Machine (Step 104).

Coordinates all encounter subsystems into a unified tick-based runtime loop:
  - TargetManager   (who to hit)
  - SpawnController (enemy waves)
  - EncounterTimeline (scheduled events)
  - PhaseController (boss phases)
  - DowntimeTracker (forced pauses)
  - MultiTargetEngine (damage distribution)

  EncounterConfig   — all parameters for one encounter simulation
  EncounterState    — live mutable state during a run
  EncounterMachine  — runs the tick loop and returns EncounterRunResult
"""

from __future__ import annotations

from dataclasses import dataclass, field

from encounter.downtime import DowntimeTracker, DowntimeWindow
from encounter.enemy import EncounterEnemy
from encounter.multi_target import HitDistribution, MultiHitConfig, MultiTargetEngine
from encounter.phases import EncounterPhase, PhaseController
from encounter.spawn_controller import SpawnController, SpawnWave
from encounter.target_manager import TargetManager
from encounter.timeline import EncounterTimeline, EventType, TimelineEvent


@dataclass
class EncounterConfig:
    """All parameters for one encounter simulation."""
    enemies:         list[EncounterEnemy]
    fight_duration:  float            = 30.0
    tick_size:       float            = 0.1
    base_damage:     float            = 100.0
    hit_config:      MultiHitConfig   = field(default_factory=MultiHitConfig)
    phases:          list[EncounterPhase]  = field(default_factory=list)
    spawn_waves:     list[SpawnWave]       = field(default_factory=list)
    downtime_windows: list[DowntimeWindow] = field(default_factory=list)
    timeline_events: list[TimelineEvent]   = field(default_factory=list)
    stop_on_all_dead: bool = True


@dataclass
class EncounterRunResult:
    """Output of a completed encounter simulation."""
    total_damage:        float
    elapsed_time:        float
    ticks_simulated:     int
    all_enemies_dead:    bool
    enemies_killed:      int
    total_casts:         int
    downtime_ticks:      int
    active_phase_id:     str | None
    damage_per_tick:     list[float] = field(default_factory=list)


class EncounterMachine:
    """
    Tick-based encounter simulation engine.

    Integrates all Phase C subsystems into one runtime loop.
    """

    def __init__(self, config: EncounterConfig) -> None:
        self._cfg = config

    def run(self) -> EncounterRunResult:
        cfg  = self._cfg

        # Fresh copies of enemies for this run
        for e in cfg.enemies:
            e.reset()

        target_mgr  = TargetManager(list(cfg.enemies))
        phase_ctrl  = PhaseController(list(cfg.phases))
        spawn_ctrl  = SpawnController(list(cfg.spawn_waves))
        timeline    = EncounterTimeline(list(cfg.timeline_events))
        downtime    = DowntimeTracker()
        for w in cfg.downtime_windows:
            downtime.add_window(w)
        mt_engine   = MultiTargetEngine()

        total_damage    = 0.0
        total_casts     = 0
        downtime_ticks  = 0
        damage_per_tick: list[float] = []
        elapsed         = 0.0
        ticks           = 0

        while elapsed < cfg.fight_duration:
            # 1. Fire timeline events
            timeline.advance(elapsed)

            # 2. Process spawns
            new_enemies = spawn_ctrl.tick(elapsed)
            for e in new_enemies:
                target_mgr.add_target(e)

            # 3. Evaluate phase transitions
            primary = target_mgr.select_primary()
            if primary is not None:
                phase_ctrl.evaluate(primary.health_pct, elapsed)

            # 4. Check downtime
            if downtime.is_downtime(elapsed):
                downtime_ticks += 1
                damage_per_tick.append(0.0)
            else:
                # 5. Apply damage if targets alive
                active = target_mgr.active_targets
                alive  = [e for e in active if e.is_alive]
                if alive:
                    results = mt_engine.apply_hit(
                        alive, cfg.base_damage, cfg.hit_config
                    )
                    tick_dmg = MultiTargetEngine.total_damage(results)
                    total_damage += tick_dmg
                    total_casts  += 1
                    damage_per_tick.append(tick_dmg)
                else:
                    damage_per_tick.append(0.0)

            # 6. Clean up dead targets
            target_mgr.remove_dead_targets()

            # 7. Stop early if all dead
            if cfg.stop_on_all_dead and target_mgr.all_dead:
                elapsed += cfg.tick_size
                ticks   += 1
                break

            elapsed += cfg.tick_size
            ticks   += 1

        enemies_killed = sum(1 for e in cfg.enemies if not e.is_alive)
        active_phase   = phase_ctrl.active_phase
        all_dead       = all(not e.is_alive for e in cfg.enemies)

        return EncounterRunResult(
            total_damage=total_damage,
            elapsed_time=elapsed,
            ticks_simulated=ticks,
            all_enemies_dead=all_dead,
            enemies_killed=enemies_killed,
            total_casts=total_casts,
            downtime_ticks=downtime_ticks,
            active_phase_id=active_phase.phase_id if active_phase else None,
            damage_per_tick=damage_per_tick,
        )
