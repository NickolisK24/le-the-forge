"""Generate the v3.1 admission-aware policy evaluation report."""

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

from app.planner_adapters.v3_1.admission_aware_policy_evaluation import build_admission_aware_policy_evaluation  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_admission_aware_policy_evaluation_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    admission = _read_json(generated / "v3_1_fixture_source_admission_policy_report.json")["fixture_source_admission_policy"]
    reviewed_inputs = _read_json(generated / "v3_1_reviewed_fixture_inputs_report.json")["reviewed_fixture_inputs"]
    policy = _read_json(generated / "v3_1_review_policy_evaluation_report.json")["review_policy_evaluation"]
    evaluation = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=admission,
        reviewed_fixture_inputs=reviewed_inputs,
        review_policy_evaluation=policy,
    )
    repeated = build_admission_aware_policy_evaluation(
        fixture_source_admission_policy=admission,
        reviewed_fixture_inputs=reviewed_inputs,
        review_policy_evaluation=policy,
    )
    report = {
        "schema_version": "v3_1.admission_aware_policy_evaluation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_12_admission_aware_policy_evaluation",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **evaluation["summary"],
            "deterministic": evaluation["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "admission_aware_policy_evaluation": evaluation,
        "deterministic_guarantees": {
            "passed": evaluation["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": evaluation["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_12_boundaries": [
            "admission-aware policy evaluation is observational governance metadata only",
            "policy_satisfied_for_review is not production approval",
            "admission-aware policy does not authorize production routing",
            "non-source policy failures remain visible",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_admission_aware_policy_evaluation_report",
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
    evaluation = report["admission_aware_policy_evaluation"]
    summary = report["summary"]
    lines = [
        "# V3.1 Admission-Aware Policy Evaluation",
        "",
        "Phase 12 lets governance policy evaluation account for fixture source admission.",
        "Satisfied-for-review records are not production approvals and do not authorize routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Satisfied for review: `{summary['satisfied_for_review_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in evaluation["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Source Admission Impact", "", "| Impact | Count |", "| --- | ---: |"])
    for impact, count in evaluation["source_admission_impact_summary"].items():
        lines.append(f"| `{impact}` | `{count}` |")
    lines.extend(["", "## Admission-Aware Records", "", "| Record | Fixture Set | Source | Original Policy | Admission | Status |", "| --- | --- | --- | --- | --- | --- |"])
    for row in evaluation["admission_aware_policy_records"]:
        lines.append(
            f"| `{row['admission_aware_policy_id']}` | `{row['fixture_set_id'] or ''}` | `{row['source_id'] or ''}` | `{row['original_policy_status']}` | `{row['admission_status'] or ''}` | `{row['admission_aware_policy_status']}` |"
        )
    lines.extend(["", "## Phase 12 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_12_boundaries"])
    lines.extend(["", "## Conclusion", "", "Admission-aware policy evaluation is available for governance review, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_admission_aware_policy_evaluation_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_ADMISSION_AWARE_POLICY_EVALUATION.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_admission_aware_policy_evaluation_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
