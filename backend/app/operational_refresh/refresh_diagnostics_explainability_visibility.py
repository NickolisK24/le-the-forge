"""Fail-visible visibility helpers for v4.1 diagnostics explainability."""

from __future__ import annotations

from .refresh_diagnostics_explainability_models import (
    DIAGNOSTIC_LAYERS,
    DIAGNOSTIC_SEVERITY_BLOCKED,
    DIAGNOSTIC_SEVERITY_INFO,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
    DIAGNOSTIC_SEVERITY_WARNING,
    DIAGNOSTIC_STATE_BLOCKED,
    DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT,
    DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY,
    DIAGNOSTIC_STATE_MISSING_COVERAGE,
    DIAGNOSTIC_STATE_PROHIBITED_DOMAIN,
    DIAGNOSTIC_STATE_STALE,
    DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER,
    DIAGNOSTIC_STATE_VISIBLE,
    DIAGNOSTIC_STATES,
    EXPLANATION_CATEGORIES,
    EXPLANATION_STATE_BLOCKED,
    EXPLANATION_STATE_CROSS_LAYER_CONFLICT,
    EXPLANATION_STATE_INCONSISTENT_CATEGORY,
    EXPLANATION_STATE_MISSING_COVERAGE,
    EXPLANATION_STATE_PROHIBITED_DOMAIN,
    EXPLANATION_STATE_STALE,
    EXPLANATION_STATE_UNSUPPORTED_PROVIDER,
    EXPLANATION_STATE_VISIBLE,
    EXPLANATION_STATES,
    FAIL_VISIBLE_DIAGNOSTIC_STATES,
    FAIL_VISIBLE_EXPLANATION_STATES,
    PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS,
    RefreshDiagnosticSummary,
    RefreshDiagnosticsExplainability,
    RefreshExplanationSummary,
    default_refresh_diagnostic_summaries,
    default_refresh_diagnostics_explainability,
    default_refresh_explanation_summaries,
)


VALID_SEVERITIES: tuple[str, ...] = (
    DIAGNOSTIC_SEVERITY_INFO,
    DIAGNOSTIC_SEVERITY_WARNING,
    DIAGNOSTIC_SEVERITY_BLOCKED,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
)


