from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_evaluation_trace_models import (
    TRACE_COMPATIBILITY_BLOCKED,
    TRACE_DEPENDENCY_BLOCKED,
    TRACE_GOVERNANCE_BLOCKED,
    TRACE_PROHIBITED,
    TRACE_STEP_BLOCKER,
    TRACE_STEP_COMPATIBILITY,
    TRACE_STEP_GOVERNANCE,
    TRACE_STEP_INTEGRITY,
    TRACE_STEP_PROVENANCE,
    TRACE_SUPPORTED,
    TRACE_UNSUPPORTED,
    export_trace_registry,
    hash_trace_registry,
    serialize_trace_registry,
)
from app.runtime_orchestration.orchestration_evaluation_trace_registry import (
    build_orchestration_evaluation_trace_registry,
    default_orchestration_evaluation_trace_registry,
    get_registered_trace_record,
    get_registered_trace_record_for_preflight,
    registered_trace_ids,
)


def _registry():
    return default_orchestration_evaluation_trace_registry()


def test_trace_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_trace_registry(first) == serialize_trace_registry(second)
    assert hash_trace_registry(first) == hash_trace_registry(second)
    assert export_trace_registry(first)["deterministic_trace_registry_hash"] == hash_trace_registry(first)


def test_trace_registry_totals_are_deterministic():
    records = export_trace_registry(_registry())["records"]

    assert len(records) == 9
    assert sum(1 for record in records if record["trace_state"] == TRACE_SUPPORTED) == 3
    assert sum(1 for record in records if record["trace_state"] == TRACE_UNSUPPORTED) == 1
    assert sum(1 for record in records if record["trace_state"] == TRACE_PROHIBITED) == 2
    assert sum(1 for record in records if record["trace_state"] == TRACE_GOVERNANCE_BLOCKED) == 1
    assert sum(1 for record in records if record["trace_state"] == TRACE_COMPATIBILITY_BLOCKED) == 1
    assert sum(1 for record in records if record["trace_state"] == TRACE_DEPENDENCY_BLOCKED) == 1


def test_trace_ids_are_unique_and_stably_ordered():
    ids = registered_trace_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.trace.compatibility-check" in ids
    assert "v3_6.trace.prohibited-domain" in ids


def test_duplicate_trace_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.records[0], reasoning_chain=("duplicate",))

    with pytest.raises(ValueError, match="Duplicate orchestration evaluation trace ids"):
        build_orchestration_evaluation_trace_registry((registry.records[0], duplicate))


def test_compatibility_check_trace_preserves_preflight_lineage():
    record = get_registered_trace_record(_registry(), "v3_6.trace.compatibility-check")
    by_preflight = get_registered_trace_record_for_preflight(_registry(), "v3_6.preflight.compatibility-check")

    assert record is not None
    assert by_preflight == record
    assert record.trace_state == TRACE_SUPPORTED
    assert record.identifier.preflight_id == "v3_6.preflight.compatibility-check"
    assert "v3_6.policy.integrity.allowed" in record.policy_ids
    assert "compatibility_matrix" in record.compatibility_domains
    assert "compatibility_blocker_visibility" in record.blocker_domains
    assert "compatibility_pre_analysis_only" in record.governance_boundaries
    assert record.provenance.replay_reference_ids == ("v3_6.trace.compatibility-check.replay",)
    assert record.provenance.rollback_reference_ids == ("v3_6.trace.compatibility-check.rollback",)


def test_trace_steps_are_ordered_and_fail_visible():
    record = get_registered_trace_record(_registry(), "v3_6.trace.compatibility-check")

    assert record is not None
    step_types = tuple(step.step_type for step in record.trace_steps)
    assert step_types[0] == "supportability_evaluation_trace_step"
    assert step_types[1] == TRACE_STEP_GOVERNANCE
    assert TRACE_STEP_COMPATIBILITY in step_types
    assert TRACE_STEP_BLOCKER in step_types
    assert TRACE_STEP_PROVENANCE in step_types
    assert TRACE_STEP_INTEGRITY in step_types
    assert tuple(step.sequence_id for step in record.trace_steps) == tuple(range(1, len(record.trace_steps) + 1))
    assert len(record.reasoning_chain) == len(record.trace_steps)


def test_blocked_unsupported_and_prohibited_traces_remain_fail_visible():
    governance = get_registered_trace_record(_registry(), "v3_6.trace.governance-review")
    dependency = get_registered_trace_record(_registry(), "v3_6.trace.dependency-analysis")
    unsupported = get_registered_trace_record(_registry(), "v3_6.trace.unsupported-domain")
    prohibited = get_registered_trace_record(_registry(), "v3_6.trace.prohibited-domain")

    assert governance is not None
    assert dependency is not None
    assert unsupported is not None
    assert prohibited is not None
    assert governance.trace_state == TRACE_GOVERNANCE_BLOCKED
    assert "governance_conflict_visibility" in governance.blocker_domains
    assert dependency.trace_state == TRACE_DEPENDENCY_BLOCKED
    assert "dependency_conflict" in dependency.dependency_domains
    assert unsupported.trace_state == TRACE_UNSUPPORTED
    assert "autonomous_orchestration" in unsupported.unsupported_domains
    assert prohibited.trace_state == TRACE_PROHIBITED
    assert "orchestration_execution" in prohibited.prohibited_domains


def test_trace_records_are_non_executing_and_planning_only():
    for record in _registry().records:
        assert record.runtime_execution_enabled is False
        assert record.orchestration_execution_enabled is False
        assert record.routing_behavior_enabled is False
        assert record.mutation_behavior_enabled is False
        assert record.production_consumption_enabled is False
        assert record.background_processing_enabled is False
        assert record.recommendation_behavior_enabled is False
        assert record.optimization_behavior_enabled is False
        assert record.autonomous_behavior_enabled is False
        assert record.graph_execution_enabled is False
        assert record.trace_execution_enabled is False
