from __future__ import annotations

from app.runtime_orchestration.v3_7_closeout_readiness_audit import (
    V37_CLOSEOUT_VALIDATION_BLOCKED,
    V37_CLOSEOUT_VALIDATION_STABLE,
    audit_v3_7_closeout_and_v3_8_readiness,
)
from app.runtime_orchestration.v3_7_closeout_readiness_models import (
    V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN,
    V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED,
    V37_CLOSEOUT_FINDING_NON_EXECUTABLE,
    V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING,
    V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING,
    V37CloseoutReadinessInput,
    hash_v3_7_closeout_readiness_result,
    serialize_v3_7_closeout_readiness_result,
    validate_v3_7_closeout_hash_stability,
    validate_v3_7_closeout_serialization_stability,
)
from scripts.report_v3_7_closeout_and_v3_8_readiness import (
    build_v3_7_closeout_and_v3_8_readiness_report,
)


def test_v3_7_closeout_preserves_full_phase_continuity():
    result = audit_v3_7_closeout_and_v3_8_readiness()

    assert result.closeout_status == V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING
    assert result.v3_8_readiness_classification == V3_7_CLOSED_OUT_READY_FOR_V3_8_PLANNING
    assert result.validation_totals["validation_status"] == V37_CLOSEOUT_VALIDATION_STABLE
    assert result.total_phases_audited == 9
    assert result.validation_totals["missing_phase_continuity_count"] == 0
    assert result.continuity_validation_totals["governance_continuity"] is True
    assert result.continuity_validation_totals["compatibility_continuity"] is True
    assert result.continuity_validation_totals["evaluation_continuity"] is True
    assert result.continuity_validation_totals["planning_session_continuity"] is True
    assert result.continuity_validation_totals["planning_scenario_continuity"] is True
    assert result.continuity_validation_totals["aggregation_continuity"] is True
    assert result.continuity_validation_totals["integrity_continuity"] is True
    assert result.continuity_validation_totals["certification_continuity"] is True


def test_v3_7_closeout_serialization_and_hash_are_stable():
    first = audit_v3_7_closeout_and_v3_8_readiness()
    second = audit_v3_7_closeout_and_v3_8_readiness()

    assert serialize_v3_7_closeout_readiness_result(first) == serialize_v3_7_closeout_readiness_result(second)
    assert hash_v3_7_closeout_readiness_result(first) == hash_v3_7_closeout_readiness_result(second)
    assert validate_v3_7_closeout_serialization_stability(first)["stable"] is True
    assert validate_v3_7_closeout_hash_stability(first)["stable"] is True


def test_v3_7_closeout_replay_rollback_provenance_and_explainability():
    result = audit_v3_7_closeout_and_v3_8_readiness()

    assert result.replay_rollback_totals["replay_safe"] is True
    assert result.replay_rollback_totals["rollback_safe"] is True
    assert result.provenance_explainability_totals["provenance_safe"] is True
    assert result.provenance_explainability_totals["explainability_safe"] is True
    assert all(evidence.replay_safe for evidence in result.phase_evidence)
    assert all(evidence.rollback_safe for evidence in result.phase_evidence)
    assert all(evidence.provenance_safe for evidence in result.phase_evidence)
    assert all(evidence.explainability_safe for evidence in result.phase_evidence)


def test_v3_7_closeout_execution_boundary_and_non_executable_guarantees():
    result = audit_v3_7_closeout_and_v3_8_readiness()

    assert result.closeout_is_non_executable is True
    assert result.runtime_execution_readiness_certified is False
    assert result.execution_authorization_enabled is False
    assert result.orchestration_execution_enabled is False
    assert result.routing_enabled is False
    assert result.scheduling_enabled is False
    assert result.dispatch_enabled is False
    assert result.traversal_enabled is False
    assert result.runtime_path_selection_enabled is False
    assert result.scenario_execution_selection_enabled is False
    assert result.execution_recommendation_enabled is False
    assert result.optimization_for_execution_enabled is False
    assert result.callable_execution_flow_enabled is False
    assert result.runtime_orchestration_engine_enabled is False
    assert result.execution_boundary_audit_totals["execution_boundary_preserved"] is True
    assert any(finding.finding_classification == V37_CLOSEOUT_FINDING_NON_EXECUTABLE for finding in result.findings)


def test_v3_7_closeout_missing_phase_is_fail_visible():
    result = audit_v3_7_closeout_and_v3_8_readiness(
        V37CloseoutReadinessInput(omitted_phase_ids=("planning_scenarios",))
    )

    assert result.closeout_status == V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING
    assert result.validation_totals["validation_status"] == V37_CLOSEOUT_VALIDATION_BLOCKED
    assert result.validation_totals["missing_phase_continuity_count"] == 1
    assert any(finding.finding_classification == "continuity_broken" for finding in result.findings)


def test_v3_7_closeout_hidden_risk_is_fail_visible():
    result = audit_v3_7_closeout_and_v3_8_readiness(
        V37CloseoutReadinessInput(force_hidden_risk_detected=True)
    )

    assert result.closeout_status == V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING
    assert result.hidden_risk_totals["hidden_risk_detected"] is True
    assert result.validation_totals["hidden_prohibited_state_count"] == 1
    hidden_finding = next(
        finding
        for finding in result.findings
        if finding.finding_classification == V37_CLOSEOUT_FINDING_HIDDEN_RISK_DETECTED
    )
    assert hidden_finding.blocks_closeout is True
    assert hidden_finding.fail_visible is True


def test_v3_7_closeout_execution_boundary_violation_blocks_closeout():
    result = audit_v3_7_closeout_and_v3_8_readiness(
        V37CloseoutReadinessInput(force_execution_boundary_violation=True)
    )

    assert result.closeout_status == V3_7_CLOSEOUT_BLOCKED_FOR_V3_8_PLANNING
    assert result.validation_totals["execution_boundary_violation_count"] == 1
    broken_finding = next(
        finding
        for finding in result.findings
        if finding.finding_classification == V37_CLOSEOUT_FINDING_EXECUTION_BOUNDARY_BROKEN
    )
    assert broken_finding.blocks_closeout is True
    assert broken_finding.fail_visible is True


def test_v3_7_closeout_report_contains_required_totals_and_boundaries():
    report = build_v3_7_closeout_and_v3_8_readiness_report()

    assert report["summary"]["validation_status"] == V37_CLOSEOUT_VALIDATION_STABLE
    assert report["total_phases_audited"] == 9
    assert report["continuity_validation_totals"]["governance_continuity"] is True
    assert report["execution_boundary_audit_totals"]["execution_boundary_violation_count"] == 0
    assert report["non_executable_confirmation"] is True
    assert report["no_execution_authorization_confirmation"] is True
    assert report["no_runtime_readiness_confirmation"] is True
    assert report["routing_scheduling_dispatch_traversal_prohibited_confirmation"] is True
