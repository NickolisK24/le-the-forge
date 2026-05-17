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

from runtime_transition.transition_certification_engine import (  # noqa: E402
    certify_v3_9_transition_continuity,
    default_transition_certification_inputs,
)
from runtime_transition.transition_certification_models import (  # noqa: E402
    CERTIFICATION_CLASSIFICATION_BLOCKED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
    CERTIFICATION_CLASSIFICATION_INCOMPLETE,
    CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_PROHIBITED,
    CERTIFICATION_CLASSIFICATION_UNKNOWN,
    CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
    CERTIFICATION_FINDING_CATEGORIES,
    CERTIFICATION_GUARANTEE_CATEGORIES,
    CERTIFICATION_GUARANTEE_EXPLAINABILITY,
    CERTIFICATION_GUARANTEE_INTEGRITY,
    CERTIFICATION_GUARANTEE_NON_EXECUTION,
    CERTIFICATION_GUARANTEE_NON_MUTATION,
    CERTIFICATION_GUARANTEE_NON_RRSS,
    CERTIFICATION_GUARANTEE_PROVENANCE,
    CERTIFICATION_GUARANTEE_REPLAY,
    CERTIFICATION_GUARANTEE_ROLLBACK,
    CERTIFICATION_GUARANTEE_VISIBILITY,
    CERTIFICATION_VISIBILITY_CATEGORIES,
    TransitionCertificationInput,
)
from runtime_transition.transition_certification_reporting import (  # noqa: E402
    build_v3_9_transition_continuity_certification_report,
)
from runtime_transition.transition_certification_serialization import (  # noqa: E402
    hash_transition_certification_report,
    serialize_transition_certification_report,
    validate_transition_certification_hash_stability,
    validate_transition_certification_serialization_stability,
)
from runtime_transition.transition_certification_validation import (  # noqa: E402
    validate_transition_certification_report,
)


