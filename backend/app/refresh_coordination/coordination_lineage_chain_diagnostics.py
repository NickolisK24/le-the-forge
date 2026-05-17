"""Diagnostics for v4.2 coordination lineage chain governance."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import (
    CoordinationDependencyGraph,
    default_coordination_dependency_graph,
)
from .coordination_lineage_chain_hashing import (
    hash_conflicting_lineage_visibility,
    hash_coordination_lineage_chain,
    hash_coordination_lineage_chain_record,
    hash_dependency_graph_lineage_chain_reference,
    hash_lineage_predecessor_reference,
    hash_lineage_source_reference,
    hash_lineage_successor_reference,
    hash_manifest_lineage_chain_reference,
    hash_missing_lineage_visibility,
    hash_prohibited_lineage_mutation_visibility,
    hash_stale_lineage_visibility,
    hash_unsupported_lineage_transition_visibility,
)
from .coordination_lineage_chain_models import (
    FAIL_VISIBLE_LINEAGE_STATES,
    LINEAGE_STATE_CONFLICTING,
    LINEAGE_STATE_MISSING,
    LINEAGE_STATE_PROHIBITED_MUTATION,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_UNSUPPORTED_TRANSITION,
    LINEAGE_STATES,
    CoordinationLineageChain,
    CoordinationLineageChainRecord,
    default_coordination_lineage_chain,
)
from .coordination_lineage_chain_serialization import serialize_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "lineage_mutation_enabled",
    "dependency_resolution_enabled",
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
    "hidden_lineage_resolution_enabled",
    "hidden_fallback_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_lineage_states(records: tuple[CoordinationLineageChainRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in LINEAGE_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.lineage_state in counts:
            counts[record.lineage_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_coordination_lineage_record_ids(
    records: tuple[CoordinationLineageChainRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        record.record_id
        for record in records
        if record.lineage_state in FAIL_VISIBLE_LINEAGE_STATES and record.fail_visible
    )


def aggregate_stale_lineage_states(chain: CoordinationLineageChain) -> tuple[str, ...]:
    return tuple(record.record_id for record in chain.records if record.lineage_state == LINEAGE_STATE_STALE)


def aggregate_missing_lineage_states(chain: CoordinationLineageChain) -> tuple[str, ...]:
    return tuple(record.record_id for record in chain.records if record.lineage_state == LINEAGE_STATE_MISSING)


def aggregate_conflicting_lineage_states(chain: CoordinationLineageChain) -> tuple[str, ...]:
    return tuple(record.record_id for record in chain.records if record.lineage_state == LINEAGE_STATE_CONFLICTING)


def aggregate_prohibited_lineage_mutation_states(chain: CoordinationLineageChain) -> tuple[str, ...]:
    return tuple(
        record.record_id for record in chain.records if record.lineage_state == LINEAGE_STATE_PROHIBITED_MUTATION
    )


def aggregate_unsupported_lineage_transition_states(chain: CoordinationLineageChain) -> tuple[str, ...]:
    return tuple(
        record.record_id for record in chain.records if record.lineage_state == LINEAGE_STATE_UNSUPPORTED_TRANSITION
    )


def coordination_lineage_chain_capability_flags(chain: CoordinationLineageChain) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        chain,
        chain.identity,
        chain.stale_lineage_visibility,
        chain.missing_lineage_visibility,
        chain.conflicting_lineage_visibility,
        chain.prohibited_lineage_mutation_visibility,
        chain.unsupported_lineage_transition_visibility,
        chain.governance_visibility,
        *chain.source_references,
        *chain.predecessor_references,
        *chain.successor_references,
        *chain.manifest_lineage_references,
        *chain.dependency_graph_lineage_references,
        *chain.records,
        *chain.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_lineage_chain_capability_flags(chain: CoordinationLineageChain) -> dict[str, bool]:
    return {key: value for key, value in coordination_lineage_chain_capability_flags(chain).items() if value}


def coordination_lineage_chains_equal(left: CoordinationLineageChain, right: CoordinationLineageChain) -> bool:
    return serialize_coordination_lineage_chain(left) == serialize_coordination_lineage_chain(right)


def validate_coordination_lineage_chain_visibility(chain: CoordinationLineageChain) -> dict[str, object]:
    stale_record_ids = aggregate_stale_lineage_states(chain)
    missing_record_ids = aggregate_missing_lineage_states(chain)
    conflicting_record_ids = aggregate_conflicting_lineage_states(chain)
    prohibited_record_ids = aggregate_prohibited_lineage_mutation_states(chain)
    unsupported_record_ids = aggregate_unsupported_lineage_transition_states(chain)
    stale_visible = set(stale_record_ids).issubset(set(chain.stale_lineage_visibility.stale_record_ids))
    missing_visible = set(missing_record_ids).issubset(set(chain.missing_lineage_visibility.missing_record_ids))
    conflicting_visible = set(conflicting_record_ids).issubset(
        set(chain.conflicting_lineage_visibility.conflicting_record_ids)
    )
    prohibited_visible = set(prohibited_record_ids).issubset(
        set(chain.prohibited_lineage_mutation_visibility.prohibited_record_ids)
    )
    unsupported_visible = set(unsupported_record_ids).issubset(
        set(chain.unsupported_lineage_transition_visibility.unsupported_record_ids)
    )
    invalid_record_ids = tuple(record.record_id for record in chain.records if record.lineage_state not in LINEAGE_STATES)
    hidden_count = sum(
        1
        for item in (
            *chain.source_references,
            *chain.predecessor_references,
            *chain.successor_references,
            *chain.records,
            chain.prohibited_lineage_mutation_visibility,
            chain.unsupported_lineage_transition_visibility,
            *chain.diagnostics,
        )
        if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            chain.stale_lineage_visibility,
            chain.missing_lineage_visibility,
            chain.conflicting_lineage_visibility,
            chain.prohibited_lineage_mutation_visibility,
            chain.unsupported_lineage_transition_visibility,
            *chain.records,
            *chain.diagnostics,
        )
        if getattr(item, "lineage_repair_enabled", False)
        or getattr(item, "lineage_inference_enabled", False)
        or getattr(item, "lineage_mutation_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
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
            stale_visible
            and missing_visible
            and conflicting_visible
            and prohibited_visible
            and unsupported_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "lineage_state_counts": count_coordination_lineage_states(chain.records),
        "fail_visible_record_ids": fail_visible_coordination_lineage_record_ids(chain.records),
        "stale_record_ids": stale_record_ids,
        "missing_record_ids": missing_record_ids,
        "conflicting_record_ids": conflicting_record_ids,
        "prohibited_record_ids": prohibited_record_ids,
        "unsupported_record_ids": unsupported_record_ids,
        "stale_lineage_visible": stale_visible,
        "missing_lineage_visible": missing_visible,
        "conflicting_lineage_visible": conflicting_visible,
        "prohibited_lineage_mutation_visible": prohibited_visible,
        "unsupported_lineage_transition_visible": unsupported_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in chain.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in chain.diagnostics),
    }


def validate_coordination_lineage_chain_continuity(chain: CoordinationLineageChain) -> dict[str, object]:
    record_ids = {record.record_id for record in chain.records}
    source_ids = {reference.source_reference_id for reference in chain.source_references}
    predecessor_ids = {reference.predecessor_reference_id for reference in chain.predecessor_references}
    successor_ids = {reference.successor_reference_id for reference in chain.successor_references}
    manifest_reference_ids = {
        reference.manifest_lineage_reference_id for reference in chain.manifest_lineage_references
    }
    graph_reference_ids = {
        reference.dependency_graph_lineage_reference_id for reference in chain.dependency_graph_lineage_references
    }
    missing_source_refs = tuple(
        sorted(record.source_reference_id for record in chain.records if record.source_reference_id not in source_ids)
    )
    missing_predecessor_refs = tuple(
        sorted(
            record.predecessor_reference_id
            for record in chain.records
            if record.predecessor_reference_id not in predecessor_ids
        )
    )
    missing_successor_refs = tuple(
        sorted(
            record.successor_reference_id for record in chain.records if record.successor_reference_id not in successor_ids
        )
    )
    missing_manifest_refs = tuple(
        sorted(
            record.manifest_lineage_reference_id
            for record in chain.records
            if record.manifest_lineage_reference_id not in manifest_reference_ids
        )
    )
    missing_graph_refs = tuple(
        sorted(
            record.dependency_graph_lineage_reference_id
            for record in chain.records
            if record.dependency_graph_lineage_reference_id not in graph_reference_ids
        )
    )
    missing_record_refs = tuple(
        sorted(
            reference
            for manifest_ref in chain.manifest_lineage_references
            for reference in manifest_ref.record_references
            if reference not in record_ids
        )
        + sorted(
            reference
            for graph_ref in chain.dependency_graph_lineage_references
            for reference in graph_ref.record_references
            if reference not in record_ids
        )
    )
    corrective_count = sum(
        1
        for item in (
            *chain.source_references,
            *chain.predecessor_references,
            *chain.successor_references,
            *chain.manifest_lineage_references,
            *chain.dependency_graph_lineage_references,
            *chain.records,
        )
        if getattr(item, "lineage_repair_enabled", False)
        or getattr(item, "lineage_inference_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
    )
    return {
        "valid": (
            len(chain.records) > 0
            and len(missing_source_refs) == 0
            and len(missing_predecessor_refs) == 0
            and len(missing_successor_refs) == 0
            and len(missing_manifest_refs) == 0
            and len(missing_graph_refs) == 0
            and len(missing_record_refs) == 0
            and all(reference.lineage_continuity_preserved for reference in chain.manifest_lineage_references)
            and all(reference.provenance_continuity_preserved for reference in chain.manifest_lineage_references)
            and all(reference.lineage_continuity_preserved for reference in chain.dependency_graph_lineage_references)
            and all(reference.dependency_graph_compatibility_preserved for reference in chain.dependency_graph_lineage_references)
            and corrective_count == 0
        ),
        "lineage_reference": chain.identity.lineage_reference,
        "continuity_reference": chain.identity.continuity_reference,
        "record_count": len(chain.records),
        "missing_source_references": missing_source_refs,
        "missing_predecessor_references": missing_predecessor_refs,
        "missing_successor_references": missing_successor_refs,
        "missing_manifest_lineage_references": missing_manifest_refs,
        "missing_dependency_graph_lineage_references": missing_graph_refs,
        "missing_record_references": missing_record_refs,
        "lineage_continuity_preserved": all(
            reference.lineage_continuity_preserved
            for reference in (*chain.manifest_lineage_references, *chain.dependency_graph_lineage_references)
        ),
        "provenance_continuity_preserved": all(
            reference.provenance_continuity_preserved for reference in chain.manifest_lineage_references
        ),
        "dependency_graph_compatibility_preserved": all(
            reference.dependency_graph_compatibility_preserved
            for reference in chain.dependency_graph_lineage_references
        ),
        "replay_safe": chain.replay_safe,
        "rollback_safe": chain.rollback_safe,
        "provenance_safe": chain.provenance_safe,
        "lineage_safe": chain.lineage_safe,
        "corrective_lineage_count": corrective_count,
    }


def validate_coordination_manifest_lineage_compatibility(
    chain: CoordinationLineageChain,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    reference_matches = any(
        reference.manifest_reference == source.identity.manifest_id
        and reference.manifest_hash_reference == manifest_hash
        for reference in chain.manifest_lineage_references
    )
    return {
        "valid": (
            chain.identity.source_manifest_reference == source.identity.manifest_id
            and chain.compatibility_manifest_reference == source.identity.manifest_id
            and chain.identity.source_manifest_hash_reference == manifest_hash
            and reference_matches
        ),
        "chain_source_manifest_reference": chain.identity.source_manifest_reference,
        "chain_compatibility_manifest_reference": chain.compatibility_manifest_reference,
        "manifest_reference": source.identity.manifest_id,
        "source_manifest_hash_reference": chain.identity.source_manifest_hash_reference,
        "expected_manifest_hash": manifest_hash,
        "manifest_hash_matches": chain.identity.source_manifest_hash_reference == manifest_hash,
        "manifest_lineage_reference_matches": reference_matches,
    }


def validate_coordination_dependency_graph_lineage_compatibility(
    chain: CoordinationLineageChain,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    graph_hash = hash_coordination_dependency_graph(source_graph)
    reference_matches = any(
        reference.dependency_graph_reference == source_graph.identity.graph_id
        and reference.dependency_graph_hash_reference == graph_hash
        for reference in chain.dependency_graph_lineage_references
    )
    return {
        "valid": (
            chain.identity.source_dependency_graph_reference == source_graph.identity.graph_id
            and chain.compatibility_dependency_graph_reference == source_graph.identity.graph_id
            and chain.identity.source_dependency_graph_hash_reference == graph_hash
            and reference_matches
        ),
        "chain_source_dependency_graph_reference": chain.identity.source_dependency_graph_reference,
        "chain_compatibility_dependency_graph_reference": chain.compatibility_dependency_graph_reference,
        "dependency_graph_reference": source_graph.identity.graph_id,
        "source_dependency_graph_hash_reference": chain.identity.source_dependency_graph_hash_reference,
        "expected_dependency_graph_hash": graph_hash,
        "dependency_graph_hash_matches": chain.identity.source_dependency_graph_hash_reference == graph_hash,
        "dependency_graph_lineage_reference_matches": reference_matches,
    }


def validate_coordination_lineage_chain_non_execution(chain: CoordinationLineageChain) -> dict[str, object]:
    enabled_flags = enabled_coordination_lineage_chain_capability_flags(chain)
    return {
        "valid": len(enabled_flags) == 0 and chain.non_executable and chain.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": chain.non_executable,
        "descriptive_only": chain.descriptive_only,
        "lineage_repair_disabled": not chain.lineage_repair_enabled,
        "lineage_inference_disabled": not chain.lineage_inference_enabled,
        "lineage_mutation_disabled": not chain.lineage_mutation_enabled,
        "dependency_resolution_disabled": not chain.dependency_resolution_enabled,
        "orchestration_execution_disabled": not chain.orchestration_execution_enabled,
        "refresh_execution_disabled": not chain.refresh_execution_enabled,
        "planner_integration_disabled": not chain.planner_integration_enabled,
        "production_consumption_disabled": (
            not chain.production_consumption_enabled and not chain.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not chain.runtime_mutation_enabled,
        "remediation_disabled": not chain.remediation_enabled,
        "automatic_correction_disabled": not chain.automatic_correction_enabled,
        "automatic_rollback_disabled": not chain.automatic_rollback_enabled,
        "authorization_disabled": not chain.authorization_enabled,
        "approval_disabled": not chain.approval_enabled,
        "ranking_disabled": not chain.ranking_enabled,
        "scoring_disabled": not chain.scoring_enabled,
        "selection_disabled": not chain.selection_enabled,
        "operational_execution_disabled": not chain.operational_execution_enabled,
        "hidden_lineage_resolution_absent": not chain.hidden_lineage_resolution_enabled,
        "implicit_execution_pathway_absent": not chain.implicit_execution_pathway_enabled,
    }


def build_coordination_lineage_chain_diagnostics(
    chain: CoordinationLineageChain | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source = chain or default_coordination_lineage_chain(source_manifest, source_graph)
    visibility = validate_coordination_lineage_chain_visibility(source)
    continuity = validate_coordination_lineage_chain_continuity(source)
    manifest_compatibility = validate_coordination_manifest_lineage_compatibility(source, source_manifest)
    graph_compatibility = validate_coordination_dependency_graph_lineage_compatibility(
        source,
        source_graph,
        source_manifest,
    )
    non_execution = validate_coordination_lineage_chain_non_execution(source)
    enabled_flags = enabled_coordination_lineage_chain_capability_flags(source)
    return {
        "chain_hash": hash_coordination_lineage_chain(source),
        "source_reference_hashes": [
            hash_lineage_source_reference(reference) for reference in source.source_references
        ],
        "predecessor_reference_hashes": [
            hash_lineage_predecessor_reference(reference) for reference in source.predecessor_references
        ],
        "successor_reference_hashes": [
            hash_lineage_successor_reference(reference) for reference in source.successor_references
        ],
        "manifest_lineage_reference_hashes": [
            hash_manifest_lineage_chain_reference(reference) for reference in source.manifest_lineage_references
        ],
        "dependency_graph_lineage_reference_hashes": [
            hash_dependency_graph_lineage_chain_reference(reference)
            for reference in source.dependency_graph_lineage_references
        ],
        "record_hashes": [hash_coordination_lineage_chain_record(record) for record in source.records],
        "stale_visibility_hash": hash_stale_lineage_visibility(source.stale_lineage_visibility),
        "missing_visibility_hash": hash_missing_lineage_visibility(source.missing_lineage_visibility),
        "conflicting_visibility_hash": hash_conflicting_lineage_visibility(source.conflicting_lineage_visibility),
        "prohibited_mutation_visibility_hash": hash_prohibited_lineage_mutation_visibility(
            source.prohibited_lineage_mutation_visibility
        ),
        "unsupported_transition_visibility_hash": hash_unsupported_lineage_transition_visibility(
            source.unsupported_lineage_transition_visibility
        ),
        "lineage_visibility_validation": visibility,
        "lineage_continuity_validation": continuity,
        "manifest_lineage_compatibility_validation": manifest_compatibility,
        "dependency_graph_lineage_compatibility_validation": graph_compatibility,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "stale_record_ids": visibility["stale_record_ids"],
        "missing_record_ids": visibility["missing_record_ids"],
        "conflicting_record_ids": visibility["conflicting_record_ids"],
        "prohibited_record_ids": visibility["prohibited_record_ids"],
        "unsupported_record_ids": visibility["unsupported_record_ids"],
        "diagnostic_categories": tuple(sorted(set(diagnostic.category for diagnostic in source.diagnostics))),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_diagnostic_count": sum(1 for diagnostic in source.diagnostics if diagnostic.fail_visible),
        "diagnostics_are_descriptive_only": all(diagnostic.descriptive_only for diagnostic in source.diagnostics),
        "fail_visible_lineage_record_count": len(visibility["fail_visible_record_ids"]),
    }
