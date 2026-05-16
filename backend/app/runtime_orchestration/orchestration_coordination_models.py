"""Declarative orchestration coordination planning models for v3.5."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize


@dataclass(frozen=True)
class OrchestrationCoordinationNode:
    node_id: str
    coordination_scope_id: str
    dependency_references: tuple[str, ...]
    blocker_reasons: tuple[str, ...]
    unsupported_reasons: tuple[str, ...]
    prohibited_reasons: tuple[str, ...]
    manual_review_reasons: tuple[str, ...]
    lineage_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    environment_references: tuple[str, ...]
    compatibility_references: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationCoordinationEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    dependency_reference: str
    sequencing_rule: str


@dataclass(frozen=True)
class OrchestrationCoordinationGraph:
    coordination_scope_id: str
    coordination_planning_graph_id: str
    coordination_scope_ids: tuple[str, ...]
    nodes: tuple[OrchestrationCoordinationNode, ...]
    edges: tuple[OrchestrationCoordinationEdge, ...]
    upstream_coordination_scopes: tuple[str, ...]
    downstream_coordination_scopes: tuple[str, ...]
    replay_lineage_aggregation: tuple[str, ...]
    rollback_lineage_aggregation: tuple[str, ...]
    governance_lineage_aggregation: tuple[str, ...]
    compatibility_lineage_aggregation: tuple[str, ...]
    environment_lineage_aggregation: tuple[str, ...]
    planning_only: bool = True
    graph_execution_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_behavior_enabled: bool = False
    mutation_behavior_enabled: bool = False
    audit_log_writing_enabled: bool = False
    production_consumption_enabled: bool = False


def default_orchestration_coordination_graph() -> OrchestrationCoordinationGraph:
    nodes = (
        OrchestrationCoordinationNode(
            node_id="coordination-node-governance-consumption",
            coordination_scope_id="coordination-scope-governance-consumption",
            dependency_references=("v3_5_governance_consumption_contract",),
            blocker_reasons=(),
            unsupported_reasons=(),
            prohibited_reasons=(),
            manual_review_reasons=(),
            lineage_references=("v3_5_governance_consumption_contract",),
            replay_lineage_references=("replay-lineage-v3-5-governance-consumption",),
            rollback_lineage_references=("rollback-lineage-v3-5-governance-consumption",),
            environment_references=("non_production_environment_isolated",),
            compatibility_references=("v3_4_governance_chain_compatible",),
        ),
        OrchestrationCoordinationNode(
            node_id="coordination-node-readiness-evaluation",
            coordination_scope_id="coordination-scope-readiness-evaluation",
            dependency_references=("v3_5_orchestration_readiness_evaluation",),
            blocker_reasons=(),
            unsupported_reasons=(),
            prohibited_reasons=(),
            manual_review_reasons=(),
            lineage_references=("v3_5_orchestration_readiness_evaluation",),
            replay_lineage_references=("replay-lineage-v3-5-governance-consumption",),
            rollback_lineage_references=("rollback-lineage-v3-5-governance-consumption",),
            environment_references=("non_production_environment_isolated",),
            compatibility_references=("v3_4_governance_chain_compatible",),
        ),
        OrchestrationCoordinationNode(
            node_id="coordination-node-dependency-resolution",
            coordination_scope_id="coordination-scope-dependency-resolution",
            dependency_references=("v3_5_governance_dependency_resolution",),
            blocker_reasons=(),
            unsupported_reasons=(),
            prohibited_reasons=(),
            manual_review_reasons=(),
            lineage_references=("v3_5_governance_dependency_resolution",),
            replay_lineage_references=("replay-lineage-v3-5-governance-consumption",),
            rollback_lineage_references=("rollback-lineage-v3-5-governance-consumption",),
            environment_references=("non_production_environment_isolated",),
            compatibility_references=("v3_4_governance_chain_compatible",),
        ),
    )
    return OrchestrationCoordinationGraph(
        coordination_scope_id="coordination-scope-v3-5-phase-4",
        coordination_planning_graph_id="coordination-graph-v3-5-phase-4",
        coordination_scope_ids=tuple(node.coordination_scope_id for node in nodes),
        nodes=nodes,
        edges=(
            OrchestrationCoordinationEdge(
                edge_id="edge-governance-consumption-to-readiness-evaluation",
                source_node_id="coordination-node-governance-consumption",
                target_node_id="coordination-node-readiness-evaluation",
                dependency_reference="v3_5_governance_consumption_contract",
                sequencing_rule="source_before_target",
            ),
            OrchestrationCoordinationEdge(
                edge_id="edge-readiness-evaluation-to-dependency-resolution",
                source_node_id="coordination-node-readiness-evaluation",
                target_node_id="coordination-node-dependency-resolution",
                dependency_reference="v3_5_orchestration_readiness_evaluation",
                sequencing_rule="source_before_target",
            ),
        ),
        upstream_coordination_scopes=("coordination-scope-governance-consumption",),
        downstream_coordination_scopes=("coordination-scope-dependency-resolution",),
        replay_lineage_aggregation=("replay-lineage-v3-5-governance-consumption",),
        rollback_lineage_aggregation=("rollback-lineage-v3-5-governance-consumption",),
        governance_lineage_aggregation=(
            "v3_5_governance_consumption_contract",
            "v3_5_governance_dependency_resolution",
            "v3_5_orchestration_readiness_evaluation",
        ),
        compatibility_lineage_aggregation=("v3_4_governance_chain_compatible",),
        environment_lineage_aggregation=("non_production_environment_isolated",),
    )


def export_coordination_node(node: OrchestrationCoordinationNode) -> dict[str, Any]:
    data = asdict(node)
    for field in (
        "dependency_references",
        "blocker_reasons",
        "unsupported_reasons",
        "prohibited_reasons",
        "manual_review_reasons",
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "environment_references",
        "compatibility_references",
    ):
        data[field] = sorted(data[field])
    return data


def export_coordination_edge(edge: OrchestrationCoordinationEdge) -> dict[str, Any]:
    return asdict(edge)


def export_coordination_graph(graph: OrchestrationCoordinationGraph) -> dict[str, Any]:
    data = asdict(graph)
    data["nodes"] = [export_coordination_node(node) for node in sorted(graph.nodes, key=lambda row: row.node_id)]
    data["edges"] = [export_coordination_edge(edge) for edge in sorted(graph.edges, key=lambda row: row.edge_id)]
    for field in (
        "coordination_scope_ids",
        "upstream_coordination_scopes",
        "downstream_coordination_scopes",
        "replay_lineage_aggregation",
        "rollback_lineage_aggregation",
        "governance_lineage_aggregation",
        "compatibility_lineage_aggregation",
        "environment_lineage_aggregation",
    ):
        data[field] = sorted(data[field])
    return data


def serialize_coordination_graph(graph: OrchestrationCoordinationGraph) -> str:
    return stable_serialize(export_coordination_graph(graph))


def hash_coordination_graph(graph: OrchestrationCoordinationGraph) -> str:
    return deterministic_hash(export_coordination_graph(graph))
