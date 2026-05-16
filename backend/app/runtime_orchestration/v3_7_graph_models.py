"""Deterministic v3.7 orchestration planning graph models.

These models describe structural orchestration reasoning only. They do not
perform graph traversal, scheduling, routing, dispatch, mutation, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V3_7_GRAPH_SCHEMA_VERSION = "v3_7.orchestration_planning_graph.1"
V3_7_GRAPH_FOUNDATIONS_PHASE_ID = "v3_7_graph_foundations"
V3_7_STRUCTURAL_REASONING_ONLY = "structural_orchestration_reasoning_only"
V3_7_VISIBILITY_VISIBLE = "visible"
V3_7_VISIBILITY_GAP = "visibility_gap"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphIdentity:
    graph_id: str
    schema_version: str
    phase_id: str
    graph_version: str
    structural_purpose: str


@dataclass(frozen=True)
class V37GraphMetadataEntry:
    metadata_key: str
    metadata_value: str
    included_in_hash: bool = True


@dataclass(frozen=True)
class V37GraphProvenance:
    provenance_id: str
    source_phase_id: str
    source_artifact_id: str
    source_kind: str
    lineage_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    governance_references: tuple[str, ...]
    compatibility_references: tuple[str, ...]
    explainability_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "lineage_references",
            "replay_lineage_references",
            "rollback_lineage_references",
            "governance_references",
            "compatibility_references",
            "explainability_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphNodeIdentity:
    node_id: str
    node_type: str
    node_label: str
    structural_purpose: str


@dataclass(frozen=True)
class V37GraphEdgeIdentity:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    structural_purpose: str


@dataclass(frozen=True)
class V37GraphGovernanceBoundary:
    boundary_id: str
    boundary_type: str
    visibility_status: str
    restriction_summary: str
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphCompatibilityBoundary:
    boundary_id: str
    source_domain: str
    target_domain: str
    compatibility_status: str
    blocker_ids: tuple[str, ...]
    unsupported_domain_ids: tuple[str, ...]
    prohibited_domain_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("blocker_ids", "unsupported_domain_ids", "prohibited_domain_ids"):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphVisibilityFinding:
    finding_id: str
    finding_kind: str
    scope_id: str
    visibility_status: str
    reason: str
    provenance_references: tuple[str, ...]

    def __post_init__(self) -> None:
        _set_tuple_field(self, "provenance_references")


@dataclass(frozen=True)
class V37GraphNode:
    identity: V37GraphNodeIdentity
    governance_boundary_ids: tuple[str, ...]
    compatibility_boundary_ids: tuple[str, ...]
    blocker_ids: tuple[str, ...]
    unsupported_domain_ids: tuple[str, ...]
    prohibited_domain_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    metadata: tuple[V37GraphMetadataEntry, ...] = ()
    node_executable: bool = False
    action_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "governance_boundary_ids",
            "compatibility_boundary_ids",
            "blocker_ids",
            "unsupported_domain_ids",
            "prohibited_domain_ids",
            "explainability_evidence_ids",
        ):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphEdge:
    identity: V37GraphEdgeIdentity
    governance_boundary_ids: tuple[str, ...]
    compatibility_boundary_ids: tuple[str, ...]
    blocker_ids: tuple[str, ...]
    unsupported_domain_ids: tuple[str, ...]
    prohibited_domain_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    metadata: tuple[V37GraphMetadataEntry, ...] = ()
    edge_executable: bool = False
    traversal_enabled: bool = False
    execution_flow_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "governance_boundary_ids",
            "compatibility_boundary_ids",
            "blocker_ids",
            "unsupported_domain_ids",
            "prohibited_domain_ids",
            "explainability_evidence_ids",
        ):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphExplainabilityEvidence:
    evidence_id: str
    subject_id: str
    subject_type: str
    why_exists: str
    governance_restrictions: tuple[str, ...]
    unsupported_boundaries: tuple[str, ...]
    prohibited_boundaries: tuple[str, ...]
    compatibility_visibility: tuple[str, ...]
    provenance_lineage: tuple[str, ...]
    continuity_references: tuple[str, ...]
    provenance: V37GraphProvenance

    def __post_init__(self) -> None:
        for field_name in (
            "governance_restrictions",
            "unsupported_boundaries",
            "prohibited_boundaries",
            "compatibility_visibility",
            "provenance_lineage",
            "continuity_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphContinuityEvidence:
    continuity_id: str
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    provenance_lineage_references: tuple[str, ...]
    explainability_lineage_references: tuple[str, ...]
    governance_lineage_references: tuple[str, ...]
    compatibility_lineage_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "replay_lineage_references",
            "rollback_lineage_references",
            "provenance_lineage_references",
            "explainability_lineage_references",
            "governance_lineage_references",
            "compatibility_lineage_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37OrchestrationPlanningGraph:
    identity: V37GraphIdentity
    metadata: tuple[V37GraphMetadataEntry, ...]
    provenance: V37GraphProvenance
    nodes: tuple[V37GraphNode, ...]
    edges: tuple[V37GraphEdge, ...]
    governance_boundaries: tuple[V37GraphGovernanceBoundary, ...]
    compatibility_boundaries: tuple[V37GraphCompatibilityBoundary, ...]
    blockers: tuple[V37GraphVisibilityFinding, ...]
    unsupported_domains: tuple[V37GraphVisibilityFinding, ...]
    prohibited_domains: tuple[V37GraphVisibilityFinding, ...]
    explainability_evidence: tuple[V37GraphExplainabilityEvidence, ...]
    continuity_evidence: tuple[V37GraphContinuityEvidence, ...]
    planning_only: bool = True
    structural_reasoning_only: bool = True
    non_executable: bool = True
    graph_execution_enabled: bool = False
    graph_traversal_execution_enabled: bool = False
    runtime_dispatch_enabled: bool = False
    scheduling_enabled: bool = False
    routing_enabled: bool = False
    mutation_enabled: bool = False
    persistent_runtime_writes_enabled: bool = False
    background_processing_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "metadata",
            "nodes",
            "edges",
            "governance_boundaries",
            "compatibility_boundaries",
            "blockers",
            "unsupported_domains",
            "prohibited_domains",
            "explainability_evidence",
            "continuity_evidence",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_v3_7_graph_provenance(subject_id: str, source_kind: str) -> V37GraphProvenance:
    return V37GraphProvenance(
        provenance_id=f"v3-7-provenance-{subject_id}",
        source_phase_id=V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
        source_artifact_id=subject_id,
        source_kind=source_kind,
        lineage_references=("v3_6_closeout_and_v3_7_readiness", subject_id),
        replay_lineage_references=("v3_6_replay_continuity", "v3_7_graph_replay_continuity"),
        rollback_lineage_references=("v3_6_rollback_continuity", "v3_7_graph_rollback_continuity"),
        governance_references=("v3_7_non_execution_governance_boundary",),
        compatibility_references=("v3_6_to_v3_7_graph_foundation_compatibility",),
        explainability_references=("v3_7_graph_explainability_evidence",),
    )


def default_v3_7_orchestration_planning_graph() -> V37OrchestrationPlanningGraph:
    identity = V37GraphIdentity(
        graph_id="v3-7-deterministic-orchestration-planning-graph",
        schema_version=V3_7_GRAPH_SCHEMA_VERSION,
        phase_id=V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
        graph_version="v3.7",
        structural_purpose=V3_7_STRUCTURAL_REASONING_ONLY,
    )
    metadata = (
        V37GraphMetadataEntry("deterministic_serializer", "json_sort_keys_stable_tuples"),
        V37GraphMetadataEntry("edge_semantics", "structural_relationship_only"),
        V37GraphMetadataEntry("node_semantics", "declarative_boundary_only"),
        V37GraphMetadataEntry("runtime_capability", "none"),
    )
    graph_provenance = default_v3_7_graph_provenance(identity.graph_id, "graph")
    governance_boundaries = (
        V37GraphGovernanceBoundary(
            boundary_id="v3_7_non_execution_governance_boundary",
            boundary_type="non_execution",
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            restriction_summary="graphs model structural orchestration reasoning only",
            provenance=default_v3_7_graph_provenance("v3_7_non_execution_governance_boundary", "governance_boundary"),
        ),
        V37GraphGovernanceBoundary(
            boundary_id="v3_7_governance_visibility_boundary",
            boundary_type="governance_visibility",
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            restriction_summary="governance restrictions remain visible in graph evidence",
            provenance=default_v3_7_graph_provenance("v3_7_governance_visibility_boundary", "governance_boundary"),
        ),
    )
    blockers = (
        V37GraphVisibilityFinding(
            finding_id="v3_7_blocker_execution_prohibited",
            finding_kind="blocker",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="execution capability is prohibited for graph foundations",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
        V37GraphVisibilityFinding(
            finding_id="v3_7_blocker_routing_scheduling_dispatch_prohibited",
            finding_kind="blocker",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="routing, scheduling, and dispatch remain prohibited",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
    )
    unsupported_domains = (
        V37GraphVisibilityFinding(
            finding_id="v3_7_unsupported_runtime_dispatch_domain",
            finding_kind="unsupported_domain",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="runtime dispatch is outside the graph foundation domain",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
        V37GraphVisibilityFinding(
            finding_id="v3_7_unsupported_optimization_domain",
            finding_kind="unsupported_domain",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="optimization systems are outside the graph foundation domain",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
    )
    prohibited_domains = (
        V37GraphVisibilityFinding(
            finding_id="v3_7_prohibited_graph_execution_domain",
            finding_kind="prohibited_domain",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="graph execution is prohibited",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
        V37GraphVisibilityFinding(
            finding_id="v3_7_prohibited_routing_scheduling_dispatch_domain",
            finding_kind="prohibited_domain",
            scope_id=identity.graph_id,
            visibility_status=V3_7_VISIBILITY_VISIBLE,
            reason="routing, scheduling, and dispatch are prohibited",
            provenance_references=("v3_7_non_execution_governance_boundary",),
        ),
    )
    compatibility_boundaries = (
        V37GraphCompatibilityBoundary(
            boundary_id="v3_6_to_v3_7_graph_foundation_compatibility",
            source_domain="v3_6_closeout_and_v3_7_readiness",
            target_domain=V3_7_GRAPH_FOUNDATIONS_PHASE_ID,
            compatibility_status="compatible_for_structural_reasoning_only",
            blocker_ids=tuple(item.finding_id for item in blockers),
            unsupported_domain_ids=tuple(item.finding_id for item in unsupported_domains),
            prohibited_domain_ids=tuple(item.finding_id for item in prohibited_domains),
            provenance=default_v3_7_graph_provenance(
                "v3_6_to_v3_7_graph_foundation_compatibility",
                "compatibility_boundary",
            ),
        ),
    )
    node_ids = (
        "v3_7_node_governance_boundary_visibility",
        "v3_7_node_provenance_continuity",
        "v3_7_node_explainability_continuity",
    )
    evidence_ids = tuple(f"v3_7_evidence_{node_id}" for node_id in node_ids)
    nodes = tuple(
        V37GraphNode(
            identity=V37GraphNodeIdentity(
                node_id=node_id,
                node_type="structural_boundary",
                node_label=node_id.replace("v3_7_node_", ""),
                structural_purpose=V3_7_STRUCTURAL_REASONING_ONLY,
            ),
            governance_boundary_ids=tuple(item.boundary_id for item in governance_boundaries),
            compatibility_boundary_ids=tuple(item.boundary_id for item in compatibility_boundaries),
            blocker_ids=tuple(item.finding_id for item in blockers),
            unsupported_domain_ids=tuple(item.finding_id for item in unsupported_domains),
            prohibited_domain_ids=tuple(item.finding_id for item in prohibited_domains),
            provenance=default_v3_7_graph_provenance(node_id, "node"),
            explainability_evidence_ids=(evidence_id,),
        )
        for node_id, evidence_id in zip(node_ids, evidence_ids)
    )
    edge_specs = (
        (
            "v3_7_edge_governance_visibility_to_provenance_continuity",
            node_ids[0],
            node_ids[1],
            "governance_visibility_supports_provenance_continuity",
        ),
        (
            "v3_7_edge_provenance_continuity_to_explainability_continuity",
            node_ids[1],
            node_ids[2],
            "provenance_continuity_supports_explainability_continuity",
        ),
    )
    edge_evidence_ids = tuple(f"v3_7_evidence_{edge_id}" for edge_id, _, _, _ in edge_specs)
    edges = tuple(
        V37GraphEdge(
            identity=V37GraphEdgeIdentity(
                edge_id=edge_id,
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                relationship_type=relationship_type,
                structural_purpose="structural_relationship_only_not_execution_flow",
            ),
            governance_boundary_ids=tuple(item.boundary_id for item in governance_boundaries),
            compatibility_boundary_ids=tuple(item.boundary_id for item in compatibility_boundaries),
            blocker_ids=tuple(item.finding_id for item in blockers),
            unsupported_domain_ids=tuple(item.finding_id for item in unsupported_domains),
            prohibited_domain_ids=tuple(item.finding_id for item in prohibited_domains),
            provenance=default_v3_7_graph_provenance(edge_id, "edge"),
            explainability_evidence_ids=(evidence_id,),
        )
        for (edge_id, source_node_id, target_node_id, relationship_type), evidence_id in zip(
            edge_specs,
            edge_evidence_ids,
        )
    )
    explainability_evidence = tuple(
        V37GraphExplainabilityEvidence(
            evidence_id=evidence_id,
            subject_id=node.identity.node_id,
            subject_type="node",
            why_exists="node preserves deterministic structural graph boundary evidence",
            governance_restrictions=tuple(item.boundary_id for item in governance_boundaries),
            unsupported_boundaries=tuple(item.finding_id for item in unsupported_domains),
            prohibited_boundaries=tuple(item.finding_id for item in prohibited_domains),
            compatibility_visibility=tuple(item.boundary_id for item in compatibility_boundaries),
            provenance_lineage=node.provenance.lineage_references,
            continuity_references=("v3_7_graph_continuity_evidence",),
            provenance=default_v3_7_graph_provenance(evidence_id, "explainability_evidence"),
        )
        for node, evidence_id in zip(nodes, evidence_ids)
    ) + tuple(
        V37GraphExplainabilityEvidence(
            evidence_id=evidence_id,
            subject_id=edge.identity.edge_id,
            subject_type="edge",
            why_exists="edge preserves a structural reasoning relationship and does not imply execution flow",
            governance_restrictions=tuple(item.boundary_id for item in governance_boundaries),
            unsupported_boundaries=tuple(item.finding_id for item in unsupported_domains),
            prohibited_boundaries=tuple(item.finding_id for item in prohibited_domains),
            compatibility_visibility=tuple(item.boundary_id for item in compatibility_boundaries),
            provenance_lineage=edge.provenance.lineage_references,
            continuity_references=("v3_7_graph_continuity_evidence",),
            provenance=default_v3_7_graph_provenance(evidence_id, "explainability_evidence"),
        )
        for edge, evidence_id in zip(edges, edge_evidence_ids)
    )
    continuity_evidence = (
        V37GraphContinuityEvidence(
            continuity_id="v3_7_graph_continuity_evidence",
            replay_lineage_references=("v3_6_replay_continuity", "v3_7_graph_replay_continuity"),
            rollback_lineage_references=("v3_6_rollback_continuity", "v3_7_graph_rollback_continuity"),
            provenance_lineage_references=tuple(
                sorted(
                    {graph_provenance.provenance_id}
                    | {node.provenance.provenance_id for node in nodes}
                    | {edge.provenance.provenance_id for edge in edges}
                )
            ),
            explainability_lineage_references=tuple(item.evidence_id for item in explainability_evidence),
            governance_lineage_references=tuple(item.boundary_id for item in governance_boundaries),
            compatibility_lineage_references=tuple(item.boundary_id for item in compatibility_boundaries),
            deterministic_hash_references=("v3_7_graph_hash",),
        ),
    )
    return V37OrchestrationPlanningGraph(
        identity=identity,
        metadata=metadata,
        provenance=graph_provenance,
        nodes=nodes,
        edges=edges,
        governance_boundaries=governance_boundaries,
        compatibility_boundaries=compatibility_boundaries,
        blockers=blockers,
        unsupported_domains=unsupported_domains,
        prohibited_domains=prohibited_domains,
        explainability_evidence=explainability_evidence,
        continuity_evidence=continuity_evidence,
    )
