"""Deterministic serialization for v4.5B.5 evidence panels."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_5b_5_evidence_panel_models import (
    EvidenceFreshnessVisibility,
    EvidenceGroupRecord,
    EvidenceItemRecord,
    EvidencePanelDiagnosticRecord,
    EvidencePanelIdentity,
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


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_5b_5_evidence_panel_payload(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_5b_5_evidence_panel_payload(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_5b_5_evidence_panel_payload(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [
            canonicalize_v4_5b_5_evidence_panel_payload(value)
            for value in payload
        ]
    return payload


def stable_serialize_v4_5b_5_evidence_panels(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_5b_5_evidence_panel_payload(payload),
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


def export_evidence_panel_identity(identity: EvidencePanelIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_evidence_panel_record(record: EvidencePanelRecord) -> dict[str, Any]:
    return asdict(record)


def export_evidence_group_record(record: EvidenceGroupRecord) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_item_record(record: EvidenceItemRecord) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_source_visibility(
    record: EvidenceSourceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_freshness_visibility(
    record: EvidenceFreshnessVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_support_status_evidence_panel(
    record: SupportStatusEvidencePanel,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_explainability_evidence_panel(
    record: ExplainabilityEvidencePanel,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_provenance_lineage_evidence_panel(
    record: ProvenanceLineageEvidencePanel,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_missing_evidence_visibility(
    record: UnsupportedMissingEvidenceVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_panel_summary_record(
    record: EvidencePanelSummaryRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_evidence_panel_diagnostic_record(
    record: EvidencePanelDiagnosticRecord,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_unsupported_evidence_panel_operational_state_visibility(
    record: UnsupportedEvidencePanelOperationalStateVisibility,
) -> dict[str, Any]:
    return _export_with_sorted_evidence(record)


def export_v4_5b_5_evidence_panels(
    intelligence: EvidencePanelIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["evidence_identity"] = export_evidence_panel_identity(
        intelligence.evidence_identity
    )
    data["evidence_panel_records"] = [
        export_evidence_panel_record(record)
        for record in sorted(
            intelligence.evidence_panel_records,
            key=lambda item: (item.deterministic_order, item.panel_record_id),
        )
    ]
    data["evidence_group_records"] = [
        export_evidence_group_record(record)
        for record in sorted(
            intelligence.evidence_group_records,
            key=lambda item: (item.deterministic_order, item.group_record_id),
        )
    ]
    data["evidence_item_records"] = [
        export_evidence_item_record(record)
        for record in sorted(
            intelligence.evidence_item_records,
            key=lambda item: (item.deterministic_order, item.item_record_id),
        )
    ]
    data["evidence_source_visibility"] = [
        export_evidence_source_visibility(record)
        for record in sorted(
            intelligence.evidence_source_visibility,
            key=lambda item: (item.deterministic_order, item.source_visibility_id),
        )
    ]
    data["evidence_freshness_visibility"] = [
        export_evidence_freshness_visibility(record)
        for record in sorted(
            intelligence.evidence_freshness_visibility,
            key=lambda item: (item.deterministic_order, item.freshness_visibility_id),
        )
    ]
    data["support_status_evidence_panels"] = [
        export_support_status_evidence_panel(record)
        for record in sorted(
            intelligence.support_status_evidence_panels,
            key=lambda item: (item.deterministic_order, item.support_panel_id),
        )
    ]
    data["explainability_evidence_panels"] = [
        export_explainability_evidence_panel(record)
        for record in sorted(
            intelligence.explainability_evidence_panels,
            key=lambda item: (item.deterministic_order, item.explainability_panel_id),
        )
    ]
    data["provenance_lineage_evidence_panels"] = [
        export_provenance_lineage_evidence_panel(record)
        for record in sorted(
            intelligence.provenance_lineage_evidence_panels,
            key=lambda item: (
                item.deterministic_order,
                item.provenance_lineage_panel_id,
            ),
        )
    ]
    data["unsupported_missing_evidence_visibility"] = [
        export_unsupported_missing_evidence_visibility(record)
        for record in sorted(
            intelligence.unsupported_missing_evidence_visibility,
            key=lambda item: (item.deterministic_order, item.unsupported_missing_id),
        )
    ]
    data["evidence_panel_summaries"] = [
        export_evidence_panel_summary_record(record)
        for record in sorted(
            intelligence.evidence_panel_summaries,
            key=lambda item: (item.deterministic_order, item.summary_record_id),
        )
    ]
    data["evidence_panel_diagnostics"] = [
        export_evidence_panel_diagnostic_record(record)
        for record in sorted(
            intelligence.evidence_panel_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["unsupported_operational_state_visibility"] = [
        export_unsupported_evidence_panel_operational_state_visibility(record)
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


def serialize_evidence_panel_identity(identity: EvidencePanelIdentity) -> str:
    return stable_serialize_v4_5b_5_evidence_panels(
        export_evidence_panel_identity(identity)
    )


def serialize_v4_5b_5_evidence_panels(
    intelligence: EvidencePanelIntelligence,
) -> str:
    return stable_serialize_v4_5b_5_evidence_panels(
        export_v4_5b_5_evidence_panels(intelligence)
    )
