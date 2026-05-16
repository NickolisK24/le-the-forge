from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.controlled_execution_gate_contracts import (
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_execution_gate_contract,
)
from app.runtime_intelligence.execution_session_sandboxing_contracts import (
    BLOCKED_CROSS_SESSION_STATE_ACCESS,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_MISSING_AUTHORIZATION_LINK,
    BLOCKED_MISSING_GATE_LINK,
    BLOCKED_MISSING_SANDBOX_ID,
    BLOCKED_MISSING_SESSION_ID,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED,
    BLOCKED_SANDBOX_SCOPE_UNSUPPORTED,
    BLOCKED_SESSION_NOT_ISOLATED,
    MANUAL_REVIEW_REQUIRED,
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_execution_session_sandbox_contract,
    evaluate_execution_session_sandbox_contract,
    serialize_execution_session_sandbox_result,
    summarize_execution_session_sandbox_result,
)
from app.runtime_intelligence.non_production_execution_authorization_contracts import (
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_non_production_execution_authorization_contract,
)
from scripts.report_v3_4_execution_session_sandboxing import (
    build_v3_4_execution_session_sandboxing_report,
)


def _base_contract():
    return default_execution_session_sandbox_contract(
        gate_contract=default_controlled_execution_gate_contract(),
        authorization_contract=default_non_production_execution_authorization_contract(),
    )


def _status(contract) -> str:
    return evaluate_execution_session_sandbox_contract(contract)["status"]


def test_valid_sandbox_readiness():
    result = evaluate_execution_session_sandbox_contract(_base_contract())
    summary = summarize_execution_session_sandbox_result(result)

    assert result["status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["sandbox_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_session_id_blocked():
    assert _status(replace(_base_contract(), session_id="")) == BLOCKED_MISSING_SESSION_ID


def test_missing_sandbox_id_blocked():
    assert _status(replace(_base_contract(), sandbox_id="")) == BLOCKED_MISSING_SANDBOX_ID


def test_missing_authorization_link_blocked():
    assert _status(replace(_base_contract(), authorization_id="")) == BLOCKED_MISSING_AUTHORIZATION_LINK


def test_missing_gate_link_blocked():
    assert _status(replace(_base_contract(), gate_contract_id="")) == BLOCKED_MISSING_GATE_LINK


def test_non_isolated_session_blocked():
    assert _status(replace(_base_contract(), isolated=False)) == BLOCKED_SESSION_NOT_ISOLATED


def test_cross_session_access_blocked():
    assert _status(replace(_base_contract(), cross_session_access_requested=True)) == BLOCKED_CROSS_SESSION_STATE_ACCESS


def test_persistent_mutation_request_blocked():
    assert _status(replace(_base_contract(), persistent_mutation_requested=True)) == BLOCKED_PERSISTENT_MUTATION_REQUESTED


def test_external_side_effect_request_blocked():
    assert _status(replace(_base_contract(), external_side_effect_requested=True)) == BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED


def test_production_environment_request_blocked():
    assert _status(replace(_base_contract(), production_environment_requested=True)) == BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED


def test_unsupported_sandbox_scope_blocked():
    assert _status(replace(_base_contract(), sandbox_scope_supported=False)) == BLOCKED_SANDBOX_SCOPE_UNSUPPORTED


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_production_authoritative_request_blocked():
    result = evaluate_execution_session_sandbox_contract(
        replace(_base_contract(), production_authoritative_manifest_treatment=True)
    )

    assert result["status"] == BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED
    assert result["prohibition_checks"]["production_authoritative_manifest_treatment"] is True


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_execution_session_sandbox_contract(
        replace(
            _base_contract(),
            session_id="",
            sandbox_id="",
            authorization_id="",
            gate_contract_id="",
            isolated=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_SESSION_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_SESSION_ID,
        BLOCKED_MISSING_SANDBOX_ID,
        BLOCKED_MISSING_AUTHORIZATION_LINK,
        BLOCKED_MISSING_GATE_LINK,
        BLOCKED_SESSION_NOT_ISOLATED,
    ]


def test_deterministic_output_stability():
    first = evaluate_execution_session_sandbox_contract(_base_contract())
    second = evaluate_execution_session_sandbox_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_execution_session_sandbox_result(first) == serialize_execution_session_sandbox_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_execution_session_sandbox_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["sandbox_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_execution_session_sandbox_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["sandbox_does_not_bypass_authorization"] is True


def test_report_covers_every_sandbox_status():
    report = build_v3_4_execution_session_sandboxing_report()
    distribution = report["status_distribution"]

    assert distribution[SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_SESSION_ID] == 1
    assert distribution[BLOCKED_MISSING_SANDBOX_ID] == 1
    assert distribution[BLOCKED_SESSION_NOT_ISOLATED] == 1
    assert distribution[BLOCKED_CROSS_SESSION_STATE_ACCESS] == 1
    assert distribution[BLOCKED_PERSISTENT_MUTATION_REQUESTED] == 1
    assert distribution[BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED] == 1
    assert distribution[BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED] == 1
    assert distribution[BLOCKED_MISSING_AUTHORIZATION_LINK] == 1
    assert distribution[BLOCKED_MISSING_GATE_LINK] == 1
    assert distribution[BLOCKED_SANDBOX_SCOPE_UNSUPPORTED] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_execution_guards_are_stable():
    first = build_v3_4_execution_session_sandboxing_report()
    second = build_v3_4_execution_session_sandboxing_report()

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
    assert first["persistent_mutation_enabled"] is False
    assert first["cross_session_state_sharing_enabled"] is False
    assert first["external_side_effects_enabled"] is False
