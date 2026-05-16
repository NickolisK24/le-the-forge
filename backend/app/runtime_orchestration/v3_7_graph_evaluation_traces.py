"""Deterministic evaluation chains and traces for v3.7 graph reasoning."""

from __future__ import annotations

from .v3_7_graph_compatibility_models import hash_v3_7_compatibility_map
from .v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from .v3_7_graph_evaluation_findings import build_v3_7_graph_evaluation_findings
from .v3_7_graph_evaluation_models import (
    V3_7_GRAPH_EVALUATION_PHASE_ID,
    V37_EVALUATION_COMPATIBILITY_RESTRICTED,
    V37_EVALUATION_CONTINUITY_WARNING,
    V37_EVALUATION_EXPERIMENTAL,
    V37_EVALUATION_GOVERNANCE_RESTRICTED,
    V37_EVALUATION_PROHIBITED,
    V37_EVALUATION_STEP_COMPATIBILITY,
    V37_EVALUATION_STEP_CONTINUITY,
    V37_EVALUATION_STEP_GOVERNANCE,
    V37_EVALUATION_STEP_PROHIBITED,
    V37_EVALUATION_STEP_UNKNOWN,
    V37_EVALUATION_STEP_UNSUPPORTED,
    V37_EVALUATION_UNKNOWN,
    V37_EVALUATION_UNSUPPORTED,
    V37GraphEvaluationChain,
    V37GraphEvaluationContinuityEvidence,
    V37GraphEvaluationFinding,
    V37GraphEvaluationStep,
    V37GraphEvaluationSummary,
    V37GraphEvaluationTrace,
)
from .v3_7_graph_models import V37GraphMetadataEntry, default_v3_7_graph_provenance


def build_v3_7_graph_evaluation_chain(compatibility_map=None) -> V37GraphEvaluationChain:
    source = compatibility_map or build_v3_7_graph_compatibility_map()
    findings = build_v3_7_graph_evaluation_findings(source)
    steps = tuple(_step_for_finding(index + 1, finding) for index, finding in enumerate(findings))
    traces = build_v3_7_graph_evaluation_traces(steps)
    chain_id = "v3_7_graph_evaluation_reasoning_chain"
    continuity = (
        V37GraphEvaluationContinuityEvidence(
            continuity_id="v3_7_graph_evaluation_continuity_evidence",
            chain_id=chain_id,
            step_ids=tuple(step.step_id for step in steps),
            trace_ids=tuple(trace.trace_id for trace in traces),
            finding_ids=tuple(finding.finding_id for finding in findings),
            compatibility_lineage_references=("v3_7_graph_compatibility_reasoning",),
            governance_lineage_references=("v3_7_graph_governance_boundary_intelligence",),
            provenance_lineage_references=tuple(sorted(finding.provenance.provenance_id for finding in findings)),
            explainability_lineage_references=("v3_7_graph_evaluation_explainability",),
            replay_lineage_references=("v3_7_graph_evaluation_replay_continuity",),
            rollback_lineage_references=("v3_7_graph_evaluation_rollback_continuity",),
            deterministic_hash_references=(hash_v3_7_compatibility_map(source),),
        ),
    )
    return V37GraphEvaluationChain(
        chain_id=chain_id,
        graph_id=source.graph_id,
        evaluation_phase_id=V3_7_GRAPH_EVALUATION_PHASE_ID,
        steps=steps,
        traces=traces,
        findings=findings,
        summary=summarize_v3_7_graph_evaluation(steps, traces, findings),
        continuity_evidence=continuity,
        provenance=default_v3_7_graph_provenance(chain_id, "graph_evaluation_chain"),
        metadata=(
            V37GraphMetadataEntry("evaluation_semantics", "structural_reasoning_evidence_only"),
            V37GraphMetadataEntry("runtime_capability", "none"),
            V37GraphMetadataEntry("ordering_semantics", "evaluation_ordering_not_execution_ordering"),
        ),
    )


