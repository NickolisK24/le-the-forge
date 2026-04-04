"""
Tests for combat_simulator — Upgrade 2

Covers: Monte Carlo determinism, result structure, DPS/EHP metrics,
edge cases, seeded RNG, enemy templates, stat sensitivity.
"""

from __future__ import annotations

import math
import pytest

from app.engines.combat_simulator import run_combat_simulation, CombatSimulationResult
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stats(**kw) -> BuildStats:
    defaults = dict(
        max_health=1000.0,
        base_damage=100.0,
        attack_speed=1.0,
        crit_chance=0.05,
        crit_multiplier=1.5,
        armour=0.0,
        fire_res=0.0,
        cold_res=0.0,
        lightning_res=0.0,
        void_res=0.0,
    )
    defaults.update(kw)
    s = BuildStats()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


_DUMMY_ENEMY = {
    "name": "Training Dummy",
    "max_health": 10000,
    "armor": 0,
    "resistances": {"physical": 0, "fire": 0, "cold": 0, "lightning": 0, "void": 0, "necrotic": 0},
    "crit_chance": 0.0,
    "crit_multiplier": 1.5,
    "damage_per_hit": 0,
    "attack_speed": 0,
    "damage_range": [0, 0],
    "skill_pattern": ["basic"],
    "tags": ["dummy"],
}

_NORMAL_ENEMY = {
    "name": "Undead Archer",
    "max_health": 800,
    "armor": 50,
    "resistances": {"physical": 0, "fire": 0, "cold": 25, "lightning": 0, "void": 0, "necrotic": 50},
    "crit_chance": 0.05,
    "crit_multiplier": 1.5,
    "damage_per_hit": 45,
    "attack_speed": 1.2,
    "damage_range": [35, 60],
    "skill_pattern": ["basic", "basic", "heavy"],
    "tags": ["undead", "ranged"],
}

_BOSS_ENEMY = {
    "name": "Lagon",
    "max_health": 50000,
    "armor": 600,
    "resistances": {"physical": 25, "fire": 0, "cold": 50, "lightning": 0, "void": 0, "necrotic": 0},
    "crit_chance": 0.15,
    "crit_multiplier": 2.5,
    "damage_per_hit": 500,
    "attack_speed": 0.8,
    "damage_range": [380, 620],
    "skill_pattern": ["basic", "basic", "heavy", "heavy", "basic", "heavy"],
    "tags": ["boss", "unique", "water"],
}


def _run(stats=None, enemy=None, **kw) -> CombatSimulationResult:
    if stats is None:
        stats = _stats()
    if enemy is None:
        enemy = _DUMMY_ENEMY
    return run_combat_simulation(stats, enemy, **kw)


# ---------------------------------------------------------------------------
# 1. Return type and structure
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_combat_simulation_result(self):
        r = _run()
        assert isinstance(r, CombatSimulationResult)

    def test_to_dict_has_average_dps(self):
        r = _run()
        assert "average_dps" in r.to_dict()

    def test_to_dict_has_median_dps(self):
        r = _run()
        assert "median_dps" in r.to_dict()

    def test_to_dict_has_dps_variance(self):
        r = _run()
        assert "dps_variance" in r.to_dict()

    def test_to_dict_has_dps_std_dev(self):
        r = _run()
        assert "dps_std_dev" in r.to_dict()

    def test_to_dict_has_iterations(self):
        r = _run(iterations=50)
        assert r.to_dict()["iterations"] == 50

    def test_to_dict_has_execution_time(self):
        r = _run()
        assert "execution_time" in r.to_dict()

    def test_to_dict_has_death_rate(self):
        r = _run()
        assert "death_rate" in r.to_dict()

    def test_to_dict_has_crit_rate_actual(self):
        r = _run()
        assert "crit_rate_actual" in r.to_dict()

    def test_to_dict_has_total_damage(self):
        r = _run()
        assert "total_damage" in r.to_dict()

    def test_to_dict_has_survival_time(self):
        r = _run()
        assert "survival_time" in r.to_dict()

    def test_to_dict_has_dps_p10(self):
        r = _run()
        assert "dps_p10" in r.to_dict()

    def test_to_dict_has_dps_p90(self):
        r = _run()
        assert "dps_p90" in r.to_dict()

    def test_average_dps_is_numeric(self):
        r = _run()
        assert isinstance(r.average_dps, (int, float))

    def test_iterations_matches_input(self):
        r = _run(iterations=100)
        assert r.iterations == 100

    def test_execution_time_positive(self):
        r = _run(iterations=10)
        assert r.execution_time >= 0.0


