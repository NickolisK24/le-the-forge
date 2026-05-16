"""Deterministic explainability for v3.7 graph planning continuity certification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_certification_evidence import build_v3_7_graph_planning_continuity_certification
from .v3_7_graph_certification_models import V37GraphPlanningContinuityCertification


V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE = "v3_7_graph_certification_explainability_stable"
V37_GRAPH_CERTIFICATION_EXPLAINABILITY_BLOCKED = "v3_7_graph_certification_explainability_blocked"


@dataclass(frozen=True)
class V37GraphCertificationExplanation:
    explanation_id: str
    explanation_type: str
    subject_id: str
    summary: str
    evidence_references: tuple[str, ...]
    deterministic_order: int
    replay_safe: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_references", tuple(self.evidence_references or ()))


@dataclass(frozen=True)
class V37GraphCertificationExplainabilityResult:
    explainability_status: str
    explanation_count: int
    certification_explanation_count: int
    scope_explanation_count: int
    evidence_source_explanation_count: int
    continuity_explanation_count: int
    failure_explanation_count: int
    provenance_explanation_count: int
    replay_rollback_explanation_count: int
    integrity_explanation_count: int
    execution_boundary_explanation_count: int
    does_not_authorize_explanation_count: int
    deterministic_explainability_hash: str
    explanations: tuple[V37GraphCertificationExplanation, ...]


def explain_v3_7_graph_certification(
    certification: V37GraphPlanningContinuityCertification | None = None,
) -> V37GraphCertificationExplainabilityResult:
    result = certification or build_v3_7_graph_planning_continuity_certification()
    explanations: list[V37GraphCertificationExplanation] = []
    order = 0

    def add(explanation_type: str, subject_id: str, summary: str, evidence: tuple[str, ...]) -> None:
        nonlocal order
        order += 1
        explanations.append(
            V37GraphCertificationExplanation(
                explanation_id=f"v3_7_graph_certification_explanation_{order:03d}_{explanation_type}",
                explanation_type=explanation_type,
                subject_id=subject_id,
                summary=summary,
                evidence_references=evidence,
                deterministic_order=order,
            )
        )

    add(
        "certification",
        result.identity.certification_id,
        "certification exists to certify end-to-end planning evidence continuity deterministically",
        (result.identity.certification_id,),
    )
    add(
        "scope",
        result.scope.identity.scope_id,
        "the certification scope includes graph, governance, compatibility, evaluation, session, scenario, aggregation, and integrity evidence",
        tuple(reference.reference_id for reference in result.scope.references),
    )
    for reference in sorted(result.scope.references, key=lambda item: item.reference_id):
        add(
            "evidence_source",
            reference.reference_id,
            f"{reference.reference_type} evidence was checked for planning continuity certification",
            (reference.reference_id,),
        )
    certified_findings = tuple(
        finding.finding_id
        for finding in result.findings
        if finding.finding_classification.endswith("_certified") or finding.finding_classification == "certification_passed"
    )
    failed_findings = tuple(
        finding.finding_id
        for finding in result.findings
        if finding.active_violation or finding.finding_classification.endswith("_uncertified")
    )
    add("continuity", result.identity.certification_id, "continuity guarantees passed when hashes and scope evidence remained stable", certified_findings)
    add("failure", result.identity.certification_id, "failed or uncertified guarantees remain fail-visible", failed_findings or (result.identity.certification_id,))
    add("provenance", result.identity.certification_id, "provenance was certified through scope and evidence lineage", result.evidence.provenance_references)
    add("replay_rollback", result.identity.certification_id, "replay and rollback certification evidence remains non-executable", result.evidence.replay_references + result.evidence.rollback_references)
    add("integrity", result.identity.certification_id, "integrity enforcement was certified as part of the continuity scope", result.evidence.integrity_evidence_references)
    add("execution_boundary", result.identity.certification_id, "execution-boundary certification passed only because no execution readiness, authorization, routing, scheduling, dispatch, traversal, optimization, or recommendation signal exists", result.evidence.execution_boundary_references)
    add("does_not_authorize", result.identity.certification_id, "certified continuity does not authorize execution and does not mark runtime execution readiness", (result.identity.certification_id,))
    ordered = tuple(sorted(explanations, key=lambda item: item.deterministic_order))
    explainability = V37GraphCertificationExplainabilityResult(
        explainability_status=(
            V37_GRAPH_CERTIFICATION_EXPLAINABILITY_STABLE
            if all(explanation.replay_safe and explanation.evidence_references for explanation in ordered)
            else V37_GRAPH_CERTIFICATION_EXPLAINABILITY_BLOCKED
        ),
        explanation_count=len(ordered),
        certification_explanation_count=sum(1 for item in ordered if item.explanation_type == "certification"),
        scope_explanation_count=sum(1 for item in ordered if item.explanation_type == "scope"),
        evidence_source_explanation_count=sum(1 for item in ordered if item.explanation_type == "evidence_source"),
        continuity_explanation_count=sum(1 for item in ordered if item.explanation_type == "continuity"),
        failure_explanation_count=sum(1 for item in ordered if item.explanation_type == "failure"),
        provenance_explanation_count=sum(1 for item in ordered if item.explanation_type == "provenance"),
        replay_rollback_explanation_count=sum(1 for item in ordered if item.explanation_type == "replay_rollback"),
        integrity_explanation_count=sum(1 for item in ordered if item.explanation_type == "integrity"),
        execution_boundary_explanation_count=sum(1 for item in ordered if item.explanation_type == "execution_boundary"),
        does_not_authorize_explanation_count=sum(1 for item in ordered if item.explanation_type == "does_not_authorize"),
        deterministic_explainability_hash="",
        explanations=ordered,
    )
    return replace(
        explainability,
        deterministic_explainability_hash=hash_v3_7_graph_certification_explainability_result(explainability),
    )


def export_v3_7_graph_certification_explanation(explanation: V37GraphCertificationExplanation) -> dict[str, Any]:
    data = asdict(explanation)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_certification_explainability_result(
    result: V37GraphCertificationExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["explanations"] = [
        export_v3_7_graph_certification_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.deterministic_order)
    ]
    return data


def serialize_v3_7_graph_certification_explainability_result(
    result: V37GraphCertificationExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_certification_explainability_result(result))


def hash_v3_7_graph_certification_explainability_result(
    result: V37GraphCertificationExplainabilityResult,
) -> str:
    data = export_v3_7_graph_certification_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)
