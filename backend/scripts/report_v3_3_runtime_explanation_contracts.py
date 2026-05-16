"""Generate the v3.3 runtime explanation contracts report."""

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
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts  # noqa: E402
from app.runtime_intelligence.explanation_hashing import hash_explanation_manifest  # noqa: E402
from app.runtime_intelligence.explanation_registry import export_explanation_registry  # noqa: E402
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts  # noqa: E402
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_explanation_contracts_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
    )
    explanations = default_runtime_explanation_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
    )
    manifest = export_explanation_registry(
        explanations,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
    )
    repeated = export_explanation_registry(
        deepcopy(explanations),
        classifications=deepcopy(classifications),
        evidence_contracts=deepcopy(evidence),
        provenance_contracts=deepcopy(provenance),
        reasoning_stage_contracts=deepcopy(reasoning),
    )
    rows = manifest["explanation_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_explanation_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_5_runtime_explanation_contracts",
        "recommendation": "RUNTIME_EXPLANATION_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_explanations_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "summary": {
            "total_explanation_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "blocker_visible_explanation_count": sum(1 for row in rows if row["blocker_visible"]),
            "risk_visible_explanation_count": sum(1 for row in rows if row["risk_visible"]),
            "limitation_visible_explanation_count": sum(1 for row in rows if row["limitation_visible"]),
            "confidence_visible_explanation_count": sum(1 for row in rows if row["confidence_visible"]),
            "replay_safe_explanation_count": sum(1 for row in rows if row["replay_safe"]),
            "drift_visible_explanation_count": sum(1 for row in rows if row["drift_visible"]),
            "production_authorized_explanation_count": sum(1 for row in rows if row["production_authorized"]),
            "unsupported_explanation_count": _count(rows, "explanation_label", "unsupported_summary"),
            "decision_boundary_explanation_count": _count(rows, "explanation_label", "decision_boundary_summary"),
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "required_section_violation_count": validation["required_section_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "explanation_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["explanation_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_explanation_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "explanation_to_evidence_compatibility_validation": {
            "passed": validation["invalid_evidence_reference_count"] == 0,
            "invalid_evidence_references": validation["invalid_evidence_references"],
        },
        "explanation_to_provenance_compatibility_validation": {
            "passed": validation["invalid_provenance_reference_count"] == 0,
            "invalid_provenance_references": validation["invalid_provenance_references"],
        },
        "explanation_to_classification_compatibility_validation": {
            "passed": validation["invalid_classification_reference_count"] == 0,
            "invalid_classification_references": validation["invalid_classification_references"],
        },
        "explanation_to_reasoning_compatibility_validation": {
            "passed": validation["invalid_reasoning_stage_reference_count"] == 0,
            "invalid_reasoning_stage_references": validation["invalid_reasoning_stage_references"],
        },
        "required_section_validation": {
            "passed": validation["required_section_violation_count"] == 0,
            "required_section_violations": validation["required_section_violations"],
        },
        "contracts_with_explicit_limitations": {
            row["explanation_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "contracts_with_explicit_risks": {
            row["explanation_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_explanations_remain_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_explanation_contract_is_production_authorized": True,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_explanation_contracts_report",
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
    rows = report["explanation_manifest"]["explanation_contracts"]
    lines = [
        "# V3.3 Runtime Explanation Contracts",
        "",
        "Phase 5 establishes deterministic runtime explanation contracts for planning-only runtime intelligence foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime explanations remain planning-only. Production runtime routing, default manifest consumption, production-authoritative manifest treatment, active runtime reasoning decisions, recommendation logic, and autonomous planner mutation remain disabled or prohibited.",
        "",
        "## Compatibility",
        "",
        "Every explanation contract references explicit classification IDs, evidence type IDs, provenance type IDs, and reasoning stage IDs from the Phase 1 through Phase 4 registries.",
        "",
        "## Summary",
        "",
        f"- Total explanation contracts: `{summary['total_explanation_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid evidence references: `{summary['invalid_evidence_reference_count']}`",
        f"- Invalid provenance references: `{summary['invalid_provenance_reference_count']}`",
        f"- Invalid classification references: `{summary['invalid_classification_reference_count']}`",
        f"- Invalid reasoning-stage references: `{summary['invalid_reasoning_stage_reference_count']}`",
        f"- Required-section violations: `{summary['required_section_violation_count']}`",
        f"- Production-authorized explanations: `{summary['production_authorized_explanation_count']}`",
        "",
        "## Explanation Contracts",
        "",
        "| Rank | Explanation | Blocker | Risk | Limitation | Confidence | Replay Safe |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['explanation_label']}` | `{str(row['blocker_visible']).lower()}` | `{str(row['risk_visible']).lower()}` | `{str(row['limitation_visible']).lower()}` | `{str(row['confidence_visible']).lower()}` | `{str(row['replay_safe']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Blocker-visible explanations remain visible through `blocker_summary`, `decision_boundary_summary`, and `unsupported_summary`.")
    lines.append("- Risk-visible explanations remain visible through risk, drift, confidence, decision-boundary, unsupported, and related summaries.")
    lines.append("- Limitation-visible explanations remain visible across all explanation contracts.")
    lines.append("- Confidence-visible explanations remain visible through `classification_summary` and `confidence_summary`.")
    lines.append("- Unsupported explanations remain visible through `unsupported_summary`.")
    lines.append("- Decision-boundary explanations remain visible through `decision_boundary_summary`.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime explanation lineage. They do not authorize production enablement, runtime consumption, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_explanation_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_EXPLANATION_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_explanation_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
