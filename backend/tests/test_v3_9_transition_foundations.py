from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_transition.transition_foundation_continuity import (  # noqa: E402
    transition_continuity_chain_key,
    transition_continuity_reference_key,
)
from runtime_transition.transition_foundation_hashing import (  # noqa: E402
    hash_v3_9_transition_continuity_reference,
    hash_v3_9_transition_foundation,
    hash_v3_9_transition_identity,
    hash_v3_9_transition_provenance_reference,
    hash_v3_9_transition_reference,
    hash_v3_9_transition_state_reference,
)
from runtime_transition.transition_foundation_models import (  # noqa: E402
    TRANSITION_CLASSIFICATION_BLOCKED,
    TRANSITION_CLASSIFICATION_INCOMPLETE,
    TRANSITION_CLASSIFICATION_PROHIBITED,
    TRANSITION_CLASSIFICATION_SUPPORTED,
    TRANSITION_CLASSIFICATION_UNKNOWN,
    TRANSITION_CLASSIFICATION_UNSUPPORTED,
    TRANSITION_VISIBILITY_FAIL_VISIBLE,
    V3_9_TRANSITION_FOUNDATION_PHASE_ID,
    V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED,
    V3_9_TRANSITION_FOUNDATION_STATUS_STABLE,
    V3_9_TRANSITION_SCHEMA_VERSION,
    default_v3_9_transition_foundation,
    export_v3_9_transition_foundation,
    identity_values_are_unique,
    transition_identity_key,
    transition_reference_key,
    transition_state_reference_key,
)
from runtime_transition.transition_foundation_provenance import (  # noqa: E402
    transition_provenance_key,
)
from runtime_transition.transition_foundation_serialization import (  # noqa: E402
    serialize_v3_9_transition_foundation,
)
from runtime_transition.transition_foundation_validation import (  # noqa: E402
    count_v3_9_transition_classifications,
    validate_v3_9_transition_foundation_guarantees,
    validate_v3_9_transition_hash_stability,
    validate_v3_9_transition_serialization_stability,
)
from scripts.report_v3_9_transition_foundations import (  # noqa: E402
    build_v3_9_transition_foundations_report,
)


def test_v3_9_transition_foundation_models_are_immutable_and_non_executable():
    foundation = default_v3_9_transition_foundation()

    with pytest.raises(FrozenInstanceError):
        foundation.orchestration_execution_enabled = True

    assert foundation.identity.schema_version == V3_9_TRANSITION_SCHEMA_VERSION
    assert foundation.identity.phase_id == V3_9_TRANSITION_FOUNDATION_PHASE_ID
    assert foundation.non_executable is True
    assert foundation.transition_modeling_only is True
    assert foundation.coordination_transition_execution_enabled is False
    assert foundation.orchestration_execution_enabled is False
    assert foundation.orchestration_traversal_enabled is False
    assert foundation.routing_enabled is False
    assert foundation.scheduling_enabled is False
    assert foundation.dispatch_enabled is False
    assert foundation.runtime_orchestration_engine_enabled is False
    assert foundation.runtime_state_machine_enabled is False
    assert foundation.transition_execution_handler_enabled is False
    assert foundation.dispatch_pipeline_enabled is False
    assert foundation.orchestration_evaluator_enabled is False
    assert foundation.optimization_enabled is False
    assert foundation.recommendation_enabled is False
    assert foundation.ranking_enabled is False
    assert foundation.scoring_enabled is False
    assert foundation.selection_enabled is False
    assert foundation.authorization_enabled is False
    assert foundation.autonomous_orchestration_enabled is False
    assert foundation.hidden_mutation_enabled is False
    assert foundation.runtime_mutation_enabled is False
    assert foundation.implicit_transition_approval_enabled is False
    assert foundation.silent_fallback_enabled is False
    assert foundation.hidden_correction_enabled is False
    assert foundation.inferred_orchestration_action_enabled is False
    assert foundation.production_execution_pathway_enabled is False
    assert foundation.callable_orchestration_flow_enabled is False
    assert all(not chain.chain_executable for chain in foundation.continuity_chains)
    assert all(not chain.traversal_enabled for chain in foundation.continuity_chains)
    assert all(record.non_executable for record in foundation.evidence_records)


