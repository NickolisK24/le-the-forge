"""Generate the v3.1 deterministic dual-run comparison report."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v3_1.dual_run_comparison import (  # noqa: E402
    V31DualRunComparison,
    build_sample_dual_run_inputs,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_dual_run_comparison_report() -> dict[str, Any]:
    legacy, trusted_shadow = build_sample_dual_run_inputs()
    comparator = V31DualRunComparison()
    comparison = comparator.compare(
        legacy_summaries=legacy,
        trusted_shadow_metadata=trusted_shadow,
    )
    repeated = comparator.compare(
        legacy_summaries=legacy,
        trusted_shadow_metadata=trusted_shadow,
    )
    deterministic = comparison["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.dual_run_comparison_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_2_deterministic_dual_run_comparison",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **comparison["summary"],
            "deterministic": deterministic,
        },
        "comparison": comparison,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": comparison["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_2_boundaries": [
            "dual-run comparison accepts summaries and shadow metadata only",
            "legacy production output remains the truth source",
            "trusted data is not default production truth",
            "drift visibility is established through explicit classifications",
            "unsupported and blocked states are intentionally surfaced",
        ],
        "metadata": {
            "source": "v3_1_dual_run_comparison_report",
            "observational_only": True,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "planner_remap_performed": False,
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V3.1 Dual-Run Comparison",
        "",
        "Phase 2 introduces deterministic dual-run comparison infrastructure around the trusted shadow layer.",
        "It is observational only; production output remains legacy-owned and trusted data is not default production truth.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total comparisons: `{summary['total_comparisons']}`",
        f"- Equivalent: `{summary['equivalent_count']}`",
        f"- Divergent: `{summary['divergent_count']}`",
        f"- Unsupported: `{summary['unsupported_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Legacy only: `{summary['legacy_only_count']}`",
        f"- Trusted only: `{summary['trusted_only_count']}`",
        f"- Unavailable: `{summary['unavailable_count']}`",
        f"- Not evaluated: `{summary['not_evaluated_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Drift Results",
        "",
        "| Comparison | Legacy | Trusted Shadow | Classification | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["comparison"]["comparison_results"]:
        reason = row["unsupported_or_blocked_reason"] or ",".join(row["reason_codes"])
        lines.append(
            f"| `{row['comparison_id']}` | `{row['legacy_status']}` | `{row['trusted_shadow_status']}` | `{row['drift_classification']}` | `{reason}` |"
        )
    lines.extend(["", "## Phase 2 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_2_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Dual-run drift visibility is now available, but production routing remains unchanged and legacy-owned.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            normalized[key] = DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_dual_run_comparison_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_DUAL_RUN_COMPARISON.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_dual_run_comparison_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
