"""Deterministic v4.3 orchestration topology visibility models.

Orchestration topology is descriptive governance evidence only. It describes
structural relationships between governance nodes without traversal, routing,
dependency resolution, scheduling, sequencing, execution, repair, inference,
authorization, planner integration, production consumption, or mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .orchestration_manifest_hashing import hash_orchestration_manifest
from .orchestration_manifest_models import (
    OrchestrationManifest,
    default_orchestration_manifest,
)


V4_3_ORCHESTRATION_TOPOLOGY_PHASE_ID = "v4_3_orchestration_topology_visibility"
V4_3_ORCHESTRATION_TOPOLOGY_SCHEMA_VERSION = "v4_3.orchestration_topology_visibility.1"
V4_3_ORCHESTRATION_TOPOLOGY_REPORT_SCHEMA_VERSION = (
    "v4_3.orchestration_topology_visibility_report.1"
)
V4_3_ORCHESTRATION_TOPOLOGY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_3_ORCHESTRATION_TOPOLOGY_STATUS_STABLE = "v4_3_orchestration_topology_visibility_stable"
V4_3_ORCHESTRATION_TOPOLOGY_STATUS_BLOCKED = "v4_3_orchestration_topology_visibility_blocked"
V4_3_ORCHESTRATION_TOPOLOGY_PURPOSE = "deterministic_orchestration_topology_visibility_only"

TOPOLOGY_STATE_SUPPORTED = "supported"
TOPOLOGY_STATE_UNSUPPORTED = "unsupported"
TOPOLOGY_STATE_BLOCKED = "blocked"
TOPOLOGY_STATE_PROHIBITED = "prohibited"
TOPOLOGY_STATE_STALE = "stale"
TOPOLOGY_STATE_CONFLICTING = "conflicting"
TOPOLOGY_STATE_MISSING_METADATA = "missing_metadata"
TOPOLOGY_STATE_UNKNOWN = "unknown"
TOPOLOGY_STATES: tuple[str, ...] = (
    TOPOLOGY_STATE_SUPPORTED,
    TOPOLOGY_STATE_UNSUPPORTED,
    TOPOLOGY_STATE_BLOCKED,
    TOPOLOGY_STATE_PROHIBITED,
    TOPOLOGY_STATE_STALE,
    TOPOLOGY_STATE_CONFLICTING,
    TOPOLOGY_STATE_MISSING_METADATA,
    TOPOLOGY_STATE_UNKNOWN,
)
FAIL_VISIBLE_TOPOLOGY_STATES: tuple[str, ...] = (
    TOPOLOGY_STATE_UNSUPPORTED,
    TOPOLOGY_STATE_BLOCKED,
    TOPOLOGY_STATE_PROHIBITED,
    TOPOLOGY_STATE_STALE,
    TOPOLOGY_STATE_CONFLICTING,
    TOPOLOGY_STATE_MISSING_METADATA,
    TOPOLOGY_STATE_UNKNOWN,
)

TOPOLOGY_RELATIONSHIP_MANIFEST_TO_GOVERNANCE = "manifest_to_governance_boundary"
TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_PROVIDER = "governance_to_future_provider_contract"
TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_OPERATIONAL_ACTIVATION = (
    "governance_to_operational_activation"
)
TOPOLOGY_RELATIONSHIP_MANIFEST_TO_PRIOR_COORDINATION = "manifest_to_prior_coordination_snapshot"
TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_AUTHORIZATION = "governance_to_execution_authorization"
TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_RUNTIME_POLICY = "governance_to_runtime_execution_policy"
TOPOLOGY_RELATIONSHIP_ACTIVATION_TO_EXECUTION = "operational_activation_to_runtime_execution"
TOPOLOGY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    TOPOLOGY_RELATIONSHIP_MANIFEST_TO_GOVERNANCE,
    TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_PROVIDER,
    TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_OPERATIONAL_ACTIVATION,
    TOPOLOGY_RELATIONSHIP_MANIFEST_TO_PRIOR_COORDINATION,
    TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_AUTHORIZATION,
    TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_RUNTIME_POLICY,
    TOPOLOGY_RELATIONSHIP_ACTIVATION_TO_EXECUTION,
)
PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    TOPOLOGY_RELATIONSHIP_ACTIVATION_TO_EXECUTION,
    "topology_based_execution",
    "topology_based_routing",
    "topology_based_recommendation",
    "route_selection",
    "dependency_resolution",
    "scheduling_sequence",
    "sequencing_execution",
)
UNSUPPORTED_TOPOLOGY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_PROVIDER,
    "future_manifest_consumer",
)

TOPOLOGY_DIAGNOSTIC_IDENTITY = "topology_identity_visibility"
TOPOLOGY_DIAGNOSTIC_DUPLICATE_NODE = "duplicate_node_visibility"
TOPOLOGY_DIAGNOSTIC_DUPLICATE_EDGE = "duplicate_edge_visibility"
TOPOLOGY_DIAGNOSTIC_SOURCE_TARGET = "source_target_visibility"
TOPOLOGY_DIAGNOSTIC_PROHIBITED_RELATIONSHIP = "prohibited_relationship_visibility"
TOPOLOGY_DIAGNOSTIC_UNSUPPORTED_RELATIONSHIP = "unsupported_relationship_visibility"
TOPOLOGY_DIAGNOSTIC_BLOCKED_RELATIONSHIP = "blocked_relationship_visibility"
TOPOLOGY_DIAGNOSTIC_STALE_RELATIONSHIP = "stale_relationship_visibility"
TOPOLOGY_DIAGNOSTIC_CONFLICTING_RELATIONSHIP = "conflicting_relationship_visibility"
TOPOLOGY_DIAGNOSTIC_MISSING_METADATA = "missing_metadata_visibility"
TOPOLOGY_DIAGNOSTIC_EXPLAINABILITY = "explainability_visibility"
TOPOLOGY_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_ORCHESTRATION_TOPOLOGY_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "runtime_execution",
    "graph_traversal_execution",
    "routing_execution",
    "scheduling_execution",
    "sequencing_execution",
    "dependency_resolution",
    "topology_based_execution",
    "topology_based_routing",
    "topology_based_recommendations",
    "automatic_remediation",
    "topology_repair",
    "graph_repair",
    "orchestration_inference",
    "operational_authorization",
    "readiness_approval",
    "planner_integration",
    "production_consumption",
    "runtime_mutation",
    "operational_state_mutation",
    "ranking",
    "scoring",
    "selection",
    "optimization",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
    "graph_engine",
    "traversal_engine",
    "routing_engine",
    "dependency_resolver",
)

EXPLICIT_ORCHESTRATION_TOPOLOGY_LIMITATIONS: tuple[str, ...] = (
    "v4.3 Phase 2 creates deterministic orchestration topology visibility only.",
    "v4.3 Phase 2 describes structural relationships before traversal.",
    "v4.3 Phase 2 does not enable graph traversal execution.",
    "v4.3 Phase 2 does not enable orchestration execution.",
    "v4.3 Phase 2 does not enable runtime execution.",
    "v4.3 Phase 2 does not enable routing execution.",
    "v4.3 Phase 2 does not enable scheduling execution.",
    "v4.3 Phase 2 does not enable sequencing execution.",
    "v4.3 Phase 2 does not enable dependency resolution.",
    "v4.3 Phase 2 does not enable topology repair or graph repair.",
    "v4.3 Phase 2 does not enable orchestration inference.",
    "v4.3 Phase 2 does not enable operational authorization or readiness approval.",
    "v4.3 Phase 2 does not enable planner integration.",
    "v4.3 Phase 2 does not enable production consumption.",
    "v4.3 Phase 2 does not enable runtime or operational state mutation.",
    "v4.3 Phase 2 does not enable ranking, scoring, selection, optimization, or recommendations.",
)

EXPLICIT_ORCHESTRATION_TOPOLOGY_PROHIBITIONS: tuple[str, ...] = (
    "No graph traversal execution exists.",
    "No graph execution exists.",
    "No orchestration execution exists.",
    "No runtime execution exists.",
    "No routing execution exists.",
    "No scheduling execution exists.",
    "No sequencing execution exists.",
    "No dependency resolution exists.",
    "No topology-based execution exists.",
    "No topology-based routing exists.",
    "No topology-based recommendation exists.",
    "No automatic remediation exists.",
    "No topology repair exists.",
    "No graph repair exists.",
    "No orchestration inference exists.",
    "No operational authorization exists.",
    "No readiness approval exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No operational state mutation exists.",
    "No ranking, scoring, selection, or optimization exists.",
    "No hidden orchestration behavior exists.",
    "No implicit execution pathway exists.",
    "No graph engine exists.",
    "No traversal engine exists.",
    "No routing engine exists.",
    "No dependency resolver exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class OrchestrationTopologyIdentity:
    topology_id: str
    topology_version: str
    topology_classification: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    schema_version: str
    generated_at: str
    governance_reference: str
    lineage_reference: str
    provenance_reference: str
    continuity_reference: str
    diagnostics_reference: str
    explainability_reference: str
    non_execution_reference: str
    governance_purpose: str = V4_3_ORCHESTRATION_TOPOLOGY_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    topology_visibility_only: bool = True
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationTopologyMetadata:
    metadata_id: str
    phase_id: str
    topology_classification: str
    source_phase_reference: str
    source_report_references: tuple[str, ...]
    governance_metadata_reference: str
    lineage_metadata_reference: str
    provenance_metadata_reference: str
    continuity_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    non_execution_metadata_reference: str
    deterministic_order: int
    purpose: str = V4_3_ORCHESTRATION_TOPOLOGY_PURPOSE
    deterministic: bool = True
    replay_safe_evidence: bool = True
    rollback_safe_evidence: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    non_executing: bool = True
    non_routing: bool = True
    non_resolving: bool = True
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "source_report_references")


@dataclass(frozen=True)
class OrchestrationTopologyNode:
    node_id: str
    node_classification: str
    node_state: str
    manifest_reference: str
    governance_metadata_reference: str
    lineage_metadata_reference: str
    provenance_metadata_reference: str
    continuity_metadata_reference: str
    diagnostics_metadata_reference: str
    explainability_metadata_reference: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationTopologyEdge:
    edge_id: str
    edge_classification: str
    edge_state: str
    source_node_id: str
    target_node_id: str
    relationship_id: str
    source_node_visible: bool
    target_node_visible: bool
    deterministic_order: int
    self_reference_allowed: bool = False
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False


@dataclass(frozen=True)
class OrchestrationTopologyRelationship:
    relationship_id: str
    relationship_type: str
    relationship_classification: str
    relationship_state: str
    source_node_id: str
    target_node_id: str
    boundary_relationship_visible: bool
    deterministic_order: int
    unsupported_reason_visibility: tuple[str, ...] = ()
    prohibited_reason_visibility: tuple[str, ...] = ()
    blocked_reason_visibility: tuple[str, ...] = ()
    stale_reason_visibility: tuple[str, ...] = ()
    conflicting_reason_visibility: tuple[str, ...] = ()
    missing_metadata_visibility: tuple[str, ...] = ()
    governance_metadata_reference: str = "v4_3_orchestration_topology_governance_metadata"
    lineage_metadata_reference: str = "v4_3_orchestration_topology_lineage_metadata"
    provenance_metadata_reference: str = "v4_3_orchestration_topology_provenance_metadata"
    continuity_metadata_reference: str = "v4_3_orchestration_topology_continuity_metadata"
    diagnostics_metadata_reference: str = "v4_3_orchestration_topology_diagnostics_metadata"
    explainability_metadata_reference: str = "v4_3_orchestration_topology_explainability_metadata"
    fail_visible: bool = False
    descriptive_only: bool = True
    hidden: bool = False
    executable: bool = False
    routable: bool = False
    schedulable: bool = False
    resolvable: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_reason_visibility",
            "prohibited_reason_visibility",
            "blocked_reason_visibility",
            "stale_reason_visibility",
            "conflicting_reason_visibility",
            "missing_metadata_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationTopologyRelationshipVisibility:
    visibility_id: str
    boundary_relationship_ids: tuple[str, ...]
    unsupported_relationship_ids: tuple[str, ...]
    prohibited_relationship_ids: tuple[str, ...]
    blocked_relationship_ids: tuple[str, ...]
    stale_relationship_ids: tuple[str, ...]
    conflicting_relationship_ids: tuple[str, ...]
    missing_metadata_relationship_ids: tuple[str, ...]
    unknown_relationship_ids: tuple[str, ...]
    prohibited_relationship_types: tuple[str, ...]
    unsupported_relationship_types: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    automatic_remediation_enabled: bool = False

    def __post_init__(self) -> None:
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
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationTopologyContinuityMetadata:
    continuity_id: str
    continuity_type: str
    continuity_state: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    relationship_references: tuple[str, ...]
    replay_reference: str
    rollback_reference: str
    provenance_reference: str
    lineage_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    topology_continuity_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    automatic_remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references", "relationship_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationTopologyDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_node_ids: tuple[str, ...]
    affected_edge_ids: tuple[str, ...]
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    repair_enabled: bool = False
    inference_enabled: bool = False
    auto_correction_enabled: bool = False
    authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_node_ids", "affected_edge_ids", "affected_relationship_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class OrchestrationTopologyExplainability:
    explanation_id: str
    category: str
    summary: str
    affected_relationship_ids: tuple[str, ...]
    deterministic_order: int
    deterministic: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    repair_enabled: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_relationship_ids")


@dataclass(frozen=True)
class OrchestrationTopology:
    identity: OrchestrationTopologyIdentity
    metadata: OrchestrationTopologyMetadata
    nodes: tuple[OrchestrationTopologyNode, ...]
    edges: tuple[OrchestrationTopologyEdge, ...]
    relationships: tuple[OrchestrationTopologyRelationship, ...]
    relationship_visibility: OrchestrationTopologyRelationshipVisibility
    continuity_metadata: tuple[OrchestrationTopologyContinuityMetadata, ...]
    diagnostics: tuple[OrchestrationTopologyDiagnostic, ...]
    explainability_summaries: tuple[OrchestrationTopologyExplainability, ...]
    topology_classification: str = "governance_safe_topology_visibility_descriptive_only"
    non_executable: bool = True
    descriptive_only: bool = True
    topology_visibility_only: bool = True
    execution_authorized: bool = False
    traversal_enabled: bool = False
    graph_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    route_selection_enabled: bool = False
    topology_based_execution_enabled: bool = False
    topology_based_routing_enabled: bool = False
    topology_based_recommendation_enabled: bool = False
    automatic_remediation_enabled: bool = False
    topology_repair_enabled: bool = False
    graph_repair_enabled: bool = False
    orchestration_inference_enabled: bool = False
    operational_authorization_enabled: bool = False
    readiness_approval_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_state_mutation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    graph_engine_enabled: bool = False
    traversal_engine_enabled: bool = False
    routing_engine_enabled: bool = False
    dependency_resolver_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "nodes",
            "edges",
            "relationships",
            "continuity_metadata",
            "diagnostics",
            "explainability_summaries",
        ):
            _set_tuple_field(self, field_name)


def default_orchestration_topology_identity(
    manifest: OrchestrationManifest | None = None,
) -> OrchestrationTopologyIdentity:
    source_manifest = manifest or default_orchestration_manifest()
    return OrchestrationTopologyIdentity(
        topology_id="v4_3_orchestration_topology_primary",
        topology_version="v4.3.0-phase-2",
        topology_classification="descriptive_only_topology_visibility",
        source_manifest_reference=source_manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_orchestration_manifest(source_manifest),
        schema_version=V4_3_ORCHESTRATION_TOPOLOGY_SCHEMA_VERSION,
        generated_at=V4_3_ORCHESTRATION_TOPOLOGY_GENERATED_AT,
        governance_reference="v4_3_orchestration_topology_governance_primary",
        lineage_reference="v4_3_orchestration_topology_lineage_primary",
        provenance_reference="v4_3_orchestration_topology_provenance_primary",
        continuity_reference="v4_3_orchestration_topology_continuity_primary",
        diagnostics_reference="v4_3_orchestration_topology_diagnostics_primary",
        explainability_reference="v4_3_orchestration_topology_explainability_primary",
        non_execution_reference="v4_3_orchestration_topology_non_execution_primary",
    )


def default_orchestration_topology_metadata(
    identity: OrchestrationTopologyIdentity | None = None,
) -> OrchestrationTopologyMetadata:
    source = identity or default_orchestration_topology_identity()
    return OrchestrationTopologyMetadata(
        metadata_id="v4_3_orchestration_topology_metadata_primary",
        phase_id=V4_3_ORCHESTRATION_TOPOLOGY_PHASE_ID,
        topology_classification="descriptive_only_topology_visibility",
        source_phase_reference="v4_3_orchestration_manifest_foundations",
        source_report_references=(
            "docs/generated/v4_3_orchestration_manifest_foundations_report.json",
            "docs/migration/V4_3_ORCHESTRATION_MANIFEST_FOUNDATIONS.md",
        ),
        governance_metadata_reference=source.governance_reference,
        lineage_metadata_reference=source.lineage_reference,
        provenance_metadata_reference=source.provenance_reference,
        continuity_metadata_reference=source.continuity_reference,
        diagnostics_metadata_reference=source.diagnostics_reference,
        explainability_metadata_reference=source.explainability_reference,
        non_execution_metadata_reference=source.non_execution_reference,
        deterministic_order=10,
    )


def default_orchestration_topology_nodes() -> tuple[OrchestrationTopologyNode, ...]:
    common = {
        "manifest_reference": "v4_3_orchestration_manifest_primary",
        "governance_metadata_reference": "v4_3_orchestration_topology_governance_primary",
        "lineage_metadata_reference": "v4_3_orchestration_topology_lineage_primary",
        "provenance_metadata_reference": "v4_3_orchestration_topology_provenance_primary",
        "continuity_metadata_reference": "v4_3_orchestration_topology_continuity_primary",
        "diagnostics_metadata_reference": "v4_3_orchestration_topology_diagnostics_primary",
        "explainability_metadata_reference": "v4_3_orchestration_topology_explainability_primary",
    }
    return (
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_manifest_foundation",
            node_classification="manifest_foundation",
            node_state=TOPOLOGY_STATE_SUPPORTED,
            deterministic_order=10,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_governance_boundary",
            node_classification="governance_boundary",
            node_state=TOPOLOGY_STATE_SUPPORTED,
            deterministic_order=20,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_future_provider_contract",
            node_classification="future_provider_contract",
            node_state=TOPOLOGY_STATE_UNSUPPORTED,
            deterministic_order=30,
            fail_visible=True,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_operational_activation",
            node_classification="operational_activation",
            node_state=TOPOLOGY_STATE_BLOCKED,
            deterministic_order=40,
            fail_visible=True,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_prior_coordination_snapshot",
            node_classification="prior_coordination_snapshot",
            node_state=TOPOLOGY_STATE_STALE,
            deterministic_order=50,
            fail_visible=True,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_execution_authorization_metadata",
            node_classification="execution_authorization_metadata",
            node_state=TOPOLOGY_STATE_CONFLICTING,
            deterministic_order=60,
            fail_visible=True,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_runtime_execution_policy",
            node_classification="runtime_execution_policy",
            node_state=TOPOLOGY_STATE_MISSING_METADATA,
            deterministic_order=70,
            fail_visible=True,
            **common,
        ),
        OrchestrationTopologyNode(
            node_id="v4_3_topology_node_runtime_orchestration_execution",
            node_classification="runtime_orchestration_execution",
            node_state=TOPOLOGY_STATE_PROHIBITED,
            deterministic_order=80,
            fail_visible=True,
            **common,
        ),
    )


def default_orchestration_topology_relationships() -> tuple[OrchestrationTopologyRelationship, ...]:
    return (
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_manifest_to_governance",
            relationship_type=TOPOLOGY_RELATIONSHIP_MANIFEST_TO_GOVERNANCE,
            relationship_classification="boundary_relationship",
            relationship_state=TOPOLOGY_STATE_SUPPORTED,
            source_node_id="v4_3_topology_node_manifest_foundation",
            target_node_id="v4_3_topology_node_governance_boundary",
            boundary_relationship_visible=True,
            deterministic_order=10,
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_governance_to_provider",
            relationship_type=TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_PROVIDER,
            relationship_classification="unsupported_relationship",
            relationship_state=TOPOLOGY_STATE_UNSUPPORTED,
            source_node_id="v4_3_topology_node_governance_boundary",
            target_node_id="v4_3_topology_node_future_provider_contract",
            boundary_relationship_visible=True,
            deterministic_order=20,
            fail_visible=True,
            unsupported_reason_visibility=("future provider topology contracts remain unsupported",),
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_governance_to_activation",
            relationship_type=TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_OPERATIONAL_ACTIVATION,
            relationship_classification="blocked_relationship",
            relationship_state=TOPOLOGY_STATE_BLOCKED,
            source_node_id="v4_3_topology_node_governance_boundary",
            target_node_id="v4_3_topology_node_operational_activation",
            boundary_relationship_visible=True,
            deterministic_order=30,
            fail_visible=True,
            blocked_reason_visibility=("operational activation remains blocked by descriptive-only topology scope",),
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_manifest_to_prior_coordination",
            relationship_type=TOPOLOGY_RELATIONSHIP_MANIFEST_TO_PRIOR_COORDINATION,
            relationship_classification="stale_relationship",
            relationship_state=TOPOLOGY_STATE_STALE,
            source_node_id="v4_3_topology_node_manifest_foundation",
            target_node_id="v4_3_topology_node_prior_coordination_snapshot",
            boundary_relationship_visible=True,
            deterministic_order=40,
            fail_visible=True,
            stale_reason_visibility=("v4.2 coordination topology ancestry is read-only evidence",),
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_governance_to_authorization",
            relationship_type=TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_AUTHORIZATION,
            relationship_classification="conflicting_relationship",
            relationship_state=TOPOLOGY_STATE_CONFLICTING,
            source_node_id="v4_3_topology_node_governance_boundary",
            target_node_id="v4_3_topology_node_execution_authorization_metadata",
            boundary_relationship_visible=True,
            deterministic_order=50,
            fail_visible=True,
            conflicting_reason_visibility=(
                "execution authorization metadata conflicts with non-execution topology governance",
            ),
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_governance_to_runtime_policy",
            relationship_type=TOPOLOGY_RELATIONSHIP_GOVERNANCE_TO_RUNTIME_POLICY,
            relationship_classification="missing_metadata_relationship",
            relationship_state=TOPOLOGY_STATE_MISSING_METADATA,
            source_node_id="v4_3_topology_node_governance_boundary",
            target_node_id="v4_3_topology_node_runtime_execution_policy",
            boundary_relationship_visible=True,
            deterministic_order=60,
            fail_visible=True,
            missing_metadata_visibility=(
                "runtime execution policy metadata is intentionally absent because execution is prohibited",
            ),
        ),
        OrchestrationTopologyRelationship(
            relationship_id="v4_3_topology_relationship_activation_to_execution",
            relationship_type=TOPOLOGY_RELATIONSHIP_ACTIVATION_TO_EXECUTION,
            relationship_classification="prohibited_relationship",
            relationship_state=TOPOLOGY_STATE_PROHIBITED,
            source_node_id="v4_3_topology_node_operational_activation",
            target_node_id="v4_3_topology_node_runtime_orchestration_execution",
            boundary_relationship_visible=True,
            deterministic_order=70,
            fail_visible=True,
            prohibited_reason_visibility=("runtime orchestration execution relationships are prohibited",),
        ),
    )


def default_orchestration_topology_edges(
    relationships: tuple[OrchestrationTopologyRelationship, ...] | None = None,
) -> tuple[OrchestrationTopologyEdge, ...]:
    relationship_records = relationships or default_orchestration_topology_relationships()
    return tuple(
        OrchestrationTopologyEdge(
            edge_id=f"{relationship.relationship_id}_edge",
            edge_classification=relationship.relationship_classification,
            edge_state=relationship.relationship_state,
            source_node_id=relationship.source_node_id,
            target_node_id=relationship.target_node_id,
            relationship_id=relationship.relationship_id,
            source_node_visible=True,
            target_node_visible=True,
            deterministic_order=relationship.deterministic_order,
            fail_visible=relationship.fail_visible,
        )
        for relationship in relationship_records
    )


def default_orchestration_relationship_visibility(
    relationships: tuple[OrchestrationTopologyRelationship, ...] | None = None,
) -> OrchestrationTopologyRelationshipVisibility:
    relationship_records = relationships or default_orchestration_topology_relationships()
    return OrchestrationTopologyRelationshipVisibility(
        visibility_id="v4_3_orchestration_topology_relationship_visibility_primary",
        boundary_relationship_ids=tuple(
            relationship.relationship_id for relationship in relationship_records if relationship.boundary_relationship_visible
        ),
        unsupported_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_UNSUPPORTED
        ),
        prohibited_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_PROHIBITED
        ),
        blocked_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_BLOCKED
        ),
        stale_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_STALE
        ),
        conflicting_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_CONFLICTING
        ),
        missing_metadata_relationship_ids=tuple(
            relationship.relationship_id
            for relationship in relationship_records
            if relationship.relationship_state == TOPOLOGY_STATE_MISSING_METADATA
        ),
        unknown_relationship_ids=("v4_3_topology_relationship_future_consumer_unknown",),
        prohibited_relationship_types=PROHIBITED_TOPOLOGY_RELATIONSHIP_TYPES,
        unsupported_relationship_types=UNSUPPORTED_TOPOLOGY_RELATIONSHIP_TYPES,
        deterministic_order=10,
    )


def default_orchestration_topology_continuity_metadata(
    identity: OrchestrationTopologyIdentity | None = None,
    nodes: tuple[OrchestrationTopologyNode, ...] | None = None,
    edges: tuple[OrchestrationTopologyEdge, ...] | None = None,
    relationships: tuple[OrchestrationTopologyRelationship, ...] | None = None,
) -> tuple[OrchestrationTopologyContinuityMetadata, ...]:
    source = identity or default_orchestration_topology_identity()
    node_records = nodes or default_orchestration_topology_nodes()
    relationship_records = relationships or default_orchestration_topology_relationships()
    edge_records = edges or default_orchestration_topology_edges(relationship_records)
    node_ids = tuple(node.node_id for node in node_records)
    edge_ids = tuple(edge.edge_id for edge in edge_records)
    relationship_ids = tuple(relationship.relationship_id for relationship in relationship_records)
    return (
        OrchestrationTopologyContinuityMetadata(
            continuity_id="v4_3_orchestration_topology_continuity_identity",
            continuity_type="topology_identity_continuity",
            continuity_state=TOPOLOGY_STATE_SUPPORTED,
            node_references=node_ids,
            edge_references=edge_ids,
            relationship_references=relationship_ids,
            replay_reference="v4_3_orchestration_topology_replay_primary",
            rollback_reference="v4_3_orchestration_topology_rollback_primary",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            deterministic_hash_reference="v4_3_orchestration_topology_identity_continuity_hash",
            deterministic_order=10,
        ),
        OrchestrationTopologyContinuityMetadata(
            continuity_id="v4_3_orchestration_topology_continuity_replay_rollback",
            continuity_type="replay_rollback_safety",
            continuity_state=TOPOLOGY_STATE_SUPPORTED,
            node_references=node_ids,
            edge_references=edge_ids,
            relationship_references=relationship_ids,
            replay_reference="v4_3_orchestration_topology_serialization_snapshot",
            rollback_reference="v4_3_orchestration_topology_hash_snapshot",
            provenance_reference=source.provenance_reference,
            lineage_reference=source.lineage_reference,
            deterministic_hash_reference="v4_3_orchestration_topology_replay_rollback_hash",
            deterministic_order=20,
        ),
    )


def default_orchestration_topology_diagnostics(
    relationships: tuple[OrchestrationTopologyRelationship, ...] | None = None,
) -> tuple[OrchestrationTopologyDiagnostic, ...]:
    relationship_records = relationships or default_orchestration_topology_relationships()
    unsupported_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_UNSUPPORTED
    )
    blocked_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_BLOCKED
    )
    prohibited_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_PROHIBITED
    )
    stale_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_STALE
    )
    conflicting_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_CONFLICTING
    )
    missing_metadata_ids = tuple(
        relationship.relationship_id
        for relationship in relationship_records
        if relationship.relationship_state == TOPOLOGY_STATE_MISSING_METADATA
    )
    return (
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_identity_visible",
            category=TOPOLOGY_DIAGNOSTIC_IDENTITY,
            severity="info",
            finding="Topology identity is deterministic and non-executable.",
            affected_node_ids=(),
            affected_edge_ids=(),
            affected_relationship_ids=(),
            deterministic_order=10,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_unsupported_relationship_visible",
            category=TOPOLOGY_DIAGNOSTIC_UNSUPPORTED_RELATIONSHIP,
            severity="warning",
            finding="Unsupported topology relationships remain visible and unavailable.",
            affected_node_ids=("v4_3_topology_node_future_provider_contract",),
            affected_edge_ids=("v4_3_topology_relationship_governance_to_provider_edge",),
            affected_relationship_ids=unsupported_ids,
            deterministic_order=20,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_blocked_relationship_visible",
            category=TOPOLOGY_DIAGNOSTIC_BLOCKED_RELATIONSHIP,
            severity="blocked",
            finding="Blocked topology relationships remain visible and do not trigger traversal.",
            affected_node_ids=("v4_3_topology_node_operational_activation",),
            affected_edge_ids=("v4_3_topology_relationship_governance_to_activation_edge",),
            affected_relationship_ids=blocked_ids,
            deterministic_order=30,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_prohibited_relationship_visible",
            category=TOPOLOGY_DIAGNOSTIC_PROHIBITED_RELATIONSHIP,
            severity="prohibited",
            finding="Prohibited topology relationships remain fail-visible and inactive.",
            affected_node_ids=("v4_3_topology_node_runtime_orchestration_execution",),
            affected_edge_ids=("v4_3_topology_relationship_activation_to_execution_edge",),
            affected_relationship_ids=prohibited_ids,
            deterministic_order=40,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_stale_relationship_visible",
            category=TOPOLOGY_DIAGNOSTIC_STALE_RELATIONSHIP,
            severity="warning",
            finding="Stale topology ancestry remains read-only evidence.",
            affected_node_ids=("v4_3_topology_node_prior_coordination_snapshot",),
            affected_edge_ids=("v4_3_topology_relationship_manifest_to_prior_coordination_edge",),
            affected_relationship_ids=stale_ids,
            deterministic_order=50,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_conflicting_relationship_visible",
            category=TOPOLOGY_DIAGNOSTIC_CONFLICTING_RELATIONSHIP,
            severity="blocked",
            finding="Conflicting authorization relationships remain blocked and descriptive.",
            affected_node_ids=("v4_3_topology_node_execution_authorization_metadata",),
            affected_edge_ids=("v4_3_topology_relationship_governance_to_authorization_edge",),
            affected_relationship_ids=conflicting_ids,
            deterministic_order=60,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_missing_metadata_visible",
            category=TOPOLOGY_DIAGNOSTIC_MISSING_METADATA,
            severity="warning",
            finding="Missing runtime execution metadata remains visible because execution is prohibited.",
            affected_node_ids=("v4_3_topology_node_runtime_execution_policy",),
            affected_edge_ids=("v4_3_topology_relationship_governance_to_runtime_policy_edge",),
            affected_relationship_ids=missing_metadata_ids,
            deterministic_order=70,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_explainability_visible",
            category=TOPOLOGY_DIAGNOSTIC_EXPLAINABILITY,
            severity="info",
            finding="Topology explainability describes unavailable traversal, routing, dependency resolution, and execution.",
            affected_node_ids=(),
            affected_edge_ids=(),
            affected_relationship_ids=tuple(relationship.relationship_id for relationship in relationship_records),
            deterministic_order=80,
        ),
        OrchestrationTopologyDiagnostic(
            diagnostic_id="v4_3_topology_diagnostic_non_execution_visible",
            category=TOPOLOGY_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Topology infrastructure remains non-executing, non-traversing, non-routing, and non-resolving.",
            affected_node_ids=(),
            affected_edge_ids=(),
            affected_relationship_ids=tuple(relationship.relationship_id for relationship in relationship_records),
            deterministic_order=90,
        ),
    )


def default_orchestration_topology_explainability() -> tuple[OrchestrationTopologyExplainability, ...]:
    return (
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_blocked",
            category="blocked_topology",
            summary="The topology is blocked for operational activation because Phase 2 models structure only.",
            affected_relationship_ids=("v4_3_topology_relationship_governance_to_activation",),
            deterministic_order=10,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_prohibited",
            category="prohibited_relationship",
            summary="Runtime execution relationships are prohibited by non-execution topology governance.",
            affected_relationship_ids=("v4_3_topology_relationship_activation_to_execution",),
            deterministic_order=20,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_unsupported",
            category="unsupported_relationship",
            summary="Future provider relationships are unsupported until a later approved governance phase.",
            affected_relationship_ids=("v4_3_topology_relationship_governance_to_provider",),
            deterministic_order=30,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_stale",
            category="stale_relationship",
            summary="Prior v4.2 coordination topology ancestry is stale read-only evidence, not a live source.",
            affected_relationship_ids=("v4_3_topology_relationship_manifest_to_prior_coordination",),
            deterministic_order=40,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_conflicting",
            category="conflicting_relationship",
            summary="Execution authorization relationships conflict with the explicit non-execution boundary.",
            affected_relationship_ids=("v4_3_topology_relationship_governance_to_authorization",),
            deterministic_order=50,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_traversal_unavailable",
            category="traversal_unavailable",
            summary="Topology traversal is unavailable because the topology is evidence, not an executable graph.",
            affected_relationship_ids=(),
            deterministic_order=60,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_routing_unavailable",
            category="routing_unavailable",
            summary="Routing is unavailable because relationship visibility does not select paths or routes.",
            affected_relationship_ids=(),
            deterministic_order=70,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_dependency_resolution_unavailable",
            category="dependency_resolution_unavailable",
            summary="Dependency resolution is unavailable because relationships are not resolvers.",
            affected_relationship_ids=(),
            deterministic_order=80,
        ),
        OrchestrationTopologyExplainability(
            explanation_id="v4_3_topology_explainability_execution_disabled",
            category="execution_disabled",
            summary="Execution remains disabled across graph, runtime, routing, scheduling, and sequencing surfaces.",
            affected_relationship_ids=(),
            deterministic_order=90,
        ),
    )


def default_orchestration_topology() -> OrchestrationTopology:
    identity = default_orchestration_topology_identity()
    nodes = default_orchestration_topology_nodes()
    relationships = default_orchestration_topology_relationships()
    edges = default_orchestration_topology_edges(relationships)
    return OrchestrationTopology(
        identity=identity,
        metadata=default_orchestration_topology_metadata(identity),
        nodes=nodes,
        edges=edges,
        relationships=relationships,
        relationship_visibility=default_orchestration_relationship_visibility(relationships),
        continuity_metadata=default_orchestration_topology_continuity_metadata(
            identity,
            nodes,
            edges,
            relationships,
        ),
        diagnostics=default_orchestration_topology_diagnostics(relationships),
        explainability_summaries=default_orchestration_topology_explainability(),
    )
