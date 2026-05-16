"""Generate the v3.3 runtime reasoning chain contracts report."""

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
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts  # noqa: E402
from app.runtime_intelligence.reasoning_chain_hashing import hash_reasoning_chain_manifest  # noqa: E402
from app.runtime_intelligence.reasoning_chain_registry import export_reasoning_chain_registry  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_reasoning_chain_contracts_report() -> dict[str, Any]:
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
    )
    manifest = export_reasoning_chain_registry(
        reasoning,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
    )
    repeated = export_reasoning_chain_registry(
        deepcopy(reasoning),
        classifications=deepcopy(classifications),
        evidence_contracts=deepcopy(evidence),
        provenance_contracts=deepcopy(provenance),
    )
    rows = manifest["reasoning_stage_contracts"]
    validation = manifest["registry_validation"]
    duplicate_detection = validation["duplicate_detection"]
    report = {
        "schema_version": "v3_3.runtime_reasoning_chain_contracts_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_4_runtime_reasoning_chain_contracts",
        "recommendation": "RUNTIME_REASONING_CHAIN_CONTRACT_FOUNDATION_READY_FOR_PLANNING_ONLY",
        "runtime_reasoning_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "summary": {
            "total_reasoning_chain_stage_contract_count": len(rows),
            "deterministic_ordering_valid": _deterministic_ordering_valid(rows),
            "stable_hash_valid": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "replay_validation_passed": manifest["replay_validation"]["replay_stable"],
            "duplicate_detection_passed": not any(duplicate_detection.values()),
            "blocker_capable_stage_count": sum(1 for row in rows if row["blocker_capable"]),
            "risk_capable_stage_count": sum(1 for row in rows if row["risk_capable"]),
            "limitation_capable_stage_count": sum(1 for row in rows if row["limitation_capable"]),
            "replay_safe_stage_count": sum(1 for row in rows if row["replay_safe"]),
            "drift_visible_stage_count": sum(1 for row in rows if row["drift_visible"]),
            "production_authorized_stage_count": sum(1 for row in rows if row["production_authorized"]),
            "decision_boundary_stage_count": _count(rows, "stage_label", "decision_boundary_check"),
            "invalid_evidence_reference_count": validation["invalid_evidence_reference_count"],
            "invalid_provenance_reference_count": validation["invalid_provenance_reference_count"],
            "invalid_classification_reference_count": validation["invalid_classification_reference_count"],
            "invalid_previous_stage_reference_count": validation["invalid_previous_stage_reference_count"],
            "previous_stage_rank_violation_count": validation["previous_stage_rank_violation_count"],
            "contracts_with_explicit_limitations_count": sum(1 for row in rows if row["explicit_limitations"]),
            "contracts_with_explicit_risks_count": sum(1 for row in rows if row["explicit_risks"]),
            "production_behavior_changed": False,
            "deterministic": True,
        },
        "reasoning_chain_manifest": manifest,
        "deterministic_ordering_validation": {
            "passed": _deterministic_ordering_valid(rows),
            "ordered_labels": [row["stage_label"] for row in rows],
            "ordered_ranks": [row["deterministic_rank"] for row in rows],
        },
        "stable_hash_validation": {
            "passed": manifest["deterministic_hash"] == repeated["deterministic_hash"],
            "sample_hash": manifest["deterministic_hash"],
            "repeated_hash": repeated["deterministic_hash"],
            "hash_without_report_timestamp": hash_reasoning_chain_manifest(manifest),
        },
        "replay_validation_results": manifest["replay_validation"],
        "duplicate_detection_results": duplicate_detection,
        "reasoning_to_evidence_compatibility_validation": {
            "passed": validation["invalid_evidence_reference_count"] == 0,
            "invalid_evidence_references": validation["invalid_evidence_references"],
        },
        "reasoning_to_provenance_compatibility_validation": {
            "passed": validation["invalid_provenance_reference_count"] == 0,
            "invalid_provenance_references": validation["invalid_provenance_references"],
        },
        "reasoning_to_classification_compatibility_validation": {
            "passed": validation["invalid_classification_reference_count"] == 0,
            "invalid_classification_references": validation["invalid_classification_references"],
        },
        "required_previous_stage_validation": {
            "passed": validation["invalid_previous_stage_reference_count"] == 0
            and validation["previous_stage_rank_violation_count"] == 0,
            "invalid_previous_stage_references": validation["invalid_previous_stage_references"],
            "previous_stage_rank_violations": validation["previous_stage_rank_violations"],
        },
        "contracts_with_explicit_limitations": {
            row["stage_label"]: row["explicit_limitations"] for row in rows if row["explicit_limitations"]
        },
        "contracts_with_explicit_risks": {
            row["stage_label"]: row["explicit_risks"] for row in rows if row["explicit_risks"]
        },
        "safety_confirmations": {
            "runtime_reasoning_remains_planning_only": True,
            "production_runtime_routing_prohibited": True,
            "default_runtime_manifest_consumption_disabled": True,
            "production_authoritative_manifest_treatment_prohibited": True,
            "no_reasoning_chain_stage_is_production_authorized": True,
            "active_runtime_reasoning_decisions_enabled": False,
            "runtime_evidence_synthesis_enabled": False,
            "recommendation_logic_enabled": False,
            "autonomous_planner_mutation_enabled": False,
        },
        "metadata": {
            "source": "v3_3_runtime_reasoning_chain_contracts_report",
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
    rows = report["reasoning_chain_manifest"]["reasoning_stage_contracts"]
    lines = [
        "# V3.3 Runtime Reasoning Chain Contracts",
        "",
        "Phase 4 establishes deterministic runtime reasoning chain contracts for planning-only runtime intelligence foundations.",
        "",
        "## Boundaries",
        "",
        "Runtime reasoning remains planning-only. Active runtime reasoning decisions, recommendation logic, evidence synthesis, production runtime routing, default manifest consumption, and production-authoritative manifest treatment remain disabled or prohibited.",
        "",
        "## Compatibility",
        "",
        "Every reasoning stage references explicit classification IDs, evidence type IDs, provenance type IDs, and ordered previous stages where required.",
        "",
        "## Summary",
        "",
        f"- Total reasoning stages: `{summary['total_reasoning_chain_stage_contract_count']}`",
        f"- Deterministic ordering valid: `{str(summary['deterministic_ordering_valid']).lower()}`",
        f"- Stable hash valid: `{str(summary['stable_hash_valid']).lower()}`",
        f"- Replay validation passed: `{str(summary['replay_validation_passed']).lower()}`",
        f"- Duplicate detection passed: `{str(summary['duplicate_detection_passed']).lower()}`",
        f"- Invalid evidence references: `{summary['invalid_evidence_reference_count']}`",
        f"- Invalid provenance references: `{summary['invalid_provenance_reference_count']}`",
        f"- Invalid classification references: `{summary['invalid_classification_reference_count']}`",
        f"- Invalid previous-stage references: `{summary['invalid_previous_stage_reference_count']}`",
        f"- Production-authorized stages: `{summary['production_authorized_stage_count']}`",
        "",
        "## Reasoning Stages",
        "",
        "| Rank | Stage | Blocker | Risk | Limitation | Replay Safe |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['deterministic_rank']}` | `{row['stage_label']}` | `{str(row['blocker_capable']).lower()}` | `{str(row['risk_capable']).lower()}` | `{str(row['limitation_capable']).lower()}` | `{str(row['replay_safe']).lower()}` |")
    lines.extend(["", "## Explicit Visibility", ""])
    lines.append("- Blocker-capable stages remain visible.")
    lines.append("- Risk-capable stages remain visible.")
    lines.append("- Limitation-capable stages remain visible.")
    lines.append("- Decision-boundary stage remains visible through `decision_boundary_check`.")
    lines.extend(["", "## Conclusion", "", "These contracts provide deterministic planning-only runtime reasoning lineage. They do not authorize production enablement, runtime consumption, active reasoning decisions, recommendation logic, or autonomous planner mutation."])
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
    parser.add_argument("--output", default="docs/generated/v3_3_runtime_reasoning_chain_contracts_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_3_RUNTIME_REASONING_CHAIN_CONTRACTS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_3_runtime_reasoning_chain_contracts_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
