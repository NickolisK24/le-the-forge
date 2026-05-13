"""Generate the v2 golden baseline planning report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v2.golden_baselines import build_golden_baseline_plan


def build_v2_golden_baseline_plan_report(*, root: str | Path | None = None) -> dict[str, Any]:
    plan = build_golden_baseline_plan(root=root)
    return {
        "schema_version": "v2.golden_baseline_plan.1",
        "generated_at": datetime.now(UTC).isoformat(),
        **plan,
        "future_next_step": {
            "recommendation": "create existing-production-only planner output snapshots before any experimental mechanical adapter mode",
            "planner_remap_ready": False,
            "blocked_until": [
                "non-mechanical fixtures are reviewed",
                "representative production builds are selected",
                "value normalization evidence exists for any mechanical assertion",
                "dry-run deltas are explainable without changing production output",
            ],
        },
        "metadata": {
            "source": "v2_golden_baseline_plan",
            "read_only": True,
            "planning_only": True,
            "production_consumed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Golden Baseline Plan",
        "",
        "Phase 23 defines the baseline categories and fixture scaffold required before any future mechanical planner remap.",
        "It does not use v2 stat or modifier data for production planner calculations.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Baseline categories: `{summary['baseline_category_count']}`",
        f"- Safe-now fixtures: `{summary['safe_now_fixture_count']}`",
        f"- Blocked fixtures: `{summary['blocked_fixture_count']}`",
        f"- Mechanical fixture categories: `{summary['mechanical_fixture_count']}`",
        f"- Non-mechanical fixture categories: `{summary['non_mechanical_fixture_count']}`",
        f"- Stable-calculable count: `{summary['stable_calculable_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Baseline Categories",
        "",
        "| Category | Status | Fixture | Mechanical |",
        "| --- | --- | --- | --- |",
    ]
    for category in report["baseline_categories"]:
        lines.append(
            f"| `{category['category_id']}` | `{category['current_status']}` | `{category['fixture_path']}` | `{str(category['mechanical_calculation_involved']).lower()}` |"
        )
    lines.extend(["", "## Blocker Summary", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in sorted(report["blocker_summary"].items()):
        lines.append(f"| `{status}` | `{count}` |")
    lines.extend(["", "## Required Preconditions Before Mechanical Remap", ""])
    lines.extend(f"- {item}" for item in report["required_preconditions_before_mechanical_remap"])
    lines.extend(["", "## Fixture Scaffold", ""])
    lines.extend(f"- `{path}`" for path in report["fixture_paths"])
    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No production planner route was added.",
            "- No stat or modifier calculation behavior was changed.",
            "- No crafting, simulation, or stat aggregation behavior was changed.",
            "- No value scale was promoted.",
            "- No unresolved skill identity reference was bridged.",
            "- Safe-now fixtures are non-mechanical planning fixtures only.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_golden_baseline_plan.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_GOLDEN_BASELINE_PLAN.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_golden_baseline_plan_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
