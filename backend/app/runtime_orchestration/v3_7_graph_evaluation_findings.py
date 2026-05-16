"""Fail-visible findings for v3.7 graph evaluation reasoning."""

from __future__ import annotations

from .v3_7_graph_compatibility_models import (
    V37_COMPATIBILITY_RESTRICTED,
    V37_COMPATIBILITY_VISIBILITY_VISIBLE,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
)
from .v3_7_graph_compatibility_rules import build_v3_7_graph_compatibility_map
from .v3_7_graph_evaluation_models import (
    V37_EVALUATION_COMPATIBILITY_RESTRICTED,
    V37_EVALUATION_CONTINUITY_WARNING,
    V37_EVALUATION_FINDING_CLASSIFICATIONS,
    V37_EVALUATION_GOVERNANCE_RESTRICTED,
    V37GraphEvaluationFinding,
)
from .v3_7_graph_models import default_v3_7_graph_provenance


def build_v3_7_graph_evaluation_findings(compatibility_map=None) -> tuple[V37GraphEvaluationFinding, ...]:
    source = compatibility_map or build_v3_7_graph_compatibility_map()
    findings: list[V37GraphEvaluationFinding] = []
    for finding in source.findings:
        findings.append(
            V37GraphEvaluationFinding(
                finding_id=f"evaluation_{finding.finding_id}",
                finding_classification=finding.compatibility_classification,
                subject_type=finding.subject_type,
                subject_id=finding.subject_id,
                reason=finding.reason,
                evidence_ids=(finding.finding_id, finding.rule_id),
                compatibility_reference_ids=(finding.rule_id,),
                governance_reference_ids=finding.governance_rule_ids,
                provenance=default_v3_7_graph_provenance(
                    f"evaluation_{finding.finding_id}",
                    "graph_evaluation_finding",
                ),
                fail_visible=finding.fail_visible,
                hidden=finding.visibility_status != V37_COMPATIBILITY_VISIBILITY_VISIBLE,
            )
        )

    compatibility_restricted_edges = tuple(
        result for result in source.edge_results if result.compatibility_classification == V37_COMPATIBILITY_RESTRICTED
    )
    for edge_result in compatibility_restricted_edges:
        findings.append(
            V37GraphEvaluationFinding(
                finding_id=f"evaluation_compatibility_restricted_{edge_result.edge_id}",
                finding_classification=V37_EVALUATION_COMPATIBILITY_RESTRICTED,
                subject_type="edge_compatibility",
                subject_id=edge_result.edge_id,
                reason="edge relationship remains compatibility-restricted structural evidence",
                evidence_ids=edge_result.explainability_evidence_ids,
                compatibility_reference_ids=(edge_result.rule_id,),
                governance_reference_ids=edge_result.governance_rule_ids,
                provenance=default_v3_7_graph_provenance(
                    f"evaluation_compatibility_restricted_{edge_result.edge_id}",
                    "graph_evaluation_finding",
                ),
            )
        )

    governance_restricted_results = tuple(
        result
        for result in source.node_results + source.edge_results
        if result.compatibility_classification == V37_GOVERNANCE_RESTRICTED_COMPATIBILITY
    )
    if governance_restricted_results and not any(
        finding.finding_classification == V37_EVALUATION_GOVERNANCE_RESTRICTED for finding in findings
    ):
        result = governance_restricted_results[0]
        subject_id = getattr(result, "relationship_id", getattr(result, "edge_id", "governance_restricted"))
        findings.append(
            V37GraphEvaluationFinding(
                finding_id=f"evaluation_governance_restricted_{subject_id}",
                finding_classification=V37_EVALUATION_GOVERNANCE_RESTRICTED,
                subject_type="governance_aware_evaluation",
                subject_id=subject_id,
                reason="governance-restricted compatibility remains visible in evaluation reasoning",
                evidence_ids=(subject_id,),
                compatibility_reference_ids=(result.rule_id,),
                governance_reference_ids=result.governance_rule_ids,
                provenance=default_v3_7_graph_provenance(
                    f"evaluation_governance_restricted_{subject_id}",
                    "graph_evaluation_finding",
                ),
            )
        )

    findings.append(
        V37GraphEvaluationFinding(
            finding_id="evaluation_structural_continuity_warning",
            finding_classification=V37_EVALUATION_CONTINUITY_WARNING,
            subject_type="evaluation_continuity",
            subject_id=source.graph_id,
            reason="structural reasoning continuity requires replay, rollback, provenance, and explainability evidence",
            evidence_ids=("v3_7_graph_evaluation_continuity_evidence",),
            compatibility_reference_ids=("v3_7_graph_compatibility_reasoning",),
            governance_reference_ids=("v3_7_graph_governance_boundary_intelligence",),
            provenance=default_v3_7_graph_provenance(
                "evaluation_structural_continuity_warning",
                "graph_evaluation_finding",
            ),
        )
    )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def export_v3_7_graph_evaluation_finding_classifications() -> list[str]:
    return list(V37_EVALUATION_FINDING_CLASSIFICATIONS)


def count_v3_7_graph_evaluation_findings_by_classification(
    findings: tuple[V37GraphEvaluationFinding, ...],
) -> dict[str, int]:
    counts = {classification: 0 for classification in V37_EVALUATION_FINDING_CLASSIFICATIONS}
    for finding in findings:
        counts[finding.finding_classification] = counts.get(finding.finding_classification, 0) + 1
    return dict(sorted(counts.items()))
