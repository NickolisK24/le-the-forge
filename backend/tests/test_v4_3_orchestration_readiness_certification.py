from __future__ import annotations

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

from orchestration_governance.orchestration_continuity_certification import (  # noqa: E402
    default_orchestration_continuity_integrity_certification,
    validate_continuity_non_execution_authorization_decision,
    validate_integrity_certifications,
)
from orchestration_governance.orchestration_continuity_hashing import (  # noqa: E402
    hash_orchestration_continuity_integrity_certification,
)
from orchestration_governance.orchestration_readiness_certification import (  # noqa: E402
    build_readiness_certification_diagnostics,
    default_orchestration_readiness_certification,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_approval_count,
    enabled_orchestration_authorization_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    readiness_certification_identity_key,
    readiness_certifications_equal,
    validate_readiness_certification_identity,
    validate_readiness_certifications,
    validate_readiness_explainability,
    validate_readiness_non_execution_authorization_approval_decision,
    validate_state_readiness_visibility,
)
from orchestration_governance.orchestration_readiness_hashing import (  # noqa: E402
    hash_orchestration_readiness_certification,
    hash_readiness_certification_record,
    hash_readiness_diagnostic,
    hash_readiness_explainability,
    hash_readiness_state_summary,
)
from orchestration_governance.orchestration_readiness_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS,
    READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY,
    READINESS_LAYER_IDS,
    READINESS_STATE_BLOCKED,
    READINESS_STATE_CONFLICTING,
    READINESS_STATE_PROHIBITED,
    READINESS_STATE_STALE,
    READINESS_STATE_UNSUPPORTED,
    V4_3_ORCHESTRATION_READINESS_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_READINESS_STATUS_STABLE,
)
from orchestration_governance.orchestration_readiness_serialization import (  # noqa: E402
    export_orchestration_readiness_certification,
    serialize_orchestration_readiness_certification,
)
from scripts.report_v4_3_orchestration_readiness_certification import (  # noqa: E402
    build_v4_3_orchestration_readiness_certification_report,
)


def test_v4_3_readiness_models_are_immutable_and_non_operational():
    certification = default_orchestration_readiness_certification()
    continuity = default_orchestration_continuity_integrity_certification()

    with pytest.raises(FrozenInstanceError):
        certification.orchestration_approval_enabled = True

    assert certification.identity.schema_version == V4_3_ORCHESTRATION_READINESS_SCHEMA_VERSION
    assert certification.identity.source_continuity_integrity_reference == continuity.identity.certification_id
    assert certification.identity.source_continuity_integrity_hash_reference == (
        hash_orchestration_continuity_integrity_certification(continuity)
    )
    assert certification.non_executable is True
    assert certification.non_authorizing is True
    assert certification.non_approving is True
    assert certification.non_decisioning is True
    assert certification.descriptive_only is True
    assert enabled_coordination_execution_count(certification) == 0
    assert enabled_transition_execution_count(certification) == 0
    assert enabled_policy_enforcement_count(certification) == 0
    assert enabled_operational_capability_count(certification) == 0
    assert enabled_orchestration_decision_count(certification) == 0
    assert enabled_orchestration_recommendation_count(certification) == 0
    assert enabled_orchestration_authorization_count(certification) == 0
    assert enabled_orchestration_approval_count(certification) == 0


def test_v4_3_readiness_identity_key_is_stable():
    certification = default_orchestration_readiness_certification()
    continuity = default_orchestration_continuity_integrity_certification()

    assert readiness_certification_identity_key(certification) == (
        "v4_3.orchestration_readiness_certification.1"
        "|v4_3_orchestration_readiness_certification_primary"
        "|v4.3.0-phase-9"
        f"|{continuity.identity.source_manifest_reference}"
        f"|{continuity.identity.source_manifest_hash_reference}"
        f"|{continuity.identity.source_topology_reference}"
        f"|{continuity.identity.source_topology_hash_reference}"
        f"|{continuity.identity.source_capability_reference}"
        f"|{continuity.identity.source_capability_hash_reference}"
        f"|{continuity.identity.source_policy_reference}"
        f"|{continuity.identity.source_policy_hash_reference}"
        f"|{continuity.identity.source_transition_reference}"
        f"|{continuity.identity.source_transition_hash_reference}"
        f"|{continuity.identity.source_coordination_reference}"
        f"|{continuity.identity.source_coordination_hash_reference}"
        f"|{continuity.identity.source_diagnostics_reference}"
        f"|{continuity.identity.source_diagnostics_hash_reference}"
        f"|{continuity.identity.certification_id}"
        f"|{hash_orchestration_continuity_integrity_certification(continuity)}"
        "|v4_3_readiness_governance_primary"
    )


