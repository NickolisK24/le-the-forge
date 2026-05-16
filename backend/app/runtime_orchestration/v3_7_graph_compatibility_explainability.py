"""Deterministic explainability for v3.7 graph compatibility reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_compatibility_models import V37GraphCompatibilityMap


V37_COMPATIBILITY_EXPLAINABILITY_STABLE = "v3_7_graph_compatibility_explainability_stable"
V37_COMPATIBILITY_EXPLAINABILITY_BLOCKED = "v3_7_graph_compatibility_explainability_blocked"


@dataclass(frozen=True)
class V37GraphCompatibilityExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    compatibility_classification: str
    why_compatible_or_blocked: str
    governance_influences: tuple[str, ...]
    provenance_lineage: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True


@dataclass(frozen=True)
class V37GraphCompatibilityExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    node_explanation_count: int
    edge_explanation_count: int
    compatible_explanation_count: int
    incompatible_explanation_count: int
    unsupported_explanation_count: int
    prohibited_explanation_count: int
    unknown_explanation_count: int
    governance_influenced_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphCompatibilityExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_compatibility(
    compatibility_map: V37GraphCompatibilityMap,
) -> V37GraphCompatibilityExplainabilityResult:
    explanations = _build_explanations(compatibility_map)
    expected_subjects = {
        ("node_compatibility", item.relationship_id)
        for item in compatibility_map.node_results
    } | {
        ("edge_compatibility", item.edge_id)
        for item in compatibility_map.edge_results
    } | {
        (item.finding_kind, item.finding_id)
        for item in compatibility_map.findings
    }
    actual_subjects = {(item.subject_type, item.subject_id) for item in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected_subjects - actual_subjects))
    blocked = bool(missing) or any(
        not explanation.why_compatible_or_blocked
        or not explanation.provenance_lineage
        or not explanation.reasoning_chain
        for explanation in explanations
    )
    result = V37GraphCompatibilityExplainabilityResult(
        explainability_status=(
            V37_COMPATIBILITY_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_COMPATIBILITY_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        node_explanation_count=sum(1 for item in explanations if item.subject_type == "node_compatibility"),
        edge_explanation_count=sum(1 for item in explanations if item.subject_type == "edge_compatibility"),
        compatible_explanation_count=sum(1 for item in explanations if item.compatibility_classification == "compatible"),
        incompatible_explanation_count=sum(1 for item in explanations if item.compatibility_classification == "incompatible"),
        unsupported_explanation_count=sum(1 for item in explanations if item.compatibility_classification == "unsupported"),
        prohibited_explanation_count=sum(1 for item in explanations if item.compatibility_classification == "prohibited"),
        unknown_explanation_count=sum(1 for item in explanations if item.compatibility_classification == "unknown"),
        governance_influenced_explanation_count=sum(1 for item in explanations if item.governance_influences),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_compatibility_explainability_result(result),
    )


def export_v3_7_graph_compatibility_explanation(
    explanation: V37GraphCompatibilityExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in ("governance_influences", "provenance_lineage", "reasoning_chain"):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_compatibility_explainability_result(
    result: V37GraphCompatibilityExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_compatibility_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_compatibility_explainability_result(
    result: V37GraphCompatibilityExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_compatibility_explainability_result(result))


def hash_v3_7_graph_compatibility_explainability_result(
    result: V37GraphCompatibilityExplainabilityResult,
) -> str:
    data = export_v3_7_graph_compatibility_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(
    compatibility_map: V37GraphCompatibilityMap,
) -> tuple[V37GraphCompatibilityExplanation, ...]:
    rule_reasons = {rule.rule_id: rule.restriction_summary for rule in compatibility_map.rules}
    explanations: list[V37GraphCompatibilityExplanation] = []
    for result in compatibility_map.node_results:
        explanations.append(
            V37GraphCompatibilityExplanation(
                explanation_id=f"explain_node_{result.relationship_id}",
                subject_type="node_compatibility",
                subject_id=result.relationship_id,
                compatibility_classification=result.compatibility_classification,
                why_compatible_or_blocked=rule_reasons.get(result.rule_id, result.rule_id),
                governance_influences=result.governance_rule_ids,
                provenance_lineage=result.provenance.lineage_references,
                reasoning_chain=(
                    "source_node_domain",
                    "target_node_domain",
                    "governance_classification",
                    "compatibility_rule",
                    "non_executable_planning_evidence",
                ),
            )
        )
    for result in compatibility_map.edge_results:
        explanations.append(
            V37GraphCompatibilityExplanation(
                explanation_id=f"explain_edge_{result.edge_id}",
                subject_type="edge_compatibility",
                subject_id=result.edge_id,
                compatibility_classification=result.compatibility_classification,
                why_compatible_or_blocked=rule_reasons.get(result.rule_id, result.rule_id),
                governance_influences=result.governance_rule_ids,
                provenance_lineage=result.provenance.lineage_references,
                reasoning_chain=(
                    "edge_identity",
                    "edge_governance_classification",
                    "domain_compatibility",
                    "compatibility_rule",
                    "no_graph_traversal",
                ),
            )
        )
    for finding in compatibility_map.findings:
        explanations.append(
            V37GraphCompatibilityExplanation(
                explanation_id=f"explain_finding_{finding.finding_id}",
                subject_type=finding.finding_kind,
                subject_id=finding.finding_id,
                compatibility_classification=finding.compatibility_classification,
                why_compatible_or_blocked=finding.reason,
                governance_influences=finding.governance_rule_ids,
                provenance_lineage=finding.provenance.lineage_references,
                reasoning_chain=(
                    "compatibility_rule",
                    finding.compatibility_classification,
                    "fail_visible_compatibility_finding",
                    "non_executable_planning_evidence",
                ),
            )
        )
    return tuple(explanations)
