"""Generate the v3.4 replay-safe execution scope contracts report."""

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
from app.runtime_intelligence.replay_safe_execution_scope_contracts import (  # noqa: E402
    BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED,
    BLOCKED_MISSING_REPLAY_IDENTITY,
    BLOCKED_MISSING_REPLAY_SCOPE_ID,
    BLOCKED_REPLAY_CAPTURE_DISABLED,
    BLOCKED_REPLAY_ENVIRONMENT_MISMATCH,
    BLOCKED_REPLAY_LINEAGE_MISSING,
    BLOCKED_REPLAY_MANIFEST_MISSING,
    BLOCKED_REPLAY_MANIFEST_UNTRUSTED,
    BLOCKED_REPLAY_NOT_REQUIRED,
    BLOCKED_REPLAY_SCOPE_UNSUPPORTED,
    BLOCKED_REPLAY_SESSION_MISMATCH,
    MANUAL_REVIEW_REQUIRED,
    REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
    default_replay_safe_execution_scope_contract,
    evaluate_replay_safe_execution_scope_contract,
    summarize_replay_safe_execution_scope_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_4_replay_safe_execution_scopes_report() -> dict[str, Any]:
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_replay_safe_scope_readiness"]
    report = {
        "schema_version": "v3_4.replay_safe_execution_scope_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.4_phase_4_replay_safe_execution_scope_contracts",
        "recommendation": "REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "v3_4_phase_4_replay_scope_contract_only": True,
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
        "replay_manifest_execution_enabled": False,
        "replay_manifest_production_authoritative": False,
        "final_replay_scope_readiness_status": focused["status"],
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "replay_scope_ready_scenario_count": status_distribution.get(REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING, 0),
            "manual_review_required_scenario_count": status_distribution.get(MANUAL_REVIEW_REQUIRED, 0),
            "blocked_scenario_count": sum(count for status, count in status_distribution.items() if status.startswith("blocked_")),
            "phase1_gate_compatible_scenario_count": sum(1 for result in scenarios.values() if result["replay_scope_does_not_bypass_gate"]),
            "phase2_authorization_compatible_scenario_count": sum(1 for result in scenarios.values() if result["replay_scope_does_not_bypass_authorization"]),
            "phase3_sandbox_compatible_scenario_count": sum(1 for result in scenarios.values() if result["replay_scope_does_not_bypass_sandbox"]),
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
            "replay_manifest_execution_enabled": False,
            "replay_manifest_production_authoritative": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "safety_confirmations": {
            "v3_4_phase_4_is_replay_scope_contract_only": True,
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
            "replay_manifest_execution_enabled": False,
            "replay_manifest_production_authoritative": False,
            "replay_scope_does_not_bypass_phase1_execution_gates": True,
            "replay_scope_does_not_bypass_phase2_authorization": True,
            "replay_scope_does_not_bypass_phase3_sandboxing": True,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.4 Replay-Safe Execution Scope Contracts",
        "",
        "## Phase Status",
        "",
        f"- Final replay-scope readiness status: `{report['final_replay_scope_readiness_status']}`",
        "- v3.4 Phase 4 is replay-scope-contract-only.",
        "- No execution is enabled.",
        "- Live replay execution remains prohibited.",
        "- Replay scopes are planning and audit contracts only.",
        "- Replay scopes do not bypass Phase 1 gates.",
        "- Replay scopes do not bypass Phase 2 authorization.",
        "- Replay scopes do not bypass Phase 3 sandboxing.",
        "",
        "## Boundary Requirements",
        "",
        "Replay manifests must not be executed or treated as production-authoritative. Replay lineage must remain explicit and fail-visible. Missing replay scope identity, replay identity, replay requirements, capture, manifest evidence, trust, lineage, supported scope, environment match, and session match are explicit blockers.",
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
        "- Replay manifests are not executed.",
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
            "Future phases may consume these replay-scope contracts as planning evidence, but this phase must not execute replay manifests or any runtime behavior. Any future controlled execution experiment must still satisfy Phase 1 gates, Phase 2 authorization, Phase 3 sandboxing, and explicit replay lineage.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    gate = default_controlled_execution_gate_contract()
    authorization = default_non_production_execution_authorization_contract()
    sandbox = default_execution_session_sandbox_contract(gate_contract=gate, authorization_contract=authorization)
    base = default_replay_safe_execution_scope_contract(
        gate_contract=gate,
        authorization_contract=authorization,
        sandbox_contract=sandbox,
    )
    contracts = {
        "valid_replay_safe_scope_readiness": base,
        "missing_replay_scope_id_blocked": replace(base, replay_scope_id=""),
        "missing_replay_identity_blocked": replace(base, replay_identity=""),
        "replay_not_required_blocked": replace(base, replay_required=False),
        "replay_capture_disabled_blocked": replace(base, replay_capture_enabled=False),
        "missing_replay_manifest_blocked": replace(base, replay_manifest_present=False),
        "untrusted_replay_manifest_blocked": replace(base, replay_manifest_trusted=False),
        "missing_replay_lineage_blocked": replace(base, replay_lineage_present=False),
        "unsupported_replay_scope_blocked": replace(base, replay_scope_supported=False),
        "live_replay_execution_request_blocked": replace(base, live_replay_execution_requested=True),
        "environment_mismatch_blocked": replace(base, environment="ci", expected_environment="non_production"),
        "session_mismatch_blocked": replace(base, session_id="session-mismatch"),
        "manual_review_required": replace(base, manual_review_required=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_replay_safe_execution_scope_contract(contract)
        results[scenario_id] = {
            **summarize_replay_safe_execution_scope_result(result),
            "blockers": result["blockers"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        REPLAY_SCOPE_READY_FOR_CONTROLLED_EXECUTION_PLANNING,
        BLOCKED_MISSING_REPLAY_SCOPE_ID,
        BLOCKED_MISSING_REPLAY_IDENTITY,
        BLOCKED_REPLAY_NOT_REQUIRED,
        BLOCKED_REPLAY_CAPTURE_DISABLED,
        BLOCKED_REPLAY_MANIFEST_MISSING,
        BLOCKED_REPLAY_MANIFEST_UNTRUSTED,
        BLOCKED_REPLAY_LINEAGE_MISSING,
        BLOCKED_REPLAY_SCOPE_UNSUPPORTED,
        BLOCKED_LIVE_REPLAY_EXECUTION_PROHIBITED,
        BLOCKED_REPLAY_ENVIRONMENT_MISMATCH,
        BLOCKED_REPLAY_SESSION_MISMATCH,
        MANUAL_REVIEW_REQUIRED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_4_replay_safe_execution_scopes_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_4_REPLAY_SAFE_EXECUTION_SCOPE_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_4_replay_safe_execution_scopes_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
