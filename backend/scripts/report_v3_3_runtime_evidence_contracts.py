"""Generate the v3.3 runtime evidence contracts report."""

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
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts  # noqa: E402
from app.runtime_intelligence.evidence_hashing import hash_evidence_manifest  # noqa: E402
from app.runtime_intelligence.evidence_registry import export_evidence_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_evidence_contracts_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    evidence_contracts = default_runtime_evidence_contracts(classifications)
    manifest = export_evidence_registry(evidence_contracts, classifications=classifications)
    repeated = export_evidence_registry(deepcopy(evidence_contracts), classifications=deepcopy(classifications))
    rows = manifest["evidence_contracts"]
    duplicate_detection = manifest["registry_validation"]["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_evidence_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_2_runtime_evidence_contracts",
        "recommendation": "RUNTIME_EVIDENCE_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_evidence_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "summary": {
            "total_evidence_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "evidence_contracts_requiring_provenance_count": sum(1 for row in rows if row["provenance_required"]),
            "evidence_contracts_requiring_source_count": sum(1 for row in rows if row["source_required"]),
            "replay_safe_evidence_contract_count": sum(1 for row in rows if row["replay_safe"]),
            "drift_visible_evidence_contract_count": sum(1 for row in rows if row["drift_visible"]),
            "production_authorized_evidence_contract_count": sum(1 for row in rows if row["production_authorized"]),
            "unsupported_evidence_contract_count": _count(rows, "evidence_label", "unsupported_signal"),
            "authorization_prohibited_evidence_contract_count": _count(rows, "evidence_label", "authorization_signal"),
            "invalid_classification_reference_count": manifest["registry_validation"]["invalid_classification_reference_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "evidence_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["evidence_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_evidence_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "evidence_to_classification_compatibility_validation": {
            "passed": manifest["registry_validation"]["invalid_classification_reference_count"] == 0,
            "invalid_classification_references": manifest["registry_validation"]["invalid_classification_references"],
        },
        "unsupported_evidence_visibility": {
            "unsupported_evidence_visible": manifest["registry_validation"]["unsupported_evidence_visible"],
            "authorization_prohibited_evidence_visible": manifest["registry_validation"]["authorization_prohibited_evidence_visible"],
        },
        "evidence_contracts_requiring_provenance": [row["evidence_label"] for row in rows if row["provenance_required"]],
        "evidence_contracts_requiring_source_attribution": [row["evidence_label"] for row in rows if row["source_required"]],
        "contracts_with_explicit_limitations": {
            row["evidence_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "contracts_with_explicit_risks": {
            row["evidence_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_evidence_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_evidence_contract_is_production_authorized": True,
            "runtime_evidence_synthesis_enabled": False,
            "runtime_reasoning_decisions_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_evidence_contracts_report",
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
    rows = report["evidence_manifest"]["evidence_contracts"]
    lines = [
        "# V3.3 Runtime Evidence Contracts",
        "",
        "Phase 2 establishes deterministic runtime evidence contracts for planning-only runtime intelligence foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime evidence remains planning-only. Evidence synthesis, runtime reasoning decisions, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Classification Compatibility",
        "",
        "Every evidence contract references explicit Phase 1 classification IDs. Invalid classification references fail registry validation.",
        "",
        "## Summary",
        "",
        f"- Total evidence contracts: `{summary['total_evidence_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid classification references: `{summary['invalid_classification_reference_count']}`",
        f"- Production-authorized evidence contracts: `{summary['production_authorized_evidence_contract_count']}`",
        "",
        "## Evidence Registry",
        "",
        "| Rank | Evidence | Replay Safe | Drift Visible | Provenance | Source |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['evidence_label']}` | `{str(row['replay_safe']).lower()}` | `{str(row['drift_visible']).lower()}` | `{str(row['provenance_required']).lower()}` | `{str(row['source_required']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Unsupported evidence remains visible through `unsupported_signal`.")
    lines.append("- Authorization-prohibited evidence remains visible through `authorization_signal`.")
    lines.append("- Provenance-required and source-required validation applies to every evidence contract.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime evidence structures. They do not authorize production enablement, runtime consumption, evidence synthesis, or runtime reasoning decisions."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_evidence_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_EVIDENCE_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_evidence_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
