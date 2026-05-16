"""Generate the v3.1 experimental runtime readiness closeout report."""

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

from app.planner_adapters.v3_1.experimental_runtime_readiness_closeout import build_experimental_runtime_readiness_closeout  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_experimental_runtime_readiness_closeout_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    eligibility = _read_json(repo_root / "docs" / "generated" / "v3_1_manifest_consumption_eligibility_report.json")[
        "manifest_consumption_eligibility"
    ]
    consumption = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_test_consumption_report.json")[
        "controlled_test_consumption"
    ]
    validation = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_output_validation_report.json")[
        "controlled_consumption_output_validation"
    ]
    structural = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_parity_snapshot_report.json")[
        "controlled_consumption_parity_snapshot"
    ]
    semantic = _read_json(repo_root / "docs" / "generated" / "v3_1_trace_backfilled_semantic_parity_report.json")[
        "trace_backfilled_semantic_parity"
    ]
    promotion = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_promotion_readiness_report.json")[
        "controlled_consumption_promotion_readiness"
    ]
    guards = _read_json(repo_root / "docs" / "generated" / "v3_1_limited_experimental_runtime_guards_report.json")[
        "limited_experimental_runtime_guards"
    ]
    dry_run = _read_json(repo_root / "docs" / "generated" / "v3_1_limited_experimental_runtime_dry_run_report.json")[
        "limited_experimental_runtime_dry_run"
    ]
    stability = _read_json(repo_root / "docs" / "generated" / "v3_1_dry_run_result_stability_report.json")[
        "dry_run_result_stability"
    ]
    closeout = build_experimental_runtime_readiness_closeout(
        manifest_consumption_eligibility=eligibility,
        controlled_test_consumption=consumption,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
        controlled_consumption_promotion_readiness=promotion,
        limited_experimental_runtime_guards=guards,
        limited_experimental_runtime_dry_run=dry_run,
        dry_run_result_stability=stability,
    )
    repeated = build_experimental_runtime_readiness_closeout(
        manifest_consumption_eligibility=eligibility,
        controlled_test_consumption=consumption,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
        controlled_consumption_promotion_readiness=promotion,
        limited_experimental_runtime_guards=guards,
        limited_experimental_runtime_dry_run=dry_run,
        dry_run_result_stability=stability,
    )
    report = {
        "schema_version": "v3_1.experimental_runtime_readiness_closeout_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_28_experimental_runtime_readiness_closeout_audit",
        "recommendation": "READY_FOR_FUTURE_LIMITED_EXPERIMENTAL_RUNTIME_PHASE_REVIEW_ONLY",
        "recommended_next_phase": "future limited experimental runtime planning, still gated and not production-authorized",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {
            **closeout["summary"],
            "deterministic": closeout["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "experimental_runtime_readiness_closeout": closeout,
        "deterministic_guarantees": {
            "passed": closeout["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": closeout["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_28_boundaries": [
            "closeout is audit/reporting only",
            "closeout does not enable runtime manifest consumption",
            "closeout does not authorize production routing",
            "manifests remain non-production-authoritative",
            "production planner routing remains unchanged",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_experimental_runtime_readiness_closeout_report",
            "observational_only": True,
            "audit_reporting_only": True,
            "runtime_behavior_enabled": False,
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
    closeout = report["experimental_runtime_readiness_closeout"]
    summary = report["summary"]
    evidence = closeout["evidence_chain_summary"]
    lines = [
        "# V3.1 Experimental Runtime Readiness Closeout",
        "",
        "Phase 28 summarizes the v3.1 controlled-consumption evidence chain for future limited experimental runtime consideration.",
        "Closeout readiness is not runtime approval and does not authorize production routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Recommended next phase: {report['recommended_next_phase']}",
        f"- Runtime manifest consumption enabled: `{str(report['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(report['production_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Ready: `{summary['ready_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Evidence Chain Summary",
        "",
    ]
    for key, value in evidence.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Unresolved Blockers", "", "| Blocker | Count |", "| --- | ---: |"])
    for reason, count in closeout["unresolved_blocker_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Closeout Records",
            "",
            "| Record | Manifest | Fixture Set | Closeout Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in closeout["closeout_records"]:
        lines.append(
            f"| `{row['experimental_runtime_readiness_closeout_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['closeout_readiness_status']}` |"
        )
    lines.extend(["", "## Phase 28 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_28_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "The controlled-consumption evidence chain is summarized for governance review only. Runtime consumption and production routing remain disabled.",
        ]
    )
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
    parser.add_argument("--output", default="docs/generated/v3_1_experimental_runtime_readiness_closeout_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_EXPERIMENTAL_RUNTIME_READINESS_CLOSEOUT.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_experimental_runtime_readiness_closeout_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
