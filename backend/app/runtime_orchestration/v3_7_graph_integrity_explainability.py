"""Deterministic explainability for v3.7 graph planning integrity enforcement."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from .v3_7_graph_integrity_models import V37GraphIntegrityEnforcementResult


V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE = "v3_7_graph_integrity_explainability_stable"
V37_GRAPH_INTEGRITY_EXPLAINABILITY_BLOCKED = "v3_7_graph_integrity_explainability_blocked"


@dataclass(frozen=True)
class V37GraphIntegrityExplanation:
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
class V37GraphIntegrityExplainabilityResult:
    explainability_status: str
    explanation_count: int
    enforcement_explanation_count: int
    policy_explanation_count: int
    evidence_source_explanation_count: int
    finding_explanation_count: int
    warning_explanation_count: int
    blocked_explanation_count: int
    continuity_explanation_count: int
    provenance_explanation_count: int
    execution_boundary_explanation_count: int
    does_not_authorize_explanation_count: int
    deterministic_explainability_hash: str
    explanations: tuple[V37GraphIntegrityExplanation, ...]


def explain_v3_7_graph_integrity(
    result: V37GraphIntegrityEnforcementResult | None = None,
) -> V37GraphIntegrityExplainabilityResult:
    enforcement = result or enforce_v3_7_graph_planning_integrity()
    explanations: list[V37GraphIntegrityExplanation] = []
    order = 0

    def add(explanation_type: str, subject_id: str, summary: str, evidence: tuple[str, ...]) -> None:
        nonlocal order
        order += 1
        explanations.append(
            V37GraphIntegrityExplanation(
                explanation_id=f"v3_7_graph_integrity_explanation_{order:03d}_{explanation_type}",
                explanation_type=explanation_type,
                subject_id=subject_id,
                summary=summary,
                evidence_references=evidence,
                deterministic_order=order,
            )
        )

    add(
        "enforcement",
        enforcement.identity.enforcement_id,
        "integrity enforcement exists to validate cross-system planning evidence deterministically",
        (enforcement.identity.enforcement_id,),
    )
    add(
        "policy",
        enforcement.policy.identity.policy_id,
        "the enforced policy requires evidence-source, continuity, provenance, explainability, and execution-boundary integrity",
        (enforcement.policy.identity.policy_id,),
    )
    for source_id in sorted(enforcement.evidence_source_references):
        add("evidence_source", source_id, f"evidence source {source_id} is included in integrity validation", (source_id,))
    for finding in sorted(enforcement.findings, key=lambda item: item.finding_id):
        add(
            "finding",
            finding.finding_id,
            f"{finding.finding_classification} remains fail-visible; active_violation={finding.active_violation}",
            finding.evidence_references,
        )
    if any(finding.severity == "warning" for finding in enforcement.findings):
        add(
            "warning",
            enforcement.identity.enforcement_id,
            "warning findings are visible planning validation evidence",
            tuple(finding.finding_id for finding in enforcement.findings if finding.severity == "warning"),
        )
    blocked = tuple(finding.finding_id for finding in enforcement.findings if finding.blocks_validation)
    add(
        "blocked",
        enforcement.identity.enforcement_id,
        "blocked findings remain visible and would block integrity validation when active",
        blocked or (enforcement.identity.enforcement_id,),
    )
    add(
        "continuity",
        enforcement.identity.enforcement_id,
        "continuity hashes preserve deterministic graph, governance, compatibility, evaluation, session, scenario, and aggregation evidence",
        enforcement.continuity_hash_references,
    )
    add(
        "provenance",
        enforcement.identity.enforcement_id,
        "provenance references preserve replay-safe and rollback-safe integrity lineage",
        (enforcement.provenance.provenance_id, enforcement.policy.provenance.provenance_id),
    )
    add(
        "execution_boundary",
        enforcement.identity.enforcement_id,
        "execution-boundary integrity is preserved when no execution, routing, scheduling, dispatch, traversal, path selection, scenario selection, optimization, or recommendation authorization is present",
        enforcement.evidence_source_references,
    )
    add(
        "does_not_authorize",
        enforcement.identity.enforcement_id,
        "valid integrity remains planning validation only and does not authorize runtime orchestration",
        (enforcement.identity.enforcement_id,),
    )
    ordered = tuple(sorted(explanations, key=lambda item: item.deterministic_order))
    result_obj = V37GraphIntegrityExplainabilityResult(
        explainability_status=(
            V37_GRAPH_INTEGRITY_EXPLAINABILITY_STABLE
            if all(explanation.replay_safe and explanation.evidence_references for explanation in ordered)
            else V37_GRAPH_INTEGRITY_EXPLAINABILITY_BLOCKED
        ),
        explanation_count=len(ordered),
        enforcement_explanation_count=sum(1 for item in ordered if item.explanation_type == "enforcement"),
        policy_explanation_count=sum(1 for item in ordered if item.explanation_type == "policy"),
        evidence_source_explanation_count=sum(1 for item in ordered if item.explanation_type == "evidence_source"),
        finding_explanation_count=sum(1 for item in ordered if item.explanation_type == "finding"),
        warning_explanation_count=sum(1 for item in ordered if item.explanation_type == "warning"),
        blocked_explanation_count=sum(1 for item in ordered if item.explanation_type == "blocked"),
        continuity_explanation_count=sum(1 for item in ordered if item.explanation_type == "continuity"),
        provenance_explanation_count=sum(1 for item in ordered if item.explanation_type == "provenance"),
        execution_boundary_explanation_count=sum(
            1 for item in ordered if item.explanation_type == "execution_boundary"
        ),
        does_not_authorize_explanation_count=sum(
            1 for item in ordered if item.explanation_type == "does_not_authorize"
        ),
        deterministic_explainability_hash="",
        explanations=ordered,
    )
    return replace(
        result_obj,
        deterministic_explainability_hash=hash_v3_7_graph_integrity_explainability_result(result_obj),
    )


def export_v3_7_graph_integrity_explanation(explanation: V37GraphIntegrityExplanation) -> dict[str, Any]:
    data = asdict(explanation)
    data["evidence_references"] = sorted(data["evidence_references"])
    return data


def export_v3_7_graph_integrity_explainability_result(
    result: V37GraphIntegrityExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["explanations"] = [
        export_v3_7_graph_integrity_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.deterministic_order)
    ]
    return data


def serialize_v3_7_graph_integrity_explainability_result(
    result: V37GraphIntegrityExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_integrity_explainability_result(result))


def hash_v3_7_graph_integrity_explainability_result(result: V37GraphIntegrityExplainabilityResult) -> str:
    data = export_v3_7_graph_integrity_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)
