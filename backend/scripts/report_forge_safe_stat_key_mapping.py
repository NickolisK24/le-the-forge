"""Build a read-only legacy stat_key to Forge-safe modifier mapping report."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COMPARISON_PATH = (
    ROOT / "docs" / "generated" / "forge_safe_legacy_affix_comparison.json"
)
DEFAULT_OUTPUT_PATH = (
    ROOT / "docs" / "generated" / "forge_safe_stat_key_mapping_report.json"
)
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT / "docs" / "migration" / "FORGE_SAFE_STAT_KEY_MAPPING_REVIEW.md"
)
SOURCE_ID_RE = re.compile(r"^[a-z_]+:\d+(?:#slot\d+)?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report deterministic legacy stat_key to Forge-safe modifier mappings."
    )
    parser.add_argument("--comparison-path", type=Path, default=DEFAULT_COMPARISON_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def load_comparison(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    comparison = payload.get("comparison", payload)
    if not isinstance(comparison, dict):
        raise ValueError("comparison report must be a JSON object")
    metadata = comparison.get("metadata") or {}
    if metadata.get("truncated", {}).get("differences"):
        raise ValueError("comparison report differences are truncated")
    return comparison


def build_mapping_report(comparison: dict[str, Any]) -> dict[str, Any]:
    rows_by_stat_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    one_to_two_splits: list[dict[str, Any]] = []

    for difference in comparison.get("differences") or []:
        legacy = difference.get("legacy") or {}
        bundle = difference.get("bundle") or {}
        legacy_stat_keys = [str(value) for value in legacy.get("stat_keys") or [] if value]
        if not legacy_stat_keys:
            continue

        references = bundle_modifier_references(bundle)
        row = {
            "affix_id": _string_affix_id(difference.get("affix_id")),
            "legacy": compact_legacy_summary(legacy),
            "bundle": compact_bundle_summary(bundle),
            "references": references,
            "reference_paths": tuple(ref["property_path"] for ref in references),
        }
        for legacy_stat_key in legacy_stat_keys:
            rows_by_stat_key[legacy_stat_key].append(row)
            if legacy.get("modifier_count") == 1 and bundle.get("modifier_count") == 2:
                one_to_two_splits.append({
                    "legacy_stat_key": legacy_stat_key,
                    "affix_id": _coerce_affix_id(difference.get("affix_id")),
                    "legacy_summary": compact_legacy_summary(legacy),
                    "bundle_modifier_references": references,
                    "bundle_modifier_ids": list(bundle.get("modifier_ids") or []),
                })

    mappings = [
        build_mapping(legacy_stat_key, rows)
        for legacy_stat_key, rows in sorted(rows_by_stat_key.items())
    ]
    shape_counts = Counter(mapping["mapping_shape"] for mapping in mappings)
    all_reference_paths = {
        ref["property_path"]
        for mapping in mappings
        for ref in mapping["bundle_modifier_references"]
    }

    summary = {
        "matched_affix_count": comparison.get("summary", {}).get("matched_count", 0),
        "stat_key_difference_count": comparison.get("summary", {}).get("stat_key_difference_count", 0),
        "legacy_stat_key_count": len(mappings),
        "unique_bundle_modifier_reference_count": len(all_reference_paths),
        "one_to_one_mapping_count": shape_counts["one_to_one"],
        "one_to_many_mapping_count": shape_counts["one_to_many"],
        "missing_mapping_count": shape_counts["missing"],
        "ambiguous_mapping_count": shape_counts["ambiguous"],
        "one_to_two_affix_count": len(one_to_two_splits),
    }

    return {
        "summary": summary,
        "mapping_shape_breakdown": dict(sorted(shape_counts.items())),
        "mappings": mappings,
        "one_to_two_splits": sorted(
            one_to_two_splits,
            key=lambda item: (item["legacy_stat_key"], _sort_affix_id(item["affix_id"])),
        ),
        "metadata": {
            "source": "forge_safe_legacy_affix_comparison",
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "match_strategy": "exact_affix_id",
            "classification": "deterministic_structural_references_only",
        },
    }


def build_mapping(legacy_stat_key: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    reference_counts: Counter[str] = Counter()
    reference_examples: dict[str, dict[str, Any]] = {}
    affix_signatures = set()
    split_affix_count = 0

    for row in rows:
        paths = tuple(row["reference_paths"])
        affix_signatures.add(paths)
        if len(paths) > 1:
            split_affix_count += 1
        for reference in row["references"]:
            path = reference["property_path"]
            reference_counts[path] += 1
            reference_examples.setdefault(path, reference)

    references = []
    for path, count in sorted(reference_counts.items()):
        example = dict(reference_examples[path])
        example["affix_count"] = count
        references.append(example)

    mapping_shape = classify_mapping(rows, affix_signatures, reference_counts)
    return {
        "legacy_stat_key": legacy_stat_key,
        "affix_count": len(rows),
        "bundle_modifier_references": references,
        "mapping_shape": mapping_shape,
        "migration_risk": migration_risk(mapping_shape),
        "split_affix_count": split_affix_count,
        "example_affix_ids": [
            _coerce_affix_id(row["affix_id"])
            for row in sorted(rows, key=lambda item: _sort_affix_id(item["affix_id"]))[:10]
        ],
    }


def classify_mapping(
    rows: list[dict[str, Any]],
    affix_signatures: set[tuple[str, ...]],
    reference_counts: Counter[str],
) -> str:
    if not reference_counts:
        return "missing"
    if all(len(row["reference_paths"]) == 1 for row in rows):
        if len(reference_counts) == 1:
            return "one_to_one"
        return "ambiguous"
    if len(affix_signatures) == 1:
        return "one_to_many"
    return "ambiguous"


def migration_risk(mapping_shape: str) -> str:
    if mapping_shape == "one_to_one":
        return "low"
    if mapping_shape == "one_to_many":
        return "medium"
    return "high"


def bundle_modifier_references(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    structured_paths = sorted({
        value
        for value in (str(item) for item in bundle.get("stat_keys") or [])
        if _is_structural_reference(value)
    })
    if not structured_paths:
        structured_paths = sorted(str(item) for item in bundle.get("modifier_ids") or [] if item)

    modifier_ids = sorted(str(item) for item in bundle.get("modifier_ids") or [] if item)
    references = []
    for property_path in structured_paths:
        parts = property_path.split(":")
        references.append({
            "modifier_id": modifier_ids[0] if len(modifier_ids) == 1 else None,
            "modifier_ids": modifier_ids,
            "modifier_type": parts[0] if len(parts) > 1 else None,
            "property": parts[1] if len(parts) > 1 else property_path,
            "property_path": property_path,
            "affix_count": 0,
        })
    return references


def _is_structural_reference(value: str) -> bool:
    if ":" not in value or SOURCE_ID_RE.match(value):
        return False
    first = value.split(":", 1)[0]
    return first.isupper()


def compact_legacy_summary(legacy: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_id": legacy.get("affix_id"),
        "id": legacy.get("id"),
        "name": legacy.get("name"),
        "stat_keys": list(legacy.get("stat_keys") or []),
        "modifier_count": legacy.get("modifier_count"),
    }


def compact_bundle_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_id": bundle.get("affix_id"),
        "id": bundle.get("id"),
        "name": bundle.get("name"),
        "stat_keys": list(bundle.get("stat_keys") or []),
        "modifier_ids": list(bundle.get("modifier_ids") or []),
        "modifier_count": bundle.get("modifier_count"),
    }


def render_markdown(report: dict[str, Any], comparison_path: Path, command: str) -> str:
    summary = report["summary"]
    mappings = report["mappings"]
    one_to_many = [item for item in mappings if item["mapping_shape"] == "one_to_many"]
    ambiguous = [item for item in mappings if item["mapping_shape"] == "ambiguous"]
    missing = [item for item in mappings if item["mapping_shape"] == "missing"]
    split_counts = Counter(item["legacy_stat_key"] for item in report["one_to_two_splits"])

    lines = [
        "# Forge-Safe Stat Key Mapping Review",
        "",
        "Generated: 2026-05-11",
        "",
        "## Purpose",
        "",
        "This read-only diagnostic groups legacy Forge `stat_key` values by the Forge-safe bundle modifier/property references observed in the saved legacy-vs-bundle comparison report. It does not route planner, crafting, stat aggregation, simulation, or `/api/ref/affixes` to the Forge-safe bundle.",
        "",
        "## Source",
        "",
        f"Source comparison report: `{comparison_path}`",
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
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Mapping Shape Breakdown",
        "",
        "| Shape | Count | Migration meaning |",
        "| --- | ---: | --- |",
        f"| one_to_one | {summary['one_to_one_mapping_count']} | Candidate for future adapter work after value/applicability validation. |",
        f"| one_to_many | {summary['one_to_many_mapping_count']} | Requires explicit adapter policy for split or compound modifier routing. |",
        f"| missing | {summary['missing_mapping_count']} | Cannot map without deeper source validation. |",
        f"| ambiguous | {summary['ambiguous_mapping_count']} | Same legacy key reaches conflicting structural references. Requires audit. |",
        "",
        "## Top One-To-Many Mappings",
        "",
    ])
    lines.extend(_mapping_table(sorted(one_to_many, key=lambda item: (-item["affix_count"], item["legacy_stat_key"]))[:20]))

    lines.extend([
        "",
        "## Legacy Single stat_key To Two Bundle Modifiers",
        "",
        f"Total one-to-two affixes: {summary['one_to_two_affix_count']}",
        "",
        "These affixes block a direct legacy `stat_key` adapter because one legacy stat key would need to route into two Forge-safe modifier references without an approved split policy.",
        "",
        "| Legacy stat_key | Affix count | Example affix IDs |",
        "| --- | ---: | --- |",
    ])
    for stat_key, count in split_counts.most_common(25):
        examples = [
            str(item["affix_id"])
            for item in report["one_to_two_splits"]
            if item["legacy_stat_key"] == stat_key
        ][:8]
        lines.append(f"| `{stat_key}` | {count} | {', '.join(examples)} |")

    lines.extend([
        "",
        "## Missing And Ambiguous Mappings",
        "",
        "Missing mappings are legacy stat keys with no structural bundle modifier/property references in the comparison output. Ambiguous mappings are legacy stat keys that map to conflicting structural reference signatures across records.",
        "",
        f"- Missing mapping count: {len(missing)}",
        f"- Ambiguous mapping count: {len(ambiguous)}",
        "",
    ])
    if ambiguous:
        lines.extend(_mapping_table(sorted(ambiguous, key=lambda item: (-item["affix_count"], item["legacy_stat_key"]))[:20]))
    else:
        lines.append("No ambiguous mappings were detected by the deterministic classifier.")

    lines.extend([
        "",
        "## Migration Implications",
        "",
        "Direct legacy `stat_key` mapping is not safe yet. The report has one-to-one candidates, but the comparison still shows universal stat-key differences and 526 one-to-two modifier splits. Adapter generation can only start with one-to-one mappings, and even those still need the separate slot/applicability and value-scale blockers resolved.",
        "",
        "A future adapter can be partially generated from one-to-one mappings as a candidate table. One-to-many mappings require explicit routing policy. Missing and ambiguous mappings require deeper source validation before any production consumer can rely on them.",
        "",
        "Recommended next step: create a reviewed adapter-candidate table for one-to-one mappings only, with tests proving it remains read-only and is not consumed by planner, crafting, stat aggregation, simulation, or `/api/ref/affixes`.",
    ])
    return "\n".join(lines) + "\n"


def _mapping_table(mappings: list[dict[str, Any]]) -> list[str]:
    if not mappings:
        return ["No mappings in this category."]
    lines = [
        "| Legacy stat_key | Affixes | References | Examples |",
        "| --- | ---: | --- | --- |",
    ]
    for mapping in mappings:
        refs = ", ".join(
            f"`{ref['property_path']}`"
            for ref in mapping["bundle_modifier_references"][:4]
        )
        if len(mapping["bundle_modifier_references"]) > 4:
            refs += ", ..."
        examples = ", ".join(str(value) for value in mapping["example_affix_ids"][:6])
        lines.append(
            f"| `{mapping['legacy_stat_key']}` | {mapping['affix_count']} | {refs} | {examples} |"
        )
    return lines


def _coerce_affix_id(value: Any) -> int | str:
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value)


def _string_affix_id(value: Any) -> str:
    return str(value)


def _sort_affix_id(value: Any) -> tuple[int, Any]:
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, str(value))


def main() -> int:
    args = parse_args()
    comparison = load_comparison(args.comparison_path)
    report = build_mapping_report(comparison)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe "
        "backend\\scripts\\report_forge_safe_stat_key_mapping.py "
        "--comparison-path docs\\generated\\forge_safe_legacy_affix_comparison.json "
        "--output docs\\generated\\forge_safe_stat_key_mapping_report.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_STAT_KEY_MAPPING_REVIEW.md"
    )
    args.markdown_output.write_text(
        render_markdown(report, args.comparison_path, command),
        encoding="utf-8",
    )
    print(json.dumps({"summary": report["summary"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
