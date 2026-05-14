"""Generate the v2 passive/skill identity-only remap report."""

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

from app.planner_adapters.v2.passive_skill_identity import V2PassiveSkillIdentityMetadata


def build_v2_passive_skill_identity_remap_report(*, root: str | Path | None = None) -> dict[str, Any]:
    metadata = V2PassiveSkillIdentityMetadata(root=root).summarize_identity_metadata()
    top_blocked_reasons = [
        {"reason": reason, "count": count}
        for reason, count in sorted(metadata["blocked_reason_counts"].items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "schema_version": "v2.passive_skill_identity_remap.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            **metadata["summary"],
            "top_blocked_reasons": top_blocked_reasons,
            "optional_route_added": False,
            "optional_frontend_updated": False,
        },
        "passive_domains": metadata["passive_domains"],
        "skill_domains": metadata["skill_domains"],
        "fields_exposed": metadata["fields_exposed"],
        "fields_excluded_from_calculation": metadata["fields_excluded_from_calculation"],
        "blocked_reason_counts": metadata["blocked_reason_counts"],
        "identity_match_status_counts": metadata["identity_match_status_counts"],
        "ownership_status_counts": metadata["ownership_status_counts"],
        "metadata_samples": metadata["metadata_samples"],
        "skill_identity_audit_summary": metadata["skill_identity_audit_summary"],
        "skill_identity_examples": metadata["skill_identity_examples"],
        "passive_skill_tree_metadata_treatment": metadata["passive_skill_tree_metadata_treatment"],
        "safety_confirmations": metadata["safety_confirmations"],
        "future_next_step": {
            "recommendation": "add display-only planner/debug consumers for passive and skill identity before any passive or skill effect remap",
            "planner_remap_ready": False,
            "blocked_until": [
                "passive and skill effect normalization is proven",
                "value normalization policy moves beyond audit-only",
                "unresolved and ambiguous skill identity references are resolved from source data",
                "golden planner baselines exist for passive and skill behavior",
            ],
        },
        "metadata": {
            "source": "v2_passive_skill_identity_remap",
            "read_only": True,
            "identity_provenance_only": True,
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
    identity = report["skill_identity_audit_summary"]
    treatment = report["passive_skill_tree_metadata_treatment"]
    lines = [
        "# V2 Passive Skill Identity Remap",
        "",
        "Phase 21 adds an identity/provenance-only passive and skill metadata adapter backed by v2 trusted bundles.",
        "It does not use v2 passive or skill effects for planner calculations.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Passive identity records inspected: `{summary['passive_identity_record_count']}`",
        f"- Skill identity records inspected: `{summary['skill_identity_record_count']}`",
        f"- Identity-only eligible records: `{summary['identity_only_eligible_count']}`",
        f"- Planner-calculable records: `{summary['planner_calculable_count']}`",
        f"- Stable-calculable records: `{summary['stable_calculable_count']}`",
        f"- Value normalization: `{summary['value_normalization_status']}`",
        f"- Skill identity bridge: `{summary['skill_identity_bridge_status']}`",
        "",
        "## Skill Identity Audit",
        "",
        f"- Total class/mastery skill refs: `{identity['total_refs']}`",
        f"- Safe top-level matches: `{identity['safe_top_level_matches']}`",
        f"- Unresolved refs: `{identity['unresolved_refs']}`",
        f"- Ambiguous refs: `{identity['ambiguous_refs']}`",
        f"- Bridge safe: `{str(identity['bridge_safe']).lower()}`",
        f"- Recommended mapping strategy: `{identity['recommended_mapping_strategy']}`",
        "",
        "## Fields Exposed",
        "",
    ]
    lines.extend(f"- `{field}`" for field in report["fields_exposed"])
    lines.extend(["", "## Fields Excluded From Calculation", ""])
    lines.extend(f"- `{field}`" for field in report["fields_excluded_from_calculation"])
    lines.extend(["", "## Passive Domains", "", "| Domain | Records |", "| --- | ---: |"])
    for domain in report["passive_domains"]:
        lines.append(f"| `{domain['domain']}` | `{domain['identity_record_count']}` |")
    lines.extend(["", "## Skill Domains", "", "| Domain | Records |", "| --- | ---: |"])
    for domain in report["skill_domains"]:
        lines.append(f"| `{domain['domain']}` | `{domain['identity_record_count']}` |")
    lines.extend(
        [
            "",
            "## Passive / Skill Tree Metadata Treatment",
            "",
            f"- Passive tree links exposed: `{str(treatment['passive_tree_links_exposed']).lower()}`",
            f"- Skill tree links exposed: `{str(treatment['skill_tree_links_exposed']).lower()}`",
            f"- Passive node effects exposed as planner stats: `{str(treatment['passive_node_effects_exposed_as_planner_stats']).lower()}`",
            f"- Skill node effects exposed as planner stats: `{str(treatment['skill_node_effects_exposed_as_planner_stats']).lower()}`",
            f"- Tooltip text used for mechanics: `{str(treatment['tooltip_text_used_for_mechanics']).lower()}`",
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
            "- No passive, skill, crafting, simulation, or stat calculation behavior was changed.",
            "- No value scale was promoted.",
            "- No unresolved or ambiguous skill identity reference was bridged.",
            "- Identity-only eligibility does not imply planner-calculable or stable-calculable eligibility.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_passive_skill_identity_remap_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_PASSIVE_SKILL_IDENTITY_REMAP.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_passive_skill_identity_remap_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
