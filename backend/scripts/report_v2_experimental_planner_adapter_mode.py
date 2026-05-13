"""Generate the v2 experimental planner adapter mode report."""

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

from app.planner_adapters.v2.experimental_mode import V2ExperimentalPlannerAdapterMode


def build_v2_experimental_planner_adapter_mode_report(*, root: str | Path | None = None) -> dict[str, Any]:
    mode = V2ExperimentalPlannerAdapterMode(root=root)
    disabled = mode.summarize_mode(enabled=False)
    enabled = mode.summarize_mode(enabled=True)
    return {
        "schema_version": "v2.experimental_planner_adapter_mode_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode_enabled_behavior": enabled["mode"],
        "mode_disabled_behavior": disabled["mode"],
        "gate_mechanism": enabled["mode"]["gate_mechanism"],
        "summaries_included": enabled["summary"]["summaries_included"],
        "summary": enabled["summary"],
        "summaries": enabled["summaries"],
        "blocked_reason_summary": enabled["blocked_reason_summary"],
        "baseline_readiness": enabled["baseline_readiness"],
        "diagnostic_context": enabled["diagnostic_context"],
        "disabled_response": disabled,
        "safety_confirmations": enabled["safety_confirmations"],
        "future_next_step": {
            "recommendation": "use the mode for explicit diagnostic context only while production planner output remains unchanged",
            "planner_remap_ready": False,
            "blocked_until": [
                "value normalization evidence exists",
                "stable-calculable gates allow at least one limited family",
                "golden mechanical baselines are locked",
                "unresolved identity gaps remain blocked or are proven by source data",
            ],
        },
        "metadata": {
            "source": "v2_experimental_planner_adapter_mode",
            "read_only": True,
            "experimental": True,
            "default_enabled": False,
            "optional_route_added": False,
            "production_consumed": False,
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
        "# V2 Experimental Planner Adapter Mode",
        "",
        "Phase 24 adds a limited opt-in experimental planner adapter mode.",
        "The mode exposes diagnostic, display, dry-run, and baseline readiness context only.",
        "",
        "## Gate",
        "",
        f"- Gate mechanism: `{report['gate_mechanism']}`",
        f"- Default enabled: `{str(report['mode_disabled_behavior']['default_enabled']).lower()}`",
        f"- Disabled response active: `{str(report['mode_disabled_behavior']['active']).lower()}`",
        f"- Enabled response active: `{str(report['mode_enabled_behavior']['active']).lower()}`",
        f"- Optional route added: `{str(report['metadata']['optional_route_added']).lower()}`",
        "",
        "## Included Summaries",
        "",
    ]
    lines.extend(f"- `{name}`" for name in report["summaries_included"])
    lines.extend(
        [
            "",
            "## Safety State",
            "",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production planner output changed: `{str(safety['production_planner_output_changed']).lower()}`",
            f"- Planner remap performed: `{str(safety['planner_remap_performed']).lower()}`",
            f"- Mechanical calculations performed: `{str(safety['mechanical_calculations_performed']).lower()}`",
            f"- Planner-calculable count: `{summary['planner_calculable_count']}`",
            f"- Stable-calculable count: `{summary['stable_calculable_count']}`",
            f"- Blocked modifier count: `{summary['blocked_modifier_count']}`",
            f"- Value normalization: `{summary['value_normalization_status']}`",
            f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
            "",
            "## Baseline Readiness",
            "",
            f"- Safe-now baseline fixtures: `{summary['safe_now_baseline_fixture_count']}`",
            f"- Blocked baseline fixtures: `{summary['blocked_baseline_fixture_count']}`",
            f"- Display-only candidates: `{summary['display_only_candidate_count']}`",
            f"- Blocked mechanical categories: `{summary['blocked_mechanical_category_count']}`",
            "",
            "## Top Blocked Reasons",
            "",
            "| Reason | Count |",
            "| --- | ---: |",
        ]
    )
    for row in report["blocked_reason_summary"]:
        lines.append(f"| `{row['reason']}` | `{row['count']}` |")
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
            "- The experimental mode remains disabled unless explicitly requested.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_experimental_planner_adapter_mode_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_EXPERIMENTAL_PLANNER_ADAPTER_MODE.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_experimental_planner_adapter_mode_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
