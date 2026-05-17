"""Deterministic v4.1 replay and rollback visibility models.

Replay and rollback visibility is descriptive governance evidence only. It does
not execute replay, execute rollback, recover state, remediate blockers, correct
state, execute refreshes, orchestrate work, sequence work, migrate schemas,
consume production bundles, integrate with planners, authorize behavior, or
mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REPLAY_ROLLBACK_VISIBILITY_PHASE_ID = "v4_1_refresh_replay_rollback_visibility"
V4_1_REPLAY_ROLLBACK_VISIBILITY_SCHEMA_VERSION = "v4_1.refresh_replay_rollback_visibility.1"
V4_1_REPLAY_ROLLBACK_VISIBILITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_replay_rollback_visibility_report.1"
V4_1_REPLAY_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.refresh_replay_diagnostics_report.1"
V4_1_ROLLBACK_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.refresh_rollback_diagnostics_report.1"
V4_1_REPLAY_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_replay_continuity_report.1"
V4_1_ROLLBACK_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_rollback_continuity_report.1"
V4_1_REPLAY_ROLLBACK_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_replay_rollback_integrity_report.1"
V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_STABLE = "v4_1_refresh_replay_rollback_visibility_stable"
V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_BLOCKED = "v4_1_refresh_replay_rollback_visibility_blocked"
V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REPLAY_ROLLBACK_VISIBILITY_PURPOSE = "deterministic_replay_rollback_visibility_governance_only"

VISIBILITY_TYPE_REPLAY = "replay"
VISIBILITY_TYPE_ROLLBACK = "rollback"
VISIBILITY_TYPES: tuple[str, ...] = (VISIBILITY_TYPE_REPLAY, VISIBILITY_TYPE_ROLLBACK)

REPLAY_ROLLBACK_STATE_VISIBLE = "visible"
REPLAY_ROLLBACK_STATE_BLOCKED = "blocked"
REPLAY_ROLLBACK_STATE_UNSUPPORTED = "unsupported"
REPLAY_ROLLBACK_STATE_STALE = "stale"
REPLAY_ROLLBACK_STATE_PROHIBITED = "prohibited"
REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY = "replay_discontinuity"
REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY = "rollback_discontinuity"
REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY = "replay_lineage_discontinuity"
REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY = "rollback_lineage_discontinuity"
REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY = "replay_provenance_discontinuity"
REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY = "rollback_provenance_discontinuity"
REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT = "replay_drift_conflict"
REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT = "rollback_drift_conflict"
REPLAY_ROLLBACK_STATES: tuple[str, ...] = (
    REPLAY_ROLLBACK_STATE_VISIBLE,
    REPLAY_ROLLBACK_STATE_BLOCKED,
    REPLAY_ROLLBACK_STATE_UNSUPPORTED,
    REPLAY_ROLLBACK_STATE_STALE,
    REPLAY_ROLLBACK_STATE_PROHIBITED,
    REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT,
)
FAIL_VISIBLE_REPLAY_ROLLBACK_STATES: tuple[str, ...] = tuple(
    state for state in REPLAY_ROLLBACK_STATES if state != REPLAY_ROLLBACK_STATE_VISIBLE
)

REPLAY_ROLLBACK_SEVERITY_INFO = "info"
REPLAY_ROLLBACK_SEVERITY_WARNING = "warning"
REPLAY_ROLLBACK_SEVERITY_BLOCKED = "blocked"
REPLAY_ROLLBACK_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_REPLAY_DOMAINS: tuple[str, ...] = (
    "replay_execution",
    "recovery_execution",
    "automatic_recovery",
    "remediation_systems",
    "automatic_correction",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "schema_migration_execution",
    "automatic_migration",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_ranking_scoring_selection",
    "optimization_systems",
    "authorization_approval_systems",
    "runtime_mutation",
    "hidden_recovery_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

PROHIBITED_ROLLBACK_DOMAINS: tuple[str, ...] = (
    "rollback_execution",
    "recovery_execution",
    "automatic_rollback",
    "automatic_recovery",
    "remediation_systems",
    "automatic_correction",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "schema_migration_execution",
    "automatic_migration",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_ranking_scoring_selection",
    "optimization_systems",
    "authorization_approval_systems",
    "runtime_mutation",
    "hidden_rollback_behavior",
    "hidden_recovery_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_REPLAY_ROLLBACK_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 7 creates deterministic replay and rollback visibility metadata only.",
    "v4.1 Phase 7 does not enable rollback execution.",
    "v4.1 Phase 7 does not enable replay execution.",
    "v4.1 Phase 7 does not enable recovery execution.",
    "v4.1 Phase 7 does not enable remediation.",
    "v4.1 Phase 7 does not enable automatic correction.",
    "v4.1 Phase 7 does not enable orchestration execution.",
    "v4.1 Phase 7 does not enable automatic sequencing.",
    "v4.1 Phase 7 does not enable migration execution.",
    "v4.1 Phase 7 does not enable planner integration.",
    "v4.1 Phase 7 does not enable production consumption.",
    "v4.1 Phase 7 does not enable mutation behavior.",
)

EXPLICIT_REPLAY_ROLLBACK_PROHIBITIONS: tuple[str, ...] = (
    "No rollback execution exists.",
    "No replay execution exists.",
    "No recovery execution exists.",
    "No remediation exists.",
    "No automatic correction exists.",
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No migration execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No mutation behavior exists.",
    "No executable replay engine exists.",
    "No executable rollback planner exists.",
    "No automatic recovery behavior exists.",
    "No remediation-capable replay diagnostics exist.",
    "No silent replay or rollback correction behavior exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class ReplayRollbackVisibilityIdentity:
    visibility_id: str
    refresh_cycle_id: str
    visibility_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    source_schema_governance_reference: str
    source_sequencing_reference: str
    source_drift_certification_reference: str
    schema_version: str
    generated_at: str
    replay_reference: str
    rollback_reference: str
    lineage_reference: str
    provenance_reference: str
    diagnostics_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    governance_scope: str = "refresh_replay_rollback_visibility_descriptive_only"
    governance_purpose: str = V4_1_REPLAY_ROLLBACK_VISIBILITY_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    replay_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class ReplayRollbackEvidence:
    evidence_id: str
    visibility_type: str
    source_layer: str
    source_reference: str
    classification: str
    state: str
    severity: str
    reason: str
    lineage_reference: str
    provenance_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = False
    hidden: bool = False
    replay_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_replay_rollback_correction_enabled: bool = False


@dataclass(frozen=True)
class ReplayRollbackLineageVisibility:
    lineage_id: str
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    replay_lineage_discontinuity_visibility: tuple[str, ...]
    rollback_lineage_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    replay_lineage_continuity_preserved: bool = True
    rollback_lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_lineage_references",
            "rollback_lineage_references",
            "replay_lineage_discontinuity_visibility",
            "rollback_lineage_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackProvenanceVisibility:
    provenance_id: str
    replay_provenance_references: tuple[str, ...]
    rollback_provenance_references: tuple[str, ...]
    inherited_from_references: tuple[str, ...]
    replay_provenance_discontinuity_visibility: tuple[str, ...]
    rollback_provenance_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    replay_provenance_continuity_preserved: bool = True
    rollback_provenance_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    inferred_provenance_allowed: bool = False
    hidden_provenance_resolution_enabled: bool = False
    execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_provenance_references",
            "rollback_provenance_references",
            "inherited_from_references",
            "replay_provenance_discontinuity_visibility",
            "rollback_provenance_discontinuity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackContinuityMetadata:
    continuity_id: str
    replay_continuity_references: tuple[str, ...]
    rollback_continuity_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    replay_provenance_references: tuple[str, ...]
    rollback_provenance_references: tuple[str, ...]
    dependency_continuity_references: tuple[str, ...]
    sequencing_continuity_references: tuple[str, ...]
    schema_continuity_references: tuple[str, ...]
    drift_continuity_references: tuple[str, ...]
    deterministic_order: int
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    replay_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_continuity_references",
            "rollback_continuity_references",
            "replay_lineage_references",
            "rollback_lineage_references",
            "replay_provenance_references",
            "rollback_provenance_references",
            "dependency_continuity_references",
            "sequencing_continuity_references",
            "schema_continuity_references",
            "drift_continuity_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackDriftVisibility:
    drift_id: str
    replay_drift_conflict_ids: tuple[str, ...]
    rollback_drift_conflict_ids: tuple[str, ...]
    stale_replay_ids: tuple[str, ...]
    stale_rollback_ids: tuple[str, ...]
    deterministic_order: int
    replay_drift_visible: bool = True
    rollback_drift_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_drift_resolution_enabled: bool = False
    automatic_correction_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_drift_conflict_ids",
            "rollback_drift_conflict_ids",
            "stale_replay_ids",
            "stale_rollback_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackBlockedStateVisibility:
    blocked_id: str
    blocked_replay_ids: tuple[str, ...]
    blocked_rollback_ids: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    replay_lineage_discontinuity_visibility: tuple[str, ...]
    rollback_lineage_discontinuity_visibility: tuple[str, ...]
    replay_provenance_discontinuity_visibility: tuple[str, ...]
    rollback_provenance_discontinuity_visibility: tuple[str, ...]
    replay_drift_conflict_visibility: tuple[str, ...]
    rollback_drift_conflict_visibility: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_recovery_leakage: tuple[str, ...]
    prohibited_rollback_execution_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    recovery_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    automatic_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_replay_ids",
            "blocked_rollback_ids",
            "replay_discontinuity_visibility",
            "rollback_discontinuity_visibility",
            "replay_lineage_discontinuity_visibility",
            "rollback_lineage_discontinuity_visibility",
            "replay_provenance_discontinuity_visibility",
            "rollback_provenance_discontinuity_visibility",
            "replay_drift_conflict_visibility",
            "rollback_drift_conflict_visibility",
            "prohibited_remediation_leakage",
            "prohibited_recovery_leakage",
            "prohibited_rollback_execution_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackUnsupportedStateVisibility:
    unsupported_id: str
    unsupported_replay_ids: tuple[str, ...]
    unsupported_rollback_ids: tuple[str, ...]
    unsupported_replay_providers: tuple[str, ...]
    unsupported_rollback_providers: tuple[str, ...]
    stale_replay_ids: tuple[str, ...]
    stale_rollback_ids: tuple[str, ...]
    prohibited_replay_ids: tuple[str, ...]
    prohibited_rollback_ids: tuple[str, ...]
    prohibited_replay_domains: tuple[str, ...]
    prohibited_rollback_domains: tuple[str, ...]
    failure_visibility: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_unsupported_resolution_enabled: bool = False
    automatic_correction_enabled: bool = False
    remediation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_replay_ids",
            "unsupported_rollback_ids",
            "unsupported_replay_providers",
            "unsupported_rollback_providers",
            "stale_replay_ids",
            "stale_rollback_ids",
            "prohibited_replay_ids",
            "prohibited_rollback_ids",
            "prohibited_replay_domains",
            "prohibited_rollback_domains",
            "failure_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackDiagnostics:
    diagnostics_id: str
    replay_diagnostic_references: tuple[str, ...]
    rollback_diagnostic_references: tuple[str, ...]
    replay_warning_visibility: tuple[str, ...]
    rollback_warning_visibility: tuple[str, ...]
    replay_blocker_visibility: tuple[str, ...]
    rollback_blocker_visibility: tuple[str, ...]
    replay_integrity_visibility: tuple[str, ...]
    rollback_integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    recovery_execution_enabled: bool = False
    replay_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_replay_rollback_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "replay_diagnostic_references",
            "rollback_diagnostic_references",
            "replay_warning_visibility",
            "rollback_warning_visibility",
            "replay_blocker_visibility",
            "rollback_blocker_visibility",
            "replay_integrity_visibility",
            "rollback_integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ReplayRollbackGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    replay_execution_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    remediation_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshReplayRollbackVisibility:
    identity: ReplayRollbackVisibilityIdentity
    evidence: tuple[ReplayRollbackEvidence, ...]
    lineage_visibility: ReplayRollbackLineageVisibility
    provenance_visibility: ReplayRollbackProvenanceVisibility
    continuity_metadata: ReplayRollbackContinuityMetadata
    drift_visibility: ReplayRollbackDriftVisibility
    blocked_state_visibility: ReplayRollbackBlockedStateVisibility
    unsupported_state_visibility: ReplayRollbackUnsupportedStateVisibility
    diagnostics: ReplayRollbackDiagnostics
    governance: ReplayRollbackGovernance
    non_executable: bool = True
    descriptive_only: bool = True
    rollback_execution_enabled: bool = False
    replay_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_recovery_behavior_enabled: bool = False
    hidden_rollback_behavior_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_replay_rollback_correction_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence")


def default_replay_rollback_identity() -> ReplayRollbackVisibilityIdentity:
    return ReplayRollbackVisibilityIdentity(
        visibility_id="v4_1_refresh_replay_rollback_visibility_primary",
        refresh_cycle_id="v4_1_phase_7_refresh_replay_rollback_visibility",
        visibility_version="v4.1.0-phase-7",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        source_schema_governance_reference="v4_1_schema_evolution_governance_primary",
        source_sequencing_reference="v4_1_refresh_sequencing_visibility_primary",
        source_drift_certification_reference="v4_1_refresh_drift_certification_primary",
        schema_version=V4_1_REPLAY_ROLLBACK_VISIBILITY_SCHEMA_VERSION,
        generated_at=V4_1_REPLAY_ROLLBACK_VISIBILITY_GENERATED_AT,
        replay_reference="v4_1_replay_visibility_primary",
        rollback_reference="v4_1_rollback_visibility_primary",
        lineage_reference="v4_1_replay_rollback_lineage_primary",
        provenance_reference="v4_1_replay_rollback_provenance_primary",
        diagnostics_reference="v4_1_replay_rollback_diagnostics_primary",
        continuity_reference="v4_1_replay_rollback_continuity_primary",
        integrity_reference="v4_1_replay_rollback_integrity_primary",
        governance_reference="v4_1_replay_rollback_boundary_primary",
    )


def _evidence(
    evidence_id: str,
    visibility_type: str,
    source_layer: str,
    classification: str,
    state: str,
    reason: str,
    deterministic_order: int,
    severity: str = REPLAY_ROLLBACK_SEVERITY_WARNING,
) -> ReplayRollbackEvidence:
    return ReplayRollbackEvidence(
        evidence_id=evidence_id,
        visibility_type=visibility_type,
        source_layer=source_layer,
        source_reference=f"v4_1_{source_layer}_reference",
        classification=classification,
        state=state,
        severity=severity,
        reason=reason,
        lineage_reference=f"v4_1_{classification}_lineage",
        provenance_reference=f"v4_1_{classification}_provenance",
        deterministic_order=deterministic_order,
        fail_visible=state != REPLAY_ROLLBACK_STATE_VISIBLE,
    )


def default_replay_rollback_evidence() -> tuple[ReplayRollbackEvidence, ...]:
    return (
        _evidence("v4_1_replay_manifest_visibility", VISIBILITY_TYPE_REPLAY, "manifest", "replay_manifest_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay manifest visibility is descriptive.", 10, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_manifest_visibility", VISIBILITY_TYPE_ROLLBACK, "manifest", "rollback_manifest_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback manifest visibility is descriptive.", 20, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_dependency_visibility", VISIBILITY_TYPE_REPLAY, "dependency", "replay_dependency_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay dependency visibility is descriptive.", 30, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_dependency_visibility", VISIBILITY_TYPE_ROLLBACK, "dependency", "rollback_dependency_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback dependency visibility is descriptive.", 40, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_lineage_visibility", VISIBILITY_TYPE_REPLAY, "lineage", "replay_lineage_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay lineage visibility is descriptive.", 50, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_lineage_visibility", VISIBILITY_TYPE_ROLLBACK, "lineage", "rollback_lineage_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback lineage visibility is descriptive.", 60, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_schema_visibility", VISIBILITY_TYPE_REPLAY, "schema", "replay_schema_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay schema visibility is descriptive.", 70, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_schema_visibility", VISIBILITY_TYPE_ROLLBACK, "schema", "rollback_schema_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback schema visibility is descriptive.", 80, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_sequencing_visibility", VISIBILITY_TYPE_REPLAY, "sequencing", "replay_sequencing_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay sequencing visibility is descriptive.", 90, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_sequencing_visibility", VISIBILITY_TYPE_ROLLBACK, "sequencing", "rollback_sequencing_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback sequencing visibility is descriptive.", 100, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_drift_visibility", VISIBILITY_TYPE_REPLAY, "drift", "replay_drift_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Replay drift visibility is descriptive.", 110, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_rollback_drift_visibility", VISIBILITY_TYPE_ROLLBACK, "drift", "rollback_drift_visibility", REPLAY_ROLLBACK_STATE_VISIBLE, "Rollback drift visibility is descriptive.", 120, REPLAY_ROLLBACK_SEVERITY_INFO),
        _evidence("v4_1_replay_drift_conflict", VISIBILITY_TYPE_REPLAY, "drift", "replay_drift_conflict", REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT, "Replay drift conflict is visible and not corrected.", 130, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_rollback_drift_conflict", VISIBILITY_TYPE_ROLLBACK, "drift", "rollback_drift_conflict", REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT, "Rollback drift conflict is visible and not corrected.", 140, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_replay_lineage_discontinuity", VISIBILITY_TYPE_REPLAY, "lineage", "replay_lineage_discontinuity", REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY, "Replay lineage discontinuity is visible and not repaired.", 150, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_rollback_lineage_discontinuity", VISIBILITY_TYPE_ROLLBACK, "lineage", "rollback_lineage_discontinuity", REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY, "Rollback lineage discontinuity is visible and not repaired.", 160, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_replay_provenance_discontinuity", VISIBILITY_TYPE_REPLAY, "provenance", "replay_provenance_discontinuity", REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY, "Replay provenance discontinuity is visible and not inferred.", 170, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_rollback_provenance_discontinuity", VISIBILITY_TYPE_ROLLBACK, "provenance", "rollback_provenance_discontinuity", REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY, "Rollback provenance discontinuity is visible and not inferred.", 180, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_replay_discontinuity", VISIBILITY_TYPE_REPLAY, "replay", "replay_discontinuity", REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY, "Replay continuity discontinuity is visible and not executed.", 190, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_rollback_discontinuity", VISIBILITY_TYPE_ROLLBACK, "rollback", "rollback_discontinuity", REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY, "Rollback continuity discontinuity is visible and not executed.", 200, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_replay_stale_evidence", VISIBILITY_TYPE_REPLAY, "replay", "stale_replay_evidence", REPLAY_ROLLBACK_STATE_STALE, "Stale replay evidence is visible and not suppressed.", 210),
        _evidence("v4_1_rollback_stale_evidence", VISIBILITY_TYPE_ROLLBACK, "rollback", "stale_rollback_evidence", REPLAY_ROLLBACK_STATE_STALE, "Stale rollback evidence is visible and not suppressed.", 220),
        _evidence("v4_1_replay_unsupported_provider", VISIBILITY_TYPE_REPLAY, "unsupported", "unsupported_replay_provider", REPLAY_ROLLBACK_STATE_UNSUPPORTED, "Unsupported replay provider is visible and not normalized.", 230),
        _evidence("v4_1_rollback_unsupported_provider", VISIBILITY_TYPE_ROLLBACK, "unsupported", "unsupported_rollback_provider", REPLAY_ROLLBACK_STATE_UNSUPPORTED, "Unsupported rollback provider is visible and not normalized.", 240),
        _evidence("v4_1_replay_prohibited_execution", VISIBILITY_TYPE_REPLAY, "prohibited", "prohibited_replay_execution", REPLAY_ROLLBACK_STATE_PROHIBITED, "Replay execution path is prohibited and visible.", 250, REPLAY_ROLLBACK_SEVERITY_PROHIBITED),
        _evidence("v4_1_rollback_prohibited_execution", VISIBILITY_TYPE_ROLLBACK, "prohibited", "prohibited_rollback_execution", REPLAY_ROLLBACK_STATE_PROHIBITED, "Rollback execution path is prohibited and visible.", 260, REPLAY_ROLLBACK_SEVERITY_PROHIBITED),
        _evidence("v4_1_replay_blocked_state", VISIBILITY_TYPE_REPLAY, "blocked", "blocked_replay_state", REPLAY_ROLLBACK_STATE_BLOCKED, "Blocked replay state is visible and not recovered.", 270, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
        _evidence("v4_1_rollback_blocked_state", VISIBILITY_TYPE_ROLLBACK, "blocked", "blocked_rollback_state", REPLAY_ROLLBACK_STATE_BLOCKED, "Blocked rollback state is visible and not recovered.", 280, REPLAY_ROLLBACK_SEVERITY_BLOCKED),
    )


def default_refresh_replay_rollback_visibility() -> RefreshReplayRollbackVisibility:
    identity = default_replay_rollback_identity()
    evidence = default_replay_rollback_evidence()
    return RefreshReplayRollbackVisibility(
        identity=identity,
        evidence=evidence,
        lineage_visibility=ReplayRollbackLineageVisibility(
            lineage_id=identity.lineage_reference,
            replay_lineage_references=("v4_1_replay_visibility_primary", identity.lineage_reference),
            rollback_lineage_references=("v4_1_rollback_visibility_primary", identity.lineage_reference),
            replay_lineage_discontinuity_visibility=("v4_1_replay_lineage_discontinuity",),
            rollback_lineage_discontinuity_visibility=("v4_1_rollback_lineage_discontinuity",),
            deterministic_order=10,
        ),
        provenance_visibility=ReplayRollbackProvenanceVisibility(
            provenance_id=identity.provenance_reference,
            replay_provenance_references=("v4_1_replay_provenance_primary", identity.provenance_reference),
            rollback_provenance_references=("v4_1_rollback_provenance_primary", identity.provenance_reference),
            inherited_from_references=(
                "v4_1_refresh_manifest_primary",
                "v4_1_refresh_dependency_graph_primary",
                "v4_1_refresh_lineage_certification_primary",
                "v4_1_schema_evolution_governance_primary",
                "v4_1_refresh_sequencing_visibility_primary",
                "v4_1_refresh_drift_certification_primary",
            ),
            replay_provenance_discontinuity_visibility=("v4_1_replay_provenance_discontinuity",),
            rollback_provenance_discontinuity_visibility=("v4_1_rollback_provenance_discontinuity",),
            deterministic_order=20,
        ),
        continuity_metadata=ReplayRollbackContinuityMetadata(
            continuity_id=identity.continuity_reference,
            replay_continuity_references=(identity.replay_reference,),
            rollback_continuity_references=(identity.rollback_reference,),
            replay_lineage_references=("v4_1_replay_lineage_discontinuity",),
            rollback_lineage_references=("v4_1_rollback_lineage_discontinuity",),
            replay_provenance_references=("v4_1_replay_provenance_discontinuity",),
            rollback_provenance_references=("v4_1_rollback_provenance_discontinuity",),
            dependency_continuity_references=("v4_1_refresh_dependency_graph_primary",),
            sequencing_continuity_references=("v4_1_refresh_sequencing_visibility_primary",),
            schema_continuity_references=("v4_1_schema_evolution_governance_primary",),
            drift_continuity_references=("v4_1_refresh_drift_certification_primary",),
            deterministic_order=30,
        ),
        drift_visibility=ReplayRollbackDriftVisibility(
            drift_id="v4_1_replay_rollback_drift_visibility_primary",
            replay_drift_conflict_ids=("v4_1_replay_drift_conflict",),
            rollback_drift_conflict_ids=("v4_1_rollback_drift_conflict",),
            stale_replay_ids=("v4_1_replay_stale_evidence",),
            stale_rollback_ids=("v4_1_rollback_stale_evidence",),
            deterministic_order=40,
        ),
        blocked_state_visibility=ReplayRollbackBlockedStateVisibility(
            blocked_id="v4_1_replay_rollback_blocked_state_visibility_primary",
            blocked_replay_ids=("v4_1_replay_blocked_state",),
            blocked_rollback_ids=("v4_1_rollback_blocked_state",),
            replay_discontinuity_visibility=("v4_1_replay_discontinuity",),
            rollback_discontinuity_visibility=("v4_1_rollback_discontinuity",),
            replay_lineage_discontinuity_visibility=("v4_1_replay_lineage_discontinuity",),
            rollback_lineage_discontinuity_visibility=("v4_1_rollback_lineage_discontinuity",),
            replay_provenance_discontinuity_visibility=("v4_1_replay_provenance_discontinuity",),
            rollback_provenance_discontinuity_visibility=("v4_1_rollback_provenance_discontinuity",),
            replay_drift_conflict_visibility=("v4_1_replay_drift_conflict",),
            rollback_drift_conflict_visibility=("v4_1_rollback_drift_conflict",),
            prohibited_remediation_leakage=("remediation_systems",),
            prohibited_recovery_leakage=("recovery_execution", "automatic_recovery"),
            prohibited_rollback_execution_leakage=("rollback_execution", "automatic_rollback"),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("replay_execution", "refresh_execution", "implicit_execution_pathways"),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=50,
        ),
        unsupported_state_visibility=ReplayRollbackUnsupportedStateVisibility(
            unsupported_id="v4_1_replay_rollback_unsupported_state_visibility_primary",
            unsupported_replay_ids=("v4_1_replay_unsupported_provider",),
            unsupported_rollback_ids=("v4_1_rollback_unsupported_provider",),
            unsupported_replay_providers=("unsupported_future_replay_provider",),
            unsupported_rollback_providers=("unsupported_future_rollback_provider",),
            stale_replay_ids=("v4_1_replay_stale_evidence",),
            stale_rollback_ids=("v4_1_rollback_stale_evidence",),
            prohibited_replay_ids=("v4_1_replay_prohibited_execution",),
            prohibited_rollback_ids=("v4_1_rollback_prohibited_execution",),
            prohibited_replay_domains=PROHIBITED_REPLAY_DOMAINS,
            prohibited_rollback_domains=PROHIBITED_ROLLBACK_DOMAINS,
            failure_visibility=(
                "unsupported replay provider remains fail-visible",
                "unsupported rollback provider remains fail-visible",
                "blocked replay state remains fail-visible",
                "blocked rollback state remains fail-visible",
            ),
            deterministic_order=60,
        ),
        diagnostics=ReplayRollbackDiagnostics(
            diagnostics_id=identity.diagnostics_reference,
            replay_diagnostic_references=("v4_1_replay_diagnostics_primary",),
            rollback_diagnostic_references=("v4_1_rollback_diagnostics_primary",),
            replay_warning_visibility=("v4_1_replay_stale_evidence", "v4_1_replay_unsupported_provider"),
            rollback_warning_visibility=("v4_1_rollback_stale_evidence", "v4_1_rollback_unsupported_provider"),
            replay_blocker_visibility=("v4_1_replay_blocked_state", "v4_1_replay_discontinuity"),
            rollback_blocker_visibility=("v4_1_rollback_blocked_state", "v4_1_rollback_discontinuity"),
            replay_integrity_visibility=("v4_1_replay_integrity_primary",),
            rollback_integrity_visibility=("v4_1_rollback_integrity_primary",),
            deterministic_order=70,
        ),
        governance=ReplayRollbackGovernance(
            governance_id=identity.governance_reference,
            governance_references=(identity.governance_reference, "v4_1_replay_rollback_boundary_primary"),
            explicit_limitations=EXPLICIT_REPLAY_ROLLBACK_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_REPLAY_ROLLBACK_PROHIBITIONS,
            deterministic_order=80,
        ),
    )
