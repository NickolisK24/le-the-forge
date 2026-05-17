"""Deterministic validation for v3.9 transition boundary intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_boundary_models import (
    BOUNDARY_CLASSIFICATION_BLOCKED,
    BOUNDARY_CLASSIFICATION_INCOMPLETE,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SAFE,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATIONS,
    BOUNDARY_VISIBILITY_FAIL_VISIBLE,
    NON_SAFE_BOUNDARY_CLASSIFICATIONS,
    PROHIBITED_BOUNDARY_CAPABILITIES,
    TransitionBoundaryReport,
)
from .transition_boundary_serialization import (
    validate_transition_boundary_hash_stability,
    validate_transition_boundary_serialization_stability,
)


def count_transition_boundary_classifications(report: TransitionBoundaryReport) -> dict[str, int]:
    counts = Counter(finding.classification for finding in report.findings)
    return {classification: counts.get(classification, 0) for classification in BOUNDARY_CLASSIFICATIONS}


def validate_transition_boundary_report(report: TransitionBoundaryReport) -> dict[str, Any]:
    classification_counts = count_transition_boundary_classifications(report)
    invalid_classification_count = sum(
        1 for finding in report.findings if finding.classification not in BOUNDARY_CLASSIFICATIONS
    )
    hidden_non_safe_state_count = sum(
        1
        for finding in report.findings
        if finding.classification in NON_SAFE_BOUNDARY_CLASSIFICATIONS
        and (finding.hidden or not finding.fail_visible)
    )
    vague_non_safe_output_count = sum(
        1
        for finding in report.findings
        if finding.classification in NON_SAFE_BOUNDARY_CLASSIFICATIONS
        and (
            not finding.reason
            or not finding.deterministic_evidence_reference
            or not finding.provenance_reference
            or not finding.continuity_reference
            or not finding.explainability_message
        )
    )
    non_safe_not_fail_visible_count = sum(
        1
        for classification in report.classifications
        if classification.classification in NON_SAFE_BOUNDARY_CLASSIFICATIONS
        and (
            classification.visibility_status != BOUNDARY_VISIBILITY_FAIL_VISIBLE
            or classification.hidden
            or not classification.fail_visible
            or not classification.reason
            or not classification.deterministic_evidence_reference
            or not classification.provenance_reference
            or not classification.continuity_reference
            or not classification.explainability_message
        )
    )
    incomplete_behavior_detection_count = classification_counts[BOUNDARY_CLASSIFICATION_INCOMPLETE]
    unsupported_behavior_detection_count = classification_counts[BOUNDARY_CLASSIFICATION_UNSUPPORTED]
    prohibited_behavior_detection_count = classification_counts[BOUNDARY_CLASSIFICATION_PROHIBITED]
    unknown_behavior_detection_count = classification_counts[BOUNDARY_CLASSIFICATION_UNKNOWN]
    blocked_behavior_detection_count = classification_counts[BOUNDARY_CLASSIFICATION_BLOCKED]
    execution_boundary_violation_count = sum(
        1
        for finding in report.findings
        for capability in finding.requested_capabilities
        if capability in PROHIBITED_BOUNDARY_CAPABILITIES
    )
    evidence_integrity_violation_count = sum(
        1
        for finding in report.findings
        if not finding.evidence.replay_safe
        or not finding.evidence.rollback_safe
        or not finding.evidence.provenance_preserved
        or not finding.evidence.explainability_safe
        or not finding.evidence.non_executable
        or finding.evidence.execution_behavior_enabled
        or finding.evidence.runtime_mutation_enabled
    )
    report_execution_capability_violation_count = sum(
        1
        for value in (
            report.transition_execution_enabled,
            report.orchestration_execution_enabled,
            report.graph_traversal_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.runtime_orchestration_engine_enabled,
            report.runtime_mutation_enabled,
            report.authorization_enabled,
            report.approval_enabled,
            report.optimization_enabled,
            report.recommendation_enabled,
            report.ranking_enabled,
            report.scoring_enabled,
            report.selection_enabled,
            report.autonomous_behavior_enabled,
            report.callable_orchestration_flow_enabled,
            report.transition_handler_enabled,
            report.state_machine_enabled,
            report.production_behavior_enabled,
            report.hidden_fallback_enabled,
            report.silent_correction_enabled,
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_classification_count,
            hidden_non_safe_state_count,
            vague_non_safe_output_count,
            non_safe_not_fail_visible_count,
            evidence_integrity_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "boundary_input_count": len(report.boundary_inputs),
        "classification_record_count": len(report.classifications),
        "finding_count": len(report.findings),
        "safe_transition_count": classification_counts[BOUNDARY_CLASSIFICATION_SAFE],
        "unsupported_behavior_detection_count": unsupported_behavior_detection_count,
        "prohibited_behavior_detection_count": prohibited_behavior_detection_count,
        "unknown_behavior_detection_count": unknown_behavior_detection_count,
        "incomplete_behavior_detection_count": incomplete_behavior_detection_count,
        "blocked_behavior_detection_count": blocked_behavior_detection_count,
        "hidden_non_safe_state_count": hidden_non_safe_state_count,
        "vague_non_safe_output_count": vague_non_safe_output_count,
        "non_safe_not_fail_visible_count": non_safe_not_fail_visible_count,
        "invalid_classification_count": invalid_classification_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "replay_safe_boundary_evidence_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_boundary_evidence_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_boundary_evidence_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_boundary_evidence_count": sum(
            1 for finding in report.findings if finding.explainability_safe
        ),
        "non_execution_confirmation_count": sum(
            1 for finding in report.findings if finding.non_execution_confirmation
        ),
        "classification_counts": classification_counts,
        "non_execution_confirmation": report.non_executable
        and report_execution_capability_violation_count == 0
        and evidence_integrity_violation_count == 0,
    }


def validate_transition_boundary_serialization_guarantees(
    report: TransitionBoundaryReport,
) -> dict[str, Any]:
    serialization = validate_transition_boundary_serialization_stability(report)
    hashing = validate_transition_boundary_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "boundary_hash": hashing["first_hash"],
    }
