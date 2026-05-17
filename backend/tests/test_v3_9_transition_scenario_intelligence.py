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

from runtime_transition.transition_scenario_engine import (  # noqa: E402
    build_v3_9_transition_scenario,
    default_transition_scenario_inputs,
)
from runtime_transition.transition_scenario_models import (  # noqa: E402
    SCENARIO_CLASSIFICATION_BLOCKED,
    SCENARIO_CLASSIFICATION_INCOMPLETE,
    SCENARIO_CLASSIFICATION_MODELED,
    SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
    SCENARIO_CLASSIFICATION_PROHIBITED,
    SCENARIO_CLASSIFICATION_UNKNOWN,
    SCENARIO_CLASSIFICATION_UNMODELED,
    SCENARIO_CLASSIFICATION_UNSUPPORTED,
    SCENARIO_FINDING_CATEGORIES,
    SCENARIO_FINDING_COMPARISON,
    SCENARIO_FINDING_CONTINUITY,
    SCENARIO_FINDING_EXPLAINABILITY,
    SCENARIO_FINDING_GOVERNANCE,
    SCENARIO_FINDING_INTEGRITY,
    SCENARIO_FINDING_MISSING_EVIDENCE,
    SCENARIO_FINDING_PROHIBITED,
    SCENARIO_FINDING_PROVENANCE,
    SCENARIO_FINDING_RISK_VISIBILITY,
    SCENARIO_FINDING_SESSION_EVIDENCE,
    SCENARIO_FINDING_UNCERTAINTY,
    SCENARIO_FINDING_UNSUPPORTED,
    SCENARIO_FINDING_VARIANT,
    SCENARIO_RISK_CATEGORIES,
    SCENARIO_RISK_CONTINUITY,
    SCENARIO_RISK_EXPLAINABILITY,
    SCENARIO_RISK_GOVERNANCE,
    SCENARIO_RISK_INTEGRITY,
    SCENARIO_RISK_MISSING_EVIDENCE,
    SCENARIO_RISK_PROHIBITED_CAPABILITY,
    SCENARIO_RISK_PROVENANCE,
    SCENARIO_RISK_UNCERTAINTY,
    SCENARIO_RISK_UNSUPPORTED_DOMAIN,
    TransitionScenarioInput,
)
from runtime_transition.transition_scenario_reporting import (  # noqa: E402
    build_v3_9_transition_scenario_intelligence_report,
)
from runtime_transition.transition_scenario_serialization import (  # noqa: E402
    hash_transition_scenario_report,
    serialize_transition_scenario_report,
    validate_transition_scenario_hash_stability,
    validate_transition_scenario_serialization_stability,
)
from runtime_transition.transition_scenario_validation import (  # noqa: E402
    validate_transition_scenario_report,
)


def _default_input(input_id: str) -> TransitionScenarioInput:
    inputs = {source.input_id: source for source in default_transition_scenario_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = build_v3_9_transition_scenario((_default_input(input_id),))
    assert len(report.visibilities) == 1
    return report.visibilities[0].classification


def test_v3_9_transition_scenario_report_is_immutable_non_executable_and_non_selective():
    report = build_v3_9_transition_scenario()

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


def test_v3_9_transition_scenario_classifies_modeled_scenario():
    report = build_v3_9_transition_scenario((_default_input("modeled_transition_scenario"),))
    visibility = report.visibilities[0]

    assert visibility.classification == SCENARIO_CLASSIFICATION_MODELED
    assert visibility.visibility_status == "visible"
    assert visibility.hidden is False
    assert visibility.reason == "transition scenario is modeled for deterministic evidence reasoning only"
    assert {finding.finding_category for finding in report.findings} == {
        SCENARIO_FINDING_SESSION_EVIDENCE,
        SCENARIO_FINDING_VARIANT,
        SCENARIO_FINDING_COMPARISON,
        SCENARIO_FINDING_RISK_VISIBILITY,
        SCENARIO_FINDING_CONTINUITY,
        SCENARIO_FINDING_PROVENANCE,
        SCENARIO_FINDING_EXPLAINABILITY,
    }


def test_v3_9_transition_scenario_classifies_required_non_modeled_states():
    assert (
        _single_classification("partially_modeled_transition_scenario")
        == SCENARIO_CLASSIFICATION_PARTIALLY_MODELED
    )
    assert _single_classification("unmodeled_transition_scenario") == SCENARIO_CLASSIFICATION_UNMODELED
    assert _single_classification("blocked_transition_scenario") == SCENARIO_CLASSIFICATION_BLOCKED
    assert _single_classification("unsupported_transition_scenario") == SCENARIO_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_scenario") == SCENARIO_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_scenario") == SCENARIO_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_scenario") == SCENARIO_CLASSIFICATION_INCOMPLETE


