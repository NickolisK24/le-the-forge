from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
)
from app.runtime_intelligence.controlled_experiment_isolation_contracts import (
    BLOCKED_CROSS_EXPERIMENT_STATE_ACCESS,
    BLOCKED_EXPERIMENT_ENVIRONMENT_MISMATCH,
    BLOCKED_EXPERIMENT_EXECUTION_REQUESTED,
    BLOCKED_EXPERIMENT_NOT_ISOLATED,
    BLOCKED_EXPERIMENT_SCOPE_MISSING,
    BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED,
    BLOCKED_EXPERIMENT_SESSION_MISMATCH,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_EXPERIMENT_ID,
    BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
    BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
    BLOCKED_PERSISTENT_EXPERIMENT_STATE_REQUESTED,
    BLOCKED_PRODUCTION_STATE_ACCESS_REQUESTED,
    EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_controlled_experiment_isolation_contract,
    evaluate_controlled_experiment_isolation_contract,
    serialize_controlled_experiment_isolation_result,
    summarize_controlled_experiment_isolation_result,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_runtime_mutation_boundary_contract,
)
from app.runtime_intelligence.execution_drift_escalation_contracts import (
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_execution_drift_escalation_contract,
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
from scripts.report_v3_4_controlled_experiment_isolation import build_v3_4_controlled_experiment_isolation_report


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
    drift = default_execution_drift_escalation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
    )
    mutation = default_controlled_runtime_mutation_boundary_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
    )
    return default_controlled_experiment_isolation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
    )


def _status(contract) -> str:
    return evaluate_controlled_experiment_isolation_contract(contract)["status"]


