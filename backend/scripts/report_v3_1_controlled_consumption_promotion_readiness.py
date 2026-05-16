"""Generate the v3.1 controlled consumption promotion readiness report."""

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

from app.planner_adapters.v3_1.controlled_consumption_promotion_readiness import build_controlled_consumption_promotion_readiness  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_controlled_consumption_promotion_readiness_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    consumption = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_test_consumption_report.json")[
        "controlled_test_consumption"
    ]
    validation = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_output_validation_report.json")[
        "controlled_consumption_output_validation"
    ]
    structural = _read_json(repo_root / "docs" / "generated" / "v3_1_controlled_consumption_parity_snapshot_report.json")[
        "controlled_consumption_parity_snapshot"
    ]
    semantic = _read_json(repo_root / "docs" / "generated" / "v3_1_trace_backfilled_semantic_parity_report.json")[
        "trace_backfilled_semantic_parity"
    ]
    eligibility = _read_json(repo_root / "docs" / "generated" / "v3_1_manifest_consumption_eligibility_report.json")[
        "manifest_consumption_eligibility"
    ]
    readiness = build_controlled_consumption_promotion_readiness(
        controlled_test_consumption=consumption,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
        manifest_consumption_eligibility=eligibility,
    )
    repeated = build_controlled_consumption_promotion_readiness(
        controlled_test_consumption=consumption,
        controlled_consumption_output_validation=validation,
        controlled_consumption_parity_snapshot=structural,
        trace_backfilled_semantic_parity=semantic,
        manifest_consumption_eligibility=eligibility,
    )
    report = {
        "schema_version": "v3_1.controlled_consumption_promotion_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_24_controlled_consumption_promotion_readiness_gate",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "runtime_manifest_consumption_enabled": False,
        "runtime_production_consumption_enabled": False,
        "summary": {
            **readiness["summary"],
            "deterministic": readiness["deterministic_hash"] == repeated["deterministic_hash"],
        },
        "controlled_consumption_promotion_readiness": readiness,
        "deterministic_guarantees": {
            "passed": readiness["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": readiness["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "timestamp_excluded_from_hash": True,
            "json_sort_keys": True,
        },
        "phase_24_boundaries": [
            "promotion readiness is for future limited experimental runtime consideration only",
            "promotion readiness is not production approval",
            "promotion readiness does not authorize production routing",
            "runtime manifest consumption remains disabled",
            "manifests remain non-production-authoritative",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_controlled_consumption_promotion_readiness_report",
            "observational_only": True,
            "controlled_test_only": True,
            "future_limited_experimental_consideration_only": True,
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
    readiness = report["controlled_consumption_promotion_readiness"]
    summary = report["summary"]
    evidence = readiness["evidence_chain_summary"]
    lines = [
        "# V3.1 Controlled Consumption Promotion Readiness",
        "",
        "Phase 24 gates the controlled-consumption evidence chain for future limited experimental runtime consideration.",
        "Promotion readiness is not production approval and does not authorize routing.",
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
        f"- Records evaluated: `{summary['records_evaluated']}`",
        f"- Ready: `{summary['ready_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Production affected: `{summary['production_affected_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Evidence Chain",
        "",
        f"- Controlled consumption records: `{evidence['controlled_consumption_records']}`",
        f"- Validated output records: `{evidence['validated_output_records']}`",
        f"- Structural parity records: `{evidence['structural_parity_records']}`",
        f"- Semantic parity records: `{evidence['semantic_parity_records']}`",
        f"- Manifest eligibility records: `{evidence['manifest_eligibility_records']}`",
        f"- Runtime consumption enabled: `{str(evidence['runtime_consumption_enabled']).lower()}`",
        "",
        "## Blocker Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ]
    for reason, count in readiness["blocker_reason_counts"].items():
        lines.append(f"| `{reason}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Readiness Records",
            "",
            "| Record | Manifest | Fixture Set | Readiness |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in readiness["promotion_readiness_records"]:
        lines.append(
            f"| `{row['promotion_readiness_id']}` | `{row['manifest_id'] or ''}` | `{row['fixture_set_id'] or ''}` | `{row['promotion_readiness_status']}` |"
        )
    lines.extend(["", "## Phase 24 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_24_boundaries"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Controlled consumption promotion readiness is available for governance review, while production routing remains unchanged.",
        ]
    )
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
    parser.add_argument("--output", default="docs/generated/v3_1_controlled_consumption_promotion_readiness_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_CONTROLLED_CONSUMPTION_PROMOTION_READINESS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_controlled_consumption_promotion_readiness_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
