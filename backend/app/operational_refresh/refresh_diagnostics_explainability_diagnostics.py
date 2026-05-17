"""Deterministic diagnostics for v4.1 refresh diagnostics explainability."""

from __future__ import annotations

from typing import Any

from .refresh_diagnostics_explainability_continuity import certify_diagnostics_explainability_continuity
from .refresh_diagnostics_explainability_hashing import (
    hash_diagnostics_continuity,
    hash_diagnostics_integrity,
    hash_refresh_diagnostics_explainability,
)
from .refresh_diagnostics_explainability_integrity import enabled_diagnostics_explainability_capability_flags
from .refresh_diagnostics_explainability_models import (
    RefreshDiagnosticsExplainability,
    default_refresh_diagnostics_explainability,
)
from .refresh_diagnostics_explainability_visibility import validate_refresh_diagnostics_explainability_visibility


def build_unified_refresh_diagnostics(payload: RefreshDiagnosticsExplainability | None = None) -> dict[str, Any]:
    source = payload or default_refresh_diagnostics_explainability()
    visibility = validate_refresh_diagnostics_explainability_visibility(source)
    enabled_flags = enabled_diagnostics_explainability_capability_flags(source)
    return {
        "diagnostics_explainability_hash": hash_refresh_diagnostics_explainability(source),
        "continuity_hash": hash_diagnostics_continuity(source.continuity_metadata),
        "visibility_validation": visibility,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "diagnostic_ids": sorted(summary.diagnostic_id for summary in source.diagnostic_summaries),
        "manifest_diagnostic_ids": sorted(source.diagnostic_aggregation.manifest_diagnostic_ids),
        "dependency_diagnostic_ids": sorted(source.diagnostic_aggregation.dependency_diagnostic_ids),
        "lineage_diagnostic_ids": sorted(source.diagnostic_aggregation.lineage_diagnostic_ids),
        "schema_diagnostic_ids": sorted(source.diagnostic_aggregation.schema_diagnostic_ids),
        "sequencing_diagnostic_ids": sorted(source.diagnostic_aggregation.sequencing_diagnostic_ids),
        "drift_diagnostic_ids": sorted(source.diagnostic_aggregation.drift_diagnostic_ids),
        "replay_diagnostic_ids": sorted(source.diagnostic_aggregation.replay_diagnostic_ids),
        "rollback_diagnostic_ids": sorted(source.diagnostic_aggregation.rollback_diagnostic_ids),
        "missing_diagnostic_coverage_ids": sorted(source.diagnostic_aggregation.missing_diagnostic_coverage_ids),
        "inconsistent_severity_ids": sorted(source.diagnostic_aggregation.inconsistent_severity_ids),
        "unsupported_diagnostic_provider_ids": sorted(source.diagnostic_aggregation.unsupported_diagnostic_provider_ids),
        "prohibited_diagnostic_domain_ids": sorted(source.diagnostic_aggregation.prohibited_diagnostic_domain_ids),
        "blocked_diagnostic_ids": sorted(source.diagnostic_aggregation.blocked_diagnostic_ids),
        "stale_diagnostic_ids": sorted(source.diagnostic_aggregation.stale_diagnostic_ids),
        "cross_layer_diagnostic_conflict_ids": sorted(source.diagnostic_aggregation.cross_layer_conflict_ids),
        "diagnostics_are_descriptive_only": source.diagnostic_aggregation.descriptive_only,
        "remediation_absent": not source.diagnostic_aggregation.remediation_enabled,
        "automatic_correction_absent": not source.diagnostic_aggregation.automatic_correction_enabled,
        "recommendation_absent": not source.diagnostic_aggregation.recommendation_enabled,
    }


