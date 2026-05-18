"""Deterministic serialization for v4.4 cross-boundary consistency."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_cross_boundary_consistency_models import (
    CompatibilityConsistencySummary,
    ConsistencyEvidenceMetadata,
    ConsistencyExplainabilityRecord,
    ConsistencyRecord,
    ContinuityConsistencySummary,
    CrossBoundaryConsistencyIdentity,
    CrossBoundaryConsistencyIntelligence,
    CrossBoundaryDiagnosticRecord,
    GovernanceConsistencyClassification,
    LineageConsistencySummary,
    MultiBoundaryRelationshipRecord,
    ProvenanceConsistencySummary,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_cross_boundary_consistency_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_cross_boundary_consistency_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_cross_boundary_consistency_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_cross_boundary_consistency_evidence(value) for value in payload]
    return payload


def stable_serialize_cross_boundary_consistency(payload: Any) -> str:
    return json.dumps(
        canonicalize_cross_boundary_consistency_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_cross_boundary_consistency_identity(
    identity: CrossBoundaryConsistencyIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_governance_consistency_classification(
    classification: GovernanceConsistencyClassification,
) -> dict[str, Any]:
    return asdict(classification)


def export_consistency_record(record: ConsistencyRecord) -> dict[str, Any]:
    data = asdict(record)
    data["related_boundary_ids"] = _sorted_tuple(data["related_boundary_ids"])
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_multi_boundary_relationship_record(
    record: MultiBoundaryRelationshipRecord,
) -> dict[str, Any]:
    data = asdict(record)
    data["relationship_chain_ids"] = _sorted_tuple(data["relationship_chain_ids"])
    return data


def export_cross_boundary_diagnostic(record: CrossBoundaryDiagnosticRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_compatibility_consistency(summary: CompatibilityConsistencySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_continuity_consistency(summary: ContinuityConsistencySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["affected_boundary_ids"] = _sorted_tuple(data["affected_boundary_ids"])
    return data


def export_provenance_consistency(summary: ProvenanceConsistencySummary) -> dict[str, Any]:
    data = asdict(summary)
    for field_name in ("source_reference_ids", "source_hash_references", "consistency_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_lineage_consistency(summary: LineageConsistencySummary) -> dict[str, Any]:
    data = asdict(summary)
    for field_name in ("lineage_reference_ids", "lineage_hash_references", "consistency_reference_ids"):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_consistency_explainability(record: ConsistencyExplainabilityRecord) -> dict[str, Any]:
    data = asdict(record)
    data["explanation_chain_ids"] = _sorted_tuple(data["explanation_chain_ids"])
    return data


def export_consistency_evidence_metadata(metadata: ConsistencyEvidenceMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "consistency_record_ids",
        "relationship_record_ids",
        "diagnostic_record_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_cross_boundary_consistency_intelligence(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_cross_boundary_consistency_identity(intelligence.identity)
    data["classifications"] = [
        export_governance_consistency_classification(classification)
        for classification in sorted(
            intelligence.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["consistency_records"] = [
        export_consistency_record(record)
        for record in sorted(
            intelligence.consistency_records,
            key=lambda item: (item.deterministic_order, item.consistency_record_id),
        )
    ]
    data["relationship_records"] = [
        export_multi_boundary_relationship_record(record)
        for record in sorted(
            intelligence.relationship_records,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["diagnostics"] = [
        export_cross_boundary_diagnostic(record)
        for record in sorted(
            intelligence.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["compatibility_consistency"] = [
        export_compatibility_consistency(summary)
        for summary in sorted(
            intelligence.compatibility_consistency,
            key=lambda item: (item.deterministic_order, item.compatibility_id),
        )
    ]
    data["continuity_consistency"] = [
        export_continuity_consistency(summary)
        for summary in sorted(
            intelligence.continuity_consistency,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["provenance_consistency"] = export_provenance_consistency(
        intelligence.provenance_consistency
    )
    data["lineage_consistency"] = export_lineage_consistency(intelligence.lineage_consistency)
    data["explainability"] = [
        export_consistency_explainability(record)
        for record in sorted(
            intelligence.explainability,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["evidence_metadata"] = export_consistency_evidence_metadata(
        intelligence.evidence_metadata
    )
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_cross_boundary_consistency_identity(
    identity: CrossBoundaryConsistencyIdentity,
) -> str:
    return stable_serialize_cross_boundary_consistency(
        export_cross_boundary_consistency_identity(identity)
    )


def serialize_cross_boundary_consistency_intelligence(
    intelligence: CrossBoundaryConsistencyIntelligence,
) -> str:
    return stable_serialize_cross_boundary_consistency(
        export_cross_boundary_consistency_intelligence(intelligence)
    )
