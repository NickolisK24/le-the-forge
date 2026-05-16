from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_evaluation_replay_models import (
    REPLAY_COMPATIBILITY_BLOCKED,
    REPLAY_DEPENDENCY_BLOCKED,
    REPLAY_GOVERNANCE_BLOCKED,
    REPLAY_PROHIBITED,
    REPLAY_SUPPORTED,
    REPLAY_UNSUPPORTED,
    export_replay_registry,
    hash_replay_registry,
    serialize_replay_registry,
)
from app.runtime_orchestration.orchestration_evaluation_replay_registry import (
    build_orchestration_evaluation_replay_registry,
    default_orchestration_evaluation_replay_registry,
    get_registered_replay_packet,
    get_registered_replay_packet_for_trace,
    registered_replay_packet_ids,
)


def _registry():
    return default_orchestration_evaluation_replay_registry()


def test_replay_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_replay_registry(first) == serialize_replay_registry(second)
    assert hash_replay_registry(first) == hash_replay_registry(second)
    assert export_replay_registry(first)["deterministic_replay_registry_hash"] == hash_replay_registry(first)


def test_replay_registry_totals_are_deterministic():
    packets = export_replay_registry(_registry())["packets"]

    assert len(packets) == 9
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_SUPPORTED) == 3
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_UNSUPPORTED) == 1
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_PROHIBITED) == 2
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_GOVERNANCE_BLOCKED) == 1
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_COMPATIBILITY_BLOCKED) == 1
    assert sum(1 for packet in packets if packet["replay_state"] == REPLAY_DEPENDENCY_BLOCKED) == 1


def test_replay_packet_ids_are_unique_and_stably_ordered():
    ids = registered_replay_packet_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.replay.compatibility-check" in ids
    assert "v3_6.replay.prohibited-domain" in ids


def test_duplicate_replay_packet_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.packets[0], reasoning_chain=("duplicate",))

    with pytest.raises(ValueError, match="Duplicate orchestration evaluation replay packet ids"):
        build_orchestration_evaluation_replay_registry((registry.packets[0], duplicate))


def test_compatibility_check_replay_packet_packages_lineage():
    packet = get_registered_replay_packet(_registry(), "v3_6.replay.compatibility-check")
    by_trace = get_registered_replay_packet_for_trace(_registry(), "v3_6.trace.compatibility-check")

    assert packet is not None
    assert by_trace == packet
    assert packet.replay_state == REPLAY_SUPPORTED
    assert packet.identifier.trace_id == "v3_6.trace.compatibility-check"
    assert packet.identifier.preflight_id == "v3_6.preflight.compatibility-check"
    assert packet.identifier.mapping_id == "v3_6.mapping.compatibility-check"
    assert packet.intent_evidence
    assert packet.policy_mapping_evidence
    assert packet.preflight_evidence
    assert packet.trace_evidence
    assert packet.provenance.replay_reference_ids == ("v3_6.replay.compatibility-check.replay",)
    assert packet.provenance.rollback_reference_ids == ("v3_6.replay.compatibility-check.rollback",)


def test_replay_packets_package_required_evidence_groups():
    packet = get_registered_replay_packet(_registry(), "v3_6.replay.compatibility-check")

    assert packet is not None
    assert len(packet.intent_evidence) == 1
    assert len(packet.policy_mapping_evidence) == 1
    assert len(packet.governance_evidence) == 1
    assert len(packet.compatibility_evidence) == 1
    assert len(packet.blocker_evidence) == 1
    assert len(packet.preflight_evidence) == 1
    assert len(packet.trace_evidence) == 1
    assert len(packet.provenance_evidence) == 1
    assert len(packet.explainability_evidence) == 1
    assert len(packet.integrity_evidence) == 1
    assert len(packet.reasoning_chain) == 7


def test_blocked_unsupported_and_prohibited_replay_packets_remain_fail_visible():
    governance = get_registered_replay_packet(_registry(), "v3_6.replay.governance-review")
    dependency = get_registered_replay_packet(_registry(), "v3_6.replay.dependency-analysis")
    unsupported = get_registered_replay_packet(_registry(), "v3_6.replay.unsupported-domain")
    prohibited = get_registered_replay_packet(_registry(), "v3_6.replay.prohibited-domain")

    assert governance is not None
    assert dependency is not None
    assert unsupported is not None
    assert prohibited is not None
    assert governance.replay_state == REPLAY_GOVERNANCE_BLOCKED
    assert "governance_conflict_visibility" in governance.blocker_domains
    assert dependency.replay_state == REPLAY_DEPENDENCY_BLOCKED
    assert "dependency_conflict" in dependency.dependency_domains
    assert unsupported.replay_state == REPLAY_UNSUPPORTED
    assert "autonomous_orchestration" in unsupported.unsupported_domains
    assert unsupported.unsupported_evidence
    assert prohibited.replay_state == REPLAY_PROHIBITED
    assert "orchestration_execution" in prohibited.prohibited_domains
    assert prohibited.prohibited_evidence


def test_replay_packets_are_non_executing_and_planning_only():
    for packet in _registry().packets:
        assert packet.runtime_execution_enabled is False
        assert packet.orchestration_execution_enabled is False
        assert packet.routing_behavior_enabled is False
        assert packet.mutation_behavior_enabled is False
        assert packet.production_consumption_enabled is False
        assert packet.background_processing_enabled is False
        assert packet.recommendation_behavior_enabled is False
        assert packet.optimization_behavior_enabled is False
        assert packet.autonomous_behavior_enabled is False
        assert packet.graph_execution_enabled is False
        assert packet.replay_execution_enabled is False
        assert packet.persistent_write_enabled is False
