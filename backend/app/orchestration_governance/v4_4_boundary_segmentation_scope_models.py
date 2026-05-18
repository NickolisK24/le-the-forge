"""Deterministic v4.4 boundary segmentation and scope models.

The v4.4 Phase 5 layer models boundary segmentation and governance scope as
descriptive governance evidence only. It makes boundary groups, scoped
membership, isolation, coupling, overlap, ambiguity, continuity, provenance,
lineage, diagnostics, and explainability visible without using segmentation as
routing, dispatch, scheduling, authorization, execution, planner integration,
production consumption, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_SEGMENTATION_SCOPE_PHASE_ID = "v4_4_boundary_segmentation_scope"
V4_4_BOUNDARY_SEGMENTATION_SCOPE_SCHEMA_VERSION = "v4_4.boundary_segmentation_scope.1"
V4_4_BOUNDARY_SEGMENTATION_SCOPE_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_segmentation_scope_report.1"
)
V4_4_BOUNDARY_SEGMENTATION_SCOPE_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_STABLE = "v4_4_boundary_segmentation_scope_stable"
V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_BLOCKED = "v4_4_boundary_segmentation_scope_blocked"
V4_4_BOUNDARY_SEGMENTATION_SCOPE_PURPOSE = (
    "deterministic_governance_safe_boundary_segmentation_scope_intelligence_descriptive_only"
)
V4_4_BOUNDARY_SEGMENTATION_SCOPE_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_segmentation_scope_intelligence"
)

SEGMENTATION_SCOPE_STATE_SCOPED = "scoped"
SEGMENTATION_SCOPE_STATE_UNSCOPED = "unscoped"
SEGMENTATION_SCOPE_STATE_SEGMENTED = "segmented"
SEGMENTATION_SCOPE_STATE_UNSEGMENTED = "unsegmented"
SEGMENTATION_SCOPE_STATE_ISOLATED = "isolated"
SEGMENTATION_SCOPE_STATE_COUPLED = "coupled"
SEGMENTATION_SCOPE_STATE_OVERLAPPING = "overlapping"
SEGMENTATION_SCOPE_STATE_AMBIGUOUS = "ambiguous"
SEGMENTATION_SCOPE_STATE_CONSISTENT = "consistent"
SEGMENTATION_SCOPE_STATE_INCONSISTENT = "inconsistent"
SEGMENTATION_SCOPE_STATE_UNSUPPORTED = "unsupported"
SEGMENTATION_SCOPE_STATE_PROHIBITED = "prohibited"
SEGMENTATION_SCOPE_STATE_BLOCKED = "blocked"
SEGMENTATION_SCOPE_STATE_STALE = "stale"
SEGMENTATION_SCOPE_STATE_CONFLICTING = "conflicting"
SEGMENTATION_SCOPE_STATE_DEGRADED = "degraded"
BOUNDARY_SEGMENTATION_SCOPE_STATES: tuple[str, ...] = (
    SEGMENTATION_SCOPE_STATE_SCOPED,
    SEGMENTATION_SCOPE_STATE_UNSCOPED,
    SEGMENTATION_SCOPE_STATE_SEGMENTED,
    SEGMENTATION_SCOPE_STATE_UNSEGMENTED,
    SEGMENTATION_SCOPE_STATE_ISOLATED,
    SEGMENTATION_SCOPE_STATE_COUPLED,
    SEGMENTATION_SCOPE_STATE_OVERLAPPING,
    SEGMENTATION_SCOPE_STATE_AMBIGUOUS,
    SEGMENTATION_SCOPE_STATE_CONSISTENT,
    SEGMENTATION_SCOPE_STATE_INCONSISTENT,
    SEGMENTATION_SCOPE_STATE_UNSUPPORTED,
    SEGMENTATION_SCOPE_STATE_PROHIBITED,
    SEGMENTATION_SCOPE_STATE_BLOCKED,
    SEGMENTATION_SCOPE_STATE_STALE,
    SEGMENTATION_SCOPE_STATE_CONFLICTING,
    SEGMENTATION_SCOPE_STATE_DEGRADED,
)
FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES: tuple[str, ...] = (
    SEGMENTATION_SCOPE_STATE_UNSCOPED,
    SEGMENTATION_SCOPE_STATE_UNSEGMENTED,
    SEGMENTATION_SCOPE_STATE_COUPLED,
    SEGMENTATION_SCOPE_STATE_OVERLAPPING,
    SEGMENTATION_SCOPE_STATE_AMBIGUOUS,
    SEGMENTATION_SCOPE_STATE_INCONSISTENT,
    SEGMENTATION_SCOPE_STATE_UNSUPPORTED,
    SEGMENTATION_SCOPE_STATE_PROHIBITED,
    SEGMENTATION_SCOPE_STATE_BLOCKED,
    SEGMENTATION_SCOPE_STATE_STALE,
    SEGMENTATION_SCOPE_STATE_CONFLICTING,
    SEGMENTATION_SCOPE_STATE_DEGRADED,
)

SEGMENT_RELATIONSHIP_ISOLATION = "segment_isolation_visibility"
SEGMENT_RELATIONSHIP_COUPLING = "segment_coupling_visibility"
SEGMENT_RELATIONSHIP_OVERLAP = "segment_overlap_visibility"
SEGMENT_RELATIONSHIP_MEMBERSHIP = "scoped_membership_visibility"
SEGMENT_RELATIONSHIP_CONTINUITY = "segment_continuity_visibility"
SEGMENT_RELATIONSHIP_PROVENANCE = "scope_provenance_visibility"
SEGMENT_RELATIONSHIP_LINEAGE = "scope_lineage_visibility"
SEGMENT_RELATIONSHIP_TYPES: tuple[str, ...] = (
    SEGMENT_RELATIONSHIP_ISOLATION,
    SEGMENT_RELATIONSHIP_COUPLING,
    SEGMENT_RELATIONSHIP_OVERLAP,
    SEGMENT_RELATIONSHIP_MEMBERSHIP,
    SEGMENT_RELATIONSHIP_CONTINUITY,
    SEGMENT_RELATIONSHIP_PROVENANCE,
    SEGMENT_RELATIONSHIP_LINEAGE,
)

V4_4_BOUNDARY_SEGMENTATION_SCOPE_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_scheduling_execution_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_SEGMENTATION_SCOPE_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "segmentation_ordering_stability",
    "scope_ordering_stability",
    "segmentation_serialization_stability",
    "scope_serialization_stability",
    "segmentation_hashing_stability",
    "scope_hashing_stability",
    "segment_membership_visibility",
    "scope_ambiguity_visibility",
    "overlap_visibility",
    "isolation_coupling_visibility",
    "replay_safe_segmentation_evidence",
    "rollback_safe_segmentation_evidence",
    "provenance_visibility",
    "lineage_visibility",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_SEGMENTATION_SCOPE_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 5 models boundary segmentation and scope intelligence only.",
    "v4.4 Phase 5 segmentation visibility does not route work.",
    "v4.4 Phase 5 scope visibility does not authorize behavior.",
    "v4.4 Phase 5 boundary groups do not become routing lanes, dispatch lanes, schedule lanes, or execution paths.",
    "v4.4 Phase 5 does not execute orchestration.",
    "v4.4 Phase 5 does not authorize or approve orchestration.",
    "v4.4 Phase 5 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 5 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 5 does not integrate planners or consume production bundles.",
    "v4.4 Phase 5 does not repair, remediate, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_SEGMENTATION_SCOPE_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No segmentation system grants runtime authority.",
    "No scope result authorizes orchestration behavior.",
    "No boundary group becomes a routing lane, dispatch lane, schedule lane, or execution path.",
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
    "No segmentation-based routing exists.",
    "No scope-based authorization exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BoundarySegmentationScopeIdentity:
    segmentation_scope_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_foundation_reference: str
    source_cross_boundary_consistency_reference: str
    segment_reference: str
    scope_reference: str
    membership_reference: str
    diagnostics_reference: str
    provenance_reference: str
    lineage_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_SEGMENTATION_SCOPE_PURPOSE
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
    scheduling_execution_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class SegmentationClassification:
    classification_id: str
    subject_id: str
    segmentation_state: str
    classification_type: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    segmentation_enforcement_enabled: bool = False
    routing_authority: bool = False


@dataclass(frozen=True)
class ScopeClassification:
    classification_id: str
    subject_id: str
    scope_state: str
    classification_type: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    scope_authorization_enabled: bool = False
    operational_authority: bool = False


@dataclass(frozen=True)
class BoundarySegmentRecord:
    segment_id: str
    segment_name: str
    segment_state: str
    grouped_boundary_ids: tuple[str, ...]
    segmentation_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    segmentation_based_routing_enabled: bool = False
    boundary_group_execution_lane_enabled: bool = False
    runtime_execution_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "grouped_boundary_ids")
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class BoundaryScopeRecord:
    scope_id: str
    scope_name: str
    scope_state: str
    scoped_governance_ids: tuple[str, ...]
    scope_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    scope_based_authorization_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    runtime_execution_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "scoped_governance_ids")
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ScopedBoundaryMembershipRecord:
    membership_id: str
    scope_id: str
    segment_id: str
    boundary_id: str
    membership_state: str
    membership_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    routing_enabled: bool = False
    dispatch_enabled: bool = False
    scheduling_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SegmentRelationshipRecord:
    relationship_id: str
    source_segment_id: str
    target_segment_id: str
    relationship_type: str
    relationship_state: str
    relationship_boundary_ids: tuple[str, ...]
    relationship_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    routing_enabled: bool = False
    dispatch_enabled: bool = False
    scheduling_enabled: bool = False
    runtime_execution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "relationship_boundary_ids")


@dataclass(frozen=True)
class SegmentContinuityVisibility:
    continuity_id: str
    subject_id: str
    continuity_state: str
    continuity_type: str
    continuity_reference_ids: tuple[str, ...]
    continuity_reason: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    mutation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "continuity_reference_ids")


@dataclass(frozen=True)
class ScopeDiagnosticRecord:
    diagnostic_id: str
    subject_id: str
    diagnostic_type: str
    scope_state: str
    severity: str
    diagnostic_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    scope_based_authorization_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class SegmentationDiagnosticRecord:
    diagnostic_id: str
    subject_id: str
    diagnostic_type: str
    segmentation_state: str
    severity: str
    diagnostic_message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    segmentation_based_routing_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ScopeProvenanceVisibility:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    scope_reference_ids: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_visible: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references", "scope_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class ScopeLineageVisibility:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    segment_reference_ids: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_visible: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references", "segment_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class SegmentationExplainabilityRecord:
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
    routing_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "explanation_chain_ids")


@dataclass(frozen=True)
class SegmentationScopeEvidenceMetadata:
    evidence_id: str
    segment_record_ids: tuple[str, ...]
    scope_record_ids: tuple[str, ...]
    membership_record_ids: tuple[str, ...]
    relationship_record_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "segment_record_ids",
            "scope_record_ids",
            "membership_record_ids",
            "relationship_record_ids",
            "replay_evidence_ids",
            "rollback_evidence_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BoundarySegmentationScopeIntelligence:
    identity: BoundarySegmentationScopeIdentity
    segmentation_classifications: tuple[SegmentationClassification, ...]
    scope_classifications: tuple[ScopeClassification, ...]
    segment_records: tuple[BoundarySegmentRecord, ...]
    scope_records: tuple[BoundaryScopeRecord, ...]
    membership_records: tuple[ScopedBoundaryMembershipRecord, ...]
    relationship_records: tuple[SegmentRelationshipRecord, ...]
    continuity_visibility: tuple[SegmentContinuityVisibility, ...]
    scope_diagnostics: tuple[ScopeDiagnosticRecord, ...]
    segmentation_diagnostics: tuple[SegmentationDiagnosticRecord, ...]
    provenance_visibility: ScopeProvenanceVisibility
    lineage_visibility: ScopeLineageVisibility
    explainability: tuple[SegmentationExplainabilityRecord, ...]
    evidence_metadata: SegmentationScopeEvidenceMetadata
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_routing: bool = True
    non_dispatching: bool = True
    non_scheduling: bool = True
    non_remediating: bool = True
    non_mutating: bool = True
    runtime_execution_enabled: bool = False
    orchestration_runtime_behavior_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    segmentation_based_routing_enabled: bool = False
    scope_based_authorization_enabled: bool = False
    boundary_group_execution_lane_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "segmentation_classifications",
            "scope_classifications",
            "segment_records",
            "scope_records",
            "membership_records",
            "relationship_records",
            "continuity_visibility",
            "scope_diagnostics",
            "segmentation_diagnostics",
            "explainability",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_boundary_segmentation_scope_identity() -> BoundarySegmentationScopeIdentity:
    return BoundarySegmentationScopeIdentity(
        segmentation_scope_id="v4_4_boundary_segmentation_scope_intelligence",
        phase_id=V4_4_BOUNDARY_SEGMENTATION_SCOPE_PHASE_ID,
        schema_version=V4_4_BOUNDARY_SEGMENTATION_SCOPE_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_SEGMENTATION_SCOPE_GENERATED_AT,
        classification=V4_4_BOUNDARY_SEGMENTATION_SCOPE_CLASSIFICATION,
        source_foundation_reference="v4_4_boundary_intelligence_foundations",
        source_cross_boundary_consistency_reference="v4_4_cross_boundary_consistency",
        segment_reference="v4_4_boundary_segment_visibility",
        scope_reference="v4_4_boundary_scope_visibility",
        membership_reference="v4_4_scoped_boundary_membership_visibility",
        diagnostics_reference="v4_4_boundary_segmentation_scope_diagnostics",
        provenance_reference="v4_4_boundary_scope_provenance_visibility",
        lineage_reference="v4_4_boundary_scope_lineage_visibility",
        non_operational_reference="v4_4_boundary_segmentation_scope_non_operational_certification",
    )


def default_segment_records() -> tuple[BoundarySegmentRecord, ...]:
    definitions = (
        ("segment_governance_core", "Governance core", SEGMENTATION_SCOPE_STATE_SEGMENTED, ("boundary_foundation", "cross_boundary_consistency")),
        ("segment_unsegmented_external_runtime", "External runtime boundary", SEGMENTATION_SCOPE_STATE_UNSEGMENTED, ("runtime_semantics_visibility",)),
        ("segment_isolated_provenance", "Provenance isolation", SEGMENTATION_SCOPE_STATE_ISOLATED, ("provenance_visibility",)),
        ("segment_coupled_lineage", "Lineage coupling", SEGMENTATION_SCOPE_STATE_COUPLED, ("lineage_visibility", "continuity_visibility")),
        ("segment_overlap_refinement", "Refinement overlap", SEGMENTATION_SCOPE_STATE_OVERLAPPING, ("inheritance_refinement", "drift_visibility")),
        ("segment_ambiguous_provider", "Provider ambiguity", SEGMENTATION_SCOPE_STATE_AMBIGUOUS, ("provider_identity_visibility",)),
    )
    return tuple(
        BoundarySegmentRecord(
            segment_id=segment_id,
            segment_name=segment_name,
            segment_state=state,
            grouped_boundary_ids=boundary_ids,
            segmentation_reason=f"{state} segment visibility remains descriptive and non-routing",
            evidence_reference_ids=(
                "v4_4_cross_boundary_consistency_report",
                segment_id,
                *boundary_ids,
            ),
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES,
        )
        for index, (segment_id, segment_name, state, boundary_ids) in enumerate(definitions, start=1)
    )


def default_scope_records() -> tuple[BoundaryScopeRecord, ...]:
    definitions = (
        ("scope_governance_visible", "Governance visibility scope", SEGMENTATION_SCOPE_STATE_SCOPED, ("boundary_foundation", "segment_governance_core")),
        ("scope_external_runtime_unscoped", "External runtime scope", SEGMENTATION_SCOPE_STATE_UNSCOPED, ("runtime_semantics_visibility",)),
        ("scope_consistency_baseline", "Consistency baseline scope", SEGMENTATION_SCOPE_STATE_CONSISTENT, ("cross_boundary_consistency",)),
        ("scope_inconsistent_authority", "Authority mismatch scope", SEGMENTATION_SCOPE_STATE_INCONSISTENT, ("runtime_authority_visibility",)),
        ("scope_stale_source", "Stale source scope", SEGMENTATION_SCOPE_STATE_STALE, ("stale_source_visibility",)),
        ("scope_degraded_lineage", "Degraded lineage scope", SEGMENTATION_SCOPE_STATE_DEGRADED, ("lineage_visibility", "continuity_visibility")),
    )
    return tuple(
        BoundaryScopeRecord(
            scope_id=scope_id,
            scope_name=scope_name,
            scope_state=state,
            scoped_governance_ids=governance_ids,
            scope_reason=f"{state} scope visibility remains descriptive and non-authorizing",
            evidence_reference_ids=("v4_4_cross_boundary_consistency_report", scope_id, *governance_ids),
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES,
        )
        for index, (scope_id, scope_name, state, governance_ids) in enumerate(definitions, start=1)
    )


def default_membership_records() -> tuple[ScopedBoundaryMembershipRecord, ...]:
    definitions = (
        ("membership_foundation_scoped", "scope_governance_visible", "segment_governance_core", "boundary_foundation", SEGMENTATION_SCOPE_STATE_SCOPED),
        ("membership_runtime_unscoped", "scope_external_runtime_unscoped", "segment_unsegmented_external_runtime", "runtime_semantics_visibility", SEGMENTATION_SCOPE_STATE_UNSCOPED),
        ("membership_consistency_segmented", "scope_consistency_baseline", "segment_governance_core", "cross_boundary_consistency", SEGMENTATION_SCOPE_STATE_SEGMENTED),
        ("membership_provider_ambiguous", "scope_external_runtime_unscoped", "segment_ambiguous_provider", "provider_identity_visibility", SEGMENTATION_SCOPE_STATE_AMBIGUOUS),
        ("membership_overlap_conflicting", "scope_inconsistent_authority", "segment_overlap_refinement", "drift_visibility", SEGMENTATION_SCOPE_STATE_CONFLICTING),
        ("membership_lineage_blocked", "scope_degraded_lineage", "segment_coupled_lineage", "lineage_visibility", SEGMENTATION_SCOPE_STATE_BLOCKED),
    )
    return tuple(
        ScopedBoundaryMembershipRecord(
            membership_id=membership_id,
            scope_id=scope_id,
            segment_id=segment_id,
            boundary_id=boundary_id,
            membership_state=state,
            membership_reason=f"{state} scoped membership is visible and non-routing",
            evidence_reference_ids=(scope_id, segment_id, boundary_id),
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES,
        )
        for index, (membership_id, scope_id, segment_id, boundary_id, state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_relationship_records() -> tuple[SegmentRelationshipRecord, ...]:
    definitions = (
        ("relationship_core_isolated", "segment_governance_core", "segment_isolated_provenance", SEGMENT_RELATIONSHIP_ISOLATION, SEGMENTATION_SCOPE_STATE_ISOLATED, ("boundary_foundation", "provenance_visibility")),
        ("relationship_lineage_coupled", "segment_coupled_lineage", "segment_governance_core", SEGMENT_RELATIONSHIP_COUPLING, SEGMENTATION_SCOPE_STATE_COUPLED, ("lineage_visibility", "continuity_visibility")),
        ("relationship_refinement_overlap", "segment_overlap_refinement", "segment_governance_core", SEGMENT_RELATIONSHIP_OVERLAP, SEGMENTATION_SCOPE_STATE_OVERLAPPING, ("inheritance_refinement", "drift_visibility")),
        ("relationship_consistency_supported", "segment_governance_core", "segment_coupled_lineage", SEGMENT_RELATIONSHIP_CONTINUITY, SEGMENTATION_SCOPE_STATE_CONSISTENT, ("cross_boundary_consistency",)),
        ("relationship_scope_inconsistent", "segment_unsegmented_external_runtime", "segment_governance_core", SEGMENT_RELATIONSHIP_MEMBERSHIP, SEGMENTATION_SCOPE_STATE_INCONSISTENT, ("runtime_semantics_visibility",)),
        ("relationship_runtime_prohibited", "segment_unsegmented_external_runtime", "segment_overlap_refinement", SEGMENT_RELATIONSHIP_OVERLAP, SEGMENTATION_SCOPE_STATE_PROHIBITED, ("runtime_authority_visibility",)),
    )
    return tuple(
        SegmentRelationshipRecord(
            relationship_id=relationship_id,
            source_segment_id=source_segment_id,
            target_segment_id=target_segment_id,
            relationship_type=relationship_type,
            relationship_state=state,
            relationship_boundary_ids=boundary_ids,
            relationship_reason=f"{state} segment relationship remains descriptive and non-operational",
            deterministic_order=index,
            fail_visible=state in FAIL_VISIBLE_BOUNDARY_SEGMENTATION_SCOPE_STATES,
        )
        for index, (
            relationship_id,
            source_segment_id,
            target_segment_id,
            relationship_type,
            state,
            boundary_ids,
        ) in enumerate(definitions, start=1)
    )


def default_continuity_visibility() -> tuple[SegmentContinuityVisibility, ...]:
    definitions = (
        ("continuity_scope_consistent", "scope_governance_visible", SEGMENTATION_SCOPE_STATE_CONSISTENT, ("scope_governance_visible", "segment_governance_core")),
        ("continuity_scope_stale", "scope_stale_source", SEGMENTATION_SCOPE_STATE_STALE, ("scope_stale_source", "stale_source_visibility")),
        ("continuity_scope_degraded", "scope_degraded_lineage", SEGMENTATION_SCOPE_STATE_DEGRADED, ("scope_degraded_lineage", "lineage_visibility")),
        ("continuity_scope_unsupported", "scope_external_runtime_unscoped", SEGMENTATION_SCOPE_STATE_UNSUPPORTED, ("scope_external_runtime_unscoped", "runtime_semantics_visibility")),
    )
    return tuple(
        SegmentContinuityVisibility(
            continuity_id=continuity_id,
            subject_id=subject_id,
            continuity_state=state,
            continuity_type=f"{state}_scope_continuity_visibility",
            continuity_reference_ids=reference_ids,
            continuity_reason=f"{state} scope continuity remains visible and non-mutating",
            deterministic_order=index,
            fail_visible=True,
        )
        for index, (continuity_id, subject_id, state, reference_ids) in enumerate(definitions, start=1)
    )


def default_segmentation_classifications() -> tuple[SegmentationClassification, ...]:
    subjects = (*default_segment_records(), *default_relationship_records())
    classifications: list[SegmentationClassification] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = getattr(subject, "segment_id", None) or getattr(subject, "relationship_id")
        state = getattr(subject, "segment_state", None) or getattr(subject, "relationship_state")
        classifications.append(
            SegmentationClassification(
                classification_id=f"classification_{subject_id}",
                subject_id=str(subject_id),
                segmentation_state=str(state),
                classification_type=f"{state}_segmentation_visibility",
                classification_reason=f"{state} segmentation classification remains descriptive-only",
                deterministic_order=index,
            )
        )
    return tuple(classifications)


def default_scope_classifications() -> tuple[ScopeClassification, ...]:
    subjects = (*default_scope_records(), *default_membership_records(), *default_continuity_visibility())
    classifications: list[ScopeClassification] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = (
            getattr(subject, "scope_id", None)
            or getattr(subject, "membership_id", None)
            or getattr(subject, "continuity_id", None)
        )
        state = (
            getattr(subject, "scope_state", None)
            or getattr(subject, "membership_state", None)
            or getattr(subject, "continuity_state")
        )
        classifications.append(
            ScopeClassification(
                classification_id=f"classification_{subject_id}",
                subject_id=str(subject_id),
                scope_state=str(state),
                classification_type=f"{state}_scope_visibility",
                classification_reason=f"{state} scope classification remains descriptive-only",
                deterministic_order=index,
            )
        )
    return tuple(classifications)


def _severity_for_state(state: str) -> str:
    return {
        SEGMENTATION_SCOPE_STATE_SCOPED: "info",
        SEGMENTATION_SCOPE_STATE_SEGMENTED: "info",
        SEGMENTATION_SCOPE_STATE_ISOLATED: "info",
        SEGMENTATION_SCOPE_STATE_CONSISTENT: "info",
        SEGMENTATION_SCOPE_STATE_UNSUPPORTED: "warning",
        SEGMENTATION_SCOPE_STATE_PROHIBITED: "prohibited",
        SEGMENTATION_SCOPE_STATE_BLOCKED: "blocker",
    }.get(state, "warning")


def default_scope_diagnostics() -> tuple[ScopeDiagnosticRecord, ...]:
    return tuple(
        ScopeDiagnosticRecord(
            diagnostic_id=f"scope_diagnostic_{record.scope_id}",
            subject_id=record.scope_id,
            diagnostic_type=f"{record.scope_state}_scope_diagnostic",
            scope_state=record.scope_state,
            severity=_severity_for_state(record.scope_state),
            diagnostic_message=f"{record.scope_state} scope diagnostic remains visible without authorization",
            evidence_reference_ids=record.evidence_reference_ids,
            deterministic_order=index,
        )
        for index, record in enumerate(default_scope_records(), start=1)
    )


def default_segmentation_diagnostics() -> tuple[SegmentationDiagnosticRecord, ...]:
    subjects = (*default_segment_records(), *default_relationship_records())
    diagnostics: list[SegmentationDiagnosticRecord] = []
    for index, subject in enumerate(subjects, start=1):
        subject_id = getattr(subject, "segment_id", None) or getattr(subject, "relationship_id")
        state = getattr(subject, "segment_state", None) or getattr(subject, "relationship_state")
        diagnostics.append(
            SegmentationDiagnosticRecord(
                diagnostic_id=f"segmentation_diagnostic_{subject_id}",
                subject_id=str(subject_id),
                diagnostic_type=f"{state}_segmentation_diagnostic",
                segmentation_state=str(state),
                severity=_severity_for_state(str(state)),
                diagnostic_message=f"{state} segmentation diagnostic remains visible without routing",
                evidence_reference_ids=getattr(subject, "evidence_reference_ids", None)
                or getattr(subject, "relationship_boundary_ids"),
                deterministic_order=index,
            )
        )
    return tuple(diagnostics)


def default_segmentation_explainability() -> tuple[SegmentationExplainabilityRecord, ...]:
    diagnostics = (*default_scope_diagnostics(), *default_segmentation_diagnostics())
    records: list[SegmentationExplainabilityRecord] = []
    for index, diagnostic in enumerate(diagnostics, start=1):
        state = getattr(diagnostic, "scope_state", None) or getattr(diagnostic, "segmentation_state")
        records.append(
            SegmentationExplainabilityRecord(
                explainability_id=f"explainability_{diagnostic.diagnostic_id}",
                subject_id=diagnostic.subject_id,
                explanation_type=f"{state}_segmentation_scope_explainability",
                visibility_state=str(state),
                explanation_chain_ids=(
                    diagnostic.subject_id,
                    diagnostic.diagnostic_id,
                    V4_4_BOUNDARY_SEGMENTATION_SCOPE_PHASE_ID,
                ),
                explanation="Segmentation and scope evidence explains visibility without routing or authorization",
                deterministic_order=index,
            )
        )
    return tuple(records)


def _segment_ids() -> tuple[str, ...]:
    return tuple(record.segment_id for record in default_segment_records())


def _scope_ids() -> tuple[str, ...]:
    return tuple(record.scope_id for record in default_scope_records())


def default_scope_provenance_visibility() -> ScopeProvenanceVisibility:
    return ScopeProvenanceVisibility(
        provenance_id="v4_4_boundary_scope_provenance_visibility",
        source_reference_ids=(
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            "v4_4_boundary_conflict_drift",
            "v4_4_cross_boundary_consistency",
            V4_4_BOUNDARY_SEGMENTATION_SCOPE_PHASE_ID,
        ),
        source_hash_references=(
            "v4_4_boundary_intelligence_foundations.deterministic_report_hash",
            "v4_4_boundary_inheritance_refinement.deterministic_report_hash",
            "v4_4_boundary_conflict_drift.deterministic_report_hash",
            "v4_4_cross_boundary_consistency.deterministic_report_hash",
        ),
        scope_reference_ids=_scope_ids(),
        provenance_state="scope_provenance_visible",
        deterministic_order=1,
    )


def default_scope_lineage_visibility() -> ScopeLineageVisibility:
    return ScopeLineageVisibility(
        lineage_id="v4_4_boundary_scope_lineage_visibility",
        lineage_reference_ids=(
            "v4_3_orchestration_continuity_and_integrity_certification",
            "v4_4_boundary_intelligence_foundations",
            "v4_4_boundary_inheritance_refinement",
            "v4_4_boundary_conflict_drift",
            "v4_4_cross_boundary_consistency",
            V4_4_BOUNDARY_SEGMENTATION_SCOPE_PHASE_ID,
        ),
        lineage_hash_references=(
            "v4_3_continuity_integrity_hash_reference",
            "v4_4_boundary_intelligence_hash_reference",
            "v4_4_boundary_inheritance_hash_reference",
            "v4_4_boundary_conflict_drift_hash_reference",
            "v4_4_cross_boundary_consistency_hash_reference",
        ),
        segment_reference_ids=_segment_ids(),
        lineage_state="scope_lineage_visible",
        deterministic_order=1,
    )


def default_segmentation_scope_evidence_metadata() -> SegmentationScopeEvidenceMetadata:
    segment_ids = tuple(record.segment_id for record in default_segment_records())
    scope_ids = tuple(record.scope_id for record in default_scope_records())
    membership_ids = tuple(record.membership_id for record in default_membership_records())
    relationship_ids = tuple(record.relationship_id for record in default_relationship_records())
    all_ids = segment_ids + scope_ids + membership_ids + relationship_ids
    return SegmentationScopeEvidenceMetadata(
        evidence_id="v4_4_boundary_segmentation_scope_replay_rollback_evidence",
        segment_record_ids=segment_ids,
        scope_record_ids=scope_ids,
        membership_record_ids=membership_ids,
        relationship_record_ids=relationship_ids,
        replay_evidence_ids=all_ids,
        rollback_evidence_ids=all_ids,
        deterministic_order=1,
    )


def default_boundary_segmentation_scope_intelligence() -> BoundarySegmentationScopeIntelligence:
    return BoundarySegmentationScopeIntelligence(
        identity=default_boundary_segmentation_scope_identity(),
        segmentation_classifications=default_segmentation_classifications(),
        scope_classifications=default_scope_classifications(),
        segment_records=default_segment_records(),
        scope_records=default_scope_records(),
        membership_records=default_membership_records(),
        relationship_records=default_relationship_records(),
        continuity_visibility=default_continuity_visibility(),
        scope_diagnostics=default_scope_diagnostics(),
        segmentation_diagnostics=default_segmentation_diagnostics(),
        provenance_visibility=default_scope_provenance_visibility(),
        lineage_visibility=default_scope_lineage_visibility(),
        explainability=default_segmentation_explainability(),
        evidence_metadata=default_segmentation_scope_evidence_metadata(),
        deterministic_guarantees=V4_4_BOUNDARY_SEGMENTATION_SCOPE_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_SEGMENTATION_SCOPE_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_SEGMENTATION_SCOPE_EXPLICIT_PROHIBITIONS,
    )
