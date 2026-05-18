"""Deterministic serialization for v4.3 orchestration policy visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_policy_models import (
    OrchestrationPolicyVisibility,
    PolicyContinuityMetadata,
    PolicyDiagnostic,
    PolicyExplainability,
    PolicyRecord,
    PolicyRelationship,
    PolicySupportStateVisibility,
    PolicyTarget,
    PolicyVisibilityIdentity,
    PolicyVisibilityMetadata,
)


POLICY_DISABLED_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "policy_enforcement_enabled",
    "policy_enforcement_execution_enabled",
    "orchestration_execution_enabled",
    "runtime_execution_enabled",
    "policy_driven_routing_enabled",
    "policy_driven_traversal_enabled",
    "policy_driven_scheduling_enabled",
    "policy_driven_sequencing_enabled",
    "policy_driven_dependency_resolution_enabled",
    "policy_driven_activation_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "operational_policy_mutation_enabled",
    "runtime_mutation_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "dispatch_enabled",
    "operational_coordination_enabled",
    "state_machine_enabled",
    "hidden_enforcement_path_enabled",
    "implicit_operational_authorization_enabled",
    "policy_engine_execution_enabled",
    "orchestration_engine_enabled",
    "authorization_engine_enabled",
    "activation_pathway_enabled",
    "operational_capability_enabled",
    "executable",
    "enforceable",
    "authorizing",
    "activation_capable",
    "routable",
    "traversable",
    "schedulable",
    "planner_integrated",
    "production_consuming",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "authorization_enabled",
    "operational_mutation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_policy_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_policy_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_policy_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_policy_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_policy_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_operational_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in POLICY_DISABLED_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_policy_visibility_identity(identity: PolicyVisibilityIdentity) -> dict[str, Any]:
    return _disable_operational_fields(asdict(identity))


def export_policy_visibility_metadata(metadata: PolicyVisibilityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_policy_record(policy: PolicyRecord) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(policy))
    for field_name in (
        "target_ids",
        "prohibited_reason_visibility",
        "unsupported_reason_visibility",
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "conflicting_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_policy_target(target: PolicyTarget) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(target))
    data["policy_ids"] = sorted_entries(data["policy_ids"])
    return data


def export_policy_relationship(relationship: PolicyRelationship) -> dict[str, Any]:
    return _disable_operational_fields(asdict(relationship))


def export_policy_support_state_visibility(visibility: PolicySupportStateVisibility) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    for field_name in (
        "prohibited_policy_ids",
        "unsupported_policy_ids",
        "blocked_policy_ids",
        "stale_policy_ids",
        "conflicting_policy_ids",
        "unknown_policy_ids",
        "prohibited_classifications",
        "unsupported_classifications",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_policy_continuity_metadata(metadata: PolicyContinuityMetadata) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("policy_references", "target_references", "relationship_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_policy_diagnostic(diagnostic: PolicyDiagnostic) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(diagnostic))
    for field_name in ("affected_policy_ids", "affected_target_ids", "affected_relationship_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_policy_explainability(summary: PolicyExplainability) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    data["affected_policy_ids"] = sorted_entries(data["affected_policy_ids"])
    return data


def export_orchestration_policy_visibility(
    visibility: OrchestrationPolicyVisibility,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(visibility))
    data["identity"] = export_policy_visibility_identity(visibility.identity)
    data["metadata"] = export_policy_visibility_metadata(visibility.metadata)
    data["policies"] = [
        export_policy_record(policy)
        for policy in sorted(visibility.policies, key=lambda item: (item.deterministic_order, item.policy_id))
    ]
    data["targets"] = [
        export_policy_target(target)
        for target in sorted(visibility.targets, key=lambda item: (item.deterministic_order, item.target_id))
    ]
    data["relationships"] = [
        export_policy_relationship(relationship)
        for relationship in sorted(
            visibility.relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["support_state_visibility"] = export_policy_support_state_visibility(
        visibility.support_state_visibility
    )
    data["continuity_metadata"] = [
        export_policy_continuity_metadata(metadata)
        for metadata in sorted(
            visibility.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_policy_diagnostic(diagnostic)
        for diagnostic in sorted(visibility.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["explainability_summaries"] = [
        export_policy_explainability(summary)
        for summary in sorted(
            visibility.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_policy_visibility_identity(identity: PolicyVisibilityIdentity) -> str:
    return stable_serialize(export_policy_visibility_identity(identity))


def serialize_orchestration_policy_visibility(visibility: OrchestrationPolicyVisibility) -> str:
    return stable_serialize(export_orchestration_policy_visibility(visibility))
