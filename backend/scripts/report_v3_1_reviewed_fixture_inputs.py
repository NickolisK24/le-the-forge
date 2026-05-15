"""Generate the v3.1 reviewed fixture input discovery report."""

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

from app.planner_adapters.v3_1.reviewed_fixture_inputs import (  # noqa: E402
    build_reviewed_fixture_input_report,
    discover_default_reviewed_fixture_input_sources,
    load_reviewed_fixture_input_sources,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_1_reviewed_fixture_inputs_report() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    sources = discover_default_reviewed_fixture_input_sources(repo_root)
    loaded = load_reviewed_fixture_input_sources(sources)
    reviewed_inputs = build_reviewed_fixture_input_report(loaded)
    report = {
        "schema_version": "v3_1.reviewed_fixture_inputs_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.1_phase_6_reviewed_fixture_input_discovery",
        "recommendation": "OBSERVATIONAL_ONLY_DO_NOT_ENABLE_PRODUCTION_DEFAULT_ROUTING",
        "production_default_routing_authorized": False,
        "summary": {
            "discovered_input_source_count": reviewed_inputs["discovered_input_source_count"],
            "normalized_fixture_count": reviewed_inputs["normalized_fixture_count"],
            "duplicate_count": reviewed_inputs["duplicate_count"],
            "malformed_count": reviewed_inputs["malformed_count"],
            "unsupported_count": reviewed_inputs["unsupported_count"],
            "missing_source_count": reviewed_inputs["missing_source_count"],
            "approved_reviewed_candidate_count": reviewed_inputs["reviewed_candidate_count"],
            "production_output_affected": False,
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "reviewed_fixture_inputs": reviewed_inputs,
        "input_source_hashes": [
            {
                "source_id": source["source_id"],
                "source_type": source["source_type"],
                "source_available": bool(source.get("source_available", True)),
                "source_hash": _source_hash(source),
            }
            for source in loaded
        ],
        "phase_6_boundaries": [
            "reviewed fixture inputs are observational governance metadata only",
            "trusted infrastructure is still not production default",
            "reviewed inputs do not authorize production routing",
            "unsupported and malformed inputs remain intentionally visible",
            "legacy planner ownership remains intact",
        ],
        "metadata": {
            "source": "v3_1_reviewed_fixture_inputs_report",
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
        "# V3.1 Reviewed Fixture Inputs",
        "",
        "Phase 6 introduces deterministic reviewed fixture input discovery and normalization.",
        "Reviewed fixture inputs are governance metadata only and do not authorize production routing.",
        "",
        "## Recommendation",
        "",
        f"- Recommendation: `{report['recommendation']}`",
        f"- Production default routing authorized: `{str(report['production_default_routing_authorized']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Discovered input sources: `{summary['discovered_input_source_count']}`",
        f"- Normalized fixtures: `{summary['normalized_fixture_count']}`",
        f"- Duplicate inputs: `{summary['duplicate_count']}`",
        f"- Malformed inputs: `{summary['malformed_count']}`",
        f"- Unsupported inputs: `{summary['unsupported_count']}`",
        f"- Missing sources: `{summary['missing_source_count']}`",
        f"- Approved/reviewed candidates: `{summary['approved_reviewed_candidate_count']}`",
        f"- Production affected: `{str(summary['production_output_affected']).lower()}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Input Status Counts",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in report["reviewed_fixture_inputs"]["status_counts"].items():
        lines.append(f"| `{status}` | `{count}` |")
    lines.extend(["", "## Phase 6 Boundaries", ""])
    lines.extend(f"- {item}" for item in report["phase_6_boundaries"])
    lines.extend(["", "## Conclusion", "", "Reviewed fixture input discovery is available for governance, while production routing remains unchanged."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_hash(source: dict[str, Any]) -> str:
    payload = deepcopy(source)
    payload.pop("source_path", None)
    return build_reviewed_fixture_input_report([payload])["deterministic_hash"]


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_1_reviewed_fixture_inputs_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_1_REVIEWED_FIXTURE_INPUTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_1_reviewed_fixture_inputs_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
