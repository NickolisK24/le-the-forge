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

from orchestration_governance.orchestration_manifest_diagnostics import (  # noqa: E402
    aggregate_blocked_states,
    aggregate_conflicting_metadata_states,
    aggregate_missing_metadata_states,
    aggregate_prohibited_states,
    aggregate_stale_metadata_states,
    aggregate_unsupported_states,
    build_orchestration_manifest_diagnostics,
    count_orchestration_capability_states,
    orchestration_manifest_identity_key,
    orchestration_manifests_equal,
    validate_orchestration_continuity_metadata,
    validate_orchestration_explainability,
    validate_orchestration_manifest_non_execution,
    validate_orchestration_manifest_visibility,
)
from orchestration_governance.orchestration_manifest_hashing import (  # noqa: E402
    hash_orchestration_capability_visibility,
    hash_orchestration_continuity_metadata,
    hash_orchestration_manifest,
    hash_orchestration_manifest_identity,
)
from orchestration_governance.orchestration_manifest_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_MANIFEST_PROHIBITIONS,
    ORCHESTRATION_STATE_BLOCKED,
    ORCHESTRATION_STATE_CONFLICTING_METADATA,
    ORCHESTRATION_STATE_MISSING_METADATA,
    ORCHESTRATION_STATE_PROHIBITED,
    ORCHESTRATION_STATE_STALE_METADATA,
    ORCHESTRATION_STATE_SUPPORTED,
    ORCHESTRATION_STATE_UNKNOWN,
    ORCHESTRATION_STATE_UNSUPPORTED,
    PROHIBITED_ORCHESTRATION_CAPABILITIES,
    V4_3_ORCHESTRATION_MANIFEST_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_MANIFEST_STATUS_STABLE,
    default_orchestration_manifest,
)
from orchestration_governance.orchestration_manifest_serialization import (  # noqa: E402
    export_orchestration_manifest,
    serialize_orchestration_manifest,
)
from scripts.report_v4_3_orchestration_manifest_foundations import (  # noqa: E402
    build_v4_3_orchestration_manifest_foundations_report,
)


def test_v4_3_orchestration_manifest_models_are_immutable_and_non_executable():
    manifest = default_orchestration_manifest()

    with pytest.raises(FrozenInstanceError):
        manifest.orchestration_execution_enabled = True

    assert manifest.identity.schema_version == V4_3_ORCHESTRATION_MANIFEST_SCHEMA_VERSION
    assert manifest.non_executable is True
    assert manifest.descriptive_only is True
    assert manifest.execution_authorized is False
    assert manifest.orchestration_execution_enabled is False
    assert manifest.runtime_execution_enabled is False
    assert manifest.routing_execution_enabled is False
    assert manifest.scheduling_execution_enabled is False
    assert manifest.sequencing_execution_enabled is False
    assert manifest.dependency_resolution_enabled is False
    assert manifest.orchestration_remediation_enabled is False
    assert manifest.orchestration_repair_enabled is False
    assert manifest.orchestration_inference_enabled is False
    assert manifest.orchestration_authorization_enabled is False
    assert manifest.readiness_approval_enabled is False
    assert manifest.planner_integration_enabled is False
    assert manifest.production_consumption_enabled is False
    assert manifest.automatic_correction_enabled is False
    assert manifest.automatic_rollback_enabled is False
    assert manifest.runtime_mutation_enabled is False
    assert manifest.operational_state_mutation_enabled is False
    assert manifest.recommendation_enabled is False
    assert manifest.ranking_enabled is False
    assert manifest.scoring_enabled is False
    assert manifest.selection_enabled is False
    assert manifest.hidden_orchestration_behavior_enabled is False
    assert manifest.implicit_execution_pathway_enabled is False
    assert manifest.orchestration_engine_enabled is False
    assert manifest.state_machine_execution_enabled is False
    assert all(not capability.orchestration_execution_enabled for capability in manifest.capability_visibility)
    assert all(not capability.dependency_resolution_enabled for capability in manifest.capability_visibility)
    assert all(not diagnostic.remediation_enabled for diagnostic in manifest.diagnostics)
    assert all(not summary.recommendation_enabled for summary in manifest.explainability_summaries)


def test_v4_3_orchestration_manifest_identity_key_is_stable():
    manifest = default_orchestration_manifest()

    assert orchestration_manifest_identity_key(manifest) == (
        "v4_3.governance_safe_orchestration_manifest_foundations.1"
        "|v4_3_phase_1_governance_safe_orchestration_manifest_foundations"
        "|v4_3_orchestration_manifest_primary"
        "|v4.3.0-phase-1"
        "|v4_2_closeout_and_v4_3_readiness_report"
        "|v4_3_orchestration_manifest_provenance_primary"
        "|v4_3_orchestration_manifest_lineage_primary"
    )


