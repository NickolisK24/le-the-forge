"""
Tests for Phase O backend integration modules:
  - BuildExporter (integration/export/build_exporter.py)
  - ShareLinkGenerator (integration/sharing/share_link_generator.py)
  - BuildRepository (integration/storage/build_repository.py)
"""
from __future__ import annotations

import importlib
import json
import re
import time
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Import schema types via importlib (integration.import is a reserved path)
# ---------------------------------------------------------------------------
_schema_mod = importlib.import_module("integration.import.schemas.import_schema")
ImportSchema = _schema_mod.ImportSchema
ImportFormat = _schema_mod.ImportFormat
SkillEntry = _schema_mod.SkillEntry
GearEntry = _schema_mod.GearEntry
PassiveEntry = _schema_mod.PassiveEntry

from integration.export.build_exporter import BuildExporter, ExportResult
from integration.sharing.share_link_generator import ShareLink, ShareLinkGenerator
from integration.storage.build_repository import BuildRepository, StoredBuild


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_schema(
    build_name: str = "Test Build",
    version: str = "1.0",
    character_class: str = "Warrior",
    fmt: ImportFormat = ImportFormat.JSON,
) -> ImportSchema:
    return ImportSchema(
        format=fmt,
        version=version,
        build_name=build_name,
        character_class=character_class,
        skills=[SkillEntry("fireball", level=5)],
        passives=[PassiveEntry("node_001")],
        gear=[GearEntry("helm", "helm_001")],
        metadata={"created_by": "pytest"},
    )


def make_stored_build(
    build_id: str = "build001",
    build_name: str = "My Build",
    character_class: str = "Mage",
    version: str = "1.0",
    owner_id: str | None = "user1",
    is_public: bool = True,
    tags: list[str] | None = None,
) -> StoredBuild:
    now = time.time()
    return StoredBuild(
        build_id=build_id,
        build_name=build_name,
        character_class=character_class,
        version=version,
        data={"name": build_name},
        owner_id=owner_id,
        is_public=is_public,
        created_at=now,
        updated_at=now,
        tags=tags or [],
    )


# ===========================================================================
# BuildExporter tests
# ===========================================================================

class TestBuildExporterToJson:
    def setup_method(self):
        self.exporter = BuildExporter()
        self.schema = make_schema()

    def test_to_json_returns_string(self):
        result = self.exporter.to_json(self.schema)
        assert isinstance(result.content, str)

    def test_to_json_is_valid_json(self):
        result = self.exporter.to_json(self.schema)
        parsed = json.loads(result.content)
        assert isinstance(parsed, dict)

    def test_to_json_contains_build_name(self):
        result = self.exporter.to_json(self.schema)
        assert "Test Build" in result.content

    def test_to_json_size_bytes_positive(self):
        result = self.exporter.to_json(self.schema)
        assert result.size_bytes > 0

    def test_to_json_size_bytes_matches_content(self):
        result = self.exporter.to_json(self.schema)
        assert result.size_bytes == len(result.content.encode())

    def test_to_json_format_field(self):
        result = self.exporter.to_json(self.schema)
        assert result.format == "json"

    def test_to_json_export_result_build_name(self):
        result = self.exporter.to_json(self.schema)
        assert result.build_name == "Test Build"

    def test_to_json_export_result_version(self):
        result = self.exporter.to_json(self.schema)
        assert result.version == "1.0"

    def test_to_json_contains_character_class(self):
        result = self.exporter.to_json(self.schema)
        parsed = json.loads(result.content)
        assert parsed["character_class"] == "Warrior"


class TestBuildExporterToBuildString:
    def setup_method(self):
        self.exporter = BuildExporter()
        self.schema = make_schema()

    def test_to_build_string_no_equals_sign(self):
        result = self.exporter.to_build_string(self.schema)
        assert "=" not in result.content

    def test_to_build_string_format_field(self):
        result = self.exporter.to_build_string(self.schema)
        assert result.format == "build_string"

    def test_to_build_string_smaller_than_json(self):
        json_result = self.exporter.to_json(self.schema)
        bs_result = self.exporter.to_build_string(self.schema)
        assert bs_result.size_bytes < json_result.size_bytes

    def test_to_build_string_export_result_build_name(self):
        result = self.exporter.to_build_string(self.schema)
        assert result.build_name == "Test Build"

    def test_to_build_string_export_result_version(self):
        result = self.exporter.to_build_string(self.schema)
        assert result.version == "1.0"

    def test_to_build_string_size_bytes_positive(self):
        result = self.exporter.to_build_string(self.schema)
        assert result.size_bytes > 0


