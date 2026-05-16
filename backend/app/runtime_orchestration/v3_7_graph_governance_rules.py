"""Deterministic governance rules for v3.7 graph boundary intelligence."""

from __future__ import annotations

from .v3_7_graph_governance_domains import (
    DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,
    DOMAIN_GOVERNANCE_VISIBILITY,
    DOMAIN_GRAPH_EXECUTION,
    DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,
    DOMAIN_GRAPH_STRUCTURE_MODELING,
    DOMAIN_OPTIMIZATION,
    DOMAIN_ROUTING_SCHEDULING_DISPATCH,
    DOMAIN_RUNTIME_DISPATCH,
    default_v3_7_graph_governance_domains,
)
from .v3_7_graph_governance_models import (
    V3_7_GRAPH_GOVERNANCE_PHASE_ID,
    V37_EDGE_ALLOWED_STRUCTURAL,
    V37_EDGE_COMPATIBILITY_RESTRICTED,
    V37_EDGE_GOVERNANCE_RESTRICTED,
    V37_EDGE_PROHIBITED_STRUCTURAL,
    V37_EDGE_UNSUPPORTED_STRUCTURAL,
    V37_GOVERNANCE_VISIBILITY_VISIBLE,
    V37_NODE_EXPERIMENTAL,
    V37_NODE_GOVERNANCE_RESTRICTED,
    V37_NODE_SUPPORTED,
    V37GraphGovernanceContinuityEvidence,
    V37GraphGovernanceFinding,
    V37GraphGovernanceMap,
    V37GraphGovernanceRule,
    V37NodeGovernanceClassification,
    V37EdgeGovernanceClassification,
)
from .v3_7_graph_models import (
    V37GraphEdge,
    V37GraphNode,
    V37OrchestrationPlanningGraph,
    default_v3_7_graph_provenance,
    default_v3_7_orchestration_planning_graph,
)


RULE_GOVERNANCE_VISIBILITY_TO_PROVENANCE = "rule_governance_visibility_to_provenance"
RULE_PROVENANCE_TO_EXPLAINABILITY = "rule_provenance_to_explainability"
RULE_GRAPH_EXECUTION_PROHIBITED = "rule_graph_execution_relationship_prohibited"
RULE_ROUTING_SCHEDULING_DISPATCH_PROHIBITED = "rule_routing_scheduling_dispatch_relationship_prohibited"
RULE_RUNTIME_DISPATCH_UNSUPPORTED = "rule_runtime_dispatch_relationship_unsupported"
RULE_OPTIMIZATION_UNSUPPORTED = "rule_optimization_relationship_unsupported"


def default_v3_7_graph_governance_rules() -> tuple[V37GraphGovernanceRule, ...]:
    return (
        _rule(
            RULE_GOVERNANCE_VISIBILITY_TO_PROVENANCE,
            "node_edge_governance",
            DOMAIN_GOVERNANCE_VISIBILITY,
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            V37_NODE_GOVERNANCE_RESTRICTED,
            V37_EDGE_GOVERNANCE_RESTRICTED,
            "governance visibility can structurally reference provenance continuity",
        ),
        _rule(
            RULE_PROVENANCE_TO_EXPLAINABILITY,
            "node_edge_governance",
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,
            V37_NODE_SUPPORTED,
            V37_EDGE_COMPATIBILITY_RESTRICTED,
            "provenance continuity can structurally reference explainability continuity",
        ),
        _rule(
            RULE_GRAPH_EXECUTION_PROHIBITED,
            "prohibited_relationship",
            DOMAIN_GRAPH_EXECUTION,
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            V37_NODE_SUPPORTED,
            V37_EDGE_PROHIBITED_STRUCTURAL,
            "graph execution relationships are prohibited",
            prohibited=True,
        ),
        _rule(
            RULE_ROUTING_SCHEDULING_DISPATCH_PROHIBITED,
            "prohibited_relationship",
            DOMAIN_ROUTING_SCHEDULING_DISPATCH,
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            V37_NODE_SUPPORTED,
            V37_EDGE_PROHIBITED_STRUCTURAL,
            "routing, scheduling, and dispatch relationships are prohibited",
            prohibited=True,
        ),
        _rule(
            RULE_RUNTIME_DISPATCH_UNSUPPORTED,
            "unsupported_relationship",
            DOMAIN_RUNTIME_DISPATCH,
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            V37_NODE_SUPPORTED,
            V37_EDGE_UNSUPPORTED_STRUCTURAL,
            "runtime dispatch relationships are unsupported",
            unsupported=True,
        ),
        _rule(
            RULE_OPTIMIZATION_UNSUPPORTED,
            "unsupported_relationship",
            DOMAIN_OPTIMIZATION,
            DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,
            V37_NODE_EXPERIMENTAL,
            V37_EDGE_UNSUPPORTED_STRUCTURAL,
            "optimization feedback relationships are unsupported",
            unsupported=True,
        ),
    )


