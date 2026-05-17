from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_refresh.refresh_manifest_diagnostics import (  # noqa: E402
    build_refresh_manifest_diagnostics,
)
from operational_refresh.refresh_manifest_hashing import (  # noqa: E402
    hash_refresh_manifest,
    hash_refresh_manifest_identity,
)
from operational_refresh.refresh_manifest_integrity import (  # noqa: E402
    refresh_manifest_identities_equal,
    refresh_manifest_identity_key,
    refresh_manifests_equal,
    validate_refresh_manifest_integrity,
    validate_refresh_manifest_lineage_continuity,
    validate_refresh_manifest_non_execution,
    validate_refresh_manifest_provenance_continuity,
)
from operational_refresh.refresh_manifest_models import (  # noqa: E402
    PROHIBITED_REFRESH_DOMAINS,
    REFRESH_MANIFEST_STATE_BLOCKED,
    REFRESH_MANIFEST_STATE_PROHIBITED,
    REFRESH_MANIFEST_STATE_STALE,
    REFRESH_MANIFEST_STATE_SUPPORTED,
    REFRESH_MANIFEST_STATE_UNKNOWN,
    REFRESH_MANIFEST_STATE_UNSUPPORTED,
    V4_1_REFRESH_MANIFEST_SCHEMA_VERSION,
    V4_1_REFRESH_MANIFEST_STATUS_STABLE,
    default_refresh_manifest,
)
from operational_refresh.refresh_manifest_serialization import (  # noqa: E402
    export_refresh_manifest,
    serialize_refresh_manifest,
)
from operational_refresh.refresh_manifest_visibility import (  # noqa: E402
    count_refresh_manifest_states,
    validate_refresh_manifest_visibility,
)
from scripts.report_v4_1_refresh_manifest_foundations import (  # noqa: E402
    build_v4_1_refresh_manifest_diagnostics_report,
    build_v4_1_refresh_manifest_foundations_report,
)


def test_v4_1_refresh_manifest_models_are_immutable_and_non_executable():
    manifest = default_refresh_manifest()

    with pytest.raises(FrozenInstanceError):
        manifest.refresh_execution_enabled = True

    assert manifest.identity.schema_version == V4_1_REFRESH_MANIFEST_SCHEMA_VERSION
    assert manifest.non_executable is True
    assert manifest.descriptive_only is True
    assert manifest.refresh_execution_enabled is False
    assert manifest.orchestration_enabled is False
    assert manifest.deployment_execution_enabled is False
    assert manifest.automatic_refresh_enabled is False
    assert manifest.automatic_migration_enabled is False
    assert manifest.planner_integration_enabled is False
    assert manifest.production_consumption_enabled is False
    assert manifest.remediation_enabled is False
    assert manifest.mutation_enabled is False
    assert manifest.runtime_mutation_enabled is False
    assert manifest.recommendation_enabled is False
    assert manifest.ranking_enabled is False
    assert manifest.scoring_enabled is False
    assert manifest.selection_enabled is False
    assert manifest.authorization_enabled is False
    assert manifest.approval_enabled is False
    assert manifest.automatic_rollback_enabled is False
    assert manifest.automatic_recovery_enabled is False
    assert manifest.hidden_operational_behavior_enabled is False
    assert manifest.implicit_execution_pathway_enabled is False
    assert manifest.silent_fallback_enabled is False
    assert all(not state.executable for state in manifest.states)
    assert all(not state.automatic_resolution_enabled for state in manifest.states)
    assert all(not record.execution_enabled for record in manifest.source_lineage)
    assert all(not record.extraction_execution_enabled for record in manifest.extraction_lineage)
    assert all(not record.patch_execution_enabled for record in manifest.patch_lineage)
    assert manifest.governance_visibility.production_consumption_enabled is False
    assert manifest.governance_visibility.planner_integration_enabled is False


