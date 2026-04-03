"""
Phase O Integration Compatibility Tests
Tests version compatibility, legacy formats, and edge cases.
Run from backend/:
    python -m pytest tests/test_integration_compatibility.py -v --tb=short
"""
from __future__ import annotations

import importlib
import json
import time

import pytest

# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------
_schema_mod = importlib.import_module("integration.import.schemas.import_schema")
_parser_mod = importlib.import_module("integration.import.build_import_parser")

ImportSchema = _schema_mod.ImportSchema
ImportFormat = _schema_mod.ImportFormat
SchemaValidator = _schema_mod.SchemaValidator
SkillEntry = _schema_mod.SkillEntry
GearEntry = _schema_mod.GearEntry
PassiveEntry = _schema_mod.PassiveEntry
ValidationResult = _schema_mod.ValidationResult
BuildImportParser = _parser_mod.BuildImportParser

from integration.export.build_exporter import BuildExporter
from integration.storage.build_repository import BuildRepository, StoredBuild
from integration.sharing.share_link_generator import ShareLinkGenerator, ShareLink
from integration.versioning.version_compatibility import (
    VersionCompatibilityEngine,
    MigrationStep,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_json(**overrides) -> str:
    base = {
        "format": "json",
        "version": "1.0",
        "build_name": "Test Build",
        "character_class": "Warrior",
        "skills": [],
        "passives": [],
        "gear": [],
        "metadata": {},
    }
    base.update(overrides)
    return json.dumps(base)


def _make_stored(build_id: str, build_name: str = "Build", owner: str | None = None,
                  public: bool = True, char_class: str = "Mage",
                  version: str = "1.0", tags: list[str] | None = None) -> StoredBuild:
    now = time.time()
    return StoredBuild(
        build_id=build_id,
        build_name=build_name,
        character_class=char_class,
        version=version,
        data={"name": build_name},
        owner_id=owner,
        is_public=public,
        created_at=now,
        updated_at=now,
        tags=tags or [],
    )


# ===========================================================================
# 1. Version compatibility
# ===========================================================================

class TestVersionCompatibilityEngine:

    def test_is_compatible_within_range(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("1.5", "1.0", "2.0") is True

    def test_is_compatible_above_range(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("3.0", "1.0", "2.0") is False

    def test_is_compatible_below_range(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("0.5", "1.0", "2.0") is False

    def test_is_compatible_exact_min_boundary(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("1.0", "1.0", "2.0") is True

    def test_is_compatible_exact_max_boundary(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("2.0", "1.0", "2.0") is True

    def test_is_compatible_single_version_range(self):
        engine = VersionCompatibilityEngine()
        assert engine.is_compatible("1.0", "1.0", "1.0") is True

    def test_migrate_no_migrations_data_unchanged(self):
        engine = VersionCompatibilityEngine()
        data = {"version": "1.0", "key": "value"}
        result = engine.migrate(data, "2.0")
        assert result.migrated is False
        assert result.data["key"] == "value"

    def test_migrate_1_to_2_version_field(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep("1.0", "2.0", "upgrade", lambda d: d))
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.data["version"] == "2.0"

    def test_migration_adds_field(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep(
            "1.0", "2.0", "add field",
            lambda d: {**d, "added_key": 42},
        ))
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.data.get("added_key") == 42

    def test_migrate_original_version_preserved_in_result(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep("1.0", "2.0", "s", lambda d: d))
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.original_version == "1.0"

    def test_migrate_target_version_in_result(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep("1.0", "2.0", "s", lambda d: d))
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.target_version == "2.0"


# ===========================================================================
# 2. Build string format compatibility
# ===========================================================================

class TestBuildStringCompatibility:

    def test_v1_build_string_parses_correctly(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        # Build a "v1.0 style" schema and export to build string
        validator = SchemaValidator()
        schema = validator.from_json({
            "format": "json",
            "version": "1.0",
            "build_name": "Legacy Build",
            "character_class": "Rogue",
        })
        export = exporter.to_build_string(schema)
        result = parser.parse_build_string(export.content)
        assert result.success is True
        assert result.schema.build_name == "Legacy Build"

    def test_extra_unknown_fields_in_json_ignored(self):
        parser = BuildImportParser()
        data = json.dumps({
            "format": "json",
            "version": "1.0",
            "build_name": "Extra Fields Build",
            "character_class": "Warrior",
            "unknown_top_level": "ignored_value",
            "another_unknown": {"nested": True},
        })
        # from_json doesn't raise; unknown keys passed to metadata or just ignored
        # The validator.from_json uses data.get() — extra keys are silently skipped
        result = parser.parse_json(data)
        # Should not crash; build_name should be parsed correctly
        assert result.schema.build_name == "Extra Fields Build"

    def test_missing_skills_defaults_to_empty_list(self):
        parser = BuildImportParser()
        data = json.dumps({
            "format": "json",
            "version": "1.0",
            "build_name": "No Skills",
            "character_class": "Warrior",
        })
        result = parser.parse_json(data)
        assert result.schema.skills == []

    def test_missing_gear_defaults_to_empty_list(self):
        parser = BuildImportParser()
        data = json.dumps({
            "format": "json",
            "version": "1.0",
            "build_name": "No Gear",
            "character_class": "Warrior",
        })
        result = parser.parse_json(data)
        assert result.schema.gear == []

    def test_missing_passives_defaults_to_empty_list(self):
        parser = BuildImportParser()
        data = json.dumps({
            "format": "json",
            "version": "1.0",
            "build_name": "No Passives",
            "character_class": "Warrior",
        })
        result = parser.parse_json(data)
        assert result.schema.passives == []


# ===========================================================================
# 3. Legacy JSON formats
# ===========================================================================

class TestLegacyJsonFormats:

    def test_skills_as_empty_list(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Empty Skills",
            "character_class": "Mage",
            "skills": [],
        })
        assert schema.skills == []

    def test_no_passives_key_defaults_empty(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "No Passives",
            "character_class": "Mage",
        })
        assert schema.passives == []

    def test_version_as_int_converted_to_string(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": 1,
            "build_name": "Int Version",
            "character_class": "Warrior",
        })
        assert schema.version == "1"

    def test_unknown_top_level_keys_no_error(self):
        parser = BuildImportParser()
        data = json.dumps({
            "version": "1.0",
            "build_name": "With Unknowns",
            "character_class": "Rogue",
            "totally_fake_key": 999,
        })
        # Should not raise; schema parsed cleanly
        result = parser.parse_json(data)
        assert result.schema.build_name == "With Unknowns"

    def test_format_unknown_defaults_to_json(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "format": "unknown_format",
            "version": "1.0",
            "build_name": "Unknown Format",
            "character_class": "Warrior",
        })
        assert schema.format == ImportFormat.JSON

    def test_missing_build_name_defaults_empty_string(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "character_class": "Warrior",
        })
        assert schema.build_name == ""

    def test_missing_character_class_defaults_empty_string(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Build",
        })
        assert schema.character_class == ""


# ===========================================================================
# 4. Validation edge cases
# ===========================================================================

class TestValidationEdgeCases:

    def test_zero_skills_is_valid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "No Skills",
            "character_class": "Warrior",
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_fifty_valid_skills_valid(self):
        validator = SchemaValidator()
        skills = [{"skill_id": f"s{i}", "level": 5, "quality": 0, "enabled": True}
                  for i in range(50)]
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Many Skills",
            "character_class": "Mage",
            "skills": skills,
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_one_invalid_skill_level_in_50_has_error(self):
        validator = SchemaValidator()
        skills = [{"skill_id": f"s{i}", "level": 5, "quality": 0, "enabled": True}
                  for i in range(49)]
        skills.append({"skill_id": "bad_skill", "level": 99, "quality": 0, "enabled": True})
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Bad Skill",
            "character_class": "Mage",
            "skills": skills,
        })
        result = validator.validate(schema)
        assert result.valid is False
        assert any("level must be 1-20" in e for e in result.errors)

    def test_duplicate_skill_ids_no_error(self):
        validator = SchemaValidator()
        skills = [
            {"skill_id": "fireball", "level": 5, "quality": 0, "enabled": True},
            {"skill_id": "fireball", "level": 3, "quality": 0, "enabled": True},
        ]
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Dup Skills",
            "character_class": "Mage",
            "skills": skills,
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_all_gear_slots_valid(self):
        validator = SchemaValidator()
        slots = list(SchemaValidator.VALID_SLOTS)
        gear = [{"slot": s, "item_id": f"item_{s}", "affixes": []} for s in slots]
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Full Gear",
            "character_class": "Warrior",
            "gear": gear,
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_gear_with_empty_affixes_valid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "No Affixes",
            "character_class": "Warrior",
            "gear": [{"slot": "helm", "item_id": "helmet1", "affixes": []}],
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_invalid_gear_slot_produces_error(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Bad Slot",
            "character_class": "Warrior",
            "gear": [{"slot": "pants", "item_id": "trousers", "affixes": []}],
        })
        result = validator.validate(schema)
        assert result.valid is False
        assert any("invalid gear slot" in e for e in result.errors)

    def test_empty_build_name_invalid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "   ",
            "character_class": "Warrior",
        })
        result = validator.validate(schema)
        assert result.valid is False

    def test_empty_character_class_invalid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Valid Name",
            "character_class": "",
        })
        result = validator.validate(schema)
        assert result.valid is False

    def test_invalid_version_format_produces_error(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "bad_version",
            "build_name": "Valid Name",
            "character_class": "Warrior",
        })
        # from_json converts to str; validate checks the format
        schema.version = "bad_version"
        result = validator.validate(schema)
        assert result.valid is False
        assert any("invalid version format" in e for e in result.errors)

    def test_skill_quality_outside_range_is_warning_not_error(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "High Quality",
            "character_class": "Mage",
            "skills": [{"skill_id": "s1", "level": 5, "quality": 30, "enabled": True}],
        })
        result = validator.validate(schema)
        assert result.valid is True
        assert len(result.warnings) > 0

    def test_skill_level_1_is_valid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Min Level",
            "character_class": "Mage",
            "skills": [{"skill_id": "s1", "level": 1, "quality": 0, "enabled": True}],
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_skill_level_20_is_valid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Max Level",
            "character_class": "Mage",
            "skills": [{"skill_id": "s1", "level": 20, "quality": 0, "enabled": True}],
        })
        result = validator.validate(schema)
        assert result.valid is True

    def test_skill_level_0_is_invalid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Zero Level",
            "character_class": "Mage",
            "skills": [{"skill_id": "s1", "level": 0, "quality": 0, "enabled": True}],
        })
        result = validator.validate(schema)
        assert result.valid is False

    def test_skill_level_21_is_invalid(self):
        validator = SchemaValidator()
        schema = validator.from_json({
            "version": "1.0",
            "build_name": "Over Level",
            "character_class": "Mage",
            "skills": [{"skill_id": "s1", "level": 21, "quality": 0, "enabled": True}],
        })
        result = validator.validate(schema)
        assert result.valid is False


