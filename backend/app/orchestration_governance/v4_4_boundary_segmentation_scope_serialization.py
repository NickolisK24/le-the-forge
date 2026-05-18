"""Deterministic serialization for v4.4 boundary segmentation scope."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_segmentation_scope_models import (
    BoundaryScopeRecord,
    BoundarySegmentRecord,
    BoundarySegmentationScopeIdentity,
    BoundarySegmentationScopeIntelligence,
    ScopeClassification,
    ScopeDiagnosticRecord,
    ScopeLineageVisibility,
    ScopeProvenanceVisibility,
    ScopedBoundaryMembershipRecord,
    SegmentContinuityVisibility,
    SegmentRelationshipRecord,
    SegmentationClassification,
    SegmentationDiagnosticRecord,
    SegmentationExplainabilityRecord,
    SegmentationScopeEvidenceMetadata,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_segmentation_scope_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_segmentation_scope_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_segmentation_scope_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_segmentation_scope_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_segmentation_scope(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_segmentation_scope_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_boundary_segmentation_scope_identity(
    identity: BoundarySegmentationScopeIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_segmentation_classification(classification: SegmentationClassification) -> dict[str, Any]:
    return asdict(classification)


def export_scope_classification(classification: ScopeClassification) -> dict[str, Any]:
    return asdict(classification)


def export_boundary_segment_record(record: BoundarySegmentRecord) -> dict[str, Any]:
    data = asdict(record)
    data["grouped_boundary_ids"] = _sorted_tuple(data["grouped_boundary_ids"])
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_boundary_scope_record(record: BoundaryScopeRecord) -> dict[str, Any]:
    data = asdict(record)
    data["scoped_governance_ids"] = _sorted_tuple(data["scoped_governance_ids"])
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_scoped_boundary_membership(record: ScopedBoundaryMembershipRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_segment_relationship(record: SegmentRelationshipRecord) -> dict[str, Any]:
    data = asdict(record)
    data["relationship_boundary_ids"] = _sorted_tuple(data["relationship_boundary_ids"])
    return data


def export_segment_continuity_visibility(record: SegmentContinuityVisibility) -> dict[str, Any]:
    data = asdict(record)
    data["continuity_reference_ids"] = _sorted_tuple(data["continuity_reference_ids"])
    return data


def export_scope_diagnostic(record: ScopeDiagnosticRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_segmentation_diagnostic(record: SegmentationDiagnosticRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_scope_provenance_visibility(record: ScopeProvenanceVisibility) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("source_reference_ids", "source_hash_references", "scope_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_scope_lineage_visibility(record: ScopeLineageVisibility) -> dict[str, Any]:
    data = asdict(record)
    for field_name in ("lineage_reference_ids", "lineage_hash_references", "segment_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_segmentation_explainability(record: SegmentationExplainabilityRecord) -> dict[str, Any]:
    data = asdict(record)
    data["explanation_chain_ids"] = _sorted_tuple(data["explanation_chain_ids"])
    return data


def export_segmentation_scope_evidence_metadata(
    metadata: SegmentationScopeEvidenceMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "segment_record_ids",
        "scope_record_ids",
        "membership_record_ids",
        "relationship_record_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_boundary_segmentation_scope_intelligence(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_boundary_segmentation_scope_identity(intelligence.identity)
    data["segmentation_classifications"] = [
        export_segmentation_classification(classification)
        for classification in sorted(
            intelligence.segmentation_classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["scope_classifications"] = [
        export_scope_classification(classification)
        for classification in sorted(
            intelligence.scope_classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["segment_records"] = [
        export_boundary_segment_record(record)
        for record in sorted(
            intelligence.segment_records,
            key=lambda item: (item.deterministic_order, item.segment_id),
        )
    ]
    data["scope_records"] = [
        export_boundary_scope_record(record)
        for record in sorted(
            intelligence.scope_records,
            key=lambda item: (item.deterministic_order, item.scope_id),
        )
    ]
    data["membership_records"] = [
        export_scoped_boundary_membership(record)
        for record in sorted(
            intelligence.membership_records,
            key=lambda item: (item.deterministic_order, item.membership_id),
        )
    ]
    data["relationship_records"] = [
        export_segment_relationship(record)
        for record in sorted(
            intelligence.relationship_records,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["continuity_visibility"] = [
        export_segment_continuity_visibility(record)
        for record in sorted(
            intelligence.continuity_visibility,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["scope_diagnostics"] = [
        export_scope_diagnostic(record)
        for record in sorted(
            intelligence.scope_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["segmentation_diagnostics"] = [
        export_segmentation_diagnostic(record)
        for record in sorted(
            intelligence.segmentation_diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["provenance_visibility"] = export_scope_provenance_visibility(
        intelligence.provenance_visibility
    )
    data["lineage_visibility"] = export_scope_lineage_visibility(intelligence.lineage_visibility)
    data["explainability"] = [
        export_segmentation_explainability(record)
        for record in sorted(
            intelligence.explainability,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["evidence_metadata"] = export_segmentation_scope_evidence_metadata(
        intelligence.evidence_metadata
    )
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_boundary_segmentation_scope_identity(
    identity: BoundarySegmentationScopeIdentity,
) -> str:
    return stable_serialize_boundary_segmentation_scope(
        export_boundary_segmentation_scope_identity(identity)
    )


def serialize_boundary_segmentation_scope_intelligence(
    intelligence: BoundarySegmentationScopeIntelligence,
) -> str:
    return stable_serialize_boundary_segmentation_scope(
        export_boundary_segmentation_scope_intelligence(intelligence)
    )
