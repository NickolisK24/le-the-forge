"""Deterministic v3.9 transition continuity certification models.

Certification is evidence-only. It does not execute, approve, repair,
authorize, mutate, optimize, recommend, rank, score, select, prioritize,
route, schedule, dispatch, traverse, or expose callable behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_CERTIFICATION_PHASE_ID = "v3_9_transition_continuity_certification"
V3_9_TRANSITION_CERTIFICATION_SCHEMA_VERSION = "v3_9.transition_continuity_certification.1"
V3_9_TRANSITION_CERTIFICATION_REPORT_STABLE = "v3_9_transition_continuity_certification_stable"
V3_9_TRANSITION_CERTIFICATION_REPORT_BLOCKED = "v3_9_transition_continuity_certification_blocked"

CERTIFICATION_CLASSIFICATION_CERTIFIED = "certified"
CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS = "certified_with_warnings"
CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED = "not_certified"
CERTIFICATION_CLASSIFICATION_BLOCKED = "blocked"
CERTIFICATION_CLASSIFICATION_UNSUPPORTED = "unsupported"
CERTIFICATION_CLASSIFICATION_PROHIBITED = "prohibited"
CERTIFICATION_CLASSIFICATION_UNKNOWN = "unknown"
CERTIFICATION_CLASSIFICATION_INCOMPLETE = "incomplete"
CERTIFICATION_CLASSIFICATIONS: tuple[str, ...] = (
    CERTIFICATION_CLASSIFICATION_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_CERTIFIED_WITH_WARNINGS,
    CERTIFICATION_CLASSIFICATION_NOT_CERTIFIED,
    CERTIFICATION_CLASSIFICATION_BLOCKED,
    CERTIFICATION_CLASSIFICATION_UNSUPPORTED,
    CERTIFICATION_CLASSIFICATION_PROHIBITED,
    CERTIFICATION_CLASSIFICATION_UNKNOWN,
    CERTIFICATION_CLASSIFICATION_INCOMPLETE,
)

CERTIFICATION_DOMAIN_FOUNDATIONS = "foundations"
CERTIFICATION_DOMAIN_BOUNDARY = "boundary_intelligence"
CERTIFICATION_DOMAIN_COMPATIBILITY = "compatibility_intelligence"
CERTIFICATION_DOMAIN_EVALUATION = "evaluation_intelligence"
CERTIFICATION_DOMAIN_SESSION = "session_intelligence"
CERTIFICATION_DOMAIN_SCENARIO = "scenario_intelligence"
CERTIFICATION_DOMAIN_AGGREGATION = "aggregation_intelligence"
CERTIFICATION_DOMAIN_INTEGRITY = "integrity_enforcement"
REQUIRED_CERTIFICATION_DOMAINS: tuple[str, ...] = (
    CERTIFICATION_DOMAIN_FOUNDATIONS,
    CERTIFICATION_DOMAIN_BOUNDARY,
    CERTIFICATION_DOMAIN_COMPATIBILITY,
    CERTIFICATION_DOMAIN_EVALUATION,
    CERTIFICATION_DOMAIN_SESSION,
    CERTIFICATION_DOMAIN_SCENARIO,
    CERTIFICATION_DOMAIN_AGGREGATION,
    CERTIFICATION_DOMAIN_INTEGRITY,
)

CERTIFICATION_GUARANTEE_FOUNDATION = "foundation_continuity"
CERTIFICATION_GUARANTEE_BOUNDARY = "boundary_continuity"
CERTIFICATION_GUARANTEE_COMPATIBILITY = "compatibility_continuity"
CERTIFICATION_GUARANTEE_EVALUATION = "evaluation_continuity"
CERTIFICATION_GUARANTEE_SESSION = "session_continuity"
CERTIFICATION_GUARANTEE_SCENARIO = "scenario_continuity"
CERTIFICATION_GUARANTEE_AGGREGATION = "aggregation_continuity"
CERTIFICATION_GUARANTEE_INTEGRITY = "integrity_continuity"
CERTIFICATION_GUARANTEE_REPLAY = "replay_continuity"
CERTIFICATION_GUARANTEE_ROLLBACK = "rollback_continuity"
CERTIFICATION_GUARANTEE_PROVENANCE = "provenance_continuity"
CERTIFICATION_GUARANTEE_EXPLAINABILITY = "explainability_continuity"
CERTIFICATION_GUARANTEE_VISIBILITY = "visibility_continuity"
CERTIFICATION_GUARANTEE_NON_EXECUTION = "non_execution_continuity"
CERTIFICATION_GUARANTEE_NON_RRSS = "non_recommendation_ranking_scoring_selection_continuity"
CERTIFICATION_GUARANTEE_NON_MUTATION = "non_mutation_continuity"
CERTIFICATION_GUARANTEE_CATEGORIES: tuple[str, ...] = (
    CERTIFICATION_GUARANTEE_FOUNDATION,
    CERTIFICATION_GUARANTEE_BOUNDARY,
    CERTIFICATION_GUARANTEE_COMPATIBILITY,
    CERTIFICATION_GUARANTEE_EVALUATION,
    CERTIFICATION_GUARANTEE_SESSION,
    CERTIFICATION_GUARANTEE_SCENARIO,
    CERTIFICATION_GUARANTEE_AGGREGATION,
    CERTIFICATION_GUARANTEE_INTEGRITY,
    CERTIFICATION_GUARANTEE_REPLAY,
    CERTIFICATION_GUARANTEE_ROLLBACK,
    CERTIFICATION_GUARANTEE_PROVENANCE,
    CERTIFICATION_GUARANTEE_EXPLAINABILITY,
    CERTIFICATION_GUARANTEE_VISIBILITY,
    CERTIFICATION_GUARANTEE_NON_EXECUTION,
    CERTIFICATION_GUARANTEE_NON_RRSS,
    CERTIFICATION_GUARANTEE_NON_MUTATION,
)

CERTIFICATION_FINDING_CONTINUITY = "continuity"
CERTIFICATION_FINDING_PROVENANCE = "provenance"
CERTIFICATION_FINDING_REPLAY = "replay"
CERTIFICATION_FINDING_ROLLBACK = "rollback"
CERTIFICATION_FINDING_EXPLAINABILITY = "explainability"
CERTIFICATION_FINDING_VISIBILITY = "visibility"
CERTIFICATION_FINDING_INTEGRITY = "integrity"
CERTIFICATION_FINDING_GOVERNANCE = "governance"
CERTIFICATION_FINDING_UNSUPPORTED = "unsupported"
CERTIFICATION_FINDING_PROHIBITED = "prohibited"
CERTIFICATION_FINDING_MISSING_EVIDENCE = "missing_evidence"
CERTIFICATION_FINDING_UNCERTAINTY = "uncertainty"
CERTIFICATION_FINDING_HIDDEN_BEHAVIOR = "hidden_behavior"
CERTIFICATION_FINDING_NON_EXECUTION = "non_execution"
CERTIFICATION_FINDING_NON_RRSS = "non_recommendation_ranking_scoring_selection"
CERTIFICATION_FINDING_NON_MUTATION = "non_mutation"
CERTIFICATION_FINDING_CATEGORIES: tuple[str, ...] = (
    CERTIFICATION_FINDING_CONTINUITY,
    CERTIFICATION_FINDING_PROVENANCE,
    CERTIFICATION_FINDING_REPLAY,
    CERTIFICATION_FINDING_ROLLBACK,
    CERTIFICATION_FINDING_EXPLAINABILITY,
    CERTIFICATION_FINDING_VISIBILITY,
    CERTIFICATION_FINDING_INTEGRITY,
    CERTIFICATION_FINDING_GOVERNANCE,
    CERTIFICATION_FINDING_UNSUPPORTED,
    CERTIFICATION_FINDING_PROHIBITED,
    CERTIFICATION_FINDING_MISSING_EVIDENCE,
    CERTIFICATION_FINDING_UNCERTAINTY,
    CERTIFICATION_FINDING_HIDDEN_BEHAVIOR,
    CERTIFICATION_FINDING_NON_EXECUTION,
    CERTIFICATION_FINDING_NON_RRSS,
    CERTIFICATION_FINDING_NON_MUTATION,
)

CERTIFICATION_VISIBILITY_FAIL_VISIBLE = "fail_visible"
CERTIFICATION_VISIBILITY_CERTIFICATION_STATUS = "certification_status"
CERTIFICATION_VISIBILITY_CONTINUITY = "continuity"
CERTIFICATION_VISIBILITY_INTEGRITY = "integrity"
CERTIFICATION_VISIBILITY_HIDDEN_BEHAVIOR = "hidden_behavior"
CERTIFICATION_VISIBILITY_CAPABILITY_LEAKAGE = "capability_leakage"
CERTIFICATION_VISIBILITY_NON_EXECUTION = "non_execution"
CERTIFICATION_VISIBILITY_NON_MUTATION = "non_mutation"
CERTIFICATION_VISIBILITY_NON_RRSS = "non_recommendation_ranking_scoring_selection"
CERTIFICATION_VISIBILITY_MISSING_EVIDENCE = "missing_evidence"
CERTIFICATION_VISIBILITY_UNSUPPORTED = "unsupported"
CERTIFICATION_VISIBILITY_PROHIBITED = "prohibited"
CERTIFICATION_VISIBILITY_UNKNOWN = "unknown"
CERTIFICATION_VISIBILITY_GOVERNANCE = "governance"
CERTIFICATION_VISIBILITY_CATEGORIES: tuple[str, ...] = (
    CERTIFICATION_VISIBILITY_FAIL_VISIBLE,
    CERTIFICATION_VISIBILITY_CERTIFICATION_STATUS,
    CERTIFICATION_VISIBILITY_CONTINUITY,
    CERTIFICATION_VISIBILITY_INTEGRITY,
    CERTIFICATION_VISIBILITY_HIDDEN_BEHAVIOR,
    CERTIFICATION_VISIBILITY_CAPABILITY_LEAKAGE,
    CERTIFICATION_VISIBILITY_NON_EXECUTION,
    CERTIFICATION_VISIBILITY_NON_MUTATION,
    CERTIFICATION_VISIBILITY_NON_RRSS,
    CERTIFICATION_VISIBILITY_MISSING_EVIDENCE,
    CERTIFICATION_VISIBILITY_UNSUPPORTED,
    CERTIFICATION_VISIBILITY_PROHIBITED,
    CERTIFICATION_VISIBILITY_UNKNOWN,
    CERTIFICATION_VISIBILITY_GOVERNANCE,
)

SUPPORTED_CERTIFICATION_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_continuity_certification",
    "transition_certification_visibility",
    "transition_certification_evidence_reporting",
)
PROHIBITED_CERTIFICATION_CAPABILITIES: tuple[str, ...] = (
    "orchestration_execution",
    "transition_execution",
    "graph_traversal",
    "routing",
    "scheduling",
    "dispatch",
    "runtime_orchestration_engine",
    "runtime_mutation",
    "authorization",
    "approval",
    "optimization",
    "recommendation",
    "ranking",
    "scoring",
    "selection",
    "autonomous_behavior",
    "callable_orchestration_flow",
    "transition_handler",
    "runtime_state_machine",
    "production_behavior",
    "automatic_remediation",
    "automatic_repair",
    "remediation",
    "repair",
    "silent_correction",
    "hidden_fallback",
)
CERTIFICATION_CHOICE_PROHIBITED_CAPABILITIES: tuple[str, ...] = (
    "recommendation",
    "ranking",
    "scoring",
    "selection",
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class TransitionCertificationInput:
    input_id: str
    certification_id: str
    certification_domain: str
    required_domain_ids: tuple[str, ...]
    present_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    integrity_report_id: str
    integrity_hash: str
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    visibility_reference_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    warning_markers: tuple[str, ...] = ()
    failure_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    evidence_only_certification: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "required_domain_ids",
            "present_domain_ids",
            "evidence_ids",
            "provenance_reference_ids",
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "visibility_reference_ids",
            "requested_capabilities",
            "warning_markers",
            "failure_markers",
            "blocked_markers",
            "unsupported_markers",
            "prohibited_markers",
            "unknown_markers",
            "incomplete_markers",
            "governance_policy_ids",
            "integrity_policy_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionCertificationFinding:
    finding_id: str
    input_id: str
    finding_category: str
    classification: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    descriptive_only: bool = True
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionCertificationGuarantee:
    guarantee_id: str
    input_id: str
    guarantee_category: str
    classification: str
    certification_status: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    visible: bool = True
    hidden: bool = False
    guarantee_preserved: bool = True
    descriptive_only: bool = True
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False


@dataclass(frozen=True)
class TransitionCertificationContinuity:
    continuity_id: str
    input_id: str
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    visibility_reference_ids: tuple[str, ...]
    evidence_continuity_ids: tuple[str, ...]
    deterministic_hash_reference: str
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    visibility_continuity_preserved: bool = True
    integrity_continuity_preserved: bool = True
    non_execution_continuity_preserved: bool = True
    immutable_continuity: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "visibility_reference_ids",
            "evidence_continuity_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionCertificationVisibility:
    visibility_id: str
    input_id: str
    visibility_category: str
    classification: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    descriptive_only: bool = True
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    priority_ranking_enabled: bool = False
    weighted_scoring_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False


@dataclass(frozen=True)
class TransitionCertificationEvidence:
    evidence_id: str
    input_id: str
    certification_id: str
    source_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    guarantee_ids: tuple[str, ...]
    visibility_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_continuity_certification_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    execution_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    ranking_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    selection_behavior_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "source_domain_ids",
            "evidence_ids",
            "finding_ids",
            "guarantee_ids",
            "visibility_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionCertificationSummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    guarantee_category_counts: Mapping[str, int]
    visibility_category_counts: Mapping[str, int]
    certified_count: int
    certified_with_warnings_count: int
    not_certified_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    certification_finding_count: int
    certification_guarantee_count: int
    replay_continuity_guarantee_count: int
    rollback_continuity_guarantee_count: int
    provenance_continuity_guarantee_count: int
    explainability_continuity_guarantee_count: int
    visibility_continuity_guarantee_count: int
    integrity_continuity_guarantee_count: int
    non_execution_continuity_guarantee_count: int
    recommendation_ranking_scoring_selection_non_capability_guarantee_count: int
    mutation_non_capability_guarantee_count: int
    hidden_finding_count: int
    hidden_risk_count: int
    hidden_non_safe_state_count: int
    execution_boundary_leakage_count: int
    recommendation_leakage_count: int
    ranking_leakage_count: int
    scoring_leakage_count: int
    selection_leakage_count: int
    mutation_leakage_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))
        object.__setattr__(self, "guarantee_category_counts", dict(sorted(self.guarantee_category_counts.items())))
        object.__setattr__(self, "visibility_category_counts", dict(sorted(self.visibility_category_counts.items())))


@dataclass(frozen=True)
class TransitionCertificationReport:
    report_id: str
    report_status: str
    source_integrity_report_id: str
    source_integrity_hash: str
    certification_inputs: tuple[TransitionCertificationInput, ...]
    findings: tuple[TransitionCertificationFinding, ...]
    guarantees: tuple[TransitionCertificationGuarantee, ...]
    evidence_records: tuple[TransitionCertificationEvidence, ...]
    continuities: tuple[TransitionCertificationContinuity, ...]
    visibilities: tuple[TransitionCertificationVisibility, ...]
    summary: TransitionCertificationSummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_certification_hash: str = ""
    non_executable: bool = True
    orchestration_execution_enabled: bool = False
    transition_execution_enabled: bool = False
    graph_traversal_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    runtime_orchestration_engine_enabled: bool = False
    runtime_mutation_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    autonomous_behavior_enabled: bool = False
    callable_orchestration_flow_enabled: bool = False
    transition_handler_enabled: bool = False
    runtime_state_machine_enabled: bool = False
    production_behavior_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    automatic_remediation_enabled: bool = False
    automatic_repair_enabled: bool = False
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False
    prioritization_enabled: bool = False
    weighted_scoring_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "certification_inputs",
            "findings",
            "guarantees",
            "evidence_records",
            "continuities",
            "visibilities",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_certification_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_certification_{input_id}_{finding_category}_{safe_marker}"


def transition_certification_guarantee_id(input_id: str, guarantee_category: str) -> str:
    return f"v3_9_transition_certification_{input_id}_guarantee_{guarantee_category}"


def export_transition_certification_input(source: TransitionCertificationInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "required_domain_ids",
        "present_domain_ids",
        "evidence_ids",
        "provenance_reference_ids",
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "visibility_reference_ids",
        "requested_capabilities",
        "warning_markers",
        "failure_markers",
        "blocked_markers",
        "unsupported_markers",
        "prohibited_markers",
        "unknown_markers",
        "incomplete_markers",
        "governance_policy_ids",
        "integrity_policy_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_certification_finding(finding: TransitionCertificationFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_certification_guarantee(guarantee: TransitionCertificationGuarantee) -> dict[str, Any]:
    return asdict(guarantee)


def export_transition_certification_continuity(continuity: TransitionCertificationContinuity) -> dict[str, Any]:
    data = asdict(continuity)
    for field_name in (
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "visibility_reference_ids",
        "evidence_continuity_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_certification_visibility(visibility: TransitionCertificationVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_certification_evidence(evidence: TransitionCertificationEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_domain_ids",
        "evidence_ids",
        "finding_ids",
        "guarantee_ids",
        "visibility_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_certification_summary(summary: TransitionCertificationSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    data["guarantee_category_counts"] = dict(sorted(summary.guarantee_category_counts.items()))
    data["visibility_category_counts"] = dict(sorted(summary.visibility_category_counts.items()))
    return data


def export_transition_certification_report(report: TransitionCertificationReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_integrity_report_id": report.source_integrity_report_id,
        "source_integrity_hash": report.source_integrity_hash,
        "certification_inputs": [
            export_transition_certification_input(source)
            for source in sorted(report.certification_inputs, key=lambda item: item.input_id)
        ],
        "findings": [
            export_transition_certification_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "guarantees": [
            export_transition_certification_guarantee(guarantee)
            for guarantee in sorted(report.guarantees, key=lambda item: (item.deterministic_order, item.guarantee_id))
        ],
        "evidence_records": [
            export_transition_certification_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_certification_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "visibilities": [
            export_transition_certification_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))
        ],
        "summary": export_transition_certification_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_certification_hash": report.deterministic_certification_hash,
        "non_executable": report.non_executable,
        "orchestration_execution_enabled": report.orchestration_execution_enabled,
        "transition_execution_enabled": report.transition_execution_enabled,
        "graph_traversal_enabled": report.graph_traversal_enabled,
        "routing_enabled": report.routing_enabled,
        "scheduling_enabled": report.scheduling_enabled,
        "dispatch_enabled": report.dispatch_enabled,
        "runtime_orchestration_engine_enabled": report.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": report.runtime_mutation_enabled,
        "authorization_enabled": report.authorization_enabled,
        "approval_enabled": report.approval_enabled,
        "optimization_enabled": report.optimization_enabled,
        "recommendation_enabled": report.recommendation_enabled,
        "ranking_enabled": report.ranking_enabled,
        "scoring_enabled": report.scoring_enabled,
        "selection_enabled": report.selection_enabled,
        "autonomous_behavior_enabled": report.autonomous_behavior_enabled,
        "callable_orchestration_flow_enabled": report.callable_orchestration_flow_enabled,
        "transition_handler_enabled": report.transition_handler_enabled,
        "runtime_state_machine_enabled": report.runtime_state_machine_enabled,
        "production_behavior_enabled": report.production_behavior_enabled,
        "remediation_enabled": report.remediation_enabled,
        "repair_enabled": report.repair_enabled,
        "automatic_remediation_enabled": report.automatic_remediation_enabled,
        "automatic_repair_enabled": report.automatic_repair_enabled,
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
        "prioritization_enabled": report.prioritization_enabled,
        "weighted_scoring_enabled": report.weighted_scoring_enabled,
    }
