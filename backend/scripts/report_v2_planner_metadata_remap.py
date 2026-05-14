"""Generate the v2 non-calculating planner metadata remap report."""

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

from app.planner_adapters.v2.metadata import V2PlannerMetadataRemap


def build_v2_planner_metadata_remap_report(*, root: str | Path | None = None) -> dict[str, Any]:
    metadata = V2PlannerMetadataRemap(root=root).summarize_metadata()
    summary = metadata["summary"]
    top_blocked_reasons = [
        {"reason": reason, "count": count}
        for reason, count in sorted(metadata["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    return {
        "schema_version": "v2.planner_metadata_remap.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            **summary,
            "top_blocked_reasons": top_blocked_reasons,
            "optional_route_added": False,
        },
        "domains": metadata["domains"],
        "fields_exposed": metadata["fields_exposed"],
        "forbidden_calculation_fields": metadata["forbidden_calculation_fields"],
        "blocked_reason_counts": metadata["blocked_reason_counts"],
        "metadata_samples": metadata["metadata_samples"],
        "display_only_candidates": metadata["display_only_candidates"],
        "blocked_mechanical_data": metadata["blocked_mechanical_data"],
        "safety_confirmations": metadata["safety_confirmations"],
        "metadata_policy": metadata["metadata_policy"],
        "future_next_step": {
            "recommendation": "create non-calculating planner debug consumers before any mechanical adapter remap",
            "planner_remap_ready": False,
            "blocked_until": [
                "value normalization is proven",
                "stable-calculable gates produce nonzero eligible records",
                "unresolved skill identity remains guarded",
                "golden planner/crafting/simulation baselines exist",
            ],
        },
        "metadata": {
            "source": "v2_planner_metadata_remap",
            "read_only": True,
            "non_calculating": True,
            "production_consumed": False,
            "planner_remap_performed": False,
            "optional_route_added": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Planner Metadata Remap",
        "",
        "Phase 18 adds a non-calculating planner metadata layer.",
        "It exposes v2 identity, support, provenance, warnings, debug status, and adapter blocked reasons without feeding v2 values into planner math.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Metadata records inspected: `{summary['metadata_records_inspected']}`",
        f"- Display-only eligible records: `{summary['display_only_eligible_count']}`",
        f"- Planner-calculable records: `{summary['planner_calculable_count']}`",
        f"- Stable-calculable records: `{summary['stable_calculable_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Fields Exposed",
        "",
    ]
    lines.extend(f"- `{field}`" for field in report["fields_exposed"])
    lines.extend(["", "## Calculation Fields Explicitly Excluded", ""])
    lines.extend(f"- `{field}`" for field in report["forbidden_calculation_fields"])
    lines.extend(["", "## Domain Summary", "", "| Domain | Inspected | Display-only | Planner-calculable | Stable |", "| --- | ---: | ---: | ---: | ---: |"])
    for domain in report["domains"]:
        lines.append(
            f"| `{domain['domain']}` | `{domain['inspected_count']}` | "
            f"`{domain['display_only_eligible_count']}` | `{domain['planner_calculable_count']}` | "
            f"`{domain['stable_calculable_count']}` |"
        )
    lines.extend(["", "## Display-Only Candidates", ""])
    for candidate in report["display_only_candidates"]:
        notes = ", ".join(candidate.get("notes", []))
        lines.append(f"- `{candidate['category']}`: {notes}")
    lines.extend(["", "## Top Blocked Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for item in summary["top_blocked_reasons"]:
        lines.append(f"| `{item['reason']}` | `{item['count']}` |")
    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No production planner route was added.",
            "- No planner, crafting, simulation, or stat output was changed.",
            "- No value scale was promoted.",
            "- No unresolved skill identity was bridged.",
            "- Display-only eligibility does not imply planner-calculable or stable-calculable eligibility.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_planner_metadata_remap_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_PLANNER_METADATA_REMAP.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_planner_metadata_remap_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