def test_v4_3_readiness_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_readiness_certification()
    second = default_orchestration_readiness_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert readiness_certifications_equal(first, second)
    assert serialize_orchestration_readiness_certification(
        first
    ) == serialize_orchestration_readiness_certification(second)
    assert hash_orchestration_readiness_certification(first) == hash_orchestration_readiness_certification(
        second
    )


def test_v4_3_readiness_ordering_survives_reordered_collections():
    certification = default_orchestration_readiness_certification()
    reordered = replace(
        certification,
        readiness_certifications=tuple(reversed(certification.readiness_certifications)),
        state_readiness_summaries=tuple(reversed(certification.state_readiness_summaries)),
        diagnostics=tuple(reversed(certification.diagnostics)),
        explainability_summaries=tuple(reversed(certification.explainability_summaries)),
    )

    assert serialize_orchestration_readiness_certification(
        certification
    ) == serialize_orchestration_readiness_certification(reordered)
    assert hash_orchestration_readiness_certification(
        certification
    ) == hash_orchestration_readiness_certification(reordered)
    exported = export_orchestration_readiness_certification(reordered)
    assert [item["state_type"] for item in exported["state_readiness_summaries"]] == [
        READINESS_STATE_PROHIBITED,
        READINESS_STATE_UNSUPPORTED,
        READINESS_STATE_BLOCKED,
        READINESS_STATE_STALE,
        READINESS_STATE_CONFLICTING,
    ]


def test_v4_3_readiness_validation_certifies_architectural_closeout_planning_readiness():
    certification = default_orchestration_readiness_certification()
    identity = validate_readiness_certification_identity(certification)
    readiness = validate_readiness_certifications(certification)

    assert identity["valid"] is True
    assert identity["source_hash_mismatches"] == ()
    assert readiness["valid"] is True
    assert readiness["readiness_gap_count"] == 0
    assert readiness["governance_instability_count"] == 0
    assert readiness["continuity_failure_count"] == 0
    assert readiness["integrity_failure_count"] == 0
    assert readiness["readiness_classification"] == READINESS_CLASSIFICATION_ARCHITECTURAL_CLOSEOUT_PLANNING_READY
    assert readiness["replay_safe_readiness_status"] is True
    assert readiness["rollback_safe_readiness_status"] is True
    assert readiness["governance_readiness_visible"] is True
    assert readiness["continuity_readiness_visible"] is True
    assert readiness["integrity_readiness_visible"] is True


def test_v4_3_readiness_gap_and_governance_instability_visibility_detects_failures():
    certification = default_orchestration_readiness_certification()
    contaminated_record = replace(
        certification.readiness_certifications[0],
        readiness_gap_ids=("missing_closeout_readiness_evidence",),
        governance_instability_ids=("unstable_governance_chain",),
    )
    contaminated = replace(
        certification,
        readiness_certifications=(contaminated_record,) + certification.readiness_certifications[1:],
    )
    validation = validate_readiness_certifications(contaminated)

    assert validation["valid"] is False
    assert validation["readiness_gap_ids"] == ("missing_closeout_readiness_evidence",)
    assert validation["governance_instability_ids"] == ("unstable_governance_chain",)
    assert validation["readiness_gap_count"] == 1
    assert validation["governance_instability_count"] == 1


