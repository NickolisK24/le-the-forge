"""Deterministic serialization for v3.7 graph foundations."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.runtime_intelligence.classification_hashing import stable_serialize

from .v3_7_graph_models import (
    V37GraphCompatibilityBoundary,
    V37GraphContinuityEvidence,
    V37GraphEdge,
    V37GraphEdgeIdentity,
    V37GraphExplainabilityEvidence,
    V37GraphGovernanceBoundary,
    V37GraphIdentity,
    V37GraphMetadataEntry,
    V37GraphNode,
    V37GraphNodeIdentity,
    V37GraphProvenance,
    V37GraphVisibilityFinding,
    V37OrchestrationPlanningGraph,
)


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


def export_v3_7_graph_identity(identity: V37GraphIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_node_identity(identity: V37GraphNodeIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_edge_identity(identity: V37GraphEdgeIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_7_metadata_entry(entry: V37GraphMetadataEntry) -> dict[str, Any]:
    return asdict(entry)


def export_v3_7_graph_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = _sorted_entries(data[field_name])
    return data


def export_v3_7_governance_boundary(boundary: V37GraphGovernanceBoundary) -> dict[str, Any]:
    return {
        "boundary_id": boundary.boundary_id,
        "boundary_type": boundary.boundary_type,
        "visibility_status": boundary.visibility_status,
        "restriction_summary": boundary.restriction_summary,
        "provenance": export_v3_7_graph_provenance(boundary.provenance),
        "metadata": _export_metadata(boundary.metadata),
    }


def export_v3_7_compatibility_boundary(boundary: V37GraphCompatibilityBoundary) -> dict[str, Any]:
    return {
        "boundary_id": boundary.boundary_id,
        "source_domain": boundary.source_domain,
        "target_domain": boundary.target_domain,
        "compatibility_status": boundary.compatibility_status,
        "blocker_ids": _sorted_entries(boundary.blocker_ids),
        "unsupported_domain_ids": _sorted_entries(boundary.unsupported_domain_ids),
        "prohibited_domain_ids": _sorted_entries(boundary.prohibited_domain_ids),
        "provenance": export_v3_7_graph_provenance(boundary.provenance),
        "metadata": _export_metadata(boundary.metadata),
    }


def export_v3_7_visibility_finding(finding: V37GraphVisibilityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["provenance_references"] = _sorted_entries(data["provenance_references"])
    return data


def export_v3_7_graph_node(node: V37GraphNode) -> dict[str, Any]:
    return {
        "identity": export_v3_7_node_identity(node.identity),
        "governance_boundary_ids": _sorted_entries(node.governance_boundary_ids),
        "compatibility_boundary_ids": _sorted_entries(node.compatibility_boundary_ids),
        "blocker_ids": _sorted_entries(node.blocker_ids),
        "unsupported_domain_ids": _sorted_entries(node.unsupported_domain_ids),
        "prohibited_domain_ids": _sorted_entries(node.prohibited_domain_ids),
        "provenance": export_v3_7_graph_provenance(node.provenance),
        "explainability_evidence_ids": _sorted_entries(node.explainability_evidence_ids),
        "metadata": _export_metadata(node.metadata),
        "node_executable": node.node_executable,
        "action_enabled": node.action_enabled,
    }


def export_v3_7_graph_edge(edge: V37GraphEdge) -> dict[str, Any]:
    return {
        "identity": export_v3_7_edge_identity(edge.identity),
        "governance_boundary_ids": _sorted_entries(edge.governance_boundary_ids),
        "compatibility_boundary_ids": _sorted_entries(edge.compatibility_boundary_ids),
        "blocker_ids": _sorted_entries(edge.blocker_ids),
        "unsupported_domain_ids": _sorted_entries(edge.unsupported_domain_ids),
        "prohibited_domain_ids": _sorted_entries(edge.prohibited_domain_ids),
        "provenance": export_v3_7_graph_provenance(edge.provenance),
        "explainability_evidence_ids": _sorted_entries(edge.explainability_evidence_ids),
        "metadata": _export_metadata(edge.metadata),
        "edge_executable": edge.edge_executable,
        "traversal_enabled": edge.traversal_enabled,
        "execution_flow_enabled": edge.execution_flow_enabled,
    }


def export_v3_7_explainability_evidence(evidence: V37GraphExplainabilityEvidence) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "subject_id": evidence.subject_id,
        "subject_type": evidence.subject_type,
        "why_exists": evidence.why_exists,
        "governance_restrictions": _sorted_entries(evidence.governance_restrictions),
        "unsupported_boundaries": _sorted_entries(evidence.unsupported_boundaries),
        "prohibited_boundaries": _sorted_entries(evidence.prohibited_boundaries),
        "compatibility_visibility": _sorted_entries(evidence.compatibility_visibility),
        "provenance_lineage": _sorted_entries(evidence.provenance_lineage),
        "continuity_references": _sorted_entries(evidence.continuity_references),
        "provenance": export_v3_7_graph_provenance(evidence.provenance),
    }


def export_v3_7_continuity_evidence(evidence: V37GraphContinuityEvidence) -> dict[str, Any]:
    return {
        "continuity_id": evidence.continuity_id,
        "replay_lineage_references": _sorted_entries(evidence.replay_lineage_references),
        "rollback_lineage_references": _sorted_entries(evidence.rollback_lineage_references),
        "provenance_lineage_references": _sorted_entries(evidence.provenance_lineage_references),
        "explainability_lineage_references": _sorted_entries(evidence.explainability_lineage_references),
        "governance_lineage_references": _sorted_entries(evidence.governance_lineage_references),
        "compatibility_lineage_references": _sorted_entries(evidence.compatibility_lineage_references),
        "deterministic_hash_references": _sorted_entries(evidence.deterministic_hash_references),
    }


def export_v3_7_graph(graph: V37OrchestrationPlanningGraph) -> dict[str, Any]:
    return {
        "identity": export_v3_7_graph_identity(graph.identity),
        "metadata": _export_metadata(graph.metadata),
        "provenance": export_v3_7_graph_provenance(graph.provenance),
        "nodes": [
            export_v3_7_graph_node(node)
            for node in sorted(graph.nodes, key=lambda item: item.identity.node_id)
        ],
        "edges": [
            export_v3_7_graph_edge(edge)
            for edge in sorted(graph.edges, key=lambda item: item.identity.edge_id)
        ],
        "governance_boundaries": [
            export_v3_7_governance_boundary(boundary)
            for boundary in sorted(graph.governance_boundaries, key=lambda item: item.boundary_id)
        ],
        "compatibility_boundaries": [
            export_v3_7_compatibility_boundary(boundary)
            for boundary in sorted(graph.compatibility_boundaries, key=lambda item: item.boundary_id)
        ],
        "blockers": [
            export_v3_7_visibility_finding(finding)
            for finding in sorted(graph.blockers, key=lambda item: item.finding_id)
        ],
        "unsupported_domains": [
            export_v3_7_visibility_finding(finding)
            for finding in sorted(graph.unsupported_domains, key=lambda item: item.finding_id)
        ],
        "prohibited_domains": [
            export_v3_7_visibility_finding(finding)
            for finding in sorted(graph.prohibited_domains, key=lambda item: item.finding_id)
        ],
        "explainability_evidence": [
            export_v3_7_explainability_evidence(evidence)
            for evidence in sorted(graph.explainability_evidence, key=lambda item: item.evidence_id)
        ],
        "continuity_evidence": [
            export_v3_7_continuity_evidence(evidence)
            for evidence in sorted(graph.continuity_evidence, key=lambda item: item.continuity_id)
        ],
        "planning_only": graph.planning_only,
        "structural_reasoning_only": graph.structural_reasoning_only,
        "non_executable": graph.non_executable,
        "graph_execution_enabled": graph.graph_execution_enabled,
        "graph_traversal_execution_enabled": graph.graph_traversal_execution_enabled,
        "runtime_dispatch_enabled": graph.runtime_dispatch_enabled,
        "scheduling_enabled": graph.scheduling_enabled,
        "routing_enabled": graph.routing_enabled,
        "mutation_enabled": graph.mutation_enabled,
        "persistent_runtime_writes_enabled": graph.persistent_runtime_writes_enabled,
        "background_processing_enabled": graph.background_processing_enabled,
        "optimization_enabled": graph.optimization_enabled,
        "recommendation_enabled": graph.recommendation_enabled,
        "autonomous_orchestration_enabled": graph.autonomous_orchestration_enabled,
    }


def export_v3_7_graph_counts(graph: V37OrchestrationPlanningGraph) -> dict[str, int]:
    return {
        "metadata_count": len(graph.metadata),
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "governance_boundary_count": len(graph.governance_boundaries),
        "compatibility_boundary_count": len(graph.compatibility_boundaries),
        "blocker_count": len(graph.blockers),
        "unsupported_domain_count": len(graph.unsupported_domains),
        "prohibited_domain_count": len(graph.prohibited_domains),
        "explainability_evidence_count": len(graph.explainability_evidence),
        "continuity_evidence_count": len(graph.continuity_evidence),
    }


def serialize_v3_7_graph(graph: V37OrchestrationPlanningGraph) -> str:
    return stable_serialize(export_v3_7_graph(graph))


def validate_v3_7_graph_serialization_stability(graph: V37OrchestrationPlanningGraph) -> dict[str, Any]:
    first = serialize_v3_7_graph(graph)
    second = serialize_v3_7_graph(graph)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_tuples",
        "first_length": len(first),
        "second_length": len(second),
    }


def _export_metadata(metadata: tuple[V37GraphMetadataEntry, ...]) -> list[dict[str, Any]]:
    return [
        export_v3_7_metadata_entry(entry)
        for entry in sorted(metadata, key=lambda item: item.metadata_key)
    ]
