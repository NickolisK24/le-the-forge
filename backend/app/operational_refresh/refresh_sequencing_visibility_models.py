"""Deterministic v4.1 refresh sequencing visibility models.

Refresh sequencing visibility is descriptive governance evidence only. It does
not execute refreshes, orchestrate work, schedule ordering, resolve
dependencies, migrate schemas, recover state, roll back state, consume
production bundles, integrate with planners, remediate blockers, authorize
behavior, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_SEQUENCING_VISIBILITY_PHASE_ID = "v4_1_refresh_sequencing_visibility"
V4_1_REFRESH_SEQUENCING_VISIBILITY_SCHEMA_VERSION = "v4_1.refresh_sequencing_visibility.1"
V4_1_REFRESH_SEQUENCING_VISIBILITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_sequencing_visibility_report.1"
V4_1_REFRESH_SEQUENCING_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.refresh_sequencing_diagnostics_report.1"
V4_1_REFRESH_SEQUENCING_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_sequencing_continuity_report.1"
V4_1_REFRESH_SEQUENCING_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_sequencing_integrity_report.1"
V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE = "v4_1_refresh_sequencing_visibility_stable"
V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_BLOCKED = "v4_1_refresh_sequencing_visibility_blocked"
V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_SEQUENCING_VISIBILITY_PURPOSE = "deterministic_refresh_sequencing_visibility_governance_only"

SEQUENCING_STATE_READY = "ready"
SEQUENCING_STATE_READY_WITH_WARNINGS = "ready_with_warnings"
SEQUENCING_STATE_BLOCKED = "blocked"
SEQUENCING_STATE_UNSUPPORTED = "unsupported"
SEQUENCING_STATE_STALE = "stale"
SEQUENCING_STATE_PROHIBITED = "prohibited"
SEQUENCING_STATE_CIRCULAR = "circular_sequencing"
SEQUENCING_STATE_SEQUENCING_DISCONTINUITY = "sequencing_discontinuity"
SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY = "dependency_ordering_discontinuity"
SEQUENCING_STATE_LINEAGE_DISCONTINUITY = "lineage_discontinuity"
SEQUENCING_STATE_PROVENANCE_DISCONTINUITY = "provenance_discontinuity"
SEQUENCING_STATE_REPLAY_DISCONTINUITY = "replay_discontinuity"
SEQUENCING_STATE_ROLLBACK_DISCONTINUITY = "rollback_discontinuity"
SEQUENCING_STATES: tuple[str, ...] = (
    SEQUENCING_STATE_READY,
    SEQUENCING_STATE_READY_WITH_WARNINGS,
    SEQUENCING_STATE_BLOCKED,
    SEQUENCING_STATE_UNSUPPORTED,
    SEQUENCING_STATE_STALE,
    SEQUENCING_STATE_PROHIBITED,
    SEQUENCING_STATE_CIRCULAR,
    SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
    SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
    SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
    SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
    SEQUENCING_STATE_REPLAY_DISCONTINUITY,
    SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
)
FAIL_VISIBLE_SEQUENCING_STATES: tuple[str, ...] = (
    SEQUENCING_STATE_BLOCKED,
    SEQUENCING_STATE_UNSUPPORTED,
    SEQUENCING_STATE_STALE,
    SEQUENCING_STATE_PROHIBITED,
    SEQUENCING_STATE_CIRCULAR,
    SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
    SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
    SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
    SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
    SEQUENCING_STATE_REPLAY_DISCONTINUITY,
    SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
)

SEQUENCING_SEVERITY_INFO = "info"
SEQUENCING_SEVERITY_WARNING = "warning"
SEQUENCING_SEVERITY_BLOCKED = "blocked"
SEQUENCING_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_SEQUENCING_DOMAINS: tuple[str, ...] = (
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "automatic_dependency_resolution",
    "migration_execution",
    "automatic_migration",
    "automatic_rollback",
    "automatic_recovery",
    "planner_integration",
    "production_bundle_consumption",
    "remediation_systems",
    "recommendation_ranking_scoring_selection",
    "optimization_systems",
    "authorization_approval_systems",
    "runtime_mutation",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_REFRESH_SEQUENCING_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 5 creates deterministic refresh sequencing visibility metadata only.",
    "v4.1 Phase 5 does not enable orchestration execution.",
    "v4.1 Phase 5 does not enable automatic sequencing.",
    "v4.1 Phase 5 does not enable refresh execution.",
    "v4.1 Phase 5 does not enable migration execution.",
    "v4.1 Phase 5 does not enable planner integration.",
    "v4.1 Phase 5 does not enable production consumption.",
    "v4.1 Phase 5 does not enable remediation.",
    "v4.1 Phase 5 does not enable mutation behavior.",
)

EXPLICIT_REFRESH_SEQUENCING_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No automatic dependency resolution exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No mutation behavior exists.",
    "No executable refresh scheduler exists.",
    "No automatic sequencing planner exists.",
    "No silent ordering correction behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshSequencingIdentity:
    sequencing_id: str
    refresh_cycle_id: str
    sequencing_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    source_schema_governance_reference: str
    schema_version: str
    generated_at: str
    sequencing_reference: str
    lineage_reference: str
    provenance_reference: str
    diagnostics_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    governance_scope: str = "refresh_sequencing_visibility_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_SEQUENCING_VISIBILITY_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshOrderingNode:
    node_id: str
    refresh_unit_id: str
    dependency_graph_reference: str
    schema_reference: str
    lineage_reference: str
    provenance_reference: str
    provider: str
    state: str
    reason: str
    deterministic_order: int
    severity: str = SEQUENCING_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_ordering_correction_enabled: bool = False


@dataclass(frozen=True)
class RefreshOrderingRelationship:
    relationship_id: str
    predecessor_node_id: str
    successor_node_id: str
    dependency_reference: str
    sequencing_reference: str
    lineage_reference: str
    provenance_reference: str
    ordering_classification: str
    state: str
    reason: str
    deterministic_order: int
    severity: str = SEQUENCING_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    circular_sequencing_visibility: bool = False
    drift_visible: bool = False
    hidden: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    migration_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_ordering_correction_enabled: bool = False


@dataclass(frozen=True)
class DependencyAwareSequencingVisibility:
    visibility_id: str
    dependency_ordering_references: tuple[str, ...]
    ready_relationship_ids: tuple[str, ...]
    warning_relationship_ids: tuple[str, ...]
    blocked_relationship_ids: tuple[str, ...]
    unsupported_relationship_ids: tuple[str, ...]
    stale_relationship_ids: tuple[str, ...]
    prohibited_relationship_ids: tuple[str, ...]
    circular_relationship_ids: tuple[str, ...]
    sequencing_discontinuity_ids: tuple[str, ...]
    dependency_ordering_discontinuity_ids: tuple[str, ...]
    deterministic_order: int
    dependency_aware_visibility_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    orchestration_enabled: bool = False
    hidden_ordering_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "dependency_ordering_references",
            "ready_relationship_ids",
            "warning_relationship_ids",
            "blocked_relationship_ids",
            "unsupported_relationship_ids",
            "stale_relationship_ids",
            "prohibited_relationship_ids",
            "circular_relationship_ids",
            "sequencing_discontinuity_ids",
            "dependency_ordering_discontinuity_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingContinuityMetadata:
    continuity_id: str
    sequencing_continuity_references: tuple[str, ...]
    dependency_ordering_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    replay_sequencing_references: tuple[str, ...]
    rollback_sequencing_references: tuple[str, ...]
    deterministic_order: int
    sequencing_continuity_preserved: bool = True
    dependency_ordering_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    replay_sequencing_preserved: bool = True
    rollback_sequencing_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "sequencing_continuity_references",
            "dependency_ordering_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_sequencing_references",
            "rollback_sequencing_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingLineageVisibility:
    lineage_id: str
    lineage_references: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_lineage_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_references", "lineage_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingProvenanceVisibility:
    provenance_id: str
    provenance_references: tuple[str, ...]
    inherited_from_references: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    provenance_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    inferred_provenance_allowed: bool = False
    hidden_provenance_resolution_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("provenance_references", "inherited_from_references", "provenance_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshReplaySequencingVisibility:
    replay_id: str
    replay_sequencing_references: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    live_replay_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_sequencing_references", "replay_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshRollbackSequencingVisibility:
    rollback_id: str
    rollback_sequencing_references: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_sequencing_references", "rollback_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingDriftVisibility:
    drift_id: str
    stale_relationship_ids: tuple[str, ...]
    sequencing_drift_references: tuple[str, ...]
    dependency_ordering_drift_references: tuple[str, ...]
    deterministic_order: int
    drift_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_drift_resolution_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    silent_ordering_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("stale_relationship_ids", "sequencing_drift_references", "dependency_ordering_drift_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingBlockedStateVisibility:
    blocked_id: str
    blocked_relationship_ids: tuple[str, ...]
    blocked_ordering_states: tuple[str, ...]
    sequencing_discontinuity_visibility: tuple[str, ...]
    dependency_ordering_discontinuity_visibility: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    circular_sequencing_visibility: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    silent_ordering_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_relationship_ids",
            "blocked_ordering_states",
            "sequencing_discontinuity_visibility",
            "dependency_ordering_discontinuity_visibility",
            "lineage_discontinuity_visibility",
            "provenance_discontinuity_visibility",
            "replay_discontinuity_visibility",
            "rollback_discontinuity_visibility",
            "circular_sequencing_visibility",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_remediation_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingUnsupportedStateVisibility:
    unsupported_id: str
    unsupported_node_ids: tuple[str, ...]
    unsupported_relationship_ids: tuple[str, ...]
    unsupported_sequencing_providers: tuple[str, ...]
    stale_relationship_ids: tuple[str, ...]
    prohibited_relationship_ids: tuple[str, ...]
    prohibited_sequencing_domains: tuple[str, ...]
    failure_visibility: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_unsupported_resolution_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    silent_ordering_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_node_ids",
            "unsupported_relationship_ids",
            "unsupported_sequencing_providers",
            "stale_relationship_ids",
            "prohibited_relationship_ids",
            "prohibited_sequencing_domains",
            "failure_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingDiagnostics:
    diagnostics_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    unsupported_sequencing_visibility: tuple[str, ...]
    prohibited_sequencing_visibility: tuple[str, ...]
    circular_sequencing_visibility: tuple[str, ...]
    drift_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_ordering_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "unsupported_sequencing_visibility",
            "prohibited_sequencing_visibility",
            "circular_sequencing_visibility",
            "drift_visibility",
            "integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingGovernanceVisibility:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSequencingVisibility:
    identity: RefreshSequencingIdentity
    ordering_nodes: tuple[RefreshOrderingNode, ...]
    ordering_relationships: tuple[RefreshOrderingRelationship, ...]
    dependency_aware_visibility: DependencyAwareSequencingVisibility
    continuity_metadata: RefreshSequencingContinuityMetadata
    lineage_visibility: RefreshSequencingLineageVisibility
    provenance_visibility: RefreshSequencingProvenanceVisibility
    replay_visibility: RefreshReplaySequencingVisibility
    rollback_visibility: RefreshRollbackSequencingVisibility
    drift_visibility: RefreshSequencingDriftVisibility
    blocked_state_visibility: RefreshSequencingBlockedStateVisibility
    unsupported_state_visibility: RefreshSequencingUnsupportedStateVisibility
    diagnostics: RefreshSequencingDiagnostics
    governance: RefreshSequencingGovernanceVisibility
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_ordering_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("ordering_nodes", "ordering_relationships"):
            _set_tuple_field(self, field_name)


def default_refresh_sequencing_identity() -> RefreshSequencingIdentity:
    return RefreshSequencingIdentity(
        sequencing_id="v4_1_refresh_sequencing_visibility_primary",
        refresh_cycle_id="v4_1_phase_5_refresh_sequencing_visibility",
        sequencing_version="v4.1.0-phase-5",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        source_schema_governance_reference="v4_1_schema_evolution_governance_primary",
        schema_version=V4_1_REFRESH_SEQUENCING_VISIBILITY_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_SEQUENCING_VISIBILITY_GENERATED_AT,
        sequencing_reference="v4_1_refresh_sequencing_visibility_sequence_primary",
        lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
        provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
        diagnostics_reference="v4_1_refresh_sequencing_visibility_diagnostics_primary",
        continuity_reference="v4_1_refresh_sequencing_visibility_continuity_primary",
        integrity_reference="v4_1_refresh_sequencing_visibility_integrity_primary",
        governance_reference="v4_1_refresh_sequencing_visibility_boundary_primary",
    )


def default_refresh_ordering_nodes() -> tuple[RefreshOrderingNode, ...]:
    return (
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_manifest",
            refresh_unit_id="refresh_manifest_foundations",
            dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
            schema_reference="v4_1.refresh_manifest.1",
            lineage_reference="v4_1_refresh_manifest_lineage_primary",
            provenance_reference="v4_1_refresh_manifest_provenance_primary",
            provider="operational_refresh",
            state=SEQUENCING_STATE_READY,
            reason="Manifest foundation ordering is visible and descriptive.",
            deterministic_order=10,
        ),
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_dependency_graph",
            refresh_unit_id="refresh_dependency_graph_infrastructure",
            dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
            schema_reference="v4_1.refresh_dependency_graph.1",
            lineage_reference="v4_1_refresh_dependency_graph_lineage_primary",
            provenance_reference="v4_1_refresh_dependency_graph_provenance_primary",
            provider="operational_refresh",
            state=SEQUENCING_STATE_READY,
            reason="Dependency graph ordering is visible and descriptive.",
            deterministic_order=20,
        ),
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_lineage",
            refresh_unit_id="refresh_lineage_certification",
            dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
            schema_reference="v4_1.refresh_lineage_certification.1",
            lineage_reference="v4_1_refresh_lineage_certification_lineage_primary",
            provenance_reference="v4_1_refresh_lineage_certification_provenance_primary",
            provider="operational_refresh",
            state=SEQUENCING_STATE_READY,
            reason="Lineage certification ordering is visible and descriptive.",
            deterministic_order=30,
        ),
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_schema_governance",
            refresh_unit_id="schema_evolution_governance",
            dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
            schema_reference="v4_1.schema_evolution_governance.1",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            provider="operational_refresh",
            state=SEQUENCING_STATE_READY,
            reason="Schema governance ordering is visible and descriptive.",
            deterministic_order=40,
        ),
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_future_provider",
            refresh_unit_id="future_refresh_sequence_provider",
            dependency_graph_reference="unsupported_future_dependency_graph",
            schema_reference="v4_1.future_refresh_sequence.unrecognized",
            lineage_reference="v4_1_future_sequence_lineage_unverified",
            provenance_reference="v4_1_future_sequence_provenance_unverified",
            provider="unsupported_future_sequencing_provider",
            state=SEQUENCING_STATE_UNSUPPORTED,
            reason="Future sequencing provider is unsupported and remains fail-visible.",
            deterministic_order=50,
            severity=SEQUENCING_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshOrderingNode(
            node_id="v4_1_sequence_node_prohibited_orchestration",
            refresh_unit_id="prohibited_orchestration_sequence",
            dependency_graph_reference="prohibited_orchestration_dependency_graph",
            schema_reference="v4_1.prohibited_orchestration_sequence",
            lineage_reference="v4_1_prohibited_orchestration_sequence_lineage",
            provenance_reference="v4_1_prohibited_orchestration_sequence_provenance",
            provider="prohibited_orchestration_provider",
            state=SEQUENCING_STATE_PROHIBITED,
            reason="Orchestration-capable sequencing provider is prohibited and visible.",
            deterministic_order=60,
            severity=SEQUENCING_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_refresh_ordering_relationships() -> tuple[RefreshOrderingRelationship, ...]:
    return (
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_manifest_before_dependency_graph",
            predecessor_node_id="v4_1_sequence_node_manifest",
            successor_node_id="v4_1_sequence_node_dependency_graph",
            dependency_reference="v4_1_dependency_manifest_to_graph",
            sequencing_reference="v4_1_refresh_sequencing_visibility_sequence_primary",
            lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
            provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
            ordering_classification="dependency_aware_visible",
            state=SEQUENCING_STATE_READY,
            reason="Manifest before dependency graph ordering is visible only.",
            deterministic_order=10,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_dependency_graph_before_lineage",
            predecessor_node_id="v4_1_sequence_node_dependency_graph",
            successor_node_id="v4_1_sequence_node_lineage",
            dependency_reference="v4_1_dependency_graph_to_lineage",
            sequencing_reference="v4_1_refresh_sequencing_visibility_sequence_primary",
            lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
            provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
            ordering_classification="dependency_aware_visible",
            state=SEQUENCING_STATE_READY,
            reason="Dependency graph before lineage ordering is visible only.",
            deterministic_order=20,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_lineage_before_schema",
            predecessor_node_id="v4_1_sequence_node_lineage",
            successor_node_id="v4_1_sequence_node_schema_governance",
            dependency_reference="v4_1_dependency_lineage_to_schema",
            sequencing_reference="v4_1_refresh_sequencing_visibility_sequence_primary",
            lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
            provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
            ordering_classification="dependency_aware_visible_with_warning",
            state=SEQUENCING_STATE_READY_WITH_WARNINGS,
            reason="Lineage before schema governance ordering is visible with governance warning.",
            deterministic_order=30,
            severity=SEQUENCING_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_future_provider_unsupported",
            predecessor_node_id="v4_1_sequence_node_schema_governance",
            successor_node_id="v4_1_sequence_node_future_provider",
            dependency_reference="unsupported_future_dependency",
            sequencing_reference="v4_1_future_sequence_unverified",
            lineage_reference="v4_1_future_sequence_lineage_unverified",
            provenance_reference="v4_1_future_sequence_provenance_unverified",
            ordering_classification="unsupported_provider",
            state=SEQUENCING_STATE_UNSUPPORTED,
            reason="Future sequencing provider cannot be governed silently.",
            deterministic_order=40,
            severity=SEQUENCING_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_stale_schema_chain",
            predecessor_node_id="v4_1_sequence_node_manifest",
            successor_node_id="v4_1_sequence_node_schema_governance",
            dependency_reference="stale_schema_dependency_reference",
            sequencing_reference="v4_1_stale_sequence_reference",
            lineage_reference="v4_1_stale_sequence_lineage",
            provenance_reference="v4_1_stale_sequence_provenance",
            ordering_classification="stale_ordering_visibility",
            state=SEQUENCING_STATE_STALE,
            reason="Stale sequencing chain is visible and not corrected.",
            deterministic_order=50,
            severity=SEQUENCING_SEVERITY_WARNING,
            fail_visible=True,
            drift_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_sequencing_discontinuity",
            predecessor_node_id="v4_1_sequence_node_dependency_graph",
            successor_node_id="v4_1_sequence_node_schema_governance",
            dependency_reference="sequencing_gap_dependency_reference",
            sequencing_reference="v4_1_sequencing_gap_reference",
            lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
            provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
            ordering_classification="sequencing_gap",
            state=SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
            reason="Sequencing continuity gap is visible and not repaired.",
            deterministic_order=60,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_dependency_ordering_discontinuity",
            predecessor_node_id="v4_1_sequence_node_schema_governance",
            successor_node_id="v4_1_sequence_node_manifest",
            dependency_reference="dependency_ordering_gap_reference",
            sequencing_reference="v4_1_dependency_ordering_gap_sequence",
            lineage_reference="v4_1_dependency_ordering_gap_lineage",
            provenance_reference="v4_1_dependency_ordering_gap_provenance",
            ordering_classification="dependency_ordering_gap",
            state=SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
            reason="Dependency ordering discontinuity is visible and not resolved.",
            deterministic_order=70,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_lineage_discontinuity",
            predecessor_node_id="v4_1_sequence_node_manifest",
            successor_node_id="v4_1_sequence_node_future_provider",
            dependency_reference="lineage_gap_dependency_reference",
            sequencing_reference="v4_1_lineage_gap_sequence",
            lineage_reference="v4_1_sequence_lineage_gap_reference",
            provenance_reference="v4_1_refresh_sequencing_visibility_provenance_primary",
            ordering_classification="lineage_gap",
            state=SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
            reason="Sequencing lineage gap is visible and not inferred.",
            deterministic_order=80,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_provenance_discontinuity",
            predecessor_node_id="v4_1_sequence_node_dependency_graph",
            successor_node_id="v4_1_sequence_node_future_provider",
            dependency_reference="provenance_gap_dependency_reference",
            sequencing_reference="v4_1_provenance_gap_sequence",
            lineage_reference="v4_1_refresh_sequencing_visibility_lineage_primary",
            provenance_reference="v4_1_sequence_provenance_gap_reference",
            ordering_classification="provenance_gap",
            state=SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
            reason="Sequencing provenance gap is visible and not inferred.",
            deterministic_order=90,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_replay_discontinuity",
            predecessor_node_id="v4_1_sequence_node_lineage",
            successor_node_id="v4_1_sequence_node_future_provider",
            dependency_reference="replay_gap_dependency_reference",
            sequencing_reference="v4_1_replay_gap_sequence",
            lineage_reference="v4_1_replay_gap_lineage",
            provenance_reference="v4_1_replay_gap_provenance",
            ordering_classification="replay_gap",
            state=SEQUENCING_STATE_REPLAY_DISCONTINUITY,
            reason="Replay sequencing gap is visible and not executed.",
            deterministic_order=100,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_rollback_discontinuity",
            predecessor_node_id="v4_1_sequence_node_lineage",
            successor_node_id="v4_1_sequence_node_schema_governance",
            dependency_reference="rollback_gap_dependency_reference",
            sequencing_reference="v4_1_rollback_gap_sequence",
            lineage_reference="v4_1_rollback_gap_lineage",
            provenance_reference="v4_1_rollback_gap_provenance",
            ordering_classification="rollback_gap",
            state=SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
            reason="Rollback sequencing gap is visible and not recovered.",
            deterministic_order=110,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_circular_visibility",
            predecessor_node_id="v4_1_sequence_node_schema_governance",
            successor_node_id="v4_1_sequence_node_dependency_graph",
            dependency_reference="circular_sequence_dependency_reference",
            sequencing_reference="v4_1_circular_sequence_reference",
            lineage_reference="v4_1_circular_sequence_lineage",
            provenance_reference="v4_1_circular_sequence_provenance",
            ordering_classification="circular_sequencing_visibility",
            state=SEQUENCING_STATE_CIRCULAR,
            reason="Circular sequencing is visible and not traversed.",
            deterministic_order=120,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
            circular_sequencing_visibility=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_prohibited_orchestration",
            predecessor_node_id="v4_1_sequence_node_schema_governance",
            successor_node_id="v4_1_sequence_node_prohibited_orchestration",
            dependency_reference="prohibited_orchestration_dependency_reference",
            sequencing_reference="v4_1_prohibited_orchestration_sequence",
            lineage_reference="v4_1_prohibited_orchestration_lineage",
            provenance_reference="v4_1_prohibited_orchestration_provenance",
            ordering_classification="prohibited_orchestration_execution",
            state=SEQUENCING_STATE_PROHIBITED,
            reason="Orchestration execution path is prohibited and remains visible.",
            deterministic_order=130,
            severity=SEQUENCING_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
        RefreshOrderingRelationship(
            relationship_id="v4_1_sequence_blocked_ordering_state",
            predecessor_node_id="v4_1_sequence_node_future_provider",
            successor_node_id="v4_1_sequence_node_schema_governance",
            dependency_reference="blocked_ordering_dependency_reference",
            sequencing_reference="v4_1_blocked_ordering_sequence",
            lineage_reference="v4_1_blocked_ordering_lineage",
            provenance_reference="v4_1_blocked_ordering_provenance",
            ordering_classification="blocked_unknown_ordering",
            state=SEQUENCING_STATE_BLOCKED,
            reason="Unknown ordering is blocked and not corrected.",
            deterministic_order=140,
            severity=SEQUENCING_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
    )


def default_refresh_sequencing_visibility() -> RefreshSequencingVisibility:
    identity = default_refresh_sequencing_identity()
    nodes = default_refresh_ordering_nodes()
    relationships = default_refresh_ordering_relationships()
    return RefreshSequencingVisibility(
        identity=identity,
        ordering_nodes=nodes,
        ordering_relationships=relationships,
        dependency_aware_visibility=DependencyAwareSequencingVisibility(
            visibility_id="v4_1_dependency_aware_sequencing_visibility_primary",
            dependency_ordering_references=tuple(relationship.dependency_reference for relationship in relationships),
            ready_relationship_ids=(
                "v4_1_sequence_manifest_before_dependency_graph",
                "v4_1_sequence_dependency_graph_before_lineage",
            ),
            warning_relationship_ids=("v4_1_sequence_lineage_before_schema",),
            blocked_relationship_ids=("v4_1_sequence_blocked_ordering_state",),
            unsupported_relationship_ids=("v4_1_sequence_future_provider_unsupported",),
            stale_relationship_ids=("v4_1_sequence_stale_schema_chain",),
            prohibited_relationship_ids=("v4_1_sequence_prohibited_orchestration",),
            circular_relationship_ids=("v4_1_sequence_circular_visibility",),
            sequencing_discontinuity_ids=("v4_1_sequence_sequencing_discontinuity",),
            dependency_ordering_discontinuity_ids=("v4_1_sequence_dependency_ordering_discontinuity",),
            deterministic_order=10,
        ),
        continuity_metadata=RefreshSequencingContinuityMetadata(
            continuity_id="v4_1_refresh_sequencing_continuity_primary",
            sequencing_continuity_references=(identity.sequencing_reference,),
            dependency_ordering_references=("v4_1_dependency_aware_sequencing_visibility_primary",),
            lineage_continuity_references=(identity.lineage_reference,),
            provenance_continuity_references=(identity.provenance_reference,),
            replay_sequencing_references=("v4_1_refresh_replay_sequencing_visibility_primary",),
            rollback_sequencing_references=("v4_1_refresh_rollback_sequencing_visibility_primary",),
            deterministic_order=20,
        ),
        lineage_visibility=RefreshSequencingLineageVisibility(
            lineage_id=identity.lineage_reference,
            lineage_references=(
                "v4_1_refresh_manifest_lineage_primary",
                "v4_1_refresh_dependency_graph_lineage_primary",
                "v4_1_refresh_lineage_certification_lineage_primary",
                "v4_1_schema_evolution_governance_lineage_primary",
                identity.lineage_reference,
            ),
            lineage_discontinuity_visibility=("v4_1_sequence_lineage_discontinuity",),
            deterministic_order=30,
        ),
        provenance_visibility=RefreshSequencingProvenanceVisibility(
            provenance_id=identity.provenance_reference,
            provenance_references=(
                "v4_1_refresh_manifest_provenance_primary",
                "v4_1_refresh_dependency_graph_provenance_primary",
                "v4_1_refresh_lineage_certification_provenance_primary",
                "v4_1_schema_evolution_governance_provenance_primary",
                identity.provenance_reference,
            ),
            inherited_from_references=(
                "v4_1_refresh_manifest_primary",
                "v4_1_refresh_dependency_graph_primary",
                "v4_1_refresh_lineage_certification_primary",
                "v4_1_schema_evolution_governance_primary",
            ),
            provenance_discontinuity_visibility=("v4_1_sequence_provenance_discontinuity",),
            deterministic_order=40,
        ),
        replay_visibility=RefreshReplaySequencingVisibility(
            replay_id="v4_1_refresh_replay_sequencing_visibility_primary",
            replay_sequencing_references=("v4_1_refresh_replay_sequence_evidence_primary",),
            replay_discontinuity_visibility=("v4_1_sequence_replay_discontinuity",),
            deterministic_order=50,
        ),
        rollback_visibility=RefreshRollbackSequencingVisibility(
            rollback_id="v4_1_refresh_rollback_sequencing_visibility_primary",
            rollback_sequencing_references=("v4_1_refresh_rollback_sequence_evidence_primary",),
            rollback_discontinuity_visibility=("v4_1_sequence_rollback_discontinuity",),
            deterministic_order=60,
        ),
        drift_visibility=RefreshSequencingDriftVisibility(
            drift_id="v4_1_refresh_sequencing_drift_visibility_primary",
            stale_relationship_ids=("v4_1_sequence_stale_schema_chain",),
            sequencing_drift_references=("v4_1_sequence_stale_schema_chain",),
            dependency_ordering_drift_references=("v4_1_sequence_dependency_ordering_discontinuity",),
            deterministic_order=70,
        ),
        blocked_state_visibility=RefreshSequencingBlockedStateVisibility(
            blocked_id="v4_1_refresh_sequencing_blocked_state_visibility_primary",
            blocked_relationship_ids=("v4_1_sequence_blocked_ordering_state",),
            blocked_ordering_states=("blocked_unknown_ordering",),
            sequencing_discontinuity_visibility=("v4_1_sequence_sequencing_discontinuity",),
            dependency_ordering_discontinuity_visibility=("v4_1_sequence_dependency_ordering_discontinuity",),
            lineage_discontinuity_visibility=("v4_1_sequence_lineage_discontinuity",),
            provenance_discontinuity_visibility=("v4_1_sequence_provenance_discontinuity",),
            replay_discontinuity_visibility=("v4_1_sequence_replay_discontinuity",),
            rollback_discontinuity_visibility=("v4_1_sequence_rollback_discontinuity",),
            circular_sequencing_visibility=("v4_1_sequence_circular_visibility",),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("refresh_execution", "implicit_execution_pathways"),
            prohibited_remediation_leakage=("remediation_systems",),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=80,
        ),
        unsupported_state_visibility=RefreshSequencingUnsupportedStateVisibility(
            unsupported_id="v4_1_refresh_sequencing_unsupported_state_visibility_primary",
            unsupported_node_ids=("v4_1_sequence_node_future_provider",),
            unsupported_relationship_ids=("v4_1_sequence_future_provider_unsupported",),
            unsupported_sequencing_providers=("unsupported_future_sequencing_provider",),
            stale_relationship_ids=("v4_1_sequence_stale_schema_chain",),
            prohibited_relationship_ids=("v4_1_sequence_prohibited_orchestration",),
            prohibited_sequencing_domains=PROHIBITED_SEQUENCING_DOMAINS,
            failure_visibility=(
                "unsupported sequencing provider remains fail-visible",
                "blocked ordering state remains fail-visible",
                "circular sequencing remains fail-visible",
                "dependency ordering discontinuity remains fail-visible",
            ),
            deterministic_order=90,
        ),
        diagnostics=RefreshSequencingDiagnostics(
            diagnostics_id="v4_1_refresh_sequencing_diagnostics_primary",
            diagnostic_references=(
                "v4_1_dependency_aware_sequencing_visibility_primary",
                "v4_1_refresh_sequencing_blocked_state_visibility_primary",
                "v4_1_refresh_sequencing_unsupported_state_visibility_primary",
            ),
            warning_visibility=(
                "v4_1_sequence_lineage_before_schema",
                "v4_1_sequence_future_provider_unsupported",
                "v4_1_sequence_stale_schema_chain",
            ),
            blocker_visibility=(
                "v4_1_sequence_blocked_ordering_state",
                "v4_1_sequence_sequencing_discontinuity",
                "v4_1_sequence_dependency_ordering_discontinuity",
            ),
            unsupported_sequencing_visibility=("v4_1_sequence_future_provider_unsupported",),
            prohibited_sequencing_visibility=("v4_1_sequence_prohibited_orchestration",),
            circular_sequencing_visibility=("v4_1_sequence_circular_visibility",),
            drift_visibility=("v4_1_refresh_sequencing_drift_visibility_primary",),
            integrity_visibility=("v4_1_refresh_sequencing_integrity_primary",),
            deterministic_order=100,
        ),
        governance=RefreshSequencingGovernanceVisibility(
            governance_id=identity.governance_reference,
            governance_references=(
                identity.governance_reference,
                "v4_1_refresh_sequencing_visibility_boundary_primary",
            ),
            explicit_limitations=EXPLICIT_REFRESH_SEQUENCING_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_REFRESH_SEQUENCING_PROHIBITIONS,
            deterministic_order=110,
        ),
    )
