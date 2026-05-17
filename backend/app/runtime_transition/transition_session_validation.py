"""Deterministic validation for v3.9 transition session intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_session_models import (
    NON_COMPLETE_SESSION_CLASSIFICATIONS,
    PROHIBITED_SESSION_CAPABILITIES,
    SESSION_CLASSIFICATION_BLOCKED,
    SESSION_CLASSIFICATION_COMPLETE,
    SESSION_CLASSIFICATION_INCOMPLETE,
    SESSION_CLASSIFICATION_PARTIALLY_COMPLETE,
    SESSION_CLASSIFICATION_PROHIBITED,
    SESSION_CLASSIFICATION_UNKNOWN,
    SESSION_CLASSIFICATION_UNSUPPORTED,
    SESSION_CLASSIFICATIONS,
    SESSION_FINDING_CATEGORIES,
    SESSION_FINDING_GOVERNANCE,
    SESSION_FINDING_MISSING_EVIDENCE,
    SESSION_FINDING_UNCERTAINTY,
    TransitionSessionReport,
)
from .transition_session_serialization import (
    validate_transition_session_hash_stability,
    validate_transition_session_serialization_stability,
)


def count_transition_session_classifications(report: TransitionSessionReport) -> dict[str, int]:
    counts = Counter(visibility.classification for visibility in report.visibilities)
    return {classification: counts.get(classification, 0) for classification in SESSION_CLASSIFICATIONS}


def count_transition_session_finding_categories(report: TransitionSessionReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in SESSION_FINDING_CATEGORIES}


def validate_transition_session_report(report: TransitionSessionReport) -> dict[str, Any]:
    classification_counts = count_transition_session_classifications(report)
    finding_category_counts = count_transition_session_finding_categories(report)
    invalid_classification_count = sum(
        1 for visibility in report.visibilities if visibility.classification not in SESSION_CLASSIFICATIONS
    )
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in SESSION_FINDING_CATEGORIES
    )
    hidden_session_finding_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_entry_count = sum(1 for entry in report.entries if entry.hidden)
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
    non_complete_not_visible_count = sum(
        1
        for visibility in report.visibilities
        if visibility.classification in NON_COMPLETE_SESSION_CLASSIFICATIONS
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
    )
    entry_integrity_violation_count = sum(
        1
        for entry in report.entries
        if not entry.replay_safe
        or not entry.rollback_safe
        or not entry.provenance_preserved
        or not entry.explainability_safe
        or not entry.immutable_entry
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
    execution_boundary_violation_count = sum(
        1
        for source in report.session_inputs
        for capability in source.requested_capabilities
        if capability in PROHIBITED_SESSION_CAPABILITIES
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
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_classification_count,
            invalid_finding_category_count,
            hidden_session_finding_count,
            hidden_entry_count,
            hidden_visibility_count,
            finding_not_fail_visible_count,
            non_complete_not_visible_count,
            evidence_integrity_violation_count,
            entry_integrity_violation_count,
            continuity_integrity_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "session_input_count": len(report.session_inputs),
        "session_record_count": len(report.session_records),
        "evaluation_entry_count": len(report.entries),
        "session_finding_count": len(report.findings),
        "evidence_record_count": len(report.evidence_records),
        "continuity_record_count": len(report.continuities),
        "visibility_count": len(report.visibilities),
        "complete_count": classification_counts[SESSION_CLASSIFICATION_COMPLETE],
        "partially_complete_count": classification_counts[SESSION_CLASSIFICATION_PARTIALLY_COMPLETE],
        "incomplete_count": classification_counts[SESSION_CLASSIFICATION_INCOMPLETE],
        "blocked_count": classification_counts[SESSION_CLASSIFICATION_BLOCKED],
        "unsupported_count": classification_counts[SESSION_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[SESSION_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[SESSION_CLASSIFICATION_UNKNOWN],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_category_counts,
        "governance_finding_count": finding_category_counts[SESSION_FINDING_GOVERNANCE],
        "uncertainty_finding_count": finding_category_counts[SESSION_FINDING_UNCERTAINTY],
        "missing_evidence_finding_count": finding_category_counts[SESSION_FINDING_MISSING_EVIDENCE],
        "hidden_session_finding_count": hidden_session_finding_count,
        "hidden_entry_count": hidden_entry_count,
        "hidden_visibility_count": hidden_visibility_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "non_complete_not_visible_count": non_complete_not_visible_count,
        "invalid_classification_count": invalid_classification_count,
        "invalid_finding_category_count": invalid_finding_category_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "entry_integrity_violation_count": entry_integrity_violation_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "replay_safe_session_finding_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_session_finding_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_session_finding_count": sum(1 for finding in report.findings if finding.provenance_preserved),
        "explainability_safe_session_finding_count": sum(1 for finding in report.findings if finding.explainability_safe),
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
        and entry_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
    }


def validate_transition_session_serialization_guarantees(report: TransitionSessionReport) -> dict[str, Any]:
    serialization = validate_transition_session_serialization_stability(report)
    hashing = validate_transition_session_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "session_hash": hashing["first_hash"],
    }
