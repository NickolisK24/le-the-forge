"""Generate the v2 affix display/provenance metadata report."""

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

from app.planner_adapters.v2.affix_metadata import V2AffixDisplayProvenanceMetadata


def build_v2_affix_display_provenance_report(*, root: str | Path | None = None) -> dict[str, Any]:
    metadata = V2AffixDisplayProvenanceMetadata(root=root).summarize_metadata()
    top_blocked_reasons = [
        {"reason": reason, "count": count}
        for reason, count in sorted(metadata["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "schema_version": "v2.affix_display_provenance.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            **metadata["summary"],
            "top_blocked_reasons": top_blocked_reasons,
            "optional_route_added": False,
            "optional_frontend_updated": False,
        },
        "domains": metadata["domains"],
        "prefix_suffix_counts": metadata["prefix_suffix_counts"],
        "fields_exposed": metadata["fields_exposed"],
        "fields_excluded_from_calculation": metadata["fields_excluded_from_calculation"],
        "blocked_reason_counts": metadata["blocked_reason_counts"],
        "metadata_samples": metadata["metadata_samples"],
        "tier_modifier_metadata_treatment": metadata["tier_modifier_metadata_treatment"],
        "safety_confirmations": metadata["safety_confirmations"],
        "future_next_step": {
            "recommendation": "add non-calculating planner/debug consumers for affix identity and provenance before affix value remap",
            "planner_remap_ready": False,
            "blocked_until": [
                "affix value normalization is proven",
                "affix records pass future stable-calculable gates",
                "crafting and stat aggregation golden baselines exist",
            ],
        },
        "metadata": {
            "source": "v2_affix_display_provenance",
            "read_only": True,
            "display_provenance_only": True,
            "production_consumed": False,
            "planner_remap_performed": False,
            "optional_route_added": False,
            "optional_frontend_updated": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V2 Affix Display Provenance",
        "",
        "Phase 20 adds a display/provenance-only affix metadata adapter backed by v2 trusted affix bundles.",
        "It does not use v2 affixes, tiers, or modifier values for planner calculations.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Affixes inspected: `{summary['affix_count']}`",
        f"- Display-only eligible affixes: `{summary['display_only_eligible_count']}`",
        f"- Planner-calculable affixes: `{summary['planner_calculable_count']}`",
        f"- Stable-calculable affixes: `{summary['stable_calculable_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Fields Exposed",
        "",
    ]
    lines.extend(f"- `{field}`" for field in report["fields_exposed"])
    lines.extend(["", "## Fields Excluded From Calculation", ""])
    lines.extend(f"- `{field}`" for field in report["fields_excluded_from_calculation"])
    lines.extend(["", "## Domains", "", "| Domain | Affixes |", "| --- | ---: |"])
    for domain in report["domains"]:
        lines.append(f"| `{domain['domain']}` | `{domain['affix_count']}` |")
    lines.extend(["", "## Prefix/Suffix", "", "| Classification | Affixes |", "| --- | ---: |"])
    for label, count in sorted(report["prefix_suffix_counts"].items()):
        lines.append(f"| `{label}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Tier and Modifier Metadata Treatment",
            "",
            f"- Tier counts exposed: `{str(report['tier_modifier_metadata_treatment']['tier_counts_exposed']).lower()}`",
            f"- Tier ranges exposed: `{str(report['tier_modifier_metadata_treatment']['tier_ranges_exposed']).lower()}`",
            f"- Modifier reference metadata records exposed: `{report['tier_modifier_metadata_treatment']['modifier_reference_metadata_records_exposed']}`",
            f"- Modifier values exposed as planner stats: `{str(report['tier_modifier_metadata_treatment']['modifier_values_exposed_as_planner_stats']).lower()}`",
            "",
            "## Blocked Reasons",
            "",
            "| Reason | Count |",
            "| --- | ---: |",
        ]
    )
    for reason, count in sorted(report["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No production planner route was added.",
            "- No frontend debug page was changed in this phase.",
            "- No affix, modifier, crafting, simulation, or stat calculation behavior was changed.",
            "- No value scale was promoted.",
            "- Display-only eligibility does not imply planner-calculable or stable-calculable eligibility.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_affix_display_provenance_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_AFFIX_DISPLAY_PROVENANCE.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_affix_display_provenance_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
