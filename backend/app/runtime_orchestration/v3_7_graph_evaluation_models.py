"""Deterministic v3.7 graph evaluation reasoning models.

Evaluation records are structural reasoning evidence only. They do not
authorize graph execution, traversal, routing, scheduling, dispatch, path
selection, runtime orchestration, or graph runtime simulation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphMetadataEntry, V37GraphProvenance


V3_7_GRAPH_EVALUATION_PHASE_ID = "v3_7_graph_evaluation_reasoning"
V37_EVALUATION_COMPATIBLE = "compatible"
V37_EVALUATION_INCOMPATIBLE = "incompatible"
V37_EVALUATION_UNSUPPORTED = "unsupported"
V37_EVALUATION_PROHIBITED = "prohibited"
V37_EVALUATION_UNKNOWN = "unknown"
V37_EVALUATION_GOVERNANCE_RESTRICTED = "governance_restricted"
V37_EVALUATION_COMPATIBILITY_RESTRICTED = "compatibility_restricted"
V37_EVALUATION_EXPERIMENTAL = "experimental"
V37_EVALUATION_CONTINUITY_WARNING = "continuity_warning"
V37_EVALUATION_FINDING_CLASSIFICATIONS: tuple[str, ...] = (
    V37_EVALUATION_COMPATIBLE,
    V37_EVALUATION_INCOMPATIBLE,
    V37_EVALUATION_UNSUPPORTED,
    V37_EVALUATION_PROHIBITED,
    V37_EVALUATION_UNKNOWN,
    V37_EVALUATION_GOVERNANCE_RESTRICTED,
    V37_EVALUATION_COMPATIBILITY_RESTRICTED,
    V37_EVALUATION_EXPERIMENTAL,
    V37_EVALUATION_CONTINUITY_WARNING,
)

V37_EVALUATION_STEP_COMPATIBILITY = "compatibility_evaluation"
V37_EVALUATION_STEP_GOVERNANCE = "governance_evaluation"
V37_EVALUATION_STEP_PROHIBITED = "prohibited_state"
V37_EVALUATION_STEP_UNSUPPORTED = "unsupported_state"
V37_EVALUATION_STEP_UNKNOWN = "unknown_state"
V37_EVALUATION_STEP_CONTINUITY = "structural_continuity"
V37_EVALUATION_STEP_TYPES: tuple[str, ...] = (
    V37_EVALUATION_STEP_COMPATIBILITY,
    V37_EVALUATION_STEP_GOVERNANCE,
    V37_EVALUATION_STEP_PROHIBITED,
    V37_EVALUATION_STEP_UNSUPPORTED,
    V37_EVALUATION_STEP_UNKNOWN,
    V37_EVALUATION_STEP_CONTINUITY,
)


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphEvaluationFinding:
    finding_id: str
    finding_classification: str
    subject_type: str
    subject_id: str
    reason: str
    evidence_ids: tuple[str, ...]
    compatibility_reference_ids: tuple[str, ...]
    governance_reference_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    fail_visible: bool = True
    hidden: bool = False

    def __post_init__(self) -> None:
        for field_name in ("evidence_ids", "compatibility_reference_ids", "governance_reference_ids"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphEvaluationStep:
    step_id: str
    step_order: int
    step_type: str
    finding_classification: str
    subject_type: str
    subject_id: str
    evaluation_statement: str
    evidence_ids: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    governance_evidence_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    fail_visible: bool = True
    executable_workflow: bool = False
    traversal_enabled: bool = False
    execution_ordering_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evidence_ids",
            "compatibility_evidence_ids",
            "governance_evidence_ids",
            "explainability_evidence_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphEvaluationTrace:
    trace_id: str
    trace_order: int
    step_id: str
    finding_id: str
    finding_classification: str
    evaluation_evidence_ids: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    governance_evidence_ids: tuple[str, ...]
    provenance_evidence_ids: tuple[str, ...]
    explainability_evidence_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    deterministic_ordering_key: str
    trace_implies_traversal: bool = False
    trace_authorizes_execution: bool = False
    trace_has_side_effects: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "evaluation_evidence_ids",
            "compatibility_evidence_ids",
            "governance_evidence_ids",
            "provenance_evidence_ids",
            "explainability_evidence_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphEvaluationContinuityEvidence:
    continuity_id: str
    chain_id: str
    step_ids: tuple[str, ...]
    trace_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    compatibility_lineage_references: tuple[str, ...]
    governance_lineage_references: tuple[str, ...]
    provenance_lineage_references: tuple[str, ...]
    explainability_lineage_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "step_ids",
            "trace_ids",
            "finding_ids",
            "compatibility_lineage_references",
            "governance_lineage_references",
            "provenance_lineage_references",
            "explainability_lineage_references",
            "replay_lineage_references",
            "rollback_lineage_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphEvaluationSummary:
    step_count: int
    trace_count: int
    finding_count: int
    compatible_finding_count: int
    incompatible_finding_count: int
    unsupported_finding_count: int
    prohibited_finding_count: int
    unknown_finding_count: int
    governance_restricted_finding_count: int
    compatibility_restricted_finding_count: int
    experimental_finding_count: int
    continuity_warning_count: int
    fail_visible_finding_count: int


@dataclass(frozen=True)
class V37GraphEvaluationReplayPacket:
    replay_packet_id: str
    chain_id: str
    graph_id: str
    trace_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    evaluation_chain_hash: str
    compatibility_hash: str
    provenance_lineage_references: tuple[str, ...]
    explainability_lineage_references: tuple[str, ...]
    deterministic_trace_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    packet_is_non_executable_replay_evidence: bool = True
    orchestration_runtime_packet: bool = False
    execution_authorization: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    deterministic_replay_hash: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "trace_ids",
            "finding_ids",
            "provenance_lineage_references",
            "explainability_lineage_references",
            "deterministic_trace_references",
            "replay_lineage_references",
            "rollback_lineage_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphEvaluationChain:
    chain_id: str
    graph_id: str
    evaluation_phase_id: str
    steps: tuple[V37GraphEvaluationStep, ...]
    traces: tuple[V37GraphEvaluationTrace, ...]
    findings: tuple[V37GraphEvaluationFinding, ...]
    summary: V37GraphEvaluationSummary
    continuity_evidence: tuple[V37GraphEvaluationContinuityEvidence, ...]
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()
    evaluation_reasoning_is_non_executable: bool = True
    replay_packets_are_not_orchestration_packets: bool = True
    evaluation_traces_do_not_imply_traversal: bool = True
    evaluation_ordering_does_not_imply_execution_ordering: bool = True
    evaluation_findings_are_structural_reasoning_evidence_only: bool = True
    graph_evaluation_does_not_authorize_orchestration: bool = True
    graph_execution_enabled: bool = False
    traversal_execution_enabled: bool = False
    runtime_orchestration_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    path_selection_enabled: bool = False
    graph_optimization_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    graph_runtime_simulation_enabled: bool = False
    hidden_evaluation_side_effects_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("steps", "traces", "findings", "continuity_evidence", "metadata"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_graph_evaluation_finding(finding: V37GraphEvaluationFinding) -> dict[str, Any]:
    data = asdict(finding)
    for field_name in ("evidence_ids", "compatibility_reference_ids", "governance_reference_ids"):
        data[field_name] = sorted(data[field_name])
    data["provenance"] = _export_provenance(finding.provenance)
    return data


def export_v3_7_graph_evaluation_step(step: V37GraphEvaluationStep) -> dict[str, Any]:
    data = asdict(step)
    for field_name in (
        "evidence_ids",
        "compatibility_evidence_ids",
        "governance_evidence_ids",
        "explainability_evidence_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = sorted(data[field_name])
    data["provenance"] = _export_provenance(step.provenance)
    return data


def export_v3_7_graph_evaluation_trace(trace: V37GraphEvaluationTrace) -> dict[str, Any]:
    data = asdict(trace)
    for field_name in (
        "evaluation_evidence_ids",
        "compatibility_evidence_ids",
        "governance_evidence_ids",
        "provenance_evidence_ids",
        "explainability_evidence_ids",
        "replay_reference_ids",
        "rollback_reference_ids",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_evaluation_continuity_evidence(
    evidence: V37GraphEvaluationContinuityEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "step_ids",
        "trace_ids",
        "finding_ids",
        "compatibility_lineage_references",
        "governance_lineage_references",
        "provenance_lineage_references",
        "explainability_lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "deterministic_hash_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_evaluation_summary(summary: V37GraphEvaluationSummary) -> dict[str, Any]:
    return asdict(summary)


def export_v3_7_graph_evaluation_replay_packet(packet: V37GraphEvaluationReplayPacket) -> dict[str, Any]:
    data = asdict(packet)
    for field_name in (
        "trace_ids",
        "finding_ids",
        "provenance_lineage_references",
        "explainability_lineage_references",
        "deterministic_trace_references",
        "replay_lineage_references",
        "rollback_lineage_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_evaluation_chain(chain: V37GraphEvaluationChain) -> dict[str, Any]:
    return {
        "chain_id": chain.chain_id,
        "graph_id": chain.graph_id,
        "evaluation_phase_id": chain.evaluation_phase_id,
        "steps": [
            export_v3_7_graph_evaluation_step(step)
            for step in sorted(chain.steps, key=lambda item: (item.step_order, item.step_id))
        ],
        "traces": [
            export_v3_7_graph_evaluation_trace(trace)
            for trace in sorted(chain.traces, key=lambda item: (item.trace_order, item.trace_id))
        ],
        "findings": [
            export_v3_7_graph_evaluation_finding(finding)
            for finding in sorted(chain.findings, key=lambda item: item.finding_id)
        ],
        "summary": export_v3_7_graph_evaluation_summary(chain.summary),
        "continuity_evidence": [
            export_v3_7_graph_evaluation_continuity_evidence(evidence)
            for evidence in sorted(chain.continuity_evidence, key=lambda item: item.continuity_id)
        ],
        "provenance": _export_provenance(chain.provenance),
        "metadata": _export_metadata(chain.metadata),
        "evaluation_reasoning_is_non_executable": chain.evaluation_reasoning_is_non_executable,
        "replay_packets_are_not_orchestration_packets": chain.replay_packets_are_not_orchestration_packets,
        "evaluation_traces_do_not_imply_traversal": chain.evaluation_traces_do_not_imply_traversal,
        "evaluation_ordering_does_not_imply_execution_ordering": (
            chain.evaluation_ordering_does_not_imply_execution_ordering
        ),
        "evaluation_findings_are_structural_reasoning_evidence_only": (
            chain.evaluation_findings_are_structural_reasoning_evidence_only
        ),
        "graph_evaluation_does_not_authorize_orchestration": chain.graph_evaluation_does_not_authorize_orchestration,
        "graph_execution_enabled": chain.graph_execution_enabled,
        "traversal_execution_enabled": chain.traversal_execution_enabled,
        "runtime_orchestration_enabled": chain.runtime_orchestration_enabled,
        "routing_enabled": chain.routing_enabled,
        "scheduling_enabled": chain.scheduling_enabled,
        "dispatch_enabled": chain.dispatch_enabled,
        "path_selection_enabled": chain.path_selection_enabled,
        "graph_optimization_enabled": chain.graph_optimization_enabled,
        "recommendation_enabled": chain.recommendation_enabled,
        "autonomous_orchestration_enabled": chain.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": chain.runtime_mutation_enabled,
        "graph_runtime_simulation_enabled": chain.graph_runtime_simulation_enabled,
        "hidden_evaluation_side_effects_enabled": chain.hidden_evaluation_side_effects_enabled,
    }


def export_v3_7_graph_evaluation_counts(chain: V37GraphEvaluationChain) -> dict[str, int]:
    return {
        "evaluation_chain_count": 1,
        "evaluation_step_count": len(chain.steps),
        "evaluation_trace_count": len(chain.traces),
        "evaluation_finding_count": len(chain.findings),
        "continuity_evidence_count": len(chain.continuity_evidence),
    }


def serialize_v3_7_graph_evaluation_chain(chain: V37GraphEvaluationChain) -> str:
    return stable_serialize(export_v3_7_graph_evaluation_chain(chain))


def hash_v3_7_graph_evaluation_chain(chain: V37GraphEvaluationChain) -> str:
    return deterministic_hash(export_v3_7_graph_evaluation_chain(chain))


def serialize_v3_7_graph_evaluation_replay_packet(packet: V37GraphEvaluationReplayPacket) -> str:
    return stable_serialize(export_v3_7_graph_evaluation_replay_packet(packet))


def hash_v3_7_graph_evaluation_replay_packet(packet: V37GraphEvaluationReplayPacket) -> str:
    data = export_v3_7_graph_evaluation_replay_packet(packet)
    data.pop("deterministic_replay_hash", None)
    return deterministic_hash(data)


def validate_v3_7_graph_evaluation_serialization_stability(chain: V37GraphEvaluationChain) -> dict[str, Any]:
    first = serialize_v3_7_graph_evaluation_chain(chain)
    second = serialize_v3_7_graph_evaluation_chain(chain)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_graph_evaluation_chain",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_graph_evaluation_hash_stability(chain: V37GraphEvaluationChain) -> dict[str, Any]:
    first = hash_v3_7_graph_evaluation_chain(chain)
    second = hash_v3_7_graph_evaluation_chain(chain)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_evaluation_chain",
    }


def validate_v3_7_graph_evaluation_replay_packet_hash_stability(
    packet: V37GraphEvaluationReplayPacket,
) -> dict[str, Any]:
    first = hash_v3_7_graph_evaluation_replay_packet(packet)
    second = hash_v3_7_graph_evaluation_replay_packet(packet)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_graph_evaluation_replay_packet",
    }


def _export_metadata(metadata: tuple[V37GraphMetadataEntry, ...]) -> list[dict[str, Any]]:
    return [asdict(entry) for entry in sorted(metadata, key=lambda item: item.metadata_key)]


def _export_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data
