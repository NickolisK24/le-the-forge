from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
)
from app.runtime_intelligence.execution_drift_escalation_contracts import (
    BLOCKED_DRIFT_AUDIT_MISSING,
    BLOCKED_DRIFT_BASELINE_MISSING,
    BLOCKED_DRIFT_CHECK_NOT_REQUIRED,
    BLOCKED_DRIFT_DETECTION_MISSING,
    BLOCKED_DRIFT_ENVIRONMENT_MISMATCH,
    BLOCKED_DRIFT_SESSION_MISMATCH,
    BLOCKED_DRIFT_SEVERITY_UNSUPPORTED,
    BLOCKED_MISSING_DRIFT_AUDIT_ID,
    BLOCKED_UNRESOLVED_DRIFT_DETECTED,
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_execution_drift_escalation_contract,
    evaluate_execution_drift_escalation_contract,
    serialize_execution_drift_escalation_result,
    summarize_execution_drift_escalation_result,
)
from app.runtime_intelligence.execution_session_sandboxing_contracts import (
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_execution_session_sandbox_contract,
)
from app.runtime_intelligence.non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_non_production_execution_authorization_contract,
)
from app.runtime_intelligence.replay_safe_execution_scope_contracts import (
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_replay_safe_execution_scope_contract,
)
from app.runtime_intelligence.rollback_execution_governance_contracts import (
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_rollback_execution_governance_contract,
)
from scripts.report_v3_4_execution_drift_escalation import build_v3_4_execution_drift_escalation_report


def _base_contract():
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    sandbox = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    replay_scope = default_replay_safe_execution_scope_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
    )
    rollback = default_rollback_execution_governance_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
    )
    return default_execution_drift_escalation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
    )


def _status(contract) -> str:
    return evaluate_execution_drift_escalation_contract(contract)["status"]


def test_valid_drift_escalation_readiness():
    result = evaluate_execution_drift_escalation_contract(_base_contract())
    summary = summarize_execution_drift_escalation_result(result)

    assert result["status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["drift_escalation_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase4_replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase5_rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_drift_audit_id_blocked():
    assert _status(replace(_base_contract(), drift_audit_id="")) == BLOCKED_MISSING_DRIFT_AUDIT_ID


def test_drift_check_not_required_blocked():
    assert _status(replace(_base_contract(), drift_check_required=False)) == BLOCKED_DRIFT_CHECK_NOT_REQUIRED


def test_missing_drift_audit_blocked():
    assert _status(replace(_base_contract(), drift_audit_present=False)) == BLOCKED_DRIFT_AUDIT_MISSING


def test_missing_drift_baseline_blocked():
    assert _status(replace(_base_contract(), drift_baseline_present=False)) == BLOCKED_DRIFT_BASELINE_MISSING


def test_missing_drift_detection_blocked():
    assert _status(replace(_base_contract(), drift_detection_present=False)) == BLOCKED_DRIFT_DETECTION_MISSING


def test_unresolved_drift_detected_blocked():
    assert _status(replace(_base_contract(), unresolved_drift_detected=True)) == BLOCKED_UNRESOLVED_DRIFT_DETECTED


def test_unsupported_drift_severity_blocked():
    assert _status(replace(_base_contract(), drift_severity="unknown")) == BLOCKED_DRIFT_SEVERITY_UNSUPPORTED


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_DRIFT_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_DRIFT_SESSION_MISMATCH


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_no_automatic_drift_resolution_or_downgrade():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["prohibition_checks"]["automatic_drift_resolution_enabled"] is False
    assert result["prohibition_checks"]["drift_severity_downgrade_enabled"] is False
    assert result["prohibition_checks"]["unresolved_drift_allowed"] is False


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_execution_drift_escalation_contract(
        replace(
            _base_contract(),
            drift_audit_id="",
            drift_check_required=False,
            drift_audit_present=False,
            drift_baseline_present=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_DRIFT_AUDIT_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_DRIFT_AUDIT_ID,
        BLOCKED_DRIFT_CHECK_NOT_REQUIRED,
        BLOCKED_DRIFT_AUDIT_MISSING,
        BLOCKED_DRIFT_BASELINE_MISSING,
    ]


def test_deterministic_output_stability():
    first = evaluate_execution_drift_escalation_contract(_base_contract())
    second = evaluate_execution_drift_escalation_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_execution_drift_escalation_result(first) == serialize_execution_drift_escalation_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["drift_escalation_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["drift_escalation_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["drift_escalation_does_not_bypass_sandbox"] is True


def test_compatibility_with_phase4_replay_scope_contracts():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["phase4_replay_scope_compatibility"]["replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase4_replay_scope_compatibility"]["drift_escalation_does_not_bypass_replay_scope"] is True


def test_compatibility_with_phase5_rollback_governance_contracts():
    result = evaluate_execution_drift_escalation_contract(_base_contract())

    assert result["phase5_rollback_governance_compatibility"]["rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase5_rollback_governance_compatibility"]["drift_escalation_does_not_bypass_rollback_governance"] is True


def test_report_covers_every_drift_escalation_status():
    report = build_v3_4_execution_drift_escalation_report()
    distribution = report["status_distribution"]

    assert distribution[DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_DRIFT_AUDIT_ID] == 1
    assert distribution[BLOCKED_DRIFT_CHECK_NOT_REQUIRED] == 1
    assert distribution[BLOCKED_DRIFT_AUDIT_MISSING] == 1
    assert distribution[BLOCKED_DRIFT_BASELINE_MISSING] == 1
    assert distribution[BLOCKED_DRIFT_DETECTION_MISSING] == 1
    assert distribution[BLOCKED_UNRESOLVED_DRIFT_DETECTED] == 1
    assert distribution[BLOCKED_DRIFT_SEVERITY_UNSUPPORTED] == 1
    assert distribution[BLOCKED_DRIFT_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_DRIFT_SESSION_MISMATCH] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_execution_guards_are_stable():
    first = build_v3_4_execution_drift_escalation_report()
    second = build_v3_4_execution_drift_escalation_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["execution_enabled"] is False
    assert first["production_execution_enabled"] is False
    assert first["production_runtime_routing_authorized"] is False
    assert first["runtime_manifest_consumption_enabled"] is False
    assert first["production_authoritative_manifest_treatment"] is False
    assert first["live_runtime_execution_enabled"] is False
    assert first["live_replay_execution_enabled"] is False
    assert first["live_rollback_execution_enabled"] is False
    assert first["live_synthesis_execution_enabled"] is False
    assert first["live_decision_routing_enabled"] is False
    assert first["recommendation_logic_enabled"] is False
    assert first["autonomous_planner_mutation_enabled"] is False
    assert first["automatic_drift_resolution_enabled"] is False
    assert first["drift_severity_downgrade_enabled"] is False
    assert first["unresolved_drift_allowed"] is False