def test_v4_3_deterministic_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_manifest()
    second = default_orchestration_manifest()

    assert first == second
    assert hash(first) == hash(second)
    assert orchestration_manifests_equal(first, second)
    assert serialize_orchestration_manifest(first) == serialize_orchestration_manifest(second)
    assert hash_orchestration_manifest(first) == hash_orchestration_manifest(second)
    assert hash_orchestration_manifest_identity(first.identity) == hash_orchestration_manifest_identity(second.identity)
    exported = json.loads(serialize_orchestration_manifest(first))
    assert exported["non_executable"] is True
    assert exported["orchestration_execution_enabled"] is False
    assert exported["runtime_execution_enabled"] is False


def test_v4_3_deterministic_ordering_stability_survives_reordered_collections():
    manifest = default_orchestration_manifest()
    reordered = replace(
        manifest,
        capability_visibility=tuple(reversed(manifest.capability_visibility)),
        boundary_visibility=tuple(reversed(manifest.boundary_visibility)),
        continuity_metadata=tuple(reversed(manifest.continuity_metadata)),
        diagnostics=tuple(reversed(manifest.diagnostics)),
        explainability_summaries=tuple(reversed(manifest.explainability_summaries)),
    )

    assert serialize_orchestration_manifest(manifest) == serialize_orchestration_manifest(reordered)
    assert hash_orchestration_manifest(manifest) == hash_orchestration_manifest(reordered)
    exported = export_orchestration_manifest(reordered)
    assert [item["visibility_state"] for item in exported["capability_visibility"]] == [
        ORCHESTRATION_STATE_SUPPORTED,
        ORCHESTRATION_STATE_UNSUPPORTED,
        ORCHESTRATION_STATE_BLOCKED,
        ORCHESTRATION_STATE_STALE_METADATA,
        ORCHESTRATION_STATE_MISSING_METADATA,
        ORCHESTRATION_STATE_CONFLICTING_METADATA,
        ORCHESTRATION_STATE_PROHIBITED,
    ]
    assert exported["prohibited_state_visibility"]["prohibited_capabilities"] == sorted(
        PROHIBITED_ORCHESTRATION_CAPABILITIES
    )


def test_v4_3_orchestration_capability_visibility_is_fail_visible():
    manifest = default_orchestration_manifest()
    validation = validate_orchestration_manifest_visibility(manifest)
    counts = count_orchestration_capability_states(manifest.capability_visibility)

    assert counts[ORCHESTRATION_STATE_SUPPORTED] == 1
    assert counts[ORCHESTRATION_STATE_UNSUPPORTED] == 1
    assert counts[ORCHESTRATION_STATE_BLOCKED] == 1
    assert counts[ORCHESTRATION_STATE_STALE_METADATA] == 1
    assert counts[ORCHESTRATION_STATE_MISSING_METADATA] == 1
    assert counts[ORCHESTRATION_STATE_CONFLICTING_METADATA] == 1
    assert counts[ORCHESTRATION_STATE_PROHIBITED] == 1
    assert counts[ORCHESTRATION_STATE_UNKNOWN] == 0
    assert counts["invalid"] == 0
    assert validation["valid"] is True
    assert validation["unsupported_states_visible"] is True
    assert validation["blocked_states_visible"] is True
    assert validation["missing_metadata_visible"] is True
    assert validation["conflicting_metadata_visible"] is True
    assert validation["stale_metadata_visible"] is True
    assert validation["unknown_states_visible"] is True
    assert validation["prohibited_states_visible"] is True
    assert validation["prohibited_capabilities_visible"] is True
    assert validation["hidden_capability_count"] == 0
    assert validation["corrective_capability_count"] == 0
    assert validation["corrective_diagnostic_count"] == 0


def test_v4_3_continuity_and_explainability_visibility_are_preserved():
    manifest = default_orchestration_manifest()
    continuity = validate_orchestration_continuity_metadata(manifest)
    explainability = validate_orchestration_explainability(manifest)

    with pytest.raises(FrozenInstanceError):
        manifest.continuity_metadata[0].automatic_rollback_enabled = True

    assert continuity["valid"] is True
    assert continuity["continuity_metadata_count"] == 3
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert continuity["explainability_continuity_preserved"] is True
    assert continuity["corrective_continuity_count"] == 0
    assert explainability["valid"] is True
    assert explainability["explainability_summary_count"] == 5
    assert "blocked_state" in explainability["explainability_categories"]
    assert "unsupported_state" in explainability["explainability_categories"]
    assert "prohibited_state" in explainability["explainability_categories"]
    assert "capability_unavailable" in explainability["explainability_categories"]
    assert "governance_boundary" in explainability["explainability_categories"]
    assert explainability["corrective_explainability_count"] == 0


