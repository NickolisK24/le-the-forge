"""Generate read-only v2 planner adapter diagnostics."""

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

from app.planner_adapters.v2.diagnostics import build_planner_adapter_diagnostics


def build_v2_planner_adapter_diagnostics_report(*, root: str | Path | None = None) -> dict[str, Any]:
    report = build_planner_adapter_diagnostics(root=root)
    report["generated_at"] = datetime.now(UTC).isoformat()
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Planner Adapter Diagnostics",
        "",
        "Phase 17 adds read-only diagnostics for the v2 planner-safe adapter boundary.",
        "The diagnostics explain what the adapter can inspect, what it would block, and which future remap phases remain non-calculating.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Planner-calculable records: `{summary['planner_calculable_record_count']}`",
        f"- Stable-calculable records: `{summary['stable_calculable_count']}`",
        f"- Blocked records: `{summary['blocked_record_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Adapter-Visible Versus Planner-Calculable",
        "",
        f"- Adapter-visible records: `{summary['adapter_visible_record_count']}`",
        f"- Planner-calculable records: `{summary['planner_calculable_record_count']}`",
        f"- Domains checked: `{summary['domains_checked']}`",
        "",
        "## Display-Only Candidates",
        "",
    ]
    for item in report["display_only_candidates"]:
        notes = ", ".join(item.get("notes", []))
        lines.append(f"- `{item['category']}`: `{item['classification']}` ({notes})")

    lines.extend(["", "## Blocked Mechanical Data", ""])
    for item in report["blocked_mechanical_data"]:
        reasons = ", ".join(item.get("blocked_reasons", []))
        lines.append(f"- `{item['category']}`: `{item['classification']}` ({reasons})")

    lines.extend(
        [
            "",
            "## Top Blocked Reasons",
            "",
            "| Reason | Count |",
            "| --- | ---: |",
        ]
    )
    for item in report["top_blocked_reasons"]:
        lines.append(f"| `{item['reason']}` | `{item['count']}` |")

    lines.extend(["", "## Future Remap Phase Status", ""])
    for phase in report["future_remap_phase_status"]:
        lines.append(f"{phase['order']}. **{phase['name']}** - `{phase['status']}`")

    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No production planner route was added.",
            "- No production planner, crafting, simulation, or stat output was changed.",
            "- No value scale was promoted.",
            "- No unresolved skill identity was bridged.",
            "- The optional diagnostics route was skipped; this phase is module/script/report only.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_planner_adapter_diagnostics_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_PLANNER_ADAPTER_DIAGNOSTICS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_planner_adapter_diagnostics_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
