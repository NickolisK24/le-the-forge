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
