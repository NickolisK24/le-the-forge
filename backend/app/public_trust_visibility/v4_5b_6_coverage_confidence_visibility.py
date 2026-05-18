"""Visibility helpers for v4.5B.6 coverage and confidence."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_6_coverage_confidence_models import (
    CONFIDENCE_VISIBILITY_TYPES,
    COVERAGE_CONFIDENCE_SUMMARY_TYPES,
    COVERAGE_DIAGNOSTIC_TYPES,
    COVERAGE_VISIBILITY_TYPES,
    EVIDENCE_COVERAGE_TYPES,
    EXPLAINABILITY_COVERAGE_TYPES,
    INCOMPLETE_UNKNOWN_COVERAGE_TYPES,
    PROVENANCE_LINEAGE_COVERAGE_TYPES,
    SUPPORT_COVERAGE_TYPES,
    UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES,
    ConfidenceVisibilityRecord,
    CoverageConfidenceIntelligence,
    CoverageConfidenceSummaryRecord,
    CoverageDiagnosticRecord,
    CoverageVisibilityRecord,
    EvidenceCoverageRecord,
    ExplainabilityCoverageRecord,
    IncompleteUnknownCoverageRecord,
    ProvenanceLineageCoverageRecord,
    SupportCoverageRecord,
    UnsupportedCoverageConfidenceOperationalStateVisibility,
)


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_coverage_visibility_types(
    records: Iterable[CoverageVisibilityRecord],
) -> dict[str, int]:
    return _count((record.coverage_type for record in records), COVERAGE_VISIBILITY_TYPES)


def count_support_coverage_types(
    records: Iterable[SupportCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.support_coverage_type for record in records),
        SUPPORT_COVERAGE_TYPES,
    )


def count_evidence_coverage_types(
    records: Iterable[EvidenceCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.evidence_coverage_type for record in records),
        EVIDENCE_COVERAGE_TYPES,
    )


def count_explainability_coverage_types(
    records: Iterable[ExplainabilityCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.explainability_coverage_type for record in records),
        EXPLAINABILITY_COVERAGE_TYPES,
    )


def count_provenance_lineage_coverage_types(
    records: Iterable[ProvenanceLineageCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.provenance_lineage_coverage_type for record in records),
        PROVENANCE_LINEAGE_COVERAGE_TYPES,
    )


def count_confidence_visibility_types(
    records: Iterable[ConfidenceVisibilityRecord],
) -> dict[str, int]:
    return _count(
        (record.confidence_type for record in records),
        CONFIDENCE_VISIBILITY_TYPES,
    )


def count_incomplete_unknown_coverage_types(
    records: Iterable[IncompleteUnknownCoverageRecord],
) -> dict[str, int]:
    return _count(
        (record.incomplete_unknown_type for record in records),
        INCOMPLETE_UNKNOWN_COVERAGE_TYPES,
    )


def count_summary_types(
    records: Iterable[CoverageConfidenceSummaryRecord],
) -> dict[str, int]:
    return _count(
        (record.summary_type for record in records),
        COVERAGE_CONFIDENCE_SUMMARY_TYPES,
    )


def count_diagnostic_types(
    records: Iterable[CoverageDiagnosticRecord],
) -> dict[str, int]:
    return _count((record.diagnostic_type for record in records), COVERAGE_DIAGNOSTIC_TYPES)


def count_unsupported_operational_states(
    records: Iterable[UnsupportedCoverageConfidenceOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES,
    )


def coverage_visibility_summary(
    records: Iterable[CoverageVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "coverage_record_id": record.coverage_record_id,
            "coverage_type": record.coverage_type,
            "coverage_reference_id": record.coverage_reference_id,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "ranking_enabled": record.ranking_enabled,
            "scoring_enabled": record.scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.coverage_record_id),
        )
    ]


def support_coverage_summary(
    records: Iterable[SupportCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "support_coverage_id": record.support_coverage_id,
            "support_coverage_type": record.support_coverage_type,
            "support_status_reference_id": record.support_status_reference_id,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "approval_enabled": record.approval_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_coverage_id),
        )
    ]


def evidence_coverage_summary(
    records: Iterable[EvidenceCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_coverage_id": record.evidence_coverage_id,
            "evidence_coverage_type": record.evidence_coverage_type,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "descriptive_only": record.descriptive_only,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "evidence_ranking_enabled": record.evidence_ranking_enabled,
            "scoring_enabled": record.scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_coverage_id),
        )
    ]


def explainability_coverage_summary(
    records: Iterable[ExplainabilityCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_coverage_id": record.explainability_coverage_id,
            "explainability_coverage_type": record.explainability_coverage_type,
            "explainability_surface_reference_id": (
                record.explainability_surface_reference_id
            ),
            "continuity_reference_id": record.continuity_reference_id,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_coverage_id,
            ),
        )
    ]


def provenance_lineage_coverage_summary(
    records: Iterable[ProvenanceLineageCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "provenance_lineage_coverage_id": (
                record.provenance_lineage_coverage_id
            ),
            "provenance_lineage_coverage_type": (
                record.provenance_lineage_coverage_type
            ),
            "provenance_visibility_reference_id": (
                record.provenance_visibility_reference_id
            ),
            "lineage_visibility_reference_id": record.lineage_visibility_reference_id,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "descriptive_only": record.descriptive_only,
            "source_authority_enabled": record.source_authority_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "scoring_enabled": record.scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_coverage_id,
            ),
        )
    ]


def confidence_visibility_summary(
    records: Iterable[ConfidenceVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "confidence_record_id": record.confidence_record_id,
            "confidence_type": record.confidence_type,
            "coverage_reference_id": record.coverage_reference_id,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "descriptive_only": record.descriptive_only,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.confidence_record_id),
        )
    ]


def incomplete_unknown_coverage_summary(
    records: Iterable[IncompleteUnknownCoverageRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "incomplete_unknown_id": record.incomplete_unknown_id,
            "incomplete_unknown_type": record.incomplete_unknown_type,
            "coverage_reference_id": record.coverage_reference_id,
            "evidence_panel_reference_id": record.evidence_panel_reference_id,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "suppression_enabled": record.suppression_enabled,
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.incomplete_unknown_id),
        )
    ]


def coverage_confidence_summary_visibility(
    records: Iterable[CoverageConfidenceSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "summary_record_id": record.summary_record_id,
            "summary_type": record.summary_type,
            "coverage_reference_id": record.coverage_reference_id,
            "confidence_reference_id": record.confidence_reference_id,
            "summary_state": record.summary_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "scoring_enabled": record.scoring_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]


def coverage_diagnostic_summary(
    records: Iterable[CoverageDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "diagnostic_type": record.diagnostic_type,
            "coverage_reference_id": record.coverage_reference_id,
            "confidence_reference_id": record.confidence_reference_id,
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
            "scoring_enabled": record.scoring_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_operational_state_summary(
    records: Iterable[UnsupportedCoverageConfidenceOperationalStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "coverage_reference_id": record.coverage_reference_id,
            "confidence_reference_id": record.confidence_reference_id,
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
            "scoring_enabled": record.scoring_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_coverage_confidence_visibility(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    coverage_counts = count_coverage_visibility_types(
        intelligence.coverage_visibility_records
    )
    support_counts = count_support_coverage_types(
        intelligence.support_coverage_records
    )
    evidence_counts = count_evidence_coverage_types(
        intelligence.evidence_coverage_records
    )
    explainability_counts = count_explainability_coverage_types(
        intelligence.explainability_coverage_records
    )
    provenance_lineage_counts = count_provenance_lineage_coverage_types(
        intelligence.provenance_lineage_coverage_records
    )
    confidence_counts = count_confidence_visibility_types(
        intelligence.confidence_visibility_records
    )
    incomplete_unknown_counts = count_incomplete_unknown_coverage_types(
        intelligence.incomplete_unknown_coverage_records
    )
    summary_counts = count_summary_types(intelligence.summary_records)
    diagnostic_counts = count_diagnostic_types(intelligence.diagnostic_records)
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_coverage_visibility": sorted(
            key for key, value in coverage_counts.items() if value < 1
        ),
        "missing_support_coverage": sorted(
            key for key, value in support_counts.items() if value < 1
        ),
        "missing_evidence_coverage": sorted(
            key for key, value in evidence_counts.items() if value < 1
        ),
        "missing_explainability_coverage": sorted(
            key for key, value in explainability_counts.items() if value < 1
        ),
        "missing_provenance_lineage_coverage": sorted(
            key for key, value in provenance_lineage_counts.items() if value < 1
        ),
        "missing_confidence_visibility": sorted(
            key for key, value in confidence_counts.items() if value < 1
        ),
        "missing_incomplete_unknown_coverage": sorted(
            key for key, value in incomplete_unknown_counts.items() if value < 1
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
        "coverage_counts": coverage_counts,
        "support_counts": support_counts,
        "evidence_counts": evidence_counts,
        "explainability_counts": explainability_counts,
        "provenance_lineage_counts": provenance_lineage_counts,
        "confidence_counts": confidence_counts,
        "incomplete_unknown_counts": incomplete_unknown_counts,
        "summary_counts": summary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_coverage_confidence_summary(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "coverage_confidence_statement": intelligence.coverage_confidence_statement,
        "coverage_confidence_non_authority_statement": (
            intelligence.coverage_confidence_non_authority_statement
        ),
        "non_operational": intelligence.non_operational,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_executing": intelligence.non_executing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "non_scoring": intelligence.non_scoring,
        "confidence_authorization_enabled": (
            intelligence.confidence_authorization_enabled
        ),
        "confidence_approval_enabled": intelligence.confidence_approval_enabled,
        "coverage_ranking_enabled": intelligence.coverage_ranking_enabled,
        "confidence_recommendation_enabled": (
            intelligence.confidence_recommendation_enabled
        ),
        "trust_scoring_enabled": intelligence.trust_scoring_enabled,
        "evidence_scoring_enabled": intelligence.evidence_scoring_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
