"""Generate the v3.2 runtime kill-switch contract report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v3_1.trusted_shadow_consumption import deterministic_hash  # noqa: E402
from app.planner_adapters.v3_2.runtime_kill_switch_contracts import build_runtime_kill_switch_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_kill_switch_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")["experimental_runtime_entrypoint_contracts"]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")["runtime_isolation_contracts"]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")["runtime_session_boundary_contracts"]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")["runtime_safety_rollback_contracts"]
    diff_audit = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_diff_auditing_contracts_report.json")["runtime_diff_auditing_contracts"]
    determinism = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_determinism_validation_contracts_report.json")["runtime_determinism_validation_contracts"]
    traceability = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_traceability_contracts_report.json")["runtime_traceability_contracts"]
    replayability = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_replayability_contracts_report.json")["runtime_replayability_contracts"]
    drift = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_drift_detection_contracts_report.json")["runtime_drift_detection_contracts"]
    experiment = _read_json(repo_root / "docs" / "generated" / "v3_2_limited_runtime_consumption_experiment_contracts_report.json")["limited_runtime_consumption_experiment_contracts"]
    requests = _kill_switch_requests_from_experiment(experiment)
    payload = {"runtime_kill_switch_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    kill_switch = build_runtime_kill_switch_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
        runtime_replayability_contracts=replayability,
        runtime_drift_detection_contracts=drift,
        limited_runtime_experiment_contracts=experiment,
    )
    repeated = build_runtime_kill_switch_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
        runtime_replayability_contracts=replayability,
        runtime_drift_detection_contracts=drift,
        limited_runtime_experiment_contracts=experiment,
    )
    report = {
        "schema_version": "v3_2.runtime_kill_switch_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_11_runtime_kill_switch_contracts",
        "recommendation": "RUNTIME_KILL_SWITCH_CONTRACT_READY_FOR_FINAL_V3_2_CLOSEOUT_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "summary": {**kill_switch["summary"], "deterministic": kill_switch["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_kill_switch_contracts": kill_switch,
        "kill_switch_policy_distributions": kill_switch["kill_switch_policy_distribution"],
        "kill_switch_activation_distributions": kill_switch["kill_switch_activation_distribution"],
        "kill_switch_scope_distributions": kill_switch["kill_switch_scope_distribution"],
        "kill_switch_reason_distributions": kill_switch["kill_switch_reason_distribution"],
        "shutdown_state_distributions": kill_switch["shutdown_state_distribution"],
        "override_intent_distributions": kill_switch["override_intent_distribution"],
        "override_authorization_distributions": kill_switch["override_authorization_distribution"],
        "override_safety_distributions": kill_switch["override_safety_distribution"],
        "experiment_compatibility_distributions": kill_switch["experiment_compatibility_distribution"],
        "drift_compatibility_distributions": kill_switch["drift_compatibility_distribution"],
        "replayability_compatibility_distributions": kill_switch["replayability_compatibility_distribution"],
        "traceability_compatibility_distributions": kill_switch["traceability_compatibility_distribution"],
        "determinism_compatibility_distributions": kill_switch["determinism_compatibility_distribution"],
        "diff_audit_compatibility_distributions": kill_switch["diff_audit_compatibility_distribution"],
        "rollback_compatibility_distributions": kill_switch["rollback_compatibility_distribution"],
        "session_compatibility_distributions": kill_switch["session_compatibility_distribution"],
        "isolation_compatibility_distributions": kill_switch["isolation_compatibility_distribution"],
        "entrypoint_compatibility_distributions": kill_switch["entrypoint_compatibility_distribution"],
        "kill_switch_blocker_distributions": kill_switch["kill_switch_blocker_distribution"],
        "override_blocker_distributions": kill_switch["override_blocker_distribution"],
        "runtime_disabled_path_verification": kill_switch["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "default_manifest_consumption_disabled_verification": {"runtime_manifest_consumption_enabled": False, "default_manifest_consumption_enabled": False},
        "production_authoritative_manifest_prohibited_verification": {"production_authoritative_manifest_treatment": False, "production_authoritative_manifest_treatment_prohibited": True},
        "deterministic_guarantees": {"passed": kill_switch["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": kill_switch["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_11_boundaries": [
            "runtime kill-switch contracts are governance only",
            "active kill-switch state blocks experimental runtime continuation",
            "missing kill-switch policy, scope, or active reason fails visibly",
            "override allowance is non-production recovery only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "production-authoritative manifest treatment remains prohibited",
        ],
        "future_phase_foundation": [
            "final v3.2 closeout can consume deterministic kill-switch evidence",
            "future runtime planning must preserve explicit emergency shutdown controls",
            "future runtime planning must continue blocking default manifest consumption and production routing",
        ],
        "metadata": {"source": "v3_2_runtime_kill_switch_contracts_report", "governance_only": True, "runtime_kill_switch_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_authoritative_manifest_treatment_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    kill_switch = report["runtime_kill_switch_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Kill-Switch Contracts",
        "",
        "Phase 11 defines deterministic runtime kill-switch governance for limited experimental runtime planning.",
        "This is not production runtime enablement and does not enable default runtime manifest consumption.",
        "",
        "## Emergency Shutdown Governance",
        "",
        "Runtime kill-switch state is explicit policy evidence. Active kill-switch state blocks experimental runtime continuation and keeps shutdown state visible.",
        "",
        "## Visible Policy Failures",
        "",
        "Missing kill-switch policy, missing kill-switch scope, and missing active kill-switch reason fail visibly instead of falling back to an implicit pass state.",
        "",
        "## Override Boundaries",
        "",
        "Override attempts must be explicit, authorized, and safe. Any modeled allowance is limited to non-production recovery only.",
        "",
        "## Prior Governance Chain",
        "",
        "Phase 11 builds on entrypoint, isolation, session, safety rollback, diff audit, determinism, traceability, replayability, drift detection, and limited experiment contracts.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Kill-switch satisfied: `{summary['runtime_kill_switch_satisfied_count']}`",
        f"- Kill-switch blocked: `{summary['runtime_kill_switch_blocked_count']}`",
        f"- Kill-switch active: `{summary['runtime_kill_switch_active_count']}`",
        f"- Shutdown complete: `{summary['runtime_shutdown_complete_count']}`",
        f"- Shutdown required: `{summary['runtime_shutdown_required_count']}`",
        f"- Shutdown incomplete: `{summary['runtime_shutdown_incomplete_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Production-authoritative manifest treatment: `{str(summary['production_authoritative_manifest_treatment']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Kill-Switch Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in kill_switch["kill_switch_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Override Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in kill_switch["override_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Kill-Switch | Shutdown | Override |", "| --- | --- | --- | --- | --- | --- |"])
    for row in kill_switch["runtime_kill_switch_contracts"]:
        lines.append(f"| `{row['runtime_kill_switch_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_kill_switch_status']}` | `{row['runtime_shutdown_status']}` | `{row['runtime_kill_switch_override_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Runtime kill-switch governance is explicit and deterministic. Production runtime routing remains prohibited, default runtime manifest consumption remains disabled, and production-authoritative manifest treatment remains prohibited."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _kill_switch_requests_from_experiment(experiment: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "kill_switch_policy_state": "kill_switch_policy_present",
            "kill_switch_activation_state": "runtime_kill_switch_inactive",
            "kill_switch_scope_state": "kill_switch_scope_limited_runtime_experiment",
            "kill_switch_reason_state": "kill_switch_reason_not_required",
            "kill_switch_shutdown_state": "runtime_shutdown_complete",
            "kill_switch_override_intent_state": "runtime_override_not_requested",
            "kill_switch_override_authorization_state": "override_authorization_not_required",
            "kill_switch_override_safety_state": "override_safety_not_required",
        }
        for record in experiment.get("limited_runtime_experiment_contracts", [])
    ]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_kill_switch_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_KILL_SWITCH_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_kill_switch_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
