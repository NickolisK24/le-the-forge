"""Deterministic validation for v3.9 transition compatibility intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_compatibility_models import (
    COMPATIBILITY_CLASSIFICATION_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_INCOMPLETE,
    COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE,
    COMPATIBILITY_CLASSIFICATION_PROHIBITED,
    COMPATIBILITY_CLASSIFICATION_UNKNOWN,
    COMPATIBILITY_CLASSIFICATION_UNSUPPORTED,
    COMPATIBILITY_CLASSIFICATIONS,
    COMPATIBILITY_CONFLICT_BOUNDARY,
    COMPATIBILITY_CONFLICT_CONTINUITY,
    COMPATIBILITY_CONFLICT_EXPLAINABILITY,
    COMPATIBILITY_CONFLICT_MISSING_EVIDENCE,
    COMPATIBILITY_CONFLICT_PROHIBITED_STATE,
    COMPATIBILITY_CONFLICT_PROVENANCE,
    COMPATIBILITY_CONFLICT_TRANSITION_STATE,
    COMPATIBILITY_CONFLICT_TYPES,
    COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE,
    NON_COMPATIBLE_CLASSIFICATIONS,
    PROHIBITED_COMPATIBILITY_CAPABILITIES,
    TransitionCompatibilityReport,
)
from .transition_compatibility_serialization import (
    validate_transition_compatibility_hash_stability,
    validate_transition_compatibility_serialization_stability,
)


def count_transition_compatibility_classifications(
    report: TransitionCompatibilityReport,
) -> dict[str, int]:
    counts = Counter(finding.classification for finding in report.findings)
    return {classification: counts.get(classification, 0) for classification in COMPATIBILITY_CLASSIFICATIONS}


def count_transition_compatibility_conflicts(report: TransitionCompatibilityReport) -> dict[str, int]:
    counts = Counter(conflict.conflict_type for conflict in report.conflicts)
    return {conflict_type: counts.get(conflict_type, 0) for conflict_type in COMPATIBILITY_CONFLICT_TYPES}


def validate_transition_compatibility_report(report: TransitionCompatibilityReport) -> dict[str, Any]:
    classification_counts = count_transition_compatibility_classifications(report)
    conflict_counts = count_transition_compatibility_conflicts(report)
    invalid_classification_count = sum(
        1 for finding in report.findings if finding.classification not in COMPATIBILITY_CLASSIFICATIONS
    )
    invalid_conflict_type_count = sum(
        1 for conflict in report.conflicts if conflict.conflict_type not in COMPATIBILITY_CONFLICT_TYPES
    )
    hidden_conflict_count = sum(1 for conflict in report.conflicts if conflict.hidden)
    conflict_not_fail_visible_count = sum(
        1
        for conflict in report.conflicts
        if (
            not conflict.fail_visible
            or not conflict.evidence_reference
            or not conflict.provenance_reference
            or not conflict.continuity_reference
            or not conflict.explainability_message
        )
    )
    hidden_non_compatible_finding_count = sum(
        1
        for finding in report.findings
        if finding.classification in NON_COMPATIBLE_CLASSIFICATIONS and finding.hidden
    )
    non_compatible_not_fail_visible_count = sum(
        1
        for finding in report.findings
        if finding.classification in NON_COMPATIBLE_CLASSIFICATIONS and not finding.fail_visible
    )
    vague_non_compatible_output_count = sum(
        1
        for finding in report.findings
        if finding.classification in NON_COMPATIBLE_CLASSIFICATIONS
        and (
            not finding.reason
            or not finding.evidence.evidence_id
            or not finding.evidence.provenance_reference_ids
            or not finding.evidence.continuity_reference_ids
            or not finding.conflicts
        )
    )
    compatible_with_conflict_count = sum(
        1
        for finding in report.findings
        if finding.classification == COMPATIBILITY_CLASSIFICATION_COMPATIBLE and finding.conflicts
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
    execution_boundary_violation_count = sum(
        1
        for source in report.compatibility_inputs
        for capability in source.requested_capabilities
        if capability in PROHIBITED_COMPATIBILITY_CAPABILITIES
    )
    report_execution_capability_violation_count = sum(
        1
        for value in (
            report.transition_execution_enabled,
            report.orchestration_execution_enabled,
            report.orchestration_traversal_enabled,
            report.routing_enabled,
            report.scheduling_enabled,
            report.dispatch_enabled,
            report.orchestration_engine_enabled,
            report.runtime_mutation_enabled,
            report.autonomous_behavior_enabled,
            report.optimization_enabled,
            report.recommendation_enabled,
            report.ranking_enabled,
            report.scoring_enabled,
            report.selection_enabled,
            report.approval_enabled,
            report.authorization_enabled,
            report.callable_orchestration_flow_enabled,
            report.transition_handler_enabled,
            report.orchestration_evaluator_enabled,
            report.runtime_state_machine_enabled,
            report.production_execution_pathway_enabled,
            report.hidden_fallback_enabled,
            report.silent_correction_enabled,
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_classification_count,
            invalid_conflict_type_count,
            hidden_conflict_count,
            conflict_not_fail_visible_count,
            hidden_non_compatible_finding_count,
            non_compatible_not_fail_visible_count,
            vague_non_compatible_output_count,
            compatible_with_conflict_count,
            evidence_integrity_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "compatibility_input_count": len(report.compatibility_inputs),
        "finding_count": len(report.findings),
        "conflict_count": len(report.conflicts),
        "compatible_count": classification_counts[COMPATIBILITY_CLASSIFICATION_COMPATIBLE],
        "incompatible_count": classification_counts[COMPATIBILITY_CLASSIFICATION_INCOMPATIBLE],
        "partially_compatible_count": classification_counts[COMPATIBILITY_CLASSIFICATION_PARTIALLY_COMPATIBLE],
        "unsupported_count": classification_counts[COMPATIBILITY_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[COMPATIBILITY_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[COMPATIBILITY_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[COMPATIBILITY_CLASSIFICATION_INCOMPLETE],
        "classification_counts": classification_counts,
        "compatibility_conflict_count": len(report.conflicts),
        "provenance_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_PROVENANCE],
        "continuity_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_CONTINUITY],
        "boundary_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_BOUNDARY],
        "transition_state_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_TRANSITION_STATE],
        "unsupported_state_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_UNSUPPORTED_STATE],
        "prohibited_state_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_PROHIBITED_STATE],
        "explainability_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_EXPLAINABILITY],
        "missing_evidence_conflict_count": conflict_counts[COMPATIBILITY_CONFLICT_MISSING_EVIDENCE],
        "conflict_counts": conflict_counts,
        "hidden_conflict_count": hidden_conflict_count,
        "conflict_not_fail_visible_count": conflict_not_fail_visible_count,
        "hidden_non_compatible_finding_count": hidden_non_compatible_finding_count,
        "non_compatible_not_fail_visible_count": non_compatible_not_fail_visible_count,
        "vague_non_compatible_output_count": vague_non_compatible_output_count,
        "compatible_with_conflict_count": compatible_with_conflict_count,
        "invalid_classification_count": invalid_classification_count,
        "invalid_conflict_type_count": invalid_conflict_type_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "replay_safe_compatibility_evidence_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_compatibility_evidence_count": sum(
            1 for finding in report.findings if finding.rollback_safe
        ),
        "provenance_safe_compatibility_evidence_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_compatibility_evidence_count": sum(
            1 for finding in report.findings if finding.explainability_safe
        ),
        "non_execution_confirmation_count": sum(
            1 for finding in report.findings if finding.non_execution_confirmation
        ),
        "non_execution_confirmation": report.non_executable
        and report_execution_capability_violation_count == 0
        and evidence_integrity_violation_count == 0,
    }


def validate_transition_compatibility_serialization_guarantees(
    report: TransitionCompatibilityReport,
) -> dict[str, Any]:
    serialization = validate_transition_compatibility_serialization_stability(report)
    hashing = validate_transition_compatibility_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "compatibility_hash": hashing["first_hash"],
    }
