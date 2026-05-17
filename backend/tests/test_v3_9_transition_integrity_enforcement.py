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

from runtime_transition.transition_integrity_audit import (  # noqa: E402
    audit_v3_9_transition_integrity,
    default_transition_integrity_inputs,
)
from runtime_transition.transition_integrity_models import (  # noqa: E402
    INTEGRITY_CLASSIFICATION_BLOCKED,
    INTEGRITY_CLASSIFICATION_FAILED,
    INTEGRITY_CLASSIFICATION_INCOMPLETE,
    INTEGRITY_CLASSIFICATION_PROHIBITED,
    INTEGRITY_CLASSIFICATION_SATISFIED,
    INTEGRITY_CLASSIFICATION_UNKNOWN,
    INTEGRITY_CLASSIFICATION_UNSUPPORTED,
    INTEGRITY_CLASSIFICATION_WARNING,
    INTEGRITY_FINDING_CATEGORIES,
    INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP,
    INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK,
    INTEGRITY_VIOLATION_EXPLAINABILITY_GAP,
    INTEGRITY_VIOLATION_HIDDEN_FINDING,
    INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE,
    INTEGRITY_VIOLATION_HIDDEN_RISK,
    INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP,
    INTEGRITY_VIOLATION_MUTATION_LEAK,
    INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_PROVENANCE_GAP,
    INTEGRITY_VIOLATION_RANKING_LEAK,
    INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,
    INTEGRITY_VIOLATION_REPLAY_GAP,
    INTEGRITY_VIOLATION_ROLLBACK_GAP,
    INTEGRITY_VIOLATION_SCORING_LEAK,
    INTEGRITY_VIOLATION_SELECTION_LEAK,
    INTEGRITY_VIOLATION_TYPES,
    INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP,
    INTEGRITY_VISIBILITY_CATEGORIES,
    TransitionIntegrityInput,
)
from runtime_transition.transition_integrity_reporting import (  # noqa: E402
    build_v3_9_transition_integrity_enforcement_report,
)
from runtime_transition.transition_integrity_serialization import (  # noqa: E402
    hash_transition_integrity_report,
    serialize_transition_integrity_report,
    validate_transition_integrity_hash_stability,
    validate_transition_integrity_serialization_stability,
)
from runtime_transition.transition_integrity_validation import (  # noqa: E402
    validate_transition_integrity_report,
)


def _default_input(input_id: str) -> TransitionIntegrityInput:
    inputs = {source.input_id: source for source in default_transition_integrity_inputs()}
    return inputs[input_id]


def _single_classification(input_id: str) -> str:
    report = audit_v3_9_transition_integrity((_default_input(input_id),))
    assert report.findings
    return report.findings[0].classification


def test_v3_9_transition_integrity_report_is_immutable_audit_only_and_non_selective():
    report = audit_v3_9_transition_integrity()

    with pytest.raises(FrozenInstanceError):
        report.remediation_enabled = True

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
    assert report.weighted_severity_scoring_enabled is False


def test_v3_9_transition_integrity_classifies_all_required_states():
    assert _single_classification("integrity_satisfied_transition_chain") == INTEGRITY_CLASSIFICATION_SATISFIED
    assert _single_classification("integrity_warning_transition_chain") == INTEGRITY_CLASSIFICATION_WARNING
    assert _single_classification("integrity_failed_transition_chain") == INTEGRITY_CLASSIFICATION_FAILED
    assert _single_classification("blocked_transition_integrity_audit") == INTEGRITY_CLASSIFICATION_BLOCKED
    assert _single_classification("unsupported_transition_integrity_audit") == INTEGRITY_CLASSIFICATION_UNSUPPORTED
    assert _single_classification("prohibited_transition_integrity_audit") == INTEGRITY_CLASSIFICATION_PROHIBITED
    assert _single_classification("unknown_transition_integrity_audit") == INTEGRITY_CLASSIFICATION_UNKNOWN
    assert _single_classification("incomplete_transition_integrity_audit") == INTEGRITY_CLASSIFICATION_INCOMPLETE


