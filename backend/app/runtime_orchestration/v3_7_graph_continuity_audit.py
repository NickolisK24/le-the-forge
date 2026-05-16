"""Deterministic continuity auditing for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_evaluation_explainability import (
    V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_evaluation,
)
from .v3_7_graph_evaluation_models import (
    V37_EVALUATION_PROHIBITED,
    V37_EVALUATION_UNKNOWN,
    V37_EVALUATION_UNSUPPORTED,
    V37GraphEvaluationChain,
    V37GraphEvaluationReplayPacket,
    validate_v3_7_graph_evaluation_hash_stability,
    validate_v3_7_graph_evaluation_serialization_stability,
)
from .v3_7_graph_evaluation_provenance import (
    V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_evaluation_provenance,
)
from .v3_7_graph_evaluation_replay import (
    build_v3_7_graph_evaluation_replay_packets,
    validate_v3_7_graph_evaluation_replay_packet_stability,
)
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


V37_GRAPH_CONTINUITY_AUDIT_STABLE = "v3_7_graph_continuity_audit_stable"
V37_GRAPH_CONTINUITY_AUDIT_BLOCKED = "v3_7_graph_continuity_audit_blocked"
V37_GRAPH_CONTINUITY_VISIBLE_PROHIBITED = "v3_7_graph_continuity_visible_prohibited"
V37_GRAPH_CONTINUITY_VISIBLE_UNSUPPORTED = "v3_7_graph_continuity_visible_unsupported"
V37_GRAPH_CONTINUITY_VISIBLE_UNKNOWN = "v3_7_graph_continuity_visible_unknown"
V37_GRAPH_CONTINUITY_BLOCKED_BY_EVALUATION_GAP = "v3_7_graph_continuity_blocked_by_evaluation_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_PROVENANCE_GAP = "v3_7_graph_continuity_blocked_by_provenance_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_EXPLAINABILITY_GAP = "v3_7_graph_continuity_blocked_by_explainability_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_REPLAY_GAP = "v3_7_graph_continuity_blocked_by_replay_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_ROLLBACK_GAP = "v3_7_graph_continuity_blocked_by_rollback_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_SERIALIZATION_GAP = "v3_7_graph_continuity_blocked_by_serialization_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_HASH_GAP = "v3_7_graph_continuity_blocked_by_hash_gap"
V37_GRAPH_CONTINUITY_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_continuity_blocked_by_execution_capability"


@dataclass(frozen=True)
class V37GraphContinuityAuditFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphContinuityAuditResult:
    audit_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    evaluation_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    serialization_continuity_preserved: bool
    hashing_continuity_preserved: bool
    replay_packet_count: int
    deterministic_audit_hash: str
    findings: tuple[V37GraphContinuityAuditFinding, ...]


def audit_v3_7_graph_continuity(
    chain: V37GraphEvaluationChain | None = None,
    replay_packets: tuple[V37GraphEvaluationReplayPacket, ...] | None = None,
) -> V37GraphContinuityAuditResult:
    evaluation_chain = chain or build_v3_7_graph_evaluation_chain()
    packets = replay_packets or build_v3_7_graph_evaluation_replay_packets(evaluation_chain)
    findings: list[V37GraphContinuityAuditFinding] = []
    _add_visibility_findings(evaluation_chain, findings)

    evaluation_ok = _evaluation_continuity_preserved(evaluation_chain)
    if not evaluation_ok:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_EVALUATION_GAP,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation step and trace continuity is incomplete",
            )
        )
    provenance = audit_v3_7_graph_evaluation_provenance(evaluation_chain, packets)
    if provenance.provenance_status != V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_PROVENANCE_GAP,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation provenance continuity is incomplete",
            )
        )
    explainability = explain_v3_7_graph_evaluation(evaluation_chain)
    if explainability.explainability_status != V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_EXPLAINABILITY_GAP,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation explainability continuity is incomplete",
            )
        )
    replay_ok = bool(packets) and all(
        packet.packet_is_non_executable_replay_evidence
        and not packet.orchestration_runtime_packet
        and not packet.execution_authorization
        and packet.replay_lineage_references
        for packet in packets
    )
    if not replay_ok:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_REPLAY_GAP,
                "replay_packets",
                evaluation_chain.chain_id,
                "non-executable replay packet continuity is incomplete",
            )
        )
    rollback_ok = bool(packets) and all(packet.rollback_lineage_references for packet in packets)
    if not rollback_ok:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_ROLLBACK_GAP,
                "replay_packets",
                evaluation_chain.chain_id,
                "rollback continuity is incomplete",
            )
        )
    serialization = validate_v3_7_graph_evaluation_serialization_stability(evaluation_chain)
    if not serialization["stable"]:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_SERIALIZATION_GAP,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation chain serialization is unstable",
            )
        )
    hashing = validate_v3_7_graph_evaluation_hash_stability(evaluation_chain)
    packet_hash_ok = all(validate_v3_7_graph_evaluation_replay_packet_stability(packet)["hash_stable"] for packet in packets)
    if not hashing["stable"] or not packet_hash_ok:
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_HASH_GAP,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation or replay packet hashing is unstable",
            )
        )
    if not _non_execution_guarantee_preserved(evaluation_chain, packets):
        findings.append(
            _finding(
                V37_GRAPH_CONTINUITY_BLOCKED_BY_EXECUTION_CAPABILITY,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation reasoning exposed execution capability",
            )
        )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphContinuityAuditResult(
        audit_status=V37_GRAPH_CONTINUITY_AUDIT_STABLE if error_count == 0 else V37_GRAPH_CONTINUITY_AUDIT_BLOCKED,
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        evaluation_continuity_preserved=evaluation_ok,
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=(
            explainability.explainability_status == V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE
        ),
        governance_continuity_preserved=provenance.governance_provenance_preserved,
        compatibility_continuity_preserved=provenance.compatibility_provenance_preserved,
        replay_continuity_preserved=replay_ok,
        rollback_continuity_preserved=rollback_ok,
        serialization_continuity_preserved=serialization["stable"],
        hashing_continuity_preserved=hashing["stable"] and packet_hash_ok,
        replay_packet_count=len(packets),
        deterministic_audit_hash="",
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_audit_hash=hash_v3_7_graph_continuity_audit_result(result))


def export_v3_7_graph_continuity_audit_finding(finding: V37GraphContinuityAuditFinding) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_continuity_audit_result(result: V37GraphContinuityAuditResult) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_continuity_audit_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_continuity_audit_result(result: V37GraphContinuityAuditResult) -> str:
    return stable_serialize(export_v3_7_graph_continuity_audit_result(result))


def hash_v3_7_graph_continuity_audit_result(result: V37GraphContinuityAuditResult) -> str:
    data = export_v3_7_graph_continuity_audit_result(result)
    data.pop("deterministic_audit_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    chain: V37GraphEvaluationChain,
    findings: list[V37GraphContinuityAuditFinding],
) -> None:
    status_by_classification = {
        V37_EVALUATION_PROHIBITED: V37_GRAPH_CONTINUITY_VISIBLE_PROHIBITED,
        V37_EVALUATION_UNSUPPORTED: V37_GRAPH_CONTINUITY_VISIBLE_UNSUPPORTED,
        V37_EVALUATION_UNKNOWN: V37_GRAPH_CONTINUITY_VISIBLE_UNKNOWN,
    }
    for finding in chain.findings:
        status = status_by_classification.get(finding.finding_classification)
        if status:
            findings.append(
                _finding(
                    status,
                    finding.subject_type,
                    finding.subject_id,
                    f"{finding.finding_classification} evaluation finding remains fail-visible",
                    severity="visibility",
                )
            )


def _evaluation_continuity_preserved(chain: V37GraphEvaluationChain) -> bool:
    orders = [step.step_order for step in chain.steps]
    expected = list(range(1, len(chain.steps) + 1))
    trace_step_ids = {trace.step_id for trace in chain.traces}
    step_ids = {step.step_id for step in chain.steps}
    return (
        orders == expected
        and len(set(orders)) == len(orders)
        and step_ids == trace_step_ids
        and bool(chain.continuity_evidence)
        and all(evidence.step_ids and evidence.trace_ids and evidence.finding_ids for evidence in chain.continuity_evidence)
    )


def _non_execution_guarantee_preserved(
    chain: V37GraphEvaluationChain,
    packets: tuple[V37GraphEvaluationReplayPacket, ...],
) -> bool:
    chain_flags = (
        chain.evaluation_reasoning_is_non_executable,
        chain.replay_packets_are_not_orchestration_packets,
        chain.evaluation_traces_do_not_imply_traversal,
        chain.evaluation_ordering_does_not_imply_execution_ordering,
        chain.evaluation_findings_are_structural_reasoning_evidence_only,
        chain.graph_evaluation_does_not_authorize_orchestration,
        not chain.graph_execution_enabled,
        not chain.traversal_execution_enabled,
        not chain.runtime_orchestration_enabled,
        not chain.routing_enabled,
        not chain.scheduling_enabled,
        not chain.dispatch_enabled,
        not chain.path_selection_enabled,
        not chain.graph_optimization_enabled,
        not chain.recommendation_enabled,
        not chain.autonomous_orchestration_enabled,
        not chain.runtime_mutation_enabled,
        not chain.graph_runtime_simulation_enabled,
        not chain.hidden_evaluation_side_effects_enabled,
    )
    packet_flags = tuple(
        packet.packet_is_non_executable_replay_evidence
        and not packet.orchestration_runtime_packet
        and not packet.execution_authorization
        and not packet.routing_enabled
        and not packet.scheduling_enabled
        and not packet.dispatch_enabled
        for packet in packets
    )
    trace_flags = tuple(
        not trace.trace_implies_traversal and not trace.trace_authorizes_execution and not trace.trace_has_side_effects
        for trace in chain.traces
    )
    step_flags = tuple(
        not step.executable_workflow and not step.traversal_enabled and not step.execution_ordering_enabled
        for step in chain.steps
    )
    return all(chain_flags) and all(packet_flags) and all(trace_flags) and all(step_flags)


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphContinuityAuditFinding:
    return V37GraphContinuityAuditFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
