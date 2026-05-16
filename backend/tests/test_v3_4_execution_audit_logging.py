from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
)
from app.runtime_intelligence.controlled_experiment_isolation_contracts import (
    EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_experiment_isolation_contract,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_runtime_mutation_boundary_contract,
)
from app.runtime_intelligence.execution_audit_logging_contracts import (
    AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    BLOCKED_AUDIT_ACTOR_MISSING,
    BLOCKED_AUDIT_ENVIRONMENT_MISMATCH,
    BLOCKED_AUDIT_EVENT_TYPE_MISSING,
    BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED,
    BLOCKED_AUDIT_HASH_MISSING,
    BLOCKED_AUDIT_LINEAGE_MISSING,
    BLOCKED_AUDIT_SESSION_MISMATCH,
    BLOCKED_AUDIT_TIMESTAMP_MISSING,
    BLOCKED_AUDIT_WRITE_REQUESTED,
    BLOCKED_MISSING_AUDIT_RECORD_ID,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK,
    BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
    MANUAL_REVIEW_REQUIRED,
    default_execution_audit_logging_contract,
    evaluate_execution_audit_logging_contract,
    serialize_execution_audit_logging_result,
    summarize_execution_audit_logging_result,
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
from scripts.report_v3_4_execution_audit_logging import build_v3_4_execution_audit_logging_report


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
    experiment = default_controlled_experiment_isolation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
    )
    return default_execution_audit_logging_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
        experiment_isolation_contract=experiment,
    )


def _status(contract) -> str:
    return evaluate_execution_audit_logging_contract(contract)["status"]


