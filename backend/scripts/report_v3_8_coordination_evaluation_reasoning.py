"""Generate the v3.8 coordination evaluation reasoning report."""

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

from runtime_coordination.coordination_evaluation_models import (  # noqa: E402
    EVALUATION_STATE_BLOCKED,
    EVALUATION_STATE_EXPERIMENTAL,
    EVALUATION_STATE_INVALID,
    EVALUATION_STATE_NON_EXECUTABLE,
    EVALUATION_STATE_PLANNING_ONLY,
    EVALUATION_STATE_PROHIBITED,
    EVALUATION_STATE_UNKNOWN,
    EVALUATION_STATE_UNSUPPORTED,
    EVALUATION_STATE_VALID,
    hash_v3_8_evaluation_audit,
    validate_v3_8_evaluation_hash_stability,
    validate_v3_8_evaluation_serialization_stability,
)
from runtime_coordination.coordination_evaluation_reasoning import (  # noqa: E402
    export_v3_8_coordination_evaluation_reasoning_audit,
    reason_v3_8_coordination_evaluation,
)
from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_evaluation_reasoning_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = reason_v3_8_coordination_evaluation()
    serialization = validate_v3_8_evaluation_serialization_stability(audit)
    hashing = validate_v3_8_evaluation_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_evaluation_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_evaluation_reasoning",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic evaluation reasoning across foundation, boundary, and compatibility evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "evaluation_totals": {
            "evaluation_result_count": totals["evaluation_result_count"],
            "valid_count": totals["valid_count"],
            "invalid_count": totals["invalid_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "invalid_fail_visible": totals["fail_visible_invalid_count"] == totals["invalid_count"],
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
            == totals["evaluation_result_count"]
            == totals["boundary_context_preserved_count"],
        },
        "compatibility_context_guarantees": {
            "compatibility_context_count": totals["compatibility_context_count"],
            "compatibility_context_preserved_count": totals["compatibility_context_preserved_count"],
            "all_results_preserve_compatibility_context": totals["compatibility_context_count"]
            == totals["evaluation_result_count"]
            == totals["compatibility_context_preserved_count"],
        },
        "deterministic_guarantees": {
            "evaluation_serialization_stable": serialization["stable"],
            "evaluation_hash_stable": hashing["stable"],
            "evaluation_hash": hash_v3_8_evaluation_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["evaluation_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["evaluation_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["evaluation_result_count"],
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
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_evaluation_reasoning": export_v3_8_coordination_evaluation_reasoning_audit(audit),
        "evaluation_state_semantics": {
            EVALUATION_STATE_VALID: "deterministic evidence supports the coordination evaluation",
            EVALUATION_STATE_INVALID: (
                "deterministic evidence shows the coordination evaluation is unsafe or inconsistent"
            ),
            EVALUATION_STATE_BLOCKED: "evaluation is intentionally blocked by boundary or compatibility findings",
            EVALUATION_STATE_UNSUPPORTED: "not currently supported and kept fail-visible",
            EVALUATION_STATE_PROHIBITED: "intentionally forbidden and kept fail-visible",
            EVALUATION_STATE_UNKNOWN: "insufficient deterministic evidence exists and is kept fail-visible",
            EVALUATION_STATE_EXPERIMENTAL: "explicitly labeled experimental reasoning only",
            EVALUATION_STATE_PLANNING_ONLY: "reasoning-only, no runtime execution",
            EVALUATION_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 4 is reasoning-only",
            "v3.8 Phase 4 does not enable coordination execution",
            "v3.8 Phase 4 does not enable orchestration execution",
            "v3.8 Phase 4 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 4 does not enable optimization or recommendations",
            "v3.8 Phase 4 does not enable execution authorization",
            "v3.8 Phase 4 does not enable runtime engines or state machines",
            "v3.8 Phase 4 does not enable callable execution paths",
            "v3.8 Phase 4 does not enable persistent runtime mutation",
            "v3.8 Phase 4 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "evaluation_result_count": totals["evaluation_result_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "invalid_fail_visible": totals["fail_visible_invalid_count"] == totals["invalid_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "boundary_context_verified": totals["boundary_context_count"] == totals["evaluation_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["evaluation_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"] == totals["evaluation_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"] == totals["evaluation_result_count"],
            "provenance_verified": totals["provenance_continuity_count"] == totals["evaluation_result_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
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
        "# v3.8 Coordination Evaluation Reasoning",
        "",
        "## What Phase 4 Adds",
        "",
        "Phase 4 adds deterministic coordination evaluation reasoning across coordination foundations, boundary findings, compatibility results, provenance continuity, replay evidence, rollback evidence, explainability state, and non-execution enforcement.",
        "",
        "It evaluates coordination evidence without introducing executable orchestration behavior.",
        "",
        "## Evaluation Reasoning vs Execution",
        "",
        "Evaluation reasoning explains whether deterministic coordination evidence can be treated as valid, invalid, blocked, unsupported, prohibited, unknown, experimental, planning-only, or non-executable.",
        "",
        "It does not execute, route, schedule, dispatch, traverse, optimize, recommend, authorize, mutate runtime state, run state machines, or create callable coordination flows.",
        "",
        "## Evaluation States",
        "",
        "- `valid` means deterministic evidence supports the coordination evaluation.",
        "- `invalid` means deterministic evidence shows the coordination evaluation is unsafe or inconsistent.",
        "- `blocked` means evaluation is intentionally blocked due to boundary or compatibility findings.",
        "- `unsupported` means the evaluation is not currently supported.",
        "- `prohibited` means the evaluation is intentionally forbidden.",
        "- `unknown` means insufficient deterministic evidence exists.",
        "- `experimental` means explicitly labeled experimental reasoning only.",
        "- `planning_only` means reasoning-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Valid State Differences",
        "",
        "Invalid states have deterministic evidence that the evaluation is unsafe or inconsistent.",
        "",
        "Blocked states are intentionally stopped by boundary or compatibility findings.",
        "",
        "Unsupported states are not currently supported, but are not necessarily forbidden.",
        "",
        "Prohibited states are intentionally forbidden.",
        "",
        "Unknown states lack sufficient deterministic evidence and cannot be inferred as valid.",
        "",
        "All non-valid states remain fail-visible.",
        "",
        "## Boundary Context Preservation",
        "",
        f"- Boundary-context count: `{report['boundary_context_guarantees']['boundary_context_count']}`",
        f"- Boundary-context preserved count: `{report['boundary_context_guarantees']['boundary_context_preserved_count']}`",
        f"- All results preserve boundary context: `{report['boundary_context_guarantees']['all_results_preserve_boundary_context']}`",
        "",
        "## Compatibility Context Preservation",
        "",
        f"- Compatibility-context count: `{report['compatibility_context_guarantees']['compatibility_context_count']}`",
        f"- Compatibility-context preserved count: `{report['compatibility_context_guarantees']['compatibility_context_preserved_count']}`",
        f"- All results preserve compatibility context: `{report['compatibility_context_guarantees']['all_results_preserve_compatibility_context']}`",
        "",
        "## Evaluation Totals",
        "",
        f"- Evaluation result count: `{report['evaluation_totals']['evaluation_result_count']}`",
        f"- Valid count: `{report['evaluation_totals']['valid_count']}`",
        f"- Invalid count: `{report['evaluation_totals']['invalid_count']}`",
        f"- Blocked count: `{report['evaluation_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['evaluation_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['evaluation_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['evaluation_totals']['unknown_count']}`",
        f"- Experimental count: `{report['evaluation_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['evaluation_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['evaluation_totals']['non_executable_count']}`",
        f"- Hidden-risk count: `{report['evaluation_totals']['hidden_risk_count']}`",
        f"- Execution-boundary violations: `{report['evaluation_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Invalid fail-visible: `{report['visibility_guarantees']['invalid_fail_visible']}`",
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
        f"- Evaluation hash: `{report['deterministic_guarantees']['evaluation_hash']}`",
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
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 4 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
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
        / "v3_8_coordination_evaluation_reasoning_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_EVALUATION_REASONING.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_evaluation_reasoning_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
