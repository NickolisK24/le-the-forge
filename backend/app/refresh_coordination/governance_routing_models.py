"""Deterministic v4.2 governance routing visibility models.

Governance routing visibility is descriptive evidence only. It does not route
requests, execute orchestration, execute refreshes, execute sequences, schedule
work, resolve dependencies, repair lineage, infer lineage, consume production
bundles, integrate with planners, authorize behavior, remediate blockers, roll
back state, correct state, rank choices, score choices, select options, or
mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)


V4_2_GOVERNANCE_ROUTING_PHASE_ID = "v4_2_governance_routing_visibility"
V4_2_GOVERNANCE_ROUTING_SCHEMA_VERSION = "v4_2.governance_routing_visibility.1"
V4_2_GOVERNANCE_ROUTING_REPORT_SCHEMA_VERSION = "v4_2.governance_routing_visibility_report.1"
V4_2_GOVERNANCE_ROUTING_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_2_GOVERNANCE_ROUTING_STATUS_STABLE = "v4_2_governance_routing_stable"
V4_2_GOVERNANCE_ROUTING_STATUS_BLOCKED = "v4_2_governance_routing_blocked"
V4_2_GOVERNANCE_ROUTING_PURPOSE = "deterministic_refresh_coordination_governance_routing_visibility_only"

ROUTE_STATE_STABLE = "stable"
ROUTE_STATE_BLOCKED = "blocked"
ROUTE_STATE_PROHIBITED = "prohibited"
ROUTE_STATE_UNSUPPORTED = "unsupported"
ROUTE_STATE_STALE = "stale"
ROUTE_STATE_MISSING = "missing"
ROUTE_STATE_CONFLICTING = "conflicting"
ROUTE_STATE_UNKNOWN = "unknown"
ROUTE_STATES: tuple[str, ...] = (
    ROUTE_STATE_STABLE,
    ROUTE_STATE_BLOCKED,
    ROUTE_STATE_PROHIBITED,
    ROUTE_STATE_UNSUPPORTED,
    ROUTE_STATE_STALE,
    ROUTE_STATE_MISSING,
    ROUTE_STATE_CONFLICTING,
    ROUTE_STATE_UNKNOWN,
)
FAIL_VISIBLE_ROUTE_STATES: tuple[str, ...] = (
    ROUTE_STATE_BLOCKED,
    ROUTE_STATE_PROHIBITED,
    ROUTE_STATE_UNSUPPORTED,
    ROUTE_STATE_STALE,
    ROUTE_STATE_MISSING,
    ROUTE_STATE_CONFLICTING,
    ROUTE_STATE_UNKNOWN,
)

ROUTE_RELATIONSHIP_MANIFEST = "manifest_routing_reference"
ROUTE_RELATIONSHIP_DEPENDENCY_GRAPH = "dependency_graph_routing_reference"
ROUTE_RELATIONSHIP_LINEAGE_CHAIN = "lineage_chain_routing_reference"
ROUTE_RELATIONSHIP_SEQUENCING = "sequencing_routing_reference"
ROUTE_RELATIONSHIP_RUNTIME_ROUTE = "runtime_route_visibility"
ROUTE_RELATIONSHIP_PRODUCTION_BUNDLE = "production_bundle_route_visibility"
ROUTE_RELATIONSHIP_FUTURE_PROVIDER = "future_provider_route_visibility"
ROUTE_RELATIONSHIP_PRIOR_SNAPSHOT = "prior_snapshot_route_visibility"
ROUTE_RELATIONSHIP_TYPES: tuple[str, ...] = (
    ROUTE_RELATIONSHIP_MANIFEST,
    ROUTE_RELATIONSHIP_DEPENDENCY_GRAPH,
    ROUTE_RELATIONSHIP_LINEAGE_CHAIN,
    ROUTE_RELATIONSHIP_SEQUENCING,
    ROUTE_RELATIONSHIP_RUNTIME_ROUTE,
    ROUTE_RELATIONSHIP_PRODUCTION_BUNDLE,
    ROUTE_RELATIONSHIP_FUTURE_PROVIDER,
    ROUTE_RELATIONSHIP_PRIOR_SNAPSHOT,
)

ROUTE_DIAGNOSTIC_ORDERING = "non_executable_route_ordering_visibility"
ROUTE_DIAGNOSTIC_BLOCKED = "blocked_route_visibility"
ROUTE_DIAGNOSTIC_PROHIBITED = "prohibited_route_visibility"
ROUTE_DIAGNOSTIC_UNSUPPORTED = "unsupported_route_visibility"
ROUTE_DIAGNOSTIC_STALE = "stale_route_visibility"
ROUTE_DIAGNOSTIC_MISSING = "missing_route_visibility"
ROUTE_DIAGNOSTIC_CONFLICTING = "conflicting_route_visibility"
ROUTE_DIAGNOSTIC_COMPATIBILITY = "coordination_source_compatibility"
ROUTE_DIAGNOSTIC_NON_EXECUTION = "non_execution_boundary_visibility"

PROHIBITED_GOVERNANCE_ROUTING_CAPABILITIES: tuple[str, ...] = (
    "routing_execution",
    "orchestration_execution",
    "refresh_execution",
    "sequencing_execution",
    "scheduling_execution",
    "dependency_resolution",
    "lineage_repair",
    "lineage_inference",
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
    "hidden_route_execution",
    "implicit_execution_pathways",
)

EXPLICIT_GOVERNANCE_ROUTING_LIMITATIONS: tuple[str, ...] = (
    "v4.2 Phase 5 creates deterministic refresh coordination governance routing visibility only.",
    "v4.2 Phase 5 does not enable routing execution.",
    "v4.2 Phase 5 does not enable orchestration execution.",
    "v4.2 Phase 5 does not enable refresh execution.",
    "v4.2 Phase 5 does not enable sequencing execution.",
    "v4.2 Phase 5 does not enable scheduling execution.",
    "v4.2 Phase 5 does not enable dependency resolution.",
    "v4.2 Phase 5 does not enable lineage repair.",
    "v4.2 Phase 5 does not enable lineage inference.",
    "v4.2 Phase 5 does not enable planner integration.",
    "v4.2 Phase 5 does not enable production consumption.",
    "v4.2 Phase 5 does not enable runtime mutation.",
    "v4.2 Phase 5 does not enable remediation.",
    "v4.2 Phase 5 does not enable automatic correction.",
    "v4.2 Phase 5 does not enable automatic rollback.",
    "v4.2 Phase 5 does not enable ranking scoring or selection.",
    "v4.2 Phase 5 does not enable authorization or approval.",
)

EXPLICIT_GOVERNANCE_ROUTING_PROHIBITIONS: tuple[str, ...] = (
    "No routing execution exists.",
    "No orchestration execution exists.",
    "No refresh execution exists.",
    "No sequencing execution exists.",
    "No scheduling execution exists.",
    "No dependency resolution exists.",
    "No lineage repair exists.",
    "No lineage inference exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No runtime mutation exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No automatic rollback exists.",
    "No ranking, scoring, or selection behavior exists.",
    "No authorization or approval behavior exists.",
    "No operational execution exists.",
    "No hidden route execution exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class GovernanceRoutingIdentity:
    routing_id: str
    coordination_cycle_id: str
    routing_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    source_dependency_graph_reference: str
    source_dependency_graph_hash_reference: str
    source_lineage_chain_reference: str
    source_lineage_chain_hash_reference: str
    source_sequencing_reference: str
    source_sequencing_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    route_reference: str
    continuity_reference: str
    diagnostics_reference: str
    governance_reference: str
    governance_purpose: str = V4_2_GOVERNANCE_ROUTING_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_route_execution_enabled: bool = False


@dataclass(frozen=True)
class RoutingSourceReference:
    source_reference_id: str
    source_type: str
    source_id: str
    source_hash_reference: str
    route_state: str
    deterministic_order: int
    reason: str
    descriptive_only: bool = True
    fail_visible: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class RoutingTargetReference:
    target_reference_id: str
    target_type: str
    target_id: str
    target_hash_reference: str
    route_state: str
    deterministic_order: int
    reason: str
    descriptive_only: bool = True
    fail_visible: bool = False
    routing_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class ManifestRoutingReference:
    manifest_routing_reference_id: str
    manifest_reference: str
    manifest_hash_reference: str
    route_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "route_record_ids")


@dataclass(frozen=True)
class DependencyGraphRoutingReference:
    dependency_graph_routing_reference_id: str
    dependency_graph_reference: str
    dependency_graph_hash_reference: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    route_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("node_references", "edge_references", "route_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageRoutingReference:
    lineage_routing_reference_id: str
    lineage_chain_reference: str
    lineage_chain_hash_reference: str
    lineage_record_references: tuple[str, ...]
    route_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    routing_execution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_record_references", "route_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SequencingRoutingReference:
    sequencing_routing_reference_id: str
    sequencing_reference: str
    sequencing_hash_reference: str
    sequence_record_references: tuple[str, ...]
    route_record_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    routing_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("sequence_record_references", "route_record_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class GovernanceRouteRecord:
    route_record_id: str
    source_reference_id: str
    target_reference_id: str
    manifest_routing_reference_id: str
    dependency_graph_routing_reference_id: str
    lineage_routing_reference_id: str
    sequencing_routing_reference_id: str
    relationship_type: str
    route_state: str
    ordering_position: int
    non_executable_order_reference: str
    reason: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    severity: str = "info"
    fail_visible: bool = False
    blocked_visible: bool = False
    prohibited_visible: bool = False
    unsupported_visible: bool = False
    stale_visible: bool = False
    missing_visible: bool = False
    conflicting_visible: bool = False
    descriptive_only: bool = True
    non_authorizing: bool = True
    hidden: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_references")


@dataclass(frozen=True)
class RouteStateVisibility:
    visibility_id: str
    route_state: str
    route_record_ids: tuple[str, ...]
    source_reference_ids: tuple[str, ...]
    target_reference_ids: tuple[str, ...]
    reason_visibility: tuple[str, ...]
    deterministic_order: int
    state_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    routing_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("route_record_ids", "source_reference_ids", "target_reference_ids", "reason_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class NonExecutableRouteOrderingVisibility:
    ordering_visibility_id: str
    ordered_route_record_ids: tuple[str, ...]
    ordered_source_reference_ids: tuple[str, ...]
    ordered_target_reference_ids: tuple[str, ...]
    blocked_ordering_ids: tuple[str, ...]
    prohibited_ordering_ids: tuple[str, ...]
    unsupported_ordering_ids: tuple[str, ...]
    stale_ordering_ids: tuple[str, ...]
    missing_ordering_ids: tuple[str, ...]
    conflicting_ordering_ids: tuple[str, ...]
    deterministic_order: int
    ordering_visible: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_executable_ordering_only: bool = True
    routing_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    hidden_route_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "ordered_route_record_ids",
            "ordered_source_reference_ids",
            "ordered_target_reference_ids",
            "blocked_ordering_ids",
            "prohibited_ordering_ids",
            "unsupported_ordering_ids",
            "stale_ordering_ids",
            "missing_ordering_ids",
            "conflicting_ordering_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class GovernanceRoutingDiagnostic:
    diagnostic_id: str
    category: str
    severity: str
    finding: str
    affected_route_record_ids: tuple[str, ...]
    affected_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_rollback_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in ("affected_route_record_ids", "affected_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class GovernanceRoutingGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    non_authorizing: bool = True
    execution_authorized: bool = False
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
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
class GovernanceRoutingVisibility:
    identity: GovernanceRoutingIdentity
    source_references: tuple[RoutingSourceReference, ...]
    target_references: tuple[RoutingTargetReference, ...]
    manifest_routing_references: tuple[ManifestRoutingReference, ...]
    dependency_graph_routing_references: tuple[DependencyGraphRoutingReference, ...]
    lineage_routing_references: tuple[LineageRoutingReference, ...]
    sequencing_routing_references: tuple[SequencingRoutingReference, ...]
    route_records: tuple[GovernanceRouteRecord, ...]
    ordering_visibility: NonExecutableRouteOrderingVisibility
    blocked_route_visibility: RouteStateVisibility
    prohibited_route_visibility: RouteStateVisibility
    unsupported_route_visibility: RouteStateVisibility
    stale_route_visibility: RouteStateVisibility
    missing_route_visibility: RouteStateVisibility
    conflicting_route_visibility: RouteStateVisibility
    diagnostics: tuple[GovernanceRoutingDiagnostic, ...]
    governance_visibility: GovernanceRoutingGovernance
    compatibility_manifest_reference: str
    compatibility_dependency_graph_reference: str
    compatibility_lineage_chain_reference: str
    compatibility_sequencing_reference: str
    routing_scope: str = V4_2_GOVERNANCE_ROUTING_PURPOSE
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
    routing_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    dependency_resolution_enabled: bool = False
    lineage_repair_enabled: bool = False
    lineage_inference_enabled: bool = False
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
    hidden_route_execution_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_references",
            "target_references",
            "manifest_routing_references",
            "dependency_graph_routing_references",
            "lineage_routing_references",
            "sequencing_routing_references",
            "route_records",
            "diagnostics",
        ):
            _set_tuple_field(self, field_name)


def default_governance_routing_identity(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
) -> GovernanceRoutingIdentity:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    return GovernanceRoutingIdentity(
        routing_id="v4_2_governance_routing_primary",
        coordination_cycle_id="v4_2_refresh_coordination_governance_cycle",
        routing_version="v4.2.5",
        source_manifest_reference=source_manifest.identity.manifest_id,
        source_manifest_hash_reference=hash_coordination_manifest(source_manifest),
        source_dependency_graph_reference=source_graph.identity.graph_id,
        source_dependency_graph_hash_reference=hash_coordination_dependency_graph(source_graph),
        source_lineage_chain_reference=source_lineage.identity.chain_id,
        source_lineage_chain_hash_reference=hash_coordination_lineage_chain(source_lineage),
        source_sequencing_reference=source_sequencing.identity.sequencing_id,
        source_sequencing_hash_reference=hash_coordination_sequencing_intelligence(source_sequencing),
        schema_version=V4_2_GOVERNANCE_ROUTING_SCHEMA_VERSION,
        generated_at=V4_2_GOVERNANCE_ROUTING_GENERATED_AT,
        provenance_reference="v4_2_governance_routing_provenance_primary",
        route_reference="v4_2_governance_routing_route_primary",
        continuity_reference="v4_2_governance_routing_continuity_primary",
        diagnostics_reference="v4_2_governance_routing_diagnostics_primary",
        governance_reference="v4_2_governance_routing_governance_primary",
    )


def default_routing_source_references(identity: GovernanceRoutingIdentity | None = None) -> tuple[RoutingSourceReference, ...]:
    source = identity or default_governance_routing_identity()
    return (
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_manifest",
            source_type="coordination_manifest",
            source_id=source.source_manifest_reference,
            source_hash_reference=source.source_manifest_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=10,
            reason="Manifest governance is visible as route source evidence.",
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_dependency_graph",
            source_type="coordination_dependency_graph",
            source_id=source.source_dependency_graph_reference,
            source_hash_reference=source.source_dependency_graph_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=20,
            reason="Dependency graph governance is visible as route source evidence.",
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_lineage_chain",
            source_type="coordination_lineage_chain",
            source_id=source.source_lineage_chain_reference,
            source_hash_reference=source.source_lineage_chain_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=30,
            reason="Lineage chain governance is visible as route source evidence.",
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_sequencing",
            source_type="coordination_sequencing",
            source_id=source.source_sequencing_reference,
            source_hash_reference=source.source_sequencing_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=40,
            reason="Sequencing intelligence is visible as route source evidence.",
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_runtime_route",
            source_type="runtime_route_request",
            source_id="future_runtime_route_request",
            source_hash_reference="runtime_route_hash_not_applicable",
            route_state=ROUTE_STATE_BLOCKED,
            deterministic_order=50,
            reason="Runtime route requests remain blocked because routing execution is prohibited.",
            fail_visible=True,
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_production_bundle",
            source_type="production_bundle",
            source_id="production_runtime_bundle",
            source_hash_reference="production_bundle_hash_not_consumed",
            route_state=ROUTE_STATE_PROHIBITED,
            deterministic_order=60,
            reason="Production bundle routing remains prohibited.",
            fail_visible=True,
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_future_provider",
            source_type="future_provider_contract",
            source_id="future_refresh_provider_contract",
            source_hash_reference="future_provider_hash_not_declared",
            route_state=ROUTE_STATE_UNSUPPORTED,
            deterministic_order=70,
            reason="Future provider routing remains unsupported.",
            fail_visible=True,
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_v4_1_snapshot",
            source_type="prior_phase_snapshot",
            source_id="v4_1_refresh_governance_snapshot",
            source_hash_reference="v4_1_snapshot_hash_read_only",
            route_state=ROUTE_STATE_STALE,
            deterministic_order=80,
            reason="Prior v4.1 routing evidence remains stale read-only visibility.",
            fail_visible=True,
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_missing_target",
            source_type="future_route_target",
            source_id="future_route_target_missing",
            source_hash_reference="future_route_target_hash_missing",
            route_state=ROUTE_STATE_MISSING,
            deterministic_order=90,
            reason="Future route target remains missing.",
            fail_visible=True,
        ),
        RoutingSourceReference(
            source_reference_id="v4_2_route_source_conflicting_request",
            source_type="runtime_route_conflict",
            source_id="runtime_route_conflict_request",
            source_hash_reference="runtime_route_conflict_hash_not_applicable",
            route_state=ROUTE_STATE_CONFLICTING,
            deterministic_order=100,
            reason="Runtime route request conflicts with the non-routing boundary.",
            fail_visible=True,
        ),
    )


def default_routing_target_references(identity: GovernanceRoutingIdentity | None = None) -> tuple[RoutingTargetReference, ...]:
    source = identity or default_governance_routing_identity()
    return (
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_manifest",
            target_type="coordination_manifest",
            target_id=source.source_manifest_reference,
            target_hash_reference=source.source_manifest_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=10,
            reason="Manifest remains a descriptive route target.",
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_dependency_graph",
            target_type="coordination_dependency_graph",
            target_id=source.source_dependency_graph_reference,
            target_hash_reference=source.source_dependency_graph_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=20,
            reason="Dependency graph remains a descriptive route target.",
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_lineage_chain",
            target_type="coordination_lineage_chain",
            target_id=source.source_lineage_chain_reference,
            target_hash_reference=source.source_lineage_chain_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=30,
            reason="Lineage chain remains a descriptive route target.",
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_sequencing",
            target_type="coordination_sequencing",
            target_id=source.source_sequencing_reference,
            target_hash_reference=source.source_sequencing_hash_reference,
            route_state=ROUTE_STATE_STABLE,
            deterministic_order=40,
            reason="Sequencing remains a descriptive route target.",
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_runtime_route",
            target_type="runtime_route",
            target_id="future_runtime_route_target",
            target_hash_reference="runtime_route_hash_not_applicable",
            route_state=ROUTE_STATE_BLOCKED,
            deterministic_order=50,
            reason="Runtime route target remains blocked and inactive.",
            fail_visible=True,
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_production_bundle",
            target_type="production_bundle",
            target_id="production_runtime_bundle",
            target_hash_reference="production_bundle_hash_not_consumed",
            route_state=ROUTE_STATE_PROHIBITED,
            deterministic_order=60,
            reason="Production bundle route target remains prohibited.",
            fail_visible=True,
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_future_provider",
            target_type="future_provider_contract",
            target_id="future_refresh_provider_contract",
            target_hash_reference="future_provider_hash_not_declared",
            route_state=ROUTE_STATE_UNSUPPORTED,
            deterministic_order=70,
            reason="Future provider route target remains unsupported.",
            fail_visible=True,
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_v4_1_snapshot",
            target_type="prior_phase_snapshot",
            target_id="v4_1_refresh_governance_snapshot",
            target_hash_reference="v4_1_snapshot_hash_read_only",
            route_state=ROUTE_STATE_STALE,
            deterministic_order=80,
            reason="Prior v4.1 route target remains stale evidence.",
            fail_visible=True,
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_missing",
            target_type="future_route_target",
            target_id="future_route_target_missing",
            target_hash_reference="future_route_target_hash_missing",
            route_state=ROUTE_STATE_MISSING,
            deterministic_order=90,
            reason="Future route target remains missing.",
            fail_visible=True,
        ),
        RoutingTargetReference(
            target_reference_id="v4_2_route_target_conflicting",
            target_type="runtime_route_conflict",
            target_id="runtime_route_conflict_target",
            target_hash_reference="runtime_route_conflict_hash_not_applicable",
            route_state=ROUTE_STATE_CONFLICTING,
            deterministic_order=100,
            reason="Runtime route target conflicts with the non-routing boundary.",
            fail_visible=True,
        ),
    )


def default_governance_route_records() -> tuple[GovernanceRouteRecord, ...]:
    route_specs = (
        (
            "v4_2_route_record_manifest",
            "v4_2_route_source_manifest",
            "v4_2_route_target_manifest",
            ROUTE_RELATIONSHIP_MANIFEST,
            ROUTE_STATE_STABLE,
            10,
            "Manifest governance route visibility remains descriptive.",
            ("v4_2_coordination_manifest_primary",),
            "info",
        ),
        (
            "v4_2_route_record_dependency_graph",
            "v4_2_route_source_dependency_graph",
            "v4_2_route_target_dependency_graph",
            ROUTE_RELATIONSHIP_DEPENDENCY_GRAPH,
            ROUTE_STATE_STABLE,
            20,
            "Dependency graph route visibility remains descriptive.",
            ("v4_2_coordination_dependency_graph_primary",),
            "info",
        ),
        (
            "v4_2_route_record_lineage_chain",
            "v4_2_route_source_lineage_chain",
            "v4_2_route_target_lineage_chain",
            ROUTE_RELATIONSHIP_LINEAGE_CHAIN,
            ROUTE_STATE_STABLE,
            30,
            "Lineage chain route visibility remains descriptive.",
            ("v4_2_coordination_lineage_chain_primary",),
            "info",
        ),
        (
            "v4_2_route_record_sequencing",
            "v4_2_route_source_sequencing",
            "v4_2_route_target_sequencing",
            ROUTE_RELATIONSHIP_SEQUENCING,
            ROUTE_STATE_STABLE,
            40,
            "Sequencing route visibility remains descriptive and non-scheduling.",
            ("v4_2_coordination_sequencing_primary",),
            "info",
        ),
        (
            "v4_2_route_record_runtime_route_blocked",
            "v4_2_route_source_runtime_route",
            "v4_2_route_target_runtime_route",
            ROUTE_RELATIONSHIP_RUNTIME_ROUTE,
            ROUTE_STATE_BLOCKED,
            50,
            "Runtime routing remains blocked because routing execution is prohibited.",
            ("future_runtime_route_request", "routing_execution_prohibited"),
            "blocked",
        ),
        (
            "v4_2_route_record_production_bundle_prohibited",
            "v4_2_route_source_production_bundle",
            "v4_2_route_target_production_bundle",
            ROUTE_RELATIONSHIP_PRODUCTION_BUNDLE,
            ROUTE_STATE_PROHIBITED,
            60,
            "Production routing remains prohibited.",
            ("production_runtime_bundle", "production_consumption_prohibited"),
            "prohibited",
        ),
        (
            "v4_2_route_record_future_provider_unsupported",
            "v4_2_route_source_future_provider",
            "v4_2_route_target_future_provider",
            ROUTE_RELATIONSHIP_FUTURE_PROVIDER,
            ROUTE_STATE_UNSUPPORTED,
            70,
            "Future provider routing remains unsupported.",
            ("future_refresh_provider_contract",),
            "warning",
        ),
        (
            "v4_2_route_record_v4_1_snapshot_stale",
            "v4_2_route_source_v4_1_snapshot",
            "v4_2_route_target_v4_1_snapshot",
            ROUTE_RELATIONSHIP_PRIOR_SNAPSHOT,
            ROUTE_STATE_STALE,
            80,
            "Prior v4.1 routing evidence remains stale read-only visibility.",
            ("v4_1_refresh_governance_snapshot",),
            "warning",
        ),
        (
            "v4_2_route_record_missing_target",
            "v4_2_route_source_missing_target",
            "v4_2_route_target_missing",
            ROUTE_RELATIONSHIP_FUTURE_PROVIDER,
            ROUTE_STATE_MISSING,
            90,
            "Future route target remains missing.",
            ("future_route_target_missing",),
            "warning",
        ),
        (
            "v4_2_route_record_conflicting_runtime_route",
            "v4_2_route_source_conflicting_request",
            "v4_2_route_target_conflicting",
            ROUTE_RELATIONSHIP_RUNTIME_ROUTE,
            ROUTE_STATE_CONFLICTING,
            100,
            "Runtime route request conflicts with the non-routing boundary.",
            ("runtime_route_conflict_request", "orchestration_execution_prohibited"),
            "blocked",
        ),
    )
    return tuple(
        GovernanceRouteRecord(
            route_record_id=record_id,
            source_reference_id=source_id,
            target_reference_id=target_id,
            manifest_routing_reference_id="v4_2_manifest_routing_reference_primary",
            dependency_graph_routing_reference_id="v4_2_dependency_graph_routing_reference_primary",
            lineage_routing_reference_id="v4_2_lineage_routing_reference_primary",
            sequencing_routing_reference_id="v4_2_sequencing_routing_reference_primary",
            relationship_type=relationship_type,
            route_state=state,
            ordering_position=order,
            non_executable_order_reference="v4_2_non_executable_route_ordering_primary",
            reason=reason,
            evidence_references=evidence,
            deterministic_order=order,
            severity=severity,
            fail_visible=state in FAIL_VISIBLE_ROUTE_STATES,
            blocked_visible=state == ROUTE_STATE_BLOCKED,
            prohibited_visible=state == ROUTE_STATE_PROHIBITED,
            unsupported_visible=state == ROUTE_STATE_UNSUPPORTED,
            stale_visible=state == ROUTE_STATE_STALE,
            missing_visible=state == ROUTE_STATE_MISSING,
            conflicting_visible=state == ROUTE_STATE_CONFLICTING,
        )
        for record_id, source_id, target_id, relationship_type, state, order, reason, evidence, severity in route_specs
    )


def default_manifest_routing_references(
    identity: GovernanceRoutingIdentity | None = None,
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> tuple[ManifestRoutingReference, ...]:
    source = identity or default_governance_routing_identity()
    route_records = records or default_governance_route_records()
    return (
        ManifestRoutingReference(
            manifest_routing_reference_id="v4_2_manifest_routing_reference_primary",
            manifest_reference=source.source_manifest_reference,
            manifest_hash_reference=source.source_manifest_hash_reference,
            route_record_ids=tuple(record.route_record_id for record in route_records),
            deterministic_order=10,
        ),
    )


def default_dependency_graph_routing_references(
    identity: GovernanceRoutingIdentity | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> tuple[DependencyGraphRoutingReference, ...]:
    source = identity or default_governance_routing_identity()
    graph = dependency_graph or default_coordination_dependency_graph()
    route_records = records or default_governance_route_records()
    return (
        DependencyGraphRoutingReference(
            dependency_graph_routing_reference_id="v4_2_dependency_graph_routing_reference_primary",
            dependency_graph_reference=source.source_dependency_graph_reference,
            dependency_graph_hash_reference=source.source_dependency_graph_hash_reference,
            node_references=tuple(node.node_id for node in graph.nodes),
            edge_references=tuple(edge.edge_id for edge in graph.edges),
            route_record_ids=tuple(record.route_record_id for record in route_records),
            deterministic_order=10,
        ),
    )


def default_lineage_routing_references(
    identity: GovernanceRoutingIdentity | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> tuple[LineageRoutingReference, ...]:
    source = identity or default_governance_routing_identity()
    lineage = lineage_chain or default_coordination_lineage_chain()
    route_records = records or default_governance_route_records()
    return (
        LineageRoutingReference(
            lineage_routing_reference_id="v4_2_lineage_routing_reference_primary",
            lineage_chain_reference=source.source_lineage_chain_reference,
            lineage_chain_hash_reference=source.source_lineage_chain_hash_reference,
            lineage_record_references=tuple(record.record_id for record in lineage.records),
            route_record_ids=tuple(record.route_record_id for record in route_records),
            deterministic_order=10,
        ),
    )


def default_sequencing_routing_references(
    identity: GovernanceRoutingIdentity | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> tuple[SequencingRoutingReference, ...]:
    source = identity or default_governance_routing_identity()
    source_sequencing = sequencing or default_coordination_sequencing_intelligence()
    route_records = records or default_governance_route_records()
    return (
        SequencingRoutingReference(
            sequencing_routing_reference_id="v4_2_sequencing_routing_reference_primary",
            sequencing_reference=source.source_sequencing_reference,
            sequencing_hash_reference=source.source_sequencing_hash_reference,
            sequence_record_references=tuple(record.sequence_record_id for record in source_sequencing.sequence_records),
            route_record_ids=tuple(record.route_record_id for record in route_records),
            deterministic_order=10,
        ),
    )


def default_route_state_visibility(
    route_state: str,
    visibility_id: str,
    deterministic_order: int,
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> RouteStateVisibility:
    route_records = records or default_governance_route_records()
    matching = tuple(record for record in route_records if record.route_state == route_state)
    return RouteStateVisibility(
        visibility_id=visibility_id,
        route_state=route_state,
        route_record_ids=tuple(record.route_record_id for record in matching),
        source_reference_ids=tuple(record.source_reference_id for record in matching),
        target_reference_ids=tuple(record.target_reference_id for record in matching),
        reason_visibility=tuple(record.reason for record in matching),
        deterministic_order=deterministic_order,
    )


def default_non_executable_route_ordering_visibility(
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> NonExecutableRouteOrderingVisibility:
    route_records = tuple(sorted(records or default_governance_route_records(), key=lambda item: item.ordering_position))
    return NonExecutableRouteOrderingVisibility(
        ordering_visibility_id="v4_2_non_executable_route_ordering_primary",
        ordered_route_record_ids=tuple(record.route_record_id for record in route_records),
        ordered_source_reference_ids=tuple(record.source_reference_id for record in route_records),
        ordered_target_reference_ids=tuple(record.target_reference_id for record in route_records),
        blocked_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_BLOCKED
        ),
        prohibited_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_PROHIBITED
        ),
        unsupported_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_UNSUPPORTED
        ),
        stale_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_STALE
        ),
        missing_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_MISSING
        ),
        conflicting_ordering_ids=tuple(
            record.route_record_id for record in route_records if record.route_state == ROUTE_STATE_CONFLICTING
        ),
        deterministic_order=10,
    )


def default_governance_routing_diagnostics(
    records: tuple[GovernanceRouteRecord, ...] | None = None,
) -> tuple[GovernanceRoutingDiagnostic, ...]:
    route_records = records or default_governance_route_records()

    def ids_for(route_state: str) -> tuple[str, ...]:
        return tuple(record.route_record_id for record in route_records if record.route_state == route_state)

    def refs_for(route_state: str) -> tuple[str, ...]:
        return tuple(
            reference
            for record in route_records
            if record.route_state == route_state
            for reference in (record.source_reference_id, record.target_reference_id)
        )

    all_record_ids = tuple(record.route_record_id for record in route_records)
    all_reference_ids = tuple(
        reference for record in route_records for reference in (record.source_reference_id, record.target_reference_id)
    )
    return (
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_ordering_diagnostic",
            category=ROUTE_DIAGNOSTIC_ORDERING,
            severity="info",
            finding="Route ordering is visible as non-executable evidence only.",
            affected_route_record_ids=all_record_ids,
            affected_reference_ids=all_reference_ids,
            deterministic_order=10,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_blocked_diagnostic",
            category=ROUTE_DIAGNOSTIC_BLOCKED,
            severity="blocked",
            finding="Blocked route states remain fail-visible and unrouted.",
            affected_route_record_ids=ids_for(ROUTE_STATE_BLOCKED),
            affected_reference_ids=refs_for(ROUTE_STATE_BLOCKED),
            deterministic_order=20,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_prohibited_diagnostic",
            category=ROUTE_DIAGNOSTIC_PROHIBITED,
            severity="prohibited",
            finding="Prohibited route states remain fail-visible and inactive.",
            affected_route_record_ids=ids_for(ROUTE_STATE_PROHIBITED),
            affected_reference_ids=refs_for(ROUTE_STATE_PROHIBITED),
            deterministic_order=30,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_unsupported_diagnostic",
            category=ROUTE_DIAGNOSTIC_UNSUPPORTED,
            severity="warning",
            finding="Unsupported route states remain fail-visible and unresolved.",
            affected_route_record_ids=ids_for(ROUTE_STATE_UNSUPPORTED),
            affected_reference_ids=refs_for(ROUTE_STATE_UNSUPPORTED),
            deterministic_order=40,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_stale_diagnostic",
            category=ROUTE_DIAGNOSTIC_STALE,
            severity="warning",
            finding="Stale route states remain fail-visible read-only evidence.",
            affected_route_record_ids=ids_for(ROUTE_STATE_STALE),
            affected_reference_ids=refs_for(ROUTE_STATE_STALE),
            deterministic_order=50,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_missing_diagnostic",
            category=ROUTE_DIAGNOSTIC_MISSING,
            severity="warning",
            finding="Missing route states remain fail-visible and unrepaired.",
            affected_route_record_ids=ids_for(ROUTE_STATE_MISSING),
            affected_reference_ids=refs_for(ROUTE_STATE_MISSING),
            deterministic_order=60,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_conflicting_diagnostic",
            category=ROUTE_DIAGNOSTIC_CONFLICTING,
            severity="blocked",
            finding="Conflicting route states remain fail-visible and unresolved.",
            affected_route_record_ids=ids_for(ROUTE_STATE_CONFLICTING),
            affected_reference_ids=refs_for(ROUTE_STATE_CONFLICTING),
            deterministic_order=70,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_compatibility_diagnostic",
            category=ROUTE_DIAGNOSTIC_COMPATIBILITY,
            severity="info",
            finding="Manifest, dependency graph, lineage chain, and sequencing compatibility are deterministic evidence.",
            affected_route_record_ids=all_record_ids,
            affected_reference_ids=all_reference_ids,
            deterministic_order=80,
        ),
        GovernanceRoutingDiagnostic(
            diagnostic_id="v4_2_governance_routing_non_execution_diagnostic",
            category=ROUTE_DIAGNOSTIC_NON_EXECUTION,
            severity="info",
            finding="Governance routing visibility remains non-executing and non-routing.",
            affected_route_record_ids=all_record_ids,
            affected_reference_ids=(),
            deterministic_order=90,
        ),
    )


def default_governance_routing_governance(
    identity: GovernanceRoutingIdentity | None = None,
) -> GovernanceRoutingGovernance:
    source = identity or default_governance_routing_identity()
    return GovernanceRoutingGovernance(
        governance_id=source.governance_reference,
        governance_references=(
            "v4_2_coordination_manifest_governance_primary",
            "v4_2_coordination_dependency_graph_governance_boundary",
            "v4_2_coordination_lineage_chain_governance_boundary",
            "v4_2_coordination_sequencing_governance_boundary",
            "v4_2_governance_routing_boundary",
        ),
        explicit_limitations=EXPLICIT_GOVERNANCE_ROUTING_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_GOVERNANCE_ROUTING_PROHIBITIONS,
        deterministic_order=10,
    )


def default_governance_routing_visibility(
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
) -> GovernanceRoutingVisibility:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    identity = default_governance_routing_identity(source_manifest, source_graph, source_lineage, source_sequencing)
    records = default_governance_route_records()
    return GovernanceRoutingVisibility(
        identity=identity,
        source_references=default_routing_source_references(identity),
        target_references=default_routing_target_references(identity),
        manifest_routing_references=default_manifest_routing_references(identity, records),
        dependency_graph_routing_references=default_dependency_graph_routing_references(identity, source_graph, records),
        lineage_routing_references=default_lineage_routing_references(identity, source_lineage, records),
        sequencing_routing_references=default_sequencing_routing_references(identity, source_sequencing, records),
        route_records=records,
        ordering_visibility=default_non_executable_route_ordering_visibility(records),
        blocked_route_visibility=default_route_state_visibility(
            ROUTE_STATE_BLOCKED,
            "v4_2_governance_route_blocked_visibility_primary",
            20,
            records,
        ),
        prohibited_route_visibility=default_route_state_visibility(
            ROUTE_STATE_PROHIBITED,
            "v4_2_governance_route_prohibited_visibility_primary",
            30,
            records,
        ),
        unsupported_route_visibility=default_route_state_visibility(
            ROUTE_STATE_UNSUPPORTED,
            "v4_2_governance_route_unsupported_visibility_primary",
            40,
            records,
        ),
        stale_route_visibility=default_route_state_visibility(
            ROUTE_STATE_STALE,
            "v4_2_governance_route_stale_visibility_primary",
            50,
            records,
        ),
        missing_route_visibility=default_route_state_visibility(
            ROUTE_STATE_MISSING,
            "v4_2_governance_route_missing_visibility_primary",
            60,
            records,
        ),
        conflicting_route_visibility=default_route_state_visibility(
            ROUTE_STATE_CONFLICTING,
            "v4_2_governance_route_conflicting_visibility_primary",
            70,
            records,
        ),
        diagnostics=default_governance_routing_diagnostics(records),
        governance_visibility=default_governance_routing_governance(identity),
        compatibility_manifest_reference=source_manifest.identity.manifest_id,
        compatibility_dependency_graph_reference=source_graph.identity.graph_id,
        compatibility_lineage_chain_reference=source_lineage.identity.chain_id,
        compatibility_sequencing_reference=source_sequencing.identity.sequencing_id,
    )
