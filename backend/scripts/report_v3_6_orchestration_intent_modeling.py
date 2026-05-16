"""Generate the v3.6 orchestration intent modeling report."""

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
from app.runtime_orchestration.orchestration_intent_classifier import (  # noqa: E402
    classify_orchestration_intents,
    export_orchestration_intent_classification_result,
)
from app.runtime_orchestration.orchestration_intent_explainability import (  # noqa: E402
    explain_orchestration_intents,
    export_orchestration_intent_explainability_result,
)
from app.runtime_orchestration.orchestration_intent_integrity import (  # noqa: E402
    audit_orchestration_intent_integrity,
    export_orchestration_intent_integrity_result,
)
from app.runtime_orchestration.orchestration_intent_models import (  # noqa: E402
    INTENT_EXPLAINABILITY_STABLE,
    INTENT_INTEGRITY_STABLE,
    INTENT_TYPES,
    OrchestrationIntentClassificationInput,
    OrchestrationIntentIntegrityInput,
    export_intent_registry,
)
from app.runtime_orchestration.orchestration_intent_registry import (  # noqa: E402
    build_orchestration_intent_registry,
    default_orchestration_intent_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_intent_modeling_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_intent_modeling"]
    classification = focused["classification"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["intent_integrity_status"] == INTENT_INTEGRITY_STABLE
        and explainability["intent_explainability_status"] == INTENT_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_intent_modeling_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_4_deterministic_orchestration_intent_modeling",
        "architectural_purpose": "deterministic orchestration intent modeling",
        "planning_only": True,
        "non_production": True,
        "intent_modeling_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_intent_count": classification["registered_intent_count"],
        "supported_intent_count": classification["supported_intent_count"],
        "unsupported_intent_count": classification["unsupported_intent_count"],
        "prohibited_intent_count": classification["prohibited_intent_count"],
        "governance_boundary_count": classification["governance_boundary_count"],
        "compatibility_domain_count": classification["compatibility_domain_count"],
        "dependency_domain_count": classification["dependency_domain_count"],
        "blocker_domain_count": classification["blocker_domain_count"],
        "unsupported_domain_count": classification["unsupported_domain_count"],
        "prohibited_domain_count": classification["prohibited_domain_count"],
        "supported_domain_count": classification["supported_domain_count"],
        "provenance_continuity_status": classification["provenance_continuity_status"],
        "explainability_continuity_status": classification["explainability_continuity_status"],
        "integrity_continuity_status": classification["integrity_continuity_status"],
        "governance_continuity_status": classification["governance_continuity_status"],
        "intent_classification_status": classification["intent_classification_status"],
        "intent_explainability_status": explainability["intent_explainability_status"],
        "intent_integrity_status": integrity["intent_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_intent_classifications": list(INTENT_TYPES),
        "unsupported_intent_classifications": [
            "runtime_execution_intent",
            "routing_execution_intent",
            "optimization_execution_intent",
            "recommendation_execution_intent",
            "autonomous_path_evaluation_intent",
            "state_mutating_intent",
        ],
        "registry": focused["registry"],
        "classification": classification,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable intent identifiers",
            "stable intent serialization",
            "stable intent hashing",
            "stable intent registry hashing",
            "deterministic intent-type classification",
            "deterministic governance-boundary visibility",
            "deterministic compatibility-domain visibility",
            "deterministic dependency-domain visibility",
            "deterministic blocker-domain visibility",
            "deterministic unsupported-domain visibility",
            "deterministic prohibited-domain visibility",
            "deterministic intent explainability evidence",
            "deterministic intent integrity evidence",
            "replay-safe intent provenance continuity",
            "rollback-safe intent provenance continuity",
        ],
        "explicit_limitations": [
            "intent modeling is planning-only",
            "intent modeling does not execute orchestration",
            "intent modeling does not dispatch orchestration",
            "intent modeling does not route requests",
            "intent modeling does not mutate state",
            "intent modeling does not write audit logs",
            "intent modeling does not perform graph execution",
            "intent modeling does not schedule orchestration",
            "intent modeling does not capture runtime traces",
            "intent modeling does not read production state",
            "intent modeling does not recommend orchestration behavior",
            "intent modeling does not optimize orchestration paths",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_intent_registry_hash": classification["deterministic_registry_hash"],
        "deterministic_intent_classification_hash": classification["deterministic_intent_classification_hash"],
        "deterministic_intent_explainability_hash": explainability["deterministic_intent_explainability_hash"],
        "deterministic_intent_integrity_hash": integrity["deterministic_intent_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Intent Modeling",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 4 establishes deterministic orchestration intent modeling.",
        "",
        "It models what a future orchestration request is attempting to do before compatibility or allowance evaluation.",
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
        f"- Registered intents: `{report['registered_intent_count']}`",
        f"- Supported intents: `{report['supported_intent_count']}`",
        f"- Unsupported intents: `{report['unsupported_intent_count']}`",
        f"- Prohibited intents: `{report['prohibited_intent_count']}`",
        f"- Governance boundaries: `{report['governance_boundary_count']}`",
        f"- Compatibility domains: `{report['compatibility_domain_count']}`",
        f"- Dependency domains: `{report['dependency_domain_count']}`",
        f"- Blocker domains: `{report['blocker_domain_count']}`",
        f"- Intent classification status: `{report['intent_classification_status']}`",
        f"- Explainability status: `{report['intent_explainability_status']}`",
        f"- Integrity status: `{report['intent_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Intent Modeling Philosophy",
        "",
        "The intent layer prioritizes correctness, intent visibility, governance visibility, explainability, provenance continuity, and deterministic auditability over execution, routing, automation, recommendation systems, optimization, or autonomous orchestration.",
        "",
        "The purpose is understanding intent, not executing intent.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Intent Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_intent_classifications"])
    lines.extend(["", "## Unsupported Intent Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_intent_classifications"])
    lines.extend(
        [
            "",
            "## Governance-Boundary Guarantees",
            "",
            "Intent records preserve deterministic visibility for planning-only, non-production, non-executing, governance-first boundaries.",
            "",
            "Unsupported and prohibited domains remain fail-visible and do not become execution paths.",
            "",
            "## Explainability Guarantees",
            "",
            "Intent explainability records what an intent is attempting to do, what policy domains it touches, what compatibility domains it touches, what governance boundaries apply, what blockers may apply, and what provenance chains apply.",
            "",
            "## Integrity Guarantees",
            "",
            "Intent integrity auditing validates registry continuity, intent hash continuity, provenance continuity, explainability continuity, governance continuity, compatibility continuity, dependency continuity, blocker continuity, supported-domain continuity, and serialization stability.",
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
            "- Self-modifying orchestration logic is not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['intent_integrity_status']}`")
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
    registry = default_orchestration_intent_registry()
    return {
        "default_intent_modeling": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "governance_boundary_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "compatibility_domain_gap_visibility": _scenario_bundle(_registry_with_compatibility_gap(registry)),
        "dependency_domain_gap_visibility": _scenario_bundle(_registry_with_dependency_gap(registry)),
        "blocker_domain_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "supported_domain_gap_visibility": _scenario_bundle(_registry_with_supported_domain_gap(registry)),
        "intent_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_intent_hashes={"v3_6.intent.compatibility-check": "mismatched-intent-hash"},
        ),
    }


def _scenario_bundle(
    registry,
    expected_intent_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    classification = classify_orchestration_intents(
        OrchestrationIntentClassificationInput(
            intent_registry=registry,
            expected_intent_hashes=expected_intent_hashes,
        )
    )
    explainability = explain_orchestration_intents(registry, classification)
    integrity = audit_orchestration_intent_integrity(
        OrchestrationIntentIntegrityInput(
            intent_registry=registry,
            classification_result=classification,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_intent_registry(registry),
        "classification": export_orchestration_intent_classification_result(classification),
        "explainability": export_orchestration_intent_explainability_result(explainability),
        "integrity": export_orchestration_intent_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.intent.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_record(registry, target.identifier.intent_id, changed)


def _registry_with_governance_gap(registry):
    target = _record(registry, "v3_6.intent.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    return _replace_record(registry, target.identifier.intent_id, changed)


def _registry_with_compatibility_gap(registry):
    target = _record(registry, "v3_6.intent.compatibility-check")
    changed = replace(target, compatibility_domains=())
    return _replace_record(registry, target.identifier.intent_id, changed)


def _registry_with_dependency_gap(registry):
    target = _record(registry, "v3_6.intent.dependency-analysis")
    changed = replace(target, dependency_domains=())
    return _replace_record(registry, target.identifier.intent_id, changed)


def _registry_with_blocker_gap(registry):
    target = _record(registry, "v3_6.intent.prohibited-domain")
    changed = replace(target, blocker_domains=())
    return _replace_record(registry, target.identifier.intent_id, changed)


def _registry_with_supported_domain_gap(registry):
    target = _record(registry, "v3_6.intent.informational")
    changed = replace(target, supported_domains=())
    return _replace_record(registry, target.identifier.intent_id, changed)


def _record(registry, intent_id: str):
    return next(record for record in registry.records if record.identifier.intent_id == intent_id)


def _replace_record(registry, intent_id: str, replacement):
    return build_orchestration_intent_registry(
        tuple(
            replacement if record.identifier.intent_id == intent_id else record
            for record in registry.records
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["intent_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["intent_integrity_status"] == status)
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_intent_modeling_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_INTENT_MODELING.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_intent_modeling_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
