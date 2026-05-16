from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_replay_builder import build_orchestration_evaluation_replay_packets
from app.runtime_orchestration.orchestration_evaluation_replay_explainability import (
    explain_orchestration_evaluation_replay_packets,
    export_orchestration_evaluation_replay_explainability_result,
    hash_orchestration_evaluation_replay_explainability_result,
    serialize_orchestration_evaluation_replay_explainability_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (
    REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    REPLAY_EXPLAINABILITY_STABLE,
    OrchestrationEvaluationReplayBuildInput,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)


def _registry():
    return default_orchestration_evaluation_replay_registry()


def _explain(registry=None, build=None):
    source_registry = registry or _registry()
    source_build = build or build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=source_registry)
    )
    return explain_orchestration_evaluation_replay_packets(source_registry, source_build)


def _export(result=None):
    return export_orchestration_evaluation_replay_explainability_result(result or _explain())


def _record(registry, packet_id):
    return next(packet for packet in registry.packets if packet.identifier.packet_id == packet_id)


def _replace_packet(registry, packet_id, replacement):
    return build_orchestration_evaluation_replay_registry(
        tuple(
            replacement if packet.identifier.packet_id == packet_id else packet
            for packet in registry.packets
        )
    )


def test_replay_explainability_generates_stable_visibility():
    result = _export()

    assert result["replay_explainability_status"] == REPLAY_EXPLAINABILITY_STABLE
    assert result["governance_explanation_count"] == 9
    assert result["compatibility_explanation_count"] == 8
    assert result["dependency_explanation_count"] == 3
    assert result["blocker_explanation_count"] == 8
    assert result["unsupported_explanation_count"] == 3
    assert result["prohibited_explanation_count"] == 3
    assert result["evidence_visibility_count"] == 97
    assert result["reasoning_chain_visibility_count"] == 70
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["replay_execution_enabled"] is False
    assert result["persistent_write_enabled"] is False


def test_replay_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_evaluation_replay_explainability_result(first) == serialize_orchestration_evaluation_replay_explainability_result(second)
    assert hash_orchestration_evaluation_replay_explainability_result(first) == hash_orchestration_evaluation_replay_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatibility_check_explains_packaged_evidence():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["packet_id"] == "v3_6.replay.compatibility-check")

    assert record["replay_state"] == "replay_packet_supported"
    assert "v3_6.intent.compatibility-check" in record["evaluation_state_visibility"]
    assert "v3_6.mapping.compatibility-check" in record["evaluation_state_visibility"]
    assert any("intent_evidence_packet" in evidence for evidence in record["evidence_visibility"])
    assert any("trace_evidence_packet" in evidence for evidence in record["evidence_visibility"])
    assert any("deterministically expose blocker-chain domains" in step for step in record["reasoning_chain_visibility"])
    assert "v3_6.replay.compatibility-check.replay" in record["provenance_visibility"]


def test_blocked_unsupported_and_prohibited_replay_packets_explain_fail_visible_domains():
    result = _export()
    governance = next(item for item in result["explanation_records"] if item["packet_id"] == "v3_6.replay.governance-review")
    unsupported = next(item for item in result["explanation_records"] if item["packet_id"] == "v3_6.replay.unsupported-domain")
    prohibited = next(item for item in result["explanation_records"] if item["packet_id"] == "v3_6.replay.prohibited-domain")

    assert governance["replay_state"] == "replay_packet_governance_blocked"
    assert "governance_conflict_visibility" in governance["blocker_domain_visibility"]
    assert unsupported["replay_state"] == "replay_packet_unsupported"
    assert "autonomous_orchestration" in unsupported["unsupported_domain_visibility"]
    assert "unsupported_domain_blocker" in unsupported["blocker_domain_visibility"]
    assert prohibited["replay_state"] == "replay_packet_prohibited"
    assert "orchestration_execution" in prohibited["prohibited_domain_visibility"]
    assert "prohibited_execution_blocker" in prohibited["blocker_domain_visibility"]


def test_explainability_gap_is_fail_visible_for_missing_reasoning_chain():
    registry = _registry()
    target = _record(registry, "v3_6.replay.informational")
    changed = replace(target, reasoning_chain=())
    changed_registry = _replace_packet(registry, target.identifier.packet_id, changed)
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, build))
    record = next(item for item in result["explanation_records"] if item["packet_id"] == target.identifier.packet_id)

    assert result["replay_explainability_status"] == REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert record["explanation_status"] == REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
