"""Generate the v3.1 planner snapshot baseline report."""

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

from app.planner_adapters.v3_1.planner_snapshot_baselines import (  # noqa: E402
    V31PlannerSnapshotBaselines,
    build_sample_planner_snapshot_baseline_inputs,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_planner_snapshot_baselines_report() -> dict[str, Any]:
    dual_run = build_sample_planner_snapshot_baseline_inputs()
    baselines = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)
    repeated = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)
    deterministic = baselines["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.planner_snapshot_baselines_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_3_planner_snapshot_baseline_infrastructure",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **baselines["summary"],
            "deterministic": deterministic,
        },
        "planner_snapshot_baselines": baselines,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": baselines["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
            "stable_generation_token": baselines["metadata"]["stable_generation_token"],
        },
        "phase_3_boundaries": [
            "snapshots are observational migration-readiness artifacts",
            "trusted infrastructure is still not production default",
            "baselines support parity, drift, and regression evaluation only",
            "unsupported and blocked states remain intentionally visible",
            "planner ownership remains legacy-controlled",
        ],
        "metadata": {
            "source": "v3_1_planner_snapshot_baselines_report",
            "observational_only": True,
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
    summary = report["summary"]
    lines = [
        "# V3.1 Planner Snapshot Baselines",
        "",
        "Phase 3 introduces deterministic planner-adjacent snapshot baseline infrastructure.",
        "Snapshots are observational migration-readiness artifacts; production output remains legacy-owned.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total snapshots: `{summary['total_snapshots']}`",
        f"- Baseline candidates: `{summary['baseline_candidate_count']}`",
        f"- Comparison ready: `{summary['comparison_ready_count']}`",
        f"- Unsupported: `{summary['unsupported_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Insufficient data: `{summary['insufficient_data_count']}`",
        f"- Legacy only: `{summary['legacy_only_count']}`",
        f"- Shadow only: `{summary['shadow_only_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Snapshot Results",
        "",
        "| Snapshot | Key | Drift | Baseline Readiness | Eligible |",
        "| --- | --- | --- | --- | --- |",
    ]
    for snapshot in report["planner_snapshot_baselines"]["snapshots"]:
        drift = snapshot["dual_run_comparison_state"]["drift_classification"]
        lines.append(
            f"| `{snapshot['snapshot_id']}` | `{snapshot['stable_key']}` | `{drift}` | `{snapshot['baseline_readiness']}` | `{str(snapshot['comparison_eligible']).lower()}` |"
        )
    lines.extend(["", "## Phase 3 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_3_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Planner snapshot baselines are available for migration readiness review, but planner ownership and production routing remain unchanged.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            normalized[key] = DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_planner_snapshot_baselines_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_PLANNER_SNAPSHOT_BASELINES.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_planner_snapshot_baselines_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
