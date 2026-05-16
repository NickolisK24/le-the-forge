from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_policy_compatibility_models import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_GOVERNANCE_BLOCKED,
    COMPATIBILITY_INCOMPATIBLE,
    COMPATIBILITY_PROHIBITED,
    COMPATIBILITY_UNSUPPORTED,
    export_compatibility_registry,
    hash_compatibility_registry,
    serialize_compatibility_registry,
)
from app.runtime_orchestration.orchestration_policy_compatibility_registry import (
    build_orchestration_policy_compatibility_registry,
    default_orchestration_policy_compatibility_registry,
    get_registered_compatibility_relationship,
    registered_compatibility_relationship_ids,
)


def _registry():
    return default_orchestration_policy_compatibility_registry()


def test_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_compatibility_registry(first) == serialize_compatibility_registry(second)
    assert hash_compatibility_registry(first) == hash_compatibility_registry(second)
    assert export_compatibility_registry(first)["deterministic_compatibility_registry_hash"] == hash_compatibility_registry(first)


def test_registry_relationship_totals_are_deterministic():
    relationships = export_compatibility_registry(_registry())["relationships"]

    assert len(relationships) == 13
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_COMPATIBLE) == 5
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_INCOMPATIBLE) == 1
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_PROHIBITED) == 3
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_UNSUPPORTED) == 2
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_DEPENDENCY_BLOCKED) == 1
    assert sum(1 for relationship in relationships if relationship["compatibility_state"] == COMPATIBILITY_GOVERNANCE_BLOCKED) == 1


def test_relationship_ids_are_unique_and_stably_ordered():
    ids = registered_compatibility_relationship_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.compat.execution-routing.prohibited" in ids
    assert "v3_6.compat.integrity-execution.dependency-blocked" in ids


def test_duplicate_relationship_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.relationships[0], compatibility_classification="duplicate")

    with pytest.raises(ValueError, match="Duplicate compatibility relationship ids"):
        build_orchestration_policy_compatibility_registry((registry.relationships[0], duplicate))


def test_relationships_preserve_provenance_governance_and_blocker_chain_metadata():
    relationship = get_registered_compatibility_relationship(_registry(), "v3_6.compat.execution-routing.prohibited")
    assert relationship is not None

    assert relationship.provenance.source_phase == "v3.6_phase_2_deterministic_orchestration_policy_compatibility_matrix"
    assert relationship.provenance.replay_reference_ids == ("v3_6.compat.execution-routing.prohibited.replay",)
    assert relationship.provenance.rollback_reference_ids == ("v3_6.compat.execution-routing.prohibited.rollback",)
    assert relationship.governance_metadata["planning_only"] is True
    assert relationship.governance_metadata["execution_enabled"] is False
    assert relationship.blocker_chains[0].blocker_chain_id == "v3_6.compat.execution-routing.prohibited.blocker-chain"


def test_compatibility_relationships_are_non_executing():
    for relationship in _registry().relationships:
        assert relationship.runtime_execution_enabled is False
        assert relationship.orchestration_execution_enabled is False
        assert relationship.routing_behavior_enabled is False
        assert relationship.mutation_behavior_enabled is False
        assert relationship.audit_log_writing_enabled is False
        assert relationship.production_consumption_enabled is False
        assert relationship.graph_execution_enabled is False
        assert relationship.graph_traversal_behavior_enabled is False
        assert relationship.scheduling_behavior_enabled is False
        assert relationship.orchestration_dispatch_enabled is False
        assert relationship.runtime_trace_capture_enabled is False
        assert relationship.production_state_reads_enabled is False
        assert relationship.live_replay_enabled is False
        assert relationship.persistent_audit_storage_enabled is False
        assert relationship.compatibility_execution_enabled is False
