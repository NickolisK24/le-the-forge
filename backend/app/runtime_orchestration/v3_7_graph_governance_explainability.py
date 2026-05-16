"""Deterministic explainability for v3.7 graph governance boundaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_governance_models import (
    V37GraphGovernanceFinding,
    V37GraphGovernanceMap,
)


V37_GOVERNANCE_EXPLAINABILITY_STABLE = "v3_7_graph_governance_explainability_stable"
V37_GOVERNANCE_EXPLAINABILITY_BLOCKED = "v3_7_graph_governance_explainability_blocked"


@dataclass(frozen=True)
class V37GraphGovernanceExplanation:
    explanation_id: str
    subject_type: str
    subject_id: str
    governance_classification: str
    why_governed: str
    restriction_reasons: tuple[str, ...]
    compatibility_reasons: tuple[str, ...]
    prohibited_relationship_reasons: tuple[str, ...]
    unsupported_relationship_reasons: tuple[str, ...]
    provenance_lineage: tuple[str, ...]
    reasoning_chain: tuple[str, ...]
    replay_safe: bool = True


@dataclass(frozen=True)
class V37GraphGovernanceExplainabilityResult:
    explainability_status: str
    replay_safe: bool
    explanation_count: int
    node_explanation_count: int
    edge_explanation_count: int
    prohibited_relationship_explanation_count: int
    unsupported_relationship_explanation_count: int
    governance_restriction_explanation_count: int
    compatibility_boundary_explanation_count: int
    missing_explanation_subjects: tuple[str, ...]
    explanations: tuple[V37GraphGovernanceExplanation, ...]
    deterministic_explainability_hash: str = ""


def explain_v3_7_graph_governance(
    governance_map: V37GraphGovernanceMap,
) -> V37GraphGovernanceExplainabilityResult:
    explanations = _build_explanations(governance_map)
    expected_subjects = {
        ("node_governance", item.node_id)
        for item in governance_map.node_classifications
    } | {
        ("edge_governance", item.edge_id)
        for item in governance_map.edge_classifications
    } | {
        (finding.finding_kind, finding.finding_id)
        for finding in governance_map.findings
    }
    actual_subjects = {(item.subject_type, item.subject_id) for item in explanations}
    missing = tuple(sorted(f"{kind}:{subject_id}" for kind, subject_id in expected_subjects - actual_subjects))
    blocked = bool(missing) or any(
        not explanation.why_governed
        or not explanation.provenance_lineage
        or not explanation.reasoning_chain
        for explanation in explanations
    )
    result = V37GraphGovernanceExplainabilityResult(
        explainability_status=(
            V37_GOVERNANCE_EXPLAINABILITY_BLOCKED
            if blocked
            else V37_GOVERNANCE_EXPLAINABILITY_STABLE
        ),
        replay_safe=not blocked,
        explanation_count=len(explanations),
        node_explanation_count=sum(1 for item in explanations if item.subject_type == "node_governance"),
        edge_explanation_count=sum(1 for item in explanations if item.subject_type == "edge_governance"),
        prohibited_relationship_explanation_count=sum(
            1 for item in explanations if item.prohibited_relationship_reasons
        ),
        unsupported_relationship_explanation_count=sum(
            1 for item in explanations if item.unsupported_relationship_reasons
        ),
        governance_restriction_explanation_count=sum(1 for item in explanations if item.restriction_reasons),
        compatibility_boundary_explanation_count=sum(1 for item in explanations if item.compatibility_reasons),
        missing_explanation_subjects=missing,
        explanations=tuple(sorted(explanations, key=lambda item: item.explanation_id)),
    )
    return replace(
        result,
        deterministic_explainability_hash=hash_v3_7_graph_governance_explainability_result(result),
    )


def export_v3_7_graph_governance_explanation(
    explanation: V37GraphGovernanceExplanation,
) -> dict[str, Any]:
    data = asdict(explanation)
    for field_name in (
        "restriction_reasons",
        "compatibility_reasons",
        "prohibited_relationship_reasons",
        "unsupported_relationship_reasons",
        "provenance_lineage",
        "reasoning_chain",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_graph_governance_explainability_result(
    result: V37GraphGovernanceExplainabilityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_explanation_subjects"] = sorted(data["missing_explanation_subjects"])
    data["explanations"] = [
        export_v3_7_graph_governance_explanation(explanation)
        for explanation in sorted(result.explanations, key=lambda item: item.explanation_id)
    ]
    return data


def serialize_v3_7_graph_governance_explainability_result(
    result: V37GraphGovernanceExplainabilityResult,
) -> str:
    return stable_serialize(export_v3_7_graph_governance_explainability_result(result))


def hash_v3_7_graph_governance_explainability_result(
    result: V37GraphGovernanceExplainabilityResult,
) -> str:
    data = export_v3_7_graph_governance_explainability_result(result)
    data.pop("deterministic_explainability_hash", None)
    return deterministic_hash(data)


def _build_explanations(
    governance_map: V37GraphGovernanceMap,
) -> tuple[V37GraphGovernanceExplanation, ...]:
    rule_reasons = {rule.rule_id: rule.restriction_summary for rule in governance_map.rules}
    explanations: list[V37GraphGovernanceExplanation] = []
    for classification in governance_map.node_classifications:
        explanations.append(
            V37GraphGovernanceExplanation(
                explanation_id=f"explain_node_{classification.node_id}",
                subject_type="node_governance",
                subject_id=classification.node_id,
                governance_classification=classification.governance_classification,
                why_governed="node governance classification is structural metadata only",
                restriction_reasons=classification.restriction_ids,
                compatibility_reasons=classification.compatibility_boundary_ids,
                prohibited_relationship_reasons=tuple(
                    rule_reasons.get(rule_id, rule_id)
                    for rule_id in classification.prohibited_relationship_ids
                ),
                unsupported_relationship_reasons=tuple(
                    rule_reasons.get(rule_id, rule_id)
                    for rule_id in classification.unsupported_relationship_ids
                ),
                provenance_lineage=classification.provenance.lineage_references,
                reasoning_chain=(
                    "governance_domain",
                    "node_classification",
                    "structural_governance_visibility",
                    "non_executable_boundary",
                ),
            )
        )
    for classification in governance_map.edge_classifications:
        explanations.append(
            V37GraphGovernanceExplanation(
                explanation_id=f"explain_edge_{classification.edge_id}",
                subject_type="edge_governance",
                subject_id=classification.edge_id,
                governance_classification=classification.governance_classification,
                why_governed="edge governance classification describes a structural relationship only",
                restriction_reasons=classification.restriction_ids,
                compatibility_reasons=classification.compatibility_boundary_ids,
                prohibited_relationship_reasons=tuple(
                    rule_reasons.get(rule_id, rule_id)
                    for rule_id in classification.prohibited_relationship_ids
                ),
                unsupported_relationship_reasons=tuple(
                    rule_reasons.get(rule_id, rule_id)
                    for rule_id in classification.unsupported_relationship_ids
                ),
                provenance_lineage=classification.provenance.lineage_references,
                reasoning_chain=(
                    "governance_domain",
                    "edge_classification",
                    "structural_relationship_only",
                    "no_runtime_traversal",
                ),
            )
        )
    explanations.extend(_finding_explanation(finding) for finding in governance_map.findings)
    return tuple(explanations)


def _finding_explanation(finding: V37GraphGovernanceFinding) -> V37GraphGovernanceExplanation:
    prohibited = (finding.reason,) if finding.finding_kind == "prohibited_relationship" else ()
    unsupported = (finding.reason,) if finding.finding_kind == "unsupported_relationship" else ()
    return V37GraphGovernanceExplanation(
        explanation_id=f"explain_finding_{finding.finding_id}",
        subject_type=finding.finding_kind,
        subject_id=finding.finding_id,
        governance_classification=finding.governance_classification,
        why_governed=finding.reason,
        restriction_reasons=(finding.rule_id,),
        compatibility_reasons=(),
        prohibited_relationship_reasons=prohibited,
        unsupported_relationship_reasons=unsupported,
        provenance_lineage=finding.provenance_references,
        reasoning_chain=(
            "governance_rule",
            finding.finding_kind,
            "fail_visible_relationship_visibility",
            "non_executable_boundary",
        ),
    )
