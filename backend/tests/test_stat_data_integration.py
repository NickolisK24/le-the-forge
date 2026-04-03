"""J11 — Tests for stat_data_integration.py"""

import pytest
from data.models.skill_model import SkillModel
from data.models.enemy_model import EnemyModel
from stats.stat_data_integration import StatDataIntegration, StatInjectionResult
from state.state_engine import SimulationState


def make_state():
    return SimulationState(
        player_health=1000,
        player_max_health=1000,
        target_health=5000,
        target_max_health=5000,
    )


class TestStatInjectionCorrectness:
    def test_inject_writes_to_stat_cache(self):
        skill = SkillModel("fireball", base_damage=200, cooldown=1.0, mana_cost=10)
        enemy = EnemyModel("goblin", max_health=1000, armor=0)
        state = make_state()
        # Ensure stat_cache exists
        state.stat_cache = {}
        integration = StatDataIntegration(skill, enemy)
        result = integration.inject(state)
        assert state.stat_cache["base_damage"] == 200
        assert state.stat_cache["enemy_armor"] == 0

    def test_zero_armor_full_damage(self):
        skill = SkillModel("x", base_damage=100, cooldown=0, mana_cost=0)
        enemy = EnemyModel("dummy", max_health=100, armor=0)
        state = make_state()
        state.stat_cache = {}
        result = StatDataIntegration(skill, enemy).inject(state)
        assert result.effective_damage == pytest.approx(100.0)

    def test_high_armor_reduces_damage(self):
        skill = SkillModel("x", base_damage=1000, cooldown=0, mana_cost=0)
        enemy = EnemyModel("tanky", max_health=1000, armor=300)
        state = make_state()
        state.stat_cache = {}
        result = StatDataIntegration(skill, enemy).inject(state)
        # armor/(armor+300) = 0.5 → effective = 500
        assert result.effective_damage == pytest.approx(500.0)


class TestScalingValidation:
    def test_scale_with_level_increases_damage(self):
        skill = SkillModel("x", base_damage=100, cooldown=0, mana_cost=0)
        enemy = EnemyModel("dummy", max_health=100, armor=0)
        state = make_state()
        state.stat_cache = {}
        result = StatDataIntegration(skill, enemy).scale_with_level(state, level=50)
        assert result.effective_damage > 100
