"""Deterministic v4.5A.1 governance-safe drift foundation models.

The v4.5A.1 Track A foundation is descriptive governance intelligence only. It
models boundary drift identity, classification, lineage, evidence, continuity,
severity, explainability, and fail-visible diagnostics without remediation,
repair, authorization, orchestration response, planner execution, production
consumption, runtime mutation, or operational behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


V4_5A_1_DRIFT_FOUNDATION_PHASE_ID = "v4_5a_1_drift_foundations"
V4_5A_1_DRIFT_FOUNDATION_SCHEMA_VERSION = "v4_5a_1.drift_foundations.1"
V4_5A_1_DRIFT_FOUNDATION_REPORT_SCHEMA_VERSION = "v4_5a_1.drift_foundations_report.1"
V4_5A_1_DRIFT_FOUNDATION_GENERATED_AT = "2026-05-18T00:00:00+00:00"
V4_5A_1_DRIFT_FOUNDATION_STATUS_STABLE = "v4_5a_1_drift_foundations_stable"
V4_5A_1_DRIFT_FOUNDATION_STATUS_BLOCKED = "v4_5a_1_drift_foundations_blocked"
V4_5A_1_DRIFT_FOUNDATION_PURPOSE = (
    "deterministic_governance_safe_boundary_drift_foundations_descriptive_only"
)
V4_5A_1_DRIFT_FOUNDATION_CLASSIFICATION = (
    "governance_safe_descriptive_boundary_drift_foundation_intelligence"
)
V4_4_CLOSEOUT_READINESS_REPORT_REFERENCE = (
    "docs/generated/v4_4_closeout_and_v4_5_readiness_report.json"
)
V4_4_CLOSEOUT_READINESS_REPORT_HASH_REFERENCE = (
    "a7ee46381a3f4dba5d649374a3c9832e0100cb69a1b6084d38f7bd1ab6441287"
)

DRIFT_CATEGORY_INHERITANCE = "inheritance_drift"
DRIFT_CATEGORY_REFINEMENT = "refinement_drift"
DRIFT_CATEGORY_SEGMENTATION = "segmentation_drift"
DRIFT_CATEGORY_SCOPE = "scope_drift"
DRIFT_CATEGORY_COMPATIBILITY = "compatibility_drift"
DRIFT_CATEGORY_CONTINUITY = "continuity_drift"
DRIFT_CATEGORY_EXPLAINABILITY = "explainability_drift"
DRIFT_CATEGORY_INTEGRITY_VISIBILITY = "integrity_visibility_drift"
DRIFT_CLASSIFICATION_CATEGORIES: tuple[str, ...] = (
    DRIFT_CATEGORY_INHERITANCE,
    DRIFT_CATEGORY_REFINEMENT,
    DRIFT_CATEGORY_SEGMENTATION,
    DRIFT_CATEGORY_SCOPE,
    DRIFT_CATEGORY_COMPATIBILITY,
    DRIFT_CATEGORY_CONTINUITY,
    DRIFT_CATEGORY_EXPLAINABILITY,
    DRIFT_CATEGORY_INTEGRITY_VISIBILITY,
)

DRIFT_SEVERITY_INFORMATIONAL = "informational"
DRIFT_SEVERITY_LOW_VISIBILITY = "low_visibility"
DRIFT_SEVERITY_MODERATE_VISIBILITY = "moderate_visibility"
DRIFT_SEVERITY_HIGH_VISIBILITY = "high_visibility"
DRIFT_SEVERITY_CRITICAL_VISIBILITY = "critical_visibility"
DRIFT_SEVERITY_LEVELS: tuple[str, ...] = (
    DRIFT_SEVERITY_INFORMATIONAL,
    DRIFT_SEVERITY_LOW_VISIBILITY,
    DRIFT_SEVERITY_MODERATE_VISIBILITY,
    DRIFT_SEVERITY_HIGH_VISIBILITY,
    DRIFT_SEVERITY_CRITICAL_VISIBILITY,
)

DRIFT_EVIDENCE_SOURCE = "source_evidence"
DRIFT_EVIDENCE_INHERITED = "inherited_evidence"
DRIFT_EVIDENCE_REFINEMENT = "refinement_evidence"
DRIFT_EVIDENCE_CONTINUITY = "continuity_evidence"
DRIFT_EVIDENCE_INTEGRITY = "integrity_evidence"
DRIFT_EVIDENCE_EXPLAINABILITY = "explainability_evidence"
DRIFT_EVIDENCE_BLOCKER = "blocker_evidence"
DRIFT_EVIDENCE_WARNING = "warning_evidence"
DRIFT_EVIDENCE_TYPES: tuple[str, ...] = (
    DRIFT_EVIDENCE_SOURCE,
    DRIFT_EVIDENCE_INHERITED,
    DRIFT_EVIDENCE_REFINEMENT,
    DRIFT_EVIDENCE_CONTINUITY,
    DRIFT_EVIDENCE_INTEGRITY,
    DRIFT_EVIDENCE_EXPLAINABILITY,
    DRIFT_EVIDENCE_BLOCKER,
    DRIFT_EVIDENCE_WARNING,
)

DRIFT_CONTINUITY_LINEAGE = "lineage_continuity"
DRIFT_CONTINUITY_PROVENANCE = "provenance_continuity"
DRIFT_CONTINUITY_INHERITANCE = "inheritance_continuity"
DRIFT_CONTINUITY_REFINEMENT = "refinement_continuity"
DRIFT_CONTINUITY_GOVERNANCE = "governance_continuity"
DRIFT_CONTINUITY_INTEGRITY = "integrity_continuity"
DRIFT_CONTINUITY_TYPES: tuple[str, ...] = (
    DRIFT_CONTINUITY_LINEAGE,
    DRIFT_CONTINUITY_PROVENANCE,
    DRIFT_CONTINUITY_INHERITANCE,
    DRIFT_CONTINUITY_REFINEMENT,
    DRIFT_CONTINUITY_GOVERNANCE,
    DRIFT_CONTINUITY_INTEGRITY,
)

DRIFT_DIAGNOSTIC_UNRESOLVED_DRIFT = "unresolved_drift"
DRIFT_DIAGNOSTIC_INCOMPLETE_LINEAGE = "incomplete_lineage"
DRIFT_DIAGNOSTIC_MISSING_EVIDENCE = "missing_evidence"
DRIFT_DIAGNOSTIC_INCOMPATIBLE_REFINEMENT = "incompatible_refinement"
DRIFT_DIAGNOSTIC_CONTINUITY_GAPS = "continuity_gaps"
DRIFT_DIAGNOSTIC_EXPLAINABILITY_GAPS = "explainability_gaps"
DRIFT_DIAGNOSTIC_UNSUPPORTED_DRIFT_STATES = "unsupported_drift_states"
DRIFT_DIAGNOSTIC_TYPES: tuple[str, ...] = (
    DRIFT_DIAGNOSTIC_UNRESOLVED_DRIFT,
    DRIFT_DIAGNOSTIC_INCOMPLETE_LINEAGE,
    DRIFT_DIAGNOSTIC_MISSING_EVIDENCE,
    DRIFT_DIAGNOSTIC_INCOMPATIBLE_REFINEMENT,
    DRIFT_DIAGNOSTIC_CONTINUITY_GAPS,
    DRIFT_DIAGNOSTIC_EXPLAINABILITY_GAPS,
    DRIFT_DIAGNOSTIC_UNSUPPORTED_DRIFT_STATES,
)

DRIFT_VISIBILITY_CLASSIFIED = "classified_visible"
DRIFT_VISIBILITY_EVIDENCE_VISIBLE = "evidence_visible"
DRIFT_VISIBILITY_CONTINUITY_VISIBLE = "continuity_visible"
DRIFT_VISIBILITY_DIAGNOSTIC_VISIBLE = "diagnostic_visible"
DRIFT_VISIBILITY_UNSUPPORTED_VISIBLE = "unsupported_state_visible"
DRIFT_VISIBILITY_PRESERVED = "preserved_visible"
DRIFT_VISIBILITY_GAP_VISIBLE = "gap_visible"
DRIFT_VISIBILITY_STATES: tuple[str, ...] = (
    DRIFT_VISIBILITY_CLASSIFIED,
    DRIFT_VISIBILITY_EVIDENCE_VISIBLE,
    DRIFT_VISIBILITY_CONTINUITY_VISIBLE,
    DRIFT_VISIBILITY_DIAGNOSTIC_VISIBLE,
    DRIFT_VISIBILITY_UNSUPPORTED_VISIBLE,
    DRIFT_VISIBILITY_PRESERVED,
    DRIFT_VISIBILITY_GAP_VISIBLE,
)

UNSUPPORTED_STATE_ORCHESTRATION_EXECUTION = "orchestration_execution"
UNSUPPORTED_STATE_ORCHESTRATION_ACTIVATION = "orchestration_activation"
UNSUPPORTED_STATE_ORCHESTRATION_AUTHORIZATION = "orchestration_authorization"
UNSUPPORTED_STATE_ORCHESTRATION_ROUTING = "orchestration_routing"
UNSUPPORTED_STATE_ORCHESTRATION_SCHEDULING = "orchestration_scheduling"
UNSUPPORTED_STATE_REMEDIATION = "remediation"
UNSUPPORTED_STATE_REPAIR = "repair"
UNSUPPORTED_STATE_AUTOMATED_CORRECTION = "automated_correction"
UNSUPPORTED_STATE_RUNTIME_MUTATION = "runtime_mutation"
UNSUPPORTED_STATE_PLANNER_EXECUTION = "planner_execution"
UNSUPPORTED_STATE_OPERATIONAL_BEHAVIOR = "operational_behavior"
UNSUPPORTED_DRIFT_OPERATIONAL_STATES: tuple[str, ...] = (
    UNSUPPORTED_STATE_ORCHESTRATION_EXECUTION,
    UNSUPPORTED_STATE_ORCHESTRATION_ACTIVATION,
    UNSUPPORTED_STATE_ORCHESTRATION_AUTHORIZATION,
    UNSUPPORTED_STATE_ORCHESTRATION_ROUTING,
    UNSUPPORTED_STATE_ORCHESTRATION_SCHEDULING,
    UNSUPPORTED_STATE_REMEDIATION,
    UNSUPPORTED_STATE_REPAIR,
    UNSUPPORTED_STATE_AUTOMATED_CORRECTION,
    UNSUPPORTED_STATE_RUNTIME_MUTATION,
    UNSUPPORTED_STATE_PLANNER_EXECUTION,
    UNSUPPORTED_STATE_OPERATIONAL_BEHAVIOR,
)

V4_5A_1_DRIFT_FOUNDATION_DISABLED_COUNTER_NAMES: tuple[str, ...] = (
    "enabled_runtime_execution_count",
    "enabled_orchestration_authorization_count",
    "enabled_orchestration_approval_count",
    "enabled_orchestration_routing_count",
    "enabled_orchestration_dispatch_count",
    "enabled_orchestration_scheduling_count",
    "enabled_orchestration_sequencing_count",
    "enabled_orchestration_recommendation_count",
    "enabled_orchestration_decision_count",
    "enabled_remediation_count",
    "enabled_repair_count",
    "enabled_auto_correction_count",
    "enabled_runtime_mutation_count",
    "enabled_operational_mutation_count",
    "enabled_planner_integration_count",
    "enabled_production_consumption_count",
)

V4_5A_1_DRIFT_FOUNDATION_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic_drift_identity_stability",
    "deterministic_drift_classification_stability",
    "deterministic_drift_lineage_stability",
    "deterministic_drift_evidence_reference_stability",
    "deterministic_drift_severity_visibility",
    "deterministic_drift_continuity_visibility",
    "deterministic_drift_explainability_foundations",
    "deterministic_serialization_stability",
    "deterministic_hashing_stability",
    "replay_safe_evidence_visibility",
    "rollback_safe_drift_visibility",
    "lineage_safe_drift_visibility",
    "provenance_safe_drift_visibility",
    "integrity_safe_drift_visibility",
    "fail_visible_unsupported_state_preservation",
    "descriptive_only_governance_certification",
    "non_operational_certification",
)

V4_5A_1_DRIFT_FOUNDATION_INHERITED_PROHIBITIONS: tuple[str, ...] = (
    "No orchestration execution is introduced.",
    "No orchestration activation is introduced.",
    "No orchestration authorization is introduced.",
    "No orchestration approval is introduced.",
    "No orchestration routing is introduced.",
    "No orchestration traversal is introduced.",
    "No orchestration scheduling is introduced.",
    "No orchestration sequencing is introduced.",
    "No orchestration recommendations are introduced.",
    "No orchestration decisions are introduced.",
    "No remediation system is introduced.",
    "No repair system is introduced.",
    "No automated correction is introduced.",
    "No runtime mutation is introduced.",
    "No operational mutation is introduced.",
    "No planner integration is introduced.",
    "No production consumption is introduced.",
    "No runtime orchestration semantics are introduced.",
)

V4_5A_1_DRIFT_FOUNDATION_INHERITED_CONSTRAINTS: tuple[str, ...] = (
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

V4_5A_1_DRIFT_FOUNDATION_EXPLICIT_LIMITATIONS: tuple[str, ...] = (
    "v4.5A.1 establishes drift foundation intelligence only.",
    "v4.5A.1 does not repair, remediate, resolve, or correct drift.",
    "v4.5A.1 does not activate orchestration responses to drift.",
    "v4.5A.1 does not authorize, approve, route, dispatch, schedule, sequence, recommend, or decide orchestration.",
    "v4.5A.1 does not integrate planners or execute planner behavior.",
    "v4.5A.1 does not consume production bundles.",
    "v4.5A.1 does not mutate runtime state or operational state.",
    "v4.5A.1 preserves unsupported operational states as explicit fail-visible evidence.",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class DriftFoundationIdentity:
    foundation_id: str
    phase_id: str
    schema_version: str
    generated_at: str
    classification: str
    source_phase_id: str
    source_report_reference: str
    source_report_hash_reference: str
    purpose: str = V4_5A_1_DRIFT_FOUNDATION_PURPOSE
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
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False


@dataclass(frozen=True)
class DriftIdentityRecord:
    drift_id: str
    boundary_id: str
    source_boundary_id: str
    inherited_boundary_id: str
    refinement_boundary_id: str
    governance_scope_id: str
    continuity_chain_id: str
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
    orchestration_routing_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DriftClassificationRecord:
    classification_id: str
    drift_id: str
    category: str
    severity: str
    visibility_state: str
    classification_reason: str
    deterministic_order: int
    descriptive_only: bool = True
    non_authoritative: bool = True
    operational_meaning_enabled: bool = False
    remediation_enabled: bool = False
    authorization_enabled: bool = False
    recommendation_enabled: bool = False
    decision_enabled: bool = False


@dataclass(frozen=True)
class DriftEvidenceReference:
    evidence_id: str
    drift_id: str
    evidence_type: str
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
    hidden_inference_used: bool = False
    production_consumption_enabled: bool = False


@dataclass(frozen=True)
class DriftContinuityVisibility:
    continuity_id: str
    drift_id: str
    continuity_type: str
    continuity_chain_id: str
    source_reference_id: str
    target_reference_id: str
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
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class DriftDiagnosticRecord:
    diagnostic_id: str
    drift_id: str
    diagnostic_type: str
    severity: str
    visibility_state: str
    message: str
    evidence_reference_ids: tuple[str, ...]
    deterministic_order: int
    fail_visible: bool = True
    descriptive_only: bool = True
    hidden_fallback_used: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    auto_correction_enabled: bool = False
    orchestration_response_enabled: bool = False
    authorization_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DriftSeverityVisibility:
    severity_id: str
    severity: str
    drift_ids: tuple[str, ...]
    diagnostic_ids: tuple[str, ...]
    count: int
    deterministic_order: int
    descriptive_only: bool = True
    non_remediating: bool = True
    non_authorizing: bool = True
    non_operational: bool = True
    remediation_enabled: bool = False
    authorization_enabled: bool = False
    operational_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "drift_ids")
        _set_tuple_field(self, "diagnostic_ids")


@dataclass(frozen=True)
class UnsupportedDriftStateVisibility:
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
    authorization_enabled: bool = False

    def __post_init__(self) -> None:
        _set_tuple_field(self, "evidence_reference_ids")


@dataclass(frozen=True)
class DriftFoundationIntelligence:
    foundation_identity: DriftFoundationIdentity
    drift_identities: tuple[DriftIdentityRecord, ...]
    classifications: tuple[DriftClassificationRecord, ...]
    evidence_references: tuple[DriftEvidenceReference, ...]
    continuity_visibility: tuple[DriftContinuityVisibility, ...]
    diagnostics: tuple[DriftDiagnosticRecord, ...]
    severity_visibility: tuple[DriftSeverityVisibility, ...]
    unsupported_state_visibility: tuple[UnsupportedDriftStateVisibility, ...]
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
    non_scheduling: bool = True
    non_sequencing: bool = True
    non_recommending: bool = True
    non_deciding: bool = True
    runtime_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    orchestration_activation_enabled: bool = False
    orchestration_authorization_enabled: bool = False
    orchestration_approval_enabled: bool = False
    orchestration_routing_enabled: bool = False
    orchestration_dispatch_enabled: bool = False
    orchestration_scheduling_enabled: bool = False
    orchestration_sequencing_enabled: bool = False
    orchestration_recommendation_enabled: bool = False
    orchestration_decision_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    auto_correction_enabled: bool = False
    runtime_mutation_enabled: bool = False
    operational_mutation_enabled: bool = False
    planner_integration_enabled: bool = False
    planner_execution_enabled: bool = False
    production_consumption_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "drift_identities",
            "classifications",
            "evidence_references",
            "continuity_visibility",
            "diagnostics",
            "severity_visibility",
            "unsupported_state_visibility",
            "deterministic_guarantees",
            "inherited_prohibitions",
            "inherited_constraints",
            "explicit_limitations",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))


def default_drift_foundation_identity() -> DriftFoundationIdentity:
    return DriftFoundationIdentity(
        foundation_id="v4_5a_1_governance_safe_drift_foundations",
        phase_id=V4_5A_1_DRIFT_FOUNDATION_PHASE_ID,
        schema_version=V4_5A_1_DRIFT_FOUNDATION_SCHEMA_VERSION,
        generated_at=V4_5A_1_DRIFT_FOUNDATION_GENERATED_AT,
        classification=V4_5A_1_DRIFT_FOUNDATION_CLASSIFICATION,
        source_phase_id="v4_4_closeout_and_v4_5_readiness",
        source_report_reference=V4_4_CLOSEOUT_READINESS_REPORT_REFERENCE,
        source_report_hash_reference=V4_4_CLOSEOUT_READINESS_REPORT_HASH_REFERENCE,
    )


def default_drift_identity_records() -> tuple[DriftIdentityRecord, ...]:
    definitions = (
        ("drift_inheritance_boundary_visibility", "boundary_inheritance_visibility", "source_boundary_inheritance", "inherited_boundary_governance", "refinement_boundary_inheritance", "governance_scope_inheritance", "continuity_chain_inheritance", 1),
        ("drift_refinement_boundary_visibility", "boundary_refinement_visibility", "source_boundary_refinement", "inherited_boundary_refinement", "refinement_boundary_governance", "governance_scope_refinement", "continuity_chain_refinement", 2),
        ("drift_segmentation_boundary_visibility", "boundary_segmentation_visibility", "source_boundary_segmentation", "inherited_boundary_segmentation", "refinement_boundary_segmentation", "governance_scope_segmentation", "continuity_chain_segmentation", 3),
        ("drift_scope_boundary_visibility", "boundary_scope_visibility", "source_boundary_scope", "inherited_boundary_scope", "refinement_boundary_scope", "governance_scope_visibility", "continuity_chain_scope", 4),
        ("drift_compatibility_boundary_visibility", "boundary_compatibility_visibility", "source_boundary_compatibility", "inherited_boundary_compatibility", "refinement_boundary_compatibility", "governance_scope_compatibility", "continuity_chain_compatibility", 5),
        ("drift_continuity_boundary_visibility", "boundary_continuity_visibility", "source_boundary_continuity", "inherited_boundary_continuity", "refinement_boundary_continuity", "governance_scope_continuity", "continuity_chain_continuity", 6),
        ("drift_explainability_boundary_visibility", "boundary_explainability_visibility", "source_boundary_explainability", "inherited_boundary_explainability", "refinement_boundary_explainability", "governance_scope_explainability", "continuity_chain_explainability", 7),
        ("drift_integrity_boundary_visibility", "boundary_integrity_visibility", "source_boundary_integrity", "inherited_boundary_integrity", "refinement_boundary_integrity", "governance_scope_integrity", "continuity_chain_integrity", 8),
    )
    return tuple(DriftIdentityRecord(*definition) for definition in definitions)


def default_drift_classification_records() -> tuple[DriftClassificationRecord, ...]:
    definitions = (
        ("classification_inheritance_drift", "drift_inheritance_boundary_visibility", DRIFT_CATEGORY_INHERITANCE, DRIFT_SEVERITY_INFORMATIONAL, "Inheritance drift identity is visible without operational meaning.", 1),
        ("classification_refinement_drift", "drift_refinement_boundary_visibility", DRIFT_CATEGORY_REFINEMENT, DRIFT_SEVERITY_LOW_VISIBILITY, "Refinement drift is classified as descriptive evidence only.", 2),
        ("classification_segmentation_drift", "drift_segmentation_boundary_visibility", DRIFT_CATEGORY_SEGMENTATION, DRIFT_SEVERITY_MODERATE_VISIBILITY, "Segmentation drift visibility is modeled without routing authority.", 3),
        ("classification_scope_drift", "drift_scope_boundary_visibility", DRIFT_CATEGORY_SCOPE, DRIFT_SEVERITY_LOW_VISIBILITY, "Scope drift remains a governance-safe visibility classification.", 4),
        ("classification_compatibility_drift", "drift_compatibility_boundary_visibility", DRIFT_CATEGORY_COMPATIBILITY, DRIFT_SEVERITY_HIGH_VISIBILITY, "Compatibility drift is visible without authorization or approval semantics.", 5),
        ("classification_continuity_drift", "drift_continuity_boundary_visibility", DRIFT_CATEGORY_CONTINUITY, DRIFT_SEVERITY_CRITICAL_VISIBILITY, "Continuity drift is fail-visible and non-remediating.", 6),
        ("classification_explainability_drift", "drift_explainability_boundary_visibility", DRIFT_CATEGORY_EXPLAINABILITY, DRIFT_SEVERITY_MODERATE_VISIBILITY, "Explainability drift foundations preserve visible reasons without recommendations.", 7),
        ("classification_integrity_visibility_drift", "drift_integrity_boundary_visibility", DRIFT_CATEGORY_INTEGRITY_VISIBILITY, DRIFT_SEVERITY_HIGH_VISIBILITY, "Integrity visibility drift remains descriptive and integrity-safe.", 8),
    )
    return tuple(
        DriftClassificationRecord(
            classification_id=classification_id,
            drift_id=drift_id,
            category=category,
            severity=severity,
            visibility_state=DRIFT_VISIBILITY_CLASSIFIED,
            classification_reason=reason,
            deterministic_order=order,
        )
        for classification_id, drift_id, category, severity, reason, order in definitions
    )


def default_drift_evidence_references() -> tuple[DriftEvidenceReference, ...]:
    definitions = (
        ("evidence_source_boundary_drift", "drift_segmentation_boundary_visibility", DRIFT_EVIDENCE_SOURCE, "v4_4_boundary_segmentation_scope.deterministic_report_hash", 1),
        ("evidence_inherited_boundary_drift", "drift_inheritance_boundary_visibility", DRIFT_EVIDENCE_INHERITED, "v4_4_boundary_inheritance_refinement.deterministic_report_hash", 2),
        ("evidence_refinement_boundary_drift", "drift_refinement_boundary_visibility", DRIFT_EVIDENCE_REFINEMENT, "v4_4_boundary_inheritance_refinement.deterministic_report_hash", 3),
        ("evidence_continuity_boundary_drift", "drift_continuity_boundary_visibility", DRIFT_EVIDENCE_CONTINUITY, "v4_4_boundary_continuity_integrity.deterministic_report_hash", 4),
        ("evidence_integrity_boundary_drift", "drift_integrity_boundary_visibility", DRIFT_EVIDENCE_INTEGRITY, "v4_4_boundary_continuity_integrity.deterministic_report_hash", 5),
        ("evidence_explainability_boundary_drift", "drift_explainability_boundary_visibility", DRIFT_EVIDENCE_EXPLAINABILITY, "v4_4_boundary_explainability_aggregation.deterministic_report_hash", 6),
        ("evidence_blocker_boundary_drift", "drift_compatibility_boundary_visibility", DRIFT_EVIDENCE_BLOCKER, "v4_4_boundary_blocker_resolution.deterministic_report_hash", 7),
        ("evidence_warning_boundary_drift", "drift_scope_boundary_visibility", DRIFT_EVIDENCE_WARNING, "v4_4_closeout_and_v4_5_readiness.warning_visibility", 8),
    )
    return tuple(
        DriftEvidenceReference(
            evidence_id=evidence_id,
            drift_id=drift_id,
            evidence_type=evidence_type,
            source_reference=f"{V4_4_CLOSEOUT_READINESS_REPORT_REFERENCE}#{source_reference}",
            source_hash_reference=V4_4_CLOSEOUT_READINESS_REPORT_HASH_REFERENCE,
            replay_reference=f"replay::{evidence_id}",
            provenance_reference=f"provenance::{source_reference}",
            deterministic_order=order,
        )
        for evidence_id, drift_id, evidence_type, source_reference, order in definitions
    )


def default_drift_continuity_visibility() -> tuple[DriftContinuityVisibility, ...]:
    definitions = (
        ("continuity_inheritance_drift", "drift_inheritance_boundary_visibility", DRIFT_CONTINUITY_INHERITANCE, "continuity_chain_inheritance", "source_boundary_inheritance", "inherited_boundary_governance", 1),
        ("continuity_refinement_drift", "drift_refinement_boundary_visibility", DRIFT_CONTINUITY_REFINEMENT, "continuity_chain_refinement", "source_boundary_refinement", "refinement_boundary_governance", 2),
        ("continuity_segmentation_drift", "drift_segmentation_boundary_visibility", DRIFT_CONTINUITY_GOVERNANCE, "continuity_chain_segmentation", "source_boundary_segmentation", "governance_scope_segmentation", 3),
        ("continuity_scope_drift", "drift_scope_boundary_visibility", DRIFT_CONTINUITY_GOVERNANCE, "continuity_chain_scope", "source_boundary_scope", "governance_scope_visibility", 4),
        ("continuity_compatibility_drift", "drift_compatibility_boundary_visibility", DRIFT_CONTINUITY_INTEGRITY, "continuity_chain_compatibility", "source_boundary_compatibility", "governance_scope_compatibility", 5),
        ("continuity_lineage_drift", "drift_continuity_boundary_visibility", DRIFT_CONTINUITY_LINEAGE, "continuity_chain_continuity", "source_boundary_continuity", "inherited_boundary_continuity", 6),
        ("continuity_provenance_drift", "drift_explainability_boundary_visibility", DRIFT_CONTINUITY_PROVENANCE, "continuity_chain_explainability", "source_boundary_explainability", "governance_scope_explainability", 7),
        ("continuity_integrity_drift", "drift_integrity_boundary_visibility", DRIFT_CONTINUITY_INTEGRITY, "continuity_chain_integrity", "source_boundary_integrity", "governance_scope_integrity", 8),
    )
    return tuple(
        DriftContinuityVisibility(
            continuity_id=continuity_id,
            drift_id=drift_id,
            continuity_type=continuity_type,
            continuity_chain_id=chain_id,
            source_reference_id=source_reference,
            target_reference_id=target_reference,
            visibility_state=DRIFT_VISIBILITY_CONTINUITY_VISIBLE,
            continuity_reason=(
                "Continuity is visible, deterministic, replay-safe, and non-remediating."
            ),
            deterministic_order=order,
        )
        for (
            continuity_id,
            drift_id,
            continuity_type,
            chain_id,
            source_reference,
            target_reference,
            order,
        ) in definitions
    )


def default_drift_diagnostics() -> tuple[DriftDiagnosticRecord, ...]:
    definitions = (
        ("diagnostic_unresolved_drift", "drift_continuity_boundary_visibility", DRIFT_DIAGNOSTIC_UNRESOLVED_DRIFT, DRIFT_SEVERITY_HIGH_VISIBILITY, "Unresolved drift is preserved as explicit visibility only.", ("evidence_continuity_boundary_drift",), 1),
        ("diagnostic_incomplete_lineage", "drift_continuity_boundary_visibility", DRIFT_DIAGNOSTIC_INCOMPLETE_LINEAGE, DRIFT_SEVERITY_CRITICAL_VISIBILITY, "Incomplete lineage is fail-visible and does not trigger repair.", ("evidence_continuity_boundary_drift",), 2),
        ("diagnostic_missing_evidence", "drift_integrity_boundary_visibility", DRIFT_DIAGNOSTIC_MISSING_EVIDENCE, DRIFT_SEVERITY_HIGH_VISIBILITY, "Missing evidence is reported without fallback inference.", ("evidence_integrity_boundary_drift",), 3),
        ("diagnostic_incompatible_refinement", "drift_refinement_boundary_visibility", DRIFT_DIAGNOSTIC_INCOMPATIBLE_REFINEMENT, DRIFT_SEVERITY_MODERATE_VISIBILITY, "Incompatible refinement remains descriptive and non-authorizing.", ("evidence_refinement_boundary_drift",), 4),
        ("diagnostic_continuity_gaps", "drift_continuity_boundary_visibility", DRIFT_DIAGNOSTIC_CONTINUITY_GAPS, DRIFT_SEVERITY_CRITICAL_VISIBILITY, "Continuity gaps are visible without remediation.", ("evidence_continuity_boundary_drift",), 5),
        ("diagnostic_explainability_gaps", "drift_explainability_boundary_visibility", DRIFT_DIAGNOSTIC_EXPLAINABILITY_GAPS, DRIFT_SEVERITY_MODERATE_VISIBILITY, "Explainability gaps remain explainability-first and non-recommending.", ("evidence_explainability_boundary_drift",), 6),
        ("diagnostic_unsupported_drift_states", "drift_compatibility_boundary_visibility", DRIFT_DIAGNOSTIC_UNSUPPORTED_DRIFT_STATES, DRIFT_SEVERITY_CRITICAL_VISIBILITY, "Unsupported drift states are fail-visible and never operationalized.", ("evidence_blocker_boundary_drift",), 7),
    )
    return tuple(
        DriftDiagnosticRecord(
            diagnostic_id=diagnostic_id,
            drift_id=drift_id,
            diagnostic_type=diagnostic_type,
            severity=severity,
            visibility_state=DRIFT_VISIBILITY_DIAGNOSTIC_VISIBLE,
            message=message,
            evidence_reference_ids=evidence_reference_ids,
            deterministic_order=order,
        )
        for (
            diagnostic_id,
            drift_id,
            diagnostic_type,
            severity,
            message,
            evidence_reference_ids,
            order,
        ) in definitions
    )


def default_drift_severity_visibility() -> tuple[DriftSeverityVisibility, ...]:
    classifications = default_drift_classification_records()
    diagnostics = default_drift_diagnostics()
    records: list[DriftSeverityVisibility] = []
    for order, severity in enumerate(DRIFT_SEVERITY_LEVELS, start=1):
        drift_ids = tuple(
            classification.drift_id for classification in classifications if classification.severity == severity
        )
        diagnostic_ids = tuple(
            diagnostic.diagnostic_id for diagnostic in diagnostics if diagnostic.severity == severity
        )
        records.append(
            DriftSeverityVisibility(
                severity_id=f"severity_visibility_{severity}",
                severity=severity,
                drift_ids=drift_ids,
                diagnostic_ids=diagnostic_ids,
                count=len(drift_ids) + len(diagnostic_ids),
                deterministic_order=order,
            )
        )
    return tuple(records)


def default_unsupported_state_visibility() -> tuple[UnsupportedDriftStateVisibility, ...]:
    return tuple(
        UnsupportedDriftStateVisibility(
            state_id=f"unsupported_drift_state_{unsupported_state}",
            unsupported_state=unsupported_state,
            visibility_state=DRIFT_VISIBILITY_UNSUPPORTED_VISIBLE,
            explicit_reason=(
                f"{unsupported_state} remains unsupported for v4.5A.1 drift foundations."
            ),
            evidence_reference_ids=("evidence_blocker_boundary_drift",),
            deterministic_order=order,
        )
        for order, unsupported_state in enumerate(UNSUPPORTED_DRIFT_OPERATIONAL_STATES, start=1)
    )


def default_v4_5a_1_drift_foundations() -> DriftFoundationIntelligence:
    return DriftFoundationIntelligence(
        foundation_identity=default_drift_foundation_identity(),
        drift_identities=default_drift_identity_records(),
        classifications=default_drift_classification_records(),
        evidence_references=default_drift_evidence_references(),
        continuity_visibility=default_drift_continuity_visibility(),
        diagnostics=default_drift_diagnostics(),
        severity_visibility=default_drift_severity_visibility(),
        unsupported_state_visibility=default_unsupported_state_visibility(),
        deterministic_guarantees=V4_5A_1_DRIFT_FOUNDATION_DETERMINISTIC_GUARANTEES,
        inherited_prohibitions=V4_5A_1_DRIFT_FOUNDATION_INHERITED_PROHIBITIONS,
        inherited_constraints=V4_5A_1_DRIFT_FOUNDATION_INHERITED_CONSTRAINTS,
        explicit_limitations=V4_5A_1_DRIFT_FOUNDATION_EXPLICIT_LIMITATIONS,
    )
