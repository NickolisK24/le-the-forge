"""Generate the v3.1 limited experimental runtime dry-run report."""

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

from app.planner_adapters.v3_1.limited_experimental_runtime_dry_run import build_limited_experimental_runtime_dry_run  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_limited_experimental_runtime_dry_run_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    guards = _read_json(repo_root / "docs" / "generated" / "v3_1_limited_experimental_runtime_guards_report.json")[
        "limited_experimental_runtime_guards"
    ]
    readiness = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_promotion_readiness_report.json")[
        "controlled_consumption_promotion_readiness"
    ]
    manifests = _read_json(repo_root / "docs" / "generated" / "v3_1_admission_aware_manifest_serialization_report.json")[
        "admission_aware_manifest_serialization"
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
    dry_run = build_limited_experimental_runtime_dry_run(
        limited_experimental_runtime_guards=guards,
        controlled_consumption_promotion_readiness=readiness,
        admission_aware_manifest_serialization=manifests,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
    )
    repeated = build_limited_experimental_runtime_dry_run(
        limited_experimental_runtime_guards=guards,
        controlled_consumption_promotion_readiness=readiness,
        admission_aware_manifest_serialization=manifests,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
    )
    report = {
        "schema_version": "v3_1.limited_experimental_runtime_dry_run_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_26_limited_experimental_runtime_dry_run_adapter",
        "recommendation": "OBSERVATIONAL_ONLY_DRY_RUN_DO_NOT_ENABLE_RUNTIME_MANIFEST_CONSUMPTION",
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "production_routing_authorized": False,
        "production_default_routing_authorized": False,
        "summary": {
            **dry_run["summary"],
            "deterministic": dry_run["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "limited_experimental_runtime_dry_run": dry_run,
        "deterministic_guarantees": {
            "passed": dry_run["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": dry_run["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_26_boundaries": [
            "dry-run is explicit and non-mutating",
            "dry-run does not enable runtime manifest consumption",
            "dry-run does not authorize production routing",
            "manifests remain non-production-authoritative",
            "production planner routing remains unchanged",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_limited_experimental_runtime_dry_run_report",
            "observational_only": True,
            "dry_run_only": True,
            "non_mutating": True,
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
    dry_run = report["limited_experimental_runtime_dry_run"]
    summary = report["summary"]
    evidence = dry_run["evidence_summary"]
    lines = [
        "# V3.1 Limited Experimental Runtime Dry Run",
        "",
        "Phase 26 exercises the guarded manifest path in dry-run mode only.",
        "Dry-run is not production approval and does not enable runtime routing.",
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
        f"- Dry-run ready: `{summary['dry_run_ready_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Runtime manifest consumption enabled: `{str(summary['runtime_manifest_consumption_enabled']).lower()}`",
        f"- Production routing authorized: `{str(summary['production_routing_authorized']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Evidence Summary",
        "",
    ]
    for key, value in evidence.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Blocker Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for reason, count in dry_run["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Dry-Run Records",
            "",
            "| Record | Manifest | Fixture Set | Dry-Run Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in dry_run["limited_experimental_runtime_dry_run_records"]:
        lines.append(
            f"| `{row['limited_runtime_dry_run_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['dry_run_status']}` |"
        )
    lines.extend(["", "## Phase 26 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_26_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Limited experimental runtime dry-run evidence is available for governance review, while runtime consumption and production routing remain disabled.",
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
    parser.add_argument("--output", default="docs/generated/v3_1_limited_experimental_runtime_dry_run_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_LIMITED_EXPERIMENTAL_RUNTIME_DRY_RUN.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_limited_experimental_runtime_dry_run_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