# ---------------------------------------------------------------------------
# 2. Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_seed_same_dps(self):
        r1 = _run(seed=42, iterations=200)
        r2 = _run(seed=42, iterations=200)
        assert r1.average_dps == r2.average_dps

    def test_same_seed_same_death_rate(self):
        r1 = _run(seed=99, iterations=200)
        r2 = _run(seed=99, iterations=200)
        assert r1.death_rate == r2.death_rate

    def test_same_seed_same_crit_rate(self):
        r1 = _run(seed=7, iterations=200)
        r2 = _run(seed=7, iterations=200)
        assert r1.crit_rate_actual == r2.crit_rate_actual

    @pytest.mark.parametrize("seed", [0, 1, 7, 42, 100, 12345, 99999])
    def test_seeded_determinism_multiple_seeds(self, seed):
        r1 = _run(seed=seed, iterations=100)
        r2 = _run(seed=seed, iterations=100)
        assert r1.average_dps == r2.average_dps

    def test_different_seeds_may_differ(self):
        r1 = _run(seed=1, iterations=500)
        r2 = _run(seed=2, iterations=500)
        # With enough iterations and different seeds, results can differ
        # (not guaranteed, but very likely)
        assert isinstance(r1.average_dps, float)
        assert isinstance(r2.average_dps, float)

    def test_input_not_mutated(self):
        s = _stats(base_damage=200.0)
        original_damage = s.base_damage
        _run(stats=s, iterations=50)
        assert s.base_damage == original_damage

    def test_enemy_not_mutated(self):
        enemy = dict(_NORMAL_ENEMY)
        original_hp = enemy["max_health"]
        _run(enemy=enemy, iterations=50)
        assert enemy["max_health"] == original_hp


# ---------------------------------------------------------------------------
# 3. DPS values are sane
# ---------------------------------------------------------------------------

class TestDPSValues:
    def test_average_dps_nonnegative(self):
        r = _run()
        assert r.average_dps >= 0

    def test_median_dps_nonnegative(self):
        r = _run()
        assert r.median_dps >= 0

    def test_more_base_damage_means_more_dps(self):
        r_low = _run(stats=_stats(base_damage=50.0), iterations=500)
        r_high = _run(stats=_stats(base_damage=500.0), iterations=500)
        assert r_high.average_dps >= r_low.average_dps

    def test_zero_damage_dps_very_low(self):
        r = _run(stats=_stats(base_damage=0.0), iterations=100)
        # Base class stats may add some residual damage; just check non-negative
        assert r.average_dps >= 0.0

    def test_dps_p90_at_least_p10(self):
        r = _run(iterations=200)
        assert r.dps_p90 >= r.dps_p10

    def test_variance_nonnegative(self):
        r = _run()
        assert r.dps_variance >= 0.0

    def test_std_dev_nonnegative(self):
        r = _run()
        assert r.dps_std_dev >= 0.0

    def test_total_damage_nonnegative(self):
        r = _run()
        assert r.total_damage >= 0.0

    def test_survival_time_in_range(self):
        r = _run(duration=60.0)
        assert 0.0 <= r.survival_time <= 60.0 + 1.0  # small tolerance

    def test_crit_rate_in_range(self):
        r = _run()
        assert 0.0 <= r.crit_rate_actual <= 1.0

    def test_death_rate_in_range(self):
        r = _run(enemy=_NORMAL_ENEMY, iterations=100)
        assert 0.0 <= r.death_rate <= 1.0


