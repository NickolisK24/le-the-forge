"""
G11 — Rotation Encounter Integration tests

These tests require the Flask app context (for encounter engine),
so they use the `client` fixture from conftest.
"""
import pytest
from rotation.models.rotation_definition import RotationDefinition
from rotation.models.rotation_step import RotationStep
from skills.models.skill_definition import SkillDefinition
from services.rotation_integration import simulate_rotation_encounter


def _skill(sid, base_damage=100.0, cast_time=0.0, cooldown=1.0):
    return SkillDefinition(skill_id=sid, base_damage=base_damage,
                           cast_time=cast_time, cooldown=cooldown)


def _rotation(*skill_ids):
    steps = [RotationStep(skill_id=s) for s in skill_ids]
    return RotationDefinition(rotation_id="r", steps=steps)


_ENC = {
    "enemy_template": "TRAINING_DUMMY",
    "fight_duration": 5.0,
    "tick_size": 0.5,
    "distribution": "SINGLE",
    "crit_chance": 0.0,
    "crit_multiplier": 2.0,
}


class TestRotationDrivenEncounters:
    def test_empty_rotation_zero_damage(self, client):
        rot = RotationDefinition(rotation_id="r")
        result = simulate_rotation_encounter(rot, {}, duration=5.0,
                                             encounter_kwargs=_ENC)
        assert result.total_damage == 0.0
        assert result.total_casts == 0

    def test_single_skill_produces_damage(self, client):
        reg = {"a": _skill("a", base_damage=100.0, cooldown=1.0)}
        result = simulate_rotation_encounter(_rotation("a"), reg, duration=3.0,
                                             encounter_kwargs=_ENC)
        assert result.total_damage > 0.0
        assert result.total_casts > 0

    def test_total_casts_matches_cast_detail(self, client):
        reg = {"a": _skill("a", cooldown=1.0)}
        result = simulate_rotation_encounter(_rotation("a"), reg, duration=3.0,
                                             encounter_kwargs=_ENC)
        assert len(result.cast_results) == result.total_casts

    def test_dps_is_damage_over_duration(self, client):
        reg = {"a": _skill("a", cooldown=1.0)}
        result = simulate_rotation_encounter(_rotation("a"), reg, duration=3.0,
                                             encounter_kwargs=_ENC)
        expected_dps = result.total_damage / 3.0
        assert abs(result.dps - expected_dps) < 0.01

    def test_cast_results_have_expected_keys(self, client):
        reg = {"a": _skill("a", cooldown=1.0)}
        result = simulate_rotation_encounter(_rotation("a"), reg, duration=3.0,
                                             encounter_kwargs=_ENC)
        if result.cast_results:
            c = result.cast_results[0]
            for key in ("skill_id", "cast_at", "resolves_at", "damage"):
                assert key in c

    def test_rotation_metrics_present(self, client):
        reg = {"a": _skill("a", cooldown=1.0)}
        result = simulate_rotation_encounter(_rotation("a"), reg, duration=3.0,
                                             encounter_kwargs=_ENC)
        assert result.rotation_metrics is not None
        assert result.rotation_metrics.total_casts == result.total_casts


class TestMultiSkillDamageValidation:
    def test_two_skills_both_contribute(self, client):
        reg = {
            "a": _skill("a", base_damage=100.0, cooldown=2.0),
            "b": _skill("b", base_damage=200.0, cooldown=2.0),
        }
        result = simulate_rotation_encounter(_rotation("a", "b"), reg, duration=4.0,
                                             encounter_kwargs=_ENC)
        # Both skills should appear in cast results
        skill_ids = {c["skill_id"] for c in result.cast_results}
        assert "a" in skill_ids
        assert "b" in skill_ids

    def test_higher_damage_skill_contributes_more(self, client):
        # "big" has 10x more damage than "small"
        reg = {
            "big":   _skill("big",   base_damage=1000.0, cooldown=2.0),
            "small": _skill("small", base_damage=100.0,  cooldown=2.0),
        }
        result = simulate_rotation_encounter(_rotation("big", "small"), reg, duration=4.0,
                                             encounter_kwargs=_ENC)
        by_skill = {c["skill_id"]: c["damage"] for c in result.cast_results}
        if "big" in by_skill and "small" in by_skill:
            assert by_skill["big"] > by_skill["small"]
