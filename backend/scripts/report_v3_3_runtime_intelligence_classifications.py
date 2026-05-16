"""Generate the v3.3 runtime intelligence classification report."""

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

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications  # noqa: E402
from app.runtime_intelligence.classification_hashing import hash_classification_manifest  # noqa: E402
from app.runtime_intelligence.classification_registry import export_classification_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_intelligence_classification_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    manifest = export_classification_registry(classifications)
    repeated = export_classification_registry(deepcopy(classifications))
    rows = manifest["classifications"]
    duplicate_detection = manifest["registry_validation"]["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_intelligence_classification_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_1_runtime_intelligence_classification_contracts",
        "recommendation": "RUNTIME_INTELLIGENCE_CLASSIFICATION_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_intelligence_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "summary": {
            "total_classification_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "unsupported_classification_count": _count(rows, "classification_label", "unsupported"),
            "production_authorized_classification_count": sum(1 for row in rows if row["production_authorized"]),
            "replay_safe_classification_count": sum(1 for row in rows if row["replay_safe"]),
            "drift_visible_classification_count": sum(1 for row in rows if row["drift_visible"]),
            "classifications_requiring_provenance_count": sum(1 for row in rows if row["provenance_required"]),
            "classifications_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "classifications_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "classification_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["classification_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_classification_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "unsupported_runtime_visibility": {
            "unsupported_classification_visible": manifest["registry_validation"]["unsupported_classification_visible"],
            "authorization_prohibited_classification_visible": manifest["registry_validation"]["authorization_prohibited_classification_visible"],
            "provenance_incomplete_classification_visible": manifest["registry_validation"]["provenance_incomplete_classification_visible"],
        },
        "classifications_requiring_provenance": [row["classification_label"] for row in rows if row["provenance_required"]],
        "classifications_with_explicit_limitations": {
            row["classification_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "classifications_with_explicit_risks": {
            row["classification_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_intelligence_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "autonomous_planner_mutation_enabled": False,
            "unrestricted_runtime_execution_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_intelligence_classification_report",
            "governance_only": True,
            "runtime_behavior_enabled": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
            "deterministic_serializer": "json_sort_keys_sha256",
        },
    }
    return _normalize_generated_at(report)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    rows = report["classification_manifest"]["classifications"]
    lines = [
        "# V3.3 Runtime Intelligence Classification Contracts",
        "",
        "Phase 1 establishes deterministic runtime intelligence classification contracts for planning-only runtime reasoning foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime intelligence remains planning-only. Production runtime routing remains prohibited, default runtime manifest consumption remains disabled, and production-authoritative manifest treatment remains prohibited.",
        "",
        "## Determinism",
        "",
        "Classifications are sorted by deterministic rank, label, and id. The exported manifest uses stable JSON serialization and replay hash validation.",
        "",
        "## Summary",
        "",
        f"- Total classifications: `{summary['total_classification_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Production-authorized classifications: `{summary['production_authorized_classification_count']}`",
        f"- Replay-safe classifications: `{summary['replay_safe_classification_count']}`",
        f"- Drift-visible classifications: `{summary['drift_visible_classification_count']}`",
        "",
        "## Classification Registry",
        "",
        "| Rank | Label | Trust State | Replay Safe | Provenance Required |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['classification_label']}` | `{row['trust_state']}` | `{str(row['replay_safe']).lower()}` | `{str(row['provenance_required']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Unsupported runtime conditions remain visible through `unsupported`.")
    lines.append("- Authorization-prohibited conditions remain visible through `authorization_prohibited`.")
    lines.append("- Incomplete provenance remains visible through `provenance_incomplete`.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime intelligence classifications. They do not authorize production enablement or runtime consumption."])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _count(rows: list[dict[str, Any]], key: str, value: Any) -> int:
    return sum(1 for row in rows if row.get(key) == value)


def _deterministic_ordering_valid(rows: list[dict[str, Any]]) -> bool:
    return [row["deterministic_rank"] for row in rows] == sorted(row["deterministic_rank"] for row in rows)


def _normalize_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: DETERMINISTIC_GENERATED_AT if key == "generated_at" else _normalize_generated_at(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_generated_at(item) for item in value]
    return deepcopy(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_intelligence_classification_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_INTELLIGENCE_CLASSIFICATION_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_intelligence_classification_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
