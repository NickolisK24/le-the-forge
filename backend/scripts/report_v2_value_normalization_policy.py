"""Generate the v2 value normalization policy audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.normalization.v2.value_scale_policy import classify_family, family_key, stat_family

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs" / "generated"
MIGRATION = ROOT / "docs" / "migration"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modifier-registry", type=Path, default=GENERATED / "v2_modifier_registry.json")
    parser.add_argument("--output", type=Path, default=GENERATED / "v2_value_normalization_policy_report.json")
    parser.add_argument("--candidate-output", type=Path, default=GENERATED / "v2_value_normalization_candidate_families.json")
    parser.add_argument("--markdown-output", type=Path, default=MIGRATION / "V2_VALUE_NORMALIZATION_POLICY.md")
    args = parser.parse_args()

    registry = json.loads(args.modifier_registry.read_text(encoding="utf-8"))
    modifiers = registry.get("records", {}).get("modifiers", [])
    report, candidates = build_value_normalization_policy_report(modifiers)
    _write_json(args.output, report)
    _write_json(args.candidate_output, candidates)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown_report(report), encoding="utf-8")
    return 0


def build_value_normalization_policy_report(modifiers: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    generated_on = datetime.now(UTC).isoformat()
    source_units = [row for row in modifiers if row.get("value_scale_status") == "source_units"]
    unknown_scale = [row for row in modifiers if row.get("value_scale_status") == "unknown"]
    family_records = _group_families(modifiers)
    family_reports = [_family_report(key, rows) for key, rows in sorted(family_records.items())]
    candidate_families = [row for row in family_reports if row["policy_status"].startswith("candidate_")]
    safe_families = [row for row in family_reports if row["planner_normalization_safe"]]
    blocked_families = [row for row in family_reports if not row["planner_normalization_safe"] and not row["policy_status"].startswith("candidate_")]
    report = {
        "schema_version": "v2.value_normalization_policy.1",
        "generated_on": generated_on,
        "metadata": {
            "source": "v2_modifier_registry",
            "read_only": True,
            "experimental": True,
            "production_safe": False,
            "production_consumed": False,
            "stable_planner_consumed": False,
        },
        "summary": {
            "total_modifier_count": len(modifiers),
            "source_unit_modifier_count": len(source_units),
            "unknown_scale_modifier_count": len(unknown_scale),
            "family_count": len(family_reports),
            "candidate_family_count": len(candidate_families),
            "safe_family_count": len(safe_families),
            "blocked_family_count": len(blocked_families),
            "planner_normalized_modifier_count": 0,
            "stable_calculable_count_changed": False,
            "production_consumed": False,
        },
        "counts": {
            "source_units_by_source_type": dict(sorted(Counter(row["source_type"] for row in source_units).items())),
            "source_units_by_operation": dict(sorted(Counter(row["operation"] for row in source_units).items())),
            "source_units_by_stat_family": dict(sorted(Counter(stat_family(row["stat_id"]) for row in source_units).items())),
            "unknown_scale_by_source_type": dict(sorted(Counter(row["source_type"] for row in unknown_scale).items())),
            "unknown_scale_by_operation": dict(sorted(Counter(row["operation"] for row in unknown_scale).items())),
            "unknown_scale_by_stat_family": dict(sorted(Counter(stat_family(row["stat_id"]) for row in unknown_scale).items())),
        },
        "candidate_normalization_families": sorted(candidate_families, key=lambda row: row["modifier_count"], reverse=True),
        "safe_normalization_families": sorted(safe_families, key=lambda row: row["modifier_count"], reverse=True),
        "blocked_families": sorted(blocked_families, key=lambda row: row["modifier_count"], reverse=True),
        "unsafe_policy_notes": [
            "No broad/global scale factor is applied.",
            "Existing planner code expects percent-points for many percentage calculations, but v2 source rows do not prove which source-unit values should be multiplied or left unchanged.",
            "Flat, duration, cooldown, and cost families may already be in planner-like units for some sources, but this is not asserted without source contract or baseline evidence.",
            "Percent-like source-unit families remain candidates for source validation, not planner-normalized rows.",
        ],
    }
    candidates = {
        "schema_version": "v2.value_normalization_candidate_families.1",
        "generated_on": generated_on,
        "metadata": report["metadata"],
        "summary": {
            "candidate_family_count": len(candidate_families),
            "safe_family_count": len(safe_families),
            "production_consumed": False,
        },
        "candidate_families": report["candidate_normalization_families"],
    }
    return report, candidates


def _group_families(modifiers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in modifiers:
        grouped[family_key(row)].append(row)
    return grouped


def _family_report(key: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    decision = classify_family(rows)
    source_type, operation, family = key.split("|", 2)
    values = [_numeric(row.get("raw_value_min")) for row in rows] + [_numeric(row.get("raw_value_max")) for row in rows]
    values = [value for value in values if value is not None]
    return {
        "family_key": key,
        "source_type": source_type,
        "operation": operation,
        "stat_family": family,
        "modifier_count": len(rows),
        "value_scale_counts": dict(sorted(Counter(str(row.get("value_scale_status") or "unknown") for row in rows).items())),
        "stat_id_count": len({str(row.get("stat_id")) for row in rows}),
        "example_stat_ids": sorted({str(row.get("stat_id")) for row in rows})[:10],
        "raw_value_min": min(values) if values else None,
        "raw_value_max": max(values) if values else None,
        "policy_status": decision["policy_status"],
        "planner_normalization_safe": decision["planner_normalization_safe"],
        "proposed_scale_factor": decision["proposed_scale_factor"],
        "evidence_type": decision["evidence_type"],
        "confidence": decision["confidence"],
        "blocked_reasons": decision["blocked_reasons"],
        "example_records": _examples(rows),
    }


def _examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "canonical_modifier_id": row.get("canonical_modifier_id"),
            "source_type": row.get("source_type"),
            "source_id": row.get("source_id"),
            "source_display_name": row.get("source_display_name"),
            "stat_id": row.get("stat_id"),
            "operation": row.get("operation"),
            "raw_value_min": row.get("raw_value_min"),
            "raw_value_max": row.get("raw_value_max"),
            "value_scale_status": row.get("value_scale_status"),
        }
        for row in rows[:5]
    ]


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _top_rows(counts: dict[str, int], limit: int = 10) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]


def _markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    counts = report["counts"]
    candidates = report["candidate_normalization_families"][:10]
    blocked = report["blocked_families"][:10]
    lines = [
        "# V2 Value Normalization Policy",
        "",
        "## Purpose",
        "",
        "This Phase 10.5 audit reviews source-unit and unknown-scale v2 modifier rows before any planner adapter consumes them. It does not change production planner, stat aggregation, crafting, or simulation behavior.",
        "",
        "## Generation command",
        "",
        "```powershell",
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_value_normalization_policy.py --modifier-registry docs\\generated\\v2_modifier_registry.json --output docs\\generated\\v2_value_normalization_policy_report.json --candidate-output docs\\generated\\v2_value_normalization_candidate_families.json --markdown-output docs\\migration\\V2_VALUE_NORMALIZATION_POLICY.md",
        "```",
        "",
        "## Summary",
        "",
        f"- Total modifiers: `{summary['total_modifier_count']}`",
        f"- Source-unit modifiers: `{summary['source_unit_modifier_count']}`",
        f"- Unknown-scale modifiers: `{summary['unknown_scale_modifier_count']}`",
        f"- Candidate families needing source validation: `{summary['candidate_family_count']}`",
        f"- Safe normalization families: `{summary['safe_family_count']}`",
        f"- Blocked families: `{summary['blocked_family_count']}`",
        f"- Stable-calculable count changed: `{str(summary['stable_calculable_count_changed']).lower()}`",
        "",
        "## Top Source-Unit Source Types",
        "",
    ]
    for label, count in _top_rows(counts["source_units_by_source_type"]):
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(["", "## Top Source-Unit Operations", ""])
    for label, count in _top_rows(counts["source_units_by_operation"]):
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(["", "## Top Source-Unit Stat Families", ""])
    for label, count in _top_rows(counts["source_units_by_stat_family"]):
        lines.append(f"- `{label}`: `{count}`")
    lines.extend(["", "## Candidate Families", ""])
    if candidates:
        for row in candidates:
            lines.append(f"- `{row['family_key']}`: `{row['modifier_count']}` rows, `{row['policy_status']}`, confidence `{row['confidence']}`")
    else:
        lines.append("- None.")
    lines.extend(["", "## Blocked Families", ""])
    for row in blocked:
        lines.append(f"- `{row['family_key']}`: `{row['modifier_count']}` rows, reasons `{', '.join(row['blocked_reasons'])}`")
    lines.extend(
        [
            "",
            "## Policy Conclusion",
            "",
            "No family is promoted to planner-normalized in this audit. Existing planner code documents percent-point inputs, but that is not enough to prove how every v2 source-unit family should be scaled. Broad rules such as multiplying every `increased` or `chance` value by 100 are explicitly unsafe until backed by source contracts or golden planner baselines.",
            "",
            "## Phase 11 Guidance",
            "",
            "Future phases may consume this policy for debug and planning. Stable planner consumption must still require trusted support status, known stat IDs, known operations, resolved source identity, non-special behavior, and explicit value-scale evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
