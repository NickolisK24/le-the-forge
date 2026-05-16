from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_chain_auditor import (
    audit_orchestration_evaluation_chain_integrity,
    default_orchestration_evaluation_chain_audit_input,
)
from app.runtime_orchestration.orchestration_evaluation_chain_models import (
    CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP,
    CHAIN_AUDIT_STABLE,
    CHAIN_CONTINUITY_GAP,
    CHAIN_CONTINUITY_PRESERVED,
    CHAIN_LINK_MISSING,
    CHAIN_LINK_TRACE,
    CHAIN_VALID,
    serialize_chain_audit_result,
    hash_chain_audit_result,
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


def test_chain_audit_default_full_chain_is_stable():
    result = audit_orchestration_evaluation_chain_integrity()

    assert result.chain_audit_status == CHAIN_AUDIT_STABLE
    assert result.audited_chain_count == 9
    assert result.valid_chain_count == 9
    assert result.invalid_chain_count == 0
    assert result.trace_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.preflight_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.mapping_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.intent_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.policy_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.blocker_chain_continuity_status == CHAIN_CONTINUITY_PRESERVED
    assert result.replay_safety_status == CHAIN_CONTINUITY_PRESERVED
    assert result.rollback_safety_status == CHAIN_CONTINUITY_PRESERVED
    assert {record.chain_state for record in result.audit_records} == {CHAIN_VALID}


def test_chain_audit_serialization_and_hash_are_stable():
    result = audit_orchestration_evaluation_chain_integrity()

    assert serialize_chain_audit_result(result) == serialize_chain_audit_result(result)
    assert hash_chain_audit_result(result) == hash_chain_audit_result(result)
    assert result.deterministic_chain_audit_hash == hash_chain_audit_result(result)


def test_chain_audit_preserves_unsupported_and_prohibited_visibility():
    result = audit_orchestration_evaluation_chain_integrity()

    unsupported_records = [record for record in result.audit_records if record.unsupported_domains]
    prohibited_records = [record for record in result.audit_records if record.prohibited_domains]

    assert unsupported_records
    assert prohibited_records
    assert all(record.chain_state == CHAIN_VALID for record in unsupported_records)
    assert all(record.chain_state == CHAIN_VALID for record in prohibited_records)
    assert all(record.blocker_visibility for record in prohibited_records)
    assert all(record.replay_safe for record in result.audit_records)
    assert all(record.rollback_safe for record in result.audit_records)


def test_chain_audit_trace_gap_is_fail_visible():
    registry = default_orchestration_evaluation_replay_registry()
    target = next(packet for packet in registry.packets if packet.identifier.packet_id == "v3_6.replay.compatibility-check")
    changed = replace(target, trace_evidence=())
    changed_registry = build_orchestration_evaluation_replay_registry(
        changed if packet.identifier.packet_id == target.identifier.packet_id else packet
        for packet in registry.packets
    )
    result = audit_orchestration_evaluation_chain_integrity(_chain_input_for_registry(changed_registry))

    assert result.chain_audit_status == CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    assert result.valid_chain_count == 8
    assert result.invalid_chain_count == 1
    assert result.trace_continuity_status == CHAIN_CONTINUITY_GAP
    assert any(
        finding.link_type == CHAIN_LINK_TRACE and finding.classification == CHAIN_LINK_MISSING
        for finding in result.finding_summary
    )


def test_chain_audit_expected_hash_mismatch_is_fail_visible():
    first = audit_orchestration_evaluation_chain_integrity()
    chain_id = first.audit_records[0].identifier.chain_id
    result = audit_orchestration_evaluation_chain_integrity(
        replace(
            default_orchestration_evaluation_chain_audit_input(),
            expected_chain_hashes={chain_id: "not-the-deterministic-chain-hash"},
        )
    )

    assert result.chain_audit_status == CHAIN_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    assert result.invalid_chain_count == 1
    assert result.integrity_continuity_status == CHAIN_CONTINUITY_GAP


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
