from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_replay_builder import (
    build_orchestration_evaluation_replay_packets,
    export_orchestration_evaluation_replay_build_result,
    hash_orchestration_evaluation_replay_build_result,
    serialize_orchestration_evaluation_replay_build_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (
    REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP,
    REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS,
    REPLAY_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    REPLAY_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    REPLAY_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    REPLAY_CONTINUITY_GAP,
    REPLAY_CONTINUITY_PRESERVED,
    REPLAY_GOVERNANCE_BOUNDARY_GAP,
    REPLAY_HASH_MISMATCH,
    REPLAY_INTENT_GAP,
    REPLAY_POLICY_MAPPING_GAP,
    REPLAY_PROHIBITED_EVIDENCE_VISIBLE,
    REPLAY_PROVENANCE_GAP,
    REPLAY_TRACE_GAP,
    REPLAY_UNSUPPORTED_EVIDENCE_VISIBLE,
    OrchestrationEvaluationReplayBuildInput,
    hash_replay_registry,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)


def _registry():
    return default_orchestration_evaluation_replay_registry()


def _build(registry=None, **kwargs):
    return build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_evaluation_replay_build_result(result or _build())


def _record(registry, packet_id):
    return next(packet for packet in registry.packets if packet.identifier.packet_id == packet_id)


def _replace_packet(registry, packet_id, replacement):
    return build_orchestration_evaluation_replay_registry(
        tuple(
            replacement if packet.identifier.packet_id == packet_id else packet
            for packet in registry.packets
        )
    )


def test_default_replay_build_preserves_visible_evidence_packets():
    result = _export()

    assert result["replay_build_status"] == REPLAY_BUILD_STABLE_WITH_VISIBLE_FINDINGS
    assert result["registered_replay_packet_count"] == 9
    assert result["governance_evidence_count"] == 9
    assert result["compatibility_evidence_count"] == 8
    assert result["dependency_evidence_count"] == 3
    assert result["blocker_evidence_count"] == 8
    assert result["unsupported_replay_count"] == 3
    assert result["prohibited_replay_count"] == 3
    assert result["preflight_evidence_count"] == 9
    assert result["trace_evidence_count"] == 9
    assert result["intent_evidence_count"] == 9
    assert result["policy_mapping_evidence_count"] == 9
    assert result["reasoning_step_count"] == 70
    assert result["provenance_continuity_status"] == REPLAY_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == REPLAY_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == REPLAY_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == REPLAY_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["replay_execution_enabled"] is False
    assert result["persistent_write_enabled"] is False


def test_replay_build_serialization_and_hash_are_replay_stable():
    first = _build()
    second = _build()

    assert serialize_orchestration_evaluation_replay_build_result(first) == serialize_orchestration_evaluation_replay_build_result(second)
    assert hash_orchestration_evaluation_replay_build_result(first) == hash_orchestration_evaluation_replay_build_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_blocked_replay_states_are_fail_visible():
    result = _export()
    governance = next(record for record in result["build_records"] if record["packet_id"] == "v3_6.replay.governance-review")
    compatibility = next(record for record in result["build_records"] if record["packet_id"] == "v3_6.replay.policy-boundary")
    dependency = next(record for record in result["build_records"] if record["packet_id"] == "v3_6.replay.dependency-analysis")

    assert any(finding["classification"] == REPLAY_CLASSIFIED_AS_GOVERNANCE_BLOCKED for finding in governance["findings"])
    assert any(finding["classification"] == REPLAY_CLASSIFIED_AS_COMPATIBILITY_BLOCKED for finding in compatibility["findings"])
    assert any(finding["classification"] == REPLAY_CLASSIFIED_AS_DEPENDENCY_BLOCKED for finding in dependency["findings"])


def test_unsupported_and_prohibited_replay_evidence_are_fail_visible():
    result = _export()
    unsupported = next(record for record in result["build_records"] if record["packet_id"] == "v3_6.replay.unsupported-domain")
    prohibited = next(record for record in result["build_records"] if record["packet_id"] == "v3_6.replay.prohibited-domain")

    assert unsupported["unsupported_evidence_count"] == 1
    assert any(finding["classification"] == REPLAY_UNSUPPORTED_EVIDENCE_VISIBLE for finding in unsupported["findings"])
    assert prohibited["prohibited_evidence_count"] == 1
    assert any(finding["classification"] == REPLAY_PROHIBITED_EVIDENCE_VISIBLE for finding in prohibited["findings"])


def test_hash_mismatch_and_provenance_gap_are_structural_findings():
    registry = _registry()
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = _replace_packet(registry, target.identifier.packet_id, changed)
    result = _export(
        _build(
            changed_registry,
            expected_registry_hash="mismatched-replay-registry-hash",
            expected_packet_hashes={target.identifier.packet_id: "mismatched-replay-packet-hash"},
        )
    )

    assert result["replay_build_status"] == REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == REPLAY_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_replay_registry(changed_registry)
    assert any(finding["classification"] == REPLAY_HASH_MISMATCH for finding in result["finding_summary"])
    assert any(finding["classification"] == REPLAY_PROVENANCE_GAP for finding in result["finding_summary"])


def test_governance_boundary_gap_blocks_replay_building():
    registry = _registry()
    target = _record(registry, "v3_6.replay.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_build(_replace_packet(registry, target.identifier.packet_id, changed)))

    assert result["replay_build_status"] == REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == REPLAY_CONTINUITY_GAP
    assert any(finding["classification"] == REPLAY_GOVERNANCE_BOUNDARY_GAP for finding in result["finding_summary"])


def test_intent_mapping_and_trace_gaps_block_replay_building():
    registry = _registry()
    target = _record(registry, "v3_6.replay.compatibility-check")

    intent_result = _export(_build(_replace_packet(registry, target.identifier.packet_id, replace(target, intent_evidence=()))))
    mapping_result = _export(_build(_replace_packet(registry, target.identifier.packet_id, replace(target, policy_mapping_evidence=()))))
    trace_result = _export(_build(_replace_packet(registry, target.identifier.packet_id, replace(target, trace_evidence=()))))

    assert intent_result["replay_build_status"] == REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert any(finding["classification"] == REPLAY_INTENT_GAP for finding in intent_result["finding_summary"])
    assert mapping_result["replay_build_status"] == REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert any(finding["classification"] == REPLAY_POLICY_MAPPING_GAP for finding in mapping_result["finding_summary"])
    assert trace_result["replay_build_status"] == REPLAY_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert any(finding["classification"] == REPLAY_TRACE_GAP for finding in trace_result["finding_summary"])
