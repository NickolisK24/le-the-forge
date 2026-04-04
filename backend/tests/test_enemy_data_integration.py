"""J13 — Tests for enemy_data_integration.py"""

import pytest
from data.models.enemy_model import EnemyModel
from services.enemy_data_integration import (
    EnemyDataIntegration,
    EncounterConfig,
    EnemyValidationError,
)


def make_enemies(n=3):
    return [
        EnemyModel(f"enemy_{i}", max_health=1000 * (i + 1), armor=50 * i)
        for i in range(n)
    ]


class TestEnemyStatCorrectness:
    def test_build_encounter_success(self):
        integ = EnemyDataIntegration()
        config = integ.build_encounter(make_enemies(3))
        assert isinstance(config, EncounterConfig)
        assert config.total_health == pytest.approx(6000)
        assert len(config.enemies) == 3

    def test_total_health_sum(self):
        enemies = [
            EnemyModel("e1", max_health=500, armor=0),
            EnemyModel("e2", max_health=1500, armor=0),
        ]
        config = EnemyDataIntegration().build_encounter(enemies)
        assert config.total_health == pytest.approx(2000)

    def test_max_armor_detected(self):
        enemies = [
            EnemyModel("e1", max_health=1000, armor=100),
            EnemyModel("e2", max_health=1000, armor=500),
        ]
        config = EnemyDataIntegration().build_encounter(enemies)
        assert config.max_armor == 500


class TestEncounterValidation:
    def test_empty_encounter_raises(self):
        with pytest.raises(EnemyValidationError, match="at least one"):
            EnemyDataIntegration().build_encounter([])

    def test_too_many_enemies_raises(self):
        enemies = [EnemyModel(f"e{i}", 100, armor=0) for i in range(51)]
        with pytest.raises(EnemyValidationError, match="maximum"):
            EnemyDataIntegration().build_encounter(enemies)

    def test_scale_encounter_doubles_health(self):
        integ = EnemyDataIntegration()
        config = integ.build_encounter(make_enemies(2))
        scaled = integ.scale_encounter(config, multiplier=2.0)
        assert scaled.total_health == pytest.approx(config.total_health * 2)
