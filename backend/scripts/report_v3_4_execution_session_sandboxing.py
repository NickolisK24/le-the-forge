"""Generate the v3.4 execution session sandboxing contracts report."""

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
from app.runtime_intelligence.controlled_execution_gate_contracts import default_controlled_execution_gate_contract  # noqa: E402
from app.runtime_intelligence.execution_session_sandboxing_contracts import (  # noqa: E402
    BLOCKED_CROSS_SESSION_STATE_ACCESS,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_MISSING_AUTHORIZATION_LINK,
    BLOCKED_MISSING_GATE_LINK,
    BLOCKED_MISSING_SANDBOX_ID,
    BLOCKED_MISSING_SESSION_ID,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED,
    BLOCKED_SANDBOX_SCOPE_UNSUPPORTED,
    BLOCKED_SESSION_NOT_ISOLATED,
    MANUAL_REVIEW_REQUIRED,
    SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_execution_session_sandbox_contract,
    evaluate_execution_session_sandbox_contract,
    summarize_execution_session_sandbox_result,
)
from app.runtime_intelligence.non_production_execution_authorization_contracts import (  # noqa: E402
    default_non_production_execution_authorization_contract,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_execution_session_sandboxing_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_sandbox_readiness"]
    report = {
        "schema_version": "v3_4.execution_session_sandboxing_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_3_execution_session_sandboxing_contracts",
        "recommendation": "EXECUTION_SESSION_SANDBOXING_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_3_sandbox_contract_only": True,
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
        "persistent_mutation_enabled": False,
        "cross_session_state_sharing_enabled": False,
        "external_side_effects_enabled": False,
        "final_sandbox_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "sandbox_ready_scenario_count": status_distribution.get(SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(count for status, count in status_distribution.items() if status.startswith("blocked_")),
            "phase1_gate_compatible_scenario_count": sum(1 for result in scenarios.values() if result["sandbox_does_not_bypass_gate"]),
            "phase2_authorization_compatible_scenario_count": sum(1 for result in scenarios.values() if result["sandbox_does_not_bypass_authorization"]),
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
            "persistent_mutation_enabled": False,
            "cross_session_state_sharing_enabled": False,
            "external_side_effects_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_3_is_sandbox_contract_only": True,
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_environment_prohibited": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
            "persistent_mutation_enabled": False,
            "cross_session_state_sharing_enabled": False,
            "external_side_effects_enabled": False,
            "sandbox_does_not_bypass_phase1_execution_gates": True,
            "sandbox_does_not_bypass_phase2_authorization": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Execution Session Sandboxing Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final sandbox readiness status: `{report['final_sandbox_readiness_status']}`",
        "- v3.4 Phase 3 is sandbox-contract-only.",
        "- No execution is enabled.",
        "- Sandboxing is required before future controlled execution planning.",
        "- Sandbox contracts do not bypass Phase 1 gates.",
        "- Sandbox contracts do not bypass Phase 2 authorization.",
        "- Production environments remain prohibited.",
        "",
        "## Boundary Requirements",
        "",
        "Persistent mutation, cross-session access, and external side effects remain prohibited. Missing session identity, sandbox identity, authorization linkage, gate linkage, isolation, supported sandbox scope, and non-production environment boundaries are explicit blockers.",
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
        "- Persistent mutation remains prohibited.",
        "- Cross-session state sharing remains prohibited.",
        "- External side effects remain prohibited.",
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
            "Future phases may consume these sandbox contracts as planning evidence, but this phase must not execute anything. Any future controlled execution experiment must still satisfy Phase 1 execution gates, Phase 2 authorization, and isolated non-production sandbox boundaries.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    base = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    contracts = {
        "valid_sandbox_readiness": base,
        "missing_session_id_blocked": replace(base, session_id=""),
        "missing_sandbox_id_blocked": replace(base, sandbox_id=""),
        "missing_authorization_link_blocked": replace(base, authorization_id=""),
        "missing_gate_link_blocked": replace(base, gate_contract_id=""),
        "non_isolated_session_blocked": replace(base, isolated=False),
        "cross_session_access_blocked": replace(base, cross_session_access_requested=True),
        "persistent_mutation_blocked": replace(base, persistent_mutation_requested=True),
        "external_side_effect_blocked": replace(base, external_side_effect_requested=True),
        "production_environment_blocked": replace(base, production_environment_requested=True),
        "unsupported_sandbox_scope_blocked": replace(base, sandbox_scope_supported=False),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_execution_session_sandbox_contract(contract)
        results[scenario_id] = {
            **summarize_execution_session_sandbox_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        SANDBOX_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_SESSION_ID,
        BLOCKED_MISSING_SANDBOX_ID,
        BLOCKED_SESSION_NOT_ISOLATED,
        BLOCKED_CROSS_SESSION_STATE_ACCESS,
        BLOCKED_PERSISTENT_MUTATION_REQUESTED,
        BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
        BLOCKED_PRODUCTION_ENVIRONMENT_PROHIBITED,
        BLOCKED_MISSING_AUTHORIZATION_LINK,
        BLOCKED_MISSING_GATE_LINK,
        BLOCKED_SANDBOX_SCOPE_UNSUPPORTED,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_execution_session_sandboxing_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_EXECUTION_SESSION_SANDBOXING_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_execution_session_sandboxing_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
