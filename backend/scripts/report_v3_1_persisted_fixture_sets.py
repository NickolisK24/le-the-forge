"""Generate the v3.1 persisted fixture set report."""

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

from app.planner_adapters.v3_1.persisted_fixture_sets import (  # noqa: E402
    V31PersistedFixtureSets,
    build_sample_persisted_fixture_set_inputs,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_persisted_fixture_sets_report() -> dict[str, Any]:
    workflows = build_sample_persisted_fixture_set_inputs()
    fixture_sets = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)
    repeated = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)
    deterministic = fixture_sets["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.persisted_fixture_sets_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_5_persisted_fixture_sets",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **fixture_sets["summary"],
            "deterministic": deterministic,
        },
        "persisted_fixture_sets": fixture_sets,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": fixture_sets["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
            "stable_fixture_set_generation_token": fixture_sets["metadata"]["stable_fixture_set_generation_token"],
        },
        "phase_5_boundaries": [
            "workflows remain observational only",
            "trusted infrastructure is still not production default",
            "fixture-set membership does not authorize runtime routing",
            "unsupported and blocked states remain intentionally visible",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_persisted_fixture_sets_report",
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
        "# V3.1 Persisted Fixture Sets",
        "",
        "Phase 5 introduces deterministic persisted fixture-set infrastructure.",
        "Fixture sets are migration-readiness groupings only and do not authorize production routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total fixture sets: `{summary['total_fixture_sets']}`",
        f"- Draft: `{summary['draft_count']}`",
        f"- Review ready: `{summary['review_ready_count']}`",
        f"- Partially approved: `{summary['partially_approved_count']}`",
        f"- Approved candidate: `{summary['approved_candidate_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Unsupported: `{summary['unsupported_count']}`",
        f"- Insufficient data: `{summary['insufficient_data_count']}`",
        f"- Policy pass: `{summary['policy_pass_count']}`",
        f"- Requires review: `{summary['requires_review_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Fixture Sets",
        "",
        "| Fixture Set | State | Fixtures | Policy Status | Production Affected |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in report["persisted_fixture_sets"]["fixture_sets"]:
        lines.append(
            f"| `{row['fixture_set_id']}` | `{row['lifecycle_state']}` | `{len(row['associated_fixture_ids'])}` | `{row['policy_evaluation_status']}` | `{str(row['production_output_affected']).lower()}` |"
        )
    lines.extend(["", "## Phase 5 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_5_boundaries"])
    lines.extend(["", "## Conclusion", "", "Persisted fixture sets are available for migration governance, while production routing remains unchanged."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_persisted_fixture_sets_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_PERSISTED_FIXTURE_SETS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_persisted_fixture_sets_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
