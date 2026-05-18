"""Deterministic v4.4 boundary conflict and drift models.

The v4.4 Phase 3 layer models governance boundary drift, refinement
divergence, conflict diagnostics, compatibility evidence, and continuity
degradation as descriptive governance evidence only. It does not resolve
conflicts, correct drift, grant runtime authority, authorize orchestration,
integrate planners, consume production bundles, or mutate runtime or
operational state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID = "v4_4_boundary_conflict_drift"
V4_4_BOUNDARY_CONFLICT_DRIFT_SCHEMA_VERSION = "v4_4.boundary_conflict_drift.1"
V4_4_BOUNDARY_CONFLICT_DRIFT_REPORT_SCHEMA_VERSION = "v4_4.boundary_conflict_drift_report.1"
V4_4_BOUNDARY_CONFLICT_DRIFT_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_STABLE = "v4_4_boundary_conflict_drift_stable"
V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_BLOCKED = "v4_4_boundary_conflict_drift_blocked"
V4_4_BOUNDARY_CONFLICT_DRIFT_PURPOSE = (
    "deterministic_governance_safe_boundary_conflict_and_drift_intelligence_descriptive_only"
)
V4_4_BOUNDARY_CONFLICT_DRIFT_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_conflict_drift_intelligence"
)

CONFLICT_DRIFT_STATE_SUPPORTED = "supported"
CONFLICT_DRIFT_STATE_UNSUPPORTED = "unsupported"
CONFLICT_DRIFT_STATE_PROHIBITED = "prohibited"
CONFLICT_DRIFT_STATE_BLOCKED = "blocked"
CONFLICT_DRIFT_STATE_STALE = "stale"
CONFLICT_DRIFT_STATE_CONFLICTING = "conflicting"
CONFLICT_DRIFT_STATE_AMBIGUOUS = "ambiguous"
CONFLICT_DRIFT_STATE_DRIFTED = "drifted"
CONFLICT_DRIFT_STATE_DIVERGENT = "divergent"
CONFLICT_DRIFT_STATE_COMPATIBLE = "compatible"
CONFLICT_DRIFT_STATE_INCOMPATIBLE = "incompatible"
CONFLICT_DRIFT_STATE_DEGRADED = "degraded"
BOUNDARY_CONFLICT_DRIFT_STATES: tuple[str, ...] = (
    CONFLICT_DRIFT_STATE_SUPPORTED,
    CONFLICT_DRIFT_STATE_UNSUPPORTED,
    CONFLICT_DRIFT_STATE_PROHIBITED,
    CONFLICT_DRIFT_STATE_BLOCKED,
    CONFLICT_DRIFT_STATE_STALE,
    CONFLICT_DRIFT_STATE_CONFLICTING,
    CONFLICT_DRIFT_STATE_AMBIGUOUS,
    CONFLICT_DRIFT_STATE_DRIFTED,
    CONFLICT_DRIFT_STATE_DIVERGENT,
    CONFLICT_DRIFT_STATE_COMPATIBLE,
    CONFLICT_DRIFT_STATE_INCOMPATIBLE,
    CONFLICT_DRIFT_STATE_DEGRADED,
)
FAIL_VISIBLE_CONFLICT_DRIFT_STATES: tuple[str, ...] = (
    CONFLICT_DRIFT_STATE_UNSUPPORTED,
    CONFLICT_DRIFT_STATE_PROHIBITED,
    CONFLICT_DRIFT_STATE_BLOCKED,
    CONFLICT_DRIFT_STATE_STALE,
    CONFLICT_DRIFT_STATE_CONFLICTING,
    CONFLICT_DRIFT_STATE_AMBIGUOUS,
    CONFLICT_DRIFT_STATE_DRIFTED,
    CONFLICT_DRIFT_STATE_DIVERGENT,
    CONFLICT_DRIFT_STATE_INCOMPATIBLE,
    CONFLICT_DRIFT_STATE_DEGRADED,
)

DRIFT_TYPE_GOVERNANCE_BOUNDARY = "governance_boundary_drift"
DRIFT_TYPE_REFINEMENT_DIVERGENCE = "refinement_divergence"
DRIFT_TYPE_INHERITANCE_INCONSISTENCY = "inheritance_inconsistency"
DRIFT_TYPE_CONTINUITY_DEGRADATION = "continuity_degradation"
DRIFT_TYPE_PROVENANCE_DEGRADATION = "provenance_degradation"
DRIFT_TYPE_LINEAGE_DEGRADATION = "lineage_degradation"
DRIFT_TYPES: tuple[str, ...] = (
    DRIFT_TYPE_GOVERNANCE_BOUNDARY,
    DRIFT_TYPE_REFINEMENT_DIVERGENCE,
    DRIFT_TYPE_INHERITANCE_INCONSISTENCY,
    DRIFT_TYPE_CONTINUITY_DEGRADATION,
    DRIFT_TYPE_PROVENANCE_DEGRADATION,
    DRIFT_TYPE_LINEAGE_DEGRADATION,
)

CONFLICT_TYPE_INHERITANCE = "inheritance_conflict"
CONFLICT_TYPE_REFINEMENT = "refinement_conflict"
CONFLICT_TYPE_GOVERNANCE_ANCESTRY = "incompatible_governance_ancestry"
CONFLICT_TYPE_CONTINUITY = "continuity_conflict"
CONFLICT_TYPE_EXPLAINABILITY = "explainability_inconsistency"
CONFLICT_TYPE_PROVENANCE = "provenance_inconsistency"
CONFLICT_TYPE_LINEAGE = "lineage_inconsistency"
CONFLICT_TYPE_SEGMENTATION = "governance_safe_segmentation_conflict"
CONFLICT_TYPE_AMBIGUITY_PROPAGATION = "deterministic_ambiguity_propagation"
CONFLICT_TYPES: tuple[str, ...] = (
    CONFLICT_TYPE_INHERITANCE,
    CONFLICT_TYPE_REFINEMENT,
    CONFLICT_TYPE_GOVERNANCE_ANCESTRY,
    CONFLICT_TYPE_CONTINUITY,
    CONFLICT_TYPE_EXPLAINABILITY,
    CONFLICT_TYPE_PROVENANCE,
    CONFLICT_TYPE_LINEAGE,
    CONFLICT_TYPE_SEGMENTATION,
    CONFLICT_TYPE_AMBIGUITY_PROPAGATION,
)

V4_4_BOUNDARY_CONFLICT_DRIFT_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_CONFLICT_DRIFT_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "drift_ordering_stability",
    "conflict_ordering_stability",
    "drift_serialization_stability",
    "conflict_hashing_stability",
    "compatibility_visibility_stability",
    "incompatibility_visibility_stability",
    "continuity_degradation_visibility",
    "replay_safe_drift_evidence",
    "rollback_safe_drift_evidence",
    "provenance_continuity_visibility",
    "lineage_continuity_visibility",
    "fail_visible_ambiguity_preservation",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_CONFLICT_DRIFT_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 3 models boundary conflict and drift intelligence only.",
    "v4.4 Phase 3 drift visibility does not auto-correct governance state.",
    "v4.4 Phase 3 conflict visibility does not perform operational remediation.",
    "v4.4 Phase 3 compatibility evidence does not authorize orchestration behavior.",
    "v4.4 Phase 3 does not execute orchestration.",
    "v4.4 Phase 3 does not authorize or approve orchestration.",
    "v4.4 Phase 3 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 3 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 3 does not integrate planners or consume production bundles.",
    "v4.4 Phase 3 does not repair, remediate, auto-resolve conflicts, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_CONFLICT_DRIFT_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No drift system grants runtime authority.",
    "No conflict system performs operational remediation.",
    "No compatibility system authorizes orchestration behavior.",
    "No orchestration execution exists.",
    "No orchestration authorization exists.",
    "No orchestration approval exists.",
    "No orchestration dispatch exists.",
    "No orchestration routing exists.",
    "No orchestration traversal exists.",
    "No orchestration scheduling exists.",
    "No orchestration sequencing exists.",
    "No orchestration recommendation exists.",
    "No orchestration ranking, scoring, selection, or optimization exists.",
    "No planner integration exists.",
    "No production consumption exists.",
    "No automatic remediation exists.",
    "No automatic repair exists.",
    "No conflict auto-resolution exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundaryConflictDriftIdentity:
    conflict_drift_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_inheritance_reference: str
    source_inheritance_hash_reference: str
    drift_reference: str
    divergence_reference: str
    compatibility_reference: str
    conflict_diagnostics_reference: str
    provenance_degradation_reference: str
    lineage_degradation_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_CONFLICT_DRIFT_PURPOSE
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    governance_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class GovernanceDriftClassification:
    classification_id: str
    subject_id: str
    classification_type: str
    visibility_state: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    auto_correction_enabled: bool = False
    operational_authority: bool = False


@dataclass(frozen=True)
class BoundaryDriftRecord:
    drift_id: str
    boundary_id: str
    drift_type: str
    visibility_state: str
    drift_chain_ids: tuple[str, ...]
    drift_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    auto_correction_enabled: bool = False
    conflict_auto_resolution_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "drift_chain_ids")
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class RefinementDivergenceRecord:
    divergence_id: str
    source_refinement_id: str
    divergent_refinement_id: str
    visibility_state: str
    divergence_chain_ids: tuple[str, ...]
    divergence_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_operational: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    optimization_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "divergence_chain_ids")
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ConflictDiagnosticRecord:
    conflict_id: str
    subject_id: str
    conflict_type: str
    visibility_state: str
    severity: str
    diagnostic_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    conflict_auto_resolution_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class CompatibilityEvidenceRecord:
    compatibility_id: str
    source_id: str
    target_id: str
    compatibility_state: str
    compatibility_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    runtime_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ContinuityDegradationSummary:
    degradation_id: str
    subject_id: str
    degradation_state: str
    degradation_type: str
    affected_relationship_ids: tuple[str, ...]
    degradation_reason: str
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_relationship_ids")


@dataclass(frozen=True)
class ConflictExplainabilityRecord:
    explainability_id: str
    subject_id: str
    explanation_type: str
    visibility_state: str
    explanation_chain_ids: tuple[str, ...]
    explanation: str
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explanation_chain_ids")


@dataclass(frozen=True)
class ConflictLineageVisibility:
    lineage_visibility_id: str
    subject_id: str
    lineage_state: str
    lineage_reference_ids: tuple[str, ...]
    deterministic_order: int
    lineage_continuity_visible: bool = True
    descriptive_only: bool = True
    ambiguous_lineage_inferred: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "lineage_reference_ids")


@dataclass(frozen=True)
class ConflictAncestryVisibility:
    ancestry_visibility_id: str
    subject_id: str
    ancestry_state: str
    ancestry_reference_ids: tuple[str, ...]
    deterministic_order: int
    conflict_visible: bool = True
    descriptive_only: bool = True
    operational_authority: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "ancestry_reference_ids")


@dataclass(frozen=True)
class ProvenanceDegradationMetadata:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    degradation_reference_ids: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_continuity_visible: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references", "degradation_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageDegradationMetadata:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    degradation_reference_ids: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_continuity_visible: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references", "degradation_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class DriftEvidenceMetadata:
    evidence_id: str
    drift_record_ids: tuple[str, ...]
    divergence_record_ids: tuple[str, ...]
    compatibility_record_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "drift_record_ids",
            "divergence_record_ids",
            "compatibility_record_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BoundaryConflictDriftIntelligence:
    identity: BoundaryConflictDriftIdentity
    classifications: tuple[GovernanceDriftClassification, ...]
    drift_records: tuple[BoundaryDriftRecord, ...]
    divergence_records: tuple[RefinementDivergenceRecord, ...]
    conflict_diagnostics: tuple[ConflictDiagnosticRecord, ...]
    compatibility_evidence: tuple[CompatibilityEvidenceRecord, ...]
    degradation_summaries: tuple[ContinuityDegradationSummary, ...]
    explainability: tuple[ConflictExplainabilityRecord, ...]
    conflict_lineage_visibility: tuple[ConflictLineageVisibility, ...]
    conflict_ancestry_visibility: tuple[ConflictAncestryVisibility, ...]
    provenance_degradation_metadata: ProvenanceDegradationMetadata
    lineage_degradation_metadata: LineageDegradationMetadata
    drift_evidence_metadata: DriftEvidenceMetadata
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_remediating: bool = True
    non_resolving: bool = True
    non_mutating: bool = True
    runtime_execution_enabled: bool = False
    orchestration_runtime_behavior_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    conflict_auto_resolution_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "classifications",
            "drift_records",
            "divergence_records",
            "conflict_diagnostics",
            "compatibility_evidence",
            "degradation_summaries",
            "explainability",
            "conflict_lineage_visibility",
            "conflict_ancestry_visibility",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_boundary_conflict_drift_identity() -> BoundaryConflictDriftIdentity:
    return BoundaryConflictDriftIdentity(
        conflict_drift_id="v4_4_boundary_conflict_drift_intelligence",
        phase_id=V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID,
        schema_version=V4_4_BOUNDARY_CONFLICT_DRIFT_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_CONFLICT_DRIFT_GENERATED_AT,
        classification=V4_4_BOUNDARY_CONFLICT_DRIFT_CLASSIFICATION,
        source_inheritance_reference="v4_4_boundary_inheritance_refinement",
        source_inheritance_hash_reference="v4_4_boundary_inheritance_refinement.deterministic_report_hash",
        drift_reference="v4_4_governance_boundary_drift_visibility",
        divergence_reference="v4_4_refinement_divergence_visibility",
        compatibility_reference="v4_4_refinement_compatibility_visibility",
        conflict_diagnostics_reference="v4_4_boundary_conflict_diagnostics_visibility",
        provenance_degradation_reference="v4_4_boundary_provenance_degradation_visibility",
        lineage_degradation_reference="v4_4_boundary_lineage_degradation_visibility",
        non_operational_reference="v4_4_boundary_conflict_drift_non_operational_certification",
    )


def default_drift_records() -> tuple[BoundaryDriftRecord, ...]:
    definitions = (
        ("drift_governance_scope_baseline", "boundary_governance_scope_visibility", DRIFT_TYPE_GOVERNANCE_BOUNDARY, CONFLICT_DRIFT_STATE_SUPPORTED),
        ("drift_inheritance_chain_variance", "inheritance_conflicting_scope_signal", DRIFT_TYPE_INHERITANCE_INCONSISTENCY, CONFLICT_DRIFT_STATE_DRIFTED),
        ("drift_refinement_lineage_degradation", "refinement_stale_source_evidence", DRIFT_TYPE_LINEAGE_DEGRADATION, CONFLICT_DRIFT_STATE_DEGRADED),
        ("drift_stale_source_visibility", "boundary_stale_source_evidence", DRIFT_TYPE_PROVENANCE_DEGRADATION, CONFLICT_DRIFT_STATE_STALE),
        ("drift_conflicting_scope_visibility", "boundary_conflicting_scope_signal", DRIFT_TYPE_GOVERNANCE_BOUNDARY, CONFLICT_DRIFT_STATE_CONFLICTING),
        ("drift_ambiguous_provider_identity", "boundary_implicit_provider_identity", DRIFT_TYPE_PROVENANCE_DEGRADATION, CONFLICT_DRIFT_STATE_AMBIGUOUS),
        ("drift_incompatible_runtime_semantics", "boundary_external_runtime_semantics", DRIFT_TYPE_REFINEMENT_DIVERGENCE, CONFLICT_DRIFT_STATE_INCOMPATIBLE),
        ("drift_prohibited_runtime_authority", "boundary_runtime_execution", DRIFT_TYPE_CONTINUITY_DEGRADATION, CONFLICT_DRIFT_STATE_PROHIBITED),
    )
    return tuple(
        BoundaryDriftRecord(
            drift_id=drift_id,
            boundary_id=boundary_id,
            drift_type=drift_type,
            visibility_state=visibility_state,
            drift_chain_ids=(boundary_id, drift_id, V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID),
            drift_reason=f"{visibility_state} drift remains visible and is not auto-corrected",
            evidence_reference_ids=(
                "v4_4_boundary_inheritance_refinement_report",
                boundary_id,
                drift_id,
            ),
            deterministic_order=index,
            fail_visible=visibility_state in FAIL_VISIBLE_CONFLICT_DRIFT_STATES,
        )
        for index, (drift_id, boundary_id, drift_type, visibility_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_divergence_records() -> tuple[RefinementDivergenceRecord, ...]:
    definitions = (
        ("divergence_refinement_chain", "refinement_scope_to_ancestry", "refinement_conflicting_scope_signal", CONFLICT_DRIFT_STATE_DIVERGENT),
        ("divergence_compatible_lineage", "refinement_segmentation_to_lineage", "refinement_diagnostics_continuity", CONFLICT_DRIFT_STATE_COMPATIBLE),
        ("divergence_unsupported_runtime_semantics", "refinement_external_runtime_semantics", "refinement_implicit_provider_identity", CONFLICT_DRIFT_STATE_UNSUPPORTED),
        ("divergence_blocked_lineage_evidence", "inheritance_missing_lineage", "refinement_implicit_provider_identity", CONFLICT_DRIFT_STATE_BLOCKED),
        ("divergence_incompatible_planner_production", "refinement_planner_production", "boundary_planner_production", CONFLICT_DRIFT_STATE_INCOMPATIBLE),
        ("divergence_conflicting_scope", "inheritance_conflicting_scope_signal", "refinement_conflicting_scope_signal", CONFLICT_DRIFT_STATE_CONFLICTING),
    )
    return tuple(
        RefinementDivergenceRecord(
            divergence_id=divergence_id,
            source_refinement_id=source_refinement_id,
            divergent_refinement_id=divergent_refinement_id,
            visibility_state=visibility_state,
            divergence_chain_ids=(
                source_refinement_id,
                divergent_refinement_id,
                divergence_id,
            ),
            divergence_reason=f"{visibility_state} divergence remains visible without orchestration decisioning",
            evidence_reference_ids=(
                "v4_4_boundary_inheritance_refinement_report",
                source_refinement_id,
                divergent_refinement_id,
            ),
            deterministic_order=index,
            fail_visible=visibility_state in FAIL_VISIBLE_CONFLICT_DRIFT_STATES,
        )
        for index, (
            divergence_id,
            source_refinement_id,
            divergent_refinement_id,
            visibility_state,
        ) in enumerate(definitions, start=1)
    )


def default_compatibility_evidence() -> tuple[CompatibilityEvidenceRecord, ...]:
    definitions = (
        ("compatibility_scope_segmentation", "boundary_governance_scope_visibility", "boundary_deterministic_segmentation", CONFLICT_DRIFT_STATE_COMPATIBLE),
        ("compatibility_runtime_semantics", "boundary_external_runtime_semantics", "refined_external_runtime_visibility", CONFLICT_DRIFT_STATE_INCOMPATIBLE),
        ("compatibility_ambiguous_provider", "boundary_implicit_provider_identity", "refined_ambiguous_provider_visibility", CONFLICT_DRIFT_STATE_AMBIGUOUS),
        ("compatibility_degraded_lineage", "boundary_missing_lineage_evidence", "refined_ambiguous_provider_visibility", CONFLICT_DRIFT_STATE_DEGRADED),
    )
    return tuple(
        CompatibilityEvidenceRecord(
            compatibility_id=compatibility_id,
            source_id=source_id,
            target_id=target_id,
            compatibility_state=compatibility_state,
            compatibility_reason=(
                f"{compatibility_state} compatibility evidence is visible and non-authorizing"
            ),
            evidence_reference_ids=(
                "v4_4_boundary_inheritance_refinement_report",
                source_id,
                target_id,
            ),
            deterministic_order=index,
            fail_visible=compatibility_state in FAIL_VISIBLE_CONFLICT_DRIFT_STATES,
        )
        for index, (compatibility_id, source_id, target_id, compatibility_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_governance_drift_classifications() -> tuple[GovernanceDriftClassification, ...]:
    subjects = (*default_drift_records(), *default_divergence_records(), *default_compatibility_evidence())
    classifications: list[GovernanceDriftClassification] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = (
            getattr(subject, "drift_id", None)
            or getattr(subject, "divergence_id", None)
            or getattr(subject, "compatibility_id", None)
        )
        state = getattr(subject, "visibility_state", None) or getattr(subject, "compatibility_state")
        classifications.append(
            GovernanceDriftClassification(
                classification_id=f"classification_{subject_id}",
                subject_id=str(subject_id),
                classification_type=f"{state}_conflict_drift_visibility",
                visibility_state=str(state),
                classification_reason=f"{state} conflict/drift classification remains descriptive-only",
                deterministic_order=index,
            )
        )
    return tuple(classifications)


def default_conflict_diagnostics() -> tuple[ConflictDiagnosticRecord, ...]:
    severity_by_state = {
        CONFLICT_DRIFT_STATE_SUPPORTED: "info",
        CONFLICT_DRIFT_STATE_COMPATIBLE: "info",
        CONFLICT_DRIFT_STATE_UNSUPPORTED: "warning",
        CONFLICT_DRIFT_STATE_PROHIBITED: "prohibited",
        CONFLICT_DRIFT_STATE_BLOCKED: "blocker",
        CONFLICT_DRIFT_STATE_STALE: "warning",
        CONFLICT_DRIFT_STATE_CONFLICTING: "warning",
        CONFLICT_DRIFT_STATE_AMBIGUOUS: "warning",
        CONFLICT_DRIFT_STATE_DRIFTED: "warning",
        CONFLICT_DRIFT_STATE_DIVERGENT: "warning",
        CONFLICT_DRIFT_STATE_INCOMPATIBLE: "warning",
        CONFLICT_DRIFT_STATE_DEGRADED: "warning",
    }
    subjects = (*default_drift_records(), *default_divergence_records())
    diagnostics: list[ConflictDiagnosticRecord] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = getattr(subject, "drift_id", None) or getattr(subject, "divergence_id")
        state = getattr(subject, "visibility_state")
        conflict_type = CONFLICT_TYPES[(index - 1) % len(CONFLICT_TYPES)]
        diagnostics.append(
            ConflictDiagnosticRecord(
                conflict_id=f"conflict_{subject_id}",
                subject_id=str(subject_id),
                conflict_type=conflict_type,
                visibility_state=state,
                severity=severity_by_state[state],
                diagnostic_message=f"{state} conflict/drift diagnostic remains visible without auto-resolution",
                evidence_reference_ids=subject.evidence_reference_ids,
                deterministic_order=index,
            )
        )
    return tuple(diagnostics)


def default_degradation_summaries() -> tuple[ContinuityDegradationSummary, ...]:
    definitions = (
        ("degradation_lineage_visibility", "drift_refinement_lineage_degradation", CONFLICT_DRIFT_STATE_DEGRADED, ("refinement_stale_source_evidence", "refinement_implicit_provider_identity")),
        ("degradation_stale_provenance", "drift_stale_source_visibility", CONFLICT_DRIFT_STATE_STALE, ("boundary_stale_source_evidence",)),
        ("degradation_conflicting_continuity", "divergence_conflicting_scope", CONFLICT_DRIFT_STATE_CONFLICTING, ("inheritance_conflicting_scope_signal", "refinement_conflicting_scope_signal")),
    )
    return tuple(
        ContinuityDegradationSummary(
            degradation_id=degradation_id,
            subject_id=subject_id,
            degradation_state=degradation_state,
            degradation_type=f"{degradation_state}_continuity_degradation_visibility",
            affected_relationship_ids=affected_relationship_ids,
            degradation_reason=f"{degradation_state} continuity degradation is visible and not repaired",
            deterministic_order=index,
        )
        for index, (
            degradation_id,
            subject_id,
            degradation_state,
            affected_relationship_ids,
        ) in enumerate(definitions, start=1)
    )


def default_conflict_explainability() -> tuple[ConflictExplainabilityRecord, ...]:
    explanations: list[ConflictExplainabilityRecord] = []
    for index, diagnostic in enumerate(default_conflict_diagnostics(), start=1):
        explanations.append(
            ConflictExplainabilityRecord(
                explainability_id=f"explainability_{diagnostic.conflict_id}",
                subject_id=diagnostic.subject_id,
                explanation_type=f"{diagnostic.visibility_state}_conflict_explainability",
                visibility_state=diagnostic.visibility_state,
                explanation_chain_ids=(
                    diagnostic.subject_id,
                    diagnostic.conflict_id,
                    V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID,
                ),
                explanation="Conflict evidence explains uncertainty without orchestration behavior",
                deterministic_order=index,
            )
        )
    return tuple(explanations)


def default_conflict_lineage_visibility() -> tuple[ConflictLineageVisibility, ...]:
    return tuple(
        ConflictLineageVisibility(
            lineage_visibility_id=f"lineage_{drift.drift_id}",
            subject_id=drift.drift_id,
            lineage_state=drift.visibility_state,
            lineage_reference_ids=(
                "v4_4_boundary_inheritance_refinement",
                drift.boundary_id,
                drift.drift_id,
            ),
            deterministic_order=drift.deterministic_order,
        )
        for drift in default_drift_records()
    )


def default_conflict_ancestry_visibility() -> tuple[ConflictAncestryVisibility, ...]:
    return tuple(
        ConflictAncestryVisibility(
            ancestry_visibility_id=f"ancestry_{divergence.divergence_id}",
            subject_id=divergence.divergence_id,
            ancestry_state=divergence.visibility_state,
            ancestry_reference_ids=(
                divergence.source_refinement_id,
                divergence.divergent_refinement_id,
                divergence.divergence_id,
            ),
            deterministic_order=divergence.deterministic_order,
        )
        for divergence in default_divergence_records()
    )


def _degradation_reference_ids() -> tuple[str, ...]:
    return tuple(summary.degradation_id for summary in default_degradation_summaries())


def default_provenance_degradation_metadata() -> ProvenanceDegradationMetadata:
    return ProvenanceDegradationMetadata(
        provenance_id="v4_4_boundary_conflict_drift_provenance_degradation",
        source_reference_ids=(
            "v4_3_closeout_and_v4_4_readiness",
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID,
        ),
        source_hash_references=(
            "v4_3_closeout_and_v4_4_readiness.deterministic_report_hash",
            "v4_4_boundary_intelligence_foundations.deterministic_report_hash",
            "v4_4_boundary_inheritance_refinement.deterministic_report_hash",
        ),
        degradation_reference_ids=_degradation_reference_ids(),
        provenance_state="provenance_degradation_visible",
        deterministic_order=1,
    )


def default_lineage_degradation_metadata() -> LineageDegradationMetadata:
    return LineageDegradationMetadata(
        lineage_id="v4_4_boundary_conflict_drift_lineage_degradation",
        lineage_reference_ids=(
            "v4_3_orchestration_continuity_and_integrity_certification",
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            V4_4_BOUNDARY_CONFLICT_DRIFT_PHASE_ID,
        ),
        lineage_hash_references=(
            "v4_3_continuity_integrity_hash_reference",
            "v4_4_boundary_intelligence_hash_reference",
            "v4_4_boundary_inheritance_hash_reference",
        ),
        degradation_reference_ids=_degradation_reference_ids(),
        lineage_state="lineage_degradation_visible",
        deterministic_order=1,
    )


def default_drift_evidence_metadata() -> DriftEvidenceMetadata:
    drift_ids = tuple(record.drift_id for record in default_drift_records())
    divergence_ids = tuple(record.divergence_id for record in default_divergence_records())
    compatibility_ids = tuple(record.compatibility_id for record in default_compatibility_evidence())
    all_ids = drift_ids + divergence_ids + compatibility_ids
    return DriftEvidenceMetadata(
        evidence_id="v4_4_boundary_conflict_drift_replay_rollback_evidence",
        drift_record_ids=drift_ids,
        divergence_record_ids=divergence_ids,
        compatibility_record_ids=compatibility_ids,
        replay_evidence_ids=all_ids,
        rollback_evidence_ids=all_ids,
        deterministic_order=1,
    )


def default_boundary_conflict_drift_intelligence() -> BoundaryConflictDriftIntelligence:
    return BoundaryConflictDriftIntelligence(
        identity=default_boundary_conflict_drift_identity(),
        classifications=default_governance_drift_classifications(),
        drift_records=default_drift_records(),
        divergence_records=default_divergence_records(),
        conflict_diagnostics=default_conflict_diagnostics(),
        compatibility_evidence=default_compatibility_evidence(),
        degradation_summaries=default_degradation_summaries(),
        explainability=default_conflict_explainability(),
        conflict_lineage_visibility=default_conflict_lineage_visibility(),
        conflict_ancestry_visibility=default_conflict_ancestry_visibility(),
        provenance_degradation_metadata=default_provenance_degradation_metadata(),
        lineage_degradation_metadata=default_lineage_degradation_metadata(),
        drift_evidence_metadata=default_drift_evidence_metadata(),
        deterministic_guarantees=V4_4_BOUNDARY_CONFLICT_DRIFT_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_CONFLICT_DRIFT_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_CONFLICT_DRIFT_EXPLICIT_PROHIBITIONS,
    )
