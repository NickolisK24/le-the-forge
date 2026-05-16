"""Generate the v3.6 orchestration policy intelligence foundation report."""

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
from app.runtime_orchestration.orchestration_policy_evaluator import (  # noqa: E402
    evaluate_orchestration_policy_compatibility,
    export_orchestration_policy_evaluation_result,
)
from app.runtime_orchestration.orchestration_policy_explainability import (  # noqa: E402
    explain_orchestration_policy_evaluation,
    export_orchestration_policy_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_integrity import (  # noqa: E402
    audit_orchestration_policy_integrity,
    export_orchestration_policy_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_models import (  # noqa: E402
    POLICY_INTEGRITY_STABLE,
    POLICY_SUPPORTED,
    POLICY_SUPPORT_STATES,
    OrchestrationPolicyDependency,
    OrchestrationPolicyEvaluationInput,
    OrchestrationPolicyIntegrityInput,
    export_policy_registry,
    hash_policy_definition,
)
from app.runtime_orchestration.orchestration_policy_registry import (  # noqa: E402
    build_orchestration_policy_registry,
    default_orchestration_policy_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_policy_foundation_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_policy_intelligence_foundation"]
    evaluation = focused["evaluation"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["policy_integrity_status"] == POLICY_INTEGRITY_STABLE
        and explainability["explainability_status"] == "policy_explainability_stable"
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_policy_foundation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_1_deterministic_orchestration_policy_intelligence_foundation",
        "architectural_purpose": "deterministic orchestration policy intelligence",
        "planning_only": True,
        "non_production": True,
        "policy_intelligence_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_policy_count": evaluation["registered_policy_count"],
        "supported_policy_count": evaluation["supported_policy_count"],
        "prohibited_policy_count": evaluation["prohibited_policy_count"],
        "unsupported_policy_count": evaluation["unsupported_policy_count"],
        "blocker_count": evaluation["blocker_count"],
        "dependency_continuity_status": evaluation["dependency_continuity_status"],
        "provenance_continuity_status": evaluation["provenance_continuity_status"],
        "governance_continuity_status": evaluation["governance_continuity_status"],
        "integrity_continuity_status": evaluation["integrity_continuity_status"],
        "explainability_continuity_status": evaluation["explainability_continuity_status"],
        "policy_evaluation_status": evaluation["policy_evaluation_status"],
        "policy_explainability_status": explainability["explainability_status"],
        "policy_integrity_status": integrity["policy_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_policy_states": list(POLICY_SUPPORT_STATES),
        "supported_policy_ids": evaluation["supported_policy_ids"],
        "prohibited_policy_ids": evaluation["prohibited_policy_ids"],
        "unsupported_policy_ids": evaluation["unsupported_policy_ids"],
        "registry": focused["registry"],
        "evaluation": evaluation,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "blocker_summary": {
            "blocker_count": evaluation["blocker_count"],
            "prohibited_state_count": evaluation["prohibited_policy_count"],
            "unsupported_state_count": evaluation["unsupported_policy_count"],
            "fail_visible_blockers": True,
        },
        "deterministic_guarantees": [
            "stable policy identifiers",
            "stable policy serialization",
            "stable policy hashing",
            "stable registry hashing",
            "deterministic policy compatibility evaluation",
            "deterministic policy blocker generation",
            "deterministic policy explainability evidence",
            "deterministic policy integrity evidence",
            "replay-safe policy provenance continuity",
            "rollback-safe policy provenance continuity",
        ],
        "explicit_limitations": [
            "policy intelligence is planning-only",
            "policy intelligence does not execute orchestration",
            "policy intelligence does not dispatch orchestration",
            "policy intelligence does not route requests",
            "policy intelligence does not mutate state",
            "policy intelligence does not write audit logs",
            "policy intelligence does not perform graph execution",
            "policy intelligence does not schedule orchestration",
            "policy intelligence does not capture runtime traces",
            "policy intelligence does not read production state",
            "policy intelligence does not perform live replay execution",
            "policy intelligence does not persist audit state",
            "policy intelligence does not enable autonomous orchestration",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_registry_hash": evaluation["deterministic_registry_hash"],
        "deterministic_policy_evaluation_hash": evaluation["deterministic_policy_evaluation_hash"],
        "deterministic_explainability_hash": explainability["deterministic_explainability_hash"],
        "deterministic_policy_integrity_hash": integrity["deterministic_policy_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Policy Foundation",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 1 establishes deterministic orchestration policy intelligence.",
        "",
        "It models what orchestration should be allowed without enabling orchestration behavior.",
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
        "It does not perform live replay execution.",
        "",
        "It does not persist audit state.",
        "",
        f"- Registered policies: `{report['registered_policy_count']}`",
        f"- Supported policies: `{report['supported_policy_count']}`",
        f"- Prohibited policies: `{report['prohibited_policy_count']}`",
        f"- Unsupported policies: `{report['unsupported_policy_count']}`",
        f"- Blockers: `{report['blocker_count']}`",
        f"- Policy evaluation status: `{report['policy_evaluation_status']}`",
        f"- Explainability status: `{report['policy_explainability_status']}`",
        f"- Integrity status: `{report['policy_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Policy Intelligence Philosophy",
        "",
        "The foundation prioritizes correctness, trust, auditability, explainability, deterministic governance, and orchestration visibility over automation, execution, runtime capability, or routing behavior.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(
        [
            "",
            "## Supported Policy States",
            "",
        ]
    )
    lines.extend(f"- `{state}`" for state in report["supported_policy_states"])
    lines.extend(
        [
            "",
            "## Supported Policies",
            "",
        ]
    )
    lines.extend(f"- `{policy_id}`" for policy_id in report["supported_policy_ids"])
    lines.extend(
        [
            "",
            "## Prohibited Policies",
            "",
        ]
    )
    lines.extend(f"- `{policy_id}`" for policy_id in report["prohibited_policy_ids"])
    lines.extend(
        [
            "",
            "## Unsupported Policies",
            "",
        ]
    )
    lines.extend(f"- `{policy_id}`" for policy_id in report["unsupported_policy_ids"])
    lines.extend(
        [
            "",
            "## Explainability Guarantees",
            "",
            "Policy explainability records why supported policies are supported, why prohibited policies are prohibited, why unsupported policies are unsupported, and why blockers exist.",
            "",
            "Dependency chains, governance chains, continuity gaps, provenance references, integrity references, and blocker visibility remain deterministic.",
            "",
            "## Integrity Guarantees",
            "",
            "Policy integrity auditing validates registry continuity, policy hash continuity, provenance continuity, dependency continuity, governance continuity, explainability continuity, evaluation continuity, serialization stability, and blocker visibility.",
            "",
            "## Governance Continuity Guarantees",
            "",
            f"- Dependency continuity: `{report['dependency_continuity_status']}`",
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
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['policy_integrity_status']}`")
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
    registry = default_orchestration_policy_registry()
    missing_dependency_registry = _registry_with_missing_dependency(registry)
    governance_gap_registry = _registry_with_governance_gap(registry)
    provenance_gap_registry = _registry_with_provenance_gap(registry)
    explainability_gap_registry = _registry_with_explainability_gap(registry)
    scenarios = {
        "default_policy_intelligence_foundation": _scenario_bundle(registry),
        "missing_dependency_visibility": _scenario_bundle(missing_dependency_registry),
        "governance_gap_visibility": _scenario_bundle(governance_gap_registry),
        "provenance_gap_visibility": _scenario_bundle(provenance_gap_registry),
        "policy_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_policy_hashes={"v3_6.policy.modeling.allowed": "mismatched-policy-hash"},
        ),
        "explainability_gap_visibility": _scenario_bundle(explainability_gap_registry),
    }
    return scenarios


def _scenario_bundle(
    registry,
    expected_policy_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    evaluation = evaluate_orchestration_policy_compatibility(
        OrchestrationPolicyEvaluationInput(registry=registry, expected_policy_hashes=expected_policy_hashes)
    )
    explainability = explain_orchestration_policy_evaluation(registry, evaluation)
    integrity = audit_orchestration_policy_integrity(
        OrchestrationPolicyIntegrityInput(
            registry=registry,
            evaluation_result=evaluation,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_policy_registry(registry),
        "evaluation": export_orchestration_policy_evaluation_result(evaluation),
        "explainability": export_orchestration_policy_explainability_result(explainability),
        "integrity": export_orchestration_policy_integrity_result(integrity),
    }


def _registry_with_missing_dependency(registry):
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.integrity.allowed")
    changed = replace(
        target,
        dependencies=target.dependencies
        + (
            OrchestrationPolicyDependency(
                dependency_id="report-missing-policy-dependency",
                required_policy_id="v3_6.policy.missing.required",
                required_support_states=(POLICY_SUPPORTED,),
                continuity_reference_id="report-missing-policy-dependency.continuity",
            ),
        ),
    )
    return _replace_policy(registry, target.identifier.policy_id, changed)


def _registry_with_governance_gap(registry):
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    metadata = dict(target.governance_metadata)
    metadata["execution_enabled"] = True
    changed = replace(target, governance_metadata=metadata)
    return _replace_policy(registry, target.identifier.policy_id, changed)


def _registry_with_provenance_gap(registry):
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_policy(registry, target.identifier.policy_id, changed)


def _registry_with_explainability_gap(registry):
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    changed = replace(target, support_state="policy_requires_manual_review", manual_review_reasons=())
    return _replace_policy(registry, target.identifier.policy_id, changed)


def _replace_policy(registry, policy_id: str, replacement):
    return build_orchestration_policy_registry(
        tuple(replacement if policy.identifier.policy_id == policy_id else policy for policy in registry.policies)
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["policy_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["policy_integrity_status"] == status)
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
        "policy_execution_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_policy_foundation_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_POLICY_FOUNDATION.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_policy_foundation_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
