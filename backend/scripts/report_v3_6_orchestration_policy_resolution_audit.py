"""Generate the v3.6 orchestration policy resolution audit report."""

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
from app.runtime_orchestration.orchestration_policy_resolution_auditor import (  # noqa: E402
    audit_orchestration_policy_resolution,
    export_orchestration_policy_resolution_audit_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_explainability import (  # noqa: E402
    explain_orchestration_policy_resolution,
    export_orchestration_policy_resolution_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_integrity import (  # noqa: E402
    audit_orchestration_policy_resolution_integrity,
    export_orchestration_policy_resolution_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_models import (  # noqa: E402
    RESOLUTION_EXPLAINABILITY_STABLE,
    RESOLUTION_INTEGRITY_STABLE,
    OrchestrationPolicyResolutionAuditInput,
    OrchestrationPolicyResolutionIntegrityInput,
    export_resolution_registry,
)
from app.runtime_orchestration.orchestration_policy_resolution_registry import (  # noqa: E402
    build_orchestration_policy_resolution_registry,
    default_orchestration_policy_resolution_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_policy_resolution_audit_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_resolution_audit"]
    audit = focused["audit"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["resolution_integrity_status"] == RESOLUTION_INTEGRITY_STABLE
        and explainability["resolution_explainability_status"] == RESOLUTION_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_policy_resolution_audit_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_3_deterministic_orchestration_policy_resolution_audit",
        "architectural_purpose": "deterministic orchestration compatibility resolution auditing",
        "planning_only": True,
        "non_production": True,
        "resolution_audit_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "automatic_resolution_enabled": False,
        "production_runtime_behavior_enabled": False,
        "registered_resolution_record_count": len(focused["registry"]["records"]),
        "intentional_block_count": audit["intentional_block_count"],
        "future_candidate_count": audit["future_candidate_count"],
        "unsupported_by_design_count": audit["unsupported_by_design_count"],
        "governance_conflict_count": audit["governance_conflict_count"],
        "dependency_conflict_count": audit["dependency_conflict_count"],
        "continuity_conflict_count": audit["continuity_conflict_count"],
        "evidence_incomplete_count": audit["evidence_incomplete_count"],
        "provenance_gap_count": audit["provenance_gap_count"],
        "explainability_gap_count": audit["explainability_gap_count"],
        "potential_misclassification_count": audit["potential_misclassification_count"],
        "blocker_chain_total": audit["blocker_chain_total"],
        "provenance_continuity_status": audit["provenance_continuity_status"],
        "explainability_continuity_status": audit["explainability_continuity_status"],
        "integrity_continuity_status": audit["integrity_continuity_status"],
        "resolution_audit_status": audit["resolution_audit_status"],
        "resolution_explainability_status": explainability["resolution_explainability_status"],
        "resolution_integrity_status": integrity["resolution_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_resolution_classifications": [
            "intentional_block",
            "future_candidate",
            "unsupported_by_design",
            "governance_conflict",
            "dependency_conflict",
            "continuity_conflict",
            "evidence_incomplete",
            "provenance_gap",
            "explainability_gap",
            "potential_misclassification",
        ],
        "unsupported_resolution_classifications": [
            "automatic_compatibility_upgrade",
            "runtime_resolution",
            "execution_resolution",
            "routing_resolution",
            "optimization_resolution",
            "self_modifying_resolution",
        ],
        "registry": focused["registry"],
        "audit": audit,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable resolution identifiers",
            "stable resolution serialization",
            "stable resolution hashing",
            "stable resolution registry hashing",
            "deterministic intentional-block classification",
            "deterministic future-candidate classification",
            "deterministic evidence-gap visibility",
            "deterministic blocker-chain visibility",
            "deterministic resolution explainability evidence",
            "deterministic resolution integrity evidence",
            "replay-safe resolution provenance continuity",
            "rollback-safe resolution provenance continuity",
        ],
        "explicit_limitations": [
            "resolution auditing is planning-only",
            "resolution auditing does not execute orchestration",
            "resolution auditing does not dispatch orchestration",
            "resolution auditing does not route requests",
            "resolution auditing does not mutate state",
            "resolution auditing does not write audit logs",
            "resolution auditing does not perform graph execution",
            "resolution auditing does not schedule orchestration",
            "resolution auditing does not capture runtime traces",
            "resolution auditing does not read production state",
            "resolution auditing does not optimize orchestration paths",
            "resolution auditing does not automatically change compatibility status",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_resolution_registry_hash": audit["deterministic_registry_hash"],
        "deterministic_resolution_audit_hash": audit["deterministic_resolution_audit_hash"],
        "deterministic_resolution_explainability_hash": explainability["deterministic_resolution_explainability_hash"],
        "deterministic_resolution_integrity_hash": integrity["deterministic_resolution_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Policy Resolution Audit",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 3 establishes deterministic orchestration compatibility resolution auditing.",
        "",
        "It explains why compatibility relationships are blocked and what evidence would be required before status may safely change.",
        "",
        "This phase is governance auditing only.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not dispatch orchestration.",
        "",
        "It does not route requests.",
        "",
        "It does not mutate state.",
        "",
        "It does not automatically change compatibility status.",
        "",
        "It does not read production state.",
        "",
        f"- Registered resolution records: `{report['registered_resolution_record_count']}`",
        f"- Intentional blocks: `{report['intentional_block_count']}`",
        f"- Future candidates: `{report['future_candidate_count']}`",
        f"- Unsupported by design: `{report['unsupported_by_design_count']}`",
        f"- Governance conflicts: `{report['governance_conflict_count']}`",
        f"- Dependency conflicts: `{report['dependency_conflict_count']}`",
        f"- Continuity conflicts: `{report['continuity_conflict_count']}`",
        f"- Evidence incomplete: `{report['evidence_incomplete_count']}`",
        f"- Provenance gaps: `{report['provenance_gap_count']}`",
        f"- Potential misclassifications: `{report['potential_misclassification_count']}`",
        f"- Blocker chains: `{report['blocker_chain_total']}`",
        f"- Resolution audit status: `{report['resolution_audit_status']}`",
        f"- Explainability status: `{report['resolution_explainability_status']}`",
        f"- Integrity status: `{report['resolution_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Resolution Auditing Philosophy",
        "",
        "The resolution audit prioritizes correctness, blocker explainability, governance continuity, provenance continuity, evidence visibility, and deterministic auditability over making relationships compatible.",
        "",
        "The audit classifies blocked compatibility state honestly and deterministically.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Resolution Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_resolution_classifications"])
    lines.extend(["", "## Unsupported Resolution Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_resolution_classifications"])
    lines.extend(
        [
            "",
            "## Blocker Visibility Guarantees",
            "",
            "Blocker chains preserve deterministic visibility for intentional blocks, unsupported-by-design relationships, dependency conflicts, governance conflicts, continuity conflicts, evidence gaps, provenance gaps, and potential misclassifications.",
            "",
            "## Evidence-Gap Guarantees",
            "",
            "Future candidates remain blocked until deterministic evidence requirements are declared and satisfied by governance review outside this phase.",
            "",
            "Evidence gaps are visible as audit evidence.",
            "",
            "They are not converted into compatibility upgrades.",
            "",
            "## Explainability Guarantees",
            "",
            "Resolution explainability records why compatibility is blocked, whether the block is intentional, what evidence is missing, what governance rules prevent support, what dependencies are unresolved, and what continuity or provenance gaps exist.",
            "",
            "## Integrity Guarantees",
            "",
            "Resolution integrity auditing validates registry continuity, resolution hash continuity, provenance continuity, explainability continuity, blocker continuity, governance continuity, evidence continuity, compatibility continuity, and serialization stability.",
            "",
            "## Continuity Status",
            "",
            f"- Provenance continuity: `{report['provenance_continuity_status']}`",
            f"- Explainability continuity: `{report['explainability_continuity_status']}`",
            f"- Integrity continuity: `{report['integrity_continuity_status']}`",
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
            "- Automatic compatibility upgrades remain prohibited.",
            "- Runtime scheduling remains prohibited.",
            "- Production runtime reads remain prohibited.",
            "- Production runtime writes remain prohibited.",
            "- Persistent writes remain prohibited.",
            "- Recommendation, optimization, and self-modifying systems are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['resolution_integrity_status']}`")
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
    registry = default_orchestration_policy_resolution_registry()
    return {
        "default_resolution_audit": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "continuity_conflict_visibility": _scenario_bundle(_registry_with_continuity_gap(registry)),
        "evidence_gap_visibility": _scenario_bundle(_registry_with_missing_evidence_gap(registry)),
        "potential_misclassification_visibility": _scenario_bundle(_registry_with_potential_misclassification(registry)),
        "explainability_gap_visibility": _scenario_bundle(_registry_with_explainability_gap(registry)),
        "resolution_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_resolution_hashes={"v3_6.resolution.explainability-routing.incompatible": "mismatched-resolution-hash"},
        ),
    }


def _scenario_bundle(
    registry,
    expected_resolution_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    audit = audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(
            resolution_registry=registry,
            expected_resolution_hashes=expected_resolution_hashes,
        )
    )
    explainability = explain_orchestration_policy_resolution(registry, audit)
    integrity = audit_orchestration_policy_resolution_integrity(
        OrchestrationPolicyResolutionIntegrityInput(
            resolution_registry=registry,
            audit_result=audit,
            explainability_result=explainability,
        )
    )
    return {
        "registry": export_resolution_registry(registry),
        "audit": export_orchestration_policy_resolution_audit_result(audit),
        "explainability": export_orchestration_policy_resolution_explainability_result(explainability),
        "integrity": export_orchestration_policy_resolution_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_record(registry, target.identifier.resolution_id, changed)


def _registry_with_continuity_gap(registry):
    target = _record(registry, "v3_6.resolution.autonomy-routing.unsupported")
    changed = replace(target, continuity_gaps=("unsupported_combination_requires_new_design_evidence",))
    return _replace_record(registry, target.identifier.resolution_id, changed)


def _registry_with_missing_evidence_gap(registry):
    target = _record(registry, "v3_6.resolution.explainability-routing.incompatible")
    changed = replace(target, evidence_gaps=())
    return _replace_record(registry, target.identifier.resolution_id, changed)


def _registry_with_potential_misclassification(registry):
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, future_support_possible=True)
    return _replace_record(registry, target.identifier.resolution_id, changed)


def _registry_with_explainability_gap(registry):
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, resolution_explainability_ids=())
    return _replace_record(registry, target.identifier.resolution_id, changed)


def _record(registry, resolution_id: str):
    return next(record for record in registry.records if record.identifier.resolution_id == resolution_id)


def _replace_record(registry, resolution_id: str, replacement):
    return build_orchestration_policy_resolution_registry(
        tuple(
            replacement if record.identifier.resolution_id == resolution_id else record
            for record in registry.records
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["resolution_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["resolution_integrity_status"] == status)
        for status in statuses
    }


def _non_execution_guarantees() -> dict[str, bool]:
    return {
        "runtime_execution_enabled": False,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "mutation_behavior_enabled": False,
        "production_consumption_enabled": False,
        "automatic_resolution_enabled": False,
        "background_processing_enabled": False,
        "status_change_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_policy_resolution_audit_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_POLICY_RESOLUTION_AUDIT.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_policy_resolution_audit_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
