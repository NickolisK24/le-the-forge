"""
Encounter Snapshot Testing (Step 107).

Locks known-good encounter outcomes for deterministic reference builds.
"""

import pytest
from encounter.boss_templates import (ADD_FIGHT, MOVEMENT_BOSS, SHIELDED_BOSS,
                                       STANDARD_BOSS, TRAINING_DUMMY, load_template)
from encounter.multi_target import HitDistribution, MultiHitConfig
from encounter.state_machine import EncounterMachine


def _hit(dist=HitDistribution.SINGLE):
    return MultiHitConfig(distribution=dist, rng_hit=0.0, rng_crit=99.0)


class TestTrainingDummySnapshot:
    def test_total_damage(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(60_000.0)

    def test_total_casts(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_casts == 600

    def test_ticks_simulated(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.ticks_simulated == 600

    def test_enemy_not_killed(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.all_enemies_dead is False

    def test_damage_accounting(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(sum(r.damage_per_tick))


class TestStandardBossSnapshot:
    def test_total_damage(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(50_000.0)

    def test_enemy_killed(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.all_enemies_dead is True
        assert r.enemies_killed == 1

    def test_enrage_phase_activated(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.active_phase_id == "enrage"

    def test_stops_before_full_duration(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.elapsed_time < cfg.fight_duration


class TestAddFightSnapshot:
    def test_total_damage(self):
        cfg = load_template(ADD_FIGHT, base_damage=200.0,
                            hit_config=_hit(HitDistribution.CLEAVE))
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(26_000.0)

    def test_no_downtime(self):
        cfg = load_template(ADD_FIGHT, base_damage=200.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.downtime_ticks == 0


class TestMovementBossSnapshot:
    def test_has_downtime_ticks(self):
        cfg = load_template(MOVEMENT_BOSS, base_damage=200.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.downtime_ticks > 0

    def test_damage_per_tick_zero_during_downtime(self):
        cfg = load_template(MOVEMENT_BOSS, base_damage=200.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.downtime_ticks > 0
        zero_ticks = sum(1 for d in r.damage_per_tick if d == 0.0)
        assert zero_ticks >= r.downtime_ticks


class TestDeterminism:
    def test_same_output_multiple_runs(self):
        cfg = load_template(STANDARD_BOSS, base_damage=300.0, hit_config=_hit())
        r1 = EncounterMachine(cfg).run()
        cfg2 = load_template(STANDARD_BOSS, base_damage=300.0, hit_config=_hit())
        r2 = EncounterMachine(cfg2).run()
        assert r1.total_damage    == pytest.approx(r2.total_damage)
        assert r1.ticks_simulated == r2.ticks_simulated
        assert r1.total_casts     == r2.total_casts
