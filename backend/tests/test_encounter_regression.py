"""
Encounter Regression Tests (Step 108).

Locks known-good values for time-to-kill, total damage, phase transition
timing, and shield depletion across canonical encounter configurations.
All values are derived from deterministic (rng_hit=0, rng_crit=99) runs.
"""

import pytest
from encounter.boss_templates import (
    ADD_FIGHT, MOVEMENT_BOSS, SHIELDED_BOSS, STANDARD_BOSS,
    TRAINING_DUMMY, load_template,
)
from encounter.multi_target import HitDistribution, MultiHitConfig
from encounter.state_machine import EncounterMachine


def _hit(dist=HitDistribution.SINGLE):
    return MultiHitConfig(distribution=dist, rng_hit=0.0, rng_crit=99.0)


class TestTimeTokill:
    """Lock known time-to-kill values for reference configurations."""

    def test_standard_boss_ttk(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.elapsed_time == pytest.approx(13.8, abs=0.2)

    def test_standard_boss_ticks(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.ticks_simulated == 138

    def test_shielded_boss_ttk(self):
        cfg = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.elapsed_time == pytest.approx(7.5, abs=0.2)

    def test_shielded_boss_ticks(self):
        cfg = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.ticks_simulated == 75

    def test_training_dummy_never_dies(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.all_enemies_dead is False
        assert r.elapsed_time == pytest.approx(60.0, abs=0.1)


class TestTotalDamage:
    """Lock total damage output for canonical configurations."""

    def test_standard_boss_total_damage(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(50_000.0)

    def test_shielded_boss_total_damage(self):
        # Shield + health together = 5000 + 30000 = 35000
        # But boss dies at 0 hp; shield absorbs first so total health damage = 30000
        cfg = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(30_000.0, rel=0.05)

    def test_training_dummy_total_damage(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(60_000.0)

    def test_add_fight_cleave_total_damage(self):
        cfg = load_template(ADD_FIGHT, base_damage=200.0,
                            hit_config=_hit(HitDistribution.CLEAVE))
        r = EncounterMachine(cfg).run()
        assert r.total_damage == pytest.approx(26_000.0, rel=0.05)


class TestPhaseTransitionTiming:
    """Lock phase transition tick/timing for health-threshold phases."""

    def test_enrage_phase_activates(self):
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.active_phase_id == "enrage"

    def test_enrage_fires_after_70_pct_health_dealt(self):
        # Enrage fires at 30% hp remaining → 35 000 damage dealt
        cfg = load_template(STANDARD_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        cumulative = 0.0
        enrage_tick = None
        for i, d in enumerate(r.damage_per_tick):
            cumulative += d
            if enrage_tick is None and cumulative >= 35_000.0:
                enrage_tick = i
                break
        assert enrage_tick is not None
        assert enrage_tick == pytest.approx(96, abs=2)

    def test_no_phase_on_shielded_boss(self):
        cfg = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.active_phase_id is None

    def test_training_dummy_no_phase(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.active_phase_id is None


class TestShieldDepletion:
    """Verify shield is consumed before health on shielded boss."""

    def test_shielded_boss_dies(self):
        cfg = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        assert r.all_enemies_dead is True
        assert r.enemies_killed == 1

    def test_shielded_boss_requires_more_ticks_than_health_alone(self):
        # Without the 5000 shield, killing 30 000 health would take fewer ticks.
        # Shielded boss ticks ≥ bare boss with same health/armor
        from encounter.boss_templates import BossTemplate
        bare = BossTemplate("bare", boss_health=30_000.0, boss_armor=300.0,
                            boss_resistances={"fire": 50.0, "void": 60.0},
                            fight_duration=90.0)
        cfg_bare = load_template(bare, base_damage=500.0, hit_config=_hit())
        cfg_shld = load_template(SHIELDED_BOSS, base_damage=500.0, hit_config=_hit())
        r_bare = EncounterMachine(cfg_bare).run()
        r_shld = EncounterMachine(cfg_shld).run()
        assert r_shld.ticks_simulated >= r_bare.ticks_simulated


class TestDowntimeRegression:
    """Lock downtime tick counts for movement boss."""

    def test_movement_boss_downtime_ticks(self):
        cfg = load_template(MOVEMENT_BOSS, base_damage=200.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        # Two 3-second windows × 10 ticks/s = 60 downtime ticks possible;
        # fight ends before second window completes in some runs
        assert r.downtime_ticks == 30

    def test_movement_boss_zero_damage_ticks_match_downtime(self):
        cfg = load_template(MOVEMENT_BOSS, base_damage=200.0, hit_config=_hit())
        r = EncounterMachine(cfg).run()
        zero_ticks = sum(1 for d in r.damage_per_tick if d == 0.0)
        assert zero_ticks == r.downtime_ticks
