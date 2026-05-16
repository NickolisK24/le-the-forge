"""Generate the v3.5 governance dependency resolution report."""

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
    DEPENDENCY_BLOCKED,
    DEPENDENCY_ENVIRONMENT_MISMATCH,
    DEPENDENCY_INCOMPATIBLE,
    DEPENDENCY_LINEAGE_GAP,
    DEPENDENCY_MISSING,
    DEPENDENCY_PROHIBITED,
    DEPENDENCY_REQUIRES_MANUAL_REVIEW,
    DEPENDENCY_SATISFIED,
    DEPENDENCY_STATUSES,
    DEPENDENCY_UNSUPPORTED,
    default_governance_dependency_contract,
    default_governance_dependency_resolution_input,
    export_governance_dependency_resolution_result,
    resolve_governance_dependency,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_governance_dependency_resolution_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_satisfied_dependency"]
    report = {
        "schema_version": "v3_5.governance_dependency_resolution_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_3_governance_dependency_resolution_contracts",
        "planning_only": True,
        "non_production": True,
        "final_dependency_resolution_status": focused["dependency_status"],
        "dependency_statuses_supported": list(DEPENDENCY_STATUSES),
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "satisfied_dependency_summary": _list_summary(scenarios, "satisfied_evidence"),
        "missing_dependency_summary": _list_summary(scenarios, "missing_evidence"),
        "blocked_dependency_summary": _blocker_summary(scenarios, DEPENDENCY_BLOCKED),
        "unsupported_dependency_summary": _list_summary(scenarios, "unsupported_reasons"),
        "prohibited_dependency_summary": _list_summary(scenarios, "prohibited_reasons"),
        "manual_review_summary": _list_summary(scenarios, "manual_review_reasons"),
        "lineage_propagation_summary": {
            "scenario_count": len(scenarios),
            "lineage_gap_scenario_count": sum(1 for result in scenarios.values() if result["lineage_gaps"]),
            "cross_scope_lineage_scenario_count": 1,
            "non_executable_lineage_propagation": True,
        },
        "compatibility_validation_summary": _list_summary(scenarios, "compatibility_failures"),
        "environment_validation_summary": _list_summary(scenarios, "environment_mismatches"),
        "explicit_non_execution_guarantees": {
            "runtime_execution_enabled": False,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "mutation_behavior_enabled": False,
            "audit_log_writing_enabled": False,
            "production_consumption_enabled": False,
            "external_dependency_fetching_enabled": False,
            "automatic_remediation_enabled": False,
            "dependency_auto_repair_enabled": False,
            "dependency_auto_resolution_from_external_sources_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(DEPENDENCY_STATUSES),
            "satisfied_scenario_count": sum(
                1 for result in scenarios.values() if result["dependency_status"] == DEPENDENCY_SATISFIED
            ),
            "blocked_or_review_scenario_count": sum(
                1 for result in scenarios.values() if result["dependency_status"] != DEPENDENCY_SATISFIED
            ),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "replay_safe_lineage_visibility": True,
            "rollback_safe_lineage_visibility": True,
            "fail_visible_dependency_blockers": True,
            "unsupported_reason_preservation": True,
            "prohibited_reason_preservation": True,
        },
        "remaining_limitations": [
            "dependency resolution classifies declarative governance dependency inputs only",
            "dependency resolution does not execute orchestration",
            "dependency resolution does not authorize orchestration execution",
            "dependency resolution does not fetch dependencies from external sources",
            "dependency resolution does not automatically repair missing dependencies",
        ],
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Governance Dependency Resolution",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 3 is a deterministic governance dependency resolution layer.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not authorize orchestration execution.",
        "",
        "It does not route requests.",
        "",
        "It does not mutate state.",
        "",
        "It does not write audit logs.",
        "",
        "It does not fetch dependencies from external sources.",
        "",
        "It does not automatically repair missing dependencies.",
        "",
        "It only classifies declarative governance dependency inputs for future controlled orchestration planning.",
        "",
        f"- Final dependency resolution status: `{report['final_dependency_resolution_status']}`",
        f"- Deterministic hash: `{report['deterministic_hash']}`",
        "",
        "## Supported Dependency Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["dependency_statuses_supported"])
    lines.extend(
        [
            "",
            "## Dependency Input Model",
            "",
            "- dependency identity",
            "- dependency domain",
            "- required evidence",
            "- provided evidence",
            "- source contract identity",
            "- target orchestration scope",
            "- dependency lineage references",
            "- compatibility requirements",
            "- environment requirements",
            "- manual-review reasons",
            "- unsupported reasons",
            "- prohibited reasons",
            "- blocker reasons",
            "",
            "## Dependency Resolution Output Model",
            "",
            "- dependency ID",
            "- dependency status",
            "- satisfied evidence",
            "- missing evidence",
            "- blockers",
            "- unsupported reasons",
            "- prohibited reasons",
            "- manual review reasons",
            "- compatibility failures",
            "- environment mismatches",
            "- lineage gaps",
            "- deterministic explanation summary",
            "",
            "## Evidence Model",
            "",
            "Required and provided evidence are compared deterministically. Missing evidence remains fail-visible and is never inferred.",
            "",
            "## Blocker Model",
            "",
            "Dependency blockers are explicit, deterministic, fail-visible, audit-safe, and sorted by deterministic rank and blocker identity.",
            "",
            "## Unsupported-State Model",
            "",
            "Unsupported dependency states are preserved as explicit resolution outputs and do not silently satisfy dependencies.",
            "",
            "## Prohibited-Domain Model",
            "",
            "Prohibited dependency domains remain hard blockers and cannot be downgraded by manual review or compatibility evidence.",
            "",
            "## Manual-Review Model",
            "",
            "Manual review is explicit and planning-only. It does not authorize execution or dependency repair.",
            "",
            "## Lineage Propagation Model",
            "",
            "Lineage propagation records source governance contract ID, target orchestration scope ID, upstream dependencies, downstream dependencies, replay lineage, rollback lineage, compatibility lineage, and environment lineage. It performs no live traversal, external graph lookup, or automatic repair.",
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
        lines.append(f"- `{scenario_id}` -> `{result['dependency_status']}`")
    lines.extend(
        [
            "",
            "## Explicit Non-Execution Guarantees",
            "",
            "- Runtime execution remains prohibited.",
            "- Orchestration execution remains prohibited.",
            "- Routing behavior remains prohibited.",
            "- Mutation behavior remains prohibited.",
            "- Audit log writing remains prohibited.",
            "- Production consumption remains prohibited.",
            "- External dependency fetching remains prohibited.",
            "- Automatic remediation remains prohibited.",
            "- Dependency auto-repair remains prohibited.",
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
    base = default_governance_dependency_resolution_input()
    contract = default_governance_dependency_contract()
    lineage_gap_contract = replace(
        contract,
        lineage=replace(
            contract.lineage,
            replay_lineage_references=(),
            rollback_lineage_references=(),
        ),
    )
    scenarios = {
        "fully_satisfied_dependency": base,
        "missing_required_evidence": replace(
            base,
            contract=replace(contract, provided_evidence_ids=contract.provided_evidence_ids[:-1]),
        ),
        "blocked_dependency": replace(base, contract=replace(contract, blocker_reasons=("governance_blocker_visible",))),
        "unsupported_dependency": replace(
            base,
            contract=replace(contract, dependency_supported=False, unsupported_reasons=("unsupported_dependency_scope",)),
        ),
        "prohibited_dependency": replace(base, contract=replace(contract, dependency_domain="runtime_execution")),
        "manual_review_required": replace(
            base,
            contract=replace(contract, manual_review_reasons=("dependency_owner_review_required",)),
        ),
        "compatibility_failure": replace(base, contract=replace(contract, compatibility_verified=False)),
        "environment_mismatch": replace(
            base,
            contract=replace(contract, environment_evidence_ids=(), environment_verified=False),
        ),
        "dependency_lineage_gap": replace(base, contract=lineage_gap_contract),
        "multiple_simultaneous_dependency_blockers": replace(
            base,
            contract=replace(
                lineage_gap_contract,
                dependency_domain="runtime_execution",
                provided_evidence_ids=(),
                blocker_reasons=("governance_blocker_visible",),
                dependency_supported=False,
                unsupported_reasons=("unsupported_dependency_scope",),
                compatibility_verified=False,
                environment_evidence_ids=(),
                environment_verified=False,
                manual_review_reasons=("dependency_owner_review_required",),
            ),
        ),
        "cross_scope_lineage_propagation": replace(
            base,
            contract=replace(
                contract,
                lineage=replace(
                    contract.lineage,
                    upstream_dependency_ids=("v3_4_closeout_and_v3_5_readiness", "v3_5_governance_consumption_contract"),
                    downstream_dependency_ids=(
                        "v3_5_orchestration_readiness_evaluation",
                        "v3_5_governance_dependency_resolution",
                    ),
                ),
            ),
        ),
    }
    return {scenario_id: export_governance_dependency_resolution_result(resolve_governance_dependency(source)) for scenario_id, source in scenarios.items()}


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["dependency_status"] == status)
        for status in DEPENDENCY_STATUSES
    }


def _list_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenario_with_entries_count": sum(1 for result in results.values() if result[field]),
        "entry_count": sum(len(result[field]) for result in results.values()),
    }


def _blocker_summary(results: dict[str, dict[str, Any]], status: str) -> dict[str, int]:
    blockers = [
        blocker
        for result in results.values()
        for blocker in result["blockers"]
        if blocker["dependency_status"] == status
    ]
    return {
        "scenario_count": len(results),
        "scenario_with_blockers_count": sum(
            1 for result in results.values() if any(row["dependency_status"] == status for row in result["blockers"])
        ),
        "blocker_count": len(blockers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_5_governance_dependency_resolution_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_GOVERNANCE_DEPENDENCY_RESOLUTION.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_governance_dependency_resolution_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
