"""Report read-only slot vocabulary equivalence for adapter candidates."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ADAPTER_CANDIDATES = (
    ROOT / "docs" / "generated" / "forge_safe_adapter_candidates.json"
)
DEFAULT_COMPARISON_REPORT = (
    ROOT / "docs" / "generated" / "forge_safe_legacy_affix_comparison.json"
)
DEFAULT_OUTPUT = (
    ROOT / "docs" / "generated" / "forge_safe_slot_vocabulary_equivalence.json"
)
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT / "docs" / "migration" / "FORGE_SAFE_SLOT_VOCABULARY_EQUIVALENCE_REVIEW.md"
)

PURE = "pure_vocabulary_difference"
BLOCKED = "blocked_by_slot_applicability"
NEEDS_REVIEW = "needs_manual_review"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare legacy slots to Forge-safe item applicability for candidates."
    )
    parser.add_argument("--adapter-candidates", type=Path, default=DEFAULT_ADAPTER_CANDIDATES)
    parser.add_argument("--comparison-report", type=Path, default=DEFAULT_COMPARISON_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def load_comparison(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    comparison = payload.get("comparison", payload)
    if not isinstance(comparison, dict):
        raise ValueError("comparison report must contain a comparison object")
    metadata = comparison.get("metadata") or {}
    if metadata.get("truncated", {}).get("differences"):
        raise ValueError("comparison report differences are truncated")
    return comparison


def build_slot_equivalence_report(
    adapter_candidates: dict[str, Any],
    comparison: dict[str, Any],
    *,
    adapter_candidates_path: str,
    comparison_report_path: str,
) -> dict[str, Any]:
    _validate_candidate_metadata(adapter_candidates)
    candidate_keys = {
        str(candidate.get("legacy_stat_key"))
        for candidate in adapter_candidates.get("candidates") or []
        if candidate.get("legacy_stat_key")
    }
    candidate_rows = _candidate_comparison_rows(comparison, candidate_keys)
    slot_mapping_rows = _slot_mapping_rows(candidate_rows)
    slot_mappings = [
        build_slot_mapping(legacy_slot, rows)
        for legacy_slot, rows in sorted(slot_mapping_rows.items())
    ]
    candidate_statuses = [
        build_candidate_slot_status(candidate, candidate_rows)
        for candidate in adapter_candidates.get("candidates") or []
    ]

    mapping_counts = Counter(row["mapping_shape"] for row in slot_mappings)
    status_counts = Counter(row["slot_status"] for row in candidate_statuses)
    comparison_rows = [
        row for rows in candidate_rows.values() for row in rows
    ]
    legacy_slot_values = {
        slot for row in comparison_rows for slot in _legacy_slots(row)
    }
    bundle_item_values = {
        slot for row in comparison_rows for slot in _bundle_slots(row)
    }

    summary = {
        "candidate_count": len(candidate_keys),
        "candidate_affix_count": len(candidate_rows),
        "legacy_slot_value_count": len(legacy_slot_values),
        "bundle_item_value_count": len(bundle_item_values),
        "one_to_one_slot_mapping_count": mapping_counts["one_to_one"],
        "one_to_many_slot_mapping_count": mapping_counts["one_to_many"],
        "ambiguous_slot_mapping_count": mapping_counts["ambiguous"],
        "missing_slot_mapping_count": mapping_counts["missing"],
        "pure_vocabulary_candidate_count": status_counts[PURE],
        "slot_blocked_candidate_count": status_counts[BLOCKED],
        "needs_manual_review_count": status_counts[NEEDS_REVIEW],
        "production_consumed": False,
    }

    return {
        "summary": summary,
        "slot_mapping_shape_breakdown": {
            "one_to_one": mapping_counts["one_to_one"],
            "one_to_many": mapping_counts["one_to_many"],
            "ambiguous": mapping_counts["ambiguous"],
            "missing": mapping_counts["missing"],
        },
        "candidate_slot_status_breakdown": {
            PURE: status_counts[PURE],
            BLOCKED: status_counts[BLOCKED],
            NEEDS_REVIEW: status_counts[NEEDS_REVIEW],
        },
        "slot_mappings": slot_mappings,
        "candidate_slot_statuses": sorted(
            candidate_statuses,
            key=lambda item: (item["slot_status"], item["legacy_stat_key"]),
        ),
        "metadata": {
            "source": "forge_safe_adapter_candidates + forge_safe_legacy_affix_comparison",
            "adapter_candidates_source": adapter_candidates_path,
            "comparison_report_source": comparison_report_path,
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "consumption_status": "not_consumed",
            "classification_policy": "structural_slot_sets_only",
        },
    }


def build_slot_mapping(legacy_slot: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    bundle_sets = {tuple(_bundle_slots(row)) for row in rows}
    bundle_values = sorted({slot for bundle_set in bundle_sets for slot in bundle_set})
    affix_ids = [_coerce_affix_id(row.get("affix_id")) for row in rows]
    if not legacy_slot or any(not _bundle_slots(row) for row in rows):
        shape = "missing"
        risk = "high"
        notes = ["Legacy or bundle slot evidence is missing."]
    elif len(bundle_sets) == 1 and len(bundle_values) == 1:
        shape = "one_to_one"
        risk = "low"
        notes = ["Same legacy slot consistently maps to one bundle item value."]
    elif len(bundle_sets) == 1:
        shape = "one_to_many"
        risk = "medium"
        notes = ["Same legacy slot consistently maps to a bundle item group."]
    else:
        shape = "ambiguous"
        risk = "high"
        notes = ["Same legacy slot maps to multiple bundle item groups across candidate affixes."]

    return {
        "legacy_slot_value": legacy_slot,
        "bundle_item_values": bundle_values,
        "affix_count": len(rows),
        "example_affix_ids": affix_ids[:10],
        "mapping_shape": shape,
        "migration_risk": risk,
        "notes": notes,
    }


def build_candidate_slot_status(
    candidate: dict[str, Any],
    candidate_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    legacy_stat_key = str(candidate.get("legacy_stat_key") or "")
    rows = candidate_rows.get(legacy_stat_key, [])
    legacy_slot_sets = {tuple(_legacy_slots(row)) for row in rows}
    bundle_slot_sets = {tuple(_bundle_slots(row)) for row in rows}
    legacy_slot_values = sorted({slot for row in rows for slot in _legacy_slots(row)})
    bundle_item_values = sorted({slot for row in rows for slot in _bundle_slots(row)})
    affix_ids = [_coerce_affix_id(row.get("affix_id")) for row in rows]

    if not rows:
        status = NEEDS_REVIEW
        notes = ["No comparison rows were found for this adapter candidate."]
    elif not legacy_slot_values or not bundle_item_values:
        status = BLOCKED
        notes = ["Legacy or bundle applicability values are missing."]
    elif len(legacy_slot_sets) == 1 and len(bundle_slot_sets) == 1:
        status = PURE
        notes = [
            "Candidate affixes consistently map one legacy applicability set to one bundle applicability set.",
            "This does not prove gameplay correctness or value-scale equivalence.",
        ]
    else:
        status = BLOCKED
        notes = [
            "Candidate affixes have inconsistent legacy or bundle applicability sets.",
            "A deterministic slot vocabulary equivalence cannot be proven from this report alone.",
        ]

    return {
        "legacy_stat_key": legacy_stat_key,
        "slot_status": status,
        "affix_count": candidate.get("affix_count", len(rows)),
        "example_affix_ids": list(candidate.get("example_affix_ids") or affix_ids[:10]),
        "comparison_affix_ids": affix_ids,
        "legacy_slot_values": legacy_slot_values,
        "bundle_item_values": bundle_item_values,
        "legacy_slot_sets": [list(value) for value in sorted(legacy_slot_sets)],
        "bundle_item_sets": [list(value) for value in sorted(bundle_slot_sets)],
        "notes": notes,
        "consumption_status": "not_consumed",
    }


def render_markdown(
    report: dict[str, Any],
    *,
    adapter_candidates_path: Path,
    comparison_report_path: Path,
    command: str,
) -> str:
    summary = report["summary"]
    slot_mappings = report["slot_mappings"]
    candidate_statuses = report["candidate_slot_statuses"]
    legacy_slot_counts = Counter()
    bundle_slot_counts = Counter()
    for candidate in candidate_statuses:
        for slot in candidate["legacy_slot_values"]:
            legacy_slot_counts[slot] += candidate["affix_count"]
        for slot in candidate["bundle_item_values"]:
            bundle_slot_counts[slot] += candidate["affix_count"]

    lines = [
        "# Forge-Safe Slot Vocabulary Equivalence Review",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Purpose",
        "",
        "This read-only diagnostic compares legacy slot/applicability vocabulary to Forge-safe bundle item/applicability vocabulary for one-to-one adapter candidate affixes only. It does not address value-scale differences and does not enable any runtime adapter.",
        "",
        "## Sources",
        "",
        f"- Adapter candidates: `{adapter_candidates_path}`",
        f"- Comparison report: `{comparison_report_path}`",
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
        "## Top Legacy Slot Values",
        "",
        "| Legacy slot | Candidate affix references |",
        "| --- | ---: |",
    ])
    for slot, count in legacy_slot_counts.most_common(20):
        lines.append(f"| `{slot}` | {count} |")

    lines.extend([
        "",
        "## Top Bundle Item Values",
        "",
        "| Bundle item value | Candidate affix references |",
        "| --- | ---: |",
    ])
    for slot, count in bundle_slot_counts.most_common(20):
        lines.append(f"| `{slot}` | {count} |")

    lines.extend([
        "",
        "## Mapping Shape Breakdown",
        "",
        "| Shape | Count |",
        "| --- | ---: |",
    ])
    for key, value in report["slot_mapping_shape_breakdown"].items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Candidate Slot Status Breakdown",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ])
    for key, value in report["candidate_slot_status_breakdown"].items():
        lines.append(f"| {key} | {value} |")

    pure_examples = [
        item for item in candidate_statuses if item["slot_status"] == PURE
    ][:20]
    blocked_examples = [
        item for item in candidate_statuses if item["slot_status"] == BLOCKED
    ][:20]
    lines.extend([
        "",
        "## Pure Vocabulary Difference Examples",
        "",
    ])
    lines.extend(_candidate_table(pure_examples))
    lines.extend([
        "",
        "## Blocked Slot Applicability Examples",
        "",
    ])
    lines.extend(_candidate_table(blocked_examples))
    lines.extend([
        "",
        "## Migration Implications",
        "",
        "Slot vocabulary normalization is tractable for candidates classified as pure vocabulary differences because each candidate has a consistent legacy applicability set and a consistent bundle applicability set. This is still review evidence only; it does not prove gameplay correctness and does not resolve value-scale blockers.",
        "",
        "Candidates classified as blocked need slot policy/design work before adapter prototyping. Value-scale normalization remains a separate audit after slot vocabulary policy is settled.",
        "",
        "Recommended next step: document a slot vocabulary policy for the pure vocabulary candidate groups and explicitly list blocked slot-applicability cases that need design decisions before value-scale normalization work starts.",
    ])
    return "\n".join(lines) + "\n"


def _candidate_comparison_rows(
    comparison: dict[str, Any],
    candidate_keys: set[str],
) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for difference in comparison.get("differences") or []:
        legacy = difference.get("legacy") or {}
        for stat_key in legacy.get("stat_keys") or []:
            if str(stat_key) in candidate_keys:
                rows[str(stat_key)].append(difference)
    return rows


def _slot_mapping_rows(
    rows_by_stat_key: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate_rows in rows_by_stat_key.values():
        for row in candidate_rows:
            legacy_slots = _legacy_slots(row)
            if not legacy_slots:
                rows[""].append(row)
            for legacy_slot in legacy_slots:
                rows[legacy_slot].append(row)
    return rows


def _legacy_slots(row: dict[str, Any]) -> list[str]:
    legacy = row.get("legacy") or {}
    return sorted(str(slot) for slot in legacy.get("slots") or [] if slot)


def _bundle_slots(row: dict[str, Any]) -> list[str]:
    bundle = row.get("bundle") or {}
    return sorted(str(slot) for slot in bundle.get("slots") or [] if slot)


def _validate_candidate_metadata(adapter_candidates: dict[str, Any]) -> None:
    metadata = adapter_candidates.get("metadata") or {}
    if metadata.get("read_only") is not True:
        raise ValueError("adapter candidates must be read_only=true")
    if metadata.get("candidate_only") is not True:
        raise ValueError("adapter candidates must be candidate_only=true")
    if metadata.get("production_safe") is not False:
        raise ValueError("adapter candidates must be production_safe=false")


def _candidate_table(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["No candidates in this category."]
    lines = [
        "| Legacy stat_key | Affixes | Legacy slots | Bundle items | Examples |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for item in items:
        examples = ", ".join(str(value) for value in item["example_affix_ids"][:8])
        legacy_slots = ", ".join(f"`{slot}`" for slot in item["legacy_slot_values"][:8])
        bundle_slots = ", ".join(f"`{slot}`" for slot in item["bundle_item_values"][:8])
        lines.append(
            f"| `{item['legacy_stat_key']}` | {item['affix_count']} | {legacy_slots} | {bundle_slots} | {examples} |"
        )
    return lines


def _coerce_affix_id(value: Any) -> int | str:
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value)


def main() -> int:
    args = parse_args()
    adapter_candidates = load_json(args.adapter_candidates)
    comparison = load_comparison(args.comparison_report)
    report = build_slot_equivalence_report(
        adapter_candidates,
        comparison,
        adapter_candidates_path=str(args.adapter_candidates),
        comparison_report_path=str(args.comparison_report),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe "
        "backend\\scripts\\report_forge_safe_slot_vocabulary_equivalence.py "
        "--adapter-candidates docs\\generated\\forge_safe_adapter_candidates.json "
        "--comparison-report docs\\generated\\forge_safe_legacy_affix_comparison.json "
        "--output docs\\generated\\forge_safe_slot_vocabulary_equivalence.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_SLOT_VOCABULARY_EQUIVALENCE_REVIEW.md"
    )
    args.markdown_output.write_text(
        render_markdown(
            report,
            adapter_candidates_path=args.adapter_candidates,
            comparison_report_path=args.comparison_report,
            command=command,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"summary": report["summary"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