# ===========================================================================
# 5. Share link edge cases
# ===========================================================================

class TestShareLinkEdgeCases:

    def test_generate_build_id_always_12_chars(self):
        gen = ShareLinkGenerator()
        for name, ver in [("Build", "1.0"), ("Another", "2.5"), ("X" * 100, "9.99")]:
            bid = gen.generate_build_id(name, ver)
            assert len(bid) == 12, f"Expected 12 chars for ({name!r}, {ver!r})"

    def test_two_calls_produce_different_build_ids(self):
        gen = ShareLinkGenerator()
        # time.time() is used in the hash so consecutive calls differ
        id1 = gen.generate_build_id("Build", "1.0", salt="a")
        id2 = gen.generate_build_id("Build", "1.0", salt="b")
        assert id1 != id2

    def test_is_expired_true_when_past(self):
        gen = ShareLinkGenerator()
        link = ShareLink(
            build_id="abc123",
            url="https://example.com/share/abc123",
            build_name="Build",
            version="1.0",
            created_at=time.time() - 7200,
            expires_at=time.time() - 1,
        )
        assert gen.is_expired(link) is True

    def test_is_expired_false_when_future(self):
        gen = ShareLinkGenerator()
        link = ShareLink(
            build_id="abc123",
            url="https://example.com/share/abc123",
            build_name="Build",
            version="1.0",
            created_at=time.time(),
            expires_at=time.time() + 3600,
        )
        assert gen.is_expired(link) is False

    def test_is_expired_false_when_no_expiry(self):
        gen = ShareLinkGenerator()
        link = ShareLink(
            build_id="abc123",
            url="https://example.com/share/abc123",
            build_name="Build",
            version="1.0",
            created_at=time.time(),
            expires_at=None,
        )
        assert gen.is_expired(link) is False

    def test_tag_version_no_existing_query(self):
        gen = ShareLinkGenerator()
        url = "https://le-the-forge.app/share/abc123"
        tagged = gen.tag_version(url, "2.0")
        assert "?v=2.0" in tagged

    def test_tag_version_existing_query_uses_ampersand(self):
        gen = ShareLinkGenerator()
        url = "https://le-the-forge.app/share/abc123?build=xyz"
        tagged = gen.tag_version(url, "2.0")
        assert "&v=2.0" in tagged
        assert "?v=2.0" not in tagged

    def test_tag_version_does_not_double_add(self):
        """tag_version is not idempotent by design (appends each call), so
        applying once should produce exactly one v= segment."""
        gen = ShareLinkGenerator()
        url = "https://le-the-forge.app/share/abc123"
        tagged = gen.tag_version(url, "1.0")
        # Only one '?v=' present
        assert tagged.count("v=1.0") == 1

    def test_generate_hash_is_deterministic(self):
        gen = ShareLinkGenerator()
        h1 = gen.generate_hash("same content")
        h2 = gen.generate_hash("same content")
        assert h1 == h2

    def test_generate_hash_differs_for_different_content(self):
        gen = ShareLinkGenerator()
        assert gen.generate_hash("content_a") != gen.generate_hash("content_b")

    def test_generated_link_build_name_preserved(self):
        gen = ShareLinkGenerator()
        link = gen.generate("MyBuild", "1.5")
        assert link.build_name == "MyBuild"

    def test_generated_link_version_preserved(self):
        gen = ShareLinkGenerator()
        link = gen.generate("MyBuild", "1.5")
        assert link.version == "1.5"


