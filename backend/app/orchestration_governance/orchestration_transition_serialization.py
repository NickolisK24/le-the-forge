"""Deterministic serialization for v4.3 orchestration transition visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_transition_models import (
    OrchestrationTransitionVisibility,
    TransitionContinuityMetadata,
    TransitionDiagnostic,
    TransitionExplainability,
    TransitionRecord,
    TransitionRelationship,
    TransitionSupportStateVisibility,
    TransitionVisibilityIdentity,
    TransitionVisibilityMetadata,
)


TRANSITION_DISABLED_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "transition_execution_enabled",
    "orchestration_execution_enabled",
    "state_machine_execution_enabled",
    "runtime_execution_enabled",
    "orchestration_activation_enabled",
    "state_progression_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "transition_authorization_enabled",
    "readiness_approval_enabled",
    "transition_dispatch_enabled",
    "operational_coordination_enabled",
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
    "hidden_transition_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "transition_engine_enabled",
    "orchestration_runtime_enabled",
    "executable_state_machine_enabled",
    "orchestration_dispatcher_enabled",
    "operational_capability_enabled",
    "policy_enforcement_enabled",
    "executable",
    "activation_capable",
    "planner_integrated",
    "production_consuming",
    "operationally_routable",
    "schedulable",
    "routable",
    "traversable",
    "execution_enabled",
    "authorization_enabled",
    "mutation_enabled",
    "activation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_transition_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_transition_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_transition_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_transition_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_transition_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_operational_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in TRANSITION_DISABLED_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_transition_visibility_identity(identity: TransitionVisibilityIdentity) -> dict[str, Any]:
    return _disable_operational_fields(asdict(identity))


def export_transition_visibility_metadata(metadata: TransitionVisibilityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_record(transition: TransitionRecord) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(transition))
    for field_name in (
        "prohibited_reason_visibility",
        "unsupported_reason_visibility",
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "conflicting_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_relationship(relationship: TransitionRelationship) -> dict[str, Any]:
    return _disable_operational_fields(asdict(relationship))


def export_transition_support_state_visibility(
    visibility: TransitionSupportStateVisibility,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    for field_name in (
        "prohibited_transition_ids",
        "unsupported_transition_ids",
        "blocked_transition_ids",
        "stale_transition_ids",
        "conflicting_transition_ids",
        "unknown_transition_ids",
        "prohibited_classifications",
        "unsupported_classifications",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_continuity_metadata(metadata: TransitionContinuityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in (
        "transition_references",
        "relationship_references",
        "source_state_references",
        "target_state_references",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_diagnostic(diagnostic: TransitionDiagnostic) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(diagnostic))
    for field_name in ("affected_transition_ids", "affected_relationship_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_explainability(summary: TransitionExplainability) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    data["affected_transition_ids"] = sorted_entries(data["affected_transition_ids"])
    return data


def export_orchestration_transition_visibility(
    visibility: OrchestrationTransitionVisibility,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    data["identity"] = export_transition_visibility_identity(visibility.identity)
    data["metadata"] = export_transition_visibility_metadata(visibility.metadata)
    data["transitions"] = [
        export_transition_record(transition)
        for transition in sorted(
            visibility.transitions,
            key=lambda item: (item.deterministic_order, item.transition_id),
        )
    ]
    data["relationships"] = [
        export_transition_relationship(relationship)
        for relationship in sorted(
            visibility.relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["support_state_visibility"] = export_transition_support_state_visibility(
        visibility.support_state_visibility
    )
    data["continuity_metadata"] = [
        export_transition_continuity_metadata(metadata)
        for metadata in sorted(
            visibility.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_transition_diagnostic(diagnostic)
        for diagnostic in sorted(
            visibility.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explainability_summaries"] = [
        export_transition_explainability(summary)
        for summary in sorted(
            visibility.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_transition_visibility_identity(identity: TransitionVisibilityIdentity) -> str:
    return stable_serialize(export_transition_visibility_identity(identity))


def serialize_orchestration_transition_visibility(visibility: OrchestrationTransitionVisibility) -> str:
    return stable_serialize(export_orchestration_transition_visibility(visibility))
