"""Generate the v3.1 admission-aware manifest candidate refresh report."""

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

from app.planner_adapters.v3_1.admission_aware_manifest_candidates import build_admission_aware_manifest_candidates  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_admission_aware_manifest_candidates_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    readiness = _read_json(generated / "v3_1_admission_aware_readiness_gate_report.json")["admission_aware_readiness_gate"]
    original = _read_json(generated / "v3_1_approval_manifest_candidates_report.json")["approval_manifest_candidates"]
    candidates = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=readiness,
        approval_manifest_candidates=original,
    )
    repeated = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=readiness,
        approval_manifest_candidates=original,
    )
    report = {
        "schema_version": "v3_1.admission_aware_manifest_candidates_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_14_admission_aware_manifest_candidates",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **candidates["summary"],
            "deterministic": candidates["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "admission_aware_manifest_candidates": candidates,
        "deterministic_guarantees": {
            "passed": candidates["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": candidates["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_14_boundaries": [
            "admission-aware candidates are observational governance artifacts",
            "candidate_ready is not production approval",
            "candidate_ready does not authorize production routing",
            "candidates are explicitly non-production-authoritative",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_admission_aware_manifest_candidates_report",
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
    candidates = report["admission_aware_manifest_candidates"]
    summary = report["summary"]
    lines = [
        "# V3.1 Admission-Aware Manifest Candidates",
        "",
        "Phase 14 refreshes manifest candidates from admission-aware readiness results.",
        "Candidate-ready records are not production approvals and do not authorize routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Admission-aware readiness records evaluated: `{summary['admission_aware_readiness_records_evaluated']}`",
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
    lines.extend(["", "## Candidate Refresh Summary", "", "| Refresh | Count |", "| --- | ---: |"])
    for item, count in candidates["candidate_refresh_summary"].items():
        lines.append(f"| `{item}` | `{count}` |")
    lines.extend(["", "## Original Vs Admission-Aware", "", "| Comparison | Count |", "| --- | ---: |"])
    for item, count in candidates["original_vs_admission_aware_comparison"].items():
        lines.append(f"| `{item}` | `{count}` |")
    lines.extend(["", "## Refreshed Candidates", "", "| Candidate | Fixture Set | Original | Refreshed | Reclassification |", "| --- | --- | --- | --- | --- |"])
    for row in candidates["manifest_candidates"]:
        lines.append(
            f"| `{row['manifest_candidate_id']}` | `{row['fixture_set_id']}` | `{row['original_candidate_status'] or ''}` | `{row['candidate_status']}` | `{row['readiness_reclassification'] or ''}` |"
        )
    lines.extend(["", "## Phase 14 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_14_boundaries"])
    lines.extend(["", "## Conclusion", "", "Admission-aware manifest candidates are available for governance review, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_admission_aware_manifest_candidates_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_ADMISSION_AWARE_MANIFEST_CANDIDATES.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_admission_aware_manifest_candidates_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
