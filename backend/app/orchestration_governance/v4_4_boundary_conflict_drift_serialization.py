"""Deterministic serialization for v4.4 boundary conflict drift."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .v4_4_boundary_conflict_drift_models import (
    BoundaryConflictDriftIdentity,
    BoundaryConflictDriftIntelligence,
    BoundaryDriftRecord,
    CompatibilityEvidenceRecord,
    ConflictAncestryVisibility,
    ConflictDiagnosticRecord,
    ConflictExplainabilityRecord,
    ConflictLineageVisibility,
    ContinuityDegradationSummary,
    DriftEvidenceMetadata,
    GovernanceDriftClassification,
    LineageDegradationMetadata,
    ProvenanceDegradationMetadata,
    RefinementDivergenceRecord,
)


def _sorted_tuple(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_boundary_conflict_drift_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_boundary_conflict_drift_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_boundary_conflict_drift_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_boundary_conflict_drift_evidence(value) for value in payload]
    return payload


def stable_serialize_boundary_conflict_drift(payload: Any) -> str:
    return json.dumps(
        canonicalize_boundary_conflict_drift_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def export_boundary_conflict_drift_identity(
    identity: BoundaryConflictDriftIdentity,
) -> dict[str, Any]:
    return asdict(identity)


def export_governance_drift_classification(
    classification: GovernanceDriftClassification,
) -> dict[str, Any]:
    return asdict(classification)


def export_boundary_drift_record(record: BoundaryDriftRecord) -> dict[str, Any]:
    data = asdict(record)
    data["drift_chain_ids"] = _sorted_tuple(data["drift_chain_ids"])
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_refinement_divergence_record(record: RefinementDivergenceRecord) -> dict[str, Any]:
    data = asdict(record)
    data["divergence_chain_ids"] = _sorted_tuple(data["divergence_chain_ids"])
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_conflict_diagnostic(record: ConflictDiagnosticRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_compatibility_evidence(record: CompatibilityEvidenceRecord) -> dict[str, Any]:
    data = asdict(record)
    data["evidence_reference_ids"] = _sorted_tuple(data["evidence_reference_ids"])
    return data


def export_degradation_summary(summary: ContinuityDegradationSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["affected_relationship_ids"] = _sorted_tuple(data["affected_relationship_ids"])
    return data


def export_conflict_explainability(record: ConflictExplainabilityRecord) -> dict[str, Any]:
    data = asdict(record)
    data["explanation_chain_ids"] = _sorted_tuple(data["explanation_chain_ids"])
    return data


def export_conflict_lineage_visibility(record: ConflictLineageVisibility) -> dict[str, Any]:
    data = asdict(record)
    data["lineage_reference_ids"] = _sorted_tuple(data["lineage_reference_ids"])
    return data


def export_conflict_ancestry_visibility(record: ConflictAncestryVisibility) -> dict[str, Any]:
    data = asdict(record)
    data["ancestry_reference_ids"] = _sorted_tuple(data["ancestry_reference_ids"])
    return data


def export_provenance_degradation_metadata(
    metadata: ProvenanceDegradationMetadata,
) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "source_reference_ids",
        "source_hash_references",
        "degradation_reference_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_lineage_degradation_metadata(metadata: LineageDegradationMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "lineage_reference_ids",
        "lineage_hash_references",
        "degradation_reference_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_drift_evidence_metadata(metadata: DriftEvidenceMetadata) -> dict[str, Any]:
    data = asdict(metadata)
    for field_name in (
        "drift_record_ids",
        "divergence_record_ids",
        "compatibility_record_ids",
        "replay_evidence_ids",
        "rollback_evidence_ids",
    ):
        data[field_name] = _sorted_tuple(data[field_name])
    return data


def export_boundary_conflict_drift_intelligence(
    intelligence: BoundaryConflictDriftIntelligence,
) -> dict[str, Any]:
    data = asdict(intelligence)
    data["identity"] = export_boundary_conflict_drift_identity(intelligence.identity)
    data["classifications"] = [
        export_governance_drift_classification(classification)
        for classification in sorted(
            intelligence.classifications,
            key=lambda item: (item.deterministic_order, item.classification_id),
        )
    ]
    data["drift_records"] = [
        export_boundary_drift_record(record)
        for record in sorted(
            intelligence.drift_records,
            key=lambda item: (item.deterministic_order, item.drift_id),
        )
    ]
    data["divergence_records"] = [
        export_refinement_divergence_record(record)
        for record in sorted(
            intelligence.divergence_records,
            key=lambda item: (item.deterministic_order, item.divergence_id),
        )
    ]
    data["conflict_diagnostics"] = [
        export_conflict_diagnostic(record)
        for record in sorted(
            intelligence.conflict_diagnostics,
            key=lambda item: (item.deterministic_order, item.conflict_id),
        )
    ]
    data["compatibility_evidence"] = [
        export_compatibility_evidence(record)
        for record in sorted(
            intelligence.compatibility_evidence,
            key=lambda item: (item.deterministic_order, item.compatibility_id),
        )
    ]
    data["degradation_summaries"] = [
        export_degradation_summary(summary)
        for summary in sorted(
            intelligence.degradation_summaries,
            key=lambda item: (item.deterministic_order, item.degradation_id),
        )
    ]
    data["explainability"] = [
        export_conflict_explainability(record)
        for record in sorted(
            intelligence.explainability,
            key=lambda item: (item.deterministic_order, item.explainability_id),
        )
    ]
    data["conflict_lineage_visibility"] = [
        export_conflict_lineage_visibility(record)
        for record in sorted(
            intelligence.conflict_lineage_visibility,
            key=lambda item: (item.deterministic_order, item.lineage_visibility_id),
        )
    ]
    data["conflict_ancestry_visibility"] = [
        export_conflict_ancestry_visibility(record)
        for record in sorted(
            intelligence.conflict_ancestry_visibility,
            key=lambda item: (item.deterministic_order, item.ancestry_visibility_id),
        )
    ]
    data["provenance_degradation_metadata"] = export_provenance_degradation_metadata(
        intelligence.provenance_degradation_metadata
    )
    data["lineage_degradation_metadata"] = export_lineage_degradation_metadata(
        intelligence.lineage_degradation_metadata
    )
    data["drift_evidence_metadata"] = export_drift_evidence_metadata(
        intelligence.drift_evidence_metadata
    )
    data["deterministic_guarantees"] = _sorted_tuple(data["deterministic_guarantees"])
    data["explicit_limitations"] = _sorted_tuple(data["explicit_limitations"])
    data["explicit_prohibitions"] = _sorted_tuple(data["explicit_prohibitions"])
    return data


def serialize_boundary_conflict_drift_identity(identity: BoundaryConflictDriftIdentity) -> str:
    return stable_serialize_boundary_conflict_drift(export_boundary_conflict_drift_identity(identity))


def serialize_boundary_conflict_drift_intelligence(
    intelligence: BoundaryConflictDriftIntelligence,
) -> str:
    return stable_serialize_boundary_conflict_drift(
        export_boundary_conflict_drift_intelligence(intelligence)
    )
