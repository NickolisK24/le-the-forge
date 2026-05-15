"""Generate the v3 experimental mechanical dry-run mode report."""

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

from app.planner_adapters.v3.mechanical_dry_run import (  # noqa: E402
    V3ExperimentalMechanicalDryRun,
    build_sample_v3_dry_run_inputs,
)


def build_v3_experimental_dry_run_mode_report() -> dict[str, Any]:
    current_output, candidate_output = build_sample_v3_dry_run_inputs()
    comparator = V3ExperimentalMechanicalDryRun()
    disabled = comparator.compare(current_output=current_output, candidate_output=candidate_output, enabled=False)
    enabled = comparator.compare(
        current_output=current_output,
        candidate_output=candidate_output,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_7_foundation",
    )
    return {
        "schema_version": "v3.experimental_dry_run_mode_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode_disabled_behavior": disabled["mode"],
        "mode_enabled_behavior": enabled["mode"],
        "summary": enabled["summary"],
        "delta_category_counts": enabled["delta_category_counts"],
        "blocked_reasons": enabled["blocked_reasons"],
        "sample_comparison": enabled,
        "disabled_response": disabled,
        "safety_confirmations": enabled["safety_confirmations"],
        "current_limitations": [
            "candidate outputs are supplied fixtures or future adapter outputs, not production planner execution",
            "accepted changed deltas require explicit dry-run approval and baseline snapshot evidence",
            "unsupported, text-only, scripted, unknown-operation, unresolved-identity, and audit-only value rows remain blocked",
            "no final combat, stat, crafting, DPS, or simulation formulas are implemented",
        ],
        "remaining_blockers_before_mechanical_remap": [
            "approved value normalization contracts",
            "approved operation semantics",
            "resolved stat identities for target domains",
            "approved skill identity bridge policy",
            "mechanical golden baselines",
            "candidate adapter implementation behind this comparison boundary",
            "explicit production remap gate review",
        ],
        "metadata": {
            "source": "v3_experimental_dry_run_mode",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "planner_remap_performed": False,
            "production_behavior_changed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Experimental Mechanical Dry-Run Mode",
        "",
        "Phase 7 introduces the first safety layer for future mechanical comparison.",
        "It compares supplied current-planner snapshots with supplied v3 candidate snapshots.",
        "It does not execute production planner code, normalize values, or implement final mechanics.",
        "",
        "## Gate",
        "",
        f"- Default enabled: `{str(report['mode_disabled_behavior']['default_enabled']).lower()}`",
        f"- Disabled response active: `{str(report['mode_disabled_behavior']['active']).lower()}`",
        f"- Enabled response active only when explicitly requested: `{str(report['mode_enabled_behavior']['active']).lower()}`",
        f"- Read-only: `{str(report['mode_enabled_behavior']['read_only']).lower()}`",
        f"- Production consumer: `{str(report['mode_enabled_behavior']['production_consumer']).lower()}`",
        "",
        "## Comparison Summary",
        "",
        f"- Current output count: `{summary['current_output_count']}`",
        f"- Candidate output count: `{summary['candidate_output_count']}`",
        f"- Accepted deltas: `{summary['accepted_delta_count']}`",
        f"- Rejected deltas: `{summary['rejected_delta_count']}`",
        f"- Blocked deltas: `{summary['blocked_delta_count']}`",
        f"- Deterministic hash: `{report['sample_comparison']['deterministic_hash']}`",
        "",
        "## Delta Categories",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
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
            f"- Mechanical calculations performed: `{str(safety['mechanical_calculations_performed']).lower()}`",
            f"- Value normalization promoted: `{str(safety['value_normalization_promoted']).lower()}`",
            f"- Unsupported mechanics promoted: `{str(safety['unsupported_mechanics_promoted']).lower()}`",
            "",
            "## Rollback And Debug Visibility",
            "",
            "- The dry-run result includes a deterministic hash, delta category counts, blocked reasons, comparison rows, and safety confirmations.",
            "- Rollback does not require planner changes because this layer is not production-consumed.",
            "",
            "## Current Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["current_limitations"])
    lines.extend(["", "## Remaining Blockers Before Mechanical Remap", ""])
    lines.extend(f"- {item}" for item in report["remaining_blockers_before_mechanical_remap"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_experimental_dry_run_mode_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_EXPERIMENTAL_DRY_RUN_MODE.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_experimental_dry_run_mode_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