def test_valid_audit_logging_readiness():
    result = evaluate_execution_audit_logging_contract(_base_contract())
    summary = summarize_execution_audit_logging_result(result)

    assert result["status"] == AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["audit_logging_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase4_replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase5_rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase6_drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase7_mutation_boundary_status"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase8_experiment_isolation_status"] == EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_audit_record_id_blocked():
    assert _status(replace(_base_contract(), audit_record_id="")) == BLOCKED_MISSING_AUDIT_RECORD_ID


def test_missing_audit_event_type_blocked():
    assert _status(replace(_base_contract(), audit_event_type="")) == BLOCKED_AUDIT_EVENT_TYPE_MISSING


def test_unsupported_audit_event_type_blocked():
    assert _status(replace(_base_contract(), audit_event_type="unsupported_event")) == BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED


def test_missing_audit_hash_blocked():
    assert _status(replace(_base_contract(), audit_hash_present=False)) == BLOCKED_AUDIT_HASH_MISSING


def test_missing_audit_lineage_blocked():
    assert _status(replace(_base_contract(), audit_lineage_present=False)) == BLOCKED_AUDIT_LINEAGE_MISSING


def test_missing_audit_timestamp_blocked():
    assert _status(replace(_base_contract(), audit_timestamp_present=False)) == BLOCKED_AUDIT_TIMESTAMP_MISSING


def test_missing_audit_actor_blocked():
    assert _status(replace(_base_contract(), audit_actor_present=False)) == BLOCKED_AUDIT_ACTOR_MISSING


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_AUDIT_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_AUDIT_SESSION_MISMATCH


def test_audit_write_request_blocked():
    assert _status(replace(_base_contract(), audit_write_requested=True)) == BLOCKED_AUDIT_WRITE_REQUESTED


def test_missing_experiment_isolation_link_blocked():
    assert _status(replace(_base_contract(), experiment_id="")) == BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK


def test_missing_mutation_boundary_link_blocked():
    assert _status(replace(_base_contract(), mutation_boundary_id="")) == BLOCKED_MISSING_MUTATION_BOUNDARY_LINK


def test_missing_drift_escalation_link_blocked():
    assert _status(replace(_base_contract(), drift_audit_id="")) == BLOCKED_MISSING_DRIFT_ESCALATION_LINK


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_no_audit_writing_experiment_mutation_or_execution_behavior_enabled():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["prohibition_checks"]["execution_enabled"] is False
    assert result["prohibition_checks"]["experiment_execution_enabled"] is False
    assert result["prohibition_checks"]["mutation_execution_enabled"] is False
    assert result["prohibition_checks"]["audit_log_writing_enabled"] is False
    assert result["prohibition_checks"]["persistent_mutation_enabled"] is False
    assert result["prohibition_checks"]["production_state_access_enabled"] is False


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_execution_audit_logging_contract(
        replace(
            _base_contract(),
            audit_record_id="",
            audit_event_type="",
            audit_hash_present=False,
            audit_lineage_present=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_AUDIT_RECORD_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_AUDIT_RECORD_ID,
        BLOCKED_AUDIT_EVENT_TYPE_MISSING,
        BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED,
        BLOCKED_AUDIT_HASH_MISSING,
        BLOCKED_AUDIT_LINEAGE_MISSING,
    ]


def test_deterministic_output_stability():
    first = evaluate_execution_audit_logging_contract(_base_contract())
    second = evaluate_execution_audit_logging_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_execution_audit_logging_result(first) == serialize_execution_audit_logging_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["audit_logging_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["audit_logging_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["audit_logging_does_not_bypass_sandbox"] is True


def test_compatibility_with_phase4_replay_scope_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase4_replay_scope_compatibility"]["replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase4_replay_scope_compatibility"]["audit_logging_does_not_bypass_replay_scope"] is True


def test_compatibility_with_phase5_rollback_governance_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase5_rollback_governance_compatibility"]["rollback_governance_status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase5_rollback_governance_compatibility"]["audit_logging_does_not_bypass_rollback_governance"] is True


def test_compatibility_with_phase6_drift_escalation_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase6_drift_escalation_compatibility"]["drift_escalation_status"] == DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase6_drift_escalation_compatibility"]["audit_logging_does_not_bypass_drift_escalation"] is True


def test_compatibility_with_phase7_mutation_boundary_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase7_mutation_boundary_compatibility"]["mutation_boundary_status"] == MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase7_mutation_boundary_compatibility"]["audit_logging_does_not_bypass_mutation_boundary"] is True


def test_compatibility_with_phase8_experiment_isolation_contracts():
    result = evaluate_execution_audit_logging_contract(_base_contract())

    assert result["phase8_experiment_isolation_compatibility"]["experiment_isolation_status"] == EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase8_experiment_isolation_compatibility"]["audit_logging_does_not_bypass_experiment_isolation"] is True


def test_report_covers_every_audit_logging_status():
    report = build_v3_4_execution_audit_logging_report()
    distribution = report["status_distribution"]

    assert distribution[AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_AUDIT_RECORD_ID] == 1
    assert distribution[BLOCKED_AUDIT_EVENT_TYPE_MISSING] == 1
    assert distribution[BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED] == 1
    assert distribution[BLOCKED_AUDIT_HASH_MISSING] == 1
    assert distribution[BLOCKED_AUDIT_LINEAGE_MISSING] == 1
    assert distribution[BLOCKED_AUDIT_TIMESTAMP_MISSING] == 1
    assert distribution[BLOCKED_AUDIT_ACTOR_MISSING] == 1
    assert distribution[BLOCKED_AUDIT_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_AUDIT_SESSION_MISMATCH] == 1
    assert distribution[BLOCKED_AUDIT_WRITE_REQUESTED] == 1
    assert distribution[BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK] == 1
    assert distribution[BLOCKED_MISSING_MUTATION_BOUNDARY_LINK] == 1
    assert distribution[BLOCKED_MISSING_DRIFT_ESCALATION_LINK] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_write_guards_are_stable():
    first = build_v3_4_execution_audit_logging_report()
    second = build_v3_4_execution_audit_logging_report()

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
    assert first["audit_log_writing_enabled"] is False
    assert first["production_state_access_enabled"] is False
    assert first["production_mutation_enabled"] is False
    assert first["mutation_execution_enabled"] is False
    assert first["cross_experiment_state_access_enabled"] is False
