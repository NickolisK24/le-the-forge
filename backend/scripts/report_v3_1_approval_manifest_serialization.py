"""Generate the v3.1 approval manifest serialization and diff audit report."""

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

from app.planner_adapters.v3_1.approval_manifest_diff_audit import audit_approval_manifest_diffs  # noqa: E402
from app.planner_adapters.v3_1.approval_manifest_serialization import serialize_approval_manifest_candidates  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_approval_manifest_serialization_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    candidates = _read_json(repo_root / "docs" / "generated" / "v3_1_approval_manifest_candidates_report.json")[
        "approval_manifest_candidates"
    ]
    serialization = serialize_approval_manifest_candidates(approval_manifest_candidates=candidates)
    repeated = serialize_approval_manifest_candidates(approval_manifest_candidates=candidates)
    diff_audit = audit_approval_manifest_diffs(before=serialization, after=repeated)
    report = {
        "schema_version": "v3_1.approval_manifest_serialization_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_9_approval_manifest_serialization_diff_audit",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            **serialization["summary"],
            "diff_record_count": diff_audit["diff_summary"]["total_diffs_evaluated"],
            "blocked_high_risk_count": diff_audit["diff_summary"]["blocked_high_risk_count"],
            "deterministic": serialization["deterministic_hash"] == repeated["deterministic_hash"]
            and diff_audit["diff_summary"]["blocked_high_risk_count"] == 0,
        },
        "approval_manifest_serialization": serialization,
        "approval_manifest_diff_audit": diff_audit,
        "deterministic_guarantees": {
            "passed": serialization["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": serialization["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "diff_audit_hash": diff_audit["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_9_boundaries": [
            "serialized manifests are observational governance artifacts",
            "serialized manifests do not authorize production routing",
            "every serialized manifest is non-production authoritative",
            "authorization-state changes are surfaced as blocked high-risk diffs",
            "trusted infrastructure is still not production default",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_approval_manifest_serialization_report",
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
    serialization = report["approval_manifest_serialization"]
    diff_audit = report["approval_manifest_diff_audit"]
    lines = [
        "# V3.1 Approval Manifest Serialization",
        "",
        "Phase 9 serializes approval manifest candidates into deterministic, inspectable governance artifacts.",
        "Serialized manifests remain non-authoritative and do not authorize production planner routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Total candidates evaluated: `{summary['total_candidates_evaluated']}`",
        f"- Serialized manifests: `{summary['serialized_manifest_count']}`",
        f"- Excluded candidates: `{summary['excluded_count']}`",
        f"- Diff records: `{summary['diff_record_count']}`",
        f"- Blocked high-risk diffs: `{summary['blocked_high_risk_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Exclusion Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in serialization["exclusion_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Serialized Manifests", "", "| Manifest | Fixture Set | Authorization State | Production Approved |", "| --- | --- | --- | --- |"])
    for row in serialization["serialized_manifests"]:
        lines.append(
            f"| `{row['manifest_id']}` | `{row['fixture_set_id']}` | `{row['authorization_status']['authorization_state']}` | `{str(row['authorization_status']['manifest_is_production_approved']).lower()}` |"
        )
    lines.extend(["", "## Diff Audit Summary", "", "| Classification | Count |", "| --- | ---: |"])
    for classification, count in diff_audit["classification_counts"].items():
        lines.append(f"| `{classification}` | `{count}` |")
    lines.extend(["", "## Phase 9 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_9_boundaries"])
    lines.extend(["", "## Conclusion", "", "Approval manifest serialization is available for governance review, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_approval_manifest_serialization_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_APPROVAL_MANIFEST_SERIALIZATION.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_approval_manifest_serialization_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