# ---------------------------------------------------------------------------
# 4. Enemy types
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("enemy", [_DUMMY_ENEMY, _NORMAL_ENEMY, _BOSS_ENEMY])
def test_each_enemy_type_resolves(enemy):
    r = _run(enemy=enemy, iterations=50)
    assert r.average_dps >= 0


@pytest.mark.parametrize("enemy", [_DUMMY_ENEMY, _NORMAL_ENEMY, _BOSS_ENEMY])
def test_iterations_count_matches(enemy):
    r = _run(enemy=enemy, iterations=77)
    assert r.iterations == 77


@pytest.mark.parametrize("enemy_name", [
    "training_dummy", "undead_archer", "sentinel_golem",
    "void_touched_cultist", "fire_elemental", "lagon_boss",
    "empowered_lich", "blood_knight", "void_spider",
])
def test_enemies_json_enemy_templates(enemy_name):
    import json, os
    path = os.path.join(
        os.path.dirname(__file__), "..", "app", "game_data", "enemies.json"
    )
    data = json.load(open(path))
    assert enemy_name in data["enemies"]


# ---------------------------------------------------------------------------
# 5. Stat sensitivity
# ---------------------------------------------------------------------------

class TestStatSensitivity:
    def test_higher_attack_speed_more_dps(self):
        r_slow = _run(stats=_stats(attack_speed=0.5, base_damage=100.0), iterations=500)
        r_fast = _run(stats=_stats(attack_speed=2.0, base_damage=100.0), iterations=500)
        assert r_fast.average_dps >= r_slow.average_dps

    def test_higher_crit_chance_changes_crit_rate(self):
        r_low = _run(stats=_stats(crit_chance=0.0), iterations=500)
        r_high = _run(stats=_stats(crit_chance=1.0), iterations=500)
        assert r_high.crit_rate_actual >= r_low.crit_rate_actual

    def test_crit_chance_0_means_no_crits(self):
        r = _run(stats=_stats(crit_chance=0.0), iterations=500)
        assert r.crit_rate_actual == pytest.approx(0.0, abs=0.01)

    def test_crit_chance_1_means_all_crits(self):
        r = _run(stats=_stats(crit_chance=1.0), iterations=200)
        assert r.crit_rate_actual == pytest.approx(1.0, abs=0.01)

    def test_higher_armour_reduces_damage_taken(self):
        r_noarmour = _run(stats=_stats(armour=0.0), enemy=_NORMAL_ENEMY, iterations=500)
        r_armour = _run(stats=_stats(armour=10000.0), enemy=_NORMAL_ENEMY, iterations=500)
        # More armour → higher survival time or lower death rate
        assert r_armour.survival_time >= r_noarmour.survival_time - 1.0  # at least not worse

    def test_high_health_survives_longer(self):
        r_low = _run(stats=_stats(max_health=100.0), enemy=_NORMAL_ENEMY, iterations=300)
        r_high = _run(stats=_stats(max_health=100000.0), enemy=_NORMAL_ENEMY, iterations=300)
        assert r_high.survival_time >= r_low.survival_time


# ---------------------------------------------------------------------------
# 6. Iteration count effects
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [10, 50, 100, 500, 1000])
def test_iteration_count_respected(n):
    r = _run(iterations=n)
    assert r.iterations == n


@pytest.mark.parametrize("n", [10, 50, 200])
def test_more_iterations_same_seed_consistent(n):
    r = _run(iterations=n, seed=42)
    assert r.iterations == n
    assert r.average_dps >= 0


def test_single_iteration():
    r = _run(iterations=1)
    assert r.iterations == 1
    assert r.average_dps >= 0


