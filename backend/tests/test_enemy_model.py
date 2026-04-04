"""J8 — Tests for enemy_model.py"""

import pytest
from data.models.enemy_model import EnemyModel


class TestEnemyCreation:
    def test_basic_creation(self):
        e = EnemyModel(enemy_id="goblin", max_health=500, armor=10)
        assert e.enemy_id == "goblin"
        assert e.max_health == 500
        assert e.armor == 10

    def test_resistances_stored(self):
        e = EnemyModel("boss", 10000, resistances={"fire": 30, "cold": 20}, armor=100)
        assert e.resistance("fire") == 30
        assert e.resistance("void") == 0.0  # default

    def test_to_dict(self):
        e = EnemyModel("x", 1000, armor=50)
        d = e.to_dict()
        assert d["enemy_id"] == "x"
        assert d["max_health"] == 1000


class TestResistanceValidation:
    def test_zero_max_health_raises(self):
        with pytest.raises(ValueError, match="max_health"):
            EnemyModel("x", max_health=0, armor=0)

    def test_negative_armor_raises(self):
        with pytest.raises(ValueError, match="armor"):
            EnemyModel("x", max_health=100, armor=-1)

    def test_empty_enemy_id_raises(self):
        with pytest.raises(ValueError, match="enemy_id"):
            EnemyModel("", max_health=100, armor=0)


class TestCritFields:
    def test_default_crit_fields(self):
        e = EnemyModel("x", 1000, armor=0)
        assert e.crit_chance == 0.0
        assert e.crit_multiplier == 1.5

    def test_custom_crit_chance(self):
        e = EnemyModel("x", 1000, armor=0, crit_chance=0.25)
        assert e.crit_chance == 0.25

    def test_custom_crit_multiplier(self):
        e = EnemyModel("x", 1000, armor=0, crit_multiplier=3.0)
        assert e.crit_multiplier == 3.0

    def test_crit_chance_above_1_raises(self):
        with pytest.raises(ValueError, match="crit_chance"):
            EnemyModel("x", 1000, armor=0, crit_chance=1.5)

    def test_crit_chance_negative_raises(self):
        with pytest.raises(ValueError, match="crit_chance"):
            EnemyModel("x", 1000, armor=0, crit_chance=-0.1)

    def test_crit_multiplier_below_1_raises(self):
        with pytest.raises(ValueError, match="crit_multiplier"):
            EnemyModel("x", 1000, armor=0, crit_multiplier=0.5)


class TestNameAndCategory:
    def test_default_name_and_category(self):
        e = EnemyModel("x", 1000, armor=0)
        assert e.name == ""
        assert e.category == ""

    def test_custom_name_and_category(self):
        e = EnemyModel("skeleton", 500, armor=0, name="Skeleton Archer", category="undead")
        assert e.name == "Skeleton Archer"
        assert e.category == "undead"


class TestResistanceClamping:
    def test_over_100_resistance_clamped_with_warning(self):
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            e = EnemyModel("x", 1000, armor=0, resistances={"fire": 150})
        assert e.resistance("fire") == 100.0
        assert len(w) == 1
        assert "exceeds 100" in str(w[0].message).lower() or "100" in str(w[0].message)

    def test_exactly_100_no_warning(self):
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            e = EnemyModel("x", 1000, armor=0, resistances={"fire": 100})
        assert e.resistance("fire") == 100.0
        assert len(w) == 0

    def test_to_dict_includes_crit_fields(self):
        e = EnemyModel("x", 1000, armor=0, crit_chance=0.1, crit_multiplier=2.0,
                        name="Boss", category="demon")
        d = e.to_dict()
        assert d["crit_chance"] == 0.1
        assert d["crit_multiplier"] == 2.0
        assert d["name"] == "Boss"
        assert d["category"] == "demon"