def test_v3_9_transition_identity_reference_state_provenance_and_continuity_keys_are_stable():
    foundation = default_v3_9_transition_foundation()

    assert transition_identity_key(foundation.identity) == (
        "v3_9.orchestration_planning_coordination_transition_foundations.1"
        "|v3_9_transition_foundations|v3.9|v3-9-deterministic-coordination-transition-foundation"
    )
    assert transition_reference_key(foundation.transition_references[0]) == (
        "coordination_transition_reference_only|source_coordination_state"
        "|v3_8_closeout_and_v3_9_readiness|v3_9_transition_ref_v3_8_closeout"
    )
    assert transition_state_reference_key(foundation.state_references[0]) == (
        "coordination_transition_state_reference_only|supported"
        "|deterministic_transition_identity_modeling"
        "|v3_9_transition_state_supported_identity_modeling"
    )
    assert transition_provenance_key(foundation.provenance_references[0]) == (
        "coordination_transition_provenance_reference_only"
        "|v3_8_coordination_closeout_ready_for_v3_9"
        "|v3_9_transition_foundations"
        "|v3_9_transition_foundation_provenance"
    )
    assert transition_continuity_reference_key(foundation.continuity_references[0]) == (
        "coordination_transition_continuity_reference_only"
        "|replay_continuity"
        "|v3_9_transition_replay_continuity"
    )
    assert transition_continuity_chain_key(foundation.continuity_chains[0]) == (
        "coordination_transition_continuity_chain_only"
        "|v3_9_transition_foundation_continuity_chain|1"
    )
    assert identity_values_are_unique(tuple(reference.reference_id for reference in foundation.transition_references))


def test_v3_9_transition_serialization_hashing_and_equality_are_stable():
    first = default_v3_9_transition_foundation()
    second = default_v3_9_transition_foundation()

    assert first == second
    assert hash(first) == hash(second)
    assert serialize_v3_9_transition_foundation(first) == serialize_v3_9_transition_foundation(second)
    assert hash_v3_9_transition_foundation(first) == hash_v3_9_transition_foundation(second)
    assert validate_v3_9_transition_serialization_stability(first)["stable"] is True
    assert validate_v3_9_transition_hash_stability(first)["stable"] is True

    assert hash_v3_9_transition_identity(first.identity) == hash_v3_9_transition_identity(second.identity)
    assert hash_v3_9_transition_reference(first.transition_references[0]) == hash_v3_9_transition_reference(
        second.transition_references[0]
    )
    assert hash_v3_9_transition_state_reference(first.state_references[0]) == hash_v3_9_transition_state_reference(
        second.state_references[0]
    )
    assert hash_v3_9_transition_provenance_reference(
        first.provenance_references[0]
    ) == hash_v3_9_transition_provenance_reference(second.provenance_references[0])
    assert hash_v3_9_transition_continuity_reference(
        first.continuity_references[0]
    ) == hash_v3_9_transition_continuity_reference(second.continuity_references[0])


def test_v3_9_transition_serialization_sorts_structural_collections():
    foundation = default_v3_9_transition_foundation()
    reordered = replace(
        foundation,
        transition_references=tuple(reversed(foundation.transition_references)),
        state_references=tuple(reversed(foundation.state_references)),
        provenance_references=tuple(reversed(foundation.provenance_references)),
        continuity_references=tuple(reversed(foundation.continuity_references)),
        continuity_chains=tuple(reversed(foundation.continuity_chains)),
        evidence_records=tuple(reversed(foundation.evidence_records)),
    )

    assert serialize_v3_9_transition_foundation(foundation) == serialize_v3_9_transition_foundation(reordered)
    assert hash_v3_9_transition_foundation(foundation) == hash_v3_9_transition_foundation(reordered)
    exported = export_v3_9_transition_foundation(reordered)
    assert [item["reference_id"] for item in exported["transition_references"]] == sorted(
        reference.reference_id for reference in foundation.transition_references
    )
    assert [item["classification"] for item in exported["state_references"]] == [
        TRANSITION_CLASSIFICATION_SUPPORTED,
        TRANSITION_CLASSIFICATION_UNSUPPORTED,
        TRANSITION_CLASSIFICATION_PROHIBITED,
        TRANSITION_CLASSIFICATION_UNKNOWN,
        TRANSITION_CLASSIFICATION_INCOMPLETE,
        TRANSITION_CLASSIFICATION_BLOCKED,
    ]
    assert json.loads(serialize_v3_9_transition_foundation(foundation))["non_executable"] is True


def test_v3_9_transition_continuity_provenance_replay_and_rollback_are_preserved():
    foundation = default_v3_9_transition_foundation()
    validation = validate_v3_9_transition_foundation_guarantees(foundation)

    with pytest.raises(FrozenInstanceError):
        foundation.provenance_references[0].inferred_provenance_allowed = True

    assert validation["validation_status"] == V3_9_TRANSITION_FOUNDATION_STATUS_STABLE
    assert validation["valid"] is True
    assert validation["continuity_preserved"] is True
    assert validation["provenance_preserved"] is True
    assert validation["replay_safe"] is True
    assert validation["rollback_safe"] is True
    assert validation["immutable_evidence_records"] is True
    assert validation["immutable_continuity_chains"] is True
    assert validation["no_inferred_provenance"] is True
    assert len(foundation.provenance_references[0].originating_evidence_ids) == 3
    assert len(foundation.continuity_references) == 5
    assert all(reference.immutable_chain for reference in foundation.continuity_references)
    assert all(not reference.runtime_replay_enabled for reference in foundation.continuity_references)
    assert all(not reference.rollback_execution_enabled for reference in foundation.continuity_references)


