"""Deterministic serialization for v4.5B.4 provenance and lineage visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_4_provenance_lineage_visibility_models import (
    EvidenceOriginVisibility,
    ExplainabilityLineageVisibility,
    LineageVisibilityRecord,
    ProvenanceLineageDiagnosticRecord,
    ProvenanceLineageSummaryRecord,
    ProvenanceLineageVisibilityIdentity,
    ProvenanceLineageVisibilityIntelligence,
    ProvenanceVisibilityRecord,
    SourceToSurfaceVisibility,
    StaleUnknownProvenanceVisibility,
    SupportStatusLineageVisibility,
    TrustSummaryLineageVisibility,
    UnsupportedProvenanceLineageOperationalStateVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5b_4_provenance_lineage_visibility(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_4_provenance_lineage_visibility(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_4_provenance_lineage_visibility(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_4_provenance_lineage_visibility(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_4_provenance_lineage_visibility(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_4_provenance_lineage_visibility(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _export_with_sorted_evidence(record: object) -> dict[str, Any]:
    data = asdict(record)
    if "evidence_reference_ids" in data:
        data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_provenance_lineage_visibility_identity(
    identity: ProvenanceLineageVisibilityIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_provenance_visibility_record(
    record: ProvenanceVisibilityRecord,
) -> dict[str, Any]:
    return asdict(record)


def export_lineage_visibility_record(record: LineageVisibilityRecord) -> dict[str, Any]:
    return asdict(record)


def export_source_to_surface_visibility(
    record: SourceToSurfaceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_origin_visibility(
    record: EvidenceOriginVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_support_status_lineage_visibility(
    record: SupportStatusLineageVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_explainability_lineage_visibility(
    record: ExplainabilityLineageVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_trust_summary_lineage_visibility(
    record: TrustSummaryLineageVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_stale_unknown_provenance_visibility(
    record: StaleUnknownProvenanceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_provenance_lineage_summary_record(
    record: ProvenanceLineageSummaryRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_provenance_lineage_diagnostic_record(
    record: ProvenanceLineageDiagnosticRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_provenance_lineage_operational_state_visibility(
    record: UnsupportedProvenanceLineageOperationalStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_v4_5b_4_provenance_lineage_visibility(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["visibility_identity"] = export_provenance_lineage_visibility_identity(
        intelligence.visibility_identity
    )
    data["provenance_visibility_records"] = [
        export_provenance_visibility_record(record)
        for record in sorted(
            intelligence.provenance_visibility_records,
            key=lambda item: (item.deterministic_order, item.provenance_record_id),
        )
    ]
    data["lineage_visibility_records"] = [
        export_lineage_visibility_record(record)
        for record in sorted(
            intelligence.lineage_visibility_records,
            key=lambda item: (item.deterministic_order, item.lineage_record_id),
        )
    ]
    data["source_to_surface_visibility"] = [
        export_source_to_surface_visibility(record)
        for record in sorted(
            intelligence.source_to_surface_visibility,
            key=lambda item: (item.deterministic_order, item.source_surface_id),
        )
    ]
    data["evidence_origin_visibility"] = [
        export_evidence_origin_visibility(record)
        for record in sorted(
            intelligence.evidence_origin_visibility,
            key=lambda item: (item.deterministic_order, item.evidence_origin_id),
        )
    ]
    data["support_status_lineage_visibility"] = [
        export_support_status_lineage_visibility(record)
        for record in sorted(
            intelligence.support_status_lineage_visibility,
            key=lambda item: (item.deterministic_order, item.support_lineage_id),
        )
    ]
    data["explainability_lineage_visibility"] = [
        export_explainability_lineage_visibility(record)
        for record in sorted(
            intelligence.explainability_lineage_visibility,
            key=lambda item: (item.deterministic_order, item.explainability_lineage_id),
        )
    ]
    data["trust_summary_lineage_visibility"] = [
        export_trust_summary_lineage_visibility(record)
        for record in sorted(
            intelligence.trust_summary_lineage_visibility,
            key=lambda item: (item.deterministic_order, item.trust_lineage_id),
        )
    ]
    data["stale_unknown_provenance_visibility"] = [
        export_stale_unknown_provenance_visibility(record)
        for record in sorted(
            intelligence.stale_unknown_provenance_visibility,
            key=lambda item: (item.deterministic_order, item.stale_unknown_id),
        )
    ]
    data["provenance_lineage_summaries"] = [
        export_provenance_lineage_summary_record(record)
        for record in sorted(
            intelligence.provenance_lineage_summaries,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]
    data["provenance_lineage_diagnostics"] = [
        export_provenance_lineage_diagnostic_record(record)
        for record in sorted(
            intelligence.provenance_lineage_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_provenance_lineage_operational_state_visibility(record)
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


def serialize_provenance_lineage_visibility_identity(
    identity: ProvenanceLineageVisibilityIdentity,
) -> str:
    return stable_serialize_v4_5b_4_provenance_lineage_visibility(
        export_provenance_lineage_visibility_identity(identity)
    )


def serialize_v4_5b_4_provenance_lineage_visibility(
    intelligence: ProvenanceLineageVisibilityIntelligence,
) -> str:
    return stable_serialize_v4_5b_4_provenance_lineage_visibility(
        export_v4_5b_4_provenance_lineage_visibility(intelligence)
    )
