"""Generate the v3.5 orchestration integrity-audit report."""

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
    AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP,
    COORDINATION_BLOCKED_BY_DEPENDENCY,
    DEPENDENCY_MISSING,
    INTEGRITY_AUDIT_BLOCKED_BY_AUDIT_CHAIN_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_COORDINATION_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DEPENDENCY_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_DIFF_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_GOVERNANCE_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_HASH_INSTABILITY,
    INTEGRITY_AUDIT_BLOCKED_BY_SNAPSHOT_FAILURE,
    INTEGRITY_AUDIT_BLOCKED_BY_VISIBILITY_FAILURE,
    INTEGRITY_AUDIT_INTEGRITY_COMPROMISED,
    INTEGRITY_AUDIT_PROHIBITED,
    INTEGRITY_AUDIT_STABLE,
    INTEGRITY_AUDIT_STATUSES,
    SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    VISIBILITY_BLOCKED_BY_READINESS,
    audit_orchestration_planning_integrity,
    default_orchestration_integrity_audit_input,
    export_integrity_audit_priority_order,
    export_orchestration_integrity_audit_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_integrity_audit_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_stable_orchestration_planning_stack"]
    report = {
        "schema_version": "v3_5.orchestration_integrity_audit_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_9_orchestration_planning_integrity_audit_contracts",
        "planning_only": True,
        "non_production": True,
        "final_integrity_audit_status": focused["integrity_audit_status"],
        "integrity_statuses_supported": list(INTEGRITY_AUDIT_STATUSES),
        "priority_order": export_integrity_audit_priority_order(),
        "priority_order_documentation": [
            "prohibited integrity states dominate all other integrity states",
            "unsupported integrity states dominate integrity compromise and phase failures",
            "integrity compromise dominates phase-specific failures",
            "governance failures dominate dependency failures",
            "dependency failures dominate coordination failures",
            "coordination failures dominate visibility failures",
            "visibility failures dominate snapshot failures",
            "snapshot failures dominate diff/drift failures",
            "diff/drift failures dominate audit-chain failures",
            "audit-chain failures dominate hash instability",
            "hash instability dominates manual review",
            "manual review dominates stable",
            "stable is selected only when no higher-priority integrity constraints exist",
        ],
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "governance_integrity_summary": _integrity_summary(scenarios, "governance_integrity"),
        "readiness_integrity_summary": _integrity_summary(scenarios, "readiness_integrity"),
        "dependency_integrity_summary": _integrity_summary(scenarios, "dependency_integrity"),
        "coordination_integrity_summary": _integrity_summary(scenarios, "coordination_integrity"),
        "visibility_integrity_summary": _integrity_summary(scenarios, "visibility_integrity"),
        "snapshot_integrity_summary": _integrity_summary(scenarios, "snapshot_integrity"),
        "diff_drift_integrity_summary": _integrity_summary(scenarios, "diff_drift_integrity"),
        "audit_chain_integrity_summary": _integrity_summary(scenarios, "audit_chain_integrity"),
        "replay_integrity_summary": _integrity_summary(scenarios, "replay_integrity"),
        "rollback_integrity_summary": _integrity_summary(scenarios, "rollback_integrity"),
        "lineage_integrity_summary": _integrity_summary(scenarios, "lineage_integrity"),
        "serialization_integrity_summary": _integrity_summary(scenarios, "deterministic_serialization_integrity"),
        "hash_stability_summary": _integrity_summary(scenarios, "deterministic_hash_stability"),
        "failure_classification_summary": _list_summary(scenarios, "failure_classification_summary"),
        "manual_review_summary": _list_summary(scenarios, "manual_review_summary"),
        "limitation_summary": _list_summary(scenarios, "limitation_summary"),
        "deterministic_integrity_hash_examples": {
            scenario_id: result["deterministic_integrity_hash"] for scenario_id, result in scenarios.items()
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
            "persistent_audit_storage_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(INTEGRITY_AUDIT_STATUSES),
            "stable_scenario_count": sum(1 for result in scenarios.values() if result["integrity_audit_status"] == INTEGRITY_AUDIT_STABLE),
            "blocked_or_review_scenario_count": sum(1 for result in scenarios.values() if result["integrity_audit_status"] != INTEGRITY_AUDIT_STABLE),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_integrity_hashing": True,
            "priority_order_status_selection": True,
            "replay_safe_integrity_evidence": True,
            "rollback_safe_integrity_evidence": True,
        },
        "remaining_limitations": [
            "integrity auditing validates declarative planning evidence only",
            "integrity auditing does not persist audit state",
            "integrity auditing does not execute, route, mutate, write, schedule, dispatch, traverse, or repair orchestration",
            "integrity auditing does not perform live replay, capture runtime traces, or read production state",
        ],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Integrity Audit",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 9 is a deterministic orchestration planning integrity-audit layer.",
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
        "It does not persist audit state.",
        "",
        "It only validates deterministic orchestration planning integrity across the full v3.5 planning stack.",
        "",
        f"- Final integrity-audit status: `{report['final_integrity_audit_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Deterministic integrity hash: `{report['scenario_results']['fully_stable_orchestration_planning_stack']['deterministic_integrity_hash']}`",
        "",
        "## Supported Integrity Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["integrity_statuses_supported"])
    lines.extend(["", "## Deterministic Priority Order", ""])
    lines.extend(f"- `{status}`" for status in report["priority_order"])
    lines.extend(
        [
            "",
            "## Integrity-Audit Input Model",
            "",
            "Inputs include integrity audit identity, governance references, readiness/dependency/coordination/visibility/snapshot/diff/audit-chain results, replay/rollback/lineage references, expected hash, manual review, unsupported/prohibited reasons, and limitations.",
            "",
            "## Integrity-Audit Output Model",
            "",
            "Outputs include final integrity status, per-domain integrity summaries, failure classifications, blocker summaries, unsupported/prohibited summaries, limitation summaries, manual-review summaries, deterministic integrity hash, and deterministic explanation summary.",
            "",
            "## Replay and Rollback Integrity Model",
            "",
            "Replay and rollback integrity references remain explicit and fail visibly when missing.",
            "",
            "## Provenance Integrity Model",
            "",
            "Provenance integrity is modeled through lineage, audit-chain, snapshot, diff/drift, serialization, and hash continuity.",
            "",
            "## Failure Classification Model",
            "",
            "Failures remain classified by governance, dependency, coordination, visibility, snapshot, diff/drift, audit-chain, replay, rollback, lineage, serialization, and hash-instability domains.",
            "",
            "## Continuity Validation Model",
            "",
            "Continuity validation is declarative only and does not reconstruct, repair, or fetch missing evidence.",
            "",
            "## Serialization and Hash Stability Model",
            "",
            "Integrity hashes and report hashes use stable JSON serialization over caller-provided deterministic evidence.",
            "",
            "## Manual-Review Model",
            "",
            "Manual review remains explicit and does not approve replay, execution, or orchestration.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['integrity_audit_status']}`")
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
            "- Persistent audit storage remains prohibited.",
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
    base = default_orchestration_integrity_audit_input()
    dependency = base.dependency_result
    coordination = base.coordination_result
    visibility = base.visibility_result
    snapshot = base.snapshot_result
    diff = base.diff_result
    audit_chain = base.audit_chain_result
    assert dependency is not None
    assert coordination is not None
    assert visibility is not None
    assert snapshot is not None
    assert diff is not None
    assert audit_chain is not None
    scenarios = {
        "fully_stable_orchestration_planning_stack": base,
        "governance_integrity_failure": replace(base, governance_integrity_references=()),
        "dependency_integrity_failure": replace(base, dependency_result=replace(dependency, dependency_status=DEPENDENCY_MISSING)),
        "coordination_integrity_failure": replace(base, coordination_result=replace(coordination, coordination_status=COORDINATION_BLOCKED_BY_DEPENDENCY)),
        "visibility_integrity_failure": replace(base, visibility_result=replace(visibility, aggregate_visibility_status=VISIBILITY_BLOCKED_BY_READINESS)),
        "snapshot_integrity_failure": replace(base, snapshot_result=replace(snapshot, snapshot_status=SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE)),
        "diff_drift_integrity_failure": replace(base, diff_result=replace(diff, diff_status=SNAPSHOT_DIFF_DRIFT_DETECTED)),
        "audit_chain_integrity_failure": replace(base, audit_chain_result=replace(audit_chain, audit_chain_status=AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP)),
        "replay_continuity_failure": replace(base, replay_integrity_references=()),
        "hash_instability_failure": replace(base, expected_integrity_hash="mismatched-integrity-hash"),
        "multiple_simultaneous_integrity_constraints": replace(
            base,
            governance_integrity_references=(),
            dependency_result=replace(dependency, dependency_status=DEPENDENCY_MISSING),
            coordination_result=replace(coordination, coordination_status=COORDINATION_BLOCKED_BY_DEPENDENCY),
            visibility_result=replace(visibility, aggregate_visibility_status=VISIBILITY_BLOCKED_BY_READINESS),
            snapshot_result=replace(snapshot, snapshot_status=SNAPSHOT_BLOCKED_BY_VISIBILITY_STATE),
            diff_result=replace(diff, diff_status=SNAPSHOT_DIFF_DRIFT_DETECTED),
            audit_chain_result=replace(audit_chain, audit_chain_status=AUDIT_CHAIN_BLOCKED_BY_LINEAGE_GAP),
            replay_integrity_references=(),
            rollback_integrity_references=(),
            lineage_integrity_references=(),
            prohibited_reasons=("runtime_execution",),
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_integrity_review",),
        ),
    }
    return {
        scenario_id: export_orchestration_integrity_audit_result(audit_orchestration_planning_integrity(source_input))
        for scenario_id, source_input in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["integrity_audit_status"] == status)
        for status in INTEGRITY_AUDIT_STATUSES
    }


def _integrity_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "reference_count": sum(len(result[field]["references"]) for result in results.values()),
        "failure_count": sum(len(result[field]["failures"]) for result in results.values()),
        "scenario_with_failures_count": sum(1 for result in results.values() if result[field]["failures"]),
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
        default=Path("docs/generated/v3_5_orchestration_integrity_audit_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_INTEGRITY_AUDIT.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_integrity_audit_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
