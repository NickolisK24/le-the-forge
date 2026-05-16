"""Generate the v3.1 baseline trace expectation backfill report."""

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

from app.planner_adapters.v3_1.baseline_trace_expectation_backfill import build_baseline_trace_expectation_backfill  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_baseline_trace_expectation_backfill_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    expectations = _read_json(repo_root / "docs" / "generated" / "v3_1_baseline_semantic_expectations_report.json")[
        "baseline_semantic_expectations"
    ]
    parity = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_parity_snapshot_report.json")[
        "controlled_consumption_parity_snapshot"
    ]
    validation = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_output_validation_report.json")[
        "controlled_consumption_output_validation"
    ]
    manifests = _read_json(repo_root / "docs" / "generated" / "v3_1_admission_aware_manifest_serialization_report.json")[
        "admission_aware_manifest_serialization"
    ]
    backfill = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=expectations,
        controlled_consumption_parity_snapshot=parity,
        controlled_consumption_output_validation=validation,
        admission_aware_manifest_serialization=manifests,
    )
    repeated = build_baseline_trace_expectation_backfill(
        baseline_semantic_expectations=expectations,
        controlled_consumption_parity_snapshot=parity,
        controlled_consumption_output_validation=validation,
        admission_aware_manifest_serialization=manifests,
    )
    report = {
        "schema_version": "v3_1.baseline_trace_expectation_backfill_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_22_baseline_trace_expectation_backfill",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "summary": {
            **backfill["summary"],
            "deterministic": backfill["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "baseline_trace_expectation_backfill": backfill,
        "deterministic_guarantees": {
            "passed": backfill["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": backfill["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_22_boundaries": [
            "trace expectation backfill is test-only governance metadata",
            "backfilled expectations are not production approval",
            "backfilled expectations do not authorize production routing",
            "trace fields are sourced only from deterministic governance artifacts",
            "runtime manifest consumption remains disabled",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_baseline_trace_expectation_backfill_report",
            "observational_only": True,
            "controlled_test_only": True,
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
    backfill = report["baseline_trace_expectation_backfill"]
    summary = report["summary"]
    lines = [
        "# V3.1 Baseline Trace Expectation Backfill",
        "",
        "Phase 22 backfills deterministic manifest and fixture trace expectations from existing governance artifacts.",
        "Backfilled expectations are not production approval and do not authorize routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        f"- Runtime production consumption enabled: `{str(report['runtime_production_consumption_enabled']).lower()}`",
        f"- Runtime manifest consumption enabled: `{str(report['runtime_manifest_consumption_enabled']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Baseline expectation records evaluated: `{summary['baseline_expectation_records_evaluated']}`",
        f"- Backfilled: `{summary['backfilled_count']}`",
        f"- Partial: `{summary['partial_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Remaining Unavailable Fields",
        "",
        "| Field | Count |",
        "| --- | ---: |",
    ]
    for field, count in backfill["remaining_unavailable_field_counts"].items():
        lines.append(f"| `{field}` | `{count}` |")
    lines.extend(["", "## Trace Conflicts", "", "| Conflict | Count |", "| --- | ---: |"])
    for conflict, count in backfill["trace_conflict_counts"].items():
        lines.append(f"| `{conflict}` | `{count}` |")
    lines.extend(["", "## Blocker Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for reason, count in backfill["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Backfill Records",
            "",
            "| Record | Baseline | Manifest | Fixture Set | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in backfill["baseline_trace_backfill_records"]:
        lines.append(
            f"| `{row['baseline_trace_backfill_id']}` | `{row['baseline_id'] or ''}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['trace_backfill_status']}` |"
        )
    lines.extend(["", "## Phase 22 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_22_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Baseline trace expectation backfill is available for governance review, while production routing remains unchanged.",
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
    parser.add_argument("--output", default="docs/generated/v3_1_baseline_trace_expectation_backfill_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_BASELINE_TRACE_EXPECTATION_BACKFILL.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_baseline_trace_expectation_backfill_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
