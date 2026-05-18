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
from orchestration_governance.orchestration_transition_diagnostics import (  # noqa: E402
    aggregate_blocked_transitions,
    aggregate_conflicting_transitions,
    aggregate_prohibited_transitions,
    aggregate_stale_transitions,
    aggregate_unsupported_transitions,
    build_transition_visibility_diagnostics,
    enabled_operational_capability_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    transition_visibilities_equal,
    transition_visibility_identity_key,
    validate_transition_continuity,
    validate_transition_explainability,
    validate_transition_metadata,
    validate_transition_non_execution_and_non_activation,
    validate_transition_relationships,
    validate_transition_state_visibility,
    validate_transition_support_visibility,
)
from orchestration_governance.orchestration_transition_hashing import (  # noqa: E402
    hash_orchestration_transition_visibility,
    hash_transition_explainability,
    hash_transition_record,
    hash_transition_relationship,
)
from orchestration_governance.orchestration_transition_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_TRANSITION_PROHIBITIONS,
    TRANSITION_STATE_BLOCKED,
    TRANSITION_STATE_CONFLICTING,
    TRANSITION_STATE_PROHIBITED,
    TRANSITION_STATE_STALE,
    TRANSITION_STATE_SUPPORTED,
    TRANSITION_STATE_UNSUPPORTED,
    V4_3_ORCHESTRATION_TRANSITION_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_TRANSITION_STATUS_STABLE,
    default_orchestration_transition_visibility,
)
from orchestration_governance.orchestration_transition_serialization import (  # noqa: E402
    export_orchestration_transition_visibility,
    serialize_orchestration_transition_visibility,
)
from scripts.report_v4_3_orchestration_transition_visibility import (  # noqa: E402
    build_v4_3_orchestration_transition_visibility_report,
)


def test_v4_3_transition_models_are_immutable_non_executing_and_non_activating():
    visibility = default_orchestration_transition_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.transition_execution_enabled = True

    assert visibility.identity.schema_version == V4_3_ORCHESTRATION_TRANSITION_SCHEMA_VERSION
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
    assert visibility.non_executable is True
    assert visibility.non_activating is True
    assert visibility.descriptive_only is True
    assert visibility.transition_execution_enabled is False
    assert visibility.orchestration_activation_enabled is False
    assert visibility.state_progression_enabled is False
    assert visibility.routing_execution_enabled is False
    assert visibility.traversal_execution_enabled is False
    assert visibility.scheduling_execution_enabled is False
    assert visibility.dependency_resolution_enabled is False
    assert visibility.transition_authorization_enabled is False
    assert visibility.readiness_approval_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.transition_engine_enabled is False
    assert visibility.orchestration_runtime_enabled is False
    assert visibility.executable_state_machine_enabled is False
    assert visibility.orchestration_dispatcher_enabled is False
    assert enabled_transition_execution_count(visibility) == 0
    assert enabled_operational_capability_count(visibility) == 0
    assert enabled_policy_enforcement_count(visibility) == 0
    assert all(not transition.executable for transition in visibility.transitions)
    assert all(not transition.activation_capable for transition in visibility.transitions)
    assert all(not relationship.routable for relationship in visibility.relationships)


def test_v4_3_transition_identity_key_is_stable():
    visibility = default_orchestration_transition_visibility()

    assert transition_visibility_identity_key(visibility) == (
        "v4_3.orchestration_transition_visibility.1"
        "|v4_3_orchestration_transition_visibility_primary"
        "|v4.3.0-phase-5"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_primary"
        f"|{hash_orchestration_topology(default_orchestration_topology())}"
        "|v4_3_orchestration_capability_visibility_primary"
        f"|{hash_orchestration_capability_visibility(default_orchestration_capability_visibility())}"
        "|v4_3_orchestration_policy_visibility_primary"
        f"|{hash_orchestration_policy_visibility(default_orchestration_policy_visibility())}"
        "|v4_3_transition_governance_primary"
    )


def test_v4_3_transition_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_transition_visibility()
    second = default_orchestration_transition_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert transition_visibilities_equal(first, second)
    assert serialize_orchestration_transition_visibility(first) == serialize_orchestration_transition_visibility(second)
    assert hash_orchestration_transition_visibility(first) == hash_orchestration_transition_visibility(second)


