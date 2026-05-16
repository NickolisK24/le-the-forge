from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_intent_policy_mapping_models import (
    MAPPING_INTENT_TO_POLICY,
    MAPPING_PROHIBITED,
    MAPPING_SUPPORTED,
    MAPPING_UNSUPPORTED,
    export_mapping_registry,
    hash_mapping_registry,
    serialize_mapping_registry,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_registry import (
    build_orchestration_intent_policy_mapping_registry,
    default_orchestration_intent_policy_mapping_registry,
    get_registered_mapping_record,
    get_registered_mapping_record_for_intent,
    registered_mapping_ids,
)


def _registry():
    return default_orchestration_intent_policy_mapping_registry()


def test_mapping_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_mapping_registry(first) == serialize_mapping_registry(second)
    assert hash_mapping_registry(first) == hash_mapping_registry(second)
    assert export_mapping_registry(first)["deterministic_mapping_registry_hash"] == hash_mapping_registry(first)


def test_mapping_registry_totals_are_deterministic():
    records = export_mapping_registry(_registry())["records"]

    assert len(records) == 9
    assert sum(1 for record in records if record["mapping_state"] == MAPPING_SUPPORTED) == 7
    assert sum(1 for record in records if record["mapping_state"] == MAPPING_UNSUPPORTED) == 1
    assert sum(1 for record in records if record["mapping_state"] == MAPPING_PROHIBITED) == 1


def test_mapping_ids_are_unique_and_stably_ordered():
    ids = registered_mapping_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.mapping.compatibility-check" in ids
    assert "v3_6.mapping.prohibited-domain" in ids


def test_duplicate_mapping_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.records[0], mapping_rationale=("duplicate",))

    with pytest.raises(ValueError, match="Duplicate orchestration intent-policy mapping ids"):
        build_orchestration_intent_policy_mapping_registry((registry.records[0], duplicate))


def test_compatibility_check_mapping_preserves_policy_and_domain_metadata():
    record = get_registered_mapping_record(_registry(), "v3_6.mapping.compatibility-check")
    by_intent = get_registered_mapping_record_for_intent(_registry(), "v3_6.intent.compatibility-check")

    assert record is not None
    assert by_intent == record
    assert record.mapping_state == MAPPING_SUPPORTED
    assert MAPPING_INTENT_TO_POLICY in record.mapping_classifications
    assert "v3_6.policy.modeling.allowed" in record.policy_ids
    assert "v3_6.policy.governance-boundary.allowed" in record.policy_ids
    assert "v3_6.policy.integrity.allowed" in record.policy_ids
    assert "compatibility_matrix" in record.compatibility_domains
    assert "compatibility_blocker_visibility" in record.blocker_domains
    assert "compatibility_pre_analysis_only" in record.governance_boundaries
    assert record.provenance.replay_reference_ids == ("v3_6.mapping.compatibility-check.replay",)
    assert record.provenance.rollback_reference_ids == ("v3_6.mapping.compatibility-check.rollback",)


def test_unsupported_and_prohibited_mappings_remain_fail_visible():
    unsupported = get_registered_mapping_record(_registry(), "v3_6.mapping.unsupported-domain")
    prohibited = get_registered_mapping_record(_registry(), "v3_6.mapping.prohibited-domain")

    assert unsupported is not None
    assert prohibited is not None
    assert unsupported.mapping_state == MAPPING_UNSUPPORTED
    assert "v3_6.policy.autonomy.unsupported" in unsupported.policy_ids
    assert "autonomous_orchestration" in unsupported.unsupported_domains
    assert "unsupported_domain_blocker" in unsupported.blocker_domains
    assert prohibited.mapping_state == MAPPING_PROHIBITED
    assert "v3_6.policy.execution.prohibited" in prohibited.policy_ids
    assert "orchestration_execution" in prohibited.prohibited_domains
    assert "prohibited_execution_blocker" in prohibited.blocker_domains


def test_mapping_records_are_non_executing_and_planning_only():
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
        assert record.mapping_execution_enabled is False
