"""Deterministic validation for v3.9 transition continuity certification."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_certification_models import (
    CERTIFICATION_CLASSIFICATION_BLOCKED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
    CERTIFICATION_CLASSIFICATION_INCOMPLETE,
    CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_PROHIBITED,
    CERTIFICATION_CLASSIFICATION_UNKNOWN,
    CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
    CERTIFICATION_CLASSIFICATIONS,
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
    TransitionCertificationReport,
)
from .transition_certification_serialization import (
    validate_transition_certification_hash_stability,
    validate_transition_certification_serialization_stability,
)


def source_classification(report: TransitionCertificationReport, input_id: str) -> str:
    for finding in report.findings:
        if finding.input_id == input_id:
            return finding.classification
    return CERTIFICATION_CLASSIFICATION_UNKNOWN


def count_transition_certification_classifications(report: TransitionCertificationReport) -> dict[str, int]:
    counts = Counter(source_classification(report, source.input_id) for source in report.certification_inputs)
    return {classification: counts.get(classification, 0) for classification in CERTIFICATION_CLASSIFICATIONS}


def count_transition_certification_finding_categories(report: TransitionCertificationReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in CERTIFICATION_FINDING_CATEGORIES}


def count_transition_certification_guarantee_categories(report: TransitionCertificationReport) -> dict[str, int]:
    counts = Counter(guarantee.guarantee_category for guarantee in report.guarantees)
    return {category: counts.get(category, 0) for category in CERTIFICATION_GUARANTEE_CATEGORIES}


def count_transition_certification_visibility_categories(report: TransitionCertificationReport) -> dict[str, int]:
    counts = Counter(visibility.visibility_category for visibility in report.visibilities)
    return {category: counts.get(category, 0) for category in CERTIFICATION_VISIBILITY_CATEGORIES}


def validate_transition_certification_report(report: TransitionCertificationReport) -> dict[str, Any]:
    classification_counts = count_transition_certification_classifications(report)
    finding_counts = count_transition_certification_finding_categories(report)
    guarantee_counts = count_transition_certification_guarantee_categories(report)
    visibility_counts = count_transition_certification_visibility_categories(report)
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in CERTIFICATION_FINDING_CATEGORIES
    )
    invalid_guarantee_category_count = sum(
        1 for guarantee in report.guarantees if guarantee.guarantee_category not in CERTIFICATION_GUARANTEE_CATEGORIES
    )
    invalid_visibility_category_count = sum(
        1 for visibility in report.visibilities if visibility.visibility_category not in CERTIFICATION_VISIBILITY_CATEGORIES
    )
    hidden_finding_record_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_guarantee_record_count = sum(1 for guarantee in report.guarantees if guarantee.hidden)
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
            or finding.approval_enabled
            or finding.remediation_enabled
            or finding.repair_enabled
            or finding.recommendation_enabled
            or finding.ranking_enabled
            or finding.scoring_enabled
            or finding.selection_enabled
        )
    )
    guarantee_not_visible_count = sum(
        1
        for guarantee in report.guarantees
        if (
            not guarantee.visible
            or not guarantee.reason
            or not guarantee.evidence_reference
            or not guarantee.provenance_reference
            or not guarantee.continuity_reference
            or not guarantee.explainability_message
            or not guarantee.descriptive_only
            or guarantee.approval_enabled
            or guarantee.remediation_enabled
            or guarantee.repair_enabled
            or guarantee.recommendation_enabled
            or guarantee.ranking_enabled
            or guarantee.scoring_enabled
            or guarantee.selection_enabled
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
            or visibility.approval_enabled
            or visibility.remediation_enabled
            or visibility.repair_enabled
            or visibility.priority_ranking_enabled
            or visibility.weighted_scoring_enabled
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
        or evidence.approval_enabled
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
        or not continuity.visibility_continuity_preserved
        or not continuity.integrity_continuity_preserved
        or not continuity.non_execution_continuity_preserved
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
            report.weighted_scoring_enabled,
        )
        if value
    )
    validation_error_count = sum(
        (
            invalid_finding_category_count,
            invalid_guarantee_category_count,
            invalid_visibility_category_count,
            hidden_finding_record_count,
            hidden_guarantee_record_count,
            hidden_visibility_record_count,
            finding_not_fail_visible_count,
            guarantee_not_visible_count,
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
        "certification_input_count": len(report.certification_inputs),
        "certification_finding_count": len(report.findings),
        "certification_guarantee_count": len(report.guarantees),
        "certification_evidence_count": len(report.evidence_records),
        "certification_continuity_count": len(report.continuities),
        "certification_visibility_count": len(report.visibilities),
        "certified_count": classification_counts[CERTIFICATION_CLASSIFICATION_CERTIFIED],
        "certified_with_warnings_count": classification_counts[
            CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS
        ],
        "not_certified_count": classification_counts[CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED],
        "blocked_count": classification_counts[CERTIFICATION_CLASSIFICATION_BLOCKED],
        "unsupported_count": classification_counts[CERTIFICATION_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[CERTIFICATION_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[CERTIFICATION_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[CERTIFICATION_CLASSIFICATION_INCOMPLETE],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_counts,
        "guarantee_category_counts": guarantee_counts,
        "visibility_category_counts": visibility_counts,
        "replay_continuity_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_REPLAY],
        "rollback_continuity_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_ROLLBACK],
        "provenance_continuity_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_PROVENANCE],
        "explainability_continuity_guarantee_count": guarantee_counts[
            CERTIFICATION_GUARANTEE_EXPLAINABILITY
        ],
        "visibility_continuity_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_VISIBILITY],
        "integrity_continuity_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_INTEGRITY],
        "non_execution_continuity_guarantee_count": guarantee_counts[
            CERTIFICATION_GUARANTEE_NON_EXECUTION
        ],
        "recommendation_ranking_scoring_selection_non_capability_guarantee_count": guarantee_counts[
            CERTIFICATION_GUARANTEE_NON_RRSS
        ],
        "mutation_non_capability_guarantee_count": guarantee_counts[CERTIFICATION_GUARANTEE_NON_MUTATION],
        "hidden_finding_count": report.summary.hidden_finding_count,
        "hidden_risk_count": report.summary.hidden_risk_count,
        "hidden_non_safe_state_count": report.summary.hidden_non_safe_state_count,
        "execution_boundary_leakage_count": report.summary.execution_boundary_leakage_count,
        "recommendation_leakage_count": report.summary.recommendation_leakage_count,
        "ranking_leakage_count": report.summary.ranking_leakage_count,
        "scoring_leakage_count": report.summary.scoring_leakage_count,
        "selection_leakage_count": report.summary.selection_leakage_count,
        "mutation_leakage_count": report.summary.mutation_leakage_count,
        "hidden_finding_record_count": hidden_finding_record_count,
        "hidden_guarantee_record_count": hidden_guarantee_record_count,
        "hidden_visibility_record_count": hidden_visibility_record_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "guarantee_not_visible_count": guarantee_not_visible_count,
        "visibility_not_fail_visible_count": visibility_not_fail_visible_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "report_capability_leakage_count": report_capability_leakage_count,
        "replay_safe_certification_finding_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_certification_finding_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_certification_finding_count": sum(
            1 for finding in report.findings if finding.provenance_preserved
        ),
        "explainability_safe_certification_finding_count": sum(
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
        "visibility_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.visibility_continuity_preserved
        ),
        "integrity_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.integrity_continuity_preserved
        ),
        "non_execution_continuity_preserved_count": sum(
            1 for continuity in report.continuities if continuity.non_execution_continuity_preserved
        ),
        "non_execution_confirmation": report.non_executable
        and report_capability_leakage_count == 0
        and evidence_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
        "non_approval_confirmation": report.approval_enabled is False
        and report.remediation_enabled is False
        and report.repair_enabled is False
        and report.automatic_remediation_enabled is False
        and report.automatic_repair_enabled is False
        and report.silent_correction_enabled is False
        and report.hidden_fallback_enabled is False,
        "non_selective_confirmation": report.recommendation_enabled is False
        and report.ranking_enabled is False
        and report.scoring_enabled is False
        and report.selection_enabled is False
        and report.prioritization_enabled is False
        and report.weighted_scoring_enabled is False
        and guarantee_not_visible_count == 0
        and finding_not_fail_visible_count == 0
        and visibility_not_fail_visible_count == 0,
    }


def validate_transition_certification_serialization_guarantees(report: TransitionCertificationReport) -> dict[str, Any]:
    serialization = validate_transition_certification_serialization_stability(report)
    hashing = validate_transition_certification_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "certification_hash": hashing["first_hash"],
    }