def test_v4_3_transition_ordering_stability_survives_reordered_collections():
    visibility = default_orchestration_transition_visibility()
    reordered = replace(
        visibility,
        transitions=tuple(reversed(visibility.transitions)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )

    assert serialize_orchestration_transition_visibility(visibility) == serialize_orchestration_transition_visibility(
        reordered
    )
    assert hash_orchestration_transition_visibility(visibility) == hash_orchestration_transition_visibility(reordered)
    exported = export_orchestration_transition_visibility(reordered)
    assert [item["support_state"] for item in exported["transitions"]] == [
        TRANSITION_STATE_SUPPORTED,
        TRANSITION_STATE_UNSUPPORTED,
        TRANSITION_STATE_BLOCKED,
        TRANSITION_STATE_STALE,
        TRANSITION_STATE_CONFLICTING,
        TRANSITION_STATE_PROHIBITED,
    ]


def test_v4_3_transition_support_state_visibility_is_fail_visible():
    visibility = default_orchestration_transition_visibility()
    support = validate_transition_support_visibility(visibility)

    assert support["valid"] is True
    assert support["prohibited_transitions_visible"] is True
    assert support["unsupported_transitions_visible"] is True
    assert support["blocked_transitions_visible"] is True
    assert support["stale_transitions_visible"] is True
    assert support["conflicting_transitions_visible"] is True
    assert support["enabled_transition_execution_count"] == 0
    assert support["enabled_operational_capability_count"] == 0
    assert support["enabled_policy_enforcement_count"] == 0
    assert support["duplicate_transition_ids"] == ()
    assert support["hidden_count"] == 0


def test_v4_3_transition_duplicate_detection_is_visible():
    visibility = default_orchestration_transition_visibility()
    duplicate = replace(visibility.transitions[0], deterministic_order=999)
    contaminated = replace(visibility, transitions=visibility.transitions + (duplicate,))
    support = validate_transition_support_visibility(contaminated)

    assert support["valid"] is False
    assert support["duplicate_transition_ids"] == (visibility.transitions[0].transition_id,)


def test_v4_3_transition_missing_source_and_target_detection_is_visible():
    visibility = default_orchestration_transition_visibility()
    missing_source = replace(
        visibility.transitions[0],
        transition_id="v4_3_transition_missing_source",
        source_state_id="",
        deterministic_order=999,
    )
    missing_target = replace(
        visibility.transitions[1],
        transition_id="v4_3_transition_missing_target",
        target_state_id="",
        deterministic_order=1000,
    )
    self_referential = replace(
        visibility.transitions[2],
        transition_id="v4_3_transition_self_referential",
        source_state_id="same_state",
        target_state_id="same_state",
        deterministic_order=1001,
    )
    contaminated = replace(
        visibility,
        transitions=visibility.transitions + (missing_source, missing_target, self_referential),
    )
    validation = validate_transition_state_visibility(contaminated)

    assert validation["valid"] is False
    assert validation["missing_source_state_ids"] == ("v4_3_transition_missing_source",)
    assert validation["missing_target_state_ids"] == ("v4_3_transition_missing_target",)
    assert validation["self_referential_transition_ids"] == ("v4_3_transition_self_referential",)
    assert validation["invalid_source_to_target_count"] == 3


def test_v4_3_transition_invalid_relationship_detection_is_visible():
    visibility = default_orchestration_transition_visibility()
    invalid_policy = replace(
        visibility.relationships[3],
        relationship_id="v4_3_transition_invalid_policy_relationship",
        target_reference_id="missing_policy",
        deterministic_order=999,
    )
    invalid_capability = replace(
        visibility.relationships[2],
        relationship_id="v4_3_transition_invalid_capability_relationship",
        target_reference_id="missing_capability",
        deterministic_order=1000,
    )
    wrong_target_type = replace(
        visibility.relationships[1],
        relationship_id="v4_3_transition_wrong_target_type_relationship",
        target_reference_type="boundary",
        deterministic_order=1001,
    )
    contaminated = replace(
        visibility,
        relationships=visibility.relationships + (invalid_policy, invalid_capability, wrong_target_type),
    )
    validation = validate_transition_relationships(contaminated)

    assert validation["valid"] is False
    assert validation["invalid_policy_relationship_ids"] == (
        "v4_3_transition_invalid_policy_relationship",
    )
    assert validation["invalid_capability_relationship_ids"] == (
        "v4_3_transition_invalid_capability_relationship",
    )
    assert validation["invalid_target_type_relationship_ids"] == (
        "v4_3_transition_wrong_target_type_relationship",
    )
    assert validation["invalid_relationship_count"] == 3


def test_v4_3_transition_aggregation_is_deterministic():
    visibility = default_orchestration_transition_visibility()
    diagnostics = build_transition_visibility_diagnostics(visibility)

    assert aggregate_prohibited_transitions(visibility) == diagnostics["prohibited_transition_ids"]
    assert aggregate_unsupported_transitions(visibility) == diagnostics["unsupported_transition_ids"]
    assert aggregate_blocked_transitions(visibility) == diagnostics["blocked_transition_ids"]
    assert aggregate_stale_transitions(visibility) == diagnostics["stale_transition_ids"]
    assert aggregate_conflicting_transitions(visibility) == diagnostics["conflicting_transition_ids"]
    assert diagnostics["enabled_transition_execution_count"] == 0
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["enabled_policy_enforcement_count"] == 0
    assert diagnostics["execution_absent"] is True
    assert diagnostics["repair_absent"] is True
    assert diagnostics["inference_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["mutation_absent"] is True
    assert diagnostics["activation_absent"] is True


def test_v4_3_transition_metadata_continuity_and_explainability_are_valid():
    visibility = default_orchestration_transition_visibility()
    metadata = validate_transition_metadata(visibility)
    continuity = validate_transition_continuity(visibility)
    explainability = validate_transition_explainability(visibility)

    assert metadata["valid"] is True
    assert metadata["transition_boundary_metadata_present"] is True
    assert metadata["transition_policy_metadata_present"] is True
    assert metadata["provenance_metadata_present"] is True
    assert metadata["lineage_metadata_present"] is True
    assert metadata["non_execution_metadata_present"] is True
    assert metadata["non_activation_metadata_present"] is True
    assert continuity["valid"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert explainability["valid"] is True
    assert "transition_execution_unavailable" in explainability["explainability_categories"]
    assert "orchestration_activation_unavailable" in explainability["explainability_categories"]
    assert "state_progression_unavailable" in explainability["explainability_categories"]
    assert "planner_integration_unavailable" in explainability["explainability_categories"]
    assert "production_consumption_unavailable" in explainability["explainability_categories"]
    assert "governance_constraints_exist" in explainability["explainability_categories"]
    assert "operational_orchestration_prohibited" in explainability["explainability_categories"]


def test_v4_3_transition_non_execution_and_non_activation_blocks_operational_flags():
    visibility = default_orchestration_transition_visibility()
    contaminated_transition = replace(
        visibility.transitions[0],
        executable=True,
        activation_capable=True,
        state_progression_enabled=True,
        planner_integrated=True,
        production_consuming=True,
        operationally_routable=True,
        schedulable=True,
    )
    contaminated = replace(
        visibility,
        transitions=(contaminated_transition,) + visibility.transitions[1:],
        transition_execution_enabled=True,
        orchestration_activation_enabled=True,
        state_progression_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        policy_enforcement_enabled=True,
    )
    validation = validate_transition_non_execution_and_non_activation(contaminated)

    assert validate_transition_non_execution_and_non_activation(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_transition_execution_count"] >= 1
    assert validation["enabled_operational_capability_count"] >= 1
    assert validation["enabled_policy_enforcement_count"] == 1
    assert validation["transition_execution_disabled"] is False
    assert validation["orchestration_activation_disabled"] is False
    assert validation["state_progression_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_transition_report_generation_and_report_hash_are_stable():
    first = build_v4_3_orchestration_transition_visibility_report()
    second = build_v4_3_orchestration_transition_visibility_report()

    assert first == second
    assert first["transition_visibility_status"] == V4_3_ORCHESTRATION_TRANSITION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["transition_ordering_verified"] is True
    assert first["summary"]["relationship_ordering_verified"] is True
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["transition_execution_disabled"] is True
    assert first["summary"]["orchestration_activation_disabled"] is True
    assert first["summary"]["state_progression_disabled"] is True
    assert first["summary"]["routing_execution_disabled"] is True
    assert first["summary"]["traversal_execution_disabled"] is True
    assert first["summary"]["scheduling_execution_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert first["summary"]["transition_engine_absent"] is True
    assert first["summary"]["orchestration_runtime_absent"] is True
    assert first["summary"]["executable_state_machine_absent"] is True
    assert first["summary"]["orchestration_dispatcher_absent"] is True
    assert "No transition engine may exist." in EXPLICIT_ORCHESTRATION_TRANSITION_PROHIBITIONS
    assert "No transition engine may exist." in first["explicit_prohibitions"]


def test_v4_3_transition_hashes_are_stable():
    visibility = default_orchestration_transition_visibility()

    assert [hash_transition_record(transition) for transition in visibility.transitions] == [
        hash_transition_record(transition) for transition in visibility.transitions
    ]
    assert [hash_transition_relationship(relationship) for relationship in visibility.relationships] == [
        hash_transition_relationship(relationship) for relationship in visibility.relationships
    ]
    assert [hash_transition_explainability(summary) for summary in visibility.explainability_summaries] == [
        hash_transition_explainability(summary) for summary in visibility.explainability_summaries
    ]