def test_v4_3_readiness_continuity_and_integrity_failure_visibility_detects_failures():
    certification = default_orchestration_readiness_certification()
    contaminated_record = replace(
        certification.readiness_certifications[0],
        continuity_failure_ids=("continuity_certification_gap",),
        integrity_failure_ids=("integrity_hash_mismatch",),
    )
    contaminated = replace(
        certification,
        readiness_certifications=(contaminated_record,) + certification.readiness_certifications[1:],
    )
    validation = validate_readiness_certifications(contaminated)

    assert validation["valid"] is False
    assert validation["continuity_failure_ids"] == ("continuity_certification_gap",)
    assert validation["integrity_failure_ids"] == ("integrity_hash_mismatch",)
    assert validation["continuity_failure_count"] == 1
    assert validation["integrity_failure_count"] == 1


def test_v4_3_state_readiness_visibility_is_fail_visible():
    certification = default_orchestration_readiness_certification()
    states = validate_state_readiness_visibility(certification)

    assert states["valid"] is True
    assert states["prohibited_state_readiness_visible"] is True
    assert states["unsupported_state_readiness_visible"] is True
    assert states["blocked_state_readiness_visible"] is True
    assert states["stale_state_readiness_visible"] is True
    assert states["conflicting_state_readiness_visible"] is True
    assert states["prohibited_state_readiness_count"] > 0
    assert states["unsupported_state_readiness_count"] > 0
    assert states["blocked_state_readiness_count"] > 0
    assert states["stale_state_readiness_count"] > 0
    assert states["conflicting_state_readiness_count"] > 0


def test_v4_3_readiness_explainability_is_complete_and_stable():
    certification = default_orchestration_readiness_certification()
    explainability = validate_readiness_explainability(certification)

    assert explainability["valid"] is True
    assert explainability["missing_explainability_categories"] == ()
    assert "orchestration_non_executable" in explainability["explainability_categories"]
    assert "orchestration_authorization_unavailable" in explainability["explainability_categories"]
    assert "orchestration_approval_unavailable" in explainability["explainability_categories"]
    assert "governance_readiness_matters" in explainability["explainability_categories"]
    assert "continuity_readiness_matters" in explainability["explainability_categories"]
    assert "integrity_readiness_matters" in explainability["explainability_categories"]
    assert "replay_safe_evidence_matters" in explainability["explainability_categories"]
    assert "rollback_safe_evidence_matters" in explainability["explainability_categories"]
    assert "fail_visible_readiness_states_exist" in explainability["explainability_categories"]
    assert "operational_orchestration_prohibited" in explainability["explainability_categories"]
    assert explainability["deterministic"] is True
    assert explainability["replay_safe"] is True
    assert explainability["rollback_safe"] is True


