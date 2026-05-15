"""Generate the v3.1 review policy evaluation report."""

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

from app.planner_adapters.v3_1.review_policy_evaluation import (  # noqa: E402
    V31ReviewPolicyEvaluation,
    build_sample_review_policy_inputs,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_review_policy_evaluation_report() -> dict[str, Any]:
    fixture_sets = build_sample_review_policy_inputs()
    evaluation = V31ReviewPolicyEvaluation().evaluate(persisted_fixture_sets=fixture_sets)
    repeated = V31ReviewPolicyEvaluation().evaluate(persisted_fixture_sets=fixture_sets)
    deterministic = evaluation["deterministic_hash"] == repeated["deterministic_hash"]
    report = {
        "schema_version": "v3_1.review_policy_evaluation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_5_review_policy_evaluation",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **evaluation["summary"],
            "deterministic": deterministic,
        },
        "review_policy_evaluation": evaluation,
        "deterministic_guarantees": {
            "passed": deterministic,
            "sample_hash": evaluation["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
            "stable_policy_generation_token": evaluation["metadata"]["stable_policy_generation_token"],
        },
        "phase_5_boundaries": [
            "workflows remain observational only",
            "trusted infrastructure is still not production default",
            "policy evaluation does not authorize runtime routing",
            "unsupported and blocked states remain intentionally visible",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_review_policy_evaluation_report",
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
        "# V3.1 Review Policy Evaluation",
        "",
        "Phase 5 introduces deterministic review policy evaluation infrastructure.",
        "Policy evaluation is governance metadata only and does not authorize production routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total evaluations: `{summary['total_evaluations']}`",
        f"- Policy pass: `{summary['policy_pass_count']}`",
        f"- Requires review: `{summary['requires_review_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Unsupported: `{summary['unsupported_count']}`",
        f"- Insufficient data: `{summary['insufficient_data_count']}`",
        f"- Not evaluated: `{summary['not_evaluated_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Policy Evaluations",
        "",
        "| Fixture Set | Lifecycle | Outcome | Production Affected |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["review_policy_evaluation"]["evaluations"]:
        lines.append(
            f"| `{row['fixture_set_id']}` | `{row['lifecycle_state']}` | `{row['policy_outcome']}` | `{str(row['production_output_affected']).lower()}` |"
        )
    lines.extend(["", "## Phase 5 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_5_boundaries"])
    lines.extend(["", "## Conclusion", "", "Review policy evaluation is available for migration governance, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_review_policy_evaluation_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_REVIEW_POLICY_EVALUATION.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_review_policy_evaluation_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