def build_v3_7_graph_evaluation_traces(
    steps: tuple[V37GraphEvaluationStep, ...],
) -> tuple[V37GraphEvaluationTrace, ...]:
    return tuple(
        V37GraphEvaluationTrace(
            trace_id=f"trace_{step.step_id}",
            trace_order=step.step_order,
            step_id=step.step_id,
            finding_id=step.subject_id if step.subject_type == "evaluation_finding" else step.step_id,
            finding_classification=step.finding_classification,
            evaluation_evidence_ids=step.evidence_ids,
            compatibility_evidence_ids=step.compatibility_evidence_ids,
            governance_evidence_ids=step.governance_evidence_ids,
            provenance_evidence_ids=(step.provenance.provenance_id,),
            explainability_evidence_ids=step.explainability_evidence_ids,
            replay_reference_ids=step.replay_reference_ids,
            rollback_reference_ids=step.rollback_reference_ids,
            deterministic_ordering_key=f"{step.step_order:04d}:{step.step_id}",
        )
        for step in sorted(steps, key=lambda item: (item.step_order, item.step_id))
    )


def summarize_v3_7_graph_evaluation(
    steps: tuple[V37GraphEvaluationStep, ...],
    traces: tuple[V37GraphEvaluationTrace, ...],
    findings: tuple[V37GraphEvaluationFinding, ...],
) -> V37GraphEvaluationSummary:
    classifications = [finding.finding_classification for finding in findings]
    return V37GraphEvaluationSummary(
        step_count=len(steps),
        trace_count=len(traces),
        finding_count=len(findings),
        compatible_finding_count=classifications.count("compatible"),
        incompatible_finding_count=classifications.count("incompatible"),
        unsupported_finding_count=classifications.count("unsupported"),
        prohibited_finding_count=classifications.count("prohibited"),
        unknown_finding_count=classifications.count("unknown"),
        governance_restricted_finding_count=classifications.count("governance_restricted"),
        compatibility_restricted_finding_count=classifications.count("compatibility_restricted"),
        experimental_finding_count=classifications.count("experimental"),
        continuity_warning_count=classifications.count("continuity_warning"),
        fail_visible_finding_count=sum(1 for finding in findings if finding.fail_visible),
    )


def _step_for_finding(order: int, finding: V37GraphEvaluationFinding) -> V37GraphEvaluationStep:
    step_type = _step_type_for_classification(finding.finding_classification)
    return V37GraphEvaluationStep(
        step_id=f"evaluation_step_{order:04d}_{finding.finding_id}",
        step_order=order,
        step_type=step_type,
        finding_classification=finding.finding_classification,
        subject_type="evaluation_finding",
        subject_id=finding.finding_id,
        evaluation_statement=finding.reason,
        evidence_ids=finding.evidence_ids,
        compatibility_evidence_ids=finding.compatibility_reference_ids,
        governance_evidence_ids=finding.governance_reference_ids,
        provenance=finding.provenance,
        explainability_evidence_ids=(f"explain_{finding.finding_id}",),
        replay_reference_ids=("v3_7_graph_evaluation_replay_continuity", finding.finding_id),
        rollback_reference_ids=("v3_7_graph_evaluation_rollback_continuity", finding.finding_id),
    )


def _step_type_for_classification(classification: str) -> str:
    if classification == V37_EVALUATION_PROHIBITED:
        return V37_EVALUATION_STEP_PROHIBITED
    if classification == V37_EVALUATION_UNSUPPORTED:
        return V37_EVALUATION_STEP_UNSUPPORTED
    if classification == V37_EVALUATION_UNKNOWN:
        return V37_EVALUATION_STEP_UNKNOWN
    if classification in (V37_EVALUATION_GOVERNANCE_RESTRICTED,):
        return V37_EVALUATION_STEP_GOVERNANCE
    if classification == V37_EVALUATION_CONTINUITY_WARNING:
        return V37_EVALUATION_STEP_CONTINUITY
    if classification in (V37_EVALUATION_COMPATIBILITY_RESTRICTED, V37_EVALUATION_EXPERIMENTAL):
        return V37_EVALUATION_STEP_COMPATIBILITY
    return V37_EVALUATION_STEP_COMPATIBILITY
