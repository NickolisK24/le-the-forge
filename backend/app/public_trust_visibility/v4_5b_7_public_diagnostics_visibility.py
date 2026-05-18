"""Visibility helpers for v4.5B.7 public diagnostics."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5b_7_public_diagnostics_models import (
    BLOCKER_WARNING_SUMMARY_TYPES,
    COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES,
    DIAGNOSTICS_SUMMARY_TYPES,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EXPLAINABILITY_DIAGNOSTIC_TYPES,
    FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES,
    INHERITED_LIMITATION_VISIBILITY_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES,
    BlockerWarningSummaryRecord,
    CoverageConfidenceDiagnosticsRecord,
    DiagnosticsSummaryRecord,
    EvidencePanelDiagnosticsRecord,
    ExplainabilityDiagnosticsRecord,
    FailVisiblePublicDiagnosticRecord,
    InheritedLimitationVisibilityRecord,
    ProvenanceLineageDiagnosticsRecord,
    PublicDiagnosticsIntelligence,
    PublicDiagnosticsVisibilityRecord,
    SupportDiagnosticsRecord,
    UnsupportedPublicDiagnosticsOperationalStateVisibility,
)


def _count(items: Iterable[str], expected: tuple[str, ...]) -> dict[str, int]:
    counts = Counter(items)
    return {item: int(counts.get(item, 0)) for item in expected}


def count_public_diagnostics_types(
    records: Iterable[PublicDiagnosticsVisibilityRecord],
) -> dict[str, int]:
    return _count(
        (record.diagnostics_type for record in records),
        PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES,
    )


def count_support_diagnostic_types(
    records: Iterable[SupportDiagnosticsRecord],
) -> dict[str, int]:
    return _count(
        (record.support_diagnostics_type for record in records),
        SUPPORT_DIAGNOSTIC_TYPES,
    )


def count_explainability_diagnostic_types(
    records: Iterable[ExplainabilityDiagnosticsRecord],
) -> dict[str, int]:
    return _count(
        (record.explainability_diagnostics_type for record in records),
        EXPLAINABILITY_DIAGNOSTIC_TYPES,
    )


def count_provenance_lineage_diagnostic_types(
    records: Iterable[ProvenanceLineageDiagnosticsRecord],
) -> dict[str, int]:
    return _count(
        (record.provenance_lineage_diagnostics_type for record in records),
        PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    )


def count_evidence_panel_diagnostic_types(
    records: Iterable[EvidencePanelDiagnosticsRecord],
) -> dict[str, int]:
    return _count(
        (record.evidence_diagnostics_type for record in records),
        EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    )


def count_coverage_confidence_diagnostic_types(
    records: Iterable[CoverageConfidenceDiagnosticsRecord],
) -> dict[str, int]:
    return _count(
        (record.coverage_confidence_diagnostics_type for record in records),
        COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES,
    )


def count_inherited_limitation_types(
    records: Iterable[InheritedLimitationVisibilityRecord],
) -> dict[str, int]:
    return _count(
        (record.inherited_limitation_type for record in records),
        INHERITED_LIMITATION_VISIBILITY_TYPES,
    )


def count_blocker_warning_types(
    records: Iterable[BlockerWarningSummaryRecord],
) -> dict[str, int]:
    return _count(
        (record.blocker_warning_type for record in records),
        BLOCKER_WARNING_SUMMARY_TYPES,
    )


def count_summary_types(records: Iterable[DiagnosticsSummaryRecord]) -> dict[str, int]:
    return _count((record.summary_type for record in records), DIAGNOSTICS_SUMMARY_TYPES)


def count_fail_visible_diagnostic_types(
    records: Iterable[FailVisiblePublicDiagnosticRecord],
) -> dict[str, int]:
    return _count(
        (record.diagnostic_type for record in records),
        FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES,
    )


def count_unsupported_operational_states(
    records: Iterable[UnsupportedPublicDiagnosticsOperationalStateVisibility],
) -> dict[str, int]:
    return _count(
        (record.unsupported_state for record in records),
        UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES,
    )


def public_diagnostics_summary(
    records: Iterable[PublicDiagnosticsVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostics_record_id": record.diagnostics_record_id,
            "diagnostics_type": record.diagnostics_type,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "triage_enabled": record.triage_enabled,
            "operational_enabled": record.operational_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostics_record_id),
        )
    ]


def support_diagnostics_summary(
    records: Iterable[SupportDiagnosticsRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "support_diagnostics_id": record.support_diagnostics_id,
            "support_diagnostics_type": record.support_diagnostics_type,
            "support_diagnostics_reference_id": (
                record.support_diagnostics_reference_id
            ),
            "descriptive_only": record.descriptive_only,
            "triage_enabled": record.triage_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.support_diagnostics_id),
        )
    ]


def explainability_diagnostics_summary(
    records: Iterable[ExplainabilityDiagnosticsRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "explainability_diagnostics_id": record.explainability_diagnostics_id,
            "explainability_diagnostics_type": (
                record.explainability_diagnostics_type
            ),
            "explainability_diagnostics_reference_id": (
                record.explainability_diagnostics_reference_id
            ),
            "continuity_reference_id": record.continuity_reference_id,
            "descriptive_only": record.descriptive_only,
            "operational_semantics_enabled": record.operational_semantics_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_diagnostics_id,
            ),
        )
    ]


def provenance_lineage_diagnostics_summary(
    records: Iterable[ProvenanceLineageDiagnosticsRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "provenance_lineage_diagnostics_id": (
                record.provenance_lineage_diagnostics_id
            ),
            "provenance_lineage_diagnostics_type": (
                record.provenance_lineage_diagnostics_type
            ),
            "provenance_diagnostics_reference_id": (
                record.provenance_diagnostics_reference_id
            ),
            "lineage_diagnostics_reference_id": (
                record.lineage_diagnostics_reference_id
            ),
            "descriptive_only": record.descriptive_only,
            "source_authority_enabled": record.source_authority_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_diagnostics_id,
            ),
        )
    ]


def evidence_panel_diagnostics_summary(
    records: Iterable[EvidencePanelDiagnosticsRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_diagnostics_id": record.evidence_diagnostics_id,
            "evidence_diagnostics_type": record.evidence_diagnostics_type,
            "evidence_panel_diagnostics_reference_id": (
                record.evidence_panel_diagnostics_reference_id
            ),
            "descriptive_only": record.descriptive_only,
            "evidence_repair_enabled": record.evidence_repair_enabled,
            "remediation_enabled": record.remediation_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_diagnostics_id),
        )
    ]


def coverage_confidence_diagnostics_summary(
    records: Iterable[CoverageConfidenceDiagnosticsRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "coverage_confidence_diagnostics_id": (
                record.coverage_confidence_diagnostics_id
            ),
            "coverage_confidence_diagnostics_type": (
                record.coverage_confidence_diagnostics_type
            ),
            "coverage_diagnostics_reference_id": (
                record.coverage_diagnostics_reference_id
            ),
            "confidence_diagnostics_reference_id": (
                record.confidence_diagnostics_reference_id
            ),
            "descriptive_only": record.descriptive_only,
            "scoring_enabled": record.scoring_enabled,
            "trust_scoring_enabled": record.trust_scoring_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "triage_enabled": record.triage_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (
                item.deterministic_order,
                item.coverage_confidence_diagnostics_id,
            ),
        )
    ]


def inherited_limitation_summary(
    records: Iterable[InheritedLimitationVisibilityRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "inherited_limitation_id": record.inherited_limitation_id,
            "inherited_limitation_type": record.inherited_limitation_type,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "suppression_enabled": record.suppression_enabled,
            "hidden_fallback_enabled": record.hidden_fallback_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.inherited_limitation_id),
        )
    ]


def blocker_warning_summary(
    records: Iterable[BlockerWarningSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "blocker_warning_id": record.blocker_warning_id,
            "blocker_warning_type": record.blocker_warning_type,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "summary_state": record.summary_state,
            "descriptive_only": record.descriptive_only,
            "prioritization_enabled": record.prioritization_enabled,
            "triage_enabled": record.triage_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.blocker_warning_id),
        )
    ]


def diagnostics_summary_visibility(
    records: Iterable[DiagnosticsSummaryRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "summary_record_id": record.summary_record_id,
            "summary_type": record.summary_type,
            "diagnostics_reference_id": record.diagnostics_reference_id,
            "summary_state": record.summary_state,
            "descriptive_only": record.descriptive_only,
            "authorization_enabled": record.authorization_enabled,
            "approval_enabled": record.approval_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "scoring_enabled": record.scoring_enabled,
            "triage_enabled": record.triage_enabled,
            "execution_enablement_enabled": record.execution_enablement_enabled,
            "production_enablement_enabled": record.production_enablement_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]


def fail_visible_public_diagnostics_summary(
    records: Iterable[FailVisiblePublicDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "diagnostic_type": record.diagnostic_type,
            "diagnostics_reference_id": record.diagnostics_reference_id,
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
            "triage_enabled": record.triage_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def unsupported_operational_state_summary(
    records: Iterable[UnsupportedPublicDiagnosticsOperationalStateVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "diagnostics_reference_id": record.diagnostics_reference_id,
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
            "triage_enabled": record.triage_enabled,
            "suppression_enabled": record.suppression_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]


def validate_required_public_diagnostics_visibility(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    public_counts = count_public_diagnostics_types(intelligence.public_diagnostics_records)
    support_counts = count_support_diagnostic_types(
        intelligence.support_diagnostics_records
    )
    explainability_counts = count_explainability_diagnostic_types(
        intelligence.explainability_diagnostics_records
    )
    provenance_lineage_counts = count_provenance_lineage_diagnostic_types(
        intelligence.provenance_lineage_diagnostics_records
    )
    evidence_counts = count_evidence_panel_diagnostic_types(
        intelligence.evidence_panel_diagnostics_records
    )
    coverage_confidence_counts = count_coverage_confidence_diagnostic_types(
        intelligence.coverage_confidence_diagnostics_records
    )
    inherited_counts = count_inherited_limitation_types(
        intelligence.inherited_limitation_records
    )
    blocker_warning_counts = count_blocker_warning_types(
        intelligence.blocker_warning_records
    )
    summary_counts = count_summary_types(intelligence.summary_records)
    fail_visible_counts = count_fail_visible_diagnostic_types(
        intelligence.fail_visible_diagnostic_records
    )
    unsupported_operational_counts = count_unsupported_operational_states(
        intelligence.unsupported_operational_state_visibility
    )
    missing = {
        "missing_public_diagnostics": sorted(
            key for key, value in public_counts.items() if value < 1
        ),
        "missing_support_diagnostics": sorted(
            key for key, value in support_counts.items() if value < 1
        ),
        "missing_explainability_diagnostics": sorted(
            key for key, value in explainability_counts.items() if value < 1
        ),
        "missing_provenance_lineage_diagnostics": sorted(
            key for key, value in provenance_lineage_counts.items() if value < 1
        ),
        "missing_evidence_diagnostics": sorted(
            key for key, value in evidence_counts.items() if value < 1
        ),
        "missing_coverage_confidence_diagnostics": sorted(
            key for key, value in coverage_confidence_counts.items() if value < 1
        ),
        "missing_inherited_limitations": sorted(
            key for key, value in inherited_counts.items() if value < 1
        ),
        "missing_blocker_warnings": sorted(
            key for key, value in blocker_warning_counts.items() if value < 1
        ),
        "missing_summaries": sorted(
            key for key, value in summary_counts.items() if value < 1
        ),
        "missing_fail_visible_diagnostics": sorted(
            key for key, value in fail_visible_counts.items() if value < 1
        ),
        "missing_unsupported_operational_states": sorted(
            key for key, value in unsupported_operational_counts.items() if value < 1
        ),
    }
    return {
        "valid": not any(missing.values()),
        "public_counts": public_counts,
        "support_counts": support_counts,
        "explainability_counts": explainability_counts,
        "provenance_lineage_counts": provenance_lineage_counts,
        "evidence_counts": evidence_counts,
        "coverage_confidence_counts": coverage_confidence_counts,
        "inherited_counts": inherited_counts,
        "blocker_warning_counts": blocker_warning_counts,
        "summary_counts": summary_counts,
        "fail_visible_counts": fail_visible_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        **missing,
    }


def descriptive_only_public_diagnostics_summary(
    intelligence: PublicDiagnosticsIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "publicly_transparent": intelligence.publicly_transparent,
        "public_diagnostics_statement": intelligence.public_diagnostics_statement,
        "diagnostics_visibility_non_authority_statement": (
            intelligence.diagnostics_visibility_non_authority_statement
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
        "non_triaging": intelligence.non_triaging,
        "diagnostics_authorization_enabled": (
            intelligence.diagnostics_authorization_enabled
        ),
        "diagnostics_approval_enabled": intelligence.diagnostics_approval_enabled,
        "diagnostics_ranking_enabled": intelligence.diagnostics_ranking_enabled,
        "diagnostics_recommendation_enabled": (
            intelligence.diagnostics_recommendation_enabled
        ),
        "diagnostics_triage_enabled": intelligence.diagnostics_triage_enabled,
        "scoring_enabled": intelligence.scoring_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
