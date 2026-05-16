"""Generate the v3.4 execution audit logging contracts report."""

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
    default_controlled_experiment_isolation_contract,
)
from app.runtime_intelligence.controlled_runtime_mutation_boundary_contracts import (  # noqa: E402
    default_controlled_runtime_mutation_boundary_contract,
)
from app.runtime_intelligence.execution_audit_logging_contracts import (  # noqa: E402
    AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    BLOCKED_AUDIT_ACTOR_MISSING,
    BLOCKED_AUDIT_ENVIRONMENT_MISMATCH,
    BLOCKED_AUDIT_EVENT_TYPE_MISSING,
    BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED,
    BLOCKED_AUDIT_HASH_MISSING,
    BLOCKED_AUDIT_LINEAGE_MISSING,
    BLOCKED_AUDIT_SESSION_MISMATCH,
    BLOCKED_AUDIT_TIMESTAMP_MISSING,
    BLOCKED_AUDIT_WRITE_REQUESTED,
    BLOCKED_MISSING_AUDIT_RECORD_ID,
    BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
    BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK,
    BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
    MANUAL_REVIEW_REQUIRED,
    default_execution_audit_logging_contract,
    evaluate_execution_audit_logging_contract,
    summarize_execution_audit_logging_result,
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


def build_v3_4_execution_audit_logging_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_audit_logging_readiness"]
    report = {
        "schema_version": "v3_4.execution_audit_logging_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_9_execution_audit_logging_contracts",
        "recommendation": "EXECUTION_AUDIT_LOGGING_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_9_audit_logging_contract_only": True,
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
        "audit_log_writing_enabled": False,
        "production_state_access_enabled": False,
        "production_mutation_enabled": False,
        "mutation_execution_enabled": False,
        "cross_experiment_state_access_enabled": False,
        "final_audit_logging_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "audit_logging_ready_scenario_count": status_distribution.get(
                AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0
            ),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "phase1_gate_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_gate"]
            ),
            "phase2_authorization_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_authorization"]
            ),
            "phase3_sandbox_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_sandbox"]
            ),
            "phase4_replay_scope_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_replay_scope"]
            ),
            "phase5_rollback_governance_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_rollback_governance"]
            ),
            "phase6_drift_escalation_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_drift_escalation"]
            ),
            "phase7_mutation_boundary_compatible_scenario_count": sum(
                1 for result in scenarios.values() if result["audit_logging_does_not_bypass_mutation_boundary"]
            ),
            "phase8_experiment_isolation_compatible_scenario_count": sum(
                1
                for result in scenarios.values()
                if result["audit_logging_does_not_bypass_experiment_isolation"]
            ),
            "execution_enabled": False,
            "experiment_execution_enabled": False,
            "audit_log_writing_enabled": False,
            "mutation_execution_enabled": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_9_is_audit_logging_contract_only": True,
            "execution_enabled": False,
            "audit_log_writing_enabled": False,
            "experiment_execution_enabled": False,
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
            "audit_logging_does_not_bypass_phase1_execution_gates": True,
            "audit_logging_does_not_bypass_phase2_authorization": True,
            "audit_logging_does_not_bypass_phase3_sandboxing": True,
            "audit_logging_does_not_bypass_phase4_replay_scope_requirements": True,
            "audit_logging_does_not_bypass_phase5_rollback_governance": True,
            "audit_logging_does_not_bypass_phase6_drift_escalation": True,
            "audit_logging_does_not_bypass_phase7_mutation_boundaries": True,
            "audit_logging_does_not_bypass_phase8_experiment_isolation": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Execution Audit Logging Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final audit logging readiness status: `{report['final_audit_logging_readiness_status']}`",
        "- v3.4 Phase 9 is audit-logging-contract-only.",
        "- No execution is enabled.",
        "- No audit log writing is enabled.",
        "- No experiment execution is enabled.",
        "- No mutation behavior is enabled.",
        "- Audit records are planning/audit contracts only.",
        "- Audit logging does not bypass Phase 1 gates.",
        "- Audit logging does not bypass Phase 2 authorization.",
        "- Audit logging does not bypass Phase 3 sandboxing.",
        "- Audit logging does not bypass Phase 4 replay scope requirements.",
        "- Audit logging does not bypass Phase 5 rollback governance.",
        "- Audit logging does not bypass Phase 6 drift escalation.",
        "- Audit logging does not bypass Phase 7 mutation boundaries.",
        "- Audit logging does not bypass Phase 8 experiment isolation.",
        "",
        "## Boundary Requirements",
        "",
        "Audit record identity, audit event type, audit hash, lineage, timestamp, actor, environment match, session match, and governance links are explicit eligibility inputs. Unsupported audit event types and missing audit lineage, timestamp, actor, or hash remain fail-visible blockers.",
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
        "- No experiment execution is enabled.",
        "- No audit log writing is enabled.",
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
            "Future phases may consume these audit logging contracts as planning evidence, but this phase must not write audit logs or execute runtime, experiment, mutation, replay, rollback, synthesis, decision routing, recommendation, state-write, external-side-effect, or planner-mutation behavior.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _base_contract():
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
    experiment = default_controlled_experiment_isolation_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
    )
    return default_execution_audit_logging_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
        replay_scope_contract=replay_scope,
        rollback_contract=rollback,
        drift_escalation_contract=drift,
        mutation_boundary_contract=mutation,
        experiment_isolation_contract=experiment,
    )


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = _base_contract()
    contracts = {
        "valid_audit_logging_readiness": base,
        "missing_audit_record_id_blocked": replace(base, audit_record_id=""),
        "missing_audit_event_type_blocked": replace(base, audit_event_type=""),
        "unsupported_audit_event_type_blocked": replace(base, audit_event_type="unsupported_event"),
        "missing_audit_hash_blocked": replace(base, audit_hash_present=False),
        "missing_audit_lineage_blocked": replace(base, audit_lineage_present=False),
        "missing_audit_timestamp_blocked": replace(base, audit_timestamp_present=False),
        "missing_audit_actor_blocked": replace(base, audit_actor_present=False),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "audit_write_request_blocked": replace(base, audit_write_requested=True),
        "missing_experiment_isolation_link_blocked": replace(base, experiment_id=""),
        "missing_mutation_boundary_link_blocked": replace(base, mutation_boundary_id=""),
        "missing_drift_escalation_link_blocked": replace(base, drift_audit_id=""),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_execution_audit_logging_contract(contract)
        results[scenario_id] = {
            **summarize_execution_audit_logging_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        AUDIT_LOGGING_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_AUDIT_RECORD_ID,
        BLOCKED_AUDIT_EVENT_TYPE_MISSING,
        BLOCKED_AUDIT_EVENT_TYPE_UNSUPPORTED,
        BLOCKED_AUDIT_HASH_MISSING,
        BLOCKED_AUDIT_LINEAGE_MISSING,
        BLOCKED_AUDIT_TIMESTAMP_MISSING,
        BLOCKED_AUDIT_ACTOR_MISSING,
        BLOCKED_AUDIT_ENVIRONMENT_MISMATCH,
        BLOCKED_AUDIT_SESSION_MISMATCH,
        BLOCKED_AUDIT_WRITE_REQUESTED,
        BLOCKED_MISSING_EXPERIMENT_ISOLATION_LINK,
        BLOCKED_MISSING_MUTATION_BOUNDARY_LINK,
        BLOCKED_MISSING_DRIFT_ESCALATION_LINK,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_execution_audit_logging_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_EXECUTION_AUDIT_LOGGING_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_execution_audit_logging_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
