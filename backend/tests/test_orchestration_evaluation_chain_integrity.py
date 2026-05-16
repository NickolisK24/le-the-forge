from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_chain_auditor import (
    audit_orchestration_evaluation_chain_integrity,
    default_orchestration_evaluation_chain_audit_input,
)
from app.runtime_orchestration.orchestration_evaluation_chain_explainability import (
    explain_orchestration_evaluation_chain_integrity,
)
from app.runtime_orchestration.orchestration_evaluation_chain_integrity import (
    audit_orchestration_evaluation_chain_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_chain_models import (
    CHAIN_CONTINUITY_GAP,
    CHAIN_INTEGRITY_BLOCKED_BY_CONTINUITY_GAP,
    CHAIN_INTEGRITY_BLOCKED_BY_HASH_GAP,
    CHAIN_INTEGRITY_STABLE,
    OrchestrationEvaluationChainIntegrityInput,
    serialize_chain_integrity_result,
    hash_chain_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_replay_builder import (
    build_orchestration_evaluation_replay_packets,
)
from app.runtime_orchestration.orchestration_evaluation_replay_explainability import (
    explain_orchestration_evaluation_replay_packets,
)
from app.runtime_orchestration.orchestration_evaluation_replay_integrity import (
    audit_orchestration_evaluation_replay_integrity,
)
from app.runtime_orchestration.orchestration_evaluation_replay_models import (
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayIntegrityInput,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
)


def test_chain_integrity_default_is_stable():
    result = audit_orchestration_evaluation_chain_integrity_result()

    assert result.chain_integrity_status == CHAIN_INTEGRITY_STABLE
    assert result.failure_classification_summary == ()
    assert result.replay_packet_integrity.failures == ()
    assert result.trace_integrity.failures == ()
    assert result.preflight_integrity.failures == ()
    assert result.mapping_integrity.failures == ()
    assert result.intent_integrity.failures == ()
    assert result.policy_integrity.failures == ()
    assert result.blocker_integrity.failures == ()
    assert result.replay_safety_integrity.failures == ()
    assert result.rollback_safety_integrity.failures == ()


def test_chain_integrity_serialization_and_hash_are_stable():
    result = audit_orchestration_evaluation_chain_integrity_result()

    assert serialize_chain_integrity_result(result) == serialize_chain_integrity_result(result)
    assert hash_chain_integrity_result(result) == hash_chain_integrity_result(result)
    assert result.deterministic_chain_integrity_hash == hash_chain_integrity_result(result)


def test_chain_integrity_trace_gap_is_deterministic_and_explicit():
    registry = default_orchestration_evaluation_replay_registry()
    target = next(packet for packet in registry.packets if packet.identifier.packet_id == "v3_6.replay.compatibility-check")
    changed = replace(target, trace_evidence=())
    changed_registry = build_orchestration_evaluation_replay_registry(
        changed if packet.identifier.packet_id == target.identifier.packet_id else packet
        for packet in registry.packets
    )
    audit = audit_orchestration_evaluation_chain_integrity(_chain_input_for_registry(changed_registry))
    explainability = explain_orchestration_evaluation_chain_integrity(audit)
    result = audit_orchestration_evaluation_chain_integrity_result(
        OrchestrationEvaluationChainIntegrityInput(
            audit_result=audit,
            explainability_result=explainability,
        )
    )

    assert result.chain_integrity_status == CHAIN_INTEGRITY_BLOCKED_BY_CONTINUITY_GAP
    assert audit.trace_continuity_status == CHAIN_CONTINUITY_GAP
    assert "trace:v3_6.chain.compatibility-check:trace_chain:continuity_gap" in result.failure_classification_summary


def test_chain_integrity_expected_hash_mismatch_is_fail_visible():
    audit = audit_orchestration_evaluation_chain_integrity()
    explainability = explain_orchestration_evaluation_chain_integrity(audit)
    result = audit_orchestration_evaluation_chain_integrity_result(
        OrchestrationEvaluationChainIntegrityInput(
            audit_result=audit,
            explainability_result=explainability,
            expected_audit_hash="not-the-chain-audit-hash",
        )
    )

    assert result.chain_integrity_status == CHAIN_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "chain_hash:chain_audit_hash_mismatch" in result.failure_classification_summary


def _chain_input_for_registry(registry):
    build = build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=registry)
    )
    explainability = explain_orchestration_evaluation_replay_packets(registry, build)
    integrity = audit_orchestration_evaluation_replay_integrity(
        OrchestrationEvaluationReplayIntegrityInput(
            replay_registry=registry,
            build_result=build,
            explainability_result=explainability,
        )
    )
    return replace(
        default_orchestration_evaluation_chain_audit_input(),
        replay_registry=registry,
        replay_build_result=build,
        replay_explainability_result=explainability,
        replay_integrity_result=integrity,
    )
