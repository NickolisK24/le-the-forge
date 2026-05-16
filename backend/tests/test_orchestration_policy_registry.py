from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_policy_models import (
    POLICY_PROHIBITED,
    POLICY_SUPPORTED,
    POLICY_UNSUPPORTED,
    export_policy_registry,
    hash_policy_registry,
    serialize_policy_registry,
)
from app.runtime_orchestration.orchestration_policy_registry import (
    build_orchestration_policy_registry,
    default_orchestration_policy_registry,
    get_registered_policy,
    registered_policy_ids,
)


def _registry():
    return default_orchestration_policy_registry()


def test_registry_deterministic_serialization_and_hash_stability():
    first = _registry()
    second = _registry()

    assert serialize_policy_registry(first) == serialize_policy_registry(second)
    assert hash_policy_registry(first) == hash_policy_registry(second)
    assert export_policy_registry(first)["deterministic_registry_hash"] == hash_policy_registry(first)


def test_registry_registers_supported_prohibited_and_unsupported_policy_states():
    registry = _registry()
    exported = export_policy_registry(registry)
    policies = exported["policies"]

    assert exported["registry_id"] == "v3_6_orchestration_policy_intelligence_registry"
    assert len(policies) == 8
    assert sum(1 for policy in policies if policy["support_state"] == POLICY_SUPPORTED) == 4
    assert sum(1 for policy in policies if policy["support_state"] == POLICY_PROHIBITED) == 3
    assert sum(1 for policy in policies if policy["support_state"] == POLICY_UNSUPPORTED) == 1


def test_policy_ids_are_stable_sorted_and_unique():
    ids = registered_policy_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert ids[0] == "v3_6.policy.autonomy.unsupported"
    assert "v3_6.policy.execution.prohibited" in ids
    assert "v3_6.policy.integrity.allowed" in ids


def test_duplicate_policy_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(
        registry.policies[0],
        display_name="Duplicate deterministic policy identity",
    )

    with pytest.raises(ValueError, match="Duplicate orchestration policy ids"):
        build_orchestration_policy_registry((registry.policies[0], duplicate))


def test_registry_preserves_policy_provenance_and_governance_metadata():
    registry = _registry()
    modeling = get_registered_policy(registry, "v3_6.policy.modeling.allowed")
    assert modeling is not None

    assert modeling.provenance.source_phase == "v3.6_phase_1_deterministic_orchestration_policy_intelligence_foundation"
    assert modeling.provenance.replay_reference_ids == ("v3_6.policy.modeling.allowed.replay",)
    assert modeling.provenance.rollback_reference_ids == ("v3_6.policy.modeling.allowed.rollback",)
    assert modeling.governance_metadata["planning_only"] is True
    assert modeling.governance_metadata["execution_enabled"] is False
    assert modeling.governance_metadata["production_runtime_reads_enabled"] is False


def test_registry_policy_definitions_are_non_executing():
    for policy in _registry().policies:
        assert policy.runtime_execution_enabled is False
        assert policy.orchestration_execution_enabled is False
        assert policy.routing_behavior_enabled is False
        assert policy.mutation_behavior_enabled is False
        assert policy.audit_log_writing_enabled is False
        assert policy.production_consumption_enabled is False
        assert policy.graph_execution_enabled is False
        assert policy.graph_traversal_behavior_enabled is False
        assert policy.scheduling_behavior_enabled is False
        assert policy.orchestration_dispatch_enabled is False
        assert policy.runtime_trace_capture_enabled is False
        assert policy.production_state_reads_enabled is False
        assert policy.live_replay_enabled is False
        assert policy.persistent_audit_storage_enabled is False
        assert policy.policy_execution_enabled is False
