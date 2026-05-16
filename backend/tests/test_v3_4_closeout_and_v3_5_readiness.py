from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_intelligence.v3_4_closeout_readiness_audit import (
    BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE,
    BLOCKED_MISSING_PHASE_1_CONTRACTS,
    BLOCKED_MISSING_PHASE_2_CONTRACTS,
    BLOCKED_MISSING_PHASE_3_CONTRACTS,
    BLOCKED_MISSING_PHASE_4_CONTRACTS,
    BLOCKED_MISSING_PHASE_5_CONTRACTS,
    BLOCKED_MISSING_PHASE_6_CONTRACTS,
    BLOCKED_MISSING_PHASE_7_CONTRACTS,
    BLOCKED_MISSING_PHASE_8_CONTRACTS,
    BLOCKED_MISSING_PHASE_9_CONTRACTS,
    BLOCKED_MISSING_PHASE_10_READINESS_AUDIT,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    MANUAL_REVIEW_REQUIRED,
    V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
    build_v3_4_closeout_readiness_audit_from_reports,
    default_v3_4_closeout_readiness_audit_contract,
    evaluate_v3_4_closeout_readiness_audit,
    serialize_v3_4_closeout_readiness_audit,
    summarize_v3_4_closeout_readiness_audit,
)
from scripts.report_v3_4_closeout_and_v3_5_readiness import build_v3_4_closeout_and_v3_5_readiness_report


def _base_contract():
    return default_v3_4_closeout_readiness_audit_contract()


def _status(contract) -> str:
    return evaluate_v3_4_closeout_readiness_audit(contract)["status"]


def test_valid_v3_4_closeout_readiness():
    result = evaluate_v3_4_closeout_readiness_audit(_base_contract())
    summary = summarize_v3_4_closeout_readiness_audit(result)

    assert result["status"] == V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING
    assert result["v3_4_closed_out"] is True
    assert result["v3_5_planning_may_begin"] is True
    assert result["controlled_execution_authorized"] is False
    assert result["planning_only"] is True
    assert result["audit_only"] is True
    assert result["blockers"] == []
    assert summary["v3_4_closed_out"] is True
    assert len(result["phase_closeout"]) == 10
    assert all(row["closed_out"] is True for row in result["phase_closeout"])


def test_missing_phase_1_blocked():
    assert _status(replace(_base_contract(), phase_1_status="")) == BLOCKED_MISSING_PHASE_1_CONTRACTS


def test_missing_phase_2_blocked():
    assert _status(replace(_base_contract(), phase_2_status="")) == BLOCKED_MISSING_PHASE_2_CONTRACTS


def test_missing_phase_3_blocked():
    assert _status(replace(_base_contract(), phase_3_status="")) == BLOCKED_MISSING_PHASE_3_CONTRACTS


def test_missing_phase_4_blocked():
    assert _status(replace(_base_contract(), phase_4_status="")) == BLOCKED_MISSING_PHASE_4_CONTRACTS


def test_missing_phase_5_blocked():
    assert _status(replace(_base_contract(), phase_5_status="")) == BLOCKED_MISSING_PHASE_5_CONTRACTS


def test_missing_phase_6_blocked():
    assert _status(replace(_base_contract(), phase_6_status="")) == BLOCKED_MISSING_PHASE_6_CONTRACTS


def test_missing_phase_7_blocked():
    assert _status(replace(_base_contract(), phase_7_status="")) == BLOCKED_MISSING_PHASE_7_CONTRACTS


def test_missing_phase_8_blocked():
    assert _status(replace(_base_contract(), phase_8_status="")) == BLOCKED_MISSING_PHASE_8_CONTRACTS


def test_missing_phase_9_blocked():
    assert _status(replace(_base_contract(), phase_9_status="")) == BLOCKED_MISSING_PHASE_9_CONTRACTS


def test_missing_phase_10_blocked():
    assert _status(replace(_base_contract(), phase_10_status="")) == BLOCKED_MISSING_PHASE_10_READINESS_AUDIT


def test_incompatible_governance_chain_blocked():
    assert _status(replace(_base_contract(), governance_chain_compatible=False)) == BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE


def test_production_behavior_detected_blocked():
    assert _status(replace(_base_contract(), production_behavior_detected=True)) == BLOCKED_PRODUCTION_BEHAVIOR_DETECTED
    assert _status(replace(_base_contract(), production_runtime_routing_authorized=True)) == BLOCKED_PRODUCTION_BEHAVIOR_DETECTED


def test_manual_review_required():
    assert _status(replace(_base_contract(), manual_review_required=True)) == MANUAL_REVIEW_REQUIRED


def test_deterministic_output_stability():
    first = evaluate_v3_4_closeout_readiness_audit(_base_contract())
    second = evaluate_v3_4_closeout_readiness_audit(_base_contract())

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_v3_4_closeout_readiness_audit(first) == serialize_v3_4_closeout_readiness_audit(second)


def test_closeout_audit_does_not_authorize_execution():
    result = evaluate_v3_4_closeout_readiness_audit(_base_contract())

    assert result["v3_5_planning_may_begin"] is True
    assert result["controlled_execution_authorized"] is False
    assert result["prohibition_checks"]["controlled_execution_authorized"] is False
    assert result["prohibition_checks"]["execution_enabled"] is False


def test_closeout_audit_preserves_all_production_prohibitions():
    checks = evaluate_v3_4_closeout_readiness_audit(_base_contract())["prohibition_checks"]

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
    contract = build_v3_4_closeout_readiness_audit_from_reports()
    result = evaluate_v3_4_closeout_readiness_audit(contract)

    assert result["status"] == V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING
    assert len(result["phase_report_evidence"]) == 10
    assert all(row["readable"] is True for row in result["phase_report_evidence"])
    assert all(row["deterministic_hash_present"] is True for row in result["phase_report_evidence"])


def test_report_covers_every_closeout_status():
    report = build_v3_4_closeout_and_v3_5_readiness_report()
    distribution = report["status_distribution"]

    assert distribution[V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_PHASE_1_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_2_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_3_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_4_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_5_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_6_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_7_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_8_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_9_CONTRACTS] == 1
    assert distribution[BLOCKED_MISSING_PHASE_10_READINESS_AUDIT] == 1
    assert distribution[BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE] == 1
    assert distribution[BLOCKED_PRODUCTION_BEHAVIOR_DETECTED] == 1
    assert distribution[MANUAL_REVIEW_REQUIRED] == 1


def test_report_serialization_and_non_enablement_guards_are_stable():
    first = build_v3_4_closeout_and_v3_5_readiness_report()
    second = build_v3_4_closeout_and_v3_5_readiness_report()

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