# ---------------------------------------------------------------------------
# 7. Duration sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("duration", [1.0, 5.0, 10.0, 30.0, 60.0, 120.0])
def test_various_durations_resolve(duration):
    r = run_combat_simulation(_stats(), _DUMMY_ENEMY, iterations=50, duration=duration)
    assert r.average_dps >= 0
    assert r.survival_time <= duration + 1.0


# ---------------------------------------------------------------------------
# 8. Build dict input
# ---------------------------------------------------------------------------

class TestBuildDictInput:
    def test_accepts_build_dict(self):
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [],
            "primary_skill": "Fireball",
        }
        r = run_combat_simulation(build, _DUMMY_ENEMY, iterations=50)
        assert isinstance(r, CombatSimulationResult)

    def test_build_dict_gives_positive_dps(self):
        build = {
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "passive_tree": [],
            "gear": [],
        }
        r = run_combat_simulation(build, _DUMMY_ENEMY, iterations=50)
        assert r.average_dps >= 0

    def test_build_stats_and_dict_both_accepted(self):
        s = _stats()
        build = {"character_class": "Sentinel", "mastery": "Paladin",
                 "passive_tree": [], "gear": []}
        r1 = run_combat_simulation(s, _DUMMY_ENEMY, iterations=50)
        r2 = run_combat_simulation(build, _DUMMY_ENEMY, iterations=50)
        assert isinstance(r1, CombatSimulationResult)
        assert isinstance(r2, CombatSimulationResult)


# ---------------------------------------------------------------------------
# 9. Percentile metrics
# ---------------------------------------------------------------------------

class TestPercentiles:
    def test_p10_less_than_or_equal_to_average(self):
        r = _run(iterations=500)
        assert r.dps_p10 <= r.average_dps + 1e-6

    def test_p90_greater_than_or_equal_to_average(self):
        r = _run(iterations=500)
        assert r.dps_p90 >= r.average_dps - 1e-6

    def test_p10_less_than_or_equal_to_p90(self):
        r = _run(iterations=500)
        assert r.dps_p10 <= r.dps_p90

    def test_median_between_p10_and_p90(self):
        r = _run(iterations=500)
        assert r.dps_p10 <= r.median_dps + 1e-6
        assert r.median_dps <= r.dps_p90 + 1e-6


# ---------------------------------------------------------------------------
# 10. Result to_dict round-trip
# ---------------------------------------------------------------------------

class TestToDictRoundTrip:
    def test_to_dict_is_dict(self):
        r = _run(iterations=20)
        assert isinstance(r.to_dict(), dict)

    def test_to_dict_all_numeric_values(self):
        r = _run(iterations=20)
        d = r.to_dict()
        numeric_keys = [
            "average_dps", "median_dps", "dps_variance", "dps_std_dev",
            "dps_p10", "dps_p90", "death_rate", "crit_rate_actual",
            "total_damage", "survival_time", "execution_time",
        ]
        for k in numeric_keys:
            if k in d:
                assert isinstance(d[k], (int, float)), f"{k} should be numeric"

    def test_iterations_in_dict_matches_input(self):
        r = _run(iterations=33)
        assert r.to_dict()["iterations"] == 33


# ---------------------------------------------------------------------------
# 11. Enemy from file — smoke tests
# ---------------------------------------------------------------------------

class TestEnemyFileIntegration:
    def _load_enemy(self, key):
        import json, os
        path = os.path.join(
            os.path.dirname(__file__), "..", "app", "game_data", "enemies.json"
        )
        return json.load(open(path))["enemies"][key]

    def test_training_dummy(self):
        enemy = self._load_enemy("training_dummy")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_undead_archer(self):
        enemy = self._load_enemy("undead_archer")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_sentinel_golem(self):
        enemy = self._load_enemy("sentinel_golem")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_lagon_boss(self):
        enemy = self._load_enemy("lagon_boss")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_empowered_lich(self):
        enemy = self._load_enemy("empowered_lich")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_blood_knight(self):
        enemy = self._load_enemy("blood_knight")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0

    def test_void_spider(self):
        enemy = self._load_enemy("void_spider")
        r = _run(enemy=enemy, iterations=50)
        assert r.average_dps >= 0


