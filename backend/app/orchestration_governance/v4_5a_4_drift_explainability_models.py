"""Deterministic v4.5A.4 governance-safe drift explainability models.

The v4.5A.4 Track A layer explains drift, propagation, and integrity
degradation visibility without enabling remediation, repair, mitigation,
automated correction, explanation-driven action, authorization, ranking,
recommendation, orchestration response, planner execution, production
consumption, runtime mutation, or operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_5A_4_DRIFT_EXPLAINABILITY_PHASE_ID = "v4_5a_4_drift_explainability_intelligence"
V4_5A_4_DRIFT_EXPLAINABILITY_SCHEMA_VERSION = (
    "v4_5a_4.drift_explainability_intelligence.1"
)
V4_5A_4_DRIFT_EXPLAINABILITY_REPORT_SCHEMA_VERSION = (
    "v4_5a_4.drift_explainability_intelligence_report.1"
)
V4_5A_4_DRIFT_EXPLAINABILITY_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_STABLE = (
    "v4_5a_4_drift_explainability_stable"
)
V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_BLOCKED = (
    "v4_5a_4_drift_explainability_blocked"
)
V4_5A_4_DRIFT_EXPLAINABILITY_PURPOSE = (
    "deterministic_governance_safe_drift_explainability_intelligence_descriptive_only"
)
V4_5A_4_DRIFT_EXPLAINABILITY_CLASSIFICATION = (
    "governance_safe_descriptive_drift_explainability_intelligence"
)
V4_5A_3_INTEGRITY_DEGRADATION_REPORT_REFERENCE = (
    "docs/generated/v4_5a_3_integrity_degradation_intelligence_report.json"
)
V4_5A_3_INTEGRITY_DEGRADATION_REPORT_HASH_REFERENCE = (
    "70c374bc09a9e72e8ec0aaffd6f4ca34971b9888c03d8f03746c5c4a450cadfb"
)

DRIFT_CAUSE_INHERITED = "inherited_drift_cause"
DRIFT_CAUSE_REFINEMENT = "refinement_drift_cause"
DRIFT_CAUSE_SEGMENTATION = "segmentation_drift_cause"
DRIFT_CAUSE_SCOPE = "scope_drift_cause"
DRIFT_CAUSE_COMPATIBILITY = "compatibility_drift_cause"
DRIFT_CAUSE_CONTINUITY = "continuity_drift_cause"
DRIFT_CAUSE_EVIDENCE_GAP = "evidence_gap_drift_cause"
DRIFT_CAUSE_UNSUPPORTED = "unsupported_drift_cause"
DRIFT_CAUSE_TYPES: tuple[str, ...] = (
    DRIFT_CAUSE_INHERITED,
    DRIFT_CAUSE_REFINEMENT,
    DRIFT_CAUSE_SEGMENTATION,
    DRIFT_CAUSE_SCOPE,
    DRIFT_CAUSE_COMPATIBILITY,
    DRIFT_CAUSE_CONTINUITY,
    DRIFT_CAUSE_EVIDENCE_GAP,
    DRIFT_CAUSE_UNSUPPORTED,
)

PROPAGATION_EXPLANATION_DIRECT = "direct_propagation_explanation"
PROPAGATION_EXPLANATION_INHERITED = "inherited_propagation_explanation"
PROPAGATION_EXPLANATION_REFINEMENT = "refinement_propagation_explanation"
PROPAGATION_EXPLANATION_CROSS_BOUNDARY = "cross_boundary_propagation_explanation"
PROPAGATION_EXPLANATION_CONTINUITY_IMPACTING = (
    "continuity_impacting_propagation_explanation"
)
PROPAGATION_EXPLANATION_INTEGRITY_IMPACTING = (
    "integrity_impacting_propagation_explanation"
)
PROPAGATION_EXPLANATION_UNSUPPORTED = "unsupported_propagation_explanation"
PROPAGATION_EXPLANATION_TYPES: tuple[str, ...] = (
    PROPAGATION_EXPLANATION_DIRECT,
    PROPAGATION_EXPLANATION_INHERITED,
    PROPAGATION_EXPLANATION_REFINEMENT,
    PROPAGATION_EXPLANATION_CROSS_BOUNDARY,
    PROPAGATION_EXPLANATION_CONTINUITY_IMPACTING,
    PROPAGATION_EXPLANATION_INTEGRITY_IMPACTING,
    PROPAGATION_EXPLANATION_UNSUPPORTED,
)

DEGRADATION_EXPLANATION_ORIGIN = "degradation_origin_explanation"
DEGRADATION_EXPLANATION_AMPLIFICATION = "degradation_amplification_explanation"
DEGRADATION_EXPLANATION_CONTINUITY = "continuity_degradation_explanation"
DEGRADATION_EXPLANATION_LINEAGE = "lineage_degradation_explanation"
DEGRADATION_EXPLANATION_PROVENANCE = "provenance_degradation_explanation"
DEGRADATION_EXPLANATION_EXPLAINABILITY = "explainability_degradation_explanation"
DEGRADATION_EXPLANATION_UNSUPPORTED = "unsupported_degradation_explanation"
DEGRADATION_EXPLANATION_TYPES: tuple[str, ...] = (
    DEGRADATION_EXPLANATION_ORIGIN,
    DEGRADATION_EXPLANATION_AMPLIFICATION,
    DEGRADATION_EXPLANATION_CONTINUITY,
    DEGRADATION_EXPLANATION_LINEAGE,
    DEGRADATION_EXPLANATION_PROVENANCE,
    DEGRADATION_EXPLANATION_EXPLAINABILITY,
    DEGRADATION_EXPLANATION_UNSUPPORTED,
)

EVIDENCE_MAPPING_DRIFT = "drift_evidence_reference"
EVIDENCE_MAPPING_PROPAGATION = "propagation_evidence_reference"
EVIDENCE_MAPPING_DEGRADATION = "degradation_evidence_reference"
EVIDENCE_MAPPING_LINEAGE = "lineage_evidence_reference"
EVIDENCE_MAPPING_PROVENANCE = "provenance_evidence_reference"
EVIDENCE_MAPPING_INTEGRITY = "integrity_evidence_reference"
EVIDENCE_MAPPING_BLOCKER = "blocker_evidence_reference"
EVIDENCE_MAPPING_WARNING = "warning_evidence_reference"
EVIDENCE_MAPPING_TYPES: tuple[str, ...] = (
    EVIDENCE_MAPPING_DRIFT,
    EVIDENCE_MAPPING_PROPAGATION,
    EVIDENCE_MAPPING_DEGRADATION,
    EVIDENCE_MAPPING_LINEAGE,
    EVIDENCE_MAPPING_PROVENANCE,
    EVIDENCE_MAPPING_INTEGRITY,
    EVIDENCE_MAPPING_BLOCKER,
    EVIDENCE_MAPPING_WARNING,
)

COMPLETENESS_COMPLETE = "complete_explanation_chain"
COMPLETENESS_PARTIALLY_SUPPORTED = "partially_supported_explanation_chain"
COMPLETENESS_EVIDENCE_LIMITED = "evidence_limited_explanation_chain"
COMPLETENESS_LINEAGE_LIMITED = "lineage_limited_explanation_chain"
COMPLETENESS_PROVENANCE_LIMITED = "provenance_limited_explanation_chain"
COMPLETENESS_UNSUPPORTED = "unsupported_explanation_chain"
EXPLANATION_COMPLETENESS_TYPES: tuple[str, ...] = (
    COMPLETENESS_COMPLETE,
    COMPLETENESS_PARTIALLY_SUPPORTED,
    COMPLETENESS_EVIDENCE_LIMITED,
    COMPLETENESS_LINEAGE_LIMITED,
    COMPLETENESS_PROVENANCE_LIMITED,
    COMPLETENESS_UNSUPPORTED,
)

CONFIDENCE_EVIDENCE_SUPPORTED = "evidence_supported"
CONFIDENCE_PARTIALLY_SUPPORTED = "partially_supported"
CONFIDENCE_EVIDENCE_LIMITED = "evidence_limited"
CONFIDENCE_LINEAGE_LIMITED = "lineage_limited"
CONFIDENCE_PROVENANCE_LIMITED = "provenance_limited"
CONFIDENCE_UNSUPPORTED = "unsupported"
EXPLANATION_CONFIDENCE_TYPES: tuple[str, ...] = (
    CONFIDENCE_EVIDENCE_SUPPORTED,
    CONFIDENCE_PARTIALLY_SUPPORTED,
    CONFIDENCE_EVIDENCE_LIMITED,
    CONFIDENCE_LINEAGE_LIMITED,
    CONFIDENCE_PROVENANCE_LIMITED,
    CONFIDENCE_UNSUPPORTED,
)

EXPLANATION_DIAGNOSTIC_MISSING_EVIDENCE = "missing_explanation_evidence"
EXPLANATION_DIAGNOSTIC_INCOMPLETE_LINEAGE = "incomplete_explanation_lineage"
EXPLANATION_DIAGNOSTIC_INCOMPLETE_PROVENANCE = "incomplete_provenance_support"
EXPLANATION_DIAGNOSTIC_UNSUPPORTED_CAUSAL = "unsupported_causal_explanation"
EXPLANATION_DIAGNOSTIC_CONTINUITY_GAPS = "explanation_continuity_gaps"
EXPLANATION_DIAGNOSTIC_DEGRADATION_GAPS = "degradation_explanation_gaps"
EXPLANATION_DIAGNOSTIC_PROPAGATION_GAPS = "propagation_explanation_gaps"
EXPLANATION_DIAGNOSTIC_EVIDENCE_MISMATCH = "evidence_to_explanation_mismatch"
EXPLANATION_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    EXPLANATION_DIAGNOSTIC_MISSING_EVIDENCE,
    EXPLANATION_DIAGNOSTIC_INCOMPLETE_LINEAGE,
    EXPLANATION_DIAGNOSTIC_INCOMPLETE_PROVENANCE,
    EXPLANATION_DIAGNOSTIC_UNSUPPORTED_CAUSAL,
    EXPLANATION_DIAGNOSTIC_CONTINUITY_GAPS,
    EXPLANATION_DIAGNOSTIC_DEGRADATION_GAPS,
    EXPLANATION_DIAGNOSTIC_PROPAGATION_GAPS,
    EXPLANATION_DIAGNOSTIC_EVIDENCE_MISMATCH,
)

EXPLANATION_VISIBILITY_VISIBLE = "explanation_visible"
EXPLANATION_VISIBILITY_CAUSE_VISIBLE = "cause_visible"
EXPLANATION_VISIBILITY_PROPAGATION_VISIBLE = "propagation_explanation_visible"
EXPLANATION_VISIBILITY_DEGRADATION_VISIBLE = "degradation_explanation_visible"
EXPLANATION_VISIBILITY_EVIDENCE_VISIBLE = "evidence_mapping_visible"
EXPLANATION_VISIBILITY_COMPLETENESS_VISIBLE = "completeness_visible"
EXPLANATION_VISIBILITY_CONFIDENCE_VISIBLE = "confidence_visible"
EXPLANATION_VISIBILITY_UNSUPPORTED_VISIBLE = "unsupported_explanation_visible"
EXPLANATION_VISIBILITY_DIAGNOSTIC_VISIBLE = "diagnostic_visible"

UNSUPPORTED_EXPLANATION_ORCHESTRATION_EXECUTION = "orchestration_execution"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_AUTHORIZATION = "orchestration_authorization"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_APPROVAL = "orchestration_approval"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_DISPATCH = "orchestration_dispatch"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_ROUTING = "orchestration_routing"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_TRAVERSAL = "orchestration_traversal"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_SCHEDULING = "orchestration_scheduling"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_SEQUENCING = "orchestration_sequencing"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_DECISION = "orchestration_decision"
UNSUPPORTED_EXPLANATION_ORCHESTRATION_RECOMMENDATION = "orchestration_recommendation"
UNSUPPORTED_EXPLANATION_REMEDIATION = "remediation"
UNSUPPORTED_EXPLANATION_REPAIR = "repair"
UNSUPPORTED_EXPLANATION_MITIGATION = "mitigation"
UNSUPPORTED_EXPLANATION_AUTOMATED_CORRECTION = "automated_correction"
UNSUPPORTED_EXPLANATION_ACTION = "explanation_driven_action"
UNSUPPORTED_EXPLANATION_RANKING = "explanation_driven_ranking"
UNSUPPORTED_EXPLANATION_AUTHORIZATION = "explanation_driven_authorization"
UNSUPPORTED_EXPLANATION_DECISION = "explanation_driven_decision"
UNSUPPORTED_EXPLANATION_RECOMMENDATION = "explanation_driven_recommendation"
UNSUPPORTED_EXPLANATION_RUNTIME_MUTATION = "runtime_mutation"
UNSUPPORTED_EXPLANATION_OPERATIONAL_MUTATION = "operational_mutation"
UNSUPPORTED_EXPLANATION_PLANNER_INTEGRATION = "planner_integration"
UNSUPPORTED_EXPLANATION_PRODUCTION_CONSUMPTION = "production_consumption"
UNSUPPORTED_EXPLANATION_OPERATIONAL_BEHAVIOR = "implicit_operational_behavior"
UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES: tuple[str, ...] = (
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_EXECUTION,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_AUTHORIZATION,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_APPROVAL,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_DISPATCH,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_ROUTING,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_TRAVERSAL,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_SCHEDULING,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_SEQUENCING,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_DECISION,
    UNSUPPORTED_EXPLANATION_ORCHESTRATION_RECOMMENDATION,
    UNSUPPORTED_EXPLANATION_REMEDIATION,
    UNSUPPORTED_EXPLANATION_REPAIR,
    UNSUPPORTED_EXPLANATION_MITIGATION,
    UNSUPPORTED_EXPLANATION_AUTOMATED_CORRECTION,
    UNSUPPORTED_EXPLANATION_ACTION,
    UNSUPPORTED_EXPLANATION_RANKING,
    UNSUPPORTED_EXPLANATION_AUTHORIZATION,
    UNSUPPORTED_EXPLANATION_DECISION,
    UNSUPPORTED_EXPLANATION_RECOMMENDATION,
    UNSUPPORTED_EXPLANATION_RUNTIME_MUTATION,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_MUTATION,
    UNSUPPORTED_EXPLANATION_PLANNER_INTEGRATION,
    UNSUPPORTED_EXPLANATION_PRODUCTION_CONSUMPTION,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_BEHAVIOR,
)

V4_5A_4_DRIFT_EXPLAINABILITY_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
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
    "enabled_explanation_action_count",
    "enabled_explanation_ranking_count",
    "enabled_explanation_authorization_count",
    "enabled_explanation_decision_count",
    "enabled_explanation_recommendation_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
)

V4_5A_4_DRIFT_EXPLAINABILITY_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_explanation_identity_stability",
    "deterministic_cause_visibility",
    "deterministic_propagation_explanation_chains",
    "deterministic_degradation_explanation_visibility",
    "deterministic_evidence_to_explanation_mapping",
    "deterministic_completeness_visibility",
    "deterministic_confidence_visibility",
    "deterministic_serialization_stability",
    "deterministic_hashing_stability",
    "replay_safe_explanation_evidence",
    "rollback_safe_explanation_evidence",
    "lineage_safe_explanation_visibility",
    "provenance_safe_explanation_visibility",
    "integrity_safe_explanation_visibility",
    "fail_visible_unsupported_explanation_preservation",
    "descriptive_only_governance_certification",
    "non_operational_certification",
)

V4_5A_4_DRIFT_EXPLAINABILITY_INHERITED_PROHIBITIONS: tuple[str, ...] = (
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
    "No explanation-driven action is introduced.",
    "No explanation-driven ranking is introduced.",
    "No explanation-driven authorization is introduced.",
    "No explanation-driven decision is introduced.",
    "No explanation-driven recommendation is introduced.",
    "No runtime mutation is introduced.",
    "No operational mutation is introduced.",
    "No planner integration is introduced.",
    "No production consumption is introduced.",
    "No implicit operational behavior is introduced.",
)

V4_5A_4_DRIFT_EXPLAINABILITY_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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

V4_5A_4_DRIFT_EXPLAINABILITY_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.5A.4 explains drift, propagation, and degradation visibility only.",
    "v4.5A.4 does not remediate, repair, mitigate, suppress, or correct drift.",
    "v4.5A.4 does not make explanation-driven decisions or recommendations.",
    "v4.5A.4 does not rank, score, authorize, or act on explanations.",
    "v4.5A.4 does not activate orchestration responses.",
    "v4.5A.4 does not integrate planners or execute planner behavior.",
    "v4.5A.4 does not consume production bundles.",
    "v4.5A.4 does not mutate runtime state or operational state.",
    "v4.5A.4 preserves unsupported explanation states as explicit fail-visible evidence.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class DriftExplainabilityIdentity:
    drift_explainability_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_degradation_report_reference: str
    source_degradation_hash_reference: str
    purpose: str = V4_5A_4_DRIFT_EXPLAINABILITY_PURPOSE
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
    explanation_action_enabled: bool = False
    explanation_ranking_enabled: bool = False
    explanation_authorization_enabled: bool = False
    runtime_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class ExplanationRecord:
    explanation_id: str
    explanation_chain_id: str
    source_drift_id: str
    propagation_chain_id: str
    degradation_chain_id: str
    evidence_chain_id: str
    continuity_reference_id: str
    lineage_reference_id: str
    provenance_reference_id: str
    deterministic_order: int
    deterministic: bool = True
    governance_safe: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    lineage_safe: bool = True
    provenance_safe: bool = True
    integrity_safe: bool = True
    explainability_first: bool = True
    descriptive_only: bool = True
    non_operational: bool = True
    runtime_execution_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_traversal_enabled: bool = False
    explanation_action_enabled: bool = False
    explanation_ranking_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DriftCauseVisibility:
    cause_id: str
    explanation_id: str
    cause_type: str
    visibility_state: str
    cause_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    no_hidden_causal_assumption: bool = True
    no_blame_assignment: bool = True
    non_decisioning: bool = True
    automated_blame_enabled: bool = False
    action_enabled: bool = False
    decision_enabled: bool = False
    recommendation_enabled: bool = False
    authorization_enabled: bool = False


@dataclass(frozen=True)
class PropagationExplanationChain:
    propagation_explanation_id: str
    explanation_id: str
    propagation_type: str
    propagation_chain_id: str
    explanation_chain_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    explanation_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    correction_enabled: bool = False
    suppression_enabled: bool = False
    mitigation_enabled: bool = False
    orchestration_response_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class IntegrityDegradationExplanation:
    degradation_explanation_id: str
    explanation_id: str
    degradation_type: str
    degradation_chain_id: str
    evidence_reference_ids: tuple[str, ...]
    visibility_state: str
    explanation_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    replay_safe: bool = True
    provenance_safe: bool = True
    lineage_safe: bool = True
    integrity_safe: bool = True
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    correction_enabled: bool = False
    orchestration_response_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class EvidenceExplanationMapping:
    mapping_id: str
    explanation_id: str
    evidence_type: str
    evidence_reference_id: str
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
class ExplanationCompletenessVisibility:
    completeness_id: str
    explanation_id: str
    completeness_type: str
    visibility_state: str
    completeness_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_scoring: bool = True
    non_ranking: bool = True
    non_authorizing: bool = True
    scoring_enabled: bool = False
    ranking_enabled: bool = False
    authorization_enabled: bool = False
    recommendation_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplanationConfidenceVisibility:
    confidence_id: str
    explanation_id: str
    confidence_type: str
    visibility_state: str
    confidence_reason: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    non_authorizing: bool = True
    non_ranking: bool = True
    non_recommending: bool = True
    authorization_enabled: bool = False
    ranking_enabled: bool = False
    recommendation_enabled: bool = False
    execution_enabled: bool = False
    suppression_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class ExplanationDiagnostic:
    diagnostic_id: str
    explanation_id: str
    diagnostic_type: str
    confidence_type: str
    visibility_state: str
    message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden_assumption_used: bool = False
    silent_fallback_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    mitigation_enabled: bool = False
    auto_correction_enabled: bool = False
    explanation_action_enabled: bool = False
    explanation_ranking_enabled: bool = False
    explanation_authorization_enabled: bool = False
    orchestration_response_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class UnsupportedExplanationVisibility:
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
    automated_correction_enabled: bool = False
    explanation_action_enabled: bool = False
    explanation_ranking_enabled: bool = False
    explanation_authorization_enabled: bool = False
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DriftExplainabilityIntelligence:
    explainability_identity: DriftExplainabilityIdentity
    explanation_records: tuple[ExplanationRecord, ...]
    cause_visibility: tuple[DriftCauseVisibility, ...]
    propagation_explanations: tuple[PropagationExplanationChain, ...]
    degradation_explanations: tuple[IntegrityDegradationExplanation, ...]
    evidence_mappings: tuple[EvidenceExplanationMapping, ...]
    completeness_visibility: tuple[ExplanationCompletenessVisibility, ...]
    confidence_visibility: tuple[ExplanationConfidenceVisibility, ...]
    diagnostics: tuple[ExplanationDiagnostic, ...]
    unsupported_explanation_visibility: tuple[UnsupportedExplanationVisibility, ...]
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
    non_ranking: bool = True
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
    explanation_action_enabled: bool = False
    explanation_ranking_enabled: bool = False
    explanation_authorization_enabled: bool = False
    explanation_decision_enabled: bool = False
    explanation_recommendation_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "explanation_records",
            "cause_visibility",
            "propagation_explanations",
            "degradation_explanations",
            "evidence_mappings",
            "completeness_visibility",
            "confidence_visibility",
            "diagnostics",
            "unsupported_explanation_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_drift_explainability_identity() -> DriftExplainabilityIdentity:
    return DriftExplainabilityIdentity(
        drift_explainability_id="v4_5a_4_governance_safe_drift_explainability",
        phase_id=V4_5A_4_DRIFT_EXPLAINABILITY_PHASE_ID,
        schema_version=V4_5A_4_DRIFT_EXPLAINABILITY_SCHEMA_VERSION,
        generated_at=V4_5A_4_DRIFT_EXPLAINABILITY_GENERATED_AT,
        classification=V4_5A_4_DRIFT_EXPLAINABILITY_CLASSIFICATION,
        source_degradation_report_reference=V4_5A_3_INTEGRITY_DEGRADATION_REPORT_REFERENCE,
        source_degradation_hash_reference=V4_5A_3_INTEGRITY_DEGRADATION_REPORT_HASH_REFERENCE,
    )


def default_explanation_records() -> tuple[ExplanationRecord, ...]:
    definitions = (
        ("explanation_inherited_drift", "explanation_chain_inherited_drift", "drift_inheritance_boundary_visibility", "propagation_chain_inherited", "degradation_chain_inheritance", "evidence_lineage_degradation", "continuity_degradation_lineage", "continuity_chain_scope", "provenance::v4_5a_3.inheritance", 1),
        ("explanation_refinement_drift", "explanation_chain_refinement_drift", "drift_refinement_boundary_visibility", "propagation_chain_refinement", "degradation_chain_refinement", "evidence_warning_degradation", "continuity_degradation_integrity", "continuity_chain_refinement", "provenance::v4_5a_3.refinement", 2),
        ("explanation_segmentation_drift", "explanation_chain_segmentation_drift", "drift_segmentation_boundary_visibility", "propagation_chain_cross_boundary", "degradation_chain_propagation_amplified", "evidence_propagation_degradation", "continuity_degradation_governance", "continuity_chain_compatibility", "provenance::v4_5a_3.segmentation", 3),
        ("explanation_scope_drift", "explanation_chain_scope_drift", "drift_scope_boundary_visibility", "propagation_chain_inherited", "degradation_chain_inheritance", "evidence_degradation", "continuity_degradation_lineage", "continuity_chain_scope", "provenance::v4_5a_3.scope", 4),
        ("explanation_compatibility_drift", "explanation_chain_compatibility_drift", "drift_compatibility_boundary_visibility", "propagation_chain_compatibility", "degradation_chain_integrity_visibility", "evidence_integrity_degradation", "continuity_degradation_integrity", "continuity_chain_integrity", "provenance::v4_5a_3.compatibility", 5),
        ("explanation_continuity_drift", "explanation_chain_continuity_drift", "drift_continuity_boundary_visibility", "propagation_chain_continuity", "degradation_chain_continuity", "evidence_continuity_degradation", "continuity_degradation_lineage", "continuity_chain_continuity", "provenance::v4_5a_3.continuity", 6),
        ("explanation_evidence_gap_drift", "explanation_chain_evidence_gap_drift", "drift_explainability_boundary_visibility", "propagation_chain_explainability", "degradation_chain_explainability", "evidence_explainability_degradation", "continuity_degradation_explainability", "continuity_chain_explainability", "provenance::v4_5a_3.evidence_gap", 7),
        ("explanation_unsupported_drift", "explanation_chain_unsupported_drift", "drift_compatibility_boundary_visibility", "propagation_chain_cross_boundary", "degradation_chain_unsupported_integrity_state", "evidence_blocker_degradation", "continuity_degradation_governance", "continuity_chain_compatibility", "provenance::v4_5a_3.unsupported", 8),
    )
    return tuple(ExplanationRecord(*definition) for definition in definitions)


def default_drift_cause_visibility() -> tuple[DriftCauseVisibility, ...]:
    return tuple(
        DriftCauseVisibility(
            cause_id=f"cause_{record.explanation_id}",
            explanation_id=record.explanation_id,
            cause_type=DRIFT_CAUSE_TYPES[index],
            visibility_state=EXPLANATION_VISIBILITY_CAUSE_VISIBLE,
            cause_reason=f"{DRIFT_CAUSE_TYPES[index]} is visible without causal judgment, blame, action, or authorization.",
            deterministic_order=record.deterministic_order,
        )
        for index, record in enumerate(default_explanation_records())
    )


def default_propagation_explanation_chains() -> tuple[PropagationExplanationChain, ...]:
    definitions = (
        ("propagation_explanation_direct", "explanation_continuity_drift", PROPAGATION_EXPLANATION_DIRECT, "propagation_chain_direct", "explanation_chain_continuity_drift", ("mapping_degradation_evidence_reference",), 1),
        ("propagation_explanation_inherited", "explanation_inherited_drift", PROPAGATION_EXPLANATION_INHERITED, "propagation_chain_inherited", "explanation_chain_inherited_drift", ("mapping_lineage_evidence_reference",), 2),
        ("propagation_explanation_refinement", "explanation_refinement_drift", PROPAGATION_EXPLANATION_REFINEMENT, "propagation_chain_refinement", "explanation_chain_refinement_drift", ("mapping_warning_evidence_reference",), 3),
        ("propagation_explanation_cross_boundary", "explanation_segmentation_drift", PROPAGATION_EXPLANATION_CROSS_BOUNDARY, "propagation_chain_cross_boundary", "explanation_chain_segmentation_drift", ("mapping_propagation_evidence_reference",), 4),
        ("propagation_explanation_continuity_impacting", "explanation_continuity_drift", PROPAGATION_EXPLANATION_CONTINUITY_IMPACTING, "propagation_chain_continuity", "explanation_chain_continuity_drift", ("mapping_drift_evidence_reference",), 5),
        ("propagation_explanation_integrity_impacting", "explanation_compatibility_drift", PROPAGATION_EXPLANATION_INTEGRITY_IMPACTING, "propagation_chain_compatibility", "explanation_chain_compatibility_drift", ("mapping_integrity_evidence_reference",), 6),
        ("propagation_explanation_unsupported", "explanation_unsupported_drift", PROPAGATION_EXPLANATION_UNSUPPORTED, "propagation_chain_cross_boundary", "explanation_chain_unsupported_drift", ("mapping_blocker_evidence_reference",), 7),
    )
    return tuple(
        PropagationExplanationChain(
            propagation_explanation_id=propagation_explanation_id,
            explanation_id=explanation_id,
            propagation_type=propagation_type,
            propagation_chain_id=propagation_chain_id,
            explanation_chain_id=explanation_chain_id,
            evidence_reference_ids=evidence_reference_ids,
            visibility_state=EXPLANATION_VISIBILITY_PROPAGATION_VISIBLE,
            explanation_reason=f"{propagation_type} remains descriptive-only without correction or suppression.",
            deterministic_order=order,
        )
        for (
            propagation_explanation_id,
            explanation_id,
            propagation_type,
            propagation_chain_id,
            explanation_chain_id,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_integrity_degradation_explanations() -> tuple[IntegrityDegradationExplanation, ...]:
    definitions = (
        ("degradation_explanation_origin", "explanation_continuity_drift", DEGRADATION_EXPLANATION_ORIGIN, "degradation_chain_continuity", ("mapping_degradation_evidence_reference",), 1),
        ("degradation_explanation_amplification", "explanation_segmentation_drift", DEGRADATION_EXPLANATION_AMPLIFICATION, "degradation_chain_propagation_amplified", ("mapping_propagation_evidence_reference",), 2),
        ("degradation_explanation_continuity", "explanation_continuity_drift", DEGRADATION_EXPLANATION_CONTINUITY, "degradation_chain_continuity", ("mapping_drift_evidence_reference",), 3),
        ("degradation_explanation_lineage", "explanation_inherited_drift", DEGRADATION_EXPLANATION_LINEAGE, "degradation_chain_lineage", ("mapping_lineage_evidence_reference",), 4),
        ("degradation_explanation_provenance", "explanation_scope_drift", DEGRADATION_EXPLANATION_PROVENANCE, "degradation_chain_provenance", ("mapping_provenance_evidence_reference",), 5),
        ("degradation_explanation_explainability", "explanation_evidence_gap_drift", DEGRADATION_EXPLANATION_EXPLAINABILITY, "degradation_chain_explainability", ("mapping_degradation_evidence_reference",), 6),
        ("degradation_explanation_unsupported", "explanation_unsupported_drift", DEGRADATION_EXPLANATION_UNSUPPORTED, "degradation_chain_unsupported_integrity_state", ("mapping_blocker_evidence_reference",), 7),
    )
    return tuple(
        IntegrityDegradationExplanation(
            degradation_explanation_id=degradation_explanation_id,
            explanation_id=explanation_id,
            degradation_type=degradation_type,
            degradation_chain_id=degradation_chain_id,
            evidence_reference_ids=evidence_reference_ids,
            visibility_state=EXPLANATION_VISIBILITY_DEGRADATION_VISIBLE,
            explanation_reason=f"{degradation_type} remains descriptive-only without remediation or mitigation.",
            deterministic_order=order,
        )
        for (
            degradation_explanation_id,
            explanation_id,
            degradation_type,
            degradation_chain_id,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_evidence_explanation_mappings() -> tuple[EvidenceExplanationMapping, ...]:
    definitions = (
        ("mapping_drift_evidence_reference", "explanation_continuity_drift", EVIDENCE_MAPPING_DRIFT, "evidence_degradation", "degradation_evidence_chain::evidence_degradation", "v4_5a_3.drift_explanation_input", 1),
        ("mapping_propagation_evidence_reference", "explanation_segmentation_drift", EVIDENCE_MAPPING_PROPAGATION, "evidence_propagation_degradation", "degradation_evidence_chain::evidence_propagation_degradation", "v4_5a_3.propagation_explanation_input", 2),
        ("mapping_degradation_evidence_reference", "explanation_continuity_drift", EVIDENCE_MAPPING_DEGRADATION, "evidence_continuity_degradation", "degradation_evidence_chain::evidence_continuity_degradation", "v4_5a_3.degradation_explanation_input", 3),
        ("mapping_lineage_evidence_reference", "explanation_inherited_drift", EVIDENCE_MAPPING_LINEAGE, "evidence_lineage_degradation", "degradation_evidence_chain::evidence_lineage_degradation", "v4_5a_3.lineage_explanation_input", 4),
        ("mapping_provenance_evidence_reference", "explanation_scope_drift", EVIDENCE_MAPPING_PROVENANCE, "evidence_provenance_degradation", "degradation_evidence_chain::evidence_provenance_degradation", "v4_5a_3.provenance_explanation_input", 5),
        ("mapping_integrity_evidence_reference", "explanation_compatibility_drift", EVIDENCE_MAPPING_INTEGRITY, "evidence_integrity_degradation", "degradation_evidence_chain::evidence_integrity_degradation", "v4_5a_3.integrity_explanation_input", 6),
        ("mapping_blocker_evidence_reference", "explanation_unsupported_drift", EVIDENCE_MAPPING_BLOCKER, "evidence_blocker_degradation", "degradation_evidence_chain::evidence_blocker_degradation", "v4_5a_3.blocker_explanation_input", 7),
        ("mapping_warning_evidence_reference", "explanation_refinement_drift", EVIDENCE_MAPPING_WARNING, "evidence_warning_degradation", "degradation_evidence_chain::evidence_warning_degradation", "v4_5a_3.warning_explanation_input", 8),
    )
    return tuple(
        EvidenceExplanationMapping(
            mapping_id=mapping_id,
            explanation_id=explanation_id,
            evidence_type=evidence_type,
            evidence_reference_id=evidence_reference_id,
            evidence_chain_id=evidence_chain_id,
            source_reference=f"{V4_5A_3_INTEGRITY_DEGRADATION_REPORT_REFERENCE}#{source_reference}",
            source_hash_reference=V4_5A_3_INTEGRITY_DEGRADATION_REPORT_HASH_REFERENCE,
            replay_reference=f"replay::{mapping_id}",
            provenance_reference=f"provenance::{source_reference}",
            deterministic_order=order,
        )
        for (
            mapping_id,
            explanation_id,
            evidence_type,
            evidence_reference_id,
            evidence_chain_id,
            source_reference,
            order,
        ) in definitions
    )


def default_explanation_completeness_visibility() -> tuple[ExplanationCompletenessVisibility, ...]:
    definitions = (
        ("completeness_complete", "explanation_continuity_drift", COMPLETENESS_COMPLETE, ("mapping_drift_evidence_reference",), 1),
        ("completeness_partially_supported", "explanation_segmentation_drift", COMPLETENESS_PARTIALLY_SUPPORTED, ("mapping_propagation_evidence_reference",), 2),
        ("completeness_evidence_limited", "explanation_evidence_gap_drift", COMPLETENESS_EVIDENCE_LIMITED, ("mapping_degradation_evidence_reference",), 3),
        ("completeness_lineage_limited", "explanation_inherited_drift", COMPLETENESS_LINEAGE_LIMITED, ("mapping_lineage_evidence_reference",), 4),
        ("completeness_provenance_limited", "explanation_scope_drift", COMPLETENESS_PROVENANCE_LIMITED, ("mapping_provenance_evidence_reference",), 5),
        ("completeness_unsupported", "explanation_unsupported_drift", COMPLETENESS_UNSUPPORTED, ("mapping_blocker_evidence_reference",), 6),
    )
    return tuple(
        ExplanationCompletenessVisibility(
            completeness_id=completeness_id,
            explanation_id=explanation_id,
            completeness_type=completeness_type,
            visibility_state=EXPLANATION_VISIBILITY_COMPLETENESS_VISIBLE,
            completeness_reason=f"{completeness_type} remains visibility-only and is not scoring, ranking, authorization, or recommendation.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            completeness_id,
            explanation_id,
            completeness_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_explanation_confidence_visibility() -> tuple[ExplanationConfidenceVisibility, ...]:
    definitions = (
        ("confidence_evidence_supported", "explanation_continuity_drift", CONFIDENCE_EVIDENCE_SUPPORTED, ("mapping_drift_evidence_reference",), 1),
        ("confidence_partially_supported", "explanation_segmentation_drift", CONFIDENCE_PARTIALLY_SUPPORTED, ("mapping_propagation_evidence_reference",), 2),
        ("confidence_evidence_limited", "explanation_evidence_gap_drift", CONFIDENCE_EVIDENCE_LIMITED, ("mapping_degradation_evidence_reference",), 3),
        ("confidence_lineage_limited", "explanation_inherited_drift", CONFIDENCE_LINEAGE_LIMITED, ("mapping_lineage_evidence_reference",), 4),
        ("confidence_provenance_limited", "explanation_scope_drift", CONFIDENCE_PROVENANCE_LIMITED, ("mapping_provenance_evidence_reference",), 5),
        ("confidence_unsupported", "explanation_unsupported_drift", CONFIDENCE_UNSUPPORTED, ("mapping_blocker_evidence_reference",), 6),
    )
    return tuple(
        ExplanationConfidenceVisibility(
            confidence_id=confidence_id,
            explanation_id=explanation_id,
            confidence_type=confidence_type,
            visibility_state=EXPLANATION_VISIBILITY_CONFIDENCE_VISIBLE,
            confidence_reason=f"{confidence_type} remains descriptive confidence visibility only.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            confidence_id,
            explanation_id,
            confidence_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_explanation_diagnostics() -> tuple[ExplanationDiagnostic, ...]:
    definitions = (
        ("diagnostic_missing_explanation_evidence", "explanation_evidence_gap_drift", EXPLANATION_DIAGNOSTIC_MISSING_EVIDENCE, CONFIDENCE_EVIDENCE_LIMITED, ("mapping_degradation_evidence_reference",), 1),
        ("diagnostic_incomplete_explanation_lineage", "explanation_inherited_drift", EXPLANATION_DIAGNOSTIC_INCOMPLETE_LINEAGE, CONFIDENCE_LINEAGE_LIMITED, ("mapping_lineage_evidence_reference",), 2),
        ("diagnostic_incomplete_provenance_support", "explanation_scope_drift", EXPLANATION_DIAGNOSTIC_INCOMPLETE_PROVENANCE, CONFIDENCE_PROVENANCE_LIMITED, ("mapping_provenance_evidence_reference",), 3),
        ("diagnostic_unsupported_causal_explanation", "explanation_unsupported_drift", EXPLANATION_DIAGNOSTIC_UNSUPPORTED_CAUSAL, CONFIDENCE_UNSUPPORTED, ("mapping_blocker_evidence_reference",), 4),
        ("diagnostic_explanation_continuity_gaps", "explanation_continuity_drift", EXPLANATION_DIAGNOSTIC_CONTINUITY_GAPS, CONFIDENCE_PARTIALLY_SUPPORTED, ("mapping_drift_evidence_reference",), 5),
        ("diagnostic_degradation_explanation_gaps", "explanation_compatibility_drift", EXPLANATION_DIAGNOSTIC_DEGRADATION_GAPS, CONFIDENCE_PARTIALLY_SUPPORTED, ("mapping_integrity_evidence_reference",), 6),
        ("diagnostic_propagation_explanation_gaps", "explanation_segmentation_drift", EXPLANATION_DIAGNOSTIC_PROPAGATION_GAPS, CONFIDENCE_PARTIALLY_SUPPORTED, ("mapping_propagation_evidence_reference",), 7),
        ("diagnostic_evidence_to_explanation_mismatch", "explanation_refinement_drift", EXPLANATION_DIAGNOSTIC_EVIDENCE_MISMATCH, CONFIDENCE_EVIDENCE_LIMITED, ("mapping_warning_evidence_reference",), 8),
    )
    return tuple(
        ExplanationDiagnostic(
            diagnostic_id=diagnostic_id,
            explanation_id=explanation_id,
            diagnostic_type=diagnostic_type,
            confidence_type=confidence_type,
            visibility_state=EXPLANATION_VISIBILITY_DIAGNOSTIC_VISIBLE,
            message=f"{diagnostic_type} remains fail-visible and descriptive-only.",
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            diagnostic_id,
            explanation_id,
            diagnostic_type,
            confidence_type,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_unsupported_explanation_visibility() -> tuple[UnsupportedExplanationVisibility, ...]:
    return tuple(
        UnsupportedExplanationVisibility(
            state_id=f"unsupported_explanation_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            visibility_state=EXPLANATION_VISIBILITY_UNSUPPORTED_VISIBLE,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5A.4 drift explainability intelligence."
            ),
            evidence_reference_ids=("mapping_blocker_evidence_reference",),
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(
            UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
            start=1,
        )
    )


def default_v4_5a_4_drift_explainability_intelligence() -> DriftExplainabilityIntelligence:
    return DriftExplainabilityIntelligence(
        explainability_identity=default_drift_explainability_identity(),
        explanation_records=default_explanation_records(),
        cause_visibility=default_drift_cause_visibility(),
        propagation_explanations=default_propagation_explanation_chains(),
        degradation_explanations=default_integrity_degradation_explanations(),
        evidence_mappings=default_evidence_explanation_mappings(),
        completeness_visibility=default_explanation_completeness_visibility(),
        confidence_visibility=default_explanation_confidence_visibility(),
        diagnostics=default_explanation_diagnostics(),
        unsupported_explanation_visibility=default_unsupported_explanation_visibility(),
        deterministic_guarantees=V4_5A_4_DRIFT_EXPLAINABILITY_DETERMINISTIC_GUARANTEES,
        inherited_prohibitions=V4_5A_4_DRIFT_EXPLAINABILITY_INHERITED_PROHIBITIONS,
        inherited_constraints=V4_5A_4_DRIFT_EXPLAINABILITY_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5A_4_DRIFT_EXPLAINABILITY_EXPLICIT_LIMITATIONS,
    )
