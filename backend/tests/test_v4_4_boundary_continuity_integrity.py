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

from orchestration_governance.v4_4_boundary_continuity_integrity_audit import (  # noqa: E402
    boundary_continuity_integrity_capability_counter_values,
    boundary_continuity_integrity_equal,
    build_v4_4_boundary_continuity_integrity,
    build_v4_4_boundary_continuity_integrity_report,
    contaminate_boundary_continuity_integrity_for_non_operational_validation,
    enabled_boundary_continuity_integrity_capability_flags,
    validate_boundary_continuity_integrity,
    validate_boundary_continuity_integrity_non_operational,
    validate_continuity_integrity_ordering_stability,
    validate_continuity_integrity_replay_rollback_evidence,
    validate_continuity_integrity_serialization_and_hashing,
    validate_continuity_integrity_visibility,
)
from orchestration_governance.v4_4_boundary_continuity_integrity_hashing import (  # noqa: E402
    hash_boundary_continuity_integrity_certification,
    hash_continuity_certification_identity,
    hash_integrity_certification_identity,
    hash_replay_rollback_safety_record,
)
from orchestration_governance.v4_4_boundary_continuity_integrity_models import (  # noqa: E402
    BOUNDARY_CONTINUITY_INTEGRITY_STATES,
    CERTIFICATION_STATE_AMBIGUOUS,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_CONFLICTING,
    CERTIFICATION_STATE_CONTINUOUS,
    CERTIFICATION_STATE_DEGRADED,
    CERTIFICATION_STATE_DISCONTINUOUS,
    CERTIFICATION_STATE_INTEGRITY_BLOCKED,
    CERTIFICATION_STATE_INTEGRITY_SAFE,
    CERTIFICATION_STATE_INTEGRITY_WARNING,
    CERTIFICATION_STATE_LINEAGE_SAFE,
    CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_PROVENANCE_SAFE,
    CERTIFICATION_STATE_REPLAY_SAFE,
    CERTIFICATION_STATE_ROLLBACK_SAFE,
    CERTIFICATION_STATE_STALE,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_SCHEMA_VERSION,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_continuity_integrity_serialization import (  # noqa: E402
    serialize_boundary_continuity_integrity_certification,
)
from orchestration_governance.v4_4_boundary_continuity_integrity_visibility import (  # noqa: E402
    certification_diagnostic_summaries,
    certification_limitation_summaries,
    certification_summary_visibility,
    continuity_status_totals,
    fail_visible_certification_diagnostics,
    governance_safe_certification_explainability,
    integrity_status_totals,
    lineage_continuity_visibility,
    phase_chain_certification_summaries,
    provenance_continuity_visibility,
    replay_rollback_safety_visibility,
)
from orchestration_governance.v4_4_boundary_explainability_aggregation_audit import (  # noqa: E402
    build_v4_4_boundary_explainability_aggregation_report,
)


REPORT_PATH = (
    BACKEND_ROOT.parent
    / "docs"
    / "generated"
    / "v4_4_boundary_continuity_integrity_report.json"
)


def test_v4_4_continuity_integrity_models_are_immutable_and_non_operational():
    certification = build_v4_4_boundary_continuity_integrity()

    with pytest.raises(FrozenInstanceError):
        certification.runtime_execution_enabled = True

    assert (
        certification.continuity_identity.schema_version
        == V4_4_BOUNDARY_CONTINUITY_INTEGRITY_SCHEMA_VERSION
    )
    assert certification.descriptive_only is True
    assert certification.non_operational is True
    assert certification.non_authoritative is True
    assert certification.non_authorizing is True
    assert certification.non_approving is True
    assert certification.non_recommending is True
    assert certification.non_deciding is True
    assert certification.non_remediating is True
    assert certification.non_mutating is True
    assert certification.runtime_readiness_inference_disabled is True
    assert enabled_boundary_continuity_integrity_capability_flags(certification) == {}
    assert all(
        value == 0
        for value in boundary_continuity_integrity_capability_counter_values(
            certification
        ).values()
    )


def test_v4_4_continuity_integrity_visibility_preserves_required_classifications():
    certification = build_v4_4_boundary_continuity_integrity()
    visibility = validate_continuity_integrity_visibility(certification)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[CERTIFICATION_STATE_CERTIFIED] == 21
    assert counts[CERTIFICATION_STATE_PARTIALLY_CERTIFIED] == 8
    assert counts[CERTIFICATION_STATE_UNCERTIFIED] == 3
    assert counts[CERTIFICATION_STATE_CONTINUOUS] == 13
    assert counts[CERTIFICATION_STATE_DISCONTINUOUS] == 5
    assert counts[CERTIFICATION_STATE_INTEGRITY_SAFE] == 12
    assert counts[CERTIFICATION_STATE_INTEGRITY_WARNING] == 5
    assert counts[CERTIFICATION_STATE_INTEGRITY_BLOCKED] == 4
    assert counts[CERTIFICATION_STATE_REPLAY_SAFE] == 2
    assert counts[CERTIFICATION_STATE_ROLLBACK_SAFE] == 2
    assert counts[CERTIFICATION_STATE_PROVENANCE_SAFE] == 2
    assert counts[CERTIFICATION_STATE_LINEAGE_SAFE] == 2
    assert counts[CERTIFICATION_STATE_UNSUPPORTED] == 2
    assert counts[CERTIFICATION_STATE_PROHIBITED] == 2
    assert counts[CERTIFICATION_STATE_STALE] == 2
    assert counts[CERTIFICATION_STATE_CONFLICTING] == 2
    assert counts[CERTIFICATION_STATE_AMBIGUOUS] == 2
    assert counts[CERTIFICATION_STATE_DEGRADED] == 2
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []
    assert set(counts) == set(BOUNDARY_CONTINUITY_INTEGRITY_STATES)


def test_v4_4_continuity_integrity_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_continuity_integrity()
    second = build_v4_4_boundary_continuity_integrity()
    serialization = validate_continuity_integrity_serialization_and_hashing(first)

    assert first == second
    assert boundary_continuity_integrity_equal(first, second)
    assert serialize_boundary_continuity_integrity_certification(
        first
    ) == serialize_boundary_continuity_integrity_certification(second)
    assert hash_boundary_continuity_integrity_certification(
        first
    ) == hash_boundary_continuity_integrity_certification(second)
    assert serialization["valid"] is True
    assert len(hash_continuity_certification_identity(first.continuity_identity)) == 64
    assert len(hash_integrity_certification_identity(first.integrity_identity)) == 64
    assert len(hash_replay_rollback_safety_record(first.replay_rollback_record)) == 64


def test_v4_4_continuity_integrity_ordering_survives_reordered_collections():
    certification = build_v4_4_boundary_continuity_integrity()
    reordered = replace(
        certification,
        phase_evidence_references=tuple(reversed(certification.phase_evidence_references)),
        continuity_records=tuple(reversed(certification.continuity_records)),
        integrity_records=tuple(reversed(certification.integrity_records)),
        limitation_records=tuple(reversed(certification.limitation_records)),
        diagnostic_records=tuple(reversed(certification.diagnostic_records)),
        certification_summaries=tuple(reversed(certification.certification_summaries)),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(certification.explicit_prohibitions)),
    )

    assert validate_continuity_integrity_ordering_stability(certification)["valid"] is True
    assert serialize_boundary_continuity_integrity_certification(
        certification
    ) == serialize_boundary_continuity_integrity_certification(reordered)
    assert hash_boundary_continuity_integrity_certification(
        certification
    ) == hash_boundary_continuity_integrity_certification(reordered)


