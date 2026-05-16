from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_readiness_audit import (
    BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN,
    BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS,
    BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS,
    BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS,
    BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    MANUAL_REVIEW_REQUIRED,
    V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
    build_controlled_execution_readiness_audit_from_reports,
    default_controlled_execution_readiness_audit_contract,
    evaluate_controlled_execution_readiness_audit,
    serialize_controlled_execution_readiness_audit,
    summarize_controlled_execution_readiness_audit,
)
from app.runtime_intelligence.controlled_execution_gate_contracts import ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
from app.runtime_intelligence.controlled_experiment_isolation_contracts import (
    EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.execution_audit_logging_contracts import (
    AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.execution_drift_escalation_contracts import (
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.execution_session_sandboxing_contracts import (
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.replay_safe_execution_scope_contracts import (
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.rollback_execution_governance_contracts import (
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from scripts.report_v3_4_controlled_execution_readiness_audit import (
    build_v3_4_controlled_execution_readiness_audit_report,
)


def _base_contract():
    return default_controlled_execution_readiness_audit_contract()


def _status(contract) -> str:
    return evaluate_controlled_execution_readiness_audit(contract)["status"]


def test_valid_complete_v3_4_readiness():
    result = evaluate_controlled_execution_readiness_audit(_base_contract())
    summary = summarize_controlled_execution_readiness_audit(result)
    phase_statuses = {row["phase_id"]: row["status"] for row in result["phase_readiness"]}

    assert result["status"] == V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
    assert result["ready_for_future_controlled_execution_planning"] is True
    assert result["controlled_execution_authorized"] is False
    assert result["planning_only"] is True
    assert result["audit_only"] is True
    assert result["blockers"] == []
    assert summary["controlled_execution_authorized"] is False
    assert phase_statuses["phase_1_controlled_execution_gate"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_2_non_production_authorization"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_3_execution_session_sandboxing"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_4_replay_safe_execution_scope"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_5_rollback_execution_governance"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_6_execution_drift_escalation"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_7_controlled_runtime_mutation_boundary"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_8_controlled_experiment_isolation"] == EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert phase_statuses["phase_9_execution_audit_logging"] == AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_phase_1_readiness_blocked():
    assert _status(replace(_base_contract(), controlled_execution_gate_status="")) == BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS


def test_missing_phase_2_readiness_blocked():
    assert _status(replace(_base_contract(), non_production_authorization_status="")) == BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS


def test_missing_phase_3_readiness_blocked():
    assert _status(replace(_base_contract(), execution_session_sandboxing_status="")) == BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS


def test_missing_phase_4_readiness_blocked():
    assert _status(replace(_base_contract(), replay_safe_execution_scope_status="")) == BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS


def test_missing_phase_5_readiness_blocked():
    assert _status(replace(_base_contract(), rollback_execution_governance_status="")) == BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS


def test_missing_phase_6_readiness_blocked():
    assert _status(replace(_base_contract(), execution_drift_escalation_status="")) == BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS


def test_missing_phase_7_readiness_blocked():
    assert _status(replace(_base_contract(), controlled_runtime_mutation_boundary_status="")) == BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS


def test_missing_phase_8_readiness_blocked():
    assert _status(replace(_base_contract(), controlled_experiment_isolation_status="")) == BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS


def test_missing_phase_9_readiness_blocked():
    assert _status(replace(_base_contract(), execution_audit_logging_status="")) == BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS


def test_incompatible_governance_chain_blocked():
    assert _status(replace(_base_contract(), governance_chain_compatible=False)) == BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN


def test_production_behavior_detected_blocked():
    assert _status(replace(_base_contract(), production_behavior_detected=True)) == BLOCKED_PRODUCTION_BEHAVIOR_DETECTED
    assert _status(replace(_base_contract(), live_runtime_execution_enabled=True)) == BLOCKED_PRODUCTION_BEHAVIOR_DETECTED


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_deterministic_output_stability():
    first = evaluate_controlled_execution_readiness_audit(_base_contract())
    second = evaluate_controlled_execution_readiness_audit(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_controlled_execution_readiness_audit(first) == serialize_controlled_execution_readiness_audit(second)


def test_readiness_audit_does_not_authorize_execution():
    result = evaluate_controlled_execution_readiness_audit(_base_contract())

    assert result["ready_for_future_controlled_execution_planning"] is True
    assert result["controlled_execution_authorized"] is False
    assert result["prohibition_checks"]["controlled_execution_authorized"] is False
    assert result["prohibition_checks"]["execution_enabled"] is False


def test_readiness_audit_preserves_all_production_prohibitions():
    result = evaluate_controlled_execution_readiness_audit(_base_contract())
    checks = result["prohibition_checks"]

    assert checks["execution_enabled"] is False
    assert checks["production_execution_enabled"] is False
    assert checks["production_runtime_routing_authorized"] is False
    assert checks["runtime_manifest_consumption_enabled"] is False
    assert checks["production_authoritative_manifest_treatment"] is False
    assert checks["live_runtime_execution_enabled"] is False
    assert checks["live_replay_execution_enabled"] is False
    assert checks["live_rollback_execution_enabled"] is False
    assert checks["live_synthesis_execution_enabled"] is False
    assert checks["live_decision_routing_enabled"] is False
    assert checks["recommendation_logic_enabled"] is False
    assert checks["autonomous_planner_mutation_enabled"] is False
    assert checks["persistent_mutation_enabled"] is False
    assert checks["state_writes_enabled"] is False
    assert checks["external_side_effects_enabled"] is False
    assert checks["experiment_execution_enabled"] is False
    assert checks["audit_log_writing_enabled"] is False
    assert checks["production_state_access_enabled"] is False


def test_report_aggregation_from_generated_phase_reports():
    contract = build_controlled_execution_readiness_audit_from_reports()
    result = evaluate_controlled_execution_readiness_audit(contract)

    assert result["status"] == V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
    assert len(result["phase_report_evidence"]) == 9
    assert all(row["readable"] is True for row in result["phase_report_evidence"])
    assert all(row["deterministic_hash_present"] is True for row in result["phase_report_evidence"])


def test_report_covers_every_readiness_status():
    report = build_v3_4_controlled_execution_readiness_audit_report()
    distribution = report["status_distribution"]

    assert distribution[V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS] == 1
    assert distribution[BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN] == 1
    assert distribution[BLOCKED_PRODUCTION_BEHAVIOR_DETECTED] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_enablement_guards_are_stable():
    first = build_v3_4_controlled_execution_readiness_audit_report()
    second = build_v3_4_controlled_execution_readiness_audit_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["execution_enabled"] is False
    assert first["controlled_execution_authorized"] is False
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
    assert first["persistent_mutation_enabled"] is False
    assert first["state_writes_enabled"] is False
    assert first["external_side_effects_enabled"] is False
    assert first["experiment_execution_enabled"] is False
    assert first["audit_log_writing_enabled"] is False
    assert first["production_state_access_enabled"] is False
