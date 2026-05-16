from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest


APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_session_models import (  # noqa: E402
    SESSION_STATE_BLOCKED,
    SESSION_STATE_COMPLETE,
    SESSION_STATE_EXPERIMENTAL,
    SESSION_STATE_INCOMPLETE,
    SESSION_STATE_NON_EXECUTABLE,
    SESSION_STATE_PLANNING_ONLY,
    SESSION_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN,
    SESSION_STATE_UNSUPPORTED,
    SESSION_VISIBILITY_FAIL_VISIBLE,
    V3_8_SESSION_AUDIT_STABLE,
    hash_v3_8_session_audit,
    serialize_v3_8_session_audit,
    session_id,
    validate_v3_8_session_hash_stability,
    validate_v3_8_session_serialization_stability,
)
from runtime_coordination.coordination_session_reasoning import (  # noqa: E402
    reason_v3_8_coordination_session,
)
from scripts.report_v3_8_coordination_session_reasoning import (  # noqa: E402
    build_v3_8_coordination_session_reasoning_report,
)


def test_v3_8_session_audit_is_immutable_and_non_executable():
    audit = reason_v3_8_coordination_session()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_SESSION_AUDIT_STABLE
    assert audit.immutable_evidence_records is True
    assert audit.non_executable is True
    assert audit.coordination_execution_enabled is False
    assert audit.orchestration_execution_enabled is False
    assert audit.routing_enabled is False
    assert audit.scheduling_enabled is False
    assert audit.dispatch_enabled is False
    assert audit.traversal_execution_enabled is False
    assert audit.optimization_enabled is False
    assert audit.recommendation_enabled is False
    assert audit.execution_authorization_enabled is False
    assert audit.runtime_engine_enabled is False
    assert audit.state_machine_enabled is False
    assert audit.session_runtime_state_machine_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_session_serialization_hashing_and_output_are_stable():
    first = reason_v3_8_coordination_session()
    second = reason_v3_8_coordination_session()

    assert first == second
    assert serialize_v3_8_session_audit(first) == serialize_v3_8_session_audit(second)
    assert hash_v3_8_session_audit(first) == hash_v3_8_session_audit(second)
    assert validate_v3_8_session_serialization_stability(first)["stable"] is True
    assert validate_v3_8_session_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_session_audit(first))
    assert serialized["non_executable"] is True
    assert serialized["session_runtime_state_machine_enabled"] is False


def test_v3_8_session_ids_are_deterministic():
    audit = reason_v3_8_coordination_session()

    session_ids = tuple(result.session_id for result in audit.session_results)
    assert len(session_ids) == len(set(session_ids))
    for result in audit.session_results:
        subject_id = result.session_id.removeprefix(f"v3_8_session_{result.session_state}_")
        assert result.session_id == session_id(result.session_state, subject_id)
        assert result.source_coordination_references
        assert result.boundary_context_ids
        assert result.compatibility_context_ids
        assert result.evaluation_context_ids
        assert result.provenance_reference
        assert result.replay_safe_evidence
        assert result.rollback_safe_evidence
        assert result.non_execution_confirmation is True


def test_v3_8_session_counts_cover_required_states():
    audit = reason_v3_8_coordination_session()

    assert audit.validation_totals["session_result_count"] == 23
    assert audit.state_counts[SESSION_STATE_COMPLETE] == 8
    assert audit.state_counts[SESSION_STATE_INCOMPLETE] == 1
    assert audit.state_counts[SESSION_STATE_BLOCKED] == 2
    assert audit.state_counts[SESSION_STATE_UNSUPPORTED] == 3
    assert audit.state_counts[SESSION_STATE_PROHIBITED] == 4
    assert audit.state_counts[SESSION_STATE_UNKNOWN] == 2
    assert audit.state_counts[SESSION_STATE_EXPERIMENTAL] == 1
    assert audit.state_counts[SESSION_STATE_PLANNING_ONLY] == 1
    assert audit.state_counts[SESSION_STATE_NON_EXECUTABLE] == 1