def test_v4_4_continuity_integrity_visibility_helpers_remain_descriptive_only():
    certification = build_v4_4_boundary_continuity_integrity()
    phase_chain = phase_chain_certification_summaries(certification)
    continuity = continuity_status_totals(certification)
    integrity = integrity_status_totals(certification)
    limitations = certification_limitation_summaries(certification)
    diagnostics = certification_diagnostic_summaries(certification)
    summaries = certification_summary_visibility(certification)
    explanation = governance_safe_certification_explainability(certification)

    assert phase_chain["phase_evidence_reference_count"] == 6
    assert phase_chain["production_consumption_enabled_count"] == 0
    assert phase_chain["runtime_activation_enabled"] is False
    assert continuity["continuity_certification_record_count"] == 11
    assert continuity["continuous_count"] == 6
    assert continuity["discontinuous_count"] == 1
    assert continuity["runtime_activation_enabled_count"] == 0
    assert continuity["recommendation_enabled_count"] == 0
    assert continuity["decision_enabled_count"] == 0
    assert integrity["integrity_certification_record_count"] == 10
    assert integrity["integrity_safe_count"] == 8
    assert integrity["integrity_warning_count"] == 1
    assert integrity["integrity_blocked_count"] == 1
    assert integrity["certification_authorization_enabled_count"] == 0
    assert integrity["integrity_approval_enabled_count"] == 0
    assert integrity["production_readiness_inferred_count"] == 0
    assert limitations["limitation_count"] == 7
    assert limitations["automatic_remediation_enabled_count"] == 0
    assert limitations["automatic_repair_enabled_count"] == 0
    assert diagnostics["diagnostic_record_count"] == 10
    assert diagnostics["fail_visible_diagnostic_count"] == 10
    assert diagnostics["authorization_enabled_count"] == 0
    assert diagnostics["approval_enabled_count"] == 0
    assert diagnostics["recommendation_enabled_count"] == 0
    assert diagnostics["decision_enabled_count"] == 0
    assert summaries["certification_summary_count"] == 3
    assert summaries["authorization_signal_enabled_count"] == 0
    assert summaries["production_readiness_signal_enabled_count"] == 0
    assert summaries["runtime_activation_signal_enabled_count"] == 0
    assert explanation["descriptive_only"] is True
    assert explanation["non_operational"] is True
    assert explanation["runtime_readiness_inference_disabled"] is True


