"""Extract read-only Forge-safe adapter candidates from the mapping report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPING_REPORT = (
    ROOT / "docs" / "generated" / "forge_safe_stat_key_mapping_report.json"
)
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "forge_safe_adapter_candidates.json"
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT / "docs" / "migration" / "FORGE_SAFE_ADAPTER_CANDIDATES_REVIEW.md"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create candidate-only legacy stat_key adapter diagnostics."
    )
    parser.add_argument("--mapping-report", type=Path, default=DEFAULT_MAPPING_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def load_mapping_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise ValueError("mapping report must be a JSON object")
    metadata = report.get("metadata") or {}
    if metadata.get("production_safe") is not False:
        raise ValueError("mapping report must be marked production_safe=false")
    return report


def build_adapter_candidates(report: dict[str, Any], *, source_path: str) -> dict[str, Any]:
    mappings = list(report.get("mappings") or [])
    shape_counts = Counter(str(mapping.get("mapping_shape")) for mapping in mappings)
    candidates = [
        build_candidate(mapping)
        for mapping in mappings
        if mapping.get("mapping_shape") == "one_to_one"
    ]
    excluded = {
        "one_to_many": [
            exclusion_summary(mapping)
            for mapping in mappings
            if mapping.get("mapping_shape") == "one_to_many"
        ],
        "ambiguous": [
            exclusion_summary(mapping)
            for mapping in mappings
            if mapping.get("mapping_shape") == "ambiguous"
        ],
        "missing": [
            exclusion_summary(mapping)
            for mapping in mappings
            if mapping.get("mapping_shape") == "missing"
        ],
    }

    return {
        "summary": {
            "source_mapping_report": source_path,
            "source_legacy_stat_key_count": report.get("summary", {}).get("legacy_stat_key_count", 0),
            "candidate_count": len(candidates),
            "excluded_one_to_many_count": len(excluded["one_to_many"]),
            "excluded_ambiguous_count": len(excluded["ambiguous"]),
            "excluded_missing_count": len(excluded["missing"]),
            "production_consumed": False,
        },
        "candidates": sorted(candidates, key=lambda item: item["legacy_stat_key"]),
        "excluded": excluded,
        "metadata": {
            "source": "forge_safe_stat_key_mapping_report",
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "consumption_status": "not_consumed",
            "selection_rule": "mapping_shape == one_to_one",
            "excluded_mapping_shapes": ["one_to_many", "ambiguous", "missing"],
            "source_shape_counts": dict(sorted(shape_counts.items())),
        },
    }


def build_candidate(mapping: dict[str, Any]) -> dict[str, Any]:
    references = list(mapping.get("bundle_modifier_references") or [])
    if len(references) != 1:
        raise ValueError(
            f"one_to_one mapping must contain exactly one reference: {mapping.get('legacy_stat_key')}"
        )
    reference = references[0]
    return {
        "legacy_stat_key": mapping.get("legacy_stat_key"),
        "bundle_modifier_reference": {
            "modifier_id": reference.get("modifier_id"),
            "modifier_ids": list(reference.get("modifier_ids") or []),
            "modifier_type": reference.get("modifier_type"),
            "property": reference.get("property"),
            "property_path": reference.get("property_path"),
            "affix_count": reference.get("affix_count", mapping.get("affix_count", 0)),
        },
        "affix_count": mapping.get("affix_count", 0),
        "example_affix_ids": list(mapping.get("example_affix_ids") or []),
        "migration_risk": mapping.get("migration_risk"),
        "candidate_status": "reviewed_candidate",
        "consumption_status": "not_consumed",
        "read_only": True,
        "candidate_only": True,
        "production_consumed": False,
        "notes": [
            "Candidate is structurally one_to_one only.",
            "Gameplay correctness is not proven by this artifact.",
            "Not consumed by production planner, crafting, stat aggregation, simulation, or /api/ref/affixes.",
        ],
    }


def exclusion_summary(mapping: dict[str, Any]) -> dict[str, Any]:
    return {
        "legacy_stat_key": mapping.get("legacy_stat_key"),
        "mapping_shape": mapping.get("mapping_shape"),
        "affix_count": mapping.get("affix_count", 0),
        "migration_risk": mapping.get("migration_risk"),
        "example_affix_ids": list(mapping.get("example_affix_ids") or []),
        "reference_count": len(mapping.get("bundle_modifier_references") or []),
    }


def render_markdown(report: dict[str, Any], mapping_report_path: Path, command: str) -> str:
    summary = report["summary"]
    sample_candidates = report["candidates"][:25]
    one_to_many = report["excluded"]["one_to_many"][:15]
    ambiguous = report["excluded"]["ambiguous"][:15]

    lines = [
        "# Forge-Safe Adapter Candidates Review",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Purpose",
        "",
        "This read-only artifact lists only deterministic one-to-one legacy `stat_key` mappings as adapter candidates for future review. It is not a runtime adapter and is not consumed by planner, crafting, stat aggregation, simulation, or `/api/ref/affixes`.",
        "",
        "## Source",
        "",
        f"Source mapping report: `{mapping_report_path}`",
        "",
        "Generation command:",
        "",
        "```powershell",
        command,
        "```",
        "",
        "## Summary Counts",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| source_legacy_stat_key_count | {summary['source_legacy_stat_key_count']} |",
        f"| candidate_count | {summary['candidate_count']} |",
        f"| excluded_one_to_many_count | {summary['excluded_one_to_many_count']} |",
        f"| excluded_ambiguous_count | {summary['excluded_ambiguous_count']} |",
        f"| excluded_missing_count | {summary['excluded_missing_count']} |",
        f"| production_consumed | {str(summary['production_consumed']).lower()} |",
        "",
        "## Candidate Rule",
        "",
        "A candidate must have `mapping_shape == one_to_one` in the stat-key mapping report and exactly one structural Forge-safe bundle modifier/property reference. The candidate keeps the legacy `stat_key`, the bundle `property_path`, modifier IDs, affix count, examples, migration risk, and explicit `not_consumed` status.",
        "",
        "## Explicit Exclusions",
        "",
        f"- One-to-many mappings excluded: {summary['excluded_one_to_many_count']}",
        f"- Ambiguous mappings excluded: {summary['excluded_ambiguous_count']}",
        f"- Missing mappings excluded: {summary['excluded_missing_count']}",
        "",
        "One-to-many mappings are excluded because direct stat-key routing would need a split or compound modifier policy. Ambiguous mappings are excluded because one legacy key reaches conflicting structural references. Missing mappings are excluded because there is no deterministic bundle reference to review.",
        "",
        "## Candidate Examples",
        "",
        "| Legacy stat_key | Property path | Affixes | Examples |",
        "| --- | --- | ---: | --- |",
    ]
    for candidate in sample_candidates:
        reference = candidate["bundle_modifier_reference"]
        examples = ", ".join(str(value) for value in candidate["example_affix_ids"][:6])
        lines.append(
            f"| `{candidate['legacy_stat_key']}` | `{reference['property_path']}` | {candidate['affix_count']} | {examples} |"
        )

    lines.extend([
        "",
        "## Excluded One-To-Many Examples",
        "",
    ])
    lines.extend(_exclusion_table(one_to_many))
    lines.extend([
        "",
        "## Excluded Ambiguous Examples",
        "",
    ])
    lines.extend(_exclusion_table(ambiguous))
    lines.extend([
        "",
        "## Production Non-Consumption",
        "",
        "The JSON artifact is marked `read_only=true`, `candidate_only=true`, `production_safe=false`, `production_consumer=false`, and `consumption_status=not_consumed`. It is generated under `docs/generated` for review only and is not imported by production services or routes.",
        "",
        "## Migration Implications",
        "",
        "These candidates are safe for review, not safe for production consumption. One-to-one mapping shape alone does not prove gameplay correctness, value-scale compatibility, slot applicability equivalence, or simulation behavior.",
        "",
        "A future adapter must be introduced behind a separate feature flag and tested against planner, crafting, stat aggregation, and simulation baselines. One-to-many and ambiguous mappings require separate policy and design work before they can become candidates.",
        "",
        "Recommended next step: review the candidate list against value-scale and slot-applicability blockers, then design a feature-flagged adapter prototype that consumes only an explicitly approved subset in tests.",
    ])
    return "\n".join(lines) + "\n"


def _exclusion_table(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["No mappings in this excluded category."]
    lines = [
        "| Legacy stat_key | Shape | Affixes | Reference count | Examples |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for item in items:
        examples = ", ".join(str(value) for value in item["example_affix_ids"][:6])
        lines.append(
            f"| `{item['legacy_stat_key']}` | {item['mapping_shape']} | {item['affix_count']} | {item['reference_count']} | {examples} |"
        )
    return lines


def main() -> int:
    args = parse_args()
    mapping_report = load_mapping_report(args.mapping_report)
    report = build_adapter_candidates(mapping_report, source_path=str(args.mapping_report))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe "
        "backend\\scripts\\report_forge_safe_adapter_candidates.py "
        "--mapping-report docs\\generated\\forge_safe_stat_key_mapping_report.json "
        "--output docs\\generated\\forge_safe_adapter_candidates.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_ADAPTER_CANDIDATES_REVIEW.md"
    )
    args.markdown_output.write_text(
        render_markdown(report, args.mapping_report, command),
        encoding="utf-8",
    )
    print(json.dumps({"summary": report["summary"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
