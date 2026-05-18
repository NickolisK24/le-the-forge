"""Deterministic serialization for v4.4 boundary intelligence foundations."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_intelligence_foundations_models import (
    BoundaryContinuityMetadata,
    BoundaryDiagnosticRecord,
    BoundaryExplainabilityRecord,
    BoundaryFailVisibleFinding,
    BoundaryGovernanceVisibilitySummary,
    BoundaryIntegrityVisibility,
    BoundaryIntelligenceClassification,
    BoundaryIntelligenceFoundations,
    BoundaryIntelligenceIdentity,
    BoundaryIntelligenceRecord,
    BoundaryLineageMetadata,
    BoundaryProvenanceMetadata,
    BoundaryScopeVisibility,
    BoundarySegmentationVisibility,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_intelligence_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_intelligence_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_intelligence_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_intelligence_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_intelligence(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_intelligence_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_boundary_intelligence_identity(identity: BoundaryIntelligenceIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_boundary_intelligence_classification(
    classification: BoundaryIntelligenceClassification,
) -> dict[str, Any]:
    return asdict(classification)


def export_boundary_intelligence_record(record: BoundaryIntelligenceRecord) -> dict[str, Any]:
    return asdict(record)


def export_boundary_scope_visibility(scope: BoundaryScopeVisibility) -> dict[str, Any]:
    return asdict(scope)


def export_boundary_segmentation_visibility(
    segmentation: BoundarySegmentationVisibility,
) -> dict[str, Any]:
    return asdict(segmentation)


def export_boundary_diagnostic_record(diagnostic: BoundaryDiagnosticRecord) -> dict[str, Any]:
    data = asdict(diagnostic)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_boundary_explainability_record(
    explainability: BoundaryExplainabilityRecord,
) -> dict[str, Any]:
    data = asdict(explainability)
    data["visible_reason_ids"] = _sorted_tuple(data["visible_reason_ids"])
    return data


def export_boundary_integrity_visibility(
    integrity: BoundaryIntegrityVisibility,
) -> dict[str, Any]:
    return asdict(integrity)


def export_boundary_governance_visibility_summary(
    summary: BoundaryGovernanceVisibilitySummary,
) -> dict[str, Any]:
    data = asdict(summary)
    data["boundary_ids"] = _sorted_tuple(data["boundary_ids"])
    data["classification_ids"] = _sorted_tuple(data["classification_ids"])
    return data


def export_boundary_fail_visible_finding(finding: BoundaryFailVisibleFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_boundary_continuity_metadata(
    metadata: BoundaryContinuityMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "deterministic_evidence_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
        "continuity_guarantees",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_boundary_provenance_metadata(
    metadata: BoundaryProvenanceMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    data["source_reference_ids"] = _sorted_tuple(data["source_reference_ids"])
    data["source_hash_references"] = _sorted_tuple(data["source_hash_references"])
    return data


def export_boundary_lineage_metadata(metadata: BoundaryLineageMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    data["lineage_reference_ids"] = _sorted_tuple(data["lineage_reference_ids"])
    data["lineage_hash_references"] = _sorted_tuple(data["lineage_hash_references"])
    return data


def export_boundary_intelligence_foundations(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    data = asdict(foundations)
    data["identity"] = export_boundary_intelligence_identity(foundations.identity)
    data["classifications"] = [
        export_boundary_intelligence_classification(classification)
        for classification in sorted(
            foundations.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["boundary_records"] = [
        export_boundary_intelligence_record(record)
        for record in sorted(
            foundations.boundary_records,
            key=lambda item: (item.deterministic_order, item.boundary_id),
        )
    ]
    data["scope_visibility"] = [
        export_boundary_scope_visibility(scope)
        for scope in sorted(
            foundations.scope_visibility,
            key=lambda item: (item.deterministic_order, item.scope_id),
        )
    ]
    data["segmentation_visibility"] = [
        export_boundary_segmentation_visibility(segment)
        for segment in sorted(
            foundations.segmentation_visibility,
            key=lambda item: (item.deterministic_order, item.segment_id),
        )
    ]
    data["diagnostics"] = [
        export_boundary_diagnostic_record(diagnostic)
        for diagnostic in sorted(
            foundations.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explainability"] = [
        export_boundary_explainability_record(explainability)
        for explainability in sorted(
            foundations.explainability,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["integrity_visibility"] = [
        export_boundary_integrity_visibility(integrity)
        for integrity in sorted(
            foundations.integrity_visibility,
            key=lambda item: (item.deterministic_order, item.integrity_id),
        )
    ]
    data["governance_visibility_summaries"] = [
        export_boundary_governance_visibility_summary(summary)
        for summary in sorted(
            foundations.governance_visibility_summaries,
            key=lambda item: (item.deterministic_order, item.state_type),
        )
    ]
    data["fail_visible_findings"] = [
        export_boundary_fail_visible_finding(finding)
        for finding in sorted(
            foundations.fail_visible_findings,
            key=lambda item: (item.deterministic_order, item.finding_id),
        )
    ]
    data["continuity_metadata"] = export_boundary_continuity_metadata(
        foundations.continuity_metadata
    )
    data["provenance_metadata"] = export_boundary_provenance_metadata(
        foundations.provenance_metadata
    )
    data["lineage_metadata"] = export_boundary_lineage_metadata(foundations.lineage_metadata)
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_boundary_intelligence_identity(identity: BoundaryIntelligenceIdentity) -> str:
    return stable_serialize_boundary_intelligence(export_boundary_intelligence_identity(identity))


def serialize_boundary_intelligence_foundations(
    foundations: BoundaryIntelligenceFoundations,
) -> str:
    return stable_serialize_boundary_intelligence(
        export_boundary_intelligence_foundations(foundations)
    )
