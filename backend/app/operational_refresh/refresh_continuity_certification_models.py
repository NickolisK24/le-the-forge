"""Deterministic v4.1 refresh continuity certification models.

Continuity certification is descriptive governance evidence only. It does not
remediate, correct, repair, recommend, rank, score, select, approve, authorize,
execute refreshes, orchestrate work, sequence work, migrate schemas, roll back
state, recover state, consume production bundles, integrate with planners, or
mutate runtime data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_1_REFRESH_CONTINUITY_CERTIFICATION_PHASE_ID = "v4_1_refresh_continuity_certification"
V4_1_REFRESH_CONTINUITY_CERTIFICATION_SCHEMA_VERSION = "v4_1.refresh_continuity_certification.1"
V4_1_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION = (
    "v4_1.refresh_continuity_certification_report.1"
)
V4_1_UNIFIED_REFRESH_CONTINUITY_CERTIFICATION_REPORT_SCHEMA_VERSION = (
    "v4_1.unified_refresh_continuity_certification_report.1"
)
V4_1_CROSS_LAYER_CONTINUITY_DIAGNOSTICS_REPORT_SCHEMA_VERSION = (
    "v4_1.cross_layer_continuity_diagnostics_report.1"
)
V4_1_CROSS_LAYER_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION = (
    "v4_1.cross_layer_continuity_integrity_report.1"
)
V4_1_CROSS_LAYER_CONTINUITY_EXPLAINABILITY_REPORT_SCHEMA_VERSION = (
    "v4_1.cross_layer_continuity_explainability_report.1"
)
V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_STABLE = "v4_1_refresh_continuity_certification_stable"
V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_BLOCKED = "v4_1_refresh_continuity_certification_blocked"
V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT = "2026-05-17T00:00:00+00:00"
V4_1_REFRESH_CONTINUITY_CERTIFICATION_PURPOSE = (
    "deterministic_refresh_continuity_certification_governance_only"
)

CONTINUITY_LAYER_MANIFEST = "manifest"
CONTINUITY_LAYER_DEPENDENCY = "dependency"
CONTINUITY_LAYER_LINEAGE = "lineage"
CONTINUITY_LAYER_SCHEMA = "schema"
CONTINUITY_LAYER_SEQUENCING = "sequencing"
CONTINUITY_LAYER_DRIFT = "drift"
CONTINUITY_LAYER_REPLAY = "replay"
CONTINUITY_LAYER_ROLLBACK = "rollback"
CONTINUITY_LAYER_DIAGNOSTICS = "diagnostics"
CONTINUITY_LAYER_EXPLAINABILITY = "explainability"
CONTINUITY_LAYERS: tuple[str, ...] = (
    CONTINUITY_LAYER_MANIFEST,
    CONTINUITY_LAYER_DEPENDENCY,
    CONTINUITY_LAYER_LINEAGE,
    CONTINUITY_LAYER_SCHEMA,
    CONTINUITY_LAYER_SEQUENCING,
    CONTINUITY_LAYER_DRIFT,
    CONTINUITY_LAYER_REPLAY,
    CONTINUITY_LAYER_ROLLBACK,
    CONTINUITY_LAYER_DIAGNOSTICS,
    CONTINUITY_LAYER_EXPLAINABILITY,
)

CONTINUITY_STATE_PRESERVED = "continuity_preserved"
CONTINUITY_STATE_FAILURE = "continuity_failure"
CONTINUITY_STATE_UNSUPPORTED = "unsupported_continuity_state"
CONTINUITY_STATE_BLOCKED = "blocked_continuity_state"
CONTINUITY_STATE_PROHIBITED = "prohibited_continuity_state"
CONTINUITY_STATE_STALE = "stale_continuity_evidence"
CONTINUITY_STATE_CROSS_LAYER_CONFLICT = "cross_layer_continuity_conflict"
CONTINUITY_STATES: tuple[str, ...] = (
    CONTINUITY_STATE_PRESERVED,
    CONTINUITY_STATE_FAILURE,
    CONTINUITY_STATE_UNSUPPORTED,
    CONTINUITY_STATE_BLOCKED,
    CONTINUITY_STATE_PROHIBITED,
    CONTINUITY_STATE_STALE,
    CONTINUITY_STATE_CROSS_LAYER_CONFLICT,
)
FAIL_VISIBLE_CONTINUITY_STATES: tuple[str, ...] = tuple(
    state for state in CONTINUITY_STATES if state != CONTINUITY_STATE_PRESERVED
)

CONTINUITY_SEVERITY_INFO = "info"
CONTINUITY_SEVERITY_WARNING = "warning"
CONTINUITY_SEVERITY_BLOCKED = "blocked"
CONTINUITY_SEVERITY_PROHIBITED = "prohibited"

PROHIBITED_CONTINUITY_DOMAINS: tuple[str, ...] = (
    "remediation",
    "automatic_correction",
    "automatic_repair",
    "refresh_execution",
    "orchestration_execution",
    "automatic_sequencing",
    "dependency_resolution",
    "schema_migration_execution",
    "automatic_migration",
    "rollback_execution",
    "recovery_execution",
    "planner_integration",
    "production_bundle_consumption",
    "recommendation_systems",
    "ranking_systems",
    "scoring_systems",
    "selection_systems",
    "optimization_systems",
    "authorization_systems",
    "approval_systems",
    "runtime_mutation",
    "hidden_remediation_behavior",
    "hidden_orchestration_behavior",
    "implicit_execution_pathways",
)

EXPLICIT_CONTINUITY_CERTIFICATION_LIMITATIONS: tuple[str, ...] = (
    "v4.1 Phase 9 creates deterministic refresh continuity certification metadata only.",
    "v4.1 Phase 9 does not enable remediation.",
    "v4.1 Phase 9 does not enable automatic correction.",
    "v4.1 Phase 9 does not enable recommendation ranking scoring or selection.",
    "v4.1 Phase 9 does not enable approval or authorization.",
    "v4.1 Phase 9 does not enable orchestration execution.",
    "v4.1 Phase 9 does not enable automatic sequencing.",
    "v4.1 Phase 9 does not enable refresh execution.",
    "v4.1 Phase 9 does not enable migration execution.",
    "v4.1 Phase 9 does not enable recovery execution.",
    "v4.1 Phase 9 does not enable rollback execution.",
    "v4.1 Phase 9 does not enable planner integration.",
    "v4.1 Phase 9 does not enable production consumption.",
    "v4.1 Phase 9 does not enable mutation behavior.",
)

EXPLICIT_CONTINUITY_CERTIFICATION_PROHIBITIONS: tuple[str, ...] = (
    "No remediation exists.",
    "No automatic correction exists.",
    "No recommendation ranking scoring or selection exists.",
    "No approval or authorization exists.",
    "No orchestration execution exists.",
    "No automatic sequencing exists.",
    "No refresh execution exists.",
    "No migration execution exists.",
    "No recovery execution exists.",
    "No rollback execution exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No mutation behavior exists.",
    "No continuity certification becomes operational authorization.",
    "No continuity certification implies approval capability.",
    "No automatic continuity correction exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class RefreshContinuityCertificationIdentity:
    continuity_id: str
    refresh_cycle_id: str
    certification_version: str
    source_manifest_reference: str
    source_dependency_graph_reference: str
    source_lineage_certification_reference: str
    source_schema_governance_reference: str
    source_sequencing_reference: str
    source_drift_certification_reference: str
    source_replay_rollback_reference: str
    source_diagnostics_explainability_reference: str
    schema_version: str
    generated_at: str
    lineage_reference: str
    provenance_reference: str
    replay_reference: str
    rollback_reference: str
    diagnostics_reference: str
    explainability_reference: str
    integrity_reference: str
    governance_reference: str
    governance_scope: str = "refresh_continuity_certification_descriptive_only"
    governance_purpose: str = V4_1_REFRESH_CONTINUITY_CERTIFICATION_PURPOSE
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden_fallback_enabled: bool = False


@dataclass(frozen=True)
class RefreshContinuityCertificationEntry:
    certification_id: str
    layer: str
    source_reference: str
    state: str
    severity: str
    explanation: str
    continuity_reference: str
    lineage_reference: str
    provenance_reference: str
    replay_reference: str
    rollback_reference: str
    diagnostics_reference: str
    explainability_reference: str
    deterministic_order: int
    fail_visible: bool = False
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    hidden: bool = False


@dataclass(frozen=True)
class CrossLayerContinuityAggregation:
    aggregation_id: str
    manifest_certification_ids: tuple[str, ...]
    dependency_certification_ids: tuple[str, ...]
    lineage_certification_ids: tuple[str, ...]
    schema_certification_ids: tuple[str, ...]
    sequencing_certification_ids: tuple[str, ...]
    drift_certification_ids: tuple[str, ...]
    replay_certification_ids: tuple[str, ...]
    rollback_certification_ids: tuple[str, ...]
    diagnostics_certification_ids: tuple[str, ...]
    explainability_certification_ids: tuple[str, ...]
    continuity_failure_ids: tuple[str, ...]
    unsupported_continuity_ids: tuple[str, ...]
    blocked_continuity_ids: tuple[str, ...]
    prohibited_continuity_ids: tuple[str, ...]
    stale_continuity_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "manifest_certification_ids",
            "dependency_certification_ids",
            "lineage_certification_ids",
            "schema_certification_ids",
            "sequencing_certification_ids",
            "drift_certification_ids",
            "replay_certification_ids",
            "rollback_certification_ids",
            "diagnostics_certification_ids",
            "explainability_certification_ids",
            "continuity_failure_ids",
            "unsupported_continuity_ids",
            "blocked_continuity_ids",
            "prohibited_continuity_ids",
            "stale_continuity_ids",
            "cross_layer_conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityMetadata:
    continuity_id: str
    continuity_certification_references: tuple[str, ...]
    manifest_references: tuple[str, ...]
    dependency_references: tuple[str, ...]
    lineage_references: tuple[str, ...]
    schema_references: tuple[str, ...]
    sequencing_references: tuple[str, ...]
    drift_references: tuple[str, ...]
    replay_references: tuple[str, ...]
    rollback_references: tuple[str, ...]
    diagnostics_references: tuple[str, ...]
    explainability_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    deterministic_order: int
    manifest_continuity_preserved: bool = True
    dependency_continuity_preserved: bool = True
    lineage_continuity_preserved: bool = True
    schema_continuity_preserved: bool = True
    sequencing_continuity_preserved: bool = True
    drift_continuity_preserved: bool = True
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    diagnostics_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    continuity_failure_visibility_preserved: bool = True
    cross_layer_continuity_visibility_preserved: bool = True
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_certification_references",
            "manifest_references",
            "dependency_references",
            "lineage_references",
            "schema_references",
            "sequencing_references",
            "drift_references",
            "replay_references",
            "rollback_references",
            "diagnostics_references",
            "explainability_references",
            "provenance_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityDiagnostics:
    diagnostics_id: str
    certification_references: tuple[str, ...]
    failure_visibility_ids: tuple[str, ...]
    unsupported_visibility_ids: tuple[str, ...]
    blocked_visibility_ids: tuple[str, ...]
    prohibited_visibility_ids: tuple[str, ...]
    stale_visibility_ids: tuple[str, ...]
    cross_layer_conflict_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "certification_references",
            "failure_visibility_ids",
            "unsupported_visibility_ids",
            "blocked_visibility_ids",
            "prohibited_visibility_ids",
            "stale_visibility_ids",
            "cross_layer_conflict_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityExplainability:
    explainability_id: str
    limitation_explanation_ids: tuple[str, ...]
    prohibited_explanation_ids: tuple[str, ...]
    unsupported_explanation_ids: tuple[str, ...]
    blocked_explanation_ids: tuple[str, ...]
    failure_explanation_ids: tuple[str, ...]
    cross_layer_explanation_ids: tuple[str, ...]
    explanation_texts: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    execution_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "limitation_explanation_ids",
            "prohibited_explanation_ids",
            "unsupported_explanation_ids",
            "blocked_explanation_ids",
            "failure_explanation_ids",
            "cross_layer_explanation_ids",
            "explanation_texts",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityIntegrityBoundary:
    boundary_id: str
    prohibited_continuity_domains: tuple[str, ...]
    prohibited_remediation_leakage: tuple[str, ...]
    prohibited_correction_leakage: tuple[str, ...]
    prohibited_recommendation_leakage: tuple[str, ...]
    prohibited_ranking_leakage: tuple[str, ...]
    prohibited_scoring_leakage: tuple[str, ...]
    prohibited_selection_leakage: tuple[str, ...]
    prohibited_approval_leakage: tuple[str, ...]
    prohibited_authorization_leakage: tuple[str, ...]
    prohibited_orchestration_leakage: tuple[str, ...]
    prohibited_execution_leakage: tuple[str, ...]
    prohibited_planner_integration_leakage: tuple[str, ...]
    prohibited_production_consumption_leakage: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "prohibited_continuity_domains",
            "prohibited_remediation_leakage",
            "prohibited_correction_leakage",
            "prohibited_recommendation_leakage",
            "prohibited_ranking_leakage",
            "prohibited_scoring_leakage",
            "prohibited_selection_leakage",
            "prohibited_approval_leakage",
            "prohibited_authorization_leakage",
            "prohibited_orchestration_leakage",
            "prohibited_execution_leakage",
            "prohibited_planner_integration_leakage",
            "prohibited_production_consumption_leakage",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityGovernance:
    governance_id: str
    governance_references: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_executable: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    approval_enabled: bool = False
    authorization_enabled: bool = False
    orchestration_enabled: bool = False
    execution_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class RefreshContinuityCertification:
    identity: RefreshContinuityCertificationIdentity
    certifications: tuple[RefreshContinuityCertificationEntry, ...]
    cross_layer_aggregation: CrossLayerContinuityAggregation
    continuity_metadata: RefreshContinuityMetadata
    diagnostics: RefreshContinuityDiagnostics
    explainability: RefreshContinuityExplainability
    integrity_boundary: RefreshContinuityIntegrityBoundary
    governance: RefreshContinuityGovernance
    non_executable: bool = True
    descriptive_only: bool = True
    remediation_enabled: bool = False
    automatic_correction_enabled: bool = False
    automatic_repair_enabled: bool = False
    refresh_execution_enabled: bool = False
    orchestration_enabled: bool = False
    automatic_sequencing_enabled: bool = False
    dependency_resolution_enabled: bool = False
    schema_migration_execution_enabled: bool = False
    automatic_migration_enabled: bool = False
    rollback_execution_enabled: bool = False
    recovery_execution_enabled: bool = False
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

    def __post_init__(self) -> None:
        _set_tuple_field(self, "certifications")


def default_refresh_continuity_certification_identity() -> RefreshContinuityCertificationIdentity:
    return RefreshContinuityCertificationIdentity(
        continuity_id="v4_1_refresh_continuity_certification_primary",
        refresh_cycle_id="v4_1_phase_9_refresh_continuity_certification",
        certification_version="v4.1.0-phase-9",
        source_manifest_reference="v4_1_refresh_manifest_primary",
        source_dependency_graph_reference="v4_1_refresh_dependency_graph_primary",
        source_lineage_certification_reference="v4_1_refresh_lineage_certification_primary",
        source_schema_governance_reference="v4_1_schema_evolution_governance_primary",
        source_sequencing_reference="v4_1_refresh_sequencing_visibility_primary",
        source_drift_certification_reference="v4_1_refresh_drift_certification_primary",
        source_replay_rollback_reference="v4_1_refresh_replay_rollback_visibility_primary",
        source_diagnostics_explainability_reference="v4_1_refresh_diagnostics_explainability_primary",
        schema_version=V4_1_REFRESH_CONTINUITY_CERTIFICATION_SCHEMA_VERSION,
        generated_at=V4_1_REFRESH_CONTINUITY_CERTIFICATION_GENERATED_AT,
        lineage_reference="v4_1_refresh_continuity_lineage_primary",
        provenance_reference="v4_1_refresh_continuity_provenance_primary",
        replay_reference="v4_1_refresh_continuity_replay_primary",
        rollback_reference="v4_1_refresh_continuity_rollback_primary",
        diagnostics_reference="v4_1_refresh_continuity_diagnostics_primary",
        explainability_reference="v4_1_refresh_continuity_explainability_primary",
        integrity_reference="v4_1_refresh_continuity_integrity_primary",
        governance_reference="v4_1_refresh_continuity_governance_primary",
    )


def _continuity_entry(
    certification_id: str,
    layer: str,
    state: str,
    severity: str,
    explanation: str,
    deterministic_order: int,
) -> RefreshContinuityCertificationEntry:
    return RefreshContinuityCertificationEntry(
        certification_id=certification_id,
        layer=layer,
        source_reference=f"v4_1_{layer}_continuity_reference",
        state=state,
        severity=severity,
        explanation=explanation,
        continuity_reference=f"v4_1_{certification_id}_continuity",
        lineage_reference=f"v4_1_{certification_id}_lineage",
        provenance_reference=f"v4_1_{certification_id}_provenance",
        replay_reference=f"v4_1_{certification_id}_replay",
        rollback_reference=f"v4_1_{certification_id}_rollback",
        diagnostics_reference=f"v4_1_{certification_id}_diagnostics",
        explainability_reference=f"v4_1_{certification_id}_explainability",
        deterministic_order=deterministic_order,
        fail_visible=state in FAIL_VISIBLE_CONTINUITY_STATES,
    )


def default_refresh_continuity_certification_entries() -> tuple[RefreshContinuityCertificationEntry, ...]:
    preserved = tuple(
        _continuity_entry(
            certification_id=f"v4_1_{layer}_continuity_certified",
            layer=layer,
            state=CONTINUITY_STATE_PRESERVED,
            severity=CONTINUITY_SEVERITY_INFO,
            explanation=f"{layer} continuity is certified as descriptive governance evidence.",
            deterministic_order=(index + 1) * 10,
        )
        for index, layer in enumerate(CONTINUITY_LAYERS)
    )
    failures = tuple(
        _continuity_entry(
            certification_id=f"v4_1_{layer}_continuity_failure_visible",
            layer=layer,
            state=CONTINUITY_STATE_FAILURE,
            severity=CONTINUITY_SEVERITY_BLOCKED,
            explanation=f"{layer} continuity failure remains fail-visible and is not repaired.",
            deterministic_order=200 + (index + 1) * 10,
        )
        for index, layer in enumerate(CONTINUITY_LAYERS)
    )
    return (
        *preserved,
        *failures,
        _continuity_entry(
            "v4_1_unsupported_continuity_provider",
            "unsupported",
            CONTINUITY_STATE_UNSUPPORTED,
            CONTINUITY_SEVERITY_WARNING,
            "Unsupported continuity provider remains fail-visible.",
            320,
        ),
        _continuity_entry(
            "v4_1_blocked_continuity_state",
            "blocked",
            CONTINUITY_STATE_BLOCKED,
            CONTINUITY_SEVERITY_BLOCKED,
            "Blocked continuity state remains visible and is not remediated.",
            330,
        ),
        _continuity_entry(
            "v4_1_prohibited_continuity_domain",
            "prohibited",
            CONTINUITY_STATE_PROHIBITED,
            CONTINUITY_SEVERITY_PROHIBITED,
            "Prohibited continuity domain remains visible and inactive.",
            340,
        ),
        _continuity_entry(
            "v4_1_stale_continuity_evidence",
            "stale",
            CONTINUITY_STATE_STALE,
            CONTINUITY_SEVERITY_WARNING,
            "Stale continuity evidence remains visible and is not suppressed.",
            350,
        ),
        _continuity_entry(
            "v4_1_cross_layer_continuity_conflict",
            "cross_layer",
            CONTINUITY_STATE_CROSS_LAYER_CONFLICT,
            CONTINUITY_SEVERITY_BLOCKED,
            "Cross-layer continuity conflict remains visible and is not resolved.",
            360,
        ),
    )


def _entry_ids_by_state(
    entries: tuple[RefreshContinuityCertificationEntry, ...],
    state: str,
) -> tuple[str, ...]:
    return tuple(entry.certification_id for entry in entries if entry.state == state)


def _certified_layer_id(layer: str) -> tuple[str, ...]:
    return (f"v4_1_{layer}_continuity_certified",)


def default_refresh_continuity_certification() -> RefreshContinuityCertification:
    identity = default_refresh_continuity_certification_identity()
    certifications = default_refresh_continuity_certification_entries()
    failure_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_FAILURE)
    unsupported_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_UNSUPPORTED)
    blocked_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_BLOCKED)
    prohibited_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_PROHIBITED)
    stale_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_STALE)
    conflict_ids = _entry_ids_by_state(certifications, CONTINUITY_STATE_CROSS_LAYER_CONFLICT)
    return RefreshContinuityCertification(
        identity=identity,
        certifications=certifications,
        cross_layer_aggregation=CrossLayerContinuityAggregation(
            aggregation_id="v4_1_cross_layer_continuity_aggregation_primary",
            manifest_certification_ids=_certified_layer_id(CONTINUITY_LAYER_MANIFEST),
            dependency_certification_ids=_certified_layer_id(CONTINUITY_LAYER_DEPENDENCY),
            lineage_certification_ids=_certified_layer_id(CONTINUITY_LAYER_LINEAGE),
            schema_certification_ids=_certified_layer_id(CONTINUITY_LAYER_SCHEMA),
            sequencing_certification_ids=_certified_layer_id(CONTINUITY_LAYER_SEQUENCING),
            drift_certification_ids=_certified_layer_id(CONTINUITY_LAYER_DRIFT),
            replay_certification_ids=_certified_layer_id(CONTINUITY_LAYER_REPLAY),
            rollback_certification_ids=_certified_layer_id(CONTINUITY_LAYER_ROLLBACK),
            diagnostics_certification_ids=_certified_layer_id(CONTINUITY_LAYER_DIAGNOSTICS),
            explainability_certification_ids=_certified_layer_id(CONTINUITY_LAYER_EXPLAINABILITY),
            continuity_failure_ids=failure_ids,
            unsupported_continuity_ids=unsupported_ids,
            blocked_continuity_ids=blocked_ids,
            prohibited_continuity_ids=prohibited_ids,
            stale_continuity_ids=stale_ids,
            cross_layer_conflict_ids=conflict_ids,
            deterministic_order=10,
        ),
        continuity_metadata=RefreshContinuityMetadata(
            continuity_id=identity.continuity_id,
            continuity_certification_references=(identity.continuity_id,),
            manifest_references=(identity.source_manifest_reference,),
            dependency_references=(identity.source_dependency_graph_reference,),
            lineage_references=(identity.source_lineage_certification_reference, identity.lineage_reference),
            schema_references=(identity.source_schema_governance_reference,),
            sequencing_references=(identity.source_sequencing_reference,),
            drift_references=(identity.source_drift_certification_reference,),
            replay_references=(identity.source_replay_rollback_reference, identity.replay_reference),
            rollback_references=(identity.source_replay_rollback_reference, identity.rollback_reference),
            diagnostics_references=(identity.source_diagnostics_explainability_reference, identity.diagnostics_reference),
            explainability_references=(identity.source_diagnostics_explainability_reference, identity.explainability_reference),
            provenance_references=(identity.provenance_reference,),
            deterministic_order=20,
        ),
        diagnostics=RefreshContinuityDiagnostics(
            diagnostics_id=identity.diagnostics_reference,
            certification_references=tuple(entry.certification_id for entry in certifications),
            failure_visibility_ids=failure_ids,
            unsupported_visibility_ids=unsupported_ids,
            blocked_visibility_ids=blocked_ids,
            prohibited_visibility_ids=prohibited_ids,
            stale_visibility_ids=stale_ids,
            cross_layer_conflict_ids=conflict_ids,
            deterministic_order=30,
        ),
        explainability=RefreshContinuityExplainability(
            explainability_id=identity.explainability_reference,
            limitation_explanation_ids=("v4_1_continuity_limitation_explanation",),
            prohibited_explanation_ids=("v4_1_continuity_prohibited_state_explanation",),
            unsupported_explanation_ids=("v4_1_continuity_unsupported_state_explanation",),
            blocked_explanation_ids=("v4_1_continuity_blocked_state_explanation",),
            failure_explanation_ids=failure_ids,
            cross_layer_explanation_ids=conflict_ids,
            explanation_texts=(
                "Continuity certification describes evidence and does not approve operations.",
                "Continuity failures remain fail-visible and are not corrected.",
                "Unsupported, blocked, prohibited, and stale continuity states remain explicit.",
            ),
            deterministic_order=40,
        ),
        integrity_boundary=RefreshContinuityIntegrityBoundary(
            boundary_id=identity.integrity_reference,
            prohibited_continuity_domains=PROHIBITED_CONTINUITY_DOMAINS,
            prohibited_remediation_leakage=("remediation", "hidden_remediation_behavior"),
            prohibited_correction_leakage=("automatic_correction", "automatic_repair"),
            prohibited_recommendation_leakage=("recommendation_systems",),
            prohibited_ranking_leakage=("ranking_systems",),
            prohibited_scoring_leakage=("scoring_systems",),
            prohibited_selection_leakage=("selection_systems",),
            prohibited_approval_leakage=("approval_systems",),
            prohibited_authorization_leakage=("authorization_systems",),
            prohibited_orchestration_leakage=("orchestration_execution", "automatic_sequencing"),
            prohibited_execution_leakage=("refresh_execution", "rollback_execution", "recovery_execution"),
            prohibited_planner_integration_leakage=("planner_integration",),
            prohibited_production_consumption_leakage=("production_bundle_consumption",),
            deterministic_order=50,
        ),
        governance=RefreshContinuityGovernance(
            governance_id=identity.governance_reference,
            governance_references=(identity.governance_reference, "v4_1_refresh_continuity_boundary_primary"),
            explicit_limitations=EXPLICIT_CONTINUITY_CERTIFICATION_LIMITATIONS,
            explicit_prohibitions=EXPLICIT_CONTINUITY_CERTIFICATION_PROHIBITIONS,
            deterministic_order=60,
        ),
    )