def test_v4_1_refresh_manifest_identity_key_is_stable():
    manifest = default_refresh_manifest()

    assert refresh_manifest_identity_key(manifest.identity) == (
        "v4_1.refresh_manifest_foundations.1"
        "|v4_1_phase_1_refresh_manifest_foundations"
        "|v4_1_refresh_manifest_primary|v4.1.0-foundation"
        "|v4_0_closeout_and_v4_1_readiness_report"
        "|v4_1_refresh_manifest_provenance_primary"
        "|v4_1_refresh_manifest_lineage_primary"
    )


def test_v4_1_deterministic_serialization_hashing_and_equality_are_stable():
    first = default_refresh_manifest()
    second = default_refresh_manifest()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_manifests_equal(first, second)
    assert refresh_manifest_identities_equal(first.identity, second.identity)
    assert serialize_refresh_manifest(first) == serialize_refresh_manifest(second)
    assert hash_refresh_manifest(first) == hash_refresh_manifest(second)
    assert hash_refresh_manifest_identity(first.identity) == hash_refresh_manifest_identity(second.identity)
    assert json.loads(serialize_refresh_manifest(first))["non_executable"] is True


def test_v4_1_serialization_preserves_order_and_fail_visible_states():
    manifest = default_refresh_manifest()
    reordered = replace(
        manifest,
        states=tuple(reversed(manifest.states)),
        source_lineage=tuple(reversed(manifest.source_lineage)),
        extraction_lineage=tuple(reversed(manifest.extraction_lineage)),
        patch_lineage=tuple(reversed(manifest.patch_lineage)),
        schema_version_visibility=tuple(reversed(manifest.schema_version_visibility)),
        dependency_visibility=tuple(reversed(manifest.dependency_visibility)),
        trust_visibility=tuple(reversed(manifest.trust_visibility)),
        validation_visibility=tuple(reversed(manifest.validation_visibility)),
        prohibited_domain_visibility=tuple(reversed(manifest.prohibited_domain_visibility)),
        unsupported_state_visibility=tuple(reversed(manifest.unsupported_state_visibility)),
        diagnostics_visibility=tuple(reversed(manifest.diagnostics_visibility)),
    )

    assert serialize_refresh_manifest(manifest) == serialize_refresh_manifest(reordered)
    assert hash_refresh_manifest(manifest) == hash_refresh_manifest(reordered)
    exported = export_refresh_manifest(reordered)
    assert [item["state"] for item in exported["states"]] == [
        REFRESH_MANIFEST_STATE_SUPPORTED,
        REFRESH_MANIFEST_STATE_UNSUPPORTED,
        REFRESH_MANIFEST_STATE_BLOCKED,
        REFRESH_MANIFEST_STATE_UNKNOWN,
        REFRESH_MANIFEST_STATE_STALE,
        REFRESH_MANIFEST_STATE_PROHIBITED,
    ]
    visibility = exported["unsupported_state_visibility"][0]
    assert visibility["unsupported_states"] == ["v4_1_refresh_manifest_state_unsupported_source_provider"]
    assert visibility["unknown_states"] == ["v4_1_refresh_manifest_state_unknown_future_source"]
    assert visibility["blocked_states"] == ["v4_1_refresh_manifest_state_blocked_dependency_gap"]
    assert visibility["stale_states"] == ["v4_1_refresh_manifest_state_stale_lifecycle_dependency"]
    assert visibility["prohibited_states"] == ["v4_1_refresh_manifest_state_prohibited_execution_domain"]


