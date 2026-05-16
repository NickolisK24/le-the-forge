from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_foundation_models import (
    V3_8_COORDINATION_FOUNDATION_STATUS_STABLE,
    default_v3_8_coordination_foundation,
    export_v3_8_coordination_foundation,
    hash_v3_8_coordination_foundation,
    serialize_v3_8_coordination_foundation,
    validate_v3_8_coordination_foundation_guarantees,
    validate_v3_8_coordination_hash_stability,
    validate_v3_8_coordination_serialization_stability,
)
from runtime_coordination.coordination_identity_models import (
    V3_8_COORDINATION_FOUNDATION_PHASE_ID,
    V3_8_COORDINATION_SCHEMA_VERSION,
    build_v3_8_coordination_identity,
    coordination_boundary_key,
    coordination_identity_key,
    coordination_reference_key,
    identity_values_are_unique,
)
from runtime_coordination.coordination_relationship_models import (
    coordination_relationship_chain_key,
    coordination_relationship_key,
)
from scripts.report_v3_8_coordination_foundations import build_v3_8_coordination_foundations_report


def test_v3_8_coordination_foundation_models_are_immutable_and_non_executable():
    foundation = default_v3_8_coordination_foundation()

    with pytest.raises(FrozenInstanceError):
        foundation.coordination_execution_enabled = True

    assert foundation.identity.schema_version == V3_8_COORDINATION_SCHEMA_VERSION
    assert foundation.identity.phase_id == V3_8_COORDINATION_FOUNDATION_PHASE_ID
    assert foundation.planning_coordination_only is True
    assert foundation.non_executable is True
    assert foundation.coordination_execution_enabled is False
    assert foundation.orchestration_execution_enabled is False
    assert foundation.execution_authorization_enabled is False
    assert foundation.routing_enabled is False
    assert foundation.scheduling_enabled is False
    assert foundation.dispatch_enabled is False
    assert foundation.traversal_execution_enabled is False
    assert foundation.graph_traversal_execution_enabled is False
    assert foundation.runtime_path_selection_enabled is False
    assert foundation.recommendation_enabled is False
    assert foundation.optimization_enabled is False
    assert foundation.autonomous_orchestration_enabled is False
    assert foundation.callable_execution_flow_enabled is False
    assert foundation.persistent_runtime_mutation_enabled is False
    assert foundation.persistent_runtime_writes_enabled is False
    assert foundation.hidden_state_transition_enabled is False
    assert foundation.silent_fallback_enabled is False
    assert all(not relationship.relationship_executable for relationship in foundation.relationships)
    assert all(not relationship.traversal_enabled for relationship in foundation.relationships)
    assert all(not chain.chain_executable for chain in foundation.relationship_chains)
    assert all(not chain.traversal_execution_enabled for chain in foundation.relationship_chains)


def test_v3_8_coordination_identity_reference_and_relationship_keys_are_stable():
    foundation = default_v3_8_coordination_foundation()
    identity = build_v3_8_coordination_identity("coordination-a")

    assert coordination_identity_key(identity) == (
        "v3_8.orchestration_planning_coordination_foundations.1"
        "|v3_8_coordination_foundations|v3.8|coordination-a"
    )
    assert coordination_reference_key(foundation.coordination_references[0]) == (
        "planning_coordination_reference_only|prior_phase_closeout"
        "|v3_7_closeout_and_v3_8_readiness|v3_8_ref_v3_7_closeout_readiness"
    )
    assert coordination_boundary_key(foundation.coordination_boundaries[0]) == (
        "non_execution|visible|v3_8_non_execution_coordination_boundary"
    )
    assert coordination_relationship_key(foundation.relationships[0]) == (
        "coordination_identity_preserves_references"
        "|v3-8-deterministic-coordination-foundation"
        "|v3_8_coordination_reference_set|v3_8_relationship_identity_to_references"
    )
    assert coordination_relationship_chain_key(foundation.relationship_chains[0]) == (
        "structural_coordination_chain_only|v3_8_coordination_identity_to_rollback_chain|1"
    )
    assert identity_values_are_unique(tuple(reference.reference_id for reference in foundation.coordination_references))


def test_v3_8_coordination_serialization_hashing_and_equality_are_stable():
    first = default_v3_8_coordination_foundation()
    second = default_v3_8_coordination_foundation()

    assert first == second
    assert hash(first) == hash(second)
    assert serialize_v3_8_coordination_foundation(first) == serialize_v3_8_coordination_foundation(second)
    assert hash_v3_8_coordination_foundation(first) == hash_v3_8_coordination_foundation(second)
    assert validate_v3_8_coordination_serialization_stability(first)["stable"] is True
    assert validate_v3_8_coordination_hash_stability(first)["stable"] is True


