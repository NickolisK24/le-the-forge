"""Non-executable replay packet evidence for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .v3_7_graph_compatibility_models import hash_v3_7_compatibility_map
from .v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from .v3_7_graph_evaluation_models import (
    V37GraphEvaluationChain,
    V37GraphEvaluationReplayPacket,
    export_v3_7_graph_evaluation_replay_packet,
    hash_v3_7_graph_evaluation_chain,
    hash_v3_7_graph_evaluation_replay_packet,
    serialize_v3_7_graph_evaluation_replay_packet,
    validate_v3_7_graph_evaluation_replay_packet_hash_stability,
)
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


def build_v3_7_graph_evaluation_replay_packets(
    chain: V37GraphEvaluationChain | None = None,
) -> tuple[V37GraphEvaluationReplayPacket, ...]:
    evaluation_chain = chain or build_v3_7_graph_evaluation_chain()
    compatibility_map = build_v3_7_graph_compatibility_map()
    packet = V37GraphEvaluationReplayPacket(
        replay_packet_id="v3_7_graph_evaluation_replay_packet",
        chain_id=evaluation_chain.chain_id,
        graph_id=evaluation_chain.graph_id,
        trace_ids=tuple(trace.trace_id for trace in evaluation_chain.traces),
        finding_ids=tuple(finding.finding_id for finding in evaluation_chain.findings),
        evaluation_chain_hash=hash_v3_7_graph_evaluation_chain(evaluation_chain),
        compatibility_hash=hash_v3_7_compatibility_map(compatibility_map),
        provenance_lineage_references=tuple(
            sorted({evaluation_chain.provenance.provenance_id} | {step.provenance.provenance_id for step in evaluation_chain.steps})
        ),
        explainability_lineage_references=("v3_7_graph_evaluation_explainability",),
        deterministic_trace_references=tuple(trace.deterministic_ordering_key for trace in evaluation_chain.traces),
        replay_lineage_references=("v3_7_graph_evaluation_replay_continuity",),
        rollback_lineage_references=("v3_7_graph_evaluation_rollback_continuity",),
    )
    return (
        replace(
            packet,
            deterministic_replay_hash=hash_v3_7_graph_evaluation_replay_packet(packet),
        ),
    )


def validate_v3_7_graph_evaluation_replay_packet_stability(
    packet: V37GraphEvaluationReplayPacket,
) -> dict[str, Any]:
    serialization_first = serialize_v3_7_graph_evaluation_replay_packet(packet)
    serialization_second = serialize_v3_7_graph_evaluation_replay_packet(packet)
    hash_stability = validate_v3_7_graph_evaluation_replay_packet_hash_stability(packet)
    return {
        "serialization_stable": serialization_first == serialization_second,
        "hash_stable": hash_stability["stable"],
        "packet_is_non_executable_replay_evidence": packet.packet_is_non_executable_replay_evidence,
        "orchestration_runtime_packet": packet.orchestration_runtime_packet,
        "execution_authorization": packet.execution_authorization,
        "routing_enabled": packet.routing_enabled,
        "scheduling_enabled": packet.scheduling_enabled,
        "dispatch_enabled": packet.dispatch_enabled,
        "packet_hash": packet.deterministic_replay_hash,
    }


def export_v3_7_graph_evaluation_replay_packets(
    packets: tuple[V37GraphEvaluationReplayPacket, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_evaluation_replay_packet(packet)
        for packet in sorted(packets, key=lambda item: item.replay_packet_id)
    ]
