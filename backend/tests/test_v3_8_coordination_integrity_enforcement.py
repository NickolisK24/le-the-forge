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

from runtime_coordination.coordination_integrity_enforcement import (  # noqa: E402
    enforce_v3_8_coordination_integrity,
)
from runtime_coordination.coordination_integrity_models import (  # noqa: E402
    INTEGRITY_STATE_BLOCKED,
    INTEGRITY_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_NON_EXECUTABLE,
    INTEGRITY_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_PROHIBITED,
    INTEGRITY_STATE_SATISFIED,
    INTEGRITY_STATE_UNKNOWN,
    INTEGRITY_STATE_UNSUPPORTED,
    INTEGRITY_STATE_VIOLATED,
    INTEGRITY_VISIBILITY_FAIL_VISIBLE,
    V3_8_INTEGRITY_AUDIT_STABLE,
    hash_v3_8_integrity_audit,
    integrity_id,
    serialize_v3_8_integrity_audit,
    validate_v3_8_integrity_hash_stability,
    validate_v3_8_integrity_serialization_stability,
)
from scripts.report_v3_8_coordination_integrity_enforcement import (  # noqa: E402
    build_v3_8_coordination_integrity_enforcement_report,
)


def test_v3_8_integrity_audit_is_immutable_and_non_executable():
    audit = enforce_v3_8_coordination_integrity()

    with pytest.raises(FrozenInstanceError):
        audit.orchestration_execution_enabled = True

    assert audit.audit_status == V3_8_INTEGRITY_AUDIT_STABLE
    assert audit.immutable_audit_evidence_records is True
    assert audit.non_executable is True
    assert audit.coordination_execution_enabled is False
    assert audit.orchestration_execution_enabled is False
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
    assert audit.integrity_runtime_state_machine_enabled is False
    assert audit.callable_coordination_flow_enabled is False
    assert audit.persistent_runtime_mutation_enabled is False
    assert audit.hidden_transition_enabled is False
    assert audit.silent_fallback_enabled is False
    assert audit.validation_totals["execution_boundary_violation_count"] == 0


def test_v3_8_integrity_serialization_hashing_and_output_are_stable():
    first = enforce_v3_8_coordination_integrity()
    second = enforce_v3_8_coordination_integrity()

    assert first == second
    assert serialize_v3_8_integrity_audit(first) == serialize_v3_8_integrity_audit(second)
    assert hash_v3_8_integrity_audit(first) == hash_v3_8_integrity_audit(second)
    assert validate_v3_8_integrity_serialization_stability(first)["stable"] is True
    assert validate_v3_8_integrity_hash_stability(first)["stable"] is True
    serialized = json.loads(serialize_v3_8_integrity_audit(first))
    assert serialized["non_executable"] is True
    assert serialized["runtime_enforcement_engine_enabled"] is False
    assert serialized["integrity_runtime_state_machine_enabled"] is False
    assert serialized["recommendation_enabled"] is False
    assert serialized["optimization_enabled"] is False
    assert serialized["ranking_enabled"] is False
    assert serialized["scoring_enabled"] is False
    assert serialized["selection_enabled"] is False


def test_v3_8_integrity_ids_are_deterministic_and_context_rich():
    audit = enforce_v3_8_coordination_integrity()

    integrity_ids = tuple(result.integrity_id for result in audit.integrity_results)
    assert len(integrity_ids) == len(set(integrity_ids))
    for result in audit.integrity_results:
        subject_id = result.integrity_id.removeprefix(f"v3_8_integrity_{result.integrity_state}_")
        assert result.integrity_id == integrity_id(result.integrity_state, subject_id)
        assert result.source_coordination_references
        assert result.foundation_context_ids
        assert result.boundary_context_ids
        assert result.compatibility_context_ids
        assert result.evaluation_context_ids
        assert result.session_context_ids
        assert result.scenario_context_ids
        assert result.aggregation_context_ids
        assert result.provenance_reference
        assert result.replay_safe_evidence
        assert result.rollback_safe_evidence
        assert result.non_execution_confirmation is True


def test_v3_8_integrity_counts_cover_required_states():
    audit = enforce_v3_8_coordination_integrity()

    assert audit.validation_totals["integrity_result_count"] == 23
    assert audit.state_counts[INTEGRITY_STATE_SATISFIED] == 8
    assert audit.state_counts[INTEGRITY_STATE_VIOLATED] == 0
    assert audit.state_counts[INTEGRITY_STATE_BLOCKED] == 2
    assert audit.state_counts[INTEGRITY_STATE_UNSUPPORTED] == 3
    assert audit.state_counts[INTEGRITY_STATE_PROHIBITED] == 4
    assert audit.state_counts[INTEGRITY_STATE_UNKNOWN] == 3
    assert audit.state_counts[INTEGRITY_STATE_EXPERIMENTAL] == 1
    assert audit.state_counts[INTEGRITY_STATE_PLANNING_ONLY] == 1
    assert audit.state_counts[INTEGRITY_STATE_NON_EXECUTABLE] == 1
    assert audit.validation_totals["integrity_violation_count"] == 0


