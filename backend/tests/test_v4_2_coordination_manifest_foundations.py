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

from refresh_coordination.coordination_manifest_diagnostics import (  # noqa: E402
    aggregate_blocked_coordination,
    aggregate_prohibited_states,
    aggregate_unsupported_states,
    build_coordination_manifest_diagnostics,
    coordination_manifest_identity_key,
    coordination_manifests_equal,
    count_coordination_dependency_states,
    validate_coordination_continuity_visibility,
    validate_coordination_lineage_continuity,
    validate_coordination_manifest_non_execution,
    validate_coordination_manifest_visibility,
)
from refresh_coordination.coordination_manifest_hashing import (  # noqa: E402
    hash_coordination_continuity,
    hash_coordination_dependency,
    hash_coordination_lineage,
    hash_coordination_manifest,
    hash_coordination_manifest_identity,
)
from refresh_coordination.coordination_manifest_models import (  # noqa: E402
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_SUPPORTED,
    COORDINATION_STATE_UNKNOWN,
    COORDINATION_STATE_UNSUPPORTED,
    EXPLICIT_COORDINATION_MANIFEST_PROHIBITIONS,
    PROHIBITED_COORDINATION_CAPABILITIES,
    V4_2_COORDINATION_MANIFEST_SCHEMA_VERSION,
    V4_2_COORDINATION_MANIFEST_STATUS_STABLE,
    default_coordination_manifest,
)
from refresh_coordination.coordination_manifest_serialization import (  # noqa: E402
    export_coordination_manifest,
    serialize_coordination_manifest,
)
from scripts.report_v4_2_coordination_manifest_foundations import (  # noqa: E402
    build_v4_2_coordination_manifest_foundations_report,
)


def test_v4_2_coordination_manifest_models_are_immutable_and_non_executable():
    manifest = default_coordination_manifest()

    with pytest.raises(FrozenInstanceError):
        manifest.refresh_execution_enabled = True

    assert manifest.identity.schema_version == V4_2_COORDINATION_MANIFEST_SCHEMA_VERSION
    assert manifest.non_executable is True
    assert manifest.descriptive_only is True
    assert manifest.orchestration_execution_enabled is False
    assert manifest.refresh_execution_enabled is False
    assert manifest.planner_integration_enabled is False
    assert manifest.production_consumption_enabled is False
    assert manifest.production_bundle_consumption_enabled is False
    assert manifest.runtime_mutation_enabled is False
    assert manifest.remediation_enabled is False
    assert manifest.automatic_correction_enabled is False
    assert manifest.automatic_rollback_enabled is False
    assert manifest.dependency_resolution_enabled is False
    assert manifest.authorization_enabled is False
    assert manifest.approval_enabled is False
    assert manifest.recommendation_enabled is False
    assert manifest.ranking_enabled is False
    assert manifest.scoring_enabled is False
    assert manifest.selection_enabled is False
    assert manifest.operational_execution_enabled is False
    assert manifest.hidden_operational_behavior_enabled is False
    assert manifest.implicit_execution_pathway_enabled is False
    assert all(not reference.refresh_execution_enabled for reference in manifest.dependency_references)
    assert all(not reference.dependency_resolution_enabled for reference in manifest.dependency_references)
    assert all(not reference.lineage_repair_enabled for reference in manifest.lineage_references)
    assert all(not reference.automatic_rollback_enabled for reference in manifest.continuity_references)
    assert all(not diagnostic.remediation_enabled for diagnostic in manifest.diagnostics)


def test_v4_2_coordination_manifest_identity_key_is_stable():
    manifest = default_coordination_manifest()

    assert coordination_manifest_identity_key(manifest) == (
        "v4_2.refresh_coordination_manifest_foundations.1"
        "|v4_2_phase_1_refresh_coordination_manifest_foundations"
        "|v4_2_coordination_manifest_primary"
        "|v4.2.0-phase-1"
        "|v4_1_closeout_and_v4_2_readiness_report"
        "|v4_2_coordination_manifest_provenance_primary"
        "|v4_2_coordination_manifest_lineage_primary"
    )


def test_v4_2_deterministic_serialization_hashing_and_equality_are_stable():
    first = default_coordination_manifest()
    second = default_coordination_manifest()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_manifests_equal(first, second)
    assert serialize_coordination_manifest(first) == serialize_coordination_manifest(second)
    assert hash_coordination_manifest(first) == hash_coordination_manifest(second)
    assert hash_coordination_manifest_identity(first.identity) == hash_coordination_manifest_identity(second.identity)
    assert json.loads(serialize_coordination_manifest(first))["non_executable"] is True


def test_v4_2_deterministic_ordering_stability_survives_reordered_collections():
    manifest = default_coordination_manifest()
    reordered = replace(
        manifest,
        dependency_references=tuple(reversed(manifest.dependency_references)),
        lineage_references=tuple(reversed(manifest.lineage_references)),
        continuity_references=tuple(reversed(manifest.continuity_references)),
        diagnostics=tuple(reversed(manifest.diagnostics)),
    )

    assert serialize_coordination_manifest(manifest) == serialize_coordination_manifest(reordered)
    assert hash_coordination_manifest(manifest) == hash_coordination_manifest(reordered)
    exported = export_coordination_manifest(reordered)
    assert [item["dependency_state"] for item in exported["dependency_references"]] == [
        COORDINATION_STATE_SUPPORTED,
        COORDINATION_STATE_UNSUPPORTED,
        COORDINATION_STATE_BLOCKED,
        COORDINATION_STATE_STALE,
        COORDINATION_STATE_PROHIBITED,
    ]
    assert exported["prohibited_state_visibility"]["prohibited_capabilities"] == sorted(
        PROHIBITED_COORDINATION_CAPABILITIES
    )


