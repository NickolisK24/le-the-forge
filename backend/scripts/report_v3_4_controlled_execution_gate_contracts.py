"""Generate the v3.4 controlled execution gate contracts report."""

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
from app.runtime_intelligence.controlled_execution_gate_contracts import (  # noqa: E402
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_MISSING_REPLAY_REQUIREMENT,
    BLOCKED_MISSING_ROLLBACK_REQUIREMENT,
    BLOCKED_MISSING_SESSION_ISOLATION,
    BLOCKED_PRODUCTION_EXECUTION_PROHIBITED,
    BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED,
    BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED,
    BLOCKED_UNSUPPORTED_EXECUTION_SCOPE,
    ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_controlled_execution_gate_contract,
    evaluate_controlled_execution_gate_contract,
    summarize_controlled_execution_gate_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_controlled_execution_gate_contracts_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["eligible_controlled_non_production"]
    report = {
        "schema_version": "v3_4.controlled_execution_gate_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_1_controlled_execution_gate_contracts",
        "recommendation": "CONTROLLED_EXECUTION_GATE_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_1_planning_only": True,
        "execution_enabled": False,
        "production_execution_enabled": False,
        "production_runtime_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "production_authoritative_manifest_treatment": False,
        "live_runtime_execution_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "recommendation_logic_enabled": False,
        "autonomous_planner_mutation_enabled": False,
        "final_execution_gate_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "eligible_scenario_count": status_distribution.get(ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(count for status, count in status_distribution.items() if status.startswith("blocked_")),
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "production_authoritative_manifest_treatment": False,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_1_is_planning_only": True,
            "controlled_execution_gates_are_contracts_only": True,
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
    }
    report["deterministic_hash"] = deterministic_hash({key: value for key, value in report.items() if key != "deterministic_hash"})
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Controlled Execution Gate Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final execution gate readiness status: `{report['final_execution_gate_readiness_status']}`",
        "- v3.4 Phase 1 is planning-only.",
        "- Controlled execution gates are contracts only.",
        "- No execution is enabled.",
        "- Production runtime remains prohibited.",
        "",
        "## What This Phase Defines",
        "",
        "This phase defines deterministic eligibility rules for a future controlled, non-production execution planning attempt. It records explicit blockers for production execution, missing authorization, missing replay and rollback requirements, missing session isolation, unsupported scopes, decision routing requests, recommendation requests, and production-authoritative manifest requests.",
        "",
        "## Explicit Non-Enablement",
        "",
        "- No runtime execution is enabled.",
        "- No live replay execution is enabled.",
        "- No synthesis execution is enabled.",
        "- No decision routing is enabled.",
        "- No recommendation logic is enabled.",
        "- No autonomous planner mutation is enabled.",
        "- No production routing is enabled.",
        "- Runtime manifests are not consumed by default.",
        "- No manifest is marked production-authoritative.",
        "",
        "## Scenario Coverage",
        "",
    ]
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['status']}`")
    lines.extend(
        [
            "",
            "## Future Phase Boundary",
            "",
            "Future phases may consume these contracts as planning evidence, but this phase must not execute anything. Any later controlled execution experiment must remain non-production and must add its own explicit execution controls before behavior can move beyond contract evaluation.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_controlled_execution_gate_contract()
    contracts = {
        "eligible_controlled_non_production": base,
        "production_execution_blocked": replace(base, environment="production"),
        "production_authoritative_request_blocked": replace(base, production_authoritative_requested=True),
        "missing_authorization_blocked": replace(base, authorization_state="missing"),
        "missing_replay_blocked": replace(base, replay_required=False),
        "missing_rollback_blocked": replace(base, rollback_required=False),
        "missing_session_isolation_blocked": replace(base, session_isolated=False),
        "unsupported_scope_blocked": replace(base, execution_scope="unrestricted_runtime"),
        "decision_routing_request_blocked": replace(base, decision_routing_requested=True),
        "recommendation_request_blocked": replace(base, recommendation_requested=True),
        "manual_review_required_for_drift_escalation": replace(base, drift_escalation_required=True),
    }
    return {
        scenario_id: {
            **summarize_controlled_execution_gate_result(evaluate_controlled_execution_gate_contract(contract)),
            "blockers": evaluate_controlled_execution_gate_contract(contract)["blockers"],
        }
        for scenario_id, contract in contracts.items()
    }


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        ELIGIBLE_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_PRODUCTION_EXECUTION_PROHIBITED,
        BLOCKED_MISSING_REPLAY_REQUIREMENT,
        BLOCKED_MISSING_ROLLBACK_REQUIREMENT,
        BLOCKED_MISSING_SESSION_ISOLATION,
        BLOCKED_MISSING_AUTHORIZATION,
        BLOCKED_UNSUPPORTED_EXECUTION_SCOPE,
        BLOCKED_RUNTIME_DECISION_ROUTING_PROHIBITED,
        BLOCKED_RECOMMENDATION_LOGIC_PROHIBITED,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_controlled_execution_gate_contracts_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_CONTROLLED_EXECUTION_GATE_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_controlled_execution_gate_contracts_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