def test_v3_9_transition_integrity_detects_all_required_violation_categories():
    report = audit_v3_9_transition_integrity()
    validation = validate_transition_integrity_report(report)
    violation_types = {violation.violation_type for violation in report.violations}

    assert violation_types == set(INTEGRITY_VIOLATION_TYPES)
    assert validation["hidden_finding_violation_count"] >= 1
    assert validation["hidden_risk_violation_count"] >= 1
    assert validation["hidden_non_safe_state_violation_count"] >= 1
    assert validation["missing_evidence_violation_count"] >= 1
    assert validation["provenance_gap_count"] >= 1
    assert validation["replay_gap_count"] >= 1
    assert validation["rollback_gap_count"] >= 1
    assert validation["explainability_gap_count"] >= 1
    assert validation["aggregation_integrity_gap_count"] >= 1
    assert validation["execution_boundary_leakage_count"] >= 1
    assert validation["recommendation_leakage_count"] >= 1
    assert validation["ranking_leakage_count"] >= 1
    assert validation["scoring_leakage_count"] >= 1
    assert validation["selection_leakage_count"] >= 1
    assert validation["mutation_leakage_count"] >= 1
    assert validation["visibility_gap_count"] >= 1
    assert INTEGRITY_VIOLATION_HIDDEN_FINDING in violation_types
    assert INTEGRITY_VIOLATION_HIDDEN_RISK in violation_types
    assert INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE in violation_types
    assert INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP in violation_types
    assert INTEGRITY_VIOLATION_PROVENANCE_GAP in violation_types
    assert INTEGRITY_VIOLATION_REPLAY_GAP in violation_types
    assert INTEGRITY_VIOLATION_ROLLBACK_GAP in violation_types
    assert INTEGRITY_VIOLATION_EXPLAINABILITY_GAP in violation_types
    assert INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP in violation_types
    assert INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK in violation_types
    assert INTEGRITY_VIOLATION_RECOMMENDATION_LEAK in violation_types
    assert INTEGRITY_VIOLATION_RANKING_LEAK in violation_types
    assert INTEGRITY_VIOLATION_SCORING_LEAK in violation_types
    assert INTEGRITY_VIOLATION_SELECTION_LEAK in violation_types
    assert INTEGRITY_VIOLATION_MUTATION_LEAK in violation_types
    assert INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP in violation_types
    assert INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP in violation_types
    assert INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP in violation_types


def test_v3_9_transition_integrity_findings_violations_and_visibility_are_fail_visible():
    report = audit_v3_9_transition_integrity()

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
        assert finding.remediation_enabled is False
        assert finding.repair_enabled is False
        assert finding.recommendation_enabled is False
        assert finding.ranking_enabled is False
        assert finding.scoring_enabled is False
        assert finding.selection_enabled is False

    assert report.violations
    for violation in report.violations:
        assert violation.fail_visible is True
        assert violation.hidden is False
        assert violation.descriptive_only is True
        assert violation.reason
        assert violation.evidence_reference
        assert violation.provenance_reference
        assert violation.continuity_reference
        assert violation.explainability_message
        assert violation.remediation_enabled is False
        assert violation.repair_enabled is False
        assert violation.severity_score is None
        assert violation.priority_rank is None

    assert report.visibilities
    for visibility in report.visibilities:
        assert visibility.fail_visible is True
        assert visibility.hidden is False
        assert visibility.descriptive_only is True
        assert visibility.remediation_enabled is False
        assert visibility.repair_enabled is False
        assert visibility.priority_ranking_enabled is False
        assert visibility.weighted_severity_enabled is False
        assert visibility.recommendation_enabled is False
        assert visibility.ranking_enabled is False
        assert visibility.scoring_enabled is False
        assert visibility.selection_enabled is False


def test_v3_9_transition_integrity_finding_and_visibility_categories_are_visible():
    report = audit_v3_9_transition_integrity()

    assert {finding.finding_category for finding in report.findings} == set(INTEGRITY_FINDING_CATEGORIES)
    assert {violation.violation_type for violation in report.violations} == set(INTEGRITY_VIOLATION_TYPES)
    assert {visibility.visibility_category for visibility in report.visibilities} == set(
        INTEGRITY_VISIBILITY_CATEGORIES
    )
    assert report.summary.integrity_violation_count == len(report.violations)
    assert report.summary.hidden_finding_violation_count >= 1
    assert report.summary.hidden_risk_violation_count >= 1
    assert report.summary.hidden_non_safe_state_violation_count >= 1


def test_v3_9_transition_integrity_ordering_and_equality_are_deterministic():
    inputs = default_transition_integrity_inputs()
    first = audit_v3_9_transition_integrity(tuple(reversed(inputs)))
    second = audit_v3_9_transition_integrity(inputs)

    assert first == second
    assert tuple(source.input_id for source in first.integrity_inputs) == tuple(
        sorted(source.input_id for source in inputs)
    )
    assert tuple(finding.deterministic_order for finding in first.findings) == tuple(
        sorted(finding.deterministic_order for finding in first.findings)
    )
    assert tuple(violation.deterministic_order for violation in first.violations) == tuple(
        sorted(violation.deterministic_order for violation in first.violations)
    )
    assert tuple(visibility.deterministic_order for visibility in first.visibilities) == tuple(
        sorted(visibility.deterministic_order for visibility in first.visibilities)
    )
    assert len({finding.finding_id for finding in first.findings}) == len(first.findings)
    assert len({violation.violation_id for violation in first.violations}) == len(first.violations)
    assert len({visibility.visibility_id for visibility in first.visibilities}) == len(first.visibilities)


