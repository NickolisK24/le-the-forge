"""Generate the v3.2 experimental runtime closeout and v3.3 readiness report."""

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

from app.planner_adapters.v3_2.experimental_runtime_closeout_readiness_audit import (  # noqa: E402
    build_experimental_runtime_closeout_readiness_audit,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_experimental_runtime_closeout_readiness_audit_report() -> dict[str, Any]:
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
    kill_switch = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_kill_switch_contracts_report.json")["runtime_kill_switch_contracts"]
    context = {
        "unresolved_blockers": [],
        "unresolved_risks": [],
        "unresolved_limitations": [
            "v3.3 readiness is planning-only",
            "production runtime routing remains out of scope",
            "default runtime manifest consumption remains disabled",
            "production-authoritative manifest treatment remains prohibited",
        ],
    }
    closeout = build_experimental_runtime_closeout_readiness_audit(
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
        runtime_kill_switch_contracts=kill_switch,
        closeout_context=context,
    )
    repeated = build_experimental_runtime_closeout_readiness_audit(
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
        runtime_kill_switch_contracts=kill_switch,
        closeout_context=context,
    )
    report = {
        "schema_version": "v3_2.experimental_runtime_closeout_readiness_audit_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_12_experimental_runtime_closeout_readiness_audit",
        "recommendation": "V3_2_CLOSEOUT_SATISFIED_V3_3_READY_FOR_PLANNING_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "production_authoritative_manifest_treatment": False,
        "summary": {**closeout["summary"], "deterministic": closeout["deterministic_hash"] == repeated["deterministic_hash"]},
        "experimental_runtime_closeout_readiness_audit": closeout,
        "phase_coverage_distributions": closeout["phase_coverage_distribution"],
        "contract_compatibility_distributions": closeout["contract_compatibility_distribution"],
        "entrypoint_readiness_summary": closeout["entrypoint_readiness_summary"],
        "isolation_readiness_summary": closeout["isolation_readiness_summary"],
        "session_boundary_readiness_summary": closeout["session_boundary_readiness_summary"],
        "safety_rollback_readiness_summary": closeout["safety_rollback_readiness_summary"],
        "diff_audit_readiness_summary": closeout["diff_audit_readiness_summary"],
        "determinism_readiness_summary": closeout["determinism_readiness_summary"],
        "traceability_readiness_summary": closeout["traceability_readiness_summary"],
        "replayability_readiness_summary": closeout["replayability_readiness_summary"],
        "drift_detection_readiness_summary": closeout["drift_detection_readiness_summary"],
        "limited_experiment_readiness_summary": closeout["limited_experiment_readiness_summary"],
        "kill_switch_readiness_summary": closeout["kill_switch_readiness_summary"],
        "production_routing_prohibition_verification": closeout["production_routing_prohibition_verification"],
        "default_manifest_consumption_disabled_verification": closeout["default_manifest_consumption_disabled_verification"],
        "production_authoritative_manifest_prohibited_verification": closeout["production_authoritative_manifest_prohibited_verification"],
        "unresolved_blocker_summary": closeout["unresolved_blocker_summary"],
        "unresolved_risk_summary": closeout["unresolved_risk_summary"],
        "unresolved_limitation_summary": closeout["unresolved_limitation_summary"],
        "v3_3_readiness_classification": closeout["v3_3_readiness_status_counts"],
        "deterministic_guarantees": {"passed": closeout["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": closeout["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_12_boundaries": [
            "closeout is audit-only",
            "v3.3 readiness is planning-only",
            "production runtime routing remains prohibited",
            "default runtime manifest consumption remains disabled",
            "production-authoritative manifest treatment remains prohibited",
            "no new runtime behavior, runtime consumption behavior, or planner behavior is added",
        ],
        "v3_3_allowed_foundation": [
            "v3.3 may build on deterministic Phase 1 through Phase 11 governance evidence",
            "v3.3 may define future explicit non-production governance phases",
            "v3.3 must preserve production routing prohibition unless future governance explicitly defines a separate non-production step",
        ],
        "v3_3_forbidden_without_future_governance": [
            "production runtime routing",
            "default runtime manifest consumption",
            "production-authoritative manifest treatment",
            "implicit runtime activation",
            "new planner behavior without explicit governance",
        ],
        "metadata": {"source": "v3_2_experimental_runtime_closeout_readiness_audit_report", "governance_only": True, "closeout_readiness_audit_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_authoritative_manifest_treatment_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    closeout = report["experimental_runtime_closeout_readiness_audit"]
    summary = report["summary"]
    lines = [
        "# V3.2 Experimental Runtime Closeout and V3.3 Readiness",
        "",
        "Phase 12 closes out v3.2 by auditing the limited experimental runtime governance chain from Phase 1 through Phase 11.",
        "This is a closeout and readiness audit only.",
        "",
        "## What V3.2 Accomplished",
        "",
        "V3.2 established deterministic entrypoint, isolation, session boundary, safety rollback, diff audit, determinism, traceability, replayability, drift detection, limited experiment, and kill-switch governance evidence.",
        "",
        "## What V3.2 Did Not Enable",
        "",
        "V3.2 did not enable production runtime routing, default runtime manifest consumption, production-authoritative manifest treatment, new runtime behavior, new runtime consumption behavior, or new planner behavior.",
        "",
        "## Phase Chain",
        "",
        "Phases 1 through 11 form a compatibility chain. Phase 12 verifies coverage, contract compatibility, blocker visibility, limitation visibility, and planning-only v3.3 readiness.",
        "",
        "## Production Boundaries",
        "",
        "Production runtime remains prohibited. Default runtime manifest consumption remains disabled. Production-authoritative manifest treatment remains prohibited.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- V3.2 closeout satisfied: `{summary['v3_2_closeout_satisfied_count']}`",
        f"- V3.2 closeout blocked: `{summary['v3_2_closeout_blocked_count']}`",
        f"- V3.3 ready for planning: `{summary['v3_3_ready_for_planning_count']}`",
        f"- V3.3 blocked: `{summary['v3_3_blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Production-authoritative manifest treatment: `{str(summary['production_authoritative_manifest_treatment']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Unresolved Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in closeout["unresolved_blocker_summary"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Unresolved Risks", "", "| Risk | Count |", "| --- | ---: |"])
    for risk, count in closeout["unresolved_risk_summary"].items():
        lines.append(f"| `{risk}` | `{count}` |")
    lines.extend(["", "## Unresolved Limitations", "", "| Limitation | Count |", "| --- | ---: |"])
    for limitation, count in closeout["unresolved_limitation_summary"].items():
        lines.append(f"| `{limitation}` | `{count}` |")
    lines.extend(["", "## V3.3 May Build On", ""])
    lines.extend(f"- {item}" for item in report["v3_3_allowed_foundation"])
    lines.extend(["", "## V3.3 Must Not Enable Without Future Governance", ""])
    lines.extend(f"- {item}" for item in report["v3_3_forbidden_without_future_governance"])
    lines.extend(["", "## Final Classification", ""])
    for row in closeout["experimental_runtime_closeout_readiness_audits"]:
        lines.append(f"- `{row['manifest_id']}` / `{row['fixture_set_id']}`: `{row['v3_2_closeout_status']}`, `{row['v3_3_readiness_status']}`")
    lines.extend(["", "V3.3 readiness is planning-only and does not imply production enablement."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    parser.add_argument("--output", default="docs/generated/v3_2_experimental_runtime_closeout_readiness_audit_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_EXPERIMENTAL_RUNTIME_CLOSEOUT_AND_V3_3_READINESS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_experimental_runtime_closeout_readiness_audit_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
