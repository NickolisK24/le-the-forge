"""Generate the v3.5 orchestration coordination planning report."""

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
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    COORDINATION_BLOCKED_BY_ENVIRONMENT_MISMATCH,
    COORDINATION_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_INCOMPATIBLE,
    COORDINATION_PROHIBITED,
    COORDINATION_READY_FOR_PLANNING,
    COORDINATION_REQUIRES_MANUAL_REVIEW,
    COORDINATION_STATUSES,
    COORDINATION_UNSUPPORTED,
    default_orchestration_coordination_graph,
    default_orchestration_coordination_planning_input,
    export_orchestration_coordination_planning_result,
    plan_orchestration_coordination,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_coordination_planning_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_coordinated_planning_graph"]
    report = {
        "schema_version": "v3_5.orchestration_coordination_planning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_4_orchestration_coordination_planning_contracts",
        "planning_only": True,
        "non_production": True,
        "final_coordination_planning_status": focused["coordination_status"],
        "coordination_statuses_supported": list(COORDINATION_STATUSES),
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "coordination_graph_summaries": {
            "scenario_count": len(scenarios),
            "graph_count": len(scenarios),
            "non_executable_graphs": True,
        },
        "dependency_chain_summaries": _list_summary(scenarios, "dependency_chains"),
        "blocker_propagation_summaries": _list_summary(scenarios, "propagated_blockers"),
        "unsupported_state_propagation_summaries": _list_summary(scenarios, "propagated_unsupported_states"),
        "prohibited_state_propagation_summaries": _list_summary(scenarios, "propagated_prohibited_states"),
        "lineage_aggregation_summaries": _list_summary(scenarios, "propagated_lineage_gaps"),
        "compatibility_propagation_summaries": _list_summary(scenarios, "propagated_compatibility_failures"),
        "environment_propagation_summaries": _list_summary(scenarios, "propagated_environment_mismatches"),
        "manual_review_propagation_summaries": _list_summary(scenarios, "propagated_manual_review_states"),
        "explicit_non_execution_guarantees": {
            "runtime_execution_enabled": False,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "mutation_behavior_enabled": False,
            "audit_log_writing_enabled": False,
            "production_consumption_enabled": False,
            "graph_execution_enabled": False,
            "graph_traversal_execution_enabled": False,
            "scheduling_behavior_enabled": False,
            "orchestration_dispatch_enabled": False,
            "coordination_auto_resolution_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(COORDINATION_STATUSES),
            "ready_scenario_count": sum(
                1 for result in scenarios.values() if result["coordination_status"] == COORDINATION_READY_FOR_PLANNING
            ),
            "blocked_or_review_scenario_count": sum(
                1 for result in scenarios.values() if result["coordination_status"] != COORDINATION_READY_FOR_PLANNING
            ),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "coordination_graph_stability": True,
            "replay_safe_lineage_visibility": True,
            "rollback_safe_lineage_visibility": True,
            "fail_visible_coordination_blockers": True,
        },
        "remaining_limitations": [
            "coordination planning models declarative relationships only",
            "coordination planning does not execute graph nodes",
            "coordination planning does not traverse graphs automatically",
            "coordination planning does not schedule or dispatch orchestration",
            "coordination planning does not authorize orchestration",
        ],
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Coordination Planning",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 4 is a deterministic orchestration coordination planning layer.",
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
        "It only models declarative orchestration coordination relationships for future controlled orchestration planning.",
        "",
        f"- Final coordination planning status: `{report['final_coordination_planning_status']}`",
        f"- Deterministic hash: `{report['deterministic_hash']}`",
        "",
        "## Supported Coordination Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["coordination_statuses_supported"])
    lines.extend(
        [
            "",
            "## Coordination Graph Model",
            "",
            "Coordination graphs contain explicit scope IDs, graph IDs, node IDs, edge IDs, dependency references, sequencing rules, and non-execution flags.",
            "",
            "## Coordination Node and Edge Model",
            "",
            "Nodes describe planning scopes and their dependency, blocker, unsupported, prohibited, manual-review, lineage, environment, and compatibility references. Edges describe ordering relationships only.",
            "",
            "## Dependency-Chain Model",
            "",
            "Dependency chains are serialized from source node, target node, dependency reference, and sequencing rule. They do not execute or dispatch nodes.",
            "",
            "## Blocker Propagation Model",
            "",
            "Blockers are aggregated from coordination nodes and remain fail-visible and audit-safe.",
            "",
            "## Unsupported and Prohibited Propagation Model",
            "",
            "Unsupported and prohibited coordination states are propagated explicitly and never silently converted into ready status.",
            "",
            "## Lineage Aggregation Model",
            "",
            "Lineage aggregation includes upstream scopes, downstream scopes, replay lineage, rollback lineage, governance lineage, compatibility lineage, and environment lineage.",
            "",
            "## Compatibility Propagation Model",
            "",
            "Compatibility gaps remain explicit propagated failures and never authorize coordination.",
            "",
            "## Environment Propagation Model",
            "",
            "Environment mismatches remain explicit propagated failures preserving non-production isolation.",
            "",
            "## Deterministic Hash Behavior",
            "",
            "Report and result hashes use stable JSON serialization with sorted keys. The report avoids timestamps in dynamic structures, environment-dependent values, random IDs, and runtime-generated UUIDs.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['coordination_status']}`")
    lines.extend(
        [
            "",
            "## Explicit Non-Execution Guarantees",
            "",
            "- Runtime execution remains prohibited.",
            "- Orchestration execution remains prohibited.",
            "- Graph execution remains prohibited.",
            "- Scheduling behavior remains prohibited.",
            "- Orchestration dispatch remains prohibited.",
            "- Routing behavior remains prohibited.",
            "- Mutation behavior remains prohibited.",
            "- Audit log writing remains prohibited.",
            "- Production consumption remains prohibited.",
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
    base = default_orchestration_coordination_planning_input()
    graph = default_orchestration_coordination_graph()
    first_node = graph.nodes[0]
    second_node = graph.nodes[1]
    third_node = graph.nodes[2]
    lineage_gap_graph = replace(graph, replay_lineage_aggregation=(), rollback_lineage_aggregation=())
    scenarios = {
        "fully_coordinated_planning_graph": base,
        "dependency_chain_blocker_propagation": replace(
            base,
            graph=replace(graph, nodes=(replace(first_node, blocker_reasons=("dependency_chain_blocker",)), second_node, third_node)),
        ),
        "unsupported_coordination_scope": replace(
            base,
            graph=replace(graph, nodes=(replace(first_node, unsupported_reasons=("unsupported_coordination_scope",)), second_node, third_node)),
        ),
        "prohibited_coordination_scope": replace(
            base,
            graph=replace(
                graph,
                coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation"),
            ),
        ),
        "lineage_aggregation_gap": replace(base, graph=lineage_gap_graph),
        "compatibility_propagation_failure": replace(
            base,
            graph=replace(graph, nodes=(replace(first_node, compatibility_references=()), second_node, third_node)),
        ),
        "environment_propagation_mismatch": replace(
            base,
            graph=replace(graph, nodes=(replace(first_node, environment_references=()), second_node, third_node)),
        ),
        "manual_review_propagation": replace(
            base,
            graph=replace(graph, nodes=(replace(first_node, manual_review_reasons=("coordination_owner_review_required",)), second_node, third_node)),
        ),
        "multi_scope_dependency_aggregation": replace(
            base,
            graph=replace(
                graph,
                nodes=(
                    replace(first_node, dependency_references=("v3_5_governance_consumption_contract", "v3_4_closeout_and_v3_5_readiness")),
                    second_node,
                    third_node,
                ),
            ),
        ),
        "cross_scope_lineage_aggregation": replace(
            base,
            graph=replace(
                graph,
                upstream_coordination_scopes=("coordination-scope-governance-consumption", "coordination-scope-readiness-evaluation"),
                downstream_coordination_scopes=("coordination-scope-dependency-resolution", "coordination-scope-phase-4-coordination"),
                governance_lineage_aggregation=(
                    "v3_5_governance_consumption_contract",
                    "v3_5_orchestration_readiness_evaluation",
                    "v3_5_governance_dependency_resolution",
                    "v3_5_orchestration_coordination_planning",
                ),
            ),
        ),
        "multiple_simultaneous_propagated_blockers": replace(
            base,
            graph=replace(
                lineage_gap_graph,
                coordination_scope_ids=("runtime_execution", "coordination-scope-readiness-evaluation"),
                nodes=(
                    replace(
                        first_node,
                        blocker_reasons=("dependency_chain_blocker",),
                        unsupported_reasons=("unsupported_coordination_scope",),
                        manual_review_reasons=("coordination_owner_review_required",),
                        compatibility_references=(),
                        environment_references=(),
                    ),
                    second_node,
                    third_node,
                ),
            ),
        ),
    }
    return {
        scenario_id: export_orchestration_coordination_planning_result(plan_orchestration_coordination(source))
        for scenario_id, source in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["coordination_status"] == status)
        for status in COORDINATION_STATUSES
    }


def _list_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_entries_count": sum(1 for result in results.values() if result[field]),
        "entry_count": sum(len(result[field]) for result in results.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_5_orchestration_coordination_planning_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_COORDINATION_PLANNING.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_coordination_planning_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
