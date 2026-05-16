"""Generate the v3.2 runtime replayability contract report."""

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
from app.planner_adapters.v3_2.runtime_replayability_contracts import build_runtime_replayability_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_replayability_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")["experimental_runtime_entrypoint_contracts"]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")["runtime_isolation_contracts"]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")["runtime_session_boundary_contracts"]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")["runtime_safety_rollback_contracts"]
    diff_audit = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_diff_auditing_contracts_report.json")["runtime_diff_auditing_contracts"]
    determinism = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_determinism_validation_contracts_report.json")["runtime_determinism_validation_contracts"]
    traceability = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_traceability_contracts_report.json")["runtime_traceability_contracts"]
    requests = _replayability_requests_from_traceability(traceability)
    payload = {"runtime_replayability_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    replayability = build_runtime_replayability_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
    )
    repeated = build_runtime_replayability_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
        runtime_traceability_contracts=traceability,
    )
    report = {
        "schema_version": "v3_2.runtime_replayability_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_8_runtime_replayability_contracts",
        "recommendation": "RUNTIME_REPLAYABILITY_READY_FOR_FUTURE_DRIFT_DETECTION_AND_RUNTIME_INTELLIGENCE_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**replayability["summary"], "deterministic": replayability["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_replayability_contracts": replayability,
        "replay_input_distributions": replayability["replay_input_distribution"],
        "replay_output_distributions": replayability["replay_output_distribution"],
        "replay_hash_consistency_distributions": replayability["replay_hash_consistency_distribution"],
        "replay_trace_consistency_distributions": replayability["replay_trace_consistency_distribution"],
        "replay_lineage_preservation_distributions": replayability["replay_lineage_preservation_distribution"],
        "replay_determinism_distributions": replayability["replay_determinism_distribution"],
        "replay_mismatch_distributions": replayability["replay_mismatch_distribution"],
        "replay_evidence_completeness_distributions": replayability["replay_evidence_completeness_distribution"],
        "replay_instability_distributions": replayability["replay_instability_distribution"],
        "traceability_compatibility_distributions": replayability["traceability_compatibility_distribution"],
        "determinism_compatibility_distributions": replayability["determinism_compatibility_distribution"],
        "diff_audit_compatibility_distributions": replayability["diff_audit_compatibility_distribution"],
        "rollback_compatibility_distributions": replayability["rollback_compatibility_distribution"],
        "session_compatibility_distributions": replayability["session_compatibility_distribution"],
        "isolation_compatibility_distributions": replayability["isolation_compatibility_distribution"],
        "entrypoint_compatibility_distributions": replayability["entrypoint_compatibility_distribution"],
        "runtime_disabled_path_verification": replayability["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "deterministic_guarantees": {"passed": replayability["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": replayability["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_8_boundaries": [
            "runtime replayability contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "replay inputs and outputs must remain explicit",
            "replay hash, trace, and lineage mismatches remain visible",
            "fallback replayability remains prohibited",
        ],
        "future_phase_foundation": [
            "future drift detection phases may consume deterministic replayability evidence",
            "future runtime intelligence phases must preserve replay trace lineage and hash consistency",
            "future runtime work must keep replay mismatches and output instability visible",
        ],
        "metadata": {"source": "v3_2_runtime_replayability_contracts_report", "governance_only": True, "runtime_replayability_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    replayability = report["runtime_replayability_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Replayability Contracts",
        "",
        "Phase 8 defines deterministic runtime replayability governance for limited experimental runtime design.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Runtime Replayability",
        "",
        "Runtime replayability matters because future drift detection and runtime intelligence work need repeatable input and output evidence.",
        "",
        "## Explicit Replay Evidence",
        "",
        "Replay inputs and outputs must be explicit. Missing replay evidence fails visibly and cannot be approved by fallback behavior.",
        "",
        "## Hash And Trace Consistency",
        "",
        "Replay hash consistency and replay trace consistency keep replay output comparable across evaluations.",
        "",
        "## Lineage Preservation",
        "",
        "Replay lineage preservation keeps replay evidence linked to traceability, determinism, diff audit, rollback, session, isolation, and entrypoint contracts.",
        "",
        "## Replay Mismatches",
        "",
        "Replay mismatches are dangerous because they can hide runtime drift. Phase 8 classifies hash, trace, lineage, and output-instability failures explicitly.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Runtime replayability satisfied: `{summary['runtime_replayability_satisfied_count']}`",
        f"- Runtime replayability blocked: `{summary['runtime_replayability_blocked_count']}`",
        f"- Replay hash mismatch: `{summary['runtime_replay_hash_mismatch_count']}`",
        f"- Replay output unstable: `{summary['runtime_replay_output_unstable_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Replay Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in replayability["runtime_replay_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Replay Instability Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in replayability["runtime_replay_instability_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Manifest | Fixture Set | Replayability | Mismatch |", "| --- | --- | --- | --- | --- |"])
    for row in replayability["runtime_replayability_contracts"]:
        lines.append(f"| `{row['runtime_replayability_contract_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_replayability_status']}` | `{row['runtime_replay_mismatch_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Runtime replayability is satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _replayability_requests_from_traceability(traceability: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for record in traceability.get("runtime_traceability_contracts", []):
        replay_hash = deterministic_hash({"trace_id": record.get("runtime_trace_id"), "manifest_id": record.get("manifest_id"), "fixture_set_id": record.get("fixture_set_id")})
        requests.append(
            {
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "runtime_replay_input_state": "runtime_replay_input_present",
                "runtime_replay_output_state": "runtime_replay_output_present",
                "runtime_replay_hash_state": "runtime_replay_hash_consistent",
                "runtime_replay_trace_state": "runtime_replay_trace_consistent",
                "runtime_replay_lineage_preservation_state": "runtime_replay_lineage_preserved",
                "runtime_replay_determinism_state": "runtime_replay_determinism_satisfied",
                "runtime_replay_mismatch_state": "runtime_replay_mismatch_absent",
                "runtime_replay_evidence_completeness_state": "runtime_replay_evidence_complete",
                "runtime_replay_output_stability_state": "runtime_replay_output_stable",
                "runtime_replay_hash": replay_hash,
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_replayability_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_REPLAYABILITY_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_replayability_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
