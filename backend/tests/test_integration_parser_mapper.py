"""
Tests for:
  - integration.import.build_import_parser  (BuildImportParser, ParseResult)
  - integration.mapping.id_mapper           (IdMapper, MappingEntry, MappingResult)

Access the parser via importlib because 'integration.import' is a reserved
keyword path in Python.
"""
from __future__ import annotations

import base64
import importlib
import json
import pytest

# --- Parser module imports ---
_parser_mod = importlib.import_module("integration.import.build_import_parser")
BuildImportParser = _parser_mod.BuildImportParser
ParseResult = _parser_mod.ParseResult

# --- Schema module imports (for building test fixtures) ---
_schema_mod = importlib.import_module("integration.import.schemas.import_schema")
ImportSchema = _schema_mod.ImportSchema
ImportFormat = _schema_mod.ImportFormat
SkillEntry = _schema_mod.SkillEntry
GearEntry = _schema_mod.GearEntry

# --- IdMapper ---
from integration.mapping.id_mapper import IdMapper, MappingEntry, MappingResult

# --- Exporter (for round-trip tests) ---
from integration.export.build_exporter import BuildExporter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_json(**overrides) -> str:
    """Return a valid minimal build JSON string."""
    d = {
        "format": "json",
        "version": "1.0",
        "build_name": "Round Trip Build",
        "character_class": "Sentinel",
    }
    d.update(overrides)
    return json.dumps(d)


def _minimal_schema(**overrides) -> ImportSchema:
    defaults = dict(
        format=ImportFormat.JSON,
        version="1.0",
        build_name="Round Trip Build",
        character_class="Sentinel",
    )
    defaults.update(overrides)
    return ImportSchema(**defaults)


def _to_base64(data: dict) -> str:
    compact = json.dumps(data, separators=(",", ":"))
    return base64.urlsafe_b64encode(compact.encode()).decode().rstrip("=")


# ===========================================================================
# BuildImportParser.parse_json
# ===========================================================================

class TestParseJson:
    def setup_method(self):
        self.parser = BuildImportParser()

    def test_valid_json_success_true(self):
        result = self.parser.parse_json(_minimal_json())
        assert result.success is True

    def test_valid_json_schema_not_none(self):
        result = self.parser.parse_json(_minimal_json())
        assert result.schema is not None

    def test_valid_json_build_name_preserved(self):
        result = self.parser.parse_json(_minimal_json(build_name="Bleed VK"))
        assert result.schema.build_name == "Bleed VK"

    def test_valid_json_character_class_preserved(self):
        result = self.parser.parse_json(_minimal_json(character_class="Primalist"))
        assert result.schema.character_class == "Primalist"

    def test_invalid_json_success_false(self):
        result = self.parser.parse_json("{not valid json}")
        assert result.success is False

    def test_invalid_json_errors_populated(self):
        result = self.parser.parse_json("{not valid json}")
        assert len(result.errors) > 0

    def test_invalid_json_schema_none(self):
        result = self.parser.parse_json("{not valid json}")
        assert result.schema is None

    def test_invalid_json_validation_none(self):
        result = self.parser.parse_json("{not valid json}")
        assert result.validation is None

    def test_invalid_skill_level_success_false(self):
        d = {
            "format": "json",
            "version": "1.0",
            "build_name": "Bad Build",
            "character_class": "Sentinel",
            "skills": [{"skill_id": "smite", "level": 99}],
        }
        result = self.parser.parse_json(json.dumps(d))
        assert result.success is False

    def test_invalid_skill_level_errors_populated(self):
        d = {
            "format": "json",
            "version": "1.0",
            "build_name": "Bad Build",
            "character_class": "Sentinel",
            "skills": [{"skill_id": "smite", "level": 0}],
        }
        result = self.parser.parse_json(json.dumps(d))
        assert len(result.errors) > 0

    def test_empty_string_is_invalid(self):
        result = self.parser.parse_json("")
        assert result.success is False

    def test_raw_data_populated_on_success(self):
        result = self.parser.parse_json(_minimal_json())
        assert isinstance(result.raw_data, dict)
        assert "build_name" in result.raw_data

    def test_parse_result_is_dataclass_instance(self):
        result = self.parser.parse_json(_minimal_json())
        assert isinstance(result, ParseResult)


# ===========================================================================
# BuildImportParser.parse_build_string
# ===========================================================================

