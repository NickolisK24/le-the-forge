"""J3 — Tests for skill_model.py"""

import pytest
from data.models.skill_model import SkillModel


class TestSkillCreation:
    def test_basic_creation(self):
        s = SkillModel(skill_id="fireball", base_damage=100.0, cooldown=1.5, mana_cost=20.0)
        assert s.skill_id == "fireball"
        assert s.base_damage == 100.0
        assert s.cooldown == 1.5
        assert s.mana_cost == 20.0

    def test_tags_normalised_to_tuple(self):
        s = SkillModel("x", 0, 0, 0, tags=["spell", "fire"])
        assert isinstance(s.tags, tuple)
        assert "spell" in s.tags

    def test_immutable(self):
        s = SkillModel("x", 0, 0, 0)
        with pytest.raises((AttributeError, TypeError)):
            s.base_damage = 999


class TestFieldIntegrity:
    def test_empty_skill_id_raises(self):
        with pytest.raises(ValueError, match="skill_id"):
            SkillModel(skill_id="", base_damage=0, cooldown=0, mana_cost=0)

    def test_negative_damage_raises(self):
        with pytest.raises(ValueError, match="base_damage"):
            SkillModel("x", base_damage=-1, cooldown=0, mana_cost=0)

    def test_zero_cooldown_allowed(self):
        s = SkillModel("x", base_damage=10, cooldown=0, mana_cost=0)
        assert s.cooldown == 0


class TestTagValidation:
    def test_has_tag_true(self):
        s = SkillModel("x", 10, 0, 0, tags=("spell", "fire"))
        assert s.has_tag("spell") is True

    def test_has_tag_false(self):
        s = SkillModel("x", 10, 0, 0, tags=("spell",))
        assert s.has_tag("melee") is False

    def test_to_dict(self):
        s = SkillModel("fireball", 100.0, 1.5, 20.0, tags=("fire",))
        d = s.to_dict()
        assert d["skill_id"] == "fireball"
        assert isinstance(d["tags"], list)
