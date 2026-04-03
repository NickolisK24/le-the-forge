"""
Tests for Phase O backend integration modules:
  - AuthManager (integration/auth/auth_manager.py)
  - ExternalApi (integration/api/external_api.py)
  - VersionCompatibilityEngine (integration/versioning/version_compatibility.py)
  - IntegrationLogger (debug/integration_logger.py)
"""
from __future__ import annotations

import importlib
import json
import time

import pytest

from integration.auth.auth_manager import AuthManager, UserIdentity, AccessDecision
from integration.api.external_api import ExternalApi, ApiRequest, ApiResponse
from integration.storage.build_repository import BuildRepository, StoredBuild
from integration.versioning.version_compatibility import (
    VersionCompatibilityEngine,
    MigrationStep,
    CompatibilityResult,
)
from debug.integration_logger import IntegrationLogger, IntegrationLogEntry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_valid_json_body() -> dict:
    """Return a dict suitable for POST /api/import/build."""
    return {
        "data": json.dumps({
            "format": "json",
            "version": "1.0",
            "build_name": "API Test Build",
            "character_class": "Mage",
        }),
        "format": "json",
    }


def make_stored_build(
    build_id: str = "build001",
    build_name: str = "Test Build",
    character_class: str = "Mage",
    version: str = "1.0",
    owner_id: str | None = None,
    is_public: bool = True,
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
    )


# ===========================================================================
# AuthManager tests
# ===========================================================================

class TestAuthManagerRegisterUser:
    def setup_method(self):
        self.auth = AuthManager()

    def test_register_user_returns_user_identity(self):
        identity = self.auth.register_user("u1", "alice")
        assert isinstance(identity, UserIdentity)

    def test_register_user_is_authenticated(self):
        identity = self.auth.register_user("u1", "alice")
        assert identity.is_authenticated is True

    def test_register_user_correct_user_id(self):
        identity = self.auth.register_user("u1", "alice")
        assert identity.user_id == "u1"

    def test_register_user_correct_username(self):
        identity = self.auth.register_user("u1", "alice")
        assert identity.username == "alice"

    def test_register_user_default_scopes(self):
        identity = self.auth.register_user("u1", "alice")
        assert "read" in identity.scopes
        assert "write" in identity.scopes
        assert "share" in identity.scopes

    def test_register_user_custom_scopes(self):
        identity = self.auth.register_user("u1", "alice", scopes=["read"])
        assert identity.scopes == ["read"]


class TestAuthManagerGetUser:
    def setup_method(self):
        self.auth = AuthManager()

    def test_get_user_found_after_register(self):
        self.auth.register_user("u1", "alice")
        found = self.auth.get_user("u1")
        assert found is not None
        assert found.user_id == "u1"

    def test_get_user_not_found(self):
        result = self.auth.get_user("nonexistent")
        assert result is None


class TestAuthManagerApiKey:
    def setup_method(self):
        self.auth = AuthManager()
        self.auth.register_user("u1", "alice")

    def test_register_api_key_returns_hash(self):
        key_hash = self.auth.register_api_key("u1", "secret_key_123")
        assert isinstance(key_hash, str) and len(key_hash) > 0

    def test_authenticate_api_key_correct_key(self):
        self.auth.register_api_key("u1", "secret_key_123")
        identity = self.auth.authenticate_api_key("secret_key_123")
        assert identity is not None
        assert identity.user_id == "u1"

    def test_authenticate_api_key_wrong_key_returns_none(self):
        self.auth.register_api_key("u1", "secret_key_123")
        result = self.auth.authenticate_api_key("wrong_key")
        assert result is None

    def test_authenticate_api_key_empty_key_returns_none(self):
        result = self.auth.authenticate_api_key("")
        assert result is None


