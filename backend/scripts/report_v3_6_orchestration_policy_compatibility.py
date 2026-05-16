"""Generate the v3.6 orchestration policy compatibility matrix report."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration.orchestration_policy_compatibility_evaluator import (  # noqa: E402
    evaluate_orchestration_policy_compatibility_matrix,
    export_orchestration_policy_compatibility_evaluation_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_explainability import (  # noqa: E402
    explain_orchestration_policy_compatibility,
    export_orchestration_policy_compatibility_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_integrity import (  # noqa: E402
    audit_orchestration_policy_compatibility_integrity,
    export_orchestration_policy_compatibility_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_models import (  # noqa: E402
    COMPATIBILITY_EXPLAINABILITY_STABLE,
    COMPATIBILITY_INTEGRITY_STABLE,
    COMPATIBILITY_STATES,
    OrchestrationPolicyCompatibilityEvaluationInput,
    OrchestrationPolicyCompatibilityIntegrityInput,
    export_compatibility_registry,
)
from app.runtime_orchestration.orchestration_policy_compatibility_registry import (  # noqa: E402
    build_orchestration_policy_compatibility_registry,
    default_orchestration_policy_compatibility_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_policy_compatibility_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_compatibility_matrix"]
    evaluation = focused["evaluation"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_STABLE
        and explainability["compatibility_explainability_status"] == COMPATIBILITY_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_policy_compatibility_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_2_deterministic_orchestration_policy_compatibility_matrix",
        "architectural_purpose": "deterministic orchestration policy compatibility intelligence",
        "planning_only": True,
        "non_production": True,
        "compatibility_intelligence_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_compatibility_relationships": evaluation["registered_relationship_count"],
        "compatible_relationship_count": evaluation["compatible_relationship_count"],
        "incompatible_relationship_count": evaluation["incompatible_relationship_count"],
        "prohibited_relationship_count": evaluation["prohibited_relationship_count"],
        "unsupported_relationship_count": evaluation["unsupported_relationship_count"],
        "dependency_conflict_count": evaluation["dependency_conflict_count"],
        "governance_conflict_count": evaluation["governance_conflict_count"],
        "blocker_chain_count": evaluation["blocker_chain_count"],
        "blocker_count": evaluation["blocker_count"],
        "provenance_continuity_status": evaluation["provenance_continuity_status"],
        "governance_continuity_status": evaluation["governance_continuity_status"],
        "integrity_continuity_status": evaluation["integrity_continuity_status"],
        "explainability_continuity_status": evaluation["explainability_continuity_status"],
        "compatibility_evaluation_status": evaluation["compatibility_evaluation_status"],
        "compatibility_explainability_status": explainability["compatibility_explainability_status"],
        "compatibility_integrity_status": integrity["compatibility_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_compatibility_states": list(COMPATIBILITY_STATES),
        "registry": focused["registry"],
        "evaluation": evaluation,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable compatibility relationship identifiers",
            "stable compatibility relationship serialization",
            "stable compatibility relationship hashing",
            "stable compatibility registry hashing",
            "deterministic pairwise compatibility evaluation",
            "deterministic multi-policy compatibility evaluation",
            "deterministic compatibility blocker-chain visibility",
            "deterministic compatibility explainability evidence",
            "deterministic compatibility integrity evidence",
            "replay-safe compatibility provenance continuity",
            "rollback-safe compatibility provenance continuity",
        ],
        "explicit_limitations": [
            "compatibility intelligence is planning-only",
            "compatibility intelligence does not execute orchestration",
            "compatibility intelligence does not dispatch orchestration",
            "compatibility intelligence does not route requests",
            "compatibility intelligence does not mutate state",
            "compatibility intelligence does not write audit logs",
            "compatibility intelligence does not perform graph execution",
            "compatibility intelligence does not schedule orchestration",
            "compatibility intelligence does not capture runtime traces",
            "compatibility intelligence does not read production state",
            "compatibility intelligence does not optimize orchestration paths",
            "compatibility intelligence does not autonomously evaluate execution paths",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_compatibility_registry_hash": evaluation["deterministic_registry_hash"],
        "deterministic_compatibility_evaluation_hash": evaluation["deterministic_compatibility_evaluation_hash"],
        "deterministic_compatibility_explainability_hash": explainability["deterministic_compatibility_explainability_hash"],
        "deterministic_compatibility_integrity_hash": integrity["deterministic_compatibility_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Policy Compatibility Matrix",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 2 establishes deterministic orchestration policy compatibility intelligence.",
        "",
        "It models which orchestration policies may coexist and why without enabling orchestration behavior.",
        "",
        "This phase is governance intelligence only.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not dispatch orchestration.",
        "",
        "It does not route requests.",
        "",
        "It does not mutate state.",
        "",
        "It does not write audit logs.",
        "",
        "It does not perform graph execution.",
        "",
        "It does not schedule orchestration.",
        "",
        "It does not capture runtime traces.",
        "",
        "It does not read production state.",
        "",
        f"- Registered compatibility relationships: `{report['registered_compatibility_relationships']}`",
        f"- Compatible relationships: `{report['compatible_relationship_count']}`",
        f"- Incompatible relationships: `{report['incompatible_relationship_count']}`",
        f"- Prohibited relationships: `{report['prohibited_relationship_count']}`",
        f"- Unsupported relationships: `{report['unsupported_relationship_count']}`",
        f"- Dependency conflicts: `{report['dependency_conflict_count']}`",
        f"- Governance conflicts: `{report['governance_conflict_count']}`",
        f"- Blocker chains: `{report['blocker_chain_count']}`",
        f"- Compatibility evaluation status: `{report['compatibility_evaluation_status']}`",
        f"- Explainability status: `{report['compatibility_explainability_status']}`",
        f"- Integrity status: `{report['compatibility_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Compatibility Intelligence Philosophy",
        "",
        "The matrix prioritizes correctness, compatibility visibility, governance continuity, provenance continuity, explainability, and deterministic integrity over execution, routing, optimization, autonomous orchestration, or runtime intelligence.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Compatibility States", ""])
    lines.extend(f"- `{state}`" for state in report["supported_compatibility_states"])
    lines.extend(
        [
            "",
            "## Prohibited Compatibility States",
            "",
            "- `compatibility_prohibited` relationships remain fail-visible.",
            "- Prohibited pairings do not authorize execution, routing, production reads, or runtime behavior.",
            "",
            "## Unsupported Compatibility States",
            "",
            "- `compatibility_unsupported` relationships remain fail-visible.",
            "- Unsupported combinations do not become recommendations or routing decisions.",
            "",
            "## Blocker-Chain Guarantees",
            "",
            "Blocker chains preserve deterministic visibility for incompatibility, prohibited pairings, unsupported combinations, dependency conflicts, and governance conflicts.",
            "",
            "## Explainability Guarantees",
            "",
            "Compatibility explainability records why policies are compatible, incompatible, prohibited, unsupported, dependency-blocked, or governance-blocked.",
            "",
            "Dependency conflict chains, governance conflict chains, continuity conflicts, blocker chains, provenance references, and integrity references remain deterministic.",
            "",
            "## Integrity Guarantees",
            "",
            "Compatibility integrity auditing validates registry continuity, relationship hash continuity, provenance continuity, dependency continuity, governance continuity, explainability continuity, classification continuity, blocker-chain continuity, and serialization stability.",
            "",
            "## Continuity Status",
            "",
            f"- Provenance continuity: `{report['provenance_continuity_status']}`",
            f"- Governance continuity: `{report['governance_continuity_status']}`",
            f"- Integrity continuity: `{report['integrity_continuity_status']}`",
            f"- Explainability continuity: `{report['explainability_continuity_status']}`",
            "",
            "## Explicit Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["explicit_limitations"])
    lines.extend(
        [
            "",
            "## Explicit Prohibitions",
            "",
            "- Orchestration execution remains prohibited.",
            "- Runtime dispatch remains prohibited.",
            "- Graph execution remains prohibited.",
            "- Orchestration routing remains prohibited.",
            "- Autonomous orchestration remains unsupported.",
            "- Runtime scheduling remains prohibited.",
            "- Production runtime reads remain prohibited.",
            "- Production runtime writes remain prohibited.",
            "- Persistent writes remain prohibited.",
            "- Recommendation, optimization, and decision systems are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['compatibility_integrity_status']}`")
    lines.extend(
        [
            "",
            "## Replay and Rollback Safety",
            "",
            f"- Replay safety confirmed: `{report['replay_safety_confirmation']}`",
            f"- Rollback safety confirmed: `{report['rollback_safety_confirmation']}`",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    registry = default_orchestration_policy_compatibility_registry()
    provenance_gap_registry = _registry_with_provenance_gap(registry)
    dependency_gap_registry = _registry_with_dependency_gap(registry)
    governance_gap_registry = _registry_with_governance_gap(registry)
    explainability_gap_registry = _registry_with_explainability_gap(registry)
    return {
        "default_compatibility_matrix": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(provenance_gap_registry),
        "dependency_conflict_visibility_gap": _scenario_bundle(dependency_gap_registry),
        "governance_conflict_visibility_gap": _scenario_bundle(governance_gap_registry),
        "relationship_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_relationship_hashes={"v3_6.compat.modeling-governance.compatible": "mismatched-relationship-hash"},
        ),
        "explainability_gap_visibility": _scenario_bundle(explainability_gap_registry),
    }


def _scenario_bundle(
    registry,
    expected_relationship_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    evaluation = evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(
            compatibility_registry=registry,
            expected_relationship_hashes=expected_relationship_hashes,
        )
    )
    explainability = explain_orchestration_policy_compatibility(registry, evaluation)
    integrity = audit_orchestration_policy_compatibility_integrity(
        OrchestrationPolicyCompatibilityIntegrityInput(
            compatibility_registry=registry,
            evaluation_result=evaluation,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_compatibility_registry(registry),
        "evaluation": export_orchestration_policy_compatibility_evaluation_result(evaluation),
        "explainability": export_orchestration_policy_compatibility_explainability_result(explainability),
        "integrity": export_orchestration_policy_compatibility_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_relationship(registry, target.identifier.relationship_id, changed)


def _registry_with_dependency_gap(registry):
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.integrity-execution.dependency-blocked")
    changed = replace(target, dependency_conflicts=())
    return _replace_relationship(registry, target.identifier.relationship_id, changed)


def _registry_with_governance_gap(registry):
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.governance-production-runtime.governance-blocked")
    changed = replace(target, governance_conflicts=())
    return _replace_relationship(registry, target.identifier.relationship_id, changed)


def _registry_with_explainability_gap(registry):
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(target, support_rationale=(), blocker_reasons=(), blocker_chains=())
    return build_orchestration_policy_compatibility_registry((changed,))


def _replace_relationship(registry, relationship_id: str, replacement):
    return build_orchestration_policy_compatibility_registry(
        tuple(
            replacement if relationship.identifier.relationship_id == relationship_id else relationship
            for relationship in registry.relationships
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["compatibility_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["compatibility_integrity_status"] == status)
        for status in statuses
    }


def _non_execution_guarantees() -> dict[str, bool]:
    return {
        "runtime_execution_enabled": False,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "mutation_behavior_enabled": False,
        "audit_log_writing_enabled": False,
        "production_consumption_enabled": False,
        "graph_execution_enabled": False,
        "graph_traversal_behavior_enabled": False,
        "scheduling_behavior_enabled": False,
        "orchestration_dispatch_enabled": False,
        "runtime_trace_capture_enabled": False,
        "production_state_reads_enabled": False,
        "live_replay_enabled": False,
        "persistent_audit_storage_enabled": False,
        "compatibility_execution_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_policy_compatibility_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_POLICY_COMPATIBILITY_MATRIX.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_policy_compatibility_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
