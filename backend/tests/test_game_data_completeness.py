"""
Tests verifying completeness and correctness of game data JSON files.
"""

from __future__ import annotations

import json
import os
import pytest

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "game_data")


def _load(filename):
    with open(os.path.join(_DATA_DIR, filename)) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# constants.json
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def constants():
    return _load("constants.json")


class TestConstantsJson:
    def test_constants_loads(self, constants):
        assert isinstance(constants, dict)

    def test_has_combat_section(self, constants):
        assert "combat" in constants

    def test_has_defense_section(self, constants):
        assert "defense" in constants

    def test_has_crafting_section(self, constants):
        assert "crafting" in constants

    def test_has_simulation_section(self, constants):
        assert "simulation" in constants

    def test_has_optimization_section(self, constants):
        assert "optimization" in constants

    def test_combat_has_crit_chance_cap(self, constants):
        assert "crit_chance_cap" in constants["combat"]

    def test_combat_crit_chance_cap_positive(self, constants):
        assert constants["combat"]["crit_chance_cap"] > 0

    def test_defense_has_resistance_cap(self, constants):
        assert "resistance_cap" in constants["defense"]

    def test_defense_resistance_cap_positive(self, constants):
        assert constants["defense"]["resistance_cap"] > 0

    def test_defense_resistance_cap_at_most_100(self, constants):
        assert constants["defense"]["resistance_cap"] <= 100

    def test_crafting_has_max_prefixes(self, constants):
        assert "max_prefixes" in constants["crafting"]

    def test_crafting_max_prefixes_positive(self, constants):
        assert constants["crafting"]["max_prefixes"] > 0

    def test_crafting_has_max_suffixes(self, constants):
        assert "max_suffixes" in constants["crafting"]

    def test_crafting_has_max_affix_tier(self, constants):
        assert "max_affix_tier" in constants["crafting"]

    def test_crafting_max_affix_tier_at_least_7(self, constants):
        assert constants["crafting"]["max_affix_tier"] >= 7

    def test_simulation_has_default_iterations(self, constants):
        assert "default_monte_carlo_iterations" in constants["simulation"]

    def test_optimization_has_dps_weight(self, constants):
        assert "dps_weight" in constants["optimization"]

    def test_optimization_has_ehp_weight(self, constants):
        assert "ehp_weight" in constants["optimization"]


# ---------------------------------------------------------------------------
# enemies.json
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def enemies():
    return _load("enemies.json")


_REQUIRED_ENEMY_KEYS = [
    "max_health", "armor", "resistances", "crit_chance", "crit_multiplier",
    "damage_per_hit", "attack_speed", "damage_range", "skill_pattern", "tags",
]

_EXPECTED_ENEMIES = [
    "training_dummy", "undead_archer", "sentinel_golem",
    "void_touched_cultist", "fire_elemental", "lagon_boss",
    "empowered_lich", "blood_knight", "void_spider",
]

_RESISTANCE_TYPES = ["physical", "fire", "cold", "lightning", "void", "necrotic"]


class TestEnemiesJson:
    def test_enemies_loads(self, enemies):
        assert isinstance(enemies, dict)

    def test_has_enemies_key(self, enemies):
        assert "enemies" in enemies

    def test_enemies_is_dict(self, enemies):
        assert isinstance(enemies["enemies"], dict)

    def test_has_version(self, enemies):
        assert "_version" in enemies

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_expected_enemy_present(self, enemies, enemy_id):
        assert enemy_id in enemies["enemies"]

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    @pytest.mark.parametrize("key", _REQUIRED_ENEMY_KEYS)
    def test_enemy_has_required_key(self, enemies, enemy_id, key):
        assert key in enemies["enemies"][enemy_id]

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_max_health_positive(self, enemies, enemy_id):
        assert enemies["enemies"][enemy_id]["max_health"] > 0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_armor_nonneg(self, enemies, enemy_id):
        assert enemies["enemies"][enemy_id]["armor"] >= 0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_crit_chance_in_range(self, enemies, enemy_id):
        cc = enemies["enemies"][enemy_id]["crit_chance"]
        assert 0.0 <= cc <= 1.0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_crit_multiplier_at_least_1(self, enemies, enemy_id):
        assert enemies["enemies"][enemy_id]["crit_multiplier"] >= 1.0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_attack_speed_nonneg(self, enemies, enemy_id):
        assert enemies["enemies"][enemy_id]["attack_speed"] >= 0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_damage_range_is_list(self, enemies, enemy_id):
        dr = enemies["enemies"][enemy_id]["damage_range"]
        assert isinstance(dr, list)
        assert len(dr) == 2

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_damage_range_min_le_max(self, enemies, enemy_id):
        dr = enemies["enemies"][enemy_id]["damage_range"]
        assert dr[0] <= dr[1]

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_skill_pattern_nonempty(self, enemies, enemy_id):
        sp = enemies["enemies"][enemy_id]["skill_pattern"]
        assert isinstance(sp, list)
        assert len(sp) > 0

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    def test_enemy_tags_is_list(self, enemies, enemy_id):
        assert isinstance(enemies["enemies"][enemy_id]["tags"], list)

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    @pytest.mark.parametrize("res_type", _RESISTANCE_TYPES)
    def test_enemy_has_resistance_type(self, enemies, enemy_id, res_type):
        assert res_type in enemies["enemies"][enemy_id]["resistances"]

    @pytest.mark.parametrize("enemy_id", _EXPECTED_ENEMIES)
    @pytest.mark.parametrize("res_type", _RESISTANCE_TYPES)
    def test_enemy_resistance_numeric(self, enemies, enemy_id, res_type):
        val = enemies["enemies"][enemy_id]["resistances"][res_type]
        assert isinstance(val, (int, float))


# ---------------------------------------------------------------------------
# items.json (if exists)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def items_data():
    path = os.path.join(_DATA_DIR, "items.json")
    if not os.path.exists(path):
        pytest.skip("items.json not found")
    return json.load(open(path))


class TestItemsJson:
    def test_items_loads(self, items_data):
        assert isinstance(items_data, dict)

    def test_has_items_key(self, items_data):
        assert "items" in items_data or len(items_data) > 0

    @pytest.mark.parametrize("item_idx", range(5))
    def test_first_items_accessible(self, items_data, item_idx):
        items = items_data.get("items", items_data)
        if isinstance(items, dict):
            keys = list(items.keys())
        else:
            keys = list(range(len(items)))
        if item_idx < len(keys):
            assert keys[item_idx] is not None


# ---------------------------------------------------------------------------
# constants.json — all numeric values positive where expected
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("section,key,expected_positive", [
    ("combat", "crit_chance_cap", True),
    ("combat", "base_hit_chance", True),
    ("defense", "resistance_cap", True),
    ("defense", "armor_cap", True),
    ("crafting", "max_prefixes", True),
    ("crafting", "max_suffixes", True),
    ("crafting", "max_affix_tier", True),
    ("simulation", "default_monte_carlo_iterations", True),
    ("optimization", "dps_weight", True),
    ("optimization", "ehp_weight", True),
])
def test_constant_is_positive(section, key, expected_positive):
    constants = _load("constants.json")
    if section in constants and key in constants[section]:
        val = constants[section][key]
        if expected_positive:
            assert val > 0, f"{section}.{key} should be positive"


@pytest.mark.parametrize("section", ["combat", "defense", "crafting", "simulation", "optimization"])
def test_section_is_dict(section):
    constants = _load("constants.json")
    if section in constants:
        assert isinstance(constants[section], dict)