class TestBuildExporterToUrlParam:
    def setup_method(self):
        self.exporter = BuildExporter()
        self.schema = make_schema()

    def test_to_url_param_starts_with_base_url(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.content.startswith(BuildExporter.BASE_URL)

    def test_to_url_param_contains_query_string(self):
        result = self.exporter.to_url_param(self.schema)
        assert "?build=" in result.content

    def test_to_url_param_format_field(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.format == "url_param"

    def test_to_url_param_export_result_build_name(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.build_name == "Test Build"

    def test_to_url_param_export_result_version(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.version == "1.0"

    def test_to_url_param_size_bytes_positive(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.size_bytes > 0


class TestBuildExporterRoundtrip:
    def setup_method(self):
        self.exporter = BuildExporter()

    def test_roundtrip_check_valid_schema(self):
        schema = make_schema()
        assert self.exporter.roundtrip_check(schema) is True

    def test_roundtrip_preserves_build_name(self):
        schema = make_schema(build_name="Unique Dragon Build")
        assert self.exporter.roundtrip_check(schema) is True

    def test_roundtrip_preserves_version(self):
        schema = make_schema(version="2.1")
        assert self.exporter.roundtrip_check(schema) is True


class TestExportResultFields:
    def setup_method(self):
        self.exporter = BuildExporter()
        self.schema = make_schema(build_name="Field Test", version="1.5")

    def test_export_result_fields_json(self):
        result = self.exporter.to_json(self.schema)
        assert result.build_name == "Field Test"
        assert result.version == "1.5"
        assert result.format == "json"
        assert result.size_bytes > 0
        assert isinstance(result.content, str)

    def test_export_result_fields_build_string(self):
        result = self.exporter.to_build_string(self.schema)
        assert result.build_name == "Field Test"
        assert result.version == "1.5"
        assert result.format == "build_string"

    def test_export_result_fields_url_param(self):
        result = self.exporter.to_url_param(self.schema)
        assert result.build_name == "Field Test"
        assert result.version == "1.5"
        assert result.format == "url_param"


# ===========================================================================
# ShareLinkGenerator tests
# ===========================================================================

class TestShareLinkGeneratorGenerate:
    def setup_method(self):
        self.gen = ShareLinkGenerator()

    def test_generate_returns_share_link(self):
        link = self.gen.generate("My Build", "1.0")
        assert isinstance(link, ShareLink)

    def test_generate_non_empty_build_id(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.build_id and len(link.build_id) > 0

    def test_generate_url_contains_build_id(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.build_id in link.url

    def test_generate_url_starts_with_base_url(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.url.startswith(ShareLinkGenerator.BASE_URL)

    def test_generate_build_name_preserved(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.build_name == "My Build"

    def test_generate_version_preserved(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.version == "1.0"

    def test_generate_with_ttl_sets_expires_at(self):
        before = time.time()
        link = self.gen.generate("My Build", "1.0", ttl_seconds=3600)
        after = time.time()
        assert link.expires_at is not None
        assert before + 3600 <= link.expires_at <= after + 3600

    def test_generate_without_ttl_expires_at_is_none(self):
        link = self.gen.generate("My Build", "1.0")
        assert link.expires_at is None

    def test_generate_created_at_recent(self):
        before = time.time()
        link = self.gen.generate("My Build", "1.0")
        after = time.time()
        assert before <= link.created_at <= after


class TestShareLinkGeneratorBuildId:
    def setup_method(self):
        self.gen = ShareLinkGenerator()

    def test_build_id_is_12_hex_chars(self):
        link = self.gen.generate("My Build", "1.0")
        assert re.fullmatch(r"[0-9a-f]{12}", link.build_id)

    def test_generate_build_id_is_12_hex_chars(self):
        build_id = self.gen.generate_build_id("Alpha", "2.0")
        assert re.fullmatch(r"[0-9a-f]{12}", build_id)


class TestShareLinkGeneratorIsExpired:
    def setup_method(self):
        self.gen = ShareLinkGenerator()

    def test_not_expired_for_future_expires_at(self):
        link = self.gen.generate("My Build", "1.0", ttl_seconds=9999)
        assert self.gen.is_expired(link) is False

    def test_not_expired_when_expires_at_is_none(self):
        link = self.gen.generate("My Build", "1.0")
        assert self.gen.is_expired(link) is False

    def test_expired_for_past_expires_at(self):
        # Create a link with expiry in the past
        link = ShareLink(
            build_id="aabbccddeeff",
            url="https://example.com/share/aabbccddeeff",
            build_name="Old Build",
            version="1.0",
            created_at=time.time() - 100,
            expires_at=time.time() - 1,
        )
        assert self.gen.is_expired(link) is True

    def test_expired_via_tiny_ttl_with_mocked_time(self):
        # Generate with ttl=1, then mock time to be in the future
        link = self.gen.generate("Old Build", "1.0", ttl_seconds=1)
        with patch("integration.sharing.share_link_generator.time") as mock_time:
            mock_time.time.return_value = link.expires_at + 10
            assert self.gen.is_expired(link) is True


class TestShareLinkGeneratorHash:
    def setup_method(self):
        self.gen = ShareLinkGenerator()

    def test_generate_hash_same_input_same_output(self):
        h1 = self.gen.generate_hash("hello world")
        h2 = self.gen.generate_hash("hello world")
        assert h1 == h2

    def test_generate_hash_different_inputs_different_outputs(self):
        h1 = self.gen.generate_hash("build_alpha")
        h2 = self.gen.generate_hash("build_beta")
        assert h1 != h2

    def test_generate_hash_returns_hex_string(self):
        h = self.gen.generate_hash("test")
        assert re.fullmatch(r"[0-9a-f]{64}", h)


class TestShareLinkGeneratorTagVersion:
    def setup_method(self):
        self.gen = ShareLinkGenerator()

    def test_tag_version_no_query_string_uses_question_mark(self):
        tagged = self.gen.tag_version("https://example.com/share/abc", "1.0")
        assert "?v=1.0" in tagged

    def test_tag_version_existing_query_uses_ampersand(self):
        tagged = self.gen.tag_version("https://example.com/share/abc?foo=bar", "2.1")
        assert "&v=2.1" in tagged

    def test_tag_version_does_not_double_up_separator(self):
        tagged = self.gen.tag_version("https://example.com/share/abc", "1.0")
        assert tagged.count("?") == 1

    def test_tag_version_preserves_original_url(self):
        base = "https://example.com/share/abc"
        tagged = self.gen.tag_version(base, "1.0")
        assert tagged.startswith(base)


# ===========================================================================
# BuildRepository tests
# ===========================================================================

class TestBuildRepositorySaveGet:
    def setup_method(self):
        self.repo = BuildRepository()

    def test_save_and_get_roundtrip(self):
        build = make_stored_build("b001")
        self.repo.save(build)
        fetched = self.repo.get("b001")
        assert fetched is not None
        assert fetched.build_id == "b001"

    def test_get_missing_returns_none(self):
        assert self.repo.get("nonexistent") is None

    def test_save_returns_stored_build(self):
        build = make_stored_build("b002")
        result = self.repo.save(build)
        assert result.build_id == "b002"

    def test_save_upsert_updates_existing(self):
        build = make_stored_build("b003", build_name="Original")
        self.repo.save(build)
        build.build_name = "Updated"
        self.repo.save(build)
        assert self.repo.get("b003").build_name == "Updated"


class TestBuildRepositoryViewCount:
    def setup_method(self):
        self.repo = BuildRepository()

    def test_get_and_increment_views_increments(self):
        build = make_stored_build("b010")
        self.repo.save(build)
        assert build.view_count == 0
        self.repo.get_and_increment_views("b010")
        assert self.repo.get("b010").view_count == 1

    def test_get_and_increment_views_multiple_times(self):
        build = make_stored_build("b011")
        self.repo.save(build)
        for _ in range(5):
            self.repo.get_and_increment_views("b011")
        assert self.repo.get("b011").view_count == 5

    def test_get_and_increment_views_missing_returns_none(self):
        result = self.repo.get_and_increment_views("nonexistent")
        assert result is None


class TestBuildRepositoryDelete:
    def setup_method(self):
        self.repo = BuildRepository()

    def test_delete_existing_returns_true(self):
        build = make_stored_build("b020")
        self.repo.save(build)
        assert self.repo.delete("b020") is True

    def test_delete_removes_build(self):
        build = make_stored_build("b021")
        self.repo.save(build)
        self.repo.delete("b021")
        assert self.repo.get("b021") is None

    def test_delete_nonexistent_returns_false(self):
        assert self.repo.delete("nonexistent") is False


class TestBuildRepositoryListPublic:
    def setup_method(self):
        self.repo = BuildRepository()
        self.repo.save(make_stored_build("pub1", character_class="Mage", is_public=True, tags=["fire"]))
        self.repo.save(make_stored_build("pub2", build_name="Fire Mage", character_class="Mage", is_public=True, tags=["fire", "aoe"]))
        self.repo.save(make_stored_build("pub3", character_class="Warrior", is_public=True, tags=["physical"]))
        self.repo.save(make_stored_build("priv1", character_class="Rogue", is_public=False))

    def test_list_public_excludes_private(self):
        result = self.repo.list_public()
        ids = [b.build_id for b in result.builds]
        assert "priv1" not in ids

    def test_list_public_includes_public(self):
        result = self.repo.list_public()
        assert result.total == 3

    def test_list_public_filter_by_character_class(self):
        result = self.repo.list_public(character_class="Mage")
        assert all(b.character_class == "Mage" for b in result.builds)
        assert result.total == 2

    def test_list_public_filter_by_character_class_case_insensitive(self):
        result = self.repo.list_public(character_class="mage")
        assert result.total == 2

    def test_list_public_filter_by_tag(self):
        result = self.repo.list_public(tag="fire")
        assert result.total == 2

    def test_list_public_filter_by_tag_specific(self):
        result = self.repo.list_public(tag="aoe")
        assert result.total == 1
        assert result.builds[0].build_id == "pub2"

    def test_list_public_search_case_insensitive(self):
        result = self.repo.list_public(search="fire")
        assert result.total == 1
        assert result.builds[0].build_id == "pub2"

    def test_list_public_search_no_match(self):
        result = self.repo.list_public(search="zzznomatch")
        assert result.total == 0


class TestBuildRepositoryListByOwner:
    def setup_method(self):
        self.repo = BuildRepository()
        self.repo.save(make_stored_build("o1", owner_id="alice"))
        self.repo.save(make_stored_build("o2", owner_id="alice"))
        self.repo.save(make_stored_build("o3", owner_id="bob"))

    def test_list_by_owner_returns_only_owners_builds(self):
        result = self.repo.list_by_owner("alice")
        assert result.total == 2
        assert all(b.owner_id == "alice" for b in result.builds)

    def test_list_by_owner_different_owner(self):
        result = self.repo.list_by_owner("bob")
        assert result.total == 1

    def test_list_by_owner_no_builds(self):
        result = self.repo.list_by_owner("charlie")
        assert result.total == 0


class TestBuildRepositoryVersionBuild:
    def setup_method(self):
        self.repo = BuildRepository()

    def test_version_build_updates_version(self):
        build = make_stored_build("v001", version="1.0")
        self.repo.save(build)
        updated = self.repo.version_build("v001", {"new": "data"}, "2.0")
        assert updated.version == "2.0"

    def test_version_build_updates_data(self):
        build = make_stored_build("v002")
        self.repo.save(build)
        self.repo.version_build("v002", {"skill": "fireball"}, "1.1")
        assert self.repo.get("v002").data == {"skill": "fireball"}

    def test_version_build_nonexistent_returns_none(self):
        result = self.repo.version_build("nonexistent", {}, "1.0")
        assert result is None


class TestBuildRepositoryCapacity:
    def test_eviction_at_max_builds(self):
        repo = BuildRepository(max_builds=3)
        for i in range(3):
            repo.save(make_stored_build(f"evict{i}"))
        # Adding a 4th should evict the first (oldest)
        repo.save(make_stored_build("evict3"))
        assert len(repo) == 3
        assert repo.get("evict0") is None

    def test_eviction_does_not_lose_newest(self):
        repo = BuildRepository(max_builds=3)
        for i in range(3):
            repo.save(make_stored_build(f"evict{i}"))
        repo.save(make_stored_build("evict3"))
        assert repo.get("evict3") is not None


class TestBuildRepositoryLen:
    def test_len_empty(self):
        repo = BuildRepository()
        assert len(repo) == 0

    def test_len_after_save(self):
        repo = BuildRepository()
        repo.save(make_stored_build("a"))
        repo.save(make_stored_build("b"))
        assert len(repo) == 2

    def test_len_after_delete(self):
        repo = BuildRepository()
        repo.save(make_stored_build("a"))
        repo.save(make_stored_build("b"))
        repo.delete("a")
        assert len(repo) == 1
