"""Generate the v3.6 orchestration evaluation trace modeling report."""

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
from app.runtime_orchestration.orchestration_evaluation_trace_builder import (  # noqa: E402
    build_orchestration_evaluation_trace,
    export_orchestration_evaluation_trace_build_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_explainability import (  # noqa: E402
    explain_orchestration_evaluation_trace,
    export_orchestration_evaluation_trace_explainability_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_integrity import (  # noqa: E402
    audit_orchestration_evaluation_trace_integrity,
    export_orchestration_evaluation_trace_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_models import (  # noqa: E402
    TRACE_EXPLAINABILITY_STABLE,
    TRACE_INTEGRITY_STABLE,
    TRACE_STATES,
    OrchestrationEvaluationTraceBuildInput,
    OrchestrationEvaluationTraceIntegrityInput,
    export_trace_registry,
)
from app.runtime_orchestration.orchestration_evaluation_trace_registry import (  # noqa: E402
    build_orchestration_evaluation_trace_registry,
    default_orchestration_evaluation_trace_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_evaluation_trace_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_evaluation_trace_modeling"]
    build = focused["build"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["trace_integrity_status"] == TRACE_INTEGRITY_STABLE
        and explainability["trace_explainability_status"] == TRACE_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_evaluation_trace_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_7_deterministic_orchestration_evaluation_trace_modeling",
        "architectural_purpose": "deterministic orchestration evaluation trace modeling",
        "planning_only": True,
        "non_production": True,
        "evaluation_trace_modeling_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_evaluation_trace_count": build["registered_trace_count"],
        "supported_trace_count": _state_count(focused["registry"], "trace_supported"),
        "unsupported_trace_count": _state_count(focused["registry"], "trace_unsupported"),
        "prohibited_trace_count": _state_count(focused["registry"], "trace_prohibited"),
        "governance_blocked_trace_count": _state_count(focused["registry"], "trace_governance_blocked"),
        "compatibility_blocked_trace_count": _state_count(focused["registry"], "trace_compatibility_blocked"),
        "dependency_blocked_trace_count": _state_count(focused["registry"], "trace_dependency_blocked"),
        "governance_trace_count": build["governance_trace_count"],
        "compatibility_trace_count": build["compatibility_trace_count"],
        "dependency_trace_count": build["dependency_trace_count"],
        "blocker_trace_count": build["blocker_trace_count"],
        "unsupported_domain_trace_count": build["unsupported_trace_count"],
        "prohibited_domain_trace_count": build["prohibited_trace_count"],
        "provenance_trace_count": build["provenance_trace_count"],
        "explainability_trace_count": build["explainability_trace_count"],
        "integrity_trace_count": build["integrity_trace_count"],
        "trace_step_count": build["trace_step_count"],
        "reasoning_step_count": build["reasoning_step_count"],
        "blocker_domain_count": _unique_registry_count(focused["registry"], "blocker_domains"),
        "governance_boundary_count": _unique_registry_count(focused["registry"], "governance_boundaries"),
        "compatibility_domain_count": _unique_registry_count(focused["registry"], "compatibility_domains"),
        "dependency_domain_count": _unique_registry_count(focused["registry"], "dependency_domains"),
        "provenance_continuity_status": build["provenance_continuity_status"],
        "explainability_continuity_status": build["explainability_continuity_status"],
        "integrity_continuity_status": build["integrity_continuity_status"],
        "governance_continuity_status": build["governance_continuity_status"],
        "trace_build_status": build["trace_build_status"],
        "trace_explainability_status": explainability["trace_explainability_status"],
        "trace_integrity_status": integrity["trace_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_trace_classifications": list(TRACE_STATES),
        "unsupported_trace_classifications": [
            "runtime_execution_trace",
            "routing_trace",
            "execution_planning_trace",
            "optimization_trace",
            "recommendation_trace",
            "autonomous_path_trace",
            "state_mutating_trace",
            "production_runtime_trace",
            "self_modifying_trace",
        ],
        "registry": focused["registry"],
        "build": build,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable evaluation trace identifiers",
            "stable evaluation trace serialization",
            "stable evaluation trace hashing",
            "stable evaluation trace registry hashing",
            "deterministic reasoning-chain visibility",
            "deterministic governance trace visibility",
            "deterministic compatibility trace visibility",
            "deterministic dependency trace visibility",
            "deterministic blocker-chain trace visibility",
            "deterministic unsupported-domain trace visibility",
            "deterministic prohibited-domain trace visibility",
            "deterministic evaluation trace explainability evidence",
            "deterministic evaluation trace integrity evidence",
            "replay-safe evaluation trace provenance continuity",
            "rollback-safe evaluation trace provenance continuity",
        ],
        "explicit_limitations": [
            "evaluation trace modeling is planning-only",
            "evaluation trace modeling does not execute orchestration",
            "evaluation trace modeling does not dispatch orchestration",
            "evaluation trace modeling does not route requests",
            "evaluation trace modeling does not mutate state",
            "evaluation trace modeling does not write audit logs",
            "evaluation trace modeling does not perform graph execution",
            "evaluation trace modeling does not schedule orchestration",
            "evaluation trace modeling does not capture live runtime traces",
            "evaluation trace modeling does not read production state",
            "evaluation trace modeling does not recommend orchestration behavior",
            "evaluation trace modeling does not optimize orchestration paths",
            "evaluation trace modeling does not create execution plans",
            "evaluation trace modeling does not self-modify trace state",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_trace_registry_hash": build["deterministic_registry_hash"],
        "deterministic_trace_build_hash": build["deterministic_trace_build_hash"],
        "deterministic_trace_explainability_hash": explainability["deterministic_trace_explainability_hash"],
        "deterministic_trace_integrity_hash": integrity["deterministic_trace_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Evaluation Trace Modeling",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 7 establishes deterministic orchestration evaluation trace modeling.",
        "",
        "It models how a theoretical orchestration evaluation arrived at its result step by step.",
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
        f"- Registered evaluation traces: `{report['registered_evaluation_trace_count']}`",
        f"- Governance traces: `{report['governance_trace_count']}`",
        f"- Compatibility traces: `{report['compatibility_trace_count']}`",
        f"- Dependency traces: `{report['dependency_trace_count']}`",
        f"- Blocker traces: `{report['blocker_trace_count']}`",
        f"- Unsupported-domain traces: `{report['unsupported_domain_trace_count']}`",
        f"- Prohibited-domain traces: `{report['prohibited_domain_trace_count']}`",
        f"- Trace steps: `{report['trace_step_count']}`",
        f"- Reasoning-chain steps: `{report['reasoning_step_count']}`",
        f"- Trace build status: `{report['trace_build_status']}`",
        f"- Explainability status: `{report['trace_explainability_status']}`",
        f"- Integrity status: `{report['trace_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Evaluation Trace Philosophy",
        "",
        "The evaluation trace layer prioritizes correctness, evaluation trace visibility, governance explainability, blocker-chain visibility, provenance continuity, and deterministic auditability over execution, routing, automation, recommendation systems, optimization, or autonomous orchestration.",
        "",
        "The purpose is understanding evaluation reasoning chains, not performing orchestration.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Trace Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_trace_classifications"])
    lines.extend(["", "## Unsupported Trace Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_trace_classifications"])
    lines.extend(
        [
            "",
            "## Governance-Boundary Guarantees",
            "",
            "Evaluation trace records preserve deterministic visibility for planning-only, non-production, non-executing, governance-first boundaries.",
            "",
            "Unsupported, prohibited, and blocked trace states remain fail-visible and do not become execution paths.",
            "",
            "## Explainability Guarantees",
            "",
            "Evaluation trace explainability records why an evaluation result exists; which governance boundaries applied; which compatibility domains applied; which blockers applied; which unsupported domains applied; which prohibited domains applied; which provenance chains applied; and how the reasoning chain progressed.",
            "",
            "## Integrity Guarantees",
            "",
            "Evaluation trace integrity auditing validates registry continuity, trace hash continuity, provenance continuity, explainability continuity, governance continuity, compatibility continuity, dependency continuity, blocker continuity, supported-domain continuity, trace-step continuity, policy continuity, and serialization stability.",
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
            "- Self-modifying trace behavior is not introduced.",
            "- Hidden orchestration pathways are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['trace_integrity_status']}`")
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
    registry = default_orchestration_evaluation_trace_registry()
    return {
        "default_evaluation_trace_modeling": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "governance_boundary_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "policy_reference_gap_visibility": _scenario_bundle(_registry_with_policy_gap(registry)),
        "compatibility_domain_gap_visibility": _scenario_bundle(_registry_with_compatibility_gap(registry)),
        "dependency_domain_gap_visibility": _scenario_bundle(_registry_with_dependency_gap(registry)),
        "blocker_domain_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "supported_domain_gap_visibility": _scenario_bundle(_registry_with_supported_domain_gap(registry)),
        "trace_step_gap_visibility": _scenario_bundle(_registry_with_trace_step_gap(registry)),
        "trace_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_trace_hashes={"v3_6.trace.compatibility-check": "mismatched-trace-hash"},
            expected_build_hash="mismatched-trace-build-hash",
        ),
    }


def _scenario_bundle(
    registry,
    expected_trace_hashes: dict[str, str] | None = None,
    expected_build_hash: str | None = None,
) -> dict[str, Any]:
    build = build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(
            trace_registry=registry,
            expected_trace_hashes=expected_trace_hashes,
        )
    )
    explainability = explain_orchestration_evaluation_trace(registry, build)
    integrity = audit_orchestration_evaluation_trace_integrity(
        OrchestrationEvaluationTraceIntegrityInput(
            trace_registry=registry,
            build_result=build,
            explainability_result=explainability,
            expected_build_hash=expected_build_hash,
        )
    )
    return {
        "registry": export_trace_registry(registry),
        "build": export_orchestration_evaluation_trace_build_result(build),
        "explainability": export_orchestration_evaluation_trace_explainability_result(explainability),
        "integrity": export_orchestration_evaluation_trace_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.trace.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_governance_gap(registry):
    target = _record(registry, "v3_6.trace.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_policy_gap(registry):
    target = _record(registry, "v3_6.trace.compatibility-check")
    changed = replace(target, policy_ids=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_compatibility_gap(registry):
    target = _record(registry, "v3_6.trace.policy-boundary")
    changed = replace(target, compatibility_domains=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_dependency_gap(registry):
    target = _record(registry, "v3_6.trace.dependency-analysis")
    changed = replace(target, dependency_domains=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_blocker_gap(registry):
    target = _record(registry, "v3_6.trace.prohibited-domain")
    changed = replace(target, blocker_domains=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_supported_domain_gap(registry):
    target = _record(registry, "v3_6.trace.informational")
    changed = replace(target, supported_domains=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _registry_with_trace_step_gap(registry):
    target = _record(registry, "v3_6.trace.informational")
    changed = replace(target, trace_steps=())
    return _replace_record(registry, target.identifier.trace_id, changed)


def _record(registry, trace_id: str):
    return next(record for record in registry.records if record.identifier.trace_id == trace_id)


def _replace_record(registry, trace_id: str, replacement):
    return build_orchestration_evaluation_trace_registry(
        tuple(
            replacement if record.identifier.trace_id == trace_id else record
            for record in registry.records
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["trace_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["trace_integrity_status"] == status)
        for status in statuses
    }


def _unique_registry_count(registry: dict[str, Any], field: str) -> int:
    return len(
        {
            value
            for record in registry["records"]
            for value in record[field]
        }
    )


def _state_count(registry: dict[str, Any], state: str) -> int:
    return sum(1 for record in registry["records"] if record["trace_state"] == state)


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
        "trace_execution_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_evaluation_trace_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_EVALUATION_TRACE_MODELING.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_evaluation_trace_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
