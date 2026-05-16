from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (
    BLOCKED_AUTONOMOUS_MUTATION_REQUESTED,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_MUTATION_BOUNDARY_ID,
    BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
    BLOCKED_MUTATION_ENVIRONMENT_MISMATCH,
    BLOCKED_MUTATION_SCOPE_MISSING,
    BLOCKED_MUTATION_SCOPE_UNSUPPORTED,
    BLOCKED_MUTATION_SESSION_MISMATCH,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_PRODUCTION_MUTATION_REQUESTED,
    BLOCKED_STATE_WRITE_REQUESTED,
    MANUAL_REVIEW_REQUIRED,
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_runtime_mutation_boundary_contract,
    evaluate_controlled_runtime_mutation_boundary_contract,
    serialize_controlled_runtime_mutation_boundary_result,
    summarize_controlled_runtime_mutation_boundary_result,
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
from scripts.report_v3_4_controlled_runtime_mutation_boundaries import (
    build_v3_4_controlled_runtime_mutation_boundaries_report,
)


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
    return default_controlled_runtime_mutation_boundary_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
    )


def _status(contract) -> str:
    return evaluate_controlled_runtime_mutation_boundary_contract(contract)["status"]


def test_valid_mutation_boundary_readiness():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())
    summary = summarize_controlled_runtime_mutation_boundary_result(result)

    assert result["status"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["mutation_boundary_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase4_replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase5_rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase6_drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_mutation_boundary_id_blocked():
    assert _status(replace(_base_contract(), mutation_boundary_id="")) == BLOCKED_MISSING_MUTATION_BOUNDARY_ID


def test_missing_mutation_scope_blocked():
    assert _status(replace(_base_contract(), mutation_scope="")) == BLOCKED_MUTATION_SCOPE_MISSING


def test_unsupported_mutation_scope_blocked():
    assert _status(replace(_base_contract(), mutation_scope_supported=False)) == BLOCKED_MUTATION_SCOPE_UNSUPPORTED


def test_persistent_mutation_request_blocked():
    assert _status(replace(_base_contract(), persistent_mutation_requested=True)) == BLOCKED_PERSISTENT_MUTATION_REQUESTED


def test_production_mutation_request_blocked():
    assert _status(replace(_base_contract(), production_mutation_requested=True)) == BLOCKED_PRODUCTION_MUTATION_REQUESTED


def test_autonomous_mutation_request_blocked():
    assert _status(replace(_base_contract(), autonomous_mutation_requested=True)) == BLOCKED_AUTONOMOUS_MUTATION_REQUESTED


def test_external_side_effect_request_blocked():
    assert _status(replace(_base_contract(), external_side_effect_requested=True)) == BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED


def test_state_write_request_blocked():
    assert _status(replace(_base_contract(), state_write_requested=True)) == BLOCKED_STATE_WRITE_REQUESTED


def test_missing_rollback_governance_link_blocked():
    assert _status(replace(_base_contract(), rollback_plan_id="")) == BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK


def test_missing_drift_escalation_link_blocked():
    assert _status(replace(_base_contract(), drift_audit_id="")) == BLOCKED_MISSING_DRIFT_ESCALATION_LINK


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_MUTATION_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_MUTATION_SESSION_MISMATCH


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_no_mutation_or_execution_behavior_enabled():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["prohibition_checks"]["execution_enabled"] is False
    assert result["prohibition_checks"]["mutation_execution_enabled"] is False
    assert result["prohibition_checks"]["persistent_mutation_enabled"] is False
    assert result["prohibition_checks"]["production_mutation_enabled"] is False
    assert result["prohibition_checks"]["state_writes_enabled"] is False
    assert result["prohibition_checks"]["external_side_effects_enabled"] is False


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_controlled_runtime_mutation_boundary_contract(
        replace(
            _base_contract(),
            mutation_boundary_id="",
            mutation_scope="",
            mutation_scope_supported=False,
            persistent_mutation_requested=True,
        )
    )

    assert result["status"] == BLOCKED_MISSING_MUTATION_BOUNDARY_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_MUTATION_BOUNDARY_ID,
        BLOCKED_MUTATION_SCOPE_MISSING,
        BLOCKED_MUTATION_SCOPE_UNSUPPORTED,
        BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    ]


def test_deterministic_output_stability():
    first = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())
    second = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_controlled_runtime_mutation_boundary_result(first) == serialize_controlled_runtime_mutation_boundary_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["mutation_boundary_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["mutation_boundary_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["mutation_boundary_does_not_bypass_sandbox"] is True


def test_compatibility_with_phase4_replay_scope_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase4_replay_scope_compatibility"]["replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase4_replay_scope_compatibility"]["mutation_boundary_does_not_bypass_replay_scope"] is True


def test_compatibility_with_phase5_rollback_governance_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase5_rollback_governance_compatibility"]["rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase5_rollback_governance_compatibility"]["mutation_boundary_does_not_bypass_rollback_governance"] is True


def test_compatibility_with_phase6_drift_escalation_contracts():
    result = evaluate_controlled_runtime_mutation_boundary_contract(_base_contract())

    assert result["phase6_drift_escalation_compatibility"]["drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase6_drift_escalation_compatibility"]["mutation_boundary_does_not_bypass_drift_escalation"] is True


def test_report_covers_every_mutation_boundary_status():
    report = build_v3_4_controlled_runtime_mutation_boundaries_report()
    distribution = report["status_distribution"]

    assert distribution[MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_MUTATION_BOUNDARY_ID] == 1
    assert distribution[BLOCKED_MUTATION_SCOPE_MISSING] == 1
    assert distribution[BLOCKED_MUTATION_SCOPE_UNSUPPORTED] == 1
    assert distribution[BLOCKED_PERSISTENT_MUTATION_REQUESTED] == 1
    assert distribution[BLOCKED_PRODUCTION_MUTATION_REQUESTED] == 1
    assert distribution[BLOCKED_AUTONOMOUS_MUTATION_REQUESTED] == 1
    assert distribution[BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED] == 1
    assert distribution[BLOCKED_STATE_WRITE_REQUESTED] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK] == 1
    assert distribution[BLOCKED_MISSING_DRIFT_ESCALATION_LINK] == 1
    assert distribution[BLOCKED_MUTATION_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_MUTATION_SESSION_MISMATCH] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_mutation_guards_are_stable():
    first = build_v3_4_controlled_runtime_mutation_boundaries_report()
    second = build_v3_4_controlled_runtime_mutation_boundaries_report()

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
    assert first["production_mutation_enabled"] is False
    assert first["mutation_execution_enabled"] is False
