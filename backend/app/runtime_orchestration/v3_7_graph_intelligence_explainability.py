"""Deterministic explainability for v3.7 planning intelligence aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_intelligence_models import V37GraphPlanningIntelligenceAggregation


V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE = "v3_7_graph_intelligence_explainability_stable"
V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_BLOCKED = "v3_7_graph_intelligence_explainability_blocked"


@dataclass(frozen=True)
class V37GraphIntelligenceExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    why_present: str
    evidence_source_references: tuple[str, ...]
    finding_references: tuple[str, ...]
    insight_references: tuple[str, ...]
    provenance_references: tuple[str, ...]
    continuity_references: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True
    execution_authorization: bool = False
    runtime_path_selection: bool = False


@dataclass(frozen=True)
class V37GraphIntelligenceExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    aggregation_explanation_count: int
    evidence_source_explanation_count: int
    finding_explanation_count: int
    insight_explanation_count: int
    replay_explanation_count: int
    governance_visible_explanation_count: int
    compatibility_visible_explanation_count: int
    evaluation_visible_explanation_count: int
    session_visible_explanation_count: int
    scenario_visible_explanation_count: int
    risk_visibility_explanation_count: int
    does_not_authorize_explanation_count: int
    provenance_supported_explanation_count: int
    continuity_supported_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphIntelligenceExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_intelligence(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
) -> V37GraphIntelligenceExplainabilityResult:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    explanations = _build_explanations(planning_intelligence)
    expected = {("planning_intelligence_aggregation", planning_intelligence.identity.aggregation_id)}
    expected.update(("intelligence_evidence_source", source.source_id) for source in planning_intelligence.evidence_sources)
    expected.update(("intelligence_finding", finding.finding_id) for finding in planning_intelligence.findings)
    expected.update(("planning_insight", insight.insight_id) for insight in planning_intelligence.insights)
    expected.update(("intelligence_replay_evidence", evidence.replay_evidence_id) for evidence in planning_intelligence.replay_evidence)
    actual = {(explanation.subject_type, explanation.subject_id) for explanation in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected - actual))
    blocked = bool(missing) or any(
        not explanation.why_present
        or not explanation.provenance_references
        or not explanation.continuity_references
        or explanation.execution_authorization
        or explanation.runtime_path_selection
        for explanation in explanations
    )
    result = V37GraphIntelligenceExplainabilityResult(
        explainability_status=(
            V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        aggregation_explanation_count=sum(1 for item in explanations if item.subject_type == "planning_intelligence_aggregation"),
        evidence_source_explanation_count=sum(1 for item in explanations if item.subject_type == "intelligence_evidence_source"),
        finding_explanation_count=sum(1 for item in explanations if item.subject_type == "intelligence_finding"),
        insight_explanation_count=sum(1 for item in explanations if item.subject_type == "planning_insight"),
        replay_explanation_count=sum(1 for item in explanations if item.subject_type == "intelligence_replay_evidence"),
        governance_visible_explanation_count=_contains(explanations, "governance"),
        compatibility_visible_explanation_count=_contains(explanations, "compatibility"),
        evaluation_visible_explanation_count=_contains(explanations, "evaluation"),
        session_visible_explanation_count=_contains(explanations, "session"),
        scenario_visible_explanation_count=_contains(explanations, "scenario"),
        risk_visibility_explanation_count=sum(
            1
            for item in explanations
            if any(token in item.reasoning_chain for token in ("blocked_visible", "unsupported_visible", "prohibited_visible", "unknown_visible"))
        ),
        does_not_authorize_explanation_count=sum(
            1 for item in explanations if "does_not_authorize_execution" in item.reasoning_chain
        ),
        provenance_supported_explanation_count=sum(1 for item in explanations if item.provenance_references),
        continuity_supported_explanation_count=sum(1 for item in explanations if item.continuity_references),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_intelligence_explainability_result(result),
    )


def export_v3_7_graph_intelligence_explanation(
    explanation: V37GraphIntelligenceExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in (
        "evidence_source_references",
        "finding_references",
        "insight_references",
        "provenance_references",
        "continuity_references",
        "reasoning_chain",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_intelligence_explainability_result(
    result: V37GraphIntelligenceExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_intelligence_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_intelligence_explainability_result(
    result: V37GraphIntelligenceExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_intelligence_explainability_result(result))


def hash_v3_7_graph_intelligence_explainability_result(
    result: V37GraphIntelligenceExplainabilityResult,
) -> str:
    data = export_v3_7_graph_intelligence_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(aggregation: V37GraphPlanningIntelligenceAggregation) -> tuple[V37GraphIntelligenceExplanation, ...]:
    source_ids = tuple(source.source_id for source in aggregation.evidence_sources)
    finding_ids = tuple(finding.finding_id for finding in aggregation.findings)
    insight_ids = tuple(insight.insight_id for insight in aggregation.insights)
    explanations: list[V37GraphIntelligenceExplanation] = [
        V37GraphIntelligenceExplanation(
            explanation_id=f"explain_aggregation_{aggregation.identity.aggregation_id}",
            subject_type="planning_intelligence_aggregation",
            subject_id=aggregation.identity.aggregation_id,
            why_present="aggregation summarizes non-executable planning evidence across v3.7 graph layers",
            evidence_source_references=source_ids,
            finding_references=finding_ids,
            insight_references=insight_ids,
            provenance_references=(aggregation.provenance.provenance_id,),
            continuity_references=aggregation.continuity_hash_references,
            reasoning_chain=("planning_evidence_summary", "does_not_authorize_execution", "does_not_select_runtime_paths"),
        )
    ]
    for source in aggregation.evidence_sources:
        explanations.append(
            V37GraphIntelligenceExplanation(
                explanation_id=f"explain_source_{source.source_id}",
                subject_type="intelligence_evidence_source",
                subject_id=source.source_id,
                why_present=f"{source.source_type} source is included in deterministic planning evidence aggregation",
                evidence_source_references=(source.source_id,),
                finding_references=finding_ids,
                insight_references=insight_ids,
                provenance_references=source.provenance_references,
                continuity_references=source.continuity_references,
                reasoning_chain=(source.source_type, "evidence_source", "does_not_authorize_execution"),
            )
        )
    for finding in aggregation.findings:
        explanations.append(
            V37GraphIntelligenceExplanation(
                explanation_id=f"explain_finding_{finding.finding_id}",
                subject_type="intelligence_finding",
                subject_id=finding.finding_id,
                why_present=finding.summary,
                evidence_source_references=finding.evidence_references,
                finding_references=(finding.finding_id,),
                insight_references=insight_ids,
                provenance_references=(aggregation.provenance.provenance_id,),
                continuity_references=aggregation.continuity_hash_references,
                reasoning_chain=(finding.finding_classification, "fail_visible", "does_not_authorize_execution"),
            )
        )
    for insight in aggregation.insights:
        explanations.append(
            V37GraphIntelligenceExplanation(
                explanation_id=f"explain_insight_{insight.insight_id}",
                subject_type="planning_insight",
                subject_id=insight.insight_id,
                why_present=insight.summary,
                evidence_source_references=insight.evidence_source_references,
                finding_references=insight.finding_references,
                insight_references=(insight.insight_id,),
                provenance_references=insight.provenance_references,
                continuity_references=insight.continuity_references,
                reasoning_chain=(insight.insight_kind, "summary_only", "does_not_authorize_execution", "does_not_select_runtime_paths"),
            )
        )
    for evidence in aggregation.replay_evidence:
        explanations.append(
            V37GraphIntelligenceExplanation(
                explanation_id=f"explain_replay_{evidence.replay_evidence_id}",
                subject_type="intelligence_replay_evidence",
                subject_id=evidence.replay_evidence_id,
                why_present="aggregation replay evidence preserves deterministic source continuity and is not runtime replay",
                evidence_source_references=evidence.evidence_source_references,
                finding_references=finding_ids,
                insight_references=insight_ids,
                provenance_references=evidence.provenance_references,
                continuity_references=evidence.continuity_hashes,
                reasoning_chain=("replay_continuity_visible", "rollback_continuity_visible", "non_executable_replay"),
            )
        )
    return tuple(explanations)


def _contains(explanations: tuple[V37GraphIntelligenceExplanation, ...], token: str) -> int:
    return sum(1 for item in explanations if token in item.subject_id or token in item.why_present or token in item.reasoning_chain)
