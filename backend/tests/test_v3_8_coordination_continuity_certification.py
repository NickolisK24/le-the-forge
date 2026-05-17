from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_certification_models import (  # noqa: E402
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_EXPERIMENTAL,
    CERTIFICATION_STATE_NON_EXECUTABLE,
    CERTIFICATION_STATE_PLANNING_ONLY,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_UNKNOWN,
    CERTIFICATION_STATE_UNSUPPORTED,
    CERTIFICATION_VISIBILITY_FAIL_VISIBLE,
    V3_8_CERTIFICATION_AUDIT_STABLE,
    certification_id,
    hash_v3_8_certification_audit,
    serialize_v3_8_certification_audit,
    validate_v3_8_certification_hash_stability,
    validate_v3_8_certification_serialization_stability,
)
from runtime_coordination.coordination_continuity_certification import (  # noqa: E402
    certify_v3_8_coordination_continuity,
)
from scripts.report_v3_8_coordination_continuity_certification import (  # noqa: E402
    build_v3_8_coordination_continuity_certification_report,
)


def test_v3_8_certification_audit_is_immutable_and_non_executable():
    audit = certify_v3_8_coordination_continuity()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_CERTIFICATION_AUDIT_STABLE
    assert audit.immutable_certification_evidence_records is True
    assert audit.non_executable is True
    assert audit.coordination_execution_enabled is False
    assert audit.orchestration_execution_enabled is False
    assert audit.runtime_certification_engine_enabled is False
    assert audit.runtime_enforcement_engine_enabled is False
    assert audit.routing_enabled is False
    assert audit.scheduling_enabled is False
    assert audit.dispatch_enabled is False
    assert audit.traversal_execution_enabled is False
    assert audit.optimization_enabled is False
    assert audit.recommendation_enabled is False
    assert audit.ranking_enabled is False
    assert audit.scoring_enabled is False
    assert audit.selection_enabled is False
    assert audit.execution_authorization_enabled is False
    assert audit.runtime_engine_enabled is False
    assert audit.state_machine_enabled is False
    assert audit.certification_runtime_state_machine_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_certification_serialization_hashing_and_output_are_stable():
    first = certify_v3_8_coordination_continuity()
    second = certify_v3_8_coordination_continuity()

    assert first == second
    assert serialize_v3_8_certification_audit(first) == serialize_v3_8_certification_audit(second)
    assert hash_v3_8_certification_audit(first) == hash_v3_8_certification_audit(second)
    assert validate_v3_8_certification_serialization_stability(first)["stable"] is True
    assert validate_v3_8_certification_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_certification_audit(first))
    assert serialized["non_executable"] is True
    assert serialized["runtime_certification_engine_enabled"] is False
    assert serialized["runtime_enforcement_engine_enabled"] is False
    assert serialized["certification_runtime_state_machine_enabled"] is False
    assert serialized["recommendation_enabled"] is False
    assert serialized["optimization_enabled"] is False
    assert serialized["ranking_enabled"] is False
    assert serialized["scoring_enabled"] is False
    assert serialized["selection_enabled"] is False


def test_v3_8_certification_ids_are_deterministic_and_context_rich():
    audit = certify_v3_8_coordination_continuity()

    certification_ids = tuple(result.certification_id for result in audit.certification_results)
    assert len(certification_ids) == len(set(certification_ids))
    for result in audit.certification_results:
        subject_id = result.certification_id.removeprefix(
            f"v3_8_certification_{result.certification_state}_"
        )
        assert result.certification_id == certification_id(result.certification_state, subject_id)
        assert result.source_coordination_references
        assert result.foundation_context_ids
        assert result.boundary_context_ids
        assert result.compatibility_context_ids
        assert result.evaluation_context_ids
        assert result.session_context_ids
        assert result.scenario_context_ids
        assert result.aggregation_context_ids
        assert result.integrity_context_ids
        assert result.provenance_reference
        assert result.replay_safe_evidence
        assert result.rollback_safe_evidence
        assert result.non_execution_confirmation is True