def test_v3_9_transition_fail_visible_supported_unsupported_prohibited_unknown_incomplete_and_blocked_states():
    foundation = default_v3_9_transition_foundation()
    validation = validate_v3_9_transition_foundation_guarantees(foundation)
    counts = count_v3_9_transition_classifications(foundation)

    assert counts[TRANSITION_CLASSIFICATION_SUPPORTED] == 1
    assert counts[TRANSITION_CLASSIFICATION_UNSUPPORTED] == 1
    assert counts[TRANSITION_CLASSIFICATION_PROHIBITED] == 1
    assert counts[TRANSITION_CLASSIFICATION_UNKNOWN] == 1
    assert counts[TRANSITION_CLASSIFICATION_INCOMPLETE] == 1
    assert counts[TRANSITION_CLASSIFICATION_BLOCKED] == 1
    assert validation["fail_visible_non_ready_state_count"] == 5
    assert validation["hidden_non_ready_state_count"] == 0
    assert validation["invalid_transition_state_count"] == 0
    non_ready_states = [
        state for state in foundation.state_references if state.classification != TRANSITION_CLASSIFICATION_SUPPORTED
    ]
    assert all(state.visibility_status == TRANSITION_VISIBILITY_FAIL_VISIBLE for state in non_ready_states)
    assert all(state.fail_visible and not state.hidden for state in non_ready_states)
    assert all(not state.silently_coerced and not state.fallback_applied for state in foundation.state_references)


def test_v3_9_transition_validation_blocks_hidden_or_incomplete_evidence():
    foundation = default_v3_9_transition_foundation()
    hidden_state = replace(
        foundation.state_references[1],
        hidden=True,
        fail_visible=False,
    )
    hidden_foundation = replace(
        foundation,
        state_references=(*foundation.state_references[:1], hidden_state, *foundation.state_references[2:]),
    )
    incomplete_record = replace(
        foundation.evidence_records[0],
        provenance_reference_ids=(),
    )
    incomplete_foundation = replace(
        foundation,
        evidence_records=(incomplete_record, *foundation.evidence_records[1:]),
    )

    hidden_validation = validate_v3_9_transition_foundation_guarantees(hidden_foundation)
    incomplete_validation = validate_v3_9_transition_foundation_guarantees(incomplete_foundation)

    assert hidden_validation["validation_status"] == V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED
    assert hidden_validation["hidden_non_ready_state_count"] == 1
    assert hidden_validation["validation_error_count"] >= 1
    assert incomplete_validation["validation_status"] == V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED
    assert incomplete_validation["missing_provenance_reference_count"] >= 1
    assert incomplete_validation["incomplete_evidence_reference_count"] >= 1


def test_v3_9_transition_validation_blocks_execution_boundary_contamination():
    foundation = replace(
        default_v3_9_transition_foundation(),
        orchestration_execution_enabled=True,
        routing_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_v3_9_transition_foundation_guarantees(foundation)

    assert validation["validation_status"] == V3_9_TRANSITION_FOUNDATION_STATUS_BLOCKED
    assert validation["execution_boundary_violation_count"] == 3
    assert validation["non_execution_confirmation"] is False
    assert validation["valid"] is False


def test_v3_9_transition_report_contains_required_totals_and_boundaries():
    report = build_v3_9_transition_foundations_report()

    assert report["summary"]["foundation_status"] == V3_9_TRANSITION_FOUNDATION_STATUS_STABLE
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["transition_reference_count"] == 4
    assert report["summary"]["state_reference_count"] == 6
    assert report["summary"]["provenance_reference_count"] == 1
    assert report["summary"]["continuity_reference_count"] == 5
    assert report["summary"]["continuity_chain_count"] == 1
    assert report["summary"]["evidence_record_count"] == 4
    assert report["summary"]["fail_visible_non_ready_state_count"] == 5
    assert report["summary"]["hidden_non_ready_state_count"] == 0
    assert report["summary"]["invalid_transition_state_count"] == 0
    assert report["summary"]["missing_provenance_reference_count"] == 0
    assert report["summary"]["invalid_continuity_chain_count"] == 0
    assert report["summary"]["incomplete_evidence_reference_count"] == 0
    assert report["summary"]["execution_boundary_violation_count"] == 0
    assert report["summary"]["continuity_verified"] is True
    assert report["summary"]["provenance_verified"] is True
    assert report["summary"]["replay_verified"] is True
    assert report["summary"]["rollback_verified"] is True
    assert report["summary"]["immutable_evidence_records"] is True
    assert report["summary"]["non_executable_verified"] is True
    assert report["summary"]["orchestration_boundaries_enforced"] is True
    assert report["summary"]["source_artifact_continuity_preserved"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["routing_absent"] is True
    assert report["non_execution_guarantees"]["runtime_mutation_absent"] is True
    assert "v3.9 Phase 1 does not enable orchestration execution" in report["explicit_limitations"]
