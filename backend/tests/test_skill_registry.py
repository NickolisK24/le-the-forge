"""J4 — Tests for skill_registry.py"""

import pytest
from data.models.skill_model import SkillModel
from data.registries.skill_registry import SkillRegistry


def make_registry():
    skills = [
        SkillModel("fireball", 100, 1.5, 20),
        SkillModel("ice_bolt", 80, 1.0, 15),
        SkillModel("smite", 120, 2.0, 25),
    ]
    return SkillRegistry(skills)


class TestSkillRetrieval:
    def test_get_existing_skill(self):
        reg = make_registry()
        s = reg.get("fireball")
        assert s is not None
        assert s.skill_id == "fireball"

    def test_get_returns_none_for_missing(self):
        reg = make_registry()
        assert reg.get("unknown_skill") is None

    def test_get_or_raise_raises_for_missing(self):
        reg = make_registry()
        with pytest.raises(KeyError, match="unknown"):
            reg.get_or_raise("unknown")


class TestInvalidIDHandling:
    def test_ids_returns_all_ids(self):
        reg = make_registry()
        ids = reg.ids()
        assert "fireball" in ids
        assert "ice_bolt" in ids
        assert len(ids) == 3

    def test_count(self):
        reg = make_registry()
        assert reg.count() == 3
        assert len(reg) == 3

    def test_all_returns_list(self):
        reg = make_registry()
        all_skills = reg.all()
        assert len(all_skills) == 3
