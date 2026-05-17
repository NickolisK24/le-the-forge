"""Deterministic v3.9 transition integrity enforcement models.

These models audit transition intelligence evidence. They do not execute,
repair, authorize, approve, mutate, optimize, recommend, rank, score, select,
prioritize, route, schedule, dispatch, traverse, or expose callable behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_INTEGRITY_PHASE_ID = "v3_9_transition_integrity_enforcement"
V3_9_TRANSITION_INTEGRITY_SCHEMA_VERSION = "v3_9.transition_integrity_enforcement.1"
V3_9_TRANSITION_INTEGRITY_REPORT_STABLE = "v3_9_transition_integrity_enforcement_stable"
V3_9_TRANSITION_INTEGRITY_REPORT_BLOCKED = "v3_9_transition_integrity_enforcement_blocked"

INTEGRITY_CLASSIFICATION_SATISFIED = "integrity_satisfied"
INTEGRITY_CLASSIFICATION_WARNING = "integrity_warning"
INTEGRITY_CLASSIFICATION_FAILED = "integrity_failed"
INTEGRITY_CLASSIFICATION_BLOCKED = "blocked"
INTEGRITY_CLASSIFICATION_UNSUPPORTED = "unsupported"
INTEGRITY_CLASSIFICATION_PROHIBITED = "prohibited"
INTEGRITY_CLASSIFICATION_UNKNOWN = "unknown"
INTEGRITY_CLASSIFICATION_INCOMPLETE = "incomplete"
INTEGRITY_CLASSIFICATIONS: tuple[str, ...] = (
    INTEGRITY_CLASSIFICATION_SATISFIED,
    INTEGRITY_CLASSIFICATION_WARNING,
    INTEGRITY_CLASSIFICATION_FAILED,
    INTEGRITY_CLASSIFICATION_BLOCKED,
    INTEGRITY_CLASSIFICATION_UNSUPPORTED,
    INTEGRITY_CLASSIFICATION_PROHIBITED,
    INTEGRITY_CLASSIFICATION_UNKNOWN,
    INTEGRITY_CLASSIFICATION_INCOMPLETE,
)
NON_SATISFIED_INTEGRITY_CLASSIFICATIONS: tuple[str, ...] = (
    INTEGRITY_CLASSIFICATION_WARNING,
    INTEGRITY_CLASSIFICATION_FAILED,
    INTEGRITY_CLASSIFICATION_BLOCKED,
    INTEGRITY_CLASSIFICATION_UNSUPPORTED,
    INTEGRITY_CLASSIFICATION_PROHIBITED,
    INTEGRITY_CLASSIFICATION_UNKNOWN,
    INTEGRITY_CLASSIFICATION_INCOMPLETE,
)

INTEGRITY_DOMAIN_FOUNDATIONS = "foundations"
INTEGRITY_DOMAIN_BOUNDARY = "boundary_intelligence"
INTEGRITY_DOMAIN_COMPATIBILITY = "compatibility_intelligence"
INTEGRITY_DOMAIN_EVALUATION = "evaluation_intelligence"
INTEGRITY_DOMAIN_SESSION = "session_intelligence"
INTEGRITY_DOMAIN_SCENARIO = "scenario_intelligence"
INTEGRITY_DOMAIN_AGGREGATION = "aggregation_intelligence"
REQUIRED_INTEGRITY_DOMAINS: tuple[str, ...] = (
    INTEGRITY_DOMAIN_FOUNDATIONS,
    INTEGRITY_DOMAIN_BOUNDARY,
    INTEGRITY_DOMAIN_COMPATIBILITY,
    INTEGRITY_DOMAIN_EVALUATION,
    INTEGRITY_DOMAIN_SESSION,
    INTEGRITY_DOMAIN_SCENARIO,
    INTEGRITY_DOMAIN_AGGREGATION,
)

INTEGRITY_FINDING_FOUNDATION = "foundation_integrity"
INTEGRITY_FINDING_BOUNDARY = "boundary_integrity"
INTEGRITY_FINDING_COMPATIBILITY = "compatibility_integrity"
INTEGRITY_FINDING_EVALUATION = "evaluation_integrity"
INTEGRITY_FINDING_SESSION = "session_integrity"
INTEGRITY_FINDING_SCENARIO = "scenario_integrity"
INTEGRITY_FINDING_AGGREGATION = "aggregation_integrity"
INTEGRITY_FINDING_PROVENANCE = "provenance_continuity_integrity"
INTEGRITY_FINDING_REPLAY = "replay_continuity_integrity"
INTEGRITY_FINDING_ROLLBACK = "rollback_continuity_integrity"
INTEGRITY_FINDING_EXPLAINABILITY = "explainability_continuity_integrity"
INTEGRITY_FINDING_FAIL_VISIBLE = "fail_visible_finding_integrity"
INTEGRITY_FINDING_RISK_VISIBILITY = "risk_visibility_integrity"
INTEGRITY_FINDING_HIDDEN_FINDING = "hidden_finding_detection"
INTEGRITY_FINDING_HIDDEN_RISK = "hidden_risk_detection"
INTEGRITY_FINDING_HIDDEN_NON_SAFE = "hidden_non_safe_state_detection"
INTEGRITY_FINDING_CAPABILITY_LEAKAGE = "capability_leakage_detection"
INTEGRITY_FINDING_VISIBILITY_GAP = "visibility_gap_detection"
INTEGRITY_FINDING_MISSING_EVIDENCE = "missing_evidence_integrity"
INTEGRITY_FINDING_GOVERNANCE = "governance_integrity"
INTEGRITY_FINDING_INTEGRITY_PRECONDITION = "integrity_precondition"
INTEGRITY_FINDING_UNSUPPORTED = "unsupported_integrity"
INTEGRITY_FINDING_PROHIBITED = "prohibited_integrity"
INTEGRITY_FINDING_UNCERTAINTY = "uncertainty_integrity"
INTEGRITY_FINDING_CATEGORIES: tuple[str, ...] = (
    INTEGRITY_FINDING_FOUNDATION,
    INTEGRITY_FINDING_BOUNDARY,
    INTEGRITY_FINDING_COMPATIBILITY,
    INTEGRITY_FINDING_EVALUATION,
    INTEGRITY_FINDING_SESSION,
    INTEGRITY_FINDING_SCENARIO,
    INTEGRITY_FINDING_AGGREGATION,
    INTEGRITY_FINDING_PROVENANCE,
    INTEGRITY_FINDING_REPLAY,
    INTEGRITY_FINDING_ROLLBACK,
    INTEGRITY_FINDING_EXPLAINABILITY,
    INTEGRITY_FINDING_FAIL_VISIBLE,
    INTEGRITY_FINDING_RISK_VISIBILITY,
    INTEGRITY_FINDING_HIDDEN_FINDING,
    INTEGRITY_FINDING_HIDDEN_RISK,
    INTEGRITY_FINDING_HIDDEN_NON_SAFE,
    INTEGRITY_FINDING_CAPABILITY_LEAKAGE,
    INTEGRITY_FINDING_VISIBILITY_GAP,
    INTEGRITY_FINDING_MISSING_EVIDENCE,
    INTEGRITY_FINDING_GOVERNANCE,
    INTEGRITY_FINDING_INTEGRITY_PRECONDITION,
    INTEGRITY_FINDING_UNSUPPORTED,
    INTEGRITY_FINDING_PROHIBITED,
    INTEGRITY_FINDING_UNCERTAINTY,
)

INTEGRITY_VIOLATION_HIDDEN_FINDING = "hidden_finding"
INTEGRITY_VIOLATION_HIDDEN_RISK = "hidden_risk"
INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE = "hidden_non_safe_state"
INTEGRITY_VIOLATION_MISSING_FOUNDATION_EVIDENCE = "missing_foundation_evidence"
INTEGRITY_VIOLATION_MISSING_BOUNDARY_EVIDENCE = "missing_boundary_evidence"
INTEGRITY_VIOLATION_MISSING_COMPATIBILITY_EVIDENCE = "missing_compatibility_evidence"
INTEGRITY_VIOLATION_MISSING_EVALUATION_EVIDENCE = "missing_evaluation_evidence"
INTEGRITY_VIOLATION_MISSING_SESSION_EVIDENCE = "missing_session_evidence"
INTEGRITY_VIOLATION_MISSING_SCENARIO_EVIDENCE = "missing_scenario_evidence"
INTEGRITY_VIOLATION_MISSING_AGGREGATION_EVIDENCE = "missing_aggregation_evidence"
INTEGRITY_VIOLATION_PROVENANCE_GAP = "provenance_gap"
INTEGRITY_VIOLATION_REPLAY_GAP = "replay_gap"
INTEGRITY_VIOLATION_ROLLBACK_GAP = "rollback_gap"
INTEGRITY_VIOLATION_EXPLAINABILITY_GAP = "explainability_gap"
INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP = "aggregation_integrity_gap"
INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK = "execution_boundary_leak"
INTEGRITY_VIOLATION_RECOMMENDATION_LEAK = "recommendation_leak"
INTEGRITY_VIOLATION_RANKING_LEAK = "ranking_leak"
INTEGRITY_VIOLATION_SCORING_LEAK = "scoring_leak"
INTEGRITY_VIOLATION_SELECTION_LEAK = "selection_leak"
INTEGRITY_VIOLATION_MUTATION_LEAK = "mutation_leak"
INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP = "unsupported_visibility_gap"
INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP = "prohibited_visibility_gap"
INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP = "unknown_visibility_gap"
INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP = "missing_evidence_gap"
INTEGRITY_VIOLATION_TYPES: tuple[str, ...] = (
    INTEGRITY_VIOLATION_HIDDEN_FINDING,
    INTEGRITY_VIOLATION_HIDDEN_RISK,
    INTEGRITY_VIOLATION_HIDDEN_NON_SAFE_STATE,
    INTEGRITY_VIOLATION_MISSING_FOUNDATION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_BOUNDARY_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_COMPATIBILITY_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_EVALUATION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_SESSION_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_SCENARIO_EVIDENCE,
    INTEGRITY_VIOLATION_MISSING_AGGREGATION_EVIDENCE,
    INTEGRITY_VIOLATION_PROVENANCE_GAP,
    INTEGRITY_VIOLATION_REPLAY_GAP,
    INTEGRITY_VIOLATION_ROLLBACK_GAP,
    INTEGRITY_VIOLATION_EXPLAINABILITY_GAP,
    INTEGRITY_VIOLATION_AGGREGATION_INTEGRITY_GAP,
    INTEGRITY_VIOLATION_EXECUTION_BOUNDARY_LEAK,
    INTEGRITY_VIOLATION_RECOMMENDATION_LEAK,
    INTEGRITY_VIOLATION_RANKING_LEAK,
    INTEGRITY_VIOLATION_SCORING_LEAK,
    INTEGRITY_VIOLATION_SELECTION_LEAK,
    INTEGRITY_VIOLATION_MUTATION_LEAK,
    INTEGRITY_VIOLATION_UNSUPPORTED_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_PROHIBITED_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_UNKNOWN_VISIBILITY_GAP,
    INTEGRITY_VIOLATION_MISSING_EVIDENCE_GAP,
)

INTEGRITY_VISIBILITY_FAIL_VISIBLE = "fail_visible"
INTEGRITY_VISIBILITY_HIDDEN_BEHAVIOR = "hidden_behavior"
INTEGRITY_VISIBILITY_PROVENANCE = "provenance"
INTEGRITY_VISIBILITY_REPLAY = "replay"
INTEGRITY_VISIBILITY_ROLLBACK = "rollback"
INTEGRITY_VISIBILITY_EXPLAINABILITY = "explainability"
INTEGRITY_VISIBILITY_CAPABILITY_LEAKAGE = "capability_leakage"
INTEGRITY_VISIBILITY_RECOMMENDATION_SELECTION = "recommendation_ranking_scoring_selection"
INTEGRITY_VISIBILITY_MUTATION = "mutation"
INTEGRITY_VISIBILITY_MISSING_EVIDENCE = "missing_evidence"
INTEGRITY_VISIBILITY_UNSUPPORTED = "unsupported"
INTEGRITY_VISIBILITY_PROHIBITED = "prohibited"
INTEGRITY_VISIBILITY_UNKNOWN = "unknown"
INTEGRITY_VISIBILITY_GOVERNANCE = "governance"
INTEGRITY_VISIBILITY_INTEGRITY = "integrity"
INTEGRITY_VISIBILITY_CATEGORIES: tuple[str, ...] = (
    INTEGRITY_VISIBILITY_FAIL_VISIBLE,
    INTEGRITY_VISIBILITY_HIDDEN_BEHAVIOR,
    INTEGRITY_VISIBILITY_PROVENANCE,
    INTEGRITY_VISIBILITY_REPLAY,
    INTEGRITY_VISIBILITY_ROLLBACK,
    INTEGRITY_VISIBILITY_EXPLAINABILITY,
    INTEGRITY_VISIBILITY_CAPABILITY_LEAKAGE,
    INTEGRITY_VISIBILITY_RECOMMENDATION_SELECTION,
    INTEGRITY_VISIBILITY_MUTATION,
    INTEGRITY_VISIBILITY_MISSING_EVIDENCE,
    INTEGRITY_VISIBILITY_UNSUPPORTED,
    INTEGRITY_VISIBILITY_PROHIBITED,
    INTEGRITY_VISIBILITY_UNKNOWN,
    INTEGRITY_VISIBILITY_GOVERNANCE,
    INTEGRITY_VISIBILITY_INTEGRITY,
)

SUPPORTED_INTEGRITY_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_integrity_audit",
    "transition_integrity_visibility",
    "transition_integrity_evidence_reporting",
)
PROHIBITED_INTEGRITY_CAPABILITIES: tuple[str, ...] = (
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
INTEGRITY_CHOICE_PROHIBITED_CAPABILITIES: tuple[str, ...] = (
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
class TransitionIntegrityInput:
    input_id: str
    audit_id: str
    audit_domain: str
    required_domain_ids: tuple[str, ...]
    present_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    aggregation_report_id: str
    aggregation_hash: str
    requested_capabilities: tuple[str, ...] = ()
    warning_markers: tuple[str, ...] = ()
    violation_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_remediating_audit: bool = True

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
            "requested_capabilities",
            "warning_markers",
            "violation_markers",
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
class TransitionIntegrityFinding:
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
class TransitionIntegrityViolation:
    violation_id: str
    input_id: str
    violation_type: str
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
    remediation_enabled: bool = False
    repair_enabled: bool = False
    severity_score: int | None = None
    priority_rank: int | None = None


@dataclass(frozen=True)
class TransitionIntegrityContinuity:
    continuity_id: str
    input_id: str
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    evidence_continuity_ids: tuple[str, ...]
    deterministic_hash_reference: str
    replay_continuity_preserved: bool = True
    rollback_continuity_preserved: bool = True
    provenance_continuity_preserved: bool = True
    explainability_continuity_preserved: bool = True
    immutable_continuity: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "evidence_continuity_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionIntegrityVisibility:
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
    remediation_enabled: bool = False
    repair_enabled: bool = False
    priority_ranking_enabled: bool = False
    weighted_severity_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False


@dataclass(frozen=True)
class TransitionIntegrityEvidence:
    evidence_id: str
    input_id: str
    audit_id: str
    source_domain_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    violation_ids: tuple[str, ...]
    visibility_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_integrity_audit_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
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
            "violation_ids",
            "visibility_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionIntegritySummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    violation_type_counts: Mapping[str, int]
    visibility_category_counts: Mapping[str, int]
    integrity_satisfied_count: int
    integrity_warning_count: int
    integrity_failed_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    integrity_finding_count: int
    integrity_violation_count: int
    hidden_finding_violation_count: int
    hidden_risk_violation_count: int
    hidden_non_safe_state_violation_count: int
    missing_evidence_violation_count: int
    provenance_gap_count: int
    replay_gap_count: int
    rollback_gap_count: int
    explainability_gap_count: int
    aggregation_integrity_gap_count: int
    execution_boundary_leakage_count: int
    recommendation_leakage_count: int
    ranking_leakage_count: int
    scoring_leakage_count: int
    selection_leakage_count: int
    mutation_leakage_count: int
    visibility_gap_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))
        object.__setattr__(self, "violation_type_counts", dict(sorted(self.violation_type_counts.items())))
        object.__setattr__(self, "visibility_category_counts", dict(sorted(self.visibility_category_counts.items())))


@dataclass(frozen=True)
class TransitionIntegrityReport:
    report_id: str
    report_status: str
    source_aggregation_report_id: str
    source_aggregation_hash: str
    integrity_inputs: tuple[TransitionIntegrityInput, ...]
    findings: tuple[TransitionIntegrityFinding, ...]
    violations: tuple[TransitionIntegrityViolation, ...]
    evidence_records: tuple[TransitionIntegrityEvidence, ...]
    continuities: tuple[TransitionIntegrityContinuity, ...]
    visibilities: tuple[TransitionIntegrityVisibility, ...]
    summary: TransitionIntegritySummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_integrity_hash: str = ""
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
    weighted_severity_scoring_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "integrity_inputs",
            "findings",
            "violations",
            "evidence_records",
            "continuities",
            "visibilities",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_integrity_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_integrity_{input_id}_{finding_category}_{safe_marker}"


def transition_integrity_violation_id(input_id: str, violation_type: str) -> str:
    return f"v3_9_transition_integrity_{input_id}_violation_{violation_type}"


def export_transition_integrity_input(source: TransitionIntegrityInput) -> dict[str, Any]:
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
        "requested_capabilities",
        "warning_markers",
        "violation_markers",
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


def export_transition_integrity_finding(finding: TransitionIntegrityFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_integrity_violation(violation: TransitionIntegrityViolation) -> dict[str, Any]:
    return asdict(violation)


def export_transition_integrity_continuity(continuity: TransitionIntegrityContinuity) -> dict[str, Any]:
    data = asdict(continuity)
    for field_name in (
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "evidence_continuity_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_integrity_visibility(visibility: TransitionIntegrityVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_integrity_evidence(evidence: TransitionIntegrityEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "source_domain_ids",
        "evidence_ids",
        "finding_ids",
        "violation_ids",
        "visibility_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_integrity_summary(summary: TransitionIntegritySummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    data["violation_type_counts"] = dict(sorted(summary.violation_type_counts.items()))
    data["visibility_category_counts"] = dict(sorted(summary.visibility_category_counts.items()))
    return data


def export_transition_integrity_report(report: TransitionIntegrityReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_aggregation_report_id": report.source_aggregation_report_id,
        "source_aggregation_hash": report.source_aggregation_hash,
        "integrity_inputs": [
            export_transition_integrity_input(source)
            for source in sorted(report.integrity_inputs, key=lambda item: item.input_id)
        ],
        "findings": [
            export_transition_integrity_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "violations": [
            export_transition_integrity_violation(violation)
            for violation in sorted(report.violations, key=lambda item: (item.deterministic_order, item.violation_id))
        ],
        "evidence_records": [
            export_transition_integrity_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_integrity_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "visibilities": [
            export_transition_integrity_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: (item.deterministic_order, item.visibility_id))
        ],
        "summary": export_transition_integrity_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_integrity_hash": report.deterministic_integrity_hash,
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
        "weighted_severity_scoring_enabled": report.weighted_severity_scoring_enabled,
    }
