"""Generate the v3.5 orchestration visibility aggregation report."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration import (  # noqa: E402
    VISIBILITY_BLOCKED_BY_COMPATIBILITY_FAILURE,
    VISIBILITY_BLOCKED_BY_COORDINATION,
    VISIBILITY_BLOCKED_BY_DEPENDENCY,
    VISIBILITY_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    VISIBILITY_BLOCKED_BY_LINEAGE_GAP,
    VISIBILITY_BLOCKED_BY_READINESS,
    VISIBILITY_PROHIBITED,
    VISIBILITY_READY_FOR_PLANNING,
    VISIBILITY_REQUIRES_MANUAL_REVIEW,
    VISIBILITY_STATUSES,
    VISIBILITY_UNSUPPORTED,
    aggregate_orchestration_visibility,
    default_governance_dependency_contract,
    default_governance_dependency_resolution_input,
    default_governance_consumption_contract,
    default_orchestration_coordination_graph,
    default_orchestration_coordination_planning_input,
    default_orchestration_readiness_evaluation_input,
    default_orchestration_visibility_aggregation_input,
    evaluate_orchestration_readiness,
    export_orchestration_visibility_aggregation_result,
    export_visibility_priority_order,
    plan_orchestration_coordination,
    resolve_governance_dependency,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_visibility_aggregation_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_visible_ready_planning_state"]
    report = {
        "schema_version": "v3_5.orchestration_visibility_aggregation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_5_orchestration_visibility_aggregation_contracts",
        "planning_only": True,
        "non_production": True,
        "final_visibility_aggregation_status": focused["aggregate_visibility_status"],
        "aggregate_visibility_statuses_supported": list(VISIBILITY_STATUSES),
        "priority_order": export_visibility_priority_order(),
        "priority_order_documentation": [
            "prohibited states dominate all other visibility states",
            "unsupported states dominate blockers",
            "readiness blockers dominate dependency and coordination blockers",
            "dependency blockers dominate coordination blockers",
            "coordination blockers dominate lineage, compatibility, environment, and manual-review states",
            "lineage gaps dominate compatibility and environment failures",
            "compatibility failures dominate environment failures",
            "environment mismatches dominate manual review",
            "manual review dominates ready for planning",
            "ready for planning is selected only when no higher-priority visibility constraints exist",
        ],
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "readiness_aggregation_summary": _source_summary(scenarios, "readiness_summary"),
        "dependency_aggregation_summary": _source_summary(scenarios, "dependency_summary"),
        "coordination_aggregation_summary": _source_summary(scenarios, "coordination_summary"),
        "blocker_aggregation_summary": _list_summary(scenarios, "blocker_summary"),
        "unsupported_state_aggregation_summary": _list_summary(scenarios, "unsupported_state_summary"),
        "prohibited_state_aggregation_summary": _list_summary(scenarios, "prohibited_state_summary"),
        "lineage_gap_aggregation_summary": _list_summary(scenarios, "lineage_gap_summary"),
        "compatibility_failure_aggregation_summary": _list_summary(scenarios, "compatibility_failure_summary"),
        "environment_mismatch_aggregation_summary": _list_summary(scenarios, "environment_mismatch_summary"),
        "manual_review_aggregation_summary": _list_summary(scenarios, "manual_review_summary"),
        "limitation_visibility_summary": _list_summary(scenarios, "limitation_summary"),
        "explicit_non_execution_guarantees": {
            "runtime_execution_enabled": False,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "mutation_behavior_enabled": False,
            "audit_log_writing_enabled": False,
            "production_consumption_enabled": False,
            "graph_execution_enabled": False,
            "graph_traversal_behavior_enabled": False,
            "scheduling_behavior_enabled": False,
            "orchestration_dispatch_enabled": False,
            "auto_approval_behavior_enabled": False,
            "visibility_based_auto_approval_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(VISIBILITY_STATUSES),
            "ready_scenario_count": sum(
                1 for result in scenarios.values() if result["aggregate_visibility_status"] == VISIBILITY_READY_FOR_PLANNING
            ),
            "blocked_or_review_scenario_count": sum(
                1 for result in scenarios.values() if result["aggregate_visibility_status"] != VISIBILITY_READY_FOR_PLANNING
            ),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "priority_order_status_selection": True,
            "fail_visible_orchestration_explanations": True,
            "replay_safe_visibility": True,
            "rollback_safe_visibility": True,
        },
        "remaining_limitations": [
            "visibility aggregation combines declarative planning outputs only",
            "visibility aggregation does not approve orchestration planning states",
            "visibility aggregation does not execute, route, mutate, write, schedule, or dispatch orchestration",
            "visibility aggregation does not perform runtime graph traversal",
        ],
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Visibility Aggregation",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 5 is a deterministic orchestration visibility aggregation layer.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not dispatch orchestration.",
        "",
        "It does not route requests.",
        "",
        "It does not mutate state.",
        "",
        "It does not write audit logs.",
        "",
        "It does not perform graph execution.",
        "",
        "It does not perform orchestration scheduling.",
        "",
        "It does not approve orchestration planning states.",
        "",
        "It only aggregates declarative orchestration planning visibility for future controlled orchestration planning.",
        "",
        f"- Final visibility aggregation status: `{report['final_visibility_aggregation_status']}`",
        f"- Deterministic hash: `{report['deterministic_hash']}`",
        "",
        "## Supported Aggregate Visibility Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["aggregate_visibility_statuses_supported"])
    lines.extend(["", "## Deterministic Priority Order", ""])
    lines.extend(f"- `{status}`" for status in report["priority_order"])
    lines.extend(
        [
            "",
            "## Aggregation Input Model",
            "",
            "Inputs include readiness results, dependency resolution results, coordination planning results, planning graph identity, and explicit limitations.",
            "",
            "## Aggregation Output Model",
            "",
            "Outputs include final visibility status, readiness summary, dependency summary, coordination summary, blocker summary, unsupported/prohibited summaries, lineage/compatibility/environment summaries, manual-review summary, limitation summary, and deterministic explanation summary.",
            "",
            "## Readiness Aggregation Model",
            "",
            "Readiness blockers, unsupported states, prohibited domains, replay and rollback gaps, compatibility failures, environment failures, and manual review reasons are preserved explicitly.",
            "",
            "## Dependency Aggregation Model",
            "",
            "Dependency blockers, unsupported reasons, prohibited reasons, lineage gaps, compatibility failures, environment mismatches, and manual review reasons are preserved explicitly.",
            "",
            "## Coordination Aggregation Model",
            "",
            "Coordination blockers, propagated unsupported/prohibited/manual-review states, propagated lineage gaps, compatibility failures, and environment mismatches are preserved explicitly.",
            "",
            "## Blocker Aggregation Model",
            "",
            "Blockers are aggregated without hidden inference and remain deterministic, sorted, and fail-visible.",
            "",
            "## Unsupported and Prohibited Aggregation Model",
            "",
            "Unsupported and prohibited states have higher priority than blocker summaries and cannot be silently downgraded.",
            "",
            "## Lineage, Compatibility, and Environment Aggregation Model",
            "",
            "Lineage gaps, compatibility failures, and environment mismatches remain distinct visibility summaries.",
            "",
            "## Manual-Review Aggregation Model",
            "",
            "Manual review remains explicit and does not approve execution or planning states.",
            "",
            "## Deterministic Hash Behavior",
            "",
            "Report and result hashes use stable JSON serialization with sorted keys and caller-provided deterministic identifiers.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['aggregate_visibility_status']}`")
    lines.extend(
        [
            "",
            "## Explicit Non-Execution Guarantees",
            "",
            "- Runtime execution remains prohibited.",
            "- Orchestration execution remains prohibited.",
            "- Graph execution remains prohibited.",
            "- Graph traversal remains prohibited.",
            "- Scheduling behavior remains prohibited.",
            "- Orchestration dispatch remains prohibited.",
            "- Routing behavior remains prohibited.",
            "- Mutation behavior remains prohibited.",
            "- Audit log writing remains prohibited.",
            "- Production consumption remains prohibited.",
            "- Auto-approval behavior remains prohibited.",
            "- The repository remains planning-only.",
            "",
            "## Remaining Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["remaining_limitations"])
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_orchestration_visibility_aggregation_input()
    readiness_contract = default_governance_consumption_contract()
    dependency_contract = default_governance_dependency_contract()
    graph = default_orchestration_coordination_graph()
    readiness_blocked = evaluate_orchestration_readiness(
        replace(
            default_orchestration_readiness_evaluation_input(),
            contract=replace(readiness_contract, authorization_state="missing"),
        )
    )
    dependency_blocked = resolve_governance_dependency(
        replace(
            default_governance_dependency_resolution_input(),
            contract=replace(dependency_contract, blocker_reasons=("dependency_visibility_blocker",)),
        )
    )
    coordination_blocked = plan_orchestration_coordination(
        replace(
            default_orchestration_coordination_planning_input(),
            graph=replace(graph, nodes=(replace(graph.nodes[0], blocker_reasons=("coordination_visibility_blocker",)), graph.nodes[1], graph.nodes[2])),
        )
    )
    unsupported_readiness = evaluate_orchestration_readiness(
        replace(
            default_orchestration_readiness_evaluation_input(),
            contract=replace(readiness_contract, unsupported_orchestration_states=("unsupported_visibility_state",)),
        )
    )
    prohibited_coordination = plan_orchestration_coordination(
        replace(
            default_orchestration_coordination_planning_input(),
            graph=replace(graph, coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation")),
        )
    )
    lineage_gap_dependency = replace(
        base.dependency_result,
        lineage_gaps=("manual_replay_lineage_gap", "manual_rollback_lineage_gap"),
    )
    compatibility_dependency = replace(
        base.dependency_result,
        compatibility_failures=("manual_compatibility_failure",),
    )
    environment_coordination = replace(
        base.coordination_result,
        propagated_environment_mismatches=("manual_environment_mismatch",),
    )
    manual_review_readiness = replace(
        base.readiness_result,
        manual_review_reasons=("visibility_manual_review_required",),
    )
    multiple = replace(
        base,
        readiness_result=unsupported_readiness,
        dependency_result=dependency_blocked,
        coordination_result=prohibited_coordination,
    )
    scenarios = {
        "fully_visible_ready_planning_state": base,
        "readiness_blocker_dominates_final_status": replace(base, readiness_result=readiness_blocked),
        "dependency_blocker_dominates_coordination_ready_state": replace(base, dependency_result=dependency_blocked),
        "coordination_blocker_aggregation": replace(base, coordination_result=coordination_blocked),
        "unsupported_state_dominates_blockers": replace(base, readiness_result=unsupported_readiness, dependency_result=dependency_blocked),
        "prohibited_state_dominates_all_other_states": replace(multiple, coordination_result=prohibited_coordination),
        "lineage_gap_aggregation": replace(base, dependency_result=lineage_gap_dependency),
        "compatibility_failure_aggregation": replace(base, dependency_result=compatibility_dependency),
        "environment_mismatch_aggregation": replace(base, coordination_result=environment_coordination),
        "manual_review_aggregation": replace(base, readiness_result=manual_review_readiness),
        "multiple_simultaneous_visibility_constraints": multiple,
    }
    return {
        scenario_id: export_orchestration_visibility_aggregation_result(aggregate_orchestration_visibility(source))
        for scenario_id, source in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["aggregate_visibility_status"] == status)
        for status in VISIBILITY_STATUSES
    }


def _list_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_entries_count": sum(1 for result in results.values() if result[field]),
        "entry_count": sum(len(result[field]) for result in results.values()),
    }


def _source_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "non_ready_source_count": sum(
            1
            for result in results.values()
            if result[field]["blocker_ids"]
            or result[field]["unsupported_entries"]
            or result[field]["prohibited_entries"]
            or result[field]["lineage_gap_entries"]
            or result[field]["compatibility_failure_entries"]
            or result[field]["environment_mismatch_entries"]
            or result[field]["manual_review_entries"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_5_orchestration_visibility_aggregation_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_VISIBILITY_AGGREGATION.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_visibility_aggregation_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
