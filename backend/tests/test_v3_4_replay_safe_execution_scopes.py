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
    BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_REPLAY_IDENTITY,
    BLOCKED_MISSING_REPLAY_SCOPE_ID,
    BLOCKED_REPLAY_CAPTURE_DISABLED,
    BLOCKED_REPLAY_ENVIRONMENT_MISMATCH,
    BLOCKED_REPLAY_LINEAGE_MISSING,
    BLOCKED_REPLAY_MANIFEST_MISSING,
    BLOCKED_REPLAY_MANIFEST_UNTRUSTED,
    BLOCKED_REPLAY_NOT_REQUIRED,
    BLOCKED_REPLAY_SCOPE_UNSUPPORTED,
    BLOCKED_REPLAY_SESSION_MISMATCH,
    MANUAL_REVIEW_REQUIRED,
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_replay_safe_execution_scope_contract,
    evaluate_replay_safe_execution_scope_contract,
    serialize_replay_safe_execution_scope_result,
    summarize_replay_safe_execution_scope_result,
)
from scripts.report_v3_4_replay_safe_execution_scopes import build_v3_4_replay_safe_execution_scopes_report


def _base_contract():
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    sandbox = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    return default_replay_safe_execution_scope_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
    )


def _status(contract) -> str:
    return evaluate_replay_safe_execution_scope_contract(contract)["status"]


def test_valid_replay_safe_scope_readiness():
    result = evaluate_replay_safe_execution_scope_contract(_base_contract())
    summary = summarize_replay_safe_execution_scope_result(result)

    assert result["status"] == REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["replay_scope_ready"] is True
    assert result["planning_only"] is True
    assert result["blockers"] == []
    assert summary["phase1_gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase2_authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert summary["phase3_sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING


def test_missing_replay_scope_id_blocked():
    assert _status(replace(_base_contract(), replay_scope_id="")) == BLOCKED_MISSING_REPLAY_SCOPE_ID


def test_missing_replay_identity_blocked():
    assert _status(replace(_base_contract(), replay_identity="")) == BLOCKED_MISSING_REPLAY_IDENTITY


def test_replay_not_required_blocked():
    assert _status(replace(_base_contract(), replay_required=False)) == BLOCKED_REPLAY_NOT_REQUIRED


def test_replay_capture_disabled_blocked():
    assert _status(replace(_base_contract(), replay_capture_enabled=False)) == BLOCKED_REPLAY_CAPTURE_DISABLED


def test_missing_replay_manifest_blocked():
    assert _status(replace(_base_contract(), replay_manifest_present=False)) == BLOCKED_REPLAY_MANIFEST_MISSING


def test_untrusted_replay_manifest_blocked():
    assert _status(replace(_base_contract(), replay_manifest_trusted=False)) == BLOCKED_REPLAY_MANIFEST_UNTRUSTED


def test_missing_replay_lineage_blocked():
    assert _status(replace(_base_contract(), replay_lineage_present=False)) == BLOCKED_REPLAY_LINEAGE_MISSING


def test_unsupported_replay_scope_blocked():
    assert _status(replace(_base_contract(), replay_scope_supported=False)) == BLOCKED_REPLAY_SCOPE_UNSUPPORTED


def test_live_replay_execution_request_blocked():
    assert _status(replace(_base_contract(), live_replay_execution_requested=True)) == BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED


def test_environment_mismatch_blocked():
    assert _status(replace(_base_contract(), environment="ci", expected_environment="non_production")) == BLOCKED_REPLAY_ENVIRONMENT_MISMATCH


def test_session_mismatch_blocked():
    assert _status(replace(_base_contract(), session_id="session-mismatch")) == BLOCKED_REPLAY_SESSION_MISMATCH


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_replay_manifest_execution_and_production_authority_remain_disabled():
    result = evaluate_replay_safe_execution_scope_contract(
        replace(_base_contract(), production_authoritative_manifest_treatment=True)
    )

    assert result["prohibition_checks"]["replay_manifest_execution_enabled"] is False
    assert result["prohibition_checks"]["replay_manifest_production_authoritative"] is False
    assert result["prohibition_checks"]["production_authoritative_manifest_treatment"] is True


def test_blockers_accumulate_without_hiding_statuses():
    result = evaluate_replay_safe_execution_scope_contract(
        replace(
            _base_contract(),
            replay_scope_id="",
            replay_identity="",
            replay_required=False,
            replay_capture_enabled=False,
        )
    )

    assert result["status"] == BLOCKED_MISSING_REPLAY_SCOPE_ID
    assert [row["status"] for row in result["blockers"]] == [
        BLOCKED_MISSING_REPLAY_SCOPE_ID,
        BLOCKED_MISSING_REPLAY_IDENTITY,
        BLOCKED_REPLAY_NOT_REQUIRED,
        BLOCKED_REPLAY_CAPTURE_DISABLED,
    ]


def test_deterministic_output_stability():
    first = evaluate_replay_safe_execution_scope_contract(_base_contract())
    second = evaluate_replay_safe_execution_scope_contract(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_replay_safe_execution_scope_result(first) == serialize_replay_safe_execution_scope_result(second)


def test_compatibility_with_phase1_gate_contracts():
    result = evaluate_replay_safe_execution_scope_contract(_base_contract())

    assert result["phase1_gate_compatibility"]["gate_status"] == ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase1_gate_compatibility"]["replay_scope_does_not_bypass_gate"] is True


def test_compatibility_with_phase2_authorization_contracts():
    result = evaluate_replay_safe_execution_scope_contract(_base_contract())

    assert result["phase2_authorization_compatibility"]["authorization_status"] == AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase2_authorization_compatibility"]["replay_scope_does_not_bypass_authorization"] is True


def test_compatibility_with_phase3_sandboxing_contracts():
    result = evaluate_replay_safe_execution_scope_contract(_base_contract())

    assert result["phase3_sandbox_compatibility"]["sandbox_status"] == SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING
    assert result["phase3_sandbox_compatibility"]["replay_scope_does_not_bypass_sandbox"] is True


def test_report_covers_every_replay_scope_status():
    report = build_v3_4_replay_safe_execution_scopes_report()
    distribution = report["status_distribution"]

    assert distribution[REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_REPLAY_SCOPE_ID] == 1
    assert distribution[BLOCKED_MISSING_REPLAY_IDENTITY] == 1
    assert distribution[BLOCKED_REPLAY_NOT_REQUIRED] == 1
    assert distribution[BLOCKED_REPLAY_CAPTURE_DISABLED] == 1
    assert distribution[BLOCKED_REPLAY_MANIFEST_MISSING] == 1
    assert distribution[BLOCKED_REPLAY_MANIFEST_UNTRUSTED] == 1
    assert distribution[BLOCKED_REPLAY_LINEAGE_MISSING] == 1
    assert distribution[BLOCKED_REPLAY_SCOPE_UNSUPPORTED] == 1
    assert distribution[BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED] == 1
    assert distribution[BLOCKED_REPLAY_ENVIRONMENT_MISMATCH] == 1
    assert distribution[BLOCKED_REPLAY_SESSION_MISMATCH] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_execution_guards_are_stable():
    first = build_v3_4_replay_safe_execution_scopes_report()
    second = build_v3_4_replay_safe_execution_scopes_report()

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
    assert first["replay_manifest_execution_enabled"] is False
    assert first["replay_manifest_production_authoritative"] is False
