"""Artifact-only v3.5 closeout and v3.6 readiness audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash

from .v3_5_closeout_readiness_models import (
    V3_5_BLOCKED_BY_EXECUTION_LEAK,
    V3_5_BLOCKED_BY_INVALID_PHASE_STATUS,
    V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH,
    V3_5_BLOCKED_BY_MISSING_DOCUMENTATION,
    V3_5_BLOCKED_BY_MISSING_PHASE_REPORT,
    V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE,
    V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY,
    V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK,
    V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING,
    V3_5_REQUIRES_MANUAL_REVIEW,
    V35CloseoutReadinessInput,
    V35CloseoutReadinessResult,
    V35PhaseCloseoutResult,
    V35PhaseCloseoutSpec,
    classify_v3_5_closeout_status,
    classify_v3_6_planning_readiness,
    export_v3_5_closeout_result,
    serialize_v3_5_closeout_result,
)


V3_5_PHASE_SPECS: tuple[V35PhaseCloseoutSpec, ...] = (
    V35PhaseCloseoutSpec(
        "phase_1",
        "governance consumption contracts",
        "docs/generated/v3_5_governance_consumption_contracts_report.json",
        "docs/migration/V3_5_GOVERNANCE_CONSUMPTION_CONTRACTS.md",
        "final_governance_consumption_status",
        "governance_consumption_ready_for_orchestration_planning",
        ("deterministic_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_2",
        "orchestration readiness evaluation",
        "docs/generated/v3_5_orchestration_readiness_evaluation_report.json",
        "docs/migration/V3_5_ORCHESTRATION_READINESS_EVALUATION.md",
        "final_readiness_status",
        "ready_for_future_orchestration_planning",
        ("deterministic_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_3",
        "governance dependency resolution",
        "docs/generated/v3_5_governance_dependency_resolution_report.json",
        "docs/migration/V3_5_GOVERNANCE_DEPENDENCY_RESOLUTION.md",
        "final_dependency_resolution_status",
        "dependency_satisfied",
        ("deterministic_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_4",
        "orchestration coordination planning",
        "docs/generated/v3_5_orchestration_coordination_planning_report.json",
        "docs/migration/V3_5_ORCHESTRATION_COORDINATION_PLANNING.md",
        "final_coordination_planning_status",
        "coordination_ready_for_planning",
        ("deterministic_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_5",
        "orchestration visibility aggregation",
        "docs/generated/v3_5_orchestration_visibility_aggregation_report.json",
        "docs/migration/V3_5_ORCHESTRATION_VISIBILITY_AGGREGATION.md",
        "final_visibility_aggregation_status",
        "visibility_ready_for_planning",
        ("deterministic_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_6",
        "orchestration planning snapshots",
        "docs/generated/v3_5_orchestration_planning_snapshot_report.json",
        "docs/migration/V3_5_ORCHESTRATION_PLANNING_SNAPSHOT.md",
        "final_snapshot_status",
        "snapshot_ready_for_replay_planning",
        ("deterministic_report_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_7",
        "snapshot diff and drift analysis",
        "docs/generated/v3_5_snapshot_diff_and_drift_analysis_report.json",
        "docs/migration/V3_5_SNAPSHOT_DIFF_AND_DRIFT_ANALYSIS.md",
        "final_diff_status",
        "snapshot_diff_stable",
        ("deterministic_report_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_8",
        "orchestration planning audit chains",
        "docs/generated/v3_5_orchestration_audit_chain_report.json",
        "docs/migration/V3_5_ORCHESTRATION_AUDIT_CHAIN.md",
        "final_audit_chain_status",
        "audit_chain_stable",
        ("deterministic_report_hash",),
    ),
    V35PhaseCloseoutSpec(
        "phase_9",
        "orchestration planning integrity audits",
        "docs/generated/v3_5_orchestration_integrity_audit_report.json",
        "docs/migration/V3_5_ORCHESTRATION_INTEGRITY_AUDIT.md",
        "final_integrity_audit_status",
        "integrity_audit_stable",
        ("deterministic_report_hash",),
    ),
)

DEFAULT_CLOSEOUT_LIMITATIONS: tuple[str, ...] = (
    "closeout audit inspects declarative generated artifacts only",
    "closeout audit does not execute, dispatch, route, mutate, write audit logs, schedule, or traverse orchestration",
    "closeout audit does not repair missing reports, infer missing evidence, persist audit state, or enable v3.6 behavior",
    "closeout audit does not perform live replay, capture runtime traces, or read production state",
)

EXECUTION_LEAK_KEYS: frozenset[str] = frozenset(
    {
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "routing_behavior_enabled",
        "decision_routing_enabled",
        "mutation_behavior_enabled",
        "persistent_mutation_enabled",
        "state_write_enabled",
        "audit_log_writing_enabled",
        "graph_execution_enabled",
        "graph_traversal_behavior_enabled",
        "graph_traversal_execution_enabled",
        "scheduling_behavior_enabled",
        "orchestration_dispatch_enabled",
        "runtime_trace_capture_enabled",
        "live_replay_enabled",
        "live_replay_execution_enabled",
        "rollback_execution_enabled",
        "experiment_execution_enabled",
        "persistent_audit_storage_enabled",
        "v3_6_behavior_enabled",
    }
)

PRODUCTION_LEAK_KEYS: frozenset[str] = frozenset(
    {
        "production_consumption_enabled",
        "production_runtime_consumption_enabled",
        "production_routing_enabled",
        "production_authoritative_manifests_enabled",
        "production_authoritative_manifest_treatment_enabled",
        "production_state_reads_enabled",
        "default_runtime_manifest_consumption_enabled",
    }
)


def default_v3_5_closeout_readiness_input(repo_root: Path | None = None) -> V35CloseoutReadinessInput:
    return V35CloseoutReadinessInput(repo_root=repo_root or Path(__file__).resolve().parents[3])


def audit_v3_5_closeout_readiness(
    audit_input: V35CloseoutReadinessInput | None = None,
) -> V35CloseoutReadinessResult:
    source = audit_input or default_v3_5_closeout_readiness_input()
    phase_results = tuple(_audit_phase(source, spec) for spec in V3_5_PHASE_SPECS)
    missing_reports = tuple(sorted(result.phase_id for result in phase_results if not result.report_present))
    missing_docs = tuple(sorted(result.phase_id for result in phase_results if not result.documentation_present))
    invalid_statuses = tuple(sorted(result.phase_id for result in phase_results if result.report_present and not result.status_valid))
    missing_hashes = tuple(sorted(result.phase_id for result in phase_results if result.report_present and not result.deterministic_hash_present))
    missing_scenarios = tuple(sorted(result.phase_id for result in phase_results if result.report_present and not result.scenario_coverage_present))
    execution_leaks = tuple(sorted(result.phase_id for result in phase_results if result.execution_leak_detected))
    production_leaks = tuple(sorted(result.phase_id for result in phase_results if result.production_consumption_leak_detected))
    compatibility_blockers = () if source.phase_chain_compatible else ("phase_chain_compatibility",)
    manual_review = tuple(sorted(set(source.manual_review_reasons)))
    candidates = _candidate_statuses(
        missing_reports,
        invalid_statuses,
        missing_hashes,
        missing_scenarios,
        compatibility_blockers,
        missing_docs,
        execution_leaks,
        production_leaks,
        manual_review,
    )
    status = classify_v3_5_closeout_status(candidates)
    readiness = classify_v3_6_planning_readiness(status)
    limitations = tuple(sorted(set(DEFAULT_CLOSEOUT_LIMITATIONS + tuple(source.limitation_summary))))
    closeout_hash = _closeout_hash(
        phase_results,
        compatibility_blockers,
        manual_review,
        limitations,
    )
    return V35CloseoutReadinessResult(
        closeout_status=status,
        v3_6_planning_readiness=readiness,
        planning_only=True,
        phase_results=phase_results,
        phase_coverage_summary={
            "expected_phase_count": len(V3_5_PHASE_SPECS),
            "report_present_count": sum(1 for result in phase_results if result.report_present),
            "documentation_present_count": sum(1 for result in phase_results if result.documentation_present),
            "valid_status_count": sum(1 for result in phase_results if result.status_valid),
            "deterministic_hash_present_count": sum(1 for result in phase_results if result.deterministic_hash_present),
            "scenario_coverage_present_count": sum(1 for result in phase_results if result.scenario_coverage_present),
        },
        missing_report_list=missing_reports,
        missing_documentation_list=missing_docs,
        invalid_phase_status_list=invalid_statuses,
        missing_deterministic_hash_list=missing_hashes,
        missing_scenario_coverage_list=missing_scenarios,
        compatibility_blocker_summary=compatibility_blockers,
        prohibition_preservation_summary=tuple(
            sorted(
                [f"execution_leak:{phase_id}" for phase_id in execution_leaks]
                + [f"production_consumption_leak:{phase_id}" for phase_id in production_leaks]
            )
        ),
        v3_6_readiness_summary=_readiness_summary(readiness),
        manual_review_summary=manual_review,
        limitation_summary=limitations,
        deterministic_closeout_hash=closeout_hash,
        deterministic_explanation_summary=_explanation(status, missing_reports + invalid_statuses + missing_hashes + missing_scenarios + compatibility_blockers + missing_docs + execution_leaks + production_leaks + manual_review),
        runtime_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_behavior_enabled=False,
        mutation_behavior_enabled=False,
        audit_log_writing_enabled=False,
        production_consumption_enabled=False,
        graph_execution_enabled=False,
        graph_traversal_behavior_enabled=False,
        scheduling_behavior_enabled=False,
        orchestration_dispatch_enabled=False,
        runtime_trace_capture_enabled=False,
        production_state_reads_enabled=False,
        live_replay_enabled=False,
        persistent_audit_storage_enabled=False,
        v3_6_behavior_enabled=False,
    )


def export_v3_5_closeout_readiness_result(result: V35CloseoutReadinessResult) -> dict[str, Any]:
    return export_v3_5_closeout_result(result)


def serialize_v3_5_closeout_readiness_result(result: V35CloseoutReadinessResult) -> str:
    return serialize_v3_5_closeout_result(result)


def _audit_phase(source: V35CloseoutReadinessInput, spec: V35PhaseCloseoutSpec) -> V35PhaseCloseoutResult:
    report = _load_report(source, spec)
    doc_present = _documentation_present(source, spec)
    status = report.get(spec.status_field) if report else None
    hashes = tuple(sorted(str(report[field]) for field in spec.hash_fields if report and report.get(field))) if report else ()
    return V35PhaseCloseoutResult(
        phase_id=spec.phase_id,
        phase_name=spec.phase_name,
        report_path=spec.report_path,
        documentation_path=spec.documentation_path,
        report_present=report is not None,
        documentation_present=doc_present,
        status_field=spec.status_field,
        phase_status=status if isinstance(status, str) else None,
        expected_status=spec.expected_status,
        status_valid=status == spec.expected_status,
        deterministic_hash_present=bool(hashes),
        scenario_coverage_present=_scenario_coverage_present(report),
        execution_leak_detected=_leak_detected(report, EXECUTION_LEAK_KEYS),
        production_consumption_leak_detected=_leak_detected(report, PRODUCTION_LEAK_KEYS),
        deterministic_hashes=hashes,
    )


def _load_report(source: V35CloseoutReadinessInput, spec: V35PhaseCloseoutSpec) -> dict[str, Any] | None:
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


def _documentation_present(source: V35CloseoutReadinessInput, spec: V35PhaseCloseoutSpec) -> bool:
    if source.phase_documentation_present is not None:
        return bool(source.phase_documentation_present.get(spec.phase_id, False))
    return (source.repo_root / spec.documentation_path).exists()


def _scenario_coverage_present(report: dict[str, Any] | None) -> bool:
    if not report:
        return False
    summary = report.get("summary")
    if isinstance(summary, dict) and "scenario_count" in summary:
        return int(summary.get("scenario_count", 0) or 0) > 0
    scenario_results = report.get("scenario_results")
    if isinstance(scenario_results, dict) and scenario_results:
        return True
    scenario_coverage = report.get("scenario_coverage")
    return isinstance(scenario_coverage, list) and bool(scenario_coverage)


def _leak_detected(report: dict[str, Any] | None, keys: frozenset[str]) -> bool:
    if not report:
        return False
    guarantee_blocks = [report]
    explicit_guarantees = report.get("explicit_non_execution_guarantees")
    if isinstance(explicit_guarantees, dict):
        guarantee_blocks.append(explicit_guarantees)
    return any(block.get(key) is True for block in guarantee_blocks for key in keys)


def _candidate_statuses(
    missing_reports: tuple[str, ...],
    invalid_statuses: tuple[str, ...],
    missing_hashes: tuple[str, ...],
    missing_scenarios: tuple[str, ...],
    compatibility_blockers: tuple[str, ...],
    missing_docs: tuple[str, ...],
    execution_leaks: tuple[str, ...],
    production_leaks: tuple[str, ...],
    manual_review: tuple[str, ...],
) -> list[str]:
    candidates: list[str] = []
    if missing_reports:
        candidates.append(V3_5_BLOCKED_BY_MISSING_PHASE_REPORT)
    if invalid_statuses:
        candidates.append(V3_5_BLOCKED_BY_INVALID_PHASE_STATUS)
    if missing_hashes:
        candidates.append(V3_5_BLOCKED_BY_MISSING_DETERMINISTIC_HASH)
    if missing_scenarios:
        candidates.append(V3_5_BLOCKED_BY_MISSING_SCENARIO_COVERAGE)
    if compatibility_blockers:
        candidates.append(V3_5_BLOCKED_BY_PHASE_CHAIN_INCOMPATIBILITY)
    if missing_docs:
        candidates.append(V3_5_BLOCKED_BY_MISSING_DOCUMENTATION)
    if execution_leaks:
        candidates.append(V3_5_BLOCKED_BY_EXECUTION_LEAK)
    if production_leaks:
        candidates.append(V3_5_BLOCKED_BY_PRODUCTION_CONSUMPTION_LEAK)
    if manual_review:
        candidates.append(V3_5_REQUIRES_MANUAL_REVIEW)
    return candidates


def _readiness_summary(readiness: str) -> tuple[str, ...]:
    if readiness == "v3_6_planning_allowed":
        return ("v3.6 planning discussions may begin; v3.6 behavior remains disabled",)
    if readiness == "v3_6_planning_requires_manual_review":
        return ("v3.6 planning requires manual review before discussions proceed",)
    return ("v3.6 planning is blocked by closeout findings",)


def _closeout_hash(
    phase_results: tuple[V35PhaseCloseoutResult, ...],
    compatibility_blockers: tuple[str, ...],
    manual_review: tuple[str, ...],
    limitations: tuple[str, ...],
) -> str:
    return deterministic_hash(
        {
            "phase_results": [
                {
                    "phase_id": item.phase_id,
                    "phase_status": item.phase_status,
                    "report_present": item.report_present,
                    "documentation_present": item.documentation_present,
                    "status_valid": item.status_valid,
                    "deterministic_hash_present": item.deterministic_hash_present,
                    "scenario_coverage_present": item.scenario_coverage_present,
                    "execution_leak_detected": item.execution_leak_detected,
                    "production_consumption_leak_detected": item.production_consumption_leak_detected,
                    "deterministic_hashes": sorted(item.deterministic_hashes),
                }
                for item in sorted(phase_results, key=lambda result: result.phase_id)
            ],
            "compatibility_blockers": sorted(compatibility_blockers),
            "manual_review": sorted(manual_review),
            "limitations": sorted(limitations),
        }
    )


def _explanation(status: str, entries: tuple[str, ...]) -> str:
    visible = tuple(sorted(set(entries)))
    if not visible:
        if status == V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING:
            return (
                "v3.5 closeout is stable; v3.6 planning discussions may begin, but no execution, routing, mutation, "
                "audit writing, graph execution, live replay, persistent audit storage, production state read, or v3.6 behavior is authorized."
            )
        return f"v3.5 closeout classified as {status}; no execution behavior is authorized."
    return f"v3.5 closeout classified as {status}; closeout entries: {', '.join(visible)}."
