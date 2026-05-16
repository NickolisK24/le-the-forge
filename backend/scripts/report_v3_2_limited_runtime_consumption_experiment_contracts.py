"""Generate the v3.2 limited runtime consumption experiment contract report."""

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
from app.planner_adapters.v3_2.limited_runtime_consumption_experiment_contracts import build_limited_runtime_consumption_experiment_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_limited_runtime_consumption_experiment_contracts_report() -> dict[str, Any]:
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
    requests = _experiment_requests_from_drift(drift)
    payload = {"limited_runtime_experiment_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    experiment = build_limited_runtime_consumption_experiment_contract(
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
    )
    repeated = build_limited_runtime_consumption_experiment_contract(
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
    )
    report = {
        "schema_version": "v3_2.limited_runtime_consumption_experiment_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_10_limited_runtime_consumption_experiment_contracts",
        "recommendation": "LIMITED_RUNTIME_CONSUMPTION_EXPERIMENT_ELIGIBLE_FOR_FUTURE_KILL_SWITCH_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "summary": {**experiment["summary"], "deterministic": experiment["deterministic_hash"] == repeated["deterministic_hash"]},
        "limited_runtime_consumption_experiment_contracts": experiment,
        "experiment_authorization_distributions": experiment["experiment_authorization_distribution"],
        "experiment_intent_distributions": experiment["experiment_intent_distribution"],
        "experiment_scope_distributions": experiment["experiment_scope_distribution"],
        "experiment_eligibility_distributions": experiment["experiment_eligibility_distribution"],
        "experiment_consumption_mode_distributions": experiment["experiment_consumption_mode_distribution"],
        "experiment_manifest_authority_distributions": experiment["experiment_manifest_authority_distribution"],
        "experiment_production_prohibition_distributions": experiment["experiment_production_prohibition_distribution"],
        "isolation_compatibility_distributions": experiment["isolation_compatibility_distribution"],
        "session_compatibility_distributions": experiment["session_compatibility_distribution"],
        "safety_rollback_compatibility_distributions": experiment["safety_rollback_compatibility_distribution"],
        "diff_audit_compatibility_distributions": experiment["diff_audit_compatibility_distribution"],
        "determinism_compatibility_distributions": experiment["determinism_compatibility_distribution"],
        "traceability_compatibility_distributions": experiment["traceability_compatibility_distribution"],
        "replayability_compatibility_distributions": experiment["replayability_compatibility_distribution"],
        "drift_detection_compatibility_distributions": experiment["drift_detection_compatibility_distribution"],
        "rollback_readiness_distributions": experiment["rollback_readiness_distribution"],
        "experiment_blocker_distributions": experiment["experiment_blocker_distribution"],
        "runtime_disabled_path_verification": experiment["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "default_manifest_consumption_disabled_verification": {"runtime_manifest_consumption_enabled": False, "default_manifest_consumption_enabled": False},
        "deterministic_guarantees": {"passed": experiment["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": experiment["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_10_boundaries": [
            "limited runtime consumption experiment contracts are governance only",
            "this phase is not production runtime enablement",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "production-authoritative manifest treatment remains prohibited",
            "experiment eligibility requires explicit authorization, intent, and limited non-production scope",
        ],
        "future_phase_foundation": [
            "future kill-switch phases may consume deterministic experiment eligibility evidence",
            "future closeout phases must preserve non-production manifest authority",
            "future runtime planning must continue to block default manifest consumption and production routing",
        ],
        "metadata": {"source": "v3_2_limited_runtime_consumption_experiment_contracts_report", "governance_only": True, "limited_runtime_consumption_experiment_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_authoritative_manifest_treatment_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    experiment = report["limited_runtime_consumption_experiment_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Limited Runtime Consumption Experiment Contracts",
        "",
        "Phase 10 defines deterministic limited runtime consumption experiment governance for non-production runtime planning.",
        "This is not production runtime enablement and does not enable default runtime manifest consumption.",
        "",
        "## Explicit Governance",
        "",
        "Limited runtime consumption experiments require explicit authorization, explicit intent, and explicit scope before eligibility can be considered.",
        "",
        "## Limited Scope",
        "",
        "Experiment scope must be limited, isolated, reversible, and non-production. Unsafe or missing scope fails visibly.",
        "",
        "## Manifest Authority",
        "",
        "Experiment manifests remain non-production-authoritative. Production-authoritative manifest treatment remains prohibited.",
        "",
        "## Prior Governance Chain",
        "",
        "Phase 10 builds on entrypoint, isolation, session, safety rollback, diff audit, determinism, traceability, replayability, and drift detection contracts.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Experiment eligible: `{summary['limited_runtime_experiment_eligible_count']}`",
        f"- Experiment blocked: `{summary['limited_runtime_experiment_blocked_count']}`",
        f"- Authorization missing: `{summary['experiment_authorization_missing_count']}`",
        f"- Unsafe scope: `{summary['experiment_scope_unsafe_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Production-authoritative manifest treatment: `{str(summary['production_authoritative_manifest_treatment']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Experiment Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in experiment["experiment_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Eligibility | Mode |", "| --- | --- | --- | --- | --- |"])
    for row in experiment["limited_runtime_experiment_contracts"]:
        lines.append(f"| `{row['limited_runtime_experiment_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['limited_runtime_experiment_status']}` | `{row['limited_runtime_consumption_mode_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Limited runtime experiment eligibility is governance-only. Production runtime routing remains prohibited, default runtime manifest consumption remains disabled, and production-authoritative manifest treatment remains prohibited."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _experiment_requests_from_drift(drift: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "experiment_authorization_state": "experiment_authorized",
            "experiment_intent_state": "limited_runtime_consumption_experiment_intent_explicit",
            "experiment_scope_state": "non_production_isolated_reversible_limited_scope",
            "experiment_eligibility_state": "experiment_eligibility_evaluated",
            "experiment_consumption_mode_state": "experimental_only_consumption_mode",
            "experiment_manifest_authority_state": "non_production_authoritative",
            "experiment_production_prohibition_state": "production_runtime_prohibited",
            "runtime_manifest_consumption_enabled_by_default": False,
            "production_routing_authorized_by_experiment": False,
        }
        for record in drift.get("runtime_drift_detection_contracts", [])
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
    parser.add_argument("--output", default="docs/generated/v3_2_limited_runtime_consumption_experiment_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_LIMITED_RUNTIME_CONSUMPTION_EXPERIMENT_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_limited_runtime_consumption_experiment_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
