"""Deterministic orchestration evaluation replay packet explainability."""

from __future__ import annotations

from dataclasses import replace

from .orchestration_evaluation_replay_builder import build_orchestration_evaluation_replay_packets
from .orchestration_evaluation_replay_models import (
    REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    REPLAY_EXPLAINABILITY_STABLE,
    OrchestrationEvaluationReplayBuildInput,
    OrchestrationEvaluationReplayBuildRecord,
    OrchestrationEvaluationReplayBuildResult,
    OrchestrationEvaluationReplayExplainabilityResult,
    OrchestrationEvaluationReplayExplanationRecord,
    OrchestrationEvaluationReplayPacket,
    OrchestrationEvaluationReplayRegistry,
    export_replay_explainability_result,
    hash_replay_explainability_result,
    serialize_replay_explainability_result,
)
from .orchestration_evaluation_replay_registry import default_orchestration_evaluation_replay_registry


def explain_orchestration_evaluation_replay_packets(
    replay_registry: OrchestrationEvaluationReplayRegistry | None = None,
    build_result: OrchestrationEvaluationReplayBuildResult | None = None,
) -> OrchestrationEvaluationReplayExplainabilityResult:
    registry = replay_registry or default_orchestration_evaluation_replay_registry()
    build = build_result or build_orchestration_evaluation_replay_packets(
        OrchestrationEvaluationReplayBuildInput(replay_registry=registry)
    )
    packets_by_id = {packet.identifier.packet_id: packet for packet in registry.packets}
    build_by_id = {record.packet_id: record for record in build.build_records}
    records = tuple(
        _explain_record(packets_by_id[packet_id], build_by_id[packet_id])
        for packet_id in sorted(packets_by_id)
        if packet_id in build_by_id
    )
    status = (
        REPLAY_EXPLAINABILITY_STABLE
        if all(record.explanation_status == REPLAY_EXPLAINABILITY_STABLE for record in records)
        else REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    result = OrchestrationEvaluationReplayExplainabilityResult(
        registry_id=registry.registry_id,
        replay_explainability_status=status,
        planning_only=True,
        explanation_records=records,
        governance_explanation_count=_packet_count(registry.packets, "governance_evidence"),
        compatibility_explanation_count=_packet_count(registry.packets, "compatibility_evidence"),
        dependency_explanation_count=_packet_count(registry.packets, "dependency_evidence"),
        blocker_explanation_count=_packet_count(registry.packets, "blocker_evidence"),
        unsupported_explanation_count=_packet_count(registry.packets, "unsupported_evidence"),
        prohibited_explanation_count=_packet_count(registry.packets, "prohibited_evidence"),
        evidence_visibility_count=sum(len(record.evidence_visibility) for record in records),
        reasoning_chain_visibility_count=sum(len(record.reasoning_chain_visibility) for record in records),
        deterministic_replay_explainability_hash="",
        deterministic_explanation_summary=_summary(status, records),
    )
    return replace(result, deterministic_replay_explainability_hash=hash_replay_explainability_result(result))


def explain_orchestration_evaluation_replay(
    replay_registry: OrchestrationEvaluationReplayRegistry | None = None,
    build_result: OrchestrationEvaluationReplayBuildResult | None = None,
) -> OrchestrationEvaluationReplayExplainabilityResult:
    return explain_orchestration_evaluation_replay_packets(replay_registry, build_result)


def export_orchestration_evaluation_replay_explainability_result(
    result: OrchestrationEvaluationReplayExplainabilityResult,
) -> dict[str, object]:
    return export_replay_explainability_result(result)


def serialize_orchestration_evaluation_replay_explainability_result(
    result: OrchestrationEvaluationReplayExplainabilityResult,
) -> str:
    return serialize_replay_explainability_result(result)


def hash_orchestration_evaluation_replay_explainability_result(
    result: OrchestrationEvaluationReplayExplainabilityResult,
) -> str:
    return hash_replay_explainability_result(result)


def _explain_record(
    packet: OrchestrationEvaluationReplayPacket,
    build_record: OrchestrationEvaluationReplayBuildRecord,
) -> OrchestrationEvaluationReplayExplanationRecord:
    build_visibility = tuple(
        sorted(
            f"{finding.classification}:{finding.reason}"
            for finding in build_record.findings
        )
    )
    evidence_visibility = _evidence_visibility(packet)
    explanation_status = (
        REPLAY_EXPLAINABILITY_STABLE
        if _has_visibility(packet, build_record, build_visibility, evidence_visibility)
        else REPLAY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    )
    return OrchestrationEvaluationReplayExplanationRecord(
        packet_id=packet.identifier.packet_id,
        trace_id=packet.identifier.trace_id,
        replay_state=packet.replay_state,
        explanation_status=explanation_status,
        evaluation_state_visibility=(
            packet.replay_state,
            packet.identifier.intent_id,
            packet.identifier.mapping_id,
            packet.identifier.preflight_id,
            packet.identifier.trace_id,
        ),
        evidence_visibility=evidence_visibility,
        governance_boundary_visibility=tuple(sorted(packet.governance_boundaries)),
        compatibility_domain_visibility=tuple(sorted(packet.compatibility_domains)),
        dependency_domain_visibility=tuple(sorted(packet.dependency_domains)),
        blocker_domain_visibility=tuple(sorted(packet.blocker_domains)),
        unsupported_domain_visibility=tuple(sorted(packet.unsupported_domains)),
        prohibited_domain_visibility=tuple(sorted(packet.prohibited_domains)),
        supported_domain_visibility=tuple(sorted(packet.supported_domains)),
        reasoning_chain_visibility=tuple(sorted(packet.reasoning_chain)),
        provenance_visibility=_provenance_visibility(packet),
        build_visibility=build_visibility,
        integrity_visibility=tuple(sorted(evidence.evidence_id for evidence in packet.integrity_evidence)),
    )


def _evidence_visibility(packet: OrchestrationEvaluationReplayPacket) -> tuple[str, ...]:
    return tuple(
        sorted(
            f"{evidence.evidence_type}:{evidence.source_id}:{evidence.source_hash}"
            for evidence in _all_evidence(packet)
        )
    )


def _provenance_visibility(packet: OrchestrationEvaluationReplayPacket) -> tuple[str, ...]:
    provenance = packet.provenance
    return tuple(
        sorted(
            (
                provenance.source_phase,
                provenance.source_artifact,
                provenance.packet_id,
                provenance.trace_id,
                provenance.preflight_id,
                provenance.intent_id,
                provenance.mapping_id,
                *provenance.policy_ids,
                *provenance.compatibility_relationship_ids,
                *provenance.trace_reference_ids,
                *provenance.preflight_reference_ids,
                *provenance.replay_reference_ids,
                *provenance.rollback_reference_ids,
                *provenance.governance_reference_ids,
            )
        )
    )


def _has_visibility(
    packet: OrchestrationEvaluationReplayPacket,
    build_record: OrchestrationEvaluationReplayBuildRecord,
    build_visibility: tuple[str, ...],
    evidence_visibility: tuple[str, ...],
) -> bool:
    return bool(
        packet.intent_evidence
        and packet.policy_mapping_evidence
        and packet.preflight_evidence
        and packet.trace_evidence
        and packet.provenance_evidence
        and packet.explainability_evidence
        and packet.integrity_evidence
        and packet.reasoning_chain
        and packet.governance_boundaries
        and build_record.findings
        and build_visibility
        and evidence_visibility
    )


def _packet_count(packets: tuple[OrchestrationEvaluationReplayPacket, ...], field: str) -> int:
    return sum(1 for packet in packets if getattr(packet, field))


def _all_evidence(packet: OrchestrationEvaluationReplayPacket) -> tuple[object, ...]:
    fields = (
        "intent_evidence",
        "policy_mapping_evidence",
        "governance_evidence",
        "compatibility_evidence",
        "dependency_evidence",
        "blocker_evidence",
        "unsupported_evidence",
        "prohibited_evidence",
        "preflight_evidence",
        "trace_evidence",
        "provenance_evidence",
        "explainability_evidence",
        "integrity_evidence",
    )
    return tuple(evidence for field in fields for evidence in getattr(packet, field))


def _summary(
    status: str,
    records: tuple[OrchestrationEvaluationReplayExplanationRecord, ...],
) -> str:
    if status == REPLAY_EXPLAINABILITY_STABLE:
        return (
            "Replay packet explainability is stable; evaluation state, evidence bundles, governance boundaries, "
            "compatibility domains, dependencies, blockers, unsupported domains, prohibited domains, reasoning "
            "chains, provenance, build findings, and integrity evidence are visible."
        )
    missing = tuple(sorted(record.packet_id for record in records if record.explanation_status != REPLAY_EXPLAINABILITY_STABLE))
    return f"Replay packet explainability has visibility gaps for: {', '.join(missing)}."
