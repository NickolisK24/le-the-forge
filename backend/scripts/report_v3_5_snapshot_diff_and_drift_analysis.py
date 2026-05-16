"""Generate the v3.5 snapshot diff and drift analysis report."""

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
    SNAPSHOT_DIFF_BLOCKED_BY_HASH_MISMATCH,
    SNAPSHOT_DIFF_BLOCKED_BY_LINEAGE_CHANGE,
    SNAPSHOT_DIFF_BLOCKED_BY_REPLAY_INSTABILITY,
    SNAPSHOT_DIFF_CHANGED_WITHOUT_DRIFT,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_DIFF_PROHIBITED,
    SNAPSHOT_DIFF_REPLAY_SAFETY_COMPROMISED,
    SNAPSHOT_DIFF_REQUIRES_MANUAL_REVIEW,
    SNAPSHOT_DIFF_STABLE,
    SNAPSHOT_DIFF_STATUSES,
    SNAPSHOT_DIFF_UNSUPPORTED,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_UNSUPPORTED,
    analyze_orchestration_snapshot_diff,
    default_orchestration_snapshot_diff_input,
    export_orchestration_snapshot_diff_result,
    export_snapshot_diff_priority_order,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_snapshot_diff_and_drift_analysis_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_stable_snapshot_comparison"]
    report = {
        "schema_version": "v3_5.snapshot_diff_and_drift_analysis_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_7_snapshot_diff_and_drift_analysis_contracts",
        "planning_only": True,
        "non_production": True,
        "final_diff_status": focused["diff_status"],
        "diff_statuses_supported": list(SNAPSHOT_DIFF_STATUSES),
        "priority_order": export_snapshot_diff_priority_order(),
        "priority_order_documentation": [
            "prohibited diff states dominate all other diff states",
            "unsupported diff states dominate replay-safety blockers",
            "replay safety compromise dominates lineage, replay instability, hash mismatch, and drift",
            "lineage change blockers dominate replay instability and hash mismatch",
            "replay instability dominates hash mismatch",
            "hash mismatch dominates drift detection",
            "drift detection dominates manual review",
            "manual review dominates changed-without-drift",
            "changed-without-drift dominates stable",
            "stable is selected only when no higher-priority diff constraints exist",
        ],
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "readiness_diff_summary": _diff_summary(scenarios, "readiness_diffs"),
        "dependency_diff_summary": _diff_summary(scenarios, "dependency_diffs"),
        "coordination_diff_summary": _diff_summary(scenarios, "coordination_diffs"),
        "visibility_diff_summary": _diff_summary(scenarios, "visibility_diffs"),
        "blocker_diff_summary": _diff_summary(scenarios, "blocker_diffs"),
        "unsupported_prohibited_diff_summary": _diff_summary(scenarios, "unsupported_prohibited_diffs"),
        "lineage_diff_summary": _diff_summary(scenarios, "lineage_diffs"),
        "compatibility_diff_summary": _diff_summary(scenarios, "compatibility_diffs"),
        "environment_diff_summary": _diff_summary(scenarios, "environment_diffs"),
        "replay_safety_summary": _list_summary(scenarios, "replay_safety_diffs"),
        "drift_classification_summary": _list_summary(scenarios, "drift_classifications"),
        "manual_review_summary": _list_summary(scenarios, "manual_review_diffs"),
        "limitation_diff_summary": _diff_summary(scenarios, "limitation_diffs"),
        "deterministic_diff_hash_examples": {
            scenario_id: result["deterministic_diff_hash"] for scenario_id, result in scenarios.items()
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
            "runtime_trace_capture_enabled": False,
            "production_state_reads_enabled": False,
            "live_replay_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(SNAPSHOT_DIFF_STATUSES),
            "stable_scenario_count": sum(1 for result in scenarios.values() if result["diff_status"] == SNAPSHOT_DIFF_STABLE),
            "changed_or_blocked_scenario_count": sum(1 for result in scenarios.values() if result["diff_status"] != SNAPSHOT_DIFF_STABLE),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_diff_hashing": True,
            "priority_order_status_selection": True,
            "replay_safe_planning_evidence": True,
            "rollback_safe_planning_evidence": True,
        },
        "remaining_limitations": [
            "snapshot diff analysis compares declarative planning snapshots only",
            "snapshot diff analysis does not approve replay or orchestration planning states",
            "snapshot diff analysis does not execute, route, mutate, write, schedule, or dispatch orchestration",
            "snapshot diff analysis does not perform live replay, capture runtime traces, or read production state",
        ],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Snapshot Diff and Drift Analysis",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 7 is a deterministic orchestration planning snapshot diff and drift-analysis layer.",
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
        "It does not capture runtime traces.",
        "",
        "It does not read production state.",
        "",
        "It does not perform live replay execution.",
        "",
        "It only compares declarative orchestration planning snapshots and explains deterministic planning-state drift.",
        "",
        f"- Final diff status: `{report['final_diff_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Deterministic diff hash: `{report['scenario_results']['fully_stable_snapshot_comparison']['deterministic_diff_hash']}`",
        "",
        "## Supported Diff Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["diff_statuses_supported"])
    lines.extend(["", "## Deterministic Priority Order", ""])
    lines.extend(f"- `{status}`" for status in report["priority_order"])
    lines.extend(
        [
            "",
            "## Diff Input Model",
            "",
            "Inputs include source and target planning snapshots, expected snapshot hashes, replay stability, deterministic serialization verification, manual review, and explicit limitations.",
            "",
            "## Diff Output Model",
            "",
            "Outputs include final diff status, field-level diffs, replay-safety diffs, drift classifications, deterministic drift summary, deterministic explanation summary, and deterministic diff hash.",
            "",
            "## Replay-Safety Model",
            "",
            "Replay safety is modeled through snapshot hash stability, deterministic serialization preservation, lineage preservation, blocker preservation, unsupported/prohibited preservation, compatibility preservation, and environment preservation.",
            "",
            "## Drift Classification Model",
            "",
            "Drift classifications include governance, lineage, blocker, compatibility, environment, unsupported-state, prohibited-state, replay, hash, and limitation drift.",
            "",
            "## Lineage Diff Model",
            "",
            "Replay lineage, rollback lineage, and lineage gap changes remain explicit and fail-visible.",
            "",
            "## Blocker Diff Model",
            "",
            "Blocker changes are preserved without hidden inference or remediation.",
            "",
            "## Unsupported and Prohibited Diff Model",
            "",
            "Unsupported and prohibited states have high-priority statuses and cannot be silently suppressed.",
            "",
            "## Compatibility and Environment Diff Model",
            "",
            "Compatibility and environment changes remain distinct diff categories.",
            "",
            "## Manual-Review Diff Model",
            "",
            "Manual review remains explicit and does not approve replay, execution, or orchestration.",
            "",
            "## Deterministic Diff Hash Behavior",
            "",
            "Diff hashes use stable JSON serialization over caller-provided identifiers, snapshot hashes, diff categories, drift classifications, and replay-safety signals.",
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
        lines.append(f"- `{scenario_id}` -> `{result['diff_status']}`")
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
            "- Runtime trace capture remains prohibited.",
            "- Production state reads remain prohibited.",
            "- Live replay remains prohibited.",
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
    base = default_orchestration_snapshot_diff_input()
    target = base.target_snapshot
    changed_hash_target = replace(target, deterministic_snapshot_hash="changed-without-drift-hash")
    lineage_target = replace(target, replay_lineage_references=("changed-replay-lineage",))
    prohibited_target = replace(target, snapshot_status=SNAPSHOT_PROHIBITED, prohibited_state_summary=("runtime_execution",))
    unsupported_target = replace(target, snapshot_status=SNAPSHOT_UNSUPPORTED, unsupported_state_summary=("unsupported_diff_state",))
    governance_target = replace(
        target,
        readiness_state_reference=replace(target.readiness_state_reference, reference_status="blocked_by_governance_dependency"),
    )
    compatibility_target = replace(target, compatibility_references=("changed-compatibility-reference",))
    multiple_target = replace(
        target,
        snapshot_status=SNAPSHOT_PROHIBITED,
        prohibited_state_summary=("runtime_execution",),
        replay_lineage_references=("changed-replay-lineage",),
        deterministic_snapshot_hash="multiple-drift-hash",
    )
    scenarios = {
        "fully_stable_snapshot_comparison": base,
        "changed_snapshot_without_drift": replace(
            base,
            target_snapshot=changed_hash_target,
            expected_target_snapshot_hash=changed_hash_target.deterministic_snapshot_hash,
        ),
        "lineage_change_blocker": replace(
            base,
            target_snapshot=lineage_target,
            expected_target_snapshot_hash=lineage_target.deterministic_snapshot_hash,
        ),
        "replay_instability_detection": replace(base, replay_stability_verified=False),
        "hash_mismatch_detection": replace(base, expected_target_snapshot_hash="unexpected-target-snapshot-hash"),
        "prohibited_diff_state": replace(
            base,
            target_snapshot=prohibited_target,
            expected_target_snapshot_hash=prohibited_target.deterministic_snapshot_hash,
        ),
        "unsupported_diff_state": replace(
            base,
            target_snapshot=unsupported_target,
            expected_target_snapshot_hash=unsupported_target.deterministic_snapshot_hash,
        ),
        "governance_drift_detection": replace(
            base,
            target_snapshot=governance_target,
            expected_target_snapshot_hash=governance_target.deterministic_snapshot_hash,
        ),
        "compatibility_drift_detection": replace(
            base,
            target_snapshot=compatibility_target,
            expected_target_snapshot_hash=compatibility_target.deterministic_snapshot_hash,
        ),
        "replay_safety_compromise": replace(base, deterministic_serialization_verified=False),
        "multiple_simultaneous_drift_constraints": replace(
            base,
            target_snapshot=multiple_target,
            expected_target_snapshot_hash="unexpected-target-snapshot-hash",
            replay_stability_verified=False,
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_drift_review",),
        ),
    }
    return {
        scenario_id: export_orchestration_snapshot_diff_result(analyze_orchestration_snapshot_diff(source))
        for scenario_id, source in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {status: sum(1 for result in results.values() if result["diff_status"] == status) for status in SNAPSHOT_DIFF_STATUSES}


def _diff_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_diffs_count": sum(1 for result in results.values() if result[field]),
        "diff_entry_count": sum(len(result[field]) for result in results.values()),
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
        default=Path("docs/generated/v3_5_snapshot_diff_and_drift_analysis_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_SNAPSHOT_DIFF_AND_DRIFT_ANALYSIS.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_snapshot_diff_and_drift_analysis_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
