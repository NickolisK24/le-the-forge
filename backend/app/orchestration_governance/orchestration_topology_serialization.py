"""Deterministic serialization for v4.3 orchestration topology visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_topology_models import (
    OrchestrationTopology,
    OrchestrationTopologyContinuityMetadata,
    OrchestrationTopologyDiagnostic,
    OrchestrationTopologyEdge,
    OrchestrationTopologyExplainability,
    OrchestrationTopologyIdentity,
    OrchestrationTopologyMetadata,
    OrchestrationTopologyNode,
    OrchestrationTopologyRelationship,
    OrchestrationTopologyRelationshipVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "traversal_enabled",
    "graph_execution_enabled",
    "orchestration_execution_enabled",
    "runtime_execution_enabled",
    "routing_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "route_selection_enabled",
    "topology_based_execution_enabled",
    "topology_based_routing_enabled",
    "topology_based_recommendation_enabled",
    "automatic_remediation_enabled",
    "topology_repair_enabled",
    "graph_repair_enabled",
    "orchestration_inference_enabled",
    "operational_authorization_enabled",
    "readiness_approval_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "runtime_mutation_enabled",
    "operational_state_mutation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "graph_engine_enabled",
    "traversal_engine_enabled",
    "routing_engine_enabled",
    "dependency_resolver_enabled",
    "repair_enabled",
    "inference_enabled",
    "auto_correction_enabled",
    "authorization_enabled",
    "executable",
    "routable",
    "schedulable",
    "resolvable",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_topology_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_topology_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_topology_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_topology_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_topology_evidence(payload),
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


def export_orchestration_topology_identity(identity: OrchestrationTopologyIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_orchestration_topology_metadata(metadata: OrchestrationTopologyMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    data["source_report_references"] = sorted_entries(data["source_report_references"])
    return data


def export_orchestration_topology_node(node: OrchestrationTopologyNode) -> dict[str, Any]:
    return _disable_execution_fields(asdict(node))


def export_orchestration_topology_edge(edge: OrchestrationTopologyEdge) -> dict[str, Any]:
    return _disable_execution_fields(asdict(edge))


def export_orchestration_topology_relationship(
    relationship: OrchestrationTopologyRelationship,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(relationship))
    for field_name in (
        "unsupported_reason_visibility",
        "prohibited_reason_visibility",
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "conflicting_reason_visibility",
        "missing_metadata_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_topology_relationship_visibility(
    visibility: OrchestrationTopologyRelationshipVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "boundary_relationship_ids",
        "unsupported_relationship_ids",
        "prohibited_relationship_ids",
        "blocked_relationship_ids",
        "stale_relationship_ids",
        "conflicting_relationship_ids",
        "missing_metadata_relationship_ids",
        "unknown_relationship_ids",
        "prohibited_relationship_types",
        "unsupported_relationship_types",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_topology_continuity_metadata(
    metadata: OrchestrationTopologyContinuityMetadata,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("node_references", "edge_references", "relationship_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_topology_diagnostic(diagnostic: OrchestrationTopologyDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_node_ids", "affected_edge_ids", "affected_relationship_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_topology_explainability(
    summary: OrchestrationTopologyExplainability,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(summary))
    data["affected_relationship_ids"] = sorted_entries(data["affected_relationship_ids"])
    return data


def export_orchestration_topology(topology: OrchestrationTopology) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(topology))
    data["identity"] = export_orchestration_topology_identity(topology.identity)
    data["metadata"] = export_orchestration_topology_metadata(topology.metadata)
    data["nodes"] = [
        export_orchestration_topology_node(node)
        for node in sorted(topology.nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["edges"] = [
        export_orchestration_topology_edge(edge)
        for edge in sorted(topology.edges, key=lambda item: (item.deterministic_order, item.edge_id))
    ]
    data["relationships"] = [
        export_orchestration_topology_relationship(relationship)
        for relationship in sorted(
            topology.relationships,
            key=lambda item: (item.deterministic_order, item.relationship_id),
        )
    ]
    data["relationship_visibility"] = export_orchestration_topology_relationship_visibility(
        topology.relationship_visibility
    )
    data["continuity_metadata"] = [
        export_orchestration_topology_continuity_metadata(metadata)
        for metadata in sorted(
            topology.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_orchestration_topology_diagnostic(diagnostic)
        for diagnostic in sorted(topology.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["explainability_summaries"] = [
        export_orchestration_topology_explainability(summary)
        for summary in sorted(
            topology.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_orchestration_topology_identity(identity: OrchestrationTopologyIdentity) -> str:
    return stable_serialize(export_orchestration_topology_identity(identity))


def serialize_orchestration_topology(topology: OrchestrationTopology) -> str:
    return stable_serialize(export_orchestration_topology(topology))
