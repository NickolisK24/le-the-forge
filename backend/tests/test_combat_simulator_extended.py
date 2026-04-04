"""
Extended combat simulator tests — parametrized coverage.
"""

from __future__ import annotations

import pytest

from app.engines.combat_simulator import run_combat_simulation, CombatSimulationResult
from app.engines.stat_engine import BuildStats


def _stats(**kw) -> BuildStats:
    defaults = dict(max_health=1000.0, base_damage=100.0, attack_speed=1.0,
                    crit_chance=0.05, crit_multiplier=1.5, armour=0.0)
    defaults.update(kw)
    s = BuildStats()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


def _enemy(hp=1000, armor=0, damage=50, attack_speed=1.0,
           damage_range=None, crits=0.05, crit_mult=1.5,
           resistances=None) -> dict:
    return {
        "max_health": hp,
        "armor": armor,
        "crit_chance": crits,
        "crit_multiplier": crit_mult,
        "damage_per_hit": damage,
        "attack_speed": attack_speed,
        "damage_range": damage_range or [int(damage * 0.8), int(damage * 1.2)],
        "resistances": resistances or {
            "physical": 0, "fire": 0, "cold": 0,
            "lightning": 0, "void": 0, "necrotic": 0,
        },
        "skill_pattern": ["basic"],
        "tags": [],
    }


# ---------------------------------------------------------------------------
# A. All seeds produce valid results
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(20))
def test_seed_range_valid_results(seed):
    r = run_combat_simulation(_stats(), _enemy(), seed=seed, iterations=50)
    assert 0.0 <= r.death_rate <= 1.0
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("seed", range(20))
def test_seed_determinism(seed):
    s = _stats()
    e = _enemy()
    r1 = run_combat_simulation(s, e, seed=seed, iterations=100)
    r2 = run_combat_simulation(s, e, seed=seed, iterations=100)
    assert r1.average_dps == r2.average_dps


# ---------------------------------------------------------------------------
# B. Various stat configurations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("base_damage", [1.0, 10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0])
def test_base_damage_levels(base_damage):
    r = run_combat_simulation(_stats(base_damage=base_damage), _enemy(),
                               iterations=100, seed=42)
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("attack_speed", [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0])
def test_attack_speed_levels(attack_speed):
    r = run_combat_simulation(_stats(attack_speed=attack_speed), _enemy(),
                               iterations=100, seed=42)
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("crit_chance", [0.0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0])
def test_crit_chance_levels(crit_chance):
    r = run_combat_simulation(_stats(crit_chance=crit_chance), _enemy(),
                               iterations=200, seed=42)
    assert 0.0 <= r.crit_rate_actual <= 1.0


@pytest.mark.parametrize("crit_mult", [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 5.0])
def test_crit_multiplier_levels(crit_mult):
    r = run_combat_simulation(_stats(crit_multiplier=crit_mult, crit_chance=0.5),
                               _enemy(), iterations=100, seed=42)
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("armour", [0, 50, 100, 300, 500, 1000, 5000])
def test_armour_levels(armour):
    r = run_combat_simulation(_stats(armour=armour), _enemy(damage=100),
                               iterations=100, seed=42)
    assert r.death_rate <= 1.0


@pytest.mark.parametrize("max_health", [10.0, 100.0, 500.0, 1000.0, 5000.0, 10000.0])
def test_max_health_levels(max_health):
    r = run_combat_simulation(_stats(max_health=max_health), _enemy(damage=100),
                               iterations=100, seed=42)
    assert r.survival_time >= 0.0


# ---------------------------------------------------------------------------
# C. Enemy variations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("enemy_hp", [100, 500, 1000, 5000, 10000, 50000])
def test_enemy_hp_levels(enemy_hp):
    r = run_combat_simulation(_stats(), _enemy(hp=enemy_hp),
                               iterations=100, seed=42)
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("enemy_armor", [0, 100, 300, 500, 1000])
def test_enemy_armor_levels(enemy_armor):
    r = run_combat_simulation(_stats(base_damage=200.0), _enemy(armor=enemy_armor),
                               iterations=100, seed=42)
    assert r.average_dps >= 0.0


@pytest.mark.parametrize("enemy_damage", [0, 10, 50, 100, 200, 500])
def test_enemy_damage_levels(enemy_damage):
    r = run_combat_simulation(_stats(max_health=2000.0), _enemy(damage=enemy_damage),
                               iterations=100, seed=42)
    assert r.death_rate <= 1.0


