"""Generate the v2 planner-safe adapter boundary report."""

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

from app.planner_adapters.v2 import V2PlannerSafeAdapter


def build_v2_planner_adapter_report(*, root: str | Path | None = None) -> dict[str, Any]:
    adapter = V2PlannerSafeAdapter(root=root)
    summary = adapter.summarize_eligibility()
    top_blocked_reasons = sorted(
        summary["blocked_reason_counts"].items(),
        key=lambda item: (-item[1], item[0]),
    )[:10]
    report = {
        "schema_version": "v2.planner_adapter_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            **summary["summary"],
            "top_blocked_reasons": [
                {"reason": reason, "count": count}
                for reason, count in top_blocked_reasons
            ],
            "value_normalization_status": summary["policy"]["value_normalization_status"],
            "skill_identity_bridge_status": summary["policy"]["skill_identity_bridge_status"],
        },
        "domains": summary["domains"],
        "blocked_reason_counts": summary["blocked_reason_counts"],
        "eligible_samples": summary["eligible_samples"],
        "blocked_samples": summary["blocked_samples"],
        "safety_gates": summary["safety_gates"],
        "future_remap_readiness": {
            "planner_remap_ready": False,
            "reasons": [
                "stable-calculable count is zero",
                "value normalization remains audit-only",
                "skill identity bridge remains unbridged",
                "partial, unsupported, text-only, scripted, or source-unit records remain blocked",
            ],
        },
        "metadata": {
            "source": "v2_planner_safe_adapter",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "production_consumed": False,
            "planner_consumed": False,
            "value_policy_audit_only": True,
            "unresolved_skill_identity_bridged": False,
        },
    }
    return report


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Planner-Safe Adapter",
        "",
        "## Purpose",
        "",
        "This document defines the initial planner-safe adapter boundary for future v2 trusted-data consumption.",
        "",
        "The adapter is read-only and conservative. It can inspect normalized v2 modifier rows and explain why records are blocked from planner-facing calculation, but it does not switch production planner behavior to v2 data.",
        "",
        "## Summary",
        "",
        f"- Domains inspected: `{summary['domain_count']}`",
        f"- Modifiers inspected: `{summary['inspected_modifier_count']}`",
        f"- Eligible planner-calculable records: `{summary['eligible_planner_calculable_count']}`",
        f"- Blocked records: `{summary['blocked_modifier_count']}`",
        f"- Stable-calculable count: `{summary['stable_calculable_count']}`",
        f"- Production consumed: `{str(summary['production_consumed']).lower()}`",
        f"- Value normalization status: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge status: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Safety Gates",
        "",
    ]
    lines.extend(f"- `{gate}`" for gate in report["safety_gates"])
    lines.extend([
        "",
        "## Blocked Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ])
    for reason, count in sorted(report["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{reason}` | `{count}` |")

    lines.extend([
        "",
        "## Domain Coverage",
        "",
        "| Domain | Inspected | Eligible | Blocked | Stable |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for domain in report["domains"]:
        lines.append(
            f"| `{domain['domain']}` | `{domain['inspected_count']}` | `{domain['eligible_count']}` | "
            f"`{domain['blocked_count']}` | `{domain['stable_calculable_count']}` |"
        )

    lines.extend([
        "",
        "## Runtime Behavior",
        "",
        "- Production planner behavior was not changed.",
        "- Crafting, simulation, and stat aggregation behavior were not changed.",
        "- No v2 records are exposed as planner-calculable in this phase.",
        "- Unresolved skill identity references remain unbridged.",
        "- Value normalization remains audit-only.",
        "",
        "## Optional Route Status",
        "",
        "No planner adapter debug route was added in this phase. The adapter boundary is available to backend code and generated reporting only.",
        "",
        "## Recommended Next Step",
        "",
        "Use this adapter report to choose the first small planner-safe prototype only after value normalization and stable eligibility policies produce nonzero planner-safe records.",
    ])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_planner_adapter_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_PLANNER_SAFE_ADAPTER.md")
    args = parser.parse_args()

    report = build_v2_planner_adapter_report()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, Path(args.markdown_output))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