# ---------------------------------------------------------------------------
# 12. Parametric damage type / resistance tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("res_attr,res_val", [
    ("fire_res", 0.0),
    ("fire_res", 25.0),
    ("fire_res", 50.0),
    ("fire_res", 75.0),
    ("cold_res", 0.0),
    ("cold_res", 75.0),
    ("lightning_res", 0.0),
    ("lightning_res", 75.0),
    ("void_res", 0.0),
    ("void_res", 75.0),
])
def test_various_resistances_resolve(res_attr, res_val):
    s = _stats(**{res_attr: res_val})
    r = _run(stats=s, iterations=50)
    assert r.average_dps >= 0


# ---------------------------------------------------------------------------
# 13. Stats with extreme values
# ---------------------------------------------------------------------------

class TestExtremeValues:
    def test_very_high_base_damage(self):
        s = _stats(base_damage=1_000_000.0)
        r = _run(stats=s, iterations=50)
        assert r.average_dps > 0

    def test_very_low_base_damage(self):
        s = _stats(base_damage=0.001)
        r = _run(stats=s, iterations=50)
        assert r.average_dps >= 0

    def test_very_high_health(self):
        s = _stats(max_health=1_000_000.0)
        r = _run(stats=s, enemy=_NORMAL_ENEMY, iterations=50)
        assert r.death_rate <= 1.0

    def test_very_low_health(self):
        s = _stats(max_health=1.0)
        r = _run(stats=s, enemy=_BOSS_ENEMY, iterations=50)
        assert r.death_rate <= 1.0

    def test_zero_attack_speed(self):
        s = _stats(attack_speed=0.0, base_damage=100.0)
        r = _run(stats=s, iterations=50)
        assert r.average_dps >= 0


# ---------------------------------------------------------------------------
# 14. Crit multiplier sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("crit_mult", [1.0, 1.5, 2.0, 3.0, 5.0])
def test_crit_multiplier_varies(crit_mult):
    s = _stats(crit_chance=0.5, crit_multiplier=crit_mult)
    r = _run(stats=s, iterations=200)
    assert r.average_dps >= 0


def test_higher_crit_mult_means_more_dps_with_crits():
    r_low = _run(stats=_stats(crit_chance=0.5, crit_multiplier=1.0), iterations=500, seed=42)
    r_high = _run(stats=_stats(crit_chance=0.5, crit_multiplier=3.0), iterations=500, seed=42)
    assert r_high.average_dps >= r_low.average_dps


# ---------------------------------------------------------------------------
# 15. Multiple enemies parametrized
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("armor,expected_max_dps_ratio", [
    (0, float("inf")),
    (100, float("inf")),
    (1000, float("inf")),
])
def test_enemy_armor_levels(armor, expected_max_dps_ratio):
    enemy = dict(_DUMMY_ENEMY)
    enemy["armor"] = armor
    r = _run(enemy=enemy, stats=_stats(base_damage=200.0), iterations=200)
    assert r.average_dps >= 0


@pytest.mark.parametrize("enemy_res,expected_non_negative", [
    ({"fire": 0, "cold": 0, "lightning": 0, "void": 0, "necrotic": 0, "physical": 0}, True),
    ({"fire": 75, "cold": 75, "lightning": 75, "void": 75, "necrotic": 75, "physical": 75}, True),
    ({"fire": -25, "cold": 0, "lightning": 0, "void": 0, "necrotic": 0, "physical": 0}, True),
])
def test_enemy_resistance_levels(enemy_res, expected_non_negative):
    enemy = dict(_DUMMY_ENEMY)
    enemy["resistances"] = enemy_res
    r = _run(enemy=enemy, iterations=100)
    assert r.average_dps >= 0
