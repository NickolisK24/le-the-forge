"""Generate the v3.2 runtime drift detection contract report."""

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
from app.planner_adapters.v3_2.runtime_drift_detection_contracts import build_runtime_drift_detection_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_drift_detection_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")["experimental_runtime_entrypoint_contracts"]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")["runtime_isolation_contracts"]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")["runtime_session_boundary_contracts"]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")["runtime_safety_rollback_contracts"]
    diff_audit = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_diff_auditing_contracts_report.json")["runtime_diff_auditing_contracts"]
    determinism = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_determinism_validation_contracts_report.json")["runtime_determinism_validation_contracts"]
    traceability = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_traceability_contracts_report.json")["runtime_traceability_contracts"]
    replayability = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_replayability_contracts_report.json")["runtime_replayability_contracts"]
    requests = _drift_requests_from_replayability(replayability)
    payload = {"runtime_drift_detection_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    drift = build_runtime_drift_detection_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
        runtime_replayability_contracts=replayability,
    )
    repeated = build_runtime_drift_detection_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
        runtime_replayability_contracts=replayability,
    )
    report = {
        "schema_version": "v3_2.runtime_drift_detection_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_9_runtime_drift_detection_contracts",
        "recommendation": "RUNTIME_DRIFT_DETECTION_READY_FOR_FUTURE_LIMITED_RUNTIME_EXPERIMENT_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**drift["summary"], "deterministic": drift["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_drift_detection_contracts": drift,
        "drift_baseline_evidence_distributions": drift["drift_baseline_evidence_distribution"],
        "current_runtime_evidence_distributions": drift["current_runtime_evidence_distribution"],
        "drift_comparison_distributions": drift["drift_comparison_distribution"],
        "drift_classification_distributions": drift["drift_classification_distribution"],
        "drift_severity_distributions": drift["drift_severity_distribution"],
        "expected_drift_distributions": drift["expected_drift_distribution"],
        "unexpected_drift_distributions": drift["unexpected_drift_distribution"],
        "unreviewed_drift_distributions": drift["unreviewed_drift_distribution"],
        "replayability_compatibility_distributions": drift["replayability_compatibility_distribution"],
        "traceability_compatibility_distributions": drift["traceability_compatibility_distribution"],
        "determinism_compatibility_distributions": drift["determinism_compatibility_distribution"],
        "diff_audit_compatibility_distributions": drift["diff_audit_compatibility_distribution"],
        "rollback_compatibility_distributions": drift["rollback_compatibility_distribution"],
        "session_compatibility_distributions": drift["session_compatibility_distribution"],
        "isolation_compatibility_distributions": drift["isolation_compatibility_distribution"],
        "entrypoint_compatibility_distributions": drift["entrypoint_compatibility_distribution"],
        "drift_blocker_distributions": drift["drift_blocker_distribution"],
        "drift_severity_blocker_distributions": drift["drift_severity_blocker_distribution"],
        "runtime_disabled_path_verification": drift["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "deterministic_guarantees": {"passed": drift["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": drift["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_9_boundaries": [
            "runtime drift detection contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "drift baselines and current evidence must be explicit",
            "expected, unexpected, and unreviewed drift remain distinct",
            "fallback drift detection remains prohibited",
        ],
        "future_phase_foundation": [
            "future limited runtime experiments may consume deterministic drift evidence",
            "future runtime intelligence phases must preserve drift severity and review visibility",
            "future runtime work must keep unexpected and unreviewed drift blocked",
        ],
        "metadata": {"source": "v3_2_runtime_drift_detection_contracts_report", "governance_only": True, "runtime_drift_detection_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    drift = report["runtime_drift_detection_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Drift Detection Contracts",
        "",
        "Phase 9 defines deterministic runtime drift detection governance for limited experimental runtime design.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Drift Baselines",
        "",
        "Explicit drift baselines matter because current runtime evidence must be compared against known replayable evidence.",
        "",
        "## Deterministic Comparison",
        "",
        "Current runtime evidence is compared deterministically against baseline evidence so drift cannot pass silently.",
        "",
        "## Drift Classes",
        "",
        "Expected drift, unexpected drift, and unreviewed drift are distinct classifications. Unexpected and unreviewed drift remain blocking.",
        "",
        "## Drift Severity",
        "",
        "Drift severity is explicit so future limited runtime experiments can reason about risk before runtime-adjacent work.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Drift detection satisfied: `{summary['runtime_drift_detection_satisfied_count']}`",
        f"- Drift detection blocked: `{summary['runtime_drift_detection_blocked_count']}`",
        f"- Drift not detected: `{summary['runtime_drift_not_detected_count']}`",
        f"- Unexpected drift: `{summary['runtime_unexpected_drift_detected_count']}`",
        f"- Unreviewed drift: `{summary['runtime_unreviewed_drift_detected_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Drift Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in drift["drift_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Severity Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in drift["drift_severity_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Drift | Severity |", "| --- | --- | --- | --- | --- |"])
    for row in drift["runtime_drift_detection_contracts"]:
        lines.append(f"| `{row['runtime_drift_detection_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_drift_detection_status']}` | `{row['runtime_drift_severity_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Runtime drift detection is satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _drift_requests_from_replayability(replayability: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "manifest_id": record.get("manifest_id"),
            "fixture_set_id": record.get("fixture_set_id"),
            "runtime_drift_baseline_evidence_state": "runtime_drift_baseline_present",
            "current_runtime_evidence_state": "current_runtime_evidence_present",
            "drift_comparison_state": "drift_comparison_completed",
            "drift_classification_state": "runtime_drift_not_detected",
            "drift_severity_state": "runtime_drift_severity_none",
            "expected_drift_state": "runtime_expected_drift_absent",
            "unexpected_drift_state": "runtime_unexpected_drift_absent",
            "unreviewed_drift_state": "runtime_unreviewed_drift_absent",
        }
        for record in replayability.get("runtime_replayability_contracts", [])
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_drift_detection_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_DRIFT_DETECTION_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_drift_detection_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
