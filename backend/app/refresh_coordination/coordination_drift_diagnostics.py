"""Diagnostics for v4.2 coordination drift certification."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import CoordinationDependencyGraph, default_coordination_dependency_graph
from .coordination_drift_hashing import (
    hash_coordination_drift_certification,
    hash_coordination_drift_record,
    hash_cross_layer_drift_visibility,
    hash_dependency_graph_drift_reference,
    hash_drift_state_visibility,
    hash_lineage_drift_reference,
    hash_manifest_drift_reference,
    hash_routing_drift_reference,
    hash_sequencing_drift_reference,
)
from .coordination_drift_models import (
    DRIFT_STATE_CONFLICTING,
    DRIFT_STATE_CROSS_LAYER,
    DRIFT_STATE_MISSING,
    DRIFT_STATE_PROHIBITED_CORRECTION,
    DRIFT_STATE_STALE,
    DRIFT_STATE_UNSUPPORTED_TRANSITION,
    DRIFT_STATES,
    FAIL_VISIBLE_DRIFT_STATES,
    CoordinationDriftCertification,
    CoordinationDriftRecord,
    default_coordination_drift_certification,
)
from .coordination_drift_serialization import serialize_coordination_drift_certification
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import hash_governance_routing_visibility
from .governance_routing_models import GovernanceRoutingVisibility, default_governance_routing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "drift_correction_enabled",
    "drift_remediation_enabled",
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
    "hidden_drift_correction_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_drift_states(records: tuple[CoordinationDriftRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in DRIFT_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.drift_state in counts:
            counts[record.drift_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_coordination_drift_record_ids(records: tuple[CoordinationDriftRecord, ...]) -> tuple[str, ...]:
    return tuple(
        record.drift_record_id
        for record in records
        if record.drift_state in FAIL_VISIBLE_DRIFT_STATES and record.fail_visible
    )


def aggregate_drift_state_records(
    certification: CoordinationDriftCertification,
    drift_state: str,
) -> tuple[str, ...]:
    return tuple(record.drift_record_id for record in certification.drift_records if record.drift_state == drift_state)


def coordination_drift_capability_flags(certification: CoordinationDriftCertification) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.stale_drift_visibility,
        certification.missing_drift_visibility,
        certification.conflicting_drift_visibility,
        certification.prohibited_correction_visibility,
        certification.unsupported_transition_visibility,
        certification.cross_layer_drift_visibility,
        certification.governance_visibility,
        *certification.manifest_drift_references,
        *certification.dependency_graph_drift_references,
        *certification.lineage_drift_references,
        *certification.sequencing_drift_references,
        *certification.routing_drift_references,
        *certification.drift_records,
        *certification.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_drift_capability_flags(certification: CoordinationDriftCertification) -> dict[str, bool]:
    return {key: value for key, value in coordination_drift_capability_flags(certification).items() if value}


def coordination_drift_certifications_equal(
    left: CoordinationDriftCertification,
    right: CoordinationDriftCertification,
) -> bool:
    return serialize_coordination_drift_certification(left) == serialize_coordination_drift_certification(right)


def _corrective_enabled(item: object) -> bool:
    return any(bool(getattr(item, flag_name, False)) for flag_name in CAPABILITY_FLAG_NAMES)


def validate_coordination_drift_visibility(certification: CoordinationDriftCertification) -> dict[str, object]:
    stale_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_STALE)
    missing_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_MISSING)
    conflicting_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_CONFLICTING)
    prohibited_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_PROHIBITED_CORRECTION)
    unsupported_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_UNSUPPORTED_TRANSITION)
    stale_visible = set(stale_record_ids).issubset(set(certification.stale_drift_visibility.drift_record_ids))
    missing_visible = set(missing_record_ids).issubset(set(certification.missing_drift_visibility.drift_record_ids))
    conflicting_visible = set(conflicting_record_ids).issubset(
        set(certification.conflicting_drift_visibility.drift_record_ids)
    )
    prohibited_visible = set(prohibited_record_ids).issubset(
        set(certification.prohibited_correction_visibility.drift_record_ids)
    )
    unsupported_visible = set(unsupported_record_ids).issubset(
        set(certification.unsupported_transition_visibility.drift_record_ids)
    )
    invalid_record_ids = tuple(
        record.drift_record_id for record in certification.drift_records if record.drift_state not in DRIFT_STATES
    )
    hidden_count = sum(
        1
        for item in (*certification.drift_records, *certification.diagnostics)
        if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            certification.stale_drift_visibility,
            certification.missing_drift_visibility,
            certification.conflicting_drift_visibility,
            certification.prohibited_correction_visibility,
            certification.unsupported_transition_visibility,
            certification.cross_layer_drift_visibility,
            *certification.drift_records,
            *certification.diagnostics,
        )
        if _corrective_enabled(item)
    )
    return {
        "valid": (
            stale_visible
            and missing_visible
            and conflicting_visible
            and prohibited_visible
            and unsupported_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "drift_state_counts": count_coordination_drift_states(certification.drift_records),
        "fail_visible_record_ids": fail_visible_coordination_drift_record_ids(certification.drift_records),
        "stale_record_ids": stale_record_ids,
        "missing_record_ids": missing_record_ids,
        "conflicting_record_ids": conflicting_record_ids,
        "prohibited_correction_record_ids": prohibited_record_ids,
        "unsupported_transition_record_ids": unsupported_record_ids,
        "stale_drift_visible": stale_visible,
        "missing_drift_visible": missing_visible,
        "conflicting_drift_visible": conflicting_visible,
        "prohibited_correction_visible": prohibited_visible,
        "unsupported_transition_visible": unsupported_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in certification.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in certification.diagnostics),
    }


def validate_cross_layer_drift_visibility(certification: CoordinationDriftCertification) -> dict[str, object]:
    cross_layer_record_ids = aggregate_drift_state_records(certification, DRIFT_STATE_CROSS_LAYER)
    visible = set(cross_layer_record_ids).issubset(set(certification.cross_layer_drift_visibility.drift_record_ids))
    involved_layers_visible = len(certification.cross_layer_drift_visibility.involved_layer_references) > 0
    corrective_count = sum(
        1
        for item in (certification.cross_layer_drift_visibility, *certification.drift_records)
        if _corrective_enabled(item)
    )
    return {
        "valid": visible and involved_layers_visible and corrective_count == 0,
        "cross_layer_record_ids": cross_layer_record_ids,
        "cross_layer_drift_visible": visible,
        "involved_layers_visible": involved_layers_visible,
        "involved_layer_references": certification.cross_layer_drift_visibility.involved_layer_references,
        "layer_pairs": certification.cross_layer_drift_visibility.layer_pairs,
        "corrective_count": corrective_count,
    }


def validate_manifest_drift_compatibility(
    certification: CoordinationDriftCertification,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    reference_matches = any(
        reference.manifest_reference == source.identity.manifest_id
        and reference.manifest_hash_reference == manifest_hash
        for reference in certification.manifest_drift_references
    )
    return {
        "valid": (
            certification.identity.source_manifest_reference == source.identity.manifest_id
            and certification.compatibility_manifest_reference == source.identity.manifest_id
            and certification.identity.source_manifest_hash_reference == manifest_hash
            and reference_matches
        ),
        "source_manifest_reference": certification.identity.source_manifest_reference,
        "compatibility_manifest_reference": certification.compatibility_manifest_reference,
        "manifest_reference": source.identity.manifest_id,
        "source_manifest_hash_reference": certification.identity.source_manifest_hash_reference,
        "expected_manifest_hash": manifest_hash,
        "manifest_hash_matches": certification.identity.source_manifest_hash_reference == manifest_hash,
        "manifest_drift_reference_matches": reference_matches,
    }


def validate_dependency_graph_drift_compatibility(
    certification: CoordinationDriftCertification,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    graph_hash = hash_coordination_dependency_graph(source_graph)
    reference_matches = any(
        reference.dependency_graph_reference == source_graph.identity.graph_id
        and reference.dependency_graph_hash_reference == graph_hash
        for reference in certification.dependency_graph_drift_references
    )
    return {
        "valid": (
            certification.identity.source_dependency_graph_reference == source_graph.identity.graph_id
            and certification.compatibility_dependency_graph_reference == source_graph.identity.graph_id
            and certification.identity.source_dependency_graph_hash_reference == graph_hash
            and reference_matches
        ),
        "source_dependency_graph_reference": certification.identity.source_dependency_graph_reference,
        "compatibility_dependency_graph_reference": certification.compatibility_dependency_graph_reference,
        "dependency_graph_reference": source_graph.identity.graph_id,
        "source_dependency_graph_hash_reference": certification.identity.source_dependency_graph_hash_reference,
        "expected_dependency_graph_hash": graph_hash,
        "dependency_graph_hash_matches": certification.identity.source_dependency_graph_hash_reference == graph_hash,
        "dependency_graph_drift_reference_matches": reference_matches,
    }


def validate_lineage_drift_compatibility(
    certification: CoordinationDriftCertification,
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
        for reference in certification.lineage_drift_references
    )
    return {
        "valid": (
            certification.identity.source_lineage_chain_reference == source_lineage.identity.chain_id
            and certification.compatibility_lineage_chain_reference == source_lineage.identity.chain_id
            and certification.identity.source_lineage_chain_hash_reference == lineage_hash
            and reference_matches
        ),
        "source_lineage_chain_reference": certification.identity.source_lineage_chain_reference,
        "compatibility_lineage_chain_reference": certification.compatibility_lineage_chain_reference,
        "lineage_chain_reference": source_lineage.identity.chain_id,
        "source_lineage_chain_hash_reference": certification.identity.source_lineage_chain_hash_reference,
        "expected_lineage_chain_hash": lineage_hash,
        "lineage_chain_hash_matches": certification.identity.source_lineage_chain_hash_reference == lineage_hash,
        "lineage_drift_reference_matches": reference_matches,
    }


def validate_sequencing_drift_compatibility(
    certification: CoordinationDriftCertification,
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
        for reference in certification.sequencing_drift_references
    )
    return {
        "valid": (
            certification.identity.source_sequencing_reference == source_sequencing.identity.sequencing_id
            and certification.compatibility_sequencing_reference == source_sequencing.identity.sequencing_id
            and certification.identity.source_sequencing_hash_reference == sequencing_hash
            and reference_matches
        ),
        "source_sequencing_reference": certification.identity.source_sequencing_reference,
        "compatibility_sequencing_reference": certification.compatibility_sequencing_reference,
        "sequencing_reference": source_sequencing.identity.sequencing_id,
        "source_sequencing_hash_reference": certification.identity.source_sequencing_hash_reference,
        "expected_sequencing_hash": sequencing_hash,
        "sequencing_hash_matches": certification.identity.source_sequencing_hash_reference == sequencing_hash,
        "sequencing_drift_reference_matches": reference_matches,
    }


def validate_routing_drift_compatibility(
    certification: CoordinationDriftCertification,
    routing: GovernanceRoutingVisibility | None = None,
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
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    routing_hash = hash_governance_routing_visibility(source_routing)
    reference_matches = any(
        reference.routing_reference == source_routing.identity.routing_id
        and reference.routing_hash_reference == routing_hash
        for reference in certification.routing_drift_references
    )
    return {
        "valid": (
            certification.identity.source_routing_reference == source_routing.identity.routing_id
            and certification.compatibility_routing_reference == source_routing.identity.routing_id
            and certification.identity.source_routing_hash_reference == routing_hash
            and reference_matches
        ),
        "source_routing_reference": certification.identity.source_routing_reference,
        "compatibility_routing_reference": certification.compatibility_routing_reference,
        "routing_reference": source_routing.identity.routing_id,
        "source_routing_hash_reference": certification.identity.source_routing_hash_reference,
        "expected_routing_hash": routing_hash,
        "routing_hash_matches": certification.identity.source_routing_hash_reference == routing_hash,
        "routing_drift_reference_matches": reference_matches,
    }


def validate_coordination_drift_non_execution(certification: CoordinationDriftCertification) -> dict[str, object]:
    enabled_flags = enabled_coordination_drift_capability_flags(certification)
    return {
        "valid": len(enabled_flags) == 0 and certification.non_executable and certification.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": certification.non_executable,
        "descriptive_only": certification.descriptive_only,
        "drift_correction_disabled": not certification.drift_correction_enabled,
        "drift_remediation_disabled": not certification.drift_remediation_enabled,
        "routing_execution_disabled": not certification.routing_execution_enabled,
        "orchestration_execution_disabled": not certification.orchestration_execution_enabled,
        "refresh_execution_disabled": not certification.refresh_execution_enabled,
        "sequencing_execution_disabled": not certification.sequencing_execution_enabled,
        "scheduling_execution_disabled": not certification.scheduling_execution_enabled,
        "dependency_resolution_disabled": not certification.dependency_resolution_enabled,
        "lineage_repair_disabled": not certification.lineage_repair_enabled,
        "lineage_inference_disabled": not certification.lineage_inference_enabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": (
            not certification.production_consumption_enabled
            and not certification.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "remediation_disabled": not certification.remediation_enabled,
        "automatic_correction_disabled": not certification.automatic_correction_enabled,
        "automatic_rollback_disabled": not certification.automatic_rollback_enabled,
        "authorization_disabled": not certification.authorization_enabled,
        "approval_disabled": not certification.approval_enabled,
        "ranking_disabled": not certification.ranking_enabled,
        "scoring_disabled": not certification.scoring_enabled,
        "selection_disabled": not certification.selection_enabled,
        "operational_execution_disabled": not certification.operational_execution_enabled,
        "hidden_drift_correction_absent": not certification.hidden_drift_correction_enabled,
        "implicit_execution_pathway_absent": not certification.implicit_execution_pathway_enabled,
    }


def build_coordination_drift_diagnostics(
    certification: CoordinationDriftCertification | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    source = certification or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    visibility = validate_coordination_drift_visibility(source)
    cross_layer = validate_cross_layer_drift_visibility(source)
    manifest_compatibility = validate_manifest_drift_compatibility(source, source_manifest)
    graph_compatibility = validate_dependency_graph_drift_compatibility(source, source_graph, source_manifest)
    lineage_compatibility = validate_lineage_drift_compatibility(
        source,
        source_lineage,
        source_graph,
        source_manifest,
    )
    sequencing_compatibility = validate_sequencing_drift_compatibility(
        source,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    routing_compatibility = validate_routing_drift_compatibility(
        source,
        source_routing,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    non_execution = validate_coordination_drift_non_execution(source)
    enabled_flags = enabled_coordination_drift_capability_flags(source)
    return {
        "drift_certification_hash": hash_coordination_drift_certification(source),
        "manifest_drift_hashes": [
            hash_manifest_drift_reference(reference) for reference in source.manifest_drift_references
        ],
        "dependency_graph_drift_hashes": [
            hash_dependency_graph_drift_reference(reference) for reference in source.dependency_graph_drift_references
        ],
        "lineage_drift_hashes": [
            hash_lineage_drift_reference(reference) for reference in source.lineage_drift_references
        ],
        "sequencing_drift_hashes": [
            hash_sequencing_drift_reference(reference) for reference in source.sequencing_drift_references
        ],
        "routing_drift_hashes": [
            hash_routing_drift_reference(reference) for reference in source.routing_drift_references
        ],
        "drift_record_hashes": [hash_coordination_drift_record(record) for record in source.drift_records],
        "stale_visibility_hash": hash_drift_state_visibility(source.stale_drift_visibility),
        "missing_visibility_hash": hash_drift_state_visibility(source.missing_drift_visibility),
        "conflicting_visibility_hash": hash_drift_state_visibility(source.conflicting_drift_visibility),
        "prohibited_correction_visibility_hash": hash_drift_state_visibility(source.prohibited_correction_visibility),
        "unsupported_transition_visibility_hash": hash_drift_state_visibility(source.unsupported_transition_visibility),
        "cross_layer_visibility_hash": hash_cross_layer_drift_visibility(source.cross_layer_drift_visibility),
        "drift_visibility_validation": visibility,
        "cross_layer_drift_validation": cross_layer,
        "manifest_drift_compatibility_validation": manifest_compatibility,
        "dependency_graph_drift_compatibility_validation": graph_compatibility,
        "lineage_drift_compatibility_validation": lineage_compatibility,
        "sequencing_drift_compatibility_validation": sequencing_compatibility,
        "routing_drift_compatibility_validation": routing_compatibility,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "stale_record_ids": visibility["stale_record_ids"],
        "missing_record_ids": visibility["missing_record_ids"],
        "conflicting_record_ids": visibility["conflicting_record_ids"],
        "prohibited_correction_record_ids": visibility["prohibited_correction_record_ids"],
        "unsupported_transition_record_ids": visibility["unsupported_transition_record_ids"],
        "cross_layer_record_ids": cross_layer["cross_layer_record_ids"],
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "fail_visible_drift_record_count": len(visibility["fail_visible_record_ids"]),
    }
