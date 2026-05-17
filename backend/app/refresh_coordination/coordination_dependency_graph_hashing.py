"""Deterministic hashing for v4.2 coordination dependency graph governance."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_dependency_graph_models import (
    ContinuityAwareDependencyReference,
    CoordinationDependencyDirectionVisibility,
    CoordinationDependencyGraph,
    CoordinationDependencyGraphIdentity,
    CoordinationGraphEdge,
    CoordinationGraphNode,
    LineageAwareDependencyReference,
)
from .coordination_dependency_graph_serialization import (
    export_continuity_aware_dependency_reference,
    export_coordination_dependency_graph,
    export_coordination_dependency_graph_identity,
    export_coordination_graph_edge,
    export_coordination_graph_node,
    export_direction_visibility,
    export_lineage_aware_dependency_reference,
    stable_serialize,
)


def deterministic_coordination_dependency_graph_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_dependency_graph_identity(identity: CoordinationDependencyGraphIdentity) -> str:
    return deterministic_coordination_dependency_graph_hash(export_coordination_dependency_graph_identity(identity))


def hash_coordination_graph_node(node: CoordinationGraphNode) -> str:
    return deterministic_coordination_dependency_graph_hash(export_coordination_graph_node(node))


def hash_coordination_graph_edge(edge: CoordinationGraphEdge) -> str:
    return deterministic_coordination_dependency_graph_hash(export_coordination_graph_edge(edge))


def hash_coordination_direction_visibility(visibility: CoordinationDependencyDirectionVisibility) -> str:
    return deterministic_coordination_dependency_graph_hash(export_direction_visibility(visibility))


def hash_lineage_aware_dependency_reference(reference: LineageAwareDependencyReference) -> str:
    return deterministic_coordination_dependency_graph_hash(export_lineage_aware_dependency_reference(reference))


def hash_continuity_aware_dependency_reference(reference: ContinuityAwareDependencyReference) -> str:
    return deterministic_coordination_dependency_graph_hash(export_continuity_aware_dependency_reference(reference))


def hash_coordination_dependency_graph(graph: CoordinationDependencyGraph) -> str:
    return deterministic_coordination_dependency_graph_hash(export_coordination_dependency_graph(graph))
