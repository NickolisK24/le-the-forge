"""Visibility helpers for v4.5B.2 support status visibility."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_2_support_status_visibility_models import (
    CONTINUITY_SUPPORT_VISIBILITY_TYPES,
    EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES,
    EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES,
    EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES,
    PUBLIC_SUPPORT_SURFACE_TYPES,
    SUPPORT_CLASSIFICATION_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    SUPPORT_SUMMARY_TYPES,
    UNSUPPORTED_SUPPORT_OPERATIONAL_STATES,
    UNSUPPORTED_SUPPORT_STATE_TYPES,
    ContinuitySupportVisibility,
    EvidenceBasedSupportVisibility,
    ExperimentalDeprecatedVisibility,
    ExplainabilitySupportVisibility,
    PublicSupportSurfaceVisibility,
    SupportClassificationVisibility,
    SupportDiagnosticRecord,
    SupportStatusVisibilityIntelligence,
    SupportSummaryRecord,
    SupportVisibilityRecord,
    UnsupportedSupportOperationalStateVisibility,
    UnsupportedSupportStateVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_support_classifications(
    records: Iterable[SupportClassificationVisibility],
) -> dict[str, int]:
    return _count(
        (record.support_classification for record in records),
        SUPPORT_CLASSIFICATION_TYPES,
    )


def count_support_surfaces(
    records: Iterable[PublicSupportSurfaceVisibility],
) -> dict[str, int]:
    return _count((record.support_surface for record in records), PUBLIC_SUPPORT_SURFACE_TYPES)


def count_unsupported_support_states(
    records: Iterable[UnsupportedSupportStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state_type for record in records),
        UNSUPPORTED_SUPPORT_STATE_TYPES,
    )


def count_experimental_deprecated_types(
    records: Iterable[ExperimentalDeprecatedVisibility],
) -> dict[str, int]:
    return _count(
        (record.visibility_type for record in records),
        EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES,
    )


def count_evidence_based_support_types(
    records: Iterable[EvidenceBasedSupportVisibility],
) -> dict[str, int]:
    return _count(
        (record.evidence_support_type for record in records),
        EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES,
    )


def count_explainability_support_types(
    records: Iterable[ExplainabilitySupportVisibility],
) -> dict[str, int]:
    return _count(
        (record.explainability_support_type for record in records),
        EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES,
    )


def count_continuity_support_types(
    records: Iterable[ContinuitySupportVisibility],
) -> dict[str, int]:
    return _count(
        (record.continuity_support_type for record in records),
        CONTINUITY_SUPPORT_VISIBILITY_TYPES,
    )


def count_support_summary_types(
    records: Iterable[SupportSummaryRecord],
) -> dict[str, int]:
    return _count((record.summary_type for record in records), SUPPORT_SUMMARY_TYPES)


def count_support_diagnostic_types(
    records: Iterable[SupportDiagnosticRecord],
) -> dict[str, int]:
    return _count((record.diagnostic_type for record in records), SUPPORT_DIAGNOSTIC_TYPES)


def count_unsupported_operational_states(
    records: Iterable[UnsupportedSupportOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_SUPPORT_OPERATIONAL_STATES,
    )


def support_visibility_summary(
    records: Iterable[SupportVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "support_record_id": record.support_record_id,
            "support_status_id": record.support_status_id,
            "support_summary_id": record.support_summary_id,
            "support_scope_id": record.support_scope_id,
            "support_reference_id": record.support_reference_id,
            "evidence_reference_id": record.evidence_reference_id,
            "explainability_reference_id": record.explainability_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "support_authority_enabled": record.support_authority_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_record_id),
        )
    ]


def support_classification_summary(
    records: Iterable[SupportClassificationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "classification_visibility_id": record.classification_visibility_id,
            "support_classification": record.support_classification,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "operational_approval_enabled": record.operational_approval_enabled,
            "execution_semantics_enabled": record.execution_semantics_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.classification_visibility_id,
            ),
        )
    ]


def support_surface_summary(
    records: Iterable[PublicSupportSurfaceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "surface_visibility_id": record.surface_visibility_id,
            "support_surface": record.support_surface,
            "support_classification": record.support_classification,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.surface_visibility_id),
        )
    ]


def unsupported_state_summary(
    records: Iterable[UnsupportedSupportStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_visibility_id": record.unsupported_visibility_id,
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
            key=lambda item: (item.deterministic_order, item.unsupported_visibility_id),
        )
    ]


def experimental_deprecated_summary(
    records: Iterable[ExperimentalDeprecatedVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "experimental_deprecated_id": record.experimental_deprecated_id,
            "visibility_type": record.visibility_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "automatic_migration_enabled": record.automatic_migration_enabled,
            "operational_fallback_enabled": record.operational_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.experimental_deprecated_id),
        )
    ]


def evidence_based_support_summary(
    records: Iterable[EvidenceBasedSupportVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_support_id": record.evidence_support_id,
            "evidence_support_type": record.evidence_support_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "replay_safe": record.replay_safe,
            "provenance_safe": record.provenance_safe,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "approval_enabled": record.approval_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_support_id),
        )
    ]


def explainability_support_summary(
    records: Iterable[ExplainabilitySupportVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_support_id": record.explainability_support_id,
            "explainability_support_type": record.explainability_support_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.explainability_support_id),
        )
    ]


def continuity_support_summary(
    records: Iterable[ContinuitySupportVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_support_id": record.continuity_support_id,
            "continuity_support_type": record.continuity_support_type,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "restoration_enabled": record.restoration_enabled,
            "repair_enabled": record.repair_enabled,
            "remediation_enabled": record.remediation_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.continuity_support_id),
        )
    ]


def support_summary_visibility(
    records: Iterable[SupportSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "support_summary_record_id": record.support_summary_record_id,
            "support_summary_id": record.support_summary_id,
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
            key=lambda item: (item.deterministic_order, item.support_summary_record_id),
        )
    ]


def support_diagnostic_summary(
    records: Iterable[SupportDiagnosticRecord],
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
    records: Iterable[UnsupportedSupportOperationalStateVisibility],
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


def validate_required_support_status_visibility(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    classification_counts = count_support_classifications(
        intelligence.support_classifications
    )
    surface_counts = count_support_surfaces(intelligence.support_surfaces)
    unsupported_counts = count_unsupported_support_states(
        intelligence.unsupported_state_visibility
    )
    experimental_counts = count_experimental_deprecated_types(
        intelligence.experimental_deprecated_visibility
    )
    evidence_counts = count_evidence_based_support_types(
        intelligence.evidence_based_support_visibility
    )
    explainability_counts = count_explainability_support_types(
        intelligence.explainability_support_visibility
    )
    continuity_counts = count_continuity_support_types(
        intelligence.continuity_support_visibility
    )
    summary_counts = count_support_summary_types(intelligence.support_summaries)
    diagnostic_counts = count_support_diagnostic_types(
        intelligence.support_diagnostics
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_classifications": sorted(
            key for key, value in classification_counts.items() if value < 1
        ),
        "missing_surfaces": sorted(
            key for key, value in surface_counts.items() if value < 1
        ),
        "missing_unsupported_states": sorted(
            key for key, value in unsupported_counts.items() if value < 1
        ),
        "missing_experimental_deprecated": sorted(
            key for key, value in experimental_counts.items() if value < 1
        ),
        "missing_evidence_support": sorted(
            key for key, value in evidence_counts.items() if value < 1
        ),
        "missing_explainability_support": sorted(
            key for key, value in explainability_counts.items() if value < 1
        ),
        "missing_continuity_support": sorted(
            key for key, value in continuity_counts.items() if value < 1
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
        "classification_counts": classification_counts,
        "surface_counts": surface_counts,
        "unsupported_counts": unsupported_counts,
        "experimental_counts": experimental_counts,
        "evidence_counts": evidence_counts,
        "explainability_counts": explainability_counts,
        "continuity_counts": continuity_counts,
        "summary_counts": summary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_support_status_summary(
    intelligence: SupportStatusVisibilityIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "support_status_visibility_statement": (
            intelligence.support_status_visibility_statement
        ),
        "support_classification_non_authority_statement": (
            intelligence.support_classification_non_authority_statement
        ),
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "support_authorization_enabled": intelligence.support_authorization_enabled,
        "support_approval_enabled": intelligence.support_approval_enabled,
        "support_ranking_enabled": intelligence.support_ranking_enabled,
        "support_recommendation_enabled": intelligence.support_recommendation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