def test_v3_8_certification_counts_cover_required_states():
    audit = certify_v3_8_coordination_continuity()

    assert audit.validation_totals["certification_result_count"] == 23
    assert audit.state_counts[CERTIFICATION_STATE_CERTIFIED] == 8
    assert audit.state_counts[CERTIFICATION_STATE_UNCERTIFIED] == 0
    assert audit.state_counts[CERTIFICATION_STATE_BLOCKED] == 2
    assert audit.state_counts[CERTIFICATION_STATE_UNSUPPORTED] == 3
    assert audit.state_counts[CERTIFICATION_STATE_PROHIBITED] == 4
    assert audit.state_counts[CERTIFICATION_STATE_UNKNOWN] == 3
    assert audit.state_counts[CERTIFICATION_STATE_EXPERIMENTAL] == 1
    assert audit.state_counts[CERTIFICATION_STATE_PLANNING_ONLY] == 1
    assert audit.state_counts[CERTIFICATION_STATE_NON_EXECUTABLE] == 1
    assert audit.validation_totals["continuity_certification_failure_count"] == 0


def test_v3_8_certification_preserves_all_required_contexts():
    audit = certify_v3_8_coordination_continuity()
    result_count = audit.validation_totals["certification_result_count"]

    assert audit.validation_totals["foundation_context_count"] == result_count
    assert audit.validation_totals["boundary_context_count"] == result_count
    assert audit.validation_totals["compatibility_context_count"] == result_count
    assert audit.validation_totals["evaluation_context_count"] == result_count
    assert audit.validation_totals["session_context_count"] == result_count
    assert audit.validation_totals["scenario_context_count"] == result_count
    assert audit.validation_totals["aggregation_context_count"] == result_count
    assert audit.validation_totals["integrity_context_count"] == result_count
    assert audit.validation_totals["foundation_context_certified_count"] == result_count
    assert audit.validation_totals["boundary_context_certified_count"] == result_count
    assert audit.validation_totals["compatibility_context_certified_count"] == result_count
    assert audit.validation_totals["evaluation_context_certified_count"] == result_count
    assert audit.validation_totals["session_context_certified_count"] == result_count
    assert audit.validation_totals["scenario_context_certified_count"] == result_count
    assert audit.validation_totals["aggregation_context_certified_count"] == result_count
    assert audit.validation_totals["integrity_context_certified_count"] == result_count
    assert all(result.evidence.foundation_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.boundary_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.compatibility_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.evaluation_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.session_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.scenario_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.aggregation_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.integrity_continuity_certified for result in audit.certification_results)


def test_v3_8_non_certified_states_are_fail_visible_and_distinct():
    audit = certify_v3_8_coordination_continuity()
    fixture_audit = certify_v3_8_coordination_continuity(include_failure_fixture=True)
    required = {
        CERTIFICATION_STATE_BLOCKED: 2,
        CERTIFICATION_STATE_UNSUPPORTED: 3,
        CERTIFICATION_STATE_PROHIBITED: 4,
        CERTIFICATION_STATE_UNKNOWN: 3,
    }

    assert audit.validation_totals["certified_visible_count"] == 8
    for state, expected_count in required.items():
        results = [result for result in audit.certification_results if result.certification_state == state]
        assert len(results) == expected_count
        assert all(result.deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE for result in results)
        assert all(result.fail_visible and not result.hidden for result in results)
        assert all(result.hidden_risk is False for result in results)

    uncertified = [
        result
        for result in fixture_audit.certification_results
        if result.certification_state == CERTIFICATION_STATE_UNCERTIFIED
    ]
    assert len(uncertified) == 1
    assert uncertified[0].deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE
    assert uncertified[0].fail_visible is True
    assert uncertified[0].hidden is False
    assert uncertified[0].certification_failure_codes
    assert fixture_audit.validation_totals["fail_visible_uncertified_count"] == 1
    assert audit.validation_totals["fail_visible_blocked_count"] == 2
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 3


