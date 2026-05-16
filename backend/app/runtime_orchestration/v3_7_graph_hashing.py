"""Deterministic hashing for v3.7 graph foundations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_7_graph_models import (
    V37GraphEdge,
    V37GraphExplainabilityEvidence,
    V37GraphNode,
    V37GraphProvenance,
    V37OrchestrationPlanningGraph,
)
from .v3_7_graph_serialization import (
    export_v3_7_explainability_evidence,
    export_v3_7_graph,
    export_v3_7_graph_edge,
    export_v3_7_graph_node,
    export_v3_7_graph_provenance,
)


HASH_EXCLUDED_FIELD_NAMES = {
    "generated_at",
    "created_at",
    "updated_at",
    "timestamp",
    "runtime_memory_reference",
    "transient_memory_reference",
}
HASH_EXCLUDED_METADATA_KEYS = {
    "generated_at",
    "created_at",
    "updated_at",
    "timestamp",
    "runtime_memory_reference",
    "transient_memory_reference",
}


def export_v3_7_graph_hash_payload(graph: V37OrchestrationPlanningGraph) -> dict[str, Any]:
    return _strip_hash_exclusions(export_v3_7_graph(graph))


def hash_v3_7_graph(graph: V37OrchestrationPlanningGraph) -> str:
    return deterministic_hash(export_v3_7_graph_hash_payload(graph))


def hash_v3_7_graph_node(node: V37GraphNode) -> str:
    return deterministic_hash(_strip_hash_exclusions(export_v3_7_graph_node(node)))


def hash_v3_7_graph_edge(edge: V37GraphEdge) -> str:
    return deterministic_hash(_strip_hash_exclusions(export_v3_7_graph_edge(edge)))


def hash_v3_7_graph_provenance(provenance: V37GraphProvenance) -> str:
    return deterministic_hash(_strip_hash_exclusions(export_v3_7_graph_provenance(provenance)))


def hash_v3_7_explainability_evidence(evidence: V37GraphExplainabilityEvidence) -> str:
    return deterministic_hash(_strip_hash_exclusions(export_v3_7_explainability_evidence(evidence)))


def validate_v3_7_graph_hash_stability(graph: V37OrchestrationPlanningGraph) -> dict[str, Any]:
    first = hash_v3_7_graph(graph)
    second = hash_v3_7_graph(deepcopy(graph))
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json",
    }


def _strip_hash_exclusions(payload: Any) -> Any:
    if isinstance(payload, dict):
        if "metadata_key" in payload:
            metadata_key = str(payload["metadata_key"])
            if payload.get("included_in_hash") is False or metadata_key in HASH_EXCLUDED_METADATA_KEYS:
                return None
        stripped: dict[str, Any] = {}
        for key, value in payload.items():
            if key in HASH_EXCLUDED_FIELD_NAMES:
                continue
            if key == "metadata" and isinstance(value, list):
                metadata = [_strip_hash_exclusions(item) for item in value]
                stripped[key] = [item for item in metadata if item is not None]
                continue
            child = _strip_hash_exclusions(value)
            if child is not None:
                stripped[key] = child
        return stripped
    if isinstance(payload, list):
        return [item for item in (_strip_hash_exclusions(value) for value in payload) if item is not None]
    return payload
