"""Generate the v3 passive/skill mechanical comparison report."""

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

from app.planner_adapters.v3.passive_skill_comparison import (  # noqa: E402
    V3PassiveSkillMechanicalComparison,
    build_sample_passive_skill_rows,
)


def build_v3_passive_skill_mechanical_comparison_report() -> dict[str, Any]:
    current_rows, candidate_rows = build_sample_passive_skill_rows()
    comparator = V3PassiveSkillMechanicalComparison()
    disabled = comparator.compare(current_rows=current_rows, candidate_rows=candidate_rows, enabled=False)
    enabled = comparator.compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_9_passive_skill_sample",
    )
    return {
        "schema_version": "v3.passive_skill_mechanical_comparison_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode_disabled_behavior": disabled["mode"],
        "mode_enabled_behavior": enabled["mode"],
        "summary": enabled["summary"],
        "component_summary": enabled["component_summary"],
        "operation_summary": enabled["operation_summary"],
        "skill_identity_summary": enabled["skill_identity_summary"],
        "semantic_summary": enabled["semantic_summary"],
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
            "blocked_unresolved_skill_identity",
            "blocked_ambiguous_skill_identity",
            "blocked_value_normalization",
            "blocked_conditional_semantics",
            "blocked_triggered_semantics",
        ],
        "current_limitations": [
            "candidate rows are fixtures or future adapter output, not production planner execution",
            "passive and skill identity gaps remain blocking conditions",
            "conditional and triggered semantics are visible blockers, not implemented formulas",
            "cooldown, duration, chance, proc, scripted, text-only, combat, DPS, crafting, and simulation behavior remains blocked",
            "changed deltas require explicit dry-run approval and baseline snapshot evidence",
        ],
        "remaining_blockers_before_limited_opt_in_mechanical_adapter_mode": [
            "approved passive and skill identity bridge policy",
            "approved conditional and triggered operation semantics",
            "cooldown, duration, and chance formula contracts",
            "passive and skill mechanical golden baselines",
            "candidate passive and skill adapters backed by source data, not tooltip inference",
            "dry-run parity review across item, affix, passive, and skill domains",
            "explicit limited opt-in adapter gate review",
        ],
        "metadata": {
            "source": "v3_passive_skill_mechanical_comparison",
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
        "# V3 Passive And Skill Mechanical Comparison",
        "",
        "Phase 9 adds a conservative passive/skill comparison adapter behind the v3 dry-run boundary.",
        "It is comparison infrastructure only and does not calculate production passive or skill mechanics.",
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
        f"- Simple explainable candidate rows: `{summary['candidate_simple_explainable_row_count']}`",
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
            f"- Skill identity bridge added: `{str(safety['skill_identity_bridge_added']).lower()}`",
            f"- Conditional semantics implemented: `{str(safety['conditional_semantics_implemented']).lower()}`",
            f"- Triggered semantics implemented: `{str(safety['triggered_semantics_implemented']).lower()}`",
            f"- Tooltip semantics inferred: `{str(safety['tooltip_semantics_inferred']).lower()}`",
            "",
            "## Current Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["current_limitations"])
    lines.extend(["", "## Remaining Blockers Before Limited Opt-In Mechanical Adapter Mode", ""])
    lines.extend(f"- {item}" for item in report["remaining_blockers_before_limited_opt_in_mechanical_adapter_mode"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_passive_skill_mechanical_comparison_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_PASSIVE_SKILL_MECHANICAL_COMPARISON.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_passive_skill_mechanical_comparison_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
