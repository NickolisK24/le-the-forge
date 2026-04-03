"""
Phase O Integration Pipeline Tests
Tests multiple components working together end-to-end.
Run from backend/:
    python -m pytest tests/test_integration_pipeline.py -v --tb=short
"""
from __future__ import annotations

import base64
import importlib
import json
import time

import pytest

# ---------------------------------------------------------------------------
# Module imports (integration.import uses importlib due to reserved keyword)
# ---------------------------------------------------------------------------
_schema_mod = importlib.import_module("integration.import.schemas.import_schema")
_parser_mod = importlib.import_module("integration.import.build_import_parser")

ImportSchema = _schema_mod.ImportSchema
ImportFormat = _schema_mod.ImportFormat
SchemaValidator = _schema_mod.SchemaValidator
SkillEntry = _schema_mod.SkillEntry
GearEntry = _schema_mod.GearEntry
PassiveEntry = _schema_mod.PassiveEntry
BuildImportParser = _parser_mod.BuildImportParser

from integration.export.build_exporter import BuildExporter
from integration.storage.build_repository import BuildRepository, StoredBuild
from integration.auth.auth_manager import AuthManager
from integration.sharing.share_link_generator import ShareLinkGenerator
from integration.api.external_api import ExternalApi, ApiRequest
from integration.versioning.version_compatibility import (
    VersionCompatibilityEngine,
    MigrationStep,
)
from integration.mapping.id_mapper import IdMapper, MappingEntry
from debug.integration_logger import IntegrationLogger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_JSON = json.dumps({
    "format": "json",
    "version": "1.0",
    "build_name": "Roundtrip Build",
    "character_class": "Mage",
    "skills": [{"skill_id": "fireball", "level": 5, "quality": 0, "enabled": True}],
    "passives": [],
    "gear": [],
    "metadata": {},
})


