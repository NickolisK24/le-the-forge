from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_replay_builder import build_orchestration_evaluation_replay_packets
from app.runtime_orchestration.orchestration_evaluation_replay_explainability import explain_orchestration_evaluation_replay_packets
from app.runtime_orchestration.orchestration_evaluation_replay_integrity import (
    audit_orchestration_evaluation_replay_integrity,
    export_orchestration_evaluation_replay_integrity_result,
    hash_orchestration_evaluation_replay_integrity_result,
    serialize_orchestration_evaluation_replay_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (
    REPLAY_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_INTENT_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_POLICY_MAPPING_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    REPLAY_INTEGRITY_BLOCKED_BY_TRACE_GAP,
    REPLAY_INTEGRITY_STABLE,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
    hash_replay_registry,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)
from scripts.report_v3_6_orchestration_evaluation_replay_packets import build_v3_6_orchestration_evaluation_replay_report


def _registry():
    return default_orchestration_evaluation_replay_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=source_registry)
    )
    explainability = explain_orchestration_evaluation_replay_packets(source_registry, build)
    return OrchestrationEvaluationReplayIntegrityInput(
        replay_registry=source_registry,
        build_result=build,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_evaluation_replay_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_evaluation_replay_integrity_result(_audit(source))


def _record(registry, packet_id):
    return next(packet for packet in registry.packets if packet.identifier.packet_id == packet_id)


def _replace_packet(registry, packet_id, replacement):
    return build_orchestration_evaluation_replay_registry(
        tuple(
            replacement if packet.identifier.packet_id == packet_id else packet
            for packet in registry.packets
        )
    )


def test_replay_integrity_is_stable_with_visible_evidence():
    result = _export()

    assert result["replay_integrity_status"] == REPLAY_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["governance_integrity"]["references"]) == 9
    assert len(result["intent_integrity"]["references"]) == 9
    assert len(result["policy_mapping_integrity"]["references"]) == 9
    assert len(result["trace_integrity"]["references"]) == 9
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["replay_execution_enabled"] is False
    assert result["persistent_write_enabled"] is False


def test_replay_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_evaluation_replay_integrity_result(first) == serialize_orchestration_evaluation_replay_integrity_result(second)
    assert hash_orchestration_evaluation_replay_integrity_result(first) == hash_orchestration_evaluation_replay_integrity_result(second)
    assert json.dumps(export_orchestration_evaluation_replay_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_evaluation_replay_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-replay-registry-hash")
    result = _export(source)

    assert result["replay_integrity_status"] == REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_replay_registry(source.replay_registry)]
    assert "replay_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.replay.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_packet(registry, target.identifier.packet_id, changed)))

    assert result["replay_integrity_status"] == REPLAY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.replay.compatibility-check:replay_provenance_gap" in result["failure_classification_summary"]


def test_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_build_hash="mismatched-replay-build-hash",
        expected_explainability_hash="mismatched-replay-explainability-hash",
    )
    result = _export(source)

    assert result["replay_integrity_status"] == REPLAY_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "replay_build_hash_mismatch" in result["failure_classification_summary"]
    assert "replay_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_governance_boundary_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.replay.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_integrity_input(_replace_packet(registry, target.identifier.packet_id, changed)))

    assert result["replay_integrity_status"] == REPLAY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.replay.orchestration-simulation:governance_boundary_gap" in result["failure_classification_summary"]


def test_replay_evidence_identity_mapping_trace_and_domain_gaps_fail_integrity():
    registry = _registry()
    target = _record(registry, "v3_6.replay.compatibility-check")
    compatibility = _record(registry, "v3_6.replay.policy-boundary")
    dependency = _record(registry, "v3_6.replay.dependency-analysis")
    blocker = _record(registry, "v3_6.replay.prohibited-domain")
    supported = _record(registry, "v3_6.replay.informational")
    evidence = _record(registry, "v3_6.replay.continuity-analysis")

    assert _export(_integrity_input(_replace_packet(registry, target.identifier.packet_id, replace(target, intent_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_INTENT_GAP
    assert _export(_integrity_input(_replace_packet(registry, target.identifier.packet_id, replace(target, policy_mapping_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_POLICY_MAPPING_GAP
    assert _export(_integrity_input(_replace_packet(registry, target.identifier.packet_id, replace(target, trace_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP
    assert _export(_integrity_input(_replace_packet(registry, compatibility.identifier.packet_id, replace(compatibility, compatibility_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    assert _export(_integrity_input(_replace_packet(registry, dependency.identifier.packet_id, replace(dependency, dependency_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert _export(_integrity_input(_replace_packet(registry, blocker.identifier.packet_id, replace(blocker, blocker_evidence=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    assert _export(_integrity_input(_replace_packet(registry, supported.identifier.packet_id, replace(supported, supported_domains=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    assert _export(_integrity_input(_replace_packet(registry, evidence.identifier.packet_id, replace(evidence, reasoning_chain=()))))[
        "replay_integrity_status"
    ] == REPLAY_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP


def test_replay_report_summarizes_deterministic_packet_totals():
    first = build_v3_6_orchestration_evaluation_replay_report()
    second = build_v3_6_orchestration_evaluation_replay_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_replay_packet_count"] == 9
    assert first["governance_evidence_count"] == 9
    assert first["compatibility_evidence_count"] == 8
    assert first["dependency_evidence_count"] == 3
    assert first["blocker_evidence_count"] == 8
    assert first["unsupported_replay_count"] == 3
    assert first["prohibited_replay_count"] == 3
    assert first["reasoning_step_count"] == 70
    assert first["evidence_visibility_count"] == 97
    assert first["replay_integrity_status"] == REPLAY_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
