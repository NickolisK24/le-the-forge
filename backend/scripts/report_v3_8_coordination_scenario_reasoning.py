"""Generate the v3.8 coordination scenario reasoning report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402
from runtime_coordination.coordination_scenario_models import (  # noqa: E402
    SCENARIO_STATE_BLOCKED,
    SCENARIO_STATE_EXPERIMENTAL,
    SCENARIO_STATE_MODELED,
    SCENARIO_STATE_NON_EXECUTABLE,
    SCENARIO_STATE_PLANNING_ONLY,
    SCENARIO_STATE_PROHIBITED,
    SCENARIO_STATE_UNKNOWN,
    SCENARIO_STATE_UNMODELED,
    SCENARIO_STATE_UNSUPPORTED,
    hash_v3_8_scenario_audit,
    validate_v3_8_scenario_hash_stability,
    validate_v3_8_scenario_serialization_stability,
)
from runtime_coordination.coordination_scenario_reasoning import (  # noqa: E402
    export_v3_8_coordination_scenario_reasoning_audit,
    reason_v3_8_coordination_scenario,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_scenario_reasoning_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = reason_v3_8_coordination_scenario()
    serialization = validate_v3_8_scenario_serialization_stability(audit)
    hashing = validate_v3_8_scenario_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_scenario_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_scenario_reasoning",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic scenario reasoning across foundation, boundary, compatibility, evaluation, "
            "and session evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "immutable_evidence_records": audit.immutable_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "scoring_decision_system_enabled": audit.scoring_decision_system_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "scenario_runtime_state_machine_enabled": audit.scenario_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "scenario_totals": {
            "scenario_result_count": totals["scenario_result_count"],
            "modeled_count": totals["modeled_count"],
            "unmodeled_count": totals["unmodeled_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "comparison_count": totals["comparison_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "session_context_count": totals["session_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "unmodeled_fail_visible": totals["fail_visible_unmodeled_count"]
            == totals["unmodeled_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
        },
        "boundary_context_guarantees": {
            "boundary_context_count": totals["boundary_context_count"],
            "boundary_context_preserved_count": totals["boundary_context_preserved_count"],
            "all_results_preserve_boundary_context": totals["boundary_context_count"]
            == totals["scenario_result_count"]
            == totals["boundary_context_preserved_count"],
        },
        "compatibility_context_guarantees": {
            "compatibility_context_count": totals["compatibility_context_count"],
            "compatibility_context_preserved_count": totals["compatibility_context_preserved_count"],
            "all_results_preserve_compatibility_context": totals["compatibility_context_count"]
            == totals["scenario_result_count"]
            == totals["compatibility_context_preserved_count"],
        },
        "evaluation_context_guarantees": {
            "evaluation_context_count": totals["evaluation_context_count"],
            "evaluation_context_preserved_count": totals["evaluation_context_preserved_count"],
            "all_results_preserve_evaluation_context": totals["evaluation_context_count"]
            == totals["scenario_result_count"]
            == totals["evaluation_context_preserved_count"],
        },
        "session_context_guarantees": {
            "session_context_count": totals["session_context_count"],
            "session_context_preserved_count": totals["session_context_preserved_count"],
            "all_results_preserve_session_context": totals["session_context_count"]
            == totals["scenario_result_count"]
            == totals["session_context_preserved_count"],
        },
        "comparison_guarantees": {
            "comparison_count": totals["comparison_count"],
            "comparison_replay_safe_evidence_count": totals[
                "comparison_replay_safe_evidence_count"
            ],
            "comparison_rollback_safe_evidence_count": totals[
                "comparison_rollback_safe_evidence_count"
            ],
            "comparison_provenance_continuity_count": totals[
                "comparison_provenance_continuity_count"
            ],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "comparison_execution_language_violation_count": totals[
                "comparison_execution_language_violation_count"
            ],
            "recommendation_behavior_violation_count": totals[
                "recommendation_behavior_violation_count"
            ],
            "optimization_behavior_violation_count": totals[
                "optimization_behavior_violation_count"
            ],
            "comparisons_are_non_executable": all(
                comparison.non_execution_confirmation
                for comparison in audit.scenario_comparisons
            ),
        },
        "deterministic_guarantees": {
            "scenario_serialization_stable": serialization["stable"],
            "scenario_hash_stable": hashing["stable"],
            "scenario_hash": hash_v3_8_scenario_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "comparison_replay_safe_evidence_count": totals[
                "comparison_replay_safe_evidence_count"
            ],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["scenario_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "comparison_rollback_safe_evidence_count": totals[
                "comparison_rollback_safe_evidence_count"
            ],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["scenario_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "comparison_provenance_continuity_count": totals[
                "comparison_provenance_continuity_count"
            ],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["scenario_result_count"],
        },
        "scenario_record_guarantees": {
            "immutable_evidence_record_count": totals["immutable_evidence_record_count"],
            "all_scenarios_are_immutable_evidence_records": totals["immutable_evidence_record_count"]
            == totals["scenario_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
            "scenarios_are_not_runtime_state_machines": totals["runtime_state_machine_count"] == 0,
        },
        "non_execution_guarantees": {
            "coordination_execution_absent": not audit.coordination_execution_enabled,
            "orchestration_execution_absent": not audit.orchestration_execution_enabled,
            "routing_absent": not audit.routing_enabled,
            "scheduling_absent": not audit.scheduling_enabled,
            "dispatch_absent": not audit.dispatch_enabled,
            "traversal_execution_absent": not audit.traversal_execution_enabled,
            "optimization_absent": not audit.optimization_enabled,
            "recommendation_absent": not audit.recommendation_enabled,
            "scoring_decision_system_absent": not audit.scoring_decision_system_enabled,
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "scenario_runtime_state_machine_absent": not audit.scenario_runtime_state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_scenario_reasoning": export_v3_8_coordination_scenario_reasoning_audit(
            audit
        ),
        "scenario_state_semantics": {
            SCENARIO_STATE_MODELED: (
                "deterministic scenario evidence is complete enough to model hypothetically"
            ),
            SCENARIO_STATE_UNMODELED: (
                "deterministic evidence is insufficient to model the scenario"
            ),
            SCENARIO_STATE_BLOCKED: (
                "scenario is blocked by boundary, compatibility, evaluation, or session findings"
            ),
            SCENARIO_STATE_UNSUPPORTED: "scenario includes unsupported coordination states",
            SCENARIO_STATE_PROHIBITED: "scenario includes prohibited coordination states",
            SCENARIO_STATE_UNKNOWN: "scenario includes insufficient deterministic evidence",
            SCENARIO_STATE_EXPERIMENTAL: "explicitly labeled experimental reasoning only",
            SCENARIO_STATE_PLANNING_ONLY: "reasoning-only, no runtime execution",
            SCENARIO_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 6 is reasoning-only",
            "v3.8 Phase 6 does not enable coordination execution",
            "v3.8 Phase 6 does not enable orchestration execution",
            "v3.8 Phase 6 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 6 does not enable optimization or recommendations",
            "v3.8 Phase 6 does not enable scoring-based decision systems",
            "v3.8 Phase 6 does not enable execution authorization",
            "v3.8 Phase 6 does not enable runtime engines or state machines",
            "v3.8 Phase 6 does not enable callable execution paths",
            "v3.8 Phase 6 does not enable persistent runtime mutation",
            "v3.8 Phase 6 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "scenario_result_count": totals["scenario_result_count"],
            "comparison_count": totals["comparison_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "unmodeled_fail_visible": totals["fail_visible_unmodeled_count"]
            == totals["unmodeled_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "boundary_context_verified": totals["boundary_context_count"]
            == totals["scenario_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["scenario_result_count"],
            "evaluation_context_verified": totals["evaluation_context_count"]
            == totals["scenario_result_count"],
            "session_context_verified": totals["session_context_count"]
            == totals["scenario_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"]
            == totals["scenario_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"]
            == totals["scenario_result_count"],
            "provenance_verified": totals["provenance_continuity_count"]
            == totals["scenario_result_count"],
            "comparison_replay_verified": totals["comparison_replay_safe_evidence_count"]
            == totals["comparison_count"],
            "comparison_rollback_verified": totals["comparison_rollback_safe_evidence_count"]
            == totals["comparison_count"],
            "comparison_provenance_verified": totals["comparison_provenance_continuity_count"]
            == totals["comparison_count"],
            "immutable_evidence_records_verified": totals["immutable_evidence_record_count"]
            == totals["scenario_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "comparison_execution_language_violation_count": totals[
                "comparison_execution_language_violation_count"
            ],
            "recommendation_behavior_violation_count": totals[
                "recommendation_behavior_violation_count"
            ],
            "optimization_behavior_violation_count": totals[
                "optimization_behavior_violation_count"
            ],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
            "non_executable_verified": audit.non_executable,
            "orchestration_boundaries_enforced": totals["execution_boundary_violation_count"] == 0,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.8 Coordination Scenario Reasoning",
        "",
        "## What Phase 6 Adds",
        "",
        "Phase 6 adds deterministic coordination scenario reasoning that models hypothetical planning-only alternatives as immutable evidence records.",
        "",
        "Scenarios group foundation, boundary, compatibility, evaluation, and session context without introducing runtime behavior.",
        "",
        "## Scenarios vs Execution Plans",
        "",
        "Coordination scenarios are hypothetical evidence records. They do not authorize work, invoke work, change runtime state, or provide callable coordination flows.",
        "",
        f"- Immutable evidence records verified: `{report['summary']['immutable_evidence_records_verified']}`",
        f"- Runtime state-machine count: `{report['summary']['runtime_state_machine_count']}`",
        f"- Scenario runtime state machine absent: `{report['non_execution_guarantees']['scenario_runtime_state_machine_absent']}`",
        "",
        "## Scenario Comparison Scope",
        "",
        "Scenario comparison records deterministic differences between hypothetical planning-only alternatives.",
        "",
        "They preserve evidence, visibility, replay references, rollback references, and provenance references for every compared scenario.",
        "",
        "They do not choose an alternative, rank alternatives, assign decision scores, or authorize a runtime path.",
        "",
        "## Scenario States",
        "",
        "- `modeled` means deterministic scenario evidence is complete enough to model hypothetically.",
        "- `unmodeled` means deterministic evidence is insufficient to model the scenario.",
        "- `blocked` means the scenario is blocked by boundary, compatibility, evaluation, or session findings.",
        "- `unsupported` means the scenario includes unsupported coordination states.",
        "- `prohibited` means the scenario includes prohibited coordination states.",
        "- `unknown` means the scenario includes insufficient deterministic evidence.",
        "- `experimental` means explicitly labeled experimental reasoning only.",
        "- `planning_only` means reasoning-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Modeled State Differences",
        "",
        "Unmodeled scenarios lack enough deterministic evidence and stay visible.",
        "",
        "Blocked scenarios are stopped by boundary, compatibility, evaluation, or session findings.",
        "",
        "Unsupported scenarios include unsupported coordination states.",
        "",
        "Prohibited scenarios include intentionally forbidden coordination states.",
        "",
        "Unknown scenarios lack sufficient deterministic evidence.",
        "",
        "All non-modeled states remain fail-visible.",
        "",
        "## Context Preservation",
        "",
        f"- Boundary-context count: `{report['boundary_context_guarantees']['boundary_context_count']}`",
        f"- Boundary-context preserved count: `{report['boundary_context_guarantees']['boundary_context_preserved_count']}`",
        f"- Compatibility-context count: `{report['compatibility_context_guarantees']['compatibility_context_count']}`",
        f"- Compatibility-context preserved count: `{report['compatibility_context_guarantees']['compatibility_context_preserved_count']}`",
        f"- Evaluation-context count: `{report['evaluation_context_guarantees']['evaluation_context_count']}`",
        f"- Evaluation-context preserved count: `{report['evaluation_context_guarantees']['evaluation_context_preserved_count']}`",
        f"- Session-context count: `{report['session_context_guarantees']['session_context_count']}`",
        f"- Session-context preserved count: `{report['session_context_guarantees']['session_context_preserved_count']}`",
        "",
        "## Scenario Totals",
        "",
        f"- Scenario result count: `{report['scenario_totals']['scenario_result_count']}`",
        f"- Modeled count: `{report['scenario_totals']['modeled_count']}`",
        f"- Unmodeled count: `{report['scenario_totals']['unmodeled_count']}`",
        f"- Blocked count: `{report['scenario_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['scenario_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['scenario_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['scenario_totals']['unknown_count']}`",
        f"- Experimental count: `{report['scenario_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['scenario_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['scenario_totals']['non_executable_count']}`",
        f"- Comparison count: `{report['scenario_totals']['comparison_count']}`",
        f"- Hidden-risk count: `{report['scenario_totals']['hidden_risk_count']}`",
        f"- Recommendation-language violations: `{report['scenario_totals']['recommendation_language_violation_count']}`",
        f"- Optimization-language violations: `{report['scenario_totals']['optimization_language_violation_count']}`",
        f"- Execution-boundary violations: `{report['scenario_totals']['execution_boundary_violation_count']}`",
        "",
        "## Comparison Evidence",
        "",
        f"- Comparison count: `{report['comparison_guarantees']['comparison_count']}`",
        f"- Comparison replay-safe evidence count: `{report['comparison_guarantees']['comparison_replay_safe_evidence_count']}`",
        f"- Comparison rollback-safe evidence count: `{report['comparison_guarantees']['comparison_rollback_safe_evidence_count']}`",
        f"- Comparison provenance continuity count: `{report['comparison_guarantees']['comparison_provenance_continuity_count']}`",
        f"- Recommendation behavior violations: `{report['comparison_guarantees']['recommendation_behavior_violation_count']}`",
        f"- Optimization behavior violations: `{report['comparison_guarantees']['optimization_behavior_violation_count']}`",
        f"- Comparison execution-language violations: `{report['comparison_guarantees']['comparison_execution_language_violation_count']}`",
        f"- Comparisons are non-executable: `{report['comparison_guarantees']['comparisons_are_non_executable']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Unmodeled fail-visible: `{report['visibility_guarantees']['unmodeled_fail_visible']}`",
        f"- Blocked fail-visible: `{report['visibility_guarantees']['blocked_fail_visible']}`",
        f"- Unsupported fail-visible: `{report['visibility_guarantees']['unsupported_fail_visible']}`",
        f"- Prohibited fail-visible: `{report['visibility_guarantees']['prohibited_fail_visible']}`",
        f"- Unknown fail-visible: `{report['visibility_guarantees']['unknown_fail_visible']}`",
        "",
        "## Replay Rollback And Provenance",
        "",
        f"- Replay-safe evidence count: `{report['replay_guarantees']['replay_safe_evidence_count']}`",
        f"- All results have replay evidence: `{report['replay_guarantees']['all_results_have_replay_evidence']}`",
        f"- Rollback-safe evidence count: `{report['rollback_guarantees']['rollback_safe_evidence_count']}`",
        f"- All results have rollback evidence: `{report['rollback_guarantees']['all_results_have_rollback_evidence']}`",
        f"- Provenance continuity count: `{report['provenance_guarantees']['provenance_continuity_count']}`",
        f"- All results preserve provenance: `{report['provenance_guarantees']['all_results_preserve_provenance']}`",
        "",
        "## Deterministic Evidence",
        "",
        f"- Audit status: `{report['summary']['audit_status']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Scenario hash: `{report['deterministic_guarantees']['scenario_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Why This Remains Non-Executable",
        "",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Runtime engine absent: `{report['non_execution_guarantees']['runtime_engine_absent']}`",
        f"- State machine absent: `{report['non_execution_guarantees']['state_machine_absent']}`",
        f"- Scoring decision system absent: `{report['non_execution_guarantees']['scoring_decision_system_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 6 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Scoring-based decision systems.",
        "- Execution authorization.",
        "- Runtime engines.",
        "- State machines.",
        "- Runtime mutation.",
        "- Callable coordination flows.",
        "- Hidden transitions.",
        "- Silent fallback logic.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "generated"
        / "v3_8_coordination_scenario_reasoning_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_SCENARIO_REASONING.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_scenario_reasoning_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
