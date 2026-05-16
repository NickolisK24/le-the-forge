"""Generate the v3.4 non-production execution authorization contracts report."""

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
from app.runtime_intelligence.non_production_execution_authorization_contracts import (  # noqa: E402
    AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
    BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH,
    BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING,
    BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING,
    BLOCKED_AUTHORIZATION_SESSION_MISMATCH,
    BLOCKED_EXPIRED_AUTHORIZATION,
    BLOCKED_INVALID_AUTHORIZATION_SCOPE,
    BLOCKED_MISSING_AUTHORIZATION,
    BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED,
    MANUAL_REVIEW_REQUIRED,
    default_non_production_execution_authorization_contract,
    evaluate_non_production_execution_authorization_contract,
    summarize_non_production_execution_authorization_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_non_production_execution_authorization_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_non_production_authorization"]
    report = {
        "schema_version": "v3_4.non_production_execution_authorization_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_2_non_production_execution_authorization_contracts",
        "recommendation": "NON_PRODUCTION_EXECUTION_AUTHORIZATION_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_2_authorization_contract_only": True,
        "execution_enabled": False,
        "production_execution_enabled": False,
        "production_authorization_enabled": False,
        "production_runtime_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "production_authoritative_manifest_treatment": False,
        "live_runtime_execution_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "recommendation_logic_enabled": False,
        "autonomous_planner_mutation_enabled": False,
        "final_authorization_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "authorized_scenario_count": status_distribution.get(AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(count for status, count in status_distribution.items() if status.startswith("blocked_")),
            "phase1_gate_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["authorization_does_not_bypass_gate"]
            ),
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_authorization_enabled": False,
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
            "v3_4_phase_2_is_authorization_contract_only": True,
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_authorization_prohibited": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
            "authorization_does_not_bypass_phase1_execution_gates": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Non-Production Execution Authorization Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final authorization readiness status: `{report['final_authorization_readiness_status']}`",
        "- v3.4 Phase 2 is authorization-contract-only.",
        "- No execution is enabled.",
        "- Production authorization remains prohibited.",
        "- Authorization only applies to future controlled non-production execution planning.",
        "- Authorization does not bypass Phase 1 execution gates.",
        "",
        "## Boundary Requirements",
        "",
        "Replay, rollback, session isolation, and environment boundaries remain mandatory. Missing authorization, expired authorization, production authorization, environment mismatch, session mismatch, invalid scope, missing replay requirements, and missing rollback requirements are explicit blockers.",
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
        "- Production-authoritative manifests remain prohibited.",
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
            "Future phases may consume these authorization contracts as planning evidence, but this phase must not execute anything. Any future controlled execution experiment must still satisfy Phase 1 execution gates and remain non-production.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_non_production_execution_authorization_contract()
    contracts = {
        "valid_non_production_authorization": base,
        "missing_authorization_blocked": replace(base, authorization_id="", authorized_by="", authorization_state="missing"),
        "expired_authorization_blocked": replace(base, expiration_state="expired"),
        "production_authorization_blocked": replace(base, production_authorization_requested=True),
        "environment_mismatch_blocked": replace(base, requested_environment="production"),
        "session_mismatch_blocked": replace(base, requested_session_id="different-session"),
        "invalid_authorization_scope_blocked": replace(base, authorization_scope="unrestricted_runtime"),
        "missing_replay_requirement_blocked": replace(base, replay_required=False),
        "missing_rollback_requirement_blocked": replace(base, rollback_required=False),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_non_production_execution_authorization_contract(contract)
        results[scenario_id] = {
            **summarize_non_production_execution_authorization_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        AUTHORIZED_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_AUTHORIZATION,
        BLOCKED_INVALID_AUTHORIZATION_SCOPE,
        BLOCKED_EXPIRED_AUTHORIZATION,
        BLOCKED_PRODUCTION_AUTHORIZATION_PROHIBITED,
        BLOCKED_AUTHORIZATION_ENVIRONMENT_MISMATCH,
        BLOCKED_AUTHORIZATION_SESSION_MISMATCH,
        BLOCKED_AUTHORIZATION_REPLAY_REQUIREMENT_MISSING,
        BLOCKED_AUTHORIZATION_ROLLBACK_REQUIREMENT_MISSING,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_non_production_execution_authorization_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_NON_PRODUCTION_EXECUTION_AUTHORIZATION_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_non_production_execution_authorization_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
