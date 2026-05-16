"""Generate the v3.6 orchestration preflight evaluation report."""

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
from app.runtime_orchestration.orchestration_preflight_evaluator import (  # noqa: E402
    evaluate_orchestration_preflight,
    export_orchestration_preflight_evaluation_result,
)
from app.runtime_orchestration.orchestration_preflight_explainability import (  # noqa: E402
    explain_orchestration_preflight,
    export_orchestration_preflight_explainability_result,
)
from app.runtime_orchestration.orchestration_preflight_integrity import (  # noqa: E402
    audit_orchestration_preflight_integrity,
    export_orchestration_preflight_integrity_result,
)
from app.runtime_orchestration.orchestration_preflight_models import (  # noqa: E402
    PREFLIGHT_EXPLAINABILITY_STABLE,
    PREFLIGHT_INTEGRITY_STABLE,
    PREFLIGHT_STATES,
    OrchestrationPreflightEvaluationInput,
    OrchestrationPreflightIntegrityInput,
    export_preflight_registry,
)
from app.runtime_orchestration.orchestration_preflight_registry import (  # noqa: E402
    build_orchestration_preflight_registry,
    default_orchestration_preflight_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_preflight_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_preflight_evaluation"]
    evaluation = focused["evaluation"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_STABLE
        and explainability["preflight_explainability_status"] == PREFLIGHT_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_preflight_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_6_deterministic_orchestration_preflight_evaluation",
        "architectural_purpose": "deterministic orchestration preflight evaluation",
        "planning_only": True,
        "non_production": True,
        "preflight_evaluation_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_preflight_count": evaluation["registered_preflight_count"],
        "supported_preflight_count": evaluation["supported_preflight_count"],
        "unsupported_preflight_count": evaluation["unsupported_preflight_count"],
        "prohibited_preflight_count": evaluation["prohibited_preflight_count"],
        "governance_blocked_count": evaluation["governance_blocked_count"],
        "compatibility_blocked_count": evaluation["compatibility_blocked_count"],
        "dependency_blocked_count": evaluation["dependency_blocked_count"],
        "continuity_blocked_count": evaluation["continuity_blocked_count"],
        "provenance_blocked_count": evaluation["provenance_blocked_count"],
        "explainability_blocked_count": evaluation["explainability_blocked_count"],
        "policy_count": evaluation["policy_count"],
        "governance_boundary_count": evaluation["governance_boundary_count"],
        "compatibility_domain_count": evaluation["compatibility_domain_count"],
        "dependency_domain_count": evaluation["dependency_domain_count"],
        "blocker_domain_count": evaluation["blocker_domain_count"],
        "unsupported_domain_count": evaluation["unsupported_domain_count"],
        "prohibited_domain_count": evaluation["prohibited_domain_count"],
        "supported_domain_count": evaluation["supported_domain_count"],
        "provenance_continuity_status": evaluation["provenance_continuity_status"],
        "explainability_continuity_status": evaluation["explainability_continuity_status"],
        "integrity_continuity_status": evaluation["integrity_continuity_status"],
        "governance_continuity_status": evaluation["governance_continuity_status"],
        "preflight_evaluation_status": evaluation["preflight_evaluation_status"],
        "preflight_explainability_status": explainability["preflight_explainability_status"],
        "preflight_integrity_status": integrity["preflight_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_preflight_classifications": list(PREFLIGHT_STATES),
        "unsupported_preflight_classifications": [
            "runtime_execution_preflight",
            "routing_execution_preflight",
            "execution_planning_preflight",
            "optimization_execution_preflight",
            "recommendation_execution_preflight",
            "autonomous_path_preflight",
            "state_mutating_preflight",
            "production_runtime_preflight",
        ],
        "registry": focused["registry"],
        "evaluation": evaluation,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable preflight identifiers",
            "stable preflight serialization",
            "stable preflight hashing",
            "stable preflight registry hashing",
            "deterministic theoretical supportability visibility",
            "deterministic governance-boundary visibility",
            "deterministic compatibility-domain visibility",
            "deterministic dependency-domain visibility",
            "deterministic blocker-domain visibility",
            "deterministic unsupported-domain visibility",
            "deterministic prohibited-domain visibility",
            "deterministic preflight explainability evidence",
            "deterministic preflight integrity evidence",
            "replay-safe preflight provenance continuity",
            "rollback-safe preflight provenance continuity",
        ],
        "explicit_limitations": [
            "preflight evaluation is planning-only",
            "preflight evaluation does not execute orchestration",
            "preflight evaluation does not dispatch orchestration",
            "preflight evaluation does not route requests",
            "preflight evaluation does not mutate state",
            "preflight evaluation does not write audit logs",
            "preflight evaluation does not perform graph execution",
            "preflight evaluation does not schedule orchestration",
            "preflight evaluation does not capture runtime traces",
            "preflight evaluation does not read production state",
            "preflight evaluation does not recommend orchestration behavior",
            "preflight evaluation does not optimize orchestration paths",
            "preflight evaluation does not create execution plans",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_preflight_registry_hash": evaluation["deterministic_registry_hash"],
        "deterministic_preflight_evaluation_hash": evaluation["deterministic_preflight_evaluation_hash"],
        "deterministic_preflight_explainability_hash": explainability["deterministic_preflight_explainability_hash"],
        "deterministic_preflight_integrity_hash": integrity["deterministic_preflight_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Preflight Evaluation",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 6 establishes deterministic orchestration preflight evaluation.",
        "",
        "It models which governance and compatibility state would apply if an orchestration intent were theoretically evaluated.",
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
        "It does not create execution plans.",
        "",
        "It does not read production state.",
        "",
        f"- Registered preflight evaluations: `{report['registered_preflight_count']}`",
        f"- Supported preflight evaluations: `{report['supported_preflight_count']}`",
        f"- Unsupported preflight evaluations: `{report['unsupported_preflight_count']}`",
        f"- Prohibited preflight evaluations: `{report['prohibited_preflight_count']}`",
        f"- Governance-blocked evaluations: `{report['governance_blocked_count']}`",
        f"- Compatibility-blocked evaluations: `{report['compatibility_blocked_count']}`",
        f"- Dependency-blocked evaluations: `{report['dependency_blocked_count']}`",
        f"- Blocker domains: `{report['blocker_domain_count']}`",
        f"- Preflight evaluation status: `{report['preflight_evaluation_status']}`",
        f"- Explainability status: `{report['preflight_explainability_status']}`",
        f"- Integrity status: `{report['preflight_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Preflight Evaluation Philosophy",
        "",
        "The preflight layer prioritizes correctness, preflight visibility, governance visibility, blocker visibility, explainability, provenance continuity, and deterministic auditability over execution, routing, automation, recommendation systems, optimization, or autonomous orchestration.",
        "",
        "The purpose is understanding theoretical orchestration state, not performing orchestration.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Preflight Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_preflight_classifications"])
    lines.extend(["", "## Unsupported Preflight Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_preflight_classifications"])
    lines.extend(
        [
            "",
            "## Governance-Boundary Guarantees",
            "",
            "Preflight records preserve deterministic visibility for planning-only, non-production, non-executing, governance-first boundaries.",
            "",
            "Unsupported, prohibited, and blocked preflight states remain fail-visible and do not become execution paths.",
            "",
            "## Explainability Guarantees",
            "",
            "Preflight explainability records why a state is supported, unsupported, prohibited, or blocked; which governance boundaries apply; which compatibility domains apply; which blockers apply; which unsupported domains apply; which provenance chains apply; and why the evaluation result exists.",
            "",
            "## Integrity Guarantees",
            "",
            "Preflight integrity auditing validates registry continuity, preflight hash continuity, provenance continuity, explainability continuity, governance continuity, compatibility continuity, dependency continuity, blocker continuity, supported-domain continuity, policy continuity, and serialization stability.",
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
            "- Execution planning is not introduced.",
            "- Hidden orchestration pathways are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['preflight_integrity_status']}`")
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
    registry = default_orchestration_preflight_registry()
    return {
        "default_preflight_evaluation": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "governance_boundary_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "policy_reference_gap_visibility": _scenario_bundle(_registry_with_policy_gap(registry)),
        "compatibility_domain_gap_visibility": _scenario_bundle(_registry_with_compatibility_gap(registry)),
        "dependency_domain_gap_visibility": _scenario_bundle(_registry_with_dependency_gap(registry)),
        "blocker_domain_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "supported_domain_gap_visibility": _scenario_bundle(_registry_with_supported_domain_gap(registry)),
        "preflight_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_preflight_hashes={"v3_6.preflight.compatibility-check": "mismatched-preflight-hash"},
        ),
    }


def _scenario_bundle(
    registry,
    expected_preflight_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    evaluation = evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(
            preflight_registry=registry,
            expected_preflight_hashes=expected_preflight_hashes,
        )
    )
    explainability = explain_orchestration_preflight(registry, evaluation)
    integrity = audit_orchestration_preflight_integrity(
        OrchestrationPreflightIntegrityInput(
            preflight_registry=registry,
            evaluation_result=evaluation,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_preflight_registry(registry),
        "evaluation": export_orchestration_preflight_evaluation_result(evaluation),
        "explainability": export_orchestration_preflight_explainability_result(explainability),
        "integrity": export_orchestration_preflight_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.preflight.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_governance_gap(registry):
    target = _record(registry, "v3_6.preflight.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_policy_gap(registry):
    target = _record(registry, "v3_6.preflight.compatibility-check")
    changed = replace(target, policy_ids=())
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_compatibility_gap(registry):
    target = _record(registry, "v3_6.preflight.policy-boundary")
    changed = replace(target, compatibility_domains=())
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_dependency_gap(registry):
    target = _record(registry, "v3_6.preflight.dependency-analysis")
    changed = replace(target, dependency_domains=())
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_blocker_gap(registry):
    target = _record(registry, "v3_6.preflight.prohibited-domain")
    changed = replace(target, blocker_domains=())
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _registry_with_supported_domain_gap(registry):
    target = _record(registry, "v3_6.preflight.informational")
    changed = replace(target, supported_domains=())
    return _replace_record(registry, target.identifier.preflight_id, changed)


def _record(registry, preflight_id: str):
    return next(record for record in registry.records if record.identifier.preflight_id == preflight_id)


def _replace_record(registry, preflight_id: str, replacement):
    return build_orchestration_preflight_registry(
        tuple(
            replacement if record.identifier.preflight_id == preflight_id else record
            for record in registry.records
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["preflight_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["preflight_integrity_status"] == status)
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
        "preflight_execution_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_preflight_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_PREFLIGHT_EVALUATION.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_preflight_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
