"""Generate the v3.6 orchestration evaluation chain integrity report."""

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
from app.runtime_orchestration.orchestration_evaluation_chain_auditor import (  # noqa: E402
    audit_orchestration_evaluation_chain_integrity,
    default_orchestration_evaluation_chain_audit_input,
    export_orchestration_evaluation_chain_audit_result,
)
from app.runtime_orchestration.orchestration_evaluation_chain_explainability import (  # noqa: E402
    explain_orchestration_evaluation_chain_integrity,
    export_orchestration_evaluation_chain_explainability_result,
)
from app.runtime_orchestration.orchestration_evaluation_chain_integrity import (  # noqa: E402
    audit_orchestration_evaluation_chain_integrity_result,
    export_orchestration_evaluation_chain_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_chain_models import (  # noqa: E402
    CHAIN_AUDIT_STABLE,
    CHAIN_CONTINUITY_PRESERVED,
    CHAIN_EXPLAINABILITY_STABLE,
    CHAIN_INTEGRITY_STABLE,
    OrchestrationEvaluationChainIntegrityInput,
)
from app.runtime_orchestration.orchestration_evaluation_replay_builder import (  # noqa: E402
    build_orchestration_evaluation_replay_packets,
)
from app.runtime_orchestration.orchestration_evaluation_replay_explainability import (  # noqa: E402
    explain_orchestration_evaluation_replay_packets,
)
from app.runtime_orchestration.orchestration_evaluation_replay_integrity import (  # noqa: E402
    audit_orchestration_evaluation_replay_integrity,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (  # noqa: E402
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (  # noqa: E402
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_evaluation_chain_integrity_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_chain_integrity"]
    audit = focused["audit"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if audit["chain_audit_status"] == CHAIN_AUDIT_STABLE
        and explainability["chain_explainability_status"] == CHAIN_EXPLAINABILITY_STABLE
        and integrity["chain_integrity_status"] == CHAIN_INTEGRITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_evaluation_chain_integrity_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_9_deterministic_orchestration_evaluation_chain_integrity_audit",
        "architectural_purpose": "deterministic orchestration evaluation chain integrity auditing",
        "planning_only": True,
        "non_production": True,
        "chain_audit_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "persistent_write_enabled": False,
        "audited_chain_count": audit["audited_chain_count"],
        "valid_chain_count": audit["valid_chain_count"],
        "invalid_chain_count": audit["invalid_chain_count"],
        "policy_continuity_status": audit["policy_continuity_status"],
        "compatibility_continuity_status": audit["compatibility_continuity_status"],
        "resolution_continuity_status": audit["resolution_continuity_status"],
        "intent_continuity_status": audit["intent_continuity_status"],
        "mapping_continuity_status": audit["mapping_continuity_status"],
        "preflight_continuity_status": audit["preflight_continuity_status"],
        "trace_continuity_status": audit["trace_continuity_status"],
        "replay_continuity_status": audit["replay_continuity_status"],
        "blocker_chain_continuity_status": audit["blocker_chain_continuity_status"],
        "governance_boundary_continuity_status": audit["governance_boundary_continuity_status"],
        "provenance_continuity_status": audit["provenance_continuity_status"],
        "explainability_continuity_status": audit["explainability_continuity_status"],
        "integrity_continuity_status": audit["integrity_continuity_status"],
        "replay_safety_status": audit["replay_safety_status"],
        "rollback_safety_status": audit["rollback_safety_status"],
        "chain_audit_status": audit["chain_audit_status"],
        "chain_explainability_status": explainability["chain_explainability_status"],
        "chain_integrity_status": integrity["chain_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "blocker_visibility_count": explainability["blocker_visibility_count"],
        "unsupported_visibility_count": explainability["unsupported_visibility_count"],
        "prohibited_visibility_count": explainability["prohibited_visibility_count"],
        "valid_link_count": explainability["valid_link_count"],
        "missing_link_count": explainability["missing_link_count"],
        "audited_chain_links": [
            "intent_to_mapping",
            "mapping_to_policy",
            "mapping_to_preflight",
            "compatibility_to_resolution",
            "preflight_to_trace",
            "trace_to_replay_packet",
            "blocker_chain_visibility",
            "governance_boundary_visibility",
            "provenance_continuity",
            "explainability_continuity",
            "integrity_continuity",
            "replay_safety",
            "rollback_safety",
        ],
        "valid_chain_states": ["evaluation_chain_valid"],
        "failure_states": [
            "evaluation_chain_invalid",
            "evaluation_chain_link_missing",
            "evaluation_chain_hash_mismatch",
            "evaluation_chain_source_evidence_gap",
            "evaluation_chain_blocker_visibility_gap",
            "evaluation_chain_governance_visibility_gap",
            "evaluation_chain_provenance_gap",
            "evaluation_chain_explainability_gap",
            "evaluation_chain_integrity_gap",
            "evaluation_chain_replay_safety_gap",
            "evaluation_chain_rollback_safety_gap",
            "evaluation_chain_non_execution_gap",
        ],
        "deterministic_guarantees": [
            "deterministic full-chain continuity",
            "deterministic policy-chain continuity",
            "deterministic compatibility-chain continuity",
            "deterministic resolution-chain continuity",
            "deterministic intent-chain continuity",
            "deterministic mapping-chain continuity",
            "deterministic preflight-chain continuity",
            "deterministic trace-chain continuity",
            "deterministic replay-chain continuity",
            "deterministic blocker-chain continuity",
            "deterministic governance-boundary continuity",
            "deterministic provenance continuity",
            "deterministic explainability continuity",
            "deterministic integrity continuity",
            "deterministic chain replay safety",
            "deterministic chain rollback safety",
        ],
        "explicit_limitations": [
            "chain integrity auditing is planning-only",
            "chain integrity auditing does not execute orchestration",
            "chain integrity auditing does not dispatch orchestration",
            "chain integrity auditing does not route requests",
            "chain integrity auditing does not mutate state",
            "chain integrity auditing does not write persistent audit logs",
            "chain integrity auditing does not perform graph execution",
            "chain integrity auditing does not schedule orchestration",
            "chain integrity auditing does not read live runtime state",
            "chain integrity auditing does not recommend orchestration behavior",
            "chain integrity auditing does not optimize orchestration paths",
            "chain integrity auditing does not create execution plans",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "audit": audit,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "replay_safety_confirmation": audit["replay_safety_status"] == CHAIN_CONTINUITY_PRESERVED,
        "rollback_safety_confirmation": audit["rollback_safety_status"] == CHAIN_CONTINUITY_PRESERVED,
        "deterministic_source_hashes": audit["deterministic_source_hashes"],
        "deterministic_chain_audit_hash": audit["deterministic_chain_audit_hash"],
        "deterministic_chain_explainability_hash": explainability["deterministic_chain_explainability_hash"],
        "deterministic_chain_integrity_hash": integrity["deterministic_chain_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Evaluation Chain Integrity Audit",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 9 establishes deterministic orchestration evaluation chain integrity auditing.",
        "",
        "It verifies that intent, policy mapping, compatibility, resolution, preflight, trace, and replay packet evidence form a stable, replay-safe, rollback-safe, provenance-safe, explainable chain.",
        "",
        "This phase is planning-only governance intelligence.",
        "",
        "It does not execute orchestration.",
        "",
        "It does not route orchestration.",
        "",
        "It does not mutate state.",
        "",
        "It does not create execution plans.",
        "",
        f"- Audited chains: `{report['audited_chain_count']}`",
        f"- Valid chains: `{report['valid_chain_count']}`",
        f"- Invalid chains: `{report['invalid_chain_count']}`",
        f"- Policy continuity: `{report['policy_continuity_status']}`",
        f"- Compatibility continuity: `{report['compatibility_continuity_status']}`",
        f"- Resolution continuity: `{report['resolution_continuity_status']}`",
        f"- Intent continuity: `{report['intent_continuity_status']}`",
        f"- Mapping continuity: `{report['mapping_continuity_status']}`",
        f"- Preflight continuity: `{report['preflight_continuity_status']}`",
        f"- Trace continuity: `{report['trace_continuity_status']}`",
        f"- Replay continuity: `{report['replay_continuity_status']}`",
        f"- Blocker-chain continuity: `{report['blocker_chain_continuity_status']}`",
        f"- Provenance continuity: `{report['provenance_continuity_status']}`",
        f"- Explainability continuity: `{report['explainability_continuity_status']}`",
        f"- Integrity continuity: `{report['integrity_continuity_status']}`",
        f"- Chain audit status: `{report['chain_audit_status']}`",
        f"- Explainability status: `{report['chain_explainability_status']}`",
        f"- Integrity status: `{report['chain_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Chain Audit Philosophy",
        "",
        "The chain audit prioritizes chain correctness, continuity validation, provenance continuity, replay continuity, explainability continuity, and deterministic auditability over execution, routing, optimization, recommendation systems, or autonomous orchestration.",
        "",
        "The purpose is proving evidence-chain stability, not enabling orchestration capability.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Audited Chain Links", ""])
    lines.extend(f"- `{item}`" for item in report["audited_chain_links"])
    lines.extend(["", "## Valid Chain States", ""])
    lines.extend(f"- `{item}`" for item in report["valid_chain_states"])
    lines.extend(["", "## Failure States", ""])
    lines.extend(f"- `{item}`" for item in report["failure_states"])
    lines.extend(
        [
            "",
            "## Replay Guarantees",
            "",
            "Replay packet references are audited for deterministic visibility and remain non-executing.",
            "",
            f"- Replay safety confirmed: `{report['replay_safety_confirmation']}`",
            "",
            "## Rollback Guarantees",
            "",
            "Rollback references are audited for deterministic visibility without mutation or persistent writes.",
            "",
            f"- Rollback safety confirmed: `{report['rollback_safety_confirmation']}`",
            "",
            "## Explainability Guarantees",
            "",
            "Chain explainability records what chain was audited, which links are valid, which links are missing, which blockers are preserved, which unsupported and prohibited states are preserved, and whether replay and rollback safety hold.",
            "",
            "## Integrity Guarantees",
            "",
            "Chain integrity auditing validates source evidence continuity, chain hash continuity, replay packet continuity, trace continuity, preflight continuity, mapping continuity, intent continuity, policy continuity, blocker continuity, governance continuity, provenance continuity, explainability continuity, replay safety, rollback safety, and deterministic serialization.",
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
            "- Orchestration routing remains prohibited.",
            "- Autonomous orchestration remains unsupported.",
            "- Execution-capable graphs remain prohibited.",
            "- Scheduling remains prohibited.",
            "- Recommendation systems are not introduced.",
            "- Optimization systems are not introduced.",
            "- Mutation behavior remains prohibited.",
            "- Persistent writes remain prohibited.",
            "- Live runtime reads remain prohibited.",
            "- Background processing remains prohibited.",
            "- Execution planning remains prohibited.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['chain_integrity_status']}`")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _scenario_results() -> dict[str, dict[str, Any]]:
    registry = default_orchestration_evaluation_replay_registry()
    return {
        "default_chain_integrity": _scenario_bundle(registry),
        "trace_gap_visibility": _scenario_bundle(_registry_with_trace_gap(registry)),
        "preflight_gap_visibility": _scenario_bundle(_registry_with_preflight_gap(registry)),
        "mapping_gap_visibility": _scenario_bundle(_registry_with_mapping_gap(registry)),
        "governance_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "blocker_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "chain_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_chain_hashes={"v3_6.chain.compatibility-check": "mismatched-chain-record-hash"},
        ),
    }


def _scenario_bundle(registry, expected_chain_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=registry)
    )
    replay_explainability = explain_orchestration_evaluation_replay_packets(registry, build)
    replay_integrity = audit_orchestration_evaluation_replay_integrity(
        OrchestrationEvaluationReplayIntegrityInput(
            replay_registry=registry,
            build_result=build,
            explainability_result=replay_explainability,
        )
    )
    audit_input = replace(
        default_orchestration_evaluation_chain_audit_input(),
        replay_registry=registry,
        replay_build_result=build,
        replay_explainability_result=replay_explainability,
        replay_integrity_result=replay_integrity,
        expected_chain_hashes=expected_chain_hashes,
    )
    audit = audit_orchestration_evaluation_chain_integrity(audit_input)
    explainability = explain_orchestration_evaluation_chain_integrity(audit)
    integrity = audit_orchestration_evaluation_chain_integrity_result(
        OrchestrationEvaluationChainIntegrityInput(
            audit_result=audit,
            explainability_result=explainability,
        )
    )
    return {
        "audit": export_orchestration_evaluation_chain_audit_result(audit),
        "explainability": export_orchestration_evaluation_chain_explainability_result(explainability),
        "integrity": export_orchestration_evaluation_chain_integrity_result(integrity),
    }


def _registry_with_trace_gap(registry):
    return _replace_packet_field(registry, "v3_6.replay.compatibility-check", trace_evidence=())


def _registry_with_preflight_gap(registry):
    return _replace_packet_field(registry, "v3_6.replay.compatibility-check", preflight_evidence=())


def _registry_with_mapping_gap(registry):
    return _replace_packet_field(registry, "v3_6.replay.compatibility-check", policy_mapping_evidence=())


def _registry_with_governance_gap(registry):
    return _replace_packet_field(registry, "v3_6.replay.compatibility-check", governance_evidence=())


def _registry_with_blocker_gap(registry):
    return _replace_packet_field(registry, "v3_6.replay.prohibited-domain", blocker_evidence=())


def _replace_packet_field(registry, packet_id: str, **changes):
    target = next(packet for packet in registry.packets if packet.identifier.packet_id == packet_id)
    changed = replace(target, **changes)
    return build_orchestration_evaluation_replay_registry(
        changed if packet.identifier.packet_id == packet_id else packet
        for packet in registry.packets
    )


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
        "persistent_write_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_evaluation_chain_integrity_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_EVALUATION_CHAIN_INTEGRITY_AUDIT.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_evaluation_chain_integrity_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