class TestAuthManagerOwnership:
    def setup_method(self):
        self.auth = AuthManager()
        self.auth.register_user("u1", "alice")

    def test_claim_ownership_returns_record(self):
        record = self.auth.claim_ownership("build001", "u1")
        assert record.build_id == "build001"
        assert record.owner_id == "u1"

    def test_get_owner_correct(self):
        self.auth.claim_ownership("build001", "u1")
        assert self.auth.get_owner("build001") == "u1"

    def test_get_owner_no_claim_returns_none(self):
        assert self.auth.get_owner("unclaimed_build") is None


class TestAuthManagerCheckAccess:
    def setup_method(self):
        self.auth = AuthManager()
        self.auth.register_user("owner", "alice", scopes=["read", "write", "share"])
        self.auth.register_user("other", "bob", scopes=["read", "write", "share"])
        self.auth.register_user("readonly", "carol", scopes=["read"])
        self.auth.claim_ownership("build001", "owner")

    def test_read_allowed_for_authenticated_user_with_read_scope(self):
        decision = self.auth.check_access("other", "build001", "read")
        assert decision.allowed is True

    def test_write_blocked_for_non_owner(self):
        decision = self.auth.check_access("other", "build001", "write")
        assert decision.allowed is False

    def test_write_allowed_for_owner(self):
        decision = self.auth.check_access("owner", "build001", "write")
        assert decision.allowed is True

    def test_read_blocked_if_missing_scope(self):
        # Use a non-empty scope list that doesn't include "read"
        # (empty list is falsy so register_user defaults to full scopes)
        self.auth.register_user("noscope", "dave", scopes=["share"])
        decision = self.auth.check_access("noscope", "build001", "read")
        assert decision.allowed is False
        assert "missing scope" in decision.reason

    def test_access_fails_if_user_not_authenticated(self):
        self.auth.register_user("revoked", "eve")
        self.auth.revoke_user("revoked")
        decision = self.auth.check_access("revoked", "build001", "read")
        assert decision.allowed is False

    def test_access_fails_unknown_user(self):
        decision = self.auth.check_access("unknown_user", "build001", "read")
        assert decision.allowed is False

    def test_write_allowed_when_no_owner(self):
        # No ownership claimed on build999
        decision = self.auth.check_access("other", "build999", "write")
        assert decision.allowed is True

    def test_access_decision_reason_for_allowed(self):
        decision = self.auth.check_access("owner", "build001", "read")
        assert decision.reason == "allowed"


class TestAuthManagerRevokeUser:
    def setup_method(self):
        self.auth = AuthManager()

    def test_revoke_user_sets_is_authenticated_false(self):
        self.auth.register_user("u1", "alice")
        self.auth.revoke_user("u1")
        assert self.auth.get_user("u1").is_authenticated is False

    def test_revoke_user_returns_true_if_exists(self):
        self.auth.register_user("u1", "alice")
        assert self.auth.revoke_user("u1") is True

    def test_revoke_user_returns_false_if_not_exists(self):
        assert self.auth.revoke_user("nonexistent") is False


# ===========================================================================
# ExternalApi tests
# ===========================================================================

class TestExternalApiImportBuild:
    def setup_method(self):
        self.api = ExternalApi()

    def test_import_build_valid_body_returns_200(self):
        req = ApiRequest("POST", "/api/import/build", body=make_valid_json_body())
        resp = self.api.handle(req)
        assert resp.status_code == 200

    def test_import_build_valid_body_contains_build_id(self):
        req = ApiRequest("POST", "/api/import/build", body=make_valid_json_body())
        resp = self.api.handle(req)
        assert "build_id" in resp.body

    def test_import_build_invalid_body_returns_400(self):
        req = ApiRequest("POST", "/api/import/build", body={"data": "not_valid_json!@#"})
        resp = self.api.handle(req)
        assert resp.status_code == 400

    def test_import_build_empty_body_returns_400(self):
        req = ApiRequest("POST", "/api/import/build", body={})
        resp = self.api.handle(req)
        assert resp.status_code == 400

    def test_import_build_invalid_returns_error_key(self):
        req = ApiRequest("POST", "/api/import/build", body={"data": "!!!invalid!!!"})
        resp = self.api.handle(req)
        assert "error" in resp.body


