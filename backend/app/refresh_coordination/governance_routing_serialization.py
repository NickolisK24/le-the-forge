"""Canonical serialization for v4.2 governance routing visibility."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .governance_routing_models import (
    DependencyGraphRoutingReference,
    GovernanceRouteRecord,
    GovernanceRoutingDiagnostic,
    GovernanceRoutingGovernance,
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


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "routing_execution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "dependency_resolution_enabled",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "hidden_route_execution_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_governance_routing_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_governance_routing_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_governance_routing_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_governance_routing_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_governance_routing_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_governance_routing_identity(identity: GovernanceRoutingIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_routing_source_reference(reference: RoutingSourceReference) -> dict[str, Any]:
    return _disable_execution_fields(asdict(reference))


def export_routing_target_reference(reference: RoutingTargetReference) -> dict[str, Any]:
    return _disable_execution_fields(asdict(reference))


def export_manifest_routing_reference(reference: ManifestRoutingReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["route_record_ids"] = sorted_entries(data["route_record_ids"])
    return data


def export_dependency_graph_routing_reference(reference: DependencyGraphRoutingReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("node_references", "edge_references", "route_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lineage_routing_reference(reference: LineageRoutingReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("lineage_record_references", "route_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_sequencing_routing_reference(reference: SequencingRoutingReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("sequence_record_references", "route_record_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_route_record(record: GovernanceRouteRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_route_state_visibility(visibility: RouteStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("route_record_ids", "source_reference_ids", "target_reference_ids", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_non_executable_route_ordering_visibility(
    visibility: NonExecutableRouteOrderingVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "ordered_route_record_ids",
        "ordered_source_reference_ids",
        "ordered_target_reference_ids",
        "blocked_ordering_ids",
        "prohibited_ordering_ids",
        "unsupported_ordering_ids",
        "stale_ordering_ids",
        "missing_ordering_ids",
        "conflicting_ordering_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_routing_diagnostic(diagnostic: GovernanceRoutingDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_route_record_ids", "affected_reference_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_routing_governance(governance: GovernanceRoutingGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_routing_visibility(routing: GovernanceRoutingVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(routing))
    data["identity"] = export_governance_routing_identity(routing.identity)
    data["source_references"] = [
        export_routing_source_reference(reference)
        for reference in sorted(routing.source_references, key=lambda item: (item.deterministic_order, item.source_reference_id))
    ]
    data["target_references"] = [
        export_routing_target_reference(reference)
        for reference in sorted(routing.target_references, key=lambda item: (item.deterministic_order, item.target_reference_id))
    ]
    data["manifest_routing_references"] = [
        export_manifest_routing_reference(reference)
        for reference in sorted(
            routing.manifest_routing_references,
            key=lambda item: (item.deterministic_order, item.manifest_routing_reference_id),
        )
    ]
    data["dependency_graph_routing_references"] = [
        export_dependency_graph_routing_reference(reference)
        for reference in sorted(
            routing.dependency_graph_routing_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_routing_reference_id),
        )
    ]
    data["lineage_routing_references"] = [
        export_lineage_routing_reference(reference)
        for reference in sorted(
            routing.lineage_routing_references,
            key=lambda item: (item.deterministic_order, item.lineage_routing_reference_id),
        )
    ]
    data["sequencing_routing_references"] = [
        export_sequencing_routing_reference(reference)
        for reference in sorted(
            routing.sequencing_routing_references,
            key=lambda item: (item.deterministic_order, item.sequencing_routing_reference_id),
        )
    ]
    data["route_records"] = [
        export_governance_route_record(record)
        for record in sorted(routing.route_records, key=lambda item: (item.deterministic_order, item.route_record_id))
    ]
    data["ordering_visibility"] = export_non_executable_route_ordering_visibility(routing.ordering_visibility)
    data["blocked_route_visibility"] = export_route_state_visibility(routing.blocked_route_visibility)
    data["prohibited_route_visibility"] = export_route_state_visibility(routing.prohibited_route_visibility)
    data["unsupported_route_visibility"] = export_route_state_visibility(routing.unsupported_route_visibility)
    data["stale_route_visibility"] = export_route_state_visibility(routing.stale_route_visibility)
    data["missing_route_visibility"] = export_route_state_visibility(routing.missing_route_visibility)
    data["conflicting_route_visibility"] = export_route_state_visibility(routing.conflicting_route_visibility)
    data["diagnostics"] = [
        export_governance_routing_diagnostic(diagnostic)
        for diagnostic in sorted(routing.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["governance_visibility"] = export_governance_routing_governance(routing.governance_visibility)
    return data


def serialize_governance_routing_identity(identity: GovernanceRoutingIdentity) -> str:
    return stable_serialize(export_governance_routing_identity(identity))


def serialize_governance_routing_visibility(routing: GovernanceRoutingVisibility) -> str:
    return stable_serialize(export_governance_routing_visibility(routing))
