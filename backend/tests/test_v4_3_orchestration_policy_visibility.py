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
from orchestration_governance.orchestration_policy_diagnostics import (  # noqa: E402
    aggregate_blocked_policies,
    aggregate_conflicting_policies,
    aggregate_prohibited_policies,
    aggregate_stale_policies,
    aggregate_unsupported_policies,
    build_policy_visibility_diagnostics,
    enabled_operational_capability_count,
    enabled_policy_enforcement_count,
    policy_visibilities_equal,
    policy_visibility_identity_key,
    validate_policy_continuity,
    validate_policy_explainability,
    validate_policy_metadata,
    validate_policy_non_execution_and_non_enforcement,
    validate_policy_relationships,
    validate_policy_support_visibility,
    validate_policy_targets,
)
from orchestration_governance.orchestration_policy_hashing import (  # noqa: E402
    hash_orchestration_policy_visibility,
    hash_policy_explainability,
    hash_policy_record,
    hash_policy_relationship,
    hash_policy_target,
)
from orchestration_governance.orchestration_policy_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_POLICY_PROHIBITIONS,
    POLICY_STATE_BLOCKED,
    POLICY_STATE_CONFLICTING,
    POLICY_STATE_PROHIBITED,
    POLICY_STATE_STALE,
    POLICY_STATE_SUPPORTED,
    POLICY_STATE_UNSUPPORTED,
    V4_3_ORCHESTRATION_POLICY_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_POLICY_STATUS_STABLE,
    default_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_policy_serialization import (  # noqa: E402
    export_orchestration_policy_visibility,
    serialize_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_topology_hashing import hash_orchestration_topology  # noqa: E402
from orchestration_governance.orchestration_topology_models import default_orchestration_topology  # noqa: E402
from scripts.report_v4_3_orchestration_policy_visibility import (  # noqa: E402
    build_v4_3_orchestration_policy_visibility_report,
)


def test_v4_3_policy_models_are_immutable_non_enforcing_and_non_executable():
    visibility = default_orchestration_policy_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.policy_enforcement_enabled = True

    assert visibility.identity.schema_version == V4_3_ORCHESTRATION_POLICY_SCHEMA_VERSION
    assert visibility.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert visibility.identity.source_topology_hash_reference == hash_orchestration_topology(
        default_orchestration_topology()
    )
    assert visibility.identity.source_capability_hash_reference == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert visibility.non_enforceable is True
    assert visibility.non_executable is True
    assert visibility.descriptive_only is True
    assert visibility.policy_enforcement_enabled is False
    assert visibility.policy_enforcement_execution_enabled is False
    assert visibility.orchestration_execution_enabled is False
    assert visibility.runtime_execution_enabled is False
    assert visibility.policy_driven_routing_enabled is False
    assert visibility.policy_driven_traversal_enabled is False
    assert visibility.policy_driven_scheduling_enabled is False
    assert visibility.policy_driven_dependency_resolution_enabled is False
    assert visibility.orchestration_authorization_enabled is False
    assert visibility.readiness_approval_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.policy_engine_execution_enabled is False
    assert visibility.orchestration_engine_enabled is False
    assert visibility.authorization_engine_enabled is False
    assert visibility.activation_pathway_enabled is False
    assert enabled_policy_enforcement_count(visibility) == 0
    assert enabled_operational_capability_count(visibility) == 0
    assert all(not policy.enforceable for policy in visibility.policies)
    assert all(not policy.authorizing for policy in visibility.policies)
    assert all(not relationship.routable for relationship in visibility.relationships)


def test_v4_3_policy_identity_key_is_stable():
    visibility = default_orchestration_policy_visibility()

    assert policy_visibility_identity_key(visibility) == (
        "v4_3.orchestration_policy_visibility.1"
        "|v4_3_orchestration_policy_visibility_primary"
        "|v4.3.0-phase-4"
        "|v4_3_orchestration_manifest_primary"
        f"|{hash_orchestration_manifest(default_orchestration_manifest())}"
        "|v4_3_orchestration_topology_primary"
        f"|{hash_orchestration_topology(default_orchestration_topology())}"
        "|v4_3_orchestration_capability_visibility_primary"
        f"|{hash_orchestration_capability_visibility(default_orchestration_capability_visibility())}"
        "|v4_3_policy_governance_primary"
    )


def test_v4_3_policy_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_policy_visibility()
    second = default_orchestration_policy_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert policy_visibilities_equal(first, second)
    assert serialize_orchestration_policy_visibility(first) == serialize_orchestration_policy_visibility(second)
    assert hash_orchestration_policy_visibility(first) == hash_orchestration_policy_visibility(second)


def test_v4_3_policy_ordering_stability_survives_reordered_collections():
    visibility = default_orchestration_policy_visibility()
    reordered = replace(
        visibility,
        policies=tuple(reversed(visibility.policies)),
        targets=tuple(reversed(visibility.targets)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )

    assert serialize_orchestration_policy_visibility(visibility) == serialize_orchestration_policy_visibility(
        reordered
    )
    assert hash_orchestration_policy_visibility(visibility) == hash_orchestration_policy_visibility(reordered)
    exported = export_orchestration_policy_visibility(reordered)
    assert [item["support_state"] for item in exported["policies"]] == [
        POLICY_STATE_SUPPORTED,
        POLICY_STATE_UNSUPPORTED,
        POLICY_STATE_BLOCKED,
        POLICY_STATE_STALE,
        POLICY_STATE_CONFLICTING,
        POLICY_STATE_PROHIBITED,
    ]


def test_v4_3_policy_support_state_visibility_is_fail_visible():
    visibility = default_orchestration_policy_visibility()
    support = validate_policy_support_visibility(visibility)

    assert support["valid"] is True
    assert support["prohibited_policies_visible"] is True
    assert support["unsupported_policies_visible"] is True
    assert support["blocked_policies_visible"] is True
    assert support["stale_policies_visible"] is True
    assert support["conflicting_policies_visible"] is True
    assert support["enabled_policy_enforcement_count"] == 0
    assert support["enabled_operational_capability_count"] == 0
    assert support["duplicate_policy_ids"] == ()
    assert support["hidden_count"] == 0


def test_v4_3_policy_duplicate_detection_is_visible():
    visibility = default_orchestration_policy_visibility()
    duplicate = replace(visibility.policies[0], deterministic_order=999)
    contaminated = replace(visibility, policies=visibility.policies + (duplicate,))
    support = validate_policy_support_visibility(contaminated)

    assert support["valid"] is False
    assert support["duplicate_policy_ids"] == (visibility.policies[0].policy_id,)


def test_v4_3_policy_missing_target_detection_is_visible():
    visibility = default_orchestration_policy_visibility()
    policy_without_target = replace(visibility.policies[0], target_ids=())
    blank_target = replace(
        visibility.targets[0],
        target_id="",
        target_reference_id="",
        policy_ids=(),
    )
    contaminated = replace(
        visibility,
        policies=(policy_without_target,) + visibility.policies[1:],
        targets=(blank_target,) + visibility.targets[1:],
    )
    validation = validate_policy_targets(contaminated)

    assert validation["valid"] is False
    assert policy_without_target.policy_id in validation["missing_policy_target_ids"]
    assert validation["missing_target_references"] == ("",)
    assert validation["missing_target_policy_refs"] == ("",)
    assert validation["invalid_target_count"] >= 3


def test_v4_3_policy_invalid_relationship_detection_is_visible():
    visibility = default_orchestration_policy_visibility()
    missing_manifest_target = replace(
        visibility.relationships[0],
        relationship_id="v4_3_policy_invalid_manifest_relationship",
        target_reference_id="missing_manifest",
        deterministic_order=999,
    )
    wrong_target_type = replace(
        visibility.relationships[1],
        relationship_id="v4_3_policy_wrong_target_type_relationship",
        target_reference_type="boundary",
        deterministic_order=1000,
    )
    unknown_policy = replace(
        visibility.relationships[2],
        relationship_id="v4_3_policy_unknown_source_relationship",
        source_policy_id="missing_policy",
        deterministic_order=1001,
    )
    contaminated = replace(
        visibility,
        relationships=visibility.relationships
        + (missing_manifest_target, wrong_target_type, unknown_policy),
    )
    validation = validate_policy_relationships(contaminated)

    assert validation["valid"] is False
    assert validation["invalid_manifest_relationship_ids"] == (
        "v4_3_policy_invalid_manifest_relationship",
    )
    assert validation["invalid_target_type_relationship_ids"] == (
        "v4_3_policy_wrong_target_type_relationship",
    )
    assert validation["unknown_policy_relationship_ids"] == (
        "v4_3_policy_unknown_source_relationship",
    )
    assert validation["invalid_relationship_count"] == 3


def test_v4_3_policy_aggregation_is_deterministic():
    visibility = default_orchestration_policy_visibility()
    diagnostics = build_policy_visibility_diagnostics(visibility)

    assert aggregate_prohibited_policies(visibility) == diagnostics["prohibited_policy_ids"]
    assert aggregate_unsupported_policies(visibility) == diagnostics["unsupported_policy_ids"]
    assert aggregate_blocked_policies(visibility) == diagnostics["blocked_policy_ids"]
    assert aggregate_stale_policies(visibility) == diagnostics["stale_policy_ids"]
    assert aggregate_conflicting_policies(visibility) == diagnostics["conflicting_policy_ids"]
    assert diagnostics["enabled_policy_enforcement_count"] == 0
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["repair_absent"] is True
    assert diagnostics["inference_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert diagnostics["operational_mutation_absent"] is True
    assert diagnostics["policy_enforcement_absent"] is True
    assert diagnostics["execution_absent"] is True


def test_v4_3_policy_metadata_continuity_and_explainability_are_valid():
    visibility = default_orchestration_policy_visibility()
    metadata = validate_policy_metadata(visibility)
    continuity = validate_policy_continuity(visibility)
    explainability = validate_policy_explainability(visibility)

    assert metadata["valid"] is True
    assert metadata["governance_metadata_present"] is True
    assert metadata["policy_scope_metadata_present"] is True
    assert metadata["policy_target_metadata_present"] is True
    assert metadata["provenance_metadata_present"] is True
    assert metadata["lineage_metadata_present"] is True
    assert metadata["non_enforcement_metadata_present"] is True
    assert metadata["non_execution_metadata_present"] is True
    assert continuity["valid"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert explainability["valid"] is True
    assert "policy_enforcement_unavailable" in explainability["explainability_categories"]
    assert "authorization_unavailable" in explainability["explainability_categories"]
    assert "activation_unavailable" in explainability["explainability_categories"]
    assert "execution_unavailable" in explainability["explainability_categories"]
    assert "planner_integration_unavailable" in explainability["explainability_categories"]
    assert "production_consumption_unavailable" in explainability["explainability_categories"]
    assert "governance_constraints_exist" in explainability["explainability_categories"]


def test_v4_3_policy_non_execution_and_non_enforcement_blocks_operational_flags():
    visibility = default_orchestration_policy_visibility()
    contaminated_policy = replace(
        visibility.policies[0],
        enforceable=True,
        authorizing=True,
        activation_capable=True,
        planner_integrated=True,
        production_consuming=True,
    )
    contaminated = replace(
        visibility,
        policies=(contaminated_policy,) + visibility.policies[1:],
        policy_enforcement_enabled=True,
        policy_enforcement_execution_enabled=True,
        policy_driven_activation_enabled=True,
        orchestration_authorization_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_policy_non_execution_and_non_enforcement(contaminated)

    assert validate_policy_non_execution_and_non_enforcement(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_policy_enforcement_count"] >= 1
    assert validation["enabled_operational_capability_count"] >= 1
    assert validation["policy_enforcement_disabled"] is False
    assert validation["policy_enforcement_execution_disabled"] is False
    assert validation["policy_driven_activation_disabled"] is False
    assert validation["orchestration_authorization_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_policy_report_generation_and_report_hash_are_stable():
    first = build_v4_3_orchestration_policy_visibility_report()
    second = build_v4_3_orchestration_policy_visibility_report()

    assert first == second
    assert first["policy_visibility_status"] == V4_3_ORCHESTRATION_POLICY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["policy_ordering_verified"] is True
    assert first["summary"]["target_ordering_verified"] is True
    assert first["summary"]["relationship_ordering_verified"] is True
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["policy_enforcement_disabled"] is True
    assert first["summary"]["orchestration_execution_disabled"] is True
    assert first["summary"]["policy_driven_routing_disabled"] is True
    assert first["summary"]["policy_driven_traversal_disabled"] is True
    assert first["summary"]["policy_driven_scheduling_disabled"] is True
    assert first["summary"]["policy_driven_dependency_resolution_disabled"] is True
    assert first["summary"]["policy_driven_activation_disabled"] is True
    assert first["summary"]["orchestration_authorization_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert first["summary"]["policy_engine_execution_absent"] is True
    assert first["summary"]["orchestration_engine_absent"] is True
    assert first["summary"]["authorization_engine_absent"] is True
    assert first["summary"]["activation_pathway_absent"] is True
    assert "No policy engine may execute." in EXPLICIT_ORCHESTRATION_POLICY_PROHIBITIONS
    assert "No policy engine may execute." in first["explicit_prohibitions"]


def test_v4_3_policy_hashes_are_stable():
    visibility = default_orchestration_policy_visibility()

    assert [hash_policy_record(policy) for policy in visibility.policies] == [
        hash_policy_record(policy) for policy in visibility.policies
    ]
    assert [hash_policy_target(target) for target in visibility.targets] == [
        hash_policy_target(target) for target in visibility.targets
    ]
    assert [hash_policy_relationship(relationship) for relationship in visibility.relationships] == [
        hash_policy_relationship(relationship) for relationship in visibility.relationships
    ]
    assert [hash_policy_explainability(summary) for summary in visibility.explainability_summaries] == [
        hash_policy_explainability(summary) for summary in visibility.explainability_summaries
    ]
