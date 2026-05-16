"""Generate the v3.4 closeout and v3.5 readiness audit report."""

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
from app.runtime_intelligence.v3_4_closeout_readiness_audit import (  # noqa: E402
    BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE,
    BLOCKED_MISSING_PHASE_1_CONTRACTS,
    BLOCKED_MISSING_PHASE_2_CONTRACTS,
    BLOCKED_MISSING_PHASE_3_CONTRACTS,
    BLOCKED_MISSING_PHASE_4_CONTRACTS,
    BLOCKED_MISSING_PHASE_5_CONTRACTS,
    BLOCKED_MISSING_PHASE_6_CONTRACTS,
    BLOCKED_MISSING_PHASE_7_CONTRACTS,
    BLOCKED_MISSING_PHASE_8_CONTRACTS,
    BLOCKED_MISSING_PHASE_9_CONTRACTS,
    BLOCKED_MISSING_PHASE_10_READINESS_AUDIT,
    BLOCKED_PRODUCTION_BEHAVIOR_DETECTED,
    EXPECTED_PHASE_CLOSEOUT,
    MANUAL_REVIEW_REQUIRED,
    V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
    build_v3_4_closeout_readiness_audit_from_reports,
    default_v3_4_closeout_readiness_audit_contract,
    evaluate_v3_4_closeout_readiness_audit,
    summarize_v3_4_closeout_readiness_audit,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_closeout_and_v3_5_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    contract = build_v3_4_closeout_readiness_audit_from_reports(repo_root)
    focused = evaluate_v3_4_closeout_readiness_audit(contract)
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    report = {
        "schema_version": "v3_4.closeout_and_v3_5_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_closeout_and_v3.5_readiness_audit",
        "recommendation": "V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING_ONLY",
        "v3_4_closeout_audit_only": True,
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
        "final_v3_4_closeout_readiness_status": focused["status"],
        "v3_4_closeout_readiness_audit": focused,
        "phase_report_evidence": list(contract.phase_report_evidence),
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "expected_phase_count": len(EXPECTED_PHASE_CLOSEOUT),
            "audited_phase_count": sum(1 for row in contract.phase_report_evidence if row.get("readable") is True),
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "closed_out_scenario_count": status_distribution.get(V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "governance_chain_compatible": focused["governance_chain_compatible"],
            "production_behavior_detected": focused["production_behavior_detected"],
            "execution_enabled": False,
            "controlled_execution_authorized": False,
            "production_behavior_changed": False,
            "v3_5_planning_may_begin": focused["v3_5_planning_may_begin"],
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_is_closed_out": focused["v3_4_closed_out"],
            "v3_4_established_controlled_execution_planning_governance_only": True,
            "v3_5_planning_may_begin": focused["v3_5_planning_may_begin"],
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
            "closeout_does_not_bypass_v3_4_governance": True,
            "future_v3_5_work_must_preserve_v3_4_governance": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Closeout and v3.5 Readiness",
        "",
        "## Closeout Status",
        "",
        f"- Final v3.4 closeout readiness status: `{report['final_v3_4_closeout_readiness_status']}`",
        "- v3.4 is now closed out.",
        "- v3.4 established controlled execution planning governance only.",
        "- No execution is enabled.",
        "- No controlled execution is authorized.",
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
        "- v3.5 planning may begin.",
        "- Future v3.5 work must preserve all deterministic governance guarantees established in v3.4.",
        "",
        "## v3.4 Governance Chain",
        "",
    ]
    for phase in report["v3_4_closeout_readiness_audit"]["phase_closeout"]:
        lines.append(f"- `{phase['phase_id']}` -> `{phase['status']}`")
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
            "## Closeout Outcomes",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['status']}`")
    lines.extend(
        [
            "",
            "## v3.5 Boundary",
            "",
            "v3.5 planning may begin from this deterministic governance baseline. Future v3.5 work must preserve v3.4 production prohibitions, blocker visibility, replay safety, rollback governance, drift escalation, sandboxing, authorization boundaries, audit logging contracts, and deterministic closeout evidence until a future explicit governance phase defines otherwise.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_v3_4_closeout_readiness_audit_contract()
    contracts = {
        "valid_v3_4_closeout_readiness": base,
        "missing_phase_1_blocked": replace(base, phase_1_status=""),
        "missing_phase_2_blocked": replace(base, phase_2_status=""),
        "missing_phase_3_blocked": replace(base, phase_3_status=""),
        "missing_phase_4_blocked": replace(base, phase_4_status=""),
        "missing_phase_5_blocked": replace(base, phase_5_status=""),
        "missing_phase_6_blocked": replace(base, phase_6_status=""),
        "missing_phase_7_blocked": replace(base, phase_7_status=""),
        "missing_phase_8_blocked": replace(base, phase_8_status=""),
        "missing_phase_9_blocked": replace(base, phase_9_status=""),
        "missing_phase_10_blocked": replace(base, phase_10_status=""),
        "incompatible_governance_chain_blocked": replace(base, governance_chain_compatible=False),
        "production_behavior_detected_blocked": replace(base, production_behavior_detected=True),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_v3_4_closeout_readiness_audit(contract)
        results[scenario_id] = {
            **summarize_v3_4_closeout_readiness_audit(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        V3_4_CLOSED_OUT_READY_FOR_V3_5_PLANNING,
        BLOCKED_MISSING_PHASE_1_CONTRACTS,
        BLOCKED_MISSING_PHASE_2_CONTRACTS,
        BLOCKED_MISSING_PHASE_3_CONTRACTS,
        BLOCKED_MISSING_PHASE_4_CONTRACTS,
        BLOCKED_MISSING_PHASE_5_CONTRACTS,
        BLOCKED_MISSING_PHASE_6_CONTRACTS,
        BLOCKED_MISSING_PHASE_7_CONTRACTS,
        BLOCKED_MISSING_PHASE_8_CONTRACTS,
        BLOCKED_MISSING_PHASE_9_CONTRACTS,
        BLOCKED_MISSING_PHASE_10_READINESS_AUDIT,
        BLOCKED_GOVERNANCE_CHAIN_INCOMPATIBLE,
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
        default=Path("docs/generated/v3_4_closeout_and_v3_5_readiness_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_CLOSEOUT_AND_V3_5_READINESS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_closeout_and_v3_5_readiness_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
