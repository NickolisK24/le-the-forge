"""Canonical serialization for v4.2 coordination drift certification."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_drift_models import (
    CoordinationDriftCertification,
    CoordinationDriftDiagnostic,
    CoordinationDriftGovernance,
    CoordinationDriftIdentity,
    CoordinationDriftRecord,
    CrossLayerDriftVisibility,
    DependencyGraphDriftReference,
    DriftStateVisibility,
    LineageDriftReference,
    ManifestDriftReference,
    RoutingDriftReference,
    SequencingDriftReference,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "drift_correction_enabled",
    "drift_remediation_enabled",
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
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "hidden_drift_correction_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_drift_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_drift_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_drift_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_drift_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_drift_evidence(payload),
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


def export_coordination_drift_identity(identity: CoordinationDriftIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_manifest_drift_reference(reference: ManifestDriftReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["drift_record_ids"] = sorted_entries(data["drift_record_ids"])
    return data


def export_dependency_graph_drift_reference(reference: DependencyGraphDriftReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("node_references", "edge_references", "drift_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lineage_drift_reference(reference: LineageDriftReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("lineage_record_references", "drift_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_sequencing_drift_reference(reference: SequencingDriftReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("sequence_record_references", "drift_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_routing_drift_reference(reference: RoutingDriftReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("route_record_references", "drift_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_drift_record(record: CoordinationDriftRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("layer_references", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_drift_state_visibility(visibility: DriftStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("drift_record_ids", "layer_references", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_cross_layer_drift_visibility(visibility: CrossLayerDriftVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("drift_record_ids", "involved_layer_references", "layer_pairs", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_drift_diagnostic(diagnostic: CoordinationDriftDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_drift_record_ids", "affected_layer_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_drift_governance(governance: CoordinationDriftGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_drift_certification(certification: CoordinationDriftCertification) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(certification))
    data["identity"] = export_coordination_drift_identity(certification.identity)
    data["manifest_drift_references"] = [
        export_manifest_drift_reference(reference)
        for reference in sorted(
            certification.manifest_drift_references,
            key=lambda item: (item.deterministic_order, item.manifest_drift_reference_id),
        )
    ]
    data["dependency_graph_drift_references"] = [
        export_dependency_graph_drift_reference(reference)
        for reference in sorted(
            certification.dependency_graph_drift_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_drift_reference_id),
        )
    ]
    data["lineage_drift_references"] = [
        export_lineage_drift_reference(reference)
        for reference in sorted(
            certification.lineage_drift_references,
            key=lambda item: (item.deterministic_order, item.lineage_drift_reference_id),
        )
    ]
    data["sequencing_drift_references"] = [
        export_sequencing_drift_reference(reference)
        for reference in sorted(
            certification.sequencing_drift_references,
            key=lambda item: (item.deterministic_order, item.sequencing_drift_reference_id),
        )
    ]
    data["routing_drift_references"] = [
        export_routing_drift_reference(reference)
        for reference in sorted(
            certification.routing_drift_references,
            key=lambda item: (item.deterministic_order, item.routing_drift_reference_id),
        )
    ]
    data["drift_records"] = [
        export_coordination_drift_record(record)
        for record in sorted(
            certification.drift_records,
            key=lambda item: (item.deterministic_order, item.drift_record_id),
        )
    ]
    data["stale_drift_visibility"] = export_drift_state_visibility(certification.stale_drift_visibility)
    data["missing_drift_visibility"] = export_drift_state_visibility(certification.missing_drift_visibility)
    data["conflicting_drift_visibility"] = export_drift_state_visibility(certification.conflicting_drift_visibility)
    data["prohibited_correction_visibility"] = export_drift_state_visibility(
        certification.prohibited_correction_visibility
    )
    data["unsupported_transition_visibility"] = export_drift_state_visibility(
        certification.unsupported_transition_visibility
    )
    data["cross_layer_drift_visibility"] = export_cross_layer_drift_visibility(
        certification.cross_layer_drift_visibility
    )
    data["diagnostics"] = [
        export_coordination_drift_diagnostic(diagnostic)
        for diagnostic in sorted(
            certification.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["governance_visibility"] = export_coordination_drift_governance(certification.governance_visibility)
    return data


def serialize_coordination_drift_identity(identity: CoordinationDriftIdentity) -> str:
    return stable_serialize(export_coordination_drift_identity(identity))


def serialize_coordination_drift_certification(certification: CoordinationDriftCertification) -> str:
    return stable_serialize(export_coordination_drift_certification(certification))
