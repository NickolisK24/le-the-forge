"""Generate the v3 item/affix mechanical comparison report."""

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

from app.planner_adapters.v3.item_affix_comparison import (  # noqa: E402
    V3ItemAffixMechanicalComparison,
    build_sample_item_affix_rows,
)


def build_v3_item_affix_mechanical_comparison_report() -> dict[str, Any]:
    current_rows, candidate_rows = build_sample_item_affix_rows()
    comparator = V3ItemAffixMechanicalComparison()
    disabled = comparator.compare(current_rows=current_rows, candidate_rows=candidate_rows, enabled=False)
    enabled = comparator.compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_8_item_affix_sample",
    )
    return {
        "schema_version": "v3.item_affix_mechanical_comparison_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode_disabled_behavior": disabled["mode"],
        "mode_enabled_behavior": enabled["mode"],
        "summary": enabled["summary"],
        "component_summary": enabled["component_summary"],
        "operation_summary": enabled["operation_summary"],
        "delta_category_counts": enabled["delta_category_counts"],
        "blocked_reasons": enabled["blocked_reasons"],
        "sample_comparison": enabled,
        "disabled_response": disabled,
        "safety_confirmations": enabled["safety_confirmations"],
        "supported_comparison_categories": [
            "accepted_unchanged",
            "accepted_explicit_dry_run_delta",
            "rejected_unapproved_delta",
        ],
        "blocked_comparison_categories": [
            "blocked_missing_candidate",
            "blocked_missing_current",
            "blocked_missing_provenance",
            "blocked_unsupported_mechanic",
            "blocked_text_only_mechanic",
            "blocked_scripted_mechanic",
            "blocked_unknown_operation",
            "blocked_unresolved_stat_identity",
            "blocked_value_normalization",
        ],
        "current_limitations": [
            "only item bases, implicits, and standard affix rows are represented",
            "candidate rows are fixtures or future adapter output, not production planner execution",
            "unique, set, scripted, text-only, conditional, proc, skill-specific, combat, DPS, and crafting behavior remains blocked",
            "value normalization must already be approved per row; unknown or audit-only values remain blocked",
            "changed deltas require explicit dry-run approval and baseline snapshot evidence",
        ],
        "remaining_blockers_before_passive_skill_comparison": [
            "passive and skill identity bridge policy",
            "passive and skill mechanical golden baselines",
            "unsupported scripted passive and skill behavior policy",
            "operation semantics for conditional, triggered, cooldown, duration, and chance effects",
            "candidate passive and skill row adapters behind the dry-run boundary",
        ],
        "metadata": {
            "source": "v3_item_affix_mechanical_comparison",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Item And Affix Mechanical Comparison",
        "",
        "Phase 8 adds the first item/affix domain adapter behind the v3 dry-run comparison boundary.",
        "It is read-only, opt-in, and non-production-consuming.",
        "It does not replace production planner math or implement final combat/stat formulas.",
        "",
        "## Gate",
        "",
        f"- Default enabled: `{str(report['mode_disabled_behavior']['default_enabled']).lower()}`",
        f"- Disabled response active: `{str(report['mode_disabled_behavior']['active']).lower()}`",
        f"- Enabled only by explicit request: `{str(report['mode_enabled_behavior']['active']).lower()}`",
        f"- Production consumer: `{str(report['mode_enabled_behavior']['production_consumer']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Current rows: `{summary['current_row_count']}`",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Mechanically explainable candidate rows: `{summary['candidate_mechanically_explainable_row_count']}`",
        f"- Accepted deltas: `{summary['accepted_delta_count']}`",
        f"- Rejected deltas: `{summary['rejected_delta_count']}`",
        f"- Blocked deltas: `{summary['blocked_delta_count']}`",
        f"- Deterministic hash: `{report['sample_comparison']['deterministic_hash']}`",
        "",
        "## Component Summary",
        "",
        "| Component | Count |",
        "| --- | ---: |",
    ]
    for component, count in report["component_summary"].items():
        lines.append(f"| `{component}` | `{count}` |")
    lines.extend(["", "## Delta Categories", "", "| Category | Count |", "| --- | ---: |"])
    for category, count in report["delta_category_counts"].items():
        lines.append(f"| `{category}` | `{count}` |")
    lines.extend(["", "## Blocked Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for row in report["blocked_reasons"]:
        lines.append(f"| `{row['reason']}` | `{row['count']}` |")
    lines.extend(
        [
            "",
            "## Safety Confirmations",
            "",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production enabled: `{str(safety['production_enabled']).lower()}`",
            f"- Production planner output changed: `{str(safety['production_planner_output_changed']).lower()}`",
            f"- Planner remap performed: `{str(safety['planner_remap_performed']).lower()}`",
            f"- Runtime stat aggregation changed: `{str(safety['runtime_stat_aggregation_changed']).lower()}`",
            f"- Unique/set logic added: `{str(safety['unique_set_logic_added']).lower()}`",
            f"- Tooltip semantics inferred: `{str(safety['tooltip_semantics_inferred']).lower()}`",
            "",
            "## Current Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["current_limitations"])
    lines.extend(["", "## Remaining Blockers Before Passive/Skill Comparison", ""])
    lines.extend(f"- {item}" for item in report["remaining_blockers_before_passive_skill_comparison"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_item_affix_mechanical_comparison_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_ITEM_AFFIX_MECHANICAL_COMPARISON.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_item_affix_mechanical_comparison_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
