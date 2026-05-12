"""Validate Forge-safe adapter candidates against comparison blockers."""

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
    ROOT / "docs" / "generated" / "forge_safe_adapter_candidate_validation.json"
)
DEFAULT_MARKDOWN_OUTPUT = (
    ROOT
    / "docs"
    / "migration"
    / "FORGE_SAFE_ADAPTER_CANDIDATE_VALIDATION_REVIEW.md"
)

APPROVED = "approved_for_test_adapter_candidate"
BLOCKED_VALUE = "blocked_by_value_scale"
BLOCKED_SLOT = "blocked_by_slot_applicability"
BLOCKED_BOTH = "blocked_by_both"
NEEDS_REVIEW = "needs_manual_review"
STATUSES = [APPROVED, BLOCKED_VALUE, BLOCKED_SLOT, BLOCKED_BOTH, NEEDS_REVIEW]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one-to-one adapter candidates against existing blockers."
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


def build_validation_report(
    adapter_candidates: dict[str, Any],
    comparison: dict[str, Any],
    *,
    adapter_candidates_path: str,
    comparison_report_path: str,
) -> dict[str, Any]:
    _validate_candidate_metadata(adapter_candidates)
    comparison_by_stat_key = _comparison_by_legacy_stat_key(comparison)

    validated = [
        validate_candidate(candidate, comparison_by_stat_key)
        for candidate in adapter_candidates.get("candidates") or []
    ]
    status_counts = Counter(item["candidate_status"] for item in validated)
    summary = {
        "candidate_count": len(validated),
        "approved_for_test_adapter_candidate_count": status_counts[APPROVED],
        "blocked_by_value_scale_count": status_counts[BLOCKED_VALUE],
        "blocked_by_slot_applicability_count": status_counts[BLOCKED_SLOT],
        "blocked_by_both_count": status_counts[BLOCKED_BOTH],
        "needs_manual_review_count": status_counts[NEEDS_REVIEW],
        "production_consumed": False,
    }

    return {
        "summary": summary,
        "status_breakdown": {status: status_counts[status] for status in STATUSES},
        "validated_candidates": sorted(
            validated,
            key=lambda item: (item["candidate_status"], item["legacy_stat_key"]),
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
            "classification_policy": "conservative_existing_evidence_only",
        },
    }


