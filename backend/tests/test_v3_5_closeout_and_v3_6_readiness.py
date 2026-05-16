from __future__ import annotations

import copy
import json
from pathlib import Path

from app.runtime_orchestration import (
    V3_5_BLOCKED_BY_EXECUTION_LEAK,
    V3_5_BLOCKED_BY_INVALID_PHASE_STATUS,
    V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_5_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_5_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY,
    V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK,
    V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING,
    V3_5_PHASE_SPECS,
    V3_5_REQUIRES_MANUAL_REVIEW,
    V3_6_PLANNING_ALLOWED,
    V3_6_PLANNING_BLOCKED,
    V3_6_PLANNING_REQUIRES_MANUAL_REVIEW,
    V35CloseoutReadinessInput,
    audit_v3_5_closeout_readiness,
    export_v3_5_closeout_readiness_result,
    hash_v3_5_closeout_result,
    serialize_v3_5_closeout_readiness_result,
)
from scripts.report_v3_5_closeout_and_v3_6_readiness import build_v3_5_closeout_and_v3_6_readiness_report


REPO_ROOT = Path(__file__).resolve().parents[2]


def _phase_reports():
    return {
        spec.phase_id: json.loads((REPO_ROOT / spec.report_path).read_text(encoding="utf-8"))
        for spec in V3_5_PHASE_SPECS
    }


def _phase_docs():
    return {spec.phase_id: (REPO_ROOT / spec.documentation_path).exists() for spec in V3_5_PHASE_SPECS}


def _input(reports=None, docs=None, **kwargs):
    return V35CloseoutReadinessInput(
        repo_root=REPO_ROOT,
        phase_reports=reports if reports is not None else _phase_reports(),
        phase_documentation_present=docs if docs is not None else _phase_docs(),
        **kwargs,
    )


def _export(source=None):
    return export_v3_5_closeout_readiness_result(audit_v3_5_closeout_readiness(source or _input()))


def test_deterministic_closeout_classification():
    first = _export()
    second = _export()

    assert first["closeout_status"] == V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING
    assert first["v3_6_planning_readiness"] == V3_6_PLANNING_ALLOWED
    assert first["deterministic_closeout_hash"] == second["deterministic_closeout_hash"]
    assert first["planning_only"] is True


def test_stable_serialization_and_hash_output():
    result = audit_v3_5_closeout_readiness(_input())

    assert serialize_v3_5_closeout_readiness_result(result) == serialize_v3_5_closeout_readiness_result(audit_v3_5_closeout_readiness(_input()))
    assert hash_v3_5_closeout_result(result) == hash_v3_5_closeout_result(audit_v3_5_closeout_readiness(_input()))


def test_required_report_and_documentation_coverage():
    result = _export()

    assert result["phase_coverage_summary"]["expected_phase_count"] == 9
    assert result["phase_coverage_summary"]["report_present_count"] == 9
    assert result["phase_coverage_summary"]["documentation_present_count"] == 9
    assert result["missing_report_list"] == []
    assert result["missing_documentation_list"] == []


def test_missing_phase_report_detection():
    reports = _phase_reports()
    reports["phase_4"] = None
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_MISSING_PHASE_REPORT
    assert result["v3_6_planning_readiness"] == V3_6_PLANNING_BLOCKED
    assert result["missing_report_list"] == ["phase_4"]


def test_missing_documentation_detection():
    docs = _phase_docs()
    docs["phase_5"] = False
    result = _export(_input(docs=docs))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_MISSING_DOCUMENTATION
    assert result["missing_documentation_list"] == ["phase_5"]


def test_invalid_phase_status_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_2"]["final_readiness_status"] = "blocked_by_governance_dependency"
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_INVALID_PHASE_STATUS
    assert result["invalid_phase_status_list"] == ["phase_2"]


def test_missing_hash_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_9"].pop("deterministic_report_hash", None)
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH
    assert result["missing_deterministic_hash_list"] == ["phase_9"]


def test_missing_scenario_coverage_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_3"]["summary"]["scenario_count"] = 0
    reports["phase_3"]["scenario_results"] = {}
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE
    assert result["missing_scenario_coverage_list"] == ["phase_3"]


