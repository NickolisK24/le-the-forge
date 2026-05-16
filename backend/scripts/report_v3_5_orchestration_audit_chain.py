"""Generate the v3.5 orchestration audit-chain report."""

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
    AUDIT_CHAIN_BLOCKED_BY_MISSING_DIFF_ANALYSIS,
    AUDIT_CHAIN_BLOCKED_BY_MISSING_SNAPSHOT,
    AUDIT_CHAIN_BLOCKED_BY_REPLAY_GAP,
    AUDIT_CHAIN_INTEGRITY_COMPROMISED,
    AUDIT_CHAIN_PROHIBITED,
    AUDIT_CHAIN_REQUIRES_MANUAL_REVIEW,
    AUDIT_CHAIN_STABLE,
    AUDIT_CHAIN_STATUSES,
    AUDIT_CHAIN_UNSUPPORTED,
    SNAPSHOT_DIFF_DRIFT_DETECTED,
    SNAPSHOT_PROHIBITED,
    SNAPSHOT_UNSUPPORTED,
    build_orchestration_audit_chain,
    default_orchestration_audit_chain_input,
    export_audit_chain_priority_order,
    export_orchestration_audit_chain_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_audit_chain_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_stable_audit_chain"]
    report = {
        "schema_version": "v3_5.orchestration_audit_chain_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_8_orchestration_planning_audit_chain_contracts",
        "planning_only": True,
        "non_production": True,
        "final_audit_chain_status": focused["audit_chain_status"],
        "audit_chain_statuses_supported": list(AUDIT_CHAIN_STATUSES),
        "priority_order": export_audit_chain_priority_order(),
        "priority_order_documentation": [
            "prohibited audit-chain states dominate all other audit-chain states",
            "unsupported audit-chain states dominate integrity and missing-state blockers",
            "integrity compromise dominates missing snapshot and missing diff-analysis blockers",
            "missing snapshot dominates missing diff-analysis",
            "missing diff analysis dominates lineage and replay gaps",
            "lineage gaps dominate replay gaps",
            "replay gaps dominate hash instability",
            "hash instability dominates manual review",
            "manual review dominates stable",
            "stable is selected only when no higher-priority audit-chain constraints exist",
        ],
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "snapshot_continuity_summary": _sequence_summary(scenarios, "chain_snapshot_sequence"),
        "diff_analysis_continuity_summary": _sequence_summary(scenarios, "chain_diff_analysis_sequence"),
        "lineage_continuity_summary": _continuity_summary(scenarios, "lineage_continuity"),
        "replay_continuity_summary": _continuity_summary(scenarios, "replay_continuity"),
        "governance_continuity_summary": _continuity_summary(scenarios, "governance_continuity"),
        "blocker_continuity_summary": _continuity_summary(scenarios, "blocker_continuity"),
        "compatibility_continuity_summary": _continuity_summary(scenarios, "compatibility_continuity"),
        "environment_continuity_summary": _continuity_summary(scenarios, "environment_continuity"),
        "integrity_validation_summary": _list_summary(scenarios, "integrity_summary"),
        "lineage_gap_summary": _list_summary(scenarios, "lineage_gap_summary"),
        "replay_gap_summary": _list_summary(scenarios, "replay_gap_summary"),
        "manual_review_summary": _list_summary(scenarios, "manual_review_summary"),
        "limitation_summary": _list_summary(scenarios, "limitation_summary"),
        "deterministic_audit_chain_hash_examples": {
            scenario_id: result["deterministic_audit_chain_hash"] for scenario_id, result in scenarios.items()
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
            "supported_status_count": len(AUDIT_CHAIN_STATUSES),
            "stable_scenario_count": sum(1 for result in scenarios.values() if result["audit_chain_status"] == AUDIT_CHAIN_STABLE),
            "blocked_or_review_scenario_count": sum(1 for result in scenarios.values() if result["audit_chain_status"] != AUDIT_CHAIN_STABLE),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_audit_chain_hashing": True,
            "priority_order_status_selection": True,
            "replay_safe_provenance_evidence": True,
            "rollback_safe_provenance_evidence": True,
        },
        "remaining_limitations": [
            "audit-chain construction models declarative planning provenance only",
            "audit-chain construction does not persist audit state",
            "audit-chain construction does not execute, route, mutate, write, schedule, or dispatch orchestration",
            "audit-chain construction does not perform live replay, capture runtime traces, or read production state",
        ],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Audit Chain",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 8 is a deterministic orchestration planning audit-chain layer.",
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
        "It only constructs declarative orchestration planning provenance chains and validates deterministic planning continuity.",
        "",
        f"- Final audit-chain status: `{report['final_audit_chain_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Deterministic audit-chain hash: `{report['scenario_results']['fully_stable_audit_chain']['deterministic_audit_chain_hash']}`",
        "",
        "## Supported Audit Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["audit_chain_statuses_supported"])
    lines.extend(["", "## Deterministic Priority Order", ""])
    lines.extend(f"- `{status}`" for status in report["priority_order"])
    lines.extend(
        [
            "",
            "## Audit-Chain Input Model",
            "",
            "Inputs include chain identity, root snapshot identity, snapshot sequence, diff-analysis sequence, continuity references, expected hash, manual review, unsupported/prohibited reasons, and limitations.",
            "",
            "## Audit-Chain Output Model",
            "",
            "Outputs include final audit-chain status, snapshot and diff sequences, continuity summaries, gap summaries, integrity summaries, manual-review summaries, limitation summaries, deterministic audit-chain hash, and deterministic explanation summary.",
            "",
            "## Replay Continuity Model",
            "",
            "Replay continuity remains explicit and fails visibly when references are missing.",
            "",
            "## Provenance Integrity Model",
            "",
            "Integrity checks validate snapshot continuity, diff-analysis continuity, deterministic serialization, and source/target hash alignment.",
            "",
            "## Lineage-Gap Model",
            "",
            "Lineage and governance continuity gaps remain explicit and are never repaired silently.",
            "",
            "## Blocker Continuity Model",
            "",
            "Blocker continuity references are preserved as declarative audit evidence.",
            "",
            "## Compatibility and Environment Continuity Model",
            "",
            "Compatibility and environment continuity references remain distinct and deterministic.",
            "",
            "## Manual-Review Model",
            "",
            "Manual review remains explicit and does not approve replay, execution, or orchestration.",
            "",
            "## Deterministic Audit-Chain Hash Behavior",
            "",
            "Audit-chain hashes use stable JSON serialization over caller-provided identifiers, snapshot hashes, diff statuses, continuity references, integrity entries, and manual-review entries.",
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
        lines.append(f"- `{scenario_id}` -> `{result['audit_chain_status']}`")
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
    base = default_orchestration_audit_chain_input()
    source, target = base.snapshot_sequence
    diff = base.diff_analysis_sequence[0]
    assert source is not None and target is not None and diff is not None
    prohibited_snapshot = replace(target, snapshot_status=SNAPSHOT_PROHIBITED)
    unsupported_snapshot = replace(target, snapshot_status=SNAPSHOT_UNSUPPORTED)
    governance_diff = replace(diff, diff_status=SNAPSHOT_DIFF_DRIFT_DETECTED, drift_classifications=("governance_drift",))
    compatibility_diff = replace(diff, diff_status=SNAPSHOT_DIFF_DRIFT_DETECTED, drift_classifications=("compatibility_drift",))
    broken_diff = replace(diff, source_snapshot_hash="mismatched-source-snapshot-hash")
    scenarios = {
        "fully_stable_audit_chain": base,
        "lineage_gap_detection": replace(base, chain_lineage_references=()),
        "replay_continuity_gap": replace(base, replay_continuity_references=()),
        "missing_snapshot_detection": replace(base, snapshot_sequence=(source, None)),
        "missing_diff_analysis_detection": replace(base, diff_analysis_sequence=()),
        "integrity_compromise_detection": replace(base, diff_analysis_sequence=(broken_diff,)),
        "prohibited_audit_chain_state": replace(base, snapshot_sequence=(source, prohibited_snapshot), prohibited_reasons=("runtime_execution",)),
        "unsupported_audit_chain_state": replace(base, snapshot_sequence=(source, unsupported_snapshot), unsupported_reasons=("unsupported_audit_chain_state",)),
        "governance_continuity_drift": replace(base, diff_analysis_sequence=(governance_diff,), governance_continuity_references=()),
        "compatibility_continuity_drift": replace(base, diff_analysis_sequence=(compatibility_diff,), compatibility_continuity_references=()),
        "multiple_simultaneous_continuity_constraints": replace(
            base,
            snapshot_sequence=(source, prohibited_snapshot),
            diff_analysis_sequence=(),
            chain_lineage_references=(),
            replay_continuity_references=(),
            prohibited_reasons=("runtime_execution",),
            deterministic_serialization_verified=False,
            manual_review_reasons=("manual_audit_chain_review",),
        ),
    }
    return {
        scenario_id: export_orchestration_audit_chain_result(build_orchestration_audit_chain(source_input))
        for scenario_id, source_input in scenarios.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {status: sum(1 for result in results.values() if result["audit_chain_status"] == status) for status in AUDIT_CHAIN_STATUSES}


def _sequence_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_entries_count": sum(1 for result in results.values() if result[field]),
        "entry_count": sum(len(result[field]) for result in results.values()),
    }


def _continuity_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "reference_count": sum(len(result[field]["references"]) for result in results.values()),
        "gap_count": sum(len(result[field]["gaps"]) for result in results.values()),
        "scenario_with_gaps_count": sum(1 for result in results.values() if result[field]["gaps"]),
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
        default=Path("docs/generated/v3_5_orchestration_audit_chain_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_AUDIT_CHAIN.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_audit_chain_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
