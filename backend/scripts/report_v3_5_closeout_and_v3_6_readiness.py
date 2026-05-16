"""Generate the v3.5 closeout and v3.6 readiness report."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration import (  # noqa: E402
    V3_5_CLOSEOUT_STATUSES,
    V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING,
    V3_6_PLANNING_CLASSIFICATIONS,
    V35CloseoutReadinessInput,
    audit_v3_5_closeout_readiness,
    export_v3_5_closeout_readiness_result,
)
from app.runtime_orchestration.v3_5_closeout_readiness_audit import V3_5_PHASE_SPECS  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_closeout_and_v3_6_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    scenarios = _scenario_results(root)
    focused = scenarios["full_v3_5_chain_present_and_stable"]
    report = {
        "schema_version": "v3_5.closeout_and_v3_6_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_10_closeout_and_v3_6_readiness",
        "closeout_scope": "full_v3_5_orchestration_planning_chain",
        "planning_only": True,
        "non_production": True,
        "final_closeout_status": focused["closeout_status"],
        "v3_6_planning_readiness_classification": focused["v3_6_planning_readiness"],
        "closeout_statuses_supported": list(V3_5_CLOSEOUT_STATUSES),
        "v3_6_planning_classifications_supported": list(V3_6_PLANNING_CLASSIFICATIONS),
        "full_phase_coverage": _phase_coverage(),
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "missing_report_summary": _list_summary(scenarios, "missing_report_list"),
        "missing_documentation_summary": _list_summary(scenarios, "missing_documentation_list"),
        "invalid_status_summary": _list_summary(scenarios, "invalid_phase_status_list"),
        "deterministic_hash_summary": {
            "scenario_count": len(scenarios),
            "scenario_with_missing_hash_count": sum(1 for result in scenarios.values() if result["missing_deterministic_hash_list"]),
            "stable_closeout_hashing": True,
        },
        "scenario_coverage_summary": _list_summary(scenarios, "missing_scenario_coverage_list"),
        "prohibition_preservation_summary": _list_summary(scenarios, "prohibition_preservation_summary"),
        "phase_chain_compatibility_summary": _list_summary(scenarios, "compatibility_blocker_summary"),
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
            "v3_6_behavior_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "expected_phase_count": len(V3_5_PHASE_SPECS),
            "stable_scenario_count": sum(1 for result in scenarios.values() if result["closeout_status"] == V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING),
            "blocked_or_review_scenario_count": sum(1 for result in scenarios.values() if result["closeout_status"] != V3_5_CLOSED_OUT_READY_FOR_V3_6_PLANNING),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "stable_closeout_hashing": True,
            "report_presence_validated": True,
            "documentation_presence_validated": True,
            "prohibition_preservation_validated": True,
        },
        "remaining_limitations": [
            "closeout audit inspects generated artifacts only",
            "closeout audit does not repair missing reports or infer missing evidence",
            "closeout audit does not execute, route, mutate, write audit logs, schedule, dispatch, or traverse orchestration",
            "closeout audit does not perform live replay, capture runtime traces, read production state, persist audit state, or enable v3.6 behavior",
        ],
        "deterministic_closeout_hash": focused["deterministic_closeout_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Closeout and v3.6 Readiness",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 10 is a deterministic closeout and v3.6 readiness audit.",
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
        "It does not enable v3.6 behavior.",
        "",
        "It only validates whether the full v3.5 orchestration planning chain is complete enough for v3.6 planning discussions to begin.",
        "",
        f"- Final closeout status: `{report['final_closeout_status']}`",
        f"- v3.6 planning readiness: `{report['v3_6_planning_readiness_classification']}`",
        f"- Deterministic closeout hash: `{report['deterministic_closeout_hash']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Full v3.5 Phase Coverage",
        "",
    ]
    for phase in report["full_phase_coverage"]:
        lines.append(f"- `{phase['phase_id']}`: {phase['phase_name']} -> `{phase['report_path']}`")
    lines.extend(
        [
            "",
            "## Closeout Audit Input Model",
            "",
            "Inputs include the expected phase report set, expected migration documentation set, expected final statuses, deterministic hash fields, scenario coverage evidence, phase-chain compatibility, manual review reasons, and limitations.",
            "",
            "## Closeout Audit Output Model",
            "",
            "Outputs include final closeout status, v3.6 planning readiness classification, phase coverage, missing report and documentation lists, invalid status lists, missing hash and scenario lists, compatibility blockers, prohibition preservation, limitations, deterministic closeout hash, and explanation summary.",
            "",
            "## v3.6 Planning Readiness Model",
            "",
            "v3.6 planning is allowed only when all required reports and docs exist, all final statuses are acceptable, hashes and scenario coverage are present, no execution or production leak is detected, and phase-chain compatibility is preserved.",
            "",
            "This classification authorizes planning discussion only. It does not authorize v3.6 implementation behavior.",
            "",
            "## Deterministic Closeout Hash Behavior",
            "",
            "Closeout hashes use stable JSON serialization over phase coverage, final statuses, deterministic hashes, scenario coverage, compatibility blockers, manual review, and limitations.",
            "",
            "## Phase-Chain Compatibility Rules",
            "",
            "Every v3.5 phase must have a present report, present migration document, expected final status, deterministic hash, scenario coverage, and preserved non-execution and non-production guarantees.",
            "",
            "## Prohibition Preservation Model",
            "",
            "The closeout audit blocks execution leaks, routing leaks, mutation leaks, production consumption leaks, graph execution leaks, scheduling or dispatch leaks, runtime trace capture, production state reads, live replay, persistent audit storage, and v3.6 behavior.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['closeout_status']}` / `{result['v3_6_planning_readiness']}`")
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
            "- v3.6 behavior remains disabled.",
            "- The repository remains planning-only.",
            "",
            "## Remaining Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["remaining_limitations"])
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results(repo_root: Path) -> dict[str, dict[str, Any]]:
    reports = _current_phase_reports(repo_root)
    docs = {spec.phase_id: (repo_root / spec.documentation_path).exists() for spec in V3_5_PHASE_SPECS}
    missing_report = dict(reports)
    missing_report["phase_4"] = None
    missing_doc = dict(docs)
    missing_doc["phase_5"] = False
    invalid_status = copy.deepcopy(reports)
    invalid_status["phase_2"]["final_readiness_status"] = "blocked_by_governance_dependency"
    missing_hash = copy.deepcopy(reports)
    missing_hash["phase_9"].pop("deterministic_report_hash", None)
    missing_scenario = copy.deepcopy(reports)
    missing_scenario["phase_3"]["summary"]["scenario_count"] = 0
    missing_scenario["phase_3"]["scenario_results"] = {}
    execution_leak = copy.deepcopy(reports)
    execution_leak["phase_1"]["runtime_execution_enabled"] = True
    production_leak = copy.deepcopy(reports)
    production_leak["phase_6"]["explicit_non_execution_guarantees"]["production_consumption_enabled"] = True
    blocked_state = copy.deepcopy(reports)
    blocked_state["phase_7"].pop("deterministic_report_hash", None)
    scenarios = {
        "full_v3_5_chain_present_and_stable": V35CloseoutReadinessInput(repo_root, reports, docs),
        "missing_phase_report": V35CloseoutReadinessInput(repo_root, missing_report, docs),
        "missing_migration_documentation": V35CloseoutReadinessInput(repo_root, reports, missing_doc),
        "invalid_phase_status": V35CloseoutReadinessInput(repo_root, invalid_status, docs),
        "missing_deterministic_hash": V35CloseoutReadinessInput(repo_root, missing_hash, docs),
        "missing_scenario_coverage": V35CloseoutReadinessInput(repo_root, missing_scenario, docs),
        "execution_leak_detection": V35CloseoutReadinessInput(repo_root, execution_leak, docs),
        "production_consumption_leak_detection": V35CloseoutReadinessInput(repo_root, production_leak, docs),
        "phase_chain_incompatibility": V35CloseoutReadinessInput(repo_root, reports, docs, phase_chain_compatible=False),
        "manual_review_readiness_state": V35CloseoutReadinessInput(repo_root, reports, docs, manual_review_reasons=("manual_closeout_review",)),
        "v3_6_planning_blocked_state": V35CloseoutReadinessInput(repo_root, blocked_state, docs),
    }
    return {
        scenario_id: export_v3_5_closeout_readiness_result(audit_v3_5_closeout_readiness(source_input))
        for scenario_id, source_input in scenarios.items()
    }


def _current_phase_reports(repo_root: Path) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for spec in V3_5_PHASE_SPECS:
        reports[spec.phase_id] = json.loads((repo_root / spec.report_path).read_text(encoding="utf-8"))
    return reports


def _phase_coverage() -> list[dict[str, str]]:
    return [
        {
            "phase_id": spec.phase_id,
            "phase_name": spec.phase_name,
            "report_path": spec.report_path,
            "documentation_path": spec.documentation_path,
            "status_field": spec.status_field,
            "expected_status": spec.expected_status,
        }
        for spec in V3_5_PHASE_SPECS
    ]


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["closeout_status"] == status)
        for status in V3_5_CLOSEOUT_STATUSES
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
        default=Path("docs/generated/v3_5_closeout_and_v3_6_readiness_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_CLOSEOUT_AND_V3_6_READINESS.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_closeout_and_v3_6_readiness_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