def count_diagnostic_states(summaries: tuple[RefreshDiagnosticSummary, ...] | list[RefreshDiagnosticSummary]) -> dict[str, int]:
    counts = {state: 0 for state in DIAGNOSTIC_STATES}
    counts["invalid"] = 0
    for summary in summaries:
        if summary.state in counts:
            counts[summary.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_explanation_states(
    summaries: tuple[RefreshExplanationSummary, ...] | list[RefreshExplanationSummary],
) -> dict[str, int]:
    counts = {state: 0 for state in EXPLANATION_STATES}
    counts["invalid"] = 0
    for summary in summaries:
        if summary.state in counts:
            counts[summary.state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_diagnostic_ids(
    summaries: tuple[RefreshDiagnosticSummary, ...] | list[RefreshDiagnosticSummary],
) -> tuple[str, ...]:
    return tuple(summary.diagnostic_id for summary in summaries if summary.state in FAIL_VISIBLE_DIAGNOSTIC_STATES and summary.fail_visible)


def fail_visible_explanation_ids(
    summaries: tuple[RefreshExplanationSummary, ...] | list[RefreshExplanationSummary],
) -> tuple[str, ...]:
    return tuple(
        summary.explanation_id for summary in summaries if summary.state in FAIL_VISIBLE_EXPLANATION_STATES and summary.fail_visible
    )


def _diagnostic_action_semantics_enabled(summary: RefreshDiagnosticSummary) -> bool:
    return (
        summary.remediation_enabled
        or summary.automatic_correction_enabled
        or summary.recommendation_enabled
        or summary.ranking_enabled
        or summary.scoring_enabled
        or summary.selection_enabled
        or summary.approval_enabled
        or summary.authorization_enabled
        or summary.refresh_execution_enabled
        or summary.orchestration_enabled
        or summary.planner_integration_enabled
        or summary.production_consumption_enabled
        or summary.runtime_mutation_enabled
    )


def _explanation_action_semantics_enabled(summary: RefreshExplanationSummary) -> bool:
    return (
        summary.remediation_enabled
        or summary.automatic_correction_enabled
        or summary.recommendation_enabled
        or summary.ranking_enabled
        or summary.scoring_enabled
        or summary.selection_enabled
        or summary.approval_enabled
        or summary.authorization_enabled
        or summary.refresh_execution_enabled
        or summary.orchestration_enabled
        or summary.planner_integration_enabled
        or summary.production_consumption_enabled
        or summary.runtime_mutation_enabled
    )


def validate_refresh_diagnostics_explainability_visibility(
    payload: RefreshDiagnosticsExplainability,
) -> dict[str, object]:
    diagnostic_counts = count_diagnostic_states(payload.diagnostic_summaries)
    explanation_counts = count_explanation_states(payload.explanation_summaries)
    diagnostics_by_layer = {
        layer: tuple(summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.source_layer == layer)
        for layer in DIAGNOSTIC_LAYERS
    }
    visible_diagnostics_by_layer = {
        layer: tuple(
            summary.diagnostic_id
            for summary in payload.diagnostic_summaries
            if summary.source_layer == layer and summary.state == DIAGNOSTIC_STATE_VISIBLE
        )
        for layer in DIAGNOSTIC_LAYERS
    }
    categories_present = set(summary.category for summary in payload.explanation_summaries)
    diagnostic_severities_valid = all(summary.severity in VALID_SEVERITIES for summary in payload.diagnostic_summaries)
    explanation_severities_valid = all(summary.severity in VALID_SEVERITIES for summary in payload.explanation_summaries)
    explanation_categories_valid = categories_present.issubset(set(EXPLANATION_CATEGORIES))
    all_categories_visible = set(EXPLANATION_CATEGORIES).issubset(categories_present)
    diagnostic = payload.diagnostic_aggregation
    explanation = payload.explanation_aggregation
    integrity = payload.integrity_boundary
    missing_diagnostics = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_MISSING_COVERAGE
    )
    inconsistent_severities = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY
    )
    unsupported_diagnostics = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER
    )
    prohibited_diagnostics = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_PROHIBITED_DOMAIN
    )
    blocked_diagnostics = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_BLOCKED
    )
    stale_diagnostics = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_STALE
    )
    diagnostic_conflicts = tuple(
        summary.diagnostic_id for summary in payload.diagnostic_summaries if summary.state == DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT
    )
    missing_explanations = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_MISSING_COVERAGE
    )
    inconsistent_categories = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_INCONSISTENT_CATEGORY
    )
    unsupported_explanations = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_UNSUPPORTED_PROVIDER
    )
    prohibited_explanations = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_PROHIBITED_DOMAIN
    )
    blocked_explanations = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_BLOCKED
    )
    stale_explanations = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_STALE
    )
    explanation_conflicts = tuple(
        summary.explanation_id for summary in payload.explanation_summaries if summary.state == EXPLANATION_STATE_CROSS_LAYER_CONFLICT
    )
    hidden_diagnostic_count = sum(1 for summary in payload.diagnostic_summaries if summary.hidden)
    hidden_explanation_count = sum(1 for summary in payload.explanation_summaries if summary.hidden)
    diagnostic_action_count = sum(1 for summary in payload.diagnostic_summaries if _diagnostic_action_semantics_enabled(summary))
    explanation_action_count = sum(1 for summary in payload.explanation_summaries if _explanation_action_semantics_enabled(summary))
    prohibited_domains_visible = set(PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS).issubset(
        set(integrity.prohibited_diagnostic_domains)
    ) and set(PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS).issubset(set(integrity.prohibited_explanation_domains))
    visibility_failures = [
        any(not visible_diagnostics_by_layer[layer] for layer in DIAGNOSTIC_LAYERS),
        bool(set(missing_diagnostics) - set(diagnostic.missing_diagnostic_coverage_ids)),
        bool(set(inconsistent_severities) - set(diagnostic.inconsistent_severity_ids)),
        bool(set(unsupported_diagnostics) - set(diagnostic.unsupported_diagnostic_provider_ids)),
        bool(set(prohibited_diagnostics) - set(diagnostic.prohibited_diagnostic_domain_ids)),
        bool(set(blocked_diagnostics) - set(diagnostic.blocked_diagnostic_ids)),
        bool(set(stale_diagnostics) - set(diagnostic.stale_diagnostic_ids)),
        bool(set(diagnostic_conflicts) - set(diagnostic.cross_layer_conflict_ids)),
        bool(set(missing_explanations) - set(explanation.missing_explanation_coverage_ids)),
        bool(set(inconsistent_categories) - set(explanation.inconsistent_category_ids)),
        bool(set(unsupported_explanations) - set(explanation.unsupported_explanation_provider_ids)),
        bool(set(prohibited_explanations) - set(explanation.prohibited_explanation_domain_ids)),
        bool(set(blocked_explanations) - set(explanation.blocked_explanation_ids)),
        bool(set(stale_explanations) - set(explanation.stale_explanation_ids)),
        bool(set(explanation_conflicts) - set(explanation.cross_layer_conflict_ids)),
        not diagnostic_severities_valid,
        not explanation_severities_valid,
        not explanation_categories_valid,
        not all_categories_visible,
        not prohibited_domains_visible,
    ]
    return {
        "diagnostic_state_counts": diagnostic_counts,
        "explanation_state_counts": explanation_counts,
        "diagnostics_by_layer": {layer: len(diagnostics_by_layer[layer]) for layer in DIAGNOSTIC_LAYERS},
        "visible_diagnostics_by_layer": {layer: len(visible_diagnostics_by_layer[layer]) for layer in DIAGNOSTIC_LAYERS},
        "fail_visible_diagnostic_count": len(fail_visible_diagnostic_ids(payload.diagnostic_summaries)),
        "fail_visible_explanation_count": len(fail_visible_explanation_ids(payload.explanation_summaries)),
        "missing_diagnostic_coverage_count": len(diagnostic.missing_diagnostic_coverage_ids),
        "missing_explanation_coverage_count": len(explanation.missing_explanation_coverage_ids),
        "inconsistent_diagnostic_severity_count": len(diagnostic.inconsistent_severity_ids),
        "inconsistent_explanation_category_count": len(explanation.inconsistent_category_ids),
        "unsupported_diagnostic_provider_count": len(diagnostic.unsupported_diagnostic_provider_ids),
        "unsupported_explanation_provider_count": len(explanation.unsupported_explanation_provider_ids),
        "prohibited_diagnostic_domain_count": len(diagnostic.prohibited_diagnostic_domain_ids),
        "prohibited_explanation_domain_count": len(explanation.prohibited_explanation_domain_ids),
        "blocked_diagnostic_count": len(diagnostic.blocked_diagnostic_ids),
        "blocked_explanation_count": len(explanation.blocked_explanation_ids),
        "stale_diagnostic_count": len(diagnostic.stale_diagnostic_ids),
        "stale_explanation_count": len(explanation.stale_explanation_ids),
        "cross_layer_diagnostic_conflict_count": len(diagnostic.cross_layer_conflict_ids),
        "cross_layer_explanation_conflict_count": len(explanation.cross_layer_conflict_ids),
        "limitation_explanation_count": len(explanation.limitation_explanation_ids),
        "explanation_category_count": len(categories_present),
        "prohibited_domain_visibility_count": len(integrity.prohibited_diagnostic_domains),
        "hidden_diagnostic_count": hidden_diagnostic_count,
        "hidden_explanation_count": hidden_explanation_count,
        "diagnostic_action_semantics_count": diagnostic_action_count,
        "explanation_action_semantics_count": explanation_action_count,
        "invalid_diagnostic_state_count": diagnostic_counts["invalid"],
        "invalid_explanation_state_count": explanation_counts["invalid"],
        "diagnostic_layer_coverage_complete": all(visible_diagnostics_by_layer[layer] for layer in DIAGNOSTIC_LAYERS),
        "explanation_category_coverage_complete": all_categories_visible,
        "diagnostic_severities_valid": diagnostic_severities_valid,
        "explanation_severities_valid": explanation_severities_valid,
        "explanation_categories_valid": explanation_categories_valid,
        "missing_diagnostic_coverage_visible": not bool(set(missing_diagnostics) - set(diagnostic.missing_diagnostic_coverage_ids)),
        "missing_explanation_coverage_visible": not bool(
            set(missing_explanations) - set(explanation.missing_explanation_coverage_ids)
        ),
        "unsupported_state_explanations_visible": bool(explanation.unsupported_explanation_ids),
        "blocked_state_explanations_visible": bool(explanation.blocked_explanation_ids),
        "prohibited_state_explanations_visible": bool(explanation.prohibited_explanation_ids),
        "limitation_explanations_visible": bool(explanation.limitation_explanation_ids),
        "cross_layer_diagnostic_aggregation_visible": bool(diagnostic.cross_layer_conflict_ids),
        "cross_layer_explanation_aggregation_visible": bool(explanation.cross_layer_conflict_ids),
        "prohibited_domains_visible": prohibited_domains_visible,
        "visibility_is_descriptive_only": all(
            getattr(record, "descriptive_only", False)
            for record in (
                *payload.diagnostic_summaries,
                *payload.explanation_summaries,
                payload.diagnostic_aggregation,
                payload.explanation_aggregation,
                payload.continuity_metadata,
                payload.integrity_boundary,
                payload.governance,
            )
        ),
        "valid": (
            not any(visibility_failures)
            and hidden_diagnostic_count == 0
            and hidden_explanation_count == 0
            and diagnostic_action_count == 0
            and explanation_action_count == 0
            and diagnostic_counts["invalid"] == 0
            and explanation_counts["invalid"] == 0
        ),
    }


def build_default_refresh_diagnostic_summaries() -> tuple[RefreshDiagnosticSummary, ...]:
    return default_refresh_diagnostic_summaries()


def build_default_refresh_explanation_summaries() -> tuple[RefreshExplanationSummary, ...]:
    return default_refresh_explanation_summaries()


def build_default_refresh_diagnostics_explainability() -> RefreshDiagnosticsExplainability:
    return default_refresh_diagnostics_explainability()