class TestExternalApiExportBuild:
    def setup_method(self):
        self.api = ExternalApi()
        # Save directly into the api's internal repo (empty repo is falsy, so
        # ExternalApi always creates its own; we access it via _repo after init)
        self.api._repo.save(make_stored_build("known_id"))

    def test_export_build_found_returns_200(self):
        req = ApiRequest("GET", "/api/export/build", query_params={"id": "known_id"})
        resp = self.api.handle(req)
        assert resp.status_code == 200

    def test_export_build_not_found_returns_404(self):
        req = ApiRequest("GET", "/api/export/build", query_params={"id": "unknown_id"})
        resp = self.api.handle(req)
        assert resp.status_code == 404

    def test_export_build_missing_id_returns_400(self):
        req = ApiRequest("GET", "/api/export/build")
        resp = self.api.handle(req)
        assert resp.status_code == 400


class TestExternalApiShareBuild:
    def setup_method(self):
        self.api = ExternalApi()
        self.api._repo.save(make_stored_build("share_me"))

    def test_share_build_returns_200(self):
        req = ApiRequest("POST", "/api/share/build", body={"build_id": "share_me"})
        resp = self.api.handle(req)
        assert resp.status_code == 200

    def test_share_build_contains_share_url(self):
        req = ApiRequest("POST", "/api/share/build", body={"build_id": "share_me"})
        resp = self.api.handle(req)
        assert "share_url" in resp.body

    def test_share_build_missing_build_id_returns_400(self):
        req = ApiRequest("POST", "/api/share/build", body={})
        resp = self.api.handle(req)
        assert resp.status_code == 400

    def test_share_build_nonexistent_returns_404(self):
        req = ApiRequest("POST", "/api/share/build", body={"build_id": "ghost"})
        resp = self.api.handle(req)
        assert resp.status_code == 404


class TestExternalApiGetBuild:
    def setup_method(self):
        self.api = ExternalApi()
        self.api._repo.save(make_stored_build("get_me"))

    def test_get_build_not_found_returns_404(self):
        req = ApiRequest("GET", "/api/build/nonexistent")
        resp = self.api.handle(req)
        assert resp.status_code == 404

    def test_get_build_found_returns_200(self):
        req = ApiRequest("GET", "/api/build/get_me")
        resp = self.api.handle(req)
        assert resp.status_code == 200

    def test_get_build_increments_view_count(self):
        req = ApiRequest("GET", "/api/build/get_me")
        self.api.handle(req)
        self.api.handle(req)
        build = self.api._repo.get("get_me")
        assert build.view_count == 2

    def test_get_build_response_contains_build(self):
        req = ApiRequest("GET", "/api/build/get_me")
        resp = self.api.handle(req)
        assert "build" in resp.body


class TestExternalApiUnknownRoute:
    def setup_method(self):
        self.api = ExternalApi()

    def test_unknown_route_returns_404(self):
        req = ApiRequest("GET", "/api/unknown/route")
        resp = self.api.handle(req)
        assert resp.status_code == 404

    def test_unknown_method_returns_404(self):
        req = ApiRequest("DELETE", "/api/import/build")
        resp = self.api.handle(req)
        assert resp.status_code == 404


# ===========================================================================
# VersionCompatibilityEngine tests
# ===========================================================================

def make_step(from_v: str, to_v: str, transform=None) -> MigrationStep:
    if transform is None:
        def transform(d):
            d = dict(d)
            d["migrated"] = True
            return d
    return MigrationStep(
        from_version=from_v,
        to_version=to_v,
        description=f"Migrate {from_v} -> {to_v}",
        migrate_fn=transform,
    )


