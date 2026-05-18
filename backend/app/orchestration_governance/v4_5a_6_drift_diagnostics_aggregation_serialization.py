"""Deterministic serialization for v4.5A.6 drift diagnostics aggregation."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5a_6_drift_diagnostics_aggregation_models import (
    AggregatedDiagnosticRecord,
    BlockerWarningSummaryVisibility,
    ContinuityGapSummaryVisibility,
    DiagnosticAggregationRecord,
    DiagnosticSeveritySummaryVisibility,
    DiagnosticSourceAggregation,
    DriftDiagnosticsAggregationIdentity,
    DriftDiagnosticsAggregationIntelligence,
    EvidenceGapSummaryVisibility,
    UnsupportedAggregationVisibility,
    UnsupportedStateSummaryVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5a_6_drift_diagnostics_aggregation_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5a_6_drift_diagnostics_aggregation_evidence(
            asdict(payload)
        )
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5a_6_drift_diagnostics_aggregation_evidence(
                value
            )
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5a_6_drift_diagnostics_aggregation_evidence(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5a_6_drift_diagnostics_aggregation(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5a_6_drift_diagnostics_aggregation_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_drift_diagnostics_aggregation_identity(
    identity: DriftDiagnosticsAggregationIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_diagnostic_aggregation_record(
    record: DiagnosticAggregationRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_diagnostic_source_aggregation(
    record: DiagnosticSourceAggregation,
) -> dict[str, Any]:
    return asdict(record)


def export_unsupported_state_summary_visibility(
    record: UnsupportedStateSummaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_evidence_gap_summary_visibility(
    record: EvidenceGapSummaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_continuity_gap_summary_visibility(
    record: ContinuityGapSummaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_diagnostic_severity_summary_visibility(
    record: DiagnosticSeveritySummaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_blocker_warning_summary_visibility(
    record: BlockerWarningSummaryVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_aggregated_diagnostic_record(
    record: AggregatedDiagnosticRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_unsupported_aggregation_visibility(
    record: UnsupportedAggregationVisibility,
) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_v4_5a_6_drift_diagnostics_aggregation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["aggregation_identity"] = export_drift_diagnostics_aggregation_identity(
        intelligence.aggregation_identity
    )
    data["diagnostic_aggregation_records"] = [
        export_diagnostic_aggregation_record(record)
        for record in sorted(
            intelligence.diagnostic_aggregation_records,
            key=lambda item: (item.deterministic_order, item.aggregation_record_id),
        )
    ]
    data["diagnostic_source_aggregation"] = [
        export_diagnostic_source_aggregation(record)
        for record in sorted(
            intelligence.diagnostic_source_aggregation,
            key=lambda item: (item.deterministic_order, item.source_aggregation_id),
        )
    ]
    data["unsupported_state_summaries"] = [
        export_unsupported_state_summary_visibility(record)
        for record in sorted(
            intelligence.unsupported_state_summaries,
            key=lambda item: (item.deterministic_order, item.unsupported_summary_id),
        )
    ]
    data["evidence_gap_summaries"] = [
        export_evidence_gap_summary_visibility(record)
        for record in sorted(
            intelligence.evidence_gap_summaries,
            key=lambda item: (item.deterministic_order, item.evidence_gap_id),
        )
    ]
    data["continuity_gap_summaries"] = [
        export_continuity_gap_summary_visibility(record)
        for record in sorted(
            intelligence.continuity_gap_summaries,
            key=lambda item: (item.deterministic_order, item.continuity_gap_id),
        )
    ]
    data["severity_summaries"] = [
        export_diagnostic_severity_summary_visibility(record)
        for record in sorted(
            intelligence.severity_summaries,
            key=lambda item: (item.deterministic_order, item.severity_summary_id),
        )
    ]
    data["blocker_warning_summaries"] = [
        export_blocker_warning_summary_visibility(record)
        for record in sorted(
            intelligence.blocker_warning_summaries,
            key=lambda item: (item.deterministic_order, item.blocker_warning_id),
        )
    ]
    data["aggregated_diagnostics"] = [
        export_aggregated_diagnostic_record(record)
        for record in sorted(
            intelligence.aggregated_diagnostics,
            key=lambda item: (item.deterministic_order, item.aggregated_diagnostic_id),
        )
    ]
    data["unsupported_aggregation_visibility"] = [
        export_unsupported_aggregation_visibility(record)
        for record in sorted(
            intelligence.unsupported_aggregation_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_drift_diagnostics_aggregation_identity(
    identity: DriftDiagnosticsAggregationIdentity,
) -> str:
    return stable_serialize_v4_5a_6_drift_diagnostics_aggregation(
        export_drift_diagnostics_aggregation_identity(identity)
    )


def serialize_v4_5a_6_drift_diagnostics_aggregation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> str:
    return stable_serialize_v4_5a_6_drift_diagnostics_aggregation(
        export_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    )
