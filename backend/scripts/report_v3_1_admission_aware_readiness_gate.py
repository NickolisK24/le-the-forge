"""Generate the v3.1 admission-aware readiness gate report."""

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

from app.planner_adapters.v3_1.admission_aware_readiness_gate import build_admission_aware_readiness_gate  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_admission_aware_readiness_gate_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    readiness = _read_json(generated / "v3_1_fixture_set_readiness_gate_report.json")["fixture_set_readiness_gate"]
    policy = _read_json(generated / "v3_1_admission_aware_policy_evaluation_report.json")["admission_aware_policy_evaluation"]
    reviewed_inputs = _read_json(generated / "v3_1_reviewed_fixture_inputs_report.json")["reviewed_fixture_inputs"]
    fixture_sets = _read_json(generated / "v3_1_persisted_fixture_sets_report.json")["persisted_fixture_sets"]
    gate = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=readiness,
        admission_aware_policy_evaluation=policy,
        reviewed_fixture_inputs=reviewed_inputs,
        persisted_fixture_sets=fixture_sets,
    )
    repeated = build_admission_aware_readiness_gate(
        fixture_set_readiness_gate=readiness,
        admission_aware_policy_evaluation=policy,
        reviewed_fixture_inputs=reviewed_inputs,
        persisted_fixture_sets=fixture_sets,
    )
    report = {
        "schema_version": "v3_1.admission_aware_readiness_gate_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_13_admission_aware_readiness_gate",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **gate["summary"],
            "deterministic": gate["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "admission_aware_readiness_gate": gate,
        "deterministic_guarantees": {
            "passed": gate["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": gate["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_13_boundaries": [
            "admission-aware readiness is observational governance metadata only",
            "ready_for_approval_review is not production approval",
            "admission-aware readiness does not authorize production routing",
            "remaining non-policy blockers stay visible",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_admission_aware_readiness_gate_report",
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
    gate = report["admission_aware_readiness_gate"]
    summary = report["summary"]
    lines = [
        "# V3.1 Admission-Aware Readiness Gate",
        "",
        "Phase 13 re-evaluates readiness after source admission and admission-aware policy review.",
        "Ready-for-approval-review records are not production approvals and do not authorize routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Ready for approval review: `{summary['ready_for_approval_review_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in gate["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Readiness Reclassification", "", "| Reclassification | Count |", "| --- | ---: |"])
    for item, count in gate["readiness_reclassification_summary"].items():
        lines.append(f"| `{item}` | `{count}` |")
    lines.extend(["", "## Admission-Aware Records", "", "| Record | Fixture Set | Original | Policy | Final |", "| --- | --- | --- | --- | --- |"])
    for row in gate["admission_aware_readiness_records"]:
        lines.append(
            f"| `{row['admission_aware_readiness_id']}` | `{row['fixture_set_id']}` | `{row['original_readiness_status']}` | `{row['admission_aware_policy_status'] or ''}` | `{row['final_admission_aware_readiness_status']}` |"
        )
    lines.extend(["", "## Phase 13 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_13_boundaries"])
    lines.extend(["", "## Conclusion", "", "Admission-aware readiness is available for governance review, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_admission_aware_readiness_gate_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_ADMISSION_AWARE_READINESS_GATE.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_admission_aware_readiness_gate_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
