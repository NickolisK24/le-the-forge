"""Deterministic governance domains for v3.7 graph boundary intelligence."""

from __future__ import annotations

from .v3_7_graph_governance_models import (
    V37_DOMAIN_CLASSIFICATIONS,
    V37_DOMAIN_COMPATIBILITY_RESTRICTED,
    V37_DOMAIN_EXPERIMENTAL,
    V37_DOMAIN_GOVERNANCE_RESTRICTED,
    V37_DOMAIN_PROHIBITED,
    V37_DOMAIN_SUPPORTED,
    V37_DOMAIN_UNSUPPORTED,
    V37GraphGovernanceDomain,
)
from .v3_7_graph_models import V37GraphProvenance, default_v3_7_graph_provenance


DOMAIN_GRAPH_STRUCTURE_MODELING = "domain_graph_structure_modeling"
DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE = "domain_graph_governance_boundary_intelligence"
DOMAIN_GOVERNANCE_VISIBILITY = "domain_governance_visibility"
DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY = "domain_compatibility_boundary_visibility"
DOMAIN_RUNTIME_DISPATCH = "domain_runtime_dispatch"
DOMAIN_OPTIMIZATION = "domain_optimization"
DOMAIN_GRAPH_EXECUTION = "domain_graph_execution"
DOMAIN_ROUTING_SCHEDULING_DISPATCH = "domain_routing_scheduling_dispatch"


def default_v3_7_graph_governance_domains() -> tuple[V37GraphGovernanceDomain, ...]:
    return (
        _domain(
            DOMAIN_GRAPH_STRUCTURE_MODELING,
            "Graph Structure Modeling",
            V37_DOMAIN_SUPPORTED,
            restriction_ids=("restriction_structural_reasoning_only",),
        ),
        _domain(
            DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,
            "Graph Governance Boundary Intelligence",
            V37_DOMAIN_EXPERIMENTAL,
            restriction_ids=("restriction_metadata_only",),
        ),
        _domain(
            DOMAIN_GOVERNANCE_VISIBILITY,
            "Governance Visibility",
            V37_DOMAIN_GOVERNANCE_RESTRICTED,
            restriction_ids=("restriction_governance_visible",),
        ),
        _domain(
            DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,
            "Compatibility Boundary Visibility",
            V37_DOMAIN_COMPATIBILITY_RESTRICTED,
            restriction_ids=("restriction_compatibility_visible",),
            compatibility_boundary_ids=("v3_6_to_v3_7_graph_foundation_compatibility",),
        ),
        _domain(
            DOMAIN_RUNTIME_DISPATCH,
            "Runtime Dispatch",
            V37_DOMAIN_UNSUPPORTED,
            restriction_ids=("restriction_runtime_dispatch_unsupported",),
        ),
        _domain(
            DOMAIN_OPTIMIZATION,
            "Optimization",
            V37_DOMAIN_UNSUPPORTED,
            restriction_ids=("restriction_optimization_unsupported",),
        ),
        _domain(
            DOMAIN_GRAPH_EXECUTION,
            "Graph Execution",
            V37_DOMAIN_PROHIBITED,
            restriction_ids=("restriction_graph_execution_prohibited",),
        ),
        _domain(
            DOMAIN_ROUTING_SCHEDULING_DISPATCH,
            "Routing Scheduling Dispatch",
            V37_DOMAIN_PROHIBITED,
            restriction_ids=("restriction_routing_scheduling_dispatch_prohibited",),
        ),
    )


def classify_v3_7_governance_domain(domain_id: str) -> str:
    for domain in default_v3_7_graph_governance_domains():
        if domain.domain_id == domain_id:
            return domain.domain_classification
    return V37_DOMAIN_UNSUPPORTED


def export_v3_7_domain_classifications() -> list[str]:
    return list(V37_DOMAIN_CLASSIFICATIONS)


def _domain(
    domain_id: str,
    domain_name: str,
    classification: str,
    restriction_ids: tuple[str, ...],
    compatibility_boundary_ids: tuple[str, ...] = (),
) -> V37GraphGovernanceDomain:
    return V37GraphGovernanceDomain(
        domain_id=domain_id,
        domain_name=domain_name,
        domain_classification=classification,
        restriction_ids=restriction_ids,
        compatibility_boundary_ids=compatibility_boundary_ids,
        provenance=_governance_domain_provenance(domain_id),
    )


def _governance_domain_provenance(domain_id: str) -> V37GraphProvenance:
    return default_v3_7_graph_provenance(domain_id, "graph_governance_domain")
