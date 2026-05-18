"""Visibility helpers for v4.5B.3 explainability surfaces."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_3_explainability_surface_models import (
    CONTINUITY_EXPLANATION_TYPES,
    EVIDENCE_TO_EXPLANATION_MAPPING_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    EXPLANATION_SUMMARY_TYPES,
    LIMITATION_EXPLANATION_TYPES,
    SUPPORT_STATE_EXPLANATION_TYPES,
    TRUST_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_EXPLANATION_TYPES,
    ContinuityExplanationVisibility,
    EvidenceToExplanationMapping,
    ExplainabilitySurfaceIntelligence,
    ExplainabilitySurfaceRecord,
    ExplanationDiagnosticRecord,
    ExplanationSummaryRecord,
    LimitationExplanationVisibility,
    PublicTrustExplanationVisibility,
    SupportStateExplanationSurface,
    UnsupportedExplanationOperationalStateVisibility,
    UnsupportedStateExplanationVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_support_state_explanation_types(
    records: Iterable[SupportStateExplanationSurface],
) -> dict[str, int]:
    return _count(
        (record.explanation_type for record in records),
        SUPPORT_STATE_EXPLANATION_TYPES,
    )


def count_evidence_mapping_types(
    records: Iterable[EvidenceToExplanationMapping],
) -> dict[str, int]:
    return _count(
        (record.mapping_type for record in records),
        EVIDENCE_TO_EXPLANATION_MAPPING_TYPES,
    )


def count_limitation_explanation_types(
    records: Iterable[LimitationExplanationVisibility],
) -> dict[str, int]:
    return _count((record.limitation_type for record in records), LIMITATION_EXPLANATION_TYPES)


def count_trust_explanation_types(
    records: Iterable[PublicTrustExplanationVisibility],
) -> dict[str, int]:
    return _count((record.trust_explanation_type for record in records), TRUST_EXPLANATION_TYPES)


def count_continuity_explanation_types(
    records: Iterable[ContinuityExplanationVisibility],
) -> dict[str, int]:
    return _count(
        (record.continuity_explanation_type for record in records),
        CONTINUITY_EXPLANATION_TYPES,
    )


def count_unsupported_state_explanation_types(
    records: Iterable[UnsupportedStateExplanationVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state_type for record in records),
        UNSUPPORTED_STATE_EXPLANATION_TYPES,
    )


def count_explanation_summary_types(
    records: Iterable[ExplanationSummaryRecord],
) -> dict[str, int]:
    return _count((record.summary_type for record in records), EXPLANATION_SUMMARY_TYPES)


def count_explanation_diagnostic_types(
    records: Iterable[ExplanationDiagnosticRecord],
) -> dict[str, int]:
    return _count((record.diagnostic_type for record in records), EXPLANATION_DIAGNOSTIC_TYPES)


def count_unsupported_operational_states(
    records: Iterable[UnsupportedExplanationOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    )


def explanation_surface_summary(
    records: Iterable[ExplainabilitySurfaceRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "surface_record_id": record.surface_record_id,
            "explainability_surface_id": record.explainability_surface_id,
            "explanation_summary_id": record.explanation_summary_id,
            "support_visibility_reference_id": record.support_visibility_reference_id,
            "evidence_reference_id": record.evidence_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "trust_summary_reference_id": record.trust_summary_reference_id,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "explainability_authority_enabled": (
                record.explainability_authority_enabled
            ),
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.surface_record_id),
        )
    ]


def support_state_explanation_summary(
    records: Iterable[SupportStateExplanationSurface],
) -> list[dict[str, Any]]:
    return [
        {
            "support_state_explanation_id": record.support_state_explanation_id,
            "explanation_type": record.explanation_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "ranking_enabled": record.ranking_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "correctness_guarantee_enabled": record.correctness_guarantee_enabled,
            "operational_readiness_enabled": record.operational_readiness_enabled,
            "execution_safety_enabled": record.execution_safety_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_state_explanation_id),
        )
    ]


def evidence_to_explanation_mapping_summary(
    records: Iterable[EvidenceToExplanationMapping],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_mapping_id": record.evidence_mapping_id,
            "mapping_type": record.mapping_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "explanation_reference_ids": _ordered_ids(record.explanation_reference_ids),
            "descriptive_only": record.descriptive_only,
            "replay_safe": record.replay_safe,
            "provenance_safe": record.provenance_safe,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_mapping_id),
        )
    ]


def limitation_explanation_summary(
    records: Iterable[LimitationExplanationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "limitation_explanation_id": record.limitation_explanation_id,
            "limitation_type": record.limitation_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "operational_fallback_enabled": record.operational_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.limitation_explanation_id),
        )
    ]


def trust_explanation_summary(
    records: Iterable[PublicTrustExplanationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "trust_explanation_id": record.trust_explanation_id,
            "trust_explanation_type": record.trust_explanation_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "execution_semantics_enabled": record.execution_semantics_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.trust_explanation_id),
        )
    ]


def continuity_explanation_summary(
    records: Iterable[ContinuityExplanationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_explanation_id": record.continuity_explanation_id,
            "continuity_explanation_type": record.continuity_explanation_type,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.continuity_explanation_id),
        )
    ]


def unsupported_state_explanation_summary(
    records: Iterable[UnsupportedStateExplanationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_explanation_id": record.unsupported_explanation_id,
            "unsupported_state_type": record.unsupported_state_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "suppression_enabled": record.suppression_enabled,
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.unsupported_explanation_id),
        )
    ]


def explanation_summary_visibility(
    records: Iterable[ExplanationSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "explanation_summary_record_id": record.explanation_summary_record_id,
            "explanation_summary_id": record.explanation_summary_id,
            "summary_type": record.summary_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "summary_state": record.summary_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.explanation_summary_record_id,
            ),
        )
    ]


def explanation_diagnostic_summary(
    records: Iterable[ExplanationDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "diagnostic_type": record.diagnostic_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "message": record.message,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "silent_fallback_enabled": record.silent_fallback_enabled,
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_operational_state_summary(
    records: Iterable[UnsupportedExplanationOperationalStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_enabled": record.operational_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "automated_correction_enabled": record.automated_correction_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_explainability_surfaces(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    support_counts = count_support_state_explanation_types(
        intelligence.support_state_explanations
    )
    mapping_counts = count_evidence_mapping_types(
        intelligence.evidence_to_explanation_mappings
    )
    limitation_counts = count_limitation_explanation_types(
        intelligence.limitation_explanations
    )
    trust_counts = count_trust_explanation_types(intelligence.trust_explanations)
    continuity_counts = count_continuity_explanation_types(
        intelligence.continuity_explanations
    )
    unsupported_counts = count_unsupported_state_explanation_types(
        intelligence.unsupported_state_explanations
    )
    summary_counts = count_explanation_summary_types(
        intelligence.explanation_summaries
    )
    diagnostic_counts = count_explanation_diagnostic_types(
        intelligence.explanation_diagnostics
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_support_state_explanations": sorted(
            key for key, value in support_counts.items() if value < 1
        ),
        "missing_evidence_mappings": sorted(
            key for key, value in mapping_counts.items() if value < 1
        ),
        "missing_limitation_explanations": sorted(
            key for key, value in limitation_counts.items() if value < 1
        ),
        "missing_trust_explanations": sorted(
            key for key, value in trust_counts.items() if value < 1
        ),
        "missing_continuity_explanations": sorted(
            key for key, value in continuity_counts.items() if value < 1
        ),
        "missing_unsupported_state_explanations": sorted(
            key for key, value in unsupported_counts.items() if value < 1
        ),
        "missing_summaries": sorted(
            key for key, value in summary_counts.items() if value < 1
        ),
        "missing_diagnostics": sorted(
            key for key, value in diagnostic_counts.items() if value < 1
        ),
        "missing_unsupported_operational_states": sorted(
            key for key, value in unsupported_operational_counts.items() if value < 1
        ),
    }
    return {
        "valid": not any(missing.values()),
        "support_counts": support_counts,
        "mapping_counts": mapping_counts,
        "limitation_counts": limitation_counts,
        "trust_counts": trust_counts,
        "continuity_counts": continuity_counts,
        "unsupported_counts": unsupported_counts,
        "summary_counts": summary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_explainability_surface_summary(
    intelligence: ExplainabilitySurfaceIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "explainability_surface_statement": (
            intelligence.explainability_surface_statement
        ),
        "explainability_visibility_non_authority_statement": (
            intelligence.explainability_visibility_non_authority_statement
        ),
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "explainability_authorization_enabled": (
            intelligence.explainability_authorization_enabled
        ),
        "explainability_approval_enabled": intelligence.explainability_approval_enabled,
        "explainability_ranking_enabled": intelligence.explainability_ranking_enabled,
        "explainability_recommendation_enabled": (
            intelligence.explainability_recommendation_enabled
        ),
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
