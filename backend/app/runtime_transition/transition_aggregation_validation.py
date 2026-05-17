"""Deterministic validation for v3.9 transition intelligence aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_aggregation_models import (
    AGGREGATION_CHOICE_PROHIBITED_CAPABILITIES,
    AGGREGATION_CLASSIFICATION_AGGREGATED,
    AGGREGATION_CLASSIFICATION_BLOCKED,
    AGGREGATION_CLASSIFICATION_INCOMPLETE,
    AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED,
    AGGREGATION_CLASSIFICATION_PROHIBITED,
    AGGREGATION_CLASSIFICATION_UNKNOWN,
    AGGREGATION_CLASSIFICATION_UNAGGREGATED,
    AGGREGATION_CLASSIFICATION_UNSUPPORTED,
    AGGREGATION_CLASSIFICATIONS,
    AGGREGATION_FINDING_CATEGORIES,
    AGGREGATION_VISIBILITY_CATEGORIES,
    AGGREGATION_VISIBILITY_GOVERNANCE,
    AGGREGATION_VISIBILITY_INTEGRITY,
    AGGREGATION_VISIBILITY_MISSING_EVIDENCE,
    AGGREGATION_VISIBILITY_UNCERTAINTY,
    NON_AGGREGATED_CLASSIFICATIONS,
    PROHIBITED_AGGREGATION_CAPABILITIES,
    TransitionAggregationReport,
)
from .transition_aggregation_serialization import (
    validate_transition_aggregation_hash_stability,
    validate_transition_aggregation_serialization_stability,
)


def count_transition_aggregation_classifications(report: TransitionAggregationReport) -> dict[str, int]:
    counts = Counter(record.classification for record in report.aggregation_records)
    return {classification: counts.get(classification, 0) for classification in AGGREGATION_CLASSIFICATIONS}


def count_transition_aggregation_finding_categories(report: TransitionAggregationReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in AGGREGATION_FINDING_CATEGORIES}


def count_transition_aggregation_visibility_categories(report: TransitionAggregationReport) -> dict[str, int]:
    counts = Counter(visibility.visibility_category for visibility in report.visibilities)
    return {category: counts.get(category, 0) for category in AGGREGATION_VISIBILITY_CATEGORIES}


def validate_transition_aggregation_report(report: TransitionAggregationReport) -> dict[str, Any]:
    classification_counts = count_transition_aggregation_classifications(report)
    finding_counts = count_transition_aggregation_finding_categories(report)
    visibility_counts = count_transition_aggregation_visibility_categories(report)
    invalid_classification_count = sum(
        1 for record in report.aggregation_records if record.classification not in AGGREGATION_CLASSIFICATIONS
    )
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in AGGREGATION_FINDING_CATEGORIES
    )
    invalid_visibility_category_count = sum(
        1 for visibility in report.visibilities if visibility.visibility_category not in AGGREGATION_VISIBILITY_CATEGORIES
    )
    hidden_aggregation_finding_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_visibility_count = sum(1 for visibility in report.visibilities if visibility.hidden)
    hidden_risk_visibility_count = sum(1 for risk_visibility in report.risk_visibility_records if risk_visibility.hidden)
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
            or visibility.prioritization_enabled
            or visibility.weighting_enabled
            or visibility.recommendation_enabled
            or visibility.ranking_enabled
            or visibility.scoring_enabled
            or visibility.selection_enabled
        )
    )
    non_aggregated_not_visible_count = sum(
        1
        for visibility in report.visibilities
        if visibility.classification in NON_AGGREGATED_CLASSIFICATIONS
        and (not visibility.fail_visible or visibility.hidden or not visibility.reason)
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
    provenance_integrity_violation_count = sum(
        1
        for provenance in report.provenance_records
        if not provenance.provenance_preserved or not provenance.immutable_provenance
    )
    risk_visibility_selection_violation_count = sum(
        1
        for risk_visibility in report.risk_visibility_records
        if not risk_visibility.descriptive_only
        or risk_visibility.recommendation_enabled
        or risk_visibility.ranking_enabled
        or risk_visibility.scoring_enabled
        or risk_visibility.selection_enabled
    )
    record_selection_violation_count = sum(
        1
        for record in report.aggregation_records
        if record.recommendation_enabled or record.ranking_enabled or record.scoring_enabled or record.selection_enabled
    )
    execution_boundary_violation_count = sum(
        1
        for source in report.aggregation_inputs
        for capability in source.requested_capabilities
        if capability in PROHIBITED_AGGREGATION_CAPABILITIES
    )
    recommendation_ranking_scoring_selection_violation_count = sum(
        1
        for source in report.aggregation_inputs
        for capability in source.requested_capabilities
        if capability in AGGREGATION_CHOICE_PROHIBITED_CAPABILITIES
    )
    report_execution_capability_violation_count = sum(
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
            report.hidden_fallback_enabled,
            report.silent_correction_enabled,
            report.prioritization_enabled,
            report.weighting_enabled,
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_classification_count,
            invalid_finding_category_count,
            invalid_visibility_category_count,
            hidden_aggregation_finding_count,
            hidden_visibility_count,
            hidden_risk_visibility_count,
            finding_not_fail_visible_count,
            visibility_not_fail_visible_count,
            non_aggregated_not_visible_count,
            evidence_integrity_violation_count,
            continuity_integrity_violation_count,
            provenance_integrity_violation_count,
            risk_visibility_selection_violation_count,
            record_selection_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "aggregation_input_count": len(report.aggregation_inputs),
        "aggregation_record_count": len(report.aggregation_records),
        "aggregation_finding_count": len(report.findings),
        "aggregation_visibility_count": len(report.visibilities),
        "evidence_record_count": len(report.evidence_records),
        "continuity_record_count": len(report.continuities),
        "provenance_record_count": len(report.provenance_records),
        "risk_visibility_record_count": len(report.risk_visibility_records),
        "aggregated_count": classification_counts[AGGREGATION_CLASSIFICATION_AGGREGATED],
        "partially_aggregated_count": classification_counts[AGGREGATION_CLASSIFICATION_PARTIALLY_AGGREGATED],
        "unaggregated_count": classification_counts[AGGREGATION_CLASSIFICATION_UNAGGREGATED],
        "blocked_count": classification_counts[AGGREGATION_CLASSIFICATION_BLOCKED],
        "unsupported_count": classification_counts[AGGREGATION_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[AGGREGATION_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[AGGREGATION_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[AGGREGATION_CLASSIFICATION_INCOMPLETE],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_counts,
        "visibility_category_counts": visibility_counts,
        "governance_visibility_count": visibility_counts[AGGREGATION_VISIBILITY_GOVERNANCE],
        "integrity_visibility_count": visibility_counts[AGGREGATION_VISIBILITY_INTEGRITY],
        "uncertainty_visibility_count": visibility_counts[AGGREGATION_VISIBILITY_UNCERTAINTY],
        "missing_evidence_visibility_count": visibility_counts[AGGREGATION_VISIBILITY_MISSING_EVIDENCE],
        "hidden_aggregation_finding_count": hidden_aggregation_finding_count,
        "hidden_visibility_count": hidden_visibility_count,
        "hidden_risk_visibility_count": hidden_risk_visibility_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "visibility_not_fail_visible_count": visibility_not_fail_visible_count,
        "non_aggregated_not_visible_count": non_aggregated_not_visible_count,
        "invalid_classification_count": invalid_classification_count,
        "invalid_finding_category_count": invalid_finding_category_count,
        "invalid_visibility_category_count": invalid_visibility_category_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "recommendation_ranking_scoring_selection_violation_count": recommendation_ranking_scoring_selection_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "provenance_integrity_violation_count": provenance_integrity_violation_count,
        "risk_visibility_selection_violation_count": risk_visibility_selection_violation_count,
        "record_selection_violation_count": record_selection_violation_count,
        "replay_safe_aggregation_finding_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_aggregation_finding_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_aggregation_finding_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_aggregation_finding_count": sum(
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
        "no_recommendation_confirmation_count": sum(
            1 for finding in report.findings if finding.no_recommendation_confirmation
        ),
        "non_execution_confirmation": report.non_executable
        and report_execution_capability_violation_count == 0
        and evidence_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
        "non_selective_confirmation": report.recommendation_enabled is False
        and report.ranking_enabled is False
        and report.scoring_enabled is False
        and report.selection_enabled is False
        and report.prioritization_enabled is False
        and report.weighting_enabled is False
        and visibility_not_fail_visible_count == 0
        and risk_visibility_selection_violation_count == 0
        and record_selection_violation_count == 0,
    }


def validate_transition_aggregation_serialization_guarantees(report: TransitionAggregationReport) -> dict[str, Any]:
    serialization = validate_transition_aggregation_serialization_stability(report)
    hashing = validate_transition_aggregation_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "aggregation_hash": hashing["first_hash"],
    }
