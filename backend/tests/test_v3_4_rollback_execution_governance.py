from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
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
    BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_ROLLBACK_PLAN_ID,
    BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH,
    BLOCKED_ROLLBACK_LINEAGE_MISSING,
    BLOCKED_ROLLBACK_NOT_REQUIRED,
    BLOCKED_ROLLBACK_PLAN_MISSING,
    BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED,
    BLOCKED_ROLLBACK_SESSION_MISMATCH,
    BLOCKED_ROLLBACK_TARGET_MISSING,
    BLOCKED_ROLLBACK_VALIDATION_MISSING,
    MANUAL_REVIEW_REQUIRED,
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_rollback_execution_governance_contract,
    evaluate_rollback_execution_governance_contract,
    serialize_rollback_execution_governance_result,
    summarize_rollback_execution_governance_result,
)
from scripts.report_v3_4_rollback_execution_governance import build_v3_4_rollback_execution_governance_report


def _base_contract():
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    sandbox = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    replay_scope = default_replay_safe_execution_scope_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
    )
    return default_rollback_execution_governance_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
    )


def _status(contract) -> str:
    return evaluate_rollback_execution_governance_contract(contract)["status"]


def test_valid_rollback_governance_readiness():
    result = evaluate_rollback_execution_governance_contract(_base_contract())
    summary = summarize_rollback_execution_governance_result(result)

    assert result["status"] == ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["rollback_governance_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase4_replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_rollback_plan_id_blocked():
    assert _status(replace(_base_contract(), rollback_plan_id="")) == BLOCKED_MISSING_ROLLBACK_PLAN_ID


def test_rollback_not_required_blocked():
    assert _status(replace(_base_contract(), rollback_required=False)) == BLOCKED_ROLLBACK_NOT_REQUIRED


def test_missing_rollback_plan_blocked():
    assert _status(replace(_base_contract(), rollback_plan_present=False)) == BLOCKED_ROLLBACK_PLAN_MISSING


def test_missing_rollback_lineage_blocked():
    assert _status(replace(_base_contract(), rollback_lineage_present=False)) == BLOCKED_ROLLBACK_LINEAGE_MISSING


def test_missing_rollback_target_blocked():
    assert _status(replace(_base_contract(), rollback_target_present=False)) == BLOCKED_ROLLBACK_TARGET_MISSING


def test_missing_rollback_validation_blocked():
    assert _status(replace(_base_contract(), rollback_validation_present=False)) == BLOCKED_ROLLBACK_VALIDATION_MISSING


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_ROLLBACK_SESSION_MISMATCH


def test_unsupported_rollback_scope_blocked():
    assert _status(replace(_base_contract(), rollback_scope_supported=False)) == BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED


def test_live_rollback_execution_request_blocked():
    assert _status(replace(_base_contract(), live_rollback_execution_requested=True)) == BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_rollback_plan_execution_and_production_authority_remain_disabled():
    result = evaluate_rollback_execution_governance_contract(
        replace(_base_contract(), production_authoritative_manifest_treatment=True)
    )

    assert result["prohibition_checks"]["rollback_plan_execution_enabled"] is False
    assert result["prohibition_checks"]["production_authoritative_manifest_treatment"] is True


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_rollback_execution_governance_contract(
        replace(
            _base_contract(),
            rollback_plan_id="",
            rollback_required=False,
            rollback_plan_present=False,
            rollback_lineage_present=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_ROLLBACK_PLAN_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_ROLLBACK_PLAN_ID,
        BLOCKED_ROLLBACK_NOT_REQUIRED,
        BLOCKED_ROLLBACK_PLAN_MISSING,
        BLOCKED_ROLLBACK_LINEAGE_MISSING,
    ]


def test_deterministic_output_stability():
    first = evaluate_rollback_execution_governance_contract(_base_contract())
    second = evaluate_rollback_execution_governance_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_rollback_execution_governance_result(first) == serialize_rollback_execution_governance_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_rollback_execution_governance_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["rollback_governance_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_rollback_execution_governance_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["rollback_governance_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_rollback_execution_governance_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["rollback_governance_does_not_bypass_sandbox"] is True


def test_compatibility_with_phase4_replay_scope_contracts():
    result = evaluate_rollback_execution_governance_contract(_base_contract())

    assert result["phase4_replay_scope_compatibility"]["replay_scope_status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase4_replay_scope_compatibility"]["rollback_governance_does_not_bypass_replay_scope"] is True


def test_report_covers_every_rollback_governance_status():
    report = build_v3_4_rollback_execution_governance_report()
    distribution = report["status_distribution"]

    assert distribution[ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_PLAN_ID] == 1
    assert distribution[BLOCKED_ROLLBACK_NOT_REQUIRED] == 1
    assert distribution[BLOCKED_ROLLBACK_PLAN_MISSING] == 1
    assert distribution[BLOCKED_ROLLBACK_LINEAGE_MISSING] == 1
    assert distribution[BLOCKED_ROLLBACK_TARGET_MISSING] == 1
    assert distribution[BLOCKED_ROLLBACK_VALIDATION_MISSING] == 1
    assert distribution[BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_ROLLBACK_SESSION_MISMATCH] == 1
    assert distribution[BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED] == 1
    assert distribution[BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_execution_guards_are_stable():
    first = build_v3_4_rollback_execution_governance_report()
    second = build_v3_4_rollback_execution_governance_report()

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
    assert first["rollback_plan_execution_enabled"] is False
