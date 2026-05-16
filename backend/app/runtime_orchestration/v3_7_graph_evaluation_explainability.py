"""Deterministic explainability for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_evaluation_models import (
    V37_EVALUATION_COMPATIBLE,
    V37_EVALUATION_INCOMPATIBLE,
    V37_EVALUATION_PROHIBITED,
    V37_EVALUATION_UNKNOWN,
    V37_EVALUATION_UNSUPPORTED,
    V37GraphEvaluationChain,
)
from .v3_7_graph_evaluation_traces import build_v3_7_graph_evaluation_chain


V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE = "v3_7_graph_evaluation_explainability_stable"
V37_GRAPH_EVALUATION_EXPLAINABILITY_BLOCKED = "v3_7_graph_evaluation_explainability_blocked"


@dataclass(frozen=True)
class V37GraphEvaluationExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    finding_classification: str
    why_evaluated_this_way: str
    governance_evidence_ids: tuple[str, ...]
    compatibility_evidence_ids: tuple[str, ...]
    provenance_lineage: tuple[str, ...]
    continuity_rule_ids: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True
    execution_authorization: bool = False


@dataclass(frozen=True)
class V37GraphEvaluationExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    successful_evaluation_explanation_count: int
    unsuccessful_evaluation_explanation_count: int
    prohibited_explanation_count: int
    unsupported_explanation_count: int
    unknown_explanation_count: int
    governance_influenced_explanation_count: int
    compatibility_influenced_explanation_count: int
    continuity_influenced_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphEvaluationExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_evaluation(
    chain: V37GraphEvaluationChain | None = None,
) -> V37GraphEvaluationExplainabilityResult:
    evaluation_chain = chain or build_v3_7_graph_evaluation_chain()
    explanations = _build_explanations(evaluation_chain)
    expected_subjects = {("evaluation_step", step.step_id) for step in evaluation_chain.steps} | {
        ("evaluation_finding", finding.finding_id) for finding in evaluation_chain.findings
    }
    actual_subjects = {(explanation.subject_type, explanation.subject_id) for explanation in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected_subjects - actual_subjects))
    blocked = bool(missing) or any(
        not explanation.why_evaluated_this_way
        or not explanation.provenance_lineage
        or not explanation.reasoning_chain
        or explanation.execution_authorization
        for explanation in explanations
    )
    result = V37GraphEvaluationExplainabilityResult(
        explainability_status=(
            V37_GRAPH_EVALUATION_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        successful_evaluation_explanation_count=sum(
            1 for item in explanations if item.finding_classification == V37_EVALUATION_COMPATIBLE
        ),
        unsuccessful_evaluation_explanation_count=sum(
            1
            for item in explanations
            if item.finding_classification
            in (V37_EVALUATION_INCOMPATIBLE, V37_EVALUATION_PROHIBITED, V37_EVALUATION_UNSUPPORTED, V37_EVALUATION_UNKNOWN)
        ),
        prohibited_explanation_count=sum(
            1 for item in explanations if item.finding_classification == V37_EVALUATION_PROHIBITED
        ),
        unsupported_explanation_count=sum(
            1 for item in explanations if item.finding_classification == V37_EVALUATION_UNSUPPORTED
        ),
        unknown_explanation_count=sum(
            1 for item in explanations if item.finding_classification == V37_EVALUATION_UNKNOWN
        ),
        governance_influenced_explanation_count=sum(1 for item in explanations if item.governance_evidence_ids),
        compatibility_influenced_explanation_count=sum(1 for item in explanations if item.compatibility_evidence_ids),
        continuity_influenced_explanation_count=sum(1 for item in explanations if item.continuity_rule_ids),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_evaluation_explainability_result(result),
    )


def export_v3_7_graph_evaluation_explanation(
    explanation: V37GraphEvaluationExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in (
        "governance_evidence_ids",
        "compatibility_evidence_ids",
        "provenance_lineage",
        "continuity_rule_ids",
        "reasoning_chain",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_evaluation_explainability_result(
    result: V37GraphEvaluationExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_evaluation_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_evaluation_explainability_result(
    result: V37GraphEvaluationExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_evaluation_explainability_result(result))


def hash_v3_7_graph_evaluation_explainability_result(
    result: V37GraphEvaluationExplainabilityResult,
) -> str:
    data = export_v3_7_graph_evaluation_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(
    chain: V37GraphEvaluationChain,
) -> tuple[V37GraphEvaluationExplanation, ...]:
    explanations: list[V37GraphEvaluationExplanation] = []
    continuity_ids = tuple(evidence.continuity_id for evidence in chain.continuity_evidence)
    for step in chain.steps:
        explanations.append(
            V37GraphEvaluationExplanation(
                explanation_id=f"explain_{step.step_id}",
                subject_type="evaluation_step",
                subject_id=step.step_id,
                finding_classification=step.finding_classification,
                why_evaluated_this_way=step.evaluation_statement,
                governance_evidence_ids=step.governance_evidence_ids,
                compatibility_evidence_ids=step.compatibility_evidence_ids,
                provenance_lineage=step.provenance.lineage_references,
                continuity_rule_ids=continuity_ids,
                reasoning_chain=(
                    "evaluation_step",
                    step.step_type,
                    step.finding_classification,
                    "structural_reasoning_evidence_only",
                    "no_execution_authorization",
                ),
            )
        )
    for finding in chain.findings:
        explanations.append(
            V37GraphEvaluationExplanation(
                explanation_id=f"explain_finding_{finding.finding_id}",
                subject_type="evaluation_finding",
                subject_id=finding.finding_id,
                finding_classification=finding.finding_classification,
                why_evaluated_this_way=finding.reason,
                governance_evidence_ids=finding.governance_reference_ids,
                compatibility_evidence_ids=finding.compatibility_reference_ids,
                provenance_lineage=finding.provenance.lineage_references,
                continuity_rule_ids=continuity_ids,
                reasoning_chain=(
                    "evaluation_finding",
                    finding.finding_classification,
                    "fail_visible",
                    "replay_safe_reasoning",
                    "non_executable_evidence",
                ),
            )
        )
    return tuple(explanations)
