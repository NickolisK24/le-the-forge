"""Canonical serialization for v4.2 coordination dependency graph governance."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_dependency_graph_models import (
    ContinuityAwareDependencyReference,
    CoordinationBlockedDependencyVisibility,
    CoordinationDependencyDirectionVisibility,
    CoordinationDependencyGraph,
    CoordinationDependencyGraphDiagnostic,
    CoordinationDependencyGraphGovernance,
    CoordinationDependencyGraphIdentity,
    CoordinationGraphEdge,
    CoordinationGraphNode,
    CoordinationProhibitedDependencyVisibility,
    CoordinationUnsupportedDependencyVisibility,
    LineageAwareDependencyReference,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "graph_execution_enabled",
    "dependency_resolution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "recovery_execution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "lineage_repair_enabled",
    "inferred_lineage_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_dependency_resolution_enabled",
    "hidden_direction_inference_enabled",
    "hidden_fallback_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_dependency_graph_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_dependency_graph_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_dependency_graph_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_dependency_graph_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_dependency_graph_evidence(payload),
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


def export_coordination_dependency_graph_identity(
    identity: CoordinationDependencyGraphIdentity,
) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_coordination_graph_node(node: CoordinationGraphNode) -> dict[str, Any]:
    return _disable_execution_fields(asdict(node))


def export_coordination_graph_edge(edge: CoordinationGraphEdge) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(edge))
    for field_name in ("blocked_reason_visibility", "prohibited_reason_visibility", "unsupported_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_direction_visibility(visibility: CoordinationDependencyDirectionVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "directional_edge_ids",
        "reverse_dependency_visibility",
        "ambiguous_direction_visibility",
        "circular_direction_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_blocked_dependency_visibility(visibility: CoordinationBlockedDependencyVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("blocked_node_ids", "blocked_edge_ids", "blocked_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_prohibited_dependency_visibility(
    visibility: CoordinationProhibitedDependencyVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "prohibited_node_ids",
        "prohibited_edge_ids",
        "prohibited_capabilities",
        "prohibited_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_dependency_visibility(
    visibility: CoordinationUnsupportedDependencyVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "unsupported_node_ids",
        "unsupported_edge_ids",
        "unknown_dependency_visibility",
        "stale_dependency_visibility",
        "unsupported_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lineage_aware_dependency_reference(reference: LineageAwareDependencyReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("node_references", "edge_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_continuity_aware_dependency_reference(reference: ContinuityAwareDependencyReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["dependency_references"] = sorted_entries(data["dependency_references"])
    return data


def export_coordination_dependency_graph_diagnostic(
    diagnostic: CoordinationDependencyGraphDiagnostic,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_node_ids", "affected_edge_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_dependency_graph_governance(
    governance: CoordinationDependencyGraphGovernance,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_dependency_graph(graph: CoordinationDependencyGraph) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(graph))
    data["identity"] = export_coordination_dependency_graph_identity(graph.identity)
    data["nodes"] = [
        export_coordination_graph_node(node)
        for node in sorted(graph.nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["edges"] = [
        export_coordination_graph_edge(edge)
        for edge in sorted(graph.edges, key=lambda item: (item.deterministic_order, item.edge_id))
    ]
    data["direction_visibility"] = export_direction_visibility(graph.direction_visibility)
    data["blocked_dependency_visibility"] = export_blocked_dependency_visibility(graph.blocked_dependency_visibility)
    data["prohibited_dependency_visibility"] = export_prohibited_dependency_visibility(
        graph.prohibited_dependency_visibility
    )
    data["unsupported_dependency_visibility"] = export_unsupported_dependency_visibility(
        graph.unsupported_dependency_visibility
    )
    data["lineage_references"] = [
        export_lineage_aware_dependency_reference(reference)
        for reference in sorted(
            graph.lineage_references,
            key=lambda item: (item.deterministic_order, item.lineage_dependency_id),
        )
    ]
    data["continuity_references"] = [
        export_continuity_aware_dependency_reference(reference)
        for reference in sorted(
            graph.continuity_references,
            key=lambda item: (item.deterministic_order, item.continuity_dependency_id),
        )
    ]
    data["diagnostics"] = [
        export_coordination_dependency_graph_diagnostic(diagnostic)
        for diagnostic in sorted(graph.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["governance_visibility"] = export_coordination_dependency_graph_governance(graph.governance_visibility)
    return data


def serialize_coordination_dependency_graph_identity(identity: CoordinationDependencyGraphIdentity) -> str:
    return stable_serialize(export_coordination_dependency_graph_identity(identity))


def serialize_coordination_dependency_graph(graph: CoordinationDependencyGraph) -> str:
    return stable_serialize(export_coordination_dependency_graph(graph))
