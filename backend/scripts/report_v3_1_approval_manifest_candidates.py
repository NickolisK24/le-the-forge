"""Generate the v3.1 approval manifest candidate report."""

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

from app.planner_adapters.v3_1.approval_manifest_candidates import build_approval_manifest_candidates  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_approval_manifest_candidates_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    readiness = _read_json(repo_root / "docs" / "generated" / "v3_1_fixture_set_readiness_gate_report.json")["fixture_set_readiness_gate"]
    candidates = build_approval_manifest_candidates(readiness_gate=readiness)
    repeated = build_approval_manifest_candidates(readiness_gate=readiness)
    report = {
        "schema_version": "v3_1.approval_manifest_candidates_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_8_approval_manifest_candidates",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **candidates["summary"],
            "deterministic": candidates["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "approval_manifest_candidates": candidates,
        "deterministic_guarantees": {
            "passed": candidates["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": candidates["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_8_boundaries": [
            "manifest candidates are observational governance artifacts",
            "manifest candidates do not authorize production routing",
            "candidate_ready does not mean production-approved",
            "trusted infrastructure is still not production default",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_approval_manifest_candidates_report",
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
    candidates = report["approval_manifest_candidates"]
    lines = [
        "# V3.1 Approval Manifest Candidates",
        "",
        "Phase 8 introduces deterministic approval manifest candidate generation from readiness-approved fixture sets.",
        "Candidates do not authorize production planner routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total readiness records evaluated: `{summary['total_readiness_records_evaluated']}`",
        f"- Candidate ready: `{summary['candidate_ready_count']}`",
        f"- Excluded: `{summary['excluded_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Exclusion Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in candidates["exclusion_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Manifest Candidates", "", "| Candidate | Fixture Set | Status | Production Approved |", "| --- | --- | --- | --- |"])
    for row in candidates["manifest_candidates"]:
        lines.append(
            f"| `{row['manifest_candidate_id']}` | `{row['fixture_set_id']}` | `{row['candidate_status']}` | `{str(row['authorization_status']['candidate_is_production_approved']).lower()}` |"
        )
    lines.extend(["", "## Phase 8 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_8_boundaries"])
    lines.extend(["", "## Conclusion", "", "Approval manifest candidates are available for governance review, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_approval_manifest_candidates_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_APPROVAL_MANIFEST_CANDIDATES.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_approval_manifest_candidates_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
