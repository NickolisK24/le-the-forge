"""Deterministic hashing for v4.2 governance routing visibility."""

from __future__ import annotations

import hashlib
from typing import Any

from .governance_routing_models import (
    DependencyGraphRoutingReference,
    GovernanceRouteRecord,
    GovernanceRoutingIdentity,
    GovernanceRoutingVisibility,
    LineageRoutingReference,
    ManifestRoutingReference,
    NonExecutableRouteOrderingVisibility,
    RouteStateVisibility,
    RoutingSourceReference,
    RoutingTargetReference,
    SequencingRoutingReference,
)
from .governance_routing_serialization import (
    export_dependency_graph_routing_reference,
    export_governance_route_record,
    export_governance_routing_identity,
    export_governance_routing_visibility,
    export_lineage_routing_reference,
    export_manifest_routing_reference,
    export_non_executable_route_ordering_visibility,
    export_route_state_visibility,
    export_routing_source_reference,
    export_routing_target_reference,
    export_sequencing_routing_reference,
    stable_serialize,
)


def deterministic_governance_routing_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_governance_routing_identity(identity: GovernanceRoutingIdentity) -> str:
    return deterministic_governance_routing_hash(export_governance_routing_identity(identity))


def hash_routing_source_reference(reference: RoutingSourceReference) -> str:
    return deterministic_governance_routing_hash(export_routing_source_reference(reference))


def hash_routing_target_reference(reference: RoutingTargetReference) -> str:
    return deterministic_governance_routing_hash(export_routing_target_reference(reference))


def hash_manifest_routing_reference(reference: ManifestRoutingReference) -> str:
    return deterministic_governance_routing_hash(export_manifest_routing_reference(reference))


def hash_dependency_graph_routing_reference(reference: DependencyGraphRoutingReference) -> str:
    return deterministic_governance_routing_hash(export_dependency_graph_routing_reference(reference))


def hash_lineage_routing_reference(reference: LineageRoutingReference) -> str:
    return deterministic_governance_routing_hash(export_lineage_routing_reference(reference))


def hash_sequencing_routing_reference(reference: SequencingRoutingReference) -> str:
    return deterministic_governance_routing_hash(export_sequencing_routing_reference(reference))


def hash_governance_route_record(record: GovernanceRouteRecord) -> str:
    return deterministic_governance_routing_hash(export_governance_route_record(record))


def hash_route_state_visibility(visibility: RouteStateVisibility) -> str:
    return deterministic_governance_routing_hash(export_route_state_visibility(visibility))


def hash_non_executable_route_ordering_visibility(visibility: NonExecutableRouteOrderingVisibility) -> str:
    return deterministic_governance_routing_hash(export_non_executable_route_ordering_visibility(visibility))


def hash_governance_routing_visibility(routing: GovernanceRoutingVisibility) -> str:
    return deterministic_governance_routing_hash(export_governance_routing_visibility(routing))
