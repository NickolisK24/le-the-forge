"""Generate the v3.1 dry-run result stability audit report."""

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

from app.planner_adapters.v3_1.dry_run_result_stability import audit_dry_run_result_stability  # noqa: E402
from scripts.report_v3_1_limited_experimental_runtime_dry_run import build_v3_1_limited_experimental_runtime_dry_run_report  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_dry_run_result_stability_report() -> dict[str, Any]:
    first_report = build_v3_1_limited_experimental_runtime_dry_run_report()
    second_report = build_v3_1_limited_experimental_runtime_dry_run_report()
    first_snapshot = first_report["limited_experimental_runtime_dry_run"]
    second_snapshot = second_report["limited_experimental_runtime_dry_run"]
    stability = audit_dry_run_result_stability([first_snapshot, second_snapshot])
    report = {
        "schema_version": "v3_1.dry_run_result_stability_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_27_dry_run_result_stability_audit",
        "recommendation": "OBSERVATIONAL_ONLY_STABILITY_AUDIT_DO_NOT_ENABLE_RUNTIME_MANIFEST_CONSUMPTION",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": stability["summary"],
        "dry_run_result_stability": stability,
        "deterministic_guarantees": {
            "passed": first_snapshot["deterministic_hash"] == second_snapshot["deterministic_hash"],
            "sample_hash": first_snapshot["deterministic_hash"],
            "repeated_hash": second_snapshot["deterministic_hash"],
            "stability_hash": stability["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_27_boundaries": [
            "stability audit compares repeated dry-run snapshots only",
            "stability audit does not enable runtime manifest consumption",
            "stability audit does not authorize production routing",
            "manifests remain non-production-authoritative",
            "production planner routing remains unchanged",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_dry_run_result_stability_report",
            "observational_only": True,
            "dry_run_governance_only": True,
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
    stability = report["dry_run_result_stability"]
    summary = report["summary"]
    compared = stability["compared_snapshot_summary"]
    lines = [
        "# V3.1 Dry-Run Result Stability",
        "",
        "Phase 27 verifies repeated limited experimental runtime dry-run results are deterministic.",
        "Dry-run stability is not production approval and does not enable runtime routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Runtime manifest consumption enabled: `{str(report['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(report['production_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Stable: `{summary['stable_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Compared Snapshot Summary",
        "",
        f"- Compared snapshot count: `{compared['compared_snapshot_count']}`",
        f"- Snapshot count sufficient: `{str(compared['snapshot_count_sufficient']).lower()}`",
        f"- Records per snapshot: `{compared['records_per_snapshot']}`",
        "",
        "## Drift Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in stability["drift_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Stability Records",
            "",
            "| Record | Manifest | Fixture Set | Compared Snapshots | Stability Status | Drift Fields |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in stability["dry_run_result_stability_records"]:
        lines.append(
            f"| `{row['dry_run_stability_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['compared_snapshot_count']}` | `{row['stability_status']}` | `{', '.join(row['drift_fields'])}` |"
        )
    lines.extend(["", "## Phase 27 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_27_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Dry-run stability evidence is available for governance review, while runtime consumption and production routing remain disabled.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_dry_run_result_stability_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_DRY_RUN_RESULT_STABILITY.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_dry_run_result_stability_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
