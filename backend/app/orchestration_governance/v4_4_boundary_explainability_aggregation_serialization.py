"""Deterministic serialization for v4.4 boundary explainability aggregation."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_explainability_aggregation_models import (
    BoundaryExplainabilityAggregationIdentity,
    BoundaryExplainabilityAggregationIntelligence,
    DiagnosticAggregationIdentity,
    DiagnosticAggregationRecord,
    ExplainabilityAggregationRecord,
    ExplanationCoverageSummary,
    ExplanationTraceRecord,
    LineageAggregationSummary,
    PhaseEvidenceSummary,
    ProvenanceAggregationSummary,
    ReplayRollbackAggregationSummary,
    SourceEvidenceReference,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_explainability_aggregation_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_explainability_aggregation_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_explainability_aggregation_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_explainability_aggregation_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_explainability_aggregation(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_explainability_aggregation_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_boundary_explainability_aggregation_identity(
    identity: BoundaryExplainabilityAggregationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_diagnostic_aggregation_identity(
    identity: DiagnosticAggregationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_source_evidence_reference(record: SourceEvidenceReference) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_phase_evidence_summary(summary: PhaseEvidenceSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["explained_reference_ids"] = _sorted_tuple(data["explained_reference_ids"])
    data["unresolved_reference_ids"] = _sorted_tuple(data["unresolved_reference_ids"])
    return data


def export_explainability_aggregation_record(
    record: ExplainabilityAggregationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["explanation_trace_ids"] = _sorted_tuple(data["explanation_trace_ids"])
    data["diagnostic_reference_ids"] = _sorted_tuple(data["diagnostic_reference_ids"])
    return data


def export_diagnostic_aggregation_record(record: DiagnosticAggregationRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_explanation_coverage_summary(summary: ExplanationCoverageSummary) -> dict[str, Any]:
    return asdict(summary)


def export_explanation_trace(record: ExplanationTraceRecord) -> dict[str, Any]:
    data = asdict(record)
    data["trace_reference_ids"] = _sorted_tuple(data["trace_reference_ids"])
    return data


def export_provenance_aggregation_summary(summary: ProvenanceAggregationSummary) -> dict[str, Any]:
    data = asdict(summary)
    for field_name in ("source_reference_ids", "source_hash_references", "diagnostic_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_lineage_aggregation_summary(summary: LineageAggregationSummary) -> dict[str, Any]:
    data = asdict(summary)
    for field_name in ("lineage_reference_ids", "lineage_hash_references", "explanation_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_replay_rollback_aggregation_summary(
    summary: ReplayRollbackAggregationSummary,
) -> dict[str, Any]:
    data = asdict(summary)
    for field_name in (
        "source_evidence_ids",
        "explanation_record_ids",
        "diagnostic_record_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_boundary_explainability_aggregation_intelligence(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_boundary_explainability_aggregation_identity(intelligence.identity)
    data["diagnostic_identity"] = export_diagnostic_aggregation_identity(
        intelligence.diagnostic_identity
    )
    data["source_evidence_references"] = [
        export_source_evidence_reference(record)
        for record in sorted(
            intelligence.source_evidence_references,
            key=lambda item: (item.deterministic_order, item.source_id),
        )
    ]
    data["phase_evidence_summaries"] = [
        export_phase_evidence_summary(record)
        for record in sorted(
            intelligence.phase_evidence_summaries,
            key=lambda item: (item.deterministic_order, item.summary_id),
        )
    ]
    data["explainability_records"] = [
        export_explainability_aggregation_record(record)
        for record in sorted(
            intelligence.explainability_records,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["diagnostic_records"] = [
        export_diagnostic_aggregation_record(record)
        for record in sorted(
            intelligence.diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["coverage_summaries"] = [
        export_explanation_coverage_summary(record)
        for record in sorted(
            intelligence.coverage_summaries,
            key=lambda item: (item.deterministic_order, item.coverage_id),
        )
    ]
    data["explanation_traces"] = [
        export_explanation_trace(record)
        for record in sorted(
            intelligence.explanation_traces,
            key=lambda item: (item.deterministic_order, item.trace_id),
        )
    ]
    data["provenance_summary"] = export_provenance_aggregation_summary(
        intelligence.provenance_summary
    )
    data["lineage_summary"] = export_lineage_aggregation_summary(intelligence.lineage_summary)
    data["replay_rollback_summary"] = export_replay_rollback_aggregation_summary(
        intelligence.replay_rollback_summary
    )
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_boundary_explainability_aggregation_identity(
    identity: BoundaryExplainabilityAggregationIdentity,
) -> str:
    return stable_serialize_boundary_explainability_aggregation(
        export_boundary_explainability_aggregation_identity(identity)
    )


def serialize_boundary_explainability_aggregation_intelligence(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> str:
    return stable_serialize_boundary_explainability_aggregation(
        export_boundary_explainability_aggregation_intelligence(intelligence)
    )
