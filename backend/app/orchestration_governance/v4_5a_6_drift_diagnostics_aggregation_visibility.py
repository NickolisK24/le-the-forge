"""Visibility helpers for v4.5A.6 drift diagnostics aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_5a_6_drift_diagnostics_aggregation_models import (
    AGGREGATED_DIAGNOSTIC_TYPES,
    BLOCKER_WARNING_SUMMARY_TYPES,
    CONTINUITY_GAP_SUMMARY_TYPES,
    DIAGNOSTIC_SEVERITY_SUMMARY_TYPES,
    DIAGNOSTIC_SOURCE_TYPES,
    EVIDENCE_GAP_SUMMARY_TYPES,
    UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_SUMMARY_TYPES,
    AggregatedDiagnosticRecord,
    BlockerWarningSummaryVisibility,
    ContinuityGapSummaryVisibility,
    DiagnosticAggregationRecord,
    DiagnosticSeveritySummaryVisibility,
    DiagnosticSourceAggregation,
    DriftDiagnosticsAggregationIntelligence,
    EvidenceGapSummaryVisibility,
    UnsupportedAggregationVisibility,
    UnsupportedStateSummaryVisibility,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_diagnostic_source_types(
    records: Iterable[DiagnosticSourceAggregation],
) -> dict[str, int]:
    counts = Counter(record.source_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DIAGNOSTIC_SOURCE_TYPES}


def count_unsupported_state_summary_types(
    records: Iterable[UnsupportedStateSummaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_summary_type for record in records)
    return {item: int(counts.get(item, 0)) for item in UNSUPPORTED_STATE_SUMMARY_TYPES}


def count_evidence_gap_summary_types(
    records: Iterable[EvidenceGapSummaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.evidence_gap_type for record in records)
    return {item: int(counts.get(item, 0)) for item in EVIDENCE_GAP_SUMMARY_TYPES}


def count_continuity_gap_summary_types(
    records: Iterable[ContinuityGapSummaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.continuity_gap_type for record in records)
    return {item: int(counts.get(item, 0)) for item in CONTINUITY_GAP_SUMMARY_TYPES}


def count_severity_summary_types(
    records: Iterable[DiagnosticSeveritySummaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.severity_type for record in records)
    return {item: int(counts.get(item, 0)) for item in DIAGNOSTIC_SEVERITY_SUMMARY_TYPES}


def count_blocker_warning_summary_types(
    records: Iterable[BlockerWarningSummaryVisibility],
) -> dict[str, int]:
    counts = Counter(record.blocker_warning_type for record in records)
    return {item: int(counts.get(item, 0)) for item in BLOCKER_WARNING_SUMMARY_TYPES}


def count_aggregated_diagnostic_types(
    records: Iterable[AggregatedDiagnosticRecord],
) -> dict[str, int]:
    counts = Counter(record.diagnostic_type for record in records)
    return {item: int(counts.get(item, 0)) for item in AGGREGATED_DIAGNOSTIC_TYPES}


def count_unsupported_aggregation_states(
    records: Iterable[UnsupportedAggregationVisibility],
) -> dict[str, int]:
    counts = Counter(record.unsupported_state for record in records)
    return {
        item: int(counts.get(item, 0))
        for item in UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES
    }


def aggregation_summary_visibility(
    records: Iterable[DiagnosticAggregationRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "aggregation_record_id": record.aggregation_record_id,
            "diagnostic_aggregation_id": record.diagnostic_aggregation_id,
            "source_drift_id": record.source_drift_id,
            "propagation_chain_id": record.propagation_chain_id,
            "degradation_chain_id": record.degradation_chain_id,
            "explanation_chain_id": record.explanation_chain_id,
            "cross_boundary_continuity_id": record.cross_boundary_continuity_id,
            "evidence_chain_id": record.evidence_chain_id,
            "lineage_reference_id": record.lineage_reference_id,
            "provenance_reference_id": record.provenance_reference_id,
            "continuity_reference_id": record.continuity_reference_id,
            "source_diagnostic_type": record.source_diagnostic_type,
            "source_report_reference": record.source_report_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "automated_prioritization_enabled": record.automated_prioritization_enabled,
            "automated_triage_enabled": record.automated_triage_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.aggregation_record_id),
        )
    ]


def diagnostic_source_summary_visibility(
    records: Iterable[DiagnosticSourceAggregation],
) -> list[dict[str, Any]]:
    return [
        {
            "source_aggregation_id": record.source_aggregation_id,
            "aggregation_record_id": record.aggregation_record_id,
            "source_type": record.source_type,
            "source_report_reference": record.source_report_reference,
            "source_hash_reference": record.source_hash_reference,
            "diagnostic_count": record.diagnostic_count,
            "unsupported_state_count": record.unsupported_state_count,
            "evidence_gap_count": record.evidence_gap_count,
            "continuity_gap_count": record.continuity_gap_count,
            "inherited_prohibition_count": record.inherited_prohibition_count,
            "inherited_constraint_count": record.inherited_constraint_count,
            "descriptive_only": record.descriptive_only,
            "no_triage": record.no_triage,
            "no_prioritization": record.no_prioritization,
            "no_ranking": record.no_ranking,
            "no_recommendation": record.no_recommendation,
            "automated_triage_enabled": record.automated_triage_enabled,
            "automated_prioritization_enabled": record.automated_prioritization_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.source_aggregation_id),
        )
    ]


def unsupported_state_summary_visibility(
    records: Iterable[UnsupportedStateSummaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "unsupported_summary_id": record.unsupported_summary_id,
            "aggregation_record_id": record.aggregation_record_id,
            "unsupported_summary_type": record.unsupported_summary_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "state_count": record.state_count,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "automatic_response_enabled": record.automatic_response_enabled,
            "remediation_enabled": record.remediation_enabled,
            "recommendation_enabled": record.recommendation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.unsupported_summary_id),
        )
    ]


def evidence_gap_summary_visibility(
    records: Iterable[EvidenceGapSummaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "evidence_gap_id": record.evidence_gap_id,
            "aggregation_record_id": record.aggregation_record_id,
            "evidence_gap_type": record.evidence_gap_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "replay_safe": record.replay_safe,
            "rollback_safe": record.rollback_safe,
            "provenance_safe": record.provenance_safe,
            "lineage_safe": record.lineage_safe,
            "descriptive_only": record.descriptive_only,
            "evidence_repair_enabled": record.evidence_repair_enabled,
            "backfill_enabled": record.backfill_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.evidence_gap_id),
        )
    ]


def continuity_gap_summary_visibility(
    records: Iterable[ContinuityGapSummaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "continuity_gap_id": record.continuity_gap_id,
            "aggregation_record_id": record.aggregation_record_id,
            "continuity_gap_type": record.continuity_gap_type,
            "continuity_reference_id": record.continuity_reference_id,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "fail_visible": record.fail_visible,
            "continuity_restoration_enabled": record.continuity_restoration_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.continuity_gap_id),
        )
    ]


def severity_summary_visibility(
    records: Iterable[DiagnosticSeveritySummaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "severity_summary_id": record.severity_summary_id,
            "aggregation_record_id": record.aggregation_record_id,
            "severity_type": record.severity_type,
            "diagnostic_count": record.diagnostic_count,
            "visibility_reason": record.visibility_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "non_ranking": record.non_ranking,
            "non_recommending": record.non_recommending,
            "non_authorizing": record.non_authorizing,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "authorization_enabled": record.authorization_enabled,
            "automated_triage_enabled": record.automated_triage_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.severity_summary_id),
        )
    ]


def blocker_warning_summary_visibility(
    records: Iterable[BlockerWarningSummaryVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "blocker_warning_id": record.blocker_warning_id,
            "aggregation_record_id": record.aggregation_record_id,
            "blocker_warning_type": record.blocker_warning_type,
            "visibility_category": record.visibility_category,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "descriptive_only": record.descriptive_only,
            "action_logic_enabled": record.action_logic_enabled,
            "prioritization_enabled": record.prioritization_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "remediation_enabled": record.remediation_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.blocker_warning_id),
        )
    ]


def fail_visible_aggregated_diagnostic_summaries(
    records: Iterable[AggregatedDiagnosticRecord],
) -> list[dict[str, Any]]:
    return [
        {
            "aggregated_diagnostic_id": record.aggregated_diagnostic_id,
            "aggregation_record_id": record.aggregation_record_id,
            "diagnostic_type": record.diagnostic_type,
            "source_reference": record.source_reference,
            "source_hash_reference": record.source_hash_reference,
            "continuity_reference_id": record.continuity_reference_id,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "message": record.message,
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "silent_fallback_enabled": record.silent_fallback_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "auto_correction_enabled": record.auto_correction_enabled,
            "automated_triage_enabled": record.automated_triage_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "orchestration_response_enabled": record.orchestration_response_enabled,
        }
        for record in sorted(
            records,
            key=lambda item: (item.deterministic_order, item.aggregated_diagnostic_id),
        )
    ]


def unsupported_aggregation_visibility_summaries(
    records: Iterable[UnsupportedAggregationVisibility],
) -> list[dict[str, Any]]:
    return [
        {
            "state_id": record.state_id,
            "unsupported_state": record.unsupported_state,
            "explicit_reason": record.explicit_reason,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
            "fail_visible": record.fail_visible,
            "descriptive_only": record.descriptive_only,
            "operational_enabled": record.operational_enabled,
            "authorization_enabled": record.authorization_enabled,
            "automated_prioritization_enabled": record.automated_prioritization_enabled,
            "automated_triage_enabled": record.automated_triage_enabled,
            "ranking_enabled": record.ranking_enabled,
            "recommendation_enabled": record.recommendation_enabled,
            "remediation_enabled": record.remediation_enabled,
            "repair_enabled": record.repair_enabled,
            "mitigation_enabled": record.mitigation_enabled,
            "automated_correction_enabled": record.automated_correction_enabled,
            "continuity_restoration_enabled": record.continuity_restoration_enabled,
        }
        for record in sorted(records, key=lambda item: (item.deterministic_order, item.state_id))
    ]


def validate_required_diagnostics_aggregation_visibility(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    source_counts = count_diagnostic_source_types(intelligence.diagnostic_source_aggregation)
    unsupported_counts = count_unsupported_state_summary_types(
        intelligence.unsupported_state_summaries
    )
    evidence_counts = count_evidence_gap_summary_types(intelligence.evidence_gap_summaries)
    continuity_counts = count_continuity_gap_summary_types(
        intelligence.continuity_gap_summaries
    )
    severity_counts = count_severity_summary_types(intelligence.severity_summaries)
    blocker_warning_counts = count_blocker_warning_summary_types(
        intelligence.blocker_warning_summaries
    )
    diagnostic_counts = count_aggregated_diagnostic_types(
        intelligence.aggregated_diagnostics
    )
    unsupported_operational_counts = count_unsupported_aggregation_states(
        intelligence.unsupported_aggregation_visibility
    )
    missing_source_types = [key for key, count in source_counts.items() if count <= 0]
    missing_unsupported_summary_types = [
        key for key, count in unsupported_counts.items() if count <= 0
    ]
    missing_evidence_gap_types = [
        key for key, count in evidence_counts.items() if count <= 0
    ]
    missing_continuity_gap_types = [
        key for key, count in continuity_counts.items() if count <= 0
    ]
    missing_severity_types = [
        key for key, count in severity_counts.items() if count <= 0
    ]
    missing_blocker_warning_types = [
        key for key, count in blocker_warning_counts.items() if count <= 0
    ]
    missing_diagnostic_types = [
        key for key, count in diagnostic_counts.items() if count <= 0
    ]
    missing_unsupported_operational_states = [
        key for key, count in unsupported_operational_counts.items() if count <= 0
    ]
    return {
        "valid": not (
            missing_source_types
            or missing_unsupported_summary_types
            or missing_evidence_gap_types
            or missing_continuity_gap_types
            or missing_severity_types
            or missing_blocker_warning_types
            or missing_diagnostic_types
            or missing_unsupported_operational_states
        ),
        "source_counts": source_counts,
        "unsupported_summary_counts": unsupported_counts,
        "evidence_gap_counts": evidence_counts,
        "continuity_gap_counts": continuity_counts,
        "severity_counts": severity_counts,
        "blocker_warning_counts": blocker_warning_counts,
        "diagnostic_counts": diagnostic_counts,
        "unsupported_operational_counts": unsupported_operational_counts,
        "missing_source_types": missing_source_types,
        "missing_unsupported_summary_types": missing_unsupported_summary_types,
        "missing_evidence_gap_types": missing_evidence_gap_types,
        "missing_continuity_gap_types": missing_continuity_gap_types,
        "missing_severity_types": missing_severity_types,
        "missing_blocker_warning_types": missing_blocker_warning_types,
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_operational_states": missing_unsupported_operational_states,
    }


def descriptive_only_diagnostics_aggregation_summary(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    return {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_executing": intelligence.non_executing,
        "non_authorizing": intelligence.non_authorizing,
        "non_remediating": intelligence.non_remediating,
        "non_runtime_mutating": intelligence.non_runtime_mutating,
        "non_operational_mutating": intelligence.non_operational_mutating,
        "non_routing": intelligence.non_routing,
        "non_dispatching": intelligence.non_dispatching,
        "non_traversing": intelligence.non_traversing,
        "non_scheduling": intelligence.non_scheduling,
        "non_sequencing": intelligence.non_sequencing,
        "non_deciding": intelligence.non_deciding,
        "non_ranking": intelligence.non_ranking,
        "non_recommending": intelligence.non_recommending,
        "non_triaging": intelligence.non_triaging,
        "runtime_execution_enabled": intelligence.runtime_execution_enabled,
        "orchestration_execution_enabled": intelligence.orchestration_execution_enabled,
        "orchestration_authorization_enabled": intelligence.orchestration_authorization_enabled,
        "orchestration_approval_enabled": intelligence.orchestration_approval_enabled,
        "orchestration_dispatch_enabled": intelligence.orchestration_dispatch_enabled,
        "orchestration_routing_enabled": intelligence.orchestration_routing_enabled,
        "orchestration_traversal_enabled": intelligence.orchestration_traversal_enabled,
        "orchestration_scheduling_enabled": intelligence.orchestration_scheduling_enabled,
        "orchestration_sequencing_enabled": intelligence.orchestration_sequencing_enabled,
        "orchestration_decision_enabled": intelligence.orchestration_decision_enabled,
        "orchestration_recommendation_enabled": intelligence.orchestration_recommendation_enabled,
        "automated_prioritization_enabled": intelligence.automated_prioritization_enabled,
        "automated_triage_enabled": intelligence.automated_triage_enabled,
        "ranking_enabled": intelligence.ranking_enabled,
        "recommendation_enabled": intelligence.recommendation_enabled,
        "prioritization_action_enabled": intelligence.prioritization_action_enabled,
        "remediation_enabled": intelligence.remediation_enabled,
        "repair_enabled": intelligence.repair_enabled,
        "mitigation_enabled": intelligence.mitigation_enabled,
        "auto_correction_enabled": intelligence.auto_correction_enabled,
        "continuity_restoration_enabled": intelligence.continuity_restoration_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "planner_execution_enabled": intelligence.planner_execution_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
    }