def test_v3_8_coordination_serialization_sorts_structural_collections():
    foundation = default_v3_8_coordination_foundation()
    reordered = replace(
        foundation,
        metadata=tuple(reversed(foundation.metadata)),
        coordination_references=tuple(reversed(foundation.coordination_references)),
        coordination_boundaries=tuple(reversed(foundation.coordination_boundaries)),
        relationships=tuple(reversed(foundation.relationships)),
        replay_evidence=tuple(reversed(foundation.replay_evidence)),
        rollback_evidence=tuple(reversed(foundation.rollback_evidence)),
        unsupported_states=tuple(reversed(foundation.unsupported_states)),
        prohibited_states=tuple(reversed(foundation.prohibited_states)),
        unknown_states=tuple(reversed(foundation.unknown_states)),
    )

    assert serialize_v3_8_coordination_foundation(foundation) == serialize_v3_8_coordination_foundation(
        reordered
    )
    exported = export_v3_8_coordination_foundation(reordered)
    assert [item["reference_id"] for item in exported["coordination_references"]] == sorted(
        reference.reference_id for reference in foundation.coordination_references
    )
    assert [item["relationship_id"] for item in exported["relationships"]] == [
        relationship.relationship_id for relationship in foundation.relationships
    ]
    assert json.loads(serialize_v3_8_coordination_foundation(foundation))["non_executable"] is True


def test_v3_8_coordination_continuity_provenance_replay_and_rollback_are_preserved():
    foundation = default_v3_8_coordination_foundation()
    validation = validate_v3_8_coordination_foundation_guarantees(foundation)

    assert validation["validation_status"] == V3_8_COORDINATION_FOUNDATION_STATUS_STABLE
    assert validation["valid"] is True
    assert validation["continuity_preserved"] is True
    assert validation["provenance_preserved"] is True
    assert validation["replay_safe"] is True
    assert validation["rollback_safe"] is True
    assert foundation.continuity_state.continuity_preserved is True
    assert foundation.provenance_state.provenance_preserved is True
    assert len(foundation.continuity_state.preserved_reference_ids) == 4
    assert len(foundation.provenance_state.prior_phase_reference_ids) == 3
    assert all(evidence.replay_safe and not evidence.runtime_replay_enabled for evidence in foundation.replay_evidence)
    assert all(
        evidence.rollback_safe and not evidence.rollback_execution_enabled
        for evidence in foundation.rollback_evidence
    )


def test_v3_8_coordination_fail_visible_unsupported_prohibited_and_unknown_states():
    foundation = default_v3_8_coordination_foundation()
    validation = validate_v3_8_coordination_foundation_guarantees(foundation)

    assert validation["unsupported_state_count"] == 3
    assert validation["prohibited_state_count"] == 4
    assert validation["unknown_state_count"] == 2
    assert validation["fail_visible_state_count"] == 9
    assert all(state.fail_visible and not state.hidden for state in foundation.unsupported_states)
    assert all(state.fail_visible and not state.hidden for state in foundation.prohibited_states)
    assert all(state.fail_visible and not state.hidden for state in foundation.unknown_states)
    assert foundation.explainability_state.fail_visible is True
    assert foundation.explainability_state.hidden_state is False
    assert foundation.integrity_state.execution_boundary_violation_ids == ()
    assert foundation.integrity_state.silent_fallback_detected is False
    assert foundation.integrity_state.hidden_transition_detected is False


def test_v3_8_coordination_relationship_continuity_is_deterministic_and_non_executable():
    foundation = default_v3_8_coordination_foundation()
    validation = validate_v3_8_coordination_foundation_guarantees(foundation)
    relationship_ids = tuple(relationship.relationship_id for relationship in foundation.relationships)

    assert validation["relationship_count"] == 6
    assert validation["relationship_chain_count"] == 1
    assert validation["relationship_execution_violation_count"] == 0
    assert validation["chain_execution_violation_count"] == 0
    assert foundation.relationship_chains[0].relationship_ids == relationship_ids
    assert all(relationship.continuity_reference_ids for relationship in foundation.relationships)
    assert all(relationship.provenance_reference_ids for relationship in foundation.relationships)
    assert all(relationship.explainability_reference_ids for relationship in foundation.relationships)
    assert all(relationship.replay_reference_ids for relationship in foundation.relationships)
    assert all(relationship.rollback_reference_ids for relationship in foundation.relationships)


def test_v3_8_coordination_report_contains_required_totals_and_boundaries():
    report = build_v3_8_coordination_foundations_report()

    assert report["summary"]["foundation_status"] == V3_8_COORDINATION_FOUNDATION_STATUS_STABLE
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["continuity_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["explainability_verified"] is True
    assert report["summary"]["integrity_verified"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["source_artifact_totals"]["source_artifact_continuity_preserved"] is True
    assert report["non_execution_guarantees"]["coordination_execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["scheduling_absent"] is True
    assert report["non_execution_guarantees"]["dispatch_absent"] is True
    assert report["non_execution_guarantees"]["traversal_execution_absent"] is True
