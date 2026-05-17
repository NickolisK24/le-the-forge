"""Deterministic validation for v3.9 transition scenario intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_scenario_models import (
    NON_MODELED_SCENARIO_CLASSIFICATIONS,
    PROHIBITED_SCENARIO_CAPABILITIES,
    SCENARIO_CHOICE_PROHIBITED_CAPABILITIES,
    SCENARIO_CLASSIFICATION_BLOCKED,
    SCENARIO_CLASSIFICATION_INCOMPLETE,
    SCENARIO_CLASSIFICATION_MODELED,
    SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
    SCENARIO_CLASSIFICATION_PROHIBITED,
    SCENARIO_CLASSIFICATION_UNKNOWN,
    SCENARIO_CLASSIFICATION_UNMODELED,
    SCENARIO_CLASSIFICATION_UNSUPPORTED,
    SCENARIO_CLASSIFICATIONS,
    SCENARIO_FINDING_CATEGORIES,
    SCENARIO_RISK_CATEGORIES,
    SCENARIO_RISK_GOVERNANCE,
    SCENARIO_RISK_MISSING_EVIDENCE,
    SCENARIO_RISK_UNCERTAINTY,
    TransitionScenarioReport,
)
from .transition_scenario_serialization import (
    validate_transition_scenario_hash_stability,
    validate_transition_scenario_serialization_stability,
)


def count_transition_scenario_classifications(report: TransitionScenarioReport) -> dict[str, int]:
    counts = Counter(visibility.classification for visibility in report.visibilities)
    return {classification: counts.get(classification, 0) for classification in SCENARIO_CLASSIFICATIONS}


def count_transition_scenario_finding_categories(report: TransitionScenarioReport) -> dict[str, int]:
    counts = Counter(finding.finding_category for finding in report.findings)
    return {category: counts.get(category, 0) for category in SCENARIO_FINDING_CATEGORIES}


def count_transition_scenario_risk_categories(report: TransitionScenarioReport) -> dict[str, int]:
    counts = Counter(risk.risk_category for risk in report.risks)
    return {category: counts.get(category, 0) for category in SCENARIO_RISK_CATEGORIES}


def validate_transition_scenario_report(report: TransitionScenarioReport) -> dict[str, Any]:
    classification_counts = count_transition_scenario_classifications(report)
    finding_category_counts = count_transition_scenario_finding_categories(report)
    risk_category_counts = count_transition_scenario_risk_categories(report)
    invalid_classification_count = sum(
        1 for visibility in report.visibilities if visibility.classification not in SCENARIO_CLASSIFICATIONS
    )
    invalid_finding_category_count = sum(
        1 for finding in report.findings if finding.finding_category not in SCENARIO_FINDING_CATEGORIES
    )
    invalid_risk_category_count = sum(1 for risk in report.risks if risk.risk_category not in SCENARIO_RISK_CATEGORIES)
    hidden_scenario_finding_count = sum(1 for finding in report.findings if finding.hidden)
    hidden_risk_count = sum(1 for risk in report.risks if risk.hidden)
    hidden_variant_count = sum(1 for variant in report.variants if variant.hidden)
    hidden_comparison_count = sum(1 for comparison in report.comparisons if comparison.hidden)
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
    risk_not_fail_visible_count = sum(
        1
        for risk in report.risks
        if (
            not risk.fail_visible
            or not risk.description
            or not risk.evidence_reference
            or not risk.provenance_reference
            or not risk.continuity_reference
            or not risk.explainability_message
            or not risk.descriptive_only
            or risk.score_assigned
            or risk.ranking_assigned
            or risk.recommendation_made
            or risk.selection_made
        )
    )
    non_modeled_not_visible_count = sum(
        1
        for visibility in report.visibilities
        if visibility.classification in NON_MODELED_SCENARIO_CLASSIFICATIONS
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
    variant_integrity_violation_count = sum(
        1
        for variant in report.variants
        if not variant.replay_safe
        or not variant.rollback_safe
        or not variant.provenance_preserved
        or not variant.explainability_safe
        or not variant.immutable_variant
        or variant.recommendation_enabled
        or variant.ranking_enabled
        or variant.scoring_enabled
        or variant.selection_enabled
    )
    comparison_selection_violation_count = sum(
        1
        for comparison in report.comparisons
        if not comparison.descriptive_only
        or comparison.winner_selected
        or comparison.recommendation_made
        or comparison.ranking_assigned
        or comparison.scoring_assigned
        or comparison.selection_made
    )
    record_selection_violation_count = sum(
        1
        for record in report.scenario_records
        if record.recommendation_enabled or record.ranking_enabled or record.scoring_enabled or record.selection_enabled
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
        for source in report.scenario_inputs
        for capability in source.requested_capabilities
        if capability in PROHIBITED_SCENARIO_CAPABILITIES
    )
    recommendation_ranking_scoring_selection_violation_count = sum(
        1
        for source in report.scenario_inputs
        for capability in source.requested_capabilities
        if capability in SCENARIO_CHOICE_PROHIBITED_CAPABILITIES
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
            invalid_risk_category_count,
            hidden_scenario_finding_count,
            hidden_risk_count,
            hidden_variant_count,
            hidden_comparison_count,
            hidden_visibility_count,
            finding_not_fail_visible_count,
            risk_not_fail_visible_count,
            non_modeled_not_visible_count,
            evidence_integrity_violation_count,
            variant_integrity_violation_count,
            comparison_selection_violation_count,
            record_selection_violation_count,
            continuity_integrity_violation_count,
            report_execution_capability_violation_count,
            0 if report.non_executable else 1,
        )
    )
    return {
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "scenario_input_count": len(report.scenario_inputs),
        "scenario_record_count": len(report.scenario_records),
        "scenario_variant_count": len(report.variants),
        "scenario_comparison_count": len(report.comparisons),
        "scenario_risk_count": len(report.risks),
        "scenario_finding_count": len(report.findings),
        "evidence_record_count": len(report.evidence_records),
        "continuity_record_count": len(report.continuities),
        "visibility_count": len(report.visibilities),
        "modeled_count": classification_counts[SCENARIO_CLASSIFICATION_MODELED],
        "partially_modeled_count": classification_counts[SCENARIO_CLASSIFICATION_PARTIALLY_MODELED],
        "unmodeled_count": classification_counts[SCENARIO_CLASSIFICATION_UNMODELED],
        "blocked_count": classification_counts[SCENARIO_CLASSIFICATION_BLOCKED],
        "unsupported_count": classification_counts[SCENARIO_CLASSIFICATION_UNSUPPORTED],
        "prohibited_count": classification_counts[SCENARIO_CLASSIFICATION_PROHIBITED],
        "unknown_count": classification_counts[SCENARIO_CLASSIFICATION_UNKNOWN],
        "incomplete_count": classification_counts[SCENARIO_CLASSIFICATION_INCOMPLETE],
        "classification_counts": classification_counts,
        "finding_category_counts": finding_category_counts,
        "risk_category_counts": risk_category_counts,
        "governance_risk_count": risk_category_counts[SCENARIO_RISK_GOVERNANCE],
        "uncertainty_risk_count": risk_category_counts[SCENARIO_RISK_UNCERTAINTY],
        "missing_evidence_risk_count": risk_category_counts[SCENARIO_RISK_MISSING_EVIDENCE],
        "hidden_scenario_finding_count": hidden_scenario_finding_count,
        "hidden_risk_count": hidden_risk_count,
        "hidden_variant_count": hidden_variant_count,
        "hidden_comparison_count": hidden_comparison_count,
        "hidden_visibility_count": hidden_visibility_count,
        "finding_not_fail_visible_count": finding_not_fail_visible_count,
        "risk_not_fail_visible_count": risk_not_fail_visible_count,
        "non_modeled_not_visible_count": non_modeled_not_visible_count,
        "invalid_classification_count": invalid_classification_count,
        "invalid_finding_category_count": invalid_finding_category_count,
        "invalid_risk_category_count": invalid_risk_category_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "recommendation_ranking_scoring_selection_violation_count": recommendation_ranking_scoring_selection_violation_count,
        "report_execution_capability_violation_count": report_execution_capability_violation_count,
        "evidence_integrity_violation_count": evidence_integrity_violation_count,
        "variant_integrity_violation_count": variant_integrity_violation_count,
        "comparison_selection_violation_count": comparison_selection_violation_count,
        "record_selection_violation_count": record_selection_violation_count,
        "continuity_integrity_violation_count": continuity_integrity_violation_count,
        "replay_safe_scenario_finding_count": sum(1 for finding in report.findings if finding.replay_safe),
        "rollback_safe_scenario_finding_count": sum(1 for finding in report.findings if finding.rollback_safe),
        "provenance_safe_scenario_finding_count": sum(1 for finding in report.findings if finding.provenance_preserved),
        "explainability_safe_scenario_finding_count": sum(1 for finding in report.findings if finding.explainability_safe),
        "replay_safe_risk_count": sum(1 for risk in report.risks if risk.replay_safe),
        "rollback_safe_risk_count": sum(1 for risk in report.risks if risk.rollback_safe),
        "provenance_safe_risk_count": sum(1 for risk in report.risks if risk.provenance_preserved),
        "explainability_safe_risk_count": sum(1 for risk in report.risks if risk.explainability_safe),
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
        and variant_integrity_violation_count == 0
        and continuity_integrity_violation_count == 0,
        "non_selective_confirmation": report.recommendation_enabled is False
        and report.ranking_enabled is False
        and report.scoring_enabled is False
        and report.selection_enabled is False
        and comparison_selection_violation_count == 0
        and record_selection_violation_count == 0
        and risk_not_fail_visible_count == 0,
    }


def validate_transition_scenario_serialization_guarantees(report: TransitionScenarioReport) -> dict[str, Any]:
    serialization = validate_transition_scenario_serialization_stability(report)
    hashing = validate_transition_scenario_hash_stability(report)
    return {
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "serialization_first_length": serialization["first_length"],
        "serialization_second_length": serialization["second_length"],
        "hash_algorithm": hashing["hash_algorithm"],
        "scenario_hash": hashing["first_hash"],
    }