def test_v4_3_readiness_non_execution_authorization_approval_and_decision_blocks_operational_flags():
    certification = default_orchestration_readiness_certification()
    contaminated_record = replace(
        certification.readiness_certifications[0],
        authorization_enabled=True,
        approval_enabled=True,
        decision_enabled=True,
        recommendation_enabled=True,
    )
    contaminated = replace(
        certification,
        readiness_certifications=(contaminated_record,) + certification.readiness_certifications[1:],
        orchestration_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        readiness_approval_enabled=True,
        orchestration_decision_enabled=True,
        orchestration_recommendation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_readiness_non_execution_authorization_approval_decision(contaminated)

    assert validate_readiness_non_execution_authorization_approval_decision(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_operational_capability_count"] == 1
    assert validation["enabled_orchestration_authorization_count"] == 1
    assert validation["enabled_orchestration_approval_count"] == 1
    assert validation["enabled_orchestration_decision_count"] == 1
    assert validation["enabled_orchestration_recommendation_count"] == 1
    assert validation["orchestration_execution_disabled"] is False
    assert validation["orchestration_authorization_disabled"] is False
    assert validation["orchestration_approval_disabled"] is False
    assert validation["readiness_approval_disabled"] is False
    assert validation["orchestration_decision_disabled"] is False
    assert validation["orchestration_recommendation_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_readiness_diagnostics_are_descriptive_only():
    certification = default_orchestration_readiness_certification()
    diagnostics = build_readiness_certification_diagnostics(certification)

    assert diagnostics["readiness_certification_count"] == len(certification.readiness_certifications)
    assert diagnostics["readiness_gap_count"] == 0
    assert diagnostics["governance_instability_count"] == 0
    assert diagnostics["continuity_failure_count"] == 0
    assert diagnostics["integrity_failure_count"] == 0
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["explainability_is_descriptive_only"] is True
    assert diagnostics["enabled_coordination_execution_count"] == 0
    assert diagnostics["enabled_transition_execution_count"] == 0
    assert diagnostics["enabled_policy_enforcement_count"] == 0
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["enabled_orchestration_decision_count"] == 0
    assert diagnostics["enabled_orchestration_recommendation_count"] == 0
    assert diagnostics["enabled_orchestration_authorization_count"] == 0
    assert diagnostics["enabled_orchestration_approval_count"] == 0


def test_v4_3_readiness_report_generation_and_hash_are_stable():
    first = build_v4_3_orchestration_readiness_certification_report()
    second = build_v4_3_orchestration_readiness_certification_report()

    assert first == second
    assert first["readiness_certification_status"] == V4_3_ORCHESTRATION_READINESS_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["readiness_ordering_verified"] is True
    assert first["summary"]["state_readiness_ordering_verified"] is True
    assert first["summary"]["diagnostics_ordering_verified"] is True
    assert first["summary"]["explainability_ordering_verified"] is True
    assert first["summary"]["enabled_coordination_execution_count"] == 0
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["enabled_orchestration_decision_count"] == 0
    assert first["summary"]["enabled_orchestration_recommendation_count"] == 0
    assert first["summary"]["enabled_orchestration_authorization_count"] == 0
    assert first["summary"]["enabled_orchestration_approval_count"] == 0
    assert first["summary"]["orchestration_activation_disabled"] is True
    assert first["summary"]["orchestration_approval_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert "No orchestration approval pathway may exist." in EXPLICIT_ORCHESTRATION_READINESS_PROHIBITIONS
    assert "No orchestration approval pathway may exist." in first["explicit_prohibitions"]


def test_v4_3_readiness_component_hashes_are_stable():
    certification = default_orchestration_readiness_certification()

    assert [
        hash_readiness_certification_record(item) for item in certification.readiness_certifications
    ] == [
        hash_readiness_certification_record(item) for item in certification.readiness_certifications
    ]
    assert [hash_readiness_state_summary(item) for item in certification.state_readiness_summaries] == [
        hash_readiness_state_summary(item) for item in certification.state_readiness_summaries
    ]
    assert [hash_readiness_diagnostic(item) for item in certification.diagnostics] == [
        hash_readiness_diagnostic(item) for item in certification.diagnostics
    ]
    assert [
        hash_readiness_explainability(item) for item in certification.explainability_summaries
    ] == [
        hash_readiness_explainability(item) for item in certification.explainability_summaries
    ]


def test_v4_3_readiness_is_compatible_with_phase_1_through_8_artifacts():
    readiness = default_orchestration_readiness_certification()
    continuity = default_orchestration_continuity_integrity_certification()
    continuity_integrity = validate_integrity_certifications(continuity)
    continuity_non_execution = validate_continuity_non_execution_authorization_decision(continuity)

    assert tuple(readiness.metadata.source_layer_ids) == READINESS_LAYER_IDS
    assert readiness.identity.source_manifest_reference == continuity.identity.source_manifest_reference
    assert readiness.identity.source_topology_reference == continuity.identity.source_topology_reference
    assert readiness.identity.source_capability_reference == continuity.identity.source_capability_reference
    assert readiness.identity.source_policy_reference == continuity.identity.source_policy_reference
    assert readiness.identity.source_transition_reference == continuity.identity.source_transition_reference
    assert readiness.identity.source_coordination_reference == continuity.identity.source_coordination_reference
    assert readiness.identity.source_diagnostics_reference == continuity.identity.source_diagnostics_reference
    assert readiness.identity.source_continuity_integrity_reference == continuity.identity.certification_id
    assert readiness.identity.source_continuity_integrity_hash_reference == (
        hash_orchestration_continuity_integrity_certification(continuity)
    )
    assert continuity_integrity["valid"] is True
    assert continuity_non_execution["enabled_orchestration_authorization_count"] == 0
    assert continuity_non_execution["enabled_orchestration_decision_count"] == 0
