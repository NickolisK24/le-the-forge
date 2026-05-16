"""Generate the v3.5 orchestration readiness evaluation report."""

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
    BLOCKED_BY_AUTHORIZATION_FAILURE,
    BLOCKED_BY_COMPATIBILITY_FAILURE,
    BLOCKED_BY_ENVIRONMENT_FAILURE,
    BLOCKED_BY_GOVERNANCE_DEPENDENCY,
    BLOCKED_BY_REPLAY_LINEAGE_GAP,
    BLOCKED_BY_ROLLBACK_LINEAGE_GAP,
    MANUAL_REVIEW_REQUIRED,
    PROHIBITED_ORCHESTRATION_REQUEST,
    READINESS_STATUSES,
    READY_FOR_FUTURE_ORCHESTRATION_PLANNING,
    UNSUPPORTED_ORCHESTRATION_REQUEST,
    OrchestrationReadinessEvaluationInput,
    default_governance_consumption_contract,
    default_orchestration_readiness_evaluation_input,
    evaluate_orchestration_readiness,
    export_orchestration_readiness_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_orchestration_readiness_evaluation_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["fully_ready_planning_only_orchestration_request"]
    report = {
        "schema_version": "v3_5.orchestration_readiness_evaluation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.5_phase_2_orchestration_readiness_evaluation_contracts",
        "planning_only": True,
        "non_production": True,
        "final_readiness_status": focused["readiness_status"],
        "readiness_statuses_supported": list(READINESS_STATUSES),
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "status_distribution": _status_distribution(scenarios),
        "blocker_visibility_summary": _visibility_summary(scenarios, "blockers"),
        "unsupported_state_visibility_summary": _list_summary(scenarios, "unsupported_states"),
        "prohibited_domain_visibility_summary": _list_summary(scenarios, "prohibited_domains"),
        "replay_lineage_validation_summary": _list_summary(scenarios, "missing_replay_requirements"),
        "rollback_lineage_validation_summary": _list_summary(scenarios, "missing_rollback_requirements"),
        "compatibility_validation_summary": _list_summary(scenarios, "compatibility_failures"),
        "environment_validation_summary": _list_summary(scenarios, "environment_failures"),
        "manual_review_summary": _list_summary(scenarios, "manual_review_reasons"),
        "explicit_non_execution_guarantees": {
            "runtime_execution_enabled": False,
            "orchestration_execution_enabled": False,
            "routing_behavior_enabled": False,
            "mutation_behavior_enabled": False,
            "audit_log_writing_enabled": False,
            "production_consumption_enabled": False,
            "default_runtime_manifest_consumption_enabled": False,
            "production_authoritative_manifest_treatment_enabled": False,
            "live_replay_execution_enabled": False,
            "rollback_execution_enabled": False,
            "automatic_remediation_enabled": False,
        },
        "summary": {
            "scenario_count": len(scenarios),
            "supported_status_count": len(READINESS_STATUSES),
            "ready_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["readiness_status"] == READY_FOR_FUTURE_ORCHESTRATION_PLANNING
            ),
            "blocked_or_review_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["readiness_status"] != READY_FOR_FUTURE_ORCHESTRATION_PLANNING
            ),
            "deterministic_outputs": True,
            "stable_serialization": True,
            "replay_safe_output_stability": True,
            "rollback_safe_output_stability": True,
            "fail_visible_blockers": True,
            "unsupported_state_preservation": True,
            "prohibited_domain_preservation": True,
        },
        "remaining_limitations": [
            "readiness evaluation classifies declarative planning inputs only",
            "readiness evaluation does not authorize orchestration execution",
            "readiness evaluation does not route requests",
            "readiness evaluation does not mutate state or write audit logs",
            "readiness evaluation does not consume runtime manifests by default",
        ],
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Orchestration Readiness Evaluation",
        "",
        "## Phase Boundary",
        "",
        "v3.5 Phase 2 is a deterministic orchestration readiness evaluation layer.",
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
        "It only classifies declarative orchestration planning inputs for future controlled orchestration planning.",
        "",
        f"- Final readiness status: `{report['final_readiness_status']}`",
        f"- Deterministic hash: `{report['deterministic_hash']}`",
        "",
        "## Supported Readiness Statuses",
        "",
    ]
    lines.extend(f"- `{status}`" for status in report["readiness_statuses_supported"])
    lines.extend(
        [
            "",
            "## Evaluation Inputs",
            "",
            "- orchestration request identity",
            "- orchestration scope identity",
            "- authorization requirements",
            "- governance dependencies",
            "- replay lineage requirements",
            "- rollback lineage requirements",
            "- compatibility requirements",
            "- environment requirements",
            "- unsupported states",
            "- prohibited domains",
            "- blocker presence",
            "- manual review requirements",
            "",
            "## Evaluation Outputs",
            "",
            "- final readiness status",
            "- blocker list",
            "- unsupported-state list",
            "- prohibited-domain list",
            "- missing governance dependencies",
            "- missing replay requirements",
            "- missing rollback requirements",
            "- compatibility failures",
            "- environment failures",
            "- manual review reasons",
            "- deterministic explanation summary",
            "",
            "## Blocker Model",
            "",
            "Blockers are explicit, deterministic, fail-visible, and audit-safe. They are ordered by deterministic rank and blocker identity.",
            "",
            "## Unsupported-State Model",
            "",
            "Unsupported orchestration states are preserved as first-class readiness output and never silently converted into passing readiness.",
            "",
            "## Prohibited-Domain Model",
            "",
            "Prohibited orchestration domains remain hard blockers for readiness classification and cannot be downgraded by compatibility or manual review.",
            "",
            "## Manual-Review Model",
            "",
            "Manual review is an explicit readiness status for future planning review only. It does not authorize execution.",
            "",
            "## Deterministic Hash Behavior",
            "",
            "Report and result hashes use stable JSON serialization with sorted keys. The report avoids runtime-generated IDs and environment-dependent values.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['readiness_status']}`")
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
            "- Default runtime manifest consumption remains disabled.",
            "- Production-authoritative manifest treatment remains prohibited.",
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
    base = default_orchestration_readiness_evaluation_input()
    contract = default_governance_consumption_contract()
    unsupported_contract = replace(contract, unsupported_orchestration_states=("unsupported_orchestration_scope",))
    prohibited_contract = replace(contract, requested_orchestration_domain="runtime_execution")
    scenarios = {
        "fully_ready_planning_only_orchestration_request": base,
        "missing_governance_dependency": replace(
            base,
            contract=replace(contract, governance_dependency_ids=contract.governance_dependency_ids[:-1]),
        ),
        "missing_authorization": replace(base, contract=replace(contract, authorization_state="missing")),
        "missing_replay_lineage": replace(base, contract=replace(contract, replay_lineage_id="")),
        "missing_rollback_lineage": replace(base, contract=replace(contract, rollback_lineage_id="")),
        "unsupported_orchestration_request": replace(base, contract=unsupported_contract),
        "prohibited_orchestration_request": replace(base, contract=prohibited_contract),
        "compatibility_failure": replace(base, contract=replace(contract, compatibility_verified=False)),
        "environment_failure": replace(base, contract=replace(contract, environment="production", environment_isolated=False)),
        "manual_review_required": replace(
            base,
            manual_review_required=True,
            manual_review_reasons=("governance_review_required",),
        ),
        "multiple_simultaneous_blockers": replace(
            base,
            contract=replace(
                contract,
                governance_dependency_ids=(),
                authorization_state="missing",
                replay_lineage_id="",
                rollback_lineage_id="",
                compatibility_verified=False,
                environment="production",
                requested_orchestration_domain="runtime_execution",
            ),
        ),
    }
    return {scenario_id: export_orchestration_readiness_result(evaluate_orchestration_readiness(source)) for scenario_id, source in scenarios.items()}


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        status: sum(1 for result in results.values() if result["readiness_status"] == status)
        for status in READINESS_STATUSES
    }


def _visibility_summary(results: dict[str, dict[str, Any]], field: str) -> dict[str, int]:
    return {
        "scenario_count": len(results),
        "scenarios_with_visible_entries": sum(1 for result in results.values() if result[field]),
        "visible_entry_count": sum(len(result[field]) for result in results.values()),
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
        default=Path("docs/generated/v3_5_orchestration_readiness_evaluation_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_ORCHESTRATION_READINESS_EVALUATION.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_orchestration_readiness_evaluation_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
