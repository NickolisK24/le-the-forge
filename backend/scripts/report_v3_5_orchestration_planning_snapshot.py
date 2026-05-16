"""Generate the v3.5 orchestration planning snapshot report."""

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
    SNAPSHOT_BLOCKED_BY_HASH_INSTABILITY,
    SNAPSHOT_BLOCKED_BY_LINEAGE_GAP,
    SNAPSHOT_BLOCKED_BY_MISSING_COORDINATION_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_DEPENDENCY_STATE,
    SNAPSHOT_BLOCKED_BY_MISSING_READINESS_STATE,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_READY_FOR_REPLAY_PLANNING,
    SNAPSHOT_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_STATUSES,
    SNAPSHOT_UNSUPPORTED,
    VISIBILITY_PROHIBITED,
    VISIBILITY_UNSUPPORTED,
    default_orchestration_planning_snapshot_input,
    export_orchestration_planning_snapshot_result,
    export_snapshot_priority_order,
    generate_orchestration_planning_snapshot,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_planning_snapshot_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_snapshot_ready_planning_state"]
    report = {
        "schema_version": "v3_5.orchestration_planning_snapshot_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_6_orchestration_planning_snapshot_contracts",
        "planning_only": True,
        "non_production": True,
        "final_snapshot_status": focused["snapshot_status"],
        "snapshot_statuses_supported": list(SNAPSHOT_STATUSES),
        "priority_order": export_snapshot_priority_order(),
        "priority_order_documentation": [
            "prohibited snapshot states dominate all other snapshot states",
            "unsupported snapshot states dominate missing-state blockers",
            "missing visibility state dominates missing readiness, dependency, and coordination states",
            "missing readiness state dominates missing dependency and coordination states",
            "missing dependency state dominates missing coordination state",
            "missing coordination state dominates lineage and hash blockers",
            "lineage gaps dominate hash instability",
            "hash instability dominates manual review",
            "manual review dominates ready for replay planning",
            "ready for replay planning is selected only when no higher-priority snapshot constraints exist",
        ],
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "snapshot_generation_summary": {
            "scenario_count": len(scenarios),
            "snapshot_hash_example_count": len({result["deterministic_snapshot_hash"] for result in scenarios.values()}),
        },
        "readiness_preservation_summary": _reference_summary(scenarios, "readiness_state_reference"),
        "dependency_preservation_summary": _reference_summary(scenarios, "dependency_state_reference"),
        "coordination_preservation_summary": _reference_summary(scenarios, "coordination_state_reference"),
        "visibility_preservation_summary": _reference_summary(scenarios, "visibility_aggregation_reference"),
        "blocker_preservation_summary": _list_summary(scenarios, "blocker_summary"),
        "unsupported_prohibited_preservation_summary": {
            "unsupported": _list_summary(scenarios, "unsupported_state_summary"),
            "prohibited": _list_summary(scenarios, "prohibited_state_summary"),
        },
        "lineage_preservation_summary": {
            "lineage_gaps": _list_summary(scenarios, "lineage_summary"),
            "replay_lineage": _list_summary(scenarios, "replay_lineage_references"),
            "rollback_lineage": _list_summary(scenarios, "rollback_lineage_references"),
        },
        "manual_review_preservation_summary": _list_summary(scenarios, "manual_review_summary"),
        "limitation_preservation_summary": _list_summary(scenarios, "limitation_summary"),
        "deterministic_snapshot_hash_examples": {
            scenario_id: result["deterministic_snapshot_hash"] for scenario_id, result in scenarios.items()
        },
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
            "runtime_trace_capture_enabled": False,
            "production_state_reads_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(SNAPSHOT_STATUSES),
            "ready_scenario_count": sum(
                1 for result in scenarios.values() if result["snapshot_status"] == SNAPSHOT_READY_FOR_REPLAY_PLANNING
            ),
            "blocked_or_review_scenario_count": sum(
                1 for result in scenarios.values() if result["snapshot_status"] != SNAPSHOT_READY_FOR_REPLAY_PLANNING
            ),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_snapshot_hashing": True,
            "priority_order_status_selection": True,
            "replay_safe_snapshot_evidence": True,
            "rollback_safe_snapshot_evidence": True,
        },
        "remaining_limitations": [
            "snapshot generation freezes declarative planning outputs only",
            "snapshot generation does not approve orchestration planning states",
            "snapshot generation does not execute, route, mutate, write, schedule, or dispatch orchestration",
            "snapshot generation does not capture runtime traces or read production state",
        ],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Planning Snapshot",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 6 is a deterministic orchestration planning snapshot layer.",
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
        "It does not capture runtime traces.",
        "",
        "It does not read production state.",
        "",
        "It only freezes declarative orchestration planning inputs into deterministic replay-safe snapshot objects.",
        "",
        f"- Final snapshot status: `{report['final_snapshot_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Deterministic snapshot hash: `{report['scenario_results']['fully_snapshot_ready_planning_state']['deterministic_snapshot_hash']}`",
        "",
        "## Supported Snapshot Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["snapshot_statuses_supported"])
    lines.extend(["", "## Deterministic Priority Order", ""])
    lines.extend(f"- `{status}`" for status in report["priority_order"])
    lines.extend(
        [
            "",
            "## Snapshot Input Model",
            "",
            "Inputs include readiness, dependency, coordination, visibility aggregation, replay lineage, rollback lineage, compatibility, environment, limitations, manual review, and hash stability fields.",
            "",
            "## Snapshot Output Model",
            "",
            "Outputs include final snapshot status, state references, blocker summary, unsupported/prohibited summaries, lineage summary, manual-review summary, limitation summary, deterministic snapshot hash, and deterministic explanation summary.",
            "",
            "## Readiness Preservation Model",
            "",
            "Readiness state identity, status, and deterministic hash are preserved as explicit snapshot references.",
            "",
            "## Dependency Preservation Model",
            "",
            "Dependency state identity, status, and deterministic hash are preserved as explicit snapshot references.",
            "",
            "## Coordination Preservation Model",
            "",
            "Coordination graph identity, status, and deterministic hash are preserved as explicit snapshot references.",
            "",
            "## Visibility Preservation Model",
            "",
            "Visibility aggregation identity, status, and deterministic hash are preserved as explicit snapshot references.",
            "",
            "## Blocker Preservation Model",
            "",
            "Blockers are frozen without hidden inference and remain deterministic, sorted, and fail-visible.",
            "",
            "## Unsupported and Prohibited Preservation Model",
            "",
            "Unsupported and prohibited states have higher priority than missing-state and lineage blockers and cannot be silently downgraded.",
            "",
            "## Lineage Preservation Model",
            "",
            "Replay lineage, rollback lineage, and lineage gaps remain explicit and replay-safe.",
            "",
            "## Manual-Review Preservation Model",
            "",
            "Manual review remains explicit and does not approve execution or planning states.",
            "",
            "## Deterministic Snapshot Hash Behavior",
            "",
            "Snapshot hashes use stable JSON serialization over caller-provided identifiers, state references, lineage, blockers, limitations, and hash-stability flags.",
            "",
            "## Deterministic Report Hash Behavior",
            "",
            "Report hashes use stable JSON serialization with sorted keys and deterministic scenario inputs.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['snapshot_status']}`")
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
            "- Runtime trace capture remains prohibited.",
            "- Production state reads remain prohibited.",
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
    base = default_orchestration_planning_snapshot_input()
    visibility = base.visibility_result
    assert visibility is not None
    prohibited_visibility = replace(
        visibility,
        aggregate_visibility_status=VISIBILITY_PROHIBITED,
        prohibited_state_summary=("runtime_execution",),
    )
    unsupported_visibility = replace(
        visibility,
        aggregate_visibility_status=VISIBILITY_UNSUPPORTED,
        unsupported_state_summary=("unsupported_snapshot_state",),
    )
    lineage_visibility = replace(visibility, lineage_gap_summary=("visibility_lineage_gap",))
    manual_visibility = replace(visibility, manual_review_summary=("snapshot_manual_review_required",))
    scenarios = {
        "fully_snapshot_ready_planning_state": base,
        "missing_visibility_state": replace(base, visibility_result=None),
        "missing_readiness_state": replace(base, readiness_result=None),
        "missing_dependency_state": replace(base, dependency_result=None),
        "missing_coordination_state": replace(base, coordination_result=None),
        "prohibited_snapshot_state": replace(base, visibility_result=prohibited_visibility),
        "unsupported_snapshot_state": replace(base, visibility_result=unsupported_visibility),
        "lineage_gap_preservation": replace(base, visibility_result=lineage_visibility, replay_lineage_references=()),
        "hash_instability_blocker": replace(base, hash_stability_verified=False),
        "manual_review_snapshot": replace(base, visibility_result=manual_visibility),
        "multiple_simultaneous_snapshot_constraints": replace(
            base,
            readiness_result=None,
            visibility_result=prohibited_visibility,
            replay_lineage_references=(),
            hash_stability_verified=False,
            manual_review_reasons=("manual_priority_check",),
        ),
    }
    return {
        scenario_id: export_orchestration_planning_snapshot_result(generate_orchestration_planning_snapshot(source))
        for scenario_id, source in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {status: sum(1 for result in results.values() if result["snapshot_status"] == status) for status in SNAPSHOT_STATUSES}


def _list_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_entries_count": sum(1 for result in results.values() if result[field]),
        "entry_count": sum(len(result[field]) for result in results.values()),
    }


def _reference_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "present_count": sum(1 for result in results.values() if result[field] is not None),
        "missing_count": sum(1 for result in results.values() if result[field] is None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_5_orchestration_planning_snapshot_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_PLANNING_SNAPSHOT.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_planning_snapshot_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
