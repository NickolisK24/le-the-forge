"""Generate the v3.4 controlled execution readiness audit report."""

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
from app.runtime_intelligence.controlled_execution_readiness_audit import (  # noqa: E402
    BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN,
    BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS,
    BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS,
    BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS,
    BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS,
    BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS,
    BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    EXPECTED_PHASE_READINESS,
    MANUAL_REVIEW_REQUIRED,
    V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
    build_controlled_execution_readiness_audit_from_reports,
    default_controlled_execution_readiness_audit_contract,
    evaluate_controlled_execution_readiness_audit,
    summarize_controlled_execution_readiness_audit,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_controlled_execution_readiness_audit_report(repo_root: Path | None = None) -> dict[str, Any]:
    contract = build_controlled_execution_readiness_audit_from_reports(repo_root)
    focused = evaluate_controlled_execution_readiness_audit(contract)
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    report = {
        "schema_version": "v3_4.controlled_execution_readiness_audit_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_10_controlled_execution_readiness_audit",
        "recommendation": "V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING_ONLY",
        "v3_4_phase_10_readiness_audit_only": True,
        "planning_only": True,
        "audit_only": True,
        "execution_enabled": False,
        "controlled_execution_authorized": False,
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
        "final_v3_4_readiness_status": focused["status"],
        "controlled_execution_readiness_audit": focused,
        "phase_report_evidence": list(contract.phase_report_evidence),
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "expected_phase_count": len(EXPECTED_PHASE_READINESS),
            "audited_phase_count": sum(1 for row in contract.phase_report_evidence if row.get("readable") is True),
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "ready_scenario_count": status_distribution.get(V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "governance_chain_compatible": focused["governance_chain_compatible"],
            "production_behavior_detected": focused["production_behavior_detected"],
            "execution_enabled": False,
            "controlled_execution_authorized": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_10_is_readiness_audit_only": True,
            "planning_only": True,
            "audit_only": True,
            "execution_enabled": False,
            "controlled_execution_authorized": False,
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
            "experiment_execution_enabled": False,
            "audit_log_writing_enabled": False,
            "phase10_does_not_bypass_phase1_through_phase9_governance": True,
            "passing_readiness_does_not_authorize_execution": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Controlled Execution Readiness Audit",
        "",
        "## Phase Status",
        "",
        f"- Final v3.4 readiness status: `{report['final_v3_4_readiness_status']}`",
        "- v3.4 Phase 10 is readiness-audit-only.",
        "- No execution is enabled.",
        "- No controlled execution is authorized.",
        "- Readiness means only future controlled execution planning may continue.",
        "- Production runtime remains prohibited.",
        "- Default runtime manifest consumption remains disabled.",
        "- Production-authoritative manifest treatment remains prohibited.",
        "- Recommendation logic remains prohibited.",
        "- Runtime execution remains prohibited.",
        "- Live replay execution remains prohibited.",
        "- Rollback execution remains prohibited.",
        "- Synthesis execution remains prohibited.",
        "- Decision routing remains prohibited.",
        "- Autonomous mutation remains prohibited.",
        "- Audit log writing remains prohibited.",
        "- Phase 10 does not bypass any Phase 1-9 governance requirement.",
        "",
        "## Audited Governance Chain",
        "",
    ]
    for phase in report["controlled_execution_readiness_audit"]["phase_readiness"]:
        lines.append(
            f"- `{phase['phase_id']}` -> `{phase['status']}` (expected `{phase['expected_status']}`)"
        )
    lines.extend(
        [
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
            "## Readiness Outcomes",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['status']}`")
    lines.extend(
        [
            "",
            "## Future Phase Boundary",
            "",
            "Future phases may use this readiness audit as planning evidence only. This audit does not authorize controlled execution and must not be treated as runtime, replay, rollback, synthesis, decision routing, recommendation, mutation, experiment, audit-writing, external-side-effect, or production behavior.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_controlled_execution_readiness_audit_contract()
    contracts = {
        "valid_complete_v3_4_readiness": base,
        "missing_phase_1_readiness_blocked": replace(base, controlled_execution_gate_status=""),
        "missing_phase_2_readiness_blocked": replace(base, non_production_authorization_status=""),
        "missing_phase_3_readiness_blocked": replace(base, execution_session_sandboxing_status=""),
        "missing_phase_4_readiness_blocked": replace(base, replay_safe_execution_scope_status=""),
        "missing_phase_5_readiness_blocked": replace(base, rollback_execution_governance_status=""),
        "missing_phase_6_readiness_blocked": replace(base, execution_drift_escalation_status=""),
        "missing_phase_7_readiness_blocked": replace(base, controlled_runtime_mutation_boundary_status=""),
        "missing_phase_8_readiness_blocked": replace(base, controlled_experiment_isolation_status=""),
        "missing_phase_9_readiness_blocked": replace(base, execution_audit_logging_status=""),
        "incompatible_governance_chain_blocked": replace(base, governance_chain_compatible=False),
        "production_behavior_detected_blocked": replace(base, production_behavior_detected=True),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_controlled_execution_readiness_audit(contract)
        results[scenario_id] = {
            **summarize_controlled_execution_readiness_audit(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        V3_4_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_CONTROLLED_EXECUTION_GATE_CONTRACTS,
        BLOCKED_MISSING_NON_PRODUCTION_AUTHORIZATION_CONTRACTS,
        BLOCKED_MISSING_EXECUTION_SESSION_SANDBOXING_CONTRACTS,
        BLOCKED_MISSING_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS,
        BLOCKED_MISSING_ROLLBACK_EXECUTION_GOVERNANCE_CONTRACTS,
        BLOCKED_MISSING_EXECUTION_DRIFT_ESCALATION_CONTRACTS,
        BLOCKED_MISSING_CONTROLLED_RUNTIME_MUTATION_BOUNDARY_CONTRACTS,
        BLOCKED_MISSING_CONTROLLED_EXPERIMENT_ISOLATION_CONTRACTS,
        BLOCKED_MISSING_EXECUTION_AUDIT_LOGGING_CONTRACTS,
        BLOCKED_INCOMPATIBLE_GOVERNANCE_CHAIN,
        BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_controlled_execution_readiness_audit_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_CONTROLLED_EXECUTION_READINESS_AUDIT.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_controlled_execution_readiness_audit_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
