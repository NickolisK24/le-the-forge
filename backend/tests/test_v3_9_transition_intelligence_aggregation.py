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

from runtime_transition.transition_aggregation_engine import (  # noqa: E402
    build_v3_9_transition_aggregation,
    default_transition_aggregation_inputs,
)
from runtime_transition.transition_aggregation_models import (  # noqa: E402
    AGGREGATION_CLASSIFICATION_AGGREGATED,
    AGGREGATION_CLASSIFICATION_BLOCKED,
    AGGREGATION_CLASSIFICATION_INCOMPLETE,
    AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
    AGGREGATION_CLASSIFICATION_PROHIBITED,
    AGGREGATION_CLASSIFICATION_UNKNOWN,
    AGGREGATION_CLASSIFICATION_UNAGGREGATED,
    AGGREGATION_CLASSIFICATION_UNSUPPORTED,
    AGGREGATION_FINDING_BOUNDARY,
    AGGREGATION_FINDING_CATEGORIES,
    AGGREGATION_FINDING_COMPATIBILITY,
    AGGREGATION_FINDING_CONTINUITY,
    AGGREGATION_FINDING_EVALUATION,
    AGGREGATION_FINDING_EXPLAINABILITY,
    AGGREGATION_FINDING_FOUNDATION,
    AGGREGATION_FINDING_GOVERNANCE,
    AGGREGATION_FINDING_INTEGRITY,
    AGGREGATION_FINDING_MISSING_EVIDENCE,
    AGGREGATION_FINDING_PROHIBITED,
    AGGREGATION_FINDING_PROVENANCE,
    AGGREGATION_FINDING_SCENARIO,
    AGGREGATION_FINDING_SESSION,
    AGGREGATION_FINDING_UNCERTAINTY,
    AGGREGATION_FINDING_UNSUPPORTED,
    AGGREGATION_FINDING_VISIBILITY,
    AGGREGATION_VISIBILITY_CATEGORIES,
    AGGREGATION_VISIBILITY_CONTINUITY,
    AGGREGATION_VISIBILITY_EXPLAINABILITY,
    AGGREGATION_VISIBILITY_FAIL_VISIBLE,
    AGGREGATION_VISIBILITY_GOVERNANCE,
    AGGREGATION_VISIBILITY_INTEGRITY,
    AGGREGATION_VISIBILITY_MISSING_EVIDENCE,
    AGGREGATION_VISIBILITY_PROHIBITED_STATE,
    AGGREGATION_VISIBILITY_PROVENANCE,
    AGGREGATION_VISIBILITY_SCENARIO_RISK,
    AGGREGATION_VISIBILITY_UNCERTAINTY,
    AGGREGATION_VISIBILITY_UNSUPPORTED_STATE,
    TransitionAggregationInput,
)
from runtime_transition.transition_aggregation_reporting import (  # noqa: E402
    build_v3_9_transition_intelligence_aggregation_report,
)
from runtime_transition.transition_aggregation_serialization import (  # noqa: E402
    hash_transition_aggregation_report,
    serialize_transition_aggregation_report,
    validate_transition_aggregation_hash_stability,
    validate_transition_aggregation_serialization_stability,
)
from runtime_transition.transition_aggregation_validation import (  # noqa: E402
    validate_transition_aggregation_report,
)