class TestParseBuildString:
    def setup_method(self):
        self.parser = BuildImportParser()
        self.exporter = BuildExporter()

    def test_round_trip_success_true(self):
        schema = _minimal_schema(build_name="Round Trip Build")
        export_result = self.exporter.to_build_string(schema)
        parse_result = self.parser.parse_build_string(export_result.content)
        assert parse_result.success is True

    def test_round_trip_same_build_name(self):
        schema = _minimal_schema(build_name="Unique Name 42")
        export_result = self.exporter.to_build_string(schema)
        parse_result = self.parser.parse_build_string(export_result.content)
        assert parse_result.schema is not None
        assert parse_result.schema.build_name == "Unique Name 42"

    def test_round_trip_character_class_preserved(self):
        schema = _minimal_schema(character_class="Mage")
        export_result = self.exporter.to_build_string(schema)
        parse_result = self.parser.parse_build_string(export_result.content)
        assert parse_result.schema.character_class == "Mage"

    def test_invalid_base64_success_false(self):
        result = self.parser.parse_build_string("!!!not_base64!!!")
        assert result.success is False

    def test_invalid_base64_errors_populated(self):
        result = self.parser.parse_build_string("!!!not_base64!!!")
        assert len(result.errors) > 0

    def test_base64_with_missing_padding_repaired(self):
        # Build a valid base64url string and manually strip all padding
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        unpadded = export_result.content.rstrip("=")
        result = self.parser.parse_build_string(unpadded)
        assert result.success is True

    def test_valid_base64_but_invalid_json_content_fails(self):
        garbage = base64.urlsafe_b64encode(b"not json at all").decode().rstrip("=")
        result = self.parser.parse_build_string(garbage)
        assert result.success is False

    def test_round_trip_with_skills(self):
        schema = _minimal_schema(
            skills=[SkillEntry("smite", level=10, quality=5)]
        )
        export_result = self.exporter.to_build_string(schema)
        parse_result = self.parser.parse_build_string(export_result.content)
        assert parse_result.success is True
        assert len(parse_result.schema.skills) == 1


# ===========================================================================
# BuildImportParser.parse_url
# ===========================================================================