def test_v3_9_transition_scenario_findings_and_risks_are_fail_visible():
    report = build_v3_9_transition_scenario()

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

    assert report.risks
    for risk in report.risks:
        assert risk.fail_visible is True
        assert risk.hidden is False
        assert risk.description
        assert risk.descriptive_only is True
        assert risk.score_assigned is False
        assert risk.ranking_assigned is False
        assert risk.recommendation_made is False
        assert risk.selection_made is False

    non_modeled = [
        visibility
        for visibility in report.visibilities
        if visibility.classification != SCENARIO_CLASSIFICATION_MODELED
    ]
    assert len(non_modeled) == 7
    assert all(visibility.visibility_status == "fail_visible" for visibility in non_modeled)
    assert all(visibility.hidden is False for visibility in non_modeled)
    assert all(visibility.scenario_state_visible is True for visibility in non_modeled)


def test_v3_9_transition_scenario_finding_and_risk_categories_are_visible():
    report = build_v3_9_transition_scenario()
    finding_categories = {finding.finding_category for finding in report.findings}
    risk_categories = {risk.risk_category for risk in report.risks}

    assert finding_categories == set(SCENARIO_FINDING_CATEGORIES)
    assert SCENARIO_FINDING_SESSION_EVIDENCE in finding_categories
    assert SCENARIO_FINDING_VARIANT in finding_categories
    assert SCENARIO_FINDING_COMPARISON in finding_categories
    assert SCENARIO_FINDING_RISK_VISIBILITY in finding_categories
    assert SCENARIO_FINDING_CONTINUITY in finding_categories
    assert SCENARIO_FINDING_PROVENANCE in finding_categories
    assert SCENARIO_FINDING_EXPLAINABILITY in finding_categories
    assert SCENARIO_FINDING_GOVERNANCE in finding_categories
    assert SCENARIO_FINDING_INTEGRITY in finding_categories
    assert SCENARIO_FINDING_UNSUPPORTED in finding_categories
    assert SCENARIO_FINDING_PROHIBITED in finding_categories
    assert SCENARIO_FINDING_MISSING_EVIDENCE in finding_categories
    assert SCENARIO_FINDING_UNCERTAINTY in finding_categories

    assert risk_categories == set(SCENARIO_RISK_CATEGORIES)
    assert SCENARIO_RISK_PROVENANCE in risk_categories
    assert SCENARIO_RISK_CONTINUITY in risk_categories
    assert SCENARIO_RISK_EXPLAINABILITY in risk_categories
    assert SCENARIO_RISK_UNSUPPORTED_DOMAIN in risk_categories
    assert SCENARIO_RISK_PROHIBITED_CAPABILITY in risk_categories
    assert SCENARIO_RISK_MISSING_EVIDENCE in risk_categories
    assert SCENARIO_RISK_UNCERTAINTY in risk_categories
    assert SCENARIO_RISK_GOVERNANCE in risk_categories
    assert SCENARIO_RISK_INTEGRITY in risk_categories
    assert report.summary.hidden_scenario_finding_count == 0
    assert report.summary.hidden_risk_count == 0


def test_v3_9_transition_scenario_ordering_and_equality_are_deterministic():
    inputs = default_transition_scenario_inputs()
    first = build_v3_9_transition_scenario(tuple(reversed(inputs)))
    second = build_v3_9_transition_scenario(inputs)

    assert first == second
    assert tuple(visibility.input_id for visibility in first.visibilities) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(variant.deterministic_order for variant in first.variants) == tuple(
        sorted(variant.deterministic_order for variant in first.variants)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(risk.deterministic_order for risk in first.risks) == tuple(
        sorted(risk.deterministic_order for risk in first.risks)
    )
    assert tuple(comparison.deterministic_order for comparison in first.comparisons) == tuple(
        sorted(comparison.deterministic_order for comparison in first.comparisons)
    )
    assert len({variant.variant_id for variant in first.variants}) == len(first.variants)
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)
    assert len({risk.risk_id for risk in first.risks}) == len(first.risks)
    assert len({comparison.comparison_id for comparison in first.comparisons}) == len(first.comparisons)


def test_v3_9_transition_scenario_serialization_hashing_and_equality_are_stable():
    first = build_v3_9_transition_scenario()
    second = build_v3_9_transition_scenario()

    assert first == second
    assert serialize_transition_scenario_report(first) == serialize_transition_scenario_report(second)
    assert hash_transition_scenario_report(first) == hash_transition_scenario_report(second)
    assert validate_transition_scenario_serialization_stability(first)["stable"] is True
    assert validate_transition_scenario_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_scenario_report(first))["non_executable"] is True


