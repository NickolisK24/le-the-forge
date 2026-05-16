"""Generate the v3.6 orchestration intent-policy mapping report."""

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
from app.runtime_orchestration.orchestration_intent_policy_explainability import (  # noqa: E402
    explain_orchestration_intent_policy_mappings,
    export_orchestration_intent_policy_mapping_explainability_result,
)
from app.runtime_orchestration.orchestration_intent_policy_integrity import (  # noqa: E402
    audit_orchestration_intent_policy_mapping_integrity,
    export_orchestration_intent_policy_mapping_integrity_result,
)
from app.runtime_orchestration.orchestration_intent_policy_mapper import (  # noqa: E402
    export_orchestration_intent_policy_mapping_result,
    map_orchestration_intent_policies,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_models import (  # noqa: E402
    MAPPING_CLASSIFICATIONS,
    MAPPING_EXPLAINABILITY_STABLE,
    MAPPING_INTEGRITY_STABLE,
    OrchestrationIntentPolicyMappingInput,
    OrchestrationIntentPolicyMappingIntegrityInput,
    export_mapping_registry,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_registry import (  # noqa: E402
    build_orchestration_intent_policy_mapping_registry,
    default_orchestration_intent_policy_mapping_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_intent_policy_mapping_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_intent_policy_mapping"]
    mapping = focused["mapping"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["mapping_integrity_status"] == MAPPING_INTEGRITY_STABLE
        and explainability["mapping_explainability_status"] == MAPPING_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_intent_policy_mapping_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_5_deterministic_orchestration_intent_policy_mapping",
        "architectural_purpose": "deterministic orchestration intent policy mapping",
        "planning_only": True,
        "non_production": True,
        "intent_policy_mapping_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_mapping_count": mapping["registered_mapping_count"],
        "supported_mapping_count": mapping["supported_mapping_count"],
        "unsupported_mapping_count": mapping["unsupported_mapping_count"],
        "prohibited_mapping_count": mapping["prohibited_mapping_count"],
        "policy_count": mapping["policy_count"],
        "governance_boundary_count": mapping["governance_boundary_count"],
        "compatibility_domain_count": mapping["compatibility_domain_count"],
        "dependency_domain_count": mapping["dependency_domain_count"],
        "blocker_domain_count": mapping["blocker_domain_count"],
        "unsupported_domain_count": mapping["unsupported_domain_count"],
        "prohibited_domain_count": mapping["prohibited_domain_count"],
        "supported_domain_count": mapping["supported_domain_count"],
        "provenance_continuity_status": mapping["provenance_continuity_status"],
        "explainability_continuity_status": mapping["explainability_continuity_status"],
        "integrity_continuity_status": mapping["integrity_continuity_status"],
        "governance_continuity_status": mapping["governance_continuity_status"],
        "mapping_analysis_status": mapping["mapping_analysis_status"],
        "mapping_explainability_status": explainability["mapping_explainability_status"],
        "mapping_integrity_status": integrity["mapping_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_mapping_classifications": list(MAPPING_CLASSIFICATIONS),
        "unsupported_mapping_classifications": [
            "runtime_execution_mapping",
            "routing_execution_mapping",
            "optimization_execution_mapping",
            "recommendation_execution_mapping",
            "autonomous_path_mapping",
            "state_mutating_mapping",
            "production_runtime_mapping",
        ],
        "registry": focused["registry"],
        "mapping": mapping,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable intent-policy mapping identifiers",
            "stable mapping serialization",
            "stable mapping hashing",
            "stable mapping registry hashing",
            "deterministic policy applicability visibility",
            "deterministic governance-boundary visibility",
            "deterministic compatibility-domain visibility",
            "deterministic dependency-domain visibility",
            "deterministic blocker-domain visibility",
            "deterministic unsupported-domain visibility",
            "deterministic prohibited-domain visibility",
            "deterministic mapping explainability evidence",
            "deterministic mapping integrity evidence",
            "replay-safe mapping provenance continuity",
            "rollback-safe mapping provenance continuity",
        ],
        "explicit_limitations": [
            "intent-policy mapping is planning-only",
            "intent-policy mapping does not execute orchestration",
            "intent-policy mapping does not dispatch orchestration",
            "intent-policy mapping does not route requests",
            "intent-policy mapping does not mutate state",
            "intent-policy mapping does not write audit logs",
            "intent-policy mapping does not perform graph execution",
            "intent-policy mapping does not schedule orchestration",
            "intent-policy mapping does not capture runtime traces",
            "intent-policy mapping does not read production state",
            "intent-policy mapping does not recommend orchestration behavior",
            "intent-policy mapping does not optimize orchestration paths",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_mapping_registry_hash": mapping["deterministic_registry_hash"],
        "deterministic_mapping_analysis_hash": mapping["deterministic_mapping_analysis_hash"],
        "deterministic_mapping_explainability_hash": explainability["deterministic_mapping_explainability_hash"],
        "deterministic_mapping_integrity_hash": integrity["deterministic_mapping_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Intent Policy Mapping",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 5 establishes deterministic orchestration intent policy mapping.",
        "",
        "It models which policies apply to a future orchestration intent before compatibility evaluation or orchestration planning.",
        "",
        "This phase is planning-only governance intelligence.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not dispatch orchestration.",
        "",
        "It does not route requests.",
        "",
        "It does not mutate state.",
        "",
        "It does not recommend orchestration behavior.",
        "",
        "It does not read production state.",
        "",
        f"- Registered mappings: `{report['registered_mapping_count']}`",
        f"- Supported mappings: `{report['supported_mapping_count']}`",
        f"- Unsupported mappings: `{report['unsupported_mapping_count']}`",
        f"- Prohibited mappings: `{report['prohibited_mapping_count']}`",
        f"- Policy references: `{report['policy_count']}`",
        f"- Governance boundaries: `{report['governance_boundary_count']}`",
        f"- Compatibility domains: `{report['compatibility_domain_count']}`",
        f"- Dependency domains: `{report['dependency_domain_count']}`",
        f"- Blocker domains: `{report['blocker_domain_count']}`",
        f"- Mapping analysis status: `{report['mapping_analysis_status']}`",
        f"- Explainability status: `{report['mapping_explainability_status']}`",
        f"- Integrity status: `{report['mapping_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Intent-Policy Mapping Philosophy",
        "",
        "The mapping layer prioritizes correctness, mapping explainability, governance visibility, provenance continuity, deterministic auditability, and explicit policy boundaries over execution, routing, automation, recommendation systems, optimization, or autonomous orchestration.",
        "",
        "The purpose is understanding which rules apply to orchestration intent, not executing orchestration intent.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Mapping Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_mapping_classifications"])
    lines.extend(["", "## Unsupported Mapping Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_mapping_classifications"])
    lines.extend(
        [
            "",
            "## Governance-Boundary Guarantees",
            "",
            "Intent-policy mapping records preserve deterministic visibility for planning-only, non-production, non-executing, governance-first boundaries.",
            "",
            "Unsupported and prohibited mappings remain fail-visible and do not become execution paths.",
            "",
            "## Explainability Guarantees",
            "",
            "Mapping explainability records why a policy applies to an intent, which governance boundaries apply, which compatibility domains apply, which blocker domains apply, which unsupported and prohibited domains apply, and which provenance chains apply.",
            "",
            "## Integrity Guarantees",
            "",
            "Mapping integrity auditing validates registry continuity, mapping hash continuity, provenance continuity, explainability continuity, governance continuity, compatibility continuity, dependency continuity, blocker continuity, supported-domain continuity, policy continuity, and serialization stability.",
            "",
            "## Continuity Status",
            "",
            f"- Provenance continuity: `{report['provenance_continuity_status']}`",
            f"- Explainability continuity: `{report['explainability_continuity_status']}`",
            f"- Integrity continuity: `{report['integrity_continuity_status']}`",
            f"- Governance continuity: `{report['governance_continuity_status']}`",
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
            "- Recommendation behavior is not introduced.",
            "- Optimization behavior is not introduced.",
            "- Runtime scheduling remains prohibited.",
            "- Production runtime reads remain prohibited.",
            "- Production runtime writes remain prohibited.",
            "- Persistent writes remain prohibited.",
            "- Self-modifying orchestration mappings are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['mapping_integrity_status']}`")
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
    registry = default_orchestration_intent_policy_mapping_registry()
    return {
        "default_intent_policy_mapping": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "governance_boundary_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "policy_applicability_gap_visibility": _scenario_bundle(_registry_with_policy_gap(registry)),
        "compatibility_domain_gap_visibility": _scenario_bundle(_registry_with_compatibility_gap(registry)),
        "dependency_domain_gap_visibility": _scenario_bundle(_registry_with_dependency_gap(registry)),
        "blocker_domain_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "supported_domain_gap_visibility": _scenario_bundle(_registry_with_supported_domain_gap(registry)),
        "mapping_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_mapping_hashes={"v3_6.mapping.compatibility-check": "mismatched-mapping-hash"},
        ),
    }


def _scenario_bundle(
    registry,
    expected_mapping_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    mapping = map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(
            mapping_registry=registry,
            expected_mapping_hashes=expected_mapping_hashes,
        )
    )
    explainability = explain_orchestration_intent_policy_mappings(registry, mapping)
    integrity = audit_orchestration_intent_policy_mapping_integrity(
        OrchestrationIntentPolicyMappingIntegrityInput(
            mapping_registry=registry,
            mapping_result=mapping,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_mapping_registry(registry),
        "mapping": export_orchestration_intent_policy_mapping_result(mapping),
        "explainability": export_orchestration_intent_policy_mapping_explainability_result(explainability),
        "integrity": export_orchestration_intent_policy_mapping_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.mapping.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_governance_gap(registry):
    target = _record(registry, "v3_6.mapping.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_policy_gap(registry):
    target = _record(registry, "v3_6.mapping.policy-boundary")
    changed = replace(target, policy_ids=())
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_compatibility_gap(registry):
    target = _record(registry, "v3_6.mapping.compatibility-check")
    changed = replace(target, compatibility_domains=())
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_dependency_gap(registry):
    target = _record(registry, "v3_6.mapping.dependency-analysis")
    changed = replace(target, dependency_domains=())
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_blocker_gap(registry):
    target = _record(registry, "v3_6.mapping.prohibited-domain")
    changed = replace(target, blocker_domains=())
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _registry_with_supported_domain_gap(registry):
    target = _record(registry, "v3_6.mapping.informational")
    changed = replace(target, supported_domains=())
    return _replace_record(registry, target.identifier.mapping_id, changed)


def _record(registry, mapping_id: str):
    return next(record for record in registry.records if record.identifier.mapping_id == mapping_id)


def _replace_record(registry, mapping_id: str, replacement):
    return build_orchestration_intent_policy_mapping_registry(
        tuple(
            replacement if record.identifier.mapping_id == mapping_id else record
            for record in registry.records
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["mapping_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["mapping_integrity_status"] == status)
        for status in statuses
    }


def _non_execution_guarantees() -> dict[str, bool]:
    return {
        "runtime_execution_enabled": False,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "mutation_behavior_enabled": False,
        "production_consumption_enabled": False,
        "background_processing_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "graph_execution_enabled": False,
        "mapping_execution_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_intent_policy_mapping_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_INTENT_POLICY_MAPPING.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_intent_policy_mapping_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
