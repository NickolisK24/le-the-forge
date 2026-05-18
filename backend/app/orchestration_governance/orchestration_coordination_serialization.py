"""Deterministic serialization for v4.3 orchestration coordination visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_coordination_models import (
    CoordinationContinuityMetadata,
    CoordinationDiagnostic,
    CoordinationExplainability,
    CoordinationParticipant,
    CoordinationRecord,
    CoordinationRelationship,
    CoordinationSupportStateVisibility,
    CoordinationVisibilityIdentity,
    CoordinationVisibilityMetadata,
    OrchestrationCoordinationVisibility,
)


COORDINATION_DISABLED_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "coordination_execution_enabled",
    "orchestration_execution_enabled",
    "operational_coordination_enabled",
    "runtime_coordination_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_activation_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "state_machine_execution_enabled",
    "transition_execution_enabled",
    "coordination_authorization_enabled",
    "readiness_approval_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_coordination_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "orchestration_coordination_engine_enabled",
    "dispatcher_enabled",
    "runtime_coordinator_enabled",
    "operational_state_machine_enabled",
    "operational_capability_enabled",
    "policy_enforcement_enabled",
    "executable",
    "dispatch_capable",
    "activation_capable",
    "planner_integrated",
    "production_consuming",
    "operationally_routable",
    "schedulable",
    "routable",
    "traversable",
    "execution_enabled",
    "dispatch_enabled",
    "authorization_enabled",
    "mutation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_operational_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in COORDINATION_DISABLED_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_coordination_visibility_identity(identity: CoordinationVisibilityIdentity) -> dict[str, Any]:
    return _disable_operational_fields(asdict(identity))


def export_coordination_visibility_metadata(metadata: CoordinationVisibilityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_record(coordination: CoordinationRecord) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(coordination))
    for field_name in (
        "participant_ids",
        "prohibited_reason_visibility",
        "unsupported_reason_visibility",
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "conflicting_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_participant(participant: CoordinationParticipant) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(participant))
    data["coordination_ids"] = sorted_entries(data["coordination_ids"])
    return data


def export_coordination_relationship(relationship: CoordinationRelationship) -> dict[str, Any]:
    return _disable_operational_fields(asdict(relationship))


def export_coordination_support_state_visibility(
    visibility: CoordinationSupportStateVisibility,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    for field_name in (
        "prohibited_coordination_ids",
        "unsupported_coordination_ids",
        "blocked_coordination_ids",
        "stale_coordination_ids",
        "conflicting_coordination_ids",
        "unknown_coordination_ids",
        "prohibited_classifications",
        "unsupported_classifications",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_continuity_metadata(metadata: CoordinationContinuityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("coordination_references", "participant_references", "relationship_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_diagnostic(diagnostic: CoordinationDiagnostic) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(diagnostic))
    for field_name in ("affected_coordination_ids", "affected_participant_ids", "affected_relationship_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_explainability(summary: CoordinationExplainability) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    data["affected_coordination_ids"] = sorted_entries(data["affected_coordination_ids"])
    return data


def export_orchestration_coordination_visibility(
    visibility: OrchestrationCoordinationVisibility,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    data["identity"] = export_coordination_visibility_identity(visibility.identity)
    data["metadata"] = export_coordination_visibility_metadata(visibility.metadata)
    data["coordinations"] = [
        export_coordination_record(coordination)
        for coordination in sorted(
            visibility.coordinations,
            key=lambda item: (item.deterministic_order, item.coordination_id),
        )
    ]
    data["participants"] = [
        export_coordination_participant(participant)
        for participant in sorted(
            visibility.participants,
            key=lambda item: (item.deterministic_order, item.participant_id),
        )
    ]
    data["relationships"] = [
        export_coordination_relationship(relationship)
        for relationship in sorted(
            visibility.relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["support_state_visibility"] = export_coordination_support_state_visibility(
        visibility.support_state_visibility
    )
    data["continuity_metadata"] = [
        export_coordination_continuity_metadata(metadata)
        for metadata in sorted(
            visibility.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_coordination_diagnostic(diagnostic)
        for diagnostic in sorted(
            visibility.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explainability_summaries"] = [
        export_coordination_explainability(summary)
        for summary in sorted(
            visibility.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_coordination_visibility_identity(identity: CoordinationVisibilityIdentity) -> str:
    return stable_serialize(export_coordination_visibility_identity(identity))


def serialize_orchestration_coordination_visibility(visibility: OrchestrationCoordinationVisibility) -> str:
    return stable_serialize(export_orchestration_coordination_visibility(visibility))
