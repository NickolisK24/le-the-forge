"""Provenance continuity for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_evaluation_models import V37GraphEvaluationChain, V37GraphEvaluationReplayPacket
from .v3_7_graph_evaluation_replay import build_v3_7_graph_evaluation_replay_packets
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain
from .v3_7_graph_models import V37GraphProvenance


V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED = "v3_7_graph_evaluation_provenance_preserved"
V37_GRAPH_EVALUATION_PROVENANCE_BLOCKED = "v3_7_graph_evaluation_provenance_blocked"


@dataclass(frozen=True)
class V37GraphEvaluationProvenanceResult:
    provenance_status: str
    chain_provenance_preserved: bool
    step_provenance_preserved: bool
    finding_provenance_preserved: bool
    trace_provenance_preserved: bool
    replay_provenance_preserved: bool
    compatibility_provenance_preserved: bool
    governance_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_evaluation_provenance(
    chain: V37GraphEvaluationChain | None = None,
    replay_packets: tuple[V37GraphEvaluationReplayPacket, ...] | None = None,
) -> V37GraphEvaluationProvenanceResult:
    evaluation_chain = chain or build_v3_7_graph_evaluation_chain()
    packets = replay_packets or build_v3_7_graph_evaluation_replay_packets(evaluation_chain)
    missing: list[str] = []
    chain_ok = _provenance_complete(evaluation_chain.provenance)
    if not chain_ok:
        missing.append(evaluation_chain.chain_id)
    step_ok = _all_complete(((step.step_id, step.provenance) for step in evaluation_chain.steps), missing)
    finding_ok = _all_complete(((finding.finding_id, finding.provenance) for finding in evaluation_chain.findings), missing)
    trace_ok = all(trace.provenance_evidence_ids for trace in evaluation_chain.traces)
    if not trace_ok:
        missing.append("evaluation_traces")
    replay_ok = all(
        packet.provenance_lineage_references
        and packet.replay_lineage_references
        and packet.rollback_lineage_references
        for packet in packets
    )
    if not replay_ok:
        missing.append("evaluation_replay_packets")
    records = collect_v3_7_graph_evaluation_provenance(evaluation_chain)
    compatibility_ok = all(record.compatibility_references for record in records) and all(
        packet.compatibility_hash for packet in packets
    )
    governance_ok = all(record.governance_references for record in records)
    explainability_ok = all(record.explainability_references for record in records) and all(
        packet.explainability_lineage_references for packet in packets
    )
    continuity_ok = bool(evaluation_chain.continuity_evidence) and all(
        evidence.provenance_lineage_references
        and evidence.compatibility_lineage_references
        and evidence.governance_lineage_references
        for evidence in evaluation_chain.continuity_evidence
    )
    replay_continuity_ok = all(record.replay_lineage_references for record in records) and all(
        packet.replay_lineage_references for packet in packets
    )
    rollback_continuity_ok = all(record.rollback_lineage_references for record in records) and all(
        packet.rollback_lineage_references for packet in packets
    )
    preserved = all(
        (
            chain_ok,
            step_ok,
            finding_ok,
            trace_ok,
            replay_ok,
            compatibility_ok,
            governance_ok,
            explainability_ok,
            continuity_ok,
            replay_continuity_ok,
            rollback_continuity_ok,
        )
    )
    result = V37GraphEvaluationProvenanceResult(
        provenance_status=(
            V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED
            if preserved
            else V37_GRAPH_EVALUATION_PROVENANCE_BLOCKED
        ),
        chain_provenance_preserved=chain_ok,
        step_provenance_preserved=step_ok,
        finding_provenance_preserved=finding_ok,
        trace_provenance_preserved=trace_ok,
        replay_provenance_preserved=replay_ok,
        compatibility_provenance_preserved=compatibility_ok,
        governance_provenance_preserved=governance_ok,
        explainability_provenance_preserved=explainability_ok,
        continuity_provenance_preserved=continuity_ok,
        replay_continuity_preserved=replay_continuity_ok,
        rollback_continuity_preserved=rollback_continuity_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_evaluation_provenance_result(result),
    )


def collect_v3_7_graph_evaluation_provenance(
    chain: V37GraphEvaluationChain,
) -> tuple[V37GraphProvenance, ...]:
    records = [chain.provenance]
    records.extend(step.provenance for step in chain.steps)
    records.extend(finding.provenance for finding in chain.findings)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_evaluation_provenance_result(
    result: V37GraphEvaluationProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_evaluation_provenance_result(
    result: V37GraphEvaluationProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_evaluation_provenance_result(result))


def hash_v3_7_graph_evaluation_provenance_result(
    result: V37GraphEvaluationProvenanceResult,
) -> str:
    data = export_v3_7_graph_evaluation_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _all_complete(records: object, missing: list[str]) -> bool:
    complete = True
    for subject_id, provenance in records:
        if not _provenance_complete(provenance):
            missing.append(subject_id)
            complete = False
    return complete


def _provenance_complete(provenance: V37GraphProvenance) -> bool:
    return all(
        (
            provenance.provenance_id,
            provenance.source_phase_id,
            provenance.source_artifact_id,
            provenance.source_kind,
            provenance.lineage_references,
            provenance.replay_lineage_references,
            provenance.rollback_lineage_references,
            provenance.governance_references,
            provenance.compatibility_references,
            provenance.explainability_references,
        )
    )
