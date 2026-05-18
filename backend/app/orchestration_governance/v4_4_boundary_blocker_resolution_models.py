"""Deterministic v4.4 boundary blocker resolution closeout models.

The v4.4 Phase 9 layer classifies, preserves, resolves, or escalates Phase 8
readiness blockers and warnings as descriptive closeout preparation evidence
only. Blocker resolution is visibility, not remediation: it does not authorize
execution, approve or activate orchestration, infer runtime readiness, integrate
planners, consume production inputs, suppress warnings, or mutate state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID = "v4_4_boundary_blocker_resolution"
V4_4_BOUNDARY_BLOCKER_RESOLUTION_SCHEMA_VERSION = (
    "v4_4.boundary_blocker_resolution.1"
)
V4_4_BOUNDARY_BLOCKER_RESOLUTION_REPORT_SCHEMA_VERSION = (
    "v4_4.boundary_blocker_resolution_report.1"
)
V4_4_BOUNDARY_BLOCKER_RESOLUTION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_STABLE = (
    "v4_4_boundary_blocker_resolution_stable"
)
V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_BLOCKED = (
    "v4_4_boundary_blocker_resolution_blocked"
)
V4_4_BOUNDARY_BLOCKER_RESOLUTION_PURPOSE = (
    "deterministic_governance_safe_blocker_resolution_closeout_preparation"
)
V4_4_BOUNDARY_BLOCKER_RESOLUTION_CLASSIFICATION = (
    "governance_safe_descriptive_blocker_resolution_closeout_preparation"
)

BLOCKER_STATE_RESOLVED = "resolved"
BLOCKER_STATE_INTENTIONALLY_PRESERVED = "intentionally_preserved"
BLOCKER_STATE_INHERITED_PROHIBITION = "inherited_prohibition"
BLOCKER_STATE_INHERITED_CONSTRAINT = "inherited_constraint"
BLOCKER_STATE_ESCALATED = "escalated"
BLOCKER_STATE_CLOSEOUT_READY = "closeout_ready"
BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS = "closeout_ready_with_limitations"
BLOCKER_STATE_CLOSEOUT_BLOCKED = "closeout_blocked"
BLOCKER_STATE_SUPPORTED = "supported"
BLOCKER_STATE_UNSUPPORTED = "unsupported"
BLOCKER_STATE_PROHIBITED = "prohibited"
BLOCKER_STATE_BLOCKED = "blocked"
BLOCKER_STATE_STALE = "stale"
BLOCKER_STATE_CONFLICTING = "conflicting"
BLOCKER_STATE_AMBIGUOUS = "ambiguous"
BLOCKER_STATE_DEGRADED = "degraded"
BLOCKER_STATE_WARNING = "warning"
BLOCKER_STATE_INFORMATIONAL = "informational"

BOUNDARY_BLOCKER_RESOLUTION_STATES: tuple[str, ...] = (
    BLOCKER_STATE_RESOLVED,
    BLOCKER_STATE_INTENTIONALLY_PRESERVED,
    BLOCKER_STATE_INHERITED_PROHIBITION,
    BLOCKER_STATE_INHERITED_CONSTRAINT,
    BLOCKER_STATE_ESCALATED,
    BLOCKER_STATE_CLOSEOUT_READY,
    BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
    BLOCKER_STATE_CLOSEOUT_BLOCKED,
    BLOCKER_STATE_SUPPORTED,
    BLOCKER_STATE_UNSUPPORTED,
    BLOCKER_STATE_PROHIBITED,
    BLOCKER_STATE_BLOCKED,
    BLOCKER_STATE_STALE,
    BLOCKER_STATE_CONFLICTING,
    BLOCKER_STATE_AMBIGUOUS,
    BLOCKER_STATE_DEGRADED,
    BLOCKER_STATE_WARNING,
    BLOCKER_STATE_INFORMATIONAL,
)

FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES: tuple[str, ...] = (
    BLOCKER_STATE_INTENTIONALLY_PRESERVED,
    BLOCKER_STATE_INHERITED_PROHIBITION,
    BLOCKER_STATE_INHERITED_CONSTRAINT,
    BLOCKER_STATE_ESCALATED,
    BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
    BLOCKER_STATE_CLOSEOUT_BLOCKED,
    BLOCKER_STATE_UNSUPPORTED,
    BLOCKER_STATE_PROHIBITED,
    BLOCKER_STATE_BLOCKED,
    BLOCKER_STATE_STALE,
    BLOCKER_STATE_CONFLICTING,
    BLOCKER_STATE_AMBIGUOUS,
    BLOCKER_STATE_DEGRADED,
    BLOCKER_STATE_WARNING,
)

V4_4_BOUNDARY_BLOCKER_RESOLUTION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_orchestration_activation_count",
    "enabled_dispatch_execution_count",
    "enabled_routing_execution_count",
    "enabled_scheduling_execution_count",
    "enabled_recommendation_count",
    "enabled_decision_count",
    "enabled_blocker_authorization_count",
    "enabled_closeout_activation_count",
    "enabled_operational_mutation_count",
)

V4_4_BOUNDARY_BLOCKER_RESOLUTION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "blocker_classification_ordering_stability",
    "warning_classification_ordering_stability",
    "blocker_serialization_stability",
    "warning_serialization_stability",
    "escalation_hashing_stability",
    "closeout_hashing_stability",
    "fail_visible_blocker_preservation",
    "inherited_prohibition_preservation",
    "inherited_constraint_preservation",
    "unresolved_limitation_visibility",
    "escalation_trace_visibility",
    "v4_5_planning_boundary_preservation",
    "replay_safe_evidence",
    "rollback_safe_evidence",
    "provenance_continuity_preservation",
    "lineage_continuity_preservation",
    "governance_safe_descriptive_only_enforcement",
    "non_operational_certification",
)

V4_4_BOUNDARY_BLOCKER_RESOLUTION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.4 Phase 9 classifies and preserves blockers for closeout preparation only.",
    "v4.4 Phase 9 blocker resolution is visibility, not automatic remediation.",
    "v4.4 Phase 9 warning classification does not suppress fail-visible evidence.",
    "v4.4 Phase 9 closeout eligibility is not runtime readiness.",
    "v4.4 Phase 9 escalation visibility does not activate runtime behavior.",
    "v4.4 Phase 9 does not execute orchestration.",
    "v4.4 Phase 9 does not authorize, approve, or activate orchestration.",
    "v4.4 Phase 9 does not dispatch, route, traverse, schedule, or sequence orchestration.",
    "v4.4 Phase 9 does not recommend, rank, score, select, optimize, or decide orchestration.",
    "v4.4 Phase 9 does not integrate planners or consume production bundles.",
    "v4.4 Phase 9 does not repair, remediate, or mutate runtime or operational state.",
)

V4_4_BOUNDARY_BLOCKER_RESOLUTION_EXPLICIT_PROHIBITIONS: tuple[str, ...] = (
    "No blocker resolution system grants runtime authority.",
    "No closeout preparation system authorizes orchestration behavior.",
    "No escalation result activates runtime behavior, planner integration, production consumption, recommendation, decision, approval, or execution.",
    "No blocker classification becomes operational approval.",
    "No warning classification suppresses fail-visible evidence.",
    "No closeout preparation implies runtime activation.",
    "No orchestration execution exists.",
    "No orchestration authorization exists.",
    "No orchestration approval exists.",
    "No orchestration activation exists.",
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
    "No blocker auto-resolution exists.",
    "No warning suppression exists.",
    "No readiness-based authorization exists.",
    "No closeout-based activation exists.",
    "No runtime mutation exists.",
    "No operational mutation exists.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class BlockerClassificationIdentity:
    blocker_classification_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    blocker_reference: str
    warning_reference: str
    closeout_reference: str
    escalation_reference: str
    non_operational_reference: str
    purpose: str = V4_4_BOUNDARY_BLOCKER_RESOLUTION_PURPOSE
    deterministic: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    integrity_safe: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_activation_enabled: bool = False
    blocker_authorization_enabled: bool = False
    closeout_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class WarningClassificationIdentity:
    warning_classification_id: str
    phase_id: str
    schema_version: str
    warning_reference: str
    fail_visible_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    non_operational: bool = True
    warning_suppression_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False


@dataclass(frozen=True)
class CloseoutEligibilityIdentity:
    closeout_eligibility_id: str
    phase_id: str
    eligibility_reference: str
    limitation_reference: str
    escalation_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    closeout_activation_enabled: bool = False
    runtime_readiness_inferred: bool = False


@dataclass(frozen=True)
class V45InheritedPlanningBoundaryIdentity:
    planning_boundary_id: str
    phase_id: str
    planning_boundary_reference: str
    inherited_constraint_reference: str
    inherited_prohibition_reference: str
    deterministic_order: int
    descriptive_only: bool = True
    planning_only: bool = True
    v4_5_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class Phase8ReadinessEvidenceReference:
    evidence_id: str
    source_phase_id: str
    source_report_reference: str
    source_hash_reference: str
    readiness_state: str
    blocker_state: str
    warning_state: str
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class BlockerClassificationRecord:
    blocker_id: str
    source_phase_id: str
    classification_state: str
    closeout_state: str
    severity: str
    blocker_summary: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    blocker_authorization_enabled: bool = False
    approval_enabled: bool = False
    activation_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    automatic_remediation_enabled: bool = False
    blocker_auto_resolution_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class WarningClassificationRecord:
    warning_id: str
    source_phase_id: str
    classification_state: str
    warning_state: str
    severity: str
    warning_summary: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    warning_suppression_enabled: bool = False
    approval_enabled: bool = False
    activation_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    automatic_remediation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class InheritedProhibitionRecord:
    prohibition_id: str
    prohibition_state: str
    prohibited_behavior: str
    inherited_from_phase_ids: tuple[str, ...]
    planning_boundary_reference: str
    deterministic_order: int
    fail_visible: bool = True
    is_prohibition: bool = True
    descriptive_only: bool = True
    planning_only: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "inherited_from_phase_ids")


@dataclass(frozen=True)
class InheritedConstraintRecord:
    constraint_id: str
    constraint_state: str
    constraint_type: str
    constraint_summary: str
    inherited_from_phase_ids: tuple[str, ...]
    deterministic_order: int
    inherited_by_v4_5: bool = True
    descriptive_only: bool = True
    planning_only: bool = True
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    v4_5_activation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "inherited_from_phase_ids")


@dataclass(frozen=True)
class UnresolvedLimitationRecord:
    limitation_id: str
    source_phase_id: str
    limitation_state: str
    limitation_summary: str
    inherited_by_v4_5: bool
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EscalationRecord:
    escalation_id: str
    source_finding_id: str
    escalation_state: str
    escalation_summary: str
    trace_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    non_actioning: bool = True
    closeout_activation_enabled: bool = False
    automatic_remediation_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "trace_reference_ids")


@dataclass(frozen=True)
class CloseoutEligibilityRecord:
    eligibility_id: str
    subject_id: str
    eligibility_state: str
    classification_state: str
    eligibility_summary: str
    limitation_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    closeout_activation_enabled: bool = False
    readiness_authorization_enabled: bool = False
    runtime_readiness_inferred: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "limitation_reference_ids")


@dataclass(frozen=True)
class V45InheritedPlanningBoundaryRecord:
    planning_boundary_id: str
    boundary_state: str
    planning_boundary_state: str
    boundary_summary: str
    inherited_constraint_ids: tuple[str, ...]
    inherited_prohibition_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    planning_only: bool = True
    v4_5_activation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_readiness_inferred: bool = False

    def __post_init__(self) -> None:
        for field_name in ("inherited_constraint_ids", "inherited_prohibition_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class FailVisibleExplanationRecord:
    explanation_id: str
    explanation_state: str
    explanation_type: str
    explanation_summary: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool
    descriptive_only: bool = True
    non_authoritative: bool = True
    approval_enabled: bool = False
    activation_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class NonOperationalBlockerCertificationRecord:
    certification_id: str
    certification_state: str
    certification_summary: str
    deterministic_order: int
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_activation_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    blocker_authorization_enabled: bool = False
    closeout_activation_enabled: bool = False
    operational_mutation_enabled: bool = False


@dataclass(frozen=True)
class BlockerResolutionProvenanceRecord:
    provenance_id: str
    source_reference_ids: tuple[str, ...]
    source_hash_references: tuple[str, ...]
    provenance_state: str
    deterministic_order: int
    provenance_continuity_preserved: bool = True
    hidden_source_inference_used: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("source_reference_ids", "source_hash_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BlockerResolutionLineageRecord:
    lineage_id: str
    lineage_reference_ids: tuple[str, ...]
    lineage_hash_references: tuple[str, ...]
    lineage_state: str
    deterministic_order: int
    lineage_continuity_preserved: bool = True
    ambiguous_lineage_inferred: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("lineage_reference_ids", "lineage_hash_references"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class BlockerResolutionReplayRollbackRecord:
    evidence_id: str
    replay_state: str
    rollback_state: str
    evidence_reference_ids: tuple[str, ...]
    replay_evidence_ids: tuple[str, ...]
    rollback_evidence_ids: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("evidence_reference_ids", "replay_evidence_ids", "rollback_evidence_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class CloseoutPreparationSummaryRecord:
    summary_id: str
    closeout_state: str
    blocker_state: str
    warning_state: str
    escalation_state: str
    certification_state: str
    summary_reference_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    planning_only: bool = True
    non_operational: bool = True
    closeout_activation_signal_enabled: bool = False
    blocker_authorization_signal_enabled: bool = False
    runtime_readiness_inferred: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "summary_reference_ids")


@dataclass(frozen=True)
class BoundaryBlockerResolutionCloseoutPreparation:
    blocker_identity: BlockerClassificationIdentity
    warning_identity: WarningClassificationIdentity
    closeout_identity: CloseoutEligibilityIdentity
    planning_boundary_identity: V45InheritedPlanningBoundaryIdentity
    phase8_evidence_references: tuple[Phase8ReadinessEvidenceReference, ...]
    blocker_records: tuple[BlockerClassificationRecord, ...]
    warning_records: tuple[WarningClassificationRecord, ...]
    inherited_prohibition_records: tuple[InheritedProhibitionRecord, ...]
    inherited_constraint_records: tuple[InheritedConstraintRecord, ...]
    limitation_records: tuple[UnresolvedLimitationRecord, ...]
    escalation_records: tuple[EscalationRecord, ...]
    closeout_eligibility_records: tuple[CloseoutEligibilityRecord, ...]
    planning_boundary_records: tuple[V45InheritedPlanningBoundaryRecord, ...]
    fail_visible_explanations: tuple[FailVisibleExplanationRecord, ...]
    non_operational_certifications: tuple[NonOperationalBlockerCertificationRecord, ...]
    provenance_record: BlockerResolutionProvenanceRecord
    lineage_record: BlockerResolutionLineageRecord
    replay_rollback_record: BlockerResolutionReplayRollbackRecord
    closeout_summaries: tuple[CloseoutPreparationSummaryRecord, ...]
    deterministic_guarantees: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    explicit_prohibitions: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_authoritative: bool = True
    non_authorizing: bool = True
    non_approving: bool = True
    non_activating: bool = True
    non_recommending: bool = True
    non_deciding: bool = True
    non_remediating: bool = True
    non_mutating: bool = True
    runtime_readiness_inference_disabled: bool = True
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_activation_enabled: bool = False
    dispatch_execution_enabled: bool = False
    routing_execution_enabled: bool = False
    scheduling_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    sequencing_execution_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False
    blocker_authorization_enabled: bool = False
    closeout_activation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    optimization_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    blocker_auto_resolution_enabled: bool = False
    warning_suppression_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "phase8_evidence_references",
            "blocker_records",
            "warning_records",
            "inherited_prohibition_records",
            "inherited_constraint_records",
            "limitation_records",
            "escalation_records",
            "closeout_eligibility_records",
            "planning_boundary_records",
            "fail_visible_explanations",
            "non_operational_certifications",
            "closeout_summaries",
            "deterministic_guarantees",
            "explicit_limitations",
            "explicit_prohibitions",
        ):
            _set_tuple_field(self, field_name)


def default_phase_ids() -> tuple[str, ...]:
    return (
        "v4_4_boundary_intelligence_foundations",
        "v4_4_boundary_inheritance_refinement",
        "v4_4_boundary_conflict_drift",
        "v4_4_cross_boundary_consistency",
        "v4_4_boundary_segmentation_scope",
        "v4_4_boundary_explainability_aggregation",
        "v4_4_boundary_continuity_integrity",
        "v4_4_boundary_readiness_transition",
    )


def default_blocker_identity() -> BlockerClassificationIdentity:
    return BlockerClassificationIdentity(
        blocker_classification_id="v4_4_boundary_blocker_classification_identity",
        phase_id=V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID,
        schema_version=V4_4_BOUNDARY_BLOCKER_RESOLUTION_SCHEMA_VERSION,
        generated_at=V4_4_BOUNDARY_BLOCKER_RESOLUTION_GENERATED_AT,
        classification=V4_4_BOUNDARY_BLOCKER_RESOLUTION_CLASSIFICATION,
        blocker_reference="v4_4_phase_8_blocker_visibility",
        warning_reference="v4_4_phase_8_warning_visibility",
        closeout_reference="v4_4_closeout_preparation_visibility",
        escalation_reference="v4_4_fail_visible_escalation_visibility",
        non_operational_reference="v4_4_phase_9_non_operational_certification",
    )


def default_warning_identity() -> WarningClassificationIdentity:
    return WarningClassificationIdentity(
        warning_classification_id="v4_4_boundary_warning_classification_identity",
        phase_id=V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID,
        schema_version=V4_4_BOUNDARY_BLOCKER_RESOLUTION_SCHEMA_VERSION,
        warning_reference="v4_4_phase_8_warning_visibility",
        fail_visible_reference="v4_4_warning_fail_visible_preservation",
        deterministic_order=1,
    )


def default_closeout_identity() -> CloseoutEligibilityIdentity:
    return CloseoutEligibilityIdentity(
        closeout_eligibility_id="v4_4_boundary_closeout_eligibility_identity",
        phase_id=V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID,
        eligibility_reference="v4_4_closeout_ready_with_limitations_visibility",
        limitation_reference="v4_4_unresolved_limitation_visibility",
        escalation_reference="v4_4_escalation_trace_visibility",
        deterministic_order=1,
    )


def default_planning_boundary_identity() -> V45InheritedPlanningBoundaryIdentity:
    return V45InheritedPlanningBoundaryIdentity(
        planning_boundary_id="v4_5_inherited_planning_boundary_identity",
        phase_id=V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID,
        planning_boundary_reference="v4_5_planning_only_boundary_preservation",
        inherited_constraint_reference="v4_5_inherited_constraint_visibility",
        inherited_prohibition_reference="v4_5_inherited_prohibition_visibility",
        deterministic_order=1,
    )


def default_phase8_evidence_references() -> tuple[Phase8ReadinessEvidenceReference, ...]:
    definitions = (
        (
            "phase8_readiness_evidence",
            "v4_4_boundary_readiness_transition",
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
            BLOCKER_STATE_BLOCKED,
            BLOCKER_STATE_WARNING,
        ),
        (
            "phase8_runtime_activation_evidence",
            "v4_5_runtime_activation",
            BLOCKER_STATE_CLOSEOUT_BLOCKED,
            BLOCKER_STATE_BLOCKED,
            BLOCKER_STATE_WARNING,
        ),
        (
            "phase8_planning_boundary_evidence",
            "v4_5_planning_constraints",
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
            BLOCKER_STATE_INHERITED_CONSTRAINT,
            BLOCKER_STATE_INFORMATIONAL,
        ),
    )
    return tuple(
        Phase8ReadinessEvidenceReference(
            evidence_id=evidence_id,
            source_phase_id=source_phase_id,
            source_report_reference="docs/generated/v4_4_boundary_readiness_transition_report.json",
            source_hash_reference="v4_4_boundary_readiness_transition.deterministic_report_hash",
            readiness_state=readiness_state,
            blocker_state=blocker_state,
            warning_state=warning_state,
            deterministic_order=index,
            fail_visible=readiness_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or blocker_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or warning_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (
            evidence_id,
            source_phase_id,
            readiness_state,
            blocker_state,
            warning_state,
        ) in enumerate(definitions, start=1)
    )


def default_blocker_records() -> tuple[BlockerClassificationRecord, ...]:
    definitions = (
        (
            "blocker_runtime_readiness_preserved",
            "runtime_readiness_visibility",
            BLOCKER_STATE_INTENTIONALLY_PRESERVED,
            BLOCKER_STATE_CLOSEOUT_BLOCKED,
            "blocker",
        ),
        (
            "blocker_v4_5_activation_inherited_prohibition",
            "v4_5_runtime_activation",
            BLOCKER_STATE_INHERITED_PROHIBITION,
            BLOCKER_STATE_PROHIBITED,
            "blocker",
        ),
        (
            "blocker_production_consumption_inherited_prohibition",
            "v4_5_production_consumption",
            BLOCKER_STATE_INHERITED_PROHIBITION,
            BLOCKER_STATE_PROHIBITED,
            "blocker",
        ),
        (
            "blocker_planner_integration_inherited_constraint",
            "v4_5_planner_integration",
            BLOCKER_STATE_INHERITED_CONSTRAINT,
            BLOCKER_STATE_BLOCKED,
            "blocker",
        ),
        (
            "blocker_closeout_review_packet_resolved",
            "v4_4_closeout_review_packet",
            BLOCKER_STATE_RESOLVED,
            BLOCKER_STATE_SUPPORTED,
            "informational",
        ),
        (
            "blocker_runtime_authority_escalated",
            "runtime_authority_visibility",
            BLOCKER_STATE_ESCALATED,
            BLOCKER_STATE_BLOCKED,
            "blocker",
        ),
    )
    return tuple(
        BlockerClassificationRecord(
            blocker_id=blocker_id,
            source_phase_id=source_phase_id,
            classification_state=classification_state,
            closeout_state=closeout_state,
            severity=severity,
            blocker_summary=(
                f"{classification_state} blocker classification remains descriptive and "
                "does not authorize remediation or runtime activation"
            ),
            evidence_reference_ids=(source_phase_id, blocker_id, classification_state),
            deterministic_order=index,
            fail_visible=classification_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or closeout_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (
            blocker_id,
            source_phase_id,
            classification_state,
            closeout_state,
            severity,
        ) in enumerate(definitions, start=1)
    )


def default_warning_records() -> tuple[WarningClassificationRecord, ...]:
    definitions = (
        (
            "warning_inheritance_refinement_preserved",
            "v4_4_boundary_inheritance_refinement",
            BLOCKER_STATE_INHERITED_CONSTRAINT,
            BLOCKER_STATE_WARNING,
            "warning",
        ),
        (
            "warning_conflict_drift_escalated",
            "v4_4_boundary_conflict_drift",
            BLOCKER_STATE_ESCALATED,
            BLOCKER_STATE_WARNING,
            "warning",
        ),
        (
            "warning_segmentation_scope_preserved",
            "v4_4_boundary_segmentation_scope",
            BLOCKER_STATE_INTENTIONALLY_PRESERVED,
            BLOCKER_STATE_AMBIGUOUS,
            "warning",
        ),
        (
            "warning_v4_5_constraints_inherited",
            "v4_5_planning_constraints",
            BLOCKER_STATE_INHERITED_CONSTRAINT,
            BLOCKER_STATE_WARNING,
            "warning",
        ),
        (
            "warning_closeout_context_informational",
            "v4_4_closeout_preparation_context",
            BLOCKER_STATE_INFORMATIONAL,
            BLOCKER_STATE_SUPPORTED,
            "informational",
        ),
    )
    return tuple(
        WarningClassificationRecord(
            warning_id=warning_id,
            source_phase_id=source_phase_id,
            classification_state=classification_state,
            warning_state=warning_state,
            severity=severity,
            warning_summary=(
                f"{classification_state} warning classification remains visible and "
                "is not suppressed or converted into remediation"
            ),
            evidence_reference_ids=(source_phase_id, warning_id, warning_state),
            deterministic_order=index,
            fail_visible=classification_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or warning_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (
            warning_id,
            source_phase_id,
            classification_state,
            warning_state,
            severity,
        ) in enumerate(definitions, start=1)
    )


def default_inherited_prohibition_records() -> tuple[InheritedProhibitionRecord, ...]:
    definitions = (
        ("prohibition_no_runtime_activation", "runtime_activation"),
        ("prohibition_no_planner_integration", "planner_integration"),
        ("prohibition_no_production_consumption", "production_consumption"),
        ("prohibition_no_recommendation_decision", "recommendation_decision"),
    )
    return tuple(
        InheritedProhibitionRecord(
            prohibition_id=prohibition_id,
            prohibition_state=BLOCKER_STATE_PROHIBITED,
            prohibited_behavior=prohibited_behavior,
            inherited_from_phase_ids=default_phase_ids(),
            planning_boundary_reference="v4_5_planning_only_boundary",
            deterministic_order=index,
        )
        for index, (prohibition_id, prohibited_behavior) in enumerate(definitions, start=1)
    )


def default_inherited_constraint_records() -> tuple[InheritedConstraintRecord, ...]:
    definitions = (
        ("constraint_planning_only", BLOCKER_STATE_SUPPORTED, "planning_only"),
        ("constraint_descriptive_only", BLOCKER_STATE_SUPPORTED, "descriptive_only"),
        ("constraint_no_runtime_activation", BLOCKER_STATE_INHERITED_PROHIBITION, "runtime_activation_prohibited"),
        ("constraint_no_planner_integration", BLOCKER_STATE_INHERITED_PROHIBITION, "planner_integration_prohibited"),
        ("constraint_no_production_consumption", BLOCKER_STATE_INHERITED_PROHIBITION, "production_consumption_prohibited"),
        ("constraint_no_recommendation_decision", BLOCKER_STATE_INHERITED_PROHIBITION, "recommendation_decision_prohibited"),
        ("constraint_inherit_limitations", BLOCKER_STATE_INHERITED_CONSTRAINT, "inherited_limitation_visibility"),
        ("constraint_drift_integrity_scope", BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS, "drift_integrity_preparation_scope"),
    )
    return tuple(
        InheritedConstraintRecord(
            constraint_id=constraint_id,
            constraint_state=constraint_state,
            constraint_type=constraint_type,
            constraint_summary=(
                f"{constraint_type} remains inherited for v4.5 planning without "
                "runtime activation or planner integration"
            ),
            inherited_from_phase_ids=default_phase_ids(),
            deterministic_order=index,
        )
        for index, (constraint_id, constraint_state, constraint_type) in enumerate(
            definitions,
            start=1,
        )
    )


def default_limitation_records() -> tuple[UnresolvedLimitationRecord, ...]:
    definitions = (
        ("limitation_unsupported_boundary", "v4_4_boundary_intelligence_foundations", BLOCKER_STATE_UNSUPPORTED),
        ("limitation_prohibited_runtime_authority", "v4_4_boundary_continuity_integrity", BLOCKER_STATE_PROHIBITED),
        ("limitation_stale_drift_evidence", "v4_4_boundary_conflict_drift", BLOCKER_STATE_STALE),
        ("limitation_conflicting_consistency", "v4_4_cross_boundary_consistency", BLOCKER_STATE_CONFLICTING),
        ("limitation_ambiguous_scope", "v4_4_boundary_segmentation_scope", BLOCKER_STATE_AMBIGUOUS),
        ("limitation_degraded_lineage", "v4_4_boundary_continuity_integrity", BLOCKER_STATE_DEGRADED),
        ("limitation_blocked_runtime_activation", "v4_5_runtime_activation", BLOCKER_STATE_BLOCKED),
    )
    return tuple(
        UnresolvedLimitationRecord(
            limitation_id=limitation_id,
            source_phase_id=source_phase_id,
            limitation_state=limitation_state,
            limitation_summary=(
                f"{limitation_state} limitation remains visible for closeout and "
                "v4.5 planning-boundary preservation"
            ),
            inherited_by_v4_5=True,
            evidence_reference_ids=(source_phase_id, limitation_id, limitation_state),
            deterministic_order=index,
        )
        for index, (limitation_id, source_phase_id, limitation_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_escalation_records() -> tuple[EscalationRecord, ...]:
    definitions = (
        ("escalation_runtime_readiness", "blocker_runtime_readiness_preserved", BLOCKER_STATE_ESCALATED),
        ("escalation_v4_5_activation", "blocker_v4_5_activation_inherited_prohibition", BLOCKER_STATE_INHERITED_PROHIBITION),
        ("escalation_production_consumption", "blocker_production_consumption_inherited_prohibition", BLOCKER_STATE_INHERITED_PROHIBITION),
        ("escalation_closeout_limitations", "limitation_blocked_runtime_activation", BLOCKER_STATE_INTENTIONALLY_PRESERVED),
    )
    return tuple(
        EscalationRecord(
            escalation_id=escalation_id,
            source_finding_id=source_finding_id,
            escalation_state=escalation_state,
            escalation_summary=(
                f"{source_finding_id} escalation remains visible and non-actioning"
            ),
            trace_reference_ids=(source_finding_id, escalation_id, escalation_state),
            deterministic_order=index,
        )
        for index, (escalation_id, source_finding_id, escalation_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_closeout_eligibility_records() -> tuple[CloseoutEligibilityRecord, ...]:
    definitions = (
        (
            "eligibility_v4_4_closeout_preparation",
            "v4_4_boundary_intelligence_closeout",
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
            BLOCKER_STATE_INTENTIONALLY_PRESERVED,
        ),
        (
            "eligibility_runtime_authority",
            "runtime_authority_visibility",
            BLOCKER_STATE_CLOSEOUT_BLOCKED,
            BLOCKER_STATE_PROHIBITED,
        ),
        (
            "eligibility_v4_5_planning_boundary",
            "v4_5_planning_boundary",
            BLOCKER_STATE_CLOSEOUT_READY,
            BLOCKER_STATE_SUPPORTED,
        ),
    )
    limitation_ids = tuple(record.limitation_id for record in default_limitation_records())
    return tuple(
        CloseoutEligibilityRecord(
            eligibility_id=eligibility_id,
            subject_id=subject_id,
            eligibility_state=eligibility_state,
            classification_state=classification_state,
            eligibility_summary=(
                f"{eligibility_state} closeout preparation visibility is descriptive "
                "and cannot activate runtime behavior"
            ),
            limitation_reference_ids=limitation_ids,
            deterministic_order=index,
            fail_visible=eligibility_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or classification_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (
            eligibility_id,
            subject_id,
            eligibility_state,
            classification_state,
        ) in enumerate(definitions, start=1)
    )


def default_planning_boundary_records() -> tuple[V45InheritedPlanningBoundaryRecord, ...]:
    constraint_ids = tuple(record.constraint_id for record in default_inherited_constraint_records())
    prohibition_ids = tuple(record.prohibition_id for record in default_inherited_prohibition_records())
    definitions = (
        (
            "planning_boundary_v4_5_planning_only",
            BLOCKER_STATE_INHERITED_CONSTRAINT,
            BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
        ),
        (
            "planning_boundary_v4_5_prohibitions",
            BLOCKER_STATE_INHERITED_PROHIBITION,
            BLOCKER_STATE_PROHIBITED,
        ),
        (
            "planning_boundary_v4_5_activation_blocked",
            BLOCKER_STATE_BLOCKED,
            BLOCKER_STATE_CLOSEOUT_BLOCKED,
        ),
    )
    return tuple(
        V45InheritedPlanningBoundaryRecord(
            planning_boundary_id=planning_boundary_id,
            boundary_state=boundary_state,
            planning_boundary_state=planning_boundary_state,
            boundary_summary=(
                f"{planning_boundary_id} preserves v4.5 planning boundary without "
                "activation, planner integration, or production consumption"
            ),
            inherited_constraint_ids=constraint_ids,
            inherited_prohibition_ids=prohibition_ids,
            deterministic_order=index,
            fail_visible=boundary_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES
            or planning_boundary_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (planning_boundary_id, boundary_state, planning_boundary_state) in enumerate(
            definitions,
            start=1,
        )
    )


def default_fail_visible_explanations() -> tuple[FailVisibleExplanationRecord, ...]:
    definitions = (
        ("explain_runtime_blocker", BLOCKER_STATE_BLOCKED, "blocker"),
        ("explain_warning_preservation", BLOCKER_STATE_WARNING, "warning"),
        ("explain_inherited_prohibition", BLOCKER_STATE_INHERITED_PROHIBITION, "prohibition"),
        ("explain_inherited_constraint", BLOCKER_STATE_INHERITED_CONSTRAINT, "constraint"),
        ("explain_unresolved_limitation", BLOCKER_STATE_DEGRADED, "limitation"),
    )
    return tuple(
        FailVisibleExplanationRecord(
            explanation_id=explanation_id,
            explanation_state=explanation_state,
            explanation_type=explanation_type,
            explanation_summary=(
                f"{explanation_type} explanation preserves fail-visible evidence "
                "without approval, recommendation, or remediation"
            ),
            evidence_reference_ids=(explanation_id, explanation_state, explanation_type),
            deterministic_order=index,
            fail_visible=explanation_state in FAIL_VISIBLE_BLOCKER_RESOLUTION_STATES,
        )
        for index, (explanation_id, explanation_state, explanation_type) in enumerate(
            definitions,
            start=1,
        )
    )


def default_non_operational_certifications() -> tuple[NonOperationalBlockerCertificationRecord, ...]:
    return (
        NonOperationalBlockerCertificationRecord(
            certification_id="non_operational_orchestration_execution",
            certification_state=BLOCKER_STATE_SUPPORTED,
            certification_summary="orchestration execution remains disabled",
            deterministic_order=1,
        ),
        NonOperationalBlockerCertificationRecord(
            certification_id="non_operational_authorization_approval_activation",
            certification_state=BLOCKER_STATE_SUPPORTED,
            certification_summary="authorization, approval, and activation remain disabled",
            deterministic_order=2,
        ),
        NonOperationalBlockerCertificationRecord(
            certification_id="non_operational_recommendation_decision",
            certification_state=BLOCKER_STATE_SUPPORTED,
            certification_summary="recommendation and decision behavior remain disabled",
            deterministic_order=3,
        ),
        NonOperationalBlockerCertificationRecord(
            certification_id="non_operational_production_consumption",
            certification_state=BLOCKER_STATE_SUPPORTED,
            certification_summary="production consumption remains disabled",
            deterministic_order=4,
        ),
    )


def default_provenance_record() -> BlockerResolutionProvenanceRecord:
    evidence = default_phase8_evidence_references()
    return BlockerResolutionProvenanceRecord(
        provenance_id="v4_4_boundary_blocker_resolution_provenance",
        source_reference_ids=tuple(record.source_report_reference for record in evidence),
        source_hash_references=tuple(record.source_hash_reference for record in evidence),
        provenance_state=BLOCKER_STATE_SUPPORTED,
        deterministic_order=1,
    )


def default_lineage_record() -> BlockerResolutionLineageRecord:
    return BlockerResolutionLineageRecord(
        lineage_id="v4_4_boundary_blocker_resolution_lineage",
        lineage_reference_ids=default_phase_ids() + (V4_4_BOUNDARY_BLOCKER_RESOLUTION_PHASE_ID,),
        lineage_hash_references=tuple(
            f"{phase_id}.deterministic_hash_reference" for phase_id in default_phase_ids()
        ),
        lineage_state=BLOCKER_STATE_SUPPORTED,
        deterministic_order=1,
    )


def _replay_evidence_ids() -> tuple[str, ...]:
    return (
        tuple(record.evidence_id for record in default_phase8_evidence_references())
        + tuple(record.blocker_id for record in default_blocker_records())
        + tuple(record.warning_id for record in default_warning_records())
        + tuple(record.prohibition_id for record in default_inherited_prohibition_records())
        + tuple(record.constraint_id for record in default_inherited_constraint_records())
        + tuple(record.limitation_id for record in default_limitation_records())
        + tuple(record.escalation_id for record in default_escalation_records())
        + tuple(record.eligibility_id for record in default_closeout_eligibility_records())
        + tuple(record.planning_boundary_id for record in default_planning_boundary_records())
        + tuple(record.explanation_id for record in default_fail_visible_explanations())
    )


def default_replay_rollback_record() -> BlockerResolutionReplayRollbackRecord:
    evidence_ids = _replay_evidence_ids()
    return BlockerResolutionReplayRollbackRecord(
        evidence_id="v4_4_boundary_blocker_resolution_replay_rollback",
        replay_state=BLOCKER_STATE_SUPPORTED,
        rollback_state=BLOCKER_STATE_SUPPORTED,
        evidence_reference_ids=evidence_ids,
        replay_evidence_ids=evidence_ids,
        rollback_evidence_ids=evidence_ids,
        deterministic_order=1,
    )


def default_closeout_summaries() -> tuple[CloseoutPreparationSummaryRecord, ...]:
    return (
        CloseoutPreparationSummaryRecord(
            summary_id="summary_v4_4_closeout_preparation",
            closeout_state=BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
            blocker_state=BLOCKER_STATE_INTENTIONALLY_PRESERVED,
            warning_state=BLOCKER_STATE_WARNING,
            escalation_state=BLOCKER_STATE_ESCALATED,
            certification_state=BLOCKER_STATE_SUPPORTED,
            summary_reference_ids=("v4_4_boundary_intelligence_phase_chain",),
            deterministic_order=1,
        ),
        CloseoutPreparationSummaryRecord(
            summary_id="summary_runtime_authority_remains_blocked",
            closeout_state=BLOCKER_STATE_CLOSEOUT_BLOCKED,
            blocker_state=BLOCKER_STATE_INHERITED_PROHIBITION,
            warning_state=BLOCKER_STATE_WARNING,
            escalation_state=BLOCKER_STATE_ESCALATED,
            certification_state=BLOCKER_STATE_PROHIBITED,
            summary_reference_ids=("runtime_authority_visibility", "v4_5_runtime_activation"),
            deterministic_order=2,
        ),
        CloseoutPreparationSummaryRecord(
            summary_id="summary_v4_5_planning_boundary",
            closeout_state=BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
            blocker_state=BLOCKER_STATE_INHERITED_CONSTRAINT,
            warning_state=BLOCKER_STATE_INFORMATIONAL,
            escalation_state=BLOCKER_STATE_INTENTIONALLY_PRESERVED,
            certification_state=BLOCKER_STATE_SUPPORTED,
            summary_reference_ids=("v4_5_planning_boundary",),
            deterministic_order=3,
        ),
    )


def default_boundary_blocker_resolution_closeout_preparation() -> (
    BoundaryBlockerResolutionCloseoutPreparation
):
    return BoundaryBlockerResolutionCloseoutPreparation(
        blocker_identity=default_blocker_identity(),
        warning_identity=default_warning_identity(),
        closeout_identity=default_closeout_identity(),
        planning_boundary_identity=default_planning_boundary_identity(),
        phase8_evidence_references=default_phase8_evidence_references(),
        blocker_records=default_blocker_records(),
        warning_records=default_warning_records(),
        inherited_prohibition_records=default_inherited_prohibition_records(),
        inherited_constraint_records=default_inherited_constraint_records(),
        limitation_records=default_limitation_records(),
        escalation_records=default_escalation_records(),
        closeout_eligibility_records=default_closeout_eligibility_records(),
        planning_boundary_records=default_planning_boundary_records(),
        fail_visible_explanations=default_fail_visible_explanations(),
        non_operational_certifications=default_non_operational_certifications(),
        provenance_record=default_provenance_record(),
        lineage_record=default_lineage_record(),
        replay_rollback_record=default_replay_rollback_record(),
        closeout_summaries=default_closeout_summaries(),
        deterministic_guarantees=V4_4_BOUNDARY_BLOCKER_RESOLUTION_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_4_BOUNDARY_BLOCKER_RESOLUTION_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_4_BOUNDARY_BLOCKER_RESOLUTION_EXPLICIT_PROHIBITIONS,
    )
