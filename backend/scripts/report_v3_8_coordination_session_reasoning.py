"""Generate the v3.8 coordination session reasoning report."""

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
from runtime_coordination.coordination_session_models import (  # noqa: E402
    SESSION_STATE_BLOCKED,
    SESSION_STATE_COMPLETE,
    SESSION_STATE_EXPERIMENTAL,
    SESSION_STATE_INCOMPLETE,
    SESSION_STATE_NON_EXECUTABLE,
    SESSION_STATE_PLANNING_ONLY,
    SESSION_STATE_PROHIBITED,
    SESSION_STATE_UNKNOWN,
    SESSION_STATE_UNSUPPORTED,
    hash_v3_8_session_audit,
    validate_v3_8_session_hash_stability,
    validate_v3_8_session_serialization_stability,
)
from runtime_coordination.coordination_session_reasoning import (  # noqa: E402
    export_v3_8_coordination_session_reasoning_audit,
    reason_v3_8_coordination_session,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_session_reasoning_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = reason_v3_8_coordination_session()
    serialization = validate_v3_8_session_serialization_stability(audit)
    hashing = validate_v3_8_session_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_session_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_session_reasoning",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic session reasoning across foundation, boundary, compatibility, and evaluation evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
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
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "session_runtime_state_machine_enabled": audit.session_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "session_totals": {
            "session_result_count": totals["session_result_count"],
            "complete_count": totals["complete_count"],
            "incomplete_count": totals["incomplete_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "incomplete_fail_visible": totals["fail_visible_incomplete_count"]
            == totals["incomplete_count"],
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
            == totals["session_result_count"]
            == totals["boundary_context_preserved_count"],
        },
        "compatibility_context_guarantees": {
            "compatibility_context_count": totals["compatibility_context_count"],
            "compatibility_context_preserved_count": totals["compatibility_context_preserved_count"],
            "all_results_preserve_compatibility_context": totals["compatibility_context_count"]
            == totals["session_result_count"]
            == totals["compatibility_context_preserved_count"],
        },
        "evaluation_context_guarantees": {
            "evaluation_context_count": totals["evaluation_context_count"],
            "evaluation_context_preserved_count": totals["evaluation_context_preserved_count"],
            "all_results_preserve_evaluation_context": totals["evaluation_context_count"]
            == totals["session_result_count"]
            == totals["evaluation_context_preserved_count"],
        },
        "deterministic_guarantees": {
            "session_serialization_stable": serialization["stable"],
            "session_hash_stable": hashing["stable"],
            "session_hash": hash_v3_8_session_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["session_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["session_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["session_result_count"],
        },
        "session_record_guarantees": {
            "immutable_evidence_record_count": totals["immutable_evidence_record_count"],
            "all_sessions_are_immutable_evidence_records": totals["immutable_evidence_record_count"]
            == totals["session_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
            "sessions_are_not_runtime_state_machines": totals["runtime_state_machine_count"] == 0,
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
            "session_runtime_state_machine_absent": not audit.session_runtime_state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_session_reasoning": export_v3_8_coordination_session_reasoning_audit(audit),
        "session_state_semantics": {
            SESSION_STATE_COMPLETE: "deterministic session evidence is complete and internally consistent",
            SESSION_STATE_INCOMPLETE: "required deterministic evidence is missing and kept fail-visible",
            SESSION_STATE_BLOCKED: (
                "session is blocked due to boundary, compatibility, or evaluation findings"
            ),
            SESSION_STATE_UNSUPPORTED: "session includes unsupported coordination states",
            SESSION_STATE_PROHIBITED: "session includes prohibited coordination states",
            SESSION_STATE_UNKNOWN: "session includes insufficient deterministic evidence",
            SESSION_STATE_EXPERIMENTAL: "explicitly labeled experimental reasoning only",
            SESSION_STATE_PLANNING_ONLY: "reasoning-only, no runtime execution",
            SESSION_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 5 is reasoning-only",
            "v3.8 Phase 5 does not enable coordination execution",
            "v3.8 Phase 5 does not enable orchestration execution",
            "v3.8 Phase 5 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 5 does not enable optimization or recommendations",
            "v3.8 Phase 5 does not enable execution authorization",
            "v3.8 Phase 5 does not enable runtime engines or state machines",
            "v3.8 Phase 5 does not enable callable execution paths",
            "v3.8 Phase 5 does not enable persistent runtime mutation",
            "v3.8 Phase 5 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "session_result_count": totals["session_result_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "incomplete_fail_visible": totals["fail_visible_incomplete_count"]
            == totals["incomplete_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "boundary_context_verified": totals["boundary_context_count"] == totals["session_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["session_result_count"],
            "evaluation_context_verified": totals["evaluation_context_count"]
            == totals["session_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"] == totals["session_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"] == totals["session_result_count"],
            "provenance_verified": totals["provenance_continuity_count"] == totals["session_result_count"],
            "immutable_evidence_records_verified": totals["immutable_evidence_record_count"]
            == totals["session_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
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
        "# v3.8 Coordination Session Reasoning",
        "",
        "## What Phase 5 Adds",
        "",
        "Phase 5 adds deterministic coordination session reasoning that groups foundation, boundary, compatibility, and evaluation evidence into immutable session-level planning records.",
        "",
        "These records organize reasoning evidence without introducing runtime behavior.",
        "",
        "## Sessions vs Runtime State Machines",
        "",
        "Coordination sessions are immutable evidence records. They do not advance through runtime states, perform transitions, execute work, or mutate persistent runtime state.",
        "",
        f"- Immutable evidence records verified: `{report['summary']['immutable_evidence_records_verified']}`",
        f"- Runtime state-machine count: `{report['summary']['runtime_state_machine_count']}`",
        f"- Session runtime state machine absent: `{report['non_execution_guarantees']['session_runtime_state_machine_absent']}`",
        "",
        "## Session States",
        "",
        "- `complete` means deterministic session evidence is complete and internally consistent.",
        "- `incomplete` means required deterministic evidence is missing.",
        "- `blocked` means the session is blocked due to boundary, compatibility, or evaluation findings.",
        "- `unsupported` means the session includes unsupported coordination states.",
        "- `prohibited` means the session includes prohibited coordination states.",
        "- `unknown` means the session includes insufficient deterministic evidence.",
        "- `experimental` means explicitly labeled experimental reasoning only.",
        "- `planning_only` means reasoning-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Complete State Differences",
        "",
        "Incomplete sessions lack required deterministic evidence and stay visible.",
        "",
        "Blocked sessions are stopped by boundary, compatibility, or evaluation findings.",
        "",
        "Unsupported sessions include unsupported coordination states.",
        "",
        "Prohibited sessions include intentionally forbidden coordination states.",
        "",
        "Unknown sessions lack sufficient deterministic evidence.",
        "",
        "All non-complete states remain fail-visible.",
        "",
        "## Context Preservation",
        "",
        f"- Boundary-context count: `{report['boundary_context_guarantees']['boundary_context_count']}`",
        f"- Boundary-context preserved count: `{report['boundary_context_guarantees']['boundary_context_preserved_count']}`",
        f"- Compatibility-context count: `{report['compatibility_context_guarantees']['compatibility_context_count']}`",
        f"- Compatibility-context preserved count: `{report['compatibility_context_guarantees']['compatibility_context_preserved_count']}`",
        f"- Evaluation-context count: `{report['evaluation_context_guarantees']['evaluation_context_count']}`",
        f"- Evaluation-context preserved count: `{report['evaluation_context_guarantees']['evaluation_context_preserved_count']}`",
        "",
        "## Session Totals",
        "",
        f"- Session result count: `{report['session_totals']['session_result_count']}`",
        f"- Complete count: `{report['session_totals']['complete_count']}`",
        f"- Incomplete count: `{report['session_totals']['incomplete_count']}`",
        f"- Blocked count: `{report['session_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['session_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['session_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['session_totals']['unknown_count']}`",
        f"- Experimental count: `{report['session_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['session_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['session_totals']['non_executable_count']}`",
        f"- Hidden-risk count: `{report['session_totals']['hidden_risk_count']}`",
        f"- Execution-boundary violations: `{report['session_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Incomplete fail-visible: `{report['visibility_guarantees']['incomplete_fail_visible']}`",
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
        f"- Session hash: `{report['deterministic_guarantees']['session_hash']}`",
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
        "## Phase 5 Does Not Enable",
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
        / "v3_8_coordination_session_reasoning_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_SESSION_REASONING.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_session_reasoning_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