def test_v4_2_coordination_dependency_visibility_is_fail_visible():
    manifest = default_coordination_manifest()
    validation = validate_coordination_manifest_visibility(manifest)
    counts = count_coordination_dependency_states(manifest.dependency_references)

    assert counts[COORDINATION_STATE_SUPPORTED] == 1
    assert counts[COORDINATION_STATE_UNSUPPORTED] == 1
    assert counts[COORDINATION_STATE_BLOCKED] == 1
    assert counts[COORDINATION_STATE_STALE] == 1
    assert counts[COORDINATION_STATE_PROHIBITED] == 1
    assert counts[COORDINATION_STATE_UNKNOWN] == 0
    assert counts["invalid"] == 0
    assert validation["valid"] is True
    assert validation["unsupported_states_visible"] is True
    assert validation["blocked_states_visible"] is True
    assert validation["stale_states_visible"] is True
    assert validation["unknown_states_visible"] is True
    assert validation["prohibited_states_visible"] is True
    assert validation["prohibited_capabilities_visible"] is True
    assert validation["hidden_dependency_count"] == 0
    assert validation["corrective_dependency_count"] == 0
    assert validation["corrective_diagnostic_count"] == 0


def test_v4_2_lineage_and_continuity_visibility_are_preserved():
    manifest = default_coordination_manifest()
    lineage = validate_coordination_lineage_continuity(manifest)
    continuity = validate_coordination_continuity_visibility(manifest)

    with pytest.raises(FrozenInstanceError):
        manifest.lineage_references[0].inferred_lineage_enabled = True

    assert lineage["valid"] is True
    assert lineage["lineage_reference_count"] == 2
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["identity_lineage_visible"] is True
    assert lineage["hidden_lineage_resolution_count"] == 0
    assert continuity["valid"] is True
    assert continuity["continuity_reference_count"] == 3
    assert continuity["continuity_preserved"] is True
    assert continuity["continuity_visible"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_safe"] is True
    assert continuity["lineage_safe"] is True


def test_v4_2_replay_and_rollback_safe_evidence_generation_is_deterministic():
    manifest = default_coordination_manifest()
    continuity_hashes = [hash_coordination_continuity(reference) for reference in manifest.continuity_references]
    dependency_hashes = [hash_coordination_dependency(reference) for reference in manifest.dependency_references]
    lineage_hashes = [hash_coordination_lineage(reference) for reference in manifest.lineage_references]

    assert continuity_hashes == [hash_coordination_continuity(reference) for reference in manifest.continuity_references]
    assert dependency_hashes == [hash_coordination_dependency(reference) for reference in manifest.dependency_references]
    assert lineage_hashes == [hash_coordination_lineage(reference) for reference in manifest.lineage_references]
    assert all(reference.replay_safe for reference in manifest.continuity_references)
    assert all(reference.rollback_safe for reference in manifest.continuity_references)
    assert manifest.metadata.replay_safe_evidence is True
    assert manifest.metadata.rollback_safe_evidence is True


def test_v4_2_prohibited_unsupported_and_blocked_aggregation_are_deterministic():
    manifest = default_coordination_manifest()
    diagnostics = build_coordination_manifest_diagnostics(manifest)

    assert aggregate_unsupported_states(manifest) == diagnostics["unsupported_state_ids"]
    assert aggregate_blocked_coordination(manifest) == diagnostics["blocked_coordination_ids"]
    assert aggregate_prohibited_states(manifest) == diagnostics["prohibited_state_ids"]
    assert len(diagnostics["prohibited_state_ids"]) >= len(PROHIBITED_COORDINATION_CAPABILITIES)
    assert diagnostics["fail_visible_diagnostic_count"] == len(manifest.diagnostics)
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["approval_absent"] is True
    assert diagnostics["execution_absent"] is True


def test_v4_2_non_execution_validation_blocks_execution_planner_production_and_mutation_flags():
    manifest = default_coordination_manifest()
    contaminated = replace(
        manifest,
        orchestration_execution_enabled=True,
        refresh_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_coordination_manifest_non_execution(contaminated)

    assert validate_coordination_manifest_non_execution(manifest)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 5
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_report_contains_required_deterministic_evidence_and_boundaries():
    report = build_v4_2_coordination_manifest_foundations_report()

    assert report["foundation_status"] == V4_2_COORDINATION_MANIFEST_STATUS_STABLE
    assert report["coordination_mode"] == "descriptive_only_non_executable"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["deterministic_ordering_verified"] is True
    assert report["summary"]["dependency_visibility_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["continuity_visibility_verified"] is True
    assert report["summary"]["replay_safe_evidence_generated"] is True
    assert report["summary"]["rollback_safe_evidence_generated"] is True
    assert report["summary"]["prohibited_state_visibility_verified"] is True
    assert report["summary"]["unsupported_state_visibility_verified"] is True
    assert report["summary"]["fail_visible_diagnostics_verified"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert "No orchestration execution exists." in EXPLICIT_COORDINATION_MANIFEST_PROHIBITIONS
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No runtime mutation exists." in report["explicit_prohibitions"]
