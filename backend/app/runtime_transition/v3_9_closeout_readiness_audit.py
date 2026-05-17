"""Artifact-only v3.9 closeout and v4.0 readiness audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .transition_foundation_hashing import deterministic_hash
from .v3_9_closeout_readiness_models import (
    FINDING_BLOCKER,
    FINDING_CAPABILITY_LEAKAGE,
    FINDING_CONTINUITY_CERTIFICATION,
    FINDING_DETERMINISTIC_GUARANTEE,
    FINDING_GENERATED_REPORT,
    FINDING_HIDDEN_BEHAVIOR,
    FINDING_INCOMPLETE_EVIDENCE,
    FINDING_INTEGRITY,
    FINDING_MIGRATION_DOC,
    FINDING_NON_EXECUTION,
    FINDING_NON_MUTATION,
    FINDING_NON_RRSS,
    FINDING_PHASE_EVIDENCE,
    FINDING_V4_READINESS,
    FINDING_VALIDATION,
    FINDING_WARNING,
    V3_9_CLOSEOUT_BLOCKED,
    V3_9_CLOSEOUT_INCOMPLETE,
    V3_9_CLOSEOUT_READY_FOR_V4_PLANNING,
    V3_9_CLOSEOUT_WITH_WARNINGS,
    V3_9_NOT_READY_FOR_V4_PLANNING,
    V39CloseoutFinding,
    V39CloseoutReadinessInput,
    V39CloseoutReadinessReport,
    V39CloseoutSummary,
    V39PhaseCloseoutSpec,
    V39PhaseEvidenceRecord,
    classify_v3_9_closeout,
    classify_v4_readiness,
    hash_v3_9_closeout_readiness_report,
    transition_closeout_finding_id,
)


V3_9_PHASE_SPECS: tuple[V39PhaseCloseoutSpec, ...] = (
    V39PhaseCloseoutSpec(
        "phase_1_foundations",
        "transition foundations",
        "docs/generated/v3_9_transition_foundations_report.json",
        "docs/migration/V3_9_TRANSITION_FOUNDATIONS.md",
        "foundation_status",
        "v3_9_transition_foundation_stable",
        (
            "supported_state_count",
            "unsupported_state_count",
            "prohibited_state_count",
            "unknown_state_count",
            "incomplete_state_count",
            "blocked_state_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_2_boundary",
        "transition boundary intelligence",
        "docs/generated/v3_9_transition_boundary_intelligence_report.json",
        "docs/migration/V3_9_TRANSITION_BOUNDARY_INTELLIGENCE.md",
        "boundary_report_status",
        "v3_9_transition_boundary_intelligence_stable",
        (
            "safe_transition_count",
            "unsupported_behavior_detection_count",
            "prohibited_behavior_detection_count",
            "unknown_behavior_detection_count",
            "incomplete_behavior_detection_count",
            "blocked_behavior_detection_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_3_compatibility",
        "transition compatibility intelligence",
        "docs/generated/v3_9_transition_compatibility_intelligence_report.json",
        "docs/migration/V3_9_TRANSITION_COMPATIBILITY_INTELLIGENCE.md",
        "compatibility_report_status",
        "v3_9_transition_compatibility_intelligence_stable",
        (
            "compatible_count",
            "incompatible_count",
            "partially_compatible_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_4_evaluation",
        "transition evaluation intelligence",
        "docs/generated/v3_9_transition_evaluation_intelligence_report.json",
        "docs/migration/V3_9_TRANSITION_EVALUATION_INTELLIGENCE.md",
        "evaluation_report_status",
        "v3_9_transition_evaluation_intelligence_stable",
        (
            "successful_count",
            "partially_successful_count",
            "unsuccessful_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
            "blocked_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_5_session",
        "transition session intelligence",
        "docs/generated/v3_9_transition_session_intelligence_report.json",
        "docs/migration/V3_9_TRANSITION_SESSION_INTELLIGENCE.md",
        "session_report_status",
        "v3_9_transition_session_intelligence_stable",
        (
            "complete_count",
            "partially_complete_count",
            "incomplete_count",
            "blocked_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_6_scenario",
        "transition scenario intelligence",
        "docs/generated/v3_9_transition_scenario_intelligence_report.json",
        "docs/migration/V3_9_TRANSITION_SCENARIO_INTELLIGENCE.md",
        "scenario_report_status",
        "v3_9_transition_scenario_intelligence_stable",
        (
            "modeled_count",
            "partially_modeled_count",
            "unmodeled_count",
            "blocked_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_7_aggregation",
        "transition intelligence aggregation",
        "docs/generated/v3_9_transition_intelligence_aggregation_report.json",
        "docs/migration/V3_9_TRANSITION_INTELLIGENCE_AGGREGATION.md",
        "aggregation_report_status",
        "v3_9_transition_intelligence_aggregation_stable",
        (
            "aggregated_count",
            "partially_aggregated_count",
            "unaggregated_count",
            "blocked_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_8_integrity",
        "transition integrity enforcement",
        "docs/generated/v3_9_transition_integrity_enforcement_report.json",
        "docs/migration/V3_9_TRANSITION_INTEGRITY_ENFORCEMENT.md",
        "integrity_report_status",
        "v3_9_transition_integrity_enforcement_stable",
        (
            "integrity_satisfied_count",
            "integrity_warning_count",
            "integrity_failed_count",
            "blocked_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
        ),
    ),
    V39PhaseCloseoutSpec(
        "phase_9_certification",
        "transition continuity certification",
        "docs/generated/v3_9_transition_continuity_certification_report.json",
        "docs/migration/V3_9_TRANSITION_CONTINUITY_CERTIFICATION.md",
        "certification_report_status",
        "v3_9_transition_continuity_certification_stable",
        (
            "certified_count",
            "certified_with_warnings_count",
            "not_certified_count",
            "blocked_count",
            "unsupported_count",
            "prohibited_count",
            "unknown_count",
            "incomplete_count",
        ),
    ),
)

EXECUTION_CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "transition_execution_enabled",
        "coordination_transition_execution_enabled",
        "graph_execution_enabled",
        "graph_traversal_enabled",
        "orchestration_traversal_enabled",
        "routing_enabled",
        "scheduling_enabled",
        "dispatch_enabled",
        "dispatch_pipeline_enabled",
        "runtime_orchestration_engine_enabled",
        "transition_execution_handler_enabled",
        "callable_orchestration_flow_enabled",
        "production_execution_pathway_enabled",
        "runtime_state_machine_enabled",
    }
)

ORCHESTRATION_CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "orchestration_execution_enabled",
        "orchestration_traversal_enabled",
        "runtime_orchestration_engine_enabled",
        "orchestration_evaluator_enabled",
        "callable_orchestration_flow_enabled",
        "transition_execution_handler_enabled",
        "runtime_state_machine_enabled",
        "routing_enabled",
        "scheduling_enabled",
        "dispatch_enabled",
    }
)

RRSS_CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "recommendation_enabled",
        "recommendation_behavior_enabled",
        "ranking_enabled",
        "ranking_behavior_enabled",
        "scoring_enabled",
        "scoring_behavior_enabled",
        "selection_enabled",
        "selection_behavior_enabled",
        "optimization_enabled",
        "prioritization_enabled",
        "weighted_scoring_enabled",
    }
)

APPROVAL_REMEDIATION_REPAIR_KEYS: frozenset[str] = frozenset(
    {
        "authorization_enabled",
        "approval_enabled",
        "implicit_transition_approval_enabled",
        "remediation_enabled",
        "repair_enabled",
        "automatic_remediation_enabled",
        "automatic_repair_enabled",
        "silent_correction_enabled",
        "hidden_correction_enabled",
        "hidden_fallback_enabled",
        "silent_fallback_enabled",
    }
)

MUTATION_CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "runtime_mutation_enabled",
        "mutation_behavior_enabled",
        "persistent_mutation_enabled",
        "state_write_enabled",
        "hidden_mutation_enabled",
    }
)

WARNING_COUNT_KEYS: tuple[str, ...] = (
    "hidden_finding_count",
    "hidden_risk_count",
    "hidden_non_safe_state_count",
    "hidden_behavior_count",
    "hidden_conflict_count",
    "hidden_scenario_finding_count",
    "hidden_session_finding_count",
    "hidden_aggregation_finding_count",
    "hidden_visibility_count",
    "hidden_finding_violation_count",
    "hidden_risk_violation_count",
    "hidden_non_safe_state_violation_count",
    "execution_boundary_leakage_count",
    "recommendation_leakage_count",
    "ranking_leakage_count",
    "scoring_leakage_count",
    "selection_leakage_count",
    "mutation_leakage_count",
)


def default_v3_9_closeout_readiness_input(repo_root: Path | None = None) -> V39CloseoutReadinessInput:
    return V39CloseoutReadinessInput(repo_root=repo_root or Path(__file__).resolve().parents[3])


def audit_v3_9_closeout_readiness(
    closeout_input: V39CloseoutReadinessInput | None = None,
) -> V39CloseoutReadinessReport:
    source = closeout_input or default_v3_9_closeout_readiness_input()
    phase_evidence = tuple(_audit_phase(source, spec) for spec in V3_9_PHASE_SPECS)
    findings = _build_findings(source, phase_evidence)
    candidates = _candidate_classifications(source, phase_evidence)
    final_classification = classify_v3_9_closeout(candidates)
    v4_classification = classify_v4_readiness(final_classification)
    summary = _build_summary(final_classification, v4_classification, phase_evidence, findings)
    placeholder = V39CloseoutReadinessReport(
        closeout_input=source,
        phase_evidence=phase_evidence,
        findings=findings,
        summary=summary,
        deterministic_report_hash="pending",
    )
    return V39CloseoutReadinessReport(
        closeout_input=source,
        phase_evidence=phase_evidence,
        findings=findings,
        summary=summary,
        deterministic_report_hash=hash_v3_9_closeout_readiness_report(placeholder),
    )


def _audit_phase(source: V39CloseoutReadinessInput, spec: V39PhaseCloseoutSpec) -> V39PhaseEvidenceRecord:
    report = _load_report(source, spec)
    summary = _summary_block(report)
    status = _status_value(report, summary, spec.status_field)
    deterministic_report_hash = _deterministic_report_hash(report)
    deterministic_serialization_verified = bool(summary.get("deterministic_serialization_verified", False))
    deterministic_hashing_verified = bool(summary.get("deterministic_hashing_verified", False))
    if spec.phase_id == "phase_1_foundations":
        deterministic_serialization_verified = bool(summary.get("deterministic_serialization_verified", False))
        deterministic_hashing_verified = bool(summary.get("deterministic_hashing_verified", False))
    non_executable_verified = bool(
        summary.get("non_executable_verified", False)
        or report and (report.get("non_executable") is True or report.get("foundation_is_non_executable") is True)
    )
    return V39PhaseEvidenceRecord(
        phase_id=spec.phase_id,
        phase_name=spec.phase_name,
        report_path=spec.report_path,
        migration_doc_path=spec.migration_doc_path,
        report_present=report is not None,
        migration_doc_present=_migration_doc_present(source, spec),
        report_is_json_object=isinstance(report, dict),
        phase_status=str(status or ""),
        expected_status=spec.expected_status,
        phase_status_valid=status == spec.expected_status,
        deterministic_hash_present=bool(deterministic_report_hash),
        classification_coverage_present=_classification_coverage_present(report, summary, spec),
        deterministic_serialization_verified=deterministic_serialization_verified,
        deterministic_hashing_verified=deterministic_hashing_verified,
        non_executable_verified=non_executable_verified,
        validation_error_count=_int(summary.get("validation_error_count")),
        warning_count=_warning_count(summary),
        hidden_behavior_count=_hidden_behavior_count(summary),
        hidden_finding_count=_int(summary.get("hidden_finding_count"))
        + _int(summary.get("hidden_finding_violation_count"))
        + _int(summary.get("hidden_scenario_finding_count"))
        + _int(summary.get("hidden_session_finding_count"))
        + _int(summary.get("hidden_aggregation_finding_count")),
        hidden_risk_count=_int(summary.get("hidden_risk_count")) + _int(summary.get("hidden_risk_violation_count")),
        hidden_non_safe_state_count=_int(summary.get("hidden_non_safe_state_count"))
        + _int(summary.get("hidden_non_safe_state_violation_count")),
        execution_capability_enabled_count=_capability_count(report, EXECUTION_CAPABILITY_KEYS),
        orchestration_capability_introduced_count=_capability_count(report, ORCHESTRATION_CAPABILITY_KEYS),
        recommendation_ranking_scoring_selection_capability_introduced_count=_capability_count(
            report, RRSS_CAPABILITY_KEYS
        ),
        authorization_approval_remediation_repair_capability_introduced_count=_capability_count(
            report, APPROVAL_REMEDIATION_REPAIR_KEYS
        ),
        runtime_mutation_capability_introduced_count=_capability_count(report, MUTATION_CAPABILITY_KEYS),
        deterministic_report_hash=deterministic_report_hash,
        source_report_hash=deterministic_hash(report or {}),
    )


def _load_report(source: V39CloseoutReadinessInput, spec: V39PhaseCloseoutSpec) -> dict[str, Any] | None:
    if source.phase_reports is not None:
        report = source.phase_reports.get(spec.phase_id)
        return dict(report) if isinstance(report, Mapping) else None
    path = source.repo_root / spec.report_path
    if not path.exists():
        return None
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return report if isinstance(report, dict) else None


def _migration_doc_present(source: V39CloseoutReadinessInput, spec: V39PhaseCloseoutSpec) -> bool:
    if source.migration_docs_present is not None:
        return bool(source.migration_docs_present.get(spec.phase_id, False))
    return (source.repo_root / spec.migration_doc_path).exists()


def _summary_block(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {}
    summary = report.get("summary")
    return summary if isinstance(summary, dict) else {}


def _status_value(report: dict[str, Any] | None, summary: dict[str, Any], field: str) -> Any:
    if field in summary:
        return summary[field]
    if report and field in report:
        return report[field]
    return None


def _deterministic_report_hash(report: dict[str, Any] | None) -> str:
    if not report:
        return ""
    for field in ("deterministic_report_hash", "deterministic_closeout_hash"):
        value = report.get(field)
        if isinstance(value, str) and value:
            return value
    deterministic = report.get("deterministic_guarantees")
    if isinstance(deterministic, dict):
        for field in (
            "certification_hash",
            "integrity_hash",
            "aggregation_hash",
            "scenario_hash",
            "session_hash",
            "evaluation_hash",
            "compatibility_hash",
            "boundary_hash",
        ):
            value = deterministic.get(field)
            if isinstance(value, str) and value:
                return value
    return ""


def _classification_coverage_present(
    report: dict[str, Any] | None,
    summary: dict[str, Any],
    spec: V39PhaseCloseoutSpec,
) -> bool:
    if not report:
        return False
    source = summary
    if spec.phase_id == "phase_1_foundations":
        state_guarantees = report.get("state_classification_guarantees")
        source = state_guarantees if isinstance(state_guarantees, dict) else summary
    return all(_int(source.get(field)) > 0 for field in spec.required_count_fields)


def _capability_count(report: dict[str, Any] | None, keys: frozenset[str]) -> int:
    if not report:
        return 0
    blocks: list[Mapping[str, Any]] = [report]
    for block_name in ("explicit_non_execution_guarantees", "non_execution_guarantees"):
        block = report.get(block_name)
        if isinstance(block, Mapping):
            blocks.append(block)
    return sum(1 for block in blocks for key in keys if block.get(key) is True)


def _warning_count(summary: dict[str, Any]) -> int:
    return sum(_int(summary.get(key)) for key in WARNING_COUNT_KEYS)


def _hidden_behavior_count(summary: dict[str, Any]) -> int:
    return sum(
        _int(summary.get(key))
        for key in (
            "hidden_behavior_count",
            "hidden_finding_count",
            "hidden_finding_violation_count",
            "hidden_risk_count",
            "hidden_risk_violation_count",
            "hidden_non_safe_state_count",
            "hidden_non_safe_state_violation_count",
            "hidden_conflict_count",
            "hidden_scenario_finding_count",
            "hidden_session_finding_count",
            "hidden_aggregation_finding_count",
            "hidden_visibility_count",
        )
    )


def _candidate_classifications(
    source: V39CloseoutReadinessInput,
    phase_evidence: tuple[V39PhaseEvidenceRecord, ...],
) -> tuple[str, ...]:
    candidates: list[str] = []
    if any(not item.report_present or not item.migration_doc_present or not item.report_is_json_object for item in phase_evidence):
        candidates.append(V3_9_CLOSEOUT_INCOMPLETE)
    if source.governance_blockers or source.closeout_blockers:
        candidates.append(V3_9_CLOSEOUT_BLOCKED)
    if any(
        item.validation_error_count
        or not item.phase_status_valid
        or not item.deterministic_hash_present
        or not item.classification_coverage_present
        or not item.deterministic_serialization_verified
        or not item.deterministic_hashing_verified
        or not item.non_executable_verified
        or item.execution_capability_enabled_count
        or item.orchestration_capability_introduced_count
        or item.recommendation_ranking_scoring_selection_capability_introduced_count
        or item.authorization_approval_remediation_repair_capability_introduced_count
        or item.runtime_mutation_capability_introduced_count
        for item in phase_evidence
    ):
        candidates.append(V3_9_NOT_READY_FOR_V4_PLANNING)
    warning_count = sum(item.warning_count for item in phase_evidence)
    if warning_count and source.expected_fail_visible_warnings:
        candidates.append(V3_9_CLOSEOUT_WITH_WARNINGS)
    if warning_count and not source.expected_fail_visible_warnings:
        candidates.append(V3_9_NOT_READY_FOR_V4_PLANNING)
    return tuple(candidates)


def _build_findings(
    source: V39CloseoutReadinessInput,
    phase_evidence: tuple[V39PhaseEvidenceRecord, ...],
) -> tuple[V39CloseoutFinding, ...]:
    findings: list[V39CloseoutFinding] = []
    order = 0
    for record in sorted(phase_evidence, key=lambda item: item.phase_id):
        order += 1
        findings.append(_finding(record, FINDING_PHASE_EVIDENCE, V3_9_CLOSEOUT_READY_FOR_V4_PLANNING, "phase evidence audited", order))
        order += 1
        report_classification = (
            V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
            if record.report_present and record.report_is_json_object
            else V3_9_CLOSEOUT_INCOMPLETE
        )
        findings.append(_finding(record, FINDING_GENERATED_REPORT, report_classification, "generated report presence audited", order))
        order += 1
        doc_classification = (
            V3_9_CLOSEOUT_READY_FOR_V4_PLANNING if record.migration_doc_present else V3_9_CLOSEOUT_INCOMPLETE
        )
        findings.append(_finding(record, FINDING_MIGRATION_DOC, doc_classification, "migration documentation presence audited", order))
        order += 1
        validation_classification = (
            V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
            if record.validation_error_count == 0 and record.phase_status_valid
            else V3_9_NOT_READY_FOR_V4_PLANNING
        )
        findings.append(
            _finding(
                record,
                FINDING_VALIDATION,
                validation_classification,
                f"validation errors={record.validation_error_count}; status={record.phase_status}",
                order,
            )
        )
        order += 1
        deterministic_classification = (
            V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
            if record.deterministic_hash_present
            and record.classification_coverage_present
            and record.deterministic_serialization_verified
            and record.deterministic_hashing_verified
            else V3_9_NOT_READY_FOR_V4_PLANNING
        )
        findings.append(
            _finding(
                record,
                FINDING_DETERMINISTIC_GUARANTEE,
                deterministic_classification,
                "deterministic serialization, hashing, and classification coverage audited",
                order,
            )
        )
        order += 1
        warning_classification = (
            V3_9_CLOSEOUT_WITH_WARNINGS
            if record.warning_count and source.expected_fail_visible_warnings
            else V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
            if record.warning_count == 0
            else V3_9_NOT_READY_FOR_V4_PLANNING
        )
        findings.append(
            _finding(
                record,
                FINDING_WARNING,
                warning_classification,
                f"fail-visible warning count={record.warning_count}",
                order,
            )
        )
        order += 1
        hidden_classification = (
            V3_9_CLOSEOUT_WITH_WARNINGS
            if record.hidden_behavior_count and source.expected_fail_visible_warnings
            else V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
            if record.hidden_behavior_count == 0
            else V3_9_NOT_READY_FOR_V4_PLANNING
        )
        findings.append(
            _finding(
                record,
                FINDING_HIDDEN_BEHAVIOR,
                hidden_classification,
                f"hidden behavior evidence count={record.hidden_behavior_count}",
                order,
            )
        )
        order += 1
        leakage_count = (
            record.execution_capability_enabled_count
            + record.orchestration_capability_introduced_count
            + record.recommendation_ranking_scoring_selection_capability_introduced_count
            + record.authorization_approval_remediation_repair_capability_introduced_count
            + record.runtime_mutation_capability_introduced_count
        )
        findings.append(
            _finding(
                record,
                FINDING_CAPABILITY_LEAKAGE,
                V3_9_CLOSEOUT_READY_FOR_V4_PLANNING
                if leakage_count == 0
                else V3_9_NOT_READY_FOR_V4_PLANNING,
                f"report-level prohibited capability enabled count={leakage_count}",
                order,
            )
        )
        for category, count in (
            (FINDING_NON_EXECUTION, record.execution_capability_enabled_count + record.orchestration_capability_introduced_count),
            (FINDING_NON_MUTATION, record.runtime_mutation_capability_introduced_count),
            (FINDING_NON_RRSS, record.recommendation_ranking_scoring_selection_capability_introduced_count),
        ):
            order += 1
            findings.append(
                _finding(
                    record,
                    category,
                    V3_9_CLOSEOUT_READY_FOR_V4_PLANNING if count == 0 else V3_9_NOT_READY_FOR_V4_PLANNING,
                    f"{category} prohibited capability count={count}",
                    order,
                )
            )
    for phase_id, category, reason in (
        ("phase_7_aggregation", "aggregation presence", "aggregation evidence exists"),
        ("phase_6_scenario", "scenario presence", "scenario evidence exists"),
        ("phase_5_session", "session presence", "session evidence exists"),
        ("phase_4_evaluation", "evaluation presence", "evaluation evidence exists"),
        ("phase_3_compatibility", "compatibility presence", "compatibility evidence exists"),
        ("phase_2_boundary", "boundary presence", "boundary evidence exists"),
        ("phase_1_foundations", "foundation presence", "foundation evidence exists"),
    ):
        record = next(item for item in phase_evidence if item.phase_id == phase_id)
        order += 1
        findings.append(
            _finding(
                record,
                FINDING_PHASE_EVIDENCE,
                V3_9_CLOSEOUT_READY_FOR_V4_PLANNING if record.report_present else V3_9_CLOSEOUT_INCOMPLETE,
                f"{category}: {reason}",
                order,
            )
        )
    for phase_id, finding_category, reason in (
        ("phase_8_integrity", FINDING_INTEGRITY, "integrity enforcement exists and is stable"),
        ("phase_9_certification", FINDING_CONTINUITY_CERTIFICATION, "continuity certification exists and is stable"),
    ):
        record = next(item for item in phase_evidence if item.phase_id == phase_id)
        order += 1
        findings.append(
            _finding(
                record,
                finding_category,
                V3_9_CLOSEOUT_READY_FOR_V4_PLANNING if record.phase_status_valid else V3_9_NOT_READY_FOR_V4_PLANNING,
                reason,
                order,
            )
        )
    if source.governance_blockers or source.closeout_blockers:
        order += 1
        findings.append(
            V39CloseoutFinding(
                finding_id=transition_closeout_finding_id("global", FINDING_BLOCKER),
                finding_category=FINDING_BLOCKER,
                classification=V3_9_CLOSEOUT_BLOCKED,
                phase_id="global",
                reason=", ".join(sorted(source.governance_blockers + source.closeout_blockers)),
                evidence_reference="v3_9_closeout_global_blockers",
                fail_visible=True,
                deterministic_order=order,
            )
        )
    if any(not item.report_present or not item.migration_doc_present for item in phase_evidence):
        order += 1
        findings.append(
            V39CloseoutFinding(
                finding_id=transition_closeout_finding_id("global", FINDING_INCOMPLETE_EVIDENCE),
                finding_category=FINDING_INCOMPLETE_EVIDENCE,
                classification=V3_9_CLOSEOUT_INCOMPLETE,
                phase_id="global",
                reason="required phase evidence is incomplete",
                evidence_reference="v3_9_closeout_required_phase_evidence",
                fail_visible=True,
                deterministic_order=order,
            )
        )
    order += 1
    findings.append(
        V39CloseoutFinding(
            finding_id=transition_closeout_finding_id("global", FINDING_V4_READINESS),
            finding_category=FINDING_V4_READINESS,
            classification=classify_v3_9_closeout(_candidate_classifications(source, phase_evidence)),
            phase_id="global",
            reason="v4.0 planning readiness audited without enabling runtime behavior",
            evidence_reference="v3_9_closeout_v4_readiness",
            fail_visible=True,
            deterministic_order=order,
        )
    )
    return tuple(sorted(findings, key=lambda item: item.deterministic_order))


def _finding(
    record: V39PhaseEvidenceRecord,
    category: str,
    classification: str,
    reason: str,
    deterministic_order: int,
) -> V39CloseoutFinding:
    return V39CloseoutFinding(
        finding_id=transition_closeout_finding_id(record.phase_id, category),
        finding_category=category,
        classification=classification,
        phase_id=record.phase_id,
        reason=reason,
        evidence_reference=record.report_path,
        fail_visible=True,
        deterministic_order=deterministic_order,
    )


def _build_summary(
    final_classification: str,
    v4_classification: str,
    phase_evidence: tuple[V39PhaseEvidenceRecord, ...],
    findings: tuple[V39CloseoutFinding, ...],
) -> V39CloseoutSummary:
    phase_8 = next((item for item in phase_evidence if item.phase_id == "phase_8_integrity"), None)
    phase_9 = next((item for item in phase_evidence if item.phase_id == "phase_9_certification"), None)
    payload = {
        "final_closeout_classification": final_classification,
        "v4_readiness_classification": v4_classification,
        "phase_ids": [item.phase_id for item in sorted(phase_evidence, key=lambda item: item.phase_id)],
        "finding_ids": [item.finding_id for item in sorted(findings, key=lambda item: item.deterministic_order)],
    }
    return V39CloseoutSummary(
        final_closeout_classification=final_classification,
        v4_readiness_classification=v4_classification,
        phase_evidence_count=len(phase_evidence),
        generated_report_count=sum(1 for item in phase_evidence if item.report_present and item.report_is_json_object),
        migration_doc_count=sum(1 for item in phase_evidence if item.migration_doc_present),
        missing_report_count=sum(1 for item in phase_evidence if not item.report_present or not item.report_is_json_object),
        missing_doc_count=sum(1 for item in phase_evidence if not item.migration_doc_present),
        validation_error_count=sum(item.validation_error_count for item in phase_evidence),
        blocker_count=sum(1 for finding in findings if finding.finding_category == FINDING_BLOCKER),
        warning_count=sum(item.warning_count for item in phase_evidence),
        hidden_behavior_count=sum(item.hidden_behavior_count for item in phase_evidence),
        hidden_finding_count=sum(item.hidden_finding_count for item in phase_evidence),
        hidden_risk_count=sum(item.hidden_risk_count for item in phase_evidence),
        hidden_non_safe_state_count=sum(item.hidden_non_safe_state_count for item in phase_evidence),
        execution_capability_enabled_count=sum(item.execution_capability_enabled_count for item in phase_evidence),
        orchestration_capability_introduced_count=sum(
            item.orchestration_capability_introduced_count for item in phase_evidence
        ),
        recommendation_ranking_scoring_selection_capability_introduced_count=sum(
            item.recommendation_ranking_scoring_selection_capability_introduced_count for item in phase_evidence
        ),
        authorization_approval_remediation_repair_capability_introduced_count=sum(
            item.authorization_approval_remediation_repair_capability_introduced_count for item in phase_evidence
        ),
        runtime_mutation_capability_introduced_count=sum(
            item.runtime_mutation_capability_introduced_count for item in phase_evidence
        ),
        integrity_enforcement_status=phase_8.phase_status if phase_8 else "",
        continuity_certification_status=phase_9.phase_status if phase_9 else "",
        deterministic_summary_hash=deterministic_hash(payload),
    )


def _int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0
