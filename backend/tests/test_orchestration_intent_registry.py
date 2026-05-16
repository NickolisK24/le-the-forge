from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_intent_models import (
    INTENT_COMPATIBILITY_CHECK,
    INTENT_PROHIBITED,
    INTENT_SUPPORTED,
    INTENT_UNSUPPORTED,
    export_intent_registry,
    hash_intent_registry,
    serialize_intent_registry,
)
from app.runtime_orchestration.orchestration_intent_registry import (
    build_orchestration_intent_registry,
    default_orchestration_intent_registry,
    get_registered_intent_record,
    registered_intent_ids,
)


def _registry():
    return default_orchestration_intent_registry()


def test_intent_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_intent_registry(first) == serialize_intent_registry(second)
    assert hash_intent_registry(first) == hash_intent_registry(second)
    assert export_intent_registry(first)["deterministic_intent_registry_hash"] == hash_intent_registry(first)


def test_intent_registry_totals_are_deterministic():
    records = export_intent_registry(_registry())["records"]

    assert len(records) == 9
    assert sum(1 for record in records if record["support_state"] == INTENT_SUPPORTED) == 7
    assert sum(1 for record in records if record["support_state"] == INTENT_UNSUPPORTED) == 1
    assert sum(1 for record in records if record["support_state"] == INTENT_PROHIBITED) == 1


def test_intent_ids_are_unique_and_stably_ordered():
    ids = registered_intent_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.intent.compatibility-check" in ids
    assert "v3_6.intent.prohibited-domain" in ids


def test_duplicate_intent_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.records[0], intent_goal="duplicate")

    with pytest.raises(ValueError, match="Duplicate orchestration intent ids"):
        build_orchestration_intent_registry((registry.records[0], duplicate))


def test_compatibility_check_intent_preserves_domain_metadata():
    record = get_registered_intent_record(_registry(), "v3_6.intent.compatibility-check")
    assert record is not None

    assert record.intent_type == INTENT_COMPATIBILITY_CHECK
    assert record.support_state == INTENT_SUPPORTED
    assert "compatibility_matrix" in record.compatibility_domains
    assert "compatibility_blocker_visibility" in record.blocker_domains
    assert "compatibility_pre_analysis_only" in record.governance_boundaries
    assert record.provenance.replay_reference_ids == ("v3_6.intent.compatibility-check.replay",)
    assert record.provenance.rollback_reference_ids == ("v3_6.intent.compatibility-check.rollback",)


def test_unsupported_and_prohibited_intents_remain_fail_visible():
    unsupported = get_registered_intent_record(_registry(), "v3_6.intent.unsupported-domain")
    prohibited = get_registered_intent_record(_registry(), "v3_6.intent.prohibited-domain")

    assert unsupported is not None
    assert prohibited is not None
    assert unsupported.support_state == INTENT_UNSUPPORTED
    assert "autonomous_orchestration" in unsupported.unsupported_domains
    assert "unsupported_domain_blocker" in unsupported.blocker_domains
    assert prohibited.support_state == INTENT_PROHIBITED
    assert "orchestration_execution" in prohibited.prohibited_domains
    assert "prohibited_execution_blocker" in prohibited.blocker_domains


def test_intent_records_are_non_executing_and_planning_only():
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
