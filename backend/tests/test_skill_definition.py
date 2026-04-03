"""
G1 — SkillDefinition tests
"""
import pytest
from skills.models.skill_definition import SkillDefinition


class TestSkillDefinitionCreation:
    def test_minimal(self):
        s = SkillDefinition(skill_id="fireball")
        assert s.skill_id == "fireball"
        assert s.base_damage == 0.0
        assert s.cast_time == 0.0
        assert s.cooldown == 0.0
        assert s.resource_cost == 0.0
        assert s.tags == []

    def test_full(self):
        s = SkillDefinition(
            skill_id="rip_blood",
            base_damage=150.0,
            cast_time=0.5,
            cooldown=2.0,
            resource_cost=30.0,
            tags=["spell", "necrotic"],
        )
        assert s.base_damage == 150.0
        assert s.cast_time == 0.5
        assert s.cooldown == 2.0
        assert s.resource_cost == 30.0
        assert s.tags == ["spell", "necrotic"]

    def test_tags_normalised_to_lowercase(self):
        s = SkillDefinition(skill_id="x", tags=["Spell", "FIRE"])
        assert s.tags == ["spell", "fire"]

    def test_zero_cooldown_allowed(self):
        s = SkillDefinition(skill_id="x", cooldown=0.0)
        assert s.cooldown == 0.0

    def test_zero_cast_time_allowed(self):
        s = SkillDefinition(skill_id="x", cast_time=0.0)
        assert s.cast_time == 0.0


class TestSkillDefinitionValidation:
    def test_empty_skill_id_raises(self):
        with pytest.raises(ValueError, match="skill_id"):
            SkillDefinition(skill_id="")

    def test_negative_cast_time_raises(self):
        with pytest.raises(ValueError, match="cast_time"):
            SkillDefinition(skill_id="x", cast_time=-0.1)

    def test_negative_cooldown_raises(self):
        with pytest.raises(ValueError, match="cooldown"):
            SkillDefinition(skill_id="x", cooldown=-1.0)

    def test_negative_resource_cost_raises(self):
        with pytest.raises(ValueError, match="resource_cost"):
            SkillDefinition(skill_id="x", resource_cost=-5.0)


class TestSkillDefinitionSerialisation:
    def _skill(self):
        return SkillDefinition(
            skill_id="blast",
            base_damage=200.0,
            cast_time=0.8,
            cooldown=4.0,
            resource_cost=50.0,
            tags=["spell", "fire"],
        )

    def test_to_dict_keys(self):
        d = self._skill().to_dict()
        assert set(d.keys()) == {
            "skill_id", "base_damage", "cast_time",
            "cooldown", "resource_cost", "tags",
        }

    def test_roundtrip(self):
        original = self._skill()
        restored = SkillDefinition.from_dict(original.to_dict())
        assert restored.skill_id      == original.skill_id
        assert restored.base_damage   == original.base_damage
        assert restored.cast_time     == original.cast_time
        assert restored.cooldown      == original.cooldown
        assert restored.resource_cost == original.resource_cost
        assert restored.tags          == original.tags

    def test_from_dict_defaults(self):
        s = SkillDefinition.from_dict({"skill_id": "x"})
        assert s.base_damage   == 0.0
        assert s.cast_time     == 0.0
        assert s.cooldown      == 0.0
        assert s.resource_cost == 0.0
        assert s.tags          == []
