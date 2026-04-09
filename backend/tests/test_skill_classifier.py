"""
Tests for skill classification and primary skill detection.
"""

import pytest

from app.skills.skill_classifier import (
    classify_skill,
    classify_skills,
    detect_primary_skill,
)


# ---------------------------------------------------------------------------
# classify_skill
# ---------------------------------------------------------------------------

class TestClassifySkill:
    def test_shift_is_utility(self):
        assert classify_skill("Shift") == "utility"

    def test_lunge_is_utility(self):
        assert classify_skill("Lunge") == "utility"

    def test_teleport_is_utility(self):
        assert classify_skill("Teleport") == "utility"

    def test_holy_aura_is_utility(self):
        assert classify_skill("Holy Aura") == "utility"

    def test_smoke_bomb_is_utility(self):
        assert classify_skill("Smoke Bomb") == "utility"

    def test_flame_ward_is_utility(self):
        assert classify_skill("Flame Ward") == "utility"

    def test_umbral_blades_is_damage(self):
        assert classify_skill("Umbral Blades") == "damage"

    def test_hammer_throw_is_damage(self):
        assert classify_skill("Hammer Throw") == "damage"

    def test_fireball_is_damage(self):
        assert classify_skill("Fireball") == "damage"

    def test_shadow_cascade_is_damage(self):
        assert classify_skill("Shadow Cascade") == "damage"

    def test_summon_scorpion_is_minion(self):
        assert classify_skill("Summon Scorpion") == "minion"

    def test_summon_bear_is_minion(self):
        assert classify_skill("Summon Bear") == "minion"

    def test_manifest_armor_is_minion(self):
        assert classify_skill("Manifest Armor") == "minion"

    def test_thorn_totem_is_minion(self):
        assert classify_skill("Thorn Totem") == "minion"

    def test_unknown_skill_is_damage(self):
        assert classify_skill("Unknown Future Skill") == "damage"


class TestClassifySkills:
    def test_batch_classification(self):
        result = classify_skills(["Shift", "Umbral Blades", "Summon Bear"])
        assert result == {
            "Shift": "utility",
            "Umbral Blades": "damage",
            "Summon Bear": "minion",
        }


# ---------------------------------------------------------------------------
# detect_primary_skill
# ---------------------------------------------------------------------------

class TestDetectPrimarySkill:
    def test_rogue_build_selects_highest_allocated(self):
        """Umbral Blades (18 nodes) should be primary over Shurikens (12)."""
        skills = [
            {"skill_name": "Shift", "slot": 0, "allocated_nodes": 0},
            {"skill_name": "Umbral Blades", "slot": 1, "allocated_nodes": 18},
            {"skill_name": "Shurikens", "slot": 2, "allocated_nodes": 12},
        ]
        assert detect_primary_skill(skills) == "Umbral Blades"

    def test_all_utility_falls_back_to_slot_0(self):
        """When all skills are utility, fall back to first slot."""
        skills = [
            {"skill_name": "Shift", "slot": 0, "allocated_nodes": 5},
            {"skill_name": "Lunge", "slot": 1, "allocated_nodes": 3},
            {"skill_name": "Smoke Bomb", "slot": 2, "allocated_nodes": 10},
        ]
        assert detect_primary_skill(skills) == "Shift"

    def test_tiebreak_prefers_lower_slot(self):
        """Equal nodes → lower slot number wins."""
        skills = [
            {"skill_name": "Shift", "slot": 0, "allocated_nodes": 0},
            {"skill_name": "Fireball", "slot": 1, "allocated_nodes": 15},
            {"skill_name": "Lightning Blast", "slot": 2, "allocated_nodes": 15},
        ]
        assert detect_primary_skill(skills) == "Fireball"

    def test_empty_skill_list_returns_none(self):
        assert detect_primary_skill([]) is None

    def test_single_damage_skill_with_zero_nodes(self):
        """A single damage skill is still primary even with 0 allocated nodes."""
        skills = [
            {"skill_name": "Shift", "slot": 0, "allocated_nodes": 0},
            {"skill_name": "Fireball", "slot": 1, "allocated_nodes": 0},
        ]
        assert detect_primary_skill(skills) == "Fireball"

    def test_minion_skills_excluded_from_primary(self):
        """Minion skills should not be selected as primary."""
        skills = [
            {"skill_name": "Summon Bear", "slot": 0, "allocated_nodes": 20},
            {"skill_name": "Swipe", "slot": 1, "allocated_nodes": 5},
        ]
        assert detect_primary_skill(skills) == "Swipe"

    def test_mixed_build_selects_damage(self):
        """Full 5-skill build with mix of types → highest damage skill."""
        skills = [
            {"skill_name": "Shift", "slot": 0, "allocated_nodes": 0},
            {"skill_name": "Umbral Blades", "slot": 1, "allocated_nodes": 18},
            {"skill_name": "Shadow Cascade", "slot": 2, "allocated_nodes": 15},
            {"skill_name": "Smoke Bomb", "slot": 3, "allocated_nodes": 8},
            {"skill_name": "Synchronized Strike", "slot": 4, "allocated_nodes": 10},
        ]
        assert detect_primary_skill(skills) == "Umbral Blades"
