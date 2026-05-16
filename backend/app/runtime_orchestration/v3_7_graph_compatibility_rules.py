"""Deterministic compatibility rules for v3.7 graph reasoning."""

from __future__ import annotations

from .v3_7_graph_compatibility_domains import (
    COMPAT_DOMAIN_COMPATIBILITY_BOUNDARY,
    COMPAT_DOMAIN_EXPERIMENTAL_GOVERNANCE,
    COMPAT_DOMAIN_GRAPH_EXECUTION,
    COMPAT_DOMAIN_GRAPH_STRUCTURE,
    COMPAT_DOMAIN_GOVERNANCE_VISIBILITY,
    COMPAT_DOMAIN_LEGACY_STRUCTURE,
    COMPAT_DOMAIN_RUNTIME_DISPATCH,
    COMPAT_DOMAIN_UNKNOWN_EXTERNAL,
    default_v3_7_graph_compatibility_domains,
)
from .v3_7_graph_compatibility_models import (
    V3_7_GRAPH_COMPATIBILITY_PHASE_ID,
    V37_COMPATIBILITY_RESTRICTED,
    V37_COMPATIBILITY_VISIBILITY_VISIBLE,
    V37_COMPATIBLE,
    V37_EXPERIMENTAL_COMPATIBILITY,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
    V37_INCOMPATIBLE,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    V37_UNSUPPORTED_COMPATIBILITY,
    V37EdgeCompatibilityResult,
    V37GraphCompatibilityAggregation,
    V37GraphCompatibilityContinuityEvidence,
    V37GraphCompatibilityFinding,
    V37GraphCompatibilityMap,
    V37GraphCompatibilityRule,
    V37NodeCompatibilityResult,
)
from .v3_7_graph_governance_models import (
    V37_EDGE_COMPATIBILITY_RESTRICTED,
    V37_EDGE_GOVERNANCE_RESTRICTED,
    V37_NODE_EXPERIMENTAL,
    V37_NODE_GOVERNANCE_RESTRICTED,
)
from .v3_7_graph_governance_rules import build_v3_7_graph_governance_map
from .v3_7_graph_models import default_v3_7_graph_provenance


RULE_COMPAT_STRUCTURE_TO_STRUCTURE = "rule_compat_structure_to_structure"
RULE_COMPAT_GOVERNANCE_TO_STRUCTURE = "rule_compat_governance_to_structure"
RULE_COMPAT_STRUCTURE_TO_EXPERIMENTAL = "rule_compat_structure_to_experimental"
RULE_COMPAT_LEGACY_INCOMPATIBLE = "rule_compat_legacy_incompatible"
RULE_COMPAT_RUNTIME_DISPATCH_UNSUPPORTED = "rule_compat_runtime_dispatch_unsupported"
RULE_COMPAT_GRAPH_EXECUTION_PROHIBITED = "rule_compat_graph_execution_prohibited"
RULE_COMPAT_UNKNOWN_EXTERNAL = "rule_compat_unknown_external"


def default_v3_7_graph_compatibility_rules() -> tuple[V37GraphCompatibilityRule, ...]:
    return (
        _rule(
            RULE_COMPAT_STRUCTURE_TO_STRUCTURE,
            "node_edge_compatibility",
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            V37_COMPATIBLE,
            (),
            "graph structure relationships are structurally compatible",
        ),
        _rule(
            RULE_COMPAT_GOVERNANCE_TO_STRUCTURE,
            "governance_aware_compatibility",
            COMPAT_DOMAIN_GOVERNANCE_VISIBILITY,
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
            ("rule_governance_visibility_to_provenance",),
            "governance visibility relationships are compatible with governance restrictions",
        ),
        _rule(
            RULE_COMPAT_STRUCTURE_TO_EXPERIMENTAL,
            "compatibility_restricted",
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            COMPAT_DOMAIN_EXPERIMENTAL_GOVERNANCE,
            V37_EXPERIMENTAL_COMPATIBILITY,
            ("rule_provenance_to_explainability",),
            "experimental governance relationships remain visible as experimental compatibility",
        ),
        _rule(
            RULE_COMPAT_LEGACY_INCOMPATIBLE,
            "incompatible_relationship",
            COMPAT_DOMAIN_LEGACY_STRUCTURE,
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            V37_INCOMPATIBLE,
            (),
            "legacy structural assumptions are incompatible with v3.7 compatibility reasoning",
        ),
        _rule(
            RULE_COMPAT_RUNTIME_DISPATCH_UNSUPPORTED,
            "unsupported_relationship",
            COMPAT_DOMAIN_RUNTIME_DISPATCH,
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            V37_UNSUPPORTED_COMPATIBILITY,
            ("rule_runtime_dispatch_relationship_unsupported",),
            "runtime dispatch compatibility is unsupported",
        ),
        _rule(
            RULE_COMPAT_GRAPH_EXECUTION_PROHIBITED,
            "prohibited_relationship",
            COMPAT_DOMAIN_GRAPH_EXECUTION,
            COMPAT_DOMAIN_GRAPH_STRUCTURE,
            V37_PROHIBITED_COMPATIBILITY,
            ("rule_graph_execution_relationship_prohibited",),
            "graph execution compatibility is prohibited",
        ),
        _rule(
            RULE_COMPAT_UNKNOWN_EXTERNAL,
            "unknown_relationship",
            COMPAT_DOMAIN_UNKNOWN_EXTERNAL,
            COMPAT_DOMAIN_COMPATIBILITY_BOUNDARY,
            V37_UNKNOWN_COMPATIBILITY,
            (),
            "unknown external compatibility remains visible and unresolved",
        ),
    )


