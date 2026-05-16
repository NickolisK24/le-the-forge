from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_MISSING_REPLAY_REQUIREMENT,
    BLOCKED_MISSING_ROLLBACK_REQUIREMENT,
    BLOCKED_MISSING_SESSION_ISOLATION,
    BLOCKED_PRODUCTION_EXECUTION_PROHIBITED,
    BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED,
    BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED,
    BLOCKED_UNSUPPORTED_EXECUTION_SCOPE,
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_controlled_execution_gate_contract,
    evaluate_controlled_execution_gate_contract,
    serialize_controlled_execution_gate_result,
    summarize_controlled_execution_gate_result,
)
from scripts.report_v3_4_controlled_execution_gate_contracts import (
    build_v3_4_controlled_execution_gate_contracts_report,
)


def _status(contract) -> str:
    return evaluate_controlled_execution_gate_contract(contract)["status"]


def test_valid_controlled_execution_planning_eligibility():
    result = evaluate_controlled_execution_gate_contract(default_controlled_execution_gate_contract())
    summary = summarize_controlled_execution_gate_result(result)

    assert result["status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["eligible"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["production_execution_enabled"] is False


def test_production_execution_blocked():
    contract = replace(default_controlled_execution_gate_contract(), environment="production")

    assert _status(contract) == BLOCKED_PRODUCTION_EXECUTION_PROHIBITED


def test_missing_authorization_blocked():
    contract = replace(default_controlled_execution_gate_contract(), authorization_state="missing")

    assert _status(contract) == BLOCKED_MISSING_AUTHORIZATION


def test_missing_rollback_blocked():
    contract = replace(default_controlled_execution_gate_contract(), rollback_required=False)

    assert _status(contract) == BLOCKED_MISSING_ROLLBACK_REQUIREMENT


def test_missing_replay_blocked():
    contract = replace(default_controlled_execution_gate_contract(), replay_required=False)

    assert _status(contract) == BLOCKED_MISSING_REPLAY_REQUIREMENT


def test_missing_session_isolation_blocked():
    contract = replace(default_controlled_execution_gate_contract(), session_isolated=False)

    assert _status(contract) == BLOCKED_MISSING_SESSION_ISOLATION


def test_unsupported_execution_scope_blocked():
    contract = replace(default_controlled_execution_gate_contract(), execution_scope="unrestricted_runtime")

    assert _status(contract) == BLOCKED_UNSUPPORTED_EXECUTION_SCOPE


def test_decision_routing_request_blocked():
    contract = replace(default_controlled_execution_gate_contract(), decision_routing_requested=True)

    assert _status(contract) == BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED


def test_recommendation_request_blocked():
    contract = replace(default_controlled_execution_gate_contract(), recommendation_requested=True)

    assert _status(contract) == BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED


def test_production_authoritative_request_blocked():
    contract = replace(default_controlled_execution_gate_contract(), production_authoritative_requested=True)
    result = evaluate_controlled_execution_gate_contract(contract)

    assert result["status"] == BLOCKED_PRODUCTION_EXECUTION_PROHIBITED
    assert result["prohibition_checks"]["production_authoritative_manifest_treatment"] is True
    assert result["eligible"] is False


def test_manual_review_required_for_drift_escalation():
    contract = replace(default_controlled_execution_gate_contract(), drift_escalation_required=True)

    assert _status(contract) == MANUAL_REVIEW_REQUIRED


def test_explicit_prohibition_inputs_are_blocked():
    base = default_controlled_execution_gate_contract()
    prohibited_contracts = [
        replace(base, runtime_manifest_consumption_enabled=True),
        replace(base, live_runtime_execution_enabled=True),
        replace(base, live_replay_execution_enabled=True),
        replace(base, live_synthesis_execution_enabled=True),
        replace(base, autonomous_planner_mutation_enabled=True),
    ]

    for contract in prohibited_contracts:
        assert _status(contract) == BLOCKED_PRODUCTION_EXECUTION_PROHIBITED


def test_blockers_accumulate_without_hiding_statuses():
    contract = replace(
        default_controlled_execution_gate_contract(),
        authorization_state="missing",
        replay_required=False,
        rollback_required=False,
        session_isolated=False,
    )
    result = evaluate_controlled_execution_gate_contract(contract)

    assert result["status"] == BLOCKED_MISSING_AUTHORIZATION
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_AUTHORIZATION,
        BLOCKED_MISSING_REPLAY_REQUIREMENT,
        BLOCKED_MISSING_ROLLBACK_REQUIREMENT,
        BLOCKED_MISSING_SESSION_ISOLATION,
    ]


def test_deterministic_output_stability():
    first = evaluate_controlled_execution_gate_contract(default_controlled_execution_gate_contract())
    second = evaluate_controlled_execution_gate_contract(default_controlled_execution_gate_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_controlled_execution_gate_result(first) == serialize_controlled_execution_gate_result(second)


def test_report_covers_all_allowed_and_blocking_statuses():
    report = build_v3_4_controlled_execution_gate_contracts_report()
    distribution = report["status_distribution"]

    assert distribution[ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_PRODUCTION_EXECUTION_PROHIBITED] == 2
    assert distribution[BLOCKED_MISSING_AUTHORIZATION] == 1
    assert distribution[BLOCKED_MISSING_REPLAY_REQUIREMENT] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_REQUIREMENT] == 1
    assert distribution[BLOCKED_MISSING_SESSION_ISOLATION] == 1
    assert distribution[BLOCKED_UNSUPPORTED_EXECUTION_SCOPE] == 1
    assert distribution[BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED] == 1
    assert distribution[BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_consumption_guards_are_stable():
    first = build_v3_4_controlled_execution_gate_contracts_report()
    second = build_v3_4_controlled_execution_gate_contracts_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["execution_enabled"] is False
    assert first["production_execution_enabled"] is False
    assert first["production_runtime_routing_authorized"] is False
    assert first["runtime_manifest_consumption_enabled"] is False
    assert first["production_authoritative_manifest_treatment"] is False
    assert first["live_runtime_execution_enabled"] is False
    assert first["live_replay_execution_enabled"] is False
    assert first["live_synthesis_execution_enabled"] is False
    assert first["live_decision_routing_enabled"] is False
    assert first["recommendation_logic_enabled"] is False
    assert first["autonomous_planner_mutation_enabled"] is False
