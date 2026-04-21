"""
Phase 0 · 0G-1 — Schema tests for skills_metadata.json.

The 0G-1 task adds four fields to every skill entry:
    base_damage_min, base_damage_max, damage_scaling_stat, attack_type

Values stay null until the per-class population tasks (0G-2..0G-6).
These tests lock the contract so that:
  - the data file keeps the new fields present on every skill,
  - the pipeline strips the ``_schema`` meta key before exposing data,
  - populated values that violate the enum/type raise at load time,
  - the ``get_skill_base_damage`` accessor returns the expected shape.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.game_data.game_data_loader import (
    get_all_skills_metadata,
    get_skill_base_damage,
)
from app.game_data.pipeline import GameDataPipeline


_SKILLS_META_PATH = (
    Path(__file__).resolve().parents[2]
    / "data" / "classes" / "skills_metadata.json"
)

_NEW_FIELDS = (
    "base_damage_min",
    "base_damage_max",
    "damage_scaling_stat",
    "attack_type",
)


class TestSkillsMetadataFile:
    def test_every_skill_has_new_fields(self):
        raw = json.loads(_SKILLS_META_PATH.read_text())
        skills = {k: v for k, v in raw.items() if not k.startswith("_")}
        assert skills, "expected at least one skill entry"
        missing = {
            name: [f for f in _NEW_FIELDS if f not in entry]
            for name, entry in skills.items()
            if any(f not in entry for f in _NEW_FIELDS)
        }
        assert not missing, f"skills missing 0G-1 fields: {missing}"

    def test_schema_block_declares_expected_fields(self):
        raw = json.loads(_SKILLS_META_PATH.read_text())
        assert "_schema" in raw, "expected self-describing _schema block"
        fields = raw["_schema"].get("fields", {})
        for f in _NEW_FIELDS:
            assert f in fields, f"_schema.fields missing {f!r}"


class TestPipelineStripsMetaKeys:
    def test_schema_key_is_not_exposed_to_consumers(self):
        meta = get_all_skills_metadata()
        assert "_schema" not in meta
        # Sanity: we still get real skills.
        assert len(meta) > 0


class TestPipelineValidation:
    def _base_skill(self, **overrides) -> dict:
        entry = {
            "id": "t",
            "name": "Test",
            "description": "",
            "lore": "",
            "class": "",
            "base_damage_min": None,
            "base_damage_max": None,
            "damage_scaling_stat": None,
            "attack_type": None,
        }
        entry.update(overrides)
        return entry

    def test_rejects_non_numeric_base_damage_min(self):
        p = GameDataPipeline()
        with pytest.raises(RuntimeError, match="base_damage_min"):
            p._validate_skill_damage_fields(
                "Bad", self._base_skill(base_damage_min="42")
            )

    def test_rejects_min_greater_than_max(self):
        p = GameDataPipeline()
        with pytest.raises(RuntimeError, match="base_damage_min > base_damage_max"):
            p._validate_skill_damage_fields(
                "Bad",
                self._base_skill(base_damage_min=100, base_damage_max=10),
            )

    def test_rejects_unknown_attack_type(self):
        p = GameDataPipeline()
        with pytest.raises(RuntimeError, match="attack_type"):
            p._validate_skill_damage_fields(
                "Bad", self._base_skill(attack_type="lollygag")
            )

    def test_rejects_unknown_scaling_stat(self):
        p = GameDataPipeline()
        with pytest.raises(RuntimeError, match="damage_scaling_stat"):
            p._validate_skill_damage_fields(
                "Bad", self._base_skill(damage_scaling_stat="charisma")
            )

    def test_all_null_fields_are_valid(self):
        p = GameDataPipeline()
        p._validate_skill_damage_fields("Blank", self._base_skill())

    def test_populated_fields_pass_validation(self):
        p = GameDataPipeline()
        p._validate_skill_damage_fields(
            "Ok",
            self._base_skill(
                base_damage_min=10,
                base_damage_max=20,
                damage_scaling_stat="strength",
                attack_type="melee",
            ),
        )


class TestAccessor:
    def test_returns_none_for_unknown_skill(self):
        assert get_skill_base_damage("Definitely Not A Skill 🦑") is None

    def test_returns_none_when_all_fields_null(self):
        # Every real skill currently has null 0G-1 fields (user populates in
        # later tasks); so any live skill key should return None.
        meta = get_all_skills_metadata()
        a_skill = next(iter(meta))
        assert get_skill_base_damage(a_skill) is None

    def test_returns_shape_when_any_field_populated(self, monkeypatch):
        # Surgically overwrite one skill's fields in the live pipeline cache
        # so we exercise the populated-path without mutating on-disk data.
        meta = get_all_skills_metadata()
        target = next(iter(meta))
        original = dict(meta[target])
        meta[target].update({
            "base_damage_min": 50,
            "base_damage_max": 75,
            "damage_scaling_stat": "intelligence",
            "attack_type": "spell",
        })
        try:
            payload = get_skill_base_damage(target)
            assert payload == {
                "base_damage_min": 50,
                "base_damage_max": 75,
                "damage_scaling_stat": "intelligence",
                "attack_type": "spell",
            }
        finally:
            meta[target].clear()
            meta[target].update(original)
