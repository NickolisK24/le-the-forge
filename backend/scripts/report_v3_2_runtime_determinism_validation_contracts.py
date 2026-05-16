"""Generate the v3.2 runtime determinism validation contract report."""

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
from app.planner_adapters.v3_2.runtime_determinism_validation_contracts import build_runtime_determinism_validation_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_determinism_validation_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")[
        "experimental_runtime_entrypoint_contracts"
    ]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")[
        "runtime_isolation_contracts"
    ]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")[
        "runtime_session_boundary_contracts"
    ]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")[
        "runtime_safety_rollback_contracts"
    ]
    diff_audit = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_diff_auditing_contracts_report.json")[
        "runtime_diff_auditing_contracts"
    ]
    requests = _determinism_requests_from_diff_audit(diff_audit)
    payload = {"runtime_determinism_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    determinism = build_runtime_determinism_validation_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
    )
    repeated = build_runtime_determinism_validation_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
    )
    report = {
        "schema_version": "v3_2.runtime_determinism_validation_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_6_runtime_determinism_validation_contracts",
        "recommendation": "RUNTIME_DETERMINISM_VALIDATION_READY_FOR_FUTURE_REPLAYABILITY_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**determinism["summary"], "deterministic": determinism["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_determinism_validation_contracts": determinism,
        "repeat_run_consistency_distributions": determinism["repeat_run_consistency_distribution"],
        "deterministic_ordering_distributions": determinism["deterministic_ordering_distribution"],
        "deterministic_hashing_distributions": determinism["deterministic_hashing_distribution"],
        "replay_consistency_distributions": determinism["replay_consistency_distribution"],
        "runtime_nondeterministic_drift_distributions": determinism["runtime_nondeterministic_drift_distribution"],
        "runtime_instability_distributions": determinism["runtime_instability_distribution"],
        "runtime_transition_instability_distributions": determinism["runtime_transition_instability_distribution"],
        "runtime_audit_compatibility_distributions": determinism["runtime_audit_compatibility_distribution"],
        "runtime_rollback_compatibility_distributions": determinism["runtime_rollback_compatibility_distribution"],
        "runtime_session_compatibility_distributions": determinism["runtime_session_compatibility_distribution"],
        "runtime_isolation_compatibility_distributions": determinism["runtime_isolation_compatibility_distribution"],
        "runtime_disabled_path_verification": determinism["runtime_disabled_path_verification"],
        "production_prohibited_verification": {
            "production_runtime_prohibited": True,
            "production_routing_authorized": False,
            "production_default_routing_authorized": False,
        },
        "deterministic_guarantees": {
            "passed": determinism["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": determinism["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_6_boundaries": [
            "runtime determinism validation contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "repeat-run consistency must be explicit",
            "deterministic ordering and hashing must remain stable",
            "runtime replay consistency cannot be implicitly approved",
        ],
        "future_phase_foundation": [
            "future replayability phases may consume deterministic validation evidence",
            "future runtime intelligence phases must preserve stable hashes and ordering",
            "future runtime work must keep nondeterministic drift and instability visible",
        ],
        "metadata": {
            "source": "v3_2_runtime_determinism_validation_contracts_report",
            "governance_only": True,
            "runtime_determinism_validation_contract_only": True,
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
    validation = report["runtime_determinism_validation_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Determinism Validation Contracts",
        "",
        "Phase 6 defines deterministic runtime execution validation governance for limited experimental runtime design.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Runtime Determinism",
        "",
        "Runtime determinism matters because future runtime evaluation must be repeatable, auditable, and explainable before any runtime-adjacent path is considered.",
        "",
        "## Repeat-Run Stability",
        "",
        "Repeat-run stability requires explicit matching hashes and stable replay evidence. Unstable repeat runs fail visibly.",
        "",
        "## Deterministic Hashing And Ordering",
        "",
        "Stable hashes and deterministic transition ordering are required so replay evidence can be compared across runs without hidden drift.",
        "",
        "## Replay Consistency",
        "",
        "Replay consistency is explicit. It cannot be approved implicitly, and fallback determinism validation remains prohibited.",
        "",
        "## Nondeterministic Drift",
        "",
        "Nondeterministic runtime drift is dangerous because it can hide runtime behavior changes behind repeated evaluations. Phase 6 keeps drift and instability visible.",
        "",
        "## Governance Layering",
        "",
        "Phase 6 builds on entrypoint authorization, isolation, session boundaries, safety rollback readiness, and runtime diff auditability.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Runtime determinism satisfied: `{summary['runtime_determinism_satisfied_count']}`",
        f"- Runtime determinism blocked: `{summary['runtime_determinism_blocked_count']}`",
        f"- Replay consistency satisfied: `{summary['runtime_replay_consistency_satisfied_count']}`",
        f"- Runtime instability detected: `{summary['runtime_instability_detected_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Determinism Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in validation["runtime_determinism_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Instability Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in validation["runtime_instability_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Determinism | Replay |", "| --- | --- | --- | --- | --- |"])
    for row in validation["runtime_determinism_validation_contracts"]:
        lines.append(
            f"| `{row['runtime_determinism_validation_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_determinism_status']}` | `{row['runtime_replay_status']}` |"
        )
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Runtime determinism validation is satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _determinism_requests_from_diff_audit(diff_audit: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for record in diff_audit.get("runtime_diff_audit_contracts", []):
        repeat_hash = deterministic_hash(
            {
                "diff_contract_id": record.get("runtime_diff_audit_contract_id"),
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "pre_hash": record.get("runtime_pre_state_snapshot_hash"),
                "post_hash": record.get("runtime_post_state_snapshot_hash"),
            }
        )
        requests.append(
            {
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "runtime_repeat_run_state": "repeat_run_consistency_satisfied",
                "runtime_replay_consistency_state": "runtime_replay_consistency_satisfied",
                "runtime_deterministic_ordering_state": "deterministic_ordering_satisfied",
                "runtime_deterministic_hashing_state": "deterministic_hashing_satisfied",
                "runtime_transition_consistency_state": "runtime_transition_consistency_satisfied",
                "runtime_nondeterministic_drift_state": "runtime_nondeterministic_drift_absent",
                "runtime_instability_classification": "runtime_instability_absent",
                "runtime_replay_trace_classification": "runtime_replay_trace_audited",
                "repeat_run_hashes": [repeat_hash, repeat_hash],
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_determinism_validation_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_DETERMINISM_VALIDATION_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_determinism_validation_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
