from __future__ import annotations

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

from runtime_transition.transition_evaluation_engine import (  # noqa: E402
    default_transition_evaluation_inputs,
    evaluate_v3_9_transition_evaluation,
)
from runtime_transition.transition_evaluation_models import (  # noqa: E402
    EVALUATION_CLASSIFICATION_BLOCKED,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_FINDING_CATEGORIES,
    EVALUATION_FINDING_COMPATIBILITY,
    EVALUATION_FINDING_CONTINUITY,
    EVALUATION_FINDING_EXPLAINABILITY,
    EVALUATION_FINDING_GOVERNANCE,
    EVALUATION_FINDING_INTEGRITY,
    EVALUATION_FINDING_MISSING_EVIDENCE,
    EVALUATION_FINDING_PROHIBITED,
    EVALUATION_FINDING_PROVENANCE,
    EVALUATION_FINDING_UNCERTAINTY,
    EVALUATION_FINDING_UNSUPPORTED,
    TransitionEvaluationInput,
)
from runtime_transition.transition_evaluation_reporting import (  # noqa: E402
    build_v3_9_transition_evaluation_intelligence_report,
)
from runtime_transition.transition_evaluation_serialization import (  # noqa: E402
    hash_transition_evaluation_report,
    serialize_transition_evaluation_report,
    validate_transition_evaluation_hash_stability,
    validate_transition_evaluation_serialization_stability,
)
from runtime_transition.transition_evaluation_validation import (  # noqa: E402
    validate_transition_evaluation_report,
)


def _default_input(input_id: str) -> TransitionEvaluationInput:
    inputs = {source.input_id: source for source in default_transition_evaluation_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = evaluate_v3_9_transition_evaluation((_default_input(input_id),))
    assert len(report.visibilities) == 1
    return report.visibilities[0].classification


def test_v3_9_transition_evaluation_report_is_immutable_and_non_executable():
    report = evaluate_v3_9_transition_evaluation()

    with pytest.raises(FrozenInstanceError):
        report.orchestration_execution_enabled = True

    assert report.non_executable is True
    assert report.transition_execution_enabled is False
    assert report.orchestration_execution_enabled is False
    assert report.orchestration_traversal_enabled is False
    assert report.runtime_orchestration_engine_enabled is False
    assert report.routing_enabled is False
    assert report.scheduling_enabled is False
    assert report.dispatch_enabled is False
    assert report.runtime_mutation_enabled is False
    assert report.approval_enabled is False
    assert report.authorization_enabled is False
    assert report.optimization_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False
    assert report.autonomous_orchestration_behavior_enabled is False
    assert report.transition_handler_enabled is False
    assert report.orchestration_evaluator_enabled is False
    assert report.runtime_state_machine_enabled is False
    assert report.callable_orchestration_flow_enabled is False
    assert report.production_execution_pathway_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False
    assert report.implicit_approval_enabled is False


def test_v3_9_transition_evaluation_classifies_successful_evaluation():
    report = evaluate_v3_9_transition_evaluation((_default_input("successful_transition_evaluation"),))
    visibility = report.visibilities[0]

    assert visibility.classification == EVALUATION_CLASSIFICATION_SUCCESSFUL
    assert visibility.visibility_status == "visible"
    assert visibility.hidden is False
    assert visibility.reason == "transition evaluation is successful for deterministic evidence reasoning only"
    assert {finding.finding_category for finding in report.findings} == {
        EVALUATION_FINDING_COMPATIBILITY,
        EVALUATION_FINDING_CONTINUITY,
        EVALUATION_FINDING_PROVENANCE,
        EVALUATION_FINDING_EXPLAINABILITY,
    }


def test_v3_9_transition_evaluation_classifies_required_non_success_states():
    assert (
        _single_classification("partially_successful_transition_evaluation")
        == EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL
    )
    assert _single_classification("unsuccessful_transition_evaluation") == EVALUATION_CLASSIFICATION_UNSUCCESSFUL
    assert _single_classification("unsupported_transition_evaluation") == EVALUATION_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_evaluation") == EVALUATION_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_evaluation") == EVALUATION_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_evaluation") == EVALUATION_CLASSIFICATION_INCOMPLETE
    assert _single_classification("blocked_transition_evaluation") == EVALUATION_CLASSIFICATION_BLOCKED


def test_v3_9_transition_evaluation_findings_are_fail_visible_and_complete():
    report = evaluate_v3_9_transition_evaluation()

    assert report.findings
    for finding in report.findings:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.reason
        assert finding.evidence_reference
        assert finding.provenance_reference
        assert finding.continuity_reference
        assert finding.explainability_message
        assert finding.non_execution_confirmation is True

    non_success = [
        visibility
        for visibility in report.visibilities
        if visibility.classification != EVALUATION_CLASSIFICATION_SUCCESSFUL
    ]
    assert len(non_success) == 7
    assert all(visibility.visibility_status == "fail_visible" for visibility in non_success)
    assert all(visibility.hidden is False for visibility in non_success)