def test_v4_1_visibility_preserves_unsupported_prohibited_and_diagnostics_state():
    manifest = default_refresh_manifest()
    validation = validate_refresh_manifest_visibility(manifest)
    counts = count_refresh_manifest_states(manifest.states)

    assert counts[REFRESH_MANIFEST_STATE_SUPPORTED] == 1
    assert counts[REFRESH_MANIFEST_STATE_UNSUPPORTED] == 1
    assert counts[REFRESH_MANIFEST_STATE_BLOCKED] == 1
    assert counts[REFRESH_MANIFEST_STATE_UNKNOWN] == 1
    assert counts[REFRESH_MANIFEST_STATE_STALE] == 1
    assert counts[REFRESH_MANIFEST_STATE_PROHIBITED] == 1
    assert counts["invalid"] == 0
    assert validation["valid"] is True
    assert validation["unsupported_states_visible"] is True
    assert validation["unknown_states_visible"] is True
    assert validation["blocked_states_visible"] is True
    assert validation["prohibited_states_visible"] is True
    assert validation["stale_states_visible"] is True
    assert validation["prohibited_domains_visible"] is True
    assert validation["prohibited_domain_visibility_count"] == len(PROHIBITED_REFRESH_DOMAINS)
    assert validation["hidden_state_count"] == 0
    assert validation["corrective_state_count"] == 0
    assert validation["state_execution_semantics_count"] == 0
    assert validation["hidden_visibility_count"] == 0
    assert validation["corrective_visibility_count"] == 0


def test_v4_1_provenance_lineage_replay_and_rollback_continuity_are_preserved():
    manifest = default_refresh_manifest()
    provenance = validate_refresh_manifest_provenance_continuity(manifest)
    lineage = validate_refresh_manifest_lineage_continuity(manifest)

    with pytest.raises(FrozenInstanceError):
        manifest.source_lineage[0].inferred_source_allowed = True

    assert provenance["valid"] is True
    assert provenance["provenance_visible"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["no_inferred_provenance"] is True
    assert provenance["hidden_source_resolution_absent"] is True
    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["replay_safe"] is True
    assert lineage["rollback_safe"] is True
    assert lineage["source_lineage_count"] == 1
    assert lineage["extraction_lineage_count"] == 1
    assert lineage["patch_lineage_count"] == 1
    assert lineage["rollback_reference_count"] == 3
    assert lineage["replay_reference_count"] == 3


def test_v4_1_non_execution_validation_blocks_execution_production_and_planner_flags():
    manifest = default_refresh_manifest()
    contaminated = replace(
        manifest,
        refresh_execution_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_refresh_manifest_non_execution(contaminated)

    assert validate_refresh_manifest_non_execution(manifest)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 3
    assert validation["refresh_execution_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_integrity_validation_blocks_hidden_correction_and_execution_semantics():
    manifest = default_refresh_manifest()
    hidden_state = replace(
        manifest.states[1],
        hidden=True,
        fail_visible=False,
        executable=True,
        automatic_resolution_enabled=True,
    )
    corrective_diagnostics = replace(
        manifest.diagnostics_visibility[0],
        remediation_enabled=True,
        silent_fallback_enabled=True,
    )
    contaminated = replace(
        manifest,
        states=(manifest.states[0], hidden_state, *manifest.states[2:]),
        diagnostics_visibility=(corrective_diagnostics,),
    )
    validation = validate_refresh_manifest_integrity(contaminated)

    assert validate_refresh_manifest_integrity(manifest)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_state_count"] == 1
    assert validation["visibility_validation"]["corrective_state_count"] == 1
    assert validation["visibility_validation"]["state_execution_semantics_count"] == 1
    assert validation["visibility_validation"]["corrective_visibility_count"] == 1


def test_v4_1_refresh_manifest_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_refresh_manifest_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_REFRESH_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["silent_fallback_absent"] is True
    assert diagnostics["automatic_recovery_absent"] is True


def test_v4_1_refresh_manifest_reports_contain_required_evidence_and_boundaries():
    report = build_v4_1_refresh_manifest_foundations_report()
    diagnostics_report = build_v4_1_refresh_manifest_diagnostics_report()

    assert report["foundation_status"] == V4_1_REFRESH_MANIFEST_STATUS_STABLE
    assert report["refresh_governance_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["deterministic_equality_verified"] is True
    assert report["summary"]["deterministic_visibility_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["provenance_continuity_verified"] is True
    assert report["summary"]["replay_continuity_verified"] is True
    assert report["summary"]["rollback_continuity_verified"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["production_consumption_disabled_validated"] is True
    assert report["summary"]["planner_integration_disabled_validated"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert "No execution behavior exists." in report["explicit_prohibitions"]
    assert "No orchestration exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
