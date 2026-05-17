"""Deterministic v4.1 refresh lineage certification models.

Refresh lineage certification is descriptive governance evidence only. It does
not execute refreshes, orchestrate work, migrate schemas, repair lineage,
correct continuity, consume production bundles, integrate with planners,
authorize behavior, remediate blockers, recover state, roll back state, or
mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_LINEAGE_CERTIFICATION_PHASE_ID = "v4_1_refresh_lineage_certification"
V4_1_REFRESH_LINEAGE_CERTIFICATION_SCHEMA_VERSION = "v4_1.refresh_lineage_certification.1"
V4_1_REFRESH_LINEAGE_CERTIFICATION_REPORT_SCHEMA_VERSION = "v4_1.refresh_lineage_certification_report.1"
V4_1_REFRESH_LINEAGE_CERTIFICATION_DIAGNOSTICS_SCHEMA_VERSION = "v4_1.refresh_lineage_certification_diagnostics_report.1"
V4_1_REFRESH_LINEAGE_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_lineage_continuity_report.1"
V4_1_REFRESH_LINEAGE_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_lineage_integrity_report.1"
V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE = "v4_1_refresh_lineage_certification_stable"
V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_BLOCKED = "v4_1_refresh_lineage_certification_blocked"
V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_LINEAGE_CERTIFICATION_PURPOSE = "deterministic_refresh_lineage_certification_governance_only"

LINEAGE_STATE_SUPPORTED = "supported"
LINEAGE_STATE_BLOCKED = "blocked"
LINEAGE_STATE_UNSUPPORTED = "unsupported"
LINEAGE_STATE_STALE = "stale"
LINEAGE_STATE_PROHIBITED = "prohibited"
LINEAGE_STATE_CIRCULAR_ANCESTRY = "circular_ancestry"
LINEAGE_STATE_LINEAGE_DISCONTINUITY = "lineage_discontinuity"
LINEAGE_STATE_PROVENANCE_DISCONTINUITY = "provenance_discontinuity"
LINEAGE_STATE_SCHEMA_DISCONTINUITY = "schema_discontinuity"
LINEAGE_STATES: tuple[str, ...] = (
    LINEAGE_STATE_SUPPORTED,
    LINEAGE_STATE_BLOCKED,
    LINEAGE_STATE_UNSUPPORTED,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_PROHIBITED,
    LINEAGE_STATE_CIRCULAR_ANCESTRY,
    LINEAGE_STATE_LINEAGE_DISCONTINUITY,
    LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
    LINEAGE_STATE_SCHEMA_DISCONTINUITY,
)
FAIL_VISIBLE_LINEAGE_STATES: tuple[str, ...] = (
    LINEAGE_STATE_BLOCKED,
    LINEAGE_STATE_UNSUPPORTED,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_PROHIBITED,
    LINEAGE_STATE_CIRCULAR_ANCESTRY,
    LINEAGE_STATE_LINEAGE_DISCONTINUITY,
    LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
    LINEAGE_STATE_SCHEMA_DISCONTINUITY,
)

LINEAGE_SEVERITY_INFO = "info"
LINEAGE_SEVERITY_WARNING = "warning"
LINEAGE_SEVERITY_BLOCKED = "blocked"
LINEAGE_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_LINEAGE_DOMAINS: tuple[str, ...] = (
    "refresh_execution",
    "orchestration_execution",
    "migration_execution",
    "automatic_lineage_repair",
    "automatic_continuity_correction",
    "automatic_schema_migration",
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

EXPLICIT_LINEAGE_CERTIFICATION_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 3 creates deterministic refresh lineage certification metadata only.",
    "v4.1 Phase 3 does not enable refresh execution.",
    "v4.1 Phase 3 does not enable orchestration.",
    "v4.1 Phase 3 does not enable migration execution.",
    "v4.1 Phase 3 does not enable automatic repair.",
    "v4.1 Phase 3 does not enable automatic continuity correction.",
    "v4.1 Phase 3 does not enable planner integration.",
    "v4.1 Phase 3 does not enable production consumption.",
    "v4.1 Phase 3 does not enable remediation.",
    "v4.1 Phase 3 does not enable mutation behavior.",
)

EXPLICIT_LINEAGE_CERTIFICATION_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No automatic repair exists.",
    "No automatic continuity correction exists.",
    "No automatic schema migration exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No mutation behavior exists.",
    "No silent continuity correction behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshLineageIdentity:
    certification_id: str
    refresh_cycle_id: str
    certification_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    schema_version: str
    generated_at: str
    lineage_reference: str
    ancestry_reference: str
    provenance_reference: str
    diagnostics_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    certification_scope: str = "refresh_lineage_identity_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_LINEAGE_CERTIFICATION_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    migration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshAncestryNode:
    node_id: str
    generation_id: str
    parent_generation_id: str
    manifest_reference: str
    dependency_graph_reference: str
    schema_reference: str
    lineage_reference: str
    provenance_reference: str
    state: str
    reason: str
    deterministic_order: int
    severity: str = LINEAGE_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    refresh_execution_enabled: bool = False
    migration_execution_enabled: bool = False
    automatic_lineage_repair_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_correction_enabled: bool = False


@dataclass(frozen=True)
class RefreshAncestryLink:
    link_id: str
    parent_node_id: str
    child_node_id: str
    relationship_state: str
    relationship_type: str
    reason: str
    lineage_reference: str
    provenance_reference: str
    deterministic_order: int
    severity: str = LINEAGE_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    circular_ancestry_visibility: bool = False
    drift_visible: bool = False
    hidden: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    migration_execution_enabled: bool = False
    automatic_lineage_repair_enabled: bool = False
    automatic_continuity_correction_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    remediation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_correction_enabled: bool = False


@dataclass(frozen=True)
class RefreshProvenanceInheritance:
    inheritance_id: str
    inherited_from_references: tuple[str, ...]
    inherited_to_reference: str
    source_evidence_references: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    provenance_inherited: bool = True
    provenance_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    inferred_provenance_allowed: bool = False
    hidden_provenance_resolution_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "inherited_from_references",
            "source_evidence_references",
            "provenance_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshEvolutionVisibility:
    evolution_id: str
    parent_child_lineage_visibility: tuple[str, ...]
    schema_transition_visibility: tuple[str, ...]
    ancestry_discontinuity_visibility: tuple[str, ...]
    stale_lineage_visibility: tuple[str, ...]
    drift_visibility: tuple[str, ...]
    deterministic_order: int
    evolution_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_migration_enabled: bool = False
    automatic_lineage_repair_enabled: bool = False
    hidden_evolution_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "parent_child_lineage_visibility",
            "schema_transition_visibility",
            "ancestry_discontinuity_visibility",
            "stale_lineage_visibility",
            "drift_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageContinuityMetadata:
    continuity_id: str
    ancestry_continuity_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    schema_transition_references: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    continuity_preserved: bool = True
    ancestry_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    replay_lineage_preserved: bool = True
    rollback_lineage_preserved: bool = True
    schema_transition_continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    automatic_continuity_correction_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "ancestry_continuity_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_lineage_references",
            "rollback_lineage_references",
            "schema_transition_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshReplayLineageVisibility:
    replay_id: str
    replay_lineage_references: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    replay_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    live_replay_enabled: bool = False
    refresh_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_lineage_references", "replay_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshRollbackLineageVisibility:
    rollback_id: str
    rollback_lineage_references: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    deterministic_hash_reference: str
    deterministic_order: int
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    recovery_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_lineage_references", "rollback_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshSchemaTransitionContinuity:
    schema_transition_id: str
    source_schema_reference: str
    target_schema_reference: str
    schema_transition_visibility: tuple[str, ...]
    schema_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    schema_transition_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_schema_migration_enabled: bool = False
    migration_execution_enabled: bool = False
    hidden_schema_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("schema_transition_visibility", "schema_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageBlockedStateVisibility:
    blocked_visibility_id: str
    blocked_lineage_links: tuple[str, ...]
    circular_ancestry_links: tuple[str, ...]
    ancestry_discontinuity_visibility: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    schema_discontinuity_visibility: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_migration_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    silent_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_lineage_links",
            "circular_ancestry_links",
            "ancestry_discontinuity_visibility",
            "lineage_discontinuity_visibility",
            "provenance_discontinuity_visibility",
            "replay_discontinuity_visibility",
            "rollback_discontinuity_visibility",
            "schema_discontinuity_visibility",
            "prohibited_execution_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_remediation_leakage",
            "prohibited_migration_leakage",
            "prohibited_planner_integration_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageUnsupportedStateVisibility:
    unsupported_visibility_id: str
    unsupported_lineage_nodes: tuple[str, ...]
    unsupported_lineage_links: tuple[str, ...]
    unsupported_lineage_providers: tuple[str, ...]
    stale_lineage_links: tuple[str, ...]
    prohibited_lineage_links: tuple[str, ...]
    prohibited_lineage_domains: tuple[str, ...]
    failure_visibility: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_lineage_repair_enabled: bool = False
    hidden_unsupported_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_lineage_nodes",
            "unsupported_lineage_links",
            "unsupported_lineage_providers",
            "stale_lineage_links",
            "prohibited_lineage_links",
            "prohibited_lineage_domains",
            "failure_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageDriftVisibility:
    drift_id: str
    stale_lineage_references: tuple[str, ...]
    changed_schema_references: tuple[str, ...]
    lineage_drift_references: tuple[str, ...]
    deterministic_order: int
    drift_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_migration_enabled: bool = False
    automatic_continuity_correction_enabled: bool = False
    hidden_drift_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("stale_lineage_references", "changed_schema_references", "lineage_drift_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageDiagnostics:
    diagnostics_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    circular_ancestry_visibility: tuple[str, ...]
    unsupported_lineage_visibility: tuple[str, ...]
    prohibited_lineage_visibility: tuple[str, ...]
    drift_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_recovery_enabled: bool = False
    silent_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "circular_ancestry_visibility",
            "unsupported_lineage_visibility",
            "prohibited_lineage_visibility",
            "drift_visibility",
            "integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshLineageGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_visible: bool = True
    descriptive_only: bool = True
    execution_authorized: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    migration_execution_enabled: bool = False
    automatic_repair_enabled: bool = False
    automatic_continuity_correction_enabled: bool = False
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
class RefreshLineageCertification:
    identity: RefreshLineageIdentity
    ancestry_nodes: tuple[RefreshAncestryNode, ...]
    ancestry_links: tuple[RefreshAncestryLink, ...]
    provenance_inheritance: tuple[RefreshProvenanceInheritance, ...]
    evolution_visibility: RefreshEvolutionVisibility
    continuity_metadata: RefreshLineageContinuityMetadata
    replay_lineage_visibility: RefreshReplayLineageVisibility
    rollback_lineage_visibility: RefreshRollbackLineageVisibility
    schema_transition_continuity: RefreshSchemaTransitionContinuity
    blocked_state_visibility: RefreshLineageBlockedStateVisibility
    unsupported_state_visibility: RefreshLineageUnsupportedStateVisibility
    drift_visibility: RefreshLineageDriftVisibility
    diagnostics: RefreshLineageDiagnostics
    governance: RefreshLineageGovernance
    certification_scope: str = V4_1_REFRESH_LINEAGE_CERTIFICATION_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    migration_execution_enabled: bool = False
    automatic_lineage_repair_enabled: bool = False
    automatic_continuity_correction_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
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
    silent_continuity_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("ancestry_nodes", "ancestry_links", "provenance_inheritance"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def default_lineage_identity() -> RefreshLineageIdentity:
    return RefreshLineageIdentity(
        certification_id="v4_1_refresh_lineage_certification_primary",
        refresh_cycle_id="v4_1_phase_3_refresh_lineage_certification",
        certification_version="v4.1.0-phase-3",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        schema_version=V4_1_REFRESH_LINEAGE_CERTIFICATION_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_LINEAGE_CERTIFICATION_GENERATED_AT,
        lineage_reference="v4_1_refresh_lineage_certification_lineage_primary",
        ancestry_reference="v4_1_refresh_lineage_certification_ancestry_primary",
        provenance_reference="v4_1_refresh_lineage_certification_provenance_primary",
        diagnostics_reference="v4_1_refresh_lineage_certification_diagnostics_primary",
        continuity_reference="v4_1_refresh_lineage_certification_continuity_primary",
        integrity_reference="v4_1_refresh_lineage_certification_integrity_primary",
        governance_reference="v4_1_refresh_lineage_certification_governance_primary",
    )


def default_ancestry_nodes(identity: RefreshLineageIdentity | None = None) -> tuple[RefreshAncestryNode, ...]:
    source = identity or default_lineage_identity()
    return (
        RefreshAncestryNode(
            node_id="v4_1_lineage_node_v4_0_closeout",
            generation_id="v4_0_closeout_generation",
            parent_generation_id="v3_9_transition_generation",
            manifest_reference="v4_0_closeout_and_v4_1_readiness_report",
            dependency_graph_reference="v4_0_operational_lifecycle_governance",
            schema_reference="v4_0.closeout_and_v4_1_readiness_report.1",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=LINEAGE_STATE_SUPPORTED,
            reason="v4.0 closeout generation anchors v4.1 refresh lineage certification",
            deterministic_order=1,
        ),
        RefreshAncestryNode(
            node_id="v4_1_lineage_node_refresh_manifest",
            generation_id="v4_1_refresh_manifest_generation",
            parent_generation_id="v4_0_closeout_generation",
            manifest_reference=source.source_manifest_reference,
            dependency_graph_reference="v4_1_refresh_manifest_foundations",
            schema_reference="v4_1.refresh_manifest_foundations.1",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=LINEAGE_STATE_SUPPORTED,
            reason="phase 1 refresh manifest generation is deterministic governance evidence",
            deterministic_order=2,
        ),
        RefreshAncestryNode(
            node_id="v4_1_lineage_node_dependency_graph",
            generation_id="v4_1_refresh_dependency_graph_generation",
            parent_generation_id="v4_1_refresh_manifest_generation",
            manifest_reference="v4_1_refresh_dependency_graph_primary",
            dependency_graph_reference=source.source_dependency_graph_reference,
            schema_reference="v4_1.refresh_dependency_graph_infrastructure.1",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=LINEAGE_STATE_SUPPORTED,
            reason="phase 2 dependency graph generation is deterministic governance evidence",
            deterministic_order=3,
        ),
        RefreshAncestryNode(
            node_id="v4_1_lineage_node_future_refresh_generation",
            generation_id="future_refresh_generation",
            parent_generation_id="v4_1_refresh_dependency_graph_generation",
            manifest_reference="future_refresh_generation_manifest",
            dependency_graph_reference="future_refresh_dependency_graph_not_declared",
            schema_reference="future.refresh_lineage.schema.unknown",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=LINEAGE_STATE_UNSUPPORTED,
            reason="future refresh generation provider is not declared in phase 3",
            deterministic_order=4,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshAncestryNode(
            node_id="v4_1_lineage_node_prohibited_migration",
            generation_id="prohibited_migration_generation",
            parent_generation_id="v4_1_refresh_dependency_graph_generation",
            manifest_reference="runtime_migration_source",
            dependency_graph_reference="production_runtime_migration_dependency",
            schema_reference="runtime.migration.prohibited",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            state=LINEAGE_STATE_PROHIBITED,
            reason="runtime migration lineage is prohibited for certification",
            deterministic_order=5,
            severity=LINEAGE_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_ancestry_links(identity: RefreshLineageIdentity | None = None) -> tuple[RefreshAncestryLink, ...]:
    source = identity or default_lineage_identity()
    return (
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_closeout_to_manifest",
            parent_node_id="v4_1_lineage_node_v4_0_closeout",
            child_node_id="v4_1_lineage_node_refresh_manifest",
            relationship_state=LINEAGE_STATE_SUPPORTED,
            relationship_type="parent_child_lineage",
            reason="v4.1 manifest lineage descends from v4.0 closeout evidence",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=1,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_manifest_to_dependency_graph",
            parent_node_id="v4_1_lineage_node_refresh_manifest",
            child_node_id="v4_1_lineage_node_dependency_graph",
            relationship_state=LINEAGE_STATE_SUPPORTED,
            relationship_type="parent_child_lineage",
            reason="v4.1 dependency graph lineage descends from v4.1 manifest evidence",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=2,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_future_generation_unsupported",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_future_refresh_generation",
            relationship_state=LINEAGE_STATE_UNSUPPORTED,
            relationship_type="future_generation_provider",
            reason="future refresh generation lineage provider is unsupported and fail-visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=3,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_future_generation_circular_visibility",
            parent_node_id="v4_1_lineage_node_future_refresh_generation",
            child_node_id="v4_1_lineage_node_refresh_manifest",
            relationship_state=LINEAGE_STATE_CIRCULAR_ANCESTRY,
            relationship_type="circular_ancestry_visibility",
            reason="potential future-generation circular ancestry is visible and not repaired",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=4,
            severity=LINEAGE_SEVERITY_BLOCKED,
            fail_visible=True,
            circular_ancestry_visibility=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_stale_schema_transition",
            parent_node_id="v4_1_lineage_node_v4_0_closeout",
            child_node_id="v4_1_lineage_node_dependency_graph",
            relationship_state=LINEAGE_STATE_STALE,
            relationship_type="schema_transition_lineage",
            reason="v4.0 to v4.1 schema transition remains stale descriptive evidence",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=5,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
            drift_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_future_ancestry_gap",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_future_refresh_generation",
            relationship_state=LINEAGE_STATE_LINEAGE_DISCONTINUITY,
            relationship_type="ancestry_gap_visibility",
            reason="future generation ancestry continuity is not declared and remains visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=6,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_future_provenance_gap",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_future_refresh_generation",
            relationship_state=LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
            relationship_type="provenance_gap_visibility",
            reason="future generation provenance inheritance is not declared and remains visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=7,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_schema_discontinuity_visibility",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_future_refresh_generation",
            relationship_state=LINEAGE_STATE_SCHEMA_DISCONTINUITY,
            relationship_type="schema_discontinuity_visibility",
            reason="future schema transition is not declared and remains visible",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=8,
            severity=LINEAGE_SEVERITY_WARNING,
            fail_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_prohibited_migration",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_prohibited_migration",
            relationship_state=LINEAGE_STATE_PROHIBITED,
            relationship_type="prohibited_migration_lineage",
            reason="migration execution lineage is prohibited and not invoked",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=9,
            severity=LINEAGE_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
        RefreshAncestryLink(
            link_id="v4_1_lineage_link_blocked_continuity_gap",
            parent_node_id="v4_1_lineage_node_dependency_graph",
            child_node_id="v4_1_lineage_node_future_refresh_generation",
            relationship_state=LINEAGE_STATE_BLOCKED,
            relationship_type="blocked_continuity_gap",
            reason="future refresh continuity certification target is not declared",
            lineage_reference=source.lineage_reference,
            provenance_reference=source.provenance_reference,
            deterministic_order=10,
            severity=LINEAGE_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
    )


def default_provenance_inheritance(identity: RefreshLineageIdentity | None = None) -> RefreshProvenanceInheritance:
    source = identity or default_lineage_identity()
    return RefreshProvenanceInheritance(
        inheritance_id="v4_1_refresh_lineage_provenance_inheritance_primary",
        inherited_from_references=(
            "v4_0_closeout_and_v4_1_readiness_report",
            "v4_1_refresh_manifest_foundations_report",
            "v4_1_refresh_dependency_graph_report",
        ),
        inherited_to_reference=source.provenance_reference,
        source_evidence_references=(
            "docs/generated/v4_1_refresh_manifest_foundations_report.json",
            "docs/generated/v4_1_refresh_dependency_graph_report.json",
            "docs/migration/V4_1_REFRESH_DEPENDENCY_GRAPH_INFRASTRUCTURE.md",
        ),
        provenance_discontinuity_visibility=("v4_1_future_generation_provenance_not_declared",),
        deterministic_order=1,
    )


def default_evolution_visibility(links: tuple[RefreshAncestryLink, ...] | None = None) -> RefreshEvolutionVisibility:
    ancestry_links = links or default_ancestry_links()
    return RefreshEvolutionVisibility(
        evolution_id="v4_1_refresh_lineage_evolution_visibility_primary",
        parent_child_lineage_visibility=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_SUPPORTED),
        schema_transition_visibility=("v4_0_to_v4_1_schema_transition_descriptive_only",),
        ancestry_discontinuity_visibility=tuple(
            link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_LINEAGE_DISCONTINUITY
        ),
        stale_lineage_visibility=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_STALE),
        drift_visibility=("future_refresh_generation_drift_not_declared",),
        deterministic_order=1,
    )


def default_continuity_metadata(identity: RefreshLineageIdentity | None = None) -> RefreshLineageContinuityMetadata:
    source = identity or default_lineage_identity()
    return RefreshLineageContinuityMetadata(
        continuity_id=source.continuity_reference,
        ancestry_continuity_references=(source.ancestry_reference, "v4_1_refresh_lineage_ancestry_chain_primary"),
        lineage_continuity_references=(source.lineage_reference, "v4_1_refresh_dependency_graph_lineage_primary"),
        provenance_continuity_references=(source.provenance_reference, "v4_1_refresh_lineage_provenance_inheritance_primary"),
        replay_lineage_references=("v4_1_refresh_lineage_replay_primary",),
        rollback_lineage_references=("v4_1_refresh_lineage_rollback_primary",),
        schema_transition_references=("v4_1_refresh_lineage_schema_transition_primary",),
        deterministic_hash_reference="v4_1_refresh_lineage_continuity_hash",
        deterministic_order=1,
    )


def default_replay_lineage_visibility() -> RefreshReplayLineageVisibility:
    return RefreshReplayLineageVisibility(
        replay_id="v4_1_refresh_lineage_replay_primary",
        replay_lineage_references=(
            "v4_1_refresh_lineage_certification_serialization_snapshot",
            "v4_1_refresh_lineage_certification_hash_snapshot",
        ),
        replay_discontinuity_visibility=("future_refresh_lineage_replay_source_not_declared",),
        deterministic_hash_reference="v4_1_refresh_lineage_replay_hash",
        deterministic_order=1,
    )


def default_rollback_lineage_visibility() -> RefreshRollbackLineageVisibility:
    return RefreshRollbackLineageVisibility(
        rollback_id="v4_1_refresh_lineage_rollback_primary",
        rollback_lineage_references=(
            "docs/generated/v4_1_refresh_dependency_graph_report.json",
            "docs/generated/v4_1_refresh_manifest_foundations_report.json",
        ),
        rollback_discontinuity_visibility=("future_refresh_lineage_rollback_target_not_declared",),
        deterministic_hash_reference="v4_1_refresh_lineage_rollback_hash",
        deterministic_order=1,
    )


def default_schema_transition_continuity() -> RefreshSchemaTransitionContinuity:
    return RefreshSchemaTransitionContinuity(
        schema_transition_id="v4_1_refresh_lineage_schema_transition_primary",
        source_schema_reference="v4_1.refresh_dependency_graph_infrastructure.1",
        target_schema_reference=V4_1_REFRESH_LINEAGE_CERTIFICATION_SCHEMA_VERSION,
        schema_transition_visibility=("v4_1_dependency_graph_to_lineage_certification_schema_transition",),
        schema_discontinuity_visibility=("future_refresh_lineage_schema_transition_not_declared",),
        deterministic_order=1,
    )


def default_blocked_state_visibility(links: tuple[RefreshAncestryLink, ...] | None = None) -> RefreshLineageBlockedStateVisibility:
    ancestry_links = links or default_ancestry_links()
    return RefreshLineageBlockedStateVisibility(
        blocked_visibility_id="v4_1_refresh_lineage_blocked_visibility_primary",
        blocked_lineage_links=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_BLOCKED),
        circular_ancestry_links=tuple(link.link_id for link in ancestry_links if link.circular_ancestry_visibility),
        ancestry_discontinuity_visibility=("v4_1_future_generation_ancestry_not_declared",),
        lineage_discontinuity_visibility=tuple(
            link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_LINEAGE_DISCONTINUITY
        ),
        provenance_discontinuity_visibility=tuple(
            link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_PROVENANCE_DISCONTINUITY
        ),
        replay_discontinuity_visibility=("future_refresh_lineage_replay_source_not_declared",),
        rollback_discontinuity_visibility=("future_refresh_lineage_rollback_target_not_declared",),
        schema_discontinuity_visibility=tuple(
            link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_SCHEMA_DISCONTINUITY
        ),
        prohibited_execution_leakage=("refresh_execution_enabled",),
        prohibited_orchestration_leakage=("orchestration_enabled",),
        prohibited_remediation_leakage=("remediation_enabled",),
        prohibited_migration_leakage=("migration_execution_enabled",),
        prohibited_planner_integration_leakage=("planner_integration_enabled",),
        deterministic_order=1,
    )


def default_unsupported_state_visibility(
    nodes: tuple[RefreshAncestryNode, ...] | None = None,
    links: tuple[RefreshAncestryLink, ...] | None = None,
) -> RefreshLineageUnsupportedStateVisibility:
    ancestry_nodes = nodes or default_ancestry_nodes()
    ancestry_links = links or default_ancestry_links()
    return RefreshLineageUnsupportedStateVisibility(
        unsupported_visibility_id="v4_1_refresh_lineage_unsupported_visibility_primary",
        unsupported_lineage_nodes=tuple(node.node_id for node in ancestry_nodes if node.state == LINEAGE_STATE_UNSUPPORTED),
        unsupported_lineage_links=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_UNSUPPORTED),
        unsupported_lineage_providers=("future_refresh_generation_provider_not_declared",),
        stale_lineage_links=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_STALE),
        prohibited_lineage_links=tuple(link.link_id for link in ancestry_links if link.relationship_state == LINEAGE_STATE_PROHIBITED),
        prohibited_lineage_domains=PROHIBITED_LINEAGE_DOMAINS,
        failure_visibility=("future_refresh_generation_continuity_target_not_declared",),
        deterministic_order=1,
    )


def default_drift_visibility(links: tuple[RefreshAncestryLink, ...] | None = None) -> RefreshLineageDriftVisibility:
    ancestry_links = links or default_ancestry_links()
    return RefreshLineageDriftVisibility(
        drift_id="v4_1_refresh_lineage_drift_visibility_primary",
        stale_lineage_references=tuple(link.link_id for link in ancestry_links if link.drift_visible),
        changed_schema_references=("v4_1_dependency_graph_to_lineage_certification_schema_transition",),
        lineage_drift_references=("future_refresh_generation_drift_not_declared",),
        deterministic_order=1,
    )


def default_diagnostics(
    blocked: RefreshLineageBlockedStateVisibility | None = None,
    unsupported: RefreshLineageUnsupportedStateVisibility | None = None,
    drift: RefreshLineageDriftVisibility | None = None,
) -> RefreshLineageDiagnostics:
    blocked_visibility = blocked or default_blocked_state_visibility()
    unsupported_visibility = unsupported or default_unsupported_state_visibility()
    drift_visibility = drift or default_drift_visibility()
    return RefreshLineageDiagnostics(
        diagnostics_id="v4_1_refresh_lineage_certification_diagnostics_primary",
        diagnostic_references=(
            "v4_1_refresh_lineage_visibility_validation",
            "v4_1_refresh_lineage_continuity_validation",
            "v4_1_refresh_lineage_integrity_validation",
            "v4_1_refresh_lineage_non_execution_validation",
        ),
        warning_visibility=unsupported_visibility.unsupported_lineage_links
        + unsupported_visibility.stale_lineage_links
        + drift_visibility.stale_lineage_references,
        blocker_visibility=blocked_visibility.blocked_lineage_links
        + blocked_visibility.circular_ancestry_links
        + blocked_visibility.ancestry_discontinuity_visibility
        + blocked_visibility.lineage_discontinuity_visibility
        + blocked_visibility.provenance_discontinuity_visibility
        + blocked_visibility.schema_discontinuity_visibility,
        circular_ancestry_visibility=blocked_visibility.circular_ancestry_links,
        unsupported_lineage_visibility=unsupported_visibility.unsupported_lineage_nodes
        + unsupported_visibility.unsupported_lineage_links,
        prohibited_lineage_visibility=unsupported_visibility.prohibited_lineage_links
        + unsupported_visibility.prohibited_lineage_domains,
        drift_visibility=drift_visibility.stale_lineage_references + drift_visibility.lineage_drift_references,
        integrity_visibility=blocked_visibility.prohibited_execution_leakage
        + blocked_visibility.prohibited_orchestration_leakage
        + blocked_visibility.prohibited_remediation_leakage
        + blocked_visibility.prohibited_migration_leakage
        + blocked_visibility.prohibited_planner_integration_leakage,
        deterministic_order=1,
    )


def default_governance() -> RefreshLineageGovernance:
    return RefreshLineageGovernance(
        governance_id="v4_1_refresh_lineage_certification_governance_primary",
        governance_references=(
            "v4_1_refresh_manifest_foundations",
            "v4_1_refresh_dependency_graph_infrastructure",
            "v4_1_refresh_lineage_certification_boundary",
        ),
        explicit_limitations=EXPLICIT_LINEAGE_CERTIFICATION_LIMITATIONS,
        explicit_prohibitions=EXPLICIT_LINEAGE_CERTIFICATION_PROHIBITIONS,
        deterministic_order=1,
    )


def default_refresh_lineage_certification() -> RefreshLineageCertification:
    identity = default_lineage_identity()
    nodes = default_ancestry_nodes(identity)
    links = default_ancestry_links(identity)
    blocked = default_blocked_state_visibility(links)
    unsupported = default_unsupported_state_visibility(nodes, links)
    drift = default_drift_visibility(links)
    return RefreshLineageCertification(
        identity=identity,
        ancestry_nodes=nodes,
        ancestry_links=links,
        provenance_inheritance=(default_provenance_inheritance(identity),),
        evolution_visibility=default_evolution_visibility(links),
        continuity_metadata=default_continuity_metadata(identity),
        replay_lineage_visibility=default_replay_lineage_visibility(),
        rollback_lineage_visibility=default_rollback_lineage_visibility(),
        schema_transition_continuity=default_schema_transition_continuity(),
        blocked_state_visibility=blocked,
        unsupported_state_visibility=unsupported,
        drift_visibility=drift,
        diagnostics=default_diagnostics(blocked, unsupported, drift),
        governance=default_governance(),
    )
