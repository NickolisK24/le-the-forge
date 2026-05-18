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

from orchestration_governance.orchestration_capability_hashing import (  # noqa: E402
    hash_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_models import (  # noqa: E402
    default_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_coordination_diagnostics import (  # noqa: E402
    aggregate_blocked_coordinations,
    aggregate_conflicting_coordinations,
    aggregate_prohibited_coordinations,
    aggregate_stale_coordinations,
    aggregate_unsupported_coordinations,
    build_coordination_visibility_diagnostics,
    coordination_visibilities_equal,
    coordination_visibility_identity_key,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    validate_coordination_continuity,
    validate_coordination_explainability,
    validate_coordination_metadata,
    validate_coordination_non_execution_and_non_coordination,
    validate_coordination_participants,
    validate_coordination_relationships,
    validate_coordination_support_visibility,
)
from orchestration_governance.orchestration_coordination_hashing import (  # noqa: E402
    hash_coordination_explainability,
    hash_coordination_participant,
    hash_coordination_record,
    hash_coordination_relationship,
    hash_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_models import (  # noqa: E402
    COORDINATION_STATE_BLOCKED,
    COORDINATION_STATE_CONFLICTING,
    COORDINATION_STATE_PROHIBITED,
    COORDINATION_STATE_STALE,
    COORDINATION_STATE_SUPPORTED,
    COORDINATION_STATE_UNSUPPORTED,
    EXPLICIT_ORCHESTRATION_COORDINATION_PROHIBITIONS,
    V4_3_ORCHESTRATION_COORDINATION_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_COORDINATION_STATUS_STABLE,
    default_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_serialization import (  # noqa: E402
    export_orchestration_coordination_visibility,
    serialize_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_manifest_hashing import hash_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_manifest_models import default_orchestration_manifest  # noqa: E402
from orchestration_governance.orchestration_policy_hashing import (  # noqa: E402
    hash_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_policy_models import (  # noqa: E402
    default_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_topology_hashing import hash_orchestration_topology  # noqa: E402
from orchestration_governance.orchestration_topology_models import default_orchestration_topology  # noqa: E402
from orchestration_governance.orchestration_transition_hashing import (  # noqa: E402
    hash_orchestration_transition_visibility,
)
from orchestration_governance.orchestration_transition_models import (  # noqa: E402
    default_orchestration_transition_visibility,
)
from scripts.report_v4_3_orchestration_coordination_visibility import (  # noqa: E402
    build_v4_3_orchestration_coordination_visibility_report,
)


def test_v4_3_coordination_models_are_immutable_non_executing_and_non_coordinating():
    visibility = default_orchestration_coordination_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.coordination_execution_enabled = True

    assert visibility.identity.schema_version == V4_3_ORCHESTRATION_COORDINATION_SCHEMA_VERSION
    assert visibility.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert visibility.identity.source_topology_hash_reference == hash_orchestration_topology(
        default_orchestration_topology()
    )
    assert visibility.identity.source_capability_hash_reference == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert visibility.identity.source_policy_hash_reference == hash_orchestration_policy_visibility(
        default_orchestration_policy_visibility()
    )
    assert visibility.identity.source_transition_hash_reference == hash_orchestration_transition_visibility(
        default_orchestration_transition_visibility()
    )
    assert visibility.non_executable is True
    assert visibility.non_coordinating is True
    assert visibility.descriptive_only is True
    assert visibility.coordination_execution_enabled is False
    assert visibility.orchestration_dispatch_enabled is False
    assert visibility.runtime_coordination_enabled is False
    assert visibility.orchestration_activation_enabled is False
    assert visibility.routing_execution_enabled is False
    assert visibility.traversal_execution_enabled is False
    assert visibility.scheduling_execution_enabled is False
    assert visibility.dependency_resolution_enabled is False
    assert visibility.transition_execution_enabled is False
    assert visibility.coordination_authorization_enabled is False
    assert visibility.readiness_approval_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.orchestration_coordination_engine_enabled is False
    assert visibility.dispatcher_enabled is False
    assert visibility.runtime_coordinator_enabled is False
    assert visibility.operational_state_machine_enabled is False
    assert enabled_coordination_execution_count(visibility) == 0
    assert enabled_transition_execution_count(visibility) == 0
    assert enabled_policy_enforcement_count(visibility) == 0
    assert enabled_operational_capability_count(visibility) == 0
    assert all(not coordination.executable for coordination in visibility.coordinations)
    assert all(not coordination.dispatch_capable for coordination in visibility.coordinations)
    assert all(not participant.dispatch_capable for participant in visibility.participants)
    assert all(not relationship.routable for relationship in visibility.relationships)


def test_v4_3_coordination_identity_key_is_stable():
    visibility = default_orchestration_coordination_visibility()

    assert coordination_visibility_identity_key(visibility) == (
        "v4_3.orchestration_coordination_visibility.1"
        "|v4_3_orchestration_coordination_visibility_primary"
        "|v4.3.0-phase-6"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_primary"
        f"|{hash_orchestration_topology(default_orchestration_topology())}"
        "|v4_3_orchestration_capability_visibility_primary"
        f"|{hash_orchestration_capability_visibility(default_orchestration_capability_visibility())}"
        "|v4_3_orchestration_policy_visibility_primary"
        f"|{hash_orchestration_policy_visibility(default_orchestration_policy_visibility())}"
        "|v4_3_orchestration_transition_visibility_primary"
        f"|{hash_orchestration_transition_visibility(default_orchestration_transition_visibility())}"
        "|v4_3_coordination_governance_primary"
    )


def test_v4_3_coordination_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_coordination_visibility()
    second = default_orchestration_coordination_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_visibilities_equal(first, second)
    assert serialize_orchestration_coordination_visibility(first) == serialize_orchestration_coordination_visibility(second)
    assert hash_orchestration_coordination_visibility(first) == hash_orchestration_coordination_visibility(second)


def test_v4_3_coordination_ordering_stability_survives_reordered_collections():
    visibility = default_orchestration_coordination_visibility()
    reordered = replace(
        visibility,
        coordinations=tuple(reversed(visibility.coordinations)),
        participants=tuple(reversed(visibility.participants)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )

    assert serialize_orchestration_coordination_visibility(visibility) == serialize_orchestration_coordination_visibility(
        reordered
    )
    assert hash_orchestration_coordination_visibility(visibility) == hash_orchestration_coordination_visibility(reordered)
    exported = export_orchestration_coordination_visibility(reordered)
    assert [item["support_state"] for item in exported["coordinations"]] == [
        COORDINATION_STATE_SUPPORTED,
        COORDINATION_STATE_UNSUPPORTED,
        COORDINATION_STATE_BLOCKED,
        COORDINATION_STATE_STALE,
        COORDINATION_STATE_CONFLICTING,
        COORDINATION_STATE_PROHIBITED,
    ]
    assert [item["participant_id"] for item in exported["participants"]] == [
        "v4_3_coordination_participant_manifest",
        "v4_3_coordination_participant_topology",
        "v4_3_coordination_participant_capability",
        "v4_3_coordination_participant_policy",
        "v4_3_coordination_participant_transition",
        "v4_3_coordination_participant_boundary",
    ]


def test_v4_3_coordination_support_state_visibility_is_fail_visible():
    visibility = default_orchestration_coordination_visibility()
    support = validate_coordination_support_visibility(visibility)

    assert support["valid"] is True
    assert support["prohibited_coordinations_visible"] is True
    assert support["unsupported_coordinations_visible"] is True
    assert support["blocked_coordinations_visible"] is True
    assert support["stale_coordinations_visible"] is True
    assert support["conflicting_coordinations_visible"] is True
    assert support["enabled_coordination_execution_count"] == 0
    assert support["enabled_transition_execution_count"] == 0
    assert support["enabled_policy_enforcement_count"] == 0
    assert support["enabled_operational_capability_count"] == 0
    assert support["duplicate_coordination_ids"] == ()
    assert support["hidden_count"] == 0


def test_v4_3_coordination_duplicate_detection_is_visible():
    visibility = default_orchestration_coordination_visibility()
    duplicate = replace(visibility.coordinations[0], deterministic_order=999)
    contaminated = replace(visibility, coordinations=visibility.coordinations + (duplicate,))
    support = validate_coordination_support_visibility(contaminated)

    assert support["valid"] is False
    assert support["duplicate_coordination_ids"] == (visibility.coordinations[0].coordination_id,)


def test_v4_3_coordination_missing_participant_detection_is_visible():
    visibility = default_orchestration_coordination_visibility()
    missing_reference = replace(
        visibility.participants[0],
        participant_reference_id="",
        deterministic_order=999,
    )
    missing_participant_links = replace(
        visibility.coordinations[0],
        coordination_id="v4_3_coordination_missing_participants",
        participant_ids=(),
        deterministic_order=1000,
    )
    contaminated = replace(
        visibility,
        participants=(missing_reference,) + visibility.participants[1:],
        coordinations=visibility.coordinations + (missing_participant_links,),
    )
    validation = validate_coordination_participants(contaminated)

    assert validation["valid"] is False
    assert validation["missing_participant_references"] == (
        "v4_3_coordination_participant_manifest",
    )
    assert validation["missing_coordination_participant_refs"] == (
        "v4_3_coordination_missing_participants",
    )
    assert validation["invalid_participant_count"] == 2


def test_v4_3_coordination_invalid_relationship_detection_is_visible():
    visibility = default_orchestration_coordination_visibility()
    invalid_policy = replace(
        visibility.relationships[3],
        relationship_id="v4_3_coordination_invalid_policy_relationship",
        target_reference_id="missing_policy",
        deterministic_order=999,
    )
    invalid_capability = replace(
        visibility.relationships[2],
        relationship_id="v4_3_coordination_invalid_capability_relationship",
        target_reference_id="missing_capability",
        deterministic_order=1000,
    )
    invalid_transition = replace(
        visibility.relationships[4],
        relationship_id="v4_3_coordination_invalid_transition_relationship",
        target_reference_id="missing_transition",
        deterministic_order=1001,
    )
    wrong_target_type = replace(
        visibility.relationships[1],
        relationship_id="v4_3_coordination_wrong_target_type_relationship",
        target_reference_type="boundary",
        deterministic_order=1002,
    )
    contaminated = replace(
        visibility,
        relationships=visibility.relationships
        + (invalid_policy, invalid_capability, invalid_transition, wrong_target_type),
    )
    validation = validate_coordination_relationships(contaminated)

    assert validation["valid"] is False
    assert validation["invalid_policy_relationship_ids"] == (
        "v4_3_coordination_invalid_policy_relationship",
    )
    assert validation["invalid_capability_relationship_ids"] == (
        "v4_3_coordination_invalid_capability_relationship",
    )
    assert validation["invalid_transition_relationship_ids"] == (
        "v4_3_coordination_invalid_transition_relationship",
    )
    assert validation["invalid_target_type_relationship_ids"] == (
        "v4_3_coordination_wrong_target_type_relationship",
    )
    assert validation["invalid_relationship_count"] == 4


def test_v4_3_coordination_aggregation_is_deterministic():
    visibility = default_orchestration_coordination_visibility()
    diagnostics = build_coordination_visibility_diagnostics(visibility)

    assert aggregate_prohibited_coordinations(visibility) == diagnostics["prohibited_coordination_ids"]
    assert aggregate_unsupported_coordinations(visibility) == diagnostics["unsupported_coordination_ids"]
    assert aggregate_blocked_coordinations(visibility) == diagnostics["blocked_coordination_ids"]
    assert aggregate_stale_coordinations(visibility) == diagnostics["stale_coordination_ids"]
    assert aggregate_conflicting_coordinations(visibility) == diagnostics["conflicting_coordination_ids"]
    assert diagnostics["enabled_coordination_execution_count"] == 0
    assert diagnostics["enabled_transition_execution_count"] == 0
    assert diagnostics["enabled_policy_enforcement_count"] == 0
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["execution_absent"] is True
    assert diagnostics["dispatch_absent"] is True
    assert diagnostics["repair_absent"] is True
    assert diagnostics["inference_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["mutation_absent"] is True


def test_v4_3_coordination_metadata_continuity_and_explainability_are_valid():
    visibility = default_orchestration_coordination_visibility()
    metadata = validate_coordination_metadata(visibility)
    continuity = validate_coordination_continuity(visibility)
    explainability = validate_coordination_explainability(visibility)

    assert metadata["valid"] is True
    assert metadata["coordination_boundary_metadata_present"] is True
    assert metadata["coordination_policy_metadata_present"] is True
    assert metadata["coordination_transition_metadata_present"] is True
    assert metadata["provenance_metadata_present"] is True
    assert metadata["lineage_metadata_present"] is True
    assert metadata["non_execution_metadata_present"] is True
    assert metadata["non_coordination_metadata_present"] is True
    assert continuity["valid"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert explainability["valid"] is True
    assert "operational_coordination_unavailable" in explainability["explainability_categories"]
    assert "orchestration_dispatch_unavailable" in explainability["explainability_categories"]
    assert "orchestration_activation_unavailable" in explainability["explainability_categories"]
    assert "planner_integration_unavailable" in explainability["explainability_categories"]
    assert "production_consumption_unavailable" in explainability["explainability_categories"]
    assert "governance_constraints_exist" in explainability["explainability_categories"]
    assert "runtime_coordination_prohibited" in explainability["explainability_categories"]


def test_v4_3_coordination_non_execution_and_non_coordination_blocks_operational_flags():
    visibility = default_orchestration_coordination_visibility()
    contaminated_coordination = replace(
        visibility.coordinations[0],
        executable=True,
        dispatch_capable=True,
        activation_capable=True,
        planner_integrated=True,
        production_consuming=True,
        operationally_routable=True,
        schedulable=True,
    )
    contaminated_relationship = replace(
        visibility.relationships[0],
        relationship_id="v4_3_coordination_operational_relationship",
        executable=True,
        dispatch_capable=True,
        routable=True,
        deterministic_order=999,
    )
    contaminated = replace(
        visibility,
        coordinations=(contaminated_coordination,) + visibility.coordinations[1:],
        relationships=(contaminated_relationship,) + visibility.relationships[1:],
        coordination_execution_enabled=True,
        orchestration_dispatch_enabled=True,
        runtime_coordination_enabled=True,
        orchestration_activation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        policy_enforcement_enabled=True,
    )
    validation = validate_coordination_non_execution_and_non_coordination(contaminated)

    assert validate_coordination_non_execution_and_non_coordination(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_coordination_execution_count"] >= 1
    assert validation["enabled_transition_execution_count"] == 0
    assert validation["enabled_policy_enforcement_count"] == 1
    assert validation["enabled_operational_capability_count"] >= 1
    assert validation["coordination_execution_disabled"] is False
    assert validation["runtime_coordination_disabled"] is False
    assert validation["orchestration_dispatch_disabled"] is False
    assert validation["orchestration_activation_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_coordination_report_generation_and_report_hash_are_stable():
    first = build_v4_3_orchestration_coordination_visibility_report()
    second = build_v4_3_orchestration_coordination_visibility_report()

    assert first == second
    assert first["coordination_visibility_status"] == V4_3_ORCHESTRATION_COORDINATION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["coordination_ordering_verified"] is True
    assert first["summary"]["participant_ordering_verified"] is True
    assert first["summary"]["relationship_ordering_verified"] is True
    assert first["summary"]["enabled_coordination_execution_count"] == 0
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["coordination_execution_disabled"] is True
    assert first["summary"]["operational_coordination_disabled"] is True
    assert first["summary"]["runtime_coordination_disabled"] is True
    assert first["summary"]["orchestration_dispatch_disabled"] is True
    assert first["summary"]["orchestration_activation_disabled"] is True
    assert first["summary"]["routing_execution_disabled"] is True
    assert first["summary"]["traversal_execution_disabled"] is True
    assert first["summary"]["scheduling_execution_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert first["summary"]["orchestration_coordination_engine_absent"] is True
    assert first["summary"]["dispatcher_absent"] is True
    assert first["summary"]["runtime_coordinator_absent"] is True
    assert first["summary"]["operational_state_machine_absent"] is True
    assert "No orchestration coordination engine may exist." in EXPLICIT_ORCHESTRATION_COORDINATION_PROHIBITIONS
    assert "No orchestration coordination engine may exist." in first["explicit_prohibitions"]


def test_v4_3_coordination_hashes_are_stable():
    visibility = default_orchestration_coordination_visibility()

    assert [hash_coordination_record(coordination) for coordination in visibility.coordinations] == [
        hash_coordination_record(coordination) for coordination in visibility.coordinations
    ]
    assert [hash_coordination_participant(participant) for participant in visibility.participants] == [
        hash_coordination_participant(participant) for participant in visibility.participants
    ]
    assert [hash_coordination_relationship(relationship) for relationship in visibility.relationships] == [
        hash_coordination_relationship(relationship) for relationship in visibility.relationships
    ]
    assert [hash_coordination_explainability(summary) for summary in visibility.explainability_summaries] == [
        hash_coordination_explainability(summary) for summary in visibility.explainability_summaries
    ]
