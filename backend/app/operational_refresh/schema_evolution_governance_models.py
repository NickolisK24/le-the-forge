"""Deterministic v4.1 schema evolution governance models.

Schema evolution governance is descriptive evidence only. It does not migrate
schemas, repair compatibility, execute refreshes, orchestrate work, consume
production bundles, integrate with planners, authorize behavior, remediate
blockers, recover state, roll back state, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PHASE_ID = "v4_1_schema_evolution_governance"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION = "v4_1.schema_evolution_governance.1"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_REPORT_SCHEMA_VERSION = "v4_1.schema_evolution_governance_report.1"
V4_1_SCHEMA_EVOLUTION_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.schema_evolution_diagnostics_report.1"
V4_1_SCHEMA_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.schema_continuity_certification_report.1"
V4_1_SCHEMA_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.schema_integrity_certification_report.1"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE = "v4_1_schema_evolution_governance_stable"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_BLOCKED = "v4_1_schema_evolution_governance_blocked"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PURPOSE = "deterministic_schema_evolution_governance_only"

SCHEMA_STATE_COMPATIBLE = "compatible"
SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS = "compatible_with_warnings"
SCHEMA_STATE_BLOCKED = "blocked"
SCHEMA_STATE_UNSUPPORTED = "unsupported"
SCHEMA_STATE_STALE = "stale"
SCHEMA_STATE_PROHIBITED = "prohibited"
SCHEMA_STATE_CIRCULAR_ANCESTRY = "circular_schema_ancestry"
SCHEMA_STATE_VERSION_DISCONTINUITY = "schema_version_discontinuity"
SCHEMA_STATE_LINEAGE_DISCONTINUITY = "schema_lineage_discontinuity"
SCHEMA_STATE_PROVENANCE_DISCONTINUITY = "schema_provenance_discontinuity"
SCHEMA_STATE_REPLAY_DISCONTINUITY = "schema_replay_discontinuity"
SCHEMA_STATE_ROLLBACK_DISCONTINUITY = "schema_rollback_discontinuity"
SCHEMA_STATES: tuple[str, ...] = (
    SCHEMA_STATE_COMPATIBLE,
    SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS,
    SCHEMA_STATE_BLOCKED,
    SCHEMA_STATE_UNSUPPORTED,
    SCHEMA_STATE_STALE,
    SCHEMA_STATE_PROHIBITED,
    SCHEMA_STATE_CIRCULAR_ANCESTRY,
    SCHEMA_STATE_VERSION_DISCONTINUITY,
    SCHEMA_STATE_LINEAGE_DISCONTINUITY,
    SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
    SCHEMA_STATE_REPLAY_DISCONTINUITY,
    SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
)
FAIL_VISIBLE_SCHEMA_STATES: tuple[str, ...] = (
    SCHEMA_STATE_BLOCKED,
    SCHEMA_STATE_UNSUPPORTED,
    SCHEMA_STATE_STALE,
    SCHEMA_STATE_PROHIBITED,
    SCHEMA_STATE_CIRCULAR_ANCESTRY,
    SCHEMA_STATE_VERSION_DISCONTINUITY,
    SCHEMA_STATE_LINEAGE_DISCONTINUITY,
    SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
    SCHEMA_STATE_REPLAY_DISCONTINUITY,
    SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
)

SCHEMA_SEVERITY_INFO = "info"
SCHEMA_SEVERITY_WARNING = "warning"
SCHEMA_SEVERITY_BLOCKED = "blocked"
SCHEMA_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_SCHEMA_DOMAINS: tuple[str, ...] = (
    "schema_migration_execution",
    "automatic_schema_migration",
    "automatic_schema_repair",
    "automatic_compatibility_correction",
    "refresh_execution",
    "orchestration_execution",
    "planner_integration",
    "production_bundle_consumption",
    "remediation_systems",
    "recommendation_ranking_scoring_selection",
    "optimization_systems",
    "authorization_approval_systems",
    "runtime_mutation",
    "automatic_rollback",
    "automatic_recovery",
    "hidden_migration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_SCHEMA_EVOLUTION_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 4 creates deterministic schema evolution governance metadata only.",
    "v4.1 Phase 4 does not enable schema migration execution.",
    "v4.1 Phase 4 does not enable automatic compatibility correction.",
    "v4.1 Phase 4 does not enable refresh execution.",
    "v4.1 Phase 4 does not enable orchestration.",
    "v4.1 Phase 4 does not enable planner integration.",
    "v4.1 Phase 4 does not enable production consumption.",
    "v4.1 Phase 4 does not enable remediation.",
    "v4.1 Phase 4 does not enable mutation behavior.",
)

EXPLICIT_SCHEMA_EVOLUTION_PROHIBITIONS: tuple[str, ...] = (
    "No schema migration execution exists.",
    "No automatic schema migration exists.",
    "No automatic schema repair exists.",
    "No automatic compatibility correction exists.",
    "No refresh execution exists.",
    "No orchestration exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No remediation exists.",
    "No mutation behavior exists.",
    "No silent compatibility fallback behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class SchemaEvolutionIdentity:
    governance_id: str
    refresh_cycle_id: str
    governance_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    schema_version: str
    generated_at: str
    schema_reference: str
    lineage_reference: str
    provenance_reference: str
    diagnostics_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    governance_scope: str = "schema_evolution_identity_descriptive_only"
    governance_purpose: str = V4_1_SCHEMA_EVOLUTION_GOVERNANCE_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    schema_migration_execution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class SchemaVersionNode:
    node_id: str
    schema_version: str
    schema_provider: str
    source_reference: str
    lineage_reference: str
    provenance_reference: str
    state: str
    reason: str
    deterministic_order: int
    severity: str = SCHEMA_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_compatibility_fallback_enabled: bool = False


@dataclass(frozen=True)
class SchemaVersionTransition:
    transition_id: str
    source_node_id: str
    target_node_id: str
    source_schema_version: str
    target_schema_version: str
    compatibility_classification: str
    state: str
    reason: str
    lineage_reference: str
    provenance_reference: str
    deterministic_order: int
    severity: str = SCHEMA_SEVERITY_INFO
    descriptive_only: bool = True
    fail_visible: bool = False
    circular_schema_ancestry_visibility: bool = False
    drift_visible: bool = False
    hidden: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_compatibility_fallback_enabled: bool = False


@dataclass(frozen=True)
class SchemaCompatibilityVisibility:
    compatibility_id: str
    transition_classifications: tuple[str, ...]
    compatible_transition_ids: tuple[str, ...]
    warning_transition_ids: tuple[str, ...]
    blocked_transition_ids: tuple[str, ...]
    unsupported_transition_ids: tuple[str, ...]
    stale_transition_ids: tuple[str, ...]
    prohibited_transition_ids: tuple[str, ...]
    circular_schema_ancestry_ids: tuple[str, ...]
    schema_version_discontinuity_ids: tuple[str, ...]
    deterministic_order: int
    compatibility_visible: bool = True
    compatibility_correction_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_compatibility_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "transition_classifications",
            "compatible_transition_ids",
            "warning_transition_ids",
            "blocked_transition_ids",
            "unsupported_transition_ids",
            "stale_transition_ids",
            "prohibited_transition_ids",
            "circular_schema_ancestry_ids",
            "schema_version_discontinuity_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaContinuityMetadata:
    continuity_id: str
    schema_continuity_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    replay_continuity_references: tuple[str, ...]
    rollback_continuity_references: tuple[str, ...]
    compatibility_references: tuple[str, ...]
    deterministic_order: int
    schema_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    compatibility_visibility_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "schema_continuity_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_continuity_references",
            "rollback_continuity_references",
            "compatibility_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaLineageVisibility:
    lineage_id: str
    lineage_references: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    circular_schema_ancestry_visibility: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_lineage_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "lineage_references",
            "lineage_discontinuity_visibility",
            "circular_schema_ancestry_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaProvenanceVisibility:
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
        for field_name in (
            "provenance_references",
            "inherited_from_references",
            "provenance_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaReplayVisibility:
    replay_id: str
    replay_references: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    live_replay_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    refresh_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_references", "replay_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaRollbackVisibility:
    rollback_id: str
    rollback_references: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_references", "rollback_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaDriftVisibility:
    drift_id: str
    stale_transition_ids: tuple[str, ...]
    schema_drift_references: tuple[str, ...]
    compatibility_drift_references: tuple[str, ...]
    deterministic_order: int
    drift_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_drift_resolution_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("stale_transition_ids", "schema_drift_references", "compatibility_drift_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaBlockedStateVisibility:
    blocked_id: str
    blocked_transition_ids: tuple[str, ...]
    blocked_compatibility_states: tuple[str, ...]
    schema_version_discontinuity_visibility: tuple[str, ...]
    schema_lineage_discontinuity_visibility: tuple[str, ...]
    schema_provenance_discontinuity_visibility: tuple[str, ...]
    schema_replay_discontinuity_visibility: tuple[str, ...]
    schema_rollback_discontinuity_visibility: tuple[str, ...]
    circular_schema_ancestry_visibility: tuple[str, ...]
    prohibited_migration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    silent_compatibility_fallback_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_transition_ids",
            "blocked_compatibility_states",
            "schema_version_discontinuity_visibility",
            "schema_lineage_discontinuity_visibility",
            "schema_provenance_discontinuity_visibility",
            "schema_replay_discontinuity_visibility",
            "schema_rollback_discontinuity_visibility",
            "circular_schema_ancestry_visibility",
            "prohibited_migration_leakage",
            "prohibited_execution_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_remediation_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaUnsupportedStateVisibility:
    unsupported_id: str
    unsupported_node_ids: tuple[str, ...]
    unsupported_transition_ids: tuple[str, ...]
    unsupported_schema_providers: tuple[str, ...]
    stale_transition_ids: tuple[str, ...]
    prohibited_transition_ids: tuple[str, ...]
    prohibited_schema_domains: tuple[str, ...]
    failure_visibility: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_unsupported_resolution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_node_ids",
            "unsupported_transition_ids",
            "unsupported_schema_providers",
            "stale_transition_ids",
            "prohibited_transition_ids",
            "prohibited_schema_domains",
            "failure_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaEvolutionDiagnostics:
    diagnostics_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    unsupported_schema_visibility: tuple[str, ...]
    prohibited_schema_visibility: tuple[str, ...]
    compatibility_visibility: tuple[str, ...]
    drift_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_compatibility_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "unsupported_schema_visibility",
            "prohibited_schema_visibility",
            "compatibility_visibility",
            "drift_visibility",
            "integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaGovernanceVisibility:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    schema_migration_execution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SchemaEvolutionGovernance:
    identity: SchemaEvolutionIdentity
    version_nodes: tuple[SchemaVersionNode, ...]
    version_transitions: tuple[SchemaVersionTransition, ...]
    compatibility_visibility: SchemaCompatibilityVisibility
    continuity_metadata: SchemaContinuityMetadata
    lineage_visibility: SchemaLineageVisibility
    provenance_visibility: SchemaProvenanceVisibility
    replay_visibility: SchemaReplayVisibility
    rollback_visibility: SchemaRollbackVisibility
    drift_visibility: SchemaDriftVisibility
    blocked_state_visibility: SchemaBlockedStateVisibility
    unsupported_state_visibility: SchemaUnsupportedStateVisibility
    diagnostics: SchemaEvolutionDiagnostics
    governance: SchemaGovernanceVisibility
    non_executable: bool = True
    descriptive_only: bool = True
    schema_migration_execution_enabled: bool = False
    automatic_schema_migration_enabled: bool = False
    automatic_schema_repair_enabled: bool = False
    automatic_compatibility_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
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
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    hidden_migration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_compatibility_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("version_nodes", "version_transitions"):
            _set_tuple_field(self, field_name)


def default_schema_evolution_identity() -> SchemaEvolutionIdentity:
    return SchemaEvolutionIdentity(
        governance_id="v4_1_schema_evolution_governance_primary",
        refresh_cycle_id="v4_1_phase_4_schema_evolution_governance",
        governance_version="v4.1.0-phase-4",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
        generated_at=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_GENERATED_AT,
        schema_reference="v4_1_schema_evolution_governance_schema_primary",
        lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
        provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
        diagnostics_reference="v4_1_schema_evolution_governance_diagnostics_primary",
        continuity_reference="v4_1_schema_evolution_governance_continuity_primary",
        integrity_reference="v4_1_schema_evolution_governance_integrity_primary",
        governance_reference="v4_1_schema_evolution_governance_boundary_primary",
    )


def default_schema_version_nodes() -> tuple[SchemaVersionNode, ...]:
    return (
        SchemaVersionNode(
            node_id="v4_1_schema_node_v4_0_closeout",
            schema_version="v4_0.closeout_readiness.1",
            schema_provider="operational_lifecycle",
            source_reference="docs/generated/v4_0_closeout_and_v4_1_readiness_report.json",
            lineage_reference="v4_0_operational_lifecycle_lineage",
            provenance_reference="v4_0_operational_lifecycle_provenance",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="v4.0 closeout schema remains descriptive evidence for v4.1 readiness.",
            deterministic_order=10,
        ),
        SchemaVersionNode(
            node_id="v4_1_schema_node_refresh_manifest",
            schema_version="v4_1.refresh_manifest.1",
            schema_provider="operational_refresh",
            source_reference="docs/generated/v4_1_refresh_manifest_report.json",
            lineage_reference="v4_1_refresh_manifest_lineage_primary",
            provenance_reference="v4_1_refresh_manifest_provenance_primary",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Phase 1 refresh manifest schema is visible and deterministic.",
            deterministic_order=20,
        ),
        SchemaVersionNode(
            node_id="v4_1_schema_node_dependency_graph",
            schema_version="v4_1.refresh_dependency_graph.1",
            schema_provider="operational_refresh",
            source_reference="docs/generated/v4_1_refresh_dependency_graph_report.json",
            lineage_reference="v4_1_refresh_dependency_graph_lineage_primary",
            provenance_reference="v4_1_refresh_dependency_graph_provenance_primary",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Phase 2 dependency graph schema is visible and deterministic.",
            deterministic_order=30,
        ),
        SchemaVersionNode(
            node_id="v4_1_schema_node_lineage_certification",
            schema_version="v4_1.refresh_lineage_certification.1",
            schema_provider="operational_refresh",
            source_reference="docs/generated/v4_1_refresh_lineage_certification_report.json",
            lineage_reference="v4_1_refresh_lineage_certification_lineage_primary",
            provenance_reference="v4_1_refresh_lineage_certification_provenance_primary",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Phase 3 lineage certification schema is visible and deterministic.",
            deterministic_order=40,
        ),
        SchemaVersionNode(
            node_id="v4_1_schema_node_future_provider",
            schema_version="v4_1.future_refresh_schema.unrecognized",
            schema_provider="unsupported_future_schema_provider",
            source_reference="unsupported_future_schema_reference",
            lineage_reference="v4_1_future_schema_lineage_unverified",
            provenance_reference="v4_1_future_schema_provenance_unverified",
            state=SCHEMA_STATE_UNSUPPORTED,
            reason="Future schema provider is unsupported and remains fail-visible.",
            deterministic_order=50,
            severity=SCHEMA_SEVERITY_WARNING,
            fail_visible=True,
        ),
        SchemaVersionNode(
            node_id="v4_1_schema_node_prohibited_migration",
            schema_version="v4_1.prohibited_migration_schema",
            schema_provider="prohibited_migration_provider",
            source_reference="prohibited_schema_migration_reference",
            lineage_reference="v4_1_prohibited_schema_lineage",
            provenance_reference="v4_1_prohibited_schema_provenance",
            state=SCHEMA_STATE_PROHIBITED,
            reason="Schema migration execution provider is prohibited and remains visible.",
            deterministic_order=60,
            severity=SCHEMA_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
    )


def default_schema_version_transitions() -> tuple[SchemaVersionTransition, ...]:
    return (
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_v4_0_to_manifest",
            source_node_id="v4_1_schema_node_v4_0_closeout",
            target_node_id="v4_1_schema_node_refresh_manifest",
            source_schema_version="v4_0.closeout_readiness.1",
            target_schema_version="v4_1.refresh_manifest.1",
            compatibility_classification="descriptive_compatible",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Manifest schema extends v4.0 readiness evidence without migration.",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            deterministic_order=10,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_manifest_to_dependency_graph",
            source_node_id="v4_1_schema_node_refresh_manifest",
            target_node_id="v4_1_schema_node_dependency_graph",
            source_schema_version="v4_1.refresh_manifest.1",
            target_schema_version="v4_1.refresh_dependency_graph.1",
            compatibility_classification="descriptive_compatible",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Dependency graph schema references manifest evidence descriptively.",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            deterministic_order=20,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_dependency_graph_to_lineage",
            source_node_id="v4_1_schema_node_dependency_graph",
            target_node_id="v4_1_schema_node_lineage_certification",
            source_schema_version="v4_1.refresh_dependency_graph.1",
            target_schema_version="v4_1.refresh_lineage_certification.1",
            compatibility_classification="descriptive_compatible",
            state=SCHEMA_STATE_COMPATIBLE,
            reason="Lineage certification schema references dependency governance evidence descriptively.",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            deterministic_order=30,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_lineage_to_schema_governance",
            source_node_id="v4_1_schema_node_lineage_certification",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_lineage_certification.1",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="compatible_with_governance_warnings",
            state=SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS,
            reason="Schema governance adds compatibility visibility without migration capability.",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            deterministic_order=40,
            severity=SCHEMA_SEVERITY_WARNING,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_future_provider_unsupported",
            source_node_id="v4_1_schema_node_lineage_certification",
            target_node_id="v4_1_schema_node_future_provider",
            source_schema_version="v4_1.refresh_lineage_certification.1",
            target_schema_version="v4_1.future_refresh_schema.unrecognized",
            compatibility_classification="unsupported_provider",
            state=SCHEMA_STATE_UNSUPPORTED,
            reason="Future schema provider cannot be governed silently.",
            lineage_reference="v4_1_future_schema_lineage_unverified",
            provenance_reference="v4_1_future_schema_provenance_unverified",
            deterministic_order=50,
            severity=SCHEMA_SEVERITY_WARNING,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_stale_manifest_version",
            source_node_id="v4_1_schema_node_refresh_manifest",
            target_node_id="v4_1_schema_node_lineage_certification",
            source_schema_version="v4_1.refresh_manifest.0",
            target_schema_version="v4_1.refresh_lineage_certification.1",
            compatibility_classification="stale_source_schema",
            state=SCHEMA_STATE_STALE,
            reason="Stale manifest schema version is visible and not corrected.",
            lineage_reference="v4_1_schema_stale_lineage_reference",
            provenance_reference="v4_1_schema_stale_provenance_reference",
            deterministic_order=60,
            severity=SCHEMA_SEVERITY_WARNING,
            fail_visible=True,
            drift_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_version_discontinuity",
            source_node_id="v4_1_schema_node_dependency_graph",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_dependency_graph.1",
            target_schema_version="v4_3.unapproved_schema_jump",
            compatibility_classification="schema_version_gap",
            state=SCHEMA_STATE_VERSION_DISCONTINUITY,
            reason="Unapproved schema version jump is visible and not migrated.",
            lineage_reference="v4_1_schema_version_discontinuity_lineage",
            provenance_reference="v4_1_schema_version_discontinuity_provenance",
            deterministic_order=70,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_lineage_discontinuity",
            source_node_id="v4_1_schema_node_refresh_manifest",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_manifest.1",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="lineage_gap",
            state=SCHEMA_STATE_LINEAGE_DISCONTINUITY,
            reason="Schema lineage continuity gap is visible and not repaired.",
            lineage_reference="v4_1_schema_lineage_gap_reference",
            provenance_reference="v4_1_schema_evolution_governance_provenance_primary",
            deterministic_order=80,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_provenance_discontinuity",
            source_node_id="v4_1_schema_node_dependency_graph",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_dependency_graph.1",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="provenance_gap",
            state=SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
            reason="Schema provenance continuity gap is visible and not inferred.",
            lineage_reference="v4_1_schema_evolution_governance_lineage_primary",
            provenance_reference="v4_1_schema_provenance_gap_reference",
            deterministic_order=90,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_replay_discontinuity",
            source_node_id="v4_1_schema_node_lineage_certification",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_lineage_certification.1",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="replay_gap",
            state=SCHEMA_STATE_REPLAY_DISCONTINUITY,
            reason="Schema replay continuity gap is visible and not executed.",
            lineage_reference="v4_1_schema_replay_gap_lineage",
            provenance_reference="v4_1_schema_replay_gap_provenance",
            deterministic_order=100,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_rollback_discontinuity",
            source_node_id="v4_1_schema_node_lineage_certification",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.refresh_lineage_certification.1",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="rollback_gap",
            state=SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
            reason="Schema rollback continuity gap is visible and not recovered.",
            lineage_reference="v4_1_schema_rollback_gap_lineage",
            provenance_reference="v4_1_schema_rollback_gap_provenance",
            deterministic_order=110,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_circular_ancestry",
            source_node_id="v4_1_schema_evolution_governance_primary",
            target_node_id="v4_1_schema_node_dependency_graph",
            source_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            target_schema_version="v4_1.refresh_dependency_graph.1",
            compatibility_classification="circular_schema_ancestry",
            state=SCHEMA_STATE_CIRCULAR_ANCESTRY,
            reason="Circular schema ancestry is visible and not traversed.",
            lineage_reference="v4_1_schema_circular_ancestry_lineage",
            provenance_reference="v4_1_schema_circular_ancestry_provenance",
            deterministic_order=120,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
            circular_schema_ancestry_visibility=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_prohibited_migration",
            source_node_id="v4_1_schema_node_lineage_certification",
            target_node_id="v4_1_schema_node_prohibited_migration",
            source_schema_version="v4_1.refresh_lineage_certification.1",
            target_schema_version="v4_1.prohibited_migration_schema",
            compatibility_classification="prohibited_migration_execution",
            state=SCHEMA_STATE_PROHIBITED,
            reason="Migration execution path is prohibited and remains visible.",
            lineage_reference="v4_1_schema_prohibited_migration_lineage",
            provenance_reference="v4_1_schema_prohibited_migration_provenance",
            deterministic_order=130,
            severity=SCHEMA_SEVERITY_PROHIBITED,
            fail_visible=True,
        ),
        SchemaVersionTransition(
            transition_id="v4_1_schema_transition_blocked_compatibility",
            source_node_id="v4_1_schema_node_future_provider",
            target_node_id="v4_1_schema_evolution_governance_primary",
            source_schema_version="v4_1.future_refresh_schema.unrecognized",
            target_schema_version=V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
            compatibility_classification="blocked_unknown_compatibility",
            state=SCHEMA_STATE_BLOCKED,
            reason="Unknown compatibility is blocked and not corrected.",
            lineage_reference="v4_1_schema_blocked_compatibility_lineage",
            provenance_reference="v4_1_schema_blocked_compatibility_provenance",
            deterministic_order=140,
            severity=SCHEMA_SEVERITY_BLOCKED,
            fail_visible=True,
        ),
    )


def default_schema_evolution_governance() -> SchemaEvolutionGovernance:
    identity = default_schema_evolution_identity()
    nodes = default_schema_version_nodes()
    transitions = default_schema_version_transitions()
    return SchemaEvolutionGovernance(
        identity=identity,
        version_nodes=nodes,
        version_transitions=transitions,
        compatibility_visibility=SchemaCompatibilityVisibility(
            compatibility_id="v4_1_schema_evolution_compatibility_visibility_primary",
            transition_classifications=tuple(transition.compatibility_classification for transition in transitions),
            compatible_transition_ids=(
                "v4_1_schema_transition_v4_0_to_manifest",
                "v4_1_schema_transition_manifest_to_dependency_graph",
                "v4_1_schema_transition_dependency_graph_to_lineage",
            ),
            warning_transition_ids=("v4_1_schema_transition_lineage_to_schema_governance",),
            blocked_transition_ids=("v4_1_schema_transition_blocked_compatibility",),
            unsupported_transition_ids=("v4_1_schema_transition_future_provider_unsupported",),
            stale_transition_ids=("v4_1_schema_transition_stale_manifest_version",),
            prohibited_transition_ids=("v4_1_schema_transition_prohibited_migration",),
            circular_schema_ancestry_ids=("v4_1_schema_transition_circular_ancestry",),
            schema_version_discontinuity_ids=("v4_1_schema_transition_version_discontinuity",),
            deterministic_order=10,
        ),
        continuity_metadata=SchemaContinuityMetadata(
            continuity_id="v4_1_schema_evolution_continuity_primary",
            schema_continuity_references=(identity.schema_reference,),
            lineage_continuity_references=(identity.lineage_reference,),
            provenance_continuity_references=(identity.provenance_reference,),
            replay_continuity_references=("v4_1_schema_replay_visibility_primary",),
            rollback_continuity_references=("v4_1_schema_rollback_visibility_primary",),
            compatibility_references=("v4_1_schema_evolution_compatibility_visibility_primary",),
            deterministic_order=20,
        ),
        lineage_visibility=SchemaLineageVisibility(
            lineage_id=identity.lineage_reference,
            lineage_references=(
                "v4_1_refresh_manifest_lineage_primary",
                "v4_1_refresh_dependency_graph_lineage_primary",
                "v4_1_refresh_lineage_certification_lineage_primary",
                identity.lineage_reference,
            ),
            lineage_discontinuity_visibility=("v4_1_schema_transition_lineage_discontinuity",),
            circular_schema_ancestry_visibility=("v4_1_schema_transition_circular_ancestry",),
            deterministic_order=30,
        ),
        provenance_visibility=SchemaProvenanceVisibility(
            provenance_id=identity.provenance_reference,
            provenance_references=(
                "v4_1_refresh_manifest_provenance_primary",
                "v4_1_refresh_dependency_graph_provenance_primary",
                "v4_1_refresh_lineage_certification_provenance_primary",
                identity.provenance_reference,
            ),
            inherited_from_references=(
                "v4_1_refresh_manifest_primary",
                "v4_1_refresh_dependency_graph_primary",
                "v4_1_refresh_lineage_certification_primary",
            ),
            provenance_discontinuity_visibility=("v4_1_schema_transition_provenance_discontinuity",),
            deterministic_order=40,
        ),
        replay_visibility=SchemaReplayVisibility(
            replay_id="v4_1_schema_replay_visibility_primary",
            replay_references=("v4_1_schema_replay_evidence_primary",),
            replay_discontinuity_visibility=("v4_1_schema_transition_replay_discontinuity",),
            deterministic_order=50,
        ),
        rollback_visibility=SchemaRollbackVisibility(
            rollback_id="v4_1_schema_rollback_visibility_primary",
            rollback_references=("v4_1_schema_rollback_evidence_primary",),
            rollback_discontinuity_visibility=("v4_1_schema_transition_rollback_discontinuity",),
            deterministic_order=60,
        ),
        drift_visibility=SchemaDriftVisibility(
            drift_id="v4_1_schema_drift_visibility_primary",
            stale_transition_ids=("v4_1_schema_transition_stale_manifest_version",),
            schema_drift_references=("v4_1_schema_transition_stale_manifest_version",),
            compatibility_drift_references=("v4_1_schema_transition_lineage_to_schema_governance",),
            deterministic_order=70,
        ),
        blocked_state_visibility=SchemaBlockedStateVisibility(
            blocked_id="v4_1_schema_blocked_state_visibility_primary",
            blocked_transition_ids=("v4_1_schema_transition_blocked_compatibility",),
            blocked_compatibility_states=("blocked_unknown_compatibility",),
            schema_version_discontinuity_visibility=("v4_1_schema_transition_version_discontinuity",),
            schema_lineage_discontinuity_visibility=("v4_1_schema_transition_lineage_discontinuity",),
            schema_provenance_discontinuity_visibility=("v4_1_schema_transition_provenance_discontinuity",),
            schema_replay_discontinuity_visibility=("v4_1_schema_transition_replay_discontinuity",),
            schema_rollback_discontinuity_visibility=("v4_1_schema_transition_rollback_discontinuity",),
            circular_schema_ancestry_visibility=("v4_1_schema_transition_circular_ancestry",),
            prohibited_migration_leakage=("schema_migration_execution", "automatic_schema_migration"),
            prohibited_execution_leakage=("refresh_execution", "implicit_execution_pathways"),
            prohibited_orchestration_leakage=("orchestration_execution",),
            prohibited_remediation_leakage=("remediation_systems",),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=80,
        ),
        unsupported_state_visibility=SchemaUnsupportedStateVisibility(
            unsupported_id="v4_1_schema_unsupported_state_visibility_primary",
            unsupported_node_ids=("v4_1_schema_node_future_provider",),
            unsupported_transition_ids=("v4_1_schema_transition_future_provider_unsupported",),
            unsupported_schema_providers=("unsupported_future_schema_provider",),
            stale_transition_ids=("v4_1_schema_transition_stale_manifest_version",),
            prohibited_transition_ids=("v4_1_schema_transition_prohibited_migration",),
            prohibited_schema_domains=PROHIBITED_SCHEMA_DOMAINS,
            failure_visibility=(
                "unsupported schema provider remains fail-visible",
                "blocked compatibility remains fail-visible",
                "schema version discontinuity remains fail-visible",
                "circular schema ancestry remains fail-visible",
            ),
            deterministic_order=90,
        ),
        diagnostics=SchemaEvolutionDiagnostics(
            diagnostics_id="v4_1_schema_evolution_diagnostics_primary",
            diagnostic_references=(
                "v4_1_schema_blocked_state_visibility_primary",
                "v4_1_schema_unsupported_state_visibility_primary",
                "v4_1_schema_drift_visibility_primary",
            ),
            warning_visibility=(
                "v4_1_schema_transition_lineage_to_schema_governance",
                "v4_1_schema_transition_future_provider_unsupported",
                "v4_1_schema_transition_stale_manifest_version",
            ),
            blocker_visibility=(
                "v4_1_schema_transition_blocked_compatibility",
                "v4_1_schema_transition_version_discontinuity",
                "v4_1_schema_transition_circular_ancestry",
            ),
            unsupported_schema_visibility=("v4_1_schema_transition_future_provider_unsupported",),
            prohibited_schema_visibility=("v4_1_schema_transition_prohibited_migration",),
            compatibility_visibility=("v4_1_schema_evolution_compatibility_visibility_primary",),
            drift_visibility=("v4_1_schema_drift_visibility_primary",),
            integrity_visibility=("v4_1_schema_evolution_integrity_primary",),
            deterministic_order=100,
        ),
        governance=SchemaGovernanceVisibility(
            governance_id=identity.governance_reference,
            governance_references=(
                identity.governance_reference,
                "v4_1_schema_evolution_governance_boundary_primary",
            ),
            explicit_limitations=EXPLICIT_SCHEMA_EVOLUTION_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_SCHEMA_EVOLUTION_PROHIBITIONS,
            deterministic_order=110,
        ),
    )
