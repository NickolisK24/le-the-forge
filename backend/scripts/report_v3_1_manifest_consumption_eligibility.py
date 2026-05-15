"""Generate the v3.1 manifest consumption eligibility report."""

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

from app.planner_adapters.v3_1.manifest_consumption_eligibility import evaluate_manifest_consumption_eligibility  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_manifest_consumption_eligibility_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    serialization = _read_json(repo_root / "docs" / "generated" / "v3_1_admission_aware_manifest_serialization_report.json")[
        "admission_aware_manifest_serialization"
    ]
    eligibility = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=serialization)
    repeated = evaluate_manifest_consumption_eligibility(admission_aware_manifest_serialization=serialization)
    report = {
        "schema_version": "v3_1.manifest_consumption_eligibility_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_16_manifest_consumption_eligibility",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "controlled_test_consumption_only": True,
        "summary": {
            **eligibility["summary"],
            "deterministic": eligibility["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "manifest_consumption_eligibility": eligibility,
        "deterministic_guarantees": {
            "passed": eligibility["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": eligibility["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_16_boundaries": [
            "eligibility is for controlled test consumption only",
            "eligibility does not authorize production routing",
            "eligible manifests are not production approvals",
            "runtime manifest consumption remains disabled",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_manifest_consumption_eligibility_report",
            "observational_only": True,
            "production_behavior_changed": False,
            "production_default_routing_authorized": False,
            "planner_remap_performed": False,
            "controlled_test_consumption_only": True,
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    eligibility = report["manifest_consumption_eligibility"]
    summary = report["summary"]
    lines = [
        "# V3.1 Manifest Consumption Eligibility",
        "",
        "Phase 16 evaluates non-production-authoritative manifests for controlled test consumption eligibility only.",
        "Eligibility does not authorize production routing or runtime manifest consumption.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        f"- Runtime manifest consumption enabled: `{str(report['runtime_manifest_consumption_enabled']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Manifests evaluated: `{summary['manifests_evaluated']}`",
        f"- Eligible: `{summary['eligible_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in eligibility["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Eligibility Records", "", "| Record | Manifest | Fixture Set | Status | Authorization |", "| --- | --- | --- | --- | --- |"])
    for row in eligibility["eligibility_records"]:
        lines.append(
            f"| `{row['eligibility_record_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['eligibility_status']}` | `{row['authorization_state'] or ''}` |"
        )
    lines.extend(["", "## Phase 16 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_16_boundaries"])
    lines.extend(["", "## Conclusion", "", "Manifest eligibility is available for controlled test planning only, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_manifest_consumption_eligibility_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_MANIFEST_CONSUMPTION_ELIGIBILITY.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_manifest_consumption_eligibility_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
