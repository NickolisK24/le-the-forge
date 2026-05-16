"""Generate the v3.5 governance consumption orchestration contracts report."""

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
from app.runtime_orchestration import (  # noqa: E402
    BLOCKED_COMPATIBILITY_REQUIREMENT,
    BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT,
    BLOCKED_EXECUTION_BEHAVIOR_DETECTED,
    BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT,
    BLOCKED_MISSING_GOVERNANCE_DEPENDENCY,
    BLOCKED_MISSING_ORCHESTRATION_IDENTITY,
    BLOCKED_MISSING_REPLAY_LINEAGE,
    BLOCKED_MISSING_ROLLBACK_LINEAGE,
    BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN,
    BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE,
    GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
    default_governance_consumption_contract,
    default_orchestration_blockers,
    default_orchestration_boundary_model,
    default_orchestration_visibility_model,
    evaluate_governance_consumption_contract,
    export_orchestration_blockers,
    export_orchestration_boundary,
    export_orchestration_visibility,
    summarize_governance_consumption_result,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_5_governance_consumption_contracts_report() -> dict[str, Any]:
    boundary = default_orchestration_boundary_model()
    visibility = default_orchestration_visibility_model()
    blockers = default_orchestration_blockers()
    scenarios = _scenario_results()
    status_distribution = _status_distribution(scenarios)
    focused = scenarios["valid_governance_consumption_planning"]
    report = {
        "schema_version": "v3_5.governance_consumption_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.5_phase_1_governance_consumption_orchestration_contracts",
        "recommendation": "GOVERNANCE_CONSUMPTION_ORCHESTRATION_CONTRACTS_READY_FOR_PLANNING_ONLY",
        "planning_only": True,
        "non_production": True,
        "governance_first": True,
        "runtime_execution_enabled": False,
        "orchestration_execution_enabled": False,
        "autonomous_orchestration_enabled": False,
        "recommendation_system_enabled": False,
        "decision_routing_enabled": False,
        "production_routing_enabled": False,
        "persistent_mutation_enabled": False,
        "state_writes_enabled": False,
        "audit_log_writes_enabled": False,
        "external_side_effects_enabled": False,
        "production_authoritative_manifests_enabled": False,
        "production_runtime_consumption_enabled": False,
        "experiment_execution_enabled": False,
        "self_modifying_orchestration_enabled": False,
        "hidden_fallback_logic_enabled": False,
        "final_governance_consumption_status": focused["status"],
        "orchestration_governance_philosophy": [
            "correctness first",
            "deterministic orchestration planning only",
            "governance-chain preservation",
            "replay-safe lineage",
            "rollback-safe lineage",
            "explicit unsupported states",
            "explicit orchestration boundaries",
            "explainable orchestration visibility",
            "deterministic validation",
            "operational auditability",
        ],
        "deterministic_orchestration_limitations": [
            "contracts describe governance consumption planning only",
            "contracts do not execute orchestration flows",
            "contracts do not route decisions",
            "contracts do not mutate state",
            "contracts do not write audit logs",
        ],
        "unsupported_orchestration_states": list(boundary.unsupported_orchestration_states),
        "prohibited_orchestration_domains": list(boundary.prohibited_orchestration_domains),
        "allowed_orchestration_domains": list(boundary.allowed_orchestration_domains),
        "boundary_model": export_orchestration_boundary(boundary),
        "visibility_model": export_orchestration_visibility(visibility),
        "blocker_models": export_orchestration_blockers(blockers),
        "scenario_results": scenarios,
        "status_distribution": status_distribution,
        "summary": {
            "scenario_count": len(scenarios),
            "allowed_status_count": len(status_distribution),
            "ready_scenario_count": status_distribution.get(
                GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
                0,
            ),
            "blocked_scenario_count": sum(
                count for status, count in status_distribution.items() if status.startswith("blocked_")
            ),
            "governance_dependency_rule_count": len(focused["contract"]["governance_dependency_ids"]),
            "unsupported_state_count": len(boundary.unsupported_orchestration_states),
            "prohibited_domain_count": len(boundary.prohibited_orchestration_domains),
            "blocker_model_count": len(blockers),
            "replay_safe_guarantee": focused["replay_safe_contract_generation"],
            "rollback_safe_guarantee": focused["rollback_safe_contract_generation"],
            "compatibility_guarantee": focused["compatibility_safe_evolution"],
            "auditability_guarantee": focused["auditability"],
            "deterministic": True,
        },
        "safety_confirmations": {
            "governance_consumption_planning_only": True,
            "not_orchestration_execution": True,
            "runtime_execution_enabled": False,
            "orchestration_execution_enabled": False,
            "autonomous_orchestration_enabled": False,
            "recommendation_system_enabled": False,
            "decision_routing_enabled": False,
            "production_routing_enabled": False,
            "persistent_mutation_enabled": False,
            "state_writes_enabled": False,
            "audit_log_writes_enabled": False,
            "external_side_effects_enabled": False,
            "production_authoritative_manifests_enabled": False,
            "production_runtime_consumption_enabled": False,
            "experiment_execution_enabled": False,
            "self_modifying_orchestration_enabled": False,
            "hidden_fallback_logic_enabled": False,
        },
    }
    report["deterministic_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.5 Governance Consumption Orchestration Contracts",
        "",
        "## Phase Boundary",
        "",
        f"- Final governance consumption status: `{report['final_governance_consumption_status']}`",
        "- This phase does NOT enable orchestration execution.",
        "- This phase does NOT enable autonomous behavior.",
        "- This phase does NOT enable runtime routing.",
        "- This phase ONLY establishes deterministic orchestration governance contracts.",
        "- Governance consumption planning only.",
        "",
        "## Governance Philosophy",
        "",
    ]
    lines.extend(f"- {item}" for item in report["orchestration_governance_philosophy"])
    lines.extend(
        [
            "",
            "## Deterministic Orchestration Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["deterministic_orchestration_limitations"])
    lines.extend(
        [
            "",
            "## Unsupported Orchestration States",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in report["unsupported_orchestration_states"])
    lines.extend(
        [
            "",
            "## Prohibited Orchestration Domains",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in report["prohibited_orchestration_domains"])
    lines.extend(
        [
            "",
            "## Governance Dependency Rules",
            "",
            "Future orchestration planning must preserve explicit authorization, governance dependencies, replay lineage, rollback lineage, compatibility requirements, and non-production environment isolation before any later phase may consume these contracts.",
            "",
            "## Guarantees",
            "",
            "- Replay-safe guarantees are explicit and hash-stable.",
            "- Rollback-safe guarantees are explicit and hash-stable.",
            "- Compatibility guarantees are explicit and fail-visible.",
            "- Auditability guarantees are explicit and deterministic.",
            "- Non-execution guarantees are explicit across all prohibited execution, routing, mutation, and side-effect surfaces.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, result in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{result['status']}`")
    lines.extend(
        [
            "",
            "## Explicit Non-Execution Guarantees",
            "",
            "- Runtime execution remains prohibited.",
            "- Orchestration execution remains prohibited.",
            "- Autonomous orchestration remains prohibited.",
            "- Production routing remains prohibited.",
            "- Mutation behavior remains prohibited.",
            "- Audit log writes remain prohibited.",
            "- External side effects remain prohibited.",
            "- The repository remains planning-only.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    base = default_governance_consumption_contract()
    contracts = {
        "valid_governance_consumption_planning": base,
        "missing_orchestration_identity_blocked": replace(base, orchestration_request_id=""),
        "missing_authorization_requirement_blocked": replace(base, authorization_state="missing"),
        "missing_governance_dependency_blocked": replace(base, governance_dependency_ids=()),
        "missing_replay_lineage_blocked": replace(base, replay_lineage_id=""),
        "missing_rollback_lineage_blocked": replace(base, rollback_lineage_id=""),
        "compatibility_requirement_blocked": replace(base, compatibility_verified=False),
        "unsupported_state_visible_blocked": replace(base, unsupported_orchestration_states=("unsupported_orchestration_scope",)),
        "prohibited_domain_blocked": replace(base, requested_orchestration_domain="runtime_execution"),
        "environment_isolation_blocked": replace(base, environment_isolated=False),
        "execution_behavior_detected_blocked": replace(base, orchestration_execution_enabled=True),
    }
    results: dict[str, dict[str, Any]] = {}
    for scenario_id, contract in contracts.items():
        result = evaluate_governance_consumption_contract(contract)
        results[scenario_id] = {
            **summarize_governance_consumption_result(result),
            "blockers": result["blockers"],
            "contract": result["contract"],
        }
    return results


def _status_distribution(results: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = (
        GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
        BLOCKED_MISSING_ORCHESTRATION_IDENTITY,
        BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT,
        BLOCKED_MISSING_GOVERNANCE_DEPENDENCY,
        BLOCKED_MISSING_REPLAY_LINEAGE,
        BLOCKED_MISSING_ROLLBACK_LINEAGE,
        BLOCKED_COMPATIBILITY_REQUIREMENT,
        BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE,
        BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN,
        BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT,
        BLOCKED_EXECUTION_BEHAVIOR_DETECTED,
    )
    return {status: sum(1 for result in results.values() if result["status"] == status) for status in statuses}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_5_governance_consumption_contracts_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_5_GOVERNANCE_CONSUMPTION_CONTRACTS.md"),
    )
    args = parser.parse_args()
    report = build_v3_5_governance_consumption_contracts_report()
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