def test_valid_experiment_isolation_readiness():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())
    summary = summarize_controlled_experiment_isolation_result(result)

    assert result["status"] == EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["experiment_isolation_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase4_replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase5_rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase6_drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase7_mutation_boundary_status"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_experiment_id_blocked():
    assert _status(replace(_base_contract(), experiment_id="")) == BLOCKED_MISSING_EXPERIMENT_ID


def test_missing_experiment_scope_blocked():
    assert _status(replace(_base_contract(), experiment_scope="")) == BLOCKED_EXPERIMENT_SCOPE_MISSING


def test_unsupported_experiment_scope_blocked():
    assert _status(replace(_base_contract(), experiment_scope_supported=False)) == BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED


def test_non_isolated_experiment_blocked():
    assert _status(replace(_base_contract(), experiment_isolated=False)) == BLOCKED_EXPERIMENT_NOT_ISOLATED


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_EXPERIMENT_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_EXPERIMENT_SESSION_MISMATCH


def test_cross_experiment_state_access_blocked():
    assert _status(replace(_base_contract(), cross_experiment_state_access_requested=True)) == BLOCKED_CROSS_EXPERIMENT_STATE_ACCESS


def test_production_state_access_blocked():
    assert _status(replace(_base_contract(), production_state_access_requested=True)) == BLOCKED_PRODUCTION_STATE_ACCESS_REQUESTED


def test_persistent_experiment_state_request_blocked():
    assert _status(replace(_base_contract(), persistent_experiment_state_requested=True)) == BLOCKED_PERSISTENT_EXPERIMENT_STATE_REQUESTED


def test_experiment_execution_request_blocked():
    assert _status(replace(_base_contract(), experiment_execution_requested=True)) == BLOCKED_EXPERIMENT_EXECUTION_REQUESTED


def test_missing_mutation_boundary_link_blocked():
    assert _status(replace(_base_contract(), mutation_boundary_id="")) == BLOCKED_MISSING_MUTATION_BOUNDARY_LINK


def test_missing_drift_escalation_link_blocked():
    assert _status(replace(_base_contract(), drift_audit_id="")) == BLOCKED_MISSING_DRIFT_ESCALATION_LINK


def test_missing_rollback_governance_link_blocked():
    assert _status(replace(_base_contract(), rollback_plan_id="")) == BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_no_experiment_mutation_or_execution_behavior_enabled():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["prohibition_checks"]["execution_enabled"] is False
    assert result["prohibition_checks"]["experiment_execution_enabled"] is False
    assert result["prohibition_checks"]["mutation_execution_enabled"] is False
    assert result["prohibition_checks"]["persistent_mutation_enabled"] is False
    assert result["prohibition_checks"]["production_state_access_enabled"] is False
    assert result["prohibition_checks"]["cross_experiment_state_access_enabled"] is False


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_controlled_experiment_isolation_contract(
        replace(
            _base_contract(),
            experiment_id="",
            experiment_scope="",
            experiment_scope_supported=False,
            experiment_isolated=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_EXPERIMENT_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_EXPERIMENT_ID,
        BLOCKED_EXPERIMENT_SCOPE_MISSING,
        BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED,
        BLOCKED_EXPERIMENT_NOT_ISOLATED,
    ]


def test_deterministic_output_stability():
    first = evaluate_controlled_experiment_isolation_contract(_base_contract())
    second = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_controlled_experiment_isolation_result(first) == serialize_controlled_experiment_isolation_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["experiment_isolation_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["experiment_isolation_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["experiment_isolation_does_not_bypass_sandbox"] is True


def test_compatibility_with_phase4_replay_scope_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase4_replay_scope_compatibility"]["replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase4_replay_scope_compatibility"]["experiment_isolation_does_not_bypass_replay_scope"] is True


def test_compatibility_with_phase5_rollback_governance_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase5_rollback_governance_compatibility"]["rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase5_rollback_governance_compatibility"]["experiment_isolation_does_not_bypass_rollback_governance"] is True


def test_compatibility_with_phase6_drift_escalation_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase6_drift_escalation_compatibility"]["drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase6_drift_escalation_compatibility"]["experiment_isolation_does_not_bypass_drift_escalation"] is True


def test_compatibility_with_phase7_mutation_boundary_contracts():
    result = evaluate_controlled_experiment_isolation_contract(_base_contract())

    assert result["phase7_mutation_boundary_compatibility"]["mutation_boundary_status"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase7_mutation_boundary_compatibility"]["experiment_isolation_does_not_bypass_mutation_boundary"] is True


def test_report_covers_every_experiment_isolation_status():
    report = build_v3_4_controlled_experiment_isolation_report()
    distribution = report["status_distribution"]

    assert distribution[EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_EXPERIMENT_ID] == 1
    assert distribution[BLOCKED_EXPERIMENT_SCOPE_MISSING] == 1
    assert distribution[BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED] == 1
    assert distribution[BLOCKED_EXPERIMENT_NOT_ISOLATED] == 1
    assert distribution[BLOCKED_EXPERIMENT_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_EXPERIMENT_SESSION_MISMATCH] == 1
    assert distribution[BLOCKED_CROSS_EXPERIMENT_STATE_ACCESS] == 1
    assert distribution[BLOCKED_PRODUCTION_STATE_ACCESS_REQUESTED] == 1
    assert distribution[BLOCKED_PERSISTENT_EXPERIMENT_STATE_REQUESTED] == 1
    assert distribution[BLOCKED_EXPERIMENT_EXECUTION_REQUESTED] == 1
    assert distribution[BLOCKED_MISSING_MUTATION_BOUNDARY_LINK] == 1
    assert distribution[BLOCKED_MISSING_DRIFT_ESCALATION_LINK] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_experiment_guards_are_stable():
    first = build_v3_4_controlled_experiment_isolation_report()
    second = build_v3_4_controlled_experiment_isolation_report()

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
    assert first["persistent_mutation_enabled"] is False
    assert first["state_writes_enabled"] is False
    assert first["external_side_effects_enabled"] is False
    assert first["experiment_execution_enabled"] is False
    assert first["production_state_access_enabled"] is False
    assert first["production_mutation_enabled"] is False
    assert first["mutation_execution_enabled"] is False
    assert first["cross_experiment_state_access_enabled"] is False
