"""J12 — Tests for skill_data_integration.py"""

import pytest
from data.models.skill_model import SkillModel
from data.registries.skill_registry import SkillRegistry
from services.skill_data_integration import SkillDataIntegration


def make_integration():
    skills = [
        SkillModel("fireball", 100, cooldown=2.0, mana_cost=20),
        SkillModel("ice_bolt",  80, cooldown=1.0, mana_cost=15),
        SkillModel("smite",    120, cooldown=0.5, mana_cost=10),
    ]
    registry = SkillRegistry(skills)
    return SkillDataIntegration(registry)


class TestSkillUsageCorrectness:
    def test_use_skill_returns_correct_damage(self):
        integ = make_integration()
        result = integ.use_skill("fireball", current_time=0.0)
        assert result.damage_dealt == pytest.approx(100.0)
        assert result.mana_spent == 20.0

    def test_damage_multiplier_applied(self):
        integ = make_integration()
        result = integ.use_skill("fireball", current_time=0.0, damage_multiplier=1.5)
        assert result.damage_dealt == pytest.approx(150.0)

    def test_unknown_skill_raises(self):
        integ = make_integration()
        with pytest.raises(KeyError):
            integ.use_skill("unknown", current_time=0.0)


class TestCooldownAlignment:
    def test_cooldown_end_recorded(self):
        integ = make_integration()
        result = integ.use_skill("fireball", current_time=5.0)
        assert result.on_cooldown_until == pytest.approx(7.0)  # 5 + 2

    def test_on_cooldown_true_before_end(self):
        integ = make_integration()
        integ.use_skill("fireball", current_time=0.0)
        assert integ.is_on_cooldown("fireball", current_time=1.0) is True

    def test_on_cooldown_false_after_end(self):
        integ = make_integration()
        integ.use_skill("fireball", current_time=0.0)
        assert integ.is_on_cooldown("fireball", current_time=3.0) is False

    def test_simulate_rotation_respects_cooldowns(self):
        integ = make_integration()
        results = integ.simulate_rotation(["fireball", "fireball"], start_time=0.0, gap=0.5)
        # Second fireball must wait until cooldown expires (t=2.0)
        assert results[1].time_used >= 2.0
