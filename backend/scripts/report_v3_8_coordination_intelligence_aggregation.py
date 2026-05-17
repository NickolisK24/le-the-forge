"""Generate the v3.8 coordination intelligence aggregation report."""

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

from runtime_coordination.coordination_aggregation_models import (  # noqa: E402
    AGGREGATION_STATE_AGGREGATED,
    AGGREGATION_STATE_BLOCKED,
    AGGREGATION_STATE_EXPERIMENTAL,
    AGGREGATION_STATE_NON_EXECUTABLE,
    AGGREGATION_STATE_PARTIAL,
    AGGREGATION_STATE_PLANNING_ONLY,
    AGGREGATION_STATE_PROHIBITED,
    AGGREGATION_STATE_UNKNOWN,
    AGGREGATION_STATE_UNSUPPORTED,
    hash_v3_8_aggregation_audit,
    validate_v3_8_aggregation_hash_stability,
    validate_v3_8_aggregation_serialization_stability,
)
from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402
from runtime_coordination.coordination_intelligence_aggregation import (  # noqa: E402
    aggregate_v3_8_coordination_intelligence,
    export_v3_8_coordination_intelligence_aggregation_audit,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_intelligence_aggregation_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = aggregate_v3_8_coordination_intelligence()
    serialization = validate_v3_8_aggregation_serialization_stability(audit)
    hashing = validate_v3_8_aggregation_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_intelligence_aggregation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_intelligence_aggregation",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic aggregation across foundation, boundary, compatibility, evaluation, "
            "session, and scenario evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "source_scenario_audit_id": audit.source_scenario_audit_id,
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
        "ranking_enabled": audit.ranking_enabled,
        "scoring_choice_system_enabled": audit.scoring_choice_system_enabled,
        "selection_engine_enabled": audit.selection_engine_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "aggregation_runtime_state_machine_enabled": audit.aggregation_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "aggregation_totals": {
            "aggregation_result_count": totals["aggregation_result_count"],
            "aggregated_count": totals["aggregated_count"],
            "partial_count": totals["partial_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "summary_count": totals["summary_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "session_context_count": totals["session_context_count"],
            "scenario_context_count": totals["scenario_context_count"],
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
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "partial_fail_visible": totals["fail_visible_partial_count"] == totals["partial_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "fail_visible_finding_count": totals["fail_visible_finding_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
        },
        "context_guarantees": {
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
            "all_results_preserve_context": (
                totals["boundary_context_count"]
                == totals["compatibility_context_count"]
                == totals["evaluation_context_count"]
                == totals["session_context_count"]
                == totals["scenario_context_count"]
                == totals["aggregation_result_count"]
            ),
        },
        "summary_guarantees": {
            "summary_count": totals["summary_count"],
            "summary_non_execution_confirmation_count": totals[
                "summary_non_execution_confirmation_count"
            ],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_language_violation_count": totals["scoring_language_violation_count"],
            "selection_language_violation_count": totals["selection_language_violation_count"],
            "summary_execution_language_violation_count": totals[
                "summary_execution_language_violation_count"
            ],
            "recommendation_behavior_violation_count": totals[
                "recommendation_behavior_violation_count"
            ],
            "optimization_behavior_violation_count": totals[
                "optimization_behavior_violation_count"
            ],
            "ranking_behavior_violation_count": totals["ranking_behavior_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
        },
        "deterministic_guarantees": {
            "aggregation_serialization_stable": serialization["stable"],
            "aggregation_hash_stable": hashing["stable"],
            "aggregation_hash": hash_v3_8_aggregation_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["aggregation_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["aggregation_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["aggregation_result_count"],
        },
        "aggregation_record_guarantees": {
            "immutable_evidence_record_count": totals["immutable_evidence_record_count"],
            "all_aggregations_are_immutable_evidence_records": totals[
                "immutable_evidence_record_count"
            ]
            == totals["aggregation_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
            "aggregations_are_not_runtime_state_machines": totals["runtime_state_machine_count"]
            == 0,
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
            "ranking_absent": not audit.ranking_enabled,
            "scoring_choice_system_absent": not audit.scoring_choice_system_enabled,
            "selection_engine_absent": not audit.selection_engine_enabled,
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "aggregation_runtime_state_machine_absent": not audit.aggregation_runtime_state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_intelligence_aggregation": export_v3_8_coordination_intelligence_aggregation_audit(
            audit
        ),
        "aggregation_state_semantics": {
            AGGREGATION_STATE_AGGREGATED: "deterministic evidence is complete enough to aggregate",
            AGGREGATION_STATE_PARTIAL: "deterministic evidence is present but incomplete",
            AGGREGATION_STATE_BLOCKED: (
                "aggregation is blocked by boundary, compatibility, evaluation, session, or scenario findings"
            ),
            AGGREGATION_STATE_UNSUPPORTED: "aggregation includes unsupported coordination states",
            AGGREGATION_STATE_PROHIBITED: "aggregation includes prohibited coordination states",
            AGGREGATION_STATE_UNKNOWN: "aggregation includes insufficient deterministic evidence",
            AGGREGATION_STATE_EXPERIMENTAL: "explicitly labeled experimental aggregation only",
            AGGREGATION_STATE_PLANNING_ONLY: "reasoning-only, no runtime execution",
            AGGREGATION_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 7 is aggregation-only",
            "v3.8 Phase 7 does not enable coordination execution",
            "v3.8 Phase 7 does not enable orchestration execution",
            "v3.8 Phase 7 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 7 does not enable optimization or recommendations",
            "v3.8 Phase 7 does not enable selection engines",
            "v3.8 Phase 7 does not enable scoring-based choice systems",
            "v3.8 Phase 7 does not enable execution authorization",
            "v3.8 Phase 7 does not enable runtime engines or state machines",
            "v3.8 Phase 7 does not enable callable execution paths",
            "v3.8 Phase 7 does not enable persistent runtime mutation",
            "v3.8 Phase 7 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "aggregation_result_count": totals["aggregation_result_count"],
            "summary_count": totals["summary_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "partial_fail_visible": totals["fail_visible_partial_count"]
            == totals["partial_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "boundary_context_verified": totals["boundary_context_count"]
            == totals["aggregation_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["aggregation_result_count"],
            "evaluation_context_verified": totals["evaluation_context_count"]
            == totals["aggregation_result_count"],
            "session_context_verified": totals["session_context_count"]
            == totals["aggregation_result_count"],
            "scenario_context_verified": totals["scenario_context_count"]
            == totals["aggregation_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"]
            == totals["aggregation_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"]
            == totals["aggregation_result_count"],
            "provenance_verified": totals["provenance_continuity_count"]
            == totals["aggregation_result_count"],
            "immutable_evidence_records_verified": totals["immutable_evidence_record_count"]
            == totals["aggregation_result_count"],
            "runtime_state_machine_count": totals["runtime_state_machine_count"],
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
        "# v3.8 Coordination Intelligence Aggregation",
        "",
        "## What Phase 7 Adds",
        "",
        "Phase 7 adds deterministic coordination intelligence aggregation across foundation, boundary, compatibility, evaluation, session, and scenario evidence.",
        "",
        "Aggregation records are immutable evidence records. Summaries preserve visibility and coverage without producing decisions.",
        "",
        "## Aggregation Boundaries",
        "",
        "Aggregation differs from execution because it only records evidence coverage and visibility.",
        "",
        "Aggregation differs from optimization because it does not improve, tune, or prefer alternatives.",
        "",
        "Aggregation differs from recommendations because it does not propose an action.",
        "",
        "Aggregation differs from selection because it does not choose a path or alternative.",
        "",
        "## Summary Behavior",
        "",
        "Summaries are deterministic coverage records. They preserve supported, unsupported, prohibited, and unknown visibility while keeping compatibility, evaluation, session, and scenario visibility countable.",
        "",
        f"- Summary count: `{report['summary_guarantees']['summary_count']}`",
        f"- Recommendation-language violations: `{report['summary_guarantees']['recommendation_language_violation_count']}`",
        f"- Optimization-language violations: `{report['summary_guarantees']['optimization_language_violation_count']}`",
        f"- Ranking-language violations: `{report['summary_guarantees']['ranking_language_violation_count']}`",
        f"- Scoring behavior violations: `{report['summary_guarantees']['scoring_behavior_violation_count']}`",
        f"- Selection behavior violations: `{report['summary_guarantees']['selection_behavior_violation_count']}`",
        "",
        "## Aggregation States",
        "",
        "- `aggregated` means deterministic evidence is complete enough to aggregate.",
        "- `partial` means deterministic evidence is present but incomplete.",
        "- `blocked` means aggregation is blocked by boundary, compatibility, evaluation, session, or scenario findings.",
        "- `unsupported` means aggregation includes unsupported coordination states.",
        "- `prohibited` means aggregation includes prohibited coordination states.",
        "- `unknown` means aggregation includes insufficient deterministic evidence.",
        "- `experimental` means explicitly labeled experimental aggregation only.",
        "- `planning_only` means reasoning-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Aggregated State Differences",
        "",
        "Partial aggregations have evidence, but not enough complete deterministic evidence.",
        "",
        "Blocked aggregations are stopped by prior coordination findings.",
        "",
        "Unsupported aggregations include unsupported coordination states.",
        "",
        "Prohibited aggregations include intentionally forbidden coordination states.",
        "",
        "Unknown aggregations lack sufficient deterministic evidence.",
        "",
        "All non-aggregated states remain fail-visible.",
        "",
        "## Context Preservation",
        "",
        f"- Boundary-context count: `{report['context_guarantees']['boundary_context_count']}`",
        f"- Boundary-context preserved count: `{report['context_guarantees']['boundary_context_preserved_count']}`",
        f"- Compatibility-context count: `{report['context_guarantees']['compatibility_context_count']}`",
        f"- Compatibility-context preserved count: `{report['context_guarantees']['compatibility_context_preserved_count']}`",
        f"- Evaluation-context count: `{report['context_guarantees']['evaluation_context_count']}`",
        f"- Evaluation-context preserved count: `{report['context_guarantees']['evaluation_context_preserved_count']}`",
        f"- Session-context count: `{report['context_guarantees']['session_context_count']}`",
        f"- Session-context preserved count: `{report['context_guarantees']['session_context_preserved_count']}`",
        f"- Scenario-context count: `{report['context_guarantees']['scenario_context_count']}`",
        f"- Scenario-context preserved count: `{report['context_guarantees']['scenario_context_preserved_count']}`",
        "",
        "## Aggregation Totals",
        "",
        f"- Aggregation result count: `{report['aggregation_totals']['aggregation_result_count']}`",
        f"- Aggregated count: `{report['aggregation_totals']['aggregated_count']}`",
        f"- Partial count: `{report['aggregation_totals']['partial_count']}`",
        f"- Blocked count: `{report['aggregation_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['aggregation_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['aggregation_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['aggregation_totals']['unknown_count']}`",
        f"- Experimental count: `{report['aggregation_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['aggregation_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['aggregation_totals']['non_executable_count']}`",
        f"- Hidden-risk count: `{report['aggregation_totals']['hidden_risk_count']}`",
        f"- Execution-boundary violations: `{report['aggregation_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Partial fail-visible: `{report['visibility_guarantees']['partial_fail_visible']}`",
        f"- Blocked fail-visible: `{report['visibility_guarantees']['blocked_fail_visible']}`",
        f"- Unsupported fail-visible: `{report['visibility_guarantees']['unsupported_fail_visible']}`",
        f"- Prohibited fail-visible: `{report['visibility_guarantees']['prohibited_fail_visible']}`",
        f"- Unknown fail-visible: `{report['visibility_guarantees']['unknown_fail_visible']}`",
        f"- Fail-visible finding count: `{report['visibility_guarantees']['fail_visible_finding_count']}`",
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
        f"- Aggregation hash: `{report['deterministic_guarantees']['aggregation_hash']}`",
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
        f"- Recommendation absent: `{report['non_execution_guarantees']['recommendation_absent']}`",
        f"- Optimization absent: `{report['non_execution_guarantees']['optimization_absent']}`",
        f"- Ranking absent: `{report['non_execution_guarantees']['ranking_absent']}`",
        f"- Scoring choice system absent: `{report['non_execution_guarantees']['scoring_choice_system_absent']}`",
        f"- Selection engine absent: `{report['non_execution_guarantees']['selection_engine_absent']}`",
        f"- Runtime engine absent: `{report['non_execution_guarantees']['runtime_engine_absent']}`",
        f"- State machine absent: `{report['non_execution_guarantees']['state_machine_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 7 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Selection engines.",
        "- Scoring-based choice systems.",
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
        / "v3_8_coordination_intelligence_aggregation_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_INTELLIGENCE_AGGREGATION.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_intelligence_aggregation_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