@pytest.mark.parametrize("res_val", [0, 10, 25, 50, 75])
def test_enemy_resistance_levels(res_val):
    resistances = {
        "physical": res_val, "fire": res_val, "cold": res_val,
        "lightning": res_val, "void": res_val, "necrotic": res_val,
    }
    r = run_combat_simulation(_stats(), _enemy(resistances=resistances),
                               iterations=100, seed=42)
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# D. Duration variations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("duration", [0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0])
def test_duration_levels(duration):
    r = run_combat_simulation(_stats(), _enemy(), iterations=50,
                               duration=duration, seed=42)
    assert r.survival_time <= duration + 1.0
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# E. Iteration count variations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 5, 10, 20, 50, 100, 200])
def test_iteration_counts(n):
    r = run_combat_simulation(_stats(), _enemy(), iterations=n, seed=42)
    assert r.iterations == n
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# F. Character class builds
# ---------------------------------------------------------------------------

_CLASS_BUILDS = [
    ("Mage", "Sorcerer"),
    ("Sentinel", "Paladin"),
    ("Rogue", "Bladedancer"),
    ("Primalist", "Druid"),
    ("Acolyte", "Lich"),
]


@pytest.mark.parametrize("char_class,mastery", _CLASS_BUILDS)
def test_class_builds_resolve(char_class, mastery):
    build = {"character_class": char_class, "mastery": mastery,
             "passive_tree": [], "gear": []}
    r = run_combat_simulation(build, _enemy(), iterations=50, seed=42)
    assert isinstance(r, CombatSimulationResult)


@pytest.mark.parametrize("char_class,mastery", _CLASS_BUILDS)
def test_class_builds_nonneg_dps(char_class, mastery):
    build = {"character_class": char_class, "mastery": mastery,
             "passive_tree": [], "gear": []}
    r = run_combat_simulation(build, _enemy(), iterations=50, seed=42)
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# G. Metrics monotonicity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [42, 99, 123])
def test_p90_gte_p10(seed):
    r = run_combat_simulation(_stats(), _enemy(), iterations=200, seed=seed)
    assert r.dps_p90 >= r.dps_p10


@pytest.mark.parametrize("seed", [42, 99, 123])
def test_median_between_p10_p90(seed):
    r = run_combat_simulation(_stats(), _enemy(), iterations=200, seed=seed)
    assert r.dps_p10 <= r.median_dps + 1e-6
    assert r.median_dps <= r.dps_p90 + 1e-6


@pytest.mark.parametrize("iterations", [50, 100, 200])
def test_variance_nonneg(iterations):
    r = run_combat_simulation(_stats(), _enemy(), iterations=iterations, seed=42)
    assert r.dps_variance >= 0.0


# ---------------------------------------------------------------------------
# H. All result fields present per iteration count
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [10, 50, 100])
def test_all_fields_present(n):
    r = run_combat_simulation(_stats(), _enemy(), iterations=n, seed=42)
    d = r.to_dict()
    required = {"average_dps", "median_dps", "dps_variance", "dps_std_dev",
                "dps_p10", "dps_p90", "death_rate", "crit_rate_actual",
                "total_damage", "survival_time", "iterations", "execution_time"}
    assert required.issubset(d.keys())


# ---------------------------------------------------------------------------
# I. Tick size variations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tick", [0.1, 0.25, 0.5, 1.0, 2.0])
def test_tick_sizes(tick):
    r = run_combat_simulation(_stats(), _enemy(), iterations=50,
                               tick=tick, duration=10.0, seed=42)
    assert r.average_dps >= 0.0
    assert r.iterations == 50


# ---------------------------------------------------------------------------
# J. Enemy with various skill patterns
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_pattern", [
    ["basic"],
    ["basic", "heavy"],
    ["basic", "basic", "heavy"],
    ["heavy", "heavy", "heavy"],
    ["basic", "heavy", "basic", "heavy"],
])
def test_skill_patterns(skill_pattern):
    e = _enemy()
    e["skill_pattern"] = skill_pattern
    r = run_combat_simulation(_stats(), e, iterations=50, seed=42)
    assert r.average_dps >= 0.0


# ---------------------------------------------------------------------------
# K. Death rate behavior
# ---------------------------------------------------------------------------

def test_invincible_player_no_deaths():
    r = run_combat_simulation(
        _stats(max_health=1_000_000.0, armour=99999.0),
        _enemy(damage=1),
        iterations=200, seed=42
    )
    assert r.death_rate == pytest.approx(0.0, abs=0.05)


def test_fragile_player_high_death_rate():
    r = run_combat_simulation(
        _stats(max_health=1.0),
        _enemy(damage=1000, attack_speed=10.0),
        iterations=200, seed=42
    )
    assert r.death_rate > 0.0
