"""Deterministic v3.8 closeout and v3.9 readiness audit."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .v3_8_closeout_readiness_models import (
    V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING,
    V3_8_CLOSEOUT_BLOCKED,
    V3_8_CLOSEOUT_ID,
    V3_8_CLOSEOUT_INCOMPLETE,
    V3_8_CLOSEOUT_PHASE_ID,
    V3_8_CLOSEOUT_PROHIBITED,
    V3_8_CLOSEOUT_UNKNOWN,
    V3_8_CLOSEOUT_UNSUPPORTED,
    V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE,
    V3_8_CLOSEOUT_VISIBILITY_VISIBLE,
    V3_9_PLANNING_BLOCKED,
    V3_9_PLANNING_READY,
    V38CloseoutPhaseEvidence,
    V38CloseoutReadinessInput,
    V38CloseoutReadinessResult,
    export_v3_8_closeout_readiness_result,
    hash_v3_8_closeout_readiness_result,
)


EXPECTED_PHASE_COUNT = 9
PHASE_CHAIN: tuple[dict[str, object], ...] = (
    {
        "phase_order": 1,
        "phase_id": "coordination_foundations",
        "phase_name": "Coordination Foundations",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_foundation_models.py",
            "backend/app/runtime_coordination/coordination_identity_models.py",
            "backend/app/runtime_coordination/coordination_relationship_models.py",
            "backend/app/runtime_coordination/coordination_continuity_models.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_foundations_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_FOUNDATIONS.md",
        "script_path": "backend/scripts/report_v3_8_coordination_foundations.py",
        "test_path": "backend/tests/test_v3_8_coordination_foundations.py",
    },
    {
        "phase_order": 2,
        "phase_id": "coordination_boundary_intelligence",
        "phase_name": "Coordination Boundary Intelligence",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_boundary_models.py",
            "backend/app/runtime_coordination/coordination_boundary_intelligence.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_boundary_intelligence_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_BOUNDARY_INTELLIGENCE.md",
        "script_path": "backend/scripts/report_v3_8_coordination_boundary_intelligence.py",
        "test_path": "backend/tests/test_v3_8_coordination_boundary_intelligence.py",
    },
    {
        "phase_order": 3,
        "phase_id": "coordination_compatibility_reasoning",
        "phase_name": "Coordination Compatibility Reasoning",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_compatibility_models.py",
            "backend/app/runtime_coordination/coordination_compatibility_reasoning.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_compatibility_reasoning_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_COMPATIBILITY_REASONING.md",
        "script_path": "backend/scripts/report_v3_8_coordination_compatibility_reasoning.py",
        "test_path": "backend/tests/test_v3_8_coordination_compatibility_reasoning.py",
    },
    {
        "phase_order": 4,
        "phase_id": "coordination_evaluation_reasoning",
        "phase_name": "Coordination Evaluation Reasoning",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_evaluation_models.py",
            "backend/app/runtime_coordination/coordination_evaluation_reasoning.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_evaluation_reasoning_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_EVALUATION_REASONING.md",
        "script_path": "backend/scripts/report_v3_8_coordination_evaluation_reasoning.py",
        "test_path": "backend/tests/test_v3_8_coordination_evaluation_reasoning.py",
    },
    {
        "phase_order": 5,
        "phase_id": "coordination_session_reasoning",
        "phase_name": "Coordination Session Reasoning",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_session_models.py",
            "backend/app/runtime_coordination/coordination_session_reasoning.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_session_reasoning_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_SESSION_REASONING.md",
        "script_path": "backend/scripts/report_v3_8_coordination_session_reasoning.py",
        "test_path": "backend/tests/test_v3_8_coordination_session_reasoning.py",
    },
    {
        "phase_order": 6,
        "phase_id": "coordination_scenario_reasoning",
        "phase_name": "Coordination Scenario Reasoning",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_scenario_models.py",
            "backend/app/runtime_coordination/coordination_scenario_reasoning.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_scenario_reasoning_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_SCENARIO_REASONING.md",
        "script_path": "backend/scripts/report_v3_8_coordination_scenario_reasoning.py",
        "test_path": "backend/tests/test_v3_8_coordination_scenario_reasoning.py",
    },
    {
        "phase_order": 7,
        "phase_id": "coordination_intelligence_aggregation",
        "phase_name": "Coordination Intelligence Aggregation",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_aggregation_models.py",
            "backend/app/runtime_coordination/coordination_intelligence_aggregation.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_intelligence_aggregation_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_INTELLIGENCE_AGGREGATION.md",
        "script_path": "backend/scripts/report_v3_8_coordination_intelligence_aggregation.py",
        "test_path": "backend/tests/test_v3_8_coordination_intelligence_aggregation.py",
    },
    {
        "phase_order": 8,
        "phase_id": "coordination_integrity_enforcement",
        "phase_name": "Coordination Integrity Enforcement",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_integrity_models.py",
            "backend/app/runtime_coordination/coordination_integrity_enforcement.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_integrity_enforcement_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_INTEGRITY_ENFORCEMENT.md",
        "script_path": "backend/scripts/report_v3_8_coordination_integrity_enforcement.py",
        "test_path": "backend/tests/test_v3_8_coordination_integrity_enforcement.py",
    },
    {
        "phase_order": 9,
        "phase_id": "coordination_continuity_certification",
        "phase_name": "Coordination Continuity Certification",
        "module_paths": (
            "backend/app/runtime_coordination/coordination_certification_models.py",
            "backend/app/runtime_coordination/coordination_continuity_certification.py",
        ),
        "report_path": "docs/generated/v3_8_coordination_continuity_certification_report.json",
        "migration_doc_path": "docs/migration/V3_8_COORDINATION_CONTINUITY_CERTIFICATION.md",
        "script_path": "backend/scripts/report_v3_8_coordination_continuity_certification.py",
        "test_path": "backend/tests/test_v3_8_coordination_continuity_certification.py",
    },
)


def default_v3_8_closeout_readiness_input() -> V38CloseoutReadinessInput:
    return V38CloseoutReadinessInput()


def audit_v3_8_closeout_and_v3_9_readiness(
    source: V38CloseoutReadinessInput | None = None,
) -> V38CloseoutReadinessResult:
    request = source or default_v3_8_closeout_readiness_input()
    repo_root = _repo_root(request)
    phase_evidence = _phase_evidence(repo_root, request)
    blockers = _blockers(phase_evidence, request)
    warnings = _warnings(phase_evidence, request)
    validation_totals = _validation_totals(phase_evidence, blockers, warnings, request)
    closeout_state = _closeout_state(validation_totals, request)
    ready = closeout_state == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
    result = V38CloseoutReadinessResult(
        closeout_id=V3_8_CLOSEOUT_ID,
        audited_phase_list=phase_evidence,
        generated_report_list=tuple(
            sorted(evidence.report_path for evidence in phase_evidence if evidence.report_exists)
        ),
        migration_doc_list=tuple(
            sorted(evidence.migration_doc_path for evidence in phase_evidence if evidence.migration_doc_exists)
        ),
        closeout_state=closeout_state,
        v3_9_readiness_state=V3_9_PLANNING_READY if ready else V3_9_PLANNING_BLOCKED,
        explanation=_explanation(closeout_state),
        blocker_list=blockers,
        warning_list=warnings,
        provenance_continuity_summary={
            "provenance_continuity_count": validation_totals["provenance_continuity_count"],
            "expected_phase_count": EXPECTED_PHASE_COUNT,
            "provenance_continuity_complete": validation_totals["provenance_continuity_count"]
            == EXPECTED_PHASE_COUNT,
        },
        replay_evidence_summary={
            "replay_evidence_count": validation_totals["replay_evidence_count"],
            "expected_phase_count": EXPECTED_PHASE_COUNT,
            "replay_evidence_complete": validation_totals["replay_evidence_count"]
            == EXPECTED_PHASE_COUNT,
        },
        rollback_evidence_summary={
            "rollback_evidence_count": validation_totals["rollback_evidence_count"],
            "expected_phase_count": EXPECTED_PHASE_COUNT,
            "rollback_evidence_complete": validation_totals["rollback_evidence_count"]
            == EXPECTED_PHASE_COUNT,
        },
        deterministic_visibility_summary={
            "fail_visible_state_count": validation_totals["fail_visible_state_count"],
            "unsupported_visibility_count": validation_totals["unsupported_visibility_count"],
            "prohibited_visibility_count": validation_totals["prohibited_visibility_count"],
            "unknown_visibility_count": validation_totals["unknown_visibility_count"],
            "hidden_risk_count": validation_totals["hidden_risk_count"],
            "non_ready_states_fail_visible": closeout_state
            == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
            or validation_totals["non_ready_state_fail_visible"],
        },
        validation_totals=validation_totals,
        suggested_v3_9_planning_themes=(
            "coordination transition reasoning",
            "cross-coordination continuity deltas",
            "transition readiness evidence",
            "transition risk visibility",
            "transition provenance chains",
            "transition replay and rollback safety",
            "transition integrity auditing",
            "transition certification",
        ),
        non_execution_confirmation=validation_totals["execution_boundary_violation_count"] == 0,
        prohibited_behavior_confirmation=validation_totals["prohibited_behavior_violation_count"] == 0,
        closeout_visibility_status=V3_8_CLOSEOUT_VISIBILITY_VISIBLE
        if ready
        else V3_8_CLOSEOUT_VISIBILITY_FAIL_VISIBLE,
        fail_visible=True,
        hidden=False,
        coordination_execution_enabled=False,
        orchestration_execution_enabled=False,
        routing_enabled=False,
        scheduling_enabled=False,
        dispatch_enabled=False,
        traversal_enabled=False,
        optimization_enabled=False,
        recommendation_enabled=False,
        ranking_enabled=False,
        scoring_enabled=False,
        selection_enabled=False,
        execution_authorization_enabled=False,
        runtime_mutation_enabled=False,
        runtime_engine_enabled=False,
        state_machine_enabled=False,
        callable_coordination_flow_enabled=False,
        hidden_transition_enabled=False,
        silent_fallback_enabled=False,
        production_behavior_enabled=False,
    )
    return replace(result, deterministic_closeout_hash=hash_v3_8_closeout_readiness_result(result))


def export_v3_8_closeout_and_v3_9_readiness_result(
    result: V38CloseoutReadinessResult,
) -> dict[str, object]:
    return export_v3_8_closeout_readiness_result(result)


def _repo_root(request: V38CloseoutReadinessInput) -> Path:
    if request.repo_root:
        return Path(request.repo_root)
    return Path(__file__).resolve().parents[3]


def _phase_evidence(
    repo_root: Path,
    request: V38CloseoutReadinessInput,
) -> tuple[V38CloseoutPhaseEvidence, ...]:
    phase_records: list[V38CloseoutPhaseEvidence] = []
    for phase in PHASE_CHAIN:
        phase_id = str(phase["phase_id"])
        if phase_id in request.omitted_phase_ids:
            continue
        report_path = str(phase["report_path"])
        migration_doc_path = str(phase["migration_doc_path"])
        report_exists = _exists(repo_root, report_path) and report_path not in request.omitted_report_paths
        migration_doc_exists = _exists(repo_root, migration_doc_path) and migration_doc_path not in request.omitted_migration_doc_paths
        report = _load_report(repo_root / report_path) if report_exists else {}
        summary = report.get("summary", {}) if isinstance(report.get("summary", {}), dict) else {}
        module_paths = tuple(str(path) for path in phase["module_paths"])
        phase_records.append(
            V38CloseoutPhaseEvidence(
                phase_order=int(phase["phase_order"]),
                phase_id=phase_id,
                phase_name=str(phase["phase_name"]),
                module_paths=module_paths,
                report_path=report_path,
                migration_doc_path=migration_doc_path,
                script_path=str(phase["script_path"]),
                test_path=str(phase["test_path"]),
                report_hash=str(report.get("deterministic_report_hash", "")),
                report_exists=report_exists,
                migration_doc_exists=migration_doc_exists,
                module_paths_exist=all(_exists(repo_root, path) for path in module_paths),
                script_exists=_exists(repo_root, str(phase["script_path"])),
                test_exists=_exists(repo_root, str(phase["test_path"])),
                deterministic_evidence_present=bool(report.get("deterministic_report_hash"))
                and bool(summary.get("deterministic_serialization_verified", True))
                and bool(summary.get("deterministic_hashing_verified", True)),
                replay_evidence_visible=bool(summary.get("replay_verified", False)),
                rollback_evidence_visible=bool(summary.get("rollback_verified", False)),
                provenance_continuity_visible=bool(summary.get("provenance_verified", False)),
                non_executable_verified=bool(summary.get("non_executable_verified", False)),
                orchestration_boundaries_enforced=bool(
                    summary.get("orchestration_boundaries_enforced", False)
                ),
                unsupported_visibility=bool(summary.get("unsupported_fail_visible", False)),
                prohibited_visibility=bool(summary.get("prohibited_fail_visible", False)),
                unknown_visibility=bool(summary.get("unknown_fail_visible", False)),
                fail_visible_state_count=_fail_visible_state_count(summary),
                hidden_risk_count=int(summary.get("hidden_risk_count", 0) or 0),
                recommendation_language_violation_count=int(
                    summary.get("recommendation_language_violation_count", 0) or 0
                ),
                optimization_language_violation_count=int(
                    summary.get("optimization_language_violation_count", 0) or 0
                ),
                ranking_language_violation_count=int(
                    summary.get("ranking_language_violation_count", 0) or 0
                ),
                scoring_behavior_violation_count=int(
                    summary.get("scoring_behavior_violation_count", 0) or 0
                ),
                selection_behavior_violation_count=int(
                    summary.get("selection_behavior_violation_count", 0) or 0
                ),
                execution_boundary_violation_count=int(
                    summary.get("execution_boundary_violation_count", 0) or 0
                ),
            )
        )
    return tuple(sorted(phase_records, key=lambda item: item.phase_order))


def _exists(repo_root: Path, path: str) -> bool:
    return (repo_root / path).exists()


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fail_visible_state_count(summary: dict[str, Any]) -> int:
    return sum(1 for key, value in summary.items() if key.endswith("_fail_visible") and value is True)


def _blockers(
    phase_evidence: tuple[V38CloseoutPhaseEvidence, ...],
    request: V38CloseoutReadinessInput,
) -> tuple[str, ...]:
    blockers: list[str] = list(request.manual_blockers)
    present_phase_ids = {evidence.phase_id for evidence in phase_evidence}
    expected_phase_ids = {str(phase["phase_id"]) for phase in PHASE_CHAIN}
    for phase_id in sorted(expected_phase_ids - present_phase_ids):
        blockers.append(f"missing_phase:{phase_id}")
    for evidence in phase_evidence:
        if not evidence.report_exists:
            blockers.append(f"missing_generated_report:{evidence.report_path}")
        if not evidence.migration_doc_exists:
            blockers.append(f"missing_migration_doc:{evidence.migration_doc_path}")
        if not evidence.module_paths_exist:
            blockers.append(f"missing_module_paths:{evidence.phase_id}")
        if not evidence.script_exists:
            blockers.append(f"missing_report_script:{evidence.script_path}")
        if not evidence.test_exists:
            blockers.append(f"missing_test:{evidence.test_path}")
        if not evidence.deterministic_evidence_present:
            blockers.append(f"missing_deterministic_evidence:{evidence.phase_id}")
        if not evidence.replay_evidence_visible:
            blockers.append(f"missing_replay_evidence:{evidence.phase_id}")
        if not evidence.rollback_evidence_visible:
            blockers.append(f"missing_rollback_evidence:{evidence.phase_id}")
        if not evidence.provenance_continuity_visible:
            blockers.append(f"missing_provenance_continuity:{evidence.phase_id}")
        if not evidence.non_executable_verified:
            blockers.append(f"missing_non_execution_confirmation:{evidence.phase_id}")
        if not evidence.orchestration_boundaries_enforced:
            blockers.append(f"orchestration_boundary_not_enforced:{evidence.phase_id}")
    if request.force_hidden_risk_count:
        blockers.append("forced_hidden_risk")
    if request.force_recommendation_language_violation_count:
        blockers.append("forced_recommendation_language_violation")
    if request.force_optimization_language_violation_count:
        blockers.append("forced_optimization_language_violation")
    if request.force_ranking_language_violation_count:
        blockers.append("forced_ranking_language_violation")
    if request.force_scoring_behavior_violation_count:
        blockers.append("forced_scoring_behavior_violation")
    if request.force_selection_behavior_violation_count:
        blockers.append("forced_selection_behavior_violation")
    if request.force_execution_boundary_violation_count:
        blockers.append("forced_execution_boundary_violation")
    if request.force_unsupported_state:
        blockers.append("forced_unsupported_state")
    if request.force_prohibited_state:
        blockers.append("forced_prohibited_state")
    if request.force_unknown_state:
        blockers.append("forced_unknown_state")
    return tuple(sorted(set(blockers)))


def _warnings(
    phase_evidence: tuple[V38CloseoutPhaseEvidence, ...],
    request: V38CloseoutReadinessInput,
) -> tuple[str, ...]:
    warnings: list[str] = []
    for evidence in phase_evidence:
        if evidence.unsupported_visibility:
            warnings.append(f"unsupported_state_visible:{evidence.phase_id}")
        if evidence.prohibited_visibility:
            warnings.append(f"prohibited_state_visible:{evidence.phase_id}")
        if evidence.unknown_visibility:
            warnings.append(f"unknown_state_visible:{evidence.phase_id}")
    if request.force_unsupported_state:
        warnings.append("forced_unsupported_state_fail_visible")
    if request.force_prohibited_state:
        warnings.append("forced_prohibited_state_fail_visible")
    if request.force_unknown_state:
        warnings.append("forced_unknown_state_fail_visible")
    return tuple(sorted(set(warnings)))


def _validation_totals(
    phase_evidence: tuple[V38CloseoutPhaseEvidence, ...],
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
    request: V38CloseoutReadinessInput,
) -> dict[str, int | bool | str]:
    hidden_risk_count = sum(evidence.hidden_risk_count for evidence in phase_evidence) + request.force_hidden_risk_count
    recommendation_language_violation_count = (
        sum(evidence.recommendation_language_violation_count for evidence in phase_evidence)
        + request.force_recommendation_language_violation_count
    )
    optimization_language_violation_count = (
        sum(evidence.optimization_language_violation_count for evidence in phase_evidence)
        + request.force_optimization_language_violation_count
    )
    ranking_language_violation_count = (
        sum(evidence.ranking_language_violation_count for evidence in phase_evidence)
        + request.force_ranking_language_violation_count
    )
    scoring_behavior_violation_count = (
        sum(evidence.scoring_behavior_violation_count for evidence in phase_evidence)
        + request.force_scoring_behavior_violation_count
    )
    selection_behavior_violation_count = (
        sum(evidence.selection_behavior_violation_count for evidence in phase_evidence)
        + request.force_selection_behavior_violation_count
    )
    execution_boundary_violation_count = (
        sum(evidence.execution_boundary_violation_count for evidence in phase_evidence)
        + request.force_execution_boundary_violation_count
    )
    prohibited_behavior_violation_count = (
        recommendation_language_violation_count
        + optimization_language_violation_count
        + ranking_language_violation_count
        + scoring_behavior_violation_count
        + selection_behavior_violation_count
        + execution_boundary_violation_count
    )
    return {
        "expected_phase_count": EXPECTED_PHASE_COUNT,
        "audited_phase_count": len(phase_evidence),
        "generated_report_count": sum(1 for evidence in phase_evidence if evidence.report_exists),
        "migration_documentation_count": sum(
            1 for evidence in phase_evidence if evidence.migration_doc_exists
        ),
        "deterministic_evidence_count": sum(
            1 for evidence in phase_evidence if evidence.deterministic_evidence_present
        ),
        "replay_evidence_count": sum(1 for evidence in phase_evidence if evidence.replay_evidence_visible),
        "rollback_evidence_count": sum(
            1 for evidence in phase_evidence if evidence.rollback_evidence_visible
        ),
        "provenance_continuity_count": sum(
            1 for evidence in phase_evidence if evidence.provenance_continuity_visible
        ),
        "fail_visible_state_count": sum(evidence.fail_visible_state_count for evidence in phase_evidence),
        "unsupported_visibility_count": sum(1 for evidence in phase_evidence if evidence.unsupported_visibility),
        "prohibited_visibility_count": sum(1 for evidence in phase_evidence if evidence.prohibited_visibility),
        "unknown_visibility_count": sum(1 for evidence in phase_evidence if evidence.unknown_visibility),
        "hidden_risk_count": hidden_risk_count,
        "recommendation_language_violation_count": recommendation_language_violation_count,
        "optimization_language_violation_count": optimization_language_violation_count,
        "ranking_language_violation_count": ranking_language_violation_count,
        "scoring_behavior_violation_count": scoring_behavior_violation_count,
        "selection_behavior_violation_count": selection_behavior_violation_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "prohibited_behavior_violation_count": prohibited_behavior_violation_count,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "non_ready_state_fail_visible": len(blockers) > 0,
        "non_execution_confirmation": execution_boundary_violation_count == 0,
        "prohibited_behavior_confirmation": prohibited_behavior_violation_count == 0,
        "v3_8_closeout_ready": (
            len(blockers) == 0
            and len(phase_evidence) == EXPECTED_PHASE_COUNT
            and hidden_risk_count == 0
            and prohibited_behavior_violation_count == 0
        ),
    }


def _closeout_state(
    validation_totals: dict[str, int | bool | str],
    request: V38CloseoutReadinessInput,
) -> str:
    if validation_totals["v3_8_closeout_ready"]:
        return V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING
    if request.force_prohibited_state or validation_totals["prohibited_behavior_violation_count"]:
        return V3_8_CLOSEOUT_PROHIBITED
    if validation_totals["audited_phase_count"] != validation_totals["expected_phase_count"]:
        return V3_8_CLOSEOUT_INCOMPLETE
    if validation_totals["generated_report_count"] != validation_totals["expected_phase_count"]:
        return V3_8_CLOSEOUT_INCOMPLETE
    if validation_totals["migration_documentation_count"] != validation_totals["expected_phase_count"]:
        return V3_8_CLOSEOUT_INCOMPLETE
    if request.force_unsupported_state:
        return V3_8_CLOSEOUT_UNSUPPORTED
    if request.force_unknown_state:
        return V3_8_CLOSEOUT_UNKNOWN
    return V3_8_CLOSEOUT_BLOCKED


def _explanation(closeout_state: str) -> str:
    if closeout_state == V3_8_CLOSED_OUT_READY_FOR_V3_9_PLANNING:
        return (
            "v3.8 deterministic orchestration-planning coordination intelligence is complete "
            "enough for v3.9 planning while remaining non-executable"
        )
    if closeout_state == V3_8_CLOSEOUT_INCOMPLETE:
        return "v3.8 closeout is incomplete because required deterministic evidence is missing"
    if closeout_state == V3_8_CLOSEOUT_UNSUPPORTED:
        return "v3.8 closeout includes fail-visible unsupported evidence"
    if closeout_state == V3_8_CLOSEOUT_PROHIBITED:
        return "v3.8 closeout includes fail-visible prohibited evidence or prohibited behavior contamination"
    if closeout_state == V3_8_CLOSEOUT_UNKNOWN:
        return "v3.8 closeout includes fail-visible unknown evidence"
    return "v3.8 closeout is blocked by fail-visible findings"
