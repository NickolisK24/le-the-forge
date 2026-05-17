"""Diagnostics for v4.2 coordination sequencing intelligence."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import (
    CoordinationLineageChain,
    default_coordination_lineage_chain,
)
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import (
    hash_coordination_sequence_record,
    hash_coordination_sequencing_intelligence,
    hash_dependency_graph_sequence_reference,
    hash_lineage_sequence_reference,
    hash_manifest_sequence_reference,
    hash_non_executable_sequence_ordering_visibility,
    hash_sequence_state_visibility,
    hash_sequence_step_identity,
)
from .coordination_sequencing_models import (
    FAIL_VISIBLE_SEQUENCE_STATES,
    SEQUENCE_STATE_BLOCKED,
    SEQUENCE_STATE_CONFLICTING,
    SEQUENCE_STATE_MISSING,
    SEQUENCE_STATE_PROHIBITED,
    SEQUENCE_STATE_STALE,
    SEQUENCE_STATE_UNSUPPORTED,
    SEQUENCE_STATES,
    CoordinationSequenceRecord,
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .coordination_sequencing_serialization import serialize_coordination_sequencing_intelligence


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "dependency_resolution_enabled",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
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
    "hidden_sequence_execution_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_sequence_states(records: tuple[CoordinationSequenceRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in SEQUENCE_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.sequence_state in counts:
            counts[record.sequence_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_coordination_sequence_record_ids(
    records: tuple[CoordinationSequenceRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        record.sequence_record_id
        for record in records
        if record.sequence_state in FAIL_VISIBLE_SEQUENCE_STATES and record.fail_visible
    )


def aggregate_sequence_state_records(
    sequencing: CoordinationSequencingIntelligence,
    sequence_state: str,
) -> tuple[str, ...]:
    return tuple(
        record.sequence_record_id for record in sequencing.sequence_records if record.sequence_state == sequence_state
    )


def coordination_sequencing_capability_flags(sequencing: CoordinationSequencingIntelligence) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        sequencing,
        sequencing.identity,
        sequencing.ordering_visibility,
        sequencing.blocked_sequence_visibility,
        sequencing.prohibited_sequence_visibility,
        sequencing.unsupported_sequence_visibility,
        sequencing.stale_sequence_visibility,
        sequencing.missing_sequence_visibility,
        sequencing.conflicting_sequence_visibility,
        sequencing.governance_visibility,
        *sequencing.step_identities,
        *sequencing.manifest_sequence_references,
        *sequencing.dependency_graph_sequence_references,
        *sequencing.lineage_sequence_references,
        *sequencing.sequence_records,
        *sequencing.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_sequencing_capability_flags(
    sequencing: CoordinationSequencingIntelligence,
) -> dict[str, bool]:
    return {key: value for key, value in coordination_sequencing_capability_flags(sequencing).items() if value}


def coordination_sequencing_intelligence_equal(
    left: CoordinationSequencingIntelligence,
    right: CoordinationSequencingIntelligence,
) -> bool:
    return serialize_coordination_sequencing_intelligence(left) == serialize_coordination_sequencing_intelligence(right)


def validate_coordination_sequence_visibility(sequencing: CoordinationSequencingIntelligence) -> dict[str, object]:
    blocked_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_BLOCKED)
    prohibited_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_PROHIBITED)
    unsupported_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_UNSUPPORTED)
    stale_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_STALE)
    missing_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_MISSING)
    conflicting_record_ids = aggregate_sequence_state_records(sequencing, SEQUENCE_STATE_CONFLICTING)
    blocked_visible = set(blocked_record_ids).issubset(set(sequencing.blocked_sequence_visibility.sequence_record_ids))
    prohibited_visible = set(prohibited_record_ids).issubset(
        set(sequencing.prohibited_sequence_visibility.sequence_record_ids)
    )
    unsupported_visible = set(unsupported_record_ids).issubset(
        set(sequencing.unsupported_sequence_visibility.sequence_record_ids)
    )
    stale_visible = set(stale_record_ids).issubset(set(sequencing.stale_sequence_visibility.sequence_record_ids))
    missing_visible = set(missing_record_ids).issubset(set(sequencing.missing_sequence_visibility.sequence_record_ids))
    conflicting_visible = set(conflicting_record_ids).issubset(
        set(sequencing.conflicting_sequence_visibility.sequence_record_ids)
    )
    invalid_record_ids = tuple(
        record.sequence_record_id for record in sequencing.sequence_records if record.sequence_state not in SEQUENCE_STATES
    )
    hidden_count = sum(
        1
        for item in (*sequencing.sequence_records, *sequencing.diagnostics)
        if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            sequencing.ordering_visibility,
            sequencing.blocked_sequence_visibility,
            sequencing.prohibited_sequence_visibility,
            sequencing.unsupported_sequence_visibility,
            sequencing.stale_sequence_visibility,
            sequencing.missing_sequence_visibility,
            sequencing.conflicting_sequence_visibility,
            *sequencing.sequence_records,
            *sequencing.diagnostics,
        )
        if getattr(item, "sequencing_execution_enabled", False)
        or getattr(item, "scheduling_execution_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "lineage_repair_enabled", False)
        or getattr(item, "lineage_inference_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
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
        "sequence_state_counts": count_coordination_sequence_states(sequencing.sequence_records),
        "fail_visible_record_ids": fail_visible_coordination_sequence_record_ids(sequencing.sequence_records),
        "blocked_record_ids": blocked_record_ids,
        "prohibited_record_ids": prohibited_record_ids,
        "unsupported_record_ids": unsupported_record_ids,
        "stale_record_ids": stale_record_ids,
        "missing_record_ids": missing_record_ids,
        "conflicting_record_ids": conflicting_record_ids,
        "blocked_sequences_visible": blocked_visible,
        "prohibited_sequences_visible": prohibited_visible,
        "unsupported_sequences_visible": unsupported_visible,
        "stale_sequences_visible": stale_visible,
        "missing_sequences_visible": missing_visible,
        "conflicting_sequences_visible": conflicting_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in sequencing.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in sequencing.diagnostics),
    }


def validate_non_executable_sequence_ordering(sequencing: CoordinationSequencingIntelligence) -> dict[str, object]:
    ordered_records = tuple(sorted(sequencing.sequence_records, key=lambda item: item.ordering_position))
    ordered_record_ids = tuple(record.sequence_record_id for record in ordered_records)
    ordered_step_ids = tuple(record.step_identity_id for record in ordered_records)
    missing_ordered_records = tuple(
        sorted(set(ordered_record_ids) - set(sequencing.ordering_visibility.ordered_sequence_record_ids))
    )
    missing_ordered_steps = tuple(
        sorted(set(ordered_step_ids) - set(sequencing.ordering_visibility.ordered_step_identity_ids))
    )
    corrective_count = sum(
        1
        for item in (sequencing.ordering_visibility, *sequencing.sequence_records)
        if getattr(item, "sequencing_execution_enabled", False)
        or getattr(item, "scheduling_execution_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
    )
    return {
        "valid": (
            ordered_record_ids == sequencing.ordering_visibility.ordered_sequence_record_ids
            and ordered_step_ids == sequencing.ordering_visibility.ordered_step_identity_ids
            and len(missing_ordered_records) == 0
            and len(missing_ordered_steps) == 0
            and sequencing.ordering_visibility.non_executable_ordering_only
            and corrective_count == 0
        ),
        "ordered_sequence_record_ids": ordered_record_ids,
        "ordered_step_identity_ids": ordered_step_ids,
        "missing_ordered_records": missing_ordered_records,
        "missing_ordered_steps": missing_ordered_steps,
        "non_executable_ordering_only": sequencing.ordering_visibility.non_executable_ordering_only,
        "sequencing_execution_disabled": not sequencing.ordering_visibility.sequencing_execution_enabled,
        "scheduling_execution_disabled": not sequencing.ordering_visibility.scheduling_execution_enabled,
        "corrective_ordering_count": corrective_count,
    }


def validate_coordination_manifest_sequence_compatibility(
    sequencing: CoordinationSequencingIntelligence,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    reference_matches = any(
        reference.manifest_reference == source.identity.manifest_id
        and reference.manifest_hash_reference == manifest_hash
        for reference in sequencing.manifest_sequence_references
    )
    return {
        "valid": (
            sequencing.identity.source_manifest_reference == source.identity.manifest_id
            and sequencing.compatibility_manifest_reference == source.identity.manifest_id
            and sequencing.identity.source_manifest_hash_reference == manifest_hash
            and reference_matches
        ),
        "sequencing_source_manifest_reference": sequencing.identity.source_manifest_reference,
        "sequencing_compatibility_manifest_reference": sequencing.compatibility_manifest_reference,
        "manifest_reference": source.identity.manifest_id,
        "source_manifest_hash_reference": sequencing.identity.source_manifest_hash_reference,
        "expected_manifest_hash": manifest_hash,
        "manifest_hash_matches": sequencing.identity.source_manifest_hash_reference == manifest_hash,
        "manifest_sequence_reference_matches": reference_matches,
    }


def validate_coordination_dependency_graph_sequence_compatibility(
    sequencing: CoordinationSequencingIntelligence,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    graph_hash = hash_coordination_dependency_graph(source_graph)
    reference_matches = any(
        reference.dependency_graph_reference == source_graph.identity.graph_id
        and reference.dependency_graph_hash_reference == graph_hash
        for reference in sequencing.dependency_graph_sequence_references
    )
    return {
        "valid": (
            sequencing.identity.source_dependency_graph_reference == source_graph.identity.graph_id
            and sequencing.compatibility_dependency_graph_reference == source_graph.identity.graph_id
            and sequencing.identity.source_dependency_graph_hash_reference == graph_hash
            and reference_matches
        ),
        "sequencing_source_dependency_graph_reference": sequencing.identity.source_dependency_graph_reference,
        "sequencing_compatibility_dependency_graph_reference": sequencing.compatibility_dependency_graph_reference,
        "dependency_graph_reference": source_graph.identity.graph_id,
        "source_dependency_graph_hash_reference": sequencing.identity.source_dependency_graph_hash_reference,
        "expected_dependency_graph_hash": graph_hash,
        "dependency_graph_hash_matches": sequencing.identity.source_dependency_graph_hash_reference == graph_hash,
        "dependency_graph_sequence_reference_matches": reference_matches,
    }


def validate_coordination_lineage_chain_sequence_compatibility(
    sequencing: CoordinationSequencingIntelligence,
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
        for reference in sequencing.lineage_sequence_references
    )
    return {
        "valid": (
            sequencing.identity.source_lineage_chain_reference == source_lineage.identity.chain_id
            and sequencing.compatibility_lineage_chain_reference == source_lineage.identity.chain_id
            and sequencing.identity.source_lineage_chain_hash_reference == lineage_hash
            and reference_matches
        ),
        "sequencing_source_lineage_chain_reference": sequencing.identity.source_lineage_chain_reference,
        "sequencing_compatibility_lineage_chain_reference": sequencing.compatibility_lineage_chain_reference,
        "lineage_chain_reference": source_lineage.identity.chain_id,
        "source_lineage_chain_hash_reference": sequencing.identity.source_lineage_chain_hash_reference,
        "expected_lineage_chain_hash": lineage_hash,
        "lineage_chain_hash_matches": sequencing.identity.source_lineage_chain_hash_reference == lineage_hash,
        "lineage_sequence_reference_matches": reference_matches,
    }


def validate_coordination_sequencing_non_execution(sequencing: CoordinationSequencingIntelligence) -> dict[str, object]:
    enabled_flags = enabled_coordination_sequencing_capability_flags(sequencing)
    return {
        "valid": len(enabled_flags) == 0 and sequencing.non_executable and sequencing.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": sequencing.non_executable,
        "descriptive_only": sequencing.descriptive_only,
        "sequencing_execution_disabled": not sequencing.sequencing_execution_enabled,
        "scheduling_execution_disabled": not sequencing.scheduling_execution_enabled,
        "dependency_resolution_disabled": not sequencing.dependency_resolution_enabled,
        "lineage_repair_disabled": not sequencing.lineage_repair_enabled,
        "lineage_inference_disabled": not sequencing.lineage_inference_enabled,
        "orchestration_execution_disabled": not sequencing.orchestration_execution_enabled,
        "refresh_execution_disabled": not sequencing.refresh_execution_enabled,
        "planner_integration_disabled": not sequencing.planner_integration_enabled,
        "production_consumption_disabled": (
            not sequencing.production_consumption_enabled and not sequencing.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not sequencing.runtime_mutation_enabled,
        "remediation_disabled": not sequencing.remediation_enabled,
        "automatic_correction_disabled": not sequencing.automatic_correction_enabled,
        "automatic_rollback_disabled": not sequencing.automatic_rollback_enabled,
        "authorization_disabled": not sequencing.authorization_enabled,
        "approval_disabled": not sequencing.approval_enabled,
        "ranking_disabled": not sequencing.ranking_enabled,
        "scoring_disabled": not sequencing.scoring_enabled,
        "selection_disabled": not sequencing.selection_enabled,
        "operational_execution_disabled": not sequencing.operational_execution_enabled,
        "hidden_sequence_execution_absent": not sequencing.hidden_sequence_execution_enabled,
        "implicit_execution_pathway_absent": not sequencing.implicit_execution_pathway_enabled,
    }


def build_coordination_sequencing_diagnostics(
    sequencing: CoordinationSequencingIntelligence | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source = sequencing or default_coordination_sequencing_intelligence(source_manifest, source_graph, source_lineage)
    visibility = validate_coordination_sequence_visibility(source)
    ordering = validate_non_executable_sequence_ordering(source)
    manifest_compatibility = validate_coordination_manifest_sequence_compatibility(source, source_manifest)
    graph_compatibility = validate_coordination_dependency_graph_sequence_compatibility(
        source,
        source_graph,
        source_manifest,
    )
    lineage_compatibility = validate_coordination_lineage_chain_sequence_compatibility(
        source,
        source_lineage,
        source_graph,
        source_manifest,
    )
    non_execution = validate_coordination_sequencing_non_execution(source)
    enabled_flags = enabled_coordination_sequencing_capability_flags(source)
    return {
        "sequencing_hash": hash_coordination_sequencing_intelligence(source),
        "step_hashes": [hash_sequence_step_identity(step) for step in source.step_identities],
        "manifest_sequence_hashes": [
            hash_manifest_sequence_reference(reference) for reference in source.manifest_sequence_references
        ],
        "dependency_graph_sequence_hashes": [
            hash_dependency_graph_sequence_reference(reference)
            for reference in source.dependency_graph_sequence_references
        ],
        "lineage_sequence_hashes": [
            hash_lineage_sequence_reference(reference) for reference in source.lineage_sequence_references
        ],
        "sequence_record_hashes": [
            hash_coordination_sequence_record(record) for record in source.sequence_records
        ],
        "ordering_visibility_hash": hash_non_executable_sequence_ordering_visibility(source.ordering_visibility),
        "blocked_visibility_hash": hash_sequence_state_visibility(source.blocked_sequence_visibility),
        "prohibited_visibility_hash": hash_sequence_state_visibility(source.prohibited_sequence_visibility),
        "unsupported_visibility_hash": hash_sequence_state_visibility(source.unsupported_sequence_visibility),
        "stale_visibility_hash": hash_sequence_state_visibility(source.stale_sequence_visibility),
        "missing_visibility_hash": hash_sequence_state_visibility(source.missing_sequence_visibility),
        "conflicting_visibility_hash": hash_sequence_state_visibility(source.conflicting_sequence_visibility),
        "sequence_visibility_validation": visibility,
        "sequence_ordering_validation": ordering,
        "manifest_sequence_compatibility_validation": manifest_compatibility,
        "dependency_graph_sequence_compatibility_validation": graph_compatibility,
        "lineage_chain_sequence_compatibility_validation": lineage_compatibility,
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
        "fail_visible_sequence_record_count": len(visibility["fail_visible_record_ids"]),
    }
