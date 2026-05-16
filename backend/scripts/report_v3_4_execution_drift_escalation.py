"""Generate the v3.4 execution drift escalation contracts report."""

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
from app.runtime_intelligence.execution_drift_escalation_contracts import (  # noqa: E402
    BLOCKED_DRIFT_AUDIT_MISSING,
    BLOCKED_DRIFT_BASELINE_MISSING,
    BLOCKED_DRIFT_CHECK_NOT_REQUIRED,
    BLOCKED_DRIFT_DETECTION_MISSING,
    BLOCKED_DRIFT_ENVIRONMENT_MISMATCH,
    BLOCKED_DRIFT_SESSION_MISMATCH,
    BLOCKED_DRIFT_SEVERITY_UNSUPPORTED,
    BLOCKED_MISSING_DRIFT_AUDIT_ID,
    BLOCKED_UNRESOLVED_DRIFT_DETECTED,
    DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    MANUAL_REVIEW_REQUIRED,
    default_execution_drift_escalation_contract,
    evaluate_execution_drift_escalation_contract,
    summarize_execution_drift_escalation_result,
)
from app.runtime_intelligence.execution_session_sandboxing_contracts import default_execution_session_sandbox_contract  # noqa: E402
from app.runtime_intelligence.non_production_execution_authorization_contracts import (  # noqa: E402
    default_non_production_execution_authorization_contract,
)
from app.runtime_intelligence.replay_safe_execution_scope_contracts import default_replay_safe_execution_scope_contract  # noqa: E402
from app.runtime_intelligence.rollback_execution_governance_contracts import (  # noqa: E402
    default_rollback_execution_governance_contract,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_execution_drift_escalation_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_drift_escalation_readiness"]
    report = {
        "schema_version": "v3_4.execution_drift_escalation_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_6_execution_drift_escalation_contracts",
        "recommendation": "EXECUTION_DRIFT_ESCALATION_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_6_drift_escalation_contract_only": True,
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
        "automatic_drift_resolution_enabled": False,
        "drift_severity_downgrade_enabled": False,
        "unresolved_drift_allowed": False,
        "final_drift_escalation_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "drift_escalation_ready_scenario_count": status_distribution.get(
                DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0
            ),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "phase1_gate_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["drift_escalation_does_not_bypass_gate"]
            ),
            "phase2_authorization_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["drift_escalation_does_not_bypass_authorization"]
            ),
            "phase3_sandbox_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["drift_escalation_does_not_bypass_sandbox"]
            ),
            "phase4_replay_scope_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["drift_escalation_does_not_bypass_replay_scope"]
            ),
            "phase5_rollback_governance_compatible_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["drift_escalation_does_not_bypass_rollback_governance"]
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
            "automatic_drift_resolution_enabled": False,
            "drift_severity_downgrade_enabled": False,
            "unresolved_drift_allowed": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_6_is_drift_escalation_contract_only": True,
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
            "automatic_drift_resolution_enabled": False,
            "drift_severity_downgrade_enabled": False,
            "unresolved_drift_allowed": False,
            "drift_escalation_does_not_bypass_phase1_execution_gates": True,
            "drift_escalation_does_not_bypass_phase2_authorization": True,
            "drift_escalation_does_not_bypass_phase3_sandboxing": True,
            "drift_escalation_does_not_bypass_phase4_replay_scope_requirements": True,
            "drift_escalation_does_not_bypass_phase5_rollback_governance": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Execution Drift Escalation Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final drift escalation readiness status: `{report['final_drift_escalation_readiness_status']}`",
        "- v3.4 Phase 6 is drift-escalation-contract-only.",
        "- No execution is enabled.",
        "- Drift is not resolved automatically.",
        "- Unresolved drift remains fail-visible.",
        "- Drift escalation does not bypass Phase 1 gates.",
        "- Drift escalation does not bypass Phase 2 authorization.",
        "- Drift escalation does not bypass Phase 3 sandboxing.",
        "- Drift escalation does not bypass Phase 4 replay scope requirements.",
        "- Drift escalation does not bypass Phase 5 rollback governance.",
        "",
        "## Boundary Requirements",
        "",
        "Drift audit identity, drift check requirements, baseline evidence, detection evidence, supported severity, environment match, and session match are explicit eligibility inputs. Missing drift evidence, unsupported severity, and unresolved drift are deterministic blockers. Unsupported drift severities must remain blocked or require manual review.",
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
        "- Drift is not automatically resolved or downgraded.",
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
            "Future phases may consume these drift escalation contracts as planning evidence, but this phase must not execute runtime behavior, replay behavior, rollback behavior, synthesis, decision routing, recommendation logic, or planner mutation. Any future controlled execution experiment must still satisfy Phase 1 gates, Phase 2 authorization, Phase 3 sandboxing, Phase 4 replay scope requirements, Phase 5 rollback governance, and explicit drift escalation evidence.",
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
    base = default_execution_drift_escalation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
    )
    contracts = {
        "valid_drift_escalation_readiness": base,
        "missing_drift_audit_id_blocked": replace(base, drift_audit_id=""),
        "drift_check_not_required_blocked": replace(base, drift_check_required=False),
        "missing_drift_audit_blocked": replace(base, drift_audit_present=False),
        "missing_drift_baseline_blocked": replace(base, drift_baseline_present=False),
        "missing_drift_detection_blocked": replace(base, drift_detection_present=False),
        "unresolved_drift_detected_blocked": replace(base, unresolved_drift_detected=True),
        "unsupported_drift_severity_blocked": replace(base, drift_severity="unknown"),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_execution_drift_escalation_contract(contract)
        results[scenario_id] = {
            **summarize_execution_drift_escalation_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        DRIFT_ESCALATION_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_DRIFT_AUDIT_ID,
        BLOCKED_DRIFT_CHECK_NOT_REQUIRED,
        BLOCKED_DRIFT_AUDIT_MISSING,
        BLOCKED_DRIFT_BASELINE_MISSING,
        BLOCKED_DRIFT_DETECTION_MISSING,
        BLOCKED_UNRESOLVED_DRIFT_DETECTED,
        BLOCKED_DRIFT_SEVERITY_UNSUPPORTED,
        BLOCKED_DRIFT_ENVIRONMENT_MISMATCH,
        BLOCKED_DRIFT_SESSION_MISMATCH,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_execution_drift_escalation_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_EXECUTION_DRIFT_ESCALATION_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_execution_drift_escalation_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