def test_v4_4_continuity_integrity_fail_visible_diagnostics_are_preserved():
    certification = build_v4_4_boundary_continuity_integrity()
    fail_visible = fail_visible_certification_diagnostics(certification)

    assert len(fail_visible) == 10
    assert all(item["fail_visible"] is True for item in fail_visible)
    assert {item["diagnostic_state"] for item in fail_visible} >= {
        CERTIFICATION_STATE_UNSUPPORTED,
        CERTIFICATION_STATE_PROHIBITED,
        CERTIFICATION_STATE_STALE,
        CERTIFICATION_STATE_CONFLICTING,
        CERTIFICATION_STATE_AMBIGUOUS,
        CERTIFICATION_STATE_DEGRADED,
        CERTIFICATION_STATE_UNCERTIFIED,
        CERTIFICATION_STATE_INTEGRITY_WARNING,
        CERTIFICATION_STATE_INTEGRITY_BLOCKED,
        CERTIFICATION_STATE_DISCONTINUOUS,
    }


def test_v4_4_continuity_integrity_replay_rollback_provenance_and_lineage_are_preserved():
    certification = build_v4_4_boundary_continuity_integrity()
    replay = validate_continuity_integrity_replay_rollback_evidence(certification)
    validation = validate_boundary_continuity_integrity(certification)
    provenance = provenance_continuity_visibility(certification)
    lineage = lineage_continuity_visibility(certification)
    safety = replay_rollback_safety_visibility(certification)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 6
    assert replay["replay_safe_evidence_count"] == 6
    assert replay["rollback_safe_evidence_count"] == 6
    assert validation["valid"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False
    assert safety["replay_safe"] is True
    assert safety["rollback_safe"] is True
    assert safety["runtime_mutation_enabled"] is False


def test_v4_4_continuity_integrity_non_operational_validation_detects_contamination():
    certification = build_v4_4_boundary_continuity_integrity()
    contaminated = contaminate_boundary_continuity_integrity_for_non_operational_validation(
        certification
    )
    validation = validate_boundary_continuity_integrity_non_operational(contaminated)

    assert validate_boundary_continuity_integrity_non_operational(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_scheduling_execution_count"] > 0
    assert validation["counters"]["enabled_recommendation_count"] > 0
    assert validation["counters"]["enabled_decision_count"] > 0
    assert validation["counters"]["enabled_certification_authorization_count"] > 0
    assert validation["counters"]["enabled_integrity_approval_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_continuity_integrity_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_continuity_integrity_report()
    second = build_v4_4_boundary_continuity_integrity_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["continuity_serialization_verified"] is True
    assert first["summary"]["integrity_serialization_verified"] is True
    assert first["summary"]["continuity_hashing_verified"] is True
    assert first["summary"]["integrity_hashing_verified"] is True
    assert first["summary"]["phase_evidence_reference_stability_verified"] is True
    assert first["summary"]["certification_limitation_visibility_preserved"] is True
    assert first["summary"]["fail_visible_diagnostic_preserved"] is True
    assert first["summary"]["provenance_continuity_verified"] is True
    assert first["summary"]["lineage_continuity_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    assert first["summary"]["authorization_behavior_enabled"] is False
    assert first["summary"]["approval_behavior_enabled"] is False
    assert first["summary"]["recommendation_behavior_enabled"] is False
    assert first["summary"]["decision_behavior_enabled"] is False
    assert first["summary"]["runtime_readiness_inferred"] is False
    for counter_name in V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_continuity_integrity_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_continuity_integrity_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_6_explainability_regression_remains_non_operational():
    report = build_v4_4_boundary_explainability_aggregation_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_scheduling_execution_count"] == 0
    assert report["summary"]["enabled_recommendation_count"] == 0
    assert report["summary"]["enabled_decision_count"] == 0
    assert report["summary"]["planner_integration_enabled"] is False
    assert report["summary"]["production_consumption_enabled"] is False
    assert report["summary"]["runtime_mutation_enabled"] is False
    assert report["summary"]["non_operational_certification_verified"] is True
