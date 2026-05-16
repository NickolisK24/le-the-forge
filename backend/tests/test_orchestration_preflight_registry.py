from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_preflight_models import (
    PREFLIGHT_COMPATIBILITY_BLOCKED,
    PREFLIGHT_DEPENDENCY_BLOCKED,
    PREFLIGHT_GOVERNANCE_BLOCKED,
    PREFLIGHT_PROHIBITED,
    PREFLIGHT_SUPPORTED,
    PREFLIGHT_UNSUPPORTED,
    export_preflight_registry,
    hash_preflight_registry,
    serialize_preflight_registry,
)
from app.runtime_orchestration.orchestration_preflight_registry import (
    build_orchestration_preflight_registry,
    default_orchestration_preflight_registry,
    get_registered_preflight_record,
    get_registered_preflight_record_for_intent,
    registered_preflight_ids,
)


def _registry():
    return default_orchestration_preflight_registry()


def test_preflight_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_preflight_registry(first) == serialize_preflight_registry(second)
    assert hash_preflight_registry(first) == hash_preflight_registry(second)
    assert export_preflight_registry(first)["deterministic_preflight_registry_hash"] == hash_preflight_registry(first)


def test_preflight_registry_totals_are_deterministic():
    records = export_preflight_registry(_registry())["records"]

    assert len(records) == 9
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_SUPPORTED) == 3
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_UNSUPPORTED) == 1
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_PROHIBITED) == 2
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_GOVERNANCE_BLOCKED) == 1
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_COMPATIBILITY_BLOCKED) == 1
    assert sum(1 for record in records if record["preflight_state"] == PREFLIGHT_DEPENDENCY_BLOCKED) == 1


def test_preflight_ids_are_unique_and_stably_ordered():
    ids = registered_preflight_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.preflight.compatibility-check" in ids
    assert "v3_6.preflight.prohibited-domain" in ids


def test_duplicate_preflight_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.records[0], preflight_rationale=("duplicate",))

    with pytest.raises(ValueError, match="Duplicate orchestration preflight ids"):
        build_orchestration_preflight_registry((registry.records[0], duplicate))


def test_compatibility_check_preflight_preserves_theoretical_supportability():
    record = get_registered_preflight_record(_registry(), "v3_6.preflight.compatibility-check")
    by_intent = get_registered_preflight_record_for_intent(_registry(), "v3_6.intent.compatibility-check")

    assert record is not None
    assert by_intent == record
    assert record.preflight_state == PREFLIGHT_SUPPORTED
    assert record.theoretically_supportable is True
    assert "v3_6.policy.integrity.allowed" in record.policy_ids
    assert "compatibility_matrix" in record.compatibility_domains
    assert "compatibility_blocker_visibility" in record.blocker_domains
    assert "compatibility_pre_analysis_only" in record.governance_boundaries
    assert record.provenance.mapping_id == "v3_6.mapping.compatibility-check"
    assert record.provenance.replay_reference_ids == ("v3_6.preflight.compatibility-check.replay",)
    assert record.provenance.rollback_reference_ids == ("v3_6.preflight.compatibility-check.rollback",)


def test_blocked_unsupported_and_prohibited_preflights_remain_fail_visible():
    governance = get_registered_preflight_record(_registry(), "v3_6.preflight.governance-review")
    dependency = get_registered_preflight_record(_registry(), "v3_6.preflight.dependency-analysis")
    unsupported = get_registered_preflight_record(_registry(), "v3_6.preflight.unsupported-domain")
    prohibited = get_registered_preflight_record(_registry(), "v3_6.preflight.prohibited-domain")

    assert governance is not None
    assert dependency is not None
    assert unsupported is not None
    assert prohibited is not None
    assert governance.preflight_state == PREFLIGHT_GOVERNANCE_BLOCKED
    assert "governance_conflict_visibility" in governance.blocker_domains
    assert dependency.preflight_state == PREFLIGHT_DEPENDENCY_BLOCKED
    assert "dependency_conflict" in dependency.dependency_domains
    assert unsupported.preflight_state == PREFLIGHT_UNSUPPORTED
    assert "autonomous_orchestration" in unsupported.unsupported_domains
    assert prohibited.preflight_state == PREFLIGHT_PROHIBITED
    assert "orchestration_execution" in prohibited.prohibited_domains


def test_preflight_records_are_non_executing_and_planning_only():
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
        assert record.preflight_execution_enabled is False
