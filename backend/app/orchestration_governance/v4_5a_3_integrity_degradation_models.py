"""Deterministic v4.5A.3 governance-safe integrity degradation models.

The v4.5A.3 Track A layer models integrity degradation intelligence on top of
drift foundations and propagation intelligence. It is descriptive-only
governance evidence and does not remediate, repair, mitigate, suppress,
correct, execute, authorize, route, dispatch, traverse, schedule, sequence,
integrate planners, consume production data, or mutate runtime or operational
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_5A_3_INTEGRITY_DEGRADATION_PHASE_ID = "v4_5a_3_integrity_degradation_intelligence"
V4_5A_3_INTEGRITY_DEGRADATION_SCHEMA_VERSION = (
    "v4_5a_3.integrity_degradation_intelligence.1"
)
V4_5A_3_INTEGRITY_DEGRADATION_REPORT_SCHEMA_VERSION = (
    "v4_5a_3.integrity_degradation_intelligence_report.1"
)
V4_5A_3_INTEGRITY_DEGRADATION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5A_3_INTEGRITY_DEGRADATION_STATUS_STABLE = (
    "v4_5a_3_integrity_degradation_stable"
)
V4_5A_3_INTEGRITY_DEGRADATION_STATUS_BLOCKED = (
    "v4_5a_3_integrity_degradation_blocked"
)
V4_5A_3_INTEGRITY_DEGRADATION_PURPOSE = (
    "deterministic_governance_safe_integrity_degradation_intelligence_descriptive_only"
)
V4_5A_3_INTEGRITY_DEGRADATION_CLASSIFICATION = (
    "governance_safe_descriptive_integrity_degradation_intelligence"
)
V4_5A_2_DRIFT_PROPAGATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_2_drift_propagation_intelligence_report.json"
)
V4_5A_2_DRIFT_PROPAGATION_REPORT_HASH_REFERENCE = (
    "8752e48ec0e3c8c36ee4005aac59186076c4e7e33e08263c62408e4fe3cd9b7b"
)

DEGRADATION_CLASS_CONTINUITY = "continuity_degradation"
DEGRADATION_CLASS_LINEAGE = "lineage_degradation"
DEGRADATION_CLASS_PROVENANCE = "provenance_degradation"
DEGRADATION_CLASS_EXPLAINABILITY = "explainability_degradation"
DEGRADATION_CLASS_INTEGRITY_VISIBILITY = "integrity_visibility_degradation"
DEGRADATION_CLASS_INHERITANCE = "inheritance_degradation"
DEGRADATION_CLASS_REFINEMENT = "refinement_degradation"
DEGRADATION_CLASS_PROPAGATION_AMPLIFIED = "propagation_amplified_degradation"
DEGRADATION_CLASS_UNSUPPORTED_INTEGRITY_STATE = "unsupported_integrity_state"
DEGRADATION_CLASSIFICATION_TYPES: tuple[str, ...] = (
    DEGRADATION_CLASS_CONTINUITY,
    DEGRADATION_CLASS_LINEAGE,
    DEGRADATION_CLASS_PROVENANCE,
    DEGRADATION_CLASS_EXPLAINABILITY,
    DEGRADATION_CLASS_INTEGRITY_VISIBILITY,
    DEGRADATION_CLASS_INHERITANCE,
    DEGRADATION_CLASS_REFINEMENT,
    DEGRADATION_CLASS_PROPAGATION_AMPLIFIED,
    DEGRADATION_CLASS_UNSUPPORTED_INTEGRITY_STATE,
)

DEGRADATION_SEVERITY_ISOLATED = "isolated_degradation"
DEGRADATION_SEVERITY_LOCALIZED = "localized_degradation"
DEGRADATION_SEVERITY_DISTRIBUTED = "distributed_degradation"
DEGRADATION_SEVERITY_CONTINUITY_IMPACTING = "continuity_impacting_degradation"
DEGRADATION_SEVERITY_INTEGRITY_IMPACTING = "integrity_impacting_degradation"
DEGRADATION_SEVERITY_EXPLAINABILITY_IMPACTING = "explainability_impacting_degradation"
DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING = "governance_impacting_degradation"
DEGRADATION_SEVERITY_TYPES: tuple[str, ...] = (
    DEGRADATION_SEVERITY_ISOLATED,
    DEGRADATION_SEVERITY_LOCALIZED,
    DEGRADATION_SEVERITY_DISTRIBUTED,
    DEGRADATION_SEVERITY_CONTINUITY_IMPACTING,
    DEGRADATION_SEVERITY_INTEGRITY_IMPACTING,
    DEGRADATION_SEVERITY_EXPLAINABILITY_IMPACTING,
    DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING,
)

DEGRADATION_EVIDENCE_DEGRADATION = "degradation_evidence"
DEGRADATION_EVIDENCE_CONTINUITY = "continuity_evidence"
DEGRADATION_EVIDENCE_PROPAGATION = "propagation_evidence"
DEGRADATION_EVIDENCE_LINEAGE = "lineage_evidence"
DEGRADATION_EVIDENCE_PROVENANCE = "provenance_evidence"
DEGRADATION_EVIDENCE_EXPLAINABILITY = "explainability_evidence"
DEGRADATION_EVIDENCE_INTEGRITY = "integrity_evidence"
DEGRADATION_EVIDENCE_BLOCKER = "blocker_evidence"
DEGRADATION_EVIDENCE_WARNING = "warning_evidence"
DEGRADATION_EVIDENCE_TYPES: tuple[str, ...] = (
    DEGRADATION_EVIDENCE_DEGRADATION,
    DEGRADATION_EVIDENCE_CONTINUITY,
    DEGRADATION_EVIDENCE_PROPAGATION,
    DEGRADATION_EVIDENCE_LINEAGE,
    DEGRADATION_EVIDENCE_PROVENANCE,
    DEGRADATION_EVIDENCE_EXPLAINABILITY,
    DEGRADATION_EVIDENCE_INTEGRITY,
    DEGRADATION_EVIDENCE_BLOCKER,
    DEGRADATION_EVIDENCE_WARNING,
)

CONTINUITY_DEGRADATION_LINEAGE = "lineage_continuity_degradation"
CONTINUITY_DEGRADATION_PROVENANCE = "provenance_continuity_degradation"
CONTINUITY_DEGRADATION_GOVERNANCE = "governance_continuity_degradation"
CONTINUITY_DEGRADATION_EXPLAINABILITY = "explainability_continuity_degradation"
CONTINUITY_DEGRADATION_INTEGRITY = "integrity_continuity_degradation"
CONTINUITY_DEGRADATION_TYPES: tuple[str, ...] = (
    CONTINUITY_DEGRADATION_LINEAGE,
    CONTINUITY_DEGRADATION_PROVENANCE,
    CONTINUITY_DEGRADATION_GOVERNANCE,
    CONTINUITY_DEGRADATION_EXPLAINABILITY,
    CONTINUITY_DEGRADATION_INTEGRITY,
)

EXPLAINABILITY_DEGRADATION_LOSS = "explainability_loss_visibility"
EXPLAINABILITY_DEGRADATION_CONTINUITY = "continuity_explainability_degradation"
EXPLAINABILITY_DEGRADATION_EVIDENCE = "evidence_explainability_degradation"
EXPLAINABILITY_DEGRADATION_UNSUPPORTED = "unsupported_explainability_states"
EXPLAINABILITY_DEGRADATION_CHAIN = "degradation_chain_explainability"
EXPLAINABILITY_DEGRADATION_DIAGNOSTIC = "fail_visible_explainability_diagnostics"
EXPLAINABILITY_DEGRADATION_TYPES: tuple[str, ...] = (
    EXPLAINABILITY_DEGRADATION_LOSS,
    EXPLAINABILITY_DEGRADATION_CONTINUITY,
    EXPLAINABILITY_DEGRADATION_EVIDENCE,
    EXPLAINABILITY_DEGRADATION_UNSUPPORTED,
    EXPLAINABILITY_DEGRADATION_CHAIN,
    EXPLAINABILITY_DEGRADATION_DIAGNOSTIC,
)

CROSS_INTEGRITY_GOVERNANCE_SCOPE = "governance_scope_integrity_degradation"
CROSS_INTEGRITY_INHERITANCE_CHAIN = "inheritance_chain_integrity_degradation"
CROSS_INTEGRITY_REFINEMENT_CHAIN = "refinement_chain_integrity_degradation"
CROSS_INTEGRITY_SEGMENTATION_BOUNDARY = "segmentation_boundary_integrity_degradation"
CROSS_INTEGRITY_CONTINUITY_DOMAIN = "continuity_domain_integrity_degradation"
CROSS_INTEGRITY_EXPLAINABILITY_DOMAIN = "explainability_domain_integrity_degradation"
CROSS_BOUNDARY_INTEGRITY_TYPES: tuple[str, ...] = (
    CROSS_INTEGRITY_GOVERNANCE_SCOPE,
    CROSS_INTEGRITY_INHERITANCE_CHAIN,
    CROSS_INTEGRITY_REFINEMENT_CHAIN,
    CROSS_INTEGRITY_SEGMENTATION_BOUNDARY,
    CROSS_INTEGRITY_CONTINUITY_DOMAIN,
    CROSS_INTEGRITY_EXPLAINABILITY_DOMAIN,
)

DEGRADATION_DIAGNOSTIC_UNRESOLVED_CHAINS = "unresolved_degradation_chains"
DEGRADATION_DIAGNOSTIC_INCOMPLETE_CONTINUITY = "incomplete_integrity_continuity"
DEGRADATION_DIAGNOSTIC_DEGRADED_LINEAGE = "degraded_lineage_visibility"
DEGRADATION_DIAGNOSTIC_DEGRADED_PROVENANCE = "degraded_provenance_visibility"
DEGRADATION_DIAGNOSTIC_EXPLAINABILITY_GAPS = "explainability_degradation_gaps"
DEGRADATION_DIAGNOSTIC_UNSUPPORTED_STATES = "unsupported_degradation_states"
DEGRADATION_DIAGNOSTIC_EVIDENCE_DISCONTINUITIES = "integrity_evidence_discontinuities"
DEGRADATION_DIAGNOSTIC_CONTINUITY_AMPLIFICATION = "continuity_degradation_amplification"
DEGRADATION_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    DEGRADATION_DIAGNOSTIC_UNRESOLVED_CHAINS,
    DEGRADATION_DIAGNOSTIC_INCOMPLETE_CONTINUITY,
    DEGRADATION_DIAGNOSTIC_DEGRADED_LINEAGE,
    DEGRADATION_DIAGNOSTIC_DEGRADED_PROVENANCE,
    DEGRADATION_DIAGNOSTIC_EXPLAINABILITY_GAPS,
    DEGRADATION_DIAGNOSTIC_UNSUPPORTED_STATES,
    DEGRADATION_DIAGNOSTIC_EVIDENCE_DISCONTINUITIES,
    DEGRADATION_DIAGNOSTIC_CONTINUITY_AMPLIFICATION,
)

DEGRADATION_VISIBILITY_VISIBLE = "degradation_visible"
DEGRADATION_VISIBILITY_CONTINUITY_VISIBLE = "continuity_degradation_visible"
DEGRADATION_VISIBILITY_EXPLAINABILITY_VISIBLE = "explainability_degradation_visible"
DEGRADATION_VISIBILITY_EVIDENCE_VISIBLE = "evidence_visible"
DEGRADATION_VISIBILITY_UNSUPPORTED_VISIBLE = "unsupported_degradation_visible"
DEGRADATION_VISIBILITY_DIAGNOSTIC_VISIBLE = "diagnostic_visible"

UNSUPPORTED_DEGRADATION_ORCHESTRATION_EXECUTION = "orchestration_execution"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_AUTHORIZATION = "orchestration_authorization"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_APPROVAL = "orchestration_approval"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_DISPATCH = "orchestration_dispatch"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_ROUTING = "orchestration_routing"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_TRAVERSAL = "orchestration_traversal"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_SCHEDULING = "orchestration_scheduling"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_SEQUENCING = "orchestration_sequencing"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_DECISION = "orchestration_decision"
UNSUPPORTED_DEGRADATION_ORCHESTRATION_RECOMMENDATION = "orchestration_recommendation"
UNSUPPORTED_DEGRADATION_REMEDIATION = "remediation"
UNSUPPORTED_DEGRADATION_REPAIR = "repair"
UNSUPPORTED_DEGRADATION_MITIGATION = "mitigation"
UNSUPPORTED_DEGRADATION_SUPPRESSION = "degradation_suppression"
UNSUPPORTED_DEGRADATION_AUTOMATED_CORRECTION = "automated_correction"
UNSUPPORTED_DEGRADATION_RUNTIME_MUTATION = "runtime_mutation"
UNSUPPORTED_DEGRADATION_OPERATIONAL_MUTATION = "operational_mutation"
UNSUPPORTED_DEGRADATION_PLANNER_INTEGRATION = "planner_integration"
UNSUPPORTED_DEGRADATION_PRODUCTION_CONSUMPTION = "production_consumption"
UNSUPPORTED_DEGRADATION_OPERATIONAL_BEHAVIOR = "implicit_operational_behavior"
UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES: tuple[str, ...] = (
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_EXECUTION,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_AUTHORIZATION,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_APPROVAL,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_DISPATCH,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_ROUTING,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_TRAVERSAL,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_SCHEDULING,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_SEQUENCING,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_DECISION,
    UNSUPPORTED_DEGRADATION_ORCHESTRATION_RECOMMENDATION,
    UNSUPPORTED_DEGRADATION_REMEDIATION,
    UNSUPPORTED_DEGRADATION_REPAIR,
    UNSUPPORTED_DEGRADATION_MITIGATION,
    UNSUPPORTED_DEGRADATION_SUPPRESSION,
    UNSUPPORTED_DEGRADATION_AUTOMATED_CORRECTION,
    UNSUPPORTED_DEGRADATION_RUNTIME_MUTATION,
    UNSUPPORTED_DEGRADATION_OPERATIONAL_MUTATION,
    UNSUPPORTED_DEGRADATION_PLANNER_INTEGRATION,
    UNSUPPORTED_DEGRADATION_PRODUCTION_CONSUMPTION,
    UNSUPPORTED_DEGRADATION_OPERATIONAL_BEHAVIOR,
)

V4_5A_3_INTEGRITY_DEGRADATION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
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
    "enabled_degradation_suppression_count",
    "enabled_auto_correction_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
)

V4_5A_3_INTEGRITY_DEGRADATION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_degradation_identity_stability",
    "deterministic_degradation_classification_visibility",
    "deterministic_inherited_degradation_visibility",
    "deterministic_propagation_driven_degradation_visibility",
    "deterministic_continuity_degradation_visibility",
    "deterministic_explainability_degradation_visibility",
    "deterministic_degradation_evidence_chains",
    "deterministic_degradation_severity_accumulation",
    "deterministic_serialization_stability",
    "deterministic_hashing_stability",
    "replay_safe_degradation_evidence",
    "rollback_safe_degradation_evidence",
    "lineage_safe_degradation_visibility",
    "provenance_safe_degradation_visibility",
    "integrity_safe_degradation_visibility",
    "fail_visible_unsupported_degradation_preservation",
    "descriptive_only_governance_certification",
    "non_operational_certification",
)

V4_5A_3_INTEGRITY_DEGRADATION_INHERITED_PROHIBITIONS: tuple[str, ...] = (
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
    "No degradation suppression is introduced.",
    "No automated correction is introduced.",
    "No runtime mutation is introduced.",
    "No operational mutation is introduced.",
    "No planner integration is introduced.",
    "No production consumption is introduced.",
    "No implicit operational behavior is introduced.",
)

V4_5A_3_INTEGRITY_DEGRADATION_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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

V4_5A_3_INTEGRITY_DEGRADATION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.5A.3 models integrity degradation intelligence only.",
    "v4.5A.3 does not repair, remediate, mitigate, suppress, or correct degradation.",
    "v4.5A.3 does not activate orchestration responses to degradation.",
    "v4.5A.3 does not authorize, approve, dispatch, route, traverse, schedule, sequence, recommend, or decide orchestration.",
    "v4.5A.3 does not integrate planners or execute planner behavior.",
    "v4.5A.3 does not consume production bundles.",
    "v4.5A.3 does not mutate runtime state or operational state.",
    "v4.5A.3 preserves unsupported degradation states as explicit fail-visible evidence.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class IntegrityDegradationIdentity:
    integrity_degradation_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_propagation_report_reference: str
    source_propagation_hash_reference: str
    purpose: str = V4_5A_3_INTEGRITY_DEGRADATION_PURPOSE
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
    degradation_suppression_enabled: bool = False
    runtime_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DegradationRecord:
    degradation_id: str
    degradation_chain_id: str
    degradation_scope_id: str
    source_drift_id: str
    propagation_chain_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    integrity_reference_id: str
    deterministic_order: int
    deterministic: bool = True
    governance_safe: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    lineage_safe: bool = True
    provenance_safe: bool = True
    integrity_safe: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DegradationClassificationRecord:
    classification_id: str
    degradation_id: str
    classification_type: str
    severity_type: str
    visibility_state: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    non_remediating: bool = True
    non_operational: bool = True
    correction_enabled: bool = False
    remediation_enabled: bool = False
    authorization_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False


@dataclass(frozen=True)
class DegradationEvidenceChain:
    evidence_id: str
    degradation_id: str
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
class ContinuityDegradationVisibility:
    continuity_id: str
    degradation_id: str
    continuity_type: str
    degradation_chain_id: str
    continuity_reference_id: str
    lineage_reference_id: str
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
    restoration_enabled: bool = False
    repair_enabled: bool = False
    remediation_enabled: bool = False
    degradation_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class DegradationSeverityAccumulation:
    severity_id: str
    severity_type: str
    degradation_ids: tuple[str, ...]
    diagnostic_ids: tuple[str, ...]
    visibility_state: str
    severity_reason: str
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
        _set_tuple_field(self, "degradation_ids")
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class ExplainabilityDegradationVisibility:
    explainability_id: str
    degradation_id: str
    explainability_type: str
    visibility_state: str
    visible_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    explainability_first: bool = True
    descriptive_only: bool = True
    automated_response_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class CrossBoundaryIntegrityVisibility:
    cross_boundary_id: str
    degradation_id: str
    boundary_type: str
    source_boundary_reference_id: str
    target_boundary_reference_id: str
    visibility_state: str
    visibility_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    no_orchestration_traversal: bool = True
    no_operational_routing: bool = True
    traversal_enabled: bool = False
    routing_enabled: bool = False
    dispatch_enabled: bool = False


@dataclass(frozen=True)
class IntegrityDegradationDiagnostic:
    diagnostic_id: str
    degradation_id: str
    diagnostic_type: str
    severity_type: str
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
    degradation_correction_enabled: bool = False
    orchestration_response_enabled: bool = False
    authorization_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedDegradationVisibility:
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
    degradation_suppression_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class IntegrityDegradationIntelligence:
    degradation_identity: IntegrityDegradationIdentity
    degradation_records: tuple[DegradationRecord, ...]
    classifications: tuple[DegradationClassificationRecord, ...]
    evidence_chains: tuple[DegradationEvidenceChain, ...]
    continuity_degradation: tuple[ContinuityDegradationVisibility, ...]
    severity_accumulation: tuple[DegradationSeverityAccumulation, ...]
    explainability_degradation: tuple[ExplainabilityDegradationVisibility, ...]
    cross_boundary_integrity: tuple[CrossBoundaryIntegrityVisibility, ...]
    diagnostics: tuple[IntegrityDegradationDiagnostic, ...]
    unsupported_degradation_visibility: tuple[UnsupportedDegradationVisibility, ...]
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
    degradation_correction_enabled: bool = False
    degradation_suppression_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "degradation_records",
            "classifications",
            "evidence_chains",
            "continuity_degradation",
            "severity_accumulation",
            "explainability_degradation",
            "cross_boundary_integrity",
            "diagnostics",
            "unsupported_degradation_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_integrity_degradation_identity() -> IntegrityDegradationIdentity:
    return IntegrityDegradationIdentity(
        integrity_degradation_id="v4_5a_3_governance_safe_integrity_degradation",
        phase_id=V4_5A_3_INTEGRITY_DEGRADATION_PHASE_ID,
        schema_version=V4_5A_3_INTEGRITY_DEGRADATION_SCHEMA_VERSION,
        generated_at=V4_5A_3_INTEGRITY_DEGRADATION_GENERATED_AT,
        classification=V4_5A_3_INTEGRITY_DEGRADATION_CLASSIFICATION,
        source_propagation_report_reference=V4_5A_2_DRIFT_PROPAGATION_REPORT_REFERENCE,
        source_propagation_hash_reference=V4_5A_2_DRIFT_PROPAGATION_REPORT_HASH_REFERENCE,
    )


def default_degradation_records() -> tuple[DegradationRecord, ...]:
    definitions = (
        ("degradation_continuity", "degradation_chain_continuity", "degradation_scope_continuity", "drift_continuity_boundary_visibility", "propagation_chain_continuity", "continuity_propagation_continuity_visibility", "continuity_chain_continuity", "integrity_reference_continuity", 1),
        ("degradation_lineage", "degradation_chain_lineage", "degradation_scope_lineage", "drift_continuity_boundary_visibility", "propagation_chain_continuity", "continuity_propagation_continuity_visibility", "continuity_chain_continuity", "integrity_reference_lineage", 2),
        ("degradation_provenance", "degradation_chain_provenance", "degradation_scope_provenance", "drift_explainability_boundary_visibility", "propagation_chain_explainability", "continuity_propagation_explainability_visibility", "continuity_chain_explainability", "integrity_reference_provenance", 3),
        ("degradation_explainability", "degradation_chain_explainability", "degradation_scope_explainability", "drift_explainability_boundary_visibility", "propagation_chain_explainability", "continuity_propagation_explainability_visibility", "continuity_chain_explainability", "integrity_reference_explainability", 4),
        ("degradation_integrity_visibility", "degradation_chain_integrity_visibility", "degradation_scope_integrity_visibility", "drift_integrity_boundary_visibility", "propagation_chain_compatibility", "continuity_propagation_compatibility_visibility", "continuity_chain_integrity", "integrity_reference_visibility", 5),
        ("degradation_inheritance", "degradation_chain_inheritance", "degradation_scope_inheritance", "drift_inheritance_boundary_visibility", "propagation_chain_inherited", "continuity_propagation_inherited_scope", "continuity_chain_scope", "integrity_reference_inheritance", 6),
        ("degradation_refinement", "degradation_chain_refinement", "degradation_scope_refinement", "drift_refinement_boundary_visibility", "propagation_chain_refinement", "continuity_propagation_refinement_visibility", "continuity_chain_refinement", "integrity_reference_refinement", 7),
        ("degradation_propagation_amplified", "degradation_chain_propagation_amplified", "degradation_scope_propagation", "drift_compatibility_boundary_visibility", "propagation_chain_cross_boundary", "continuity_propagation_cross_boundary_visibility", "continuity_chain_compatibility", "integrity_reference_amplified", 8),
        ("degradation_unsupported_integrity_state", "degradation_chain_unsupported_integrity_state", "degradation_scope_unsupported", "drift_compatibility_boundary_visibility", "propagation_chain_cross_boundary", "continuity_propagation_cross_boundary_visibility", "continuity_chain_compatibility", "integrity_reference_unsupported", 9),
    )
    return tuple(DegradationRecord(*definition) for definition in definitions)


def default_degradation_classifications() -> tuple[DegradationClassificationRecord, ...]:
    severity_cycle = (
        DEGRADATION_SEVERITY_CONTINUITY_IMPACTING,
        DEGRADATION_SEVERITY_DISTRIBUTED,
        DEGRADATION_SEVERITY_LOCALIZED,
        DEGRADATION_SEVERITY_EXPLAINABILITY_IMPACTING,
        DEGRADATION_SEVERITY_INTEGRITY_IMPACTING,
        DEGRADATION_SEVERITY_ISOLATED,
        DEGRADATION_SEVERITY_LOCALIZED,
        DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING,
        DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING,
    )
    return tuple(
        DegradationClassificationRecord(
            classification_id=f"classification_{record.degradation_id}",
            degradation_id=record.degradation_id,
            classification_type=DEGRADATION_CLASSIFICATION_TYPES[index],
            severity_type=severity_cycle[index],
            visibility_state=DEGRADATION_VISIBILITY_VISIBLE,
            classification_reason=(
                f"{DEGRADATION_CLASSIFICATION_TYPES[index]} is visible as descriptive integrity degradation intelligence only."
            ),
            deterministic_order=record.deterministic_order,
        )
        for index, record in enumerate(default_degradation_records())
    )


def default_degradation_evidence_chains() -> tuple[DegradationEvidenceChain, ...]:
    definitions = (
        ("evidence_degradation", "degradation_continuity", DEGRADATION_EVIDENCE_DEGRADATION, "v4_5a_2.propagation_intelligence_hash", 1),
        ("evidence_continuity_degradation", "degradation_continuity", DEGRADATION_EVIDENCE_CONTINUITY, "v4_5a_2.continuity_records", 2),
        ("evidence_propagation_degradation", "degradation_propagation_amplified", DEGRADATION_EVIDENCE_PROPAGATION, "v4_5a_2.propagation_chain_hashes", 3),
        ("evidence_lineage_degradation", "degradation_lineage", DEGRADATION_EVIDENCE_LINEAGE, "v4_5a_2.lineage_continuity_preserved", 4),
        ("evidence_provenance_degradation", "degradation_provenance", DEGRADATION_EVIDENCE_PROVENANCE, "v4_5a_2.provenance_continuity_preserved", 5),
        ("evidence_explainability_degradation", "degradation_explainability", DEGRADATION_EVIDENCE_EXPLAINABILITY, "v4_5a_2.propagation_explainability_verified", 6),
        ("evidence_integrity_degradation", "degradation_integrity_visibility", DEGRADATION_EVIDENCE_INTEGRITY, "v4_5a_2.integrity_impacting_propagation", 7),
        ("evidence_blocker_degradation", "degradation_unsupported_integrity_state", DEGRADATION_EVIDENCE_BLOCKER, "v4_5a_2.unsupported_propagation_visibility", 8),
        ("evidence_warning_degradation", "degradation_refinement", DEGRADATION_EVIDENCE_WARNING, "v4_5a_2.fail_visible_propagation_diagnostics", 9),
    )
    return tuple(
        DegradationEvidenceChain(
            evidence_id=evidence_id,
            degradation_id=degradation_id,
            evidence_type=evidence_type,
            evidence_chain_id=f"degradation_evidence_chain::{evidence_id}",
            source_reference=f"{V4_5A_2_DRIFT_PROPAGATION_REPORT_REFERENCE}#{source_reference}",
            source_hash_reference=V4_5A_2_DRIFT_PROPAGATION_REPORT_HASH_REFERENCE,
            replay_reference=f"replay::{evidence_id}",
            provenance_reference=f"provenance::{source_reference}",
            deterministic_order=order,
        )
        for evidence_id, degradation_id, evidence_type, source_reference, order in definitions
    )


def default_continuity_degradation_visibility() -> tuple[ContinuityDegradationVisibility, ...]:
    definitions = (
        ("continuity_degradation_lineage", "degradation_lineage", CONTINUITY_DEGRADATION_LINEAGE, "degradation_chain_lineage", "continuity_propagation_continuity_visibility", "continuity_chain_continuity", 1),
        ("continuity_degradation_provenance", "degradation_provenance", CONTINUITY_DEGRADATION_PROVENANCE, "degradation_chain_provenance", "continuity_propagation_explainability_visibility", "continuity_chain_explainability", 2),
        ("continuity_degradation_governance", "degradation_propagation_amplified", CONTINUITY_DEGRADATION_GOVERNANCE, "degradation_chain_propagation_amplified", "continuity_propagation_cross_boundary_visibility", "continuity_chain_compatibility", 3),
        ("continuity_degradation_explainability", "degradation_explainability", CONTINUITY_DEGRADATION_EXPLAINABILITY, "degradation_chain_explainability", "continuity_propagation_explainability_visibility", "continuity_chain_explainability", 4),
        ("continuity_degradation_integrity", "degradation_integrity_visibility", CONTINUITY_DEGRADATION_INTEGRITY, "degradation_chain_integrity_visibility", "continuity_propagation_compatibility_visibility", "continuity_chain_integrity", 5),
    )
    return tuple(
        ContinuityDegradationVisibility(
            continuity_id=continuity_id,
            degradation_id=degradation_id,
            continuity_type=continuity_type,
            degradation_chain_id=chain_id,
            continuity_reference_id=continuity_reference_id,
            lineage_reference_id=lineage_reference_id,
            visibility_state=DEGRADATION_VISIBILITY_CONTINUITY_VISIBLE,
            continuity_reason=(
                "Continuity degradation is visible, deterministic, replay-safe, and non-restorative."
            ),
            deterministic_order=order,
        )
        for (
            continuity_id,
            degradation_id,
            continuity_type,
            chain_id,
            continuity_reference_id,
            lineage_reference_id,
            order,
        ) in definitions
    )


def default_degradation_diagnostics() -> tuple[IntegrityDegradationDiagnostic, ...]:
    definitions = (
        ("diagnostic_unresolved_degradation_chains", "degradation_continuity", DEGRADATION_DIAGNOSTIC_UNRESOLVED_CHAINS, DEGRADATION_SEVERITY_CONTINUITY_IMPACTING, ("evidence_degradation",), 1),
        ("diagnostic_incomplete_integrity_continuity", "degradation_integrity_visibility", DEGRADATION_DIAGNOSTIC_INCOMPLETE_CONTINUITY, DEGRADATION_SEVERITY_INTEGRITY_IMPACTING, ("evidence_integrity_degradation",), 2),
        ("diagnostic_degraded_lineage_visibility", "degradation_lineage", DEGRADATION_DIAGNOSTIC_DEGRADED_LINEAGE, DEGRADATION_SEVERITY_DISTRIBUTED, ("evidence_lineage_degradation",), 3),
        ("diagnostic_degraded_provenance_visibility", "degradation_provenance", DEGRADATION_DIAGNOSTIC_DEGRADED_PROVENANCE, DEGRADATION_SEVERITY_LOCALIZED, ("evidence_provenance_degradation",), 4),
        ("diagnostic_explainability_degradation_gaps", "degradation_explainability", DEGRADATION_DIAGNOSTIC_EXPLAINABILITY_GAPS, DEGRADATION_SEVERITY_EXPLAINABILITY_IMPACTING, ("evidence_explainability_degradation",), 5),
        ("diagnostic_unsupported_degradation_states", "degradation_unsupported_integrity_state", DEGRADATION_DIAGNOSTIC_UNSUPPORTED_STATES, DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING, ("evidence_blocker_degradation",), 6),
        ("diagnostic_integrity_evidence_discontinuities", "degradation_integrity_visibility", DEGRADATION_DIAGNOSTIC_EVIDENCE_DISCONTINUITIES, DEGRADATION_SEVERITY_INTEGRITY_IMPACTING, ("evidence_integrity_degradation",), 7),
        ("diagnostic_continuity_degradation_amplification", "degradation_propagation_amplified", DEGRADATION_DIAGNOSTIC_CONTINUITY_AMPLIFICATION, DEGRADATION_SEVERITY_GOVERNANCE_IMPACTING, ("evidence_propagation_degradation",), 8),
    )
    return tuple(
        IntegrityDegradationDiagnostic(
            diagnostic_id=diagnostic_id,
            degradation_id=degradation_id,
            diagnostic_type=diagnostic_type,
            severity_type=severity_type,
            visibility_state=DEGRADATION_VISIBILITY_DIAGNOSTIC_VISIBLE,
            message=f"{diagnostic_type} remains fail-visible and descriptive-only.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            diagnostic_id,
            degradation_id,
            diagnostic_type,
            severity_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_degradation_severity_accumulation() -> tuple[DegradationSeverityAccumulation, ...]:
    classifications = default_degradation_classifications()
    diagnostics = default_degradation_diagnostics()
    records: list[DegradationSeverityAccumulation] = []
    for order, severity_type in enumerate(DEGRADATION_SEVERITY_TYPES, start=1):
        degradation_ids = tuple(
            record.degradation_id for record in classifications if record.severity_type == severity_type
        )
        diagnostic_ids = tuple(
            record.diagnostic_id for record in diagnostics if record.severity_type == severity_type
        )
        records.append(
            DegradationSeverityAccumulation(
                severity_id=f"severity_accumulation_{severity_type}",
                severity_type=severity_type,
                degradation_ids=degradation_ids,
                diagnostic_ids=diagnostic_ids,
                visibility_state=DEGRADATION_VISIBILITY_VISIBLE,
                severity_reason=f"{severity_type} remains descriptive severity visibility only.",
                count=len(degradation_ids) + len(diagnostic_ids),
                deterministic_order=order,
            )
        )
    return tuple(records)


def default_explainability_degradation_visibility() -> tuple[ExplainabilityDegradationVisibility, ...]:
    definitions = (
        ("explainability_degradation_loss", "degradation_explainability", EXPLAINABILITY_DEGRADATION_LOSS, ("evidence_explainability_degradation",), 1),
        ("explainability_degradation_continuity", "degradation_continuity", EXPLAINABILITY_DEGRADATION_CONTINUITY, ("evidence_continuity_degradation",), 2),
        ("explainability_degradation_evidence", "degradation_integrity_visibility", EXPLAINABILITY_DEGRADATION_EVIDENCE, ("evidence_integrity_degradation",), 3),
        ("explainability_degradation_unsupported", "degradation_unsupported_integrity_state", EXPLAINABILITY_DEGRADATION_UNSUPPORTED, ("evidence_blocker_degradation",), 4),
        ("explainability_degradation_chain", "degradation_propagation_amplified", EXPLAINABILITY_DEGRADATION_CHAIN, ("evidence_propagation_degradation",), 5),
        ("explainability_degradation_diagnostic", "degradation_lineage", EXPLAINABILITY_DEGRADATION_DIAGNOSTIC, ("evidence_lineage_degradation",), 6),
    )
    return tuple(
        ExplainabilityDegradationVisibility(
            explainability_id=explainability_id,
            degradation_id=degradation_id,
            explainability_type=explainability_type,
            visibility_state=DEGRADATION_VISIBILITY_EXPLAINABILITY_VISIBLE,
            visible_reason=f"{explainability_type} remains visible without automated response.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            explainability_id,
            degradation_id,
            explainability_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_cross_boundary_integrity_visibility() -> tuple[CrossBoundaryIntegrityVisibility, ...]:
    definitions = (
        ("cross_integrity_governance_scope", "degradation_propagation_amplified", CROSS_INTEGRITY_GOVERNANCE_SCOPE, "governance_scope_source", "governance_scope_target", 1),
        ("cross_integrity_inheritance_chain", "degradation_inheritance", CROSS_INTEGRITY_INHERITANCE_CHAIN, "inheritance_chain_source", "inheritance_chain_target", 2),
        ("cross_integrity_refinement_chain", "degradation_refinement", CROSS_INTEGRITY_REFINEMENT_CHAIN, "refinement_chain_source", "refinement_chain_target", 3),
        ("cross_integrity_segmentation_boundary", "degradation_propagation_amplified", CROSS_INTEGRITY_SEGMENTATION_BOUNDARY, "segmentation_boundary_source", "segmentation_boundary_target", 4),
        ("cross_integrity_continuity_domain", "degradation_continuity", CROSS_INTEGRITY_CONTINUITY_DOMAIN, "continuity_domain_source", "continuity_domain_target", 5),
        ("cross_integrity_explainability_domain", "degradation_explainability", CROSS_INTEGRITY_EXPLAINABILITY_DOMAIN, "explainability_domain_source", "explainability_domain_target", 6),
    )
    return tuple(
        CrossBoundaryIntegrityVisibility(
            cross_boundary_id=cross_boundary_id,
            degradation_id=degradation_id,
            boundary_type=boundary_type,
            source_boundary_reference_id=source_boundary_reference_id,
            target_boundary_reference_id=target_boundary_reference_id,
            visibility_state=DEGRADATION_VISIBILITY_VISIBLE,
            visibility_reason=f"{boundary_type} is visible without orchestration traversal.",
            deterministic_order=order,
        )
        for (
            cross_boundary_id,
            degradation_id,
            boundary_type,
            source_boundary_reference_id,
            target_boundary_reference_id,
            order,
        ) in definitions
    )


def default_unsupported_degradation_visibility() -> tuple[UnsupportedDegradationVisibility, ...]:
    return tuple(
        UnsupportedDegradationVisibility(
            state_id=f"unsupported_degradation_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            visibility_state=DEGRADATION_VISIBILITY_UNSUPPORTED_VISIBLE,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5A.3 integrity degradation intelligence."
            ),
            evidence_reference_ids=("evidence_blocker_degradation",),
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(
            UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5a_3_integrity_degradation_intelligence() -> IntegrityDegradationIntelligence:
    return IntegrityDegradationIntelligence(
        degradation_identity=default_integrity_degradation_identity(),
        degradation_records=default_degradation_records(),
        classifications=default_degradation_classifications(),
        evidence_chains=default_degradation_evidence_chains(),
        continuity_degradation=default_continuity_degradation_visibility(),
        severity_accumulation=default_degradation_severity_accumulation(),
        explainability_degradation=default_explainability_degradation_visibility(),
        cross_boundary_integrity=default_cross_boundary_integrity_visibility(),
        diagnostics=default_degradation_diagnostics(),
        unsupported_degradation_visibility=default_unsupported_degradation_visibility(),
        deterministic_guarantees=V4_5A_3_INTEGRITY_DEGRADATION_DETERMINISTIC_GUARANTEES,
        inherited_prohibitions=V4_5A_3_INTEGRITY_DEGRADATION_INHERITED_PROHIBITIONS,
        inherited_constraints=V4_5A_3_INTEGRITY_DEGRADATION_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5A_3_INTEGRITY_DEGRADATION_EXPLICIT_LIMITATIONS,
    )
