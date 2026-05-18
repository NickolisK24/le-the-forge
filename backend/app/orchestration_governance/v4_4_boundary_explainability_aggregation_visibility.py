"""Visibility helpers for v4.4 boundary explainability aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .v4_4_boundary_explainability_aggregation_models import (
    BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES,
    EXPLAINABILITY_STATE_EXPLAINED,
    EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED,
    EXPLAINABILITY_STATE_UNEXPLAINED,
    FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES,
    BoundaryExplainabilityAggregationIntelligence,
    DiagnosticAggregationRecord,
    ExplainabilityAggregationRecord,
    ExplanationTraceRecord,
    SourceEvidenceReference,
)


def _ordered_ids(values: Iterable[str]) -> list[str]:
    return sorted(tuple(values or ()))


def count_source_coverage_states(records: Iterable[SourceEvidenceReference]) -> dict[str, int]:
    counts = Counter(record.coverage_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES}


def count_explanation_states(records: Iterable[ExplainabilityAggregationRecord]) -> dict[str, int]:
    counts = Counter(record.coverage_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES}


def count_diagnostic_states(records: Iterable[DiagnosticAggregationRecord]) -> dict[str, int]:
    counts = Counter(record.diagnostic_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES}


def count_trace_states(records: Iterable[ExplanationTraceRecord]) -> dict[str, int]:
    counts = Counter(record.trace_state for record in records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES}


def count_combined_explainability_states(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, int]:
    counts = Counter(record.coverage_state for record in intelligence.source_evidence_references)
    counts.update(record.diagnostic_state for record in intelligence.source_evidence_references)
    counts.update(record.coverage_state for record in intelligence.explainability_records)
    counts.update(record.diagnostic_state for record in intelligence.diagnostic_records)
    return {state: int(counts.get(state, 0)) for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES}


def source_evidence_coverage_totals(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.source_evidence_references)
    counts = count_source_coverage_states(records)
    return {
        "source_evidence_reference_count": len(records),
        "source_ids": _ordered_ids(record.source_id for record in records),
        "source_phase_ids": _ordered_ids(record.source_phase_id for record in records),
        "source_type_counts": {
            source_type: sum(1 for record in records if record.source_type == source_type)
            for source_type in sorted({record.source_type for record in records})
        },
        "coverage_state_counts": counts,
        "all_sources_available": all(record.source_available for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "production_consumption_enabled_count": sum(
            1 for record in records if record.production_consumption_enabled
        ),
    }


def explainability_coverage_summaries(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.explainability_records)
    counts = count_explanation_states(records)
    return {
        "explainability_record_count": len(records),
        "explained_count": counts[EXPLAINABILITY_STATE_EXPLAINED],
        "partially_explained_count": counts[EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED],
        "unexplained_count": counts[EXPLAINABILITY_STATE_UNEXPLAINED],
        "coverage_state_counts": counts,
        "explanation_ids": _ordered_ids(record.explanation_id for record in records),
        "descriptive_only": all(record.descriptive_only for record in records),
        "non_authoritative": all(record.non_authoritative for record in records),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "runtime_readiness_inferred_count": sum(
            1 for record in records if record.runtime_readiness_inferred
        ),
    }


def diagnostic_aggregation_summaries(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    records = tuple(intelligence.diagnostic_records)
    state_counts = count_diagnostic_states(records)
    severity_counts = Counter(record.severity for record in records)
    source_counts = Counter(record.diagnostic_source_type for record in records)
    return {
        "diagnostic_record_count": len(records),
        "state_counts": state_counts,
        "severity_counts": {
            severity: int(severity_counts[severity]) for severity in sorted(severity_counts)
        },
        "diagnostic_source_counts": {
            source: int(source_counts[source]) for source in sorted(source_counts)
        },
        "diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "unresolved_diagnostic_count": sum(1 for record in records if record.unresolved),
        "fail_visible_diagnostic_count": sum(1 for record in records if record.fail_visible),
        "descriptive_only": all(record.descriptive_only for record in records),
        "diagnostic_auto_resolution_enabled_count": sum(
            1 for record in records if record.diagnostic_auto_resolution_enabled
        ),
        "automatic_remediation_enabled_count": sum(
            1 for record in records if record.automatic_remediation_enabled
        ),
        "automatic_repair_enabled_count": sum(1 for record in records if record.automatic_repair_enabled),
        "recommendation_enabled_count": sum(1 for record in records if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in records if record.decision_enabled),
        "authorization_enabled_count": sum(1 for record in records if record.authorization_enabled),
    }


def unresolved_diagnostic_totals(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    records = tuple(record for record in intelligence.diagnostic_records if record.unresolved)
    return {
        "unresolved_diagnostic_count": len(records),
        "unresolved_diagnostic_ids": _ordered_ids(record.diagnostic_id for record in records),
        "fail_visible_unresolved_count": sum(1 for record in records if record.fail_visible),
        "states": {
            state: sum(1 for record in records if record.diagnostic_state == state)
            for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES
        },
    }


def fail_visible_diagnostic_summaries(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> list[dict[str, Any]]:
    return [
        {
            "diagnostic_id": record.diagnostic_id,
            "source_id": record.source_id,
            "diagnostic_state": record.diagnostic_state,
            "severity": record.severity,
            "unresolved": record.unresolved,
            "fail_visible": record.fail_visible,
            "evidence_reference_ids": _ordered_ids(record.evidence_reference_ids),
        }
        for record in sorted(
            (
                item
                for item in intelligence.diagnostic_records
                if item.diagnostic_state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES
            ),
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]


def provenance_visibility(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_summary
    return {
        "provenance_id": provenance.provenance_id,
        "source_reference_ids": _ordered_ids(provenance.source_reference_ids),
        "source_hash_references": _ordered_ids(provenance.source_hash_references),
        "diagnostic_reference_ids": _ordered_ids(provenance.diagnostic_reference_ids),
        "provenance_visible": provenance.provenance_visible,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "production_consumption_enabled": provenance.production_consumption_enabled,
    }


def lineage_visibility(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    lineage = intelligence.lineage_summary
    return {
        "lineage_id": lineage.lineage_id,
        "lineage_reference_ids": _ordered_ids(lineage.lineage_reference_ids),
        "lineage_hash_references": _ordered_ids(lineage.lineage_hash_references),
        "explanation_reference_ids": _ordered_ids(lineage.explanation_reference_ids),
        "lineage_visible": lineage.lineage_visible,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def governance_safe_explanation_traces(
    traces: Iterable[ExplanationTraceRecord],
) -> dict[str, Any]:
    trace_tuple = tuple(traces)
    counts = count_trace_states(trace_tuple)
    return {
        "trace_count": len(trace_tuple),
        "trace_state_counts": counts,
        "trace_ids": _ordered_ids(record.trace_id for record in trace_tuple),
        "explainability_first": all(record.explainability_first for record in trace_tuple),
        "descriptive_only": all(record.descriptive_only for record in trace_tuple),
        "recommendation_enabled_count": sum(1 for record in trace_tuple if record.recommendation_enabled),
        "decision_enabled_count": sum(1 for record in trace_tuple if record.decision_enabled),
        "runtime_readiness_inferred_count": sum(
            1 for record in trace_tuple if record.runtime_readiness_inferred
        ),
    }


def validate_required_explainability_visibility(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    counts = count_combined_explainability_states(intelligence)
    missing_states = [state for state in BOUNDARY_EXPLAINABILITY_AGGREGATION_STATES if counts[state] <= 0]
    fail_visible_missing = [
        state for state in FAIL_VISIBLE_EXPLAINABILITY_AGGREGATION_STATES if counts[state] <= 0
    ]
    return {
        "valid": not missing_states and not fail_visible_missing,
        "combined_counts": counts,
        "missing_states": missing_states,
        "missing_fail_visible_states": fail_visible_missing,
    }