def test_v3_9_transition_integrity_serialization_hashing_and_equality_are_stable():
    first = audit_v3_9_transition_integrity()
    second = audit_v3_9_transition_integrity()

    assert first == second
    assert serialize_transition_integrity_report(first) == serialize_transition_integrity_report(second)
    assert hash_transition_integrity_report(first) == hash_transition_integrity_report(second)
    assert validate_transition_integrity_serialization_stability(first)["stable"] is True
    assert validate_transition_integrity_hash_stability(first)["stable"] is True
    assert json.loads(serialize_transition_integrity_report(first))["non_executable"] is True


def test_v3_9_transition_integrity_continuity_and_provenance_are_preserved():
    report = audit_v3_9_transition_integrity()
    validation = validate_transition_integrity_report(report)

    assert validation["replay_safe_integrity_finding_count"] == validation["integrity_finding_count"]
    assert validation["rollback_safe_integrity_finding_count"] == validation["integrity_finding_count"]
    assert validation["provenance_safe_integrity_finding_count"] == validation["integrity_finding_count"]
    assert validation["explainability_safe_integrity_finding_count"] == validation["integrity_finding_count"]
    assert validation["replay_continuity_preserved_count"] == validation["integrity_continuity_count"]
    assert validation["rollback_continuity_preserved_count"] == validation["integrity_continuity_count"]
    assert validation["provenance_continuity_preserved_count"] == validation["integrity_continuity_count"]
    assert validation["explainability_continuity_preserved_count"] == validation["integrity_continuity_count"]
    assert validation["continuity_integrity_violation_count"] == 0


def test_v3_9_transition_integrity_validation_detects_hidden_record_regressions():
    report = audit_v3_9_transition_integrity()
    hidden_finding = replace(report.findings[0], hidden=True)
    hidden_violation = replace(report.violations[0], hidden=True)
    hidden_visibility = replace(report.visibilities[0], hidden=True)
    mutated_report = replace(
        report,
        findings=(hidden_finding, *report.findings[1:]),
        violations=(hidden_violation, *report.violations[1:]),
        visibilities=(hidden_visibility, *report.visibilities[1:]),
    )
    validation = validate_transition_integrity_report(mutated_report)

    assert validation["valid"] is False
    assert validation["hidden_integrity_finding_record_count"] == 1
    assert validation["hidden_integrity_violation_record_count"] == 1
    assert validation["hidden_visibility_record_count"] == 1
    assert validation["validation_error_count"] >= 3


def test_v3_9_transition_integrity_generated_report_contains_required_totals_and_guarantees():
    report = build_v3_9_transition_integrity_enforcement_report()
    summary = report["summary"]

    assert summary["integrity_satisfied_count"] == 1
    assert summary["integrity_warning_count"] == 1
    assert summary["integrity_failed_count"] == 1
    assert summary["blocked_count"] == 1
    assert summary["unsupported_count"] == 1
    assert summary["prohibited_count"] == 1
    assert summary["unknown_count"] == 1
    assert summary["incomplete_count"] == 1
    assert summary["integrity_finding_count"] > 0
    assert summary["integrity_violation_count"] > 0
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["non_executable_verified"] is True
    assert summary["non_remediation_verified"] is True
    assert summary["orchestration_boundaries_enforced"] is True
    assert summary["descriptive_audit_verified"] is True
    assert report["deterministic_guarantee_summary"]["finding_order_is_stable"] is True
    assert report["deterministic_guarantee_summary"]["violation_order_is_stable"] is True
    assert report["deterministic_guarantee_summary"]["visibility_order_is_stable"] is True
    assert report["non_execution_guarantees"]["report_capability_leakage_count"] == 0
    assert report["audit_only_guarantees"]["no_auto_remediation"] is True
    assert report["audit_only_guarantees"]["no_auto_repair"] is True
    assert report["audit_only_guarantees"]["no_recommendation_behavior"] is True
    assert report["audit_only_guarantees"]["no_ranking_behavior"] is True
    assert report["audit_only_guarantees"]["no_scoring_behavior"] is True
    assert report["audit_only_guarantees"]["no_selection_behavior"] is True
