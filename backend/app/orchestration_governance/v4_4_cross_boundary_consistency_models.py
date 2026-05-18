"""Deterministic v4.4 cross-boundary consistency models.

The v4.4 Phase 4 layer models cross-boundary governance consistency as
descriptive governance evidence only. It evaluates consistency visibility
across boundary, inheritance, refinement, drift, conflict, compatibility,
continuity, provenance, and lineage surfaces without enforcing consistency,
normalizing states, granting runtime authority, authorizing orchestration,
integrating planners, consuming production bundles, or mutating runtime or
operational state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID = "v4_4_cross_boundary_consistency"
V4_4_CROSS_BOUNDARY_CONSISTENCY_SCHEMA_VERSION = "v4_4.cross_boundary_consistency.1"
V4_4_CROSS_BOUNDARY_CONSISTENCY_REPORT_SCHEMA_VERSION = (
    "v4_4.cross_boundary_consistency_report.1"
)
V4_4_CROSS_BOUNDARY_CONSISTENCY_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_STABLE = "v4_4_cross_boundary_consistency_stable"
V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_BLOCKED = "v4_4_cross_boundary_consistency_blocked"
V4_4_CROSS_BOUNDARY_CONSISTENCY_PURPOSE = (
    "deterministic_governance_safe_cross_boundary_consistency_intelligence_descriptive_only"
)
V4_4_CROSS_BOUNDARY_CONSISTENCY_CLASSIFICATION = (
    "governance_safe_descriptive_cross_boundary_consistency_intelligence"
)

CONSISTENCY_STATE_CONSISTENT = "consistent"
CONSISTENCY_STATE_INCONSISTENT = "inconsistent"
CONSISTENCY_STATE_PARTIALLY_CONSISTENT = "partially_consistent"
CONSISTENCY_STATE_UNSUPPORTED = "unsupported"
CONSISTENCY_STATE_PROHIBITED = "prohibited"
CONSISTENCY_STATE_BLOCKED = "blocked"
CONSISTENCY_STATE_STALE = "stale"
CONSISTENCY_STATE_CONFLICTING = "conflicting"
CONSISTENCY_STATE_AMBIGUOUS = "ambiguous"
CONSISTENCY_STATE_DEGRADED = "degraded"
CONSISTENCY_STATE_COMPATIBLE = "compatible"
CONSISTENCY_STATE_INCOMPATIBLE = "incompatible"
CROSS_BOUNDARY_CONSISTENCY_STATES: tuple[str, ...] = (
    CONSISTENCY_STATE_CONSISTENT,
    CONSISTENCY_STATE_INCONSISTENT,
    CONSISTENCY_STATE_PARTIALLY_CONSISTENT,
    CONSISTENCY_STATE_UNSUPPORTED,
    CONSISTENCY_STATE_PROHIBITED,
    CONSISTENCY_STATE_BLOCKED,
    CONSISTENCY_STATE_STALE,
    CONSISTENCY_STATE_CONFLICTING,
    CONSISTENCY_STATE_AMBIGUOUS,
    CONSISTENCY_STATE_DEGRADED,
    CONSISTENCY_STATE_COMPATIBLE,
    CONSISTENCY_STATE_INCOMPATIBLE,
)
FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES: tuple[str, ...] = (
    CONSISTENCY_STATE_INCONSISTENT,
    CONSISTENCY_STATE_PARTIALLY_CONSISTENT,
    CONSISTENCY_STATE_UNSUPPORTED,
    CONSISTENCY_STATE_PROHIBITED,
    CONSISTENCY_STATE_BLOCKED,
    CONSISTENCY_STATE_STALE,
    CONSISTENCY_STATE_CONFLICTING,
    CONSISTENCY_STATE_AMBIGUOUS,
    CONSISTENCY_STATE_DEGRADED,
    CONSISTENCY_STATE_INCOMPATIBLE,
)

CONSISTENCY_SURFACE_BOUNDARY_CHAIN = "boundary_chain_consistency"
CONSISTENCY_SURFACE_INHERITANCE = "inheritance_consistency"
CONSISTENCY_SURFACE_REFINEMENT = "refinement_consistency"
CONSISTENCY_SURFACE_DRIFT = "drift_consistency"
CONSISTENCY_SURFACE_CONFLICT = "conflict_consistency"
CONSISTENCY_SURFACE_COMPATIBILITY = "compatibility_consistency"
CONSISTENCY_SURFACE_CONTINUITY = "continuity_consistency"
CONSISTENCY_SURFACE_PROVENANCE = "provenance_consistency"
CONSISTENCY_SURFACE_LINEAGE = "lineage_consistency"
CONSISTENCY_SURFACES: tuple[str, ...] = (
    CONSISTENCY_SURFACE_BOUNDARY_CHAIN,
    CONSISTENCY_SURFACE_INHERITANCE,
    CONSISTENCY_SURFACE_REFINEMENT,
    CONSISTENCY_SURFACE_DRIFT,
    CONSISTENCY_SURFACE_CONFLICT,
    CONSISTENCY_SURFACE_COMPATIBILITY,
    CONSISTENCY_SURFACE_CONTINUITY,
    CONSISTENCY_SURFACE_PROVENANCE,
    CONSISTENCY_SURFACE_LINEAGE,
)

V4_4_CROSS_BOUNDARY_CONSISTENCY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_operational_mutation_count",
)

V4_4_CROSS_BOUNDARY_CONSISTENCY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "consistency_ordering_stability",
    "relationship_ordering_stability",
    "consistency_serialization_stability",
    "consistency_hashing_stability",
    "cross_boundary_inconsistency_visibility",
    "partial_consistency_visibility",
    "degraded_consistency_visibility",
    "fail_visible_ambiguity_preservation",
    "replay_safe_consistency_evidence",
    "rollback_safe_consistency_evidence",
    "provenance_consistency_visibility",
    "lineage_consistency_visibility",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_CROSS_BOUNDARY_CONSISTENCY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 4 models cross-boundary governance consistency intelligence only.",
    "v4.4 Phase 4 consistency visibility does not enforce consistency.",
    "v4.4 Phase 4 consistency diagnostics do not perform remediation.",
    "v4.4 Phase 4 compatibility consistency evidence does not authorize orchestration behavior.",
    "v4.4 Phase 4 does not execute orchestration.",
    "v4.4 Phase 4 does not authorize or approve orchestration.",
    "v4.4 Phase 4 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 4 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 4 does not integrate planners or consume production bundles.",
    "v4.4 Phase 4 does not repair, remediate, normalize automatically, or mutate runtime or operational state.",
)

V4_4_CROSS_BOUNDARY_CONSISTENCY_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No consistency system grants runtime authority.",
    "No consistency result authorizes orchestration behavior.",
    "No consistency intelligence performs remediation or mutation.",
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
    "No consistency auto-resolution exists.",
    "No automatic normalization exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class CrossBoundaryConsistencyIdentity:
    consistency_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_foundation_reference: str
    source_inheritance_reference: str
    source_conflict_drift_reference: str
    relationship_reference: str
    diagnostics_reference: str
    provenance_consistency_reference: str
    lineage_consistency_reference: str
    non_operational_reference: str
    purpose: str = V4_4_CROSS_BOUNDARY_CONSISTENCY_PURPOSE
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
class GovernanceConsistencyClassification:
    classification_id: str
    subject_id: str
    consistency_state: str
    classification_type: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    consistency_enforcement_enabled: bool = False
    operational_authority: bool = False


@dataclass(frozen=True)
class ConsistencyRecord:
    consistency_record_id: str
    boundary_surface: str
    consistency_state: str
    related_boundary_ids: tuple[str, ...]
    consistency_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    consistency_enforcement_enabled: bool = False
    consistency_auto_resolution_enabled: bool = False
    automatic_normalization_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "related_boundary_ids")
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class MultiBoundaryRelationshipRecord:
    relationship_id: str
    source_boundary_id: str
    target_boundary_id: str
    relationship_type: str
    consistency_state: str
    relationship_chain_ids: tuple[str, ...]
    consistency_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "relationship_chain_ids")


@dataclass(frozen=True)
class CrossBoundaryDiagnosticRecord:
    diagnostic_id: str
    subject_id: str
    diagnostic_type: str
    consistency_state: str
    severity: str
    diagnostic_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    consistency_auto_resolution_enabled: bool = False
    automatic_normalization_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class CompatibilityConsistencySummary:
    compatibility_id: str
    source_id: str
    target_id: str
    consistency_state: str
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
class ContinuityConsistencySummary:
    continuity_id: str
    subject_id: str
    consistency_state: str
    continuity_type: str
    affected_boundary_ids: tuple[str, ...]
    consistency_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "affected_boundary_ids")


@dataclass(frozen=True)
class ProvenanceConsistencySummary:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    consistency_reference_ids: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_consistency_visible: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references", "consistency_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class LineageConsistencySummary:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    consistency_reference_ids: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_consistency_visible: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references", "consistency_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ConsistencyExplainabilityRecord:
    explainability_id: str
    subject_id: str
    explanation_type: str
    consistency_state: str
    explanation_chain_ids: tuple[str, ...]
    explanation: str
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    scoring_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explanation_chain_ids")


@dataclass(frozen=True)
class ConsistencyEvidenceMetadata:
    evidence_id: str
    consistency_record_ids: tuple[str, ...]
    relationship_record_ids: tuple[str, ...]
    diagnostic_record_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "consistency_record_ids",
            "relationship_record_ids",
            "diagnostic_record_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CrossBoundaryConsistencyIntelligence:
    identity: CrossBoundaryConsistencyIdentity
    classifications: tuple[GovernanceConsistencyClassification, ...]
    consistency_records: tuple[ConsistencyRecord, ...]
    relationship_records: tuple[MultiBoundaryRelationshipRecord, ...]
    diagnostics: tuple[CrossBoundaryDiagnosticRecord, ...]
    compatibility_consistency: tuple[CompatibilityConsistencySummary, ...]
    continuity_consistency: tuple[ContinuityConsistencySummary, ...]
    provenance_consistency: ProvenanceConsistencySummary
    lineage_consistency: LineageConsistencySummary
    explainability: tuple[ConsistencyExplainabilityRecord, ...]
    evidence_metadata: ConsistencyEvidenceMetadata
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_enforcing: bool = True
    non_remediating: bool = True
    non_resolving: bool = True
    non_normalizing: bool = True
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
    consistency_auto_resolution_enabled: bool = False
    automatic_normalization_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "classifications",
            "consistency_records",
            "relationship_records",
            "diagnostics",
            "compatibility_consistency",
            "continuity_consistency",
            "explainability",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_cross_boundary_consistency_identity() -> CrossBoundaryConsistencyIdentity:
    return CrossBoundaryConsistencyIdentity(
        consistency_id="v4_4_cross_boundary_consistency_intelligence",
        phase_id=V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID,
        schema_version=V4_4_CROSS_BOUNDARY_CONSISTENCY_SCHEMA_VERSION,
        generated_at=V4_4_CROSS_BOUNDARY_CONSISTENCY_GENERATED_AT,
        classification=V4_4_CROSS_BOUNDARY_CONSISTENCY_CLASSIFICATION,
        source_foundation_reference="v4_4_boundary_intelligence_foundations",
        source_inheritance_reference="v4_4_boundary_inheritance_refinement",
        source_conflict_drift_reference="v4_4_boundary_conflict_drift",
        relationship_reference="v4_4_cross_boundary_relationship_consistency",
        diagnostics_reference="v4_4_cross_boundary_consistency_diagnostics",
        provenance_consistency_reference="v4_4_cross_boundary_provenance_consistency",
        lineage_consistency_reference="v4_4_cross_boundary_lineage_consistency",
        non_operational_reference="v4_4_cross_boundary_consistency_non_operational_certification",
    )


def default_consistency_records() -> tuple[ConsistencyRecord, ...]:
    definitions = (
        ("consistency_boundary_chain_baseline", CONSISTENCY_SURFACE_BOUNDARY_CHAIN, CONSISTENCY_STATE_CONSISTENT),
        ("consistency_runtime_authority_mismatch", CONSISTENCY_SURFACE_CONFLICT, CONSISTENCY_STATE_INCONSISTENT),
        ("consistency_inheritance_refinement_partial", CONSISTENCY_SURFACE_INHERITANCE, CONSISTENCY_STATE_PARTIALLY_CONSISTENT),
        ("consistency_external_runtime_unsupported", CONSISTENCY_SURFACE_REFINEMENT, CONSISTENCY_STATE_UNSUPPORTED),
        ("consistency_runtime_authority_prohibited", CONSISTENCY_SURFACE_CONFLICT, CONSISTENCY_STATE_PROHIBITED),
        ("consistency_missing_lineage_blocked", CONSISTENCY_SURFACE_LINEAGE, CONSISTENCY_STATE_BLOCKED),
        ("consistency_source_snapshot_stale", CONSISTENCY_SURFACE_PROVENANCE, CONSISTENCY_STATE_STALE),
        ("consistency_segmentation_conflict", CONSISTENCY_SURFACE_BOUNDARY_CHAIN, CONSISTENCY_STATE_CONFLICTING),
        ("consistency_provider_identity_ambiguous", CONSISTENCY_SURFACE_PROVENANCE, CONSISTENCY_STATE_AMBIGUOUS),
        ("consistency_continuity_degraded", CONSISTENCY_SURFACE_CONTINUITY, CONSISTENCY_STATE_DEGRADED),
        ("consistency_lineage_compatible", CONSISTENCY_SURFACE_COMPATIBILITY, CONSISTENCY_STATE_COMPATIBLE),
        ("consistency_planner_production_incompatible", CONSISTENCY_SURFACE_DRIFT, CONSISTENCY_STATE_INCOMPATIBLE),
    )
    return tuple(
        ConsistencyRecord(
            consistency_record_id=record_id,
            boundary_surface=surface,
            consistency_state=state,
            related_boundary_ids=(surface, record_id, V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID),
            consistency_reason=f"{state} cross-boundary consistency remains visible and non-enforcing",
            evidence_reference_ids=(
                "v4_4_boundary_intelligence_foundations_report",
                "v4_4_boundary_inheritance_refinement_report",
                "v4_4_boundary_conflict_drift_report",
                record_id,
            ),
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES,
        )
        for index, (record_id, surface, state) in enumerate(definitions, start=1)
    )


def default_relationship_records() -> tuple[MultiBoundaryRelationshipRecord, ...]:
    definitions = (
        ("relationship_foundation_to_inheritance", "boundary_foundation", "inheritance_refinement", "foundation_inheritance_consistency", CONSISTENCY_STATE_CONSISTENT),
        ("relationship_inheritance_to_refinement", "inheritance_refinement", "refinement_visibility", "inheritance_refinement_partial", CONSISTENCY_STATE_PARTIALLY_CONSISTENT),
        ("relationship_refinement_to_runtime_semantics", "refinement_visibility", "runtime_semantics_visibility", "refinement_runtime_incompatibility", CONSISTENCY_STATE_INCOMPATIBLE),
        ("relationship_drift_to_conflict", "boundary_drift_visibility", "conflict_diagnostics", "drift_conflict_consistency", CONSISTENCY_STATE_CONFLICTING),
        ("relationship_provenance_staleness", "provenance_visibility", "stale_source_visibility", "provenance_stale_consistency", CONSISTENCY_STATE_STALE),
        ("relationship_provider_ambiguity", "provider_identity_visibility", "provenance_visibility", "provider_ambiguity_consistency", CONSISTENCY_STATE_AMBIGUOUS),
        ("relationship_lineage_compatibility", "lineage_visibility", "compatibility_visibility", "lineage_compatibility_consistency", CONSISTENCY_STATE_COMPATIBLE),
        ("relationship_continuity_degradation", "continuity_visibility", "lineage_visibility", "continuity_degradation_consistency", CONSISTENCY_STATE_DEGRADED),
    )
    return tuple(
        MultiBoundaryRelationshipRecord(
            relationship_id=relationship_id,
            source_boundary_id=source_id,
            target_boundary_id=target_id,
            relationship_type=relationship_type,
            consistency_state=state,
            relationship_chain_ids=(source_id, target_id, relationship_id),
            consistency_reason=f"{state} relationship consistency remains descriptive-only",
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES,
        )
        for index, (relationship_id, source_id, target_id, relationship_type, state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_compatibility_consistency() -> tuple[CompatibilityConsistencySummary, ...]:
    definitions = (
        ("compatibility_consistency_lineage", "lineage_visibility", "compatibility_visibility", CONSISTENCY_STATE_COMPATIBLE),
        ("compatibility_consistency_runtime_semantics", "runtime_semantics_visibility", "planner_production_visibility", CONSISTENCY_STATE_INCOMPATIBLE),
        ("compatibility_consistency_refinement_partial", "inheritance_refinement", "refinement_drift", CONSISTENCY_STATE_PARTIALLY_CONSISTENT),
        ("compatibility_consistency_continuity_degraded", "continuity_visibility", "lineage_visibility", CONSISTENCY_STATE_DEGRADED),
    )
    return tuple(
        CompatibilityConsistencySummary(
            compatibility_id=compatibility_id,
            source_id=source_id,
            target_id=target_id,
            consistency_state=state,
            compatibility_reason=f"{state} compatibility consistency is visible and non-authorizing",
            evidence_reference_ids=("v4_4_boundary_conflict_drift_report", source_id, target_id),
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_CROSS_BOUNDARY_CONSISTENCY_STATES,
        )
        for index, (compatibility_id, source_id, target_id, state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_continuity_consistency() -> tuple[ContinuityConsistencySummary, ...]:
    definitions = (
        ("continuity_consistency_foundation", "boundary_foundation", CONSISTENCY_STATE_CONSISTENT, ("boundary_foundation", "inheritance_refinement")),
        ("continuity_consistency_refinement_partial", "refinement_visibility", CONSISTENCY_STATE_PARTIALLY_CONSISTENT, ("inheritance_refinement", "drift_visibility")),
        ("continuity_consistency_lineage_degraded", "lineage_visibility", CONSISTENCY_STATE_DEGRADED, ("lineage_visibility", "conflict_diagnostics")),
        ("continuity_consistency_provenance_stale", "provenance_visibility", CONSISTENCY_STATE_STALE, ("provenance_visibility", "stale_source_visibility")),
    )
    return tuple(
        ContinuityConsistencySummary(
            continuity_id=continuity_id,
            subject_id=subject_id,
            consistency_state=state,
            continuity_type=f"{state}_continuity_consistency_visibility",
            affected_boundary_ids=affected_ids,
            consistency_reason=f"{state} continuity consistency remains visible and non-mutating",
            deterministic_order=index,
            fail_visible=True,
        )
        for index, (continuity_id, subject_id, state, affected_ids) in enumerate(definitions, start=1)
    )


def default_governance_consistency_classifications() -> tuple[GovernanceConsistencyClassification, ...]:
    subjects = (
        *default_consistency_records(),
        *default_relationship_records(),
        *default_compatibility_consistency(),
        *default_continuity_consistency(),
    )
    classifications: list[GovernanceConsistencyClassification] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = (
            getattr(subject, "consistency_record_id", None)
            or getattr(subject, "relationship_id", None)
            or getattr(subject, "compatibility_id", None)
            or getattr(subject, "continuity_id", None)
        )
        state = getattr(subject, "consistency_state")
        classifications.append(
            GovernanceConsistencyClassification(
                classification_id=f"classification_{subject_id}",
                subject_id=str(subject_id),
                consistency_state=state,
                classification_type=f"{state}_cross_boundary_consistency_visibility",
                classification_reason=f"{state} consistency classification remains descriptive-only",
                deterministic_order=index,
            )
        )
    return tuple(classifications)


def default_cross_boundary_diagnostics() -> tuple[CrossBoundaryDiagnosticRecord, ...]:
    severity_by_state = {
        CONSISTENCY_STATE_CONSISTENT: "info",
        CONSISTENCY_STATE_COMPATIBLE: "info",
        CONSISTENCY_STATE_PARTIALLY_CONSISTENT: "warning",
        CONSISTENCY_STATE_INCONSISTENT: "warning",
        CONSISTENCY_STATE_UNSUPPORTED: "warning",
        CONSISTENCY_STATE_PROHIBITED: "prohibited",
        CONSISTENCY_STATE_BLOCKED: "blocker",
        CONSISTENCY_STATE_STALE: "warning",
        CONSISTENCY_STATE_CONFLICTING: "warning",
        CONSISTENCY_STATE_AMBIGUOUS: "warning",
        CONSISTENCY_STATE_DEGRADED: "warning",
        CONSISTENCY_STATE_INCOMPATIBLE: "warning",
    }
    return tuple(
        CrossBoundaryDiagnosticRecord(
            diagnostic_id=f"diagnostic_{record.consistency_record_id}",
            subject_id=record.consistency_record_id,
            diagnostic_type=f"{record.boundary_surface}_diagnostic",
            consistency_state=record.consistency_state,
            severity=severity_by_state[record.consistency_state],
            diagnostic_message=(
                f"{record.consistency_state} cross-boundary consistency diagnostic "
                "remains visible without auto-resolution"
            ),
            evidence_reference_ids=record.evidence_reference_ids,
            deterministic_order=index,
        )
        for index, record in enumerate(default_consistency_records(), start=1)
    )


def default_consistency_explainability() -> tuple[ConsistencyExplainabilityRecord, ...]:
    return tuple(
        ConsistencyExplainabilityRecord(
            explainability_id=f"explainability_{diagnostic.diagnostic_id}",
            subject_id=diagnostic.subject_id,
            explanation_type=f"{diagnostic.consistency_state}_consistency_explainability",
            consistency_state=diagnostic.consistency_state,
            explanation_chain_ids=(
                diagnostic.subject_id,
                diagnostic.diagnostic_id,
                V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID,
            ),
            explanation="Consistency evidence explains cross-boundary uncertainty without orchestration behavior",
            deterministic_order=index,
        )
        for index, diagnostic in enumerate(default_cross_boundary_diagnostics(), start=1)
    )


def _consistency_reference_ids() -> tuple[str, ...]:
    return tuple(record.consistency_record_id for record in default_consistency_records())


def default_provenance_consistency_summary() -> ProvenanceConsistencySummary:
    return ProvenanceConsistencySummary(
        provenance_id="v4_4_cross_boundary_provenance_consistency",
        source_reference_ids=(
            "v4_3_closeout_and_v4_4_readiness",
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            "v4_4_boundary_conflict_drift",
            V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID,
        ),
        source_hash_references=(
            "v4_3_closeout_and_v4_4_readiness.deterministic_report_hash",
            "v4_4_boundary_intelligence_foundations.deterministic_report_hash",
            "v4_4_boundary_inheritance_refinement.deterministic_report_hash",
            "v4_4_boundary_conflict_drift.deterministic_report_hash",
        ),
        consistency_reference_ids=_consistency_reference_ids(),
        provenance_state="provenance_consistency_visible",
        deterministic_order=1,
    )


def default_lineage_consistency_summary() -> LineageConsistencySummary:
    return LineageConsistencySummary(
        lineage_id="v4_4_cross_boundary_lineage_consistency",
        lineage_reference_ids=(
            "v4_3_orchestration_continuity_and_integrity_certification",
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            "v4_4_boundary_conflict_drift",
            V4_4_CROSS_BOUNDARY_CONSISTENCY_PHASE_ID,
        ),
        lineage_hash_references=(
            "v4_3_continuity_integrity_hash_reference",
            "v4_4_boundary_intelligence_hash_reference",
            "v4_4_boundary_inheritance_hash_reference",
            "v4_4_boundary_conflict_drift_hash_reference",
        ),
        consistency_reference_ids=_consistency_reference_ids(),
        lineage_state="lineage_consistency_visible",
        deterministic_order=1,
    )


def default_consistency_evidence_metadata() -> ConsistencyEvidenceMetadata:
    consistency_ids = tuple(record.consistency_record_id for record in default_consistency_records())
    relationship_ids = tuple(record.relationship_id for record in default_relationship_records())
    diagnostic_ids = tuple(record.diagnostic_id for record in default_cross_boundary_diagnostics())
    all_ids = consistency_ids + relationship_ids + diagnostic_ids
    return ConsistencyEvidenceMetadata(
        evidence_id="v4_4_cross_boundary_consistency_replay_rollback_evidence",
        consistency_record_ids=consistency_ids,
        relationship_record_ids=relationship_ids,
        diagnostic_record_ids=diagnostic_ids,
        replay_evidence_ids=all_ids,
        rollback_evidence_ids=all_ids,
        deterministic_order=1,
    )


def default_cross_boundary_consistency_intelligence() -> CrossBoundaryConsistencyIntelligence:
    return CrossBoundaryConsistencyIntelligence(
        identity=default_cross_boundary_consistency_identity(),
        classifications=default_governance_consistency_classifications(),
        consistency_records=default_consistency_records(),
        relationship_records=default_relationship_records(),
        diagnostics=default_cross_boundary_diagnostics(),
        compatibility_consistency=default_compatibility_consistency(),
        continuity_consistency=default_continuity_consistency(),
        provenance_consistency=default_provenance_consistency_summary(),
        lineage_consistency=default_lineage_consistency_summary(),
        explainability=default_consistency_explainability(),
        evidence_metadata=default_consistency_evidence_metadata(),
        deterministic_guarantees=V4_4_CROSS_BOUNDARY_CONSISTENCY_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_CROSS_BOUNDARY_CONSISTENCY_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_CROSS_BOUNDARY_CONSISTENCY_EXPLICIT_PROHIBITIONS,
    )
