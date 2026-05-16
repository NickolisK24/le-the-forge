"""Deterministic compatibility domains for v3.7 graph reasoning."""

from __future__ import annotations

from .v3_7_graph_compatibility_models import (
    V37_COMPATIBILITY_CLASSIFICATIONS,
    V37_COMPATIBILITY_RESTRICTED,
    V37_COMPATIBLE,
    V37_EXPERIMENTAL_COMPATIBILITY,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
    V37_INCOMPATIBLE,
    V37_PROHIBITED_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
    V37_UNSUPPORTED_COMPATIBILITY,
    V37GraphCompatibilityDomain,
)
from .v3_7_graph_governance_domains import (
    DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,
    DOMAIN_GOVERNANCE_VISIBILITY,
    DOMAIN_GRAPH_EXECUTION,
    DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,
    DOMAIN_GRAPH_STRUCTURE_MODELING,
    DOMAIN_OPTIMIZATION,
    DOMAIN_RUNTIME_DISPATCH,
)
from .v3_7_graph_models import default_v3_7_graph_provenance


COMPAT_DOMAIN_GRAPH_STRUCTURE = "compat_domain_graph_structure"
COMPAT_DOMAIN_GOVERNANCE_VISIBILITY = "compat_domain_governance_visibility"
COMPAT_DOMAIN_COMPATIBILITY_BOUNDARY = "compat_domain_compatibility_boundary"
COMPAT_DOMAIN_EXPERIMENTAL_GOVERNANCE = "compat_domain_experimental_governance"
COMPAT_DOMAIN_LEGACY_STRUCTURE = "compat_domain_legacy_structure"
COMPAT_DOMAIN_RUNTIME_DISPATCH = "compat_domain_runtime_dispatch"
COMPAT_DOMAIN_GRAPH_EXECUTION = "compat_domain_graph_execution"
COMPAT_DOMAIN_UNKNOWN_EXTERNAL = "compat_domain_unknown_external"


def default_v3_7_graph_compatibility_domains() -> tuple[V37GraphCompatibilityDomain, ...]:
    return (
        _domain(COMPAT_DOMAIN_GRAPH_STRUCTURE, "Graph Structure", V37_COMPATIBLE, DOMAIN_GRAPH_STRUCTURE_MODELING),
        _domain(
            COMPAT_DOMAIN_GOVERNANCE_VISIBILITY,
            "Governance Visibility",
            V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
            DOMAIN_GOVERNANCE_VISIBILITY,
        ),
        _domain(
            COMPAT_DOMAIN_COMPATIBILITY_BOUNDARY,
            "Compatibility Boundary",
            V37_COMPATIBILITY_RESTRICTED,
            DOMAIN_COMPATIBILITY_BOUNDARY_VISIBILITY,
        ),
        _domain(
            COMPAT_DOMAIN_EXPERIMENTAL_GOVERNANCE,
            "Experimental Governance",
            V37_EXPERIMENTAL_COMPATIBILITY,
            DOMAIN_GRAPH_GOVERNANCE_BOUNDARY_INTELLIGENCE,
        ),
        _domain(COMPAT_DOMAIN_LEGACY_STRUCTURE, "Legacy Structure", V37_INCOMPATIBLE, DOMAIN_GRAPH_STRUCTURE_MODELING),
        _domain(COMPAT_DOMAIN_RUNTIME_DISPATCH, "Runtime Dispatch", V37_UNSUPPORTED_COMPATIBILITY, DOMAIN_RUNTIME_DISPATCH),
        _domain(COMPAT_DOMAIN_GRAPH_EXECUTION, "Graph Execution", V37_PROHIBITED_COMPATIBILITY, DOMAIN_GRAPH_EXECUTION),
        _domain(COMPAT_DOMAIN_UNKNOWN_EXTERNAL, "Unknown External", V37_UNKNOWN_COMPATIBILITY, DOMAIN_OPTIMIZATION),
    )


def classify_v3_7_compatibility_domain(domain_id: str) -> str:
    for domain in default_v3_7_graph_compatibility_domains():
        if domain.domain_id == domain_id:
            return domain.compatibility_classification
    return V37_UNKNOWN_COMPATIBILITY


def export_v3_7_compatibility_classifications() -> list[str]:
    return list(V37_COMPATIBILITY_CLASSIFICATIONS)


def _domain(
    domain_id: str,
    domain_name: str,
    classification: str,
    governance_domain_id: str,
) -> V37GraphCompatibilityDomain:
    return V37GraphCompatibilityDomain(
        domain_id=domain_id,
        domain_name=domain_name,
        compatibility_classification=classification,
        governance_domain_id=governance_domain_id,
        restriction_ids=(f"restriction_{classification}_compatibility",),
        provenance=default_v3_7_graph_provenance(domain_id, "graph_compatibility_domain"),
    )
