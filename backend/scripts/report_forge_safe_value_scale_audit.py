"""Audit value-scale evidence for slot-policy-approved Forge-safe candidates."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SLOT_POLICY = ROOT / "docs" / "generated" / "forge_safe_slot_vocabulary_policy.json"
DEFAULT_COMPARISON_REPORT = (
    ROOT / "docs" / "generated" / "forge_safe_legacy_affix_comparison.json"
)
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "forge_safe_value_scale_audit.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "FORGE_SAFE_VALUE_SCALE_AUDIT.md"

STRUCTURAL = "structurally_equivalent"
SCALE = "consistent_scale_factor"
POLARITY = "polarity_difference"
MIN_MAX = "min_max_shape_difference"
TIER_COUNT = "tier_count_difference"
MALFORMED = "malformed_or_missing_values"
NEEDS_REVIEW = "needs_manual_review"
STATUSES = [STRUCTURAL, SCALE, POLARITY, MIN_MAX, TIER_COUNT, MALFORMED, NEEDS_REVIEW]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit value-scale evidence for approved slot-policy candidates."
    )
    parser.add_argument("--slot-policy", type=Path, default=DEFAULT_SLOT_POLICY)
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


def build_value_scale_audit(
    slot_policy: dict[str, Any],
    comparison: dict[str, Any],
    *,
    slot_policy_path: str,
    comparison_report_path: str,
) -> dict[str, Any]:
    _validate_slot_policy(slot_policy)
    rows_by_stat_key = _comparison_by_legacy_stat_key(comparison)
    statuses = [
        audit_candidate(candidate, rows_by_stat_key)
        for candidate in slot_policy.get("policy_approved_candidates") or []
    ]
    excluded = [
        {
            "legacy_stat_key": candidate.get("legacy_stat_key"),
            "reason": "slot_policy_blocked",
            "affix_count": candidate.get("affix_count", 0),
            "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        }
        for candidate in slot_policy.get("blocked_candidates") or []
    ]
    counts = Counter(item["value_status"] for item in statuses)
    future_count = sum(1 for item in statuses if item["future_test_adapter_candidate"])
    summary = {
        "slot_policy_approved_candidate_count": len(slot_policy.get("policy_approved_candidates") or []),
        "audited_candidate_count": len(statuses),
        "excluded_slot_blocked_candidate_count": len(excluded),
        "structurally_equivalent_count": counts[STRUCTURAL],
        "consistent_scale_factor_count": counts[SCALE],
        "polarity_difference_count": counts[POLARITY],
        "min_max_shape_difference_count": counts[MIN_MAX],
        "tier_count_difference_count": counts[TIER_COUNT],
        "malformed_or_missing_values_count": counts[MALFORMED],
        "needs_manual_review_count": counts[NEEDS_REVIEW],
        "future_test_adapter_candidate_count": future_count,
        "production_consumed": False,
    }

    return {
        "summary": summary,
        "value_status_breakdown": {status: counts[status] for status in STATUSES},
        "scale_factor_breakdown": _scale_factor_breakdown(statuses),
        "value_scale_statuses": sorted(
            statuses,
            key=lambda item: (item["value_status"], item["legacy_stat_key"]),
        ),
        "excluded_candidates": excluded,
        "metadata": {
            "source": "forge_safe_slot_vocabulary_policy + forge_safe_legacy_affix_comparison",
            "slot_policy_source": slot_policy_path,
            "comparison_report_source": comparison_report_path,
            "read_only": True,
            "candidate_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "consumption_status": "not_consumed",
            "classification_policy": "deterministic_tier_min_max_evidence_only",
        },
    }


def audit_candidate(
    candidate: dict[str, Any],
    rows_by_stat_key: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    legacy_stat_key = str(candidate.get("legacy_stat_key") or "")
    rows = rows_by_stat_key.get(legacy_stat_key, [])
    affix_results = [classify_affix_values(row) for row in rows]
    value_status, scale_factor, blockers, notes = combine_affix_results(affix_results)
    future = (
        value_status in {STRUCTURAL, SCALE}
        and not blockers
        and bool(rows)
    )
    return {
        "legacy_stat_key": legacy_stat_key,
        "value_status": value_status,
        "affix_count": candidate.get("affix_count", len(rows)),
        "example_affix_ids": list(candidate.get("example_affix_ids") or []),
        "comparison_affix_ids": [_coerce_affix_id(row.get("affix_id")) for row in rows],
        "scale_factor": str(scale_factor) if scale_factor is not None else None,
        "tier_count_legacy": _shared_tier_count(rows, "legacy"),
        "tier_count_bundle": _shared_tier_count(rows, "bundle"),
        "blockers": blockers,
        "future_test_adapter_candidate": future,
        "notes": notes,
        "consumption_status": "not_consumed",
    }


def classify_affix_values(row: dict[str, Any]) -> dict[str, Any]:
    legacy = row.get("legacy") or {}
    bundle = row.get("bundle") or {}
    affix_id = _coerce_affix_id(row.get("affix_id"))
    if legacy.get("has_malformed_tiers") or bundle.get("has_malformed_tiers"):
        return _affix_result(affix_id, MALFORMED, "Malformed tier signal is present.")

    legacy_tiers = legacy.get("tiers")
    bundle_tiers = bundle.get("tiers")
    if not isinstance(legacy_tiers, list) or not isinstance(bundle_tiers, list):
        return _affix_result(affix_id, MALFORMED, "Tier min/max arrays are missing from comparison evidence.")
    if not legacy_tiers or not bundle_tiers:
        return _affix_result(affix_id, MALFORMED, "Tier min/max arrays are empty.")
    if len(legacy_tiers) != len(bundle_tiers):
        return _affix_result(affix_id, TIER_COUNT, "Legacy and bundle tier counts differ.")

    pairs = []
    for legacy_tier, bundle_tier in zip(legacy_tiers, bundle_tiers):
        if legacy_tier.get("tier") != bundle_tier.get("tier"):
            return _affix_result(affix_id, MIN_MAX, "Tier numbers differ.")
        for field in ("min", "max"):
            legacy_value = _decimal_or_none(legacy_tier.get(field))
            bundle_value = _decimal_or_none(bundle_tier.get(field))
            if legacy_value is None or bundle_value is None:
                return _affix_result(affix_id, MALFORMED, "Tier min/max value is missing or non-numeric.")
            pairs.append((legacy_value, bundle_value))

    if all(legacy_value == bundle_value for legacy_value, bundle_value in pairs):
        return _affix_result(affix_id, STRUCTURAL, "Tier min/max values match exactly.")
    if all(legacy_value != 0 and bundle_value == -legacy_value for legacy_value, bundle_value in pairs):
        return _affix_result(affix_id, POLARITY, "Tier values differ by polarity/sign.")

    factor = _consistent_scale_factor(pairs)
    if factor is not None:
        return _affix_result(
            affix_id,
            SCALE,
            "Tier min/max values differ by a consistent scale factor.",
            scale_factor=factor,
        )

    return _affix_result(affix_id, MIN_MAX, "Tier min/max shape is not exact, polarity-only, or a consistent scale factor.")


def combine_affix_results(results: list[dict[str, Any]]) -> tuple[str, Decimal | None, list[str], list[str]]:
    if not results:
        return NEEDS_REVIEW, None, ["No comparison evidence was found."], ["Candidate requires manual review."]
    statuses = {result["status"] for result in results}
    if len(statuses) > 1:
        return NEEDS_REVIEW, None, ["Candidate affixes have mixed value-scale statuses."], _result_notes(results)
    status = next(iter(statuses))
    scale_factor = None
    if status == SCALE:
        factors = {result.get("scale_factor") for result in results}
        if len(factors) != 1:
            return NEEDS_REVIEW, None, ["Candidate affixes have inconsistent scale factors."], _result_notes(results)
        scale_factor = next(iter(factors))
    blockers = []
    if status not in {STRUCTURAL, SCALE}:
        blockers.append(_status_blocker(status))
    return status, scale_factor, blockers, _result_notes(results)


def render_markdown(report: dict[str, Any], *, slot_policy_path: Path, comparison_report_path: Path, command: str) -> str:
    summary = report["summary"]
    statuses = report["value_scale_statuses"]
    future = [item for item in statuses if item["future_test_adapter_candidate"]]
    blocked = [item for item in statuses if not item["future_test_adapter_candidate"]]
    lines = [
        "# Forge-Safe Value Scale Audit",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Purpose",
        "",
        "This read-only audit checks value-scale and tier evidence for the slot-policy-approved Forge-safe adapter candidates. It excludes slot-blocked candidates such as `health_on_kill` and does not build or enable a runtime adapter.",
        "",
        "## Sources",
        "",
        f"- Slot policy: `{slot_policy_path}`",
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
        "## Excluded Candidates",
        "",
        "`health_on_kill` is excluded because the slot vocabulary policy keeps it blocked by inconsistent applicability evidence.",
        "",
        "## Value Status Breakdown",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ])
    for status, count in report["value_status_breakdown"].items():
        lines.append(f"| {status} | {count} |")

    lines.extend([
        "",
        "## Scale Factor Breakdown",
        "",
    ])
    if report["scale_factor_breakdown"]:
        lines.extend(["| Scale factor | Count |", "| --- | ---: |"])
        for item in report["scale_factor_breakdown"]:
            lines.append(f"| `{item['scale_factor']}` | {item['candidate_count']} |")
    else:
        lines.append("No deterministic scale factors were proven.")

    lines.extend([
        "",
        "## Future Test Adapter Candidates",
        "",
    ])
    lines.extend(_status_table(future[:25]))
    lines.extend([
        "",
        "## Top Blocked Candidates By Affix Count",
        "",
    ])
    lines.extend(_status_table(sorted(blocked, key=lambda item: (-int(item.get("affix_count") or 0), item["legacy_stat_key"]))[:25]))
    lines.extend([
        "",
        "## Migration Implications",
        "",
        "The current comparison report does not include tier min/max arrays, so value-scale equivalence cannot be proven for the slot-policy-approved candidates. This is evidence to write a value normalization policy/report that preserves full tier min/max data before any adapter prototype.",
        "",
        "Recommended next task: extend or regenerate diagnostics to preserve tier min/max evidence, then document a value normalization policy before any test-only adapter subset design.",
    ])
    return "\n".join(lines) + "\n"


def _validate_slot_policy(slot_policy: dict[str, Any]) -> None:
    metadata = slot_policy.get("metadata") or {}
    if metadata.get("read_only") is not True:
        raise ValueError("slot policy must be read_only=true")
    if metadata.get("candidate_only") is not True:
        raise ValueError("slot policy must be candidate_only=true")
    if metadata.get("production_safe") is not False:
        raise ValueError("slot policy must be production_safe=false")


def _comparison_by_legacy_stat_key(comparison: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for difference in comparison.get("differences") or []:
        legacy = difference.get("legacy") or {}
        for stat_key in legacy.get("stat_keys") or []:
            if stat_key:
                indexed[str(stat_key)].append(difference)
    return indexed


def _consistent_scale_factor(pairs: list[tuple[Decimal, Decimal]]) -> Decimal | None:
    factors = set()
    for legacy_value, bundle_value in pairs:
        if legacy_value == 0:
            if bundle_value != 0:
                return None
            continue
        if _sign(legacy_value) != _sign(bundle_value):
            return None
        factors.add(bundle_value / legacy_value)
    if len(factors) == 1:
        return next(iter(factors)).normalize()
    return None


def _shared_tier_count(rows: list[dict[str, Any]], side: str) -> int | None:
    counts = {
        (row.get(side) or {}).get("tier_count")
        for row in rows
        if (row.get(side) or {}).get("tier_count") is not None
    }
    if len(counts) == 1:
        return int(next(iter(counts)))
    return None


def _decimal_or_none(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _sign(value: Decimal) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _affix_result(affix_id: int | str, status: str, note: str, *, scale_factor: Decimal | None = None) -> dict[str, Any]:
    return {
        "affix_id": affix_id,
        "status": status,
        "note": note,
        "scale_factor": scale_factor,
    }


def _status_blocker(status: str) -> str:
    return {
        POLARITY: "Polarity/sign differs.",
        MIN_MAX: "Tier min/max shape differs.",
        TIER_COUNT: "Tier counts differ.",
        MALFORMED: "Tier values are malformed, missing, or not comparable.",
        NEEDS_REVIEW: "Value evidence needs manual review.",
    }.get(status, "Value evidence is blocked.")


def _result_notes(results: list[dict[str, Any]]) -> list[str]:
    return [
        f"affix {result['affix_id']}: {result['note']}"
        for result in results[:10]
    ]


def _scale_factor_breakdown(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(
        item["scale_factor"]
        for item in statuses
        if item["value_status"] == SCALE and item.get("scale_factor") is not None
    )
    return [
        {"scale_factor": factor, "candidate_count": count}
        for factor, count in sorted(counts.items())
    ]


def _status_table(items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["No candidates in this category."]
    lines = [
        "| Legacy stat_key | Status | Affixes | Scale factor | Examples |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in items:
        examples = ", ".join(str(value) for value in item["example_affix_ids"][:8])
        scale = item.get("scale_factor") or ""
        lines.append(
            f"| `{item['legacy_stat_key']}` | {item['value_status']} | {item['affix_count']} | {scale} | {examples} |"
        )
    return lines


def _coerce_affix_id(value: Any) -> int | str:
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value)


def main() -> int:
    args = parse_args()
    slot_policy = load_json(args.slot_policy)
    comparison = load_comparison(args.comparison_report)
    report = build_value_scale_audit(
        slot_policy,
        comparison,
        slot_policy_path=str(args.slot_policy),
        comparison_report_path=str(args.comparison_report),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe "
        "backend\\scripts\\report_forge_safe_value_scale_audit.py "
        "--slot-policy docs\\generated\\forge_safe_slot_vocabulary_policy.json "
        "--comparison-report docs\\generated\\forge_safe_legacy_affix_comparison.json "
        "--output docs\\generated\\forge_safe_value_scale_audit.json "
        "--markdown-output docs\\migration\\FORGE_SAFE_VALUE_SCALE_AUDIT.md"
    )
    args.markdown_output.write_text(
        render_markdown(
            report,
            slot_policy_path=args.slot_policy,
            comparison_report_path=args.comparison_report,
            command=command,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"summary": report["summary"], "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
