"""Deterministic serialization for v4.5B.6 coverage and confidence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_6_coverage_confidence_models import (
    ConfidenceVisibilityRecord,
    CoverageConfidenceIdentity,
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


def canonicalize_v4_5b_6_coverage_confidence_payload(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_6_coverage_confidence_payload(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_6_coverage_confidence_payload(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_6_coverage_confidence_payload(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_6_coverage_confidence(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_6_coverage_confidence_payload(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def export_coverage_confidence_identity(
    identity: CoverageConfidenceIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_coverage_visibility_record(
    record: CoverageVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_support_coverage_record(record: SupportCoverageRecord) -> dict[str, Any]:
    return asdict(record)


def export_evidence_coverage_record(record: EvidenceCoverageRecord) -> dict[str, Any]:
    return asdict(record)


def export_explainability_coverage_record(
    record: ExplainabilityCoverageRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_provenance_lineage_coverage_record(
    record: ProvenanceLineageCoverageRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_confidence_visibility_record(
    record: ConfidenceVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_incomplete_unknown_coverage_record(
    record: IncompleteUnknownCoverageRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_coverage_confidence_summary_record(
    record: CoverageConfidenceSummaryRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_coverage_diagnostic_record(
    record: CoverageDiagnosticRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_unsupported_coverage_confidence_operational_state_visibility(
    record: UnsupportedCoverageConfidenceOperationalStateVisibility,
) -> dict[str, Any]:
    return asdict(record)


def export_v4_5b_6_coverage_confidence(
    intelligence: CoverageConfidenceIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_coverage_confidence_identity(intelligence.identity)
    data["coverage_visibility_records"] = [
        export_coverage_visibility_record(record)
        for record in sorted(
            intelligence.coverage_visibility_records,
            key=lambda item: (item.deterministic_order, item.coverage_record_id),
        )
    ]
    data["support_coverage_records"] = [
        export_support_coverage_record(record)
        for record in sorted(
            intelligence.support_coverage_records,
            key=lambda item: (item.deterministic_order, item.support_coverage_id),
        )
    ]
    data["evidence_coverage_records"] = [
        export_evidence_coverage_record(record)
        for record in sorted(
            intelligence.evidence_coverage_records,
            key=lambda item: (item.deterministic_order, item.evidence_coverage_id),
        )
    ]
    data["explainability_coverage_records"] = [
        export_explainability_coverage_record(record)
        for record in sorted(
            intelligence.explainability_coverage_records,
            key=lambda item: (
                item.deterministic_order,
                item.explainability_coverage_id,
            ),
        )
    ]
    data["provenance_lineage_coverage_records"] = [
        export_provenance_lineage_coverage_record(record)
        for record in sorted(
            intelligence.provenance_lineage_coverage_records,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_coverage_id,
            ),
        )
    ]
    data["confidence_visibility_records"] = [
        export_confidence_visibility_record(record)
        for record in sorted(
            intelligence.confidence_visibility_records,
            key=lambda item: (item.deterministic_order, item.confidence_record_id),
        )
    ]
    data["incomplete_unknown_coverage_records"] = [
        export_incomplete_unknown_coverage_record(record)
        for record in sorted(
            intelligence.incomplete_unknown_coverage_records,
            key=lambda item: (item.deterministic_order, item.incomplete_unknown_id),
        )
    ]
    data["summary_records"] = [
        export_coverage_confidence_summary_record(record)
        for record in sorted(
            intelligence.summary_records,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]
    data["diagnostic_records"] = [
        export_coverage_diagnostic_record(record)
        for record in sorted(
            intelligence.diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_coverage_confidence_operational_state_visibility(record)
        for record in sorted(
            intelligence.unsupported_operational_state_visibility,
            key=lambda item: (item.deterministic_order, item.state_id),
        )
    ]
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["inherited_prohibitions"] = _sorted_tuple(data["inherited_prohibitions"])
    data["inherited_constraints"] = _sorted_tuple(data["inherited_constraints"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    return data


def serialize_coverage_confidence_identity(
    identity: CoverageConfidenceIdentity,
) -> str:
    return stable_serialize_v4_5b_6_coverage_confidence(
        export_coverage_confidence_identity(identity)
    )


def serialize_v4_5b_6_coverage_confidence(
    intelligence: CoverageConfidenceIntelligence,
) -> str:
    return stable_serialize_v4_5b_6_coverage_confidence(
        export_v4_5b_6_coverage_confidence(intelligence)
    )
