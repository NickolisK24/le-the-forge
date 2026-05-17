"""Deterministic v3.9 transition scenario intelligence models.

These models describe hypothetical transition scenarios from immutable session
evidence. They do not execute, route, schedule, dispatch, traverse, authorize,
approve, mutate, optimize, recommend, rank, score, select, or expose callable
orchestration behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .transition_foundation_serialization import sorted_entries


V3_9_TRANSITION_SCENARIO_PHASE_ID = "v3_9_transition_scenario_intelligence"
V3_9_TRANSITION_SCENARIO_SCHEMA_VERSION = "v3_9.transition_scenario_intelligence.1"
V3_9_TRANSITION_SCENARIO_REPORT_STABLE = "v3_9_transition_scenario_intelligence_stable"
V3_9_TRANSITION_SCENARIO_REPORT_BLOCKED = "v3_9_transition_scenario_intelligence_blocked"

SCENARIO_CLASSIFICATION_MODELED = "modeled"
SCENARIO_CLASSIFICATION_PARTIALLY_MODELED = "partially_modeled"
SCENARIO_CLASSIFICATION_UNMODELED = "unmodeled"
SCENARIO_CLASSIFICATION_BLOCKED = "blocked"
SCENARIO_CLASSIFICATION_UNSUPPORTED = "unsupported"
SCENARIO_CLASSIFICATION_PROHIBITED = "prohibited"
SCENARIO_CLASSIFICATION_UNKNOWN = "unknown"
SCENARIO_CLASSIFICATION_INCOMPLETE = "incomplete"
SCENARIO_CLASSIFICATIONS: tuple[str, ...] = (
    SCENARIO_CLASSIFICATION_MODELED,
    SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
    SCENARIO_CLASSIFICATION_UNMODELED,
    SCENARIO_CLASSIFICATION_BLOCKED,
    SCENARIO_CLASSIFICATION_UNSUPPORTED,
    SCENARIO_CLASSIFICATION_PROHIBITED,
    SCENARIO_CLASSIFICATION_UNKNOWN,
    SCENARIO_CLASSIFICATION_INCOMPLETE,
)
NON_MODELED_SCENARIO_CLASSIFICATIONS: tuple[str, ...] = (
    SCENARIO_CLASSIFICATION_PARTIALLY_MODELED,
    SCENARIO_CLASSIFICATION_UNMODELED,
    SCENARIO_CLASSIFICATION_BLOCKED,
    SCENARIO_CLASSIFICATION_UNSUPPORTED,
    SCENARIO_CLASSIFICATION_PROHIBITED,
    SCENARIO_CLASSIFICATION_UNKNOWN,
    SCENARIO_CLASSIFICATION_INCOMPLETE,
)

SCENARIO_FINDING_SESSION_EVIDENCE = "session_evidence"
SCENARIO_FINDING_VARIANT = "scenario_variant"
SCENARIO_FINDING_COMPARISON = "scenario_comparison"
SCENARIO_FINDING_RISK_VISIBILITY = "risk_visibility"
SCENARIO_FINDING_CONTINUITY = "continuity"
SCENARIO_FINDING_PROVENANCE = "provenance"
SCENARIO_FINDING_EXPLAINABILITY = "explainability"
SCENARIO_FINDING_GOVERNANCE = "governance"
SCENARIO_FINDING_INTEGRITY = "integrity"
SCENARIO_FINDING_UNSUPPORTED = "unsupported"
SCENARIO_FINDING_PROHIBITED = "prohibited"
SCENARIO_FINDING_MISSING_EVIDENCE = "missing_evidence"
SCENARIO_FINDING_UNCERTAINTY = "uncertainty"
SCENARIO_FINDING_CATEGORIES: tuple[str, ...] = (
    SCENARIO_FINDING_SESSION_EVIDENCE,
    SCENARIO_FINDING_VARIANT,
    SCENARIO_FINDING_COMPARISON,
    SCENARIO_FINDING_RISK_VISIBILITY,
    SCENARIO_FINDING_CONTINUITY,
    SCENARIO_FINDING_PROVENANCE,
    SCENARIO_FINDING_EXPLAINABILITY,
    SCENARIO_FINDING_GOVERNANCE,
    SCENARIO_FINDING_INTEGRITY,
    SCENARIO_FINDING_UNSUPPORTED,
    SCENARIO_FINDING_PROHIBITED,
    SCENARIO_FINDING_MISSING_EVIDENCE,
    SCENARIO_FINDING_UNCERTAINTY,
)

SCENARIO_RISK_PROVENANCE = "provenance"
SCENARIO_RISK_CONTINUITY = "continuity"
SCENARIO_RISK_EXPLAINABILITY = "explainability"
SCENARIO_RISK_UNSUPPORTED_DOMAIN = "unsupported_domain"
SCENARIO_RISK_PROHIBITED_CAPABILITY = "prohibited_capability"
SCENARIO_RISK_MISSING_EVIDENCE = "missing_evidence"
SCENARIO_RISK_UNCERTAINTY = "uncertainty"
SCENARIO_RISK_GOVERNANCE = "governance"
SCENARIO_RISK_INTEGRITY = "integrity"
SCENARIO_RISK_CATEGORIES: tuple[str, ...] = (
    SCENARIO_RISK_PROVENANCE,
    SCENARIO_RISK_CONTINUITY,
    SCENARIO_RISK_EXPLAINABILITY,
    SCENARIO_RISK_UNSUPPORTED_DOMAIN,
    SCENARIO_RISK_PROHIBITED_CAPABILITY,
    SCENARIO_RISK_MISSING_EVIDENCE,
    SCENARIO_RISK_UNCERTAINTY,
    SCENARIO_RISK_GOVERNANCE,
    SCENARIO_RISK_INTEGRITY,
)

SCENARIO_COMPARISON_MATCHING_EVIDENCE = "matching_evidence"
SCENARIO_COMPARISON_DIFFERING_EVIDENCE = "differing_evidence"
SCENARIO_COMPARISON_MISSING_EVIDENCE = "missing_evidence"
SCENARIO_COMPARISON_CONTINUITY_DIFFERENCE = "continuity_difference"
SCENARIO_COMPARISON_PROVENANCE_DIFFERENCE = "provenance_difference"
SCENARIO_COMPARISON_EXPLAINABILITY_DIFFERENCE = "explainability_difference"
SCENARIO_COMPARISON_RISK_DIFFERENCE = "risk_difference"
SCENARIO_COMPARISON_CLASSIFICATION_DIFFERENCE = "classification_difference"
SCENARIO_COMPARISON_CATEGORIES: tuple[str, ...] = (
    SCENARIO_COMPARISON_MATCHING_EVIDENCE,
    SCENARIO_COMPARISON_DIFFERING_EVIDENCE,
    SCENARIO_COMPARISON_MISSING_EVIDENCE,
    SCENARIO_COMPARISON_CONTINUITY_DIFFERENCE,
    SCENARIO_COMPARISON_PROVENANCE_DIFFERENCE,
    SCENARIO_COMPARISON_EXPLAINABILITY_DIFFERENCE,
    SCENARIO_COMPARISON_RISK_DIFFERENCE,
    SCENARIO_COMPARISON_CLASSIFICATION_DIFFERENCE,
)

SCENARIO_VISIBILITY_VISIBLE = "visible"
SCENARIO_VISIBILITY_FAIL_VISIBLE = "fail_visible"
SCENARIO_SEVERITY_INFO = "info"
SCENARIO_SEVERITY_WARNING = "warning"
SCENARIO_SEVERITY_BLOCKED = "blocked"

SUPPORTED_SCENARIO_CAPABILITIES: tuple[str, ...] = (
    "deterministic_transition_scenario_modeling",
    "transition_session_reference",
    "scenario_variant_reference",
    "scenario_comparison_evidence",
    "scenario_risk_visibility",
    "transition_provenance_reference",
    "transition_continuity_reference",
    "transition_explainability_reference",
)
PROHIBITED_SCENARIO_CAPABILITIES: tuple[str, ...] = (
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
)
SCENARIO_CHOICE_PROHIBITED_CAPABILITIES: tuple[str, ...] = (
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
class TransitionScenarioInput:
    input_id: str
    scenario_id: str
    scenario_domain: str
    session_evidence_ids: tuple[str, ...]
    scenario_variant_ids: tuple[str, ...]
    modeled_variant_ids: tuple[str, ...]
    variant_evidence_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    replay_continuity_ids: tuple[str, ...]
    rollback_continuity_ids: tuple[str, ...]
    provenance_continuity_ids: tuple[str, ...]
    explainability_continuity_ids: tuple[str, ...]
    requested_capabilities: tuple[str, ...] = ()
    comparison_variant_pairs: tuple[str, ...] = ()
    partial_success_markers: tuple[str, ...] = ()
    partial_failure_markers: tuple[str, ...] = ()
    unmodeled_markers: tuple[str, ...] = ()
    incomplete_markers: tuple[str, ...] = ()
    blocked_markers: tuple[str, ...] = ()
    unsupported_markers: tuple[str, ...] = ()
    prohibited_markers: tuple[str, ...] = ()
    unknown_markers: tuple[str, ...] = ()
    governance_policy_ids: tuple[str, ...] = ()
    integrity_policy_ids: tuple[str, ...] = ()
    explainability_context: str = ""
    non_executable_scenario: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "session_evidence_ids",
            "scenario_variant_ids",
            "modeled_variant_ids",
            "variant_evidence_ids",
            "provenance_reference_ids",
            "replay_continuity_ids",
            "rollback_continuity_ids",
            "provenance_continuity_ids",
            "explainability_continuity_ids",
            "requested_capabilities",
            "comparison_variant_pairs",
            "partial_success_markers",
            "partial_failure_markers",
            "unmodeled_markers",
            "incomplete_markers",
            "blocked_markers",
            "unsupported_markers",
            "prohibited_markers",
            "unknown_markers",
            "governance_policy_ids",
            "integrity_policy_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionScenarioVariant:
    variant_id: str
    input_id: str
    variant_label: str
    classification: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_reference: str
    deterministic_order: int
    deterministic_evidence_available: bool = True
    modeled: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    immutable_variant: bool = True
    hidden: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False


@dataclass(frozen=True)
class TransitionScenarioRisk:
    risk_id: str
    input_id: str
    risk_category: str
    classification: str
    description: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    descriptive_only: bool = True
    score_assigned: bool = False
    ranking_assigned: bool = False
    recommendation_made: bool = False
    selection_made: bool = False
    execution_boundary_violation_detected: bool = False
    recommendation_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionScenarioComparison:
    comparison_id: str
    input_id: str
    left_variant_id: str
    right_variant_id: str
    comparison_category: str
    matching_evidence: tuple[str, ...]
    differing_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    continuity_differences: tuple[str, ...]
    provenance_differences: tuple[str, ...]
    explainability_differences: tuple[str, ...]
    risk_differences: tuple[str, ...]
    classification_differences: tuple[str, ...]
    deterministic_order: int
    descriptive_only: bool = True
    winner_selected: bool = False
    recommendation_made: bool = False
    ranking_assigned: bool = False
    scoring_assigned: bool = False
    selection_made: bool = False
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "matching_evidence",
            "differing_evidence",
            "missing_evidence",
            "continuity_differences",
            "provenance_differences",
            "explainability_differences",
            "risk_differences",
            "classification_differences",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionScenarioFinding:
    finding_id: str
    input_id: str
    finding_category: str
    classification: str
    severity: str
    reason: str
    evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    deterministic_order: int
    fail_visible: bool = True
    hidden: bool = False
    execution_boundary_violation_detected: bool = False
    recommendation_boundary_violation_detected: bool = False
    non_execution_confirmation: bool = True
    no_recommendation_confirmation: bool = True
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True


@dataclass(frozen=True)
class TransitionScenarioEvidence:
    evidence_id: str
    input_id: str
    scenario_id: str
    session_evidence_ids: tuple[str, ...]
    variant_ids: tuple[str, ...]
    comparison_ids: tuple[str, ...]
    risk_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    deterministic_hash_reference: str
    evidence_scope: str = "transition_scenario_evidence_record_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    explainability_safe: bool = True
    non_executable: bool = True
    execution_behavior_enabled: bool = False
    recommendation_behavior_enabled: bool = False
    ranking_behavior_enabled: bool = False
    scoring_behavior_enabled: bool = False
    selection_behavior_enabled: bool = False
    runtime_mutation_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "session_evidence_ids",
            "variant_ids",
            "comparison_ids",
            "risk_ids",
            "finding_ids",
            "provenance_reference_ids",
            "continuity_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class TransitionScenarioContinuity:
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
class TransitionScenarioVisibility:
    visibility_id: str
    input_id: str
    classification: str
    visibility_status: str
    reason: str
    deterministic_evidence_reference: str
    provenance_reference: str
    continuity_reference: str
    explainability_message: str
    fail_visible: bool = True
    hidden: bool = False
    scenario_state_visible: bool = True


@dataclass(frozen=True)
class TransitionScenarioRecord:
    record_id: str
    input_id: str
    scenario_id: str
    classification: str
    variants: tuple[TransitionScenarioVariant, ...]
    comparisons: tuple[TransitionScenarioComparison, ...]
    risks: tuple[TransitionScenarioRisk, ...]
    findings: tuple[TransitionScenarioFinding, ...]
    evidence: TransitionScenarioEvidence
    continuity: TransitionScenarioContinuity
    visibility: TransitionScenarioVisibility
    deterministic_order: int
    immutable_record: bool = True
    non_executable: bool = True
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("variants", "comparisons", "risks", "findings"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


@dataclass(frozen=True)
class TransitionScenarioSummary:
    summary_id: str
    classification_counts: Mapping[str, int]
    finding_category_counts: Mapping[str, int]
    risk_category_counts: Mapping[str, int]
    modeled_count: int
    partially_modeled_count: int
    unmodeled_count: int
    blocked_count: int
    unsupported_count: int
    prohibited_count: int
    unknown_count: int
    incomplete_count: int
    scenario_finding_count: int
    scenario_variant_count: int
    scenario_comparison_count: int
    scenario_risk_count: int
    governance_risk_count: int
    uncertainty_risk_count: int
    missing_evidence_risk_count: int
    hidden_scenario_finding_count: int
    hidden_risk_count: int
    execution_boundary_violation_count: int
    recommendation_ranking_scoring_selection_violation_count: int
    deterministic_summary_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "classification_counts", dict(sorted(self.classification_counts.items())))
        object.__setattr__(self, "finding_category_counts", dict(sorted(self.finding_category_counts.items())))
        object.__setattr__(self, "risk_category_counts", dict(sorted(self.risk_category_counts.items())))


@dataclass(frozen=True)
class TransitionScenarioReport:
    report_id: str
    report_status: str
    source_foundation_id: str
    source_boundary_report_id: str
    source_compatibility_report_id: str
    source_evaluation_report_id: str
    source_session_report_id: str
    scenario_inputs: tuple[TransitionScenarioInput, ...]
    scenario_records: tuple[TransitionScenarioRecord, ...]
    variants: tuple[TransitionScenarioVariant, ...]
    comparisons: tuple[TransitionScenarioComparison, ...]
    risks: tuple[TransitionScenarioRisk, ...]
    findings: tuple[TransitionScenarioFinding, ...]
    evidence_records: tuple[TransitionScenarioEvidence, ...]
    continuities: tuple[TransitionScenarioContinuity, ...]
    visibilities: tuple[TransitionScenarioVisibility, ...]
    summary: TransitionScenarioSummary
    validation_totals: Mapping[str, int | bool | str]
    deterministic_scenario_hash: str = ""
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
    hidden_fallback_enabled: bool = False
    silent_correction_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "scenario_inputs",
            "scenario_records",
            "variants",
            "comparisons",
            "risks",
            "findings",
            "evidence_records",
            "continuities",
            "visibilities",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))
        object.__setattr__(self, "validation_totals", dict(sorted(self.validation_totals.items())))


def transition_scenario_finding_id(input_id: str, finding_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_scenario_{input_id}_{finding_category}_{safe_marker}"


def transition_scenario_risk_id(input_id: str, risk_category: str, marker: str) -> str:
    safe_marker = "".join(character if character.isalnum() else "_" for character in marker.lower())
    return f"v3_9_transition_scenario_{input_id}_risk_{risk_category}_{safe_marker}"


def export_transition_scenario_input(source: TransitionScenarioInput) -> dict[str, Any]:
    data = asdict(source)
    for field_name in (
        "session_evidence_ids",
        "scenario_variant_ids",
        "modeled_variant_ids",
        "variant_evidence_ids",
        "provenance_reference_ids",
        "replay_continuity_ids",
        "rollback_continuity_ids",
        "provenance_continuity_ids",
        "explainability_continuity_ids",
        "requested_capabilities",
        "comparison_variant_pairs",
        "partial_success_markers",
        "partial_failure_markers",
        "unmodeled_markers",
        "incomplete_markers",
        "blocked_markers",
        "unsupported_markers",
        "prohibited_markers",
        "unknown_markers",
        "governance_policy_ids",
        "integrity_policy_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_scenario_variant(variant: TransitionScenarioVariant) -> dict[str, Any]:
    return asdict(variant)


def export_transition_scenario_risk(risk: TransitionScenarioRisk) -> dict[str, Any]:
    return asdict(risk)


def export_transition_scenario_comparison(comparison: TransitionScenarioComparison) -> dict[str, Any]:
    data = asdict(comparison)
    for field_name in (
        "matching_evidence",
        "differing_evidence",
        "missing_evidence",
        "continuity_differences",
        "provenance_differences",
        "explainability_differences",
        "risk_differences",
        "classification_differences",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_scenario_finding(finding: TransitionScenarioFinding) -> dict[str, Any]:
    return asdict(finding)


def export_transition_scenario_evidence(evidence: TransitionScenarioEvidence) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "session_evidence_ids",
        "variant_ids",
        "comparison_ids",
        "risk_ids",
        "finding_ids",
        "provenance_reference_ids",
        "continuity_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_transition_scenario_continuity(continuity: TransitionScenarioContinuity) -> dict[str, Any]:
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


def export_transition_scenario_visibility(visibility: TransitionScenarioVisibility) -> dict[str, Any]:
    return asdict(visibility)


def export_transition_scenario_record(record: TransitionScenarioRecord) -> dict[str, Any]:
    return {
        "record_id": record.record_id,
        "input_id": record.input_id,
        "scenario_id": record.scenario_id,
        "classification": record.classification,
        "variants": [
            export_transition_scenario_variant(variant)
            for variant in sorted(record.variants, key=lambda item: (item.deterministic_order, item.variant_id))
        ],
        "comparisons": [
            export_transition_scenario_comparison(comparison)
            for comparison in sorted(record.comparisons, key=lambda item: (item.deterministic_order, item.comparison_id))
        ],
        "risks": [
            export_transition_scenario_risk(risk)
            for risk in sorted(record.risks, key=lambda item: (item.deterministic_order, item.risk_id))
        ],
        "findings": [
            export_transition_scenario_finding(finding)
            for finding in sorted(record.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "evidence": export_transition_scenario_evidence(record.evidence),
        "continuity": export_transition_scenario_continuity(record.continuity),
        "visibility": export_transition_scenario_visibility(record.visibility),
        "deterministic_order": record.deterministic_order,
        "immutable_record": record.immutable_record,
        "non_executable": record.non_executable,
        "recommendation_enabled": record.recommendation_enabled,
        "ranking_enabled": record.ranking_enabled,
        "scoring_enabled": record.scoring_enabled,
        "selection_enabled": record.selection_enabled,
    }


def export_transition_scenario_summary(summary: TransitionScenarioSummary) -> dict[str, Any]:
    data = asdict(summary)
    data["classification_counts"] = dict(sorted(summary.classification_counts.items()))
    data["finding_category_counts"] = dict(sorted(summary.finding_category_counts.items()))
    data["risk_category_counts"] = dict(sorted(summary.risk_category_counts.items()))
    return data


def export_transition_scenario_report(report: TransitionScenarioReport) -> dict[str, Any]:
    return {
        "report_id": report.report_id,
        "report_status": report.report_status,
        "source_foundation_id": report.source_foundation_id,
        "source_boundary_report_id": report.source_boundary_report_id,
        "source_compatibility_report_id": report.source_compatibility_report_id,
        "source_evaluation_report_id": report.source_evaluation_report_id,
        "source_session_report_id": report.source_session_report_id,
        "scenario_inputs": [
            export_transition_scenario_input(source)
            for source in sorted(report.scenario_inputs, key=lambda item: item.input_id)
        ],
        "scenario_records": [
            export_transition_scenario_record(record)
            for record in sorted(report.scenario_records, key=lambda item: (item.deterministic_order, item.record_id))
        ],
        "variants": [
            export_transition_scenario_variant(variant)
            for variant in sorted(report.variants, key=lambda item: (item.deterministic_order, item.variant_id))
        ],
        "comparisons": [
            export_transition_scenario_comparison(comparison)
            for comparison in sorted(report.comparisons, key=lambda item: (item.deterministic_order, item.comparison_id))
        ],
        "risks": [
            export_transition_scenario_risk(risk)
            for risk in sorted(report.risks, key=lambda item: (item.deterministic_order, item.risk_id))
        ],
        "findings": [
            export_transition_scenario_finding(finding)
            for finding in sorted(report.findings, key=lambda item: (item.deterministic_order, item.finding_id))
        ],
        "evidence_records": [
            export_transition_scenario_evidence(evidence)
            for evidence in sorted(report.evidence_records, key=lambda item: item.evidence_id)
        ],
        "continuities": [
            export_transition_scenario_continuity(continuity)
            for continuity in sorted(report.continuities, key=lambda item: item.continuity_id)
        ],
        "visibilities": [
            export_transition_scenario_visibility(visibility)
            for visibility in sorted(report.visibilities, key=lambda item: item.visibility_id)
        ],
        "summary": export_transition_scenario_summary(report.summary),
        "validation_totals": dict(sorted(report.validation_totals.items())),
        "deterministic_scenario_hash": report.deterministic_scenario_hash,
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
        "hidden_fallback_enabled": report.hidden_fallback_enabled,
        "silent_correction_enabled": report.silent_correction_enabled,
    }
