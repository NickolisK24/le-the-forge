"""Deterministic v4.1 refresh dependency graph governance models.

Refresh dependency graphs are descriptive governance evidence only. They do not
execute dependencies, orchestrate refreshes, sequence work automatically,
resolve dependencies, remediate blockers, consume production bundles, integrate
with planners, authorize behavior, recover state, roll back state, or mutate
runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_DEPENDENCY_GRAPH_PHASE_ID = "v4_1_refresh_dependency_graph_infrastructure"
V4_1_REFRESH_DEPENDENCY_GRAPH_SCHEMA_VERSION = "v4_1.refresh_dependency_graph_infrastructure.1"
V4_1_REFRESH_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION = "v4_1.refresh_dependency_graph_report.1"
V4_1_REFRESH_DEPENDENCY_GRAPH_DIAGNOSTICS_SCHEMA_VERSION = "v4_1.refresh_dependency_graph_diagnostics_report.1"
V4_1_REFRESH_DEPENDENCY_GRAPH_INTEGRITY_SCHEMA_VERSION = "v4_1.refresh_dependency_graph_integrity_report.1"
V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE = "v4_1_refresh_dependency_graph_stable"
V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_BLOCKED = "v4_1_refresh_dependency_graph_blocked"
V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_DEPENDENCY_GRAPH_PURPOSE = "deterministic_refresh_dependency_governance_intelligence_only"

DEPENDENCY_GRAPH_STATE_SUPPORTED = "supported"
DEPENDENCY_GRAPH_STATE_BLOCKED = "blocked"
DEPENDENCY_GRAPH_STATE_UNSUPPORTED = "unsupported"
DEPENDENCY_GRAPH_STATE_STALE = "stale"
DEPENDENCY_GRAPH_STATE_PROHIBITED = "prohibited"
DEPENDENCY_GRAPH_STATE_CIRCULAR = "circular"
DEPENDENCY_GRAPH_STATE_LINEAGE_GAP = "lineage_gap"
DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP = "provenance_gap"
DEPENDENCY_GRAPH_STATES: tuple[str, ...] = (
    DEPENDENCY_GRAPH_STATE_SUPPORTED,
    DEPENDENCY_GRAPH_STATE_BLOCKED,
    DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
    DEPENDENCY_GRAPH_STATE_STALE,
    DEPENDENCY_GRAPH_STATE_PROHIBITED,
    DEPENDENCY_GRAPH_STATE_CIRCULAR,
    DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
    DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
)
FAIL_VISIBLE_DEPENDENCY_GRAPH_STATES: tuple[str, ...] = (
    DEPENDENCY_GRAPH_STATE_BLOCKED,
    DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
    DEPENDENCY_GRAPH_STATE_STALE,
    DEPENDENCY_GRAPH_STATE_PROHIBITED,
    DEPENDENCY_GRAPH_STATE_CIRCULAR,
    DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
    DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
)

DEPENDENCY_SEVERITY_INFO = "info"
DEPENDENCY_SEVERITY_WARNING = "warning"
DEPENDENCY_SEVERITY_BLOCKED = "blocked"
DEPENDENCY_SEVERITY_PROHIBITED = "prohibited"

DEPENDENCY_RELATIONSHIP_MANIFEST_SOURCE = "manifest_source_dependency"
DEPENDENCY_RELATIONSHIP_SCHEMA = "schema_dependency"
DEPENDENCY_RELATIONSHIP_PROVIDER = "provider_dependency"
DEPENDENCY_RELATIONSHIP_RUNTIME_PROHIBITED = "runtime_prohibited_dependency"
DEPENDENCY_RELATIONSHIP_CIRCULAR_VISIBILITY = "circular_dependency_visibility"
DEPENDENCY_RELATIONSHIP_LINEAGE = "lineage_dependency"
DEPENDENCY_RELATIONSHIP_PROVENANCE = "provenance_dependency"
DEPENDENCY_RELATIONSHIP_TYPES: tuple[str, ...] = (
    DEPENDENCY_RELATIONSHIP_MANIFEST_SOURCE,
    DEPENDENCY_RELATIONSHIP_SCHEMA,
    DEPENDENCY_RELATIONSHIP_PROVIDER,
    DEPENDENCY_RELATIONSHIP_RUNTIME_PROHIBITED,
    DEPENDENCY_RELATIONSHIP_CIRCULAR_VISIBILITY,
    DEPENDENCY_RELATIONSHIP_LINEAGE,
    DEPENDENCY_RELATIONSHIP_PROVENANCE,
)

PROHIBITED_DEPENDENCY_DOMAINS: tuple[str, ...] = (
    "refresh_execution",
    "orchestration_execution",
    "dependency_execution",
    "automatic_refresh_sequencing",
    "automatic_dependency_resolution",
    "automatic_migration",
    "automatic_rollback",
    "automatic_recovery",
    "planner_integration",
    "production_bundle_consumption",
    "remediation_systems",
    "optimization_systems",
    "recommendation_ranking_scoring_selection",
    "authorization_approval_systems",
    "runtime_mutation",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_REFRESH_DEPENDENCY_GRAPH_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 2 creates deterministic refresh dependency governance metadata only.",
    "v4.1 Phase 2 does not enable refresh execution.",
    "v4.1 Phase 2 does not enable orchestration.",
    "v4.1 Phase 2 does not enable dependency execution.",
    "v4.1 Phase 2 does not enable automatic sequencing.",
    "v4.1 Phase 2 does not enable automatic dependency resolution.",
    "v4.1 Phase 2 does not enable planner integration.",
    "v4.1 Phase 2 does not enable production consumption.",
    "v4.1 Phase 2 does not enable remediation.",
    "v4.1 Phase 2 does not enable mutation behavior.",
)

EXPLICIT_REFRESH_DEPENDENCY_GRAPH_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration exists.",
    "No dependency execution exists.",
    "No automatic sequencing exists.",
    "No automatic dependency resolution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No mutation behavior exists.",
    "No recommendation, ranking, scoring, or selection behavior exists.",
    "No approval or authorization behavior exists.",
    "No silent dependency fallback behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshDependencyGraphIdentity:
    graph_id: str
    refresh_cycle_id: str
    graph_version: str
    source_manifest_reference: str
    source_manifest_hash_reference: str
    schema_version: str
    generated_at: str
    provenance_reference: str
    lineage_reference: str
    diagnostics_reference: str
    integrity_reference: str
    governance_reference: str
    graph_scope: str = "refresh_dependency_graph_identity_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_DEPENDENCY_GRAPH_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    graph_execution_enabled: bool = False
    orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshDependencyNode:
    node_id: str
    node_type: str
    manifest_reference: str
    provider_reference: str
    dependency_domain: str
    schema_reference: str
    source_lineage_reference: str
    provenance_reference: str
    state: str
    reason: str
    deterministic_order: int
    severity: str = DEPENDENCY_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    dependency_execution_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshDependencyEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    relationship_type: str
    relationship_state: str
    reason: str
    lineage_reference: str
    provenance_reference: str
    deterministic_order: int
    severity: str = DEPENDENCY_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    circular_visibility: bool = False
    drift_visible: bool = False
    hidden: bool = False
    dependency_execution_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    automatic_refresh_sequencing_enabled: bool = False
    orchestration_enabled: bool = False
    remediation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshDependencyLineageChain:
    lineage_chain_id: str
    graph_lineage_reference: str
    node_references: tuple[str, ...]
    edge_references: tuple[str, ...]
    prior_graph_references: tuple[str, ...]
    successor_graph_references: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    lineage_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_lineage_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "node_references",
            "edge_references",
            "prior_graph_references",
            "successor_graph_references",
            "lineage_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyProvenanceChain:
    provenance_chain_id: str
    graph_provenance_reference: str
    source_manifest_reference: str
    source_evidence_references: tuple[str, ...]
    node_provenance_references: tuple[str, ...]
    edge_provenance_references: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    provenance_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    inferred_provenance_allowed: bool = False
    hidden_provenance_resolution_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_evidence_references",
            "node_provenance_references",
            "edge_provenance_references",
            "provenance_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyContinuityMetadata:
    continuity_id: str
    graph_continuity_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    replay_continuity_references: tuple[str, ...]
    rollback_continuity_references: tuple[str, ...]
    drift_visibility_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    continuity_preserved: bool = True
    graph_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "graph_continuity_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_continuity_references",
            "rollback_continuity_references",
            "drift_visibility_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyReplayMetadata:
    replay_id: str
    replay_evidence_references: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    replay_safe: bool = True
    descriptive_only: bool = True
    live_replay_enabled: bool = False
    dependency_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_evidence_references", "replay_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyRollbackMetadata:
    rollback_id: str
    rollback_evidence_references: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    rollback_safe: bool = True
    descriptive_only: bool = True
    automatic_rollback_enabled: bool = False
    recovery_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_evidence_references", "rollback_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyBlockedStateVisibility:
    blocked_visibility_id: str
    blocked_dependency_edges: tuple[str, ...]
    circular_dependency_edges: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_resolution_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_dependency_edges",
            "circular_dependency_edges",
            "lineage_discontinuity_visibility",
            "provenance_discontinuity_visibility",
            "replay_discontinuity_visibility",
            "rollback_discontinuity_visibility",
            "prohibited_execution_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_remediation_leakage",
            "prohibited_planner_integration_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyUnsupportedStateVisibility:
    unsupported_visibility_id: str
    unsupported_dependency_nodes: tuple[str, ...]
    unsupported_dependency_edges: tuple[str, ...]
    unsupported_dependency_providers: tuple[str, ...]
    stale_dependency_edges: tuple[str, ...]
    prohibited_dependency_edges: tuple[str, ...]
    prohibited_dependency_domains: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    hidden_unsupported_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_dependency_nodes",
            "unsupported_dependency_edges",
            "unsupported_dependency_providers",
            "stale_dependency_edges",
            "prohibited_dependency_edges",
            "prohibited_dependency_domains",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyDriftVisibility:
    drift_visibility_id: str
    stale_relationships: tuple[str, ...]
    changed_manifest_references: tuple[str, ...]
    dependency_drift_references: tuple[str, ...]
    deterministic_order: int
    drift_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_migration_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    hidden_drift_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("stale_relationships", "changed_manifest_references", "dependency_drift_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyDiagnosticsVisibility:
    diagnostics_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    circular_dependency_visibility: tuple[str, ...]
    unsupported_dependency_visibility: tuple[str, ...]
    prohibited_dependency_visibility: tuple[str, ...]
    drift_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_recovery_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "circular_dependency_visibility",
            "unsupported_dependency_visibility",
            "prohibited_dependency_visibility",
            "drift_visibility",
            "integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyGovernanceVisibility:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    refresh_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_refresh_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    mutation_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDependencyGraph:
    identity: RefreshDependencyGraphIdentity
    nodes: tuple[RefreshDependencyNode, ...]
    edges: tuple[RefreshDependencyEdge, ...]
    lineage_chains: tuple[RefreshDependencyLineageChain, ...]
    provenance_chains: tuple[RefreshDependencyProvenanceChain, ...]
    continuity_metadata: RefreshDependencyContinuityMetadata
    replay_metadata: RefreshDependencyReplayMetadata
    rollback_metadata: RefreshDependencyRollbackMetadata
    blocked_state_visibility: RefreshDependencyBlockedStateVisibility
    unsupported_state_visibility: RefreshDependencyUnsupportedStateVisibility
    drift_visibility: RefreshDependencyDriftVisibility
    diagnostics_visibility: RefreshDependencyDiagnosticsVisibility
    governance_visibility: RefreshDependencyGovernanceVisibility
    graph_scope: str = V4_1_REFRESH_DEPENDENCY_GRAPH_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    graph_execution_enabled: bool = False
    dependency_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_refresh_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    automatic_migration_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_dependency_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("nodes", "edges", "lineage_chains", "provenance_chains"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_dependency_graph_identity() -> RefreshDependencyGraphIdentity:
    return RefreshDependencyGraphIdentity(
        graph_id="v4_1_refresh_dependency_graph_primary",
        refresh_cycle_id="v4_1_phase_2_refresh_dependency_graph_infrastructure",
        graph_version="v4.1.0-phase-2",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_manifest_hash_reference="9f80efd07620a61c592f10c3042f04ce1a5e477dd8312fb241548ac518a5df5d",
        schema_version=V4_1_REFRESH_DEPENDENCY_GRAPH_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT,
        provenance_reference="v4_1_refresh_dependency_graph_provenance_primary",
        lineage_reference="v4_1_refresh_dependency_graph_lineage_primary",
        diagnostics_reference="v4_1_refresh_dependency_graph_diagnostics_primary",
        integrity_reference="v4_1_refresh_dependency_graph_integrity_primary",
        governance_reference="v4_1_refresh_dependency_graph_governance_primary",
    )


def default_dependency_nodes(
    identity: RefreshDependencyGraphIdentity | None = None,
) -> tuple[RefreshDependencyNode, ...]:
    source = identity or default_dependency_graph_identity()
    return (
        RefreshDependencyNode(
            node_id="v4_1_node_refresh_manifest_primary",
            node_type="refresh_manifest",
            manifest_reference=source.source_manifest_reference,
            provider_reference="v4_1_refresh_manifest_foundations",
            dependency_domain="manifest_identity",
            schema_reference="v4_1.refresh_manifest_foundations.1",
            source_lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=DEPENDENCY_GRAPH_STATE_SUPPORTED,
            reason="phase 1 refresh manifest foundation is available as deterministic governance evidence",
            deterministic_order=1,
        ),
        RefreshDependencyNode(
            node_id="v4_1_node_v4_0_closeout_evidence",
            node_type="source_evidence",
            manifest_reference="v4_0_closeout_and_v4_1_readiness_report",
            provider_reference="v4_0_closeout_governance",
            dependency_domain="source_lineage",
            schema_reference="v4_0.closeout_and_v4_1_readiness_report.1",
            source_lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=DEPENDENCY_GRAPH_STATE_SUPPORTED,
            reason="v4.0 closeout evidence anchors refresh manifest source lineage",
            deterministic_order=2,
        ),
        RefreshDependencyNode(
            node_id="v4_1_node_future_refresh_provider",
            node_type="future_provider",
            manifest_reference="future_refresh_provider_contract",
            provider_reference="future_refresh_provider_contract_not_declared",
            dependency_domain="provider_contract",
            schema_reference="future.refresh_provider_contract.unknown",
            source_lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
            reason="future refresh provider contracts are not declared in phase 2",
            deterministic_order=3,
            severity=DEPENDENCY_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshDependencyNode(
            node_id="v4_1_node_production_runtime_bundle",
            node_type="prohibited_runtime_source",
            manifest_reference="production_runtime_bundle",
            provider_reference="production_runtime_bundle_dependency",
            dependency_domain="production_bundle_consumption",
            schema_reference="production.runtime_bundle.prohibited",
            source_lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=DEPENDENCY_GRAPH_STATE_PROHIBITED,
            reason="production bundle consumption is prohibited for refresh dependency governance",
            deterministic_order=4,
            severity=DEPENDENCY_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_dependency_edges(
    identity: RefreshDependencyGraphIdentity | None = None,
) -> tuple[RefreshDependencyEdge, ...]:
    source = identity or default_dependency_graph_identity()
    return (
        RefreshDependencyEdge(
            edge_id="v4_1_edge_manifest_to_closeout_source",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_v4_0_closeout_evidence",
            relationship_type=DEPENDENCY_RELATIONSHIP_MANIFEST_SOURCE,
            relationship_state=DEPENDENCY_GRAPH_STATE_SUPPORTED,
            reason="refresh manifest source evidence references v4.0 closeout governance",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=1,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_manifest_to_future_provider",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_future_refresh_provider",
            relationship_type=DEPENDENCY_RELATIONSHIP_PROVIDER,
            relationship_state=DEPENDENCY_GRAPH_STATE_UNSUPPORTED,
            reason="future provider relationship remains unsupported and fail-visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=2,
            severity=DEPENDENCY_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_manifest_to_production_runtime_bundle",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_production_runtime_bundle",
            relationship_type=DEPENDENCY_RELATIONSHIP_RUNTIME_PROHIBITED,
            relationship_state=DEPENDENCY_GRAPH_STATE_PROHIBITED,
            reason="production runtime bundle dependency remains prohibited and not consumed",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=3,
            severity=DEPENDENCY_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_manifest_to_blocked_dependency_gap",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_future_refresh_provider",
            relationship_type=DEPENDENCY_RELATIONSHIP_SCHEMA,
            relationship_state=DEPENDENCY_GRAPH_STATE_BLOCKED,
            reason="future refresh provider dependency schema is not declared",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=4,
            severity=DEPENDENCY_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_future_provider_to_manifest_circular_visibility",
            from_node_id="v4_1_node_future_refresh_provider",
            to_node_id="v4_1_node_refresh_manifest_primary",
            relationship_type=DEPENDENCY_RELATIONSHIP_CIRCULAR_VISIBILITY,
            relationship_state=DEPENDENCY_GRAPH_STATE_CIRCULAR,
            reason="potential future-provider cycle is visible and not traversed or resolved",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=5,
            severity=DEPENDENCY_SEVERITY_BLOCKED,
            fail_visible=True,
            circular_visibility=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_manifest_to_stale_lifecycle_dependency",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_v4_0_closeout_evidence",
            relationship_type=DEPENDENCY_RELATIONSHIP_LINEAGE,
            relationship_state=DEPENDENCY_GRAPH_STATE_STALE,
            reason="v4.0 lifecycle dependency snapshot is read-only stale governance evidence",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=6,
            severity=DEPENDENCY_SEVERITY_WARNING,
            fail_visible=True,
            drift_visible=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_future_lineage_gap_visibility",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_future_refresh_provider",
            relationship_type=DEPENDENCY_RELATIONSHIP_LINEAGE,
            relationship_state=DEPENDENCY_GRAPH_STATE_LINEAGE_GAP,
            reason="future provider lineage continuity is not declared and remains visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=7,
            severity=DEPENDENCY_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshDependencyEdge(
            edge_id="v4_1_edge_future_provenance_gap_visibility",
            from_node_id="v4_1_node_refresh_manifest_primary",
            to_node_id="v4_1_node_future_refresh_provider",
            relationship_type=DEPENDENCY_RELATIONSHIP_PROVENANCE,
            relationship_state=DEPENDENCY_GRAPH_STATE_PROVENANCE_GAP,
            reason="future provider provenance continuity is not declared and remains visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=8,
            severity=DEPENDENCY_SEVERITY_WARNING,
            fail_visible=True,
        ),
    )


def default_lineage_chain(
    identity: RefreshDependencyGraphIdentity | None = None,
    edges: tuple[RefreshDependencyEdge, ...] | None = None,
) -> RefreshDependencyLineageChain:
    source = identity or default_dependency_graph_identity()
    graph_edges = edges or default_dependency_edges(source)
    return RefreshDependencyLineageChain(
        lineage_chain_id="v4_1_refresh_dependency_lineage_chain_primary",
        graph_lineage_reference=source.lineage_reference,
        node_references=tuple(node.node_id for node in default_dependency_nodes(source)),
        edge_references=tuple(edge.edge_id for edge in graph_edges),
        prior_graph_references=(
            "v4_1_refresh_manifest_foundations",
            "v4_0_closeout_and_v4_1_readiness",
        ),
        successor_graph_references=("future_refresh_dependency_governance_phase_not_declared",),
        lineage_discontinuity_visibility=("v4_1_future_provider_lineage_not_declared",),
        deterministic_order=1,
    )


def default_provenance_chain(
    identity: RefreshDependencyGraphIdentity | None = None,
    nodes: tuple[RefreshDependencyNode, ...] | None = None,
    edges: tuple[RefreshDependencyEdge, ...] | None = None,
) -> RefreshDependencyProvenanceChain:
    source = identity or default_dependency_graph_identity()
    graph_nodes = nodes or default_dependency_nodes(source)
    graph_edges = edges or default_dependency_edges(source)
    return RefreshDependencyProvenanceChain(
        provenance_chain_id="v4_1_refresh_dependency_provenance_chain_primary",
        graph_provenance_reference=source.provenance_reference,
        source_manifest_reference=source.source_manifest_reference,
        source_evidence_references=(
            "docs/generated/v4_1_refresh_manifest_foundations_report.json",
            "docs/generated/v4_1_refresh_manifest_diagnostics_report.json",
            "docs/migration/V4_1_REFRESH_MANIFEST_FOUNDATIONS.md",
        ),
        node_provenance_references=tuple(node.provenance_reference for node in graph_nodes),
        edge_provenance_references=tuple(edge.provenance_reference for edge in graph_edges),
        provenance_discontinuity_visibility=("v4_1_future_provider_provenance_not_declared",),
        deterministic_order=1,
    )


def default_continuity_metadata(identity: RefreshDependencyGraphIdentity | None = None) -> RefreshDependencyContinuityMetadata:
    source = identity or default_dependency_graph_identity()
    return RefreshDependencyContinuityMetadata(
        continuity_id="v4_1_refresh_dependency_continuity_primary",
        graph_continuity_references=(
            source.graph_id,
            "v4_1_refresh_manifest_foundations",
        ),
        lineage_continuity_references=(
            source.lineage_reference,
            "v4_1_refresh_dependency_lineage_chain_primary",
        ),
        provenance_continuity_references=(
            source.provenance_reference,
            "v4_1_refresh_dependency_provenance_chain_primary",
        ),
        replay_continuity_references=("v4_1_refresh_dependency_replay_primary",),
        rollback_continuity_references=("v4_1_refresh_dependency_rollback_primary",),
        drift_visibility_references=("v4_1_refresh_dependency_drift_visibility_primary",),
        deterministic_hash_reference="v4_1_refresh_dependency_continuity_hash",
        deterministic_order=1,
    )


def default_replay_metadata() -> RefreshDependencyReplayMetadata:
    return RefreshDependencyReplayMetadata(
        replay_id="v4_1_refresh_dependency_replay_primary",
        replay_evidence_references=(
            "v4_1_refresh_dependency_graph_serialization_snapshot",
            "v4_1_refresh_dependency_graph_hash_snapshot",
        ),
        replay_discontinuity_visibility=("future_refresh_dependency_replay_source_not_declared",),
        deterministic_hash_reference="v4_1_refresh_dependency_replay_hash",
        deterministic_order=1,
    )


def default_rollback_metadata() -> RefreshDependencyRollbackMetadata:
    return RefreshDependencyRollbackMetadata(
        rollback_id="v4_1_refresh_dependency_rollback_primary",
        rollback_evidence_references=(
            "docs/generated/v4_1_refresh_manifest_foundations_report.json",
            "docs/generated/v4_1_refresh_manifest_diagnostics_report.json",
        ),
        rollback_discontinuity_visibility=("future_refresh_dependency_rollback_target_not_declared",),
        deterministic_hash_reference="v4_1_refresh_dependency_rollback_hash",
        deterministic_order=1,
    )


def default_blocked_state_visibility(edges: tuple[RefreshDependencyEdge] | None = None) -> RefreshDependencyBlockedStateVisibility:
    graph_edges = edges or default_dependency_edges()
    return RefreshDependencyBlockedStateVisibility(
        blocked_visibility_id="v4_1_refresh_dependency_blocked_visibility_primary",
        blocked_dependency_edges=tuple(
            edge.edge_id for edge in graph_edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_BLOCKED
        ),
        circular_dependency_edges=tuple(edge.edge_id for edge in graph_edges if edge.circular_visibility),
        lineage_discontinuity_visibility=("v4_1_future_provider_lineage_not_declared",),
        provenance_discontinuity_visibility=("v4_1_future_provider_provenance_not_declared",),
        replay_discontinuity_visibility=("future_refresh_dependency_replay_source_not_declared",),
        rollback_discontinuity_visibility=("future_refresh_dependency_rollback_target_not_declared",),
        prohibited_execution_leakage=("dependency_execution_enabled",),
        prohibited_orchestration_leakage=("orchestration_enabled",),
        prohibited_remediation_leakage=("remediation_enabled",),
        prohibited_planner_integration_leakage=("planner_integration_enabled",),
        deterministic_order=1,
    )


def default_unsupported_state_visibility(
    nodes: tuple[RefreshDependencyNode, ...] | None = None,
    edges: tuple[RefreshDependencyEdge, ...] | None = None,
) -> RefreshDependencyUnsupportedStateVisibility:
    graph_nodes = nodes or default_dependency_nodes()
    graph_edges = edges or default_dependency_edges()
    return RefreshDependencyUnsupportedStateVisibility(
        unsupported_visibility_id="v4_1_refresh_dependency_unsupported_visibility_primary",
        unsupported_dependency_nodes=tuple(
            node.node_id for node in graph_nodes if node.state == DEPENDENCY_GRAPH_STATE_UNSUPPORTED
        ),
        unsupported_dependency_edges=tuple(
            edge.edge_id for edge in graph_edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_UNSUPPORTED
        ),
        unsupported_dependency_providers=tuple(
            node.provider_reference for node in graph_nodes if node.state == DEPENDENCY_GRAPH_STATE_UNSUPPORTED
        ),
        stale_dependency_edges=tuple(
            edge.edge_id for edge in graph_edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_STALE
        ),
        prohibited_dependency_edges=tuple(
            edge.edge_id for edge in graph_edges if edge.relationship_state == DEPENDENCY_GRAPH_STATE_PROHIBITED
        ),
        prohibited_dependency_domains=PROHIBITED_DEPENDENCY_DOMAINS,
        deterministic_order=1,
    )


def default_drift_visibility(edges: tuple[RefreshDependencyEdge, ...] | None = None) -> RefreshDependencyDriftVisibility:
    graph_edges = edges or default_dependency_edges()
    return RefreshDependencyDriftVisibility(
        drift_visibility_id="v4_1_refresh_dependency_drift_visibility_primary",
        stale_relationships=tuple(edge.edge_id for edge in graph_edges if edge.drift_visible),
        changed_manifest_references=("v4_0_lifecycle_dependency_snapshot_read_only",),
        dependency_drift_references=("future_refresh_provider_contract_not_declared",),
        deterministic_order=1,
    )


def default_diagnostics_visibility(
    blocked: RefreshDependencyBlockedStateVisibility | None = None,
    unsupported: RefreshDependencyUnsupportedStateVisibility | None = None,
    drift: RefreshDependencyDriftVisibility | None = None,
) -> RefreshDependencyDiagnosticsVisibility:
    blocked_visibility = blocked or default_blocked_state_visibility()
    unsupported_visibility = unsupported or default_unsupported_state_visibility()
    drift_visibility = drift or default_drift_visibility()
    return RefreshDependencyDiagnosticsVisibility(
        diagnostics_id="v4_1_refresh_dependency_graph_diagnostics_primary",
        diagnostic_references=(
            "v4_1_refresh_dependency_visibility_validation",
            "v4_1_refresh_dependency_integrity_validation",
            "v4_1_refresh_dependency_non_execution_validation",
        ),
        warning_visibility=unsupported_visibility.unsupported_dependency_edges
        + unsupported_visibility.stale_dependency_edges
        + drift_visibility.stale_relationships,
        blocker_visibility=blocked_visibility.circular_dependency_edges
        + blocked_visibility.lineage_discontinuity_visibility
        + blocked_visibility.provenance_discontinuity_visibility,
        circular_dependency_visibility=blocked_visibility.circular_dependency_edges,
        unsupported_dependency_visibility=unsupported_visibility.unsupported_dependency_edges
        + unsupported_visibility.unsupported_dependency_nodes,
        prohibited_dependency_visibility=unsupported_visibility.prohibited_dependency_edges
        + unsupported_visibility.prohibited_dependency_domains,
        drift_visibility=drift_visibility.stale_relationships + drift_visibility.dependency_drift_references,
        integrity_visibility=blocked_visibility.prohibited_execution_leakage
        + blocked_visibility.prohibited_orchestration_leakage
        + blocked_visibility.prohibited_remediation_leakage
        + blocked_visibility.prohibited_planner_integration_leakage,
        deterministic_order=1,
    )


def default_governance_visibility() -> RefreshDependencyGovernanceVisibility:
    return RefreshDependencyGovernanceVisibility(
        governance_id="v4_1_refresh_dependency_graph_governance_primary",
        governance_references=(
            "v4_1_refresh_manifest_foundations",
            "v4_1_refresh_dependency_graph_governance_boundary",
        ),
        explicit_limitations=EXPLICIT_REFRESH_DEPENDENCY_GRAPH_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_REFRESH_DEPENDENCY_GRAPH_PROHIBITIONS,
        deterministic_order=1,
    )


def default_refresh_dependency_graph() -> RefreshDependencyGraph:
    identity = default_dependency_graph_identity()
    nodes = default_dependency_nodes(identity)
    edges = default_dependency_edges(identity)
    blocked = default_blocked_state_visibility(edges)
    unsupported = default_unsupported_state_visibility(nodes, edges)
    drift = default_drift_visibility(edges)
    return RefreshDependencyGraph(
        identity=identity,
        nodes=nodes,
        edges=edges,
        lineage_chains=(default_lineage_chain(identity, edges),),
        provenance_chains=(default_provenance_chain(identity, nodes, edges),),
        continuity_metadata=default_continuity_metadata(identity),
        replay_metadata=default_replay_metadata(),
        rollback_metadata=default_rollback_metadata(),
        blocked_state_visibility=blocked,
        unsupported_state_visibility=unsupported,
        drift_visibility=drift,
        diagnostics_visibility=default_diagnostics_visibility(blocked, unsupported, drift),
        governance_visibility=default_governance_visibility(),
    )
