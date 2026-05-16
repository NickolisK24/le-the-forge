"""Fail-visible validation for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_continuity_audit import (
    V37_GRAPH_CONTINUITY_AUDIT_STABLE,
    audit_v3_7_graph_continuity,
)
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
    hash_v3_7_graph_evaluation_chain,
    validate_v3_7_graph_evaluation_hash_stability,
    validate_v3_7_graph_evaluation_serialization_stability,
)
from .v3_7_graph_evaluation_provenance import (
    V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_evaluation_provenance,
)
from .v3_7_graph_evaluation_replay import build_v3_7_graph_evaluation_replay_packets
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


V37_GRAPH_EVALUATION_VALIDATION_STABLE = "v3_7_graph_evaluation_validation_stable"
V37_GRAPH_EVALUATION_VALIDATION_BLOCKED = "v3_7_graph_evaluation_validation_blocked"
V37_GRAPH_EVALUATION_VISIBLE_PROHIBITED = "v3_7_graph_evaluation_visible_prohibited"
V37_GRAPH_EVALUATION_VISIBLE_UNSUPPORTED = "v3_7_graph_evaluation_visible_unsupported"
V37_GRAPH_EVALUATION_VISIBLE_UNKNOWN = "v3_7_graph_evaluation_visible_unknown"
V37_GRAPH_EVALUATION_BLOCKED_BY_ORDERING = "v3_7_graph_evaluation_blocked_by_ordering"
V37_GRAPH_EVALUATION_BLOCKED_BY_EVALUATION_CONTINUITY = "v3_7_graph_evaluation_blocked_by_evaluation_continuity"
V37_GRAPH_EVALUATION_BLOCKED_BY_REPLAY_CONTINUITY = "v3_7_graph_evaluation_blocked_by_replay_continuity"
V37_GRAPH_EVALUATION_BLOCKED_BY_ROLLBACK_CONTINUITY = "v3_7_graph_evaluation_blocked_by_rollback_continuity"
V37_GRAPH_EVALUATION_BLOCKED_BY_PROVENANCE = "v3_7_graph_evaluation_blocked_by_provenance"
V37_GRAPH_EVALUATION_BLOCKED_BY_EXPLAINABILITY = "v3_7_graph_evaluation_blocked_by_explainability"
V37_GRAPH_EVALUATION_BLOCKED_BY_SERIALIZATION = "v3_7_graph_evaluation_blocked_by_serialization"
V37_GRAPH_EVALUATION_BLOCKED_BY_HASH = "v3_7_graph_evaluation_blocked_by_hash"
V37_GRAPH_EVALUATION_BLOCKED_BY_EXECUTION_CAPABILITY = "v3_7_graph_evaluation_blocked_by_execution_capability"
V37_GRAPH_EVALUATION_BLOCKED_BY_HIDDEN_FINDING = "v3_7_graph_evaluation_blocked_by_hidden_finding"


@dataclass(frozen=True)
class V37GraphEvaluationValidationFinding:
    finding_id: str
    status: str
    severity: str
    subject_type: str
    subject_id: str
    message: str
    fail_visible: bool = True


@dataclass(frozen=True)
class V37GraphEvaluationValidationResult:
    validation_status: str
    valid: bool
    finding_count: int
    error_count: int
    visibility_finding_count: int
    prohibited_state_count: int
    unsupported_state_count: int
    unknown_state_count: int
    evaluation_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    provenance_continuity_preserved: bool
    explainability_continuity_preserved: bool
    deterministic_serialization_stable: bool
    deterministic_hash_stable: bool
    non_execution_guarantee_preserved: bool
    deterministic_evaluation_hash: str
    findings: tuple[V37GraphEvaluationValidationFinding, ...]
    deterministic_validation_hash: str = ""


def validate_v3_7_graph_evaluation(
    chain: V37GraphEvaluationChain | None = None,
    replay_packets: tuple[V37GraphEvaluationReplayPacket, ...] | None = None,
) -> V37GraphEvaluationValidationResult:
    evaluation_chain = chain or build_v3_7_graph_evaluation_chain()
    packets = replay_packets or build_v3_7_graph_evaluation_replay_packets(evaluation_chain)
    findings: list[V37GraphEvaluationValidationFinding] = []
    _add_visibility_findings(evaluation_chain, findings)

    if not _ordering_valid(evaluation_chain):
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_ORDERING,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation ordering is not deterministic or contiguous",
            )
        )
    audit = audit_v3_7_graph_continuity(evaluation_chain, packets)
    if audit.audit_status != V37_GRAPH_CONTINUITY_AUDIT_STABLE:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_EVALUATION_CONTINUITY,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "graph continuity audit is blocked",
            )
        )
    provenance = audit_v3_7_graph_evaluation_provenance(evaluation_chain, packets)
    if provenance.provenance_status != V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_PROVENANCE,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "graph evaluation provenance continuity is incomplete",
            )
        )
    explainability = explain_v3_7_graph_evaluation(evaluation_chain)
    if explainability.explainability_status != V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_EXPLAINABILITY,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "graph evaluation explainability continuity is incomplete",
            )
        )
    serialization = validate_v3_7_graph_evaluation_serialization_stability(evaluation_chain)
    if not serialization["stable"]:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_SERIALIZATION,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "graph evaluation serialization is unstable",
            )
        )
    hashing = validate_v3_7_graph_evaluation_hash_stability(evaluation_chain)
    if not hashing["stable"]:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_HASH,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "graph evaluation hash is unstable",
            )
        )
    if not audit.replay_continuity_preserved:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_REPLAY_CONTINUITY,
                "replay_packets",
                evaluation_chain.chain_id,
                "replay continuity is incomplete",
            )
        )
    if not audit.rollback_continuity_preserved:
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_ROLLBACK_CONTINUITY,
                "replay_packets",
                evaluation_chain.chain_id,
                "rollback continuity is incomplete",
            )
        )
    if not audit.valid or not _non_execution_guarantee_preserved(evaluation_chain, packets):
        findings.append(
            _finding(
                V37_GRAPH_EVALUATION_BLOCKED_BY_EXECUTION_CAPABILITY,
                "evaluation_chain",
                evaluation_chain.chain_id,
                "evaluation reasoning exposed execution capability",
            )
        )
    for finding in evaluation_chain.findings:
        if finding.hidden or not finding.fail_visible:
            findings.append(
                _finding(
                    V37_GRAPH_EVALUATION_BLOCKED_BY_HIDDEN_FINDING,
                    finding.subject_type,
                    finding.subject_id,
                    "evaluation finding is hidden or not fail-visible",
                )
            )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    visibility_count = sum(1 for finding in findings if finding.severity == "visibility")
    result = V37GraphEvaluationValidationResult(
        validation_status=(
            V37_GRAPH_EVALUATION_VALIDATION_STABLE
            if error_count == 0
            else V37_GRAPH_EVALUATION_VALIDATION_BLOCKED
        ),
        valid=error_count == 0,
        finding_count=len(findings),
        error_count=error_count,
        visibility_finding_count=visibility_count,
        prohibited_state_count=_finding_class_count(evaluation_chain, V37_EVALUATION_PROHIBITED),
        unsupported_state_count=_finding_class_count(evaluation_chain, V37_EVALUATION_UNSUPPORTED),
        unknown_state_count=_finding_class_count(evaluation_chain, V37_EVALUATION_UNKNOWN),
        evaluation_continuity_preserved=audit.evaluation_continuity_preserved,
        replay_continuity_preserved=audit.replay_continuity_preserved,
        rollback_continuity_preserved=audit.rollback_continuity_preserved,
        provenance_continuity_preserved=provenance.provenance_status == V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
        explainability_continuity_preserved=(
            explainability.explainability_status == V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE
        ),
        deterministic_serialization_stable=serialization["stable"],
        deterministic_hash_stable=hashing["stable"],
        non_execution_guarantee_preserved=_non_execution_guarantee_preserved(evaluation_chain, packets),
        deterministic_evaluation_hash=hash_v3_7_graph_evaluation_chain(evaluation_chain),
        findings=tuple(sorted(findings, key=lambda item: item.finding_id)),
    )
    return replace(result, deterministic_validation_hash=hash_v3_7_graph_evaluation_validation_result(result))


def export_v3_7_graph_evaluation_validation_finding(
    finding: V37GraphEvaluationValidationFinding,
) -> dict[str, Any]:
    return asdict(finding)


def export_v3_7_graph_evaluation_validation_result(
    result: V37GraphEvaluationValidationResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["findings"] = [
        export_v3_7_graph_evaluation_validation_finding(finding)
        for finding in sorted(result.findings, key=lambda item: item.finding_id)
    ]
    return data


def serialize_v3_7_graph_evaluation_validation_result(
    result: V37GraphEvaluationValidationResult,
) -> str:
    return stable_serialize(export_v3_7_graph_evaluation_validation_result(result))


def hash_v3_7_graph_evaluation_validation_result(
    result: V37GraphEvaluationValidationResult,
) -> str:
    data = export_v3_7_graph_evaluation_validation_result(result)
    data.pop("deterministic_validation_hash", None)
    return deterministic_hash(data)


def _add_visibility_findings(
    chain: V37GraphEvaluationChain,
    findings: list[V37GraphEvaluationValidationFinding],
) -> None:
    status_by_classification = {
        V37_EVALUATION_PROHIBITED: V37_GRAPH_EVALUATION_VISIBLE_PROHIBITED,
        V37_EVALUATION_UNSUPPORTED: V37_GRAPH_EVALUATION_VISIBLE_UNSUPPORTED,
        V37_EVALUATION_UNKNOWN: V37_GRAPH_EVALUATION_VISIBLE_UNKNOWN,
    }
    for finding in chain.findings:
        status = status_by_classification.get(finding.finding_classification)
        if status:
            findings.append(
                _finding(
                    status,
                    finding.subject_type,
                    finding.subject_id,
                    f"{finding.finding_classification} evaluation state remains fail-visible",
                    severity="visibility",
                )
            )


def _ordering_valid(chain: V37GraphEvaluationChain) -> bool:
    orders = [step.step_order for step in chain.steps]
    return orders == list(range(1, len(chain.steps) + 1)) and len(set(orders)) == len(orders)


def _finding_class_count(chain: V37GraphEvaluationChain, classification: str) -> int:
    return sum(1 for finding in chain.findings if finding.finding_classification == classification)


def _non_execution_guarantee_preserved(
    chain: V37GraphEvaluationChain,
    packets: tuple[V37GraphEvaluationReplayPacket, ...],
) -> bool:
    return all(
        (
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
            all(not step.executable_workflow and not step.traversal_enabled for step in chain.steps),
            all(not trace.trace_implies_traversal and not trace.trace_authorizes_execution for trace in chain.traces),
            all(
                packet.packet_is_non_executable_replay_evidence
                and not packet.orchestration_runtime_packet
                and not packet.execution_authorization
                and not packet.routing_enabled
                and not packet.scheduling_enabled
                and not packet.dispatch_enabled
                for packet in packets
            ),
        )
    )


def _finding(
    status: str,
    subject_type: str,
    subject_id: str,
    message: str,
    severity: str = "error",
) -> V37GraphEvaluationValidationFinding:
    return V37GraphEvaluationValidationFinding(
        finding_id=f"{status}:{subject_type}:{subject_id}",
        status=status,
        severity=severity,
        subject_type=subject_type,
        subject_id=subject_id,
        message=message,
    )