def _default_input(input_id: str) -> TransitionAggregationInput:
    inputs = {source.input_id: source for source in default_transition_aggregation_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = build_v3_9_transition_aggregation((_default_input(input_id),))
    assert len(report.aggregation_records) == 1
    return report.aggregation_records[0].classification


def test_v3_9_transition_aggregation_report_is_immutable_non_executable_and_non_selective():
    report = build_v3_9_transition_aggregation()

    with pytest.raises(FrozenInstanceError):
        report.orchestration_execution_enabled = True

    assert report.non_executable is True
    assert report.orchestration_execution_enabled is False
    assert report.transition_execution_enabled is False
    assert report.graph_traversal_enabled is False
    assert report.routing_enabled is False
    assert report.scheduling_enabled is False
    assert report.dispatch_enabled is False
    assert report.runtime_orchestration_engine_enabled is False
    assert report.runtime_mutation_enabled is False
    assert report.authorization_enabled is False
    assert report.approval_enabled is False
    assert report.optimization_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False
    assert report.autonomous_behavior_enabled is False
    assert report.callable_orchestration_flow_enabled is False
    assert report.transition_handler_enabled is False
    assert report.runtime_state_machine_enabled is False
    assert report.production_behavior_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False
    assert report.prioritization_enabled is False
    assert report.weighting_enabled is False


def test_v3_9_transition_aggregation_classifies_aggregated_intelligence():
    report = build_v3_9_transition_aggregation((_default_input("aggregated_transition_intelligence"),))
    record = report.aggregation_records[0]

    assert record.classification == AGGREGATION_CLASSIFICATION_AGGREGATED
    assert record.non_executable is True
    assert record.immutable_record is True
    assert record.recommendation_enabled is False
    assert record.ranking_enabled is False
    assert record.scoring_enabled is False
    assert record.selection_enabled is False
    assert report.visibilities[0].reason.endswith(
        "transition intelligence is aggregated for deterministic descriptive summaries only"
    )
    assert {finding.finding_category for finding in report.findings} == {
        AGGREGATION_FINDING_FOUNDATION,
        AGGREGATION_FINDING_BOUNDARY,
        AGGREGATION_FINDING_COMPATIBILITY,
        AGGREGATION_FINDING_EVALUATION,
        AGGREGATION_FINDING_SESSION,
        AGGREGATION_FINDING_SCENARIO,
        AGGREGATION_FINDING_VISIBILITY,
        AGGREGATION_FINDING_CONTINUITY,
        AGGREGATION_FINDING_PROVENANCE,
        AGGREGATION_FINDING_EXPLAINABILITY,
    }


def test_v3_9_transition_aggregation_classifies_required_non_aggregated_states():
    assert (
        _single_classification("partially_aggregated_transition_intelligence")
        == AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED
    )
    assert _single_classification("unaggregated_transition_intelligence") == AGGREGATION_CLASSIFICATION_UNAGGREGATED
    assert _single_classification("blocked_transition_intelligence") == AGGREGATION_CLASSIFICATION_BLOCKED
    assert _single_classification("unsupported_transition_intelligence") == AGGREGATION_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_intelligence") == AGGREGATION_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_intelligence") == AGGREGATION_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_intelligence") == AGGREGATION_CLASSIFICATION_INCOMPLETE


def test_v3_9_transition_aggregation_findings_and_visibility_are_fail_visible():
    report = build_v3_9_transition_aggregation()

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
        assert finding.no_recommendation_confirmation is True

    assert report.visibilities
    for visibility in report.visibilities:
        assert visibility.fail_visible is True
        assert visibility.hidden is False
        assert visibility.reason
        assert visibility.evidence_reference
        assert visibility.provenance_reference
        assert visibility.continuity_reference
        assert visibility.explainability_message
        assert visibility.descriptive_only is True
        assert visibility.prioritization_enabled is False
        assert visibility.weighting_enabled is False
        assert visibility.recommendation_enabled is False
        assert visibility.ranking_enabled is False
        assert visibility.scoring_enabled is False
        assert visibility.selection_enabled is False

    non_aggregated = [
        visibility
        for visibility in report.visibilities
        if visibility.classification != AGGREGATION_CLASSIFICATION_AGGREGATED
    ]
    assert non_aggregated
    assert all(visibility.fail_visible is True for visibility in non_aggregated)
    assert all(visibility.hidden is False for visibility in non_aggregated)