class TestVersionCompatibilityEngineMigrate:
    def setup_method(self):
        self.engine = VersionCompatibilityEngine()

    def test_register_and_migrate_transforms_data(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        result = self.engine.migrate({"version": "1.0", "name": "test"}, "2.0")
        assert result.data.get("migrated") is True

    def test_migrate_steps_applied_positive(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.steps_applied > 0

    def test_migrate_migrated_true_when_step_applied(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.migrated is True

    def test_migrate_no_matching_migration_migrated_false(self):
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.migrated is False

    def test_migrate_no_matching_migration_steps_zero(self):
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.steps_applied == 0

    def test_migrate_preserves_original_version_in_result(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.original_version == "1.0"

    def test_migrate_sets_target_version(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.target_version == "2.0"

    def test_migrate_chain_applies_multiple_steps(self):
        self.engine.register_migration(make_step("1.0", "1.5"))
        self.engine.register_migration(make_step("1.5", "2.0"))
        result = self.engine.migrate({"version": "1.0"}, "2.0")
        assert result.steps_applied == 2


class TestVersionCompatibilityEngineDeprecation:
    def setup_method(self):
        self.engine = VersionCompatibilityEngine()

    def test_register_deprecation_adds_warning(self):
        self.engine.register_deprecation("1.0", "Use 2.0 instead")
        result = self.engine.migrate({"version": "1.0"}, "1.0")
        assert any("deprecated" in w for w in result.warnings)

    def test_no_deprecation_no_warnings(self):
        result = self.engine.migrate({"version": "1.0"}, "1.0")
        assert result.warnings == []


class TestVersionCompatibilityEngineIsCompatible:
    def setup_method(self):
        self.engine = VersionCompatibilityEngine()

    def test_is_compatible_within_range(self):
        assert self.engine.is_compatible("1.5", "1.0", "2.0") is True

    def test_is_compatible_at_min_boundary(self):
        assert self.engine.is_compatible("1.0", "1.0", "2.0") is True

    def test_is_compatible_at_max_boundary(self):
        assert self.engine.is_compatible("2.0", "1.0", "2.0") is True

    def test_is_compatible_below_min(self):
        assert self.engine.is_compatible("0.9", "1.0", "2.0") is False

    def test_is_compatible_above_max(self):
        assert self.engine.is_compatible("2.1", "1.0", "2.0") is False


class TestVersionCompatibilityEngineLatestVersion:
    def setup_method(self):
        self.engine = VersionCompatibilityEngine()

    def test_latest_version_returns_highest_to_version(self):
        self.engine.register_migration(make_step("1.0", "1.5"))
        self.engine.register_migration(make_step("1.5", "2.0"))
        self.engine.register_migration(make_step("2.0", "3.0"))
        assert self.engine.latest_version() == "3.0"

    def test_latest_version_single_step(self):
        self.engine.register_migration(make_step("1.0", "2.0"))
        assert self.engine.latest_version() == "2.0"

    def test_latest_version_no_migrations_returns_none(self):
        assert self.engine.latest_version() is None


# ===========================================================================
# IntegrationLogger tests
# ===========================================================================

class TestIntegrationLoggerLogMethods:
    def setup_method(self):
        self.logger = IntegrationLogger()

    def test_log_import_success_event_type(self):
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "import_success"

    def test_log_import_failure_event_type(self):
        self.logger.log_import_failure("u1", "json", ["bad data"], 5.0)
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "import_failure"

    def test_log_import_failure_build_id_is_none(self):
        self.logger.log_import_failure("u1", "json", ["error"], 5.0)
        entries = self.logger.get_entries()
        assert entries[-1].build_id is None

    def test_log_export_event_type(self):
        self.logger.log_export("b1", "u1", "json", 512, 3.0)
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "export"

    def test_log_share_event_type(self):
        self.logger.log_share("b1", "u1", "https://example.com/share/b1", 2.0)
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "share"

    def test_log_version_mismatch_event_type(self):
        self.logger.log_version_mismatch("b1", "1.0", "2.0", 1)
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "version_mismatch"

    def test_log_version_mismatch_metadata_has_from_to_steps(self):
        self.logger.log_version_mismatch("b1", "1.0", "2.0", 3)
        entry = self.logger.get_entries()[-1]
        assert entry.metadata.get("from") == "1.0"
        assert entry.metadata.get("to") == "2.0"
        assert entry.metadata.get("steps") == 3

    def test_log_auth_failure_event_type(self):
        self.logger.log_auth_failure("u1", "write", "not owner")
        entries = self.logger.get_entries()
        assert entries[-1].event_type == "auth_failure"

    def test_log_auth_failure_metadata_has_action_reason(self):
        self.logger.log_auth_failure("u1", "delete", "not owner")
        entry = self.logger.get_entries()[-1]
        assert entry.metadata.get("action") == "delete"
        assert entry.metadata.get("reason") == "not owner"


class TestIntegrationLoggerGetEntries:
    def setup_method(self):
        self.logger = IntegrationLogger()
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        self.logger.log_import_failure("u1", "json", ["err"], 5.0)
        self.logger.log_export("b1", "u1", "json", 100, 3.0)

    def test_get_entries_all(self):
        entries = self.logger.get_entries()
        assert len(entries) == 3

    def test_get_entries_filtered_by_event_type(self):
        entries = self.logger.get_entries(event_type="import_success")
        assert len(entries) == 1
        assert entries[0].event_type == "import_success"

    def test_get_entries_filter_no_match(self):
        entries = self.logger.get_entries(event_type="share")
        assert entries == []


class TestIntegrationLoggerSummary:
    def setup_method(self):
        self.logger = IntegrationLogger()

    def test_summary_by_type_counts(self):
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        self.logger.log_import_success("b2", "u1", "json", 10.0)
        self.logger.log_import_failure("u1", "json", ["err"], 5.0)
        summary = self.logger.summary()
        assert summary["by_type"]["import_success"] == 2
        assert summary["by_type"]["import_failure"] == 1

    def test_summary_total(self):
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        self.logger.log_export("b1", "u1", "json", 100, 3.0)
        summary = self.logger.summary()
        assert summary["total"] == 2

    def test_summary_success_rate_all_success(self):
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        self.logger.log_import_success("b2", "u1", "json", 10.0)
        summary = self.logger.summary()
        assert summary["success_rate"] == 1.0

    def test_summary_success_rate_mixed(self):
        self.logger.log_import_success("b1", "u1", "json", 10.0)
        self.logger.log_import_failure("u1", "json", ["err"], 5.0)
        summary = self.logger.summary()
        assert summary["success_rate"] == pytest.approx(0.5)

    def test_summary_success_rate_no_imports(self):
        self.logger.log_export("b1", "u1", "json", 100, 3.0)
        summary = self.logger.summary()
        assert summary["success_rate"] == 1.0


class TestIntegrationLoggerClearAndCapacity:
    def test_clear_empties_entries(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", "u1", "json", 1.0)
        logger.log_export("b1", "u1", "json", 10, 1.0)
        logger.clear()
        assert len(logger.get_entries()) == 0

    def test_len_after_logging(self):
        logger = IntegrationLogger()
        logger.log_import_success("b1", "u1", "json", 1.0)
        logger.log_export("b1", "u1", "json", 10, 1.0)
        assert len(logger) == 2

    def test_capacity_enforced(self):
        logger = IntegrationLogger(capacity=5)
        for i in range(10):
            logger.log_import_success(f"b{i}", "u1", "json", 1.0)
        assert len(logger) == 5

    def test_capacity_retains_newest(self):
        logger = IntegrationLogger(capacity=3)
        for i in range(5):
            logger.log_import_success(f"b{i}", "u1", "json", 1.0)
        entries = logger.get_entries()
        build_ids = [e.build_id for e in entries]
        assert "b4" in build_ids
