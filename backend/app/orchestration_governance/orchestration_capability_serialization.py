"""Deterministic serialization for v4.3 orchestration capability visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_capability_models import (
    CapabilityContinuityMetadata,
    CapabilityDiagnostic,
    CapabilityExplainability,
    CapabilityGovernanceBoundary,
    CapabilityRecord,
    CapabilityRelationship,
    CapabilitySupportStateVisibility,
    CapabilityVisibilityIdentity,
    CapabilityVisibilityMetadata,
    OrchestrationCapabilityVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "orchestration_activation_enabled",
    "runtime_execution_enabled",
    "capability_execution_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "dependency_execution_enabled",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "operational_state_mutation_enabled",
    "runtime_mutation_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "remediation_system_enabled",
    "automatic_repair_enabled",
    "inference_system_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_system_enabled",
    "resolution_system_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "orchestration_dispatch_enabled",
    "runtime_coordination_enabled",
    "state_machine_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "operational_orchestration_engine_enabled",
    "orchestration_decision_engine_enabled",
    "executable",
    "operationally_enabled",
    "authorized",
    "schedulable",
    "routable",
    "planner_integrated",
    "traversable",
    "correction_enabled",
    "inference_enabled",
    "authorization_enabled",
    "operational_mutation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_capability_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_capability_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_capability_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_capability_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_capability_evidence(payload),
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


def export_capability_visibility_identity(identity: CapabilityVisibilityIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_capability_visibility_metadata(metadata: CapabilityVisibilityMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_record(capability: CapabilityRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(capability))
    for field_name in (
        "prohibited_reason_visibility",
        "unsupported_reason_visibility",
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "conflicting_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_boundary(boundary: CapabilityGovernanceBoundary) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(boundary))
    for field_name in ("capability_ids", "prohibited_capability_ids", "unsupported_capability_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_relationship(relationship: CapabilityRelationship) -> dict[str, Any]:
    return _disable_execution_fields(asdict(relationship))


def export_capability_support_state_visibility(
    visibility: CapabilitySupportStateVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "prohibited_capability_ids",
        "unsupported_capability_ids",
        "blocked_capability_ids",
        "stale_capability_ids",
        "conflicting_capability_ids",
        "unknown_capability_ids",
        "prohibited_classifications",
        "unsupported_classifications",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_continuity_metadata(metadata: CapabilityContinuityMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("capability_references", "boundary_references", "relationship_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_diagnostic(diagnostic: CapabilityDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_capability_ids", "affected_boundary_ids", "affected_relationship_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_capability_explainability(summary: CapabilityExplainability) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(summary))
    data["affected_capability_ids"] = sorted_entries(data["affected_capability_ids"])
    return data


def export_orchestration_capability_visibility(
    visibility: OrchestrationCapabilityVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    data["identity"] = export_capability_visibility_identity(visibility.identity)
    data["metadata"] = export_capability_visibility_metadata(visibility.metadata)
    data["capabilities"] = [
        export_capability_record(capability)
        for capability in sorted(
            visibility.capabilities,
            key=lambda item: (item.deterministic_order, item.capability_id),
        )
    ]
    data["boundaries"] = [
        export_capability_boundary(boundary)
        for boundary in sorted(visibility.boundaries, key=lambda item: (item.deterministic_order, item.boundary_id))
    ]
    data["relationships"] = [
        export_capability_relationship(relationship)
        for relationship in sorted(
            visibility.relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["support_state_visibility"] = export_capability_support_state_visibility(
        visibility.support_state_visibility
    )
    data["continuity_metadata"] = [
        export_capability_continuity_metadata(metadata)
        for metadata in sorted(
            visibility.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_capability_diagnostic(diagnostic)
        for diagnostic in sorted(visibility.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["explainability_summaries"] = [
        export_capability_explainability(summary)
        for summary in sorted(
            visibility.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_capability_visibility_identity(identity: CapabilityVisibilityIdentity) -> str:
    return stable_serialize(export_capability_visibility_identity(identity))


def serialize_orchestration_capability_visibility(visibility: OrchestrationCapabilityVisibility) -> str:
    return stable_serialize(export_orchestration_capability_visibility(visibility))
