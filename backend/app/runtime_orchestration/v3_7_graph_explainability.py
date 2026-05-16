"""Deterministic explainability for v3.7 graph foundations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphExplainabilityEvidence, V37OrchestrationPlanningGraph
from .v3_7_graph_serialization import export_v3_7_explainability_evidence


V37_EXPLAINABILITY_STABLE = "v3_7_graph_explainability_stable"
V37_EXPLAINABILITY_BLOCKED = "v3_7_graph_explainability_blocked"


@dataclass(frozen=True)
class V37GraphExplainabilityResult:
    explainability_status: str
    structural_reasoning_only: bool
    replay_safe: bool
    node_explanation_count: int
    edge_explanation_count: int
    governance_restriction_count: int
    unsupported_boundary_count: int
    prohibited_boundary_count: int
    compatibility_visibility_count: int
    continuity_reference_count: int
    missing_explanation_subjects: tuple[str, ...]
    evidence: tuple[V37GraphExplainabilityEvidence, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph(graph: V37OrchestrationPlanningGraph) -> V37GraphExplainabilityResult:
    evidence = tuple(sorted(graph.explainability_evidence, key=lambda item: item.evidence_id))
    subjects = {(item.subject_type, item.subject_id) for item in evidence}
    expected_node_subjects = {("node", node.identity.node_id) for node in graph.nodes}
    expected_edge_subjects = {("edge", edge.identity.edge_id) for edge in graph.edges}
    missing = sorted(
        subject_id
        for subject_type, subject_id in (expected_node_subjects | expected_edge_subjects) - subjects
    )
    blocked = bool(missing) or any(
        not item.why_exists
        or not item.governance_restrictions
        or not item.provenance_lineage
        or not item.continuity_references
        for item in evidence
    )
    result = V37GraphExplainabilityResult(
        explainability_status=V37_EXPLAINABILITY_BLOCKED if blocked else V37_EXPLAINABILITY_STABLE,
        structural_reasoning_only=graph.structural_reasoning_only and graph.non_executable,
        replay_safe=not blocked,
        node_explanation_count=len(expected_node_subjects & subjects),
        edge_explanation_count=len(expected_edge_subjects & subjects),
        governance_restriction_count=len(
            sorted({item for evidence_item in evidence for item in evidence_item.governance_restrictions})
        ),
        unsupported_boundary_count=len(
            sorted({item for evidence_item in evidence for item in evidence_item.unsupported_boundaries})
        ),
        prohibited_boundary_count=len(
            sorted({item for evidence_item in evidence for item in evidence_item.prohibited_boundaries})
        ),
        compatibility_visibility_count=len(
            sorted({item for evidence_item in evidence for item in evidence_item.compatibility_visibility})
        ),
        continuity_reference_count=len(
            sorted({item for evidence_item in evidence for item in evidence_item.continuity_references})
        ),
        missing_explanation_subjects=tuple(missing),
        evidence=evidence,
    )
    return replace(result, deterministic_explainability_hash=hash_v3_7_graph_explainability_result(result))


def export_v3_7_graph_explainability_result(result: V37GraphExplainabilityResult) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["evidence"] = [
        export_v3_7_explainability_evidence(evidence)
        for evidence in sorted(result.evidence, key=lambda item: item.evidence_id)
    ]
    return data


def serialize_v3_7_graph_explainability_result(result: V37GraphExplainabilityResult) -> str:
    return stable_serialize(export_v3_7_graph_explainability_result(result))


def hash_v3_7_graph_explainability_result(result: V37GraphExplainabilityResult) -> str:
    data = export_v3_7_graph_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)
