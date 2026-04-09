"""
Tests for skill data coverage — every skill in the game must have valid data
in both skills.json and SKILL_STATS.
"""

import json
import os
import re
import pytest

from app.engines.combat_engine import _get_skill_def, SKILL_STATS


# Load the authoritative skill list from skills_with_trees.json
_SWT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "classes", "skills_with_trees.json"
)
_SJ_PATH = os.path.join(
    os.path.dirname(__file__), "..", "app", "game_data", "skills.json"
)


def _game_skill_names() -> list[str]:
    with open(_SWT_PATH) as f:
        data = json.load(f)
    return sorted({e["name"] for e in data if isinstance(e, dict) and e.get("name")})


def _skills_json_names() -> set[str]:
    with open(_SJ_PATH) as f:
        return set(json.load(f)["skills"].keys())


def _skill_stats_names() -> set[str]:
    return set(SKILL_STATS.keys())


GAME_SKILLS = _game_skill_names()
SJ_NAMES = _skills_json_names()
SS_NAMES = _skill_stats_names()


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

class TestSkillCoverage:
    @pytest.mark.parametrize("skill_name", GAME_SKILLS)
    def test_get_skill_def_returns_valid(self, skill_name):
        """Every game skill must return a non-None SkillStatDef."""
        sd = _get_skill_def(skill_name)
        assert sd is not None, f"_get_skill_def({skill_name!r}) returned None"

    def test_skills_json_covers_all_game_skills(self):
        """Every skill in skills_with_trees.json has an entry in skills.json."""
        missing = set(GAME_SKILLS) - SJ_NAMES
        assert missing == set(), f"Missing from skills.json: {sorted(missing)}"

    def test_skill_stats_covers_skills_json(self):
        """Every skill in skills.json has an entry in SKILL_STATS."""
        missing = SJ_NAMES - SS_NAMES
        assert missing == set(), f"In skills.json but not SKILL_STATS: {sorted(missing)}"

    def test_no_orphaned_skill_stats(self):
        """No SKILL_STATS entries without a skills.json entry."""
        orphaned = SS_NAMES - SJ_NAMES
        assert orphaned == set(), f"In SKILL_STATS but not skills.json: {sorted(orphaned)}"


# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------

class TestSkillDataQuality:
    @pytest.mark.parametrize("skill_name", GAME_SKILLS)
    def test_every_skill_has_attack_speed(self, skill_name):
        sd = _get_skill_def(skill_name)
        if sd is not None:
            assert sd.attack_speed > 0, f"{skill_name} has attack_speed={sd.attack_speed}"

    def test_damage_skills_have_positive_base(self):
        """Skills with damage tags should have base_damage > 0."""
        damage_skills = []
        with open(_SWT_PATH) as f:
            swt = json.load(f)
        dmg_tags = {"Physical", "Fire", "Cold", "Lightning", "Necrotic", "Void", "Poison", "Melee", "Bow", "Throwing"}
        for entry in swt:
            if isinstance(entry, dict) and entry.get("name"):
                tags = set(entry.get("tagsDecoded", []))
                if tags & dmg_tags and "Buff" not in tags and "Minion" not in tags:
                    if not entry.get("traversalSkill") and not entry.get("isTransform"):
                        damage_skills.append(entry["name"])

        for name in damage_skills:
            sd = _get_skill_def(name)
            if sd is not None:
                assert sd.base_damage > 0, f"{name} is a damage skill but has base_damage={sd.base_damage}"
