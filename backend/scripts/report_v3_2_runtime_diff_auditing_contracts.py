"""Generate the v3.2 runtime diff auditing contract report."""

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
from app.planner_adapters.v3_2.runtime_diff_auditing_contracts import build_runtime_diff_audit_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_diff_auditing_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")[
        "runtime_safety_rollback_contracts"
    ]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")[
        "runtime_isolation_contracts"
    ]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")[
        "runtime_session_boundary_contracts"
    ]
    requests = _diff_requests_from_safety(safety)
    payload = {"runtime_diff_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    diff_audit = build_runtime_diff_audit_contract(
        payload,
        runtime_safety_rollback_contracts=safety,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
    )
    repeated = build_runtime_diff_audit_contract(
        payload,
        runtime_safety_rollback_contracts=safety,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
    )
    report = {
        "schema_version": "v3_2.runtime_diff_auditing_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_5_runtime_diff_auditing_contracts",
        "recommendation": "RUNTIME_DIFF_AUDIT_CONTRACT_READY_FOR_FUTURE_REPLAY_AND_DRIFT_DETECTION_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**diff_audit["summary"], "deterministic": diff_audit["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_diff_auditing_contracts": diff_audit,
        "runtime_mutation_distributions": diff_audit["runtime_mutation_distribution"],
        "runtime_drift_distributions": diff_audit["runtime_drift_distribution"],
        "runtime_transition_audit_distributions": diff_audit["runtime_transition_audit_distribution"],
        "runtime_snapshot_availability_distributions": diff_audit["runtime_snapshot_availability_distribution"],
        "rollback_audit_compatibility_distributions": diff_audit["rollback_audit_compatibility_distribution"],
        "isolation_audit_compatibility_distributions": diff_audit["isolation_audit_compatibility_distribution"],
        "session_audit_compatibility_distributions": diff_audit["session_audit_compatibility_distribution"],
        "runtime_mutation_blocker_distributions": diff_audit["runtime_mutation_blocker_distribution"],
        "runtime_drift_blocker_distributions": diff_audit["runtime_drift_blocker_distribution"],
        "phase_2_isolation_audit_compatibility_summary": diff_audit["phase_2_isolation_audit_compatibility"],
        "phase_3_session_audit_compatibility_summary": diff_audit["phase_3_session_audit_compatibility"],
        "phase_4_rollback_audit_compatibility_summary": diff_audit["phase_4_rollback_audit_compatibility"],
        "runtime_disabled_path_verification": diff_audit["runtime_disabled_path_verification"],
        "production_prohibited_verification": {
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
        },
        "deterministic_guarantees": {
            "passed": diff_audit["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": diff_audit["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_5_boundaries": [
            "runtime diff auditing contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "runtime state transitions must be explicitly audited",
            "runtime mutations and drift remain visible",
            "fallback diff auditing remains prohibited",
        ],
        "future_phase_foundation": [
            "future replayability phases may consume deterministic diff audit evidence",
            "future drift-detection phases must preserve explicit before and after runtime snapshots",
            "future runtime work must keep hidden transitions and silent mutations blocked",
        ],
        "metadata": {
            "source": "v3_2_runtime_diff_auditing_contracts_report",
            "governance_only": True,
            "runtime_diff_audit_contract_only": True,
            "runtime_behavior_enabled": False,
            "production_runtime_prohibited": True,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "planner_remap_performed": False,
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    audit = report["runtime_diff_auditing_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Diff Auditing Contracts",
        "",
        "Phase 5 defines deterministic runtime diff auditing governance for limited experimental runtime design.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Runtime Observability",
        "",
        "Runtime observability requires explicit pre-state and post-state snapshots. Hidden transitions remain blocked because future runtime work needs explainable before and after evidence.",
        "",
        "## Drift Detection",
        "",
        "Runtime drift must remain deterministic and visible. Unexpected drift is classified explicitly and cannot be collapsed into a generic pass state.",
        "",
        "## Mutation Auditability",
        "",
        "Runtime mutations must be explainable and auditable. Silent mutations and fallback diff auditing remain prohibited.",
        "",
        "## Governance Layering",
        "",
        "Phase 5 builds on Phase 2 isolation, Phase 3 session boundaries, and Phase 4 safety rollback readiness. Those layers must remain compatible before diff audit satisfaction is possible.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Runtime diff audit satisfied: `{summary['runtime_diff_audit_satisfied_count']}`",
        f"- Runtime diff audit blocked: `{summary['runtime_diff_audit_blocked_count']}`",
        f"- Runtime mutation detected: `{summary['runtime_mutation_detected_count']}`",
        f"- Runtime drift detected: `{summary['runtime_drift_detected_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Mutation Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in audit["runtime_mutation_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Drift Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in audit["runtime_drift_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Diff Status | Drift Status |", "| --- | --- | --- | --- | --- |"])
    for row in audit["runtime_diff_audit_contracts"]:
        lines.append(
            f"| `{row['runtime_diff_audit_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_diff_audit_status']}` | `{row['runtime_drift_status']}` |"
        )
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Runtime diff auditing is satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _diff_requests_from_safety(safety: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for record in safety.get("runtime_safety_rollback_contracts", []):
        snapshot = {
            "fixture_set_id": record.get("fixture_set_id"),
            "manifest_id": record.get("manifest_id"),
            "production_routing_authorized": False,
            "runtime_manifest_consumption_enabled": False,
            "runtime_state": "contract_audit_no_runtime_execution",
        }
        requests.append(
            {
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "runtime_pre_state_snapshot": snapshot,
                "runtime_post_state_snapshot": deepcopy(snapshot),
                "runtime_mutation_classification": "runtime_mutation_absent",
                "runtime_drift_classification": "runtime_drift_absent",
                "runtime_transition_trace": "runtime_transition_audited",
                "runtime_diff_visibility_state": "runtime_diff_visible",
                "runtime_auditability_state": "runtime_auditable",
                "runtime_rollback_audit_compatibility_state": "rollback_audit_compatible",
                "runtime_isolation_audit_compatibility_state": "isolation_audit_compatible",
                "runtime_session_audit_compatibility_state": "session_audit_compatible",
            }
        )
    return requests


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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_diff_auditing_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_DIFF_AUDITING_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_diff_auditing_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
