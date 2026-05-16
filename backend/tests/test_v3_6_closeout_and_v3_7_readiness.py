from __future__ import annotations

import copy
import json
from pathlib import Path

from app.runtime_orchestration import (
    V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE,
    V3_6_BLOCKED_BY_EXECUTION_LEAKAGE,
    V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE,
    V3_6_BLOCKED_BY_INTEGRITY_FAILURE,
    V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE,
    V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_6_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_6_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY,
    V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR,
    V3_6_BLOCKED_BY_PROVENANCE_FAILURE,
    V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE,
    V3_6_BLOCKED_FOR_V3_7_PLANNING,
    V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING,
    V3_6_PHASE_SPECS,
    V3_6_REQUIRES_MANUAL_REVIEW,
    V36CloseoutReadinessInput,
    audit_v3_6_closeout_readiness,
    export_v3_6_closeout_readiness_result,
    hash_v3_6_closeout_result,
    serialize_v3_6_closeout_readiness_result,
)
from scripts.report_v3_6_closeout_and_v3_7_readiness import (
    build_v3_6_closeout_and_v3_7_readiness_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _phase_reports():
    return {
        spec.phase_id: json.loads((REPO_ROOT / spec.report_path).read_text(encoding="utf-8"))
        for spec in V3_6_PHASE_SPECS
    }


def _phase_docs():
    return {spec.phase_id: (REPO_ROOT / spec.documentation_path).exists() for spec in V3_6_PHASE_SPECS}


def _input(reports=None, docs=None, **kwargs):
    return V36CloseoutReadinessInput(
        repo_root=REPO_ROOT,
        phase_reports=reports if reports is not None else _phase_reports(),
        phase_documentation_present=docs if docs is not None else _phase_docs(),
        **kwargs,
    )


def _export(source=None):
    return export_v3_6_closeout_readiness_result(audit_v3_6_closeout_readiness(source or _input()))


def _remove_token_keys(report: dict[str, object], token: str) -> None:
    for key in tuple(report.keys()):
        if token in key:
            report.pop(key, None)


def test_deterministic_closeout_classification():
    first = _export()
    second = _export()

    assert first["closeout_status"] == V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING
    assert first["v3_7_readiness_classification"] == V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING
    assert first["deterministic_closeout_hash"] == second["deterministic_closeout_hash"]
    assert first["planning_only"] is True


def test_stable_serialization_and_hash_output():
    result = audit_v3_6_closeout_readiness(_input())
    replay = audit_v3_6_closeout_readiness(_input())

    assert serialize_v3_6_closeout_readiness_result(result) == serialize_v3_6_closeout_readiness_result(replay)
    assert hash_v3_6_closeout_result(result) == hash_v3_6_closeout_result(replay)


def test_full_v3_6_phase_continuity():
    result = _export()

    assert result["phase_coverage_summary"]["audited_phase_count"] == 9
    assert result["phase_coverage_summary"]["valid_phase_count"] == 9
    assert result["phase_coverage_summary"]["invalid_phase_count"] == 0
    assert result["missing_report_list"] == []
    assert result["missing_documentation_list"] == []
    assert result["missing_continuity_evidence_list"] == []


def test_replay_and_rollback_continuity():
    result = _export()

    assert result["replay_continuity_failure_list"] == []
    assert result["rollback_continuity_failure_list"] == []
    assert all(phase["replay_continuity_preserved"] for phase in result["phase_results"])
    assert all(phase["rollback_continuity_preserved"] for phase in result["phase_results"])


def test_provenance_explainability_integrity_and_blocker_continuity():
    result = _export()

    assert result["provenance_failure_list"] == []
    assert result["explainability_failure_list"] == []
    assert result["integrity_failure_list"] == []
    assert result["blocker_visibility_failure_list"] == []
    assert result["unsupported_prohibited_visibility_failure_list"] == []


def test_missing_phase_report_detection():
    reports = _phase_reports()
    reports["phase_3_resolution_auditing"] = None
    result = _export(_input(reports=reports))

    assert result["v3_7_readiness_classification"] == V3_6_BLOCKED_FOR_V3_7_PLANNING
    assert result["missing_report_list"] == ["phase_3_resolution_auditing"]
    assert V3_6_BLOCKED_BY_MISSING_PHASE_REPORT in result["readiness_blocker_summary"]


def test_missing_documentation_detection():
    docs = _phase_docs()
    docs["phase_5_intent_policy_mapping"] = False
    result = _export(_input(docs=docs))

    assert result["missing_documentation_list"] == ["phase_5_intent_policy_mapping"]
    assert V3_6_BLOCKED_BY_MISSING_DOCUMENTATION in result["readiness_blocker_summary"]


def test_missing_hash_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_9_chain_integrity_audit"].pop("deterministic_report_hash", None)
    result = _export(_input(reports=reports))

    assert result["missing_deterministic_hash_list"] == ["phase_9_chain_integrity_audit"]
    assert V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH in result["readiness_blocker_summary"]


def test_missing_scenario_coverage_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_4_intent_modeling"]["scenario_results"] = {}
    reports["phase_4_intent_modeling"]["scenario_coverage"] = []
    result = _export(_input(reports=reports))

    assert result["missing_scenario_coverage_list"] == ["phase_4_intent_modeling"]
    assert V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE in result["readiness_blocker_summary"]


def test_missing_continuity_evidence_detection():
    reports = copy.deepcopy(_phase_reports())
    for key in tuple(reports["phase_1_policy_intelligence"].keys()):
        if key.endswith("_continuity_status"):
            reports["phase_1_policy_intelligence"].pop(key, None)
    result = _export(_input(reports=reports))

    assert result["missing_continuity_evidence_list"] == ["phase_1_policy_intelligence"]
    assert V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE in result["readiness_blocker_summary"]


def test_replay_and_rollback_failure_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_8_replay_packets"]["replay_safety_confirmation"] = False
    reports["phase_7_evaluation_trace_modeling"]["rollback_safety_confirmation"] = False
    result = _export(_input(reports=reports))

    assert result["replay_continuity_failure_list"] == ["phase_8_replay_packets"]
    assert result["rollback_continuity_failure_list"] == ["phase_7_evaluation_trace_modeling"]
    assert V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE in result["readiness_blocker_summary"]
    assert V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE in result["readiness_blocker_summary"]


def test_provenance_explainability_and_integrity_failure_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_6_preflight_evaluation"]["provenance_continuity_status"] = "preflight_continuity_gap"
    reports["phase_5_intent_policy_mapping"]["explainability_continuity_status"] = "mapping_continuity_gap"
    reports["phase_2_compatibility_intelligence"]["integrity_continuity_status"] = "compatibility_continuity_gap"
    result = _export(_input(reports=reports))

    assert result["provenance_failure_list"] == ["phase_6_preflight_evaluation"]
    assert result["explainability_failure_list"] == ["phase_5_intent_policy_mapping"]
    assert result["integrity_failure_list"] == ["phase_2_compatibility_intelligence"]
    assert V3_6_BLOCKED_BY_PROVENANCE_FAILURE in result["readiness_blocker_summary"]
    assert V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE in result["readiness_blocker_summary"]
    assert V3_6_BLOCKED_BY_INTEGRITY_FAILURE in result["readiness_blocker_summary"]


def test_blocker_and_unsupported_prohibited_visibility_detection():
    reports = copy.deepcopy(_phase_reports())
    _remove_token_keys(reports["phase_1_policy_intelligence"], "blocker")
    _remove_token_keys(reports["phase_3_resolution_auditing"], "unsupported")
    _remove_token_keys(reports["phase_3_resolution_auditing"], "prohibited")
    result = _export(_input(reports=reports))

    assert result["blocker_visibility_failure_list"] == ["phase_1_policy_intelligence"]
    assert result["unsupported_prohibited_visibility_failure_list"] == ["phase_3_resolution_auditing"]
    assert V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE in result["readiness_blocker_summary"]
    assert V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE in result["readiness_blocker_summary"]


def test_execution_prohibition_and_runtime_prohibition_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_1_policy_intelligence"]["orchestration_execution_enabled"] = True
    reports["phase_4_intent_modeling"]["recommendation_behavior_enabled"] = True
    result = _export(_input(reports=reports))

    assert result["execution_leakage_list"] == ["phase_1_policy_intelligence"]
    assert result["prohibited_runtime_behavior_list"] == ["phase_4_intent_modeling"]
    assert V3_6_BLOCKED_BY_EXECUTION_LEAKAGE in result["readiness_blocker_summary"]
    assert V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR in result["readiness_blocker_summary"]


def test_phase_chain_and_manual_review_block_readiness():
    disconnected = _export(_input(phase_chain_connected=False))
    manual = _export(_input(manual_review_reasons=("manual_v3_6_closeout_review",)))

    assert disconnected["phase_chain_blocker_summary"] == ["phase_chain_connected"]
    assert V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY in disconnected["readiness_blocker_summary"]
    assert manual["manual_review_summary"] == ["manual_v3_6_closeout_review"]
    assert V3_6_REQUIRES_MANUAL_REVIEW in manual["readiness_blocker_summary"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["persistent_write_enabled"] is False
    assert result["production_runtime_behavior_enabled"] is False
    assert result["production_state_reads_enabled"] is False
    assert result["live_runtime_reads_enabled"] is False
    assert result["background_execution_enabled"] is False
    assert result["scheduling_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["autonomous_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["execution_planning_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False


def test_report_scenario_coverage_and_stability():
    first = build_v3_6_closeout_and_v3_7_readiness_report(REPO_ROOT)
    second = build_v3_6_closeout_and_v3_7_readiness_report(REPO_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 17
    assert first["audited_phase_count"] == 9
    assert first["valid_phase_count"] == 9
    assert first["invalid_phase_count"] == 0
    assert first["v3_7_readiness_classification"] == V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING
    assert first["status_distribution"][V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING] == 1
    assert first["status_distribution"][V3_6_BLOCKED_FOR_V3_7_PLANNING] == 16
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
