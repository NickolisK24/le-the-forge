"""Deterministic v3.9 closeout and v4.0 readiness audit models.

The closeout models are immutable evidence records. They do not execute,
route, schedule, dispatch, traverse, mutate, authorize, approve, remediate,
repair, optimize, recommend, rank, score, select, or create runtime behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from .transition_foundation_hashing import deterministic_hash
from .transition_foundation_serialization import stable_serialize


V3_9_CLOSEOUT_READY_FOR_V4_PLANNING = "closed_out_ready_for_v4_planning"
V3_9_CLOSEOUT_WITH_WARNINGS = "closed_out_with_warnings"
V3_9_NOT_READY_FOR_V4_PLANNING = "not_ready_for_v4_planning"
V3_9_CLOSEOUT_BLOCKED = "blocked"
V3_9_CLOSEOUT_INCOMPLETE = "incomplete"

V3_9_CLOSEOUT_CLASSIFICATIONS: tuple[str, ...] = (
    V3_9_CLOSEOUT_READY_FOR_V4_PLANNING,
    V3_9_CLOSEOUT_WITH_WARNINGS,
    V3_9_NOT_READY_FOR_V4_PLANNING,
    V3_9_CLOSEOUT_BLOCKED,
    V3_9_CLOSEOUT_INCOMPLETE,
)

V4_PLANNING_READY = "v4_planning_ready"
V4_PLANNING_READY_WITH_WARNINGS = "v4_planning_ready_with_warnings"
V4_PLANNING_NOT_READY = "v4_planning_not_ready"
V4_PLANNING_BLOCKED = "v4_planning_blocked"
V4_PLANNING_INCOMPLETE = "v4_planning_incomplete"

V4_READINESS_CLASSIFICATIONS: tuple[str, ...] = (
    V4_PLANNING_READY,
    V4_PLANNING_READY_WITH_WARNINGS,
    V4_PLANNING_NOT_READY,
    V4_PLANNING_BLOCKED,
    V4_PLANNING_INCOMPLETE,
)

FINDING_PHASE_EVIDENCE = "phase_evidence"
FINDING_GENERATED_REPORT = "generated_report"
FINDING_MIGRATION_DOC = "migration_doc"
FINDING_VALIDATION = "validation"
FINDING_DETERMINISTIC_GUARANTEE = "deterministic_guarantee"
FINDING_HIDDEN_BEHAVIOR = "hidden_behavior"
FINDING_CAPABILITY_LEAKAGE = "capability_leakage"
FINDING_NON_EXECUTION = "non_execution"
FINDING_NON_MUTATION = "non_mutation"
FINDING_NON_RRSS = "non_recommendation_ranking_scoring_selection"
FINDING_INTEGRITY = "integrity"
FINDING_CONTINUITY_CERTIFICATION = "continuity_certification"
FINDING_V4_READINESS = "v4_readiness"
FINDING_BLOCKER = "blocker"
FINDING_WARNING = "warning"
FINDING_INCOMPLETE_EVIDENCE = "incomplete_evidence"

V3_9_CLOSEOUT_FINDING_CATEGORIES: tuple[str, ...] = (
    FINDING_PHASE_EVIDENCE,
    FINDING_GENERATED_REPORT,
    FINDING_MIGRATION_DOC,
    FINDING_VALIDATION,
    FINDING_DETERMINISTIC_GUARANTEE,
    FINDING_HIDDEN_BEHAVIOR,
    FINDING_CAPABILITY_LEAKAGE,
    FINDING_NON_EXECUTION,
    FINDING_NON_MUTATION,
    FINDING_NON_RRSS,
    FINDING_INTEGRITY,
    FINDING_CONTINUITY_CERTIFICATION,
    FINDING_V4_READINESS,
    FINDING_BLOCKER,
    FINDING_WARNING,
    FINDING_INCOMPLETE_EVIDENCE,
)


@dataclass(frozen=True)
class V39PhaseCloseoutSpec:
    phase_id: str
    phase_name: str
    report_path: str
    migration_doc_path: str
    status_field: str
    expected_status: str
    required_count_fields: tuple[str, ...]


@dataclass(frozen=True)
class V39CloseoutReadinessInput:
    repo_root: Path
    phase_reports: Mapping[str, Mapping[str, Any] | None] | None = None
    migration_docs_present: Mapping[str, bool] | None = None
    governance_blockers: tuple[str, ...] = ()
    closeout_blockers: tuple[str, ...] = ()
    expected_fail_visible_warnings: bool = True


@dataclass(frozen=True)
class V39PhaseEvidenceRecord:
    phase_id: str
    phase_name: str
    report_path: str
    migration_doc_path: str
    report_present: bool
    migration_doc_present: bool
    report_is_json_object: bool
    phase_status: str
    expected_status: str
    phase_status_valid: bool
    deterministic_hash_present: bool
    classification_coverage_present: bool
    deterministic_serialization_verified: bool
    deterministic_hashing_verified: bool
    non_executable_verified: bool
    validation_error_count: int
    warning_count: int
    hidden_behavior_count: int
    hidden_finding_count: int
    hidden_risk_count: int
    hidden_non_safe_state_count: int
    execution_capability_enabled_count: int
    orchestration_capability_introduced_count: int
    recommendation_ranking_scoring_selection_capability_introduced_count: int
    authorization_approval_remediation_repair_capability_introduced_count: int
    runtime_mutation_capability_introduced_count: int
    deterministic_report_hash: str
    source_report_hash: str


@dataclass(frozen=True)
class V39CloseoutFinding:
    finding_id: str
    finding_category: str
    classification: str
    phase_id: str
    reason: str
    evidence_reference: str
    fail_visible: bool
    deterministic_order: int
    hidden: bool = False
    execution_enabled: bool = False
    orchestration_enabled: bool = False
    recommendation_enabled: bool = False
    ranking_enabled: bool = False
    scoring_enabled: bool = False
    selection_enabled: bool = False
    authorization_enabled: bool = False
    approval_enabled: bool = False
    remediation_enabled: bool = False
    repair_enabled: bool = False
    runtime_mutation_enabled: bool = False


@dataclass(frozen=True)
class V39CloseoutSummary:
    final_closeout_classification: str
    v4_readiness_classification: str
    phase_evidence_count: int
    generated_report_count: int
    migration_doc_count: int
    missing_report_count: int
    missing_doc_count: int
    validation_error_count: int
    blocker_count: int
    warning_count: int
    hidden_behavior_count: int
    hidden_finding_count: int
    hidden_risk_count: int
    hidden_non_safe_state_count: int
    execution_capability_enabled_count: int
    orchestration_capability_introduced_count: int
    recommendation_ranking_scoring_selection_capability_introduced_count: int
    authorization_approval_remediation_repair_capability_introduced_count: int
    runtime_mutation_capability_introduced_count: int
    integrity_enforcement_status: str
    continuity_certification_status: str
    deterministic_summary_hash: str


@dataclass(frozen=True)
class V39CloseoutReadinessReport:
    closeout_input: V39CloseoutReadinessInput
    phase_evidence: tuple[V39PhaseEvidenceRecord, ...]
    findings: tuple[V39CloseoutFinding, ...]
    summary: V39CloseoutSummary
    deterministic_report_hash: str
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
    remediation_enabled: bool = False
    repair_enabled: bool = False
    silent_correction_enabled: bool = False
    hidden_fallback_enabled: bool = False
    v4_runtime_behavior_enabled: bool = False


def classify_v3_9_closeout(candidate_classifications: tuple[str, ...] | list[str]) -> str:
    candidates = set(candidate_classifications)
    if V3_9_CLOSEOUT_INCOMPLETE in candidates:
        return V3_9_CLOSEOUT_INCOMPLETE
    if V3_9_CLOSEOUT_BLOCKED in candidates:
        return V3_9_CLOSEOUT_BLOCKED
    if V3_9_NOT_READY_FOR_V4_PLANNING in candidates:
        return V3_9_NOT_READY_FOR_V4_PLANNING
    if V3_9_CLOSEOUT_WITH_WARNINGS in candidates:
        return V3_9_CLOSEOUT_WITH_WARNINGS
    return V3_9_CLOSEOUT_READY_FOR_V4_PLANNING


def classify_v4_readiness(closeout_classification: str) -> str:
    if closeout_classification == V3_9_CLOSEOUT_READY_FOR_V4_PLANNING:
        return V4_PLANNING_READY
    if closeout_classification == V3_9_CLOSEOUT_WITH_WARNINGS:
        return V4_PLANNING_READY_WITH_WARNINGS
    if closeout_classification == V3_9_CLOSEOUT_BLOCKED:
        return V4_PLANNING_BLOCKED
    if closeout_classification == V3_9_CLOSEOUT_INCOMPLETE:
        return V4_PLANNING_INCOMPLETE
    return V4_PLANNING_NOT_READY


def transition_closeout_finding_id(phase_id: str, finding_category: str) -> str:
    return f"v3_9_closeout_{phase_id}_{finding_category}"


def export_v3_9_phase_evidence_record(record: V39PhaseEvidenceRecord) -> dict[str, Any]:
    return asdict(record)


def export_v3_9_closeout_finding(finding: V39CloseoutFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_9_closeout_readiness_report(report: V39CloseoutReadinessReport) -> dict[str, Any]:
    data = asdict(report)
    data["closeout_input"]["repo_root"] = str(report.closeout_input.repo_root)
    data["phase_evidence"] = [
        export_v3_9_phase_evidence_record(record)
        for record in sorted(report.phase_evidence, key=lambda item: item.phase_id)
    ]
    data["findings"] = [
        export_v3_9_closeout_finding(finding)
        for finding in sorted(report.findings, key=lambda item: item.deterministic_order)
    ]
    data["deterministic_report_hash"] = hash_v3_9_closeout_readiness_report(report)
    return data


def serialize_v3_9_closeout_readiness_report(report: V39CloseoutReadinessReport) -> str:
    return stable_serialize(export_v3_9_closeout_readiness_report(report))


def hash_v3_9_closeout_readiness_report(report: V39CloseoutReadinessReport) -> str:
    payload = asdict(report)
    payload["closeout_input"]["repo_root"] = str(report.closeout_input.repo_root)
    payload["phase_evidence"] = [
        export_v3_9_phase_evidence_record(record)
        for record in sorted(report.phase_evidence, key=lambda item: item.phase_id)
    ]
    payload["findings"] = [
        export_v3_9_closeout_finding(finding)
        for finding in sorted(report.findings, key=lambda item: item.deterministic_order)
    ]
    payload.pop("deterministic_report_hash", None)
    return deterministic_hash(payload)
