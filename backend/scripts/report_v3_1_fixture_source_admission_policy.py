"""Generate the v3.1 fixture source admission policy report."""

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

from app.planner_adapters.v3_1.fixture_source_admission_policy import evaluate_fixture_source_admission_policy  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_fixture_source_admission_policy_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    reviewed_inputs = _read_json(repo_root / "docs" / "generated" / "v3_1_reviewed_fixture_inputs_report.json")["reviewed_fixture_inputs"]
    admission = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=reviewed_inputs)
    repeated = evaluate_fixture_source_admission_policy(reviewed_fixture_inputs=reviewed_inputs)
    report = {
        "schema_version": "v3_1.fixture_source_admission_policy_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_11_fixture_source_admission_policy",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **admission["summary"],
            "deterministic": admission["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "fixture_source_admission_policy": admission,
        "deterministic_guarantees": {
            "passed": admission["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": admission["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_11_boundaries": [
            "source admission is observational governance metadata only",
            "admitted sources are eligible for governance review only",
            "admitted sources are not production-approved",
            "source admission does not authorize production routing",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_fixture_source_admission_policy_report",
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
    admission = report["fixture_source_admission_policy"]
    summary = report["summary"]
    lines = [
        "# V3.1 Fixture Source Admission Policy",
        "",
        "Phase 11 defines source-level governance admission for reviewed fixture inputs.",
        "Admitted sources are eligible for governance review only and are not production-approved.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total sources evaluated: `{summary['total_sources_evaluated']}`",
        f"- Admitted for review: `{summary['admitted_for_review_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Block Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in admission["block_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Source Evidence", "", "| Source | Type | Status | Records | Reviewed | Unsupported |", "| --- | --- | --- | ---: | ---: | ---: |"])
    for row in admission["source_admission_records"]:
        evidence = row["evidence_summary"]
        lines.append(
            f"| `{row['source_id']}` | `{row['source_type']}` | `{row['admission_status']}` | `{evidence['record_count']}` | `{evidence['reviewed_record_count']}` | `{evidence['unsupported_record_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Recommended Next Governance Action",
            "",
            admission["recommended_next_governance_action"],
            "",
            "## Phase 11 Boundaries",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["phase_11_boundaries"])
    lines.extend(["", "## Conclusion", "", "Fixture source admission is available for governance review, while production routing remains unchanged."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_fixture_source_admission_policy_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_FIXTURE_SOURCE_ADMISSION_POLICY.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_fixture_source_admission_policy_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
