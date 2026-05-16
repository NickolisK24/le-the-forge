from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
)
from app.runtime_intelligence.non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH,
    BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING,
    BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING,
    BLOCKED_AUTHORIZATION_SESSION_MISMATCH,
    BLOCKED_EXPIRED_AUTHORIZATION,
    BLOCKED_INVALID_AUTHORIZATION_SCOPE,
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED,
    MANUAL_REVIEW_REQUIRED,
    default_non_production_execution_authorization_contract,
    evaluate_non_production_execution_authorization_contract,
    serialize_non_production_execution_authorization_result,
    summarize_non_production_execution_authorization_result,
)
from scripts.report_v3_4_non_production_execution_authorization import (
    build_v3_4_non_production_execution_authorization_report,
)


def _status(contract) -> str:
    return evaluate_non_production_execution_authorization_contract(contract)["status"]


def test_valid_non_production_authorization():
    result = evaluate_non_production_execution_authorization_contract(
        default_non_production_execution_authorization_contract()
    )
    summary = summarize_non_production_execution_authorization_result(result)

    assert result["status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["authorized"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_authorization_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        authorization_id="",
        authorized_by="",
        authorization_state="missing",
    )

    assert _status(contract) == BLOCKED_MISSING_AUTHORIZATION


def test_expired_authorization_blocked():
    contract = replace(default_non_production_execution_authorization_contract(), expiration_state="expired")

    assert _status(contract) == BLOCKED_EXPIRED_AUTHORIZATION


def test_production_authorization_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        production_authorization_requested=True,
    )

    assert _status(contract) == BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED


def test_environment_mismatch_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        requested_environment="production",
    )

    assert _status(contract) == BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        requested_session_id="other-session",
    )

    assert _status(contract) == BLOCKED_AUTHORIZATION_SESSION_MISMATCH


def test_invalid_authorization_scope_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        authorization_scope="unrestricted_runtime",
    )

    assert _status(contract) == BLOCKED_INVALID_AUTHORIZATION_SCOPE


def test_missing_replay_requirement_blocked():
    contract = replace(default_non_production_execution_authorization_contract(), replay_required=False)

    assert _status(contract) == BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING


def test_missing_rollback_requirement_blocked():
    contract = replace(default_non_production_execution_authorization_contract(), rollback_required=False)

    assert _status(contract) == BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING


def test_manual_review_required():
    contract = replace(default_non_production_execution_authorization_contract(), manual_review_required=True)

    assert _status(contract) == MANUAL_REVIEW_REQUIRED


def test_unknown_authorization_state_does_not_silently_approve():
    contract = replace(default_non_production_execution_authorization_contract(), authorization_state="unknown")

    assert _status(contract) == BLOCKED_MISSING_AUTHORIZATION


def test_production_authoritative_request_is_blocked():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        production_authoritative_requested=True,
    )
    result = evaluate_non_production_execution_authorization_contract(contract)

    assert result["status"] == BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED
    assert result["prohibition_checks"]["production_authoritative_manifest_treatment"] is True


def test_blockers_accumulate_without_hiding_statuses():
    contract = replace(
        default_non_production_execution_authorization_contract(),
        authorization_id="",
        authorized_by="",
        authorization_state="missing",
        replay_required=False,
        rollback_required=False,
    )
    result = evaluate_non_production_execution_authorization_contract(contract)

    assert result["status"] == BLOCKED_MISSING_AUTHORIZATION
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_AUTHORIZATION,
        BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING,
        BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING,
    ]


def test_deterministic_output_stability():
    first = evaluate_non_production_execution_authorization_contract(
        default_non_production_execution_authorization_contract()
    )
    second = evaluate_non_production_execution_authorization_contract(
        default_non_production_execution_authorization_contract()
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_non_production_execution_authorization_result(first) == serialize_non_production_execution_authorization_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_non_production_execution_authorization_contract(
        default_non_production_execution_authorization_contract()
    )

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["gate_eligible"] is True
    assert result["phase1_gate_compatibility"]["authorization_does_not_bypass_gate"] is True


def test_report_covers_every_authorization_status():
    report = build_v3_4_non_production_execution_authorization_report()
    distribution = report["status_distribution"]

    assert distribution[AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_AUTHORIZATION] == 1
    assert distribution[BLOCKED_INVALID_AUTHORIZATION_SCOPE] == 1
    assert distribution[BLOCKED_EXPIRED_AUTHORIZATION] == 1
    assert distribution[BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED] == 1
    assert distribution[BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_AUTHORIZATION_SESSION_MISMATCH] == 1
    assert distribution[BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING] == 1
    assert distribution[BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_execution_guards_are_stable():
    first = build_v3_4_non_production_execution_authorization_report()
    second = build_v3_4_non_production_execution_authorization_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["execution_enabled"] is False
    assert first["production_execution_enabled"] is False
    assert first["production_authorization_enabled"] is False
    assert first["production_runtime_routing_authorized"] is False
    assert first["runtime_manifest_consumption_enabled"] is False
    assert first["production_authoritative_manifest_treatment"] is False
    assert first["live_runtime_execution_enabled"] is False
    assert first["live_replay_execution_enabled"] is False
    assert first["live_synthesis_execution_enabled"] is False
    assert first["live_decision_routing_enabled"] is False
    assert first["recommendation_logic_enabled"] is False
    assert first["autonomous_planner_mutation_enabled"] is False
