"""
Tests for integration.import.schemas.import_schema

Access the module via importlib because 'integration.import' is a reserved
keyword path in Python.
"""
from __future__ import annotations

import importlib
import json
import pytest

# --- Module-level import via importlib ---
_schema_mod = importlib.import_module("integration.import.schemas.import_schema")
ImportSchema = _schema_mod.ImportSchema
ImportFormat = _schema_mod.ImportFormat
SchemaValidator = _schema_mod.SchemaValidator
SkillEntry = _schema_mod.SkillEntry
GearEntry = _schema_mod.GearEntry
PassiveEntry = _schema_mod.PassiveEntry
ValidationResult = _schema_mod.ValidationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_schema(**kwargs) -> ImportSchema:
    defaults = dict(
        format=ImportFormat.JSON,
        version="1.0",
        build_name="Test Build",
        character_class="Sentinel",
    )
    defaults.update(kwargs)
    return ImportSchema(**defaults)


# ---------------------------------------------------------------------------
# ValidationResult dataclass
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_valid_true_no_errors(self):
        vr = ValidationResult(valid=True)
        assert vr.valid is True
        assert vr.errors == []
        assert vr.warnings == []

    def test_valid_false_with_errors(self):
        vr = ValidationResult(valid=False, errors=["oops"])
        assert not vr.valid
        assert "oops" in vr.errors

    def test_warnings_not_errors(self):
        vr = ValidationResult(valid=True, warnings=["heads up"])
        assert vr.valid
        assert vr.warnings == ["heads up"]
        assert vr.errors == []


# ---------------------------------------------------------------------------
# SchemaValidator.validate — happy path
# ---------------------------------------------------------------------------

class TestSchemaValidatorValidHappyPath:
    def setup_method(self):
        self.v = SchemaValidator()

    def test_valid_schema_passes(self):
        result = self.v.validate(_valid_schema())
        assert result.valid is True
        assert result.errors == []

    def test_valid_schema_with_skills(self):
        schema = _valid_schema(skills=[SkillEntry("fireball", level=5, quality=10)])
        result = self.v.validate(schema)
        assert result.valid is True

    def test_valid_schema_with_gear(self):
        schema = _valid_schema(gear=[GearEntry(slot="helm", item_id="iron_helm")])
        result = self.v.validate(schema)
        assert result.valid is True

    def test_valid_version_formats(self):
        for ver in ("1.0", "2.1", "10.5", "0.0", "99.99"):
            result = self.v.validate(_valid_schema(version=ver))
            version_errors = [e for e in result.errors if "version" in e.lower()]
            assert version_errors == [], f"Unexpected version error for {ver!r}"


# ---------------------------------------------------------------------------
# SchemaValidator.validate — build_name errors
# ---------------------------------------------------------------------------

class TestSchemaValidatorBuildName:
    def setup_method(self):
        self.v = SchemaValidator()

    def test_empty_build_name_is_error(self):
        result = self.v.validate(_valid_schema(build_name=""))
        assert not result.valid
        assert any("build_name" in e for e in result.errors)

    def test_whitespace_only_build_name_is_error(self):
        result = self.v.validate(_valid_schema(build_name="   "))
        assert not result.valid
        assert any("build_name" in e for e in result.errors)

    def test_nonempty_build_name_no_error(self):
        result = self.v.validate(_valid_schema(build_name="My Build"))
        assert not any("build_name" in e for e in result.errors)


# ---------------------------------------------------------------------------
# SchemaValidator.validate — character_class errors
# ---------------------------------------------------------------------------

class TestSchemaValidatorCharacterClass:
    def setup_method(self):
        self.v = SchemaValidator()

    def test_empty_class_is_error(self):
        result = self.v.validate(_valid_schema(character_class=""))
        assert not result.valid
        assert any("character_class" in e for e in result.errors)

    def test_whitespace_only_class_is_error(self):
        result = self.v.validate(_valid_schema(character_class="  "))
        assert not result.valid
        assert any("character_class" in e for e in result.errors)

    def test_valid_class_no_error(self):
        result = self.v.validate(_valid_schema(character_class="Acolyte"))
        assert not any("character_class" in e for e in result.errors)


# ---------------------------------------------------------------------------
# SchemaValidator.validate — version format errors
# ---------------------------------------------------------------------------

class TestSchemaValidatorVersion:
    def setup_method(self):
        self.v = SchemaValidator()

    def _version_errors(self, ver):
        return [e for e in self.v.validate(_valid_schema(version=ver)).errors if "version" in e.lower()]

    def test_version_v1_is_invalid(self):
        assert self._version_errors("v1") != []

    def test_version_bare_1_is_invalid(self):
        assert self._version_errors("1") != []

    def test_version_abc_is_invalid(self):
        assert self._version_errors("abc") != []

    def test_version_dot_only_is_invalid(self):
        assert self._version_errors(".") != []

    def test_version_empty_is_invalid(self):
        assert self._version_errors("") != []

    def test_valid_version_1_0(self):
        assert self._version_errors("1.0") == []

    def test_valid_version_2_1(self):
        assert self._version_errors("2.1") == []

    def test_valid_version_10_5(self):
        assert self._version_errors("10.5") == []