def build_v3_7_graph_governance_map(
    graph: V37OrchestrationPlanningGraph | None = None,
) -> V37GraphGovernanceMap:
    source_graph = graph or default_v3_7_orchestration_planning_graph()
    domains = default_v3_7_graph_governance_domains()
    rules = default_v3_7_graph_governance_rules()
    prohibited_rule_ids = tuple(rule.rule_id for rule in rules if rule.prohibited_relationship)
    unsupported_rule_ids = tuple(rule.rule_id for rule in rules if rule.unsupported_relationship)
    node_classifications = tuple(
        _classify_node(node, prohibited_rule_ids, unsupported_rule_ids)
        for node in source_graph.nodes
    )
    edge_classifications = tuple(_classify_edge(edge) for edge in source_graph.edges)
    findings = tuple(_relationship_visibility_findings(rules))
    continuity = (
        V37GraphGovernanceContinuityEvidence(
            continuity_id="v3_7_graph_governance_continuity_evidence",
            domain_ids=tuple(domain.domain_id for domain in domains),
            rule_ids=tuple(rule.rule_id for rule in rules),
            node_classification_ids=tuple(item.node_id for item in node_classifications),
            edge_classification_ids=tuple(item.edge_id for item in edge_classifications),
            finding_ids=tuple(finding.finding_id for finding in findings),
            governance_lineage_references=("v3_7_graph_governance_boundary_intelligence",),
            compatibility_lineage_references=("v3_6_to_v3_7_graph_foundation_compatibility",),
            provenance_lineage_references=tuple(
                sorted(
                    {domain.provenance.provenance_id for domain in domains}
                    | {rule.provenance.provenance_id for rule in rules}
                )
            ),
            explainability_lineage_references=("v3_7_graph_governance_explainability",),
            replay_lineage_references=("v3_7_graph_replay_continuity",),
            rollback_lineage_references=("v3_7_graph_rollback_continuity",),
            deterministic_hash_references=("v3_7_graph_governance_hash",),
        ),
    )
    return V37GraphGovernanceMap(
        graph_id=source_graph.identity.graph_id,
        governance_phase_id=V3_7_GRAPH_GOVERNANCE_PHASE_ID,
        domains=domains,
        rules=rules,
        node_classifications=node_classifications,
        edge_classifications=edge_classifications,
        findings=findings,
        continuity_evidence=continuity,
    )


def classify_v3_7_node_governance(node: V37GraphNode) -> str:
    node_id = node.identity.node_id
    if "governance" in node_id:
        return V37_NODE_GOVERNANCE_RESTRICTED
    if "explainability" in node_id:
        return V37_NODE_EXPERIMENTAL
    return V37_NODE_SUPPORTED


def classify_v3_7_edge_governance(edge: V37GraphEdge) -> str:
    edge_id = edge.identity.edge_id
    if "governance_visibility" in edge_id:
        return V37_EDGE_GOVERNANCE_RESTRICTED
    if "explainability" in edge_id:
        return V37_EDGE_COMPATIBILITY_RESTRICTED
    return V37_EDGE_ALLOWED_STRUCTURAL


