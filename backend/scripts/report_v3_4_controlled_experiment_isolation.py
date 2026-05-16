"""Generate the v3.4 controlled experiment isolation contracts report."""

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
from app.runtime_intelligence.controlled_experiment_isolation_contracts import (  # noqa: E402
    BLOCKED_CROSS_EXPERIMENT_STATE_ACCESS,
    BLOCKED_EXPERIMENT_ENVIRONMENT_MISMATCH,
    BLOCKED_EXPERIMENT_EXECUTION_REQUESTED,
    BLOCKED_EXPERIMENT_NOT_ISOLATED,
    BLOCKED_EXPERIMENT_SCOPE_MISSING,
    BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED,
    BLOCKED_EXPERIMENT_SESSION_MISMATCH,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_EXPERIMENT_ID,
    BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
    BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
    BLOCKED_PERSISTENT_EXPERIMENT_STATE_REQUESTED,
    BLOCKED_PRODUCTION_STATE_ACCESS_REQUESTED,
    EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_controlled_experiment_isolation_contract,
    evaluate_controlled_experiment_isolation_contract,
    summarize_controlled_experiment_isolation_result,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (  # noqa: E402
    default_controlled_runtime_mutation_boundary_contract,
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


def build_v3_4_controlled_experiment_isolation_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_experiment_isolation_readiness"]
    report = {
        "schema_version": "v3_4.controlled_experiment_isolation_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_8_controlled_experiment_isolation_contracts",
        "recommendation": "CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_8_experiment_isolation_contract_only": True,
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
        "experiment_execution_enabled": False,
        "production_state_access_enabled": False,
        "production_mutation_enabled": False,
        "mutation_execution_enabled": False,
        "cross_experiment_state_access_enabled": False,
        "final_experiment_isolation_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "experiment_isolation_ready_scenario_count": status_distribution.get(
                EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0
            ),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "phase1_gate_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["experiment_isolation_does_not_bypass_gate"]
            ),
            "phase2_authorization_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["experiment_isolation_does_not_bypass_authorization"]
            ),
            "phase3_sandbox_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["experiment_isolation_does_not_bypass_sandbox"]
            ),
            "phase4_replay_scope_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["experiment_isolation_does_not_bypass_replay_scope"]
            ),
            "phase5_rollback_governance_compatible_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["experiment_isolation_does_not_bypass_rollback_governance"]
            ),
            "phase6_drift_escalation_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["experiment_isolation_does_not_bypass_drift_escalation"]
            ),
            "phase7_mutation_boundary_compatible_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["experiment_isolation_does_not_bypass_mutation_boundary"]
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
            "experiment_execution_enabled": False,
            "production_state_access_enabled": False,
            "production_mutation_enabled": False,
            "mutation_execution_enabled": False,
            "cross_experiment_state_access_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_8_is_experiment_isolation_contract_only": True,
            "execution_enabled": False,
            "experiment_execution_enabled": False,
            "mutation_behavior_enabled": False,
            "production_state_access_enabled": False,
            "persistent_experiment_state_enabled": False,
            "cross_experiment_state_access_enabled": False,
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
            "experiment_isolation_does_not_bypass_phase1_execution_gates": True,
            "experiment_isolation_does_not_bypass_phase2_authorization": True,
            "experiment_isolation_does_not_bypass_phase3_sandboxing": True,
            "experiment_isolation_does_not_bypass_phase4_replay_scope_requirements": True,
            "experiment_isolation_does_not_bypass_phase5_rollback_governance": True,
            "experiment_isolation_does_not_bypass_phase6_drift_escalation": True,
            "experiment_isolation_does_not_bypass_phase7_mutation_boundaries": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Controlled Experiment Isolation Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final experiment isolation readiness status: `{report['final_experiment_isolation_readiness_status']}`",
        "- v3.4 Phase 8 is experiment-isolation-contract-only.",
        "- No execution is enabled.",
        "- No experiment execution is enabled.",
        "- No mutation behavior is enabled.",
        "- Production state access remains prohibited.",
        "- Persistent experiment state remains prohibited.",
        "- Cross-experiment state access remains prohibited.",
        "- Experiment isolation does not bypass Phase 1 gates.",
        "- Experiment isolation does not bypass Phase 2 authorization.",
        "- Experiment isolation does not bypass Phase 3 sandboxing.",
        "- Experiment isolation does not bypass Phase 4 replay scope requirements.",
        "- Experiment isolation does not bypass Phase 5 rollback governance.",
        "- Experiment isolation does not bypass Phase 6 drift escalation.",
        "- Experiment isolation does not bypass Phase 7 mutation boundaries.",
        "",
        "## Boundary Requirements",
        "",
        "Experiment identity, experiment scope, isolation, mutation boundary linkage, drift escalation linkage, rollback governance linkage, environment match, and session match are explicit eligibility inputs. Unsupported experiment scopes, non-isolated experiment state, cross-experiment access, production state access, persistent experiment state, and experiment execution requests are deterministic blockers. Unsupported experiment scopes must remain blocked or require manual review.",
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
        "- No experiment execution is enabled.",
        "- No production state access is enabled.",
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
            "Future phases may consume these experiment isolation contracts as planning evidence, but this phase must not execute runtime behavior, experiment behavior, mutation behavior, replay behavior, rollback behavior, synthesis, decision routing, recommendation logic, state writes, external side effects, or planner mutation. Any future controlled execution experiment must still satisfy Phase 1 gates, Phase 2 authorization, Phase 3 sandboxing, Phase 4 replay scope requirements, Phase 5 rollback governance, Phase 6 drift escalation, Phase 7 mutation boundaries, and explicit experiment isolation evidence.",
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
    mutation = default_controlled_runtime_mutation_boundary_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
    )
    base = default_controlled_experiment_isolation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
    )
    contracts = {
        "valid_experiment_isolation_readiness": base,
        "missing_experiment_id_blocked": replace(base, experiment_id=""),
        "missing_experiment_scope_blocked": replace(base, experiment_scope=""),
        "unsupported_experiment_scope_blocked": replace(base, experiment_scope_supported=False),
        "non_isolated_experiment_blocked": replace(base, experiment_isolated=False),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "cross_experiment_state_access_blocked": replace(base, cross_experiment_state_access_requested=True),
        "production_state_access_blocked": replace(base, production_state_access_requested=True),
        "persistent_experiment_state_request_blocked": replace(base, persistent_experiment_state_requested=True),
        "experiment_execution_request_blocked": replace(base, experiment_execution_requested=True),
        "missing_mutation_boundary_link_blocked": replace(base, mutation_boundary_id=""),
        "missing_drift_escalation_link_blocked": replace(base, drift_audit_id=""),
        "missing_rollback_governance_link_blocked": replace(base, rollback_plan_id=""),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_controlled_experiment_isolation_contract(contract)
        results[scenario_id] = {
            **summarize_controlled_experiment_isolation_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        EXPERIMENT_ISOLATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_EXPERIMENT_ID,
        BLOCKED_EXPERIMENT_SCOPE_MISSING,
        BLOCKED_EXPERIMENT_SCOPE_UNSUPPORTED,
        BLOCKED_EXPERIMENT_NOT_ISOLATED,
        BLOCKED_EXPERIMENT_ENVIRONMENT_MISMATCH,
        BLOCKED_EXPERIMENT_SESSION_MISMATCH,
        BLOCKED_CROSS_EXPERIMENT_STATE_ACCESS,
        BLOCKED_PRODUCTION_STATE_ACCESS_REQUESTED,
        BLOCKED_PERSISTENT_EXPERIMENT_STATE_REQUESTED,
        BLOCKED_EXPERIMENT_EXECUTION_REQUESTED,
        BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
        BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
        BLOCKED_MISSING_ROLLBACK_GOVERNANCE_LINK,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_controlled_experiment_isolation_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_controlled_experiment_isolation_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
