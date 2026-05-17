"""Deterministic v4.1 refresh drift certification models.

Refresh drift certification is descriptive governance evidence only. It does
not remediate drift, correct drift, repair state, execute refreshes,
orchestrate work, sequence work, resolve dependencies, migrate schemas, roll
back state, recover state, consume production bundles, integrate with
planners, authorize behavior, or mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_DRIFT_CERTIFICATION_PHASE_ID = "v4_1_refresh_drift_certification"
V4_1_REFRESH_DRIFT_CERTIFICATION_SCHEMA_VERSION = "v4_1.refresh_drift_certification.1"
V4_1_REFRESH_DRIFT_CERTIFICATION_REPORT_SCHEMA_VERSION = "v4_1.refresh_drift_certification_report.1"
V4_1_REFRESH_DRIFT_DIAGNOSTICS_REPORT_SCHEMA_VERSION = "v4_1.refresh_drift_diagnostics_report.1"
V4_1_REFRESH_DRIFT_CONTINUITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_drift_continuity_report.1"
V4_1_REFRESH_DRIFT_INTEGRITY_REPORT_SCHEMA_VERSION = "v4_1.refresh_drift_integrity_report.1"
V4_1_CROSS_LAYER_DRIFT_REPORT_SCHEMA_VERSION = "v4_1.cross_layer_drift_certification_report.1"
V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE = "v4_1_refresh_drift_certification_stable"
V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_BLOCKED = "v4_1_refresh_drift_certification_blocked"
V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_DRIFT_CERTIFICATION_PURPOSE = "deterministic_refresh_drift_certification_governance_only"

DRIFT_LAYER_MANIFEST = "manifest"
DRIFT_LAYER_DEPENDENCY = "dependency"
DRIFT_LAYER_LINEAGE = "lineage"
DRIFT_LAYER_SCHEMA = "schema"
DRIFT_LAYER_SEQUENCING = "sequencing"
DRIFT_LAYERS: tuple[str, ...] = (
    DRIFT_LAYER_MANIFEST,
    DRIFT_LAYER_DEPENDENCY,
    DRIFT_LAYER_LINEAGE,
    DRIFT_LAYER_SCHEMA,
    DRIFT_LAYER_SEQUENCING,
)

DRIFT_STATE_VISIBLE = "visible"
DRIFT_STATE_CROSS_LAYER_CONFLICT = "cross_layer_conflict"
DRIFT_STATE_BLOCKED = "blocked"
DRIFT_STATE_UNSUPPORTED = "unsupported"
DRIFT_STATE_STALE = "stale"
DRIFT_STATE_PROHIBITED = "prohibited"
DRIFT_STATE_LINEAGE_DISCONTINUITY = "lineage_discontinuity"
DRIFT_STATE_PROVENANCE_DISCONTINUITY = "provenance_discontinuity"
DRIFT_STATE_REPLAY_DISCONTINUITY = "replay_discontinuity"
DRIFT_STATE_ROLLBACK_DISCONTINUITY = "rollback_discontinuity"
DRIFT_STATES: tuple[str, ...] = (
    DRIFT_STATE_VISIBLE,
    DRIFT_STATE_CROSS_LAYER_CONFLICT,
    DRIFT_STATE_BLOCKED,
    DRIFT_STATE_UNSUPPORTED,
    DRIFT_STATE_STALE,
    DRIFT_STATE_PROHIBITED,
    DRIFT_STATE_LINEAGE_DISCONTINUITY,
    DRIFT_STATE_PROVENANCE_DISCONTINUITY,
    DRIFT_STATE_REPLAY_DISCONTINUITY,
    DRIFT_STATE_ROLLBACK_DISCONTINUITY,
)
FAIL_VISIBLE_DRIFT_STATES: tuple[str, ...] = (
    DRIFT_STATE_CROSS_LAYER_CONFLICT,
    DRIFT_STATE_BLOCKED,
    DRIFT_STATE_UNSUPPORTED,
    DRIFT_STATE_STALE,
    DRIFT_STATE_PROHIBITED,
    DRIFT_STATE_LINEAGE_DISCONTINUITY,
    DRIFT_STATE_PROVENANCE_DISCONTINUITY,
    DRIFT_STATE_REPLAY_DISCONTINUITY,
    DRIFT_STATE_ROLLBACK_DISCONTINUITY,
)

DRIFT_SEVERITY_INFO = "info"
DRIFT_SEVERITY_WARNING = "warning"
DRIFT_SEVERITY_BLOCKED = "blocked"
DRIFT_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_DRIFT_DOMAINS: tuple[str, ...] = (
    "drift_remediation",
    "automatic_drift_correction",
    "automatic_repair",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "automatic_dependency_resolution",
    "schema_migration_execution",
    "automatic_migration",
    "automatic_rollback",
    "automatic_recovery",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_ranking_scoring_selection",
    "optimization_systems",
    "authorization_approval_systems",
    "runtime_mutation",
    "hidden_remediation_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_REFRESH_DRIFT_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 6 creates deterministic refresh drift certification metadata only.",
    "v4.1 Phase 6 does not enable drift remediation.",
    "v4.1 Phase 6 does not enable automatic correction.",
    "v4.1 Phase 6 does not enable orchestration execution.",
    "v4.1 Phase 6 does not enable automatic sequencing.",
    "v4.1 Phase 6 does not enable refresh execution.",
    "v4.1 Phase 6 does not enable migration execution.",
    "v4.1 Phase 6 does not enable planner integration.",
    "v4.1 Phase 6 does not enable production consumption.",
    "v4.1 Phase 6 does not enable mutation behavior.",
)

EXPLICIT_REFRESH_DRIFT_PROHIBITIONS: tuple[str, ...] = (
    "No drift remediation exists.",
    "No automatic correction exists.",
    "No automatic repair exists.",
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No mutation behavior exists.",
    "No executable drift repair system exists.",
    "No automatic correction planner exists.",
    "No remediation-capable diagnostics exist.",
    "No silent drift suppression exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshDriftCertificationIdentity:
    certification_id: str
    refresh_cycle_id: str
    certification_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    source_schema_governance_reference: str
    source_sequencing_reference: str
    schema_version: str
    generated_at: str
    drift_reference: str
    lineage_reference: str
    provenance_reference: str
    diagnostics_reference: str
    continuity_reference: str
    integrity_reference: str
    governance_reference: str
    certification_scope: str = "refresh_drift_certification_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_DRIFT_CERTIFICATION_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshDriftObservation:
    observation_id: str
    source_layer: str
    source_reference: str
    drift_reference: str
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
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_drift_suppression_enabled: bool = False


@dataclass(frozen=True)
class RefreshDriftLayerVisibility:
    visibility_id: str
    manifest_drift_ids: tuple[str, ...]
    dependency_drift_ids: tuple[str, ...]
    lineage_drift_ids: tuple[str, ...]
    schema_drift_ids: tuple[str, ...]
    sequencing_drift_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_drift_resolution_enabled: bool = False
    automatic_drift_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "manifest_drift_ids",
            "dependency_drift_ids",
            "lineage_drift_ids",
            "schema_drift_ids",
            "sequencing_drift_ids",
            "cross_layer_conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftClassificationVisibility:
    classification_id: str
    classification_references: tuple[str, ...]
    severity_references: tuple[str, ...]
    blocked_drift_ids: tuple[str, ...]
    unsupported_drift_ids: tuple[str, ...]
    stale_drift_ids: tuple[str, ...]
    prohibited_drift_ids: tuple[str, ...]
    unresolved_drift_ids: tuple[str, ...]
    deterministic_order: int
    classification_visible: bool = True
    severity_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_correction_enabled: bool = False
    hidden_classification_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "classification_references",
            "severity_references",
            "blocked_drift_ids",
            "unsupported_drift_ids",
            "stale_drift_ids",
            "prohibited_drift_ids",
            "unresolved_drift_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftContinuityMetadata:
    continuity_id: str
    drift_continuity_references: tuple[str, ...]
    dependency_continuity_references: tuple[str, ...]
    sequencing_continuity_references: tuple[str, ...]
    schema_continuity_references: tuple[str, ...]
    lineage_continuity_references: tuple[str, ...]
    provenance_continuity_references: tuple[str, ...]
    replay_drift_references: tuple[str, ...]
    rollback_drift_references: tuple[str, ...]
    deterministic_order: int
    drift_continuity_preserved: bool = True
    dependency_continuity_preserved: bool = True
    sequencing_continuity_preserved: bool = True
    schema_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    replay_drift_preserved: bool = True
    rollback_drift_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    descriptive_only: bool = True
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "drift_continuity_references",
            "dependency_continuity_references",
            "sequencing_continuity_references",
            "schema_continuity_references",
            "lineage_continuity_references",
            "provenance_continuity_references",
            "replay_drift_references",
            "rollback_drift_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftLineageVisibility:
    lineage_id: str
    lineage_references: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_repair_enabled: bool = False
    hidden_lineage_resolution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_references", "lineage_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftProvenanceVisibility:
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
class RefreshDriftReplayVisibility:
    replay_id: str
    replay_drift_references: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    live_replay_enabled: bool = False
    refresh_execution_enabled: bool = False
    correction_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_drift_references", "replay_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftRollbackVisibility:
    rollback_id: str
    rollback_drift_references: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    deterministic_order: int
    rollback_safe: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("rollback_drift_references", "rollback_discontinuity_visibility"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftBlockedStateVisibility:
    blocked_id: str
    blocked_drift_ids: tuple[str, ...]
    unresolved_drift_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    lineage_discontinuity_visibility: tuple[str, ...]
    provenance_discontinuity_visibility: tuple[str, ...]
    replay_discontinuity_visibility: tuple[str, ...]
    rollback_discontinuity_visibility: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_correction_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    remediation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_drift_suppression_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "blocked_drift_ids",
            "unresolved_drift_ids",
            "cross_layer_conflict_ids",
            "lineage_discontinuity_visibility",
            "provenance_discontinuity_visibility",
            "replay_discontinuity_visibility",
            "rollback_discontinuity_visibility",
            "prohibited_remediation_leakage",
            "prohibited_correction_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftUnsupportedStateVisibility:
    unsupported_id: str
    unsupported_drift_ids: tuple[str, ...]
    unsupported_drift_providers: tuple[str, ...]
    stale_drift_ids: tuple[str, ...]
    prohibited_drift_ids: tuple[str, ...]
    prohibited_drift_domains: tuple[str, ...]
    failure_visibility: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    fail_visible: bool = True
    hidden_unsupported_resolution_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    drift_remediation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "unsupported_drift_ids",
            "unsupported_drift_providers",
            "stale_drift_ids",
            "prohibited_drift_ids",
            "prohibited_drift_domains",
            "failure_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftDiagnostics:
    diagnostics_id: str
    diagnostic_references: tuple[str, ...]
    warning_visibility: tuple[str, ...]
    blocker_visibility: tuple[str, ...]
    unsupported_drift_visibility: tuple[str, ...]
    prohibited_drift_visibility: tuple[str, ...]
    cross_layer_conflict_visibility: tuple[str, ...]
    integrity_visibility: tuple[str, ...]
    deterministic_order: int
    diagnostics_visible: bool = True
    descriptive_only: bool = True
    fail_visible: bool = True
    remediation_enabled: bool = False
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    automatic_recovery_enabled: bool = False
    runtime_mutation_enabled: bool = False
    silent_drift_suppression_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "diagnostic_references",
            "warning_visibility",
            "blocker_visibility",
            "unsupported_drift_visibility",
            "prohibited_drift_visibility",
            "cross_layer_conflict_visibility",
            "integrity_visibility",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    governance_safe: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshDriftCertification:
    identity: RefreshDriftCertificationIdentity
    drift_observations: tuple[RefreshDriftObservation, ...]
    layer_visibility: RefreshDriftLayerVisibility
    classification_visibility: RefreshDriftClassificationVisibility
    continuity_metadata: RefreshDriftContinuityMetadata
    lineage_visibility: RefreshDriftLineageVisibility
    provenance_visibility: RefreshDriftProvenanceVisibility
    replay_visibility: RefreshDriftReplayVisibility
    rollback_visibility: RefreshDriftRollbackVisibility
    blocked_state_visibility: RefreshDriftBlockedStateVisibility
    unsupported_state_visibility: RefreshDriftUnsupportedStateVisibility
    diagnostics: RefreshDriftDiagnostics
    governance: RefreshDriftGovernance
    non_executable: bool = True
    descriptive_only: bool = True
    drift_remediation_enabled: bool = False
    automatic_drift_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    automatic_dependency_resolution_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    automatic_rollback_enabled: bool = False
    automatic_recovery_enabled: bool = False
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
    hidden_remediation_behavior_enabled: bool = False
    hidden_orchestration_behavior_enabled: bool = False
    implicit_execution_pathway_enabled: bool = False
    silent_drift_suppression_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "drift_observations")


def default_refresh_drift_certification_identity() -> RefreshDriftCertificationIdentity:
    return RefreshDriftCertificationIdentity(
        certification_id="v4_1_refresh_drift_certification_primary",
        refresh_cycle_id="v4_1_phase_6_refresh_drift_certification",
        certification_version="v4.1.0-phase-6",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        source_schema_governance_reference="v4_1_schema_evolution_governance_primary",
        source_sequencing_reference="v4_1_refresh_sequencing_visibility_primary",
        schema_version=V4_1_REFRESH_DRIFT_CERTIFICATION_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_DRIFT_CERTIFICATION_GENERATED_AT,
        drift_reference="v4_1_refresh_drift_certification_drift_primary",
        lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
        provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
        diagnostics_reference="v4_1_refresh_drift_certification_diagnostics_primary",
        continuity_reference="v4_1_refresh_drift_certification_continuity_primary",
        integrity_reference="v4_1_refresh_drift_certification_integrity_primary",
        governance_reference="v4_1_refresh_drift_certification_boundary_primary",
    )


def default_refresh_drift_observations() -> tuple[RefreshDriftObservation, ...]:
    return (
        RefreshDriftObservation(
            observation_id="v4_1_drift_manifest_visibility",
            source_layer=DRIFT_LAYER_MANIFEST,
            source_reference="v4_1_refresh_manifest_primary",
            drift_reference="manifest_field_visibility_drift",
            classification="manifest_drift",
            state=DRIFT_STATE_VISIBLE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Manifest drift is visible across refresh generations.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=10,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_dependency_visibility",
            source_layer=DRIFT_LAYER_DEPENDENCY,
            source_reference="v4_1_refresh_dependency_graph_primary",
            drift_reference="dependency_edge_visibility_drift",
            classification="dependency_drift",
            state=DRIFT_STATE_VISIBLE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Dependency drift is visible across dependency governance evidence.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=20,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_lineage_visibility",
            source_layer=DRIFT_LAYER_LINEAGE,
            source_reference="v4_1_refresh_lineage_certification_primary",
            drift_reference="lineage_ancestry_visibility_drift",
            classification="lineage_drift",
            state=DRIFT_STATE_VISIBLE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Lineage drift is visible across ancestry certification evidence.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=30,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_schema_visibility",
            source_layer=DRIFT_LAYER_SCHEMA,
            source_reference="v4_1_schema_evolution_governance_primary",
            drift_reference="schema_transition_visibility_drift",
            classification="schema_drift",
            state=DRIFT_STATE_VISIBLE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Schema drift is visible across schema evolution governance evidence.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=40,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_sequencing_visibility",
            source_layer=DRIFT_LAYER_SEQUENCING,
            source_reference="v4_1_refresh_sequencing_visibility_primary",
            drift_reference="sequencing_order_visibility_drift",
            classification="sequencing_drift",
            state=DRIFT_STATE_VISIBLE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Sequencing drift is visible across dependency-aware ordering evidence.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=50,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_cross_layer_conflict",
            source_layer="cross_layer",
            source_reference="v4_1_refresh_governance_stack",
            drift_reference="cross_layer_drift_conflict_visibility",
            classification="cross_layer_drift_conflict",
            state=DRIFT_STATE_CROSS_LAYER_CONFLICT,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Cross-layer drift conflict remains blocked and visible.",
            lineage_reference="v4_1_cross_layer_conflict_lineage",
            provenance_reference="v4_1_cross_layer_conflict_provenance",
            deterministic_order=60,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_stale_evidence",
            source_layer=DRIFT_LAYER_SCHEMA,
            source_reference="v4_1_schema_evolution_governance_primary",
            drift_reference="stale_schema_drift_evidence",
            classification="stale_drift_evidence",
            state=DRIFT_STATE_STALE,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Stale drift evidence is visible and not suppressed.",
            lineage_reference="v4_1_stale_drift_lineage",
            provenance_reference="v4_1_stale_drift_provenance",
            deterministic_order=70,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_unsupported_provider",
            source_layer="unsupported",
            source_reference="unsupported_future_drift_provider",
            drift_reference="unsupported_future_drift_evidence",
            classification="unsupported_drift_provider",
            state=DRIFT_STATE_UNSUPPORTED,
            severity=DRIFT_SEVERITY_WARNING,
            reason="Unsupported drift provider is visible and not normalized.",
            lineage_reference="v4_1_unsupported_drift_lineage",
            provenance_reference="v4_1_unsupported_drift_provenance",
            deterministic_order=80,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_prohibited_remediation",
            source_layer="prohibited",
            source_reference="prohibited_drift_remediation_provider",
            drift_reference="prohibited_remediation_drift_evidence",
            classification="prohibited_drift_remediation",
            state=DRIFT_STATE_PROHIBITED,
            severity=DRIFT_SEVERITY_PROHIBITED,
            reason="Remediation-capable drift path is prohibited and visible.",
            lineage_reference="v4_1_prohibited_drift_lineage",
            provenance_reference="v4_1_prohibited_drift_provenance",
            deterministic_order=90,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_blocked_unresolved",
            source_layer="cross_layer",
            source_reference="v4_1_refresh_governance_stack",
            drift_reference="blocked_unresolved_drift_evidence",
            classification="blocked_unresolved_drift",
            state=DRIFT_STATE_BLOCKED,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Unresolved drift remains blocked and fail-visible.",
            lineage_reference="v4_1_blocked_drift_lineage",
            provenance_reference="v4_1_blocked_drift_provenance",
            deterministic_order=100,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_lineage_discontinuity",
            source_layer=DRIFT_LAYER_LINEAGE,
            source_reference="v4_1_refresh_lineage_certification_primary",
            drift_reference="drift_lineage_discontinuity",
            classification="lineage_discontinuity",
            state=DRIFT_STATE_LINEAGE_DISCONTINUITY,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Drift lineage discontinuity is visible and not repaired.",
            lineage_reference="v4_1_drift_lineage_gap_reference",
            provenance_reference="v4_1_refresh_drift_certification_provenance_primary",
            deterministic_order=110,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_provenance_discontinuity",
            source_layer=DRIFT_LAYER_DEPENDENCY,
            source_reference="v4_1_refresh_dependency_graph_primary",
            drift_reference="drift_provenance_discontinuity",
            classification="provenance_discontinuity",
            state=DRIFT_STATE_PROVENANCE_DISCONTINUITY,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Drift provenance discontinuity is visible and not inferred.",
            lineage_reference="v4_1_refresh_drift_certification_lineage_primary",
            provenance_reference="v4_1_drift_provenance_gap_reference",
            deterministic_order=120,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_replay_discontinuity",
            source_layer=DRIFT_LAYER_SEQUENCING,
            source_reference="v4_1_refresh_sequencing_visibility_primary",
            drift_reference="drift_replay_discontinuity",
            classification="replay_discontinuity",
            state=DRIFT_STATE_REPLAY_DISCONTINUITY,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Drift replay discontinuity is visible and not executed.",
            lineage_reference="v4_1_drift_replay_gap_lineage",
            provenance_reference="v4_1_drift_replay_gap_provenance",
            deterministic_order=130,
            fail_visible=True,
        ),
        RefreshDriftObservation(
            observation_id="v4_1_drift_rollback_discontinuity",
            source_layer=DRIFT_LAYER_SEQUENCING,
            source_reference="v4_1_refresh_sequencing_visibility_primary",
            drift_reference="drift_rollback_discontinuity",
            classification="rollback_discontinuity",
            state=DRIFT_STATE_ROLLBACK_DISCONTINUITY,
            severity=DRIFT_SEVERITY_BLOCKED,
            reason="Drift rollback discontinuity is visible and not recovered.",
            lineage_reference="v4_1_drift_rollback_gap_lineage",
            provenance_reference="v4_1_drift_rollback_gap_provenance",
            deterministic_order=140,
            fail_visible=True,
        ),
    )


def default_refresh_drift_certification() -> RefreshDriftCertification:
    identity = default_refresh_drift_certification_identity()
    observations = default_refresh_drift_observations()
    return RefreshDriftCertification(
        identity=identity,
        drift_observations=observations,
        layer_visibility=RefreshDriftLayerVisibility(
            visibility_id="v4_1_refresh_drift_layer_visibility_primary",
            manifest_drift_ids=("v4_1_drift_manifest_visibility",),
            dependency_drift_ids=("v4_1_drift_dependency_visibility", "v4_1_drift_provenance_discontinuity"),
            lineage_drift_ids=("v4_1_drift_lineage_visibility", "v4_1_drift_lineage_discontinuity"),
            schema_drift_ids=("v4_1_drift_schema_visibility", "v4_1_drift_stale_evidence"),
            sequencing_drift_ids=(
                "v4_1_drift_sequencing_visibility",
                "v4_1_drift_replay_discontinuity",
                "v4_1_drift_rollback_discontinuity",
            ),
            cross_layer_conflict_ids=("v4_1_drift_cross_layer_conflict",),
            deterministic_order=10,
        ),
        classification_visibility=RefreshDriftClassificationVisibility(
            classification_id="v4_1_refresh_drift_classification_visibility_primary",
            classification_references=tuple(observation.classification for observation in observations),
            severity_references=tuple(observation.severity for observation in observations),
            blocked_drift_ids=("v4_1_drift_blocked_unresolved",),
            unsupported_drift_ids=("v4_1_drift_unsupported_provider",),
            stale_drift_ids=("v4_1_drift_stale_evidence",),
            prohibited_drift_ids=("v4_1_drift_prohibited_remediation",),
            unresolved_drift_ids=("v4_1_drift_cross_layer_conflict", "v4_1_drift_blocked_unresolved"),
            deterministic_order=20,
        ),
        continuity_metadata=RefreshDriftContinuityMetadata(
            continuity_id="v4_1_refresh_drift_continuity_primary",
            drift_continuity_references=(identity.drift_reference,),
            dependency_continuity_references=("v4_1_refresh_dependency_graph_primary",),
            sequencing_continuity_references=("v4_1_refresh_sequencing_visibility_primary",),
            schema_continuity_references=("v4_1_schema_evolution_governance_primary",),
            lineage_continuity_references=(identity.lineage_reference,),
            provenance_continuity_references=(identity.provenance_reference,),
            replay_drift_references=("v4_1_refresh_drift_replay_visibility_primary",),
            rollback_drift_references=("v4_1_refresh_drift_rollback_visibility_primary",),
            deterministic_order=30,
        ),
        lineage_visibility=RefreshDriftLineageVisibility(
            lineage_id=identity.lineage_reference,
            lineage_references=(
                "v4_1_refresh_manifest_lineage_primary",
                "v4_1_refresh_dependency_graph_lineage_primary",
                "v4_1_refresh_lineage_certification_lineage_primary",
                "v4_1_schema_evolution_governance_lineage_primary",
                "v4_1_refresh_sequencing_visibility_lineage_primary",
                identity.lineage_reference,
            ),
            lineage_discontinuity_visibility=("v4_1_drift_lineage_discontinuity",),
            deterministic_order=40,
        ),
        provenance_visibility=RefreshDriftProvenanceVisibility(
            provenance_id=identity.provenance_reference,
            provenance_references=(
                "v4_1_refresh_manifest_provenance_primary",
                "v4_1_refresh_dependency_graph_provenance_primary",
                "v4_1_refresh_lineage_certification_provenance_primary",
                "v4_1_schema_evolution_governance_provenance_primary",
                "v4_1_refresh_sequencing_visibility_provenance_primary",
                identity.provenance_reference,
            ),
            inherited_from_references=(
                "v4_1_refresh_manifest_primary",
                "v4_1_refresh_dependency_graph_primary",
                "v4_1_refresh_lineage_certification_primary",
                "v4_1_schema_evolution_governance_primary",
                "v4_1_refresh_sequencing_visibility_primary",
            ),
            provenance_discontinuity_visibility=("v4_1_drift_provenance_discontinuity",),
            deterministic_order=50,
        ),
        replay_visibility=RefreshDriftReplayVisibility(
            replay_id="v4_1_refresh_drift_replay_visibility_primary",
            replay_drift_references=("v4_1_drift_replay_evidence_primary",),
            replay_discontinuity_visibility=("v4_1_drift_replay_discontinuity",),
            deterministic_order=60,
        ),
        rollback_visibility=RefreshDriftRollbackVisibility(
            rollback_id="v4_1_refresh_drift_rollback_visibility_primary",
            rollback_drift_references=("v4_1_drift_rollback_evidence_primary",),
            rollback_discontinuity_visibility=("v4_1_drift_rollback_discontinuity",),
            deterministic_order=70,
        ),
        blocked_state_visibility=RefreshDriftBlockedStateVisibility(
            blocked_id="v4_1_refresh_drift_blocked_state_visibility_primary",
            blocked_drift_ids=("v4_1_drift_blocked_unresolved",),
            unresolved_drift_ids=("v4_1_drift_cross_layer_conflict", "v4_1_drift_blocked_unresolved"),
            cross_layer_conflict_ids=("v4_1_drift_cross_layer_conflict",),
            lineage_discontinuity_visibility=("v4_1_drift_lineage_discontinuity",),
            provenance_discontinuity_visibility=("v4_1_drift_provenance_discontinuity",),
            replay_discontinuity_visibility=("v4_1_drift_replay_discontinuity",),
            rollback_discontinuity_visibility=("v4_1_drift_rollback_discontinuity",),
            prohibited_remediation_leakage=("drift_remediation", "remediation_capable_diagnostics"),
            prohibited_correction_leakage=("automatic_drift_correction", "automatic_repair"),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("refresh_execution", "implicit_execution_pathways"),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=80,
        ),
        unsupported_state_visibility=RefreshDriftUnsupportedStateVisibility(
            unsupported_id="v4_1_refresh_drift_unsupported_state_visibility_primary",
            unsupported_drift_ids=("v4_1_drift_unsupported_provider",),
            unsupported_drift_providers=("unsupported_future_drift_provider",),
            stale_drift_ids=("v4_1_drift_stale_evidence",),
            prohibited_drift_ids=("v4_1_drift_prohibited_remediation",),
            prohibited_drift_domains=PROHIBITED_DRIFT_DOMAINS,
            failure_visibility=(
                "unsupported drift provider remains fail-visible",
                "cross-layer drift conflict remains fail-visible",
                "blocked unresolved drift remains fail-visible",
                "stale drift evidence remains fail-visible",
            ),
            deterministic_order=90,
        ),
        diagnostics=RefreshDriftDiagnostics(
            diagnostics_id="v4_1_refresh_drift_diagnostics_primary",
            diagnostic_references=(
                "v4_1_refresh_drift_layer_visibility_primary",
                "v4_1_refresh_drift_classification_visibility_primary",
                "v4_1_refresh_drift_blocked_state_visibility_primary",
                "v4_1_refresh_drift_unsupported_state_visibility_primary",
            ),
            warning_visibility=(
                "v4_1_drift_manifest_visibility",
                "v4_1_drift_dependency_visibility",
                "v4_1_drift_lineage_visibility",
                "v4_1_drift_schema_visibility",
                "v4_1_drift_sequencing_visibility",
                "v4_1_drift_stale_evidence",
                "v4_1_drift_unsupported_provider",
            ),
            blocker_visibility=(
                "v4_1_drift_cross_layer_conflict",
                "v4_1_drift_blocked_unresolved",
                "v4_1_drift_lineage_discontinuity",
                "v4_1_drift_provenance_discontinuity",
            ),
            unsupported_drift_visibility=("v4_1_drift_unsupported_provider",),
            prohibited_drift_visibility=("v4_1_drift_prohibited_remediation",),
            cross_layer_conflict_visibility=("v4_1_drift_cross_layer_conflict",),
            integrity_visibility=("v4_1_refresh_drift_integrity_primary",),
            deterministic_order=100,
        ),
        governance=RefreshDriftGovernance(
            governance_id=identity.governance_reference,
            governance_references=(identity.governance_reference, "v4_1_refresh_drift_certification_boundary_primary"),
            explicit_limitations=EXPLICIT_REFRESH_DRIFT_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_REFRESH_DRIFT_PROHIBITIONS,
            deterministic_order=110,
        ),
    )