def _default_input(input_id: str) -> TransitionCertificationInput:
    inputs = {source.input_id: source for source in default_transition_certification_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = certify_v3_9_transition_continuity((_default_input(input_id),))
    assert report.findings
    return report.findings[0].classification


def test_v3_9_transition_certification_report_is_immutable_evidence_only_and_non_selective():
    report = certify_v3_9_transition_continuity()

    with pytest.raises(FrozenInstanceError):
        report.approval_enabled = True

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
    assert report.remediation_enabled is False
    assert report.repair_enabled is False
    assert report.automatic_remediation_enabled is False
    assert report.automatic_repair_enabled is False
    assert report.hidden_fallback_enabled is False
    assert report.silent_correction_enabled is False
    assert report.prioritization_enabled is False
    assert report.weighted_scoring_enabled is False


def test_v3_9_transition_certification_classifies_all_required_states():
    assert _single_classification("certified_transition_continuity") == CERTIFICATION_CLASSIFICATION_CERTIFIED
    assert (
        _single_classification("certified_with_warnings_transition_continuity")
        == CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS
    )
    assert _single_classification("not_certified_transition_continuity") == CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED
    assert _single_classification("blocked_transition_continuity_certification") == CERTIFICATION_CLASSIFICATION_BLOCKED
    assert (
        _single_classification("unsupported_transition_continuity_certification")
        == CERTIFICATION_CLASSIFICATION_UNSUPPORTED
    )
    assert (
        _single_classification("prohibited_transition_continuity_certification")
        == CERTIFICATION_CLASSIFICATION_PROHIBITED
    )
    assert _single_classification("unknown_transition_continuity_certification") == CERTIFICATION_CLASSIFICATION_UNKNOWN
    assert (
        _single_classification("incomplete_transition_continuity_certification")
        == CERTIFICATION_CLASSIFICATION_INCOMPLETE
    )


def test_v3_9_transition_certification_guarantee_categories_are_visible():
    report = certify_v3_9_transition_continuity()
    validation = validate_transition_certification_report(report)

    assert {guarantee.guarantee_category for guarantee in report.guarantees} == set(
        CERTIFICATION_GUARANTEE_CATEGORIES
    )
    assert validation["replay_continuity_guarantee_count"] == 8
    assert validation["rollback_continuity_guarantee_count"] == 8
    assert validation["provenance_continuity_guarantee_count"] == 8
    assert validation["explainability_continuity_guarantee_count"] == 8
    assert validation["visibility_continuity_guarantee_count"] == 8
    assert validation["integrity_continuity_guarantee_count"] == 8
    assert validation["non_execution_continuity_guarantee_count"] == 8
    assert validation["recommendation_ranking_scoring_selection_non_capability_guarantee_count"] == 8
    assert validation["mutation_non_capability_guarantee_count"] == 8
    assert CERTIFICATION_GUARANTEE_REPLAY in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_ROLLBACK in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_PROVENANCE in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_EXPLAINABILITY in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_VISIBILITY in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_INTEGRITY in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_NON_EXECUTION in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_NON_RRSS in report.summary.guarantee_category_counts
    assert CERTIFICATION_GUARANTEE_NON_MUTATION in report.summary.guarantee_category_counts


def test_v3_9_transition_certification_findings_and_guarantees_are_fail_visible():
    report = certify_v3_9_transition_continuity()

    assert report.findings
    for finding in report.findings:
        assert finding.fail_visible is True
        assert finding.hidden is False
        assert finding.descriptive_only is True
        assert finding.reason
        assert finding.evidence_reference
        assert finding.provenance_reference
        assert finding.continuity_reference
        assert finding.explainability_message
        assert finding.approval_enabled is False
        assert finding.remediation_enabled is False
        assert finding.repair_enabled is False
        assert finding.recommendation_enabled is False
        assert finding.ranking_enabled is False
        assert finding.scoring_enabled is False
        assert finding.selection_enabled is False

    assert report.guarantees
    for guarantee in report.guarantees:
        assert guarantee.visible is True
        assert guarantee.hidden is False
        assert guarantee.descriptive_only is True
        assert guarantee.reason
        assert guarantee.evidence_reference
        assert guarantee.provenance_reference
        assert guarantee.continuity_reference
        assert guarantee.explainability_message
        assert guarantee.approval_enabled is False
        assert guarantee.remediation_enabled is False
        assert guarantee.repair_enabled is False
        assert guarantee.recommendation_enabled is False
        assert guarantee.ranking_enabled is False
        assert guarantee.scoring_enabled is False
        assert guarantee.selection_enabled is False

    assert report.visibilities
    for visibility in report.visibilities:
        assert visibility.fail_visible is True
        assert visibility.hidden is False
        assert visibility.descriptive_only is True
        assert visibility.approval_enabled is False
        assert visibility.remediation_enabled is False
        assert visibility.repair_enabled is False
        assert visibility.priority_ranking_enabled is False
        assert visibility.weighted_scoring_enabled is False
        assert visibility.recommendation_enabled is False
        assert visibility.ranking_enabled is False
        assert visibility.scoring_enabled is False
        assert visibility.selection_enabled is False


def test_v3_9_transition_certification_finding_and_visibility_categories_are_visible():
    report = certify_v3_9_transition_continuity()

    assert {finding.finding_category for finding in report.findings} == set(CERTIFICATION_FINDING_CATEGORIES)
    assert {visibility.visibility_category for visibility in report.visibilities} == set(
        CERTIFICATION_VISIBILITY_CATEGORIES
    )
    assert report.summary.certification_finding_count == len(report.findings)
    assert report.summary.certification_guarantee_count == len(report.guarantees)


def test_v3_9_transition_certification_detects_hidden_and_leakage_evidence():
    report = certify_v3_9_transition_continuity()
    validation = validate_transition_certification_report(report)

    assert validation["hidden_finding_count"] >= 1
    assert validation["hidden_risk_count"] >= 1
    assert validation["hidden_non_safe_state_count"] >= 1
    assert validation["execution_boundary_leakage_count"] >= 1
    assert validation["recommendation_leakage_count"] >= 1
    assert validation["ranking_leakage_count"] >= 1
    assert validation["scoring_leakage_count"] >= 1
    assert validation["selection_leakage_count"] >= 1
    assert validation["mutation_leakage_count"] >= 1
    assert validation["report_capability_leakage_count"] == 0


def test_v3_9_transition_certification_ordering_and_equality_are_deterministic():
    inputs = default_transition_certification_inputs()
    first = certify_v3_9_transition_continuity(tuple(reversed(inputs)))
    second = certify_v3_9_transition_continuity(inputs)

    assert first == second
    assert tuple(source.input_id for source in first.certification_inputs) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(guarantee.deterministic_order for guarantee in first.guarantees) == tuple(
        sorted(guarantee.deterministic_order for guarantee in first.guarantees)
    )
    assert tuple(visibility.deterministic_order for visibility in first.visibilities) == tuple(
        sorted(visibility.deterministic_order for visibility in first.visibilities)
    )
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)
    assert len({guarantee.guarantee_id for guarantee in first.guarantees}) == len(first.guarantees)
    assert len({visibility.visibility_id for visibility in first.visibilities}) == len(first.visibilities)


