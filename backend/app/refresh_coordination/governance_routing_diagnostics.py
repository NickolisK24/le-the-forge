"""Diagnostics for v4.2 governance routing visibility."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import CoordinationDependencyGraph, default_coordination_dependency_graph
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import (
    hash_dependency_graph_routing_reference,
    hash_governance_route_record,
    hash_governance_routing_visibility,
    hash_lineage_routing_reference,
    hash_manifest_routing_reference,
    hash_non_executable_route_ordering_visibility,
    hash_route_state_visibility,
    hash_routing_source_reference,
    hash_routing_target_reference,
    hash_sequencing_routing_reference,
)
from .governance_routing_models import (
    FAIL_VISIBLE_ROUTE_STATES,
    ROUTE_STATE_BLOCKED,
    ROUTE_STATE_CONFLICTING,
    ROUTE_STATE_MISSING,
    ROUTE_STATE_PROHIBITED,
    ROUTE_STATE_STALE,
    ROUTE_STATE_UNSUPPORTED,
    ROUTE_STATES,
    GovernanceRouteRecord,
    GovernanceRoutingVisibility,
    default_governance_routing_visibility,
)
from .governance_routing_serialization import serialize_governance_routing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
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


def count_governance_route_states(records: tuple[GovernanceRouteRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in ROUTE_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.route_state in counts:
            counts[record.route_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_governance_route_record_ids(records: tuple[GovernanceRouteRecord, ...]) -> tuple[str, ...]:
    return tuple(
        record.route_record_id
        for record in records
        if record.route_state in FAIL_VISIBLE_ROUTE_STATES and record.fail_visible
    )


def aggregate_route_state_records(
    routing: GovernanceRoutingVisibility,
    route_state: str,
) -> tuple[str, ...]:
    return tuple(record.route_record_id for record in routing.route_records if record.route_state == route_state)


def governance_routing_capability_flags(routing: GovernanceRoutingVisibility) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        routing,
        routing.identity,
        routing.ordering_visibility,
        routing.blocked_route_visibility,
        routing.prohibited_route_visibility,
        routing.unsupported_route_visibility,
        routing.stale_route_visibility,
        routing.missing_route_visibility,
        routing.conflicting_route_visibility,
        routing.governance_visibility,
        *routing.source_references,
        *routing.target_references,
        *routing.manifest_routing_references,
        *routing.dependency_graph_routing_references,
        *routing.lineage_routing_references,
        *routing.sequencing_routing_references,
        *routing.route_records,
        *routing.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_governance_routing_capability_flags(routing: GovernanceRoutingVisibility) -> dict[str, bool]:
    return {key: value for key, value in governance_routing_capability_flags(routing).items() if value}


def governance_routing_visibility_equal(left: GovernanceRoutingVisibility, right: GovernanceRoutingVisibility) -> bool:
    return serialize_governance_routing_visibility(left) == serialize_governance_routing_visibility(right)


def validate_governance_route_visibility(routing: GovernanceRoutingVisibility) -> dict[str, object]:
    blocked_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_BLOCKED)
    prohibited_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_PROHIBITED)
    unsupported_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_UNSUPPORTED)
    stale_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_STALE)
    missing_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_MISSING)
    conflicting_record_ids = aggregate_route_state_records(routing, ROUTE_STATE_CONFLICTING)
    blocked_visible = set(blocked_record_ids).issubset(set(routing.blocked_route_visibility.route_record_ids))
    prohibited_visible = set(prohibited_record_ids).issubset(set(routing.prohibited_route_visibility.route_record_ids))
    unsupported_visible = set(unsupported_record_ids).issubset(set(routing.unsupported_route_visibility.route_record_ids))
    stale_visible = set(stale_record_ids).issubset(set(routing.stale_route_visibility.route_record_ids))
    missing_visible = set(missing_record_ids).issubset(set(routing.missing_route_visibility.route_record_ids))
    conflicting_visible = set(conflicting_record_ids).issubset(set(routing.conflicting_route_visibility.route_record_ids))
    invalid_record_ids = tuple(record.route_record_id for record in routing.route_records if record.route_state not in ROUTE_STATES)
    hidden_count = sum(
        1
        for item in (*routing.source_references, *routing.target_references, *routing.route_records, *routing.diagnostics)
        if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            routing.ordering_visibility,
            routing.blocked_route_visibility,
            routing.prohibited_route_visibility,
            routing.unsupported_route_visibility,
            routing.stale_route_visibility,
            routing.missing_route_visibility,
            routing.conflicting_route_visibility,
            *routing.route_records,
            *routing.diagnostics,
        )
        if getattr(item, "routing_execution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "sequencing_execution_enabled", False)
        or getattr(item, "scheduling_execution_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "lineage_repair_enabled", False)
        or getattr(item, "lineage_inference_enabled", False)
        or getattr(item, "planner_integration_enabled", False)
        or getattr(item, "production_consumption_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
        or getattr(item, "remediation_enabled", False)
        or getattr(item, "automatic_correction_enabled", False)
        or getattr(item, "automatic_rollback_enabled", False)
        or getattr(item, "authorization_enabled", False)
        or getattr(item, "approval_enabled", False)
        or getattr(item, "execution_enabled", False)
    )
    return {
        "valid": (
            blocked_visible
            and prohibited_visible
            and unsupported_visible
            and stale_visible
            and missing_visible
            and conflicting_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "route_state_counts": count_governance_route_states(routing.route_records),
        "fail_visible_record_ids": fail_visible_governance_route_record_ids(routing.route_records),
        "blocked_record_ids": blocked_record_ids,
        "prohibited_record_ids": prohibited_record_ids,
        "unsupported_record_ids": unsupported_record_ids,
        "stale_record_ids": stale_record_ids,
        "missing_record_ids": missing_record_ids,
        "conflicting_record_ids": conflicting_record_ids,
        "blocked_routes_visible": blocked_visible,
        "prohibited_routes_visible": prohibited_visible,
        "unsupported_routes_visible": unsupported_visible,
        "stale_routes_visible": stale_visible,
        "missing_routes_visible": missing_visible,
        "conflicting_routes_visible": conflicting_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in routing.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in routing.diagnostics),
    }


def validate_non_executable_route_ordering(routing: GovernanceRoutingVisibility) -> dict[str, object]:
    ordered_records = tuple(sorted(routing.route_records, key=lambda item: item.ordering_position))
    ordered_record_ids = tuple(record.route_record_id for record in ordered_records)
    ordered_source_ids = tuple(record.source_reference_id for record in ordered_records)
    ordered_target_ids = tuple(record.target_reference_id for record in ordered_records)
    missing_ordered_records = tuple(
        sorted(set(ordered_record_ids) - set(routing.ordering_visibility.ordered_route_record_ids))
    )
    corrective_count = sum(
        1
        for item in (routing.ordering_visibility, *routing.route_records)
        if getattr(item, "routing_execution_enabled", False)
        or getattr(item, "sequencing_execution_enabled", False)
        or getattr(item, "scheduling_execution_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
    )
    return {
        "valid": (
            ordered_record_ids == routing.ordering_visibility.ordered_route_record_ids
            and ordered_source_ids == routing.ordering_visibility.ordered_source_reference_ids
            and ordered_target_ids == routing.ordering_visibility.ordered_target_reference_ids
            and len(missing_ordered_records) == 0
            and routing.ordering_visibility.non_executable_ordering_only
            and corrective_count == 0
        ),
        "ordered_route_record_ids": ordered_record_ids,
        "ordered_source_reference_ids": ordered_source_ids,
        "ordered_target_reference_ids": ordered_target_ids,
        "missing_ordered_records": missing_ordered_records,
        "non_executable_ordering_only": routing.ordering_visibility.non_executable_ordering_only,
        "routing_execution_disabled": not routing.ordering_visibility.routing_execution_enabled,
        "corrective_ordering_count": corrective_count,
    }


def validate_manifest_routing_compatibility(
    routing: GovernanceRoutingVisibility,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    reference_matches = any(
        reference.manifest_reference == source.identity.manifest_id
        and reference.manifest_hash_reference == manifest_hash
        for reference in routing.manifest_routing_references
    )
    return {
        "valid": (
            routing.identity.source_manifest_reference == source.identity.manifest_id
            and routing.compatibility_manifest_reference == source.identity.manifest_id
            and routing.identity.source_manifest_hash_reference == manifest_hash
            and reference_matches
        ),
        "routing_source_manifest_reference": routing.identity.source_manifest_reference,
        "routing_compatibility_manifest_reference": routing.compatibility_manifest_reference,
        "manifest_reference": source.identity.manifest_id,
        "source_manifest_hash_reference": routing.identity.source_manifest_hash_reference,
        "expected_manifest_hash": manifest_hash,
        "manifest_hash_matches": routing.identity.source_manifest_hash_reference == manifest_hash,
        "manifest_routing_reference_matches": reference_matches,
    }


def validate_dependency_graph_routing_compatibility(
    routing: GovernanceRoutingVisibility,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    graph_hash = hash_coordination_dependency_graph(source_graph)
    reference_matches = any(
        reference.dependency_graph_reference == source_graph.identity.graph_id
        and reference.dependency_graph_hash_reference == graph_hash
        for reference in routing.dependency_graph_routing_references
    )
    return {
        "valid": (
            routing.identity.source_dependency_graph_reference == source_graph.identity.graph_id
            and routing.compatibility_dependency_graph_reference == source_graph.identity.graph_id
            and routing.identity.source_dependency_graph_hash_reference == graph_hash
            and reference_matches
        ),
        "routing_source_dependency_graph_reference": routing.identity.source_dependency_graph_reference,
        "routing_compatibility_dependency_graph_reference": routing.compatibility_dependency_graph_reference,
        "dependency_graph_reference": source_graph.identity.graph_id,
        "source_dependency_graph_hash_reference": routing.identity.source_dependency_graph_hash_reference,
        "expected_dependency_graph_hash": graph_hash,
        "dependency_graph_hash_matches": routing.identity.source_dependency_graph_hash_reference == graph_hash,
        "dependency_graph_routing_reference_matches": reference_matches,
    }


def validate_lineage_routing_compatibility(
    routing: GovernanceRoutingVisibility,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    lineage_hash = hash_coordination_lineage_chain(source_lineage)
    reference_matches = any(
        reference.lineage_chain_reference == source_lineage.identity.chain_id
        and reference.lineage_chain_hash_reference == lineage_hash
        for reference in routing.lineage_routing_references
    )
    return {
        "valid": (
            routing.identity.source_lineage_chain_reference == source_lineage.identity.chain_id
            and routing.compatibility_lineage_chain_reference == source_lineage.identity.chain_id
            and routing.identity.source_lineage_chain_hash_reference == lineage_hash
            and reference_matches
        ),
        "routing_source_lineage_chain_reference": routing.identity.source_lineage_chain_reference,
        "routing_compatibility_lineage_chain_reference": routing.compatibility_lineage_chain_reference,
        "lineage_chain_reference": source_lineage.identity.chain_id,
        "source_lineage_chain_hash_reference": routing.identity.source_lineage_chain_hash_reference,
        "expected_lineage_chain_hash": lineage_hash,
        "lineage_chain_hash_matches": routing.identity.source_lineage_chain_hash_reference == lineage_hash,
        "lineage_routing_reference_matches": reference_matches,
    }


def validate_sequencing_routing_compatibility(
    routing: GovernanceRoutingVisibility,
    sequencing: CoordinationSequencingIntelligence | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    sequencing_hash = hash_coordination_sequencing_intelligence(source_sequencing)
    reference_matches = any(
        reference.sequencing_reference == source_sequencing.identity.sequencing_id
        and reference.sequencing_hash_reference == sequencing_hash
        for reference in routing.sequencing_routing_references
    )
    return {
        "valid": (
            routing.identity.source_sequencing_reference == source_sequencing.identity.sequencing_id
            and routing.compatibility_sequencing_reference == source_sequencing.identity.sequencing_id
            and routing.identity.source_sequencing_hash_reference == sequencing_hash
            and reference_matches
        ),
        "routing_source_sequencing_reference": routing.identity.source_sequencing_reference,
        "routing_compatibility_sequencing_reference": routing.compatibility_sequencing_reference,
        "sequencing_reference": source_sequencing.identity.sequencing_id,
        "source_sequencing_hash_reference": routing.identity.source_sequencing_hash_reference,
        "expected_sequencing_hash": sequencing_hash,
        "sequencing_hash_matches": routing.identity.source_sequencing_hash_reference == sequencing_hash,
        "sequencing_routing_reference_matches": reference_matches,
    }


def validate_governance_routing_non_execution(routing: GovernanceRoutingVisibility) -> dict[str, object]:
    enabled_flags = enabled_governance_routing_capability_flags(routing)
    return {
        "valid": len(enabled_flags) == 0 and routing.non_executable and routing.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": routing.non_executable,
        "descriptive_only": routing.descriptive_only,
        "routing_execution_disabled": not routing.routing_execution_enabled,
        "orchestration_execution_disabled": not routing.orchestration_execution_enabled,
        "refresh_execution_disabled": not routing.refresh_execution_enabled,
        "sequencing_execution_disabled": not routing.sequencing_execution_enabled,
        "scheduling_execution_disabled": not routing.scheduling_execution_enabled,
        "dependency_resolution_disabled": not routing.dependency_resolution_enabled,
        "lineage_repair_disabled": not routing.lineage_repair_enabled,
        "lineage_inference_disabled": not routing.lineage_inference_enabled,
        "planner_integration_disabled": not routing.planner_integration_enabled,
        "production_consumption_disabled": (
            not routing.production_consumption_enabled and not routing.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not routing.runtime_mutation_enabled,
        "remediation_disabled": not routing.remediation_enabled,
        "automatic_correction_disabled": not routing.automatic_correction_enabled,
        "automatic_rollback_disabled": not routing.automatic_rollback_enabled,
        "authorization_disabled": not routing.authorization_enabled,
        "approval_disabled": not routing.approval_enabled,
        "ranking_disabled": not routing.ranking_enabled,
        "scoring_disabled": not routing.scoring_enabled,
        "selection_disabled": not routing.selection_enabled,
        "operational_execution_disabled": not routing.operational_execution_enabled,
        "hidden_route_execution_absent": not routing.hidden_route_execution_enabled,
        "implicit_execution_pathway_absent": not routing.implicit_execution_pathway_enabled,
    }


def build_governance_routing_diagnostics(
    routing: GovernanceRoutingVisibility | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    visibility = validate_governance_route_visibility(source)
    ordering = validate_non_executable_route_ordering(source)
    manifest_compatibility = validate_manifest_routing_compatibility(source, source_manifest)
    graph_compatibility = validate_dependency_graph_routing_compatibility(source, source_graph, source_manifest)
    lineage_compatibility = validate_lineage_routing_compatibility(
        source,
        source_lineage,
        source_graph,
        source_manifest,
    )
    sequencing_compatibility = validate_sequencing_routing_compatibility(
        source,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    non_execution = validate_governance_routing_non_execution(source)
    enabled_flags = enabled_governance_routing_capability_flags(source)
    return {
        "routing_hash": hash_governance_routing_visibility(source),
        "source_reference_hashes": [
            hash_routing_source_reference(reference) for reference in source.source_references
        ],
        "target_reference_hashes": [
            hash_routing_target_reference(reference) for reference in source.target_references
        ],
        "manifest_routing_hashes": [
            hash_manifest_routing_reference(reference) for reference in source.manifest_routing_references
        ],
        "dependency_graph_routing_hashes": [
            hash_dependency_graph_routing_reference(reference)
            for reference in source.dependency_graph_routing_references
        ],
        "lineage_routing_hashes": [
            hash_lineage_routing_reference(reference) for reference in source.lineage_routing_references
        ],
        "sequencing_routing_hashes": [
            hash_sequencing_routing_reference(reference) for reference in source.sequencing_routing_references
        ],
        "route_record_hashes": [hash_governance_route_record(record) for record in source.route_records],
        "ordering_visibility_hash": hash_non_executable_route_ordering_visibility(source.ordering_visibility),
        "blocked_visibility_hash": hash_route_state_visibility(source.blocked_route_visibility),
        "prohibited_visibility_hash": hash_route_state_visibility(source.prohibited_route_visibility),
        "unsupported_visibility_hash": hash_route_state_visibility(source.unsupported_route_visibility),
        "stale_visibility_hash": hash_route_state_visibility(source.stale_route_visibility),
        "missing_visibility_hash": hash_route_state_visibility(source.missing_route_visibility),
        "conflicting_visibility_hash": hash_route_state_visibility(source.conflicting_route_visibility),
        "route_visibility_validation": visibility,
        "route_ordering_validation": ordering,
        "manifest_routing_compatibility_validation": manifest_compatibility,
        "dependency_graph_routing_compatibility_validation": graph_compatibility,
        "lineage_routing_compatibility_validation": lineage_compatibility,
        "sequencing_routing_compatibility_validation": sequencing_compatibility,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "blocked_record_ids": visibility["blocked_record_ids"],
        "prohibited_record_ids": visibility["prohibited_record_ids"],
        "unsupported_record_ids": visibility["unsupported_record_ids"],
        "stale_record_ids": visibility["stale_record_ids"],
        "missing_record_ids": visibility["missing_record_ids"],
        "conflicting_record_ids": visibility["conflicting_record_ids"],
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "fail_visible_route_record_count": len(visibility["fail_visible_record_ids"]),
    }
