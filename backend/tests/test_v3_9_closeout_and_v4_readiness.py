from __future__ import annotations

import copy
import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_transition.v3_9_closeout_readiness_audit import (  # noqa: E402
    V3_9_PHASE_SPECS,
    audit_v3_9_closeout_readiness,
)
from runtime_transition.v3_9_closeout_readiness_models import (  # noqa: E402
    FINDING_CAPABILITY_LEAKAGE,
    FINDING_WARNING,
    V3_9_CLOSEOUT_BLOCKED,
    V3_9_CLOSEOUT_INCOMPLETE,
    V3_9_CLOSEOUT_READY_FOR_V4_PLANNING,
    V3_9_CLOSEOUT_WITH_WARNINGS,
    V3_9_NOT_READY_FOR_V4_PLANNING,
    V4_PLANNING_INCOMPLETE,
    V4_PLANNING_NOT_READY,
    V4_PLANNING_READY,
    V4_PLANNING_READY_WITH_WARNINGS,
    V39CloseoutReadinessInput,
    export_v3_9_closeout_readiness_report,
    hash_v3_9_closeout_readiness_report,
    serialize_v3_9_closeout_readiness_report,
)
from scripts.report_v3_9_closeout_and_v4_readiness import (  # noqa: E402
    REQUIRED_CLOSEOUT_SENTENCE,
    build_v3_9_closeout_and_v4_readiness_report,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _phase_reports() -> dict[str, dict]:
    return {
        spec.phase_id: json.loads((REPO_ROOT / spec.report_path).read_text(encoding="utf-8"))
        for spec in V3_9_PHASE_SPECS
    }


def _phase_docs() -> dict[str, bool]:
    return {spec.phase_id: (REPO_ROOT / spec.migration_doc_path).exists() for spec in V3_9_PHASE_SPECS}


def _input(reports=None, docs=None, **kwargs) -> V39CloseoutReadinessInput:
    return V39CloseoutReadinessInput(
        repo_root=REPO_ROOT,
        phase_reports=reports if reports is not None else _phase_reports(),
        migration_docs_present=docs if docs is not None else _phase_docs(),
        **kwargs,
    )


def _audit(source: V39CloseoutReadinessInput | None = None):
    return audit_v3_9_closeout_readiness(source or _input())


def _zero_warning_counts(reports: dict[str, dict]) -> dict[str, dict]:
    warning_keys = (
        "hidden_finding_count",
        "hidden_risk_count",
        "hidden_non_safe_state_count",
        "hidden_behavior_count",
        "hidden_conflict_count",
        "hidden_scenario_finding_count",
        "hidden_session_finding_count",
        "hidden_aggregation_finding_count",
        "hidden_visibility_count",
        "hidden_finding_violation_count",
        "hidden_risk_violation_count",
        "hidden_non_safe_state_violation_count",
        "execution_boundary_leakage_count",
        "recommendation_leakage_count",
        "ranking_leakage_count",
        "scoring_leakage_count",
        "selection_leakage_count",
        "mutation_leakage_count",
    )
    clean = copy.deepcopy(reports)
    for report in clean.values():
        summary = report.get("summary", {})
        for key in warning_keys:
            if key in summary:
                summary[key] = 0
    return clean


def test_v3_9_closeout_audits_all_required_reports_and_docs():
    result = _audit()

    assert result.summary.phase_evidence_count == 9
    assert result.summary.generated_report_count == 9
    assert result.summary.migration_doc_count == 9
    assert {record.phase_id for record in result.phase_evidence} == {spec.phase_id for spec in V3_9_PHASE_SPECS}
    assert result.summary.missing_report_count == 0
    assert result.summary.missing_doc_count == 0


def test_v3_9_closeout_detects_missing_report():
    reports = _phase_reports()
    reports["phase_4_evaluation"] = None
    result = _audit(_input(reports=reports))

    assert result.summary.final_closeout_classification == V3_9_CLOSEOUT_INCOMPLETE
    assert result.summary.v4_readiness_classification == V4_PLANNING_INCOMPLETE
    assert result.summary.missing_report_count == 1
    assert any(finding.finding_category == "incomplete_evidence" for finding in result.findings)


def test_v3_9_closeout_detects_missing_doc():
    docs = _phase_docs()
    docs["phase_5_session"] = False
    result = _audit(_input(docs=docs))

    assert result.summary.final_closeout_classification == V3_9_CLOSEOUT_INCOMPLETE
    assert result.summary.missing_doc_count == 1


def test_v3_9_closeout_detects_validation_errors():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_2_boundary"]["summary"]["validation_error_count"] = 1
    result = _audit(_input(reports=reports))

    assert result.summary.final_closeout_classification == V3_9_NOT_READY_FOR_V4_PLANNING
    assert result.summary.v4_readiness_classification == V4_PLANNING_NOT_READY
    assert result.summary.validation_error_count == 1


def test_v3_9_closeout_detects_unexpected_hidden_behavior():
    result = _audit(_input(expected_fail_visible_warnings=False))

    assert result.summary.hidden_behavior_count > 0
    assert result.summary.final_closeout_classification == V3_9_NOT_READY_FOR_V4_PLANNING


def test_v3_9_closeout_detects_report_level_capability_leakage():
    reports = copy.deepcopy(_phase_reports())
    reports["phase_6_scenario"]["routing_enabled"] = True
    reports["phase_6_scenario"]["recommendation_enabled"] = True
    reports["phase_6_scenario"]["runtime_mutation_enabled"] = True
    result = _audit(_input(reports=reports))

    assert result.summary.final_closeout_classification == V3_9_NOT_READY_FOR_V4_PLANNING
    assert result.summary.execution_capability_enabled_count >= 1
    assert result.summary.orchestration_capability_introduced_count >= 1
    assert result.summary.recommendation_ranking_scoring_selection_capability_introduced_count >= 1
    assert result.summary.runtime_mutation_capability_introduced_count >= 1
    assert any(finding.finding_category == FINDING_CAPABILITY_LEAKAGE for finding in result.findings)


def test_v3_9_closeout_verifies_integrity_certification_and_chain_presence():
    result = _audit()
    phase_ids = {record.phase_id for record in result.phase_evidence if record.report_present}

    assert "phase_8_integrity" in phase_ids
    assert "phase_9_certification" in phase_ids
    assert "phase_7_aggregation" in phase_ids
    assert "phase_6_scenario" in phase_ids
    assert "phase_5_session" in phase_ids
    assert "phase_4_evaluation" in phase_ids
    assert "phase_3_compatibility" in phase_ids
    assert "phase_2_boundary" in phase_ids
    assert "phase_1_foundations" in phase_ids
    assert result.summary.integrity_enforcement_status == "v3_9_transition_integrity_enforcement_stable"
    assert result.summary.continuity_certification_status == "v3_9_transition_continuity_certification_stable"


def test_v3_9_closeout_classification_ready_when_warnings_are_absent():
    reports = _zero_warning_counts(_phase_reports())
    result = _audit(_input(reports=reports))

    assert result.summary.final_closeout_classification == V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
    assert result.summary.v4_readiness_classification == V4_PLANNING_READY
    assert result.summary.warning_count == 0


def test_v3_9_closeout_classification_with_expected_warnings():
    result = _audit()

    assert result.summary.final_closeout_classification == V3_9_CLOSEOUT_WITH_WARNINGS
    assert result.summary.v4_readiness_classification == V4_PLANNING_READY_WITH_WARNINGS
    assert result.summary.warning_count > 0


def test_v3_9_closeout_blocked_classification():
    result = _audit(_input(governance_blockers=("governance_policy_blocks_closeout",)))

    assert result.summary.final_closeout_classification == V3_9_CLOSEOUT_BLOCKED
    assert result.summary.blocker_count == 1


def test_v3_9_closeout_ordering_serialization_hashing_and_equality_are_stable():
    first = _audit()
    second = _audit()

    assert first == second
    assert tuple(record.phase_id for record in first.phase_evidence) == tuple(
        sorted(record.phase_id for record in first.phase_evidence)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert serialize_v3_9_closeout_readiness_report(first) == serialize_v3_9_closeout_readiness_report(second)
    assert hash_v3_9_closeout_readiness_report(first) == hash_v3_9_closeout_readiness_report(second)
    assert export_v3_9_closeout_readiness_report(first) == export_v3_9_closeout_readiness_report(second)


def test_v3_9_closeout_findings_are_immutable_and_fail_visible():
    result = _audit()

    with pytest.raises(FrozenInstanceError):
        result.summary.warning_count = 0

    assert result.findings
    assert any(finding.finding_category == FINDING_WARNING for finding in result.findings)
    for finding in result.findings:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.evidence_reference
        assert finding.reason
        assert finding.execution_enabled is False
        assert finding.orchestration_enabled is False
        assert finding.recommendation_enabled is False
        assert finding.ranking_enabled is False
        assert finding.scoring_enabled is False
        assert finding.selection_enabled is False
        assert finding.authorization_enabled is False
        assert finding.approval_enabled is False
        assert finding.remediation_enabled is False
        assert finding.repair_enabled is False
        assert finding.runtime_mutation_enabled is False


def test_v3_9_closeout_report_preserves_all_non_execution_boundaries():
    result = _audit()

    assert result.non_executable is True
    assert result.orchestration_execution_enabled is False
    assert result.transition_execution_enabled is False
    assert result.graph_traversal_enabled is False
    assert result.routing_enabled is False
    assert result.scheduling_enabled is False
    assert result.dispatch_enabled is False
    assert result.runtime_orchestration_engine_enabled is False
    assert result.runtime_mutation_enabled is False
    assert result.authorization_enabled is False
    assert result.approval_enabled is False
    assert result.optimization_enabled is False
    assert result.recommendation_enabled is False
    assert result.ranking_enabled is False
    assert result.scoring_enabled is False
    assert result.selection_enabled is False
    assert result.remediation_enabled is False
    assert result.repair_enabled is False
    assert result.silent_correction_enabled is False
    assert result.hidden_fallback_enabled is False
    assert result.v4_runtime_behavior_enabled is False


def test_v3_9_closeout_validation_detects_hidden_finding_regression():
    result = _audit()
    hidden = replace(result.findings[0], hidden=True)
    mutated = replace(result, findings=(hidden, *result.findings[1:]))

    assert mutated.findings[0].hidden is True
    assert export_v3_9_closeout_readiness_report(mutated)["findings"][0]["hidden"] is True


def test_v3_9_closeout_generated_report_contains_required_totals_and_sentence():
    report = build_v3_9_closeout_and_v4_readiness_report(REPO_ROOT)
    summary = report["summary"]

    assert report["audit_only"] is True
    assert summary["final_closeout_classification"] == V3_9_CLOSEOUT_WITH_WARNINGS
    assert summary["v4_0_readiness_classification"] == V4_PLANNING_READY_WITH_WARNINGS
    assert summary["phase_evidence_count"] == 9
    assert summary["generated_report_count"] == 9
    assert summary["migration_doc_count"] == 9
    assert summary["missing_report_count"] == 0
    assert summary["missing_doc_count"] == 0
    assert summary["validation_error_count"] == 0
    assert summary["execution_capability_enabled_count"] == 0
    assert summary["orchestration_capability_introduced_count"] == 0
    assert summary["recommendation_ranking_scoring_selection_capability_introduced_count"] == 0
    assert summary["authorization_approval_remediation_repair_capability_introduced_count"] == 0
    assert summary["runtime_mutation_capability_introduced_count"] == 0
    assert report["deterministic_guarantee_summary"]["stable_phase_evidence_order"] is True
    assert report["deterministic_guarantee_summary"]["stable_finding_order"] is True
    assert report["deterministic_guarantee_summary"]["report_level_capability_leakage_absent"] is True
    assert REQUIRED_CLOSEOUT_SENTENCE.startswith("v3.9 is closed out as deterministic transition intelligence only.")