# ---------------------------------------------------------------------------
# SchemaValidator.validate — skill level
# ---------------------------------------------------------------------------

class TestSchemaValidatorSkillLevel:
    def setup_method(self):
        self.v = SchemaValidator()

    def _skill_errors(self, level):
        schema = _valid_schema(skills=[SkillEntry("sk1", level=level)])
        return self.v.validate(schema).errors

    def test_level_0_is_error(self):
        assert self._skill_errors(0) != []

    def test_level_21_is_error(self):
        assert self._skill_errors(21) != []

    def test_level_minus_1_is_error(self):
        assert self._skill_errors(-1) != []

    def test_level_1_ok(self):
        assert self._skill_errors(1) == []

    def test_level_20_ok(self):
        assert self._skill_errors(20) == []

    def test_level_10_ok(self):
        assert self._skill_errors(10) == []


# ---------------------------------------------------------------------------
# SchemaValidator.validate — skill quality (warnings, not errors)
# ---------------------------------------------------------------------------

class TestSchemaValidatorSkillQuality:
    def setup_method(self):
        self.v = SchemaValidator()

    def _quality_result(self, quality):
        schema = _valid_schema(skills=[SkillEntry("sk1", level=5, quality=quality)])
        return self.v.validate(schema)

    def test_quality_minus_1_is_warning_not_error(self):
        result = self._quality_result(-1)
        assert any("quality" in w for w in result.warnings)
        assert not any("quality" in e for e in result.errors)

    def test_quality_21_is_warning_not_error(self):
        result = self._quality_result(21)
        assert any("quality" in w for w in result.warnings)
        assert not any("quality" in e for e in result.errors)

    def test_quality_out_of_range_still_valid(self):
        result = self._quality_result(50)
        # warnings present but schema still valid (no errors from quality alone)
        assert result.valid is True
        assert any("quality" in w for w in result.warnings)

    def test_quality_0_no_warning(self):
        result = self._quality_result(0)
        assert not any("quality" in w for w in result.warnings)

    def test_quality_20_no_warning(self):
        result = self._quality_result(20)
        assert not any("quality" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# SchemaValidator.validate — gear slots
# ---------------------------------------------------------------------------

class TestSchemaValidatorGearSlots:
    def setup_method(self):
        self.v = SchemaValidator()

    def _slot_errors(self, slot):
        schema = _valid_schema(gear=[GearEntry(slot=slot, item_id="x")])
        return self.v.validate(schema).errors

    def test_invalid_slot_is_error(self):
        assert self._slot_errors("shoulders") != []

    def test_invalid_slot_head_is_error(self):
        assert self._slot_errors("head") != []

    def test_valid_slot_helm(self):
        assert self._slot_errors("helm") == []

    def test_valid_slot_chest(self):
        assert self._slot_errors("chest") == []

    def test_valid_slot_gloves(self):
        assert self._slot_errors("gloves") == []

    def test_valid_slot_boots(self):
        assert self._slot_errors("boots") == []

    def test_valid_slot_belt(self):
        assert self._slot_errors("belt") == []

    def test_valid_slot_ring1(self):
        assert self._slot_errors("ring1") == []

    def test_valid_slot_ring2(self):
        assert self._slot_errors("ring2") == []

    def test_valid_slot_amulet(self):
        assert self._slot_errors("amulet") == []

    def test_valid_slot_weapon1(self):
        assert self._slot_errors("weapon1") == []

    def test_valid_slot_weapon2(self):
        assert self._slot_errors("weapon2") == []

    def test_valid_slot_offhand(self):
        assert self._slot_errors("offhand") == []


# ---------------------------------------------------------------------------
# SchemaValidator.validate — multiple errors accumulate
# ---------------------------------------------------------------------------

class TestSchemaValidatorMultipleErrors:
    def setup_method(self):
        self.v = SchemaValidator()

    def test_multiple_errors_accumulate(self):
        schema = _valid_schema(
            build_name="",
            character_class="",
            version="bad",
        )
        result = self.v.validate(schema)
        assert not result.valid
        assert len(result.errors) >= 3

    def test_bad_skill_and_bad_gear_both_reported(self):
        schema = _valid_schema(
            skills=[SkillEntry("s1", level=0)],
            gear=[GearEntry(slot="invalid_slot", item_id="x")],
        )
        result = self.v.validate(schema)
        assert not result.valid
        assert len(result.errors) >= 2

    def test_valid_false_when_errors_present(self):
        schema = _valid_schema(build_name="")
        result = self.v.validate(schema)
        assert result.valid is False


# ---------------------------------------------------------------------------
# SchemaValidator.from_json — parsing
# ---------------------------------------------------------------------------

class TestSchemaValidatorFromJson:
    def setup_method(self):
        self.v = SchemaValidator()

    def _sample_dict(self, **overrides):
        d = {
            "format": "json",
            "version": "1.0",
            "build_name": "My Build",
            "character_class": "Sentinel",
        }
        d.update(overrides)
        return d

    def test_parse_valid_json_string(self):
        schema = self.v.from_json(json.dumps(self._sample_dict()))
        assert isinstance(schema, ImportSchema)
        assert schema.build_name == "My Build"

    def test_parse_dict_directly(self):
        schema = self.v.from_json(self._sample_dict())
        assert isinstance(schema, ImportSchema)
        assert schema.character_class == "Sentinel"

    def test_missing_skills_defaults_to_empty_list(self):
        schema = self.v.from_json(self._sample_dict())
        assert schema.skills == []

    def test_missing_passives_defaults_to_empty_list(self):
        schema = self.v.from_json(self._sample_dict())
        assert schema.passives == []

    def test_missing_gear_defaults_to_empty_list(self):
        schema = self.v.from_json(self._sample_dict())
        assert schema.gear == []

    def test_build_name_preserved(self):
        schema = self.v.from_json(self._sample_dict(build_name="Bleed Void Knight"))
        assert schema.build_name == "Bleed Void Knight"

    def test_character_class_preserved(self):
        schema = self.v.from_json(self._sample_dict(character_class="Primalist"))
        assert schema.character_class == "Primalist"

    def test_skills_parsed_into_skill_entries(self):
        d = self._sample_dict(skills=[{"skill_id": "smite", "level": 10, "quality": 5}])
        schema = self.v.from_json(d)
        assert len(schema.skills) == 1
        sk = schema.skills[0]
        assert isinstance(sk, SkillEntry)
        assert sk.skill_id == "smite"
        assert sk.level == 10
        assert sk.quality == 5

    def test_gear_parsed_into_gear_entries(self):
        d = self._sample_dict(gear=[{"slot": "helm", "item_id": "iron_helm"}])
        schema = self.v.from_json(d)
        assert len(schema.gear) == 1
        g = schema.gear[0]
        assert isinstance(g, GearEntry)
        assert g.slot == "helm"
        assert g.item_id == "iron_helm"

    def test_unknown_format_string_defaults_to_json(self):
        d = self._sample_dict(format="totally_unknown")
        schema = self.v.from_json(d)
        assert schema.format == ImportFormat.JSON

    def test_known_format_build_string(self):
        d = self._sample_dict(format="build_string")
        schema = self.v.from_json(d)
        assert schema.format == ImportFormat.BUILD_STRING

    def test_known_format_url(self):
        d = self._sample_dict(format="url")
        schema = self.v.from_json(d)
        assert schema.format == ImportFormat.URL

    def test_multiple_skills_parsed(self):
        d = self._sample_dict(skills=[
            {"skill_id": "smite", "level": 5},
            {"skill_id": "mana_strike", "level": 3},
        ])
        schema = self.v.from_json(d)
        assert len(schema.skills) == 2
        assert schema.skills[0].skill_id == "smite"
        assert schema.skills[1].skill_id == "mana_strike"


# ---------------------------------------------------------------------------
# ImportSchema dataclass
# ---------------------------------------------------------------------------

class TestImportSchemaDataclass:
    def test_default_skills_empty(self):
        s = ImportSchema(
            format=ImportFormat.JSON,
            version="1.0",
            build_name="x",
            character_class="Sentinel",
        )
        assert s.skills == []

    def test_default_passives_empty(self):
        s = ImportSchema(
            format=ImportFormat.JSON,
            version="1.0",
            build_name="x",
            character_class="Sentinel",
        )
        assert s.passives == []

    def test_default_gear_empty(self):
        s = ImportSchema(
            format=ImportFormat.JSON,
            version="1.0",
            build_name="x",
            character_class="Sentinel",
        )
        assert s.gear == []

    def test_format_field_is_import_format_enum(self):
        s = ImportSchema(
            format=ImportFormat.BUILD_STRING,
            version="1.0",
            build_name="x",
            character_class="Sentinel",
        )
        assert isinstance(s.format, ImportFormat)
        assert s.format == ImportFormat.BUILD_STRING

    def test_default_metadata_is_empty_dict(self):
        s = ImportSchema(
            format=ImportFormat.JSON,
            version="1.0",
            build_name="x",
            character_class="Sentinel",
        )
        assert s.metadata == {}


# ---------------------------------------------------------------------------
# ImportFormat enum
# ---------------------------------------------------------------------------

class TestImportFormatEnum:
    def test_json_value(self):
        assert ImportFormat.JSON.value == "json"

    def test_build_string_value(self):
        assert ImportFormat.BUILD_STRING.value == "build_string"

    def test_url_value(self):
        assert ImportFormat.URL.value == "url"


# ---------------------------------------------------------------------------
# SkillEntry / GearEntry / PassiveEntry dataclasses
# ---------------------------------------------------------------------------

class TestEntryDataclasses:
    def test_skill_entry_defaults(self):
        s = SkillEntry("my_skill")
        assert s.level == 1
        assert s.quality == 0
        assert s.enabled is True

    def test_gear_entry_default_affixes_empty(self):
        g = GearEntry(slot="helm", item_id="x")
        assert g.affixes == []

    def test_passive_entry_default_allocated_true(self):
        p = PassiveEntry("node_1")
        assert p.allocated is True