def test_v3_8_experimental_planning_only_and_non_executable_certification_are_explicit():
    audit = certify_v3_8_coordination_continuity()

    experimental = [
        result
        for result in audit.certification_results
        if result.certification_state == CERTIFICATION_STATE_EXPERIMENTAL
    ]
    planning_only = [
        result
        for result in audit.certification_results
        if result.certification_state == CERTIFICATION_STATE_PLANNING_ONLY
    ]
    non_executable = [
        result
        for result in audit.certification_results
        if result.certification_state == CERTIFICATION_STATE_NON_EXECUTABLE
    ]

    assert len(experimental) == 1
    assert experimental[0].experimental_label_explicit is True
    assert len(planning_only) == 1
    assert len(non_executable) == 1
    assert all(result.non_execution_confirmation is True for result in experimental + planning_only + non_executable)
    assert all(result.execution_behavior_detected is False for result in experimental + planning_only + non_executable)
    assert all(result.callable_execution_path_enabled is False for result in experimental + planning_only + non_executable)
    assert all(
        result.deterministic_visibility_status == CERTIFICATION_VISIBILITY_FAIL_VISIBLE
        for result in experimental + planning_only + non_executable
    )


def test_v3_8_certification_replay_rollback_provenance_and_immutability_are_preserved():
    audit = certify_v3_8_coordination_continuity()
    result_count = audit.validation_totals["certification_result_count"]

    assert audit.validation_totals["replay_safe_evidence_count"] == result_count
    assert audit.validation_totals["rollback_safe_evidence_count"] == result_count
    assert audit.validation_totals["provenance_continuity_count"] == result_count
    assert audit.validation_totals["explainability_continuity_count"] == result_count
    assert audit.validation_totals["non_execution_continuity_count"] == result_count
    assert audit.validation_totals["fail_visible_state_continuity_count"] == result_count
    assert audit.validation_totals["immutable_certification_evidence_record_count"] == result_count
    assert audit.validation_totals["runtime_certification_state_machine_count"] == 0
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert all(result.evidence.replay_safe for result in audit.certification_results)
    assert all(result.evidence.rollback_safe for result in audit.certification_results)
    assert all(result.evidence.provenance_certified for result in audit.certification_results)
    assert all(result.evidence.explainability_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.non_execution_continuity_certified for result in audit.certification_results)
    assert all(result.evidence.fail_visible_state_continuity_certified for result in audit.certification_results)
    assert all(
        result.immutable_certification_evidence_record
        and result.evidence.immutable_certification_evidence_record
        for result in audit.certification_results
    )
    assert all(result.runtime_certification_state_machine is False for result in audit.certification_results)
    assert all(result.evidence.runtime_certification_state_machine is False for result in audit.certification_results)


def test_v3_8_certification_failures_are_fail_visible_not_hidden():
    audit = certify_v3_8_coordination_continuity(include_failure_fixture=True)
    uncertified = [
        result
        for result in audit.certification_results
        if result.certification_state == CERTIFICATION_STATE_UNCERTIFIED
    ]

    assert audit.validation_totals["certification_result_count"] == 24
    assert audit.validation_totals["uncertified_count"] == 1
    assert audit.validation_totals["continuity_certification_failure_count"] == 1
    assert audit.validation_totals["certification_failure_code_count"] == 10
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert len(uncertified) == 1
    assert uncertified[0].hidden is False
    assert uncertified[0].hidden_risk is False
    assert uncertified[0].fail_visible is True
    assert set(uncertified[0].certification_failure_codes) == {
        "aggregation_continuity_missing",
        "boundary_continuity_missing",
        "compatibility_continuity_missing",
        "evaluation_continuity_missing",
        "integrity_continuity_missing",
        "provenance_continuity_missing",
        "replay_continuity_missing",
        "rollback_continuity_missing",
        "scenario_continuity_missing",
        "session_continuity_missing",
    }
    assert uncertified[0].evidence.boundary_continuity_certified is False
    assert uncertified[0].evidence.compatibility_continuity_certified is False
    assert uncertified[0].evidence.evaluation_continuity_certified is False
    assert uncertified[0].evidence.session_continuity_certified is False
    assert uncertified[0].evidence.scenario_continuity_certified is False
    assert uncertified[0].evidence.aggregation_continuity_certified is False
    assert uncertified[0].evidence.integrity_continuity_certified is False
    assert uncertified[0].evidence.provenance_certified is False
    assert uncertified[0].evidence.replay_safe is False
    assert uncertified[0].evidence.rollback_safe is False