def validate_candidate(
    candidate: dict[str, Any],
    comparison_by_stat_key: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    legacy_stat_key = str(candidate.get("legacy_stat_key") or "")
    rows = comparison_by_stat_key.get(legacy_stat_key, [])
    difference_types = sorted({
        str(diff_type)
        for row in rows
        for diff_type in row.get("difference_types") or []
    })
    comparison_affix_ids = [_coerce_affix_id(row.get("affix_id")) for row in rows]
    blockers = {
        "value_scale": [],
        "slot_applicability": [],
        "structural": [],
    }
    notes = []

    if not legacy_stat_key or not rows:
        status = NEEDS_REVIEW
        notes.append("No comparison evidence was found for this candidate.")
    elif candidate.get("candidate_status") != "reviewed_candidate":
        status = NEEDS_REVIEW
        notes.append("Candidate row is missing reviewed_candidate status.")
    else:
        value_blocked = "tier" in difference_types
        slot_blocked = "slot" in difference_types
        if value_blocked:
            blockers["value_scale"].append(
                "Comparison reports tier/value differences; no scale equivalence is proven."
            )
        if slot_blocked:
            blockers["slot_applicability"].append(
                "Comparison reports slot/item applicability differences; no vocabulary equivalence is proven."
            )
        if "structure" in difference_types:
            blockers["structural"].append(
                "Comparison reports source/category or name structure differences."
            )

        if value_blocked and slot_blocked:
            status = BLOCKED_BOTH
        elif value_blocked:
            status = BLOCKED_VALUE
        elif slot_blocked:
            status = BLOCKED_SLOT
        elif not difference_types or difference_types == ["stat_key"]:
            status = APPROVED
            notes.append(
                "No slot or tier/value blockers were present in existing comparison evidence."
            )
        else:
            status = NEEDS_REVIEW
            notes.append("Comparison evidence includes blockers outside slot/tier policy.")

    if status != APPROVED:
        notes.append("Candidate remains not consumed by production behavior.")

    return {
        "legacy_stat_key": legacy_stat_key,
        "candidate_status": status,
        "affix_count": candidate.get("affix_count", 0),
        "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        "bundle_modifier_reference": candidate.get("bundle_modifier_reference") or {},
        "blockers": blockers,
        "evidence": {
            "difference_types": difference_types,
            "comparison_affix_ids": comparison_affix_ids,
            "comparison_affix_count": len(rows),
        },
        "consumption_status": "not_consumed",
        "notes": notes,
    }


def render_markdown(
    report: dict[str, Any],
    *,
    adapter_candidates_path: Path,
    comparison_report_path: Path,
    command: str,
) -> str:
    summary = report["summary"]
    validated = report["validated_candidates"]
    blocked = [
        item
        for item in validated
        if item["candidate_status"] in {BLOCKED_VALUE, BLOCKED_SLOT, BLOCKED_BOTH}
    ]
    top_blocked = sorted(
        blocked,
        key=lambda item: (-int(item.get("affix_count") or 0), item["legacy_stat_key"]),
    )[:25]
    approved = [
        item for item in validated if item["candidate_status"] == APPROVED
    ]
    lines = [
        "# Forge-Safe Adapter Candidate Validation Review",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Purpose",
        "",
        "This read-only diagnostic validates the one-to-one adapter candidates against existing value-scale and slot-applicability evidence from the real legacy-vs-bundle comparison report. It does not build or enable a runtime adapter.",
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
        "## Validation Rules",
        "",
        "- `approved_for_test_adapter_candidate`: no slot or tier/value blockers in all comparison evidence for the candidate.",
        "- `blocked_by_value_scale`: tier/value differences exist and equivalence is not proven.",
        "- `blocked_by_slot_applicability`: slot/applicability differences exist and equivalence is not proven.",
        "- `blocked_by_both`: both value-scale and slot-applicability blockers exist.",
        "- `needs_manual_review`: comparison evidence is absent, incomplete, or outside the explicit slot/tier policy.",
        "",
        "The classifier does not infer safety from names, tooltips, casing, or likely vocabulary conversions.",
        "",
        "## Status Breakdown",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ])
    for status in STATUSES:
        lines.append(f"| {status} | {report['status_breakdown'][status]} |")

    lines.extend([
        "",
        "## Top Blocked Candidates By Affix Count",
        "",
    ])
    lines.extend(_candidate_table(top_blocked))

    value_blocked = sum(
        1 for item in validated if item["blockers"]["value_scale"]
    )
    slot_blocked = sum(
        1 for item in validated if item["blockers"]["slot_applicability"]
    )
    lines.extend([
        "",
        "## Blocker Summary",
        "",
        f"- Value-scale blocked candidates: {value_blocked}",
        f"- Slot-applicability blocked candidates: {slot_blocked}",
        f"- Approved candidates for future test-only adapter subset: {len(approved)}",
        "",
        "Because existing comparison evidence reports slot and tier/value differences for the matched affixes, one-to-one stat-key shape is not enough to approve candidates for direct use.",
        "",
        "## Migration Implications",
        "",
        "The 560 one-to-one candidates cannot be safely used directly. No production planner, crafting, stat aggregation, simulation, registry, or `/api/ref/affixes` behavior consumes this report.",
        "",
        "The immediate blocker category is shared by slot vocabulary and value-scale evidence. Slot-vocabulary normalization should be addressed first if the goal is to establish item applicability equivalence without touching numerical gameplay values; value-scale normalization should follow as a separate audited policy.",
        "",
        "Recommended next step: produce a read-only slot-vocabulary equivalence report for the candidate affixes, then separately audit value-scale normalization before any feature-flagged adapter prototype is designed.",
    ])
    return "\n".join(lines) + "\n"


def _validate_candidate_metadata(adapter_candidates: dict[str, Any]) -> None:
    metadata = adapter_candidates.get("metadata") or {}
    if metadata.get("read_only") is not True:
        raise ValueError("adapter candidates must be read_only=true")
    if metadata.get("candidate_only") is not True:
        raise ValueError("adapter candidates must be candidate_only=true")
    if metadata.get("production_safe") is not False:
        raise ValueError("adapter candidates must be production_safe=false")


def _comparison_by_legacy_stat_key(
    comparison: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for difference in comparison.get("differences") or []:
        legacy = difference.get("legacy") or {}
        for stat_key in legacy.get("stat_keys") or []:
            if stat_key:
                indexed[str(stat_key)].append(difference)
    return indexed


def _candidate_table(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["No blocked candidates in this category."]
    lines = [
        "| Legacy stat_key | Status | Affixes | Difference types | Examples |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in items:
        examples = ", ".join(str(value) for value in item["example_affix_ids"][:8])
        diff_types = ", ".join(item["evidence"]["difference_types"])
        lines.append(
            f"| `{item['legacy_stat_key']}` | {item['candidate_status']} | {item['affix_count']} | {diff_types} | {examples} |"
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
    report = build_validation_report(
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
        "backend\\scripts\\report_forge_safe_adapter_candidate_validation.py "
        "--adapter-candidates docs\\generated\\forge_safe_adapter_candidates.json "
        "--comparison-report docs\\generated\\forge_safe_legacy_affix_comparison.json "
        "--output docs\\generated\\forge_safe_adapter_candidate_validation.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_ADAPTER_CANDIDATE_VALIDATION_REVIEW.md"
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
