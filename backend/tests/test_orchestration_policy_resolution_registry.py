from __future__ import annotations

from dataclasses import replace

import pytest

from app.runtime_orchestration.orchestration_policy_resolution_models import (
    RESOLUTION_DEPENDENCY_CONFLICT,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_FUTURE_CANDIDATE,
    RESOLUTION_GOVERNANCE_CONFLICT,
    RESOLUTION_INTENTIONAL_BLOCK,
    RESOLUTION_UNSUPPORTED_BY_DESIGN,
    export_resolution_registry,
    hash_resolution_registry,
    serialize_resolution_registry,
)
from app.runtime_orchestration.orchestration_policy_resolution_registry import (
    build_orchestration_policy_resolution_registry,
    default_orchestration_policy_resolution_registry,
    get_registered_resolution_record,
    get_registered_resolution_record_for_relationship,
    registered_resolution_ids,
)


def _registry():
    return default_orchestration_policy_resolution_registry()


def test_resolution_registry_serialization_and_hash_are_stable():
    first = _registry()
    second = _registry()

    assert serialize_resolution_registry(first) == serialize_resolution_registry(second)
    assert hash_resolution_registry(first) == hash_resolution_registry(second)
    assert export_resolution_registry(first)["deterministic_resolution_registry_hash"] == hash_resolution_registry(first)


def test_resolution_registry_classification_totals_are_deterministic():
    records = export_resolution_registry(_registry())["records"]

    assert len(records) == 8
    assert sum(1 for record in records if RESOLUTION_INTENTIONAL_BLOCK in record["resolution_classifications"]) == 3
    assert sum(1 for record in records if RESOLUTION_FUTURE_CANDIDATE in record["resolution_classifications"]) == 1
    assert sum(1 for record in records if RESOLUTION_UNSUPPORTED_BY_DESIGN in record["resolution_classifications"]) == 2
    assert sum(1 for record in records if RESOLUTION_GOVERNANCE_CONFLICT in record["resolution_classifications"]) == 1
    assert sum(1 for record in records if RESOLUTION_DEPENDENCY_CONFLICT in record["resolution_classifications"]) == 1
    assert sum(1 for record in records if RESOLUTION_EVIDENCE_INCOMPLETE in record["resolution_classifications"]) == 1


def test_resolution_ids_are_unique_and_stably_ordered():
    ids = registered_resolution_ids(_registry())

    assert ids == tuple(sorted(ids))
    assert len(ids) == len(set(ids))
    assert "v3_6.resolution.execution-routing.prohibited" in ids
    assert "v3_6.resolution.explainability-routing.incompatible" in ids


def test_duplicate_resolution_registration_fails_visibly():
    registry = _registry()
    duplicate = replace(registry.records[0], support_rationale=("duplicate",))

    with pytest.raises(ValueError, match="Duplicate resolution ids"):
        build_orchestration_policy_resolution_registry((registry.records[0], duplicate))


def test_resolution_records_preserve_provenance_governance_and_evidence_metadata():
    record = get_registered_resolution_record(_registry(), "v3_6.resolution.explainability-routing.incompatible")
    assert record is not None

    assert record.provenance.source_phase == "v3.6_phase_3_deterministic_orchestration_policy_resolution_audit"
    assert record.provenance.compatibility_relationship_id == "v3_6.compat.explainability-routing.incompatible"
    assert record.provenance.replay_reference_ids == ("v3_6.resolution.explainability-routing.incompatible.replay",)
    assert record.provenance.rollback_reference_ids == ("v3_6.resolution.explainability-routing.incompatible.rollback",)
    assert record.governance_metadata["planning_only"] is True
    assert record.governance_metadata["automatic_resolution_enabled"] is False
    assert record.future_support_possible is True
    assert len(record.evidence_gaps) == 1
    assert "non_routing_explainability_proof" in record.evidence_gaps[0].missing_evidence_ids


def test_resolution_record_lookup_by_relationship_is_deterministic():
    record = get_registered_resolution_record_for_relationship(_registry(), "v3_6.compat.integrity-execution.dependency-blocked")
    assert record is not None

    assert record.identifier.resolution_id == "v3_6.resolution.integrity-execution.dependency-blocked"
    assert record.dependency_gaps == ("integrity-requires-non-executing-policy-surface",)


def test_resolution_records_are_non_executing_and_planning_only():
    for record in _registry().records:
        assert record.status_change_allowed is False
        assert record.automatic_resolution_enabled is False
        assert record.runtime_execution_enabled is False
        assert record.orchestration_execution_enabled is False
        assert record.routing_behavior_enabled is False
        assert record.mutation_behavior_enabled is False
        assert record.production_consumption_enabled is False
        assert record.background_processing_enabled is False
