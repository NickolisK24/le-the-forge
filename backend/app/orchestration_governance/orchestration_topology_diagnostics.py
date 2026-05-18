"""Diagnostics for deterministic v4.3 orchestration topology visibility.

Diagnostics expose topology structure, missing endpoints, duplicates,
unsupported relationships, prohibited relationships, blocked relationships,
stale relationships, conflicting relationships, missing metadata, and any
execution-capable flags. They do not repair, infer, authorize, route, schedule,
traverse, resolve, execute, or mutate topology state.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .orchestration_topology_hashing import (
    hash_orchestration_topology,
    hash_orchestration_topology_continuity_metadata,
    hash_orchestration_topology_diagnostic,
    hash_orchestration_topology_edge,
    hash_orchestration_topology_node,
    hash_orchestration_topology_relationship,
)
from .orchestration_topology_models import (
    FAIL_VISIBLE_TOPOLOGY_STATES,
    PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES,
    TOPOLOGY_STATE_BLOCKED,
    TOPOLOGY_STATE_CONFLICTING,
    TOPOLOGY_STATE_MISSING_METADATA,
    TOPOLOGY_STATE_PROHIBITED,
    TOPOLOGY_STATE_STALE,
    TOPOLOGY_STATE_UNSUPPORTED,
    TOPOLOGY_STATES,
    OrchestrationTopology,
    OrchestrationTopologyEdge,
    OrchestrationTopologyNode,
    OrchestrationTopologyRelationship,
    default_orchestration_topology,
)
from .orchestration_topology_serialization import serialize_orchestration_topology


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
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


def _duplicates(values: Iterable[str]) -> tuple[str, ...]:
    counts = Counter(values)
    return tuple(sorted(value for value, count in counts.items() if count > 1))


def count_topology_node_states(nodes: tuple[OrchestrationTopologyNode, ...]) -> dict[str, int]:
    counts = {state: 0 for state in TOPOLOGY_STATES}
    counts["invalid"] = 0
    for node in nodes:
        if node.node_state in counts:
            counts[node.node_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_topology_edge_states(edges: tuple[OrchestrationTopologyEdge, ...]) -> dict[str, int]:
    counts = {state: 0 for state in TOPOLOGY_STATES}
    counts["invalid"] = 0
    for edge in edges:
        if edge.edge_state in counts:
            counts[edge.edge_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def count_topology_relationship_states(
    relationships: tuple[OrchestrationTopologyRelationship, ...],
) -> dict[str, int]:
    counts = {state: 0 for state in TOPOLOGY_STATES}
    counts["invalid"] = 0
    for relationship in relationships:
        if relationship.relationship_state in counts:
            counts[relationship.relationship_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_topology_node_ids(nodes: tuple[OrchestrationTopologyNode, ...]) -> tuple[str, ...]:
    return tuple(
        node.node_id for node in nodes if node.node_state in FAIL_VISIBLE_TOPOLOGY_STATES and node.fail_visible
    )


def fail_visible_topology_edge_ids(edges: tuple[OrchestrationTopologyEdge, ...]) -> tuple[str, ...]:
    return tuple(
        edge.edge_id for edge in edges if edge.edge_state in FAIL_VISIBLE_TOPOLOGY_STATES and edge.fail_visible
    )


def fail_visible_topology_relationship_ids(
    relationships: tuple[OrchestrationTopologyRelationship, ...],
) -> tuple[str, ...]:
    return tuple(
        relationship.relationship_id
        for relationship in relationships
        if relationship.relationship_state in FAIL_VISIBLE_TOPOLOGY_STATES and relationship.fail_visible
    )


def aggregate_unsupported_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_UNSUPPORTED
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.unsupported_relationship_ids)))


def aggregate_prohibited_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_PROHIBITED
        or relationship.relationship_type in PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.prohibited_relationship_ids)))


def aggregate_blocked_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_BLOCKED
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.blocked_relationship_ids)))


def aggregate_stale_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_STALE
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.stale_relationship_ids)))


def aggregate_conflicting_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_CONFLICTING
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.conflicting_relationship_ids)))


def aggregate_missing_metadata_relationships(topology: OrchestrationTopology) -> tuple[str, ...]:
    relationship_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_MISSING_METADATA
    )
    return tuple(sorted(set(relationship_ids + topology.relationship_visibility.missing_metadata_relationship_ids)))


def topology_capability_flags(topology: OrchestrationTopology) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        topology,
        topology.identity,
        topology.metadata,
        topology.relationship_visibility,
        *topology.nodes,
        *topology.edges,
        *topology.relationships,
        *topology.continuity_metadata,
        *topology.diagnostics,
        *topology.explainability_summaries,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_topology_capability_flags(topology: OrchestrationTopology) -> dict[str, bool]:
    return {key: value for key, value in topology_capability_flags(topology).items() if value}


def topology_identity_key(topology: OrchestrationTopology) -> str:
    identity = topology.identity
    return "|".join(
        (
            identity.schema_version,
            identity.topology_id,
            identity.topology_version,
            identity.source_manifest_reference,
            identity.source_manifest_hash_reference,
            identity.governance_reference,
            identity.lineage_reference,
            identity.provenance_reference,
        )
    )


def topologies_equal(left: OrchestrationTopology, right: OrchestrationTopology) -> bool:
    return serialize_orchestration_topology(left) == serialize_orchestration_topology(right)


def validate_topology_identity(topology: OrchestrationTopology) -> dict[str, object]:
    identity_fields = {
        "topology_id": topology.identity.topology_id,
        "topology_version": topology.identity.topology_version,
        "topology_classification": topology.identity.topology_classification,
        "source_manifest_reference": topology.identity.source_manifest_reference,
        "source_manifest_hash_reference": topology.identity.source_manifest_hash_reference,
        "schema_version": topology.identity.schema_version,
        "governance_reference": topology.identity.governance_reference,
        "lineage_reference": topology.identity.lineage_reference,
        "provenance_reference": topology.identity.provenance_reference,
        "continuity_reference": topology.identity.continuity_reference,
        "diagnostics_reference": topology.identity.diagnostics_reference,
        "explainability_reference": topology.identity.explainability_reference,
        "non_execution_reference": topology.identity.non_execution_reference,
    }
    missing_fields = tuple(sorted(key for key, value in identity_fields.items() if not value))
    return {
        "valid": len(missing_fields) == 0,
        "missing_topology_identity_fields": missing_fields,
        "identity_key": topology_identity_key(topology),
    }


def validate_topology_structure(topology: OrchestrationTopology) -> dict[str, object]:
    node_ids = tuple(node.node_id for node in topology.nodes)
    edge_ids = tuple(edge.edge_id for edge in topology.edges)
    relationship_ids = tuple(relationship.relationship_id for relationship in topology.relationships)
    known_node_ids = set(node_ids)
    known_relationship_ids = set(relationship_ids)
    duplicate_node_ids = _duplicates(node_ids)
    duplicate_edge_ids = _duplicates(edge_ids)
    duplicate_relationship_ids = _duplicates(relationship_ids)
    missing_source_edge_ids = tuple(sorted(edge.edge_id for edge in topology.edges if not edge.source_node_id))
    missing_target_edge_ids = tuple(sorted(edge.edge_id for edge in topology.edges if not edge.target_node_id))
    unknown_source_edge_ids = tuple(
        sorted(
            edge.edge_id
            for edge in topology.edges
            if edge.source_node_id and edge.source_node_id not in known_node_ids
        )
    )
    unknown_target_edge_ids = tuple(
        sorted(
            edge.edge_id
            for edge in topology.edges
            if edge.target_node_id and edge.target_node_id not in known_node_ids
        )
    )
    missing_relationship_edge_ids = tuple(
        sorted(edge.edge_id for edge in topology.edges if edge.relationship_id not in known_relationship_ids)
    )
    self_referential_edge_ids = tuple(
        sorted(
            edge.edge_id
            for edge in topology.edges
            if edge.source_node_id == edge.target_node_id and not edge.self_reference_allowed
        )
    )
    relationship_missing_source_ids = tuple(
        sorted(relationship.relationship_id for relationship in topology.relationships if not relationship.source_node_id)
    )
    relationship_missing_target_ids = tuple(
        sorted(relationship.relationship_id for relationship in topology.relationships if not relationship.target_node_id)
    )
    relationship_unknown_source_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if relationship.source_node_id and relationship.source_node_id not in known_node_ids
        )
    )
    relationship_unknown_target_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if relationship.target_node_id and relationship.target_node_id not in known_node_ids
        )
    )
    relationship_self_referential_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if relationship.source_node_id == relationship.target_node_id and relationship.source_node_id
        )
    )
    return {
        "valid": (
            len(duplicate_node_ids) == 0
            and len(duplicate_edge_ids) == 0
            and len(duplicate_relationship_ids) == 0
            and len(missing_source_edge_ids) == 0
            and len(missing_target_edge_ids) == 0
            and len(unknown_source_edge_ids) == 0
            and len(unknown_target_edge_ids) == 0
            and len(missing_relationship_edge_ids) == 0
            and len(self_referential_edge_ids) == 0
            and len(relationship_missing_source_ids) == 0
            and len(relationship_missing_target_ids) == 0
            and len(relationship_unknown_source_ids) == 0
            and len(relationship_unknown_target_ids) == 0
            and len(relationship_self_referential_ids) == 0
        ),
        "duplicate_node_ids": duplicate_node_ids,
        "duplicate_edge_ids": duplicate_edge_ids,
        "duplicate_relationship_ids": duplicate_relationship_ids,
        "missing_source_edge_ids": missing_source_edge_ids,
        "missing_target_edge_ids": missing_target_edge_ids,
        "unknown_source_edge_ids": unknown_source_edge_ids,
        "unknown_target_edge_ids": unknown_target_edge_ids,
        "missing_relationship_edge_ids": missing_relationship_edge_ids,
        "self_referential_edge_ids": self_referential_edge_ids,
        "relationship_missing_source_ids": relationship_missing_source_ids,
        "relationship_missing_target_ids": relationship_missing_target_ids,
        "relationship_unknown_source_ids": relationship_unknown_source_ids,
        "relationship_unknown_target_ids": relationship_unknown_target_ids,
        "relationship_self_referential_ids": relationship_self_referential_ids,
    }


def validate_topology_relationship_visibility(topology: OrchestrationTopology) -> dict[str, object]:
    unsupported_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_UNSUPPORTED
    )
    prohibited_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_PROHIBITED
        or relationship.relationship_type in PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES
    )
    blocked_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_BLOCKED
    )
    stale_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_STALE
    )
    conflicting_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_CONFLICTING
    )
    missing_metadata_ids = tuple(
        relationship.relationship_id
        for relationship in topology.relationships
        if relationship.relationship_state == TOPOLOGY_STATE_MISSING_METADATA
    )
    invalid_node_ids = tuple(sorted(node.node_id for node in topology.nodes if node.node_state not in TOPOLOGY_STATES))
    invalid_edge_ids = tuple(sorted(edge.edge_id for edge in topology.edges if edge.edge_state not in TOPOLOGY_STATES))
    invalid_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if relationship.relationship_state not in TOPOLOGY_STATES
        )
    )
    unsupported_visible = set(unsupported_ids).issubset(
        set(topology.relationship_visibility.unsupported_relationship_ids)
    )
    prohibited_visible = set(prohibited_ids).issubset(
        set(topology.relationship_visibility.prohibited_relationship_ids)
    )
    blocked_visible = set(blocked_ids).issubset(set(topology.relationship_visibility.blocked_relationship_ids))
    stale_visible = set(stale_ids).issubset(set(topology.relationship_visibility.stale_relationship_ids))
    conflicting_visible = set(conflicting_ids).issubset(
        set(topology.relationship_visibility.conflicting_relationship_ids)
    )
    missing_metadata_visible = set(missing_metadata_ids).issubset(
        set(topology.relationship_visibility.missing_metadata_relationship_ids)
    )
    boundary_visible = all(
        relationship.relationship_id in topology.relationship_visibility.boundary_relationship_ids
        for relationship in topology.relationships
        if relationship.boundary_relationship_visible
    )
    prohibited_types_visible = set(PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES).issubset(
        set(topology.relationship_visibility.prohibited_relationship_types)
    )
    hidden_count = sum(
        1
        for item in (*topology.nodes, *topology.edges, *topology.relationships, *topology.diagnostics)
        if getattr(item, "hidden", False)
    )
    executable_relationship_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if relationship.executable
            or relationship.routable
            or relationship.schedulable
            or relationship.resolvable
            or relationship.traversal_enabled
            or relationship.graph_execution_enabled
            or relationship.orchestration_execution_enabled
            or relationship.runtime_execution_enabled
            or relationship.routing_execution_enabled
            or relationship.scheduling_execution_enabled
            or relationship.sequencing_execution_enabled
            or relationship.dependency_resolution_enabled
            or relationship.route_selection_enabled
            or relationship.recommendation_enabled
            or relationship.ranking_enabled
            or relationship.scoring_enabled
            or relationship.selection_enabled
            or relationship.optimization_enabled
            or relationship.production_consumption_enabled
            or relationship.runtime_mutation_enabled
            or relationship.operational_state_mutation_enabled
        )
    )
    return {
        "valid": (
            unsupported_visible
            and prohibited_visible
            and blocked_visible
            and stale_visible
            and conflicting_visible
            and missing_metadata_visible
            and boundary_visible
            and prohibited_types_visible
            and len(invalid_node_ids) == 0
            and len(invalid_edge_ids) == 0
            and len(invalid_relationship_ids) == 0
            and hidden_count == 0
            and len(executable_relationship_ids) == 0
        ),
        "node_state_counts": count_topology_node_states(topology.nodes),
        "edge_state_counts": count_topology_edge_states(topology.edges),
        "relationship_state_counts": count_topology_relationship_states(topology.relationships),
        "fail_visible_node_ids": fail_visible_topology_node_ids(topology.nodes),
        "fail_visible_edge_ids": fail_visible_topology_edge_ids(topology.edges),
        "fail_visible_relationship_ids": fail_visible_topology_relationship_ids(topology.relationships),
        "unsupported_relationship_ids": unsupported_ids,
        "prohibited_relationship_ids": prohibited_ids,
        "blocked_relationship_ids": blocked_ids,
        "stale_relationship_ids": stale_ids,
        "conflicting_relationship_ids": conflicting_ids,
        "missing_metadata_relationship_ids": missing_metadata_ids,
        "unsupported_relationships_visible": unsupported_visible,
        "prohibited_relationships_visible": prohibited_visible,
        "blocked_relationships_visible": blocked_visible,
        "stale_relationships_visible": stale_visible,
        "conflicting_relationships_visible": conflicting_visible,
        "missing_metadata_relationships_visible": missing_metadata_visible,
        "boundary_relationships_visible": boundary_visible,
        "prohibited_relationship_types_visible": prohibited_types_visible,
        "invalid_node_ids": invalid_node_ids,
        "invalid_edge_ids": invalid_edge_ids,
        "invalid_relationship_ids": invalid_relationship_ids,
        "hidden_count": hidden_count,
        "executable_relationship_ids": executable_relationship_ids,
        "unknown_relationship_ids": topology.relationship_visibility.unknown_relationship_ids,
    }


def validate_topology_metadata(topology: OrchestrationTopology) -> dict[str, object]:
    metadata_fields = {
        "governance_metadata_reference": topology.metadata.governance_metadata_reference,
        "lineage_metadata_reference": topology.metadata.lineage_metadata_reference,
        "provenance_metadata_reference": topology.metadata.provenance_metadata_reference,
        "continuity_metadata_reference": topology.metadata.continuity_metadata_reference,
        "diagnostics_metadata_reference": topology.metadata.diagnostics_metadata_reference,
        "explainability_metadata_reference": topology.metadata.explainability_metadata_reference,
        "non_execution_metadata_reference": topology.metadata.non_execution_metadata_reference,
    }
    missing_metadata_fields = tuple(sorted(key for key, value in metadata_fields.items() if not value))
    relationship_missing_metadata_ids = tuple(
        sorted(
            relationship.relationship_id
            for relationship in topology.relationships
            if not relationship.governance_metadata_reference
            or not relationship.lineage_metadata_reference
            or not relationship.provenance_metadata_reference
            or not relationship.continuity_metadata_reference
            or not relationship.diagnostics_metadata_reference
            or not relationship.explainability_metadata_reference
        )
    )
    return {
        "valid": len(missing_metadata_fields) == 0 and len(relationship_missing_metadata_ids) == 0,
        "missing_metadata_fields": missing_metadata_fields,
        "relationship_missing_metadata_ids": relationship_missing_metadata_ids,
        "governance_metadata_present": bool(topology.metadata.governance_metadata_reference),
        "lineage_metadata_present": bool(topology.metadata.lineage_metadata_reference),
        "provenance_metadata_present": bool(topology.metadata.provenance_metadata_reference),
        "continuity_metadata_present": bool(topology.metadata.continuity_metadata_reference),
        "diagnostics_metadata_present": bool(topology.metadata.diagnostics_metadata_reference),
        "explainability_metadata_present": bool(topology.metadata.explainability_metadata_reference),
        "non_execution_metadata_present": bool(topology.metadata.non_execution_metadata_reference),
    }


def validate_topology_continuity(topology: OrchestrationTopology) -> dict[str, object]:
    node_ids = {node.node_id for node in topology.nodes}
    edge_ids = {edge.edge_id for edge in topology.edges}
    relationship_ids = {relationship.relationship_id for relationship in topology.relationships}
    missing_node_refs = tuple(
        sorted(ref for metadata in topology.continuity_metadata for ref in metadata.node_references if ref not in node_ids)
    )
    missing_edge_refs = tuple(
        sorted(ref for metadata in topology.continuity_metadata for ref in metadata.edge_references if ref not in edge_ids)
    )
    missing_relationship_refs = tuple(
        sorted(
            ref
            for metadata in topology.continuity_metadata
            for ref in metadata.relationship_references
            if ref not in relationship_ids
        )
    )
    corrective_count = sum(
        1
        for metadata in topology.continuity_metadata
        if metadata.traversal_enabled
        or metadata.graph_execution_enabled
        or metadata.dependency_resolution_enabled
        or metadata.automatic_remediation_enabled
        or metadata.runtime_mutation_enabled
    )
    return {
        "valid": (
            len(topology.continuity_metadata) > 0
            and len(missing_node_refs) == 0
            and len(missing_edge_refs) == 0
            and len(missing_relationship_refs) == 0
            and all(metadata.replay_safe for metadata in topology.continuity_metadata)
            and all(metadata.rollback_safe for metadata in topology.continuity_metadata)
            and all(metadata.provenance_continuity_preserved for metadata in topology.continuity_metadata)
            and all(metadata.lineage_continuity_preserved for metadata in topology.continuity_metadata)
            and all(metadata.topology_continuity_visible for metadata in topology.continuity_metadata)
            and corrective_count == 0
        ),
        "continuity_metadata_count": len(topology.continuity_metadata),
        "missing_node_references": missing_node_refs,
        "missing_edge_references": missing_edge_refs,
        "missing_relationship_references": missing_relationship_refs,
        "replay_safe": all(metadata.replay_safe for metadata in topology.continuity_metadata),
        "rollback_safe": all(metadata.rollback_safe for metadata in topology.continuity_metadata),
        "provenance_continuity_preserved": all(
            metadata.provenance_continuity_preserved for metadata in topology.continuity_metadata
        ),
        "lineage_continuity_preserved": all(
            metadata.lineage_continuity_preserved for metadata in topology.continuity_metadata
        ),
        "topology_continuity_visible": all(
            metadata.topology_continuity_visible for metadata in topology.continuity_metadata
        ),
        "corrective_continuity_count": corrective_count,
    }


def validate_topology_explainability(topology: OrchestrationTopology) -> dict[str, object]:
    categories = tuple(sorted(set(summary.category for summary in topology.explainability_summaries)))
    required_categories = (
        "blocked_topology",
        "prohibited_relationship",
        "unsupported_relationship",
        "stale_relationship",
        "conflicting_relationship",
        "traversal_unavailable",
        "routing_unavailable",
        "dependency_resolution_unavailable",
        "execution_disabled",
    )
    corrective_count = sum(
        1
        for summary in topology.explainability_summaries
        if summary.recommendation_enabled
        or summary.ranking_enabled
        or summary.scoring_enabled
        or summary.selection_enabled
        or summary.optimization_enabled
        or summary.repair_enabled
        or summary.traversal_enabled
        or summary.graph_execution_enabled
        or summary.routing_execution_enabled
        or summary.dependency_resolution_enabled
        or summary.runtime_mutation_enabled
    )
    return {
        "valid": (
            set(required_categories).issubset(set(categories))
            and all(summary.deterministic for summary in topology.explainability_summaries)
            and all(summary.fail_visible for summary in topology.explainability_summaries)
            and all(summary.descriptive_only for summary in topology.explainability_summaries)
            and corrective_count == 0
        ),
        "explainability_summary_count": len(topology.explainability_summaries),
        "explainability_categories": categories,
        "required_categories": required_categories,
        "deterministic": all(summary.deterministic for summary in topology.explainability_summaries),
        "fail_visible": all(summary.fail_visible for summary in topology.explainability_summaries),
        "descriptive_only": all(summary.descriptive_only for summary in topology.explainability_summaries),
        "corrective_explainability_count": corrective_count,
    }


def validate_topology_non_execution(topology: OrchestrationTopology) -> dict[str, object]:
    enabled_flags = enabled_topology_capability_flags(topology)
    return {
        "valid": len(enabled_flags) == 0 and topology.non_executable and topology.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": topology.non_executable,
        "descriptive_only": topology.descriptive_only,
        "traversal_disabled": not topology.traversal_enabled,
        "graph_execution_disabled": not topology.graph_execution_enabled,
        "orchestration_execution_disabled": not topology.orchestration_execution_enabled,
        "runtime_execution_disabled": not topology.runtime_execution_enabled,
        "routing_execution_disabled": not topology.routing_execution_enabled,
        "scheduling_execution_disabled": not topology.scheduling_execution_enabled,
        "sequencing_execution_disabled": not topology.sequencing_execution_enabled,
        "dependency_resolution_disabled": not topology.dependency_resolution_enabled,
        "route_selection_disabled": not topology.route_selection_enabled,
        "topology_based_execution_disabled": not topology.topology_based_execution_enabled,
        "topology_based_routing_disabled": not topology.topology_based_routing_enabled,
        "topology_based_recommendation_disabled": not topology.topology_based_recommendation_enabled,
        "automatic_remediation_disabled": not topology.automatic_remediation_enabled,
        "topology_repair_disabled": not topology.topology_repair_enabled,
        "graph_repair_disabled": not topology.graph_repair_enabled,
        "orchestration_inference_disabled": not topology.orchestration_inference_enabled,
        "operational_authorization_disabled": not topology.operational_authorization_enabled,
        "readiness_approval_disabled": not topology.readiness_approval_enabled,
        "planner_integration_disabled": not topology.planner_integration_enabled,
        "production_consumption_disabled": not topology.production_consumption_enabled,
        "runtime_mutation_disabled": not topology.runtime_mutation_enabled,
        "operational_state_mutation_disabled": not topology.operational_state_mutation_enabled,
        "recommendation_disabled": not topology.recommendation_enabled,
        "ranking_disabled": not topology.ranking_enabled,
        "scoring_disabled": not topology.scoring_enabled,
        "selection_disabled": not topology.selection_enabled,
        "optimization_disabled": not topology.optimization_enabled,
        "hidden_orchestration_behavior_absent": not topology.hidden_orchestration_behavior_enabled,
        "implicit_execution_pathway_absent": not topology.implicit_execution_pathway_enabled,
        "graph_engine_absent": not topology.graph_engine_enabled,
        "traversal_engine_absent": not topology.traversal_engine_enabled,
        "routing_engine_absent": not topology.routing_engine_enabled,
        "dependency_resolver_absent": not topology.dependency_resolver_enabled,
    }


def build_orchestration_topology_diagnostics(topology: OrchestrationTopology | None = None) -> dict[str, Any]:
    source = topology or default_orchestration_topology()
    identity = validate_topology_identity(source)
    structure = validate_topology_structure(source)
    visibility = validate_topology_relationship_visibility(source)
    metadata = validate_topology_metadata(source)
    continuity = validate_topology_continuity(source)
    explainability = validate_topology_explainability(source)
    non_execution = validate_topology_non_execution(source)
    enabled_flags = enabled_topology_capability_flags(source)
    return {
        "topology_hash": hash_orchestration_topology(source),
        "node_hashes": [hash_orchestration_topology_node(node) for node in source.nodes],
        "edge_hashes": [hash_orchestration_topology_edge(edge) for edge in source.edges],
        "relationship_hashes": [
            hash_orchestration_topology_relationship(relationship) for relationship in source.relationships
        ],
        "diagnostic_hashes": [
            hash_orchestration_topology_diagnostic(diagnostic) for diagnostic in source.diagnostics
        ],
        "continuity_hashes": [
            hash_orchestration_topology_continuity_metadata(metadata_record)
            for metadata_record in source.continuity_metadata
        ],
        "identity_validation": identity,
        "structure_validation": structure,
        "relationship_visibility_validation": visibility,
        "metadata_validation": metadata,
        "continuity_validation": continuity,
        "explainability_validation": explainability,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "unsupported_relationship_ids": aggregate_unsupported_relationships(source),
        "prohibited_relationship_ids": aggregate_prohibited_relationships(source),
        "blocked_relationship_ids": aggregate_blocked_relationships(source),
        "stale_relationship_ids": aggregate_stale_relationships(source),
        "conflicting_relationship_ids": aggregate_conflicting_relationships(source),
        "missing_metadata_relationship_ids": aggregate_missing_metadata_relationships(source),
        "unknown_relationship_ids": tuple(sorted(source.relationship_visibility.unknown_relationship_ids)),
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "repair_absent": all(not diagnostic.repair_enabled for diagnostic in source.diagnostics),
        "inference_absent": all(not diagnostic.inference_enabled for diagnostic in source.diagnostics),
        "auto_correction_absent": all(not diagnostic.auto_correction_enabled for diagnostic in source.diagnostics),
        "authorization_absent": all(
            not diagnostic.authorization_enabled and not diagnostic.readiness_approval_enabled
            for diagnostic in source.diagnostics
        ),
        "execution_absent": all(
            not diagnostic.traversal_enabled
            and not diagnostic.graph_execution_enabled
            and not diagnostic.orchestration_execution_enabled
            and not diagnostic.runtime_execution_enabled
            and not diagnostic.routing_execution_enabled
            and not diagnostic.scheduling_execution_enabled
            and not diagnostic.sequencing_execution_enabled
            for diagnostic in source.diagnostics
        ),
        "selection_systems_absent": all(
            not diagnostic.recommendation_enabled
            and not diagnostic.ranking_enabled
            and not diagnostic.scoring_enabled
            and not diagnostic.selection_enabled
            and not diagnostic.optimization_enabled
            for diagnostic in source.diagnostics
        ),
        "fail_visible_warning_count": (
            len(visibility["unsupported_relationship_ids"])
            + len(visibility["prohibited_relationship_ids"])
            + len(visibility["blocked_relationship_ids"])
            + len(visibility["stale_relationship_ids"])
            + len(visibility["conflicting_relationship_ids"])
            + len(visibility["missing_metadata_relationship_ids"])
            + len(visibility["unknown_relationship_ids"])
        ),
    }