def test_v3_8_certification_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_continuity_certification_report()

    assert report["summary"]["audit_status"] == V3_8_CERTIFICATION_AUDIT_STABLE
    assert report["summary"]["certification_result_count"] == 23
    assert report["summary"]["continuity_certification_failure_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["certified_visible"] is True
    assert report["summary"]["uncertified_fail_visible"] is True
    assert report["summary"]["blocked_fail_visible"] is True
    assert report["summary"]["unsupported_fail_visible"] is True
    assert report["summary"]["prohibited_fail_visible"] is True
    assert report["summary"]["unknown_fail_visible"] is True
    assert report["summary"]["foundation_context_verified"] is True
    assert report["summary"]["boundary_context_verified"] is True
    assert report["summary"]["compatibility_context_verified"] is True
    assert report["summary"]["evaluation_context_verified"] is True
    assert report["summary"]["session_context_verified"] is True
    assert report["summary"]["scenario_context_verified"] is True
    assert report["summary"]["aggregation_context_verified"] is True
    assert report["summary"]["integrity_context_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["immutable_certification_evidence_records_verified"] is True
    assert report["summary"]["runtime_certification_state_machine_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["recommendation_language_violation_count"] == 0
    assert report["summary"]["optimization_language_violation_count"] == 0
    assert report["summary"]["ranking_language_violation_count"] == 0
    assert report["summary"]["scoring_behavior_violation_count"] == 0
    assert report["summary"]["selection_behavior_violation_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["certification_totals"]["certified_count"] == 8
    assert report["certification_totals"]["uncertified_count"] == 0
    assert report["certification_totals"]["blocked_count"] == 2
    assert report["certification_totals"]["unsupported_count"] == 3
    assert report["certification_totals"]["prohibited_count"] == 4
    assert report["certification_totals"]["unknown_count"] == 3
    assert report["certification_totals"]["experimental_count"] == 1
    assert report["certification_totals"]["planning_only_count"] == 1
    assert report["certification_totals"]["non_executable_count"] == 1
    assert report["certification_totals"]["foundation_context_count"] == 23
    assert report["certification_totals"]["boundary_context_count"] == 23
    assert report["certification_totals"]["compatibility_context_count"] == 23
    assert report["certification_totals"]["evaluation_context_count"] == 23
    assert report["certification_totals"]["session_context_count"] == 23
    assert report["certification_totals"]["scenario_context_count"] == 23
    assert report["certification_totals"]["aggregation_context_count"] == 23
    assert report["certification_totals"]["integrity_context_count"] == 23
    assert report["certification_totals"]["continuity_certification_failure_count"] == 0
    assert report["certification_totals"]["hidden_risk_count"] == 0
    assert report["certification_totals"]["recommendation_language_violation_count"] == 0
    assert report["certification_totals"]["optimization_language_violation_count"] == 0
    assert report["certification_totals"]["ranking_language_violation_count"] == 0
    assert report["certification_totals"]["scoring_behavior_violation_count"] == 0
    assert report["certification_totals"]["selection_behavior_violation_count"] == 0
    assert report["certification_totals"]["execution_boundary_violation_count"] == 0