def test_v3_8_integrity_preserves_all_required_contexts():
    audit = enforce_v3_8_coordination_integrity()
    result_count = audit.validation_totals["integrity_result_count"]

    assert audit.validation_totals["foundation_context_count"] == result_count
    assert audit.validation_totals["boundary_context_count"] == result_count
    assert audit.validation_totals["compatibility_context_count"] == result_count
    assert audit.validation_totals["evaluation_context_count"] == result_count
    assert audit.validation_totals["session_context_count"] == result_count
    assert audit.validation_totals["scenario_context_count"] == result_count
    assert audit.validation_totals["aggregation_context_count"] == result_count
    assert audit.validation_totals["foundation_context_preserved_count"] == result_count
    assert audit.validation_totals["boundary_context_preserved_count"] == result_count
    assert audit.validation_totals["compatibility_context_preserved_count"] == result_count
    assert audit.validation_totals["evaluation_context_preserved_count"] == result_count
    assert audit.validation_totals["session_context_preserved_count"] == result_count
    assert audit.validation_totals["scenario_context_preserved_count"] == result_count
    assert audit.validation_totals["aggregation_context_preserved_count"] == result_count
    assert all(result.evidence.foundation_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.boundary_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.compatibility_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.evaluation_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.session_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.scenario_context_preserved for result in audit.integrity_results)
    assert all(result.evidence.aggregation_context_preserved for result in audit.integrity_results)


def test_v3_8_non_satisfied_states_are_fail_visible_and_distinct():
    audit = enforce_v3_8_coordination_integrity()
    fixture_audit = enforce_v3_8_coordination_integrity(include_violation_fixture=True)
    required = {
        INTEGRITY_STATE_BLOCKED: 2,
        INTEGRITY_STATE_UNSUPPORTED: 3,
        INTEGRITY_STATE_PROHIBITED: 4,
        INTEGRITY_STATE_UNKNOWN: 3,
    }

    for state, expected_count in required.items():
        results = [result for result in audit.integrity_results if result.integrity_state == state]
        assert len(results) == expected_count
        assert all(result.deterministic_visibility_status == INTEGRITY_VISIBILITY_FAIL_VISIBLE for result in results)
        assert all(result.fail_visible and not result.hidden for result in results)
        assert all(result.hidden_risk is False for result in results)

    violated = [
        result
        for result in fixture_audit.integrity_results
        if result.integrity_state == INTEGRITY_STATE_VIOLATED
    ]
    assert len(violated) == 1
    assert violated[0].deterministic_visibility_status == INTEGRITY_VISIBILITY_FAIL_VISIBLE
    assert violated[0].fail_visible is True
    assert violated[0].hidden is False
    assert violated[0].violation_codes
    assert fixture_audit.validation_totals["fail_visible_violated_count"] == 1
    assert audit.validation_totals["fail_visible_blocked_count"] == 2
    assert audit.validation_totals["fail_visible_unsupported_count"] == 3
    assert audit.validation_totals["fail_visible_prohibited_count"] == 4
    assert audit.validation_totals["fail_visible_unknown_count"] == 3


def test_v3_8_experimental_planning_only_and_non_executable_integrity_are_explicit():
    audit = enforce_v3_8_coordination_integrity()

    experimental = [result for result in audit.integrity_results if result.integrity_state == INTEGRITY_STATE_EXPERIMENTAL]
    planning_only = [result for result in audit.integrity_results if result.integrity_state == INTEGRITY_STATE_PLANNING_ONLY]
    non_executable = [result for result in audit.integrity_results if result.integrity_state == INTEGRITY_STATE_NON_EXECUTABLE]

    assert len(experimental) == 1
    assert experimental[0].experimental_label_explicit is True
    assert len(planning_only) == 1
    assert len(non_executable) == 1
    assert all(result.non_execution_confirmation is True for result in experimental + planning_only + non_executable)
    assert all(result.execution_behavior_detected is False for result in experimental + planning_only + non_executable)
    assert all(result.callable_execution_path_enabled is False for result in experimental + planning_only + non_executable)
    assert all(
        result.deterministic_visibility_status == INTEGRITY_VISIBILITY_FAIL_VISIBLE
        for result in experimental + planning_only + non_executable
    )