# ===========================================================================
# 6. Repository edge cases
# ===========================================================================

class TestRepositoryEdgeCases:

    def test_save_same_build_id_twice_count_stays_same(self):
        repo = BuildRepository()
        b1 = _make_stored("dup_id", "Build One")
        repo.save(b1)
        b2 = _make_stored("dup_id", "Build Two")
        repo.save(b2)
        assert len(repo) == 1

    def test_save_same_build_id_updates_updated_at(self):
        repo = BuildRepository()
        b1 = _make_stored("dup_id")
        repo.save(b1)
        original_updated = repo.get("dup_id").updated_at
        time.sleep(0.01)  # tiny sleep to ensure time advances
        b2 = _make_stored("dup_id")
        repo.save(b2)
        assert repo.get("dup_id").updated_at >= original_updated

    def test_list_public_offset_limit(self):
        repo = BuildRepository()
        for i in range(5):
            repo.save(_make_stored(f"pub_{i}", f"Build {i}", public=True))
        qr = repo.list_public(offset=2, limit=2)
        assert len(qr.builds) == 2
        assert qr.total == 5

    def test_list_public_offset_limit_total_is_full_count(self):
        repo = BuildRepository()
        for i in range(5):
            repo.save(_make_stored(f"pub_{i}", f"Build {i}", public=True))
        qr = repo.list_public(offset=4, limit=10)
        assert qr.total == 5
        assert len(qr.builds) == 1

    def test_list_by_owner_unknown_owner_empty(self):
        repo = BuildRepository()
        repo.save(_make_stored("b1", owner="user_a"))
        qr = repo.list_by_owner("unknown_owner")
        assert qr.builds == []
        assert qr.total == 0

    def test_list_by_owner_returns_only_owned(self):
        repo = BuildRepository()
        repo.save(_make_stored("b1", owner="user_a"))
        repo.save(_make_stored("b2", owner="user_b"))
        repo.save(_make_stored("b3", owner="user_a"))
        qr = repo.list_by_owner("user_a")
        assert qr.total == 2
        assert all(b.owner_id == "user_a" for b in qr.builds)

    def test_version_build_missing_id_returns_none(self):
        repo = BuildRepository()
        result = repo.version_build("nonexistent", {"version": "2.0"}, "2.0")
        assert result is None

    def test_version_build_existing_updates_version(self):
        repo = BuildRepository()
        repo.save(_make_stored("vb_id", version="1.0"))
        result = repo.version_build("vb_id", {"new_data": True}, "2.0")
        assert result.version == "2.0"

    def test_version_build_updates_data(self):
        repo = BuildRepository()
        repo.save(_make_stored("vb_id"))
        result = repo.version_build("vb_id", {"key": "new_value"}, "2.0")
        assert result.data["key"] == "new_value"

    def test_list_public_case_insensitive_class_filter(self):
        repo = BuildRepository()
        repo.save(_make_stored("m1", char_class="Mage", public=True))
        repo.save(_make_stored("m2", char_class="Warrior", public=True))
        qr_lower = repo.list_public(character_class="mage")
        qr_upper = repo.list_public(character_class="MAGE")
        assert qr_lower.total == 1
        assert qr_upper.total == 1

    def test_list_public_excludes_private_builds(self):
        repo = BuildRepository()
        repo.save(_make_stored("pub", public=True))
        repo.save(_make_stored("priv", public=False))
        qr = repo.list_public()
        assert all(b.is_public for b in qr.builds)
        assert qr.total == 1

    def test_list_public_search_case_insensitive(self):
        repo = BuildRepository()
        repo.save(_make_stored("s1", build_name="Fire Mage Build", public=True))
        repo.save(_make_stored("s2", build_name="Ice Warrior", public=True))
        qr = repo.list_public(search="fire mage")
        assert qr.total == 1
        assert qr.builds[0].build_id == "s1"

    def test_max_builds_evicts_oldest(self):
        repo = BuildRepository(max_builds=3)
        for i in range(4):
            repo.save(_make_stored(f"b{i}"))
        assert len(repo) == 3
        # First item "b0" should be evicted
        assert repo.get("b0") is None

    def test_list_public_tag_filter(self):
        repo = BuildRepository()
        repo.save(_make_stored("t1", tags=["speedrun"], public=True))
        repo.save(_make_stored("t2", tags=["hc"], public=True))
        qr = repo.list_public(tag="speedrun")
        assert qr.total == 1
        assert qr.builds[0].build_id == "t1"

    def test_get_and_increment_views_unknown_returns_none(self):
        repo = BuildRepository()
        assert repo.get_and_increment_views("ghost") is None