def build_v3_7_graph_compatibility_map(governance_map=None) -> V37GraphCompatibilityMap:
    source_governance = governance_map or build_v3_7_graph_governance_map()
    domains = default_v3_7_graph_compatibility_domains()
    rules = default_v3_7_graph_compatibility_rules()
    node_by_id = {node.node_id: node for node in source_governance.node_classifications}
    node_results = tuple(
        _node_result(edge, node_by_id[edge.source_node_id], node_by_id[edge.target_node_id])
        for edge in source_governance.edge_classifications
        if edge.source_node_id in node_by_id and edge.target_node_id in node_by_id
    )
    edge_results = tuple(_edge_result(edge) for edge in source_governance.edge_classifications)
    findings = _compatibility_findings(rules)
    aggregation = aggregate_v3_7_graph_compatibility(node_results, edge_results, findings)
    continuity = (
        V37GraphCompatibilityContinuityEvidence(
            continuity_id="v3_7_graph_compatibility_continuity_evidence",
            domain_ids=tuple(domain.domain_id for domain in domains),
            rule_ids=tuple(rule.rule_id for rule in rules),
            node_relationship_ids=tuple(result.relationship_id for result in node_results),
            edge_relationship_ids=tuple(result.edge_id for result in edge_results),
            finding_ids=tuple(finding.finding_id for finding in findings),
            governance_lineage_references=("v3_7_graph_governance_boundary_intelligence",),
            compatibility_lineage_references=("v3_7_graph_compatibility_reasoning",),
            provenance_lineage_references=tuple(
                sorted(
                    {domain.provenance.provenance_id for domain in domains}
                    | {rule.provenance.provenance_id for rule in rules}
                )
            ),
            explainability_lineage_references=("v3_7_graph_compatibility_explainability",),
            replay_lineage_references=("v3_7_graph_replay_continuity",),
            rollback_lineage_references=("v3_7_graph_rollback_continuity",),
            deterministic_hash_references=("v3_7_graph_compatibility_hash",),
        ),
    )
    return V37GraphCompatibilityMap(
        graph_id=source_governance.graph_id,
        compatibility_phase_id=V3_7_GRAPH_COMPATIBILITY_PHASE_ID,
        domains=domains,
        rules=rules,
        node_results=node_results,
        edge_results=edge_results,
        findings=findings,
        aggregation=aggregation,
        continuity_evidence=continuity,
    )


def classify_v3_7_node_compatibility(source_governance: str, target_governance: str) -> str:
    if source_governance == V37_NODE_GOVERNANCE_RESTRICTED:
        return V37_GOVERNANCE_RESTRICTED_COMPATIBILITY
    if target_governance == V37_NODE_EXPERIMENTAL:
        return V37_EXPERIMENTAL_COMPATIBILITY
    return V37_COMPATIBLE


def classify_v3_7_edge_compatibility(edge_governance: str) -> str:
    if edge_governance == V37_EDGE_GOVERNANCE_RESTRICTED:
        return V37_GOVERNANCE_RESTRICTED_COMPATIBILITY
    if edge_governance == V37_EDGE_COMPATIBILITY_RESTRICTED:
        return V37_COMPATIBILITY_RESTRICTED
    return V37_COMPATIBLE


def aggregate_v3_7_graph_compatibility(
    node_results: tuple[V37NodeCompatibilityResult, ...],
    edge_results: tuple[V37EdgeCompatibilityResult, ...],
    findings: tuple[V37GraphCompatibilityFinding, ...],
) -> V37GraphCompatibilityAggregation:
    classifications = [
        result.compatibility_classification
        for result in node_results
    ] + [
        result.compatibility_classification
        for result in edge_results
    ] + [
        finding.compatibility_classification
        for finding in findings
    ]
    return V37GraphCompatibilityAggregation(
        compatible_relationship_count=classifications.count(V37_COMPATIBLE),
        incompatible_relationship_count=classifications.count(V37_INCOMPATIBLE),
        unsupported_relationship_count=classifications.count(V37_UNSUPPORTED_COMPATIBILITY),
        prohibited_relationship_count=classifications.count(V37_PROHIBITED_COMPATIBILITY),
        experimental_relationship_count=classifications.count(V37_EXPERIMENTAL_COMPATIBILITY),
        unknown_relationship_count=classifications.count(V37_UNKNOWN_COMPATIBILITY),
        governance_restricted_count=classifications.count(V37_GOVERNANCE_RESTRICTED_COMPATIBILITY),
        compatibility_restricted_count=classifications.count(V37_COMPATIBILITY_RESTRICTED),
        fail_visible_finding_count=sum(1 for finding in findings if finding.fail_visible),
        node_relationship_count=len(node_results),
        edge_relationship_count=len(edge_results),
    )