def test_v3_8_integrity_replay_rollback_provenance_and_immutability_are_preserved():
    audit = enforce_v3_8_coordination_integrity()
    result_count = audit.validation_totals["integrity_result_count"]

    assert audit.validation_totals["replay_safe_evidence_count"] == result_count
    assert audit.validation_totals["rollback_safe_evidence_count"] == result_count
    assert audit.validation_totals["provenance_continuity_count"] == result_count
    assert audit.validation_totals["immutable_audit_evidence_record_count"] == result_count
    assert audit.validation_totals["runtime_enforcement_state_machine_count"] == 0
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert all(result.evidence.replay_safe for result in audit.integrity_results)
    assert all(result.evidence.rollback_safe for result in audit.integrity_results)
    assert all(result.evidence.provenance_preserved for result in audit.integrity_results)
    assert all(
        result.immutable_audit_evidence_record and result.evidence.immutable_audit_evidence_record
        for result in audit.integrity_results
    )
    assert all(result.runtime_enforcement_state_machine is False for result in audit.integrity_results)
    assert all(result.evidence.runtime_enforcement_state_machine is False for result in audit.integrity_results)


def test_v3_8_integrity_violations_are_fail_visible_not_hidden():
    audit = enforce_v3_8_coordination_integrity(include_violation_fixture=True)
    violated = [
        result
        for result in audit.integrity_results
        if result.integrity_state == INTEGRITY_STATE_VIOLATED
    ]

    assert audit.validation_totals["integrity_result_count"] == 24
    assert audit.validation_totals["violated_count"] == 1
    assert audit.validation_totals["integrity_violation_count"] == 1
    assert audit.validation_totals["violation_code_count"] == 4
    assert audit.validation_totals["hidden_risk_count"] == 0
    assert len(violated) == 1
    assert violated[0].hidden is False
    assert violated[0].hidden_risk is False
    assert violated[0].fail_visible is True
    assert set(violated[0].violation_codes) == {
        "missing_required_context",
        "missing_provenance_continuity",
        "missing_replay_evidence",
        "missing_rollback_evidence",
    }
    assert violated[0].evidence.boundary_context_preserved is False
    assert violated[0].evidence.compatibility_context_preserved is False
    assert violated[0].evidence.evaluation_context_preserved is False
    assert violated[0].evidence.session_context_preserved is False
    assert violated[0].evidence.scenario_context_preserved is False
    assert violated[0].evidence.aggregation_context_preserved is False
    assert violated[0].evidence.provenance_preserved is False
    assert violated[0].evidence.replay_safe is False
    assert violated[0].evidence.rollback_safe is False


def test_v3_8_integrity_report_contains_required_totals_and_guarantees():
    report = build_v3_8_coordination_integrity_enforcement_report()

    assert report["summary"]["audit_status"] == V3_8_INTEGRITY_AUDIT_STABLE
    assert report["summary"]["integrity_result_count"] == 23
    assert report["summary"]["integrity_violation_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["violated_fail_visible"] is True
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
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["immutable_audit_evidence_records_verified"] is True
    assert report["summary"]["runtime_enforcement_state_machine_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["recommendation_language_violation_count"] == 0
    assert report["summary"]["optimization_language_violation_count"] == 0
    assert report["summary"]["ranking_language_violation_count"] == 0
    assert report["summary"]["scoring_behavior_violation_count"] == 0
    assert report["summary"]["selection_behavior_violation_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["integrity_totals"]["satisfied_count"] == 8
    assert report["integrity_totals"]["violated_count"] == 0
    assert report["integrity_totals"]["blocked_count"] == 2
    assert report["integrity_totals"]["unsupported_count"] == 3
    assert report["integrity_totals"]["prohibited_count"] == 4
    assert report["integrity_totals"]["unknown_count"] == 3
    assert report["integrity_totals"]["experimental_count"] == 1
    assert report["integrity_totals"]["planning_only_count"] == 1
    assert report["integrity_totals"]["non_executable_count"] == 1
    assert report["integrity_totals"]["foundation_context_count"] == 23
    assert report["integrity_totals"]["boundary_context_count"] == 23
    assert report["integrity_totals"]["compatibility_context_count"] == 23
    assert report["integrity_totals"]["evaluation_context_count"] == 23
    assert report["integrity_totals"]["session_context_count"] == 23
    assert report["integrity_totals"]["scenario_context_count"] == 23
    assert report["integrity_totals"]["aggregation_context_count"] == 23
    assert report["integrity_totals"]["hidden_risk_count"] == 0
    assert report["integrity_totals"]["integrity_violation_count"] == 0
    assert report["integrity_totals"]["recommendation_language_violation_count"] == 0
    assert report["integrity_totals"]["optimization_language_violation_count"] == 0
    assert report["integrity_totals"]["ranking_language_violation_count"] == 0
    assert report["integrity_totals"]["scoring_behavior_violation_count"] == 0
    assert report["integrity_totals"]["selection_behavior_violation_count"] == 0
    assert report["integrity_totals"]["execution_boundary_violation_count"] == 0
