"""Deterministic v4.5A.2 governance-safe drift propagation models.

The v4.5A.2 Track A layer models propagation intelligence on top of v4.5A.1
drift foundations. It is descriptive-only governance evidence and does not
remediate, repair, mitigate, suppress, correct, execute, authorize, route,
dispatch, traverse, schedule, sequence, integrate planners, consume production
data, or mutate runtime or operational state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_5A_2_DRIFT_PROPAGATION_PHASE_ID = "v4_5a_2_drift_propagation_intelligence"
V4_5A_2_DRIFT_PROPAGATION_SCHEMA_VERSION = "v4_5a_2.drift_propagation_intelligence.1"
V4_5A_2_DRIFT_PROPAGATION_REPORT_SCHEMA_VERSION = (
    "v4_5a_2.drift_propagation_intelligence_report.1"
)
V4_5A_2_DRIFT_PROPAGATION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5A_2_DRIFT_PROPAGATION_STATUS_STABLE = "v4_5a_2_drift_propagation_stable"
V4_5A_2_DRIFT_PROPAGATION_STATUS_BLOCKED = "v4_5a_2_drift_propagation_blocked"
V4_5A_2_DRIFT_PROPAGATION_PURPOSE = (
    "deterministic_governance_safe_drift_propagation_intelligence_descriptive_only"
)
V4_5A_2_DRIFT_PROPAGATION_CLASSIFICATION = (
    "governance_safe_descriptive_drift_propagation_intelligence"
)
V4_5A_1_DRIFT_FOUNDATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_1_drift_foundations_report.json"
)
V4_5A_1_DRIFT_FOUNDATION_REPORT_HASH_REFERENCE = (
    "5aa8494f9d2e323de50df02759d1fef24cabaa5a741e6ddfa289de27d747a087"
)

PROPAGATION_TYPE_DIRECT = "direct_propagation"
PROPAGATION_TYPE_INHERITED = "inherited_propagation"
PROPAGATION_TYPE_REFINEMENT = "refinement_propagation"
PROPAGATION_TYPE_CROSS_BOUNDARY = "cross_boundary_propagation"
PROPAGATION_TYPE_SEGMENTATION = "segmentation_propagation"
PROPAGATION_TYPE_COMPATIBILITY = "compatibility_propagation"
PROPAGATION_TYPE_CONTINUITY = "continuity_propagation"
PROPAGATION_TYPE_EXPLAINABILITY = "explainability_propagation"
PROPAGATION_CHAIN_TYPES: tuple[str, ...] = (
    PROPAGATION_TYPE_DIRECT,
    PROPAGATION_TYPE_INHERITED,
    PROPAGATION_TYPE_REFINEMENT,
    PROPAGATION_TYPE_CROSS_BOUNDARY,
    PROPAGATION_TYPE_SEGMENTATION,
    PROPAGATION_TYPE_COMPATIBILITY,
    PROPAGATION_TYPE_CONTINUITY,
    PROPAGATION_TYPE_EXPLAINABILITY,
)

PROPAGATION_ACCUMULATION_ISOLATED = "isolated_propagation"
PROPAGATION_ACCUMULATION_LOCALIZED = "localized_propagation"
PROPAGATION_ACCUMULATION_DISTRIBUTED = "distributed_propagation"
PROPAGATION_ACCUMULATION_CROSS_BOUNDARY = "cross_boundary_propagation"
PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING = "continuity_impacting_propagation"
PROPAGATION_ACCUMULATION_INTEGRITY_IMPACTING = "integrity_impacting_propagation"
PROPAGATION_ACCUMULATION_TYPES: tuple[str, ...] = (
    PROPAGATION_ACCUMULATION_ISOLATED,
    PROPAGATION_ACCUMULATION_LOCALIZED,
    PROPAGATION_ACCUMULATION_DISTRIBUTED,
    PROPAGATION_ACCUMULATION_CROSS_BOUNDARY,
    PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING,
    PROPAGATION_ACCUMULATION_INTEGRITY_IMPACTING,
)

PROPAGATION_EVIDENCE_PROPAGATION = "propagation_evidence"
PROPAGATION_EVIDENCE_INHERITANCE = "inheritance_evidence"
PROPAGATION_EVIDENCE_REFINEMENT = "refinement_evidence"
PROPAGATION_EVIDENCE_CONTINUITY = "continuity_evidence"
PROPAGATION_EVIDENCE_LINEAGE = "lineage_evidence"
PROPAGATION_EVIDENCE_EXPLAINABILITY = "explainability_evidence"
PROPAGATION_EVIDENCE_INTEGRITY = "integrity_evidence"
PROPAGATION_EVIDENCE_BLOCKER = "blocker_evidence"
PROPAGATION_EVIDENCE_WARNING = "warning_evidence"
PROPAGATION_EVIDENCE_TYPES: tuple[str, ...] = (
    PROPAGATION_EVIDENCE_PROPAGATION,
    PROPAGATION_EVIDENCE_INHERITANCE,
    PROPAGATION_EVIDENCE_REFINEMENT,
    PROPAGATION_EVIDENCE_CONTINUITY,
    PROPAGATION_EVIDENCE_LINEAGE,
    PROPAGATION_EVIDENCE_EXPLAINABILITY,
    PROPAGATION_EVIDENCE_INTEGRITY,
    PROPAGATION_EVIDENCE_BLOCKER,
    PROPAGATION_EVIDENCE_WARNING,
)

PROPAGATION_EXPLAINABILITY_ORIGIN = "propagation_origin_visibility"
PROPAGATION_EXPLAINABILITY_CHAIN = "propagation_chain_visibility"
PROPAGATION_EXPLAINABILITY_INHERITED = "inherited_propagation_visibility"
PROPAGATION_EXPLAINABILITY_REFINEMENT = "refinement_propagation_visibility"
PROPAGATION_EXPLAINABILITY_CONTINUITY_IMPACT = "continuity_impact_visibility"
PROPAGATION_EXPLAINABILITY_UNSUPPORTED = "unsupported_propagation_visibility"
PROPAGATION_EXPLAINABILITY_DIAGNOSTIC = "fail_visible_propagation_diagnostics"
PROPAGATION_EXPLAINABILITY_TYPES: tuple[str, ...] = (
    PROPAGATION_EXPLAINABILITY_ORIGIN,
    PROPAGATION_EXPLAINABILITY_CHAIN,
    PROPAGATION_EXPLAINABILITY_INHERITED,
    PROPAGATION_EXPLAINABILITY_REFINEMENT,
    PROPAGATION_EXPLAINABILITY_CONTINUITY_IMPACT,
    PROPAGATION_EXPLAINABILITY_UNSUPPORTED,
    PROPAGATION_EXPLAINABILITY_DIAGNOSTIC,
)

CROSS_BOUNDARY_SCOPE = "governance_scope_boundary"
CROSS_BOUNDARY_INHERITANCE = "inheritance_chain_boundary"
CROSS_BOUNDARY_REFINEMENT = "refinement_chain_boundary"
CROSS_BOUNDARY_SEGMENTATION = "segmentation_boundary"
CROSS_BOUNDARY_EXPLAINABILITY = "explainability_domain_boundary"
CROSS_BOUNDARY_PROPAGATION_TYPES: tuple[str, ...] = (
    CROSS_BOUNDARY_SCOPE,
    CROSS_BOUNDARY_INHERITANCE,
    CROSS_BOUNDARY_REFINEMENT,
    CROSS_BOUNDARY_SEGMENTATION,
    CROSS_BOUNDARY_EXPLAINABILITY,
)

PROPAGATION_DIAGNOSTIC_UNRESOLVED_CHAINS = "unresolved_propagation_chains"
PROPAGATION_DIAGNOSTIC_INCOMPLETE_LINEAGE = "incomplete_propagation_lineage"
PROPAGATION_DIAGNOSTIC_CONTINUITY_GAPS = "continuity_gaps"
PROPAGATION_DIAGNOSTIC_UNSUPPORTED_STATES = "unsupported_propagation_states"
PROPAGATION_DIAGNOSTIC_MISSING_EVIDENCE = "missing_propagation_evidence"
PROPAGATION_DIAGNOSTIC_INCOMPATIBLE_INHERITANCE = "incompatible_propagation_inheritance"
PROPAGATION_DIAGNOSTIC_EXPLAINABILITY_DISCONTINUITIES = (
    "explainability_discontinuities"
)
PROPAGATION_DIAGNOSTIC_INTEGRITY_GAPS = "propagation_integrity_gaps"
PROPAGATION_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    PROPAGATION_DIAGNOSTIC_UNRESOLVED_CHAINS,
    PROPAGATION_DIAGNOSTIC_INCOMPLETE_LINEAGE,
    PROPAGATION_DIAGNOSTIC_CONTINUITY_GAPS,
    PROPAGATION_DIAGNOSTIC_UNSUPPORTED_STATES,
    PROPAGATION_DIAGNOSTIC_MISSING_EVIDENCE,
    PROPAGATION_DIAGNOSTIC_INCOMPATIBLE_INHERITANCE,
    PROPAGATION_DIAGNOSTIC_EXPLAINABILITY_DISCONTINUITIES,
    PROPAGATION_DIAGNOSTIC_INTEGRITY_GAPS,
)

PROPAGATION_VISIBILITY_VISIBLE = "propagation_visible"
PROPAGATION_VISIBILITY_CONTINUITY_VISIBLE = "continuity_visible"
PROPAGATION_VISIBILITY_EXPLAINABILITY_VISIBLE = "explainability_visible"
PROPAGATION_VISIBILITY_EVIDENCE_VISIBLE = "evidence_visible"
PROPAGATION_VISIBILITY_UNSUPPORTED_VISIBLE = "unsupported_propagation_visible"
PROPAGATION_VISIBILITY_DIAGNOSTIC_VISIBLE = "diagnostic_visible"
PROPAGATION_VISIBILITY_STATES: tuple[str, ...] = (
    PROPAGATION_VISIBILITY_VISIBLE,
    PROPAGATION_VISIBILITY_CONTINUITY_VISIBLE,
    PROPAGATION_VISIBILITY_EXPLAINABILITY_VISIBLE,
    PROPAGATION_VISIBILITY_EVIDENCE_VISIBLE,
    PROPAGATION_VISIBILITY_UNSUPPORTED_VISIBLE,
    PROPAGATION_VISIBILITY_DIAGNOSTIC_VISIBLE,
)

UNSUPPORTED_PROPAGATION_ORCHESTRATION_EXECUTION = "orchestration_execution"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_AUTHORIZATION = "orchestration_authorization"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_APPROVAL = "orchestration_approval"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_DISPATCH = "orchestration_dispatch"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_ROUTING = "orchestration_routing"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_TRAVERSAL = "orchestration_traversal"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_SCHEDULING = "orchestration_scheduling"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_SEQUENCING = "orchestration_sequencing"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_DECISION = "orchestration_decision"
UNSUPPORTED_PROPAGATION_ORCHESTRATION_RECOMMENDATION = "orchestration_recommendation"
UNSUPPORTED_PROPAGATION_REMEDIATION = "remediation"
UNSUPPORTED_PROPAGATION_REPAIR = "repair"
UNSUPPORTED_PROPAGATION_MITIGATION = "mitigation"
UNSUPPORTED_PROPAGATION_AUTOMATED_CORRECTION = "automated_correction"
UNSUPPORTED_PROPAGATION_SUPPRESSION = "propagation_suppression"
UNSUPPORTED_PROPAGATION_RUNTIME_MUTATION = "runtime_mutation"
UNSUPPORTED_PROPAGATION_OPERATIONAL_MUTATION = "operational_mutation"
UNSUPPORTED_PROPAGATION_PLANNER_INTEGRATION = "planner_integration"
UNSUPPORTED_PROPAGATION_PRODUCTION_CONSUMPTION = "production_consumption"
UNSUPPORTED_PROPAGATION_OPERATIONAL_BEHAVIOR = "implicit_operational_behavior"
UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES: tuple[str, ...] = (
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_EXECUTION,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_AUTHORIZATION,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_APPROVAL,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_DISPATCH,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_ROUTING,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_TRAVERSAL,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_SCHEDULING,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_SEQUENCING,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_DECISION,
    UNSUPPORTED_PROPAGATION_ORCHESTRATION_RECOMMENDATION,
    UNSUPPORTED_PROPAGATION_REMEDIATION,
    UNSUPPORTED_PROPAGATION_REPAIR,
    UNSUPPORTED_PROPAGATION_MITIGATION,
    UNSUPPORTED_PROPAGATION_AUTOMATED_CORRECTION,
    UNSUPPORTED_PROPAGATION_SUPPRESSION,
    UNSUPPORTED_PROPAGATION_RUNTIME_MUTATION,
    UNSUPPORTED_PROPAGATION_OPERATIONAL_MUTATION,
    UNSUPPORTED_PROPAGATION_PLANNER_INTEGRATION,
    UNSUPPORTED_PROPAGATION_PRODUCTION_CONSUMPTION,
    UNSUPPORTED_PROPAGATION_OPERATIONAL_BEHAVIOR,
)

V4_5A_2_DRIFT_PROPAGATION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_orchestration_dispatch_count",
    "enabled_orchestration_routing_count",
    "enabled_orchestration_traversal_count",
    "enabled_orchestration_scheduling_count",
    "enabled_orchestration_sequencing_count",
    "enabled_orchestration_decision_count",
    "enabled_orchestration_recommendation_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_mitigation_count",
    "enabled_auto_correction_count",
    "enabled_propagation_suppression_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
)

V4_5A_2_DRIFT_PROPAGATION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_propagation_chain_stability",
    "deterministic_inherited_propagation_visibility",
    "deterministic_refinement_propagation_visibility",
    "deterministic_cross_boundary_propagation_visibility",
    "deterministic_propagation_continuity",
    "deterministic_severity_accumulation_visibility",
    "deterministic_propagation_evidence_chains",
    "deterministic_propagation_explainability_visibility",
    "deterministic_serialization_stability",
    "deterministic_hashing_stability",
    "replay_safe_propagation_evidence",
    "rollback_safe_propagation_evidence",
    "lineage_safe_propagation_visibility",
    "provenance_safe_propagation_visibility",
    "integrity_safe_propagation_visibility",
    "fail_visible_unsupported_propagation_preservation",
    "descriptive_only_governance_certification",
    "non_operational_certification",
)

V4_5A_2_DRIFT_PROPAGATION_INHERITED_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution is introduced.",
    "No orchestration authorization is introduced.",
    "No orchestration approval is introduced.",
    "No orchestration dispatch is introduced.",
    "No orchestration routing is introduced.",
    "No orchestration traversal is introduced.",
    "No orchestration scheduling is introduced.",
    "No orchestration sequencing is introduced.",
    "No orchestration decisions are introduced.",
    "No orchestration recommendations are introduced.",
    "No remediation system is introduced.",
    "No repair system is introduced.",
    "No mitigation system is introduced.",
    "No automated correction is introduced.",
    "No propagation suppression is introduced.",
    "No runtime mutation is introduced.",
    "No operational mutation is introduced.",
    "No planner integration is introduced.",
    "No production consumption is introduced.",
    "No implicit operational behavior is introduced.",
)

V4_5A_2_DRIFT_PROPAGATION_INHERITED_CONSTRAINTS: tuple[str, ...] = (
    "deterministic",
    "governance-safe",
    "replay-safe",
    "rollback-safe",
    "lineage-safe",
    "provenance-safe",
    "integrity-safe",
    "explainability-first",
    "fail-visible",
    "descriptive-only",
)

V4_5A_2_DRIFT_PROPAGATION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.5A.2 models drift propagation intelligence only.",
    "v4.5A.2 does not repair, remediate, mitigate, suppress, or correct propagation.",
    "v4.5A.2 does not activate orchestration responses to propagation.",
    "v4.5A.2 does not authorize, approve, dispatch, route, traverse, schedule, sequence, recommend, or decide orchestration.",
    "v4.5A.2 does not integrate planners or execute planner behavior.",
    "v4.5A.2 does not consume production bundles.",
    "v4.5A.2 does not mutate runtime state or operational state.",
    "v4.5A.2 preserves unsupported propagation states as explicit fail-visible evidence.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class DriftPropagationIdentity:
    propagation_foundation_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_foundation_report_reference: str
    source_foundation_hash_reference: str
    purpose: str = V4_5A_2_DRIFT_PROPAGATION_PURPOSE
    deterministic: bool = True
    governance_safe: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    lineage_safe: bool = True
    provenance_safe: bool = True
    integrity_safe: bool = True
    explainability_first: bool = True
    fail_visible: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    remediation_enabled: bool = False
    mitigation_enabled: bool = False
    propagation_suppression_enabled: bool = False
    runtime_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class PropagationChainRecord:
    propagation_id: str
    source_drift_id: str
    inherited_drift_id: str
    refinement_drift_id: str
    propagation_chain_id: str
    propagation_scope_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    propagation_type: str
    deterministic_order: int
    deterministic: bool = True
    governance_safe: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    lineage_safe: bool = True
    provenance_safe: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_sequencing_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class PropagationClassificationRecord:
    classification_id: str
    propagation_id: str
    propagation_type: str
    accumulation_type: str
    visibility_state: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    non_remediating: bool = True
    non_operational: bool = True
    remediation_enabled: bool = False
    authorization_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False


@dataclass(frozen=True)
class PropagationEvidenceChain:
    evidence_id: str
    propagation_id: str
    evidence_type: str
    evidence_chain_id: str
    source_reference: str
    source_hash_reference: str
    replay_reference: str
    provenance_reference: str
    deterministic_order: int
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    integrity_safe: bool = True
    descriptive_only: bool = True
    hidden_assumption_used: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class PropagationContinuityRecord:
    continuity_id: str
    propagation_id: str
    propagation_chain_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    continuity_type: str
    visibility_state: str
    continuity_reason: str
    deterministic_order: int
    continuity_preserved: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    lineage_safe: bool = True
    provenance_safe: bool = True
    integrity_safe: bool = True
    descriptive_only: bool = True
    repair_enabled: bool = False
    remediation_enabled: bool = False
    propagation_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class PropagationSeverityAccumulation:
    severity_id: str
    accumulation_type: str
    propagation_ids: tuple[str, ...]
    diagnostic_ids: tuple[str, ...]
    visibility_state: str
    accumulation_reason: str
    count: int
    deterministic_order: int
    descriptive_only: bool = True
    non_remediating: bool = True
    non_operational: bool = True
    non_authorizing: bool = True
    remediation_enabled: bool = False
    authorization_enabled: bool = False
    operational_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "propagation_ids")
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class PropagationExplainabilityVisibility:
    explainability_id: str
    propagation_id: str
    explainability_type: str
    visibility_state: str
    visible_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    operational_response_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class CrossBoundaryPropagationVisibility:
    cross_boundary_id: str
    propagation_id: str
    boundary_type: str
    source_boundary_reference_id: str
    target_boundary_reference_id: str
    visibility_state: str
    visibility_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    no_runtime_traversal: bool = True
    no_orchestration_semantics: bool = True
    traversal_enabled: bool = False
    routing_enabled: bool = False
    dispatch_enabled: bool = False


@dataclass(frozen=True)
class PropagationDiagnosticRecord:
    diagnostic_id: str
    propagation_id: str
    diagnostic_type: str
    accumulation_type: str
    visibility_state: str
    message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden_assumption_used: bool = False
    silent_suppression_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    propagation_correction_enabled: bool = False
    orchestration_response_enabled: bool = False
    authorization_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedPropagationVisibility:
    state_id: str
    unsupported_state: str
    visibility_state: str
    explicit_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    operational_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    propagation_suppression_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DriftPropagationIntelligence:
    propagation_identity: DriftPropagationIdentity
    propagation_chains: tuple[PropagationChainRecord, ...]
    classifications: tuple[PropagationClassificationRecord, ...]
    evidence_chains: tuple[PropagationEvidenceChain, ...]
    continuity_records: tuple[PropagationContinuityRecord, ...]
    severity_accumulation: tuple[PropagationSeverityAccumulation, ...]
    explainability_visibility: tuple[PropagationExplainabilityVisibility, ...]
    cross_boundary_visibility: tuple[CrossBoundaryPropagationVisibility, ...]
    diagnostics: tuple[PropagationDiagnosticRecord, ...]
    unsupported_propagation_visibility: tuple[UnsupportedPropagationVisibility, ...]
    deterministic_guarantees: tuple[str, ...]
    inherited_prohibitions: tuple[str, ...]
    inherited_constraints: tuple[str, ...]
    explicit_limitations: tuple[str, ...]
    descriptive_only: bool = True
    non_operational: bool = True
    non_executing: bool = True
    non_authorizing: bool = True
    non_remediating: bool = True
    non_runtime_mutating: bool = True
    non_operational_mutating: bool = True
    non_routing: bool = True
    non_dispatching: bool = True
    non_traversing: bool = True
    non_scheduling: bool = True
    non_sequencing: bool = True
    non_recommending: bool = True
    non_deciding: bool = True
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_sequencing_enabled: bool = False
    orchestration_decision_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    propagation_correction_enabled: bool = False
    propagation_suppression_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "propagation_chains",
            "classifications",
            "evidence_chains",
            "continuity_records",
            "severity_accumulation",
            "explainability_visibility",
            "cross_boundary_visibility",
            "diagnostics",
            "unsupported_propagation_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_propagation_identity() -> DriftPropagationIdentity:
    return DriftPropagationIdentity(
        propagation_foundation_id="v4_5a_2_governance_safe_drift_propagation",
        phase_id=V4_5A_2_DRIFT_PROPAGATION_PHASE_ID,
        schema_version=V4_5A_2_DRIFT_PROPAGATION_SCHEMA_VERSION,
        generated_at=V4_5A_2_DRIFT_PROPAGATION_GENERATED_AT,
        classification=V4_5A_2_DRIFT_PROPAGATION_CLASSIFICATION,
        source_foundation_report_reference=V4_5A_1_DRIFT_FOUNDATION_REPORT_REFERENCE,
        source_foundation_hash_reference=V4_5A_1_DRIFT_FOUNDATION_REPORT_HASH_REFERENCE,
    )


def default_propagation_chains() -> tuple[PropagationChainRecord, ...]:
    definitions = (
        ("propagation_direct_inheritance", "drift_inheritance_boundary_visibility", "drift_inheritance_boundary_visibility", "drift_refinement_boundary_visibility", "propagation_chain_direct", "propagation_scope_direct", "continuity_inheritance_drift", "continuity_chain_inheritance", PROPAGATION_TYPE_DIRECT, 1),
        ("propagation_inherited_scope", "drift_scope_boundary_visibility", "drift_inheritance_boundary_visibility", "drift_scope_boundary_visibility", "propagation_chain_inherited", "propagation_scope_inherited", "continuity_scope_drift", "continuity_chain_scope", PROPAGATION_TYPE_INHERITED, 2),
        ("propagation_refinement_visibility", "drift_refinement_boundary_visibility", "drift_inheritance_boundary_visibility", "drift_refinement_boundary_visibility", "propagation_chain_refinement", "propagation_scope_refinement", "continuity_refinement_drift", "continuity_chain_refinement", PROPAGATION_TYPE_REFINEMENT, 3),
        ("propagation_cross_boundary_visibility", "drift_compatibility_boundary_visibility", "drift_inheritance_boundary_visibility", "drift_compatibility_boundary_visibility", "propagation_chain_cross_boundary", "propagation_scope_cross_boundary", "continuity_compatibility_drift", "continuity_chain_compatibility", PROPAGATION_TYPE_CROSS_BOUNDARY, 4),
        ("propagation_segmentation_visibility", "drift_segmentation_boundary_visibility", "drift_segmentation_boundary_visibility", "drift_scope_boundary_visibility", "propagation_chain_segmentation", "propagation_scope_segmentation", "continuity_segmentation_drift", "continuity_chain_segmentation", PROPAGATION_TYPE_SEGMENTATION, 5),
        ("propagation_compatibility_visibility", "drift_compatibility_boundary_visibility", "drift_scope_boundary_visibility", "drift_integrity_boundary_visibility", "propagation_chain_compatibility", "propagation_scope_compatibility", "continuity_integrity_drift", "continuity_chain_integrity", PROPAGATION_TYPE_COMPATIBILITY, 6),
        ("propagation_continuity_visibility", "drift_continuity_boundary_visibility", "drift_continuity_boundary_visibility", "drift_integrity_boundary_visibility", "propagation_chain_continuity", "propagation_scope_continuity", "continuity_lineage_drift", "continuity_chain_continuity", PROPAGATION_TYPE_CONTINUITY, 7),
        ("propagation_explainability_visibility", "drift_explainability_boundary_visibility", "drift_explainability_boundary_visibility", "drift_integrity_boundary_visibility", "propagation_chain_explainability", "propagation_scope_explainability", "continuity_provenance_drift", "continuity_chain_explainability", PROPAGATION_TYPE_EXPLAINABILITY, 8),
    )
    return tuple(PropagationChainRecord(*definition) for definition in definitions)


def default_propagation_classifications() -> tuple[PropagationClassificationRecord, ...]:
    accumulation_cycle = (
        PROPAGATION_ACCUMULATION_ISOLATED,
        PROPAGATION_ACCUMULATION_LOCALIZED,
        PROPAGATION_ACCUMULATION_DISTRIBUTED,
        PROPAGATION_ACCUMULATION_CROSS_BOUNDARY,
        PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING,
        PROPAGATION_ACCUMULATION_INTEGRITY_IMPACTING,
        PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING,
        PROPAGATION_ACCUMULATION_DISTRIBUTED,
    )
    return tuple(
        PropagationClassificationRecord(
            classification_id=f"classification_{chain.propagation_id}",
            propagation_id=chain.propagation_id,
            propagation_type=chain.propagation_type,
            accumulation_type=accumulation_cycle[index],
            visibility_state=PROPAGATION_VISIBILITY_VISIBLE,
            classification_reason=(
                f"{chain.propagation_type} is visible as descriptive propagation intelligence only."
            ),
            deterministic_order=chain.deterministic_order,
        )
        for index, chain in enumerate(default_propagation_chains())
    )


def default_propagation_evidence_chains() -> tuple[PropagationEvidenceChain, ...]:
    definitions = (
        ("evidence_propagation_direct", "propagation_direct_inheritance", PROPAGATION_EVIDENCE_PROPAGATION, "v4_5a_1.drift_identity_hashes", 1),
        ("evidence_inheritance_propagation", "propagation_inherited_scope", PROPAGATION_EVIDENCE_INHERITANCE, "v4_5a_1.inheritance_drift_visibility", 2),
        ("evidence_refinement_propagation", "propagation_refinement_visibility", PROPAGATION_EVIDENCE_REFINEMENT, "v4_5a_1.refinement_drift_visibility", 3),
        ("evidence_continuity_propagation", "propagation_continuity_visibility", PROPAGATION_EVIDENCE_CONTINUITY, "v4_5a_1.continuity_visibility", 4),
        ("evidence_lineage_propagation", "propagation_continuity_visibility", PROPAGATION_EVIDENCE_LINEAGE, "v4_5a_1.lineage_continuity_preserved", 5),
        ("evidence_explainability_propagation", "propagation_explainability_visibility", PROPAGATION_EVIDENCE_EXPLAINABILITY, "v4_5a_1.explainability_drift_visibility", 6),
        ("evidence_integrity_propagation", "propagation_compatibility_visibility", PROPAGATION_EVIDENCE_INTEGRITY, "v4_5a_1.integrity_visibility_drift", 7),
        ("evidence_blocker_propagation", "propagation_cross_boundary_visibility", PROPAGATION_EVIDENCE_BLOCKER, "v4_5a_1.unsupported_state_visibility", 8),
        ("evidence_warning_propagation", "propagation_segmentation_visibility", PROPAGATION_EVIDENCE_WARNING, "v4_5a_1.fail_visible_diagnostics", 9),
    )
    return tuple(
        PropagationEvidenceChain(
            evidence_id=evidence_id,
            propagation_id=propagation_id,
            evidence_type=evidence_type,
            evidence_chain_id=f"evidence_chain::{evidence_id}",
            source_reference=f"{V4_5A_1_DRIFT_FOUNDATION_REPORT_REFERENCE}#{source_reference}",
            source_hash_reference=V4_5A_1_DRIFT_FOUNDATION_REPORT_HASH_REFERENCE,
            replay_reference=f"replay::{evidence_id}",
            provenance_reference=f"provenance::{source_reference}",
            deterministic_order=order,
        )
        for evidence_id, propagation_id, evidence_type, source_reference, order in definitions
    )


def default_propagation_continuity_records() -> tuple[PropagationContinuityRecord, ...]:
    return tuple(
        PropagationContinuityRecord(
            continuity_id=f"continuity_{chain.propagation_id}",
            propagation_id=chain.propagation_id,
            propagation_chain_id=chain.propagation_chain_id,
            continuity_reference_id=chain.continuity_reference_id,
            lineage_reference_id=chain.lineage_reference_id,
            continuity_type=chain.propagation_type,
            visibility_state=PROPAGATION_VISIBILITY_CONTINUITY_VISIBLE,
            continuity_reason=(
                "Propagation continuity is visible, deterministic, replay-safe, and non-corrective."
            ),
            deterministic_order=chain.deterministic_order,
        )
        for chain in default_propagation_chains()
    )


def default_propagation_diagnostics() -> tuple[PropagationDiagnosticRecord, ...]:
    definitions = (
        ("diagnostic_unresolved_propagation_chains", "propagation_continuity_visibility", PROPAGATION_DIAGNOSTIC_UNRESOLVED_CHAINS, PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING, ("evidence_continuity_propagation",), 1),
        ("diagnostic_incomplete_propagation_lineage", "propagation_continuity_visibility", PROPAGATION_DIAGNOSTIC_INCOMPLETE_LINEAGE, PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING, ("evidence_lineage_propagation",), 2),
        ("diagnostic_propagation_continuity_gaps", "propagation_continuity_visibility", PROPAGATION_DIAGNOSTIC_CONTINUITY_GAPS, PROPAGATION_ACCUMULATION_CONTINUITY_IMPACTING, ("evidence_continuity_propagation",), 3),
        ("diagnostic_unsupported_propagation_states", "propagation_cross_boundary_visibility", PROPAGATION_DIAGNOSTIC_UNSUPPORTED_STATES, PROPAGATION_ACCUMULATION_CROSS_BOUNDARY, ("evidence_blocker_propagation",), 4),
        ("diagnostic_missing_propagation_evidence", "propagation_direct_inheritance", PROPAGATION_DIAGNOSTIC_MISSING_EVIDENCE, PROPAGATION_ACCUMULATION_LOCALIZED, ("evidence_propagation_direct",), 5),
        ("diagnostic_incompatible_propagation_inheritance", "propagation_inherited_scope", PROPAGATION_DIAGNOSTIC_INCOMPATIBLE_INHERITANCE, PROPAGATION_ACCUMULATION_DISTRIBUTED, ("evidence_inheritance_propagation",), 6),
        ("diagnostic_explainability_discontinuities", "propagation_explainability_visibility", PROPAGATION_DIAGNOSTIC_EXPLAINABILITY_DISCONTINUITIES, PROPAGATION_ACCUMULATION_DISTRIBUTED, ("evidence_explainability_propagation",), 7),
        ("diagnostic_propagation_integrity_gaps", "propagation_compatibility_visibility", PROPAGATION_DIAGNOSTIC_INTEGRITY_GAPS, PROPAGATION_ACCUMULATION_INTEGRITY_IMPACTING, ("evidence_integrity_propagation",), 8),
    )
    return tuple(
        PropagationDiagnosticRecord(
            diagnostic_id=diagnostic_id,
            propagation_id=propagation_id,
            diagnostic_type=diagnostic_type,
            accumulation_type=accumulation_type,
            visibility_state=PROPAGATION_VISIBILITY_DIAGNOSTIC_VISIBLE,
            message=f"{diagnostic_type} remains fail-visible and descriptive-only.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            diagnostic_id,
            propagation_id,
            diagnostic_type,
            accumulation_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_propagation_severity_accumulation() -> tuple[PropagationSeverityAccumulation, ...]:
    classifications = default_propagation_classifications()
    diagnostics = default_propagation_diagnostics()
    records: list[PropagationSeverityAccumulation] = []
    for order, accumulation_type in enumerate(PROPAGATION_ACCUMULATION_TYPES, start=1):
        propagation_ids = tuple(
            record.propagation_id
            for record in classifications
            if record.accumulation_type == accumulation_type
        )
        diagnostic_ids = tuple(
            record.diagnostic_id
            for record in diagnostics
            if record.accumulation_type == accumulation_type
        )
        records.append(
            PropagationSeverityAccumulation(
                severity_id=f"severity_accumulation_{accumulation_type}",
                accumulation_type=accumulation_type,
                propagation_ids=propagation_ids,
                diagnostic_ids=diagnostic_ids,
                visibility_state=PROPAGATION_VISIBILITY_VISIBLE,
                accumulation_reason=(
                    f"{accumulation_type} is a descriptive severity accumulation visibility state."
                ),
                count=len(propagation_ids) + len(diagnostic_ids),
                deterministic_order=order,
            )
        )
    return tuple(records)


def default_propagation_explainability_visibility() -> tuple[PropagationExplainabilityVisibility, ...]:
    definitions = (
        ("explainability_origin", "propagation_direct_inheritance", PROPAGATION_EXPLAINABILITY_ORIGIN, ("evidence_propagation_direct",), 1),
        ("explainability_chain", "propagation_continuity_visibility", PROPAGATION_EXPLAINABILITY_CHAIN, ("evidence_continuity_propagation",), 2),
        ("explainability_inherited", "propagation_inherited_scope", PROPAGATION_EXPLAINABILITY_INHERITED, ("evidence_inheritance_propagation",), 3),
        ("explainability_refinement", "propagation_refinement_visibility", PROPAGATION_EXPLAINABILITY_REFINEMENT, ("evidence_refinement_propagation",), 4),
        ("explainability_continuity_impact", "propagation_continuity_visibility", PROPAGATION_EXPLAINABILITY_CONTINUITY_IMPACT, ("evidence_lineage_propagation",), 5),
        ("explainability_unsupported", "propagation_cross_boundary_visibility", PROPAGATION_EXPLAINABILITY_UNSUPPORTED, ("evidence_blocker_propagation",), 6),
        ("explainability_fail_visible_diagnostics", "propagation_explainability_visibility", PROPAGATION_EXPLAINABILITY_DIAGNOSTIC, ("evidence_explainability_propagation",), 7),
    )
    return tuple(
        PropagationExplainabilityVisibility(
            explainability_id=explainability_id,
            propagation_id=propagation_id,
            explainability_type=explainability_type,
            visibility_state=PROPAGATION_VISIBILITY_EXPLAINABILITY_VISIBLE,
            visible_reason=f"{explainability_type} remains visible without operational response.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            explainability_id,
            propagation_id,
            explainability_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_cross_boundary_visibility() -> tuple[CrossBoundaryPropagationVisibility, ...]:
    definitions = (
        ("cross_boundary_governance_scope", "propagation_cross_boundary_visibility", CROSS_BOUNDARY_SCOPE, "governance_scope_source", "governance_scope_target", 1),
        ("cross_boundary_inheritance_chain", "propagation_inherited_scope", CROSS_BOUNDARY_INHERITANCE, "inheritance_chain_source", "inheritance_chain_target", 2),
        ("cross_boundary_refinement_chain", "propagation_refinement_visibility", CROSS_BOUNDARY_REFINEMENT, "refinement_chain_source", "refinement_chain_target", 3),
        ("cross_boundary_segmentation", "propagation_segmentation_visibility", CROSS_BOUNDARY_SEGMENTATION, "segmentation_boundary_source", "segmentation_boundary_target", 4),
        ("cross_boundary_explainability_domain", "propagation_explainability_visibility", CROSS_BOUNDARY_EXPLAINABILITY, "explainability_domain_source", "explainability_domain_target", 5),
    )
    return tuple(
        CrossBoundaryPropagationVisibility(
            cross_boundary_id=cross_boundary_id,
            propagation_id=propagation_id,
            boundary_type=boundary_type,
            source_boundary_reference_id=source_boundary_reference_id,
            target_boundary_reference_id=target_boundary_reference_id,
            visibility_state=PROPAGATION_VISIBILITY_VISIBLE,
            visibility_reason=(
                f"{boundary_type} propagation is visible without runtime traversal."
            ),
            deterministic_order=order,
        )
        for (
            cross_boundary_id,
            propagation_id,
            boundary_type,
            source_boundary_reference_id,
            target_boundary_reference_id,
            order,
        ) in definitions
    )


def default_unsupported_propagation_visibility() -> tuple[UnsupportedPropagationVisibility, ...]:
    return tuple(
        UnsupportedPropagationVisibility(
            state_id=f"unsupported_propagation_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            visibility_state=PROPAGATION_VISIBILITY_UNSUPPORTED_VISIBLE,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5A.2 propagation intelligence."
            ),
            evidence_reference_ids=("evidence_blocker_propagation",),
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(
            UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5a_2_drift_propagation_intelligence() -> DriftPropagationIntelligence:
    return DriftPropagationIntelligence(
        propagation_identity=default_propagation_identity(),
        propagation_chains=default_propagation_chains(),
        classifications=default_propagation_classifications(),
        evidence_chains=default_propagation_evidence_chains(),
        continuity_records=default_propagation_continuity_records(),
        severity_accumulation=default_propagation_severity_accumulation(),
        explainability_visibility=default_propagation_explainability_visibility(),
        cross_boundary_visibility=default_cross_boundary_visibility(),
        diagnostics=default_propagation_diagnostics(),
        unsupported_propagation_visibility=default_unsupported_propagation_visibility(),
        deterministic_guarantees=V4_5A_2_DRIFT_PROPAGATION_DETERMINISTIC_GUARANTEES,
        inherited_prohibitions=V4_5A_2_DRIFT_PROPAGATION_INHERITED_PROHIBITIONS,
        inherited_constraints=V4_5A_2_DRIFT_PROPAGATION_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5A_2_DRIFT_PROPAGATION_EXPLICIT_LIMITATIONS,
    )
