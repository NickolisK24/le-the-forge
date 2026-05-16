"""Generate the v3.3 runtime decision boundary contracts report."""

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
from app.runtime_intelligence.decision_boundary_contracts import default_runtime_decision_boundary_contracts  # noqa: E402
from app.runtime_intelligence.decision_boundary_hashing import hash_decision_boundary_manifest  # noqa: E402
from app.runtime_intelligence.decision_boundary_registry import export_decision_boundary_registry  # noqa: E402
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts  # noqa: E402
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts  # noqa: E402
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts  # noqa: E402
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts  # noqa: E402
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_decision_boundary_contracts_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance)
    explanations = default_runtime_explanation_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning)
    confidence = default_runtime_confidence_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations)
    synthesis = default_runtime_evidence_synthesis_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence)
    boundaries = default_runtime_decision_boundary_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence, synthesis_contracts=synthesis)
    manifest = export_decision_boundary_registry(boundaries, classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence, synthesis_contracts=synthesis)
    repeated = export_decision_boundary_registry(deepcopy(boundaries), classifications=deepcopy(classifications), evidence_contracts=deepcopy(evidence), provenance_contracts=deepcopy(provenance), reasoning_stage_contracts=deepcopy(reasoning), explanation_contracts=deepcopy(explanations), confidence_contracts=deepcopy(confidence), synthesis_contracts=deepcopy(synthesis))
    rows = manifest["boundary_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_decision_boundary_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_8_runtime_decision_boundary_contracts",
        "recommendation": "RUNTIME_DECISION_BOUNDARY_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_decision_boundaries_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "summary": {
            "total_decision_boundary_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "production_authorized_boundary_count": sum(1 for row in rows if row["production_authorized"]),
            "hard_stop_boundary_count": _count(rows, "boundary_action", "hard_stop"),
            "escalation_boundary_count": _count(rows, "boundary_action", "escalation"),
            "manual_review_required_boundary_count": sum(1 for row in rows if row["requires_manual_review"]),
            "prohibition_boundary_count": _count(rows, "boundary_action", "prohibition"),
            "planning_only_marker_count": _count(rows, "boundary_action", "planning_only_marker"),
            "downstream_reasoning_blocking_boundary_count": sum(1 for row in rows if row["blocks_downstream_reasoning"]),
            "synthesis_execution_blocking_boundary_count": sum(1 for row in rows if row["blocks_synthesis_execution"]),
            "recommendation_logic_blocking_boundary_count": sum(1 for row in rows if row["blocks_recommendation_logic"]),
            "production_authorization_blocking_boundary_count": sum(1 for row in rows if row["blocks_production_authorization"]),
            "replay_validation_required_boundary_count": sum(1 for row in rows if row["requires_replay_validation"]),
            "hash_validation_required_boundary_count": sum(1 for row in rows if row["requires_hash_validation"]),
            "conflict_preserving_boundary_count": sum(1 for row in rows if row["preserves_conflicts"]),
            "drift_preserving_boundary_count": sum(1 for row in rows if row["preserves_drift"]),
            "unsupported_preserving_boundary_count": sum(1 for row in rows if row["preserves_unsupported"]),
            "blocker_preserving_boundary_count": sum(1 for row in rows if row["preserves_blockers"]),
            "limitation_preserving_boundary_count": sum(1 for row in rows if row["preserves_limitations"]),
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_reasoning_stage_reference_count": validation["invalid_reasoning_stage_reference_count"],
            "invalid_explanation_reference_count": validation["invalid_explanation_reference_count"],
            "invalid_confidence_reference_count": validation["invalid_confidence_reference_count"],
            "invalid_synthesis_reference_count": validation["invalid_synthesis_reference_count"],
            "invalid_boundary_action_count": validation["invalid_boundary_action_count"],
            "behavior_rule_violation_count": validation["behavior_rule_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "decision_boundary_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["boundary_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_decision_boundary_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "boundary_action_validation": {
            "passed": validation["invalid_boundary_action_count"] == 0,
            "invalid_boundary_actions": validation["invalid_boundary_actions"],
        },
        "stop_escalation_prohibition_manual_review_rule_validation": {
            "passed": validation["behavior_rule_violation_count"] == 0,
            "behavior_rule_violations": validation["behavior_rule_violations"],
        },
        "boundary_to_classification_compatibility_validation": {"passed": validation["invalid_classification_reference_count"] == 0, "invalid_classification_references": validation["invalid_classification_references"]},
        "boundary_to_evidence_compatibility_validation": {"passed": validation["invalid_evidence_reference_count"] == 0, "invalid_evidence_references": validation["invalid_evidence_references"]},
        "boundary_to_provenance_compatibility_validation": {"passed": validation["invalid_provenance_reference_count"] == 0, "invalid_provenance_references": validation["invalid_provenance_references"]},
        "boundary_to_reasoning_compatibility_validation": {"passed": validation["invalid_reasoning_stage_reference_count"] == 0, "invalid_reasoning_stage_references": validation["invalid_reasoning_stage_references"]},
        "boundary_to_explanation_compatibility_validation": {"passed": validation["invalid_explanation_reference_count"] == 0, "invalid_explanation_references": validation["invalid_explanation_references"]},
        "boundary_to_confidence_compatibility_validation": {"passed": validation["invalid_confidence_reference_count"] == 0, "invalid_confidence_references": validation["invalid_confidence_references"]},
        "boundary_to_synthesis_compatibility_validation": {"passed": validation["invalid_synthesis_reference_count"] == 0, "invalid_synthesis_references": validation["invalid_synthesis_references"]},
        "contracts_with_explicit_limitations": {row["boundary_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]},
        "contracts_with_explicit_risks": {row["boundary_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]},
        "safety_confirmations": {
            "runtime_decision_boundaries_remain_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_boundary_contract_is_production_authorized": True,
            "active_runtime_reasoning_decisions_enabled": False,
            "recommendation_logic_enabled": False,
            "live_synthesis_execution_enabled": False,
            "live_decision_routing_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_decision_boundary_contracts_report",
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
    rows = report["decision_boundary_manifest"]["boundary_contracts"]
    lines = [
        "# V3.3 Runtime Decision Boundary Contracts",
        "",
        "Phase 8 establishes deterministic runtime decision boundary contracts for planning-only runtime intelligence governance.",
        "",
        "## Boundaries",
        "",
        "Runtime decision boundaries remain planning-only. Live decision routing, live synthesis execution, active reasoning decisions, recommendation logic, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Summary",
        "",
        f"- Total decision boundary contracts: `{summary['total_decision_boundary_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid boundary actions: `{summary['invalid_boundary_action_count']}`",
        f"- Behavior-rule violations: `{summary['behavior_rule_violation_count']}`",
        f"- Invalid synthesis references: `{summary['invalid_synthesis_reference_count']}`",
        f"- Production-authorized boundaries: `{summary['production_authorized_boundary_count']}`",
        "",
        "## Decision Boundaries",
        "",
        "| Rank | Boundary | Action | Blocks Reasoning | Blocks Synthesis | Blocks Recommendation | Blocks Production | Manual Review |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['boundary_label']}` | `{row['boundary_action']}` | `{str(row['blocks_downstream_reasoning']).lower()}` | `{str(row['blocks_synthesis_execution']).lower()}` | `{str(row['blocks_recommendation_logic']).lower()}` | `{str(row['blocks_production_authorization']).lower()}` | `{str(row['requires_manual_review']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Hard stops, escalations, prohibitions, manual-review boundaries, replay mismatch, confidence ceiling, recommendation prohibition, and production prohibition remain visible.")
    lines.append("- Unsupported, conflict, drift, blocker, and limitation preservation remain explicit where required.")
    lines.append("- Live decision routing remains disabled.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime decision boundary governance. They do not authorize production enablement, runtime consumption, live decision routing, live synthesis execution, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_decision_boundary_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_DECISION_BOUNDARY_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_decision_boundary_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
