"""Artifact-only v3.6 closeout and v3.7 readiness audit."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .v3_6_closeout_readiness_models import (
    V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE,
    V3_6_BLOCKED_BY_EXECUTION_LEAKAGE,
    V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE,
    V3_6_BLOCKED_BY_INTEGRITY_FAILURE,
    V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE,
    V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_6_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_6_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY,
    V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR,
    V3_6_BLOCKED_BY_PROVENANCE_FAILURE,
    V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE,
    V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE,
    V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING,
    V3_6_CONTINUITY_BLOCKED,
    V3_6_CONTINUITY_PRESERVED,
    V3_6_REQUIRES_MANUAL_REVIEW,
    V3_6_VALIDATION_STABLE,
    V36CloseoutReadinessInput,
    V36CloseoutReadinessResult,
    V36PhaseCloseoutResult,
    V36PhaseCloseoutSpec,
    V36StatusExpectation,
    classify_v3_6_closeout_readiness,
    export_v3_6_closeout_result,
    hash_v3_6_closeout_result,
    serialize_v3_6_closeout_result,
)


def _expect(field_name: str, expected_value: str) -> V36StatusExpectation:
    return V36StatusExpectation(field_name, expected_value)


V3_6_PHASE_SPECS: tuple[V36PhaseCloseoutSpec, ...] = (
    V36PhaseCloseoutSpec(
        "phase_1_policy_intelligence",
        1,
        "policy intelligence",
        "docs/generated/v3_6_orchestration_policy_foundation_report.json",
        "docs/migration/V3_6_ORCHESTRATION_POLICY_FOUNDATION.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("policy_evaluation_status", "policy_evaluation_stable_with_visible_blockers"),
            _expect("policy_explainability_status", "policy_explainability_stable"),
            _expect("policy_integrity_status", "policy_integrity_stable"),
        ),
        (
            "deterministic_registry_hash",
            "deterministic_policy_evaluation_hash",
            "deterministic_explainability_hash",
            "deterministic_policy_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_2_compatibility_intelligence",
        2,
        "compatibility intelligence",
        "docs/generated/v3_6_orchestration_policy_compatibility_report.json",
        "docs/migration/V3_6_ORCHESTRATION_POLICY_COMPATIBILITY_MATRIX.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("compatibility_evaluation_status", "compatibility_evaluation_stable_with_visible_blockers"),
            _expect("compatibility_explainability_status", "compatibility_explainability_stable"),
            _expect("compatibility_integrity_status", "compatibility_integrity_stable"),
        ),
        (
            "deterministic_compatibility_registry_hash",
            "deterministic_compatibility_evaluation_hash",
            "deterministic_compatibility_explainability_hash",
            "deterministic_compatibility_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_3_resolution_auditing",
        3,
        "resolution auditing",
        "docs/generated/v3_6_orchestration_policy_resolution_audit_report.json",
        "docs/migration/V3_6_ORCHESTRATION_POLICY_RESOLUTION_AUDIT.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("resolution_audit_status", "resolution_audit_stable_with_visible_findings"),
            _expect("resolution_explainability_status", "resolution_explainability_stable"),
            _expect("resolution_integrity_status", "resolution_integrity_stable"),
        ),
        (
            "deterministic_resolution_registry_hash",
            "deterministic_resolution_audit_hash",
            "deterministic_resolution_explainability_hash",
            "deterministic_resolution_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_4_intent_modeling",
        4,
        "intent modeling",
        "docs/generated/v3_6_orchestration_intent_modeling_report.json",
        "docs/migration/V3_6_ORCHESTRATION_INTENT_MODELING.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("intent_classification_status", "intent_classification_stable_with_visible_findings"),
            _expect("intent_explainability_status", "intent_explainability_stable"),
            _expect("intent_integrity_status", "intent_integrity_stable"),
        ),
        (
            "deterministic_intent_registry_hash",
            "deterministic_intent_classification_hash",
            "deterministic_intent_explainability_hash",
            "deterministic_intent_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_5_intent_policy_mapping",
        5,
        "intent-policy mapping",
        "docs/generated/v3_6_orchestration_intent_policy_mapping_report.json",
        "docs/migration/V3_6_ORCHESTRATION_INTENT_POLICY_MAPPING.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("mapping_analysis_status", "mapping_analysis_stable_with_visible_findings"),
            _expect("mapping_explainability_status", "mapping_explainability_stable"),
            _expect("mapping_integrity_status", "mapping_integrity_stable"),
        ),
        (
            "deterministic_mapping_registry_hash",
            "deterministic_mapping_analysis_hash",
            "deterministic_mapping_explainability_hash",
            "deterministic_mapping_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_6_preflight_evaluation",
        6,
        "preflight evaluation",
        "docs/generated/v3_6_orchestration_preflight_report.json",
        "docs/migration/V3_6_ORCHESTRATION_PREFLIGHT_EVALUATION.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("preflight_evaluation_status", "preflight_evaluation_stable_with_visible_findings"),
            _expect("preflight_explainability_status", "preflight_explainability_stable"),
            _expect("preflight_integrity_status", "preflight_integrity_stable"),
        ),
        (
            "deterministic_preflight_registry_hash",
            "deterministic_preflight_evaluation_hash",
            "deterministic_preflight_explainability_hash",
            "deterministic_preflight_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_7_evaluation_trace_modeling",
        7,
        "evaluation trace modeling",
        "docs/generated/v3_6_orchestration_evaluation_trace_report.json",
        "docs/migration/V3_6_ORCHESTRATION_EVALUATION_TRACE_MODELING.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("trace_build_status", "trace_build_stable_with_visible_findings"),
            _expect("trace_explainability_status", "trace_explainability_stable"),
            _expect("trace_integrity_status", "trace_integrity_stable"),
        ),
        (
            "deterministic_trace_registry_hash",
            "deterministic_trace_build_hash",
            "deterministic_trace_explainability_hash",
            "deterministic_trace_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_8_replay_packets",
        8,
        "replay packets",
        "docs/generated/v3_6_orchestration_evaluation_replay_report.json",
        "docs/migration/V3_6_ORCHESTRATION_EVALUATION_REPLAY_PACKETS.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("replay_build_status", "replay_build_stable_with_visible_findings"),
            _expect("replay_explainability_status", "replay_explainability_stable"),
            _expect("replay_integrity_status", "replay_integrity_stable"),
        ),
        (
            "deterministic_replay_registry_hash",
            "deterministic_replay_build_hash",
            "deterministic_replay_explainability_hash",
            "deterministic_replay_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
    V36PhaseCloseoutSpec(
        "phase_9_chain_integrity_audit",
        9,
        "chain integrity auditing",
        "docs/generated/v3_6_orchestration_evaluation_chain_integrity_report.json",
        "docs/migration/V3_6_ORCHESTRATION_EVALUATION_CHAIN_INTEGRITY_AUDIT.md",
        (
            _expect("deterministic_validation_status", V3_6_VALIDATION_STABLE),
            _expect("chain_audit_status", "evaluation_chain_audit_stable"),
            _expect("chain_explainability_status", "evaluation_chain_explainability_stable"),
            _expect("chain_integrity_status", "evaluation_chain_integrity_stable"),
        ),
        (
            "deterministic_chain_audit_hash",
            "deterministic_chain_explainability_hash",
            "deterministic_chain_integrity_hash",
            "deterministic_report_hash",
        ),
    ),
)

DEFAULT_V3_6_CLOSEOUT_LIMITATIONS: tuple[str, ...] = (
    "v3.6 closeout inspects deterministic generated artifacts only",
    "v3.6 closeout does not execute, dispatch, route, mutate, schedule, optimize, or recommend orchestration",
    "v3.6 closeout does not repair missing reports, infer missing evidence, persist audit state, or enable v3.7 behavior",
    "v3.6 closeout does not perform live replay, capture runtime traces, read production state, or create execution plans",
)

V3_6_DETERMINISTIC_GUARANTEES: tuple[str, ...] = (
    "deterministic v3.6 closeout continuity",
    "deterministic readiness continuity",
    "deterministic replay preservation auditing",
    "deterministic rollback preservation auditing",
    "deterministic provenance preservation auditing",
    "deterministic explainability preservation auditing",
    "deterministic integrity preservation auditing",
    "deterministic blocker visibility auditing",
    "deterministic unsupported and prohibited visibility auditing",
    "deterministic execution prohibition auditing",
)

EXECUTION_LEAK_KEYS: frozenset[str] = frozenset(
    {
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "routing_behavior_enabled",
        "decision_routing_enabled",
        "mutation_behavior_enabled",
        "persistent_write_enabled",
        "persistent_mutation_enabled",
        "state_write_enabled",
        "graph_execution_enabled",
        "graph_traversal_behavior_enabled",
        "graph_traversal_execution_enabled",
        "scheduling_behavior_enabled",
        "orchestration_dispatch_enabled",
        "dispatch_behavior_enabled",
        "execution_planning_enabled",
        "replay_execution_enabled",
        "live_replay_execution_enabled",
    }
)

PROHIBITED_RUNTIME_KEYS: frozenset[str] = frozenset(
    {
        "automatic_resolution_enabled",
        "autonomous_behavior_enabled",
        "recommendation_behavior_enabled",
        "optimization_behavior_enabled",
        "background_execution_enabled",
        "background_processing_enabled",
        "production_runtime_behavior_enabled",
        "production_consumption_enabled",
        "production_runtime_consumption_enabled",
        "production_state_reads_enabled",
        "live_runtime_reads_enabled",
        "live_runtime_read_enabled",
        "runtime_trace_capture_enabled",
        "live_replay_enabled",
        "persistent_audit_storage_enabled",
        "audit_log_writing_enabled",
        "production_routing_enabled",
    }
)


def default_v3_6_closeout_readiness_input(repo_root: Path | None = None) -> V36CloseoutReadinessInput:
    return V36CloseoutReadinessInput(repo_root=repo_root or Path(__file__).resolve().parents[3])


def audit_v3_6_closeout_readiness(
    audit_input: V36CloseoutReadinessInput | None = None,
) -> V36CloseoutReadinessResult:
    source = audit_input or default_v3_6_closeout_readiness_input()
    phase_results = tuple(_audit_phase(source, spec) for spec in V3_6_PHASE_SPECS)
    missing_reports = _phase_ids(phase_results, lambda item: not item.report_present)
    missing_docs = _phase_ids(phase_results, lambda item: not item.documentation_present)
    invalid_statuses = _phase_ids(phase_results, lambda item: item.report_present and not item.status_valid)
    missing_hashes = _phase_ids(phase_results, lambda item: item.report_present and not item.deterministic_hash_present)
    missing_scenarios = _phase_ids(phase_results, lambda item: item.report_present and not item.scenario_coverage_present)
    missing_continuity = _phase_ids(phase_results, lambda item: item.report_present and not item.continuity_statuses)
    replay_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.replay_continuity_preserved)
    rollback_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.rollback_continuity_preserved)
    provenance_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.provenance_continuity_preserved)
    explainability_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.explainability_continuity_preserved)
    integrity_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.integrity_continuity_preserved)
    blocker_failures = _phase_ids(phase_results, lambda item: item.report_present and not item.blocker_visibility_preserved)
    unsupported_prohibited_failures = _phase_ids(
        phase_results,
        lambda item: item.report_present and not item.unsupported_prohibited_visibility_preserved,
    )
    execution_leaks = _phase_ids(phase_results, lambda item: item.execution_leakage_detected)
    prohibited_runtime = _phase_ids(phase_results, lambda item: item.prohibited_runtime_behavior_detected)
    phase_chain_blockers = () if source.phase_chain_connected else ("phase_chain_connected",)
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    blocker_statuses = _blocker_statuses(
        missing_reports,
        missing_docs,
        invalid_statuses,
        missing_hashes,
        missing_scenarios,
        missing_continuity,
        replay_failures,
        rollback_failures,
        provenance_failures,
        explainability_failures,
        integrity_failures,
        blocker_failures,
        unsupported_prohibited_failures,
        execution_leaks,
        prohibited_runtime,
        phase_chain_blockers,
        manual_review,
    )
    readiness = classify_v3_6_closeout_readiness(blocker_statuses)
    limitations = tuple(sorted(set(DEFAULT_V3_6_CLOSEOUT_LIMITATIONS + tuple(source.limitation_summary))))
    result = V36CloseoutReadinessResult(
        closeout_status=readiness,
        v3_7_readiness_classification=readiness,
        planning_only=True,
        phase_results=phase_results,
        phase_coverage_summary=_coverage_summary(phase_results),
        missing_report_list=missing_reports,
        missing_documentation_list=missing_docs,
        invalid_phase_status_list=invalid_statuses,
        missing_deterministic_hash_list=missing_hashes,
        missing_scenario_coverage_list=missing_scenarios,
        missing_continuity_evidence_list=missing_continuity,
        replay_continuity_failure_list=replay_failures,
        rollback_continuity_failure_list=rollback_failures,
        provenance_failure_list=provenance_failures,
        explainability_failure_list=explainability_failures,
        integrity_failure_list=integrity_failures,
        blocker_visibility_failure_list=blocker_failures,
        unsupported_prohibited_visibility_failure_list=unsupported_prohibited_failures,
        execution_leakage_list=execution_leaks,
        prohibited_runtime_behavior_list=prohibited_runtime,
        phase_chain_blocker_summary=phase_chain_blockers,
        readiness_blocker_summary=blocker_statuses,
        prohibition_preservation_summary=_prohibition_summary(execution_leaks, prohibited_runtime),
        deterministic_guarantee_summary=V3_6_DETERMINISTIC_GUARANTEES,
        limitation_summary=limitations,
        manual_review_summary=manual_review,
        deterministic_closeout_hash="",
        deterministic_explanation_summary=_explanation(readiness, blocker_statuses),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        persistent_write_enabled=False,
        production_runtime_behavior_enabled=False,
        production_state_reads_enabled=False,
        live_runtime_reads_enabled=False,
        background_execution_enabled=False,
        scheduling_behavior_enabled=False,
        recommendation_behavior_enabled=False,
        optimization_behavior_enabled=False,
        autonomous_behavior_enabled=False,
        graph_execution_enabled=False,
        execution_planning_enabled=False,
        orchestration_dispatch_enabled=False,
    )
    return replace(result, deterministic_closeout_hash=hash_v3_6_closeout_result(result))


def export_v3_6_closeout_readiness_result(result: V36CloseoutReadinessResult) -> dict[str, Any]:
    return export_v3_6_closeout_result(result)


def serialize_v3_6_closeout_readiness_result(result: V36CloseoutReadinessResult) -> str:
    return serialize_v3_6_closeout_result(result)


def _audit_phase(source: V36CloseoutReadinessInput, spec: V36PhaseCloseoutSpec) -> V36PhaseCloseoutResult:
    report = _load_report(source, spec)
    doc_present = _documentation_present(source, spec)
    status_results = {
        expectation.field_name: report.get(expectation.field_name) if report else None
        for expectation in spec.status_expectations
    }
    expected_statuses = {expectation.field_name: expectation.expected_value for expectation in spec.status_expectations}
    hashes = tuple(sorted(str(report[field]) for field in spec.hash_fields if report and report.get(field)))
    continuity_statuses = _continuity_statuses(report)
    return V36PhaseCloseoutResult(
        phase_id=spec.phase_id,
        phase_order=spec.phase_order,
        phase_name=spec.phase_name,
        report_path=spec.report_path,
        documentation_path=spec.documentation_path,
        report_present=report is not None,
        documentation_present=doc_present,
        status_results=dict(sorted(status_results.items())),
        expected_status_results=dict(sorted(expected_statuses.items())),
        status_valid=bool(report) and all(status_results[field] == expected for field, expected in expected_statuses.items()),
        deterministic_hash_present=len(hashes) == len(spec.hash_fields),
        deterministic_hashes=hashes,
        scenario_coverage_present=_scenario_coverage_present(report),
        continuity_statuses=continuity_statuses,
        continuity_preserved=bool(continuity_statuses) and all(_status_preserved(value) for value in continuity_statuses.values()),
        replay_continuity_preserved=_replay_continuity_preserved(report),
        rollback_continuity_preserved=_rollback_continuity_preserved(report),
        provenance_continuity_preserved=_specific_continuity_preserved(report, "provenance_continuity_status"),
        explainability_continuity_preserved=_specific_continuity_preserved(report, "explainability_continuity_status"),
        integrity_continuity_preserved=_specific_continuity_preserved(report, "integrity_continuity_status"),
        blocker_visibility_preserved=_visibility_key_present(report, "blocker"),
        unsupported_prohibited_visibility_preserved=(
            _visibility_key_present(report, "unsupported") or _visibility_key_present(report, "prohibited")
        ),
        execution_leakage_detected=_leak_detected(report, EXECUTION_LEAK_KEYS),
        prohibited_runtime_behavior_detected=_leak_detected(report, PROHIBITED_RUNTIME_KEYS),
    )


def _load_report(source: V36CloseoutReadinessInput, spec: V36PhaseCloseoutSpec) -> dict[str, Any] | None:
    if source.phase_reports is not None:
        report = source.phase_reports.get(spec.phase_id)
        return report if isinstance(report, dict) else None
    path = source.repo_root / spec.report_path
    if not path.exists():
        return None
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return report if isinstance(report, dict) else None


def _documentation_present(source: V36CloseoutReadinessInput, spec: V36PhaseCloseoutSpec) -> bool:
    if source.phase_documentation_present is not None:
        return bool(source.phase_documentation_present.get(spec.phase_id, False))
    return (source.repo_root / spec.documentation_path).exists()


def _scenario_coverage_present(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    summary = report.get("summary")
    if isinstance(summary, dict) and int(summary.get("scenario_count", 0) or 0) > 0:
        return True
    scenario_results = report.get("scenario_results")
    if isinstance(scenario_results, dict) and scenario_results:
        return True
    scenario_coverage = report.get("scenario_coverage")
    return isinstance(scenario_coverage, list) and bool(scenario_coverage)


def _continuity_statuses(report: dict[str, Any] | None) -> dict[str, str]:
    if not report:
        return {}
    return dict(
        sorted(
            (key, value)
            for key, value in report.items()
            if key.endswith("_continuity_status") and isinstance(value, str)
        )
    )


def _specific_continuity_preserved(report: dict[str, Any] | None, key: str) -> bool:
    if not report:
        return False
    value = report.get(key)
    return isinstance(value, str) and _status_preserved(value)


def _replay_continuity_preserved(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    statuses = tuple(
        value
        for key, value in report.items()
        if key in {"replay_continuity_status", "replay_safety_status"} and isinstance(value, str)
    )
    return report.get("replay_safety_confirmation") is True and all(_status_preserved(value) for value in statuses)


def _rollback_continuity_preserved(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    statuses = tuple(
        value
        for key, value in report.items()
        if key in {"rollback_continuity_status", "rollback_safety_status"} and isinstance(value, str)
    )
    return report.get("rollback_safety_confirmation") is True and all(_status_preserved(value) for value in statuses)


def _status_preserved(value: str) -> bool:
    return value.endswith("_preserved") or value.endswith("_stable") or "_stable_with_visible_" in value


def _visibility_key_present(report: dict[str, Any] | None, token: str) -> bool:
    return bool(report) and any(token in key for key in report)


def _leak_detected(report: dict[str, Any] | None, keys: frozenset[str]) -> bool:
    if not report:
        return False
    guarantee_blocks = [report]
    explicit = report.get("explicit_non_execution_guarantees")
    if isinstance(explicit, dict):
        guarantee_blocks.append(explicit)
    return any(block.get(key) is True for block in guarantee_blocks for key in keys)


def _phase_ids(
    phase_results: tuple[V36PhaseCloseoutResult, ...],
    predicate,
) -> tuple[str, ...]:
    return tuple(sorted(result.phase_id for result in phase_results if predicate(result)))


def _blocker_statuses(
    missing_reports: tuple[str, ...],
    missing_docs: tuple[str, ...],
    invalid_statuses: tuple[str, ...],
    missing_hashes: tuple[str, ...],
    missing_scenarios: tuple[str, ...],
    missing_continuity: tuple[str, ...],
    replay_failures: tuple[str, ...],
    rollback_failures: tuple[str, ...],
    provenance_failures: tuple[str, ...],
    explainability_failures: tuple[str, ...],
    integrity_failures: tuple[str, ...],
    blocker_failures: tuple[str, ...],
    unsupported_prohibited_failures: tuple[str, ...],
    execution_leaks: tuple[str, ...],
    prohibited_runtime: tuple[str, ...],
    phase_chain_blockers: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> tuple[str, ...]:
    blockers: list[str] = []
    if missing_reports:
        blockers.append(V3_6_BLOCKED_BY_MISSING_PHASE_REPORT)
    if missing_docs:
        blockers.append(V3_6_BLOCKED_BY_MISSING_DOCUMENTATION)
    if invalid_statuses:
        blockers.append(V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE)
    if missing_hashes:
        blockers.append(V3_6_BLOCKED_BY_MISSING_DETERMINISTIC_HASH)
    if missing_scenarios:
        blockers.append(V3_6_BLOCKED_BY_MISSING_SCENARIO_COVERAGE)
    if missing_continuity:
        blockers.append(V3_6_BLOCKED_BY_MISSING_CONTINUITY_EVIDENCE)
    if replay_failures:
        blockers.append(V3_6_BLOCKED_BY_REPLAY_CONTINUITY_FAILURE)
    if rollback_failures:
        blockers.append(V3_6_BLOCKED_BY_ROLLBACK_CONTINUITY_FAILURE)
    if provenance_failures:
        blockers.append(V3_6_BLOCKED_BY_PROVENANCE_FAILURE)
    if explainability_failures:
        blockers.append(V3_6_BLOCKED_BY_EXPLAINABILITY_FAILURE)
    if integrity_failures:
        blockers.append(V3_6_BLOCKED_BY_INTEGRITY_FAILURE)
    if blocker_failures:
        blockers.append(V3_6_BLOCKED_BY_BLOCKER_VISIBILITY_FAILURE)
    if unsupported_prohibited_failures:
        blockers.append(V3_6_BLOCKED_BY_UNSUPPORTED_PROHIBITED_VISIBILITY_FAILURE)
    if execution_leaks:
        blockers.append(V3_6_BLOCKED_BY_EXECUTION_LEAKAGE)
    if prohibited_runtime:
        blockers.append(V3_6_BLOCKED_BY_PROHIBITED_RUNTIME_BEHAVIOR)
    if phase_chain_blockers:
        blockers.append(V3_6_BLOCKED_BY_PHASE_CHAIN_DISCONTINUITY)
    if manual_review:
        blockers.append(V3_6_REQUIRES_MANUAL_REVIEW)
    return tuple(sorted(set(blockers)))


def _coverage_summary(phase_results: tuple[V36PhaseCloseoutResult, ...]) -> dict[str, int]:
    return {
        "audited_phase_count": len(phase_results),
        "valid_phase_count": sum(1 for result in phase_results if _phase_valid(result)),
        "invalid_phase_count": sum(1 for result in phase_results if not _phase_valid(result)),
        "report_present_count": sum(1 for result in phase_results if result.report_present),
        "documentation_present_count": sum(1 for result in phase_results if result.documentation_present),
        "status_valid_count": sum(1 for result in phase_results if result.status_valid),
        "deterministic_hash_present_count": sum(1 for result in phase_results if result.deterministic_hash_present),
        "scenario_coverage_present_count": sum(1 for result in phase_results if result.scenario_coverage_present),
    }


def _phase_valid(result: V36PhaseCloseoutResult) -> bool:
    return all(
        (
            result.report_present,
            result.documentation_present,
            result.status_valid,
            result.deterministic_hash_present,
            result.scenario_coverage_present,
            result.continuity_preserved,
            result.replay_continuity_preserved,
            result.rollback_continuity_preserved,
            result.provenance_continuity_preserved,
            result.explainability_continuity_preserved,
            result.integrity_continuity_preserved,
            result.blocker_visibility_preserved,
            result.unsupported_prohibited_visibility_preserved,
            not result.execution_leakage_detected,
            not result.prohibited_runtime_behavior_detected,
        )
    )


def _prohibition_summary(
    execution_leaks: tuple[str, ...],
    prohibited_runtime: tuple[str, ...],
) -> tuple[str, ...]:
    if not execution_leaks and not prohibited_runtime:
        return ("execution_and_runtime_prohibitions_preserved",)
    return tuple(
        sorted(
            [f"execution_leakage:{phase_id}" for phase_id in execution_leaks]
            + [f"prohibited_runtime_behavior:{phase_id}" for phase_id in prohibited_runtime]
        )
    )


def _explanation(readiness: str, blockers: tuple[str, ...]) -> str:
    if readiness == V3_6_CLOSED_OUT_READY_FOR_V3_7_PLANNING:
        return (
            "v3.6 closeout is stable; v3.7 planning may begin, but orchestration execution, routing, "
            "autonomy, mutation, scheduling, optimization, recommendation behavior, production runtime reads, "
            "background execution, persistent writes, and execution planning remain prohibited."
        )
    return f"v3.6 closeout blocks v3.7 planning because: {', '.join(sorted(blockers))}."
