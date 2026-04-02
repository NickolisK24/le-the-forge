"""Tests for boss template system (Step 106)."""

import pytest
from encounter.boss_templates import (ADD_FIGHT, MOVEMENT_BOSS, SHIELDED_BOSS,
                                       STANDARD_BOSS, TEMPLATES, TRAINING_DUMMY,
                                       load_template)
from encounter.state_machine import EncounterMachine


class TestLoadTemplate:
    def test_training_dummy_loads(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=100.0)
        assert len(cfg.enemies) == 1
        assert cfg.enemies[0].max_health == pytest.approx(1_000_000.0)
        assert cfg.enemies[0].armor      == pytest.approx(0.0)

    def test_standard_boss_resistances(self):
        cfg = load_template(STANDARD_BOSS)
        boss = cfg.enemies[0]
        assert boss.resistances["fire"] == pytest.approx(40.0)
        assert boss.resistances["physical"] == pytest.approx(20.0)

    def test_standard_boss_phase_attached(self):
        cfg = load_template(STANDARD_BOSS)
        assert len(cfg.phases) == 1
        assert cfg.phases[0].phase_id == "enrage"

    def test_shielded_boss_has_shield(self):
        cfg = load_template(SHIELDED_BOSS)
        boss = cfg.enemies[0]
        assert boss.shield     == pytest.approx(5_000.0)
        assert boss.max_shield == pytest.approx(5_000.0)

    def test_add_fight_has_waves(self):
        cfg = load_template(ADD_FIGHT)
        assert len(cfg.spawn_waves) == 2
        assert cfg.spawn_waves[0].spawn_time == pytest.approx(10.0)
        assert len(cfg.spawn_waves[0].enemies) == 3

    def test_movement_boss_has_downtime(self):
        cfg = load_template(MOVEMENT_BOSS)
        assert len(cfg.downtime_windows) == 2

    def test_fresh_enemies_each_load(self):
        cfg1 = load_template(STANDARD_BOSS)
        cfg2 = load_template(STANDARD_BOSS)
        assert cfg1.enemies[0] is not cfg2.enemies[0]

    def test_custom_base_damage(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=500.0)
        assert cfg.base_damage == pytest.approx(500.0)


class TestTemplateRegistry:
    def test_all_templates_in_registry(self):
        for name in ["training_dummy", "standard_boss", "shielded_boss",
                     "add_fight", "movement_boss"]:
            assert name in TEMPLATES

    def test_registry_lookup(self):
        assert TEMPLATES["training_dummy"] is TRAINING_DUMMY


class TestTemplateRunnable:
    def test_training_dummy_runs(self):
        cfg = load_template(TRAINING_DUMMY, base_damage=1000.0)
        result = EncounterMachine(cfg).run()
        assert result.total_damage > 0.0

    def test_add_fight_spawns_enemies(self):
        cfg = load_template(ADD_FIGHT, base_damage=500.0)
        cfg.hit_config.distribution  # just access to confirm no error
        result = EncounterMachine(cfg).run()
        assert result.total_casts > 0