def test_v3_9_transition_aggregation_finding_and_visibility_categories_are_visible():
    report = build_v3_9_transition_aggregation()
    finding_categories = {finding.finding_category for finding in report.findings}
    visibility_categories = {visibility.visibility_category for visibility in report.visibilities}

    assert finding_categories == set(AGGREGATION_FINDING_CATEGORIES)
    assert AGGREGATION_FINDING_FOUNDATION in finding_categories
    assert AGGREGATION_FINDING_BOUNDARY in finding_categories
    assert AGGREGATION_FINDING_COMPATIBILITY in finding_categories
    assert AGGREGATION_FINDING_EVALUATION in finding_categories
    assert AGGREGATION_FINDING_SESSION in finding_categories
    assert AGGREGATION_FINDING_SCENARIO in finding_categories
    assert AGGREGATION_FINDING_VISIBILITY in finding_categories
    assert AGGREGATION_FINDING_CONTINUITY in finding_categories
    assert AGGREGATION_FINDING_PROVENANCE in finding_categories
    assert AGGREGATION_FINDING_EXPLAINABILITY in finding_categories
    assert AGGREGATION_FINDING_GOVERNANCE in finding_categories
    assert AGGREGATION_FINDING_INTEGRITY in finding_categories
    assert AGGREGATION_FINDING_UNSUPPORTED in finding_categories
    assert AGGREGATION_FINDING_PROHIBITED in finding_categories
    assert AGGREGATION_FINDING_MISSING_EVIDENCE in finding_categories
    assert AGGREGATION_FINDING_UNCERTAINTY in finding_categories

    assert visibility_categories == set(AGGREGATION_VISIBILITY_CATEGORIES)
    assert AGGREGATION_VISIBILITY_FAIL_VISIBLE in visibility_categories
    assert AGGREGATION_VISIBILITY_UNSUPPORTED_STATE in visibility_categories
    assert AGGREGATION_VISIBILITY_PROHIBITED_STATE in visibility_categories
    assert AGGREGATION_VISIBILITY_UNCERTAINTY in visibility_categories
    assert AGGREGATION_VISIBILITY_CONTINUITY in visibility_categories
    assert AGGREGATION_VISIBILITY_PROVENANCE in visibility_categories
    assert AGGREGATION_VISIBILITY_EXPLAINABILITY in visibility_categories
    assert AGGREGATION_VISIBILITY_INTEGRITY in visibility_categories
    assert AGGREGATION_VISIBILITY_GOVERNANCE in visibility_categories
    assert AGGREGATION_VISIBILITY_SCENARIO_RISK in visibility_categories
    assert AGGREGATION_VISIBILITY_MISSING_EVIDENCE in visibility_categories
    assert report.summary.hidden_aggregation_finding_count == 0
    assert report.summary.hidden_visibility_count == 0


def test_v3_9_transition_aggregation_ordering_and_equality_are_deterministic():
    inputs = default_transition_aggregation_inputs()
    first = build_v3_9_transition_aggregation(tuple(reversed(inputs)))
    second = build_v3_9_transition_aggregation(inputs)

    assert first == second
    assert tuple(record.input_id for record in first.aggregation_records) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(record.deterministic_order for record in first.aggregation_records) == tuple(
        sorted(record.deterministic_order for record in first.aggregation_records)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(visibility.deterministic_order for visibility in first.visibilities) == tuple(
        sorted(visibility.deterministic_order for visibility in first.visibilities)
    )
    assert tuple(risk_visibility.deterministic_order for risk_visibility in first.risk_visibility_records) == tuple(
        sorted(risk_visibility.deterministic_order for risk_visibility in first.risk_visibility_records)
    )
    assert len({record.record_id for record in first.aggregation_records}) == len(first.aggregation_records)
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)
    assert len({visibility.visibility_id for visibility in first.visibilities}) == len(first.visibilities)
    assert len({risk.risk_visibility_id for risk in first.risk_visibility_records}) == len(first.risk_visibility_records)


def test_v3_9_transition_aggregation_serialization_hashing_and_equality_are_stable():
    first = build_v3_9_transition_aggregation()
    second = build_v3_9_transition_aggregation()

    assert first == second
    assert serialize_transition_aggregation_report(first) == serialize_transition_aggregation_report(second)
    assert hash_transition_aggregation_report(first) == hash_transition_aggregation_report(second)
    assert validate_transition_aggregation_serialization_stability(first)["stable"] is True
    assert validate_transition_aggregation_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_aggregation_report(first))["non_executable"] is True