def test_v3_9_transition_scenario_continuity_and_provenance_are_preserved():
    report = build_v3_9_transition_scenario()
    validation = validate_transition_scenario_report(report)

    assert validation["replay_safe_scenario_finding_count"] == validation["scenario_finding_count"]
    assert validation["rollback_safe_scenario_finding_count"] == validation["scenario_finding_count"]
    assert validation["provenance_safe_scenario_finding_count"] == validation["scenario_finding_count"]
    assert validation["explainability_safe_scenario_finding_count"] == validation["scenario_finding_count"]
    assert validation["replay_safe_risk_count"] == validation["scenario_risk_count"]
    assert validation["rollback_safe_risk_count"] == validation["scenario_risk_count"]
    assert validation["provenance_safe_risk_count"] == validation["scenario_risk_count"]
    assert validation["explainability_safe_risk_count"] == validation["scenario_risk_count"]
    assert validation["replay_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["continuity_record_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["continuity_record_count"]


def test_v3_9_transition_scenario_comparisons_are_non_selective():
    report = build_v3_9_transition_scenario()
    validation = validate_transition_scenario_report(report)

    assert report.comparisons
    for comparison in report.comparisons:
        assert comparison.descriptive_only is True
        assert comparison.winner_selected is False
        assert comparison.recommendation_made is False
        assert comparison.ranking_assigned is False
        assert comparison.scoring_assigned is False
        assert comparison.selection_made is False

    assert validation["comparison_selection_violation_count"] == 0
    assert validation["record_selection_violation_count"] == 0
    assert validation["non_selective_confirmation"] is True


def test_v3_9_transition_scenario_detects_execution_and_choice_boundary_requests():
    report = build_v3_9_transition_scenario((_default_input("prohibited_transition_scenario"),))
    validation = validate_transition_scenario_report(report)

    assert report.visibilities[0].classification == SCENARIO_CLASSIFICATION_PROHIBITED
    assert validation["execution_boundary_violation_count"] == 7
    assert validation["recommendation_ranking_scoring_selection_violation_count"] == 4
    assert validation["report_execution_capability_violation_count"] == 0
    assert validation["non_execution_confirmation"] is True
    assert validation["non_selective_confirmation"] is True
    assert sum(1 for finding in report.findings if finding.execution_boundary_violation_detected) == 7
    assert sum(1 for finding in report.findings if finding.recommendation_boundary_violation_detected) == 4


def test_v3_9_transition_scenario_validation_detects_hidden_findings_and_risks():
    report = build_v3_9_transition_scenario((_default_input("unknown_transition_scenario"),))
    hidden_finding = replace(report.findings[0], hidden=True, fail_visible=False)
    hidden_risk = replace(report.risks[0], hidden=True, fail_visible=False)
    hidden_report = replace(
        report,
        findings=(hidden_finding, *report.findings[1:]),
        risks=(hidden_risk, *report.risks[1:]),
    )
    validation = validate_transition_scenario_report(hidden_report)

    assert validation["valid"] is False
    assert validation["hidden_scenario_finding_count"] == 1
    assert validation["hidden_risk_count"] == 1
    assert validation["finding_not_fail_visible_count"] == 1
    assert validation["risk_not_fail_visible_count"] == 1


def test_v3_9_transition_scenario_report_contains_required_counts_and_guarantees():
    report = build_v3_9_transition_scenario_intelligence_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["modeled_count"] == 1
    assert report["summary"]["partially_modeled_count"] == 1
    assert report["summary"]["unmodeled_count"] == 1
    assert report["summary"]["blocked_count"] == 1
    assert report["summary"]["unsupported_count"] == 1
    assert report["summary"]["prohibited_count"] == 1
    assert report["summary"]["unknown_count"] == 1
    assert report["summary"]["incomplete_count"] == 1
    assert report["summary"]["scenario_finding_count"] >= 13
    assert report["summary"]["scenario_variant_count"] >= 8
    assert report["summary"]["scenario_comparison_count"] >= 2
    assert report["summary"]["scenario_risk_count"] >= 9
    assert report["summary"]["governance_risk_count"] >= 1
    assert report["summary"]["uncertainty_risk_count"] >= 1
    assert report["summary"]["missing_evidence_risk_count"] >= 1
    assert report["summary"]["hidden_scenario_finding_count"] == 0
    assert report["summary"]["hidden_risk_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 7
    assert report["summary"]["recommendation_ranking_scoring_selection_violation_count"] == 4
    assert report["summary"]["report_execution_capability_violation_count"] == 0
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["explainability_verified"] is True
    assert report["summary"]["risk_visibility_verified"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["summary"]["non_selective_comparison_verified"] is True
    assert report["summary"]["source_artifact_continuity_preserved"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["graph_traversal_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
    assert report["non_execution_guarantees"]["recommendation_absent"] is True
    assert report["non_execution_guarantees"]["ranking_absent"] is True
    assert report["non_execution_guarantees"]["scoring_absent"] is True
    assert report["non_execution_guarantees"]["selection_absent"] is True
    assert report["non_selective_comparison_guarantees"]["no_recommendation_behavior"] is True
    assert report["non_selective_comparison_guarantees"]["no_ranking_behavior"] is True
    assert report["non_selective_comparison_guarantees"]["no_scoring_behavior"] is True
    assert report["non_selective_comparison_guarantees"]["no_selection_behavior"] is True
