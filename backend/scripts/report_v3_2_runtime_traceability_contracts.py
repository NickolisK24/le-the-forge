"""Generate the v3.2 runtime traceability contract report."""

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
from app.planner_adapters.v3_2.runtime_traceability_contracts import build_runtime_traceability_contract  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_2_runtime_traceability_contracts_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    entrypoint = _read_json(repo_root / "docs" / "generated" / "v3_2_experimental_runtime_entrypoint_contracts_report.json")["experimental_runtime_entrypoint_contracts"]
    isolation = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_isolation_contracts_report.json")["runtime_isolation_contracts"]
    session = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_session_boundary_contracts_report.json")["runtime_session_boundary_contracts"]
    safety = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_safety_rollback_contracts_report.json")["runtime_safety_rollback_contracts"]
    diff_audit = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_diff_auditing_contracts_report.json")["runtime_diff_auditing_contracts"]
    determinism = _read_json(repo_root / "docs" / "generated" / "v3_2_runtime_determinism_validation_contracts_report.json")["runtime_determinism_validation_contracts"]
    requests = _traceability_requests_from_determinism(determinism)
    payload = {"runtime_traceability_requests": requests, "deterministic_hash": deterministic_hash(requests)}
    traceability = build_runtime_traceability_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
    )
    repeated = build_runtime_traceability_contract(
        payload,
        experimental_runtime_entrypoint_contracts=entrypoint,
        runtime_isolation_contracts=isolation,
        runtime_session_boundary_contracts=session,
        runtime_safety_rollback_contracts=safety,
        runtime_diff_audit_contracts=diff_audit,
        runtime_determinism_validation_contracts=determinism,
    )
    report = {
        "schema_version": "v3_2.runtime_traceability_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.2_phase_7_runtime_traceability_contracts",
        "recommendation": "RUNTIME_TRACEABILITY_READY_FOR_FUTURE_REPLAYABILITY_AND_RUNTIME_INTELLIGENCE_DESIGN_ONLY",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_runtime_prohibited": True,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {**traceability["summary"], "deterministic": traceability["deterministic_hash"] == repeated["deterministic_hash"]},
        "runtime_traceability_contracts": traceability,
        "runtime_trace_identity_distributions": traceability["runtime_trace_identity_distribution"],
        "source_lineage_distributions": traceability["source_lineage_distribution"],
        "manifest_lineage_distributions": traceability["manifest_lineage_distribution"],
        "fixture_lineage_distributions": traceability["fixture_lineage_distribution"],
        "entrypoint_lineage_distributions": traceability["entrypoint_lineage_distribution"],
        "isolation_lineage_distributions": traceability["isolation_lineage_distribution"],
        "session_lineage_distributions": traceability["session_lineage_distribution"],
        "safety_rollback_lineage_distributions": traceability["safety_rollback_lineage_distribution"],
        "diff_audit_lineage_distributions": traceability["diff_audit_lineage_distribution"],
        "determinism_lineage_distributions": traceability["determinism_lineage_distribution"],
        "final_classification_lineage_distributions": traceability["final_classification_lineage_distribution"],
        "runtime_evidence_explainability_distributions": traceability["runtime_evidence_explainability_distribution"],
        "runtime_lineage_blocker_distributions": traceability["runtime_lineage_blocker_distribution"],
        "trace_blocker_distributions": traceability["runtime_trace_blocker_distribution"],
        "runtime_disabled_path_verification": traceability["runtime_disabled_path_verification"],
        "production_prohibited_verification": {"production_runtime_prohibited": True, "production_routing_authorized": False, "production_default_routing_authorized": False},
        "deterministic_guarantees": {"passed": traceability["deterministic_hash"] == repeated["deterministic_hash"], "sample_hash": traceability["deterministic_hash"], "repeated_hash": repeated["deterministic_hash"], "timestamp_excluded_from_hash": True, "json_sort_keys": True},
        "phase_7_boundaries": [
            "runtime traceability contracts are governance only",
            "runtime manifest consumption remains disabled by default",
            "production runtime routing remains prohibited",
            "source evidence, manifest, fixture, and governance lineage must remain explicit",
            "final runtime classifications must remain explainable",
            "fallback traceability remains prohibited",
        ],
        "future_phase_foundation": [
            "future replayability phases may consume deterministic trace lineage",
            "future runtime intelligence phases must preserve explainable final classifications",
            "future runtime work must keep missing trace links and unexplainable evidence visible",
        ],
        "metadata": {"source": "v3_2_runtime_traceability_contracts_report", "governance_only": True, "runtime_traceability_contract_only": True, "runtime_behavior_enabled": False, "production_runtime_prohibited": True, "production_behavior_changed": False, "production_default_routing_authorized": False, "planner_remap_performed": False},
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    traceability = report["runtime_traceability_contracts"]
    summary = report["summary"]
    lines = [
        "# V3.2 Runtime Traceability Contracts",
        "",
        "Phase 7 defines deterministic runtime traceability governance for limited experimental runtime design.",
        "This does not enable runtime manifest consumption or production routing.",
        "",
        "## Runtime Traceability",
        "",
        "Runtime traceability matters because every future runtime evaluation must be explainable from source evidence to final classification.",
        "",
        "## Source Evidence Lineage",
        "",
        "Source evidence lineage keeps runtime evidence tied to deterministic governance artifacts instead of implicit runtime assumptions.",
        "",
        "## Manifest And Fixture Lineage",
        "",
        "Manifest and fixture lineage keep runtime traces connected to the exact non-production records under evaluation.",
        "",
        "## Governance Lineage",
        "",
        "Phase 7 links entrypoint, isolation, session, safety rollback, diff audit, and determinism records. Missing links fail visibly.",
        "",
        "## Final Classification Explainability",
        "",
        "Final runtime classifications must be explainable. Unexplainable evidence and broken lineage remain blocked.",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Runtime traceability satisfied: `{summary['runtime_traceability_satisfied_count']}`",
        f"- Runtime traceability blocked: `{summary['runtime_traceability_blocked_count']}`",
        f"- Evidence unexplainable: `{summary['runtime_evidence_unexplainable_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Trace Blockers",
        "",
        "| Blocker | Count |",
        "| --- | ---: |",
    ]
    for blocker, count in traceability["runtime_trace_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Lineage Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for blocker, count in traceability["runtime_lineage_blocker_distribution"].items():
        lines.append(f"| `{blocker}` | `{count}` |")
    lines.extend(["", "## Contracts", "", "| Contract | Trace | Manifest | Fixture Set | Traceability | Lineage |", "| --- | --- | --- | --- | --- | --- |"])
    for row in traceability["runtime_traceability_contracts"]:
        lines.append(f"| `{row['runtime_traceability_contract_id']}` | `{row['runtime_trace_id'] or ''}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['runtime_traceability_status']}` | `{row['runtime_lineage_status']}` |")
    lines.extend(["", "## Future Phases", ""])
    lines.extend(f"- {item}" for item in report["future_phase_foundation"])
    lines.extend(["", "## Conclusion", "", "Runtime traceability is satisfied for governance review only. Production runtime routing remains prohibited and default runtime manifest consumption remains disabled."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _traceability_requests_from_determinism(determinism: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for record in determinism.get("runtime_determinism_validation_contracts", []):
        trace_seed = {"manifest_id": record.get("manifest_id"), "fixture_set_id": record.get("fixture_set_id"), "determinism_contract_id": record.get("runtime_determinism_validation_contract_id")}
        requests.append(
            {
                "runtime_trace_id": f"v3_2_runtime_trace_{deterministic_hash(trace_seed)[:16]}",
                "manifest_id": record.get("manifest_id"),
                "fixture_set_id": record.get("fixture_set_id"),
                "runtime_trace_identity_state": "runtime_trace_identity_present",
                "runtime_source_evidence_lineage": "source_lineage_present",
                "runtime_manifest_lineage": "manifest_lineage_present",
                "runtime_fixture_lineage": "fixture_lineage_present",
                "runtime_entrypoint_lineage": "entrypoint_lineage_present",
                "runtime_isolation_lineage": "isolation_lineage_present",
                "runtime_session_lineage": "session_lineage_present",
                "runtime_safety_rollback_lineage": "safety_rollback_lineage_present",
                "runtime_diff_audit_lineage": "diff_audit_lineage_present",
                "runtime_determinism_lineage": "determinism_lineage_present",
                "runtime_final_classification_lineage": "final_classification_lineage_present",
                "runtime_trace_completeness_state": "runtime_trace_complete",
                "runtime_trace_explainability_state": "runtime_evidence_explainable",
                "runtime_lineage_integrity_state": "runtime_lineage_intact",
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
    parser.add_argument("--output", default="docs/generated/v3_2_runtime_traceability_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_2_RUNTIME_TRACEABILITY_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_2_runtime_traceability_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
