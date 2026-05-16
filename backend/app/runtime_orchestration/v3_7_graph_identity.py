"""Deterministic identity helpers for v3.7 graph foundations."""

from __future__ import annotations

from .v3_7_graph_models import (
    V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
    V3_7_GRAPH_SCHEMA_VERSION,
    V3_7_STRUCTURAL_REASONING_ONLY,
    V37GraphEdgeIdentity,
    V37GraphIdentity,
    V37GraphNodeIdentity,
)


def build_v3_7_graph_identity(
    graph_id: str,
    graph_version: str = "v3.7",
    structural_purpose: str = V3_7_STRUCTURAL_REASONING_ONLY,
) -> V37GraphIdentity:
    return V37GraphIdentity(
        graph_id=graph_id,
        schema_version=V3_7_GRAPH_SCHEMA_VERSION,
        phase_id=V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
        graph_version=graph_version,
        structural_purpose=structural_purpose,
    )


def build_v3_7_node_identity(
    node_id: str,
    node_type: str,
    node_label: str,
    structural_purpose: str = V3_7_STRUCTURAL_REASONING_ONLY,
) -> V37GraphNodeIdentity:
    return V37GraphNodeIdentity(
        node_id=node_id,
        node_type=node_type,
        node_label=node_label,
        structural_purpose=structural_purpose,
    )


def build_v3_7_edge_identity(
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    relationship_type: str,
    structural_purpose: str = "structural_relationship_only_not_execution_flow",
) -> V37GraphEdgeIdentity:
    return V37GraphEdgeIdentity(
        edge_id=edge_id,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        relationship_type=relationship_type,
        structural_purpose=structural_purpose,
    )


def graph_identity_key(identity: V37GraphIdentity) -> str:
    return "|".join(
        (
            identity.schema_version,
            identity.phase_id,
            identity.graph_version,
            identity.graph_id,
        )
    )


def node_identity_key(identity: V37GraphNodeIdentity) -> str:
    return "|".join((identity.node_type, identity.node_id))


def edge_identity_key(identity: V37GraphEdgeIdentity) -> str:
    return "|".join(
        (
            identity.relationship_type,
            identity.source_node_id,
            identity.target_node_id,
            identity.edge_id,
        )
    )


def identity_values_are_unique(values: tuple[str, ...] | list[str]) -> bool:
    return len(values) == len(set(values))
