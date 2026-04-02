"""Tests for encounter state machine (Step 104)."""

import pytest
from encounter.downtime import DowntimeWindow
from encounter.enemy import EncounterEnemy, EnemyArchetype
from encounter.multi_target import HitDistribution, MultiHitConfig
from encounter.phases import EncounterPhase, PhaseModifiers, PhaseTransitionType
from encounter.spawn_controller import SpawnWave
from encounter.state_machine import EncounterConfig, EncounterMachine, EncounterRunResult
from encounter.timeline import EventType, TimelineEvent


def _enemy(health=1000.0, name="e"):
    return EncounterEnemy(max_health=health, current_health=health,
                          armor=0.0, name=name)

def _cfg(**kw) -> EncounterConfig:
    defaults = dict(
        enemies=[_enemy(name="boss")],
        fight_duration=10.0,
        tick_size=0.1,
        base_damage=50.0,
        hit_config=MultiHitConfig(rng_hit=0.0, rng_crit=99.0),
    )
    defaults.update(kw)
    return EncounterConfig(**defaults)


class TestBasicRun:
    def test_run_returns_result(self):
        result = EncounterMachine(_cfg()).run()
        assert isinstance(result, EncounterRunResult)

    def test_total_damage_positive(self):
        result = EncounterMachine(_cfg()).run()
        assert result.total_damage > 0.0

    def test_ticks_simulated(self):
        result = EncounterMachine(_cfg(fight_duration=1.0, tick_size=0.1)).run()
        assert result.ticks_simulated >= 10

    def test_enemy_takes_damage(self):
        enemy = _enemy(health=10000.0)
        EncounterMachine(_cfg(enemies=[enemy], base_damage=100.0)).run()
        assert enemy.current_health < 10000.0


class TestStopOnAllDead:
    def test_stops_early_when_all_dead(self):
        enemy = _enemy(health=100.0)
        result = EncounterMachine(_cfg(
            enemies=[enemy],
            fight_duration=60.0,
            tick_size=0.1,
            base_damage=200.0,
            stop_on_all_dead=True,
        )).run()
        assert result.all_enemies_dead is True
        assert result.elapsed_time < 60.0

    def test_runs_full_when_stop_disabled(self):
        enemy = _enemy(health=1_000_000.0)
        result = EncounterMachine(_cfg(
            enemies=[enemy],
            fight_duration=5.0,
            tick_size=0.1,
            base_damage=1.0,
            stop_on_all_dead=False,
        )).run()
        assert result.elapsed_time >= 4.9


class TestDowntime:
    def test_downtime_ticks_counted(self):
        windows = [DowntimeWindow("pause", start_time=2.0, end_time=4.0)]
        result = EncounterMachine(_cfg(
            enemies=[_enemy(health=1_000_000.0)],
            fight_duration=10.0,
            tick_size=0.1,
            downtime_windows=windows,
        )).run()
        assert result.downtime_ticks > 0

    def test_downtime_reduces_casts(self):
        windows = [DowntimeWindow("pause", start_time=0.0, end_time=10.0)]
        result = EncounterMachine(_cfg(
            enemies=[_enemy(health=1_000_000.0)],
            fight_duration=10.0,
            downtime_windows=windows,
        )).run()
        assert result.total_casts == 0


class TestPhaseTransition:
    def test_phase_activates_at_health_threshold(self):
        phase = EncounterPhase(
            "rage", PhaseTransitionType.HEALTH_BELOW, 50.0,
            PhaseModifiers(damage_bonus_pct=50.0),
        )
        enemy = _enemy(health=1_000_000.0)
        result = EncounterMachine(_cfg(
            enemies=[enemy],
            fight_duration=60.0,
            tick_size=0.1,
            base_damage=10000.0,
            phases=[phase],
        )).run()
        assert result.active_phase_id == "rage"


class TestSpawnWaves:
    def test_spawned_enemies_add_to_targets(self):
        add = _enemy(health=200.0, name="add")
        waves = [SpawnWave("w1", spawn_time=2.0, enemies=[add])]
        result = EncounterMachine(_cfg(
            enemies=[_enemy(health=1_000_000.0, name="boss")],
            fight_duration=5.0,
            tick_size=0.1,
            spawn_waves=waves,
            hit_config=MultiHitConfig(
                distribution=HitDistribution.CLEAVE,
                rng_hit=0.0, rng_crit=99.0,
            ),
        )).run()
        # Add should have taken some damage after t=2.0 (CLEAVE hits all)
        assert add.current_health < 200.0


class TestMultiTarget:
    def test_cleave_hits_all_enemies(self):
        enemies = [_enemy(health=1000.0, name=f"e{i}") for i in range(3)]
        result = EncounterMachine(_cfg(
            enemies=enemies,
            fight_duration=1.0,
            tick_size=0.1,
            base_damage=10.0,
            hit_config=MultiHitConfig(
                distribution=HitDistribution.CLEAVE,
                rng_hit=0.0, rng_crit=99.0,
            ),
        )).run()
        for e in enemies:
            assert e.current_health < 1000.0


class TestDamageAccounting:
    def test_damage_per_tick_length_matches_ticks(self):
        result = EncounterMachine(_cfg(
            enemies=[_enemy(health=1_000_000.0)],
            fight_duration=2.0, tick_size=0.1,
        )).run()
        assert len(result.damage_per_tick) == result.ticks_simulated

    def test_total_damage_sum_of_per_tick(self):
        result = EncounterMachine(_cfg(
            enemies=[_enemy(health=1_000_000.0)],
            fight_duration=5.0, tick_size=0.1,
        )).run()
        assert result.total_damage == pytest.approx(sum(result.damage_per_tick))
