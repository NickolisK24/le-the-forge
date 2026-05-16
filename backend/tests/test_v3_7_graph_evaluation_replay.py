from __future__ import annotations

from app.runtime_orchestration.v3_7_graph_evaluation_models import (
    hash_v3_7_graph_evaluation_replay_packet,
    serialize_v3_7_graph_evaluation_replay_packet,
)
from app.runtime_orchestration.v3_7_graph_evaluation_replay import (
    build_v3_7_graph_evaluation_replay_packets,
    validate_v3_7_graph_evaluation_replay_packet_stability,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def test_replay_packet_is_non_executable_evidence_not_orchestration_packet():
    chain = build_v3_7_graph_evaluation_chain()
    packets = build_v3_7_graph_evaluation_replay_packets(chain)
    packet = packets[0]

    assert len(packets) == 1
    assert packet.packet_is_non_executable_replay_evidence is True
    assert packet.orchestration_runtime_packet is False
    assert packet.execution_authorization is False
    assert packet.routing_enabled is False
    assert packet.scheduling_enabled is False
    assert packet.dispatch_enabled is False
    assert tuple(packet.trace_ids) == tuple(trace.trace_id for trace in chain.traces)


def test_replay_packet_hash_and_serialization_are_stable():
    packet = build_v3_7_graph_evaluation_replay_packets()[0]
    stability = validate_v3_7_graph_evaluation_replay_packet_stability(packet)

    assert serialize_v3_7_graph_evaluation_replay_packet(packet) == serialize_v3_7_graph_evaluation_replay_packet(packet)
    assert packet.deterministic_replay_hash == hash_v3_7_graph_evaluation_replay_packet(packet)
    assert stability["serialization_stable"] is True
    assert stability["hash_stable"] is True


def test_replay_packet_preserves_replay_and_rollback_lineage():
    packet = build_v3_7_graph_evaluation_replay_packets()[0]

    assert packet.replay_lineage_references
    assert packet.rollback_lineage_references
    assert packet.provenance_lineage_references
    assert packet.explainability_lineage_references
    assert packet.deterministic_trace_references
