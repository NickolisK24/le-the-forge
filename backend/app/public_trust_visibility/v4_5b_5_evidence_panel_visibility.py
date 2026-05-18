"""Visibility helpers for v4.5B.5 evidence panels."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_5_evidence_panel_models import (
    EVIDENCE_FRESHNESS_VISIBILITY_TYPES,
    EVIDENCE_GROUPING_TYPES,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EVIDENCE_PANEL_SUMMARY_TYPES,
    EVIDENCE_SOURCE_VISIBILITY_TYPES,
    EXPLAINABILITY_EVIDENCE_PANEL_TYPES,
    PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES,
    SUPPORT_STATUS_EVIDENCE_PANEL_TYPES,
    UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
    UNSUPPORTED_MISSING_EVIDENCE_TYPES,
    EvidenceFreshnessVisibility,
    EvidenceGroupRecord,
    EvidenceItemRecord,
    EvidencePanelDiagnosticRecord,
    EvidencePanelIntelligence,
    EvidencePanelRecord,
    EvidencePanelSummaryRecord,
    EvidenceSourceVisibility,
    ExplainabilityEvidencePanel,
    ProvenanceLineageEvidencePanel,
    SupportStatusEvidencePanel,
    UnsupportedEvidencePanelOperationalStateVisibility,
    UnsupportedMissingEvidenceVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_evidence_grouping_types(
    records: Iterable[EvidenceGroupRecord],
) -> dict[str, int]:
    return _count((record.grouping_type for record in records), EVIDENCE_GROUPING_TYPES)


def count_evidence_source_types(
    records: Iterable[EvidenceSourceVisibility],
) -> dict[str, int]:
    return _count(
        (record.source_visibility_type for record in records),
        EVIDENCE_SOURCE_VISIBILITY_TYPES,
    )


def count_evidence_freshness_types(
    records: Iterable[EvidenceFreshnessVisibility],
) -> dict[str, int]:
    return _count(
        (record.freshness_type for record in records),
        EVIDENCE_FRESHNESS_VISIBILITY_TYPES,
    )


def count_support_status_evidence_types(
    records: Iterable[SupportStatusEvidencePanel],
) -> dict[str, int]:
    return _count(
        (record.support_evidence_type for record in records),
        SUPPORT_STATUS_EVIDENCE_PANEL_TYPES,
    )


def count_explainability_evidence_types(
    records: Iterable[ExplainabilityEvidencePanel],
) -> dict[str, int]:
    return _count(
        (record.explainability_evidence_type for record in records),
        EXPLAINABILITY_EVIDENCE_PANEL_TYPES,
    )


def count_provenance_lineage_evidence_types(
    records: Iterable[ProvenanceLineageEvidencePanel],
) -> dict[str, int]:
    return _count(
        (record.provenance_lineage_evidence_type for record in records),
        PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES,
    )


def count_unsupported_missing_evidence_types(
    records: Iterable[UnsupportedMissingEvidenceVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_missing_type for record in records),
        UNSUPPORTED_MISSING_EVIDENCE_TYPES,
    )


def count_evidence_panel_summary_types(
    records: Iterable[EvidencePanelSummaryRecord],
) -> dict[str, int]:
    return _count((record.summary_type for record in records), EVIDENCE_PANEL_SUMMARY_TYPES)


def count_evidence_panel_diagnostic_types(
    records: Iterable[EvidencePanelDiagnosticRecord],
) -> dict[str, int]:
    return _count(
        (record.diagnostic_type for record in records),
        EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    )


def count_unsupported_operational_states(
    records: Iterable[UnsupportedEvidencePanelOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
    )


def evidence_panel_summary(
    records: Iterable[EvidencePanelRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "panel_record_id": record.panel_record_id,
            "evidence_panel_id": record.evidence_panel_id,
            "evidence_group_id": record.evidence_group_id,
            "evidence_item_id": record.evidence_item_id,
            "descriptive_only": record.descriptive_only,
            "publicly_transparent": record.publicly_transparent,
            "fail_visible": record.fail_visible,
            "evidence_authority_enabled": record.evidence_authority_enabled,
            "evidence_authorization_enabled": record.evidence_authorization_enabled,
            "evidence_approval_enabled": record.evidence_approval_enabled,
            "evidence_ranking_enabled": record.evidence_ranking_enabled,
            "evidence_recommendation_enabled": record.evidence_recommendation_enabled,
            "evidence_scoring_enabled": record.evidence_scoring_enabled,
            "trust_scoring_enabled": record.trust_scoring_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.panel_record_id),
        )
    ]


def evidence_grouping_summary(
    records: Iterable[EvidenceGroupRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "group_record_id": record.group_record_id,
            "grouping_type": record.grouping_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "prioritization_enabled": record.prioritization_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.group_record_id),
        )
    ]


def evidence_item_summary(records: Iterable[EvidenceItemRecord]) -> list[dict[str, Any]]:
    return [
        {
            "item_record_id": record.item_record_id,
            "evidence_item_type": record.evidence_item_type,
            "source_reference_id": record.source_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "replay_safe": record.replay_safe,
            "provenance_safe": record.provenance_safe,
            "scoring_enabled": record.scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.item_record_id),
        )
    ]


def evidence_source_summary(
    records: Iterable[EvidenceSourceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "source_visibility_id": record.source_visibility_id,
            "source_visibility_type": record.source_visibility_type,
            "source_reference_id": record.source_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "source_authority_enabled": record.source_authority_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "scoring_enabled": record.scoring_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.source_visibility_id),
        )
    ]


def evidence_freshness_summary(
    records: Iterable[EvidenceFreshnessVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "freshness_visibility_id": record.freshness_visibility_id,
            "freshness_type": record.freshness_type,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "automatic_refresh_enabled": record.automatic_refresh_enabled,
            "fallback_substitution_enabled": record.fallback_substitution_enabled,
            "scoring_enabled": record.scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.freshness_visibility_id),
        )
    ]


def support_status_evidence_summary(
    records: Iterable[SupportStatusEvidencePanel],
) -> list[dict[str, Any]]:
    return [
        {
            "support_panel_id": record.support_panel_id,
            "support_evidence_type": record.support_evidence_type,
            "support_status_reference_id": record.support_status_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_panel_id),
        )
    ]


def explainability_evidence_summary(
    records: Iterable[ExplainabilityEvidencePanel],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_panel_id": record.explainability_panel_id,
            "explainability_evidence_type": record.explainability_evidence_type,
            "explainability_surface_reference_id": (
                record.explainability_surface_reference_id
            ),
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "recommendation_enabled": record.recommendation_enabled,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.explainability_panel_id),
        )
    ]


def provenance_lineage_evidence_summary(
    records: Iterable[ProvenanceLineageEvidencePanel],
) -> list[dict[str, Any]]:
    return [
        {
            "provenance_lineage_panel_id": record.provenance_lineage_panel_id,
            "provenance_lineage_evidence_type": (
                record.provenance_lineage_evidence_type
            ),
            "provenance_reference_id": record.provenance_reference_id,
            "lineage_reference_id": record.lineage_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "source_scoring_enabled": record.source_scoring_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_panel_id,
            ),
        )
    ]


def unsupported_missing_evidence_summary(
    records: Iterable[UnsupportedMissingEvidenceVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_missing_id": record.unsupported_missing_id,
            "unsupported_missing_type": record.unsupported_missing_type,
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
            key=lambda item: (item.deterministic_order, item.unsupported_missing_id),
        )
    ]


def evidence_panel_summary_visibility(
    records: Iterable[EvidencePanelSummaryRecord],
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
            "scoring_enabled": record.scoring_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]


def evidence_panel_diagnostic_summary(
    records: Iterable[EvidencePanelDiagnosticRecord],
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
            "scoring_enabled": record.scoring_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_operational_state_summary(
    records: Iterable[UnsupportedEvidencePanelOperationalStateVisibility],
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
            "scoring_enabled": record.scoring_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_evidence_panel_visibility(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    grouping_counts = count_evidence_grouping_types(intelligence.evidence_group_records)
    source_counts = count_evidence_source_types(intelligence.evidence_source_visibility)
    freshness_counts = count_evidence_freshness_types(
        intelligence.evidence_freshness_visibility
    )
    support_counts = count_support_status_evidence_types(
        intelligence.support_status_evidence_panels
    )
    explainability_counts = count_explainability_evidence_types(
        intelligence.explainability_evidence_panels
    )
    provenance_lineage_counts = count_provenance_lineage_evidence_types(
        intelligence.provenance_lineage_evidence_panels
    )
    unsupported_counts = count_unsupported_missing_evidence_types(
        intelligence.unsupported_missing_evidence_visibility
    )
    summary_counts = count_evidence_panel_summary_types(
        intelligence.evidence_panel_summaries
    )
    diagnostic_counts = count_evidence_panel_diagnostic_types(
        intelligence.evidence_panel_diagnostics
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_groupings": sorted(
            key for key, value in grouping_counts.items() if value < 1
        ),
        "missing_sources": sorted(
            key for key, value in source_counts.items() if value < 1
        ),
        "missing_freshness": sorted(
            key for key, value in freshness_counts.items() if value < 1
        ),
        "missing_support_panels": sorted(
            key for key, value in support_counts.items() if value < 1
        ),
        "missing_explainability_panels": sorted(
            key for key, value in explainability_counts.items() if value < 1
        ),
        "missing_provenance_lineage_panels": sorted(
            key for key, value in provenance_lineage_counts.items() if value < 1
        ),
        "missing_unsupported_missing_evidence": sorted(
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
        "grouping_counts": grouping_counts,
        "source_counts": source_counts,
        "freshness_counts": freshness_counts,
        "support_counts": support_counts,
        "explainability_counts": explainability_counts,
        "provenance_lineage_counts": provenance_lineage_counts,
        "unsupported_counts": unsupported_counts,
        "summary_counts": summary_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_evidence_panel_summary(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "evidence_panel_statement": intelligence.evidence_panel_statement,
        "evidence_visibility_non_authority_statement": (
            intelligence.evidence_visibility_non_authority_statement
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
        "evidence_authorization_enabled": intelligence.evidence_authorization_enabled,
        "evidence_approval_enabled": intelligence.evidence_approval_enabled,
        "evidence_ranking_enabled": intelligence.evidence_ranking_enabled,
        "evidence_recommendation_enabled": intelligence.evidence_recommendation_enabled,
        "evidence_scoring_enabled": intelligence.evidence_scoring_enabled,
        "trust_scoring_enabled": intelligence.trust_scoring_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