def test_v3_9_transition_certification_serialization_hashing_and_equality_are_stable():
    first = certify_v3_9_transition_continuity()
    second = certify_v3_9_transition_continuity()

    assert first == second
    assert serialize_transition_certification_report(first) == serialize_transition_certification_report(second)
    assert hash_transition_certification_report(first) == hash_transition_certification_report(second)
    assert validate_transition_certification_serialization_stability(first)["stable"] is True
    assert validate_transition_certification_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_certification_report(first))["non_executable"] is True


def test_v3_9_transition_certification_continuity_and_provenance_are_preserved():
    report = certify_v3_9_transition_continuity()
    validation = validate_transition_certification_report(report)

    assert validation["replay_safe_certification_finding_count"] == validation["certification_finding_count"]
    assert validation["rollback_safe_certification_finding_count"] == validation["certification_finding_count"]
    assert validation["provenance_safe_certification_finding_count"] == validation["certification_finding_count"]
    assert validation["explainability_safe_certification_finding_count"] == validation["certification_finding_count"]
    assert validation["replay_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["visibility_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["integrity_continuity_preserved_count"] == validation["certification_continuity_count"]
    assert validation["non_execution_continuity_preserved_count"] == validation["certification_continuity_count"]


def test_v3_9_transition_certification_validation_detects_hidden_record_regressions():
    report = certify_v3_9_transition_continuity()
    hidden_finding = replace(report.findings[0], hidden=True)
    hidden_guarantee = replace(report.guarantees[0], hidden=True)
    hidden_visibility = replace(report.visibilities[0], hidden=True)
    mutated_report = replace(
        report,
        findings=(hidden_finding, *report.findings[1:]),
        guarantees=(hidden_guarantee, *report.guarantees[1:]),
        visibilities=(hidden_visibility, *report.visibilities[1:]),
    )
    validation = validate_transition_certification_report(mutated_report)

    assert validation["valid"] is False
    assert validation["hidden_finding_record_count"] == 1
    assert validation["hidden_guarantee_record_count"] == 1
    assert validation["hidden_visibility_record_count"] == 1
    assert validation["validation_error_count"] >= 3


def test_v3_9_transition_certification_generated_report_contains_required_totals_and_guarantees():
    report = build_v3_9_transition_continuity_certification_report()
    summary = report["summary"]

    assert summary["certified_count"] == 1
    assert summary["certified_with_warnings_count"] == 1
    assert summary["not_certified_count"] == 1
    assert summary["blocked_count"] == 1
    assert summary["unsupported_count"] == 1
    assert summary["prohibited_count"] == 1
    assert summary["unknown_count"] == 1
    assert summary["incomplete_count"] == 1
    assert summary["certification_finding_count"] > 0
    assert summary["certification_guarantee_count"] == 128
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["non_executable_verified"] is True
    assert summary["non_approval_verified"] is True
    assert summary["orchestration_boundaries_enforced"] is True
    assert summary["descriptive_certification_verified"] is True
    assert report["deterministic_guarantee_summary"]["finding_order_is_stable"] is True
    assert report["deterministic_guarantee_summary"]["guarantee_order_is_stable"] is True
    assert report["non_execution_guarantees"]["report_capability_leakage_count"] == 0
    assert report["certification_only_guarantees"]["no_approval_behavior"] is True
    assert report["certification_only_guarantees"]["no_remediation_behavior"] is True
    assert report["certification_only_guarantees"]["no_repair_behavior"] is True
    assert report["certification_only_guarantees"]["no_recommendation_behavior"] is True
    assert report["certification_only_guarantees"]["no_ranking_behavior"] is True
    assert report["certification_only_guarantees"]["no_scoring_behavior"] is True
    assert report["certification_only_guarantees"]["no_selection_behavior"] is True
