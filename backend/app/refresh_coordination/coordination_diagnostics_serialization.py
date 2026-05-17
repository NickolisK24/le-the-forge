"""Canonical serialization for v4.2 coordination diagnostics explainability."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_diagnostics_models import (
    CoordinationDiagnosticsExplainability,
    CoordinationDiagnosticsGovernance,
    CoordinationDiagnosticsIdentity,
    CoordinationExplanationRecord,
    CrossLayerCoordinationDiagnosticRecord,
    DependencyGraphDiagnosticReference,
    DiagnosticSeverityVisibility,
    DriftDiagnosticReference,
    FailVisibleExplanationSummary,
    LineageDiagnosticReference,
    ManifestDiagnosticReference,
    RoutingDiagnosticReference,
    SequencingDiagnosticReference,
    StateAggregationVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
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
    "hidden_correction_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_diagnostics_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_diagnostics_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_diagnostics_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_diagnostics_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_diagnostics_evidence(payload),
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


def export_coordination_diagnostics_identity(identity: CoordinationDiagnosticsIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_manifest_diagnostic_reference(reference: ManifestDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_dependency_graph_diagnostic_reference(reference: DependencyGraphDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_lineage_diagnostic_reference(reference: LineageDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_sequencing_diagnostic_reference(reference: SequencingDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_routing_diagnostic_reference(reference: RoutingDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_drift_diagnostic_reference(reference: DriftDiagnosticReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["diagnostic_ids"] = sorted_entries(data["diagnostic_ids"])
    return data


def export_cross_layer_coordination_diagnostic_record(
    record: CrossLayerCoordinationDiagnosticRecord,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("source_layers", "source_diagnostic_ids", "layer_references", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_state_aggregation_visibility(visibility: StateAggregationVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("diagnostic_record_ids", "source_layers", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_diagnostic_severity_visibility(visibility: DiagnosticSeverityVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    data["diagnostic_record_ids"] = sorted_entries(data["diagnostic_record_ids"])
    return data


def export_coordination_explanation_record(record: CoordinationExplanationRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_fail_visible_explanation_summary(summary: FailVisibleExplanationSummary) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(summary))
    for field_name in ("explanation_ids", "diagnostic_record_ids", "aggregation_state_counts", "summary_lines"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_diagnostics_governance(governance: CoordinationDiagnosticsGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_diagnostics_explainability(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostics))
    data["identity"] = export_coordination_diagnostics_identity(diagnostics.identity)
    data["manifest_diagnostic_references"] = [
        export_manifest_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.manifest_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.manifest_diagnostic_reference_id),
        )
    ]
    data["dependency_graph_diagnostic_references"] = [
        export_dependency_graph_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.dependency_graph_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_diagnostic_reference_id),
        )
    ]
    data["lineage_diagnostic_references"] = [
        export_lineage_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.lineage_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.lineage_diagnostic_reference_id),
        )
    ]
    data["sequencing_diagnostic_references"] = [
        export_sequencing_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.sequencing_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.sequencing_diagnostic_reference_id),
        )
    ]
    data["routing_diagnostic_references"] = [
        export_routing_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.routing_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.routing_diagnostic_reference_id),
        )
    ]
    data["drift_diagnostic_references"] = [
        export_drift_diagnostic_reference(reference)
        for reference in sorted(
            diagnostics.drift_diagnostic_references,
            key=lambda item: (item.deterministic_order, item.drift_diagnostic_reference_id),
        )
    ]
    data["diagnostic_records"] = [
        export_cross_layer_coordination_diagnostic_record(record)
        for record in sorted(
            diagnostics.diagnostic_records,
            key=lambda item: (item.deterministic_order, item.diagnostic_record_id),
        )
    ]
    data["unsupported_state_aggregation"] = export_state_aggregation_visibility(
        diagnostics.unsupported_state_aggregation
    )
    data["prohibited_state_aggregation"] = export_state_aggregation_visibility(
        diagnostics.prohibited_state_aggregation
    )
    data["blocked_state_aggregation"] = export_state_aggregation_visibility(diagnostics.blocked_state_aggregation)
    data["stale_state_aggregation"] = export_state_aggregation_visibility(diagnostics.stale_state_aggregation)
    data["missing_state_aggregation"] = export_state_aggregation_visibility(diagnostics.missing_state_aggregation)
    data["conflicting_state_aggregation"] = export_state_aggregation_visibility(
        diagnostics.conflicting_state_aggregation
    )
    data["severity_visibility"] = [
        export_diagnostic_severity_visibility(visibility)
        for visibility in sorted(
            diagnostics.severity_visibility,
            key=lambda item: (item.deterministic_order, item.severity_visibility_id),
        )
    ]
    data["explanation_records"] = [
        export_coordination_explanation_record(record)
        for record in sorted(
            diagnostics.explanation_records,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["fail_visible_explanation_summary"] = export_fail_visible_explanation_summary(
        diagnostics.fail_visible_explanation_summary
    )
    data["governance_visibility"] = export_coordination_diagnostics_governance(
        diagnostics.governance_visibility
    )
    return data


def serialize_coordination_diagnostics_identity(identity: CoordinationDiagnosticsIdentity) -> str:
    return stable_serialize(export_coordination_diagnostics_identity(identity))


def serialize_coordination_diagnostics_explainability(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> str:
    return stable_serialize(export_coordination_diagnostics_explainability(diagnostics))