class TestParseUrl:
    def setup_method(self):
        self.parser = BuildImportParser()
        self.exporter = BuildExporter()

    def test_url_with_build_param_success(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        url = f"http://example.com/build?build={export_result.content}"
        result = self.parser.parse_url(url)
        assert result.success is True

    def test_url_with_build_param_same_build_name(self):
        schema = _minimal_schema(build_name="URL Build Test")
        export_result = self.exporter.to_build_string(schema)
        url = f"http://example.com/build?build={export_result.content}"
        result = self.parser.parse_url(url)
        assert result.schema.build_name == "URL Build Test"

    def test_url_no_build_param_success_false(self):
        result = self.parser.parse_url("http://example.com/build?foo=bar")
        assert result.success is False

    def test_url_no_build_param_errors_populated(self):
        result = self.parser.parse_url("http://example.com/build?foo=bar")
        assert len(result.errors) > 0

    def test_url_no_query_string_fails(self):
        result = self.parser.parse_url("http://example.com/build")
        assert result.success is False

    def test_url_with_json_build_param(self):
        import urllib.parse
        json_str = _minimal_json(build_name="JSON URL Build")
        encoded = urllib.parse.quote(json_str)
        url = f"http://example.com/build?build={encoded}"
        result = self.parser.parse_url(url)
        assert result.success is True
        assert result.schema.build_name == "JSON URL Build"

    def test_url_with_extra_params_ignored(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        url = f"http://example.com/build?foo=bar&build={export_result.content}&baz=qux"
        result = self.parser.parse_url(url)
        assert result.success is True


# ===========================================================================
# BuildImportParser.parse — auto-detection
# ===========================================================================

class TestParseAutoDetect:
    def setup_method(self):
        self.parser = BuildImportParser()
        self.exporter = BuildExporter()

    def test_http_url_routes_to_url_path(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        url = f"http://example.com/build?build={export_result.content}"
        result = self.parser.parse(url)
        assert result.success is True

    def test_https_url_routes_to_url_path(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        url = f"https://example.com/build?build={export_result.content}"
        result = self.parser.parse(url)
        assert result.success is True

    def test_valid_json_string_routes_to_json_path(self):
        result = self.parser.parse(_minimal_json())
        assert result.success is True

    def test_base64_string_routes_to_build_string_path(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        result = self.parser.parse(export_result.content)
        assert result.success is True

    def test_explicit_format_url(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        url = f"http://example.com/build?build={export_result.content}"
        result = self.parser.parse(url, format=ImportFormat.URL)
        assert result.success is True

    def test_explicit_format_json(self):
        result = self.parser.parse(_minimal_json(), format=ImportFormat.JSON)
        assert result.success is True

    def test_explicit_format_build_string(self):
        schema = _minimal_schema()
        export_result = self.exporter.to_build_string(schema)
        result = self.parser.parse(export_result.content, format=ImportFormat.BUILD_STRING)
        assert result.success is True

    def test_invalid_data_no_crash(self):
        result = self.parser.parse("@@@completely_garbage@@@")
        assert isinstance(result, ParseResult)
        assert result.success is False


# ===========================================================================
# IdMapper — register + map
# ===========================================================================

class TestIdMapperRegisterAndMap:
    def setup_method(self):
        self.mapper = IdMapper()

    def test_register_and_map_found_true(self):
        entry = MappingEntry("ext_skill_1", "int_skill_001", "skill")
        self.mapper.register(entry)
        result = self.mapper.map("ext_skill_1", "skill")
        assert result.found is True

    def test_register_and_map_internal_id_correct(self):
        entry = MappingEntry("ext_skill_1", "int_skill_001", "skill")
        self.mapper.register(entry)
        result = self.mapper.map("ext_skill_1", "skill")
        assert result.internal_id == "int_skill_001"

    def test_map_missing_found_false(self):
        result = self.mapper.map("nonexistent", "skill")
        assert result.found is False

    def test_map_missing_internal_id_none(self):
        result = self.mapper.map("nonexistent", "skill")
        assert result.internal_id is None

    def test_map_wrong_category_not_found(self):
        entry = MappingEntry("ext_1", "int_1", "skill")
        self.mapper.register(entry)
        result = self.mapper.map("ext_1", "item")
        assert result.found is False

    def test_map_result_has_correct_external_id(self):
        entry = MappingEntry("ext_x", "int_x", "passive")
        self.mapper.register(entry)
        result = self.mapper.map("ext_x", "passive")
        assert result.external_id == "ext_x"

    def test_map_result_has_correct_category(self):
        entry = MappingEntry("ext_x", "int_x", "item")
        self.mapper.register(entry)
        result = self.mapper.map("ext_x", "item")
        assert result.category == "item"


# ===========================================================================
# IdMapper — map_with_fallback
# ===========================================================================

class TestIdMapperMapWithFallback:
    def setup_method(self):
        self.mapper = IdMapper()

    def test_fallback_not_used_when_found(self):
        entry = MappingEntry("ext_1", "int_1", "skill")
        self.mapper.register(entry)
        result = self.mapper.map_with_fallback("ext_1", "skill", "fallback_id")
        assert result.fallback_used is False

    def test_fallback_internal_id_when_found(self):
        entry = MappingEntry("ext_1", "int_1", "skill")
        self.mapper.register(entry)
        result = self.mapper.map_with_fallback("ext_1", "skill", "fallback_id")
        assert result.internal_id == "int_1"

    def test_fallback_used_when_not_found(self):
        result = self.mapper.map_with_fallback("missing_id", "skill", "fallback_id")
        assert result.fallback_used is True

    def test_fallback_returns_fallback_id(self):
        result = self.mapper.map_with_fallback("missing_id", "skill", "fallback_id")
        assert result.internal_id == "fallback_id"

    def test_fallback_found_false_when_fallback_used(self):
        result = self.mapper.map_with_fallback("missing_id", "skill", "fallback_id")
        assert result.found is False


# ===========================================================================
# IdMapper — map_all
# ===========================================================================

class TestIdMapperMapAll:
    def setup_method(self):
        self.mapper = IdMapper()
        self.mapper.register(MappingEntry("e1", "i1", "skill"))
        self.mapper.register(MappingEntry("e2", "i2", "skill"))

    def test_map_all_returns_list(self):
        results = self.mapper.map_all(["e1", "e2"], "skill")
        assert isinstance(results, list)

    def test_map_all_length_matches_input(self):
        results = self.mapper.map_all(["e1", "e2", "missing"], "skill")
        assert len(results) == 3

    def test_map_all_found_for_registered(self):
        results = self.mapper.map_all(["e1", "e2"], "skill")
        assert all(r.found for r in results)

    def test_map_all_not_found_for_missing(self):
        results = self.mapper.map_all(["missing"], "skill")
        assert results[0].found is False

    def test_map_all_empty_input_returns_empty(self):
        results = self.mapper.map_all([], "skill")
        assert results == []

    def test_map_all_mixed_found_and_not_found(self):
        results = self.mapper.map_all(["e1", "missing"], "skill")
        assert results[0].found is True
        assert results[1].found is False


# ===========================================================================
# IdMapper — unmapped_count
# ===========================================================================

class TestIdMapperUnmappedCount:
    def setup_method(self):
        self.mapper = IdMapper()
        self.mapper.register(MappingEntry("e1", "i1", "skill"))
        self.mapper.register(MappingEntry("e2", "i2", "skill"))

    def test_unmapped_count_all_found(self):
        assert self.mapper.unmapped_count(["e1", "e2"], "skill") == 0

    def test_unmapped_count_none_found(self):
        assert self.mapper.unmapped_count(["x", "y", "z"], "skill") == 3

    def test_unmapped_count_mixed(self):
        assert self.mapper.unmapped_count(["e1", "missing"], "skill") == 1

    def test_unmapped_count_empty_list(self):
        assert self.mapper.unmapped_count([], "skill") == 0


# ===========================================================================
# IdMapper — register_bulk
# ===========================================================================

class TestIdMapperRegisterBulk:
    def setup_method(self):
        self.mapper = IdMapper()

    def test_register_bulk_adds_all_entries(self):
        entries = [
            MappingEntry("e1", "i1", "item"),
            MappingEntry("e2", "i2", "item"),
            MappingEntry("e3", "i3", "item"),
        ]
        self.mapper.register_bulk(entries)
        assert self.mapper.map("e1", "item").found is True
        assert self.mapper.map("e2", "item").found is True
        assert self.mapper.map("e3", "item").found is True

    def test_register_bulk_empty_list(self):
        self.mapper.register_bulk([])
        assert self.mapper.unmapped_count([], "item") == 0

    def test_register_bulk_multiple_categories(self):
        entries = [
            MappingEntry("sk1", "int_sk1", "skill"),
            MappingEntry("it1", "int_it1", "item"),
        ]
        self.mapper.register_bulk(entries)
        assert self.mapper.map("sk1", "skill").found is True
        assert self.mapper.map("it1", "item").found is True


# ===========================================================================
# IdMapper — list_category
# ===========================================================================

class TestIdMapperListCategory:
    def setup_method(self):
        self.mapper = IdMapper()

    def test_list_category_empty_initially(self):
        # A fresh mapper returns empty list for any category
        result = self.mapper.list_category("skill")
        assert result == []

    def test_list_category_returns_registered_entries(self):
        e1 = MappingEntry("ext_1", "int_1", "skill")
        e2 = MappingEntry("ext_2", "int_2", "skill")
        self.mapper.register(e1)
        self.mapper.register(e2)
        listing = self.mapper.list_category("skill")
        assert len(listing) == 2

    def test_list_category_only_returns_correct_category(self):
        self.mapper.register(MappingEntry("sk1", "i1", "skill"))
        self.mapper.register(MappingEntry("it1", "i2", "item"))
        skills = self.mapper.list_category("skill")
        assert all(e.category == "skill" for e in skills)

    def test_list_category_returns_mapping_entries(self):
        self.mapper.register(MappingEntry("ext_1", "int_1", "passive"))
        listing = self.mapper.list_category("passive")
        assert all(isinstance(e, MappingEntry) for e in listing)


# ===========================================================================
# IdMapper — clear_category
# ===========================================================================

class TestIdMapperClearCategory:
    def setup_method(self):
        self.mapper = IdMapper()

    def test_clear_category_empties_it(self):
        self.mapper.register(MappingEntry("e1", "i1", "skill"))
        self.mapper.clear_category("skill")
        assert self.mapper.list_category("skill") == []

    def test_clear_category_does_not_affect_others(self):
        self.mapper.register(MappingEntry("e1", "i1", "skill"))
        self.mapper.register(MappingEntry("e2", "i2", "item"))
        self.mapper.clear_category("skill")
        assert self.mapper.map("e2", "item").found is True

    def test_clear_empty_category_no_error(self):
        # Should not raise even if category was already empty
        self.mapper.clear_category("skill")
        assert self.mapper.list_category("skill") == []

    def test_clear_then_re_register(self):
        self.mapper.register(MappingEntry("e1", "i1", "skill"))
        self.mapper.clear_category("skill")
        self.mapper.register(MappingEntry("e1", "i1_new", "skill"))
        result = self.mapper.map("e1", "skill")
        assert result.internal_id == "i1_new"
