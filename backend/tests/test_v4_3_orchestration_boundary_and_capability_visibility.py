from __future__ import annotations

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

from orchestration_governance.orchestration_capability_diagnostics import (  # noqa: E402
    aggregate_blocked_capabilities,
    aggregate_conflicting_capabilities,
    aggregate_prohibited_capabilities,
    aggregate_stale_capabilities,
    aggregate_unsupported_capabilities,
    build_capability_visibility_diagnostics,
    capability_visibilities_equal,
    capability_visibility_identity_key,
    enabled_operational_capability_count,
    validate_capability_continuity,
    validate_capability_explainability,
    validate_capability_metadata,
    validate_capability_non_execution,
    validate_capability_relationships,
    validate_capability_support_visibility,
)
from orchestration_governance.orchestration_capability_hashing import (  # noqa: E402
    hash_capability_boundary,
    hash_capability_explainability,
    hash_capability_record,
    hash_capability_relationship,
    hash_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_models import (  # noqa: E402
    CAPABILITY_STATE_BLOCKED,
    CAPABILITY_STATE_CONFLICTING,
    CAPABILITY_STATE_PROHIBITED,
    CAPABILITY_STATE_STALE,
    CAPABILITY_STATE_SUPPORTED,
    CAPABILITY_STATE_UNSUPPORTED,
    EXPLICIT_ORCHESTRATION_CAPABILITY_PROHIBITIONS,
    V4_3_ORCHESTRATION_CAPABILITY_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_CAPABILITY_STATUS_STABLE,
    default_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_serialization import (  # noqa: E402
    export_orchestration_capability_visibility,
    serialize_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_manifest_hashing import hash_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_manifest_models import default_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_topology_hashing import hash_orchestration_topology  # noqa: E402
from orchestration_governance.orchestration_topology_models import default_orchestration_topology  # noqa: E402
from scripts.report_v4_3_orchestration_boundary_and_capability_visibility import (  # noqa: E402
    build_v4_3_orchestration_boundary_and_capability_visibility_report,
)


def test_v4_3_capability_models_are_immutable_and_non_executable():
    visibility = default_orchestration_capability_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.orchestration_activation_enabled = True

    assert visibility.identity.schema_version == V4_3_ORCHESTRATION_CAPABILITY_SCHEMA_VERSION
    assert visibility.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert visibility.identity.source_topology_hash_reference == hash_orchestration_topology(
        default_orchestration_topology()
    )
    assert visibility.non_executable is True
    assert visibility.descriptive_only is True
    assert visibility.orchestration_execution_enabled is False
    assert visibility.orchestration_activation_enabled is False
    assert visibility.runtime_execution_enabled is False
    assert visibility.capability_execution_enabled is False
    assert visibility.routing_execution_enabled is False
    assert visibility.traversal_execution_enabled is False
    assert visibility.scheduling_execution_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.orchestration_dispatch_enabled is False
    assert visibility.runtime_coordination_enabled is False
    assert visibility.operational_orchestration_engine_enabled is False
    assert visibility.orchestration_decision_engine_enabled is False
    assert enabled_operational_capability_count(visibility) == 0
    assert all(not capability.executable for capability in visibility.capabilities)
    assert all(not capability.operationally_enabled for capability in visibility.capabilities)
    assert all(not relationship.routable for relationship in visibility.relationships)


def test_v4_3_capability_identity_key_is_stable():
    visibility = default_orchestration_capability_visibility()

    assert capability_visibility_identity_key(visibility) == (
        "v4_3.orchestration_boundary_and_capability_visibility.1"
        "|v4_3_orchestration_capability_visibility_primary"
        "|v4.3.0-phase-3"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_primary"
        f"|{hash_orchestration_topology(default_orchestration_topology())}"
        "|v4_3_capability_governance_primary"
    )


def test_v4_3_capability_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_capability_visibility()
    second = default_orchestration_capability_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert capability_visibilities_equal(first, second)
    assert serialize_orchestration_capability_visibility(first) == serialize_orchestration_capability_visibility(second)
    assert hash_orchestration_capability_visibility(first) == hash_orchestration_capability_visibility(second)


def test_v4_3_capability_ordering_stability_survives_reordered_collections():
    visibility = default_orchestration_capability_visibility()
    reordered = replace(
        visibility,
        capabilities=tuple(reversed(visibility.capabilities)),
        boundaries=tuple(reversed(visibility.boundaries)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )

    assert serialize_orchestration_capability_visibility(visibility) == serialize_orchestration_capability_visibility(
        reordered
    )
    assert hash_orchestration_capability_visibility(visibility) == hash_orchestration_capability_visibility(reordered)
    exported = export_orchestration_capability_visibility(reordered)
    assert [item["support_state"] for item in exported["capabilities"]] == [
        CAPABILITY_STATE_SUPPORTED,
        CAPABILITY_STATE_UNSUPPORTED,
        CAPABILITY_STATE_BLOCKED,
        CAPABILITY_STATE_STALE,
        CAPABILITY_STATE_CONFLICTING,
        CAPABILITY_STATE_PROHIBITED,
    ]


def test_v4_3_capability_support_state_visibility_is_fail_visible():
    visibility = default_orchestration_capability_visibility()
    support = validate_capability_support_visibility(visibility)

    assert support["valid"] is True
    assert support["prohibited_capabilities_visible"] is True
    assert support["unsupported_capabilities_visible"] is True
    assert support["blocked_capabilities_visible"] is True
    assert support["stale_capabilities_visible"] is True
    assert support["conflicting_capabilities_visible"] is True
    assert support["enabled_operational_capability_count"] == 0
    assert support["duplicate_capability_ids"] == ()
    assert support["hidden_count"] == 0


def test_v4_3_capability_duplicate_detection_is_visible():
    visibility = default_orchestration_capability_visibility()
    duplicate = replace(visibility.capabilities[0], deterministic_order=999)
    contaminated = replace(visibility, capabilities=visibility.capabilities + (duplicate,))
    support = validate_capability_support_visibility(contaminated)

    assert support["valid"] is False
    assert support["duplicate_capability_ids"] == (visibility.capabilities[0].capability_id,)


def test_v4_3_capability_invalid_relationship_detection_is_visible():
    visibility = default_orchestration_capability_visibility()
    invalid_boundary = replace(
        visibility.relationships[0],
        relationship_id="v4_3_capability_invalid_boundary_relationship",
        target_reference_id="missing_boundary",
        deterministic_order=999,
    )
    invalid_policy = replace(
        visibility.relationships[1],
        relationship_id="v4_3_capability_invalid_policy_relationship",
        target_reference_id="unexpected_policy",
        deterministic_order=1000,
    )
    contaminated = replace(visibility, relationships=visibility.relationships + (invalid_boundary, invalid_policy))
    validation = validate_capability_relationships(contaminated)

    assert validation["valid"] is False
    assert validation["invalid_boundary_relationship_ids"] == (
        "v4_3_capability_invalid_boundary_relationship",
    )
    assert validation["invalid_policy_relationship_ids"] == (
        "v4_3_capability_invalid_policy_relationship",
    )
    assert validation["invalid_relationship_count"] == 2


def test_v4_3_capability_aggregation_is_deterministic():
    visibility = default_orchestration_capability_visibility()
    diagnostics = build_capability_visibility_diagnostics(visibility)

    assert aggregate_prohibited_capabilities(visibility) == diagnostics["prohibited_capability_ids"]
    assert aggregate_unsupported_capabilities(visibility) == diagnostics["unsupported_capability_ids"]
    assert aggregate_blocked_capabilities(visibility) == diagnostics["blocked_capability_ids"]
    assert aggregate_stale_capabilities(visibility) == diagnostics["stale_capability_ids"]
    assert aggregate_conflicting_capabilities(visibility) == diagnostics["conflicting_capability_ids"]
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["correction_absent"] is True
    assert diagnostics["inference_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["operational_mutation_absent"] is True
    assert diagnostics["execution_absent"] is True
    assert diagnostics["selection_systems_absent"] is True


def test_v4_3_capability_metadata_continuity_and_explainability_are_valid():
    visibility = default_orchestration_capability_visibility()
    metadata = validate_capability_metadata(visibility)
    continuity = validate_capability_continuity(visibility)
    explainability = validate_capability_explainability(visibility)

    assert metadata["valid"] is True
    assert metadata["governance_boundary_metadata_present"] is True
    assert metadata["operational_boundary_metadata_present"] is True
    assert metadata["provenance_metadata_present"] is True
    assert metadata["lineage_metadata_present"] is True
    assert continuity["valid"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert explainability["valid"] is True
    assert "activation_unavailable" in explainability["explainability_categories"]
    assert "execution_unavailable" in explainability["explainability_categories"]
    assert "planner_integration_unavailable" in explainability["explainability_categories"]
    assert "operational_orchestration_prohibited" in explainability["explainability_categories"]
    assert "governance_boundary" in explainability["explainability_categories"]


def test_v4_3_capability_non_execution_validation_blocks_operational_flags():
    visibility = default_orchestration_capability_visibility()
    contaminated_capability = replace(
        visibility.capabilities[0],
        executable=True,
        authorized=True,
        schedulable=True,
        routable=True,
        planner_integrated=True,
    )
    contaminated = replace(
        visibility,
        capabilities=(contaminated_capability,) + visibility.capabilities[1:],
        orchestration_activation_enabled=True,
        runtime_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_capability_non_execution(contaminated)

    assert validate_capability_non_execution(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_operational_capability_count"] == 1
    assert validation["orchestration_activation_disabled"] is False
    assert validation["runtime_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_capability_report_generation_and_report_hash_are_stable():
    first = build_v4_3_orchestration_boundary_and_capability_visibility_report()
    second = build_v4_3_orchestration_boundary_and_capability_visibility_report()

    assert first == second
    assert first["capability_visibility_status"] == V4_3_ORCHESTRATION_CAPABILITY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["capability_ordering_verified"] is True
    assert first["summary"]["boundary_ordering_verified"] is True
    assert first["summary"]["relationship_ordering_verified"] is True
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["orchestration_execution_disabled"] is True
    assert first["summary"]["orchestration_activation_disabled"] is True
    assert first["summary"]["traversal_execution_disabled"] is True
    assert first["summary"]["routing_execution_disabled"] is True
    assert first["summary"]["scheduling_execution_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert "No orchestration capability may become executable." in EXPLICIT_ORCHESTRATION_CAPABILITY_PROHIBITIONS
    assert "No operational orchestration engine exists." in first["explicit_prohibitions"]


def test_v4_3_capability_hashes_are_stable():
    visibility = default_orchestration_capability_visibility()

    assert [hash_capability_record(capability) for capability in visibility.capabilities] == [
        hash_capability_record(capability) for capability in visibility.capabilities
    ]
    assert [hash_capability_boundary(boundary) for boundary in visibility.boundaries] == [
        hash_capability_boundary(boundary) for boundary in visibility.boundaries
    ]
    assert [hash_capability_relationship(relationship) for relationship in visibility.relationships] == [
        hash_capability_relationship(relationship) for relationship in visibility.relationships
    ]
    assert [hash_capability_explainability(summary) for summary in visibility.explainability_summaries] == [
        hash_capability_explainability(summary) for summary in visibility.explainability_summaries
    ]
