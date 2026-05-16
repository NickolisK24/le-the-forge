"""Generate the v3.4 controlled runtime mutation boundary contracts report."""

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
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (  # noqa: E402
    BLOCKED_AUTONOMOUS_MUTATION_REQUESTED,
    BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_MUTATION_BOUNDARY_ID,
    BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
    BLOCKED_MUTATION_ENVIRONMENT_MISMATCH,
    BLOCKED_MUTATION_SCOPE_MISSING,
    BLOCKED_MUTATION_SCOPE_UNSUPPORTED,
    BLOCKED_MUTATION_SESSION_MISMATCH,
    BLOCKED_PERSISTENT_MUTATION_REQUESTED,
    BLOCKED_PRODUCTION_MUTATION_REQUESTED,
    BLOCKED_STATE_WRITE_REQUESTED,
    MANUAL_REVIEW_REQUIRED,
    MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_controlled_runtime_mutation_boundary_contract,
    evaluate_controlled_runtime_mutation_boundary_contract,
    summarize_controlled_runtime_mutation_boundary_result,
)
from app.runtime_intelligence.execution_drift_escalation_contracts import default_execution_drift_escalation_contract  # noqa: E402
from app.runtime_intelligence.execution_session_sandboxing_contracts import default_execution_session_sandbox_contract  # noqa: E402
from app.runtime_intelligence.non_production_execution_authorization_contracts import (  # noqa: E402
    default_non_production_execution_authorization_contract,
)
from app.runtime_intelligence.replay_safe_execution_scope_contracts import default_replay_safe_execution_scope_contract  # noqa: E402
from app.runtime_intelligence.rollback_execution_governance_contracts import (  # noqa: E402
    default_rollback_execution_governance_contract,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_controlled_runtime_mutation_boundaries_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_mutation_boundary_readiness"]
    report = {
        "schema_version": "v3_4.controlled_runtime_mutation_boundary_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_7_controlled_runtime_mutation_boundary_contracts",
        "recommendation": "CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_7_mutation_boundary_contract_only": True,
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
        "persistent_mutation_enabled": False,
        "state_writes_enabled": False,
        "external_side_effects_enabled": False,
        "production_mutation_enabled": False,
        "mutation_execution_enabled": False,
        "final_mutation_boundary_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "mutation_boundary_ready_scenario_count": status_distribution.get(
                MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0
            ),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "phase1_gate_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["mutation_boundary_does_not_bypass_gate"]
            ),
            "phase2_authorization_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["mutation_boundary_does_not_bypass_authorization"]
            ),
            "phase3_sandbox_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["mutation_boundary_does_not_bypass_sandbox"]
            ),
            "phase4_replay_scope_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["mutation_boundary_does_not_bypass_replay_scope"]
            ),
            "phase5_rollback_governance_compatible_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["mutation_boundary_does_not_bypass_rollback_governance"]
            ),
            "phase6_drift_escalation_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["mutation_boundary_does_not_bypass_drift_escalation"]
            ),
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
            "persistent_mutation_enabled": False,
            "state_writes_enabled": False,
            "external_side_effects_enabled": False,
            "production_mutation_enabled": False,
            "mutation_execution_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_7_is_mutation_boundary_contract_only": True,
            "execution_enabled": False,
            "mutation_behavior_enabled": False,
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
            "persistent_mutation_enabled": False,
            "state_writes_enabled": False,
            "external_side_effects_enabled": False,
            "production_mutation_enabled": False,
            "mutation_execution_enabled": False,
            "mutation_boundaries_do_not_bypass_phase1_execution_gates": True,
            "mutation_boundaries_do_not_bypass_phase2_authorization": True,
            "mutation_boundaries_do_not_bypass_phase3_sandboxing": True,
            "mutation_boundaries_do_not_bypass_phase4_replay_scope_requirements": True,
            "mutation_boundaries_do_not_bypass_phase5_rollback_governance": True,
            "mutation_boundaries_do_not_bypass_phase6_drift_escalation": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Controlled Runtime Mutation Boundary Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final mutation boundary readiness status: `{report['final_mutation_boundary_readiness_status']}`",
        "- v3.4 Phase 7 is mutation-boundary-contract-only.",
        "- No execution is enabled.",
        "- No mutation behavior is enabled.",
        "- Persistent mutation remains prohibited.",
        "- Production mutation remains prohibited.",
        "- Autonomous mutation remains prohibited.",
        "- External side effects remain prohibited.",
        "- State writes remain prohibited.",
        "- Mutation boundaries do not bypass Phase 1 gates.",
        "- Mutation boundaries do not bypass Phase 2 authorization.",
        "- Mutation boundaries do not bypass Phase 3 sandboxing.",
        "- Mutation boundaries do not bypass Phase 4 replay scope requirements.",
        "- Mutation boundaries do not bypass Phase 5 rollback governance.",
        "- Mutation boundaries do not bypass Phase 6 drift escalation.",
        "",
        "## Boundary Requirements",
        "",
        "Mutation boundary identity, mutation scope, rollback governance linkage, drift escalation linkage, environment match, and session match are explicit eligibility inputs. Unsupported mutation scopes, persistent mutation requests, production mutation requests, autonomous mutation requests, external side-effect requests, and state-write requests are deterministic blockers. Unsupported mutation scopes must remain blocked or require manual review.",
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
        "- No persistent mutation is enabled.",
        "- No state writes are enabled.",
        "- No external side effects are enabled.",
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
            "Future phases may consume these mutation boundary contracts as planning evidence, but this phase must not execute runtime behavior, mutation behavior, replay behavior, rollback behavior, synthesis, decision routing, recommendation logic, state writes, external side effects, or planner mutation. Any future controlled execution experiment must still satisfy Phase 1 gates, Phase 2 authorization, Phase 3 sandboxing, Phase 4 replay scope requirements, Phase 5 rollback governance, Phase 6 drift escalation, and explicit mutation boundary evidence.",
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
    rollback = default_rollback_execution_governance_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
    )
    drift = default_execution_drift_escalation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
    )
    base = default_controlled_runtime_mutation_boundary_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
    )
    contracts = {
        "valid_mutation_boundary_readiness": base,
        "missing_mutation_boundary_id_blocked": replace(base, mutation_boundary_id=""),
        "missing_mutation_scope_blocked": replace(base, mutation_scope=""),
        "unsupported_mutation_scope_blocked": replace(base, mutation_scope_supported=False),
        "persistent_mutation_request_blocked": replace(base, persistent_mutation_requested=True),
        "production_mutation_request_blocked": replace(base, production_mutation_requested=True),
        "autonomous_mutation_request_blocked": replace(base, autonomous_mutation_requested=True),
        "external_side_effect_request_blocked": replace(base, external_side_effect_requested=True),
        "state_write_request_blocked": replace(base, state_write_requested=True),
        "missing_rollback_governance_link_blocked": replace(base, rollback_plan_id=""),
        "missing_drift_escalation_link_blocked": replace(base, drift_audit_id=""),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_controlled_runtime_mutation_boundary_contract(contract)
        results[scenario_id] = {
            **summarize_controlled_runtime_mutation_boundary_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        MUTATION_BOUNDARY_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_MUTATION_BOUNDARY_ID,
        BLOCKED_MUTATION_SCOPE_MISSING,
        BLOCKED_MUTATION_SCOPE_UNSUPPORTED,
        BLOCKED_PERSISTENT_MUTATION_REQUESTED,
        BLOCKED_PRODUCTION_MUTATION_REQUESTED,
        BLOCKED_AUTONOMOUS_MUTATION_REQUESTED,
        BLOCKED_EXTERNAL_SIDE_EFFECT_REQUESTED,
        BLOCKED_STATE_WRITE_REQUESTED,
        BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
        BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
        BLOCKED_MUTATION_ENVIRONMENT_MISMATCH,
        BLOCKED_MUTATION_SESSION_MISMATCH,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_controlled_runtime_mutation_boundaries_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_controlled_runtime_mutation_boundaries_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
