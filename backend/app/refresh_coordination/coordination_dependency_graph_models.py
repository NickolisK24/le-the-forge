"""Deterministic v4.2 coordination dependency graph governance models.

Coordination dependency graphs are descriptive governance evidence only. They
do not execute dependencies, orchestrate refreshes, resolve dependencies,
consume production bundles, integrate with planners, authorize behavior,
remediate blockers, roll back state, correct state, rank choices, score
choices, select options, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest


V4_2_COORDINATION_DEPENDENCY_GRAPH_PHASE_ID = "v4_2_coordination_dependency_graph_governance"
V4_2_COORDINATION_DEPENDENCY_GRAPH_SCHEMA_VERSION = "v4_2.coordination_dependency_graph_governance.1"
V4_2_COORDINATION_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION = (
    "v4_2.coordination_dependency_graph_governance_report.1"
)
V4_2_COORDINATION_DEPENDENCY_GRAPH_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_STABLE = "v4_2_coordination_dependency_graph_stable"
V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_BLOCKED = "v4_2_coordination_dependency_graph_blocked"
V4_2_COORDINATION_DEPENDENCY_GRAPH_PURPOSE = (
    "deterministic_refresh_coordination_dependency_graph_governance_intelligence_only"
)

GRAPH_DEPENDENCY_STATE_SUPPORTED = "supported"
GRAPH_DEPENDENCY_STATE_BLOCKED = "blocked"
GRAPH_DEPENDENCY_STATE_PROHIBITED = "prohibited"
GRAPH_DEPENDENCY_STATE_UNSUPPORTED = "unsupported"
GRAPH_DEPENDENCY_STATE_STALE = "stale"
GRAPH_DEPENDENCY_STATE_LINEAGE_GAP = "lineage_gap"
GRAPH_DEPENDENCY_STATE_CONTINUITY_GAP = "continuity_gap"
GRAPH_DEPENDENCY_STATE_UNKNOWN = "unknown"
GRAPH_DEPENDENCY_STATES: tuple[str, ...] = (
    GRAPH_DEPENDENCY_STATE_SUPPORTED,
    GRAPH_DEPENDENCY_STATE_BLOCKED,
    GRAPH_DEPENDENCY_STATE_PROHIBITED,
    GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
    GRAPH_DEPENDENCY_STATE_STALE,
    GRAPH_DEPENDENCY_STATE_LINEAGE_GAP,
    GRAPH_DEPENDENCY_STATE_CONTINUITY_GAP,
    GRAPH_DEPENDENCY_STATE_UNKNOWN,
)
FAIL_VISIBLE_GRAPH_DEPENDENCY_STATES: tuple[str, ...] = (
    GRAPH_DEPENDENCY_STATE_BLOCKED,
    GRAPH_DEPENDENCY_STATE_PROHIBITED,
    GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
    GRAPH_DEPENDENCY_STATE_STALE,
    GRAPH_DEPENDENCY_STATE_LINEAGE_GAP,
    GRAPH_DEPENDENCY_STATE_CONTINUITY_GAP,
    GRAPH_DEPENDENCY_STATE_UNKNOWN,
)

GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET = "source_to_target"
GRAPH_EDGE_DIRECTION_TARGET_TO_SOURCE = "target_to_source"
GRAPH_EDGE_DIRECTION_EXTERNAL_TO_GRAPH = "external_to_graph"
GRAPH_EDGE_DIRECTIONS: tuple[str, ...] = (
    GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET,
    GRAPH_EDGE_DIRECTION_TARGET_TO_SOURCE,
    GRAPH_EDGE_DIRECTION_EXTERNAL_TO_GRAPH,
)

GRAPH_RELATIONSHIP_MANIFEST_SOURCE = "manifest_source_dependency"
GRAPH_RELATIONSHIP_READINESS = "readiness_dependency"
GRAPH_RELATIONSHIP_PROVIDER_CONTRACT = "provider_contract_dependency"
GRAPH_RELATIONSHIP_RUNTIME_SEQUENCE = "runtime_sequence_dependency"
GRAPH_RELATIONSHIP_PRODUCTION_BUNDLE = "production_bundle_dependency"
GRAPH_RELATIONSHIP_SNAPSHOT = "snapshot_dependency"
GRAPH_RELATIONSHIP_TYPES: tuple[str, ...] = (
    GRAPH_RELATIONSHIP_MANIFEST_SOURCE,
    GRAPH_RELATIONSHIP_READINESS,
    GRAPH_RELATIONSHIP_PROVIDER_CONTRACT,
    GRAPH_RELATIONSHIP_RUNTIME_SEQUENCE,
    GRAPH_RELATIONSHIP_PRODUCTION_BUNDLE,
    GRAPH_RELATIONSHIP_SNAPSHOT,
)

GRAPH_DIAGNOSTIC_DIRECTION = "dependency_direction_visibility"
GRAPH_DIAGNOSTIC_BLOCKED = "blocked_dependency_visibility"
GRAPH_DIAGNOSTIC_PROHIBITED = "prohibited_dependency_visibility"
GRAPH_DIAGNOSTIC_UNSUPPORTED = "unsupported_dependency_visibility"
GRAPH_DIAGNOSTIC_LINEAGE = "lineage_continuity_visibility"
GRAPH_DIAGNOSTIC_CONTINUITY = "continuity_visibility"
GRAPH_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_COORDINATION_DEPENDENCY_GRAPH_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "refresh_execution",
    "dependency_resolution",
    "planner_integration",
    "production_bundle_consumption",
    "runtime_mutation",
    "remediation",
    "automatic_correction",
    "automatic_rollback",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "authorization_systems",
    "approval_systems",
    "operational_execution",
    "hidden_dependency_resolution",
    "implicit_execution_pathways",
)

EXPLICIT_COORDINATION_DEPENDENCY_GRAPH_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 2 creates deterministic refresh coordination dependency graph governance intelligence only.",
    "v4.2 Phase 2 does not enable dependency resolution.",
    "v4.2 Phase 2 does not enable orchestration execution.",
    "v4.2 Phase 2 does not enable refresh execution.",
    "v4.2 Phase 2 does not enable planner integration.",
    "v4.2 Phase 2 does not enable production consumption.",
    "v4.2 Phase 2 does not enable runtime mutation.",
    "v4.2 Phase 2 does not enable remediation.",
    "v4.2 Phase 2 does not enable automatic correction.",
    "v4.2 Phase 2 does not enable automatic rollback.",
    "v4.2 Phase 2 does not enable ranking scoring or selection.",
    "v4.2 Phase 2 does not enable authorization or approval.",
)

EXPLICIT_COORDINATION_DEPENDENCY_GRAPH_PROHIBITIONS: tuple[str, ...] = (
    "No dependency resolution exists.",
    "No orchestration execution exists.",
    "No refresh execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No ranking, scoring, or selection behavior exists.",
    "No authorization or approval behavior exists.",
    "No operational execution exists.",
    "No hidden dependency resolution exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CoordinationDependencyGraphIdentity:
    graph_id: str
    coordination_cycle_id: str
    graph_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    lineage_reference: str
    continuity_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_COORDINATION_DEPENDENCY_GRAPH_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    graph_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class CoordinationGraphNode:
    node_id: str
    node_type: str
    manifest_reference: str
    dependency_domain: str
    lineage_reference: str
    continuity_reference: str
    node_state: str
    reason: str
    deterministic_order: int
    severity: str = "info"
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False


@dataclass(frozen=True)
class CoordinationGraphEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    relationship_type: str
    dependency_state: str
    direction: str
    direction_visibility_reference: str
    lineage_reference: str
    continuity_reference: str
    reason: str
    deterministic_order: int
    severity: str = "info"
    blocked_reason_visibility: tuple[str, ...] = ()
    prohibited_reason_visibility: tuple[str, ...] = ()
    unsupported_reason_visibility: tuple[str, ...] = ()
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("blocked_reason_visibility", "prohibited_reason_visibility", "unsupported_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDependencyDirectionVisibility:
    direction_visibility_id: str
    directional_edge_ids: tuple[str, ...]
    reverse_dependency_visibility: tuple[str, ...]
    ambiguous_direction_visibility: tuple[str, ...]
    circular_direction_visibility: tuple[str, ...]
    deterministic_order: int
    direction_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    automatic_correction_enabled: bool = False
    hidden_direction_inference_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "directional_edge_ids",
            "reverse_dependency_visibility",
            "ambiguous_direction_visibility",
            "circular_direction_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationBlockedDependencyVisibility:
    blocked_visibility_id: str
    blocked_node_ids: tuple[str, ...]
    blocked_edge_ids: tuple[str, ...]
    blocked_reason_visibility: tuple[str, ...]
    deterministic_order: int
    blocked_dependencies_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("blocked_node_ids", "blocked_edge_ids", "blocked_reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationProhibitedDependencyVisibility:
    prohibited_visibility_id: str
    prohibited_node_ids: tuple[str, ...]
    prohibited_edge_ids: tuple[str, ...]
    prohibited_capabilities: tuple[str, ...]
    prohibited_reason_visibility: tuple[str, ...]
    deterministic_order: int
    prohibited_dependencies_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    execution_authorized: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_node_ids",
            "prohibited_edge_ids",
            "prohibited_capabilities",
            "prohibited_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationUnsupportedDependencyVisibility:
    unsupported_visibility_id: str
    unsupported_node_ids: tuple[str, ...]
    unsupported_edge_ids: tuple[str, ...]
    unknown_dependency_visibility: tuple[str, ...]
    stale_dependency_visibility: tuple[str, ...]
    unsupported_reason_visibility: tuple[str, ...]
    deterministic_order: int
    unsupported_dependencies_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden: bool = False
    dependency_resolution_enabled: bool = False
    automatic_recovery_enabled: bool = False
    remediation_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_node_ids",
            "unsupported_edge_ids",
            "unknown_dependency_visibility",
            "stale_dependency_visibility",
            "unsupported_reason_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageAwareDependencyReference:
    lineage_dependency_id: str
    graph_lineage_reference: str
    manifest_lineage_reference: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    predecessor_manifest_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    inferred_lineage_enabled: bool = False
    lineage_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ContinuityAwareDependencyReference:
    continuity_dependency_id: str
    graph_continuity_reference: str
    manifest_continuity_reference: str
    dependency_references: tuple[str, ...]
    replay_reference: str
    rollback_reference: str
    deterministic_hash_reference: str
    deterministic_order: int
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    recovery_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "dependency_references")


@dataclass(frozen=True)
class CoordinationDependencyGraphDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_node_ids: tuple[str, ...]
    affected_edge_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    dependency_resolution_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_node_ids", "affected_edge_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDependencyGraphGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CoordinationDependencyGraph:
    identity: CoordinationDependencyGraphIdentity
    nodes: tuple[CoordinationGraphNode, ...]
    edges: tuple[CoordinationGraphEdge, ...]
    direction_visibility: CoordinationDependencyDirectionVisibility
    blocked_dependency_visibility: CoordinationBlockedDependencyVisibility
    prohibited_dependency_visibility: CoordinationProhibitedDependencyVisibility
    unsupported_dependency_visibility: CoordinationUnsupportedDependencyVisibility
    lineage_references: tuple[LineageAwareDependencyReference, ...]
    continuity_references: tuple[ContinuityAwareDependencyReference, ...]
    diagnostics: tuple[CoordinationDependencyGraphDiagnostic, ...]
    governance_visibility: CoordinationDependencyGraphGovernance
    compatibility_manifest_reference: str
    graph_scope: str = V4_2_COORDINATION_DEPENDENCY_GRAPH_PURPOSE
    deterministic: bool = True
    governance_first: bool = True
    non_executable: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    continuity_certified: bool = True
    integrity_enforced: bool = True
    dependency_resolution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    production_bundle_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    operational_execution_enabled: bool = False
    hidden_dependency_resolution_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("nodes", "edges", "lineage_references", "continuity_references", "diagnostics"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_coordination_dependency_graph_identity(
    manifest: CoordinationManifest | None = None,
) -> CoordinationDependencyGraphIdentity:
    source = manifest or default_coordination_manifest()
    return CoordinationDependencyGraphIdentity(
        graph_id="v4_2_coordination_dependency_graph_primary",
        coordination_cycle_id="v4_2_phase_2_coordination_dependency_graph_governance",
        graph_version="v4.2.0-phase-2",
        source_manifest_reference=source.identity.manifest_id,
        source_manifest_hash_reference=hash_coordination_manifest(source),
        schema_version=V4_2_COORDINATION_DEPENDENCY_GRAPH_SCHEMA_VERSION,
        generated_at=V4_2_COORDINATION_DEPENDENCY_GRAPH_GENERATED_AT,
        provenance_reference="v4_2_coordination_dependency_graph_provenance_primary",
        lineage_reference="v4_2_coordination_dependency_graph_lineage_primary",
        continuity_reference="v4_2_coordination_dependency_graph_continuity_primary",
        diagnostics_reference="v4_2_coordination_dependency_graph_diagnostics_primary",
        governance_reference="v4_2_coordination_dependency_graph_governance_primary",
    )


def default_coordination_graph_nodes(
    identity: CoordinationDependencyGraphIdentity | None = None,
) -> tuple[CoordinationGraphNode, ...]:
    source = identity or default_coordination_dependency_graph_identity()
    return (
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_manifest_foundation",
            node_type="coordination_manifest",
            manifest_reference=source.source_manifest_reference,
            dependency_domain="manifest_foundation",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_SUPPORTED,
            reason="Phase 1 coordination manifest is available as deterministic governance evidence.",
            deterministic_order=10,
        ),
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_v4_1_readiness",
            node_type="readiness_evidence",
            manifest_reference="v4_1_closeout_and_v4_2_readiness_report",
            dependency_domain="readiness_evidence",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_SUPPORTED,
            reason="v4.1 closeout and v4.2 readiness evidence remains read-only input.",
            deterministic_order=20,
        ),
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_future_provider_contract",
            node_type="future_provider_contract",
            manifest_reference="future_refresh_provider_contract",
            dependency_domain="provider_contract",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
            reason="Future provider contracts are not declared in Phase 2.",
            deterministic_order=30,
            severity="warning",
            fail_visible=True,
        ),
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_runtime_sequence",
            node_type="runtime_sequence",
            manifest_reference="future_refresh_sequence",
            dependency_domain="runtime_sequence",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_BLOCKED,
            reason="Runtime sequencing remains blocked because orchestration execution is prohibited.",
            deterministic_order=40,
            severity="blocked",
            fail_visible=True,
        ),
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_production_bundle",
            node_type="production_bundle",
            manifest_reference="production_runtime_bundle",
            dependency_domain="production_consumption",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_PROHIBITED,
            reason="Production bundle consumption is prohibited.",
            deterministic_order=50,
            severity="prohibited",
            fail_visible=True,
        ),
        CoordinationGraphNode(
            node_id="v4_2_coordination_node_v4_1_snapshot",
            node_type="prior_phase_snapshot",
            manifest_reference="v4_1_refresh_governance_snapshot",
            dependency_domain="prior_phase_snapshot",
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            node_state=GRAPH_DEPENDENCY_STATE_STALE,
            reason="Prior v4.1 governance snapshot remains stale read-only evidence.",
            deterministic_order=60,
            severity="warning",
            fail_visible=True,
        ),
    )


def default_coordination_graph_edges(
    identity: CoordinationDependencyGraphIdentity | None = None,
) -> tuple[CoordinationGraphEdge, ...]:
    source = identity or default_coordination_dependency_graph_identity()
    direction = "v4_2_coordination_dependency_graph_direction_visibility_primary"
    return (
        CoordinationGraphEdge(
            edge_id="v4_2_coordination_edge_readiness_to_manifest",
            from_node_id="v4_2_coordination_node_v4_1_readiness",
            to_node_id="v4_2_coordination_node_manifest_foundation",
            relationship_type=GRAPH_RELATIONSHIP_READINESS,
            dependency_state=GRAPH_DEPENDENCY_STATE_SUPPORTED,
            direction=GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET,
            direction_visibility_reference=direction,
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            reason="Readiness evidence feeds the manifest foundation as descriptive input.",
            deterministic_order=10,
        ),
        CoordinationGraphEdge(
            edge_id="v4_2_coordination_edge_manifest_to_future_provider",
            from_node_id="v4_2_coordination_node_manifest_foundation",
            to_node_id="v4_2_coordination_node_future_provider_contract",
            relationship_type=GRAPH_RELATIONSHIP_PROVIDER_CONTRACT,
            dependency_state=GRAPH_DEPENDENCY_STATE_UNSUPPORTED,
            direction=GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET,
            direction_visibility_reference=direction,
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            reason="Future provider contracts remain unsupported and unresolved.",
            deterministic_order=20,
            severity="warning",
            unsupported_reason_visibility=("future provider dependency is not declared",),
            fail_visible=True,
        ),
        CoordinationGraphEdge(
            edge_id="v4_2_coordination_edge_provider_to_runtime_sequence",
            from_node_id="v4_2_coordination_node_future_provider_contract",
            to_node_id="v4_2_coordination_node_runtime_sequence",
            relationship_type=GRAPH_RELATIONSHIP_RUNTIME_SEQUENCE,
            dependency_state=GRAPH_DEPENDENCY_STATE_BLOCKED,
            direction=GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET,
            direction_visibility_reference=direction,
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            reason="Runtime sequencing is blocked and does not execute.",
            deterministic_order=30,
            severity="blocked",
            blocked_reason_visibility=("orchestration execution is prohibited",),
            fail_visible=True,
        ),
        CoordinationGraphEdge(
            edge_id="v4_2_coordination_edge_production_bundle_to_manifest",
            from_node_id="v4_2_coordination_node_production_bundle",
            to_node_id="v4_2_coordination_node_manifest_foundation",
            relationship_type=GRAPH_RELATIONSHIP_PRODUCTION_BUNDLE,
            dependency_state=GRAPH_DEPENDENCY_STATE_PROHIBITED,
            direction=GRAPH_EDGE_DIRECTION_EXTERNAL_TO_GRAPH,
            direction_visibility_reference=direction,
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            reason="Production bundle input is prohibited for coordination governance.",
            deterministic_order=40,
            severity="prohibited",
            prohibited_reason_visibility=("production consumption is prohibited",),
            fail_visible=True,
        ),
        CoordinationGraphEdge(
            edge_id="v4_2_coordination_edge_v4_1_snapshot_to_manifest",
            from_node_id="v4_2_coordination_node_v4_1_snapshot",
            to_node_id="v4_2_coordination_node_manifest_foundation",
            relationship_type=GRAPH_RELATIONSHIP_SNAPSHOT,
            dependency_state=GRAPH_DEPENDENCY_STATE_STALE,
            direction=GRAPH_EDGE_DIRECTION_SOURCE_TO_TARGET,
            direction_visibility_reference=direction,
            lineage_reference=source.lineage_reference,
            continuity_reference=source.continuity_reference,
            reason="Prior governance snapshot remains stale read-only evidence.",
            deterministic_order=50,
            severity="warning",
            fail_visible=True,
        ),
    )


def default_direction_visibility(edges: tuple[CoordinationGraphEdge, ...] | None = None) -> CoordinationDependencyDirectionVisibility:
    graph_edges = edges or default_coordination_graph_edges()
    return CoordinationDependencyDirectionVisibility(
        direction_visibility_id="v4_2_coordination_dependency_graph_direction_visibility_primary",
        directional_edge_ids=tuple(edge.edge_id for edge in graph_edges),
        reverse_dependency_visibility=("v4_2_coordination_edge_production_bundle_to_manifest",),
        ambiguous_direction_visibility=("v4_2_future_provider_contract_direction_not_declared",),
        circular_direction_visibility=(),
        deterministic_order=10,
    )


def default_blocked_dependency_visibility(
    nodes: tuple[CoordinationGraphNode, ...] | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> CoordinationBlockedDependencyVisibility:
    graph_nodes = nodes or default_coordination_graph_nodes()
    graph_edges = edges or default_coordination_graph_edges()
    return CoordinationBlockedDependencyVisibility(
        blocked_visibility_id="v4_2_coordination_dependency_graph_blocked_visibility_primary",
        blocked_node_ids=tuple(node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_BLOCKED),
        blocked_edge_ids=tuple(edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_BLOCKED),
        blocked_reason_visibility=tuple(
            reason for edge in graph_edges for reason in edge.blocked_reason_visibility
        ),
        deterministic_order=20,
    )


def default_prohibited_dependency_visibility(
    nodes: tuple[CoordinationGraphNode, ...] | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> CoordinationProhibitedDependencyVisibility:
    graph_nodes = nodes or default_coordination_graph_nodes()
    graph_edges = edges or default_coordination_graph_edges()
    return CoordinationProhibitedDependencyVisibility(
        prohibited_visibility_id="v4_2_coordination_dependency_graph_prohibited_visibility_primary",
        prohibited_node_ids=tuple(
            node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_PROHIBITED
        ),
        prohibited_edge_ids=tuple(
            edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_PROHIBITED
        ),
        prohibited_capabilities=PROHIBITED_COORDINATION_DEPENDENCY_GRAPH_CAPABILITIES,
        prohibited_reason_visibility=tuple(
            f"v4_2_prohibited_dependency_graph_capability_{capability}"
            for capability in PROHIBITED_COORDINATION_DEPENDENCY_GRAPH_CAPABILITIES
        ),
        deterministic_order=30,
    )


def default_unsupported_dependency_visibility(
    nodes: tuple[CoordinationGraphNode, ...] | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> CoordinationUnsupportedDependencyVisibility:
    graph_nodes = nodes or default_coordination_graph_nodes()
    graph_edges = edges or default_coordination_graph_edges()
    stale_node_ids = tuple(node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_STALE)
    stale_edge_ids = tuple(edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_STALE)
    return CoordinationUnsupportedDependencyVisibility(
        unsupported_visibility_id="v4_2_coordination_dependency_graph_unsupported_visibility_primary",
        unsupported_node_ids=tuple(
            node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED
        ),
        unsupported_edge_ids=tuple(
            edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED
        ),
        unknown_dependency_visibility=("v4_2_future_coordination_graph_consumer_unknown",),
        stale_dependency_visibility=stale_node_ids + stale_edge_ids,
        unsupported_reason_visibility=tuple(
            reason for edge in graph_edges for reason in edge.unsupported_reason_visibility
        ),
        deterministic_order=40,
    )


def default_lineage_aware_dependency_references(
    identity: CoordinationDependencyGraphIdentity | None = None,
    nodes: tuple[CoordinationGraphNode, ...] | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> tuple[LineageAwareDependencyReference, ...]:
    source = identity or default_coordination_dependency_graph_identity()
    graph_nodes = nodes or default_coordination_graph_nodes(source)
    graph_edges = edges or default_coordination_graph_edges(source)
    return (
        LineageAwareDependencyReference(
            lineage_dependency_id="v4_2_coordination_dependency_graph_lineage_primary",
            graph_lineage_reference=source.lineage_reference,
            manifest_lineage_reference="v4_2_coordination_manifest_lineage_primary",
            node_references=tuple(node.node_id for node in graph_nodes),
            edge_references=tuple(edge.edge_id for edge in graph_edges),
            predecessor_manifest_reference=source.source_manifest_reference,
            deterministic_hash_reference="v4_2_coordination_dependency_graph_lineage_hash",
            deterministic_order=10,
        ),
    )


def default_continuity_aware_dependency_references(
    identity: CoordinationDependencyGraphIdentity | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> tuple[ContinuityAwareDependencyReference, ...]:
    source = identity or default_coordination_dependency_graph_identity()
    graph_edges = edges or default_coordination_graph_edges(source)
    return (
        ContinuityAwareDependencyReference(
            continuity_dependency_id="v4_2_coordination_dependency_graph_continuity_primary",
            graph_continuity_reference=source.continuity_reference,
            manifest_continuity_reference="v4_2_coordination_manifest_continuity_primary",
            dependency_references=tuple(edge.edge_id for edge in graph_edges),
            replay_reference="v4_2_coordination_dependency_graph_replay_primary",
            rollback_reference="v4_2_coordination_dependency_graph_rollback_primary",
            deterministic_hash_reference="v4_2_coordination_dependency_graph_continuity_hash",
            deterministic_order=10,
        ),
    )


def default_coordination_dependency_graph_diagnostics(
    nodes: tuple[CoordinationGraphNode, ...] | None = None,
    edges: tuple[CoordinationGraphEdge, ...] | None = None,
) -> tuple[CoordinationDependencyGraphDiagnostic, ...]:
    graph_nodes = nodes or default_coordination_graph_nodes()
    graph_edges = edges or default_coordination_graph_edges()
    blocked_nodes = tuple(node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_BLOCKED)
    blocked_edges = tuple(edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_BLOCKED)
    prohibited_nodes = tuple(node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_PROHIBITED)
    prohibited_edges = tuple(edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_PROHIBITED)
    unsupported_nodes = tuple(node.node_id for node in graph_nodes if node.node_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED)
    unsupported_edges = tuple(edge.edge_id for edge in graph_edges if edge.dependency_state == GRAPH_DEPENDENCY_STATE_UNSUPPORTED)
    return (
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_direction_diagnostic",
            category=GRAPH_DIAGNOSTIC_DIRECTION,
            severity="info",
            finding="Dependency direction is visible as graph evidence and does not trigger sequencing.",
            affected_node_ids=tuple(node.node_id for node in graph_nodes),
            affected_edge_ids=tuple(edge.edge_id for edge in graph_edges),
            deterministic_order=10,
        ),
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_blocked_diagnostic",
            category=GRAPH_DIAGNOSTIC_BLOCKED,
            severity="blocked",
            finding="Blocked dependencies remain fail-visible and unresolved.",
            affected_node_ids=blocked_nodes,
            affected_edge_ids=blocked_edges,
            deterministic_order=20,
        ),
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_prohibited_diagnostic",
            category=GRAPH_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            finding="Prohibited dependencies remain fail-visible and inactive.",
            affected_node_ids=prohibited_nodes,
            affected_edge_ids=prohibited_edges,
            deterministic_order=30,
        ),
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_unsupported_diagnostic",
            category=GRAPH_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            finding="Unsupported dependencies remain fail-visible and unresolved.",
            affected_node_ids=unsupported_nodes,
            affected_edge_ids=unsupported_edges,
            deterministic_order=40,
        ),
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_lineage_diagnostic",
            category=GRAPH_DIAGNOSTIC_LINEAGE,
            severity="info",
            finding="Lineage-aware dependency references preserve manifest ancestry without inference or repair.",
            affected_node_ids=tuple(node.node_id for node in graph_nodes),
            affected_edge_ids=tuple(edge.edge_id for edge in graph_edges),
            deterministic_order=50,
        ),
        CoordinationDependencyGraphDiagnostic(
            diagnostic_id="v4_2_coordination_dependency_graph_non_execution_diagnostic",
            category=GRAPH_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Dependency graph governance remains non-executing and non-authorizing.",
            affected_node_ids=(),
            affected_edge_ids=tuple(edge.edge_id for edge in graph_edges),
            deterministic_order=60,
        ),
    )


def default_coordination_dependency_graph_governance(
    identity: CoordinationDependencyGraphIdentity | None = None,
) -> CoordinationDependencyGraphGovernance:
    source = identity or default_coordination_dependency_graph_identity()
    return CoordinationDependencyGraphGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_COORDINATION_DEPENDENCY_GRAPH_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_COORDINATION_DEPENDENCY_GRAPH_PROHIBITIONS,
        deterministic_order=10,
    )


def default_coordination_dependency_graph(
    manifest: CoordinationManifest | None = None,
) -> CoordinationDependencyGraph:
    source_manifest = manifest or default_coordination_manifest()
    identity = default_coordination_dependency_graph_identity(source_manifest)
    nodes = default_coordination_graph_nodes(identity)
    edges = default_coordination_graph_edges(identity)
    return CoordinationDependencyGraph(
        identity=identity,
        nodes=nodes,
        edges=edges,
        direction_visibility=default_direction_visibility(edges),
        blocked_dependency_visibility=default_blocked_dependency_visibility(nodes, edges),
        prohibited_dependency_visibility=default_prohibited_dependency_visibility(nodes, edges),
        unsupported_dependency_visibility=default_unsupported_dependency_visibility(nodes, edges),
        lineage_references=default_lineage_aware_dependency_references(identity, nodes, edges),
        continuity_references=default_continuity_aware_dependency_references(identity, edges),
        diagnostics=default_coordination_dependency_graph_diagnostics(nodes, edges),
        governance_visibility=default_coordination_dependency_graph_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
    )
