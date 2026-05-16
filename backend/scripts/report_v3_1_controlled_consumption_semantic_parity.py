"""Generate the v3.1 controlled consumption semantic parity report."""

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

from app.planner_adapters.v3_1.controlled_consumption_semantic_parity import build_controlled_consumption_semantic_parity  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_controlled_consumption_semantic_parity_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    parity = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_parity_snapshot_report.json")[
        "controlled_consumption_parity_snapshot"
    ]
    validation = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_output_validation_report.json")[
        "controlled_consumption_output_validation"
    ]
    baselines = _read_json(repo_root / "docs" / "generated" / "v3_1_planner_snapshot_baselines_report.json")[
        "planner_snapshot_baselines"
    ]
    semantic = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=parity,
        controlled_consumption_output_validation=validation,
        planner_snapshot_baselines=baselines,
    )
    repeated = build_controlled_consumption_semantic_parity(
        controlled_consumption_parity_snapshot=parity,
        controlled_consumption_output_validation=validation,
        planner_snapshot_baselines=baselines,
    )
    report = {
        "schema_version": "v3_1.controlled_consumption_semantic_parity_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_20_controlled_consumption_semantic_parity_audit",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "summary": {
            **semantic["summary"],
            "deterministic": semantic["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "controlled_consumption_semantic_parity": semantic,
        "deterministic_guarantees": {
            "passed": semantic["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": semantic["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_20_boundaries": [
            "semantic parity audit is test-only governance metadata",
            "semantic parity confirmation is not production approval",
            "semantic parity confirmation does not authorize production routing",
            "unavailable semantic fields remain visible",
            "runtime manifest consumption remains disabled",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_controlled_consumption_semantic_parity_report",
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
    semantic = report["controlled_consumption_semantic_parity"]
    summary = report["summary"]
    lines = [
        "# V3.1 Controlled Consumption Semantic Parity",
        "",
        "Phase 20 audits controlled-test output against available planner baseline semantics.",
        "Semantic parity is not production approval and does not authorize routing.",
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
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Semantic parity confirmed: `{summary['semantic_parity_confirmed_count']}`",
        f"- Semantic parity partial: `{summary['semantic_parity_partial_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Unavailable Semantic Fields",
        "",
        "| Field | Count |",
        "| --- | ---: |",
    ]
    for field, count in semantic["unavailable_semantic_field_counts"].items():
        lines.append(f"| `{field}` | `{count}` |")
    lines.extend(["", "## Mismatch Summary", "", "| Field | Count |", "| --- | ---: |"])
    for field, count in semantic["mismatched_semantic_field_counts"].items():
        lines.append(f"| `{field}` | `{count}` |")
    lines.extend(["", "## Blocker Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for reason, count in semantic["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Semantic Parity Records",
            "",
            "| Record | Manifest | Fixture Set | Baseline | Structural | Semantic |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in semantic["semantic_parity_records"]:
        lines.append(
            f"| `{row['semantic_parity_record_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['baseline_id'] or ''}` | `{row['structural_parity_status'] or ''}` | `{row['semantic_parity_status']}` |"
        )
    lines.extend(["", "## Phase 20 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_20_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Controlled consumption semantic parity is available for governance review, while production routing remains unchanged.",
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
    parser.add_argument("--output", default="docs/generated/v3_1_controlled_consumption_semantic_parity_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_CONTROLLED_CONSUMPTION_SEMANTIC_PARITY.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_controlled_consumption_semantic_parity_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
