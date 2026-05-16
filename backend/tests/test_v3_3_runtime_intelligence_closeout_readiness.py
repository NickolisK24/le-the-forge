from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from app.runtime_intelligence.closeout_readiness_audit import (
    EXPECTED_PHASE_REPORTS,
    V3_3_BLOCKED_GOVERNANCE_COVERAGE_GAP,
    V3_3_BLOCKED_HASH_OR_REPLAY_VALIDATION_FAILURE,
    V3_3_BLOCKED_INVALID_CROSS_CONTRACT_REFERENCES,
    V3_3_BLOCKED_MISSING_REPORTS,
    V3_3_BLOCKED_PLANNING_ONLY_VIOLATION,
    V3_3_BLOCKED_PRODUCTION_AUTHORIZATION_DETECTED,
    V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
    build_runtime_intelligence_closeout_readiness_audit,
    evaluate_runtime_intelligence_closeout_readiness_audit,
    load_phase_reports,
    serialize_runtime_intelligence_closeout_readiness_audit,
    summarize_runtime_intelligence_closeout_readiness_audit,
)
from scripts.report_v3_3_runtime_intelligence_closeout_readiness import (
    build_v3_3_runtime_intelligence_closeout_readiness_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _phase_reports() -> dict[str, dict]:
    return load_phase_reports(REPO_ROOT)


def _mutate_summary(phase_reports: dict[str, dict], phase_id: str, key: str, value) -> dict[str, dict]:
    mutated = deepcopy(phase_reports)
    mutated[phase_id]["report"]["summary"][key] = value
    return mutated


def test_closeout_audit_happy_path():
    audit = build_runtime_intelligence_closeout_readiness_audit(repo_root=REPO_ROOT)
    evaluation = evaluate_runtime_intelligence_closeout_readiness_audit(audit)
    summary = summarize_runtime_intelligence_closeout_readiness_audit(audit)

    assert audit["readiness_status"] == V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
    assert evaluation["passed"] is True
    assert summary["audited_phase_count"] == summary["expected_phase_count"] == 11
    assert audit["summary"]["missing_report_count"] == 0
    assert audit["summary"]["invalid_cross_contract_reference_failure_count"] == 0
    assert audit["summary"]["production_authorized_contract_detection_count"] == 0
    assert audit["summary"]["planning_only_violation_count"] == 0
    assert audit["summary"]["governance_coverage_gap_count"] == 0
    assert audit["safety_confirmations"]["runtime_intelligence_remains_planning_only"] is True


def test_missing_report_detection():
    reports = _phase_reports()
    reports.pop("phase_3_runtime_provenance")
    audit = build_runtime_intelligence_closeout_readiness_audit(phase_reports=reports)

    assert audit["readiness_status"] == V3_3_BLOCKED_MISSING_REPORTS
    assert audit["summary"]["missing_report_count"] == 1
    assert audit["readiness_blockers"]


def test_unreadable_or_malformed_report_detection(tmp_path: Path):
    for phase in EXPECTED_PHASE_REPORTS:
        target = tmp_path / phase["report_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if phase["phase_id"] == "phase_1_runtime_intelligence_classification":
            target.write_text("{malformed", encoding="utf-8")
        else:
            source = REPO_ROOT / phase["report_path"]
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    audit = build_runtime_intelligence_closeout_readiness_audit(repo_root=tmp_path)

    assert audit["readiness_status"] == V3_3_BLOCKED_MISSING_REPORTS
    assert audit["summary"]["unreadable_report_count"] == 1


def test_stable_hash_failure_detection():
    audit = build_runtime_intelligence_closeout_readiness_audit(
        phase_reports=_mutate_summary(_phase_reports(), "phase_5_runtime_explanation", "stable_hash_valid", False)
    )

    assert audit["readiness_status"] == V3_3_BLOCKED_HASH_OR_REPLAY_VALIDATION_FAILURE
    assert audit["summary"]["stable_hash_validation_failure_count"] == 1


def test_replay_validation_failure_detection():
    audit = build_runtime_intelligence_closeout_readiness_audit(
        phase_reports=_mutate_summary(_phase_reports(), "phase_9_runtime_replay_orchestration", "replay_validation_passed", False)
    )

    assert audit["readiness_status"] == V3_3_BLOCKED_HASH_OR_REPLAY_VALIDATION_FAILURE
    assert audit["summary"]["replay_validation_failure_count"] == 1


def test_invalid_cross_contract_reference_detection():
    audit = build_runtime_intelligence_closeout_readiness_audit(
        phase_reports=_mutate_summary(_phase_reports(), "phase_7_runtime_evidence_synthesis", "invalid_confidence_reference_count", 1)
    )

    assert audit["readiness_status"] == V3_3_BLOCKED_INVALID_CROSS_CONTRACT_REFERENCES
    assert audit["summary"]["invalid_cross_contract_reference_failure_count"] == 1
    assert audit["compatibility_chain_validation"]["passed"] is False


def test_production_authorized_contract_detection():
    audit = build_runtime_intelligence_closeout_readiness_audit(
        phase_reports=_mutate_summary(_phase_reports(), "phase_8_runtime_decision_boundary", "production_authorized_boundary_count", 1)
    )

    assert audit["readiness_status"] == V3_3_BLOCKED_PRODUCTION_AUTHORIZATION_DETECTED
    assert audit["summary"]["production_authorized_contract_detection_count"] == 1


def test_planning_only_violation_detection():
    reports = _phase_reports()
    reports["phase_11_runtime_session_governance"]["report"]["live_session_execution_enabled"] = True
    audit = build_runtime_intelligence_closeout_readiness_audit(phase_reports=reports)

    assert audit["readiness_status"] == V3_3_BLOCKED_PLANNING_ONLY_VIOLATION
    assert audit["summary"]["planning_only_violation_count"] == 1


def test_governance_coverage_gap_detection():
    audit = build_runtime_intelligence_closeout_readiness_audit(
        phase_reports=_mutate_summary(_phase_reports(), "phase_11_runtime_session_governance", "session_isolating_contract_count", 0)
    )

    assert audit["readiness_status"] == V3_3_BLOCKED_GOVERNANCE_COVERAGE_GAP
    assert "session_isolation" in audit["governance_coverage_validation"]["coverage_gaps"]


def test_explicit_production_prohibition_confirmation():
    audit = build_runtime_intelligence_closeout_readiness_audit(repo_root=REPO_ROOT)

    assert audit["production_runtime_prohibited"] is True
    assert audit["production_runtime_routing_authorized"] is False
    assert audit["runtime_manifest_consumption_enabled"] is False
    assert audit["production_authoritative_manifest_treatment"] is False
    assert audit["safety_confirmations"]["passing_readiness_does_not_authorize_production_runtime_behavior"] is True


def test_deterministic_repeat_run_stability():
    first = build_runtime_intelligence_closeout_readiness_audit(repo_root=REPO_ROOT)
    second = build_runtime_intelligence_closeout_readiness_audit(repo_root=REPO_ROOT)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["replay_validation_results"]["replay_stable"] is True
    assert serialize_runtime_intelligence_closeout_readiness_audit(first) == serialize_runtime_intelligence_closeout_readiness_audit(second)


def test_generated_report_serialization_stability():
    first = build_v3_3_runtime_intelligence_closeout_readiness_report(REPO_ROOT)
    second = build_v3_3_runtime_intelligence_closeout_readiness_report(REPO_ROOT)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["readiness_status"] == V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING
    assert first["summary"]["production_authorized_contract_detection_count"] == 0