def test_v3_8_session_preserves_boundary_compatibility_and_evaluation_context():
    audit = reason_v3_8_coordination_session()

    assert audit.validation_totals["boundary_context_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["compatibility_context_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["evaluation_context_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["boundary_context_preserved_count"] == audit.validation_totals["session_result_count"]
    assert (
        audit.validation_totals["compatibility_context_preserved_count"]
        == audit.validation_totals["session_result_count"]
    )
    assert audit.validation_totals["evaluation_context_preserved_count"] == audit.validation_totals["session_result_count"]
    assert all(result.evidence.boundary_context_preserved for result in audit.session_results)
    assert all(result.evidence.compatibility_context_preserved for result in audit.session_results)
    assert all(result.evidence.evaluation_context_preserved for result in audit.session_results)


def test_v3_8_non_complete_session_states_are_fail_visible_and_distinct():
    audit = reason_v3_8_coordination_session()
    required = {
        SESSION_STATE_INCOMPLETE: 1,
        SESSION_STATE_BLOCKED: 2,
        SESSION_STATE_UNSUPPORTED: 3,
        SESSION_STATE_PROHIBITED: 4,
        SESSION_STATE_UNKNOWN: 2,
    }

    for state, expected_count in required.items():
        results = [result for result in audit.session_results if result.session_state == state]
        assert len(results) == expected_count
        assert all(result.deterministic_visibility_status == SESSION_VISIBILITY_FAIL_VISIBLE for result in results)
        assert all(result.fail_visible and not result.hidden for result in results)
        assert all(result.hidden_risk is False for result in results)

    assert audit.validation_totals["fail_visible_incomplete_count"] == 1
    assert audit.validation_totals["fail_visible_blocked_count"] == 2
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 2


def test_v3_8_experimental_planning_only_and_non_executable_sessions_are_explicit():
    audit = reason_v3_8_coordination_session()

    experimental = [result for result in audit.session_results if result.session_state == SESSION_STATE_EXPERIMENTAL]
    planning_only = [result for result in audit.session_results if result.session_state == SESSION_STATE_PLANNING_ONLY]
    non_executable = [result for result in audit.session_results if result.session_state == SESSION_STATE_NON_EXECUTABLE]

    assert len(experimental) == 1
    assert experimental[0].experimental_label_explicit is True
    assert len(planning_only) == 1
    assert len(non_executable) == 1
    assert all(result.non_execution_confirmation is True for result in experimental + planning_only + non_executable)
    assert all(result.execution_behavior_detected is False for result in experimental + planning_only + non_executable)
    assert all(result.callable_execution_path_enabled is False for result in experimental + planning_only + non_executable)
    assert all(
        result.deterministic_visibility_status == SESSION_VISIBILITY_FAIL_VISIBLE
        for result in experimental + planning_only + non_executable
    )


def test_v3_8_session_replay_rollback_provenance_and_immutability_are_preserved():
    audit = reason_v3_8_coordination_session()

    assert audit.validation_totals["replay_safe_evidence_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["rollback_safe_evidence_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["provenance_continuity_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["immutable_evidence_record_count"] == audit.validation_totals["session_result_count"]
    assert audit.validation_totals["runtime_state_machine_count"] == 0
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert all(result.evidence.replay_safe for result in audit.session_results)
    assert all(result.evidence.rollback_safe for result in audit.session_results)
    assert all(result.evidence.provenance_preserved for result in audit.session_results)
    assert all(result.immutable_evidence_record and result.evidence.immutable_evidence_record for result in audit.session_results)
    assert all(result.runtime_state_machine is False for result in audit.session_results)
    assert all(result.evidence.runtime_state_machine is False for result in audit.session_results)


def test_v3_8_session_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_session_reasoning_report()

    assert report["summary"]["audit_status"] == V3_8_SESSION_AUDIT_STABLE
    assert report["summary"]["session_result_count"] == 23
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["incomplete_fail_visible"] is True
    assert report["summary"]["blocked_fail_visible"] is True
    assert report["summary"]["unsupported_fail_visible"] is True
    assert report["summary"]["prohibited_fail_visible"] is True
    assert report["summary"]["unknown_fail_visible"] is True
    assert report["summary"]["boundary_context_verified"] is True
    assert report["summary"]["compatibility_context_verified"] is True
    assert report["summary"]["evaluation_context_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["immutable_evidence_records_verified"] is True
    assert report["summary"]["runtime_state_machine_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["session_totals"]["complete_count"] == 8
    assert report["session_totals"]["incomplete_count"] == 1
    assert report["session_totals"]["blocked_count"] == 2
    assert report["session_totals"]["unsupported_count"] == 3
    assert report["session_totals"]["prohibited_count"] == 4
    assert report["session_totals"]["unknown_count"] == 2
    assert report["session_totals"]["experimental_count"] == 1
    assert report["session_totals"]["planning_only_count"] == 1
    assert report["session_totals"]["non_executable_count"] == 1
    assert report["session_totals"]["boundary_context_count"] == 23
    assert report["session_totals"]["compatibility_context_count"] == 23
    assert report["session_totals"]["evaluation_context_count"] == 23
    assert report["session_totals"]["hidden_risk_count"] == 0
    assert report["session_totals"]["execution_boundary_violation_count"] == 0