def test_v3_9_transition_evaluation_finding_categories_are_visible():
    report = evaluate_v3_9_transition_evaluation()
    categories = {finding.finding_category for finding in report.findings}

    assert categories == set(EVALUATION_FINDING_CATEGORIES)
    assert EVALUATION_FINDING_COMPATIBILITY in categories
    assert EVALUATION_FINDING_CONTINUITY in categories
    assert EVALUATION_FINDING_PROVENANCE in categories
    assert EVALUATION_FINDING_EXPLAINABILITY in categories
    assert EVALUATION_FINDING_GOVERNANCE in categories
    assert EVALUATION_FINDING_INTEGRITY in categories
    assert EVALUATION_FINDING_UNSUPPORTED in categories
    assert EVALUATION_FINDING_PROHIBITED in categories
    assert EVALUATION_FINDING_MISSING_EVIDENCE in categories
    assert EVALUATION_FINDING_UNCERTAINTY in categories
    assert report.summary.governance_finding_count >= 1
    assert report.summary.uncertainty_finding_count >= 1
    assert report.summary.missing_evidence_finding_count >= 1
    assert report.summary.hidden_finding_count == 0


def test_v3_9_transition_evaluation_ordering_and_equality_are_deterministic():
    inputs = default_transition_evaluation_inputs()
    first = evaluate_v3_9_transition_evaluation(tuple(reversed(inputs)))
    second = evaluate_v3_9_transition_evaluation(inputs)

    assert first == second
    assert tuple(visibility.input_id for visibility in first.visibilities) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(finding.finding_id for finding in first.findings) == tuple(
        finding.finding_id for finding in second.findings
    )
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)


def test_v3_9_transition_evaluation_serialization_hashing_and_equality_are_stable():
    first = evaluate_v3_9_transition_evaluation()
    second = evaluate_v3_9_transition_evaluation()

    assert first == second
    assert serialize_transition_evaluation_report(first) == serialize_transition_evaluation_report(second)
    assert hash_transition_evaluation_report(first) == hash_transition_evaluation_report(second)
    assert validate_transition_evaluation_serialization_stability(first)["stable"] is True
    assert validate_transition_evaluation_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_evaluation_report(first))["non_executable"] is True


def test_v3_9_transition_evaluation_continuity_and_provenance_are_preserved():
    report = evaluate_v3_9_transition_evaluation()
    validation = validate_transition_evaluation_report(report)

    assert validation["replay_safe_evaluation_evidence_count"] == validation["finding_count"]
    assert validation["rollback_safe_evaluation_evidence_count"] == validation["finding_count"]
    assert validation["provenance_safe_evaluation_evidence_count"] == validation["finding_count"]
    assert validation["explainability_safe_evaluation_evidence_count"] == validation["finding_count"]
    assert validation["replay_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["continuity_record_count"]
    assert all(finding.replay_safe for finding in report.findings)
    assert all(finding.rollback_safe for finding in report.findings)
    assert all(finding.provenance_preserved for finding in report.findings)
    assert all(finding.explainability_safe for finding in report.findings)


def test_v3_9_transition_evaluation_detects_execution_boundary_violation_requests():
    report = evaluate_v3_9_transition_evaluation((_default_input("prohibited_transition_evaluation"),))
    validation = validate_transition_evaluation_report(report)

    assert report.visibilities[0].classification == EVALUATION_CLASSIFICATION_PROHIBITED
    assert validation["execution_boundary_violation_count"] == 3
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True
    assert sum(1 for finding in report.findings if finding.execution_boundary_violation_detected) == 3


def test_v3_9_transition_evaluation_validation_detects_hidden_findings():
    report = evaluate_v3_9_transition_evaluation((_default_input("unknown_transition_evaluation"),))
    hidden_finding = replace(report.findings[0], hidden=True, fail_visible=False)
    hidden_report = replace(report, findings=(hidden_finding, *report.findings[1:]))
    validation = validate_transition_evaluation_report(hidden_report)

    assert validation["valid"] is False
    assert validation["hidden_finding_count"] == 1
    assert validation["finding_not_fail_visible_count"] == 1


def test_v3_9_transition_evaluation_report_contains_required_counts_and_guarantees():
    report = build_v3_9_transition_evaluation_intelligence_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["successful_count"] == 1
    assert report["summary"]["partially_successful_count"] == 1
    assert report["summary"]["unsuccessful_count"] == 1
    assert report["summary"]["unsupported_count"] == 1
    assert report["summary"]["prohibited_count"] == 1
    assert report["summary"]["unknown_count"] == 1
    assert report["summary"]["incomplete_count"] == 1
    assert report["summary"]["blocked_count"] == 1
    assert report["summary"]["evaluation_finding_count"] >= 10
    assert report["summary"]["governance_finding_count"] >= 1
    assert report["summary"]["uncertainty_finding_count"] >= 1
    assert report["summary"]["missing_evidence_finding_count"] >= 1
    assert report["summary"]["execution_boundary_violation_count"] == 3
    assert report["summary"]["hidden_finding_count"] == 0
    assert report["summary"]["report_execution_capability_violation_count"] == 0
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["explainability_verified"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["summary"]["source_artifact_continuity_preserved"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_traversal_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
