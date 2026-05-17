"""Deterministic validation for v3.9 transition foundations.

Validation produces fail-visible evidence only. It does not correct missing
references, infer provenance, approve transitions, or execute orchestration
behavior.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .transition_foundation_continuity import TRANSITION_CONTINUITY_TYPES
from .transition_foundation_hashing import hash_v3_9_transition_foundation
from .transition_foundation_models import (
    FAIL_VISIBLE_TRANSITION_CLASSIFICATIONS,
    TRANSITION_CLASSIFICATION_BLOCKED,
    TRANSITION_CLASSIFICATION_INCOMPLETE,
    TRANSITION_CLASSIFICATION_PROHIBITED,
    TRANSITION_CLASSIFICATION_SUPPORTED,
    TRANSITION_CLASSIFICATION_UNKNOWN,
    TRANSITION_CLASSIFICATION_UNSUPPORTED,
    TRANSITION_CLASSIFICATIONS,
    TRANSITION_VISIBILITY_FAIL_VISIBLE,
    TransitionFoundation,
    V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED,
    V3_9_TRANSITION_FOUNDATION_STATUS_STABLE,
)
from .transition_foundation_serialization import serialize_v3_9_transition_foundation


def validate_v3_9_transition_serialization_stability(
    foundation: TransitionFoundation,
) -> dict[str, Any]:
    first = serialize_v3_9_transition_foundation(foundation)
    second = serialize_v3_9_transition_foundation(foundation)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_9_transition_foundations",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_9_transition_hash_stability(foundation: TransitionFoundation) -> dict[str, Any]:
    first = hash_v3_9_transition_foundation(foundation)
    second = hash_v3_9_transition_foundation(foundation)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_9_transition_foundations",
    }


def count_v3_9_transition_classifications(foundation: TransitionFoundation) -> dict[str, int]:
    counts = Counter(state.classification for state in foundation.state_references)
    return {classification: counts.get(classification, 0) for classification in TRANSITION_CLASSIFICATIONS}


def validate_v3_9_transition_foundation_guarantees(
    foundation: TransitionFoundation,
) -> dict[str, Any]:
    serialization = validate_v3_9_transition_serialization_stability(foundation)
    hashing = validate_v3_9_transition_hash_stability(foundation)
    classification_counts = count_v3_9_transition_classifications(foundation)
    invalid_transition_state_count = sum(
        1 for state in foundation.state_references if state.classification not in TRANSITION_CLASSIFICATIONS
    )
    fail_visible_non_ready_state_count = sum(
        1
        for state in foundation.state_references
        if state.classification in FAIL_VISIBLE_TRANSITION_CLASSIFICATIONS
        and state.visibility_status == TRANSITION_VISIBILITY_FAIL_VISIBLE
        and state.fail_visible
        and not state.hidden
        and not state.silently_coerced
        and not state.fallback_applied
    )
    hidden_non_ready_state_count = sum(
        1
        for state in foundation.state_references
        if state.classification in FAIL_VISIBLE_TRANSITION_CLASSIFICATIONS and (state.hidden or not state.fail_visible)
    )
    missing_state_provenance_count = sum(1 for state in foundation.state_references if not state.provenance_reference_ids)
    missing_state_continuity_count = sum(1 for state in foundation.state_references if not state.continuity_reference_ids)
    missing_reference_provenance_count = sum(
        1 for reference in foundation.transition_references if not reference.provenance_reference_ids
    )
    missing_provenance_reference_count = (
        missing_state_provenance_count
        + missing_reference_provenance_count
        + sum(1 for record in foundation.evidence_records if not record.provenance_reference_ids)
        + sum(1 for reference in foundation.continuity_references if not reference.provenance_reference_ids)
        + sum(1 for reference in foundation.provenance_references if not reference.originating_evidence_ids)
    )
    invalid_continuity_chain_count = sum(
        1
        for chain in foundation.continuity_chains
        if not chain.immutable_chain
        or not chain.continuity_reference_ids
        or not chain.provenance_reference_ids
        or chain.chain_executable
        or chain.traversal_enabled
        or chain.routing_enabled
        or chain.scheduling_enabled
        or chain.dispatch_enabled
        or chain.hidden_transition_enabled
    )
    invalid_continuity_reference_count = sum(
        1
        for reference in foundation.continuity_references
        if reference.continuity_type not in TRANSITION_CONTINUITY_TYPES
        or not reference.immutable_chain
        or not reference.continuity_preserved
        or not reference.preserved_reference_ids
        or not reference.evidence_reference_ids
        or reference.hidden
        or not reference.fail_visible
        or reference.runtime_replay_enabled
        or reference.rollback_execution_enabled
    )
    incomplete_evidence_reference_count = sum(
        1
        for record in foundation.evidence_records
        if not record.immutable_evidence_record
        or not record.provenance_reference_ids
        or not record.continuity_reference_ids
        or not record.replay_reference_ids
        or not record.rollback_reference_ids
        or not record.deterministic_hash_reference
        or not record.replay_safe
        or not record.rollback_safe
        or not record.provenance_preserved
        or not record.non_executable
        or record.runtime_mutation_enabled
        or record.execution_behavior_enabled
    )
    invalid_provenance_reference_count = sum(
        1
        for reference in foundation.provenance_references
        if not reference.provenance_preserved
        or not reference.no_inferred_provenance
        or reference.inferred_provenance_allowed
        or not reference.source_coordination_state_id
        or not reference.destination_coordination_state_id
        or not reference.originating_evidence_ids
        or not reference.transition_lineage_ids
        or not reference.continuity_chain_reference_ids
        or not reference.deterministic_hash_reference
        or reference.hidden
        or not reference.fail_visible
    )
    execution_boundary_violation_count = _execution_boundary_violation_count(foundation)
    validation_error_count = sum(
        (
            invalid_transition_state_count,
            hidden_non_ready_state_count,
            missing_provenance_reference_count,
            missing_state_continuity_count,
            invalid_continuity_chain_count,
            invalid_continuity_reference_count,
            incomplete_evidence_reference_count,
            invalid_provenance_reference_count,
            execution_boundary_violation_count,
            0 if foundation.non_executable else 1,
            0 if foundation.transition_modeling_only else 1,
        )
    )
    return {
        "validation_status": (
            V3_9_TRANSITION_FOUNDATION_STATUS_STABLE
            if validation_error_count == 0
            else V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED
        ),
        "valid": validation_error_count == 0,
        "validation_error_count": validation_error_count,
        "transition_reference_count": len(foundation.transition_references),
        "state_reference_count": len(foundation.state_references),
        "provenance_reference_count": len(foundation.provenance_references),
        "continuity_reference_count": len(foundation.continuity_references),
        "continuity_chain_count": len(foundation.continuity_chains),
        "evidence_record_count": len(foundation.evidence_records),
        "supported_state_count": classification_counts[TRANSITION_CLASSIFICATION_SUPPORTED],
        "unsupported_state_count": classification_counts[TRANSITION_CLASSIFICATION_UNSUPPORTED],
        "prohibited_state_count": classification_counts[TRANSITION_CLASSIFICATION_PROHIBITED],
        "unknown_state_count": classification_counts[TRANSITION_CLASSIFICATION_UNKNOWN],
        "incomplete_state_count": classification_counts[TRANSITION_CLASSIFICATION_INCOMPLETE],
        "blocked_state_count": classification_counts[TRANSITION_CLASSIFICATION_BLOCKED],
        "fail_visible_non_ready_state_count": fail_visible_non_ready_state_count,
        "hidden_non_ready_state_count": hidden_non_ready_state_count,
        "invalid_transition_state_count": invalid_transition_state_count,
        "missing_provenance_reference_count": missing_provenance_reference_count,
        "missing_state_continuity_count": missing_state_continuity_count,
        "invalid_continuity_chain_count": invalid_continuity_chain_count,
        "invalid_continuity_reference_count": invalid_continuity_reference_count,
        "incomplete_evidence_reference_count": incomplete_evidence_reference_count,
        "invalid_provenance_reference_count": invalid_provenance_reference_count,
        "execution_boundary_violation_count": execution_boundary_violation_count,
        "deterministic_serialization_verified": serialization["stable"],
        "deterministic_hashing_verified": hashing["stable"],
        "continuity_preserved": invalid_continuity_chain_count == 0 and invalid_continuity_reference_count == 0,
        "provenance_preserved": invalid_provenance_reference_count == 0 and missing_provenance_reference_count == 0,
        "replay_safe": all(reference.replay_safe for reference in foundation.continuity_references)
        and all(record.replay_safe for record in foundation.evidence_records),
        "rollback_safe": all(reference.rollback_safe for reference in foundation.continuity_references)
        and all(record.rollback_safe for record in foundation.evidence_records),
        "immutable_evidence_records": all(record.immutable_evidence_record for record in foundation.evidence_records),
        "immutable_continuity_chains": all(chain.immutable_chain for chain in foundation.continuity_chains),
        "non_execution_confirmation": execution_boundary_violation_count == 0 and foundation.non_executable,
        "no_inferred_provenance": all(reference.no_inferred_provenance for reference in foundation.provenance_references),
        "no_silent_fallback": not foundation.silent_fallback_enabled
        and all(not state.fallback_applied for state in foundation.state_references),
        "no_hidden_correction": not foundation.hidden_correction_enabled,
        "classification_counts": classification_counts,
    }


def _execution_boundary_violation_count(foundation: TransitionFoundation) -> int:
    direct_flags = (
        foundation.coordination_transition_execution_enabled,
        foundation.orchestration_execution_enabled,
        foundation.orchestration_traversal_enabled,
        foundation.routing_enabled,
        foundation.scheduling_enabled,
        foundation.dispatch_enabled,
        foundation.runtime_orchestration_engine_enabled,
        foundation.runtime_state_machine_enabled,
        foundation.transition_execution_handler_enabled,
        foundation.dispatch_pipeline_enabled,
        foundation.orchestration_evaluator_enabled,
        foundation.optimization_enabled,
        foundation.recommendation_enabled,
        foundation.ranking_enabled,
        foundation.scoring_enabled,
        foundation.selection_enabled,
        foundation.authorization_enabled,
        foundation.autonomous_orchestration_enabled,
        foundation.hidden_mutation_enabled,
        foundation.runtime_mutation_enabled,
        foundation.implicit_transition_approval_enabled,
        foundation.silent_fallback_enabled,
        foundation.hidden_correction_enabled,
        foundation.inferred_orchestration_action_enabled,
        foundation.production_execution_pathway_enabled,
        foundation.callable_orchestration_flow_enabled,
    )
    chain_flags = tuple(
        flag
        for chain in foundation.continuity_chains
        for flag in (
            chain.chain_executable,
            chain.traversal_enabled,
            chain.routing_enabled,
            chain.scheduling_enabled,
            chain.dispatch_enabled,
            chain.hidden_transition_enabled,
        )
    )
    evidence_flags = tuple(
        flag
        for record in foundation.evidence_records
        for flag in (record.runtime_mutation_enabled, record.execution_behavior_enabled)
    )
    return sum(1 for value in (*direct_flags, *chain_flags, *evidence_flags) if value)