def test_execution_leak_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_1"]["runtime_execution_enabled"] = True
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_EXECUTION_LEAK
    assert result["prohibition_preservation_summary"] == ["execution_leak:phase_1"]


def test_production_consumption_leak_detection():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_6"]["explicit_non_execution_guarantees"]["production_consumption_enabled"] = True
    result = _export(_input(reports=reports))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK
    assert result["prohibition_preservation_summary"] == ["production_consumption_leak:phase_6"]


def test_phase_chain_incompatibility_detection():
    result = _export(_input(phase_chain_compatible=False))

    assert result["closeout_status"] == V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY
    assert result["compatibility_blocker_summary"] == ["phase_chain_compatibility"]


def test_v3_6_readiness_classification_and_manual_review_preservation():
    result = _export(_input(manual_review_reasons=("manual_closeout_review",)))

    assert result["closeout_status"] == V3_5_REQUIRES_MANUAL_REVIEW
    assert result["v3_6_planning_readiness"] == V3_6_PLANNING_REQUIRES_MANUAL_REVIEW
    assert result["manual_review_summary"] == ["manual_closeout_review"]


def test_limitation_preservation():
    result = _export()

    assert "closeout audit inspects declarative generated artifacts only" in result["limitation_summary"]
    assert "closeout audit does not repair missing reports, infer missing evidence, persist audit state, or enable v3.6 behavior" in result["limitation_summary"]


def test_non_execution_guarantees():
    result = _export()

    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["audit_log_writing_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["graph_traversal_behavior_enabled"] is False
    assert result["scheduling_behavior_enabled"] is False
    assert result["orchestration_dispatch_enabled"] is False
    assert result["runtime_trace_capture_enabled"] is False
    assert result["production_state_reads_enabled"] is False
    assert result["live_replay_enabled"] is False
    assert result["persistent_audit_storage_enabled"] is False
    assert result["v3_6_behavior_enabled"] is False


def test_report_scenario_coverage_and_stability():
    first = build_v3_5_closeout_and_v3_6_readiness_report(REPO_ROOT)
    second = build_v3_5_closeout_and_v3_6_readiness_report(REPO_ROOT)
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["summary"]["scenario_count"] == 11
    assert first["final_closeout_status"] == V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING
    assert first["v3_6_planning_readiness_classification"] == V3_6_PLANNING_ALLOWED
    assert distribution[V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING] == 1
    assert distribution[V3_5_BLOCKED_BY_MISSING_PHASE_REPORT] == 1
    assert distribution[V3_5_BLOCKED_BY_MISSING_DOCUMENTATION] == 1
    assert distribution[V3_5_BLOCKED_BY_INVALID_PHASE_STATUS] == 1
    assert distribution[V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH] == 2
    assert distribution[V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE] == 1
    assert distribution[V3_5_BLOCKED_BY_EXECUTION_LEAK] == 1
    assert distribution[V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK] == 1
    assert distribution[V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY] == 1
    assert distribution[V3_5_REQUIRES_MANUAL_REVIEW] == 1


def test_report_preserves_non_execution_guarantees():
    guarantees = build_v3_5_closeout_and_v3_6_readiness_report(REPO_ROOT)["explicit_non_execution_guarantees"]

    assert guarantees["runtime_execution_enabled"] is False
    assert guarantees["orchestration_execution_enabled"] is False
    assert guarantees["routing_behavior_enabled"] is False
    assert guarantees["mutation_behavior_enabled"] is False
    assert guarantees["audit_log_writing_enabled"] is False
    assert guarantees["production_consumption_enabled"] is False
    assert guarantees["graph_execution_enabled"] is False
    assert guarantees["graph_traversal_behavior_enabled"] is False
    assert guarantees["scheduling_behavior_enabled"] is False
    assert guarantees["orchestration_dispatch_enabled"] is False
    assert guarantees["runtime_trace_capture_enabled"] is False
    assert guarantees["production_state_reads_enabled"] is False
    assert guarantees["live_replay_enabled"] is False
    assert guarantees["persistent_audit_storage_enabled"] is False
    assert guarantees["v3_6_behavior_enabled"] is False
