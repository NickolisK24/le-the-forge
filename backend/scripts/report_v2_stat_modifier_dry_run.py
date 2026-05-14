"""Generate the v2 stat/modifier adapter dry-run comparison report."""

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

from app.planner_adapters.v2.stat_modifier_dry_run import V2StatModifierDryRunComparison


def build_v2_stat_modifier_dry_run_report(*, root: str | Path | None = None) -> dict[str, Any]:
    dry_run = V2StatModifierDryRunComparison(root=root).summarize_dry_run()
    top_blocked_reasons = [
        {"reason": reason, "count": count}
        for reason, count in sorted(dry_run["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "schema_version": "v2.stat_modifier_dry_run.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            **dry_run["summary"],
            "top_blocked_reasons": top_blocked_reasons,
        },
        "operation_distribution": dry_run["operation_distribution"],
        "value_scale_distribution": dry_run["value_scale_distribution"],
        "source_type_distribution": dry_run["source_type_distribution"],
        "blocked_reason_counts": dry_run["blocked_reason_counts"],
        "comparison_category_summary": dry_run["comparison_category_summary"],
        "stat_identity_findings": dry_run["stat_identity_findings"],
        "modifier_identity_coverage": dry_run["modifier_identity_coverage"],
        "unsupported_scripted_text_only_counts": dry_run["unsupported_scripted_text_only_counts"],
        "current_planner_expectation_gaps": dry_run["current_planner_expectation_gaps"],
        "golden_baseline_requirements": dry_run["golden_baseline_requirements"],
        "blocked_samples": dry_run["blocked_samples"],
        "allowed_comparison_categories": dry_run["allowed_comparison_categories"],
        "safety_confirmations": dry_run["safety_confirmations"],
        "future_next_step": {
            "recommendation": "create mechanical golden baselines before any stat/modifier planner remap",
            "planner_remap_ready": False,
            "blocked_until": [
                "value normalization is proven",
                "unknown operations are classified safely",
                "stat and source identity gaps are resolved",
                "golden baseline comparisons exist for representative planner outputs",
            ],
        },
        "metadata": {
            "source": "v2_stat_modifier_dry_run",
            "read_only": True,
            "dry_run_only": True,
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
        "# V2 Stat Modifier Dry Run",
        "",
        "Phase 22 adds a dry-run comparison layer for v2 stat/modifier adapter data.",
        "It does not use v2 stat or modifier data for production planner calculations.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Stat registry entries: `{summary['stat_registry_count']}`",
        f"- Modifier rows: `{summary['modifier_row_count']}`",
        f"- Adapter-visible modifier rows: `{summary['adapter_visible_modifier_count']}`",
        f"- Planner-calculable modifier rows: `{summary['planner_calculable_modifier_count']}`",
        f"- Stable-calculable modifier rows: `{summary['stable_calculable_modifier_count']}`",
        f"- Blocked modifier rows: `{summary['blocked_modifier_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Value Scale Distribution",
        "",
        "| Value scale | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(report["value_scale_distribution"].items()):
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(["", "## Operation Distribution", "", "| Operation | Count |", "| --- | ---: |"])
    for label, count in sorted(report["operation_distribution"].items()):
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(["", "## Comparison Categories", "", "| Category | Count |", "| --- | ---: |"])
    for label, count in sorted(report["comparison_category_summary"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(["", "## Blocked Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for reason, count in sorted(report["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Current Planner Expectation Gaps", ""])
    lines.extend(f"- {item}" for item in report["current_planner_expectation_gaps"])
    lines.extend(["", "## Golden Baseline Requirements", ""])
    lines.extend(f"- {item}" for item in report["golden_baseline_requirements"])
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
            "- Dry-run visibility does not imply planner-calculable or stable-calculable eligibility.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_stat_modifier_dry_run_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_STAT_MODIFIER_DRY_RUN.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_stat_modifier_dry_run_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
