"""Canonical serialization for v4.2 coordination readiness certification."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_readiness_models import (
    CoordinationReadinessCertification,
    CoordinationReadinessDiagnostic,
    CoordinationReadinessGovernance,
    CoordinationReadinessIdentity,
    CoordinationReadinessRecord,
    DescriptiveReadinessClassification,
    LayerReadinessReference,
    PhaseEvidenceReference,
    ReadinessStateVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "readiness_approved",
    "operational_authorized",
    "readiness_approval_enabled",
    "operational_authorization_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "drift_correction_enabled",
    "drift_remediation_enabled",
    "continuity_repair_enabled",
    "continuity_inference_enabled",
    "routing_execution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "dependency_resolution_enabled",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_readiness_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_readiness_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_readiness_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_readiness_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_readiness_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_coordination_readiness_identity(identity: CoordinationReadinessIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_phase_evidence_reference(reference: PhaseEvidenceReference) -> dict[str, Any]:
    return _disable_execution_fields(asdict(reference))


def export_layer_readiness_reference(reference: LayerReadinessReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("phase_evidence_reference_ids", "readiness_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_readiness_record(record: CoordinationReadinessRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("source_layers", "phase_evidence_reference_ids", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_readiness_state_visibility(visibility: ReadinessStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("readiness_record_ids", "source_layers", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_descriptive_readiness_classification(
    classification: DescriptiveReadinessClassification,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(classification))
    for field_name in ("readiness_record_ids", "phase_evidence_reference_ids", "classification_reasons"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_readiness_diagnostic(
    diagnostic: CoordinationReadinessDiagnostic,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("readiness_record_ids", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_readiness_governance(governance: CoordinationReadinessGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def _export_layer_references(references: tuple[LayerReadinessReference, ...]) -> list[dict[str, Any]]:
    return [
        export_layer_readiness_reference(reference)
        for reference in sorted(
            references,
            key=lambda item: (item.deterministic_order, item.readiness_reference_id),
        )
    ]


def export_coordination_readiness_certification(
    certification: CoordinationReadinessCertification,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(certification))
    data["identity"] = export_coordination_readiness_identity(certification.identity)
    data["phase_evidence_references"] = [
        export_phase_evidence_reference(reference)
        for reference in sorted(
            certification.phase_evidence_references,
            key=lambda item: (item.deterministic_order, item.phase_evidence_reference_id),
        )
    ]
    data["manifest_readiness_references"] = _export_layer_references(
        certification.manifest_readiness_references
    )
    data["dependency_graph_readiness_references"] = _export_layer_references(
        certification.dependency_graph_readiness_references
    )
    data["lineage_readiness_references"] = _export_layer_references(
        certification.lineage_readiness_references
    )
    data["sequencing_readiness_references"] = _export_layer_references(
        certification.sequencing_readiness_references
    )
    data["routing_readiness_references"] = _export_layer_references(
        certification.routing_readiness_references
    )
    data["drift_readiness_references"] = _export_layer_references(
        certification.drift_readiness_references
    )
    data["diagnostics_explainability_readiness_references"] = _export_layer_references(
        certification.diagnostics_explainability_readiness_references
    )
    data["continuity_readiness_references"] = _export_layer_references(
        certification.continuity_readiness_references
    )
    data["readiness_records"] = [
        export_coordination_readiness_record(record)
        for record in sorted(
            certification.readiness_records,
            key=lambda item: (item.deterministic_order, item.readiness_record_id),
        )
    ]
    data["blocked_readiness_visibility"] = export_readiness_state_visibility(
        certification.blocked_readiness_visibility
    )
    data["prohibited_readiness_visibility"] = export_readiness_state_visibility(
        certification.prohibited_readiness_visibility
    )
    data["unsupported_readiness_visibility"] = export_readiness_state_visibility(
        certification.unsupported_readiness_visibility
    )
    data["stale_readiness_visibility"] = export_readiness_state_visibility(
        certification.stale_readiness_visibility
    )
    data["missing_readiness_visibility"] = export_readiness_state_visibility(
        certification.missing_readiness_visibility
    )
    data["conflicting_readiness_visibility"] = export_readiness_state_visibility(
        certification.conflicting_readiness_visibility
    )
    data["descriptive_readiness_classification"] = export_descriptive_readiness_classification(
        certification.descriptive_readiness_classification
    )
    data["diagnostics"] = [
        export_coordination_readiness_diagnostic(diagnostic)
        for diagnostic in sorted(
            certification.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["governance_visibility"] = export_coordination_readiness_governance(
        certification.governance_visibility
    )
    return data


def serialize_coordination_readiness_identity(identity: CoordinationReadinessIdentity) -> str:
    return stable_serialize(export_coordination_readiness_identity(identity))


def serialize_coordination_readiness_certification(certification: CoordinationReadinessCertification) -> str:
    return stable_serialize(export_coordination_readiness_certification(certification))
