"""Generate the v3.4 rollback execution governance contracts report."""

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
from app.runtime_intelligence.execution_session_sandboxing_contracts import default_execution_session_sandbox_contract  # noqa: E402
from app.runtime_intelligence.non_production_execution_authorization_contracts import (  # noqa: E402
    default_non_production_execution_authorization_contract,
)
from app.runtime_intelligence.replay_safe_execution_scope_contracts import default_replay_safe_execution_scope_contract  # noqa: E402
from app.runtime_intelligence.rollback_execution_governance_contracts import (  # noqa: E402
    BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_ROLLBACK_PLAN_ID,
    BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH,
    BLOCKED_ROLLBACK_LINEAGE_MISSING,
    BLOCKED_ROLLBACK_NOT_REQUIRED,
    BLOCKED_ROLLBACK_PLAN_MISSING,
    BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED,
    BLOCKED_ROLLBACK_SESSION_MISMATCH,
    BLOCKED_ROLLBACK_TARGET_MISSING,
    BLOCKED_ROLLBACK_VALIDATION_MISSING,
    MANUAL_REVIEW_REQUIRED,
    ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_rollback_execution_governance_contract,
    evaluate_rollback_execution_governance_contract,
    summarize_rollback_execution_governance_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_rollback_execution_governance_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_rollback_governance_readiness"]
    report = {
        "schema_version": "v3_4.rollback_execution_governance_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_5_rollback_execution_governance_contracts",
        "recommendation": "ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_5_rollback_governance_contract_only": True,
        "execution_enabled": False,
        "production_execution_enabled": False,
        "production_runtime_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "production_authoritative_manifest_treatment": False,
        "live_runtime_execution_enabled": False,
        "live_replay_execution_enabled": False,
        "live_rollback_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "recommendation_logic_enabled": False,
        "autonomous_planner_mutation_enabled": False,
        "rollback_plan_execution_enabled": False,
        "final_rollback_governance_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "rollback_governance_ready_scenario_count": status_distribution.get(ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(count for status, count in status_distribution.items() if status.startswith("blocked_")),
            "phase1_gate_compatible_scenario_count": sum(1 for result in scenarios.values() if result["rollback_governance_does_not_bypass_gate"]),
            "phase2_authorization_compatible_scenario_count": sum(1 for result in scenarios.values() if result["rollback_governance_does_not_bypass_authorization"]),
            "phase3_sandbox_compatible_scenario_count": sum(1 for result in scenarios.values() if result["rollback_governance_does_not_bypass_sandbox"]),
            "phase4_replay_scope_compatible_scenario_count": sum(1 for result in scenarios.values() if result["rollback_governance_does_not_bypass_replay_scope"]),
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "production_authoritative_manifest_treatment": False,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_rollback_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
            "rollback_plan_execution_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_5_is_rollback_governance_contract_only": True,
            "execution_enabled": False,
            "production_execution_enabled": False,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "live_runtime_execution_enabled": False,
            "live_replay_execution_enabled": False,
            "live_rollback_execution_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
            "rollback_plan_execution_enabled": False,
            "rollback_governance_does_not_bypass_phase1_execution_gates": True,
            "rollback_governance_does_not_bypass_phase2_authorization": True,
            "rollback_governance_does_not_bypass_phase3_sandboxing": True,
            "rollback_governance_does_not_bypass_phase4_replay_scope_requirements": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Rollback Execution Governance Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final rollback governance readiness status: `{report['final_rollback_governance_readiness_status']}`",
        "- v3.4 Phase 5 is rollback-governance-contract-only.",
        "- No execution is enabled.",
        "- Live rollback execution remains prohibited.",
        "- Rollback contracts are planning and audit contracts only.",
        "- Rollback governance does not bypass Phase 1 gates.",
        "- Rollback governance does not bypass Phase 2 authorization.",
        "- Rollback governance does not bypass Phase 3 sandboxing.",
        "- Rollback governance does not bypass Phase 4 replay scope requirements.",
        "",
        "## Boundary Requirements",
        "",
        "Rollback lineage, rollback target, and rollback validation must remain explicit and fail-visible. Missing rollback plan identity, rollback requirement, rollback plan evidence, lineage, target, validation, supported scope, environment match, and session match are explicit blockers.",
        "",
        "## Explicit Non-Enablement",
        "",
        "- No runtime execution is enabled.",
        "- No live replay execution is enabled.",
        "- No rollback execution is enabled.",
        "- No synthesis execution is enabled.",
        "- No decision routing is enabled.",
        "- No recommendation logic is enabled.",
        "- No autonomous planner mutation is enabled.",
        "- No production routing is enabled.",
        "- Runtime manifests are not consumed by default.",
        "- Production-authoritative manifests remain prohibited.",
        "- Rollback plans are not executed.",
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
            "Future phases may consume these rollback governance contracts as planning evidence, but this phase must not execute rollback plans or any runtime behavior. Any future controlled execution experiment must still satisfy Phase 1 gates, Phase 2 authorization, Phase 3 sandboxing, Phase 4 replay scope requirements, and explicit rollback evidence.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    sandbox = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    replay_scope = default_replay_safe_execution_scope_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
    )
    base = default_rollback_execution_governance_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
    )
    contracts = {
        "valid_rollback_governance_readiness": base,
        "missing_rollback_plan_id_blocked": replace(base, rollback_plan_id=""),
        "rollback_not_required_blocked": replace(base, rollback_required=False),
        "missing_rollback_plan_blocked": replace(base, rollback_plan_present=False),
        "missing_rollback_lineage_blocked": replace(base, rollback_lineage_present=False),
        "missing_rollback_target_blocked": replace(base, rollback_target_present=False),
        "missing_rollback_validation_blocked": replace(base, rollback_validation_present=False),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "unsupported_rollback_scope_blocked": replace(base, rollback_scope_supported=False),
        "live_rollback_execution_request_blocked": replace(base, live_rollback_execution_requested=True),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_rollback_execution_governance_contract(contract)
        results[scenario_id] = {
            **summarize_rollback_execution_governance_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        ROLLBACK_GOVERNANCE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_ROLLBACK_PLAN_ID,
        BLOCKED_ROLLBACK_NOT_REQUIRED,
        BLOCKED_ROLLBACK_PLAN_MISSING,
        BLOCKED_ROLLBACK_LINEAGE_MISSING,
        BLOCKED_ROLLBACK_TARGET_MISSING,
        BLOCKED_ROLLBACK_VALIDATION_MISSING,
        BLOCKED_ROLLBACK_ENVIRONMENT_MISMATCH,
        BLOCKED_ROLLBACK_SESSION_MISMATCH,
        BLOCKED_ROLLBACK_SCOPE_UNSUPPORTED,
        BLOCKED_LIVE_ROLLBACK_EXECUTION_PROHIBITED,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_rollback_execution_governance_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_rollback_execution_governance_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