def _node_result(edge, source_node, target_node) -> V37NodeCompatibilityResult:
    classification = classify_v3_7_node_compatibility(
        source_node.governance_classification,
        target_node.governance_classification,
    )
    rule_id = {
        V37_GOVERNANCE_RESTRICTED_COMPATIBILITY: RULE_COMPAT_GOVERNANCE_TO_STRUCTURE,
        V37_EXPERIMENTAL_COMPATIBILITY: RULE_COMPAT_STRUCTURE_TO_EXPERIMENTAL,
    }.get(classification, RULE_COMPAT_STRUCTURE_TO_STRUCTURE)
    return V37NodeCompatibilityResult(
        relationship_id=f"node_compat_{source_node.node_id}_to_{target_node.node_id}",
        source_node_id=source_node.node_id,
        target_node_id=target_node.node_id,
        source_domain_id=_node_domain(source_node.governance_classification),
        target_domain_id=_node_domain(target_node.governance_classification),
        source_governance_classification=source_node.governance_classification,
        target_governance_classification=target_node.governance_classification,
        compatibility_classification=classification,
        rule_id=rule_id,
        governance_rule_ids=tuple(edge.restriction_ids),
        finding_ids=(),
        provenance=default_v3_7_graph_provenance(edge.edge_id, "node_compatibility_result"),
        explainability_evidence_ids=(f"v3_7_compatibility_explanation_{edge.edge_id}_nodes",),
    )


def _edge_result(edge) -> V37EdgeCompatibilityResult:
    classification = classify_v3_7_edge_compatibility(edge.governance_classification)
    rule_id = {
        V37_GOVERNANCE_RESTRICTED_COMPATIBILITY: RULE_COMPAT_GOVERNANCE_TO_STRUCTURE,
        V37_COMPATIBILITY_RESTRICTED: RULE_COMPAT_STRUCTURE_TO_EXPERIMENTAL,
    }.get(classification, RULE_COMPAT_STRUCTURE_TO_STRUCTURE)
    return V37EdgeCompatibilityResult(
        edge_id=edge.edge_id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        relationship_type=edge.relationship_type,
        edge_governance_classification=edge.governance_classification,
        domain_compatibility_classification=classification,
        compatibility_classification=classification,
        rule_id=rule_id,
        governance_rule_ids=tuple(edge.restriction_ids),
        finding_ids=(),
        provenance=default_v3_7_graph_provenance(edge.edge_id, "edge_compatibility_result"),
        explainability_evidence_ids=(f"v3_7_compatibility_explanation_{edge.edge_id}_edge",),
    )


def _compatibility_findings(
    rules: tuple[V37GraphCompatibilityRule, ...],
) -> tuple[V37GraphCompatibilityFinding, ...]:
    findings: list[V37GraphCompatibilityFinding] = []
    for rule in rules:
        findings.append(
            V37GraphCompatibilityFinding(
                finding_id=f"finding_{rule.rule_id}",
                finding_kind=f"{rule.compatibility_classification}_compatibility",
                subject_type="compatibility_rule",
                subject_id=rule.rule_id,
                compatibility_classification=rule.compatibility_classification,
                visibility_status=V37_COMPATIBILITY_VISIBILITY_VISIBLE,
                reason=rule.restriction_summary,
                rule_id=rule.rule_id,
                governance_rule_ids=rule.governance_rule_ids,
                provenance=default_v3_7_graph_provenance(rule.rule_id, "compatibility_finding"),
            )
        )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def _node_domain(governance_classification: str) -> str:
    if governance_classification == V37_NODE_GOVERNANCE_RESTRICTED:
        return COMPAT_DOMAIN_GOVERNANCE_VISIBILITY
    if governance_classification == V37_NODE_EXPERIMENTAL:
        return COMPAT_DOMAIN_EXPERIMENTAL_GOVERNANCE
    return COMPAT_DOMAIN_GRAPH_STRUCTURE


def _rule(
    rule_id: str,
    rule_kind: str,
    source_domain_id: str,
    target_domain_id: str,
    classification: str,
    governance_rule_ids: tuple[str, ...],
    restriction_summary: str,
) -> V37GraphCompatibilityRule:
    return V37GraphCompatibilityRule(
        rule_id=rule_id,
        rule_kind=rule_kind,
        source_domain_id=source_domain_id,
        target_domain_id=target_domain_id,
        compatibility_classification=classification,
        governance_rule_ids=governance_rule_ids,
        restriction_summary=restriction_summary,
        visible=True,
        provenance=default_v3_7_graph_provenance(rule_id, "graph_compatibility_rule"),
    )
