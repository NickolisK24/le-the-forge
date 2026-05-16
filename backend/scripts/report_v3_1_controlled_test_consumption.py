"""Generate the v3.1 controlled test consumption report."""

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

from app.planner_adapters.v3_1.controlled_test_consumption import build_controlled_test_consumption  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_controlled_test_consumption_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    generated = repo_root / "docs" / "generated"
    eligibility = _read_json(generated / "v3_1_manifest_consumption_eligibility_report.json")["manifest_consumption_eligibility"]
    serialization = _read_json(generated / "v3_1_admission_aware_manifest_serialization_report.json")[
        "admission_aware_manifest_serialization"
    ]
    consumption = build_controlled_test_consumption(
        manifest_consumption_eligibility=eligibility,
        admission_aware_manifest_serialization=serialization,
        controlled_test_mode=True,
    )
    repeated = build_controlled_test_consumption(
        manifest_consumption_eligibility=eligibility,
        admission_aware_manifest_serialization=serialization,
        controlled_test_mode=True,
    )
    report = {
        "schema_version": "v3_1.controlled_test_consumption_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_17_controlled_test_consumption",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "runtime_production_consumption_enabled": False,
        "runtime_manifest_consumption_enabled": False,
        "controlled_test_mode": True,
        "summary": {
            **consumption["summary"],
            "deterministic": consumption["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "controlled_test_consumption": consumption,
        "deterministic_guarantees": {
            "passed": consumption["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": consumption["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_17_boundaries": [
            "controlled test consumption requires explicit test-only invocation",
            "controlled test consumption does not authorize production routing",
            "runtime production manifest consumption remains disabled",
            "production planner routing remains unchanged",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_controlled_test_consumption_report",
            "observational_only": True,
            "controlled_test_only": True,
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
    consumption = report["controlled_test_consumption"]
    summary = report["summary"]
    lines = [
        "# V3.1 Controlled Test Consumption",
        "",
        "Phase 17 consumes eligible non-production manifests only through explicit controlled test mode.",
        "This does not authorize production routing or runtime production manifest consumption.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        f"- Runtime production consumption enabled: `{str(report['runtime_production_consumption_enabled']).lower()}`",
        f"- Runtime manifest consumption enabled: `{str(report['runtime_manifest_consumption_enabled']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Manifests evaluated: `{summary['manifests_evaluated']}`",
        f"- Controlled-test consumed: `{summary['controlled_test_consumed_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Blocker Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in consumption["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(["", "## Controlled Consumption Records", "", "| Record | Manifest | Fixture Set | Status | Authorization |", "| --- | --- | --- | --- | --- |"])
    for row in consumption["controlled_consumption_records"]:
        lines.append(
            f"| `{row['controlled_consumption_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['controlled_consumption_status']}` | `{row['authorization_state'] or ''}` |"
        )
    lines.extend(["", "## Phase 17 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_17_boundaries"])
    lines.extend(["", "## Conclusion", "", "Controlled test consumption is available for isolated governance testing only, while production routing remains unchanged."])
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
    parser.add_argument("--output", default="docs/generated/v3_1_controlled_test_consumption_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_CONTROLLED_TEST_CONSUMPTION.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_controlled_test_consumption_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