def _classify_node(
    node: V37GraphNode,
    prohibited_rule_ids: tuple[str, ...],
    unsupported_rule_ids: tuple[str, ...],
) -> V37NodeGovernanceClassification:
    classification = classify_v3_7_node_governance(node)
    domain_ids = {
        V37_NODE_GOVERNANCE_RESTRICTED: (DOMAIN_GOVERNANCE_VISIBILITY,),
        V37_NODE_EXPERIMENTAL: (DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,),
    }.get(classification, (DOMAIN_GRAPH_STRUCTURE_MODELING,))
    return V37NodeGovernanceClassification(
        node_id=node.identity.node_id,
        node_type=node.identity.node_type,
        governance_classification=classification,
        governance_domain_ids=domain_ids,
        restriction_ids=tuple(node.governance_boundary_ids),
        compatibility_boundary_ids=tuple(node.compatibility_boundary_ids),
        prohibited_relationship_ids=prohibited_rule_ids,
        unsupported_relationship_ids=unsupported_rule_ids,
        provenance=default_v3_7_graph_provenance(node.identity.node_id, "node_governance_classification"),
        explainability_evidence_ids=(f"v3_7_governance_explanation_{node.identity.node_id}",),
    )


def _classify_edge(edge: V37GraphEdge) -> V37EdgeGovernanceClassification:
    classification = classify_v3_7_edge_governance(edge)
    rule_id = (
        RULE_GOVERNANCE_VISIBILITY_TO_PROVENANCE
        if classification == V37_EDGE_GOVERNANCE_RESTRICTED
        else RULE_PROVENANCE_TO_EXPLAINABILITY
    )
    domain_ids = {
        V37_EDGE_GOVERNANCE_RESTRICTED: (DOMAIN_GOVERNANCE_VISIBILITY,),
        V37_EDGE_COMPATIBILITY_RESTRICTED: (DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,),
    }.get(classification, (DOMAIN_GRAPH_STRUCTURE_MODELING,))
    return V37EdgeGovernanceClassification(
        edge_id=edge.identity.edge_id,
        source_node_id=edge.identity.source_node_id,
        target_node_id=edge.identity.target_node_id,
        relationship_type=edge.identity.relationship_type,
        governance_classification=classification,
        governance_domain_ids=domain_ids,
        restriction_ids=(rule_id,),
        compatibility_boundary_ids=tuple(edge.compatibility_boundary_ids),
        prohibited_relationship_ids=(),
        unsupported_relationship_ids=(),
        provenance=default_v3_7_graph_provenance(edge.identity.edge_id, "edge_governance_classification"),
        explainability_evidence_ids=(f"v3_7_governance_explanation_{edge.identity.edge_id}",),
    )


def _relationship_visibility_findings(
    rules: tuple[V37GraphGovernanceRule, ...],
) -> tuple[V37GraphGovernanceFinding, ...]:
    findings: list[V37GraphGovernanceFinding] = []
    for rule in rules:
        if not rule.prohibited_relationship and not rule.unsupported_relationship:
            continue
        kind = "prohibited_relationship" if rule.prohibited_relationship else "unsupported_relationship"
        findings.append(
            V37GraphGovernanceFinding(
                finding_id=f"finding_{rule.rule_id}",
                finding_kind=kind,
                subject_type="governance_rule",
                subject_id=rule.rule_id,
                governance_classification=rule.edge_classification,
                visibility_status=V37_GOVERNANCE_VISIBILITY_VISIBLE,
                reason=rule.restriction_summary,
                rule_id=rule.rule_id,
                provenance_references=(rule.provenance.provenance_id,),
            )
        )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def _rule(
    rule_id: str,
    rule_kind: str,
    source_domain_id: str,
    target_domain_id: str,
    node_classification: str,
    edge_classification: str,
    restriction_summary: str,
    prohibited: bool = False,
    unsupported: bool = False,
) -> V37GraphGovernanceRule:
    return V37GraphGovernanceRule(
        rule_id=rule_id,
        rule_kind=rule_kind,
        source_domain_id=source_domain_id,
        target_domain_id=target_domain_id,
        node_classification=node_classification,
        edge_classification=edge_classification,
        restriction_summary=restriction_summary,
        relationship_visible=True,
        prohibited_relationship=prohibited,
        unsupported_relationship=unsupported,
        provenance=default_v3_7_graph_provenance(rule_id, "graph_governance_rule"),
    )
