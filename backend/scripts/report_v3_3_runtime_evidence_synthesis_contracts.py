"""Generate the v3.3 runtime evidence synthesis contracts report."""

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
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts  # noqa: E402
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts  # noqa: E402
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts  # noqa: E402
from app.runtime_intelligence.evidence_synthesis_hashing import hash_evidence_synthesis_manifest  # noqa: E402
from app.runtime_intelligence.evidence_synthesis_registry import export_evidence_synthesis_registry  # noqa: E402
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts  # noqa: E402
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts  # noqa: E402
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_evidence_synthesis_contracts_report() -> dict[str, Any]:
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
    confidence = default_runtime_confidence_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
    )
    syntheses = default_runtime_evidence_synthesis_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
        confidence_contracts=confidence,
    )
    manifest = export_evidence_synthesis_registry(
        syntheses,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
        confidence_contracts=confidence,
    )
    repeated = export_evidence_synthesis_registry(
        deepcopy(syntheses),
        classifications=deepcopy(classifications),
        evidence_contracts=deepcopy(evidence),
        provenance_contracts=deepcopy(provenance),
        reasoning_stage_contracts=deepcopy(reasoning),
        explanation_contracts=deepcopy(explanations),
        confidence_contracts=deepcopy(confidence),
    )
    rows = manifest["synthesis_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_evidence_synthesis_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_7_runtime_evidence_synthesis_contracts",
        "recommendation": "RUNTIME_EVIDENCE_SYNTHESIS_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_evidence_synthesis_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "live_synthesis_execution_enabled": False,
        "summary": {
            "total_synthesis_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "production_authorized_synthesis_count": sum(1 for row in rows if row["production_authorized"]),
            "conflict_preserving_synthesis_count": sum(1 for row in rows if row["preserves_conflicts"]),
            "drift_preserving_synthesis_count": sum(1 for row in rows if row["preserves_drift"]),
            "unsupported_preserving_synthesis_count": sum(1 for row in rows if row["preserves_unsupported"]),
            "blocker_preserving_synthesis_count": sum(1 for row in rows if row["preserves_blockers"]),
            "limitation_preserving_synthesis_count": sum(1 for row in rows if row["preserves_limitations"]),
            "provenance_preserving_synthesis_count": sum(1 for row in rows if row["preserves_provenance"]),
            "replay_validation_required_synthesis_count": sum(1 for row in rows if row["requires_replay_validation"]),
            "hash_validation_required_synthesis_count": sum(1 for row in rows if row["requires_hash_validation"]),
            "decision_boundary_preserving_synthesis_count": _count(rows, "synthesis_label", "decision_boundary_preserving_merge"),
            "input_count_violation_count": validation["input_count_violation_count"],
            "preservation_rule_violation_count": validation["preservation_rule_violation_count"],
            "invalid_input_evidence_reference_count": validation["invalid_input_evidence_reference_count"],
            "invalid_output_evidence_reference_count": validation["invalid_output_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_confidence_reference_count": validation["invalid_confidence_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "invalid_explanation_reference_count": validation["invalid_explanation_reference_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "evidence_synthesis_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["synthesis_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_evidence_synthesis_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "input_output_count_validation": {
            "passed": validation["input_count_violation_count"] == 0,
            "input_count_violations": validation["input_count_violations"],
        },
        "preservation_rule_validation": {
            "passed": validation["preservation_rule_violation_count"] == 0,
            "preservation_rule_violations": validation["preservation_rule_violations"],
            "replay_rule_violations": validation["replay_rule_violations"],
        },
        "synthesis_to_input_evidence_compatibility_validation": {
            "passed": validation["invalid_input_evidence_reference_count"] == 0,
            "invalid_input_evidence_references": validation["invalid_input_evidence_references"],
        },
        "synthesis_to_output_evidence_compatibility_validation": {
            "passed": validation["invalid_output_evidence_reference_count"] == 0,
            "invalid_output_evidence_references": validation["invalid_output_evidence_references"],
        },
        "synthesis_to_provenance_compatibility_validation": {
            "passed": validation["invalid_provenance_reference_count"] == 0,
            "invalid_provenance_references": validation["invalid_provenance_references"],
        },
        "synthesis_to_classification_compatibility_validation": {
            "passed": validation["invalid_classification_reference_count"] == 0,
            "invalid_classification_references": validation["invalid_classification_references"],
        },
        "synthesis_to_confidence_compatibility_validation": {
            "passed": validation["invalid_confidence_reference_count"] == 0,
            "invalid_confidence_references": validation["invalid_confidence_references"],
        },
        "synthesis_to_reasoning_compatibility_validation": {
            "passed": validation["invalid_reasoning_stage_reference_count"] == 0,
            "invalid_reasoning_stage_references": validation["invalid_reasoning_stage_references"],
        },
        "synthesis_to_explanation_compatibility_validation": {
            "passed": validation["invalid_explanation_reference_count"] == 0,
            "invalid_explanation_references": validation["invalid_explanation_references"],
        },
        "contracts_with_explicit_limitations": {
            row["synthesis_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "contracts_with_explicit_risks": {
            row["synthesis_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_evidence_synthesis_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_synthesis_contract_is_production_authorized": True,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "live_synthesis_execution_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_evidence_synthesis_contracts_report",
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
    rows = report["evidence_synthesis_manifest"]["synthesis_contracts"]
    lines = [
        "# V3.3 Runtime Evidence Synthesis Contracts",
        "",
        "Phase 7 establishes deterministic runtime evidence synthesis contracts for planning-only runtime intelligence foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime evidence synthesis remains planning-only. Live synthesis execution, active runtime reasoning decisions, recommendation logic, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Compatibility",
        "",
        "Every synthesis contract references explicit classification IDs, input and output evidence type IDs, provenance type IDs, confidence type IDs, reasoning stage IDs, and explanation type IDs from the Phase 1 through Phase 6 registries.",
        "",
        "## Summary",
        "",
        f"- Total synthesis contracts: `{summary['total_synthesis_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Input/output count violations: `{summary['input_count_violation_count']}`",
        f"- Preservation-rule violations: `{summary['preservation_rule_violation_count']}`",
        f"- Invalid input evidence references: `{summary['invalid_input_evidence_reference_count']}`",
        f"- Invalid output evidence references: `{summary['invalid_output_evidence_reference_count']}`",
        f"- Invalid confidence references: `{summary['invalid_confidence_reference_count']}`",
        f"- Production-authorized syntheses: `{summary['production_authorized_synthesis_count']}`",
        "",
        "## Synthesis Contracts",
        "",
        "| Rank | Synthesis | Min | Max | Conflicts | Drift | Unsupported | Blockers | Limitations | Provenance | Replay Required |",
        "| ---: | --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['synthesis_label']}` | `{row['minimum_input_count']}` | `{row['maximum_input_count']}` | `{str(row['preserves_conflicts']).lower()}` | `{str(row['preserves_drift']).lower()}` | `{str(row['preserves_unsupported']).lower()}` | `{str(row['preserves_blockers']).lower()}` | `{str(row['preserves_limitations']).lower()}` | `{str(row['preserves_provenance']).lower()}` | `{str(row['requires_replay_validation']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Conflict, drift, unsupported, blocker, limitation, provenance, and decision-boundary preservation remain explicit.")
    lines.append("- Preservation-specific synthesis contracts are validated against their required preservation flags.")
    lines.append("- Live synthesis execution remains disabled.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime evidence synthesis governance. They do not authorize production enablement, runtime consumption, live synthesis execution, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_evidence_synthesis_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_EVIDENCE_SYNTHESIS_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_evidence_synthesis_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
