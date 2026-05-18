"""Deterministic hashing for v4.3 orchestration topology visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_topology_models import (
    OrchestrationTopology,
    OrchestrationTopologyContinuityMetadata,
    OrchestrationTopologyDiagnostic,
    OrchestrationTopologyEdge,
    OrchestrationTopologyIdentity,
    OrchestrationTopologyNode,
    OrchestrationTopologyRelationship,
)
from .orchestration_topology_serialization import (
    export_orchestration_topology,
    export_orchestration_topology_continuity_metadata,
    export_orchestration_topology_diagnostic,
    export_orchestration_topology_edge,
    export_orchestration_topology_identity,
    export_orchestration_topology_node,
    export_orchestration_topology_relationship,
    stable_serialize,
)


def deterministic_orchestration_topology_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_orchestration_topology_identity(identity: OrchestrationTopologyIdentity) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_identity(identity))


def hash_orchestration_topology_node(node: OrchestrationTopologyNode) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_node(node))


def hash_orchestration_topology_edge(edge: OrchestrationTopologyEdge) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_edge(edge))


def hash_orchestration_topology_relationship(relationship: OrchestrationTopologyRelationship) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_relationship(relationship))


def hash_orchestration_topology_diagnostic(diagnostic: OrchestrationTopologyDiagnostic) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_diagnostic(diagnostic))


def hash_orchestration_topology_continuity_metadata(metadata: OrchestrationTopologyContinuityMetadata) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology_continuity_metadata(metadata))


def hash_orchestration_topology(topology: OrchestrationTopology) -> str:
    return deterministic_orchestration_topology_hash(export_orchestration_topology(topology))