def test_v4_3_replay_and_rollback_safe_evidence_generation_is_deterministic():
    manifest = default_orchestration_manifest()
    continuity_hashes = [
        hash_orchestration_continuity_metadata(metadata) for metadata in manifest.continuity_metadata
    ]
    capability_hashes = [
        hash_orchestration_capability_visibility(visibility) for visibility in manifest.capability_visibility
    ]

    assert continuity_hashes == [
        hash_orchestration_continuity_metadata(metadata) for metadata in manifest.continuity_metadata
    ]
    assert capability_hashes == [
        hash_orchestration_capability_visibility(visibility) for visibility in manifest.capability_visibility
    ]
    assert all(metadata.replay_safe for metadata in manifest.continuity_metadata)
    assert all(metadata.rollback_safe for metadata in manifest.continuity_metadata)
    assert manifest.metadata.replay_safe_evidence is True
    assert manifest.metadata.rollback_safe_evidence is True


def test_v4_3_prohibited_unsupported_blocked_and_metadata_aggregation_are_deterministic():
    manifest = default_orchestration_manifest()
    diagnostics = build_orchestration_manifest_diagnostics(manifest)

    assert aggregate_unsupported_states(manifest) == diagnostics["unsupported_state_ids"]
    assert aggregate_blocked_states(manifest) == diagnostics["blocked_state_ids"]
    assert aggregate_prohibited_states(manifest) == diagnostics["prohibited_state_ids"]
    assert aggregate_missing_metadata_states(manifest) == diagnostics["missing_metadata_ids"]
    assert aggregate_conflicting_metadata_states(manifest) == diagnostics["conflicting_metadata_ids"]
    assert aggregate_stale_metadata_states(manifest) == diagnostics["stale_metadata_ids"]
    assert len(diagnostics["prohibited_state_ids"]) >= len(PROHIBITED_ORCHESTRATION_CAPABILITIES)
    assert diagnostics["fail_visible_diagnostic_count"] == len(manifest.diagnostics)
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["approval_absent"] is True
    assert diagnostics["execution_absent"] is True
    assert diagnostics["selection_systems_absent"] is True


def test_v4_3_non_execution_validation_blocks_operational_flags():
    manifest = default_orchestration_manifest()
    contaminated = replace(
        manifest,
        orchestration_execution_enabled=True,
        runtime_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        sequencing_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_orchestration_manifest_non_execution(contaminated)

    assert validate_orchestration_manifest_non_execution(manifest)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 8
    assert validation["orchestration_execution_disabled"] is False
    assert validation["runtime_execution_disabled"] is False
    assert validation["routing_execution_disabled"] is False
    assert validation["scheduling_execution_disabled"] is False
    assert validation["sequencing_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_3_report_contains_required_deterministic_evidence_and_boundaries():
    report = build_v4_3_orchestration_manifest_foundations_report()

    assert report["foundation_status"] == V4_3_ORCHESTRATION_MANIFEST_STATUS_STABLE
    assert report["orchestration_mode"] == "descriptive_only_non_executable"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["deterministic_ordering_verified"] is True
    assert report["summary"]["capability_visibility_verified"] is True
    assert report["summary"]["continuity_visibility_verified"] is True
    assert report["summary"]["explainability_visibility_verified"] is True
    assert report["summary"]["replay_safe_evidence_generated"] is True
    assert report["summary"]["rollback_safe_evidence_generated"] is True
    assert report["summary"]["prohibited_state_visibility_verified"] is True
    assert report["summary"]["unsupported_state_visibility_verified"] is True
    assert report["summary"]["blocked_state_visibility_verified"] is True
    assert report["summary"]["missing_metadata_visibility_verified"] is True
    assert report["summary"]["conflicting_metadata_visibility_verified"] is True
    assert report["summary"]["stale_metadata_visibility_verified"] is True
    assert report["summary"]["fail_visible_diagnostics_verified"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["runtime_execution_disabled"] is True
    assert report["summary"]["routing_execution_disabled"] is True
    assert report["summary"]["scheduling_execution_disabled"] is True
    assert report["summary"]["sequencing_execution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert report["summary"]["orchestration_engine_absent"] is True
    assert report["summary"]["state_machine_execution_absent"] is True
    assert "No orchestration execution exists." in EXPLICIT_ORCHESTRATION_MANIFEST_PROHIBITIONS
    assert "No orchestration engine exists." in report["explicit_prohibitions"]
    assert "No orchestration state machine executes." in report["explicit_prohibitions"]
