from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_chain_auditor import (
    audit_orchestration_evaluation_chain_integrity,
    default_orchestration_evaluation_chain_audit_input,
)
from app.runtime_orchestration.orchestration_evaluation_chain_explainability import (
    explain_orchestration_evaluation_chain_integrity,
)
from app.runtime_orchestration.orchestration_evaluation_chain_models import (
    CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    CHAIN_EXPLAINABILITY_STABLE,
    CHAIN_LINK_TRACE,
    serialize_chain_explainability_result,
    hash_chain_explainability_result,
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


def test_chain_explainability_default_is_stable_and_visible():
    audit = audit_orchestration_evaluation_chain_integrity()
    result = explain_orchestration_evaluation_chain_integrity(audit)

    assert result.chain_explainability_status == CHAIN_EXPLAINABILITY_STABLE
    assert len(result.explanation_records) == audit.audited_chain_count
    assert result.valid_link_count >= audit.audited_chain_count
    assert result.missing_link_count == 0
    assert result.blocker_visibility_count > 0
    assert result.provenance_visibility_count == audit.audited_chain_count
    assert result.explainability_visibility_count == audit.audited_chain_count
    assert result.integrity_visibility_count == audit.audited_chain_count


def test_chain_explainability_serialization_and_hash_are_stable():
    result = explain_orchestration_evaluation_chain_integrity()

    assert serialize_chain_explainability_result(result) == serialize_chain_explainability_result(result)
    assert hash_chain_explainability_result(result) == hash_chain_explainability_result(result)
    assert result.deterministic_chain_explainability_hash == hash_chain_explainability_result(result)


def test_chain_explainability_makes_trace_gap_visible():
    registry = default_orchestration_evaluation_replay_registry()
    target = next(packet for packet in registry.packets if packet.identifier.packet_id == "v3_6.replay.compatibility-check")
    changed = replace(target, trace_evidence=())
    changed_registry = build_orchestration_evaluation_replay_registry(
        changed if packet.identifier.packet_id == target.identifier.packet_id else packet
        for packet in registry.packets
    )
    audit = audit_orchestration_evaluation_chain_integrity(_chain_input_for_registry(changed_registry))
    result = explain_orchestration_evaluation_chain_integrity(audit)

    assert result.chain_explainability_status == CHAIN_EXPLAINABILITY_STABLE
    assert result.missing_link_count == 1
    record = next(item for item in result.explanation_records if item.chain_id == "v3_6.chain.compatibility-check")
    assert any(CHAIN_LINK_TRACE in item for item in record.missing_link_visibility)


def test_chain_explainability_blocks_when_required_visibility_is_absent():
    registry = default_orchestration_evaluation_replay_registry()
    target = next(packet for packet in registry.packets if packet.identifier.packet_id == "v3_6.replay.compatibility-check")
    changed = replace(target, governance_evidence=())
    changed_registry = build_orchestration_evaluation_replay_registry(
        changed if packet.identifier.packet_id == target.identifier.packet_id else packet
        for packet in registry.packets
    )
    audit = audit_orchestration_evaluation_chain_integrity(_chain_input_for_registry(changed_registry))
    result = explain_orchestration_evaluation_chain_integrity(audit)

    assert result.chain_explainability_status == CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    record = next(item for item in result.explanation_records if item.chain_id == "v3_6.chain.compatibility-check")
    assert record.explanation_status == CHAIN_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP


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
