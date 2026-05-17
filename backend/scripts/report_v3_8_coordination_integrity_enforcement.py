"""Generate the v3.8 coordination integrity enforcement report."""

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
from runtime_coordination.coordination_integrity_enforcement import (  # noqa: E402
    enforce_v3_8_coordination_integrity,
    export_v3_8_coordination_integrity_enforcement_audit,
)
from runtime_coordination.coordination_integrity_models import (  # noqa: E402
    INTEGRITY_STATE_BLOCKED,
    INTEGRITY_STATE_EXPERIMENTAL,
    INTEGRITY_STATE_NON_EXECUTABLE,
    INTEGRITY_STATE_PLANNING_ONLY,
    INTEGRITY_STATE_PROHIBITED,
    INTEGRITY_STATE_SATISFIED,
    INTEGRITY_STATE_UNKNOWN,
    INTEGRITY_STATE_UNSUPPORTED,
    INTEGRITY_STATE_VIOLATED,
    hash_v3_8_integrity_audit,
    validate_v3_8_integrity_hash_stability,
    validate_v3_8_integrity_serialization_stability,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_integrity_enforcement_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = enforce_v3_8_coordination_integrity()
    serialization = validate_v3_8_integrity_serialization_stability(audit)
    hashing = validate_v3_8_integrity_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_integrity_enforcement_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_integrity_enforcement",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic audit-only integrity enforcement across foundation, boundary, "
            "compatibility, evaluation, session, scenario, and aggregation evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "source_scenario_audit_id": audit.source_scenario_audit_id,
        "source_aggregation_audit_id": audit.source_aggregation_audit_id,
        "immutable_audit_evidence_records": audit.immutable_audit_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "runtime_enforcement_engine_enabled": audit.runtime_enforcement_engine_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "ranking_enabled": audit.ranking_enabled,
        "scoring_enabled": audit.scoring_enabled,
        "selection_enabled": audit.selection_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "integrity_runtime_state_machine_enabled": audit.integrity_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "integrity_totals": {
            "integrity_result_count": totals["integrity_result_count"],
            "satisfied_count": totals["satisfied_count"],
            "violated_count": totals["violated_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "foundation_context_count": totals["foundation_context_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "session_context_count": totals["session_context_count"],
            "scenario_context_count": totals["scenario_context_count"],
            "aggregation_context_count": totals["aggregation_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "integrity_violation_count": totals["integrity_violation_count"],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "violated_fail_visible": totals["fail_visible_violated_count"] == totals["violated_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "integrity_violation_count": totals["integrity_violation_count"],
        },
        "context_guarantees": {
            "foundation_context_count": totals["foundation_context_count"],
            "foundation_context_preserved_count": totals["foundation_context_preserved_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "boundary_context_preserved_count": totals["boundary_context_preserved_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "compatibility_context_preserved_count": totals["compatibility_context_preserved_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "evaluation_context_preserved_count": totals["evaluation_context_preserved_count"],
            "session_context_count": totals["session_context_count"],
            "session_context_preserved_count": totals["session_context_preserved_count"],
            "scenario_context_count": totals["scenario_context_count"],
            "scenario_context_preserved_count": totals["scenario_context_preserved_count"],
            "aggregation_context_count": totals["aggregation_context_count"],
            "aggregation_context_preserved_count": totals["aggregation_context_preserved_count"],
            "all_results_preserve_context": (
                totals["foundation_context_count"]
                == totals["boundary_context_count"]
                == totals["compatibility_context_count"]
                == totals["evaluation_context_count"]
                == totals["session_context_count"]
                == totals["scenario_context_count"]
                == totals["aggregation_context_count"]
                == totals["integrity_result_count"]
            ),
        },
        "deterministic_guarantees": {
            "integrity_serialization_stable": serialization["stable"],
            "integrity_hash_stable": hashing["stable"],
            "integrity_hash": hash_v3_8_integrity_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["integrity_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["integrity_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["integrity_result_count"],
        },
        "integrity_record_guarantees": {
            "immutable_audit_evidence_record_count": totals[
                "immutable_audit_evidence_record_count"
            ],
            "all_integrity_records_are_immutable_audit_evidence_records": totals[
                "immutable_audit_evidence_record_count"
            ]
            == totals["integrity_result_count"],
            "runtime_enforcement_state_machine_count": totals[
                "runtime_enforcement_state_machine_count"
            ],
            "integrity_records_are_not_runtime_state_machines": totals[
                "runtime_enforcement_state_machine_count"
            ]
            == 0,
        },
        "contamination_guarantees": {
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
            "recommendation_behavior_violation_count": totals[
                "recommendation_behavior_violation_count"
            ],
            "optimization_behavior_violation_count": totals[
                "optimization_behavior_violation_count"
            ],
            "ranking_behavior_violation_count": totals["ranking_behavior_violation_count"],
        },
        "non_execution_guarantees": {
            "coordination_execution_absent": not audit.coordination_execution_enabled,
            "orchestration_execution_absent": not audit.orchestration_execution_enabled,
            "runtime_enforcement_engine_absent": not audit.runtime_enforcement_engine_enabled,
            "routing_absent": not audit.routing_enabled,
            "scheduling_absent": not audit.scheduling_enabled,
            "dispatch_absent": not audit.dispatch_enabled,
            "traversal_execution_absent": not audit.traversal_execution_enabled,
            "optimization_absent": not audit.optimization_enabled,
            "recommendation_absent": not audit.recommendation_enabled,
            "ranking_absent": not audit.ranking_enabled,
            "scoring_absent": not audit.scoring_enabled,
            "selection_absent": not audit.selection_enabled,
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "integrity_runtime_state_machine_absent": not audit.integrity_runtime_state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_integrity_enforcement": export_v3_8_coordination_integrity_enforcement_audit(
            audit
        ),
        "integrity_state_semantics": {
            INTEGRITY_STATE_SATISFIED: "deterministic evidence satisfies integrity expectations",
            INTEGRITY_STATE_VIOLATED: "deterministic evidence shows an integrity violation",
            INTEGRITY_STATE_BLOCKED: "integrity enforcement is blocked by prior coordination findings",
            INTEGRITY_STATE_UNSUPPORTED: "integrity enforcement includes unsupported coordination states",
            INTEGRITY_STATE_PROHIBITED: "integrity enforcement includes prohibited coordination states",
            INTEGRITY_STATE_UNKNOWN: "insufficient deterministic evidence exists",
            INTEGRITY_STATE_EXPERIMENTAL: "explicitly labeled experimental integrity audit only",
            INTEGRITY_STATE_PLANNING_ONLY: "audit-only, no runtime execution",
            INTEGRITY_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 8 is audit-only integrity enforcement",
            "v3.8 Phase 8 does not enable runtime enforcement engines",
            "v3.8 Phase 8 does not enable coordination execution",
            "v3.8 Phase 8 does not enable orchestration execution",
            "v3.8 Phase 8 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 8 does not enable optimization or recommendations",
            "v3.8 Phase 8 does not enable ranking, scoring, or selection",
            "v3.8 Phase 8 does not enable authorization",
            "v3.8 Phase 8 does not enable runtime engines or state machines",
            "v3.8 Phase 8 does not enable callable coordination flows",
            "v3.8 Phase 8 does not enable persistent runtime mutation",
            "v3.8 Phase 8 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "integrity_result_count": totals["integrity_result_count"],
            "integrity_violation_count": totals["integrity_violation_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "violated_fail_visible": totals["fail_visible_violated_count"] == totals["violated_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "foundation_context_verified": totals["foundation_context_count"]
            == totals["integrity_result_count"],
            "boundary_context_verified": totals["boundary_context_count"]
            == totals["integrity_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["integrity_result_count"],
            "evaluation_context_verified": totals["evaluation_context_count"]
            == totals["integrity_result_count"],
            "session_context_verified": totals["session_context_count"]
            == totals["integrity_result_count"],
            "scenario_context_verified": totals["scenario_context_count"]
            == totals["integrity_result_count"],
            "aggregation_context_verified": totals["aggregation_context_count"]
            == totals["integrity_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"]
            == totals["integrity_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"]
            == totals["integrity_result_count"],
            "provenance_verified": totals["provenance_continuity_count"]
            == totals["integrity_result_count"],
            "immutable_audit_evidence_records_verified": totals[
                "immutable_audit_evidence_record_count"
            ]
            == totals["integrity_result_count"],
            "runtime_enforcement_state_machine_count": totals[
                "runtime_enforcement_state_machine_count"
            ],
            "hidden_risk_count": totals["hidden_risk_count"],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
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
        "# v3.8 Coordination Integrity Enforcement",
        "",
        "## What Phase 8 Adds",
        "",
        "Phase 8 adds deterministic coordination integrity enforcement by audit across foundation, boundary, compatibility, evaluation, session, scenario, and aggregation evidence.",
        "",
        "Integrity records are immutable audit evidence records. They detect missing context, missing evidence, hidden risk, and contamination without enabling runtime behavior.",
        "",
        "## Audit Enforcement Boundaries",
        "",
        "Integrity enforcement differs from runtime enforcement because it records deterministic audit findings and does not run an enforcement engine.",
        "",
        "Integrity enforcement differs from execution because it does not invoke, authorize, or mutate coordination behavior.",
        "",
        "## Context Preservation Across Phases 1-7",
        "",
        f"- Foundation-context count: `{report['context_guarantees']['foundation_context_count']}`",
        f"- Boundary-context count: `{report['context_guarantees']['boundary_context_count']}`",
        f"- Compatibility-context count: `{report['context_guarantees']['compatibility_context_count']}`",
        f"- Evaluation-context count: `{report['context_guarantees']['evaluation_context_count']}`",
        f"- Session-context count: `{report['context_guarantees']['session_context_count']}`",
        f"- Scenario-context count: `{report['context_guarantees']['scenario_context_count']}`",
        f"- Aggregation-context count: `{report['context_guarantees']['aggregation_context_count']}`",
        f"- All results preserve context: `{report['context_guarantees']['all_results_preserve_context']}`",
        "",
        "## Integrity States",
        "",
        "- `satisfied` means deterministic evidence satisfies integrity expectations.",
        "- `violated` means deterministic evidence shows an integrity violation.",
        "- `blocked` means integrity enforcement is blocked by prior coordination findings.",
        "- `unsupported` means integrity enforcement includes unsupported coordination states.",
        "- `prohibited` means integrity enforcement includes prohibited coordination states.",
        "- `unknown` means insufficient deterministic evidence exists.",
        "- `experimental` means explicitly labeled experimental integrity audit only.",
        "- `planning_only` means audit-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Satisfied State Differences",
        "",
        "Violated records contain explicit violation codes.",
        "",
        "Blocked records are stopped by prior coordination findings.",
        "",
        "Unsupported records include unsupported coordination states.",
        "",
        "Prohibited records include intentionally forbidden coordination states.",
        "",
        "Unknown records lack sufficient deterministic evidence.",
        "",
        "All non-satisfied states remain fail-visible.",
        "",
        "## Hidden-Risk Detection",
        "",
        "Hidden-risk detection counts hidden unsupported, prohibited, unknown, blocked, execution-contaminated, and decision-contaminated evidence. No detected violation is silently ignored.",
        "",
        f"- Hidden-risk count: `{report['integrity_totals']['hidden_risk_count']}`",
        f"- Integrity-violation count: `{report['integrity_totals']['integrity_violation_count']}`",
        "",
        "## Integrity Totals",
        "",
        f"- Integrity result count: `{report['integrity_totals']['integrity_result_count']}`",
        f"- Satisfied count: `{report['integrity_totals']['satisfied_count']}`",
        f"- Violated count: `{report['integrity_totals']['violated_count']}`",
        f"- Blocked count: `{report['integrity_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['integrity_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['integrity_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['integrity_totals']['unknown_count']}`",
        f"- Experimental count: `{report['integrity_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['integrity_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['integrity_totals']['non_executable_count']}`",
        f"- Execution-boundary violations: `{report['integrity_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Violated fail-visible: `{report['visibility_guarantees']['violated_fail_visible']}`",
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
        f"- Integrity hash: `{report['deterministic_guarantees']['integrity_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Why This Remains Non-Executable",
        "",
        f"- Runtime enforcement engine absent: `{report['non_execution_guarantees']['runtime_enforcement_engine_absent']}`",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Recommendation absent: `{report['non_execution_guarantees']['recommendation_absent']}`",
        f"- Optimization absent: `{report['non_execution_guarantees']['optimization_absent']}`",
        f"- Ranking absent: `{report['non_execution_guarantees']['ranking_absent']}`",
        f"- Scoring absent: `{report['non_execution_guarantees']['scoring_absent']}`",
        f"- Selection absent: `{report['non_execution_guarantees']['selection_absent']}`",
        f"- State machine absent: `{report['non_execution_guarantees']['state_machine_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 8 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Runtime enforcement engines.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Authorization.",
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
        / "v3_8_coordination_integrity_enforcement_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_INTEGRITY_ENFORCEMENT.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_integrity_enforcement_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