def test_v3_9_transition_aggregation_continuity_and_provenance_are_preserved():
    report = build_v3_9_transition_aggregation()
    validation = validate_transition_aggregation_report(report)

    assert validation["replay_safe_aggregation_finding_count"] == validation["aggregation_finding_count"]
    assert validation["rollback_safe_aggregation_finding_count"] == validation["aggregation_finding_count"]
    assert validation["provenance_safe_aggregation_finding_count"] == validation["aggregation_finding_count"]
    assert validation["explainability_safe_aggregation_finding_count"] == validation["aggregation_finding_count"]
    assert validation["replay_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["provenance_integrity_violation_count"] == 0
    assert validation["continuity_integrity_violation_count"] == 0


def test_v3_9_transition_aggregation_visibility_is_descriptive_only():
    report = build_v3_9_transition_aggregation()
    validation = validate_transition_aggregation_report(report)

    assert all(visibility.descriptive_only is True for visibility in report.visibilities)
    assert all(risk.descriptive_only is True for risk in report.risk_visibility_records)
    assert all(risk.recommendation_enabled is False for risk in report.risk_visibility_records)
    assert all(risk.ranking_enabled is False for risk in report.risk_visibility_records)
    assert all(risk.scoring_enabled is False for risk in report.risk_visibility_records)
    assert all(risk.selection_enabled is False for risk in report.risk_visibility_records)
    assert validation["risk_visibility_selection_violation_count"] == 0
    assert validation["record_selection_violation_count"] == 0
    assert validation["non_selective_confirmation"] is True


def test_v3_9_transition_aggregation_detects_prohibited_boundaries_without_enabling_them():
    report = build_v3_9_transition_aggregation()
    validation = validate_transition_aggregation_report(report)
    prohibited_findings = [
        finding for finding in report.findings if finding.classification == AGGREGATION_CLASSIFICATION_PROHIBITED
    ]

    assert prohibited_findings
    assert validation["execution_boundary_violation_count"] == 7
    assert validation["recommendation_ranking_scoring_selection_violation_count"] == 4
    assert report.summary.execution_boundary_violation_count == 7
    assert report.summary.recommendation_ranking_scoring_selection_violation_count == 4
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True
    assert report.orchestration_execution_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False


def test_v3_9_transition_aggregation_validation_detects_hidden_state_regressions():
    report = build_v3_9_transition_aggregation()
    hidden_finding = replace(report.findings[0], hidden=True)
    hidden_visibility = replace(report.visibilities[0], hidden=True)
    mutated_report = replace(
        report,
        findings=(hidden_finding, *report.findings[1:]),
        visibilities=(hidden_visibility, *report.visibilities[1:]),
    )
    validation = validate_transition_aggregation_report(mutated_report)

    assert validation["valid"] is False
    assert validation["hidden_aggregation_finding_count"] == 1
    assert validation["hidden_visibility_count"] == 1
    assert validation["validation_error_count"] >= 2


def test_v3_9_transition_aggregation_generated_report_contains_required_totals_and_guarantees():
    report = build_v3_9_transition_intelligence_aggregation_report()
    summary = report["summary"]

    assert summary["aggregated_count"] == 1
    assert summary["partially_aggregated_count"] == 1
    assert summary["unaggregated_count"] == 1
    assert summary["blocked_count"] == 1
    assert summary["unsupported_count"] == 1
    assert summary["prohibited_count"] == 1
    assert summary["unknown_count"] == 1
    assert summary["incomplete_count"] == 1
    assert summary["hidden_aggregation_finding_count"] == 0
    assert summary["hidden_visibility_count"] == 0
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["non_executable_verified"] is True
    assert summary["orchestration_boundaries_enforced"] is True
    assert summary["descriptive_aggregation_verified"] is True
    assert report["aggregation_totals"]["aggregation_finding_count"] == summary["aggregation_finding_count"]
    assert report["aggregation_totals"]["aggregation_visibility_count"] == summary["aggregation_visibility_count"]
    assert report["deterministic_guarantee_summary"]["finding_order_is_stable"] is True
    assert report["deterministic_guarantee_summary"]["visibility_order_is_stable"] is True
    assert report["non_execution_guarantees"]["report_execution_capability_violation_count"] == 0
    assert report["descriptive_aggregation_guarantees"]["no_recommendation_behavior"] is True
    assert report["descriptive_aggregation_guarantees"]["no_ranking_behavior"] is True
    assert report["descriptive_aggregation_guarantees"]["no_scoring_behavior"] is True
    assert report["descriptive_aggregation_guarantees"]["no_selection_behavior"] is True
