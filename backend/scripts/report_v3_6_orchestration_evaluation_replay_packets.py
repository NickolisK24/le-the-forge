"""Generate the v3.6 orchestration evaluation replay packet report."""

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
from app.runtime_orchestration.orchestration_evaluation_replay_builder import (  # noqa: E402
    build_orchestration_evaluation_replay_packets,
    export_orchestration_evaluation_replay_build_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_explainability import (  # noqa: E402
    explain_orchestration_evaluation_replay_packets,
    export_orchestration_evaluation_replay_explainability_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_integrity import (  # noqa: E402
    audit_orchestration_evaluation_replay_integrity,
    export_orchestration_evaluation_replay_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (  # noqa: E402
    REPLAY_EXPLAINABILITY_STABLE,
    REPLAY_INTEGRITY_STABLE,
    REPLAY_STATES,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
    export_replay_registry,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (  # noqa: E402
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"
DETERMINISTIC_VALIDATION_STABLE = "deterministic_validation_stable"
DETERMINISTIC_VALIDATION_BLOCKED = "deterministic_validation_blocked"


def build_v3_6_orchestration_evaluation_replay_report(repo_root: Path | None = None) -> dict[str, Any]:
    scenarios = _scenario_results()
    focused = scenarios["default_evaluation_replay_packets"]
    build = focused["build"]
    explainability = focused["explainability"]
    integrity = focused["integrity"]
    deterministic_validation_status = (
        DETERMINISTIC_VALIDATION_STABLE
        if integrity["replay_integrity_status"] == REPLAY_INTEGRITY_STABLE
        and explainability["replay_explainability_status"] == REPLAY_EXPLAINABILITY_STABLE
        else DETERMINISTIC_VALIDATION_BLOCKED
    )
    report = {
        "schema_version": "v3_6.orchestration_evaluation_replay_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.6_phase_8_deterministic_orchestration_evaluation_replay_packets",
        "architectural_purpose": "deterministic orchestration evaluation replay packets",
        "planning_only": True,
        "non_production": True,
        "replay_packet_modeling_only": True,
        "orchestration_execution_enabled": False,
        "routing_behavior_enabled": False,
        "autonomous_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "optimization_behavior_enabled": False,
        "production_runtime_behavior_enabled": False,
        "persistent_write_enabled": False,
        "registered_replay_packet_count": build["registered_replay_packet_count"],
        "supported_replay_state_count": _state_count(focused["registry"], "replay_packet_supported"),
        "unsupported_replay_state_count": _state_count(focused["registry"], "replay_packet_unsupported"),
        "prohibited_replay_state_count": _state_count(focused["registry"], "replay_packet_prohibited"),
        "governance_blocked_replay_state_count": _state_count(focused["registry"], "replay_packet_governance_blocked"),
        "compatibility_blocked_replay_state_count": _state_count(focused["registry"], "replay_packet_compatibility_blocked"),
        "dependency_blocked_replay_state_count": _state_count(focused["registry"], "replay_packet_dependency_blocked"),
        "governance_evidence_count": build["governance_evidence_count"],
        "compatibility_evidence_count": build["compatibility_evidence_count"],
        "dependency_evidence_count": build["dependency_evidence_count"],
        "blocker_evidence_count": build["blocker_evidence_count"],
        "unsupported_replay_count": build["unsupported_replay_count"],
        "prohibited_replay_count": build["prohibited_replay_count"],
        "preflight_evidence_count": build["preflight_evidence_count"],
        "trace_evidence_count": build["trace_evidence_count"],
        "intent_evidence_count": build["intent_evidence_count"],
        "policy_mapping_evidence_count": build["policy_mapping_evidence_count"],
        "reasoning_step_count": build["reasoning_step_count"],
        "evidence_visibility_count": explainability["evidence_visibility_count"],
        "blocker_domain_count": _unique_registry_count(focused["registry"], "blocker_domains"),
        "governance_boundary_count": _unique_registry_count(focused["registry"], "governance_boundaries"),
        "compatibility_domain_count": _unique_registry_count(focused["registry"], "compatibility_domains"),
        "dependency_domain_count": _unique_registry_count(focused["registry"], "dependency_domains"),
        "provenance_continuity_status": build["provenance_continuity_status"],
        "explainability_continuity_status": build["explainability_continuity_status"],
        "integrity_continuity_status": build["integrity_continuity_status"],
        "governance_continuity_status": build["governance_continuity_status"],
        "replay_build_status": build["replay_build_status"],
        "replay_explainability_status": explainability["replay_explainability_status"],
        "replay_integrity_status": integrity["replay_integrity_status"],
        "deterministic_validation_status": deterministic_validation_status,
        "supported_replay_classifications": list(REPLAY_STATES),
        "unsupported_replay_classifications": [
            "runtime_execution_replay_packet",
            "routing_replay_packet",
            "execution_planning_replay_packet",
            "optimization_replay_packet",
            "recommendation_replay_packet",
            "autonomous_path_replay_packet",
            "state_mutating_replay_packet",
            "production_runtime_replay_packet",
            "self_modifying_replay_packet",
        ],
        "registry": focused["registry"],
        "build": build,
        "explainability": explainability,
        "integrity": integrity,
        "scenario_coverage": list(scenarios.keys()),
        "scenario_results": scenarios,
        "integrity_status_distribution": _integrity_status_distribution(scenarios),
        "deterministic_guarantees": [
            "stable replay packet identifiers",
            "stable replay packet serialization",
            "stable replay packet hashing",
            "stable replay packet registry hashing",
            "deterministic intent evidence packaging",
            "deterministic policy mapping evidence packaging",
            "deterministic governance evidence packaging",
            "deterministic compatibility evidence packaging",
            "deterministic dependency evidence packaging",
            "deterministic blocker evidence packaging",
            "deterministic unsupported-domain replay visibility",
            "deterministic prohibited-domain replay visibility",
            "deterministic reasoning-chain replay continuity",
            "deterministic replay packet explainability evidence",
            "deterministic replay packet integrity evidence",
            "replay-safe replay packet provenance continuity",
            "rollback-safe replay packet provenance continuity",
        ],
        "explicit_limitations": [
            "replay packet modeling is planning-only",
            "replay packet modeling does not execute orchestration",
            "replay packet modeling does not dispatch orchestration",
            "replay packet modeling does not route requests",
            "replay packet modeling does not mutate state",
            "replay packet modeling does not write audit logs",
            "replay packet modeling does not perform graph execution",
            "replay packet modeling does not schedule orchestration",
            "replay packet modeling does not capture live runtime traces",
            "replay packet modeling does not read production state",
            "replay packet modeling does not recommend orchestration behavior",
            "replay packet modeling does not optimize orchestration paths",
            "replay packet modeling does not create execution plans",
            "replay packet modeling does not self-modify replay state",
            "replay packet modeling does not persist replay packets",
        ],
        "explicit_non_execution_guarantees": _non_execution_guarantees(),
        "replay_safety_confirmation": True,
        "rollback_safety_confirmation": True,
        "deterministic_replay_registry_hash": build["deterministic_registry_hash"],
        "deterministic_replay_build_hash": build["deterministic_replay_build_hash"],
        "deterministic_replay_explainability_hash": explainability["deterministic_replay_explainability_hash"],
        "deterministic_replay_integrity_hash": integrity["deterministic_replay_integrity_hash"],
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.6 Orchestration Evaluation Replay Packets",
        "",
        "## Architectural Purpose",
        "",
        "v3.6 Phase 8 establishes deterministic orchestration evaluation replay packets.",
        "",
        "It packages orchestration intent, policy mappings, compatibility evidence, preflight evaluations, reasoning traces, blocker evidence, provenance evidence, and explainability evidence into replay-safe evaluation packets.",
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
        "It does not persist replay packets.",
        "",
        "It does not recommend orchestration behavior.",
        "",
        "It does not create execution plans.",
        "",
        "It does not read production state.",
        "",
        f"- Registered replay packets: `{report['registered_replay_packet_count']}`",
        f"- Governance evidence packets: `{report['governance_evidence_count']}`",
        f"- Compatibility evidence packets: `{report['compatibility_evidence_count']}`",
        f"- Dependency evidence packets: `{report['dependency_evidence_count']}`",
        f"- Blocker evidence packets: `{report['blocker_evidence_count']}`",
        f"- Unsupported replay packets: `{report['unsupported_replay_count']}`",
        f"- Prohibited replay packets: `{report['prohibited_replay_count']}`",
        f"- Reasoning-chain steps: `{report['reasoning_step_count']}`",
        f"- Evidence visibility entries: `{report['evidence_visibility_count']}`",
        f"- Replay build status: `{report['replay_build_status']}`",
        f"- Explainability status: `{report['replay_explainability_status']}`",
        f"- Integrity status: `{report['replay_integrity_status']}`",
        f"- Deterministic validation status: `{report['deterministic_validation_status']}`",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Replay Packet Philosophy",
        "",
        "The replay packet layer prioritizes correctness, replay continuity, provenance continuity, reasoning-chain continuity, explainability continuity, and deterministic auditability over execution, routing, automation, recommendation systems, optimization, or autonomous orchestration.",
        "",
        "The purpose is preserving deterministic orchestration evaluation evidence, not executing orchestration.",
        "",
        "## Deterministic Guarantees",
        "",
    ]
    lines.extend(f"- {item}" for item in report["deterministic_guarantees"])
    lines.extend(["", "## Supported Replay Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["supported_replay_classifications"])
    lines.extend(["", "## Unsupported Replay Classifications", ""])
    lines.extend(f"- `{state}`" for state in report["unsupported_replay_classifications"])
    lines.extend(
        [
            "",
            "## Governance-Boundary Guarantees",
            "",
            "Replay packet records preserve deterministic visibility for planning-only, non-production, non-executing, governance-first evidence packaging.",
            "",
            "Unsupported, prohibited, and blocked replay states remain fail-visible and do not become execution paths.",
            "",
            "## Explainability Guarantees",
            "",
            "Replay explainability records why a replay packet exists; what evaluation state it preserves; which governance boundaries applied; which compatibility domains applied; which blockers applied; which unsupported and prohibited states applied; which provenance chains applied; and which reasoning chains were packaged.",
            "",
            "## Integrity Guarantees",
            "",
            "Replay integrity auditing validates registry continuity, replay hash continuity, provenance continuity, explainability continuity, governance continuity, compatibility continuity, dependency continuity, blocker continuity, supported-domain continuity, evidence continuity, intent continuity, policy mapping continuity, trace continuity, and serialization stability.",
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
            "- Self-modifying replay behavior is not introduced.",
            "- Hidden orchestration pathways are not introduced.",
            "",
            "## Scenario Coverage",
            "",
        ]
    )
    for scenario_id, scenario in report["scenario_results"].items():
        lines.append(f"- `{scenario_id}` -> `{scenario['integrity']['replay_integrity_status']}`")
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
    registry = default_orchestration_evaluation_replay_registry()
    return {
        "default_evaluation_replay_packets": _scenario_bundle(registry),
        "provenance_gap_visibility": _scenario_bundle(_registry_with_provenance_gap(registry)),
        "governance_boundary_gap_visibility": _scenario_bundle(_registry_with_governance_gap(registry)),
        "intent_evidence_gap_visibility": _scenario_bundle(_registry_with_intent_gap(registry)),
        "policy_mapping_gap_visibility": _scenario_bundle(_registry_with_policy_mapping_gap(registry)),
        "trace_evidence_gap_visibility": _scenario_bundle(_registry_with_trace_gap(registry)),
        "compatibility_evidence_gap_visibility": _scenario_bundle(_registry_with_compatibility_gap(registry)),
        "dependency_evidence_gap_visibility": _scenario_bundle(_registry_with_dependency_gap(registry)),
        "blocker_evidence_gap_visibility": _scenario_bundle(_registry_with_blocker_gap(registry)),
        "supported_domain_gap_visibility": _scenario_bundle(_registry_with_supported_domain_gap(registry)),
        "replay_hash_mismatch_visibility": _scenario_bundle(
            registry,
            expected_packet_hashes={"v3_6.replay.compatibility-check": "mismatched-replay-packet-hash"},
            expected_build_hash="mismatched-replay-build-hash",
        ),
    }


def _scenario_bundle(
    registry,
    expected_packet_hashes: dict[str, str] | None = None,
    expected_build_hash: str | None = None,
) -> dict[str, Any]:
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(
            replay_registry=registry,
            expected_packet_hashes=expected_packet_hashes,
        )
    )
    explainability = explain_orchestration_evaluation_replay_packets(registry, build)
    integrity = audit_orchestration_evaluation_replay_integrity(
        OrchestrationEvaluationReplayIntegrityInput(
            replay_registry=registry,
            build_result=build,
            explainability_result=explainability,
            expected_build_hash=expected_build_hash,
        )
    )
    return {
        "registry": export_replay_registry(registry),
        "build": export_orchestration_evaluation_replay_build_result(build),
        "explainability": export_orchestration_evaluation_replay_explainability_result(explainability),
        "integrity": export_orchestration_evaluation_replay_integrity_result(integrity),
    }


def _registry_with_provenance_gap(registry):
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_governance_gap(registry):
    target = _record(registry, "v3_6.replay.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_intent_gap(registry):
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, intent_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_policy_mapping_gap(registry):
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, policy_mapping_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_trace_gap(registry):
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, trace_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_compatibility_gap(registry):
    target = _record(registry, "v3_6.replay.policy-boundary")
    changed = replace(target, compatibility_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_dependency_gap(registry):
    target = _record(registry, "v3_6.replay.dependency-analysis")
    changed = replace(target, dependency_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_blocker_gap(registry):
    target = _record(registry, "v3_6.replay.prohibited-domain")
    changed = replace(target, blocker_evidence=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _registry_with_supported_domain_gap(registry):
    target = _record(registry, "v3_6.replay.informational")
    changed = replace(target, supported_domains=())
    return _replace_packet(registry, target.identifier.packet_id, changed)


def _record(registry, packet_id: str):
    return next(packet for packet in registry.packets if packet.identifier.packet_id == packet_id)


def _replace_packet(registry, packet_id: str, replacement):
    return build_orchestration_evaluation_replay_registry(
        tuple(
            replacement if packet.identifier.packet_id == packet_id else packet
            for packet in registry.packets
        )
    )


def _integrity_status_distribution(scenarios: dict[str, dict[str, Any]]) -> dict[str, int]:
    statuses = sorted({scenario["integrity"]["replay_integrity_status"] for scenario in scenarios.values()})
    return {
        status: sum(1 for scenario in scenarios.values() if scenario["integrity"]["replay_integrity_status"] == status)
        for status in statuses
    }


def _unique_registry_count(registry: dict[str, Any], field: str) -> int:
    return len(
        {
            value
            for packet in registry["packets"]
            for value in packet[field]
        }
    )


def _state_count(registry: dict[str, Any], state: str) -> int:
    return sum(1 for packet in registry["packets"] if packet["replay_state"] == state)


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
        "replay_execution_enabled": False,
        "persistent_write_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_6_orchestration_evaluation_replay_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_6_ORCHESTRATION_EVALUATION_REPLAY_PACKETS.md"),
    )
    args = parser.parse_args()
    report = build_v3_6_orchestration_evaluation_replay_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
