"""Deterministic validation for v3.9 transition integrity enforcement."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_integrity_models import (
    INTEGRITY_CLASSIFICATION_BLOCKED,
    INTEGRITY_CLASSIFICATION_FAILED,
    INTEGRITY_CLASSIFICATION_INCOMPLETE,
    INTEGRITY_CLASSIFICATION_PROHIBITED,
    INTEGRITY_CLASSIFICATION_SATISFIED,
    INTEGRITY_CLASSIFICATION_UNKNOWN,
    INTEGRITY_CLASSIFICATION_UNSUPPORTED,
    INTEGRITY_CLASSIFICATION_WARNING,
    INTEGRITY_CLASSIFICATIONS,
    INTEGRITY_FINDING_CATEGORIES,
    INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP,
    INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK,
    INTEGRITY_VIOLATION_EXPLAINABILITY_GAP,
    INTEGRITY_VIOLATION_HIDDEN_FINDING,
    INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE,
    INTEGRITY_VIOLATION_HIDDEN_RISK,
    INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP,
    INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_PROVENANCE_GAP,
    INTEGRITY_VIOLATION_RANKING_LEAK,
    INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,
    INTEGRITY_VIOLATION_REPLAY_GAP,
    INTEGRITY_VIOLATION_ROLLBACK_GAP,
    INTEGRITY_VIOLATION_SCORING_LEAK,
    INTEGRITY_VIOLATION_SELECTION_LEAK,
    INTEGRITY_VIOLATION_MUTATION_LEAK,
    INTEGRITY_VIOLATION_TYPES,
    INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP,
    INTEGRITY_VISIBILITY_CATEGORIES,
    TransitionIntegrityReport,
)
from .transition_integrity_serialization import (
    validate_transition_integrity_hash_stability,
    validate_transition_integrity_serialization_stability,
)


def count_transition_integrity_classifications(report: TransitionIntegrityReport) -> dict[str, int]:
    counts = Counter(source_classification(report, source.input_id) for source in report.integrity_inputs)
    return {classification: counts.get(classification, 0) for classification in INTEGRITY_CLASSIFICATIONS}


def count_transition_integrity_finding_categories(report: TransitionIntegrityReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in INTEGRITY_FINDING_CATEGORIES}


def count_transition_integrity_violation_types(report: TransitionIntegrityReport) -> dict[str, int]:
    counts = Counter(violation.violation_type for violation in report.violations)
    return {violation_type: counts.get(violation_type, 0) for violation_type in INTEGRITY_VIOLATION_TYPES}


def count_transition_integrity_visibility_categories(report: TransitionIntegrityReport) -> dict[str, int]:
    counts = Counter(visibility.visibility_category for visibility in report.visibilities)
    return {category: counts.get(category, 0) for category in INTEGRITY_VISIBILITY_CATEGORIES}


def validate_transition_integrity_report(report: TransitionIntegrityReport) -> dict[str, Any]:
    classification_counts = count_transition_integrity_classifications(report)
    finding_counts = count_transition_integrity_finding_categories(report)
    violation_counts = count_transition_integrity_violation_types(report)
    visibility_counts = count_transition_integrity_visibility_categories(report)
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in INTEGRITY_FINDING_CATEGORIES
    )
    invalid_violation_type_count = sum(
        1 for violation in report.violations if violation.violation_type not in INTEGRITY_VIOLATION_TYPES
    )
    invalid_visibility_category_count = sum(
        1 for visibility in report.visibilities if visibility.visibility_category not in INTEGRITY_VISIBILITY_CATEGORIES
    )
    hidden_integrity_finding_record_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_integrity_violation_record_count = sum(1 for violation in report.violations if violation.hidden)
    hidden_visibility_record_count = sum(1 for visibility in report.visibilities if visibility.hidden)
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
            or not finding.descriptive_only
            or finding.remediation_enabled
            or finding.repair_enabled
            or finding.recommendation_enabled
            or finding.ranking_enabled
            or finding.scoring_enabled
            or finding.selection_enabled
        )
    )
    violation_not_fail_visible_count = sum(
        1
        for violation in report.violations
        if (
            not violation.fail_visible
            or not violation.reason
            or not violation.evidence_reference
            or not violation.provenance_reference
            or not violation.continuity_reference
            or not violation.explainability_message
            or not violation.descriptive_only
            or violation.remediation_enabled
            or violation.repair_enabled
            or violation.severity_score is not None
            or violation.priority_rank is not None
        )
    )
    visibility_not_fail_visible_count = sum(
        1
        for visibility in report.visibilities
        if (
            not visibility.fail_visible
            or not visibility.reason
            or not visibility.evidence_reference
            or not visibility.provenance_reference
            or not visibility.continuity_reference
            or not visibility.explainability_message
            or not visibility.descriptive_only
            or visibility.remediation_enabled
            or visibility.repair_enabled
            or visibility.priority_ranking_enabled
            or visibility.weighted_severity_enabled
            or visibility.recommendation_enabled
            or visibility.ranking_enabled
            or visibility.scoring_enabled
            or visibility.selection_enabled
        )
    )
    evidence_integrity_violation_count = sum(
        1
        for evidence in report.evidence_records
        if not evidence.replay_safe
        or not evidence.rollback_safe
        or not evidence.provenance_preserved
        or not evidence.explainability_safe
        or not evidence.non_executable
        or evidence.remediation_enabled
        or evidence.repair_enabled
        or evidence.execution_behavior_enabled
        or evidence.runtime_mutation_enabled
        or evidence.recommendation_behavior_enabled
        or evidence.ranking_behavior_enabled
        or evidence.scoring_behavior_enabled
        or evidence.selection_behavior_enabled
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
    report_capability_leakage_count = sum(
        1
        for value in (
            report.orchestration_execution_enabled,
            report.transition_execution_enabled,
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
            report.runtime_state_machine_enabled,
            report.production_behavior_enabled,
            report.remediation_enabled,
            report.repair_enabled,
            report.automatic_remediation_enabled,
            report.automatic_repair_enabled,
            report.hidden_fallback_enabled,
            report.silent_correction_enabled,
            report.prioritization_enabled,
            report.weighted_severity_scoring_enabled,
        )
        if value
    )
    missing_evidence_violation_count = sum(
        count
        for violation_type, count in violation_counts.items()
        if violation_type.startswith("missing_") and violation_type.endswith("_evidence")
    ) + violation_counts[INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP]
    visibility_gap_count = (
        violation_counts[INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP]
        + violation_counts[INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP]
        + violation_counts[INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP]
    )
    validation_error_count = sum(
        (
            invalid_finding_category_count,
            invalid_violation_type_count,
            invalid_visibility_category_count,
            hidden_integrity_finding_record_count,
            hidden_integrity_violation_record_count,
            hidden_visibility_record_count,
            finding_not_fail_visible_count,
            violation_not_fail_visible_count,
            visibility_not_fail_visible_count,
            evidence_integrity_violation_count,
            continuity_integrity_violation_count,
            report_capability_leakage_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "integrity_input_count": len(report.integrity_inputs),
        "integrity_finding_count": len(report.findings),
        "integrity_violation_count": len(report.violations),
        "integrity_evidence_count": len(report.evidence_records),
        "integrity_continuity_count": len(report.continuities),
        "integrity_visibility_count": len(report.visibilities),
        "integrity_satisfied_count": classification_counts[INTEGRITY_CLASSIFICATION_SATISFIED],
        "integrity_warning_count": classification_counts[INTEGRITY_CLASSIFICATION_WARNING],
        "integrity_failed_count": classification_counts[INTEGRITY_CLASSIFICATION_FAILED],
        "blocked_count": classification_counts[INTEGRITY_CLASSIFICATION_BLOCKED],
        "unsupported_count": classification_counts[INTEGRITY_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[INTEGRITY_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[INTEGRITY_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[INTEGRITY_CLASSIFICATION_INCOMPLETE],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_counts,
        "violation_type_counts": violation_counts,
        "visibility_category_counts": visibility_counts,
        "hidden_finding_violation_count": violation_counts[INTEGRITY_VIOLATION_HIDDEN_FINDING],
        "hidden_risk_violation_count": violation_counts[INTEGRITY_VIOLATION_HIDDEN_RISK],
        "hidden_non_safe_state_violation_count": violation_counts[
            INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE
        ],
        "missing_evidence_violation_count": missing_evidence_violation_count,
        "provenance_gap_count": violation_counts[INTEGRITY_VIOLATION_PROVENANCE_GAP],
        "replay_gap_count": violation_counts[INTEGRITY_VIOLATION_REPLAY_GAP],
        "rollback_gap_count": violation_counts[INTEGRITY_VIOLATION_ROLLBACK_GAP],
        "explainability_gap_count": violation_counts[INTEGRITY_VIOLATION_EXPLAINABILITY_GAP],
        "aggregation_integrity_gap_count": violation_counts[
            INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP
        ],
        "execution_boundary_leakage_count": violation_counts[
            INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK
        ],
        "recommendation_leakage_count": violation_counts[INTEGRITY_VIOLATION_RECOMMENDATION_LEAK],
        "ranking_leakage_count": violation_counts[INTEGRITY_VIOLATION_RANKING_LEAK],
        "scoring_leakage_count": violation_counts[INTEGRITY_VIOLATION_SCORING_LEAK],
        "selection_leakage_count": violation_counts[INTEGRITY_VIOLATION_SELECTION_LEAK],
        "mutation_leakage_count": violation_counts[INTEGRITY_VIOLATION_MUTATION_LEAK],
        "visibility_gap_count": visibility_gap_count,
        "hidden_integrity_finding_record_count": hidden_integrity_finding_record_count,
        "hidden_integrity_violation_record_count": hidden_integrity_violation_record_count,
        "hidden_visibility_record_count": hidden_visibility_record_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "violation_not_fail_visible_count": violation_not_fail_visible_count,
        "visibility_not_fail_visible_count": visibility_not_fail_visible_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "report_capability_leakage_count": report_capability_leakage_count,
        "replay_safe_integrity_finding_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_integrity_finding_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_integrity_finding_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_integrity_finding_count": sum(
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
        "non_execution_confirmation": report.non_executable
        and report_capability_leakage_count == 0
        and evidence_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
        "non_remediation_confirmation": report.remediation_enabled is False
        and report.repair_enabled is False
        and report.automatic_remediation_enabled is False
        and report.automatic_repair_enabled is False
        and report.silent_correction_enabled is False
        and report.hidden_fallback_enabled is False
        and evidence_integrity_violation_count == 0,
        "non_selective_confirmation": report.recommendation_enabled is False
        and report.ranking_enabled is False
        and report.scoring_enabled is False
        and report.selection_enabled is False
        and report.prioritization_enabled is False
        and report.weighted_severity_scoring_enabled is False
        and visibility_not_fail_visible_count == 0
        and violation_not_fail_visible_count == 0,
    }


def validate_transition_integrity_serialization_guarantees(report: TransitionIntegrityReport) -> dict[str, Any]:
    serialization = validate_transition_integrity_serialization_stability(report)
    hashing = validate_transition_integrity_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "integrity_hash": hashing["first_hash"],
    }


def source_classification(report: TransitionIntegrityReport, input_id: str) -> str:
    for finding in report.findings:
        if finding.input_id == input_id:
            return finding.classification
    return INTEGRITY_CLASSIFICATION_UNKNOWN