def _make_stored(build_id: str, build_name: str = "Test", owner: str | None = None,
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
# 1. Import → Export roundtrip
# ===========================================================================

class TestImportExportRoundtrip:

    def test_parse_json_export_json_reparse_build_name(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        assert result.success
        export = exporter.to_json(result.schema)
        result2 = parser.parse_json(export.content)
        assert result2.success
        assert result2.schema.build_name == "Roundtrip Build"

    def test_parse_json_to_build_string_reparse_success(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        assert result.success
        export = exporter.to_build_string(result.schema)
        result2 = parser.parse_build_string(export.content)
        assert result2.success

    def test_build_string_roundtrip_preserves_character_class(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_build_string(result.schema)
        result2 = parser.parse_build_string(export.content)
        assert result2.schema.character_class == "Mage"

    def test_build_string_roundtrip_preserves_version(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_build_string(result.schema)
        result2 = parser.parse_build_string(export.content)
        assert result2.schema.version == "1.0"

    def test_exporter_roundtrip_check_returns_true(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        assert exporter.roundtrip_check(result.schema) is True

    def test_to_json_export_result_build_name(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_json(result.schema)
        assert export.build_name == "Roundtrip Build"

    def test_to_build_string_export_result_version(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_build_string(result.schema)
        assert export.version == "1.0"

    def test_to_url_param_contains_build_param(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_url_param(result.schema)
        assert "?build=" in export.content

    def test_parse_url_roundtrip(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_url_param(result.schema)
        result2 = parser.parse_url(export.content)
        assert result2.success
        assert result2.schema.build_name == "Roundtrip Build"


# ===========================================================================
# 2. Import → Store → Retrieve pipeline
# ===========================================================================

class TestImportStoreRetrieve:

    def test_import_store_retrieve_found(self):
        parser = BuildImportParser()
        repo = BuildRepository()
        result = parser.parse_json(VALID_JSON)
        assert result.success
        gen = ShareLinkGenerator()
        build_id = gen.generate_build_id(result.schema.build_name, result.schema.version)
        stored = _make_stored(build_id, result.schema.build_name)
        repo.save(stored)
        assert repo.get(build_id) is not None

    def test_import_store_list_public_appears(self):
        parser = BuildImportParser()
        repo = BuildRepository()
        result = parser.parse_json(VALID_JSON)
        gen = ShareLinkGenerator()
        build_id = gen.generate_build_id(result.schema.build_name, result.schema.version)
        stored = _make_stored(build_id, result.schema.build_name, public=True)
        repo.save(stored)
        qr = repo.list_public()
        ids = [b.build_id for b in qr.builds]
        assert build_id in ids

    def test_import_store_delete_get_returns_none(self):
        parser = BuildImportParser()
        repo = BuildRepository()
        result = parser.parse_json(VALID_JSON)
        gen = ShareLinkGenerator()
        build_id = gen.generate_build_id(result.schema.build_name, result.schema.version)
        stored = _make_stored(build_id, result.schema.build_name)
        repo.save(stored)
        repo.delete(build_id)
        assert repo.get(build_id) is None

    def test_delete_returns_true_when_found(self):
        repo = BuildRepository()
        stored = _make_stored("del_id")
        repo.save(stored)
        assert repo.delete("del_id") is True

    def test_delete_returns_false_when_not_found(self):
        repo = BuildRepository()
        assert repo.delete("nonexistent") is False

    def test_repo_len_increases_on_save(self):
        repo = BuildRepository()
        repo.save(_make_stored("a1"))
        repo.save(_make_stored("b2"))
        assert len(repo) == 2

    def test_get_and_increment_views(self):
        repo = BuildRepository()
        stored = _make_stored("view_id")
        repo.save(stored)
        b = repo.get_and_increment_views("view_id")
        assert b.view_count == 1


# ===========================================================================
# 3. Import → Auth → Share pipeline
# ===========================================================================

class TestImportAuthShare:

    def test_owner_has_write_access(self):
        auth = AuthManager()
        repo = BuildRepository()
        auth.register_user("user1", "Alice")
        stored = _make_stored("build_abc", owner="user1")
        repo.save(stored)
        auth.claim_ownership("build_abc", "user1")
        decision = auth.check_access("user1", "build_abc", "write")
        assert decision.allowed is True

    def test_non_owner_denied_write(self):
        auth = AuthManager()
        auth.register_user("user1", "Alice")
        auth.register_user("user2", "Bob")
        auth.claim_ownership("build_xyz", "user1")
        decision = auth.check_access("user2", "build_xyz", "write")
        assert decision.allowed is False

    def test_share_link_for_stored_build_is_nonempty(self):
        repo = BuildRepository()
        gen = ShareLinkGenerator()
        stored = _make_stored("share_build", "My Build")
        repo.save(stored)
        link = gen.generate(stored.build_name, stored.version)
        assert len(link.url) > 0

    def test_unauthenticated_user_denied(self):
        auth = AuthManager()
        decision = auth.check_access("ghost_user", "build_123", "write")
        assert decision.allowed is False

    def test_revoked_user_denied(self):
        auth = AuthManager()
        auth.register_user("user_r", "Revoked")
        auth.revoke_user("user_r")
        decision = auth.check_access("user_r", "some_build", "write")
        assert decision.allowed is False

    def test_read_scope_allowed(self):
        auth = AuthManager()
        auth.register_user("reader", "Reader", scopes=["read"])
        decision = auth.check_access("reader", "any_build", "read")
        assert decision.allowed is True

    def test_missing_scope_denied(self):
        auth = AuthManager()
        auth.register_user("readonly_user", "ReadOnly", scopes=["read"])
        decision = auth.check_access("readonly_user", "any_build", "write")
        assert decision.allowed is False


# ===========================================================================
# 4. Export → Share link pipeline
# ===========================================================================

class TestExportShareLink:

    def test_export_to_build_string_generate_share_link_valid(self):
        parser = BuildImportParser()
        exporter = BuildExporter()
        gen = ShareLinkGenerator()
        result = parser.parse_json(VALID_JSON)
        export = exporter.to_build_string(result.schema)
        link = gen.generate(export.content[:50], result.schema.version)
        assert link.url.startswith("https://")

    def test_share_link_build_id_is_12_chars(self):
        gen = ShareLinkGenerator()
        link = gen.generate("My Build", "1.0")
        assert len(link.build_id) == 12

    def test_share_link_url_contains_build_id(self):
        gen = ShareLinkGenerator()
        link = gen.generate("My Build", "1.0")
        assert link.build_id in link.url

    def test_share_link_no_expiry_not_expired(self):
        gen = ShareLinkGenerator()
        link = gen.generate("My Build", "1.0", ttl_seconds=None)
        assert gen.is_expired(link) is False

    def test_share_link_with_future_expiry_not_expired(self):
        gen = ShareLinkGenerator()
        link = gen.generate("My Build", "1.0", ttl_seconds=3600)
        assert gen.is_expired(link) is False


# ===========================================================================
# 5. API end-to-end
# ===========================================================================

class TestApiEndToEnd:

    def _build_api(self):
        repo = BuildRepository()
        auth = AuthManager()
        api = ExternalApi(repository=repo, auth=auth)
        return api, repo, auth

    def test_post_import_get_build_status_200(self):
        api, repo, auth = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": VALID_JSON})
        resp = api.handle(req)
        assert resp.status_code == 200
        build_id = resp.body["build_id"]
        req2 = ApiRequest("GET", f"/api/build/{build_id}")
        resp2 = api.handle(req2)
        assert resp2.status_code == 200

    def test_post_import_returns_build_name(self):
        api, _, _ = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": VALID_JSON})
        resp = api.handle(req)
        assert resp.body["build_name"] == "Roundtrip Build"

    def test_get_build_increments_views(self):
        api, _, _ = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": VALID_JSON})
        resp = api.handle(req)
        build_id = resp.body["build_id"]
        api.handle(ApiRequest("GET", f"/api/build/{build_id}"))
        resp2 = api.handle(ApiRequest("GET", f"/api/build/{build_id}"))
        assert resp2.body["build"]["views"] == 2

    def test_post_share_returns_share_url(self):
        api, _, _ = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": VALID_JSON})
        resp = api.handle(req)
        build_id = resp.body["build_id"]
        share_req = ApiRequest("POST", "/api/share/build", body={"build_id": build_id})
        share_resp = api.handle(share_req)
        assert share_resp.status_code == 200
        assert "share_url" in share_resp.body

    def test_share_get_by_returned_id_status_200(self):
        api, _, _ = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": VALID_JSON})
        resp = api.handle(req)
        original_build_id = resp.body["build_id"]
        share_req = ApiRequest("POST", "/api/share/build", body={"build_id": original_build_id})
        share_resp = api.handle(share_req)
        # The share endpoint returns a new build_id; but we can still get the original
        resp2 = api.handle(ApiRequest("GET", f"/api/build/{original_build_id}"))
        assert resp2.status_code == 200

    def test_authenticated_import_claims_build(self):
        api, repo, auth = self._build_api()
        auth.register_user("u1", "Alice")
        auth.register_api_key("u1", "secret_key")
        req = ApiRequest(
            "POST", "/api/import/build",
            body={"data": VALID_JSON},
            headers={"X-Api-Key": "secret_key"},
        )
        resp = api.handle(req)
        assert resp.status_code == 200
        build_id = resp.body["build_id"]
        stored = repo.get(build_id)
        assert stored.owner_id == "u1"

    def test_import_invalid_json_returns_400(self):
        api, _, _ = self._build_api()
        req = ApiRequest("POST", "/api/import/build", body={"data": "not json at all!"})
        resp = api.handle(req)
        assert resp.status_code == 400

    def test_get_nonexistent_build_returns_404(self):
        api, _, _ = self._build_api()
        resp = api.handle(ApiRequest("GET", "/api/build/doesnotexist"))
        assert resp.status_code == 404

    def test_unknown_endpoint_returns_404(self):
        api, _, _ = self._build_api()
        resp = api.handle(ApiRequest("GET", "/api/unknown"))
        assert resp.status_code == 404

    def test_share_missing_build_id_returns_400(self):
        api, _, _ = self._build_api()
        resp = api.handle(ApiRequest("POST", "/api/share/build", body={}))
        assert resp.status_code == 400

    def test_share_unknown_build_returns_404(self):
        api, _, _ = self._build_api()
        resp = api.handle(ApiRequest("POST", "/api/share/build", body={"build_id": "ghost"}))
        assert resp.status_code == 404

    def test_export_build_returns_data(self):
        api, repo, _ = self._build_api()
        stored = _make_stored("export_test")
        repo.save(stored)
        resp = api.handle(ApiRequest("GET", "/api/export/build", query_params={"id": "export_test"}))
        assert resp.status_code == 200
        assert "data" in resp.body

    def test_export_build_missing_id_returns_400(self):
        api, _, _ = self._build_api()
        resp = api.handle(ApiRequest("GET", "/api/export/build"))
        assert resp.status_code == 400


# ===========================================================================
# 6. Versioning pipeline
# ===========================================================================

class TestVersioningPipeline:

    def _engine_with_1_to_2(self) -> VersionCompatibilityEngine:
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep(
            "1.0", "2.0", "1.0→2.0",
            lambda d: {**d, "new_field": "added"},
        ))
        return engine

    def test_migrate_1_0_to_2_0_version_becomes_2_0(self):
        engine = self._engine_with_1_to_2()
        result = engine.migrate({"version": "1.0", "name": "test"}, "2.0")
        assert result.data["version"] == "2.0"

    def test_migrate_steps_applied_is_1(self):
        engine = self._engine_with_1_to_2()
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.steps_applied == 1

    def test_migrate_migrated_flag_true(self):
        engine = self._engine_with_1_to_2()
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.migrated is True

    def test_migrate_chain_1_0_to_1_5_to_2_0(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep(
            "1.0", "1.5", "step1",
            lambda d: {**d, "mid": True},
        ))
        engine.register_migration(MigrationStep(
            "1.5", "2.0", "step2",
            lambda d: {**d, "final": True},
        ))
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.data["version"] == "2.0"
        assert result.steps_applied == 2
        assert result.data.get("mid") is True
        assert result.data.get("final") is True

    def test_migrate_no_migrations_not_migrated(self):
        engine = VersionCompatibilityEngine()
        result = engine.migrate({"version": "1.0", "name": "x"}, "2.0")
        assert result.migrated is False
        assert result.data["name"] == "x"

    def test_deprecated_version_triggers_warning(self):
        engine = self._engine_with_1_to_2()
        engine.register_deprecation("1.0", "please upgrade")
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert len(result.warnings) > 0
        assert "deprecated" in result.warnings[0].lower()

    def test_migrate_adds_new_field(self):
        engine = self._engine_with_1_to_2()
        result = engine.migrate({"version": "1.0"}, "2.0")
        assert result.data.get("new_field") == "added"

    def test_latest_version_returns_highest(self):
        engine = VersionCompatibilityEngine()
        engine.register_migration(MigrationStep("1.0", "1.5", "s1", lambda d: d))
        engine.register_migration(MigrationStep("1.5", "2.0", "s2", lambda d: d))
        assert engine.latest_version() == "2.0"

    def test_latest_version_none_when_no_migrations(self):
        engine = VersionCompatibilityEngine()
        assert engine.latest_version() is None


# ===========================================================================
# 7. IdMapper pipeline
# ===========================================================================

class TestIdMapperPipeline:

    def test_register_and_map_skill(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("ext_fire", "int_fireball", "skill"))
        result = mapper.map("ext_fire", "skill")
        assert result.found is True
        assert result.internal_id == "int_fireball"

    def test_map_all_skills_all_found(self):
        mapper = IdMapper()
        mapper.register_bulk([
            MappingEntry("s1", "fireball", "skill"),
            MappingEntry("s2", "icebolt", "skill"),
            MappingEntry("s3", "lightning", "skill"),
        ])
        results = mapper.map_all(["s1", "s2", "s3"], "skill")
        assert all(r.found for r in results)
        assert [r.internal_id for r in results] == ["fireball", "icebolt", "lightning"]

    def test_unmapped_count_unknown_ids(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("known", "internal", "skill"))
        count = mapper.unmapped_count(["known", "unknown1", "unknown2"], "skill")
        assert count == 2

    def test_unmapped_count_all_known(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("a", "A", "skill"))
        mapper.register(MappingEntry("b", "B", "skill"))
        count = mapper.unmapped_count(["a", "b"], "skill")
        assert count == 0

    def test_map_unknown_returns_not_found(self):
        mapper = IdMapper()
        result = mapper.map("ghost", "skill")
        assert result.found is False
        assert result.internal_id is None

    def test_map_with_fallback_used_when_missing(self):
        mapper = IdMapper()
        result = mapper.map_with_fallback("missing_skill", "skill", "default_skill")
        assert result.fallback_used is True
        assert result.internal_id == "default_skill"

    def test_map_with_fallback_not_used_when_found(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("found_id", "mapped", "skill"))
        result = mapper.map_with_fallback("found_id", "skill", "fallback")
        assert result.fallback_used is False
        assert result.internal_id == "mapped"

    def test_clear_category_removes_all(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("s1", "x", "skill"))
        mapper.clear_category("skill")
        assert mapper.unmapped_count(["s1"], "skill") == 1

    def test_list_category_returns_all_entries(self):
        mapper = IdMapper()
        mapper.register_bulk([
            MappingEntry("p1", "pass1", "passive"),
            MappingEntry("p2", "pass2", "passive"),
        ])
        entries = mapper.list_category("passive")
        assert len(entries) == 2

    def test_item_category_separate_from_skill(self):
        mapper = IdMapper()
        mapper.register(MappingEntry("sword_ext", "sword_int", "item"))
        skill_result = mapper.map("sword_ext", "skill")
        item_result = mapper.map("sword_ext", "item")
        assert skill_result.found is False
        assert item_result.found is True


# ===========================================================================
# 8. Logger integration
# ===========================================================================

class TestLoggerIntegration:

    def test_import_success_summary_count_1(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", "u1", "json", 12.5)
        summary = logger.summary()
        assert summary["by_type"].get("import_success") == 1

    def test_import_success_success_rate_1(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", "u1", "json", 12.5)
        assert logger.summary()["success_rate"] == 1.0

    def test_import_failure_success_rate_less_than_1(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", None, "json", 5.0)
        logger.log_import_failure(None, "json", ["parse error"], 2.0)
        assert logger.summary()["success_rate"] < 1.0

    def test_import_failure_success_rate_0_only_failures(self):
        logger = IntegrationLogger()
        logger.log_import_failure(None, "json", ["err"], 1.0)
        logger.log_import_failure(None, "json", ["err2"], 1.0)
        assert logger.summary()["success_rate"] == 0.0

    def test_multiple_operations_by_type_accurate(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", None, "json", 5.0)
        logger.log_export("b1", None, "json", 512, 3.0)
        logger.log_share("b1", None, "https://example.com/share/b1", 1.0)
        by_type = logger.summary()["by_type"]
        assert by_type.get("import_success") == 1
        assert by_type.get("export") == 1
        assert by_type.get("share") == 1

    def test_summary_total_matches_logged(self):
        logger = IntegrationLogger()
        for i in range(5):
            logger.log_import_success(f"b{i}", None, "json", 1.0)
        assert logger.summary()["total"] == 5

    def test_get_entries_filtered_by_type(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", None, "json", 1.0)
        logger.log_import_failure(None, "json", [], 1.0)
        entries = logger.get_entries("import_failure")
        assert len(entries) == 1
        assert entries[0].event_type == "import_failure"

    def test_get_entries_all_returned_when_none(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", None, "json", 1.0)
        logger.log_export("b1", None, "json", 100, 1.0)
        entries = logger.get_entries()
        assert len(entries) == 2

    def test_clear_empties_log(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", None, "json", 1.0)
        logger.clear()
        assert len(logger) == 0

    def test_log_auth_failure_in_by_type(self):
        logger = IntegrationLogger()
        logger.log_auth_failure("u1", "write", "not owner")
        by_type = logger.summary()["by_type"]
        assert by_type.get("auth_failure") == 1

    def test_log_version_mismatch_in_by_type(self):
        logger = IntegrationLogger()
        logger.log_version_mismatch("b1", "1.0", "2.0", 1)
        by_type = logger.summary()["by_type"]
        assert by_type.get("version_mismatch") == 1

    def test_no_imports_success_rate_is_1(self):
        logger = IntegrationLogger()
        logger.log_export("b1", None, "json", 100, 1.0)
        assert logger.summary()["success_rate"] == 1.0

    def test_capacity_limit_oldest_evicted(self):
        logger = IntegrationLogger(capacity=3)
        for i in range(5):
            logger.log_import_success(f"b{i}", None, "json", 1.0)
        assert len(logger) == 3
