"""Generate the v3.3 runtime provenance contracts report."""

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
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts  # noqa: E402
from app.runtime_intelligence.provenance_hashing import hash_provenance_manifest  # noqa: E402
from app.runtime_intelligence.provenance_registry import export_provenance_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_provenance_contracts_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    evidence_contracts = default_runtime_evidence_contracts(classifications)
    provenance_contracts = default_runtime_provenance_contracts(
        classifications=classifications,
        evidence_contracts=evidence_contracts,
    )
    manifest = export_provenance_registry(
        provenance_contracts,
        classifications=classifications,
        evidence_contracts=evidence_contracts,
    )
    repeated = export_provenance_registry(
        deepcopy(provenance_contracts),
        classifications=deepcopy(classifications),
        evidence_contracts=deepcopy(evidence_contracts),
    )
    rows = manifest["provenance_contracts"]
    duplicate_detection = manifest["registry_validation"]["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_provenance_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_3_runtime_provenance_contracts",
        "recommendation": "RUNTIME_PROVENANCE_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_provenance_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "summary": {
            "total_provenance_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "provenance_contracts_requiring_source_count": sum(1 for row in rows if row["source_required"]),
            "provenance_contracts_requiring_hash_count": sum(1 for row in rows if row["hash_required"]),
            "replay_safe_provenance_contract_count": sum(1 for row in rows if row["replay_safe"]),
            "drift_visible_provenance_contract_count": sum(1 for row in rows if row["drift_visible"]),
            "production_authorized_provenance_contract_count": sum(1 for row in rows if row["production_authorized"]),
            "unsupported_provenance_contract_count": _count(rows, "provenance_label", "unsupported_source"),
            "authorization_gate_provenance_contract_count": _count(rows, "provenance_label", "authorization_gate_source"),
            "invalid_evidence_reference_count": manifest["registry_validation"]["invalid_evidence_reference_count"],
            "invalid_classification_reference_count": manifest["registry_validation"]["invalid_classification_reference_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "provenance_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["provenance_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_provenance_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "provenance_to_evidence_compatibility_validation": {
            "passed": manifest["registry_validation"]["invalid_evidence_reference_count"] == 0,
            "invalid_evidence_references": manifest["registry_validation"]["invalid_evidence_references"],
        },
        "provenance_to_classification_compatibility_validation": {
            "passed": manifest["registry_validation"]["invalid_classification_reference_count"] == 0,
            "invalid_classification_references": manifest["registry_validation"]["invalid_classification_references"],
        },
        "unsupported_provenance_visibility": {
            "unsupported_provenance_visible": manifest["registry_validation"]["unsupported_provenance_visible"],
            "authorization_gate_provenance_visible": manifest["registry_validation"]["authorization_gate_provenance_visible"],
        },
        "provenance_contracts_requiring_source_attribution": [row["provenance_label"] for row in rows if row["source_required"]],
        "provenance_contracts_requiring_hashes": [row["provenance_label"] for row in rows if row["hash_required"]],
        "contracts_with_explicit_limitations": {
            row["provenance_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "contracts_with_explicit_risks": {
            row["provenance_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_provenance_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_provenance_contract_is_production_authorized": True,
            "runtime_evidence_synthesis_enabled": False,
            "runtime_reasoning_decisions_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_provenance_contracts_report",
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
    rows = report["provenance_manifest"]["provenance_contracts"]
    lines = [
        "# V3.3 Runtime Provenance Contracts",
        "",
        "Phase 3 establishes deterministic runtime provenance contracts for planning-only runtime intelligence foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime provenance remains planning-only. Evidence synthesis, runtime reasoning decisions, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Compatibility",
        "",
        "Every provenance contract references explicit Phase 1 classification IDs and Phase 2 evidence type IDs. Invalid references fail registry validation.",
        "",
        "## Summary",
        "",
        f"- Total provenance contracts: `{summary['total_provenance_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid evidence references: `{summary['invalid_evidence_reference_count']}`",
        f"- Invalid classification references: `{summary['invalid_classification_reference_count']}`",
        f"- Production-authorized provenance contracts: `{summary['production_authorized_provenance_contract_count']}`",
        "",
        "## Provenance Registry",
        "",
        "| Rank | Provenance | Replay Safe | Drift Visible | Source | Hash |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['provenance_label']}` | `{str(row['replay_safe']).lower()}` | `{str(row['drift_visible']).lower()}` | `{str(row['source_required']).lower()}` | `{str(row['hash_required']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Unsupported provenance remains visible through `unsupported_source`.")
    lines.append("- Authorization-gate provenance remains visible through `authorization_gate_source`.")
    lines.append("- Source-required and hash-required validation applies to every provenance contract.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime provenance structures. They do not authorize production enablement, runtime consumption, evidence synthesis, or runtime reasoning decisions."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_provenance_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_PROVENANCE_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_provenance_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
