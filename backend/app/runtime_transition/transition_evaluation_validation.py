"""Deterministic validation for v3.9 transition evaluation intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_evaluation_models import (
    EVALUATION_CLASSIFICATION_BLOCKED,
    EVALUATION_CLASSIFICATION_INCOMPLETE,
    EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_PROHIBITED,
    EVALUATION_CLASSIFICATION_SUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNKNOWN,
    EVALUATION_CLASSIFICATION_UNSUCCESSFUL,
    EVALUATION_CLASSIFICATION_UNSUPPORTED,
    EVALUATION_CLASSIFICATIONS,
    EVALUATION_FINDING_CATEGORIES,
    EVALUATION_FINDING_GOVERNANCE,
    EVALUATION_FINDING_MISSING_EVIDENCE,
    EVALUATION_FINDING_UNCERTAINTY,
    NON_SUCCESSFUL_EVALUATION_CLASSIFICATIONS,
    PROHIBITED_EVALUATION_CAPABILITIES,
    TransitionEvaluationReport,
)
from .transition_evaluation_serialization import (
    validate_transition_evaluation_hash_stability,
    validate_transition_evaluation_serialization_stability,
)


def count_transition_evaluation_classifications(report: TransitionEvaluationReport) -> dict[str, int]:
    counts = Counter(visibility.classification for visibility in report.visibilities)
    return {classification: counts.get(classification, 0) for classification in EVALUATION_CLASSIFICATIONS}


def count_transition_evaluation_finding_categories(report: TransitionEvaluationReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in EVALUATION_FINDING_CATEGORIES}


def validate_transition_evaluation_report(report: TransitionEvaluationReport) -> dict[str, Any]:
    classification_counts = count_transition_evaluation_classifications(report)
    finding_category_counts = count_transition_evaluation_finding_categories(report)
    invalid_classification_count = sum(
        1 for visibility in report.visibilities if visibility.classification not in EVALUATION_CLASSIFICATIONS
    )
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in EVALUATION_FINDING_CATEGORIES
    )
    hidden_finding_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_visibility_count = sum(1 for visibility in report.visibilities if visibility.hidden)
    finding_not_fail_visible_count = sum(
        1
        for finding in report.findings
        if (
            not finding.fail_visible
            or not finding.reason
            or not finding.evidence_reference
            or not finding.provenance_reference
            or not finding.continuity_reference
            or not finding.explainability_message
        )
    )
    non_successful_not_visible_count = sum(
        1
        for visibility in report.visibilities
        if visibility.classification in NON_SUCCESSFUL_EVALUATION_CLASSIFICATIONS
        and (not visibility.fail_visible or visibility.hidden or not visibility.reason)
    )
    successful_with_failure_finding_count = sum(
        1
        for visibility in report.visibilities
        if visibility.classification == EVALUATION_CLASSIFICATION_SUCCESSFUL
        for finding in report.findings
        if finding.input_id == visibility.input_id
        and finding.finding_category
        in (EVALUATION_FINDING_MISSING_EVIDENCE, EVALUATION_FINDING_GOVERNANCE)
        and finding.severity != "info"
    )
    continuity_integrity_violation_count = sum(
        1
        for continuity in report.continuities
        if not continuity.replay_continuity_preserved
        or not continuity.rollback_continuity_preserved
        or not continuity.provenance_continuity_preserved
        or not continuity.explainability_continuity_preserved
        or not continuity.immutable_continuity
    )
    evidence_integrity_violation_count = sum(
        1
        for evidence in report.evidence_records
        if not evidence.replay_safe
        or not evidence.rollback_safe
        or not evidence.provenance_preserved
        or not evidence.explainability_safe
        or not evidence.non_executable
        or evidence.execution_behavior_enabled
        or evidence.runtime_mutation_enabled
    )
    execution_boundary_violation_count = sum(
        1
        for source in report.evaluation_inputs
        for capability in source.requested_capabilities
        if capability in PROHIBITED_EVALUATION_CAPABILITIES
    )
    report_execution_capability_violation_count = sum(
        1
        for value in (
            report.transition_execution_enabled,
            report.orchestration_execution_enabled,
            report.orchestration_traversal_enabled,
            report.runtime_orchestration_engine_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.runtime_mutation_enabled,
            report.approval_enabled,
            report.authorization_enabled,
            report.optimization_enabled,
            report.recommendation_enabled,
            report.ranking_enabled,
            report.scoring_enabled,
            report.selection_enabled,
            report.autonomous_orchestration_behavior_enabled,
            report.transition_handler_enabled,
            report.orchestration_evaluator_enabled,
            report.runtime_state_machine_enabled,
            report.callable_orchestration_flow_enabled,
            report.production_execution_pathway_enabled,
            report.hidden_fallback_enabled,
            report.silent_correction_enabled,
            report.implicit_approval_enabled,
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_classification_count,
            invalid_finding_category_count,
            hidden_finding_count,
            hidden_visibility_count,
            finding_not_fail_visible_count,
            non_successful_not_visible_count,
            successful_with_failure_finding_count,
            continuity_integrity_violation_count,
            evidence_integrity_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "evaluation_input_count": len(report.evaluation_inputs),
        "visibility_count": len(report.visibilities),
        "finding_count": len(report.findings),
        "evidence_record_count": len(report.evidence_records),
        "continuity_record_count": len(report.continuities),
        "successful_count": classification_counts[EVALUATION_CLASSIFICATION_SUCCESSFUL],
        "partially_successful_count": classification_counts[EVALUATION_CLASSIFICATION_PARTIALLY_SUCCESSFUL],
        "unsuccessful_count": classification_counts[EVALUATION_CLASSIFICATION_UNSUCCESSFUL],
        "unsupported_count": classification_counts[EVALUATION_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[EVALUATION_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[EVALUATION_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[EVALUATION_CLASSIFICATION_INCOMPLETE],
        "blocked_count": classification_counts[EVALUATION_CLASSIFICATION_BLOCKED],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_category_counts,
        "evaluation_finding_count": len(report.findings),
        "governance_finding_count": finding_category_counts[EVALUATION_FINDING_GOVERNANCE],
        "uncertainty_finding_count": finding_category_counts[EVALUATION_FINDING_UNCERTAINTY],
        "missing_evidence_finding_count": finding_category_counts[EVALUATION_FINDING_MISSING_EVIDENCE],
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "hidden_finding_count": hidden_finding_count,
        "hidden_visibility_count": hidden_visibility_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "non_successful_not_visible_count": non_successful_not_visible_count,
        "successful_with_failure_finding_count": successful_with_failure_finding_count,
        "invalid_classification_count": invalid_classification_count,
        "invalid_finding_category_count": invalid_finding_category_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "replay_safe_evaluation_evidence_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_evaluation_evidence_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_evaluation_evidence_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_evaluation_evidence_count": sum(
            1 for finding in report.findings if finding.explainability_safe
        ),
        "replay_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.replay_continuity_preserved
        ),
        "rollback_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.rollback_continuity_preserved
        ),
        "provenance_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.provenance_continuity_preserved
        ),
        "explainability_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.explainability_continuity_preserved
        ),
        "non_execution_confirmation_count": sum(
            1 for finding in report.findings if finding.non_execution_confirmation
        ),
        "non_execution_confirmation": report.non_executable
        and report_execution_capability_violation_count == 0
        and evidence_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
    }


def validate_transition_evaluation_serialization_guarantees(
    report: TransitionEvaluationReport,
) -> dict[str, Any]:
    serialization = validate_transition_evaluation_serialization_stability(report)
    hashing = validate_transition_evaluation_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "evaluation_hash": hashing["first_hash"],
    }