def build_unified_refresh_explainability(payload: RefreshDiagnosticsExplainability | None = None) -> dict[str, Any]:
    source = payload or default_refresh_diagnostics_explainability()
    visibility = validate_refresh_diagnostics_explainability_visibility(source)
    enabled_flags = enabled_diagnostics_explainability_capability_flags(source)
    return {
        "diagnostics_explainability_hash": hash_refresh_diagnostics_explainability(source),
        "integrity_hash": hash_diagnostics_integrity(source.integrity_boundary),
        "visibility_validation": visibility,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "explanation_ids": sorted(source.explanation_aggregation.explanation_ids),
        "unsupported_explanation_ids": sorted(source.explanation_aggregation.unsupported_explanation_ids),
        "blocked_explanation_ids": sorted(source.explanation_aggregation.blocked_explanation_ids),
        "prohibited_explanation_ids": sorted(source.explanation_aggregation.prohibited_explanation_ids),
        "limitation_explanation_ids": sorted(source.explanation_aggregation.limitation_explanation_ids),
        "missing_explanation_coverage_ids": sorted(source.explanation_aggregation.missing_explanation_coverage_ids),
        "inconsistent_category_ids": sorted(source.explanation_aggregation.inconsistent_category_ids),
        "unsupported_explanation_provider_ids": sorted(source.explanation_aggregation.unsupported_explanation_provider_ids),
        "prohibited_explanation_domain_ids": sorted(source.explanation_aggregation.prohibited_explanation_domain_ids),
        "stale_explanation_ids": sorted(source.explanation_aggregation.stale_explanation_ids),
        "cross_layer_explanation_conflict_ids": sorted(source.explanation_aggregation.cross_layer_conflict_ids),
        "explanations_are_descriptive_only": source.explanation_aggregation.descriptive_only,
        "recommendation_absent": not source.explanation_aggregation.recommendation_enabled,
        "ranking_absent": not source.explanation_aggregation.ranking_enabled,
        "scoring_absent": not source.explanation_aggregation.scoring_enabled,
        "selection_absent": not source.explanation_aggregation.selection_enabled,
        "approval_absent": not source.explanation_aggregation.approval_enabled,
        "authorization_absent": not source.explanation_aggregation.authorization_enabled,
    }


def build_refresh_diagnostics_explainability_diagnostics(
    payload: RefreshDiagnosticsExplainability | None = None,
) -> dict[str, Any]:
    source = payload or default_refresh_diagnostics_explainability()
    visibility = validate_refresh_diagnostics_explainability_visibility(source)
    continuity = certify_diagnostics_explainability_continuity(source)
    enabled_flags = enabled_diagnostics_explainability_capability_flags(source)
    diagnostics = build_unified_refresh_diagnostics(source)
    explainability = build_unified_refresh_explainability(source)
    return {
        "diagnostics_explainability_hash": hash_refresh_diagnostics_explainability(source),
        "continuity_hash": hash_diagnostics_continuity(source.continuity_metadata),
        "integrity_hash": hash_diagnostics_integrity(source.integrity_boundary),
        "visibility_validation": visibility,
        "continuity_certification": continuity,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "unified_diagnostics": diagnostics,
        "unified_explainability": explainability,
        "prohibited_diagnostic_domains": sorted(source.integrity_boundary.prohibited_diagnostic_domains),
        "prohibited_explanation_domains": sorted(source.integrity_boundary.prohibited_explanation_domains),
        "explicit_limitations": sorted(source.governance.explicit_limitations),
        "explicit_prohibitions": sorted(source.governance.explicit_prohibitions),
        "diagnostics_visible": visibility["diagnostic_layer_coverage_complete"],
        "explanations_visible": visibility["explanation_category_coverage_complete"],
        "diagnostics_are_descriptive_only": source.diagnostic_aggregation.descriptive_only,
        "explanations_are_descriptive_only": source.explanation_aggregation.descriptive_only,
        "remediation_absent": not source.remediation_enabled,
        "automatic_correction_absent": not source.automatic_correction_enabled,
        "recommendation_absent": not source.recommendation_enabled,
        "ranking_absent": not source.ranking_enabled,
        "scoring_absent": not source.scoring_enabled,
        "selection_absent": not source.selection_enabled,
        "approval_absent": not source.approval_enabled,
        "authorization_absent": not source.authorization_enabled,
        "orchestration_absent": not source.orchestration_enabled,
        "execution_absent": not source.refresh_execution_enabled,
        "planner_integration_absent": not source.planner_integration_enabled,
        "production_consumption_absent": not source.production_consumption_enabled,
        "fail_visible_warning_count": (
            visibility["fail_visible_diagnostic_count"]
            + visibility["fail_visible_explanation_count"]
            + visibility["prohibited_domain_visibility_count"]
            + visibility["missing_diagnostic_coverage_count"]
            + visibility["missing_explanation_coverage_count"]
            + visibility["blocked_diagnostic_count"]
            + visibility["blocked_explanation_count"]
        ),
    }
