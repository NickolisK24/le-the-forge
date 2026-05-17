"""Canonical serialization for v4.2 coordination continuity certification."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_continuity_models import (
    CoordinationContinuityCertification,
    CoordinationContinuityDiagnostic,
    CoordinationContinuityGovernance,
    CoordinationContinuityIdentity,
    ContinuityStateVisibility,
    CrossLayerContinuitySummary,
    CrossLayerCoordinationContinuityRecord,
    DependencyGraphContinuityReference,
    DiagnosticsContinuityReference,
    DriftContinuityReference,
    ExplainabilityContinuityReference,
    LineageContinuityReference,
    ManifestContinuityReference,
    RoutingContinuityReference,
    SequencingContinuityReference,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "continuity_repair_enabled",
    "continuity_inference_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
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
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "hidden_continuity_repair_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_continuity_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_continuity_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_continuity_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_continuity_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_continuity_evidence(payload),
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


def export_coordination_continuity_identity(identity: CoordinationContinuityIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_manifest_continuity_reference(reference: ManifestContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_dependency_graph_continuity_reference(
    reference: DependencyGraphContinuityReference,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lineage_continuity_reference(reference: LineageContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_sequencing_continuity_reference(reference: SequencingContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_routing_continuity_reference(reference: RoutingContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_drift_continuity_reference(reference: DriftContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_diagnostics_continuity_reference(reference: DiagnosticsContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "diagnostic_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_explainability_continuity_reference(
    reference: ExplainabilityContinuityReference,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("continuity_record_ids", "explanation_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_cross_layer_coordination_continuity_record(
    record: CrossLayerCoordinationContinuityRecord,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("source_layers", "source_reference_ids", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_continuity_state_visibility(visibility: ContinuityStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("continuity_record_ids", "source_layers", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_cross_layer_continuity_summary(summary: CrossLayerContinuitySummary) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(summary))
    for field_name in (
        "continuity_record_ids",
        "involved_layer_references",
        "continuity_state_counts",
        "summary_lines",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_continuity_diagnostic(
    diagnostic: CoordinationContinuityDiagnostic,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("continuity_record_ids", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_continuity_governance(
    governance: CoordinationContinuityGovernance,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_continuity_certification(
    certification: CoordinationContinuityCertification,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(certification))
    data["identity"] = export_coordination_continuity_identity(certification.identity)
    data["manifest_continuity_references"] = [
        export_manifest_continuity_reference(reference)
        for reference in sorted(
            certification.manifest_continuity_references,
            key=lambda item: (item.deterministic_order, item.manifest_continuity_reference_id),
        )
    ]
    data["dependency_graph_continuity_references"] = [
        export_dependency_graph_continuity_reference(reference)
        for reference in sorted(
            certification.dependency_graph_continuity_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_continuity_reference_id),
        )
    ]
    data["lineage_continuity_references"] = [
        export_lineage_continuity_reference(reference)
        for reference in sorted(
            certification.lineage_continuity_references,
            key=lambda item: (item.deterministic_order, item.lineage_continuity_reference_id),
        )
    ]
    data["sequencing_continuity_references"] = [
        export_sequencing_continuity_reference(reference)
        for reference in sorted(
            certification.sequencing_continuity_references,
            key=lambda item: (item.deterministic_order, item.sequencing_continuity_reference_id),
        )
    ]
    data["routing_continuity_references"] = [
        export_routing_continuity_reference(reference)
        for reference in sorted(
            certification.routing_continuity_references,
            key=lambda item: (item.deterministic_order, item.routing_continuity_reference_id),
        )
    ]
    data["drift_continuity_references"] = [
        export_drift_continuity_reference(reference)
        for reference in sorted(
            certification.drift_continuity_references,
            key=lambda item: (item.deterministic_order, item.drift_continuity_reference_id),
        )
    ]
    data["diagnostics_continuity_references"] = [
        export_diagnostics_continuity_reference(reference)
        for reference in sorted(
            certification.diagnostics_continuity_references,
            key=lambda item: (item.deterministic_order, item.diagnostics_continuity_reference_id),
        )
    ]
    data["explainability_continuity_references"] = [
        export_explainability_continuity_reference(reference)
        for reference in sorted(
            certification.explainability_continuity_references,
            key=lambda item: (item.deterministic_order, item.explainability_continuity_reference_id),
        )
    ]
    data["continuity_records"] = [
        export_cross_layer_coordination_continuity_record(record)
        for record in sorted(
            certification.continuity_records,
            key=lambda item: (item.deterministic_order, item.continuity_record_id),
        )
    ]
    data["stale_continuity_visibility"] = export_continuity_state_visibility(
        certification.stale_continuity_visibility
    )
    data["missing_continuity_visibility"] = export_continuity_state_visibility(
        certification.missing_continuity_visibility
    )
    data["conflicting_continuity_visibility"] = export_continuity_state_visibility(
        certification.conflicting_continuity_visibility
    )
    data["prohibited_repair_visibility"] = export_continuity_state_visibility(
        certification.prohibited_repair_visibility
    )
    data["unsupported_transition_visibility"] = export_continuity_state_visibility(
        certification.unsupported_transition_visibility
    )
    data["cross_layer_continuity_summary"] = export_cross_layer_continuity_summary(
        certification.cross_layer_continuity_summary
    )
    data["diagnostics"] = [
        export_coordination_continuity_diagnostic(diagnostic)
        for diagnostic in sorted(
            certification.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["governance_visibility"] = export_coordination_continuity_governance(
        certification.governance_visibility
    )
    return data


def serialize_coordination_continuity_identity(identity: CoordinationContinuityIdentity) -> str:
    return stable_serialize(export_coordination_continuity_identity(identity))


def serialize_coordination_continuity_certification(
    certification: CoordinationContinuityCertification,
) -> str:
    return stable_serialize(export_coordination_continuity_certification(certification))
