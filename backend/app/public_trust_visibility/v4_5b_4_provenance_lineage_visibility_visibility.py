"""Visibility helpers for v4.5B.4 provenance and lineage visibility."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_4_provenance_lineage_visibility_models import (
    EVIDENCE_ORIGIN_VISIBILITY_TYPES,
    EXPLAINABILITY_LINEAGE_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PROVENANCE_LINEAGE_SUMMARY_TYPES,
    SOURCE_TO_SURFACE_VISIBILITY_TYPES,
    STALE_UNKNOWN_PROVENANCE_TYPES,
    SUPPORT_STATUS_LINEAGE_TYPES,
    TRUST_SUMMARY_LINEAGE_TYPES,
    UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES,
    EvidenceOriginVisibility,
    ExplainabilityLineageVisibility,
    LineageVisibilityRecord,
    ProvenanceLineageDiagnosticRecord,
    ProvenanceLineageSummaryRecord,
    ProvenanceLineageVisibilityIntelligence,
    ProvenanceVisibilityRecord,
    SourceToSurfaceVisibility,
    StaleUnknownProvenanceVisibility,
    SupportStatusLineageVisibility,
    TrustSummaryLineageVisibility,
    UnsupportedProvenanceLineageOperationalStateVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_source_to_surface_types(
    records: Iterable[SourceToSurfaceVisibility],
) -> dict[str, int]:
    return _count(
        (record.visibility_type for record in records),
        SOURCE_TO_SURFACE_VISIBILITY_TYPES,
    )


def count_evidence_origin_types(
    records: Iterable[EvidenceOriginVisibility],
) -> dict[str, int]:
    return _count(
        (record.evidence_origin_type for record in records),
        EVIDENCE_ORIGIN_VISIBILITY_TYPES,
    )


def count_support_status_lineage_types(
    records: Iterable[SupportStatusLineageVisibility],
) -> dict[str, int]:
    return _count(
        (record.support_lineage_type for record in records),
        SUPPORT_STATUS_LINEAGE_TYPES,
    )


def count_explainability_lineage_types(
    records: Iterable[ExplainabilityLineageVisibility],
) -> dict[str, int]:
    return _count(
        (record.explainability_lineage_type for record in records),
        EXPLAINABILITY_LINEAGE_TYPES,
    )


def count_trust_summary_lineage_types(
    records: Iterable[TrustSummaryLineageVisibility],
) -> dict[str, int]:
    return _count(
        (record.trust_lineage_type for record in records),
        TRUST_SUMMARY_LINEAGE_TYPES,
    )


def count_stale_unknown_provenance_types(
    records: Iterable[StaleUnknownProvenanceVisibility],
) -> dict[str, int]:
    return _count(
        (record.provenance_state_type for record in records),
        STALE_UNKNOWN_PROVENANCE_TYPES,
    )


def count_provenance_lineage_summary_types(
    records: Iterable[ProvenanceLineageSummaryRecord],
) -> dict[str, int]:
    return _count(
        (record.summary_type for record in records),
        PROVENANCE_LINEAGE_SUMMARY_TYPES,
    )


def count_provenance_lineage_diagnostic_types(
    records: Iterable[ProvenanceLineageDiagnosticRecord],
) -> dict[str, int]:
    return _count(
        (record.diagnostic_type for record in records),
        PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    )


def count_unsupported_operational_states(
    records: Iterable[UnsupportedProvenanceLineageOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES,
    )


def provenance_visibility_summary(
    records: Iterable[ProvenanceVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "provenance_record_id": record.provenance_record_id,
            "provenance_visibility_id": record.provenance_visibility_id,
            "source_reference_id": record.source_reference_id,
            "evidence_reference_id": record.evidence_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "source_authority_enabled": record.source_authority_enabled,
            "source_authorization_enabled": record.source_authorization_enabled,
            "source_approval_enabled": record.source_approval_enabled,
            "provenance_ranking_enabled": record.provenance_ranking_enabled,
            "trust_scoring_enabled": record.trust_scoring_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.provenance_record_id),
        )
    ]


def lineage_visibility_summary(
    records: Iterable[LineageVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "lineage_record_id": record.lineage_record_id,
            "lineage_visibility_id": record.lineage_visibility_id,
            "source_reference_id": record.source_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "lineage_recommendation_enabled": (
                record.lineage_recommendation_enabled
            ),
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.lineage_record_id),
        )
    ]


def source_to_surface_summary(
    records: Iterable[SourceToSurfaceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "source_surface_id": record.source_surface_id,
            "visibility_type": record.visibility_type,
            "source_reference_id": record.source_reference_id,
            "surface_reference_id": record.surface_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "source_authority_enabled": record.source_authority_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "ranking_enabled": record.ranking_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.source_surface_id),
        )
    ]


def evidence_origin_summary(
    records: Iterable[EvidenceOriginVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_origin_id": record.evidence_origin_id,
            "evidence_origin_type": record.evidence_origin_type,
            "source_reference_id": record.source_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "provenance_reference_id": record.provenance_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "descriptive_only": record.descriptive_only,
            "replay_safe": record.replay_safe,
            "provenance_safe": record.provenance_safe,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "ranking_enabled": record.ranking_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_origin_id),
        )
    ]


def support_status_lineage_summary(
    records: Iterable[SupportStatusLineageVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "support_lineage_id": record.support_lineage_id,
            "support_lineage_type": record.support_lineage_type,
            "support_status_reference_id": record.support_status_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_lineage_id),
        )
    ]


def explainability_lineage_summary(
    records: Iterable[ExplainabilityLineageVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_lineage_id": record.explainability_lineage_id,
            "explainability_lineage_type": record.explainability_lineage_type,
            "explainability_surface_reference_id": (
                record.explainability_surface_reference_id
            ),
            "lineage_reference_id": record.lineage_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "explanation_approval_enabled": record.explanation_approval_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.explainability_lineage_id),
        )
    ]


def trust_summary_lineage_summary(
    records: Iterable[TrustSummaryLineageVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "trust_lineage_id": record.trust_lineage_id,
            "trust_lineage_type": record.trust_lineage_type,
            "trust_summary_reference_id": record.trust_summary_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "operational_readiness_enabled": record.operational_readiness_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.trust_lineage_id),
        )
    ]


def stale_unknown_provenance_summary(
    records: Iterable[StaleUnknownProvenanceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "stale_unknown_id": record.stale_unknown_id,
            "provenance_state_type": record.provenance_state_type,
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
            key=lambda item: (item.deterministic_order, item.stale_unknown_id),
        )
    ]


def provenance_lineage_summary_visibility(
    records: Iterable[ProvenanceLineageSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "summary_record_id": record.summary_record_id,
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
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]


def provenance_lineage_diagnostic_summary(
    records: Iterable[ProvenanceLineageDiagnosticRecord],
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
    records: Iterable[UnsupportedProvenanceLineageOperationalStateVisibility],
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


def validate_required_provenance_lineage_visibility(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    source_counts = count_source_to_surface_types(
        intelligence.source_to_surface_visibility
    )
    evidence_counts = count_evidence_origin_types(
        intelligence.evidence_origin_visibility
    )
    support_counts = count_support_status_lineage_types(
        intelligence.support_status_lineage_visibility
    )
    explainability_counts = count_explainability_lineage_types(
        intelligence.explainability_lineage_visibility
    )
    trust_counts = count_trust_summary_lineage_types(
        intelligence.trust_summary_lineage_visibility
    )
    stale_unknown_counts = count_stale_unknown_provenance_types(
        intelligence.stale_unknown_provenance_visibility
    )
    summary_counts = count_provenance_lineage_summary_types(
        intelligence.provenance_lineage_summaries
    )
    diagnostic_counts = count_provenance_lineage_diagnostic_types(
        intelligence.provenance_lineage_diagnostics
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_source_to_surface": sorted(
            key for key, value in source_counts.items() if value < 1
        ),
        "missing_evidence_origin": sorted(
            key for key, value in evidence_counts.items() if value < 1
        ),
        "missing_support_status_lineage": sorted(
            key for key, value in support_counts.items() if value < 1
        ),
        "missing_explainability_lineage": sorted(
            key for key, value in explainability_counts.items() if value < 1
        ),
        "missing_trust_summary_lineage": sorted(
            key for key, value in trust_counts.items() if value < 1
        ),
        "missing_stale_unknown_provenance": sorted(
            key for key, value in stale_unknown_counts.items() if value < 1
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
        "source_counts": source_counts,
        "evidence_counts": evidence_counts,
        "support_counts": support_counts,
        "explainability_counts": explainability_counts,
        "trust_counts": trust_counts,
        "stale_unknown_counts": stale_unknown_counts,
        "summary_counts": summary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_provenance_lineage_summary(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "provenance_lineage_visibility_statement": (
            intelligence.provenance_lineage_visibility_statement
        ),
        "source_visibility_non_authority_statement": (
            intelligence.source_visibility_non_authority_statement
        ),
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "source_authorization_enabled": intelligence.source_authorization_enabled,
        "source_approval_enabled": intelligence.source_approval_enabled,
        "provenance_ranking_enabled": intelligence.provenance_ranking_enabled,
        "lineage_recommendation_enabled": intelligence.lineage_recommendation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
