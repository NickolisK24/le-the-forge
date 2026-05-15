"""Generate the v3.1 baseline fixture approval workflow report."""

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

from app.planner_adapters.v3_1.baseline_fixture_workflows import (  # noqa: E402
    V31BaselineFixtureWorkflows,
    build_sample_baseline_fixture_workflow_inputs,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_baseline_fixture_workflows_report() -> dict[str, Any]:
    snapshots = build_sample_baseline_fixture_workflow_inputs()
    workflows = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)
    repeated = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)
    deterministic = workflows["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.baseline_fixture_workflows_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_4_baseline_fixture_approval_workflows",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **workflows["summary"],
            "deterministic": deterministic,
        },
        "baseline_fixture_workflows": workflows,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": workflows["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
            "stable_workflow_generation_token": workflows["metadata"]["stable_workflow_generation_token"],
        },
        "phase_4_boundaries": [
            "workflows are observational governance infrastructure only",
            "trusted infrastructure is still not production default",
            "production planner ownership remains legacy-controlled",
            "approval workflows are migration-readiness tooling",
            "unsupported and blocked states remain intentionally visible",
            "approval status does not imply production routing approval",
        ],
        "metadata": {
            "source": "v3_1_baseline_fixture_workflows_report",
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
        "# V3.1 Baseline Fixture Workflows",
        "",
        "Phase 4 introduces deterministic baseline fixture approval workflow infrastructure.",
        "Approval status is migration-readiness governance only and does not authorize production routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total fixtures: `{summary['total_fixtures']}`",
        f"- Pending review: `{summary['pending_review_count']}`",
        f"- Approved candidate: `{summary['approved_candidate_count']}`",
        f"- Approved baseline: `{summary['approved_baseline_count']}`",
        f"- Rejected: `{summary['rejected_count']}`",
        f"- Unsupported: `{summary['unsupported_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Insufficient data: `{summary['insufficient_data_count']}`",
        f"- Archived: `{summary['archived_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Fixture Results",
        "",
        "| Fixture | Snapshot | Baseline | Approval State | Production Affected |",
        "| --- | --- | --- | --- | --- |",
    ]
    for fixture in report["baseline_fixture_workflows"]["fixtures"]:
        lines.append(
            f"| `{fixture['fixture_id']}` | `{fixture['associated_snapshot_id']}` | `{fixture['baseline_classification']}` | `{fixture['approval_state']}` | `{str(fixture['production_output_affected']).lower()}` |"
        )
    lines.extend(["", "## Phase 4 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_4_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Baseline fixture workflows are available for migration governance, but production planner ownership and routing remain unchanged.",
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
    parser.add_argument("--output", default="docs/generated/v3_1_baseline_fixture_workflows_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_BASELINE_FIXTURE_WORKFLOWS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_baseline_fixture_workflows_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
