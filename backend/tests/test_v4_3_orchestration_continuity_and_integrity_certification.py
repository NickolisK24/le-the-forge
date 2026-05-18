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

from orchestration_governance.orchestration_capability_hashing import (  # noqa: E402
    hash_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_models import (  # noqa: E402
    default_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_continuity_certification import (  # noqa: E402
    build_continuity_integrity_certification_diagnostics,
    continuity_certification_identity_key,
    continuity_certifications_equal,
    default_orchestration_continuity_integrity_certification,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_authorization_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    validate_continuity_certification_identity,
    validate_continuity_certifications,
    validate_continuity_explainability,
    validate_continuity_non_execution_authorization_decision,
    validate_integrity_certifications,
    validate_state_certification_visibility,
)
from orchestration_governance.orchestration_continuity_hashing import (  # noqa: E402
    hash_certification_state_summary,
    hash_continuity_certification_diagnostic,
    hash_continuity_certification_explainability,
    hash_continuity_certification_record,
    hash_integrity_certification_record,
    hash_orchestration_continuity_integrity_certification,
)
from orchestration_governance.orchestration_continuity_models import (  # noqa: E402
    CERTIFICATION_LAYER_IDS,
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_CONFLICTING,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_STALE,
    CERTIFICATION_STATE_UNSUPPORTED,
    EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS,
    V4_3_ORCHESTRATION_CONTINUITY_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_CONTINUITY_STATUS_STABLE,
)
from orchestration_governance.orchestration_continuity_serialization import (  # noqa: E402
    export_orchestration_continuity_integrity_certification,
    serialize_orchestration_continuity_integrity_certification,
)
from orchestration_governance.orchestration_coordination_hashing import (  # noqa: E402
    hash_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_models import (  # noqa: E402
    default_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_diagnostics_aggregation import (  # noqa: E402
    default_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_diagnostics_hashing import (  # noqa: E402
    hash_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_manifest_hashing import (  # noqa: E402
    hash_orchestration_manifest,
)
from orchestration_governance.orchestration_manifest_models import (  # noqa: E402
    default_orchestration_manifest,
)
from orchestration_governance.orchestration_policy_hashing import (  # noqa: E402
    hash_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_policy_models import (  # noqa: E402
    default_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_topology_hashing import (  # noqa: E402
    hash_orchestration_topology,
)
from orchestration_governance.orchestration_topology_models import (  # noqa: E402
    default_orchestration_topology,
)
from orchestration_governance.orchestration_transition_hashing import (  # noqa: E402
    hash_orchestration_transition_visibility,
)
from orchestration_governance.orchestration_transition_models import (  # noqa: E402
    default_orchestration_transition_visibility,
)
from scripts.report_v4_3_orchestration_continuity_and_integrity_certification import (  # noqa: E402
    build_v4_3_orchestration_continuity_and_integrity_certification_report,
)


def test_v4_3_continuity_certification_models_are_immutable_and_non_operational():
    certification = default_orchestration_continuity_integrity_certification()

    with pytest.raises(FrozenInstanceError):
        certification.orchestration_authorization_enabled = True

    assert certification.identity.schema_version == V4_3_ORCHESTRATION_CONTINUITY_SCHEMA_VERSION
    assert certification.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert certification.identity.source_topology_hash_reference == hash_orchestration_topology(
        default_orchestration_topology()
    )
    assert certification.identity.source_capability_hash_reference == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert certification.identity.source_policy_hash_reference == hash_orchestration_policy_visibility(
        default_orchestration_policy_visibility()
    )
    assert certification.identity.source_transition_hash_reference == hash_orchestration_transition_visibility(
        default_orchestration_transition_visibility()
    )
    assert certification.identity.source_coordination_hash_reference == hash_orchestration_coordination_visibility(
        default_orchestration_coordination_visibility()
    )
    assert certification.identity.source_diagnostics_hash_reference == hash_orchestration_diagnostics_aggregation(
        default_orchestration_diagnostics_aggregation()
    )
    assert certification.non_executable is True
    assert certification.non_authorizing is True
    assert certification.non_decisioning is True
    assert certification.descriptive_only is True
    assert enabled_coordination_execution_count(certification) == 0
    assert enabled_transition_execution_count(certification) == 0
    assert enabled_policy_enforcement_count(certification) == 0
    assert enabled_operational_capability_count(certification) == 0
    assert enabled_orchestration_decision_count(certification) == 0
    assert enabled_orchestration_recommendation_count(certification) == 0
    assert enabled_orchestration_authorization_count(certification) == 0


def test_v4_3_continuity_certification_identity_key_is_stable():
    certification = default_orchestration_continuity_integrity_certification()

    assert continuity_certification_identity_key(certification) == (
        "v4_3.orchestration_continuity_and_integrity_certification.1"
        "|v4_3_orchestration_continuity_integrity_certification_primary"
        "|v4.3.0-phase-8"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_primary"
        f"|{hash_orchestration_topology(default_orchestration_topology())}"
        "|v4_3_orchestration_capability_visibility_primary"
        f"|{hash_orchestration_capability_visibility(default_orchestration_capability_visibility())}"
        "|v4_3_orchestration_policy_visibility_primary"
        f"|{hash_orchestration_policy_visibility(default_orchestration_policy_visibility())}"
        "|v4_3_orchestration_transition_visibility_primary"
        f"|{hash_orchestration_transition_visibility(default_orchestration_transition_visibility())}"
        "|v4_3_orchestration_coordination_visibility_primary"
        f"|{hash_orchestration_coordination_visibility(default_orchestration_coordination_visibility())}"
        "|v4_3_orchestration_diagnostics_and_explainability_primary"
        f"|{hash_orchestration_diagnostics_aggregation(default_orchestration_diagnostics_aggregation())}"
        "|v4_3_continuity_integrity_governance_primary"
    )


def test_v4_3_continuity_certification_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_continuity_integrity_certification()
    second = default_orchestration_continuity_integrity_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert continuity_certifications_equal(first, second)
    assert serialize_orchestration_continuity_integrity_certification(
        first
    ) == serialize_orchestration_continuity_integrity_certification(second)
    assert hash_orchestration_continuity_integrity_certification(
        first
    ) == hash_orchestration_continuity_integrity_certification(second)


def test_v4_3_continuity_certification_ordering_survives_reordered_collections():
    certification = default_orchestration_continuity_integrity_certification()
    reordered = replace(
        certification,
        continuity_certifications=tuple(reversed(certification.continuity_certifications)),
        integrity_certifications=tuple(reversed(certification.integrity_certifications)),
        state_certification_summaries=tuple(reversed(certification.state_certification_summaries)),
        diagnostics=tuple(reversed(certification.diagnostics)),
        explainability_summaries=tuple(reversed(certification.explainability_summaries)),
    )

    assert serialize_orchestration_continuity_integrity_certification(
        certification
    ) == serialize_orchestration_continuity_integrity_certification(reordered)
    assert hash_orchestration_continuity_integrity_certification(
        certification
    ) == hash_orchestration_continuity_integrity_certification(reordered)
    exported = export_orchestration_continuity_integrity_certification(reordered)
    assert [item["layer_id"] for item in exported["integrity_certifications"]] == list(CERTIFICATION_LAYER_IDS)
    assert [item["state_type"] for item in exported["state_certification_summaries"]] == [
        CERTIFICATION_STATE_PROHIBITED,
        CERTIFICATION_STATE_UNSUPPORTED,
        CERTIFICATION_STATE_BLOCKED,
        CERTIFICATION_STATE_STALE,
        CERTIFICATION_STATE_CONFLICTING,
    ]


def test_v4_3_continuity_and_integrity_validations_certify_stability():
    certification = default_orchestration_continuity_integrity_certification()
    identity = validate_continuity_certification_identity(certification)
    continuity = validate_continuity_certifications(certification)
    integrity = validate_integrity_certifications(certification)

    assert identity["valid"] is True
    assert identity["source_hash_mismatches"] == ()
    assert continuity["valid"] is True
    assert continuity["continuity_gap_count"] == 0
    assert continuity["integrity_failure_count"] == 0
    assert continuity["replay_safe_certification_status"] is True
    assert continuity["rollback_safe_certification_status"] is True
    assert continuity["lineage_consistency_visible"] is True
    assert continuity["provenance_consistency_visible"] is True
    assert continuity["governance_consistency_visible"] is True
    assert integrity["valid"] is True
    assert integrity["integrity_failure_count"] == 0
    assert integrity["continuity_gap_count"] == 0
    assert integrity["cross_layer_integrity_visible"] is True


def test_v4_3_continuity_gap_visibility_detects_gaps():
    certification = default_orchestration_continuity_integrity_certification()
    contaminated_record = replace(
        certification.continuity_certifications[0],
        continuity_gap_ids=("missing_lineage_reference",),
    )
    contaminated = replace(
        certification,
        continuity_certifications=(contaminated_record,) + certification.continuity_certifications[1:],
    )
    validation = validate_continuity_certifications(contaminated)

    assert validation["valid"] is False
    assert validation["continuity_gap_ids"] == ("missing_lineage_reference",)
    assert validation["continuity_gap_count"] == 1


def test_v4_3_integrity_failure_visibility_detects_hash_mismatch():
    certification = default_orchestration_continuity_integrity_certification()
    contaminated_record = replace(
        certification.integrity_certifications[0],
        actual_hash_reference="mismatched_hash",
        integrity_failure_ids=("manifest_hash_mismatch",),
    )
    contaminated = replace(
        certification,
        integrity_certifications=(contaminated_record,) + certification.integrity_certifications[1:],
    )
    validation = validate_integrity_certifications(contaminated)

    assert validation["valid"] is False
    assert validation["hash_mismatch_ids"] == (certification.integrity_certifications[0].integrity_id,)
    assert validation["integrity_failure_ids"] == ("manifest_hash_mismatch",)
    assert validation["integrity_failure_count"] == 2


def test_v4_3_state_certification_visibility_is_fail_visible():
    certification = default_orchestration_continuity_integrity_certification()
    states = validate_state_certification_visibility(certification)

    assert states["valid"] is True
    assert states["prohibited_state_certification_visible"] is True
    assert states["unsupported_state_certification_visible"] is True
    assert states["blocked_state_certification_visible"] is True
    assert states["stale_state_certification_visible"] is True
    assert states["conflicting_state_certification_visible"] is True
    assert states["prohibited_state_certification_count"] > 0
    assert states["unsupported_state_certification_count"] > 0
    assert states["blocked_state_certification_count"] > 0
    assert states["stale_state_certification_count"] > 0
    assert states["conflicting_state_certification_count"] > 0


def test_v4_3_continuity_explainability_is_complete_and_stable():
    certification = default_orchestration_continuity_integrity_certification()
    explainability = validate_continuity_explainability(certification)

    assert explainability["valid"] is True
    assert explainability["missing_explainability_categories"] == ()
    assert "orchestration_non_executable" in explainability["explainability_categories"]
    assert "orchestration_authorization_unavailable" in explainability["explainability_categories"]
    assert "governance_consistency_matters" in explainability["explainability_categories"]
    assert "lineage_continuity_matters" in explainability["explainability_categories"]
    assert "provenance_continuity_matters" in explainability["explainability_categories"]
    assert "replay_safe_evidence_matters" in explainability["explainability_categories"]
    assert "rollback_safe_evidence_matters" in explainability["explainability_categories"]
    assert "fail_visible_inconsistencies_exist" in explainability["explainability_categories"]
    assert "operational_orchestration_prohibited" in explainability["explainability_categories"]
    assert explainability["deterministic"] is True
    assert explainability["replay_safe"] is True
    assert explainability["rollback_safe"] is True


def test_v4_3_continuity_non_execution_authorization_and_decision_blocks_operational_flags():
    certification = default_orchestration_continuity_integrity_certification()
    contaminated_record = replace(
        certification.continuity_certifications[0],
        authorization_enabled=True,
        decision_enabled=True,
        recommendation_enabled=True,
    )
    contaminated = replace(
        certification,
        continuity_certifications=(contaminated_record,) + certification.continuity_certifications[1:],
        orchestration_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_decision_enabled=True,
        orchestration_recommendation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_continuity_non_execution_authorization_decision(contaminated)

    assert validate_continuity_non_execution_authorization_decision(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_operational_capability_count"] == 1
    assert validation["enabled_orchestration_authorization_count"] == 1
    assert validation["enabled_orchestration_decision_count"] == 1
    assert validation["enabled_orchestration_recommendation_count"] == 1
    assert validation["orchestration_execution_disabled"] is False
    assert validation["orchestration_authorization_disabled"] is False
    assert validation["orchestration_decision_disabled"] is False
    assert validation["orchestration_recommendation_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_continuity_certification_diagnostics_are_descriptive_only():
    certification = default_orchestration_continuity_integrity_certification()
    diagnostics = build_continuity_integrity_certification_diagnostics(certification)

    assert diagnostics["continuity_certification_count"] == len(certification.continuity_certifications)
    assert diagnostics["integrity_certification_count"] == len(certification.integrity_certifications)
    assert diagnostics["continuity_gap_count"] == 0
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


def test_v4_3_continuity_report_generation_and_hash_are_stable():
    first = build_v4_3_orchestration_continuity_and_integrity_certification_report()
    second = build_v4_3_orchestration_continuity_and_integrity_certification_report()

    assert first == second
    assert first["continuity_integrity_certification_status"] == V4_3_ORCHESTRATION_CONTINUITY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["continuity_ordering_verified"] is True
    assert first["summary"]["integrity_ordering_verified"] is True
    assert first["summary"]["diagnostics_ordering_verified"] is True
    assert first["summary"]["explainability_ordering_verified"] is True
    assert first["summary"]["enabled_coordination_execution_count"] == 0
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["enabled_orchestration_decision_count"] == 0
    assert first["summary"]["enabled_orchestration_recommendation_count"] == 0
    assert first["summary"]["enabled_orchestration_authorization_count"] == 0
    assert first["summary"]["orchestration_activation_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert "No orchestration authorization pathway may exist." in EXPLICIT_ORCHESTRATION_CONTINUITY_PROHIBITIONS
    assert "No orchestration authorization pathway may exist." in first["explicit_prohibitions"]


def test_v4_3_continuity_component_hashes_are_stable():
    certification = default_orchestration_continuity_integrity_certification()

    assert [
        hash_continuity_certification_record(item) for item in certification.continuity_certifications
    ] == [
        hash_continuity_certification_record(item) for item in certification.continuity_certifications
    ]
    assert [hash_integrity_certification_record(item) for item in certification.integrity_certifications] == [
        hash_integrity_certification_record(item) for item in certification.integrity_certifications
    ]
    assert [hash_certification_state_summary(item) for item in certification.state_certification_summaries] == [
        hash_certification_state_summary(item) for item in certification.state_certification_summaries
    ]
    assert [hash_continuity_certification_diagnostic(item) for item in certification.diagnostics] == [
        hash_continuity_certification_diagnostic(item) for item in certification.diagnostics
    ]
    assert [
        hash_continuity_certification_explainability(item)
        for item in certification.explainability_summaries
    ] == [
        hash_continuity_certification_explainability(item)
        for item in certification.explainability_summaries
    ]


def test_v4_3_continuity_is_compatible_with_phase_1_through_7_artifacts():
    certification = default_orchestration_continuity_integrity_certification()
    integrity_hashes = {
        item.layer_id: item.actual_hash_reference
        for item in certification.integrity_certifications
    }

    assert integrity_hashes["manifest"] == hash_orchestration_manifest(default_orchestration_manifest())
    assert integrity_hashes["topology"] == hash_orchestration_topology(default_orchestration_topology())
    assert integrity_hashes["capability"] == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert integrity_hashes["policy"] == hash_orchestration_policy_visibility(
        default_orchestration_policy_visibility()
    )
    assert integrity_hashes["transition"] == hash_orchestration_transition_visibility(
        default_orchestration_transition_visibility()
    )
    assert integrity_hashes["coordination"] == hash_orchestration_coordination_visibility(
        default_orchestration_coordination_visibility()
    )
    assert integrity_hashes["diagnostics_aggregation"] == hash_orchestration_diagnostics_aggregation(
        default_orchestration_diagnostics_aggregation()
    )
