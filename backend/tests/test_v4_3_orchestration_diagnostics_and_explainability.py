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
from orchestration_governance.orchestration_coordination_hashing import (  # noqa: E402
    hash_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_coordination_models import (  # noqa: E402
    default_orchestration_coordination_visibility,
)
from orchestration_governance.orchestration_diagnostics_aggregation import (  # noqa: E402
    build_orchestration_diagnostics_aggregation_diagnostics,
    diagnostics_aggregation_identity_key,
    diagnostics_aggregations_equal,
    enabled_coordination_execution_count,
    enabled_operational_capability_count,
    enabled_orchestration_decision_count,
    enabled_orchestration_recommendation_count,
    enabled_policy_enforcement_count,
    enabled_transition_execution_count,
    validate_diagnostics_aggregation_explainability,
    validate_diagnostics_aggregation_identity,
    validate_diagnostics_aggregation_layers,
    validate_diagnostics_aggregation_non_execution_and_non_decision,
    validate_diagnostics_aggregation_state_visibility,
)
from orchestration_governance.orchestration_diagnostics_aggregation import (  # noqa: E402
    default_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_diagnostics_hashing import (  # noqa: E402
    hash_aggregated_diagnostic_finding,
    hash_aggregated_explainability_summary,
    hash_cross_layer_state_summary,
    hash_governance_layer_diagnostic_summary,
    hash_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_diagnostics_models import (  # noqa: E402
    CROSS_LAYER_STATE_BLOCKED,
    CROSS_LAYER_STATE_CONFLICTING,
    CROSS_LAYER_STATE_PROHIBITED,
    CROSS_LAYER_STATE_STALE,
    CROSS_LAYER_STATE_UNSUPPORTED,
    EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS,
    GOVERNANCE_LAYER_IDS,
    V4_3_ORCHESTRATION_DIAGNOSTICS_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_STABLE,
)
from orchestration_governance.orchestration_diagnostics_serialization import (  # noqa: E402
    export_orchestration_diagnostics_aggregation,
    serialize_orchestration_diagnostics_aggregation,
)
from orchestration_governance.orchestration_manifest_hashing import (  # noqa: E402
    hash_orchestration_manifest,
)
from orchestration_governance.orchestration_manifest_models import (  # noqa: E402
    default_orchestration_manifest,
)
from orchestration_governance.orchestration_policy_hashing import (  # noqa: E402
    hash_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_policy_models import (  # noqa: E402
    default_orchestration_policy_visibility,
)
from orchestration_governance.orchestration_topology_hashing import (  # noqa: E402
    hash_orchestration_topology,
)
from orchestration_governance.orchestration_topology_models import (  # noqa: E402
    default_orchestration_topology,
)
from orchestration_governance.orchestration_transition_hashing import (  # noqa: E402
    hash_orchestration_transition_visibility,
)
from orchestration_governance.orchestration_transition_models import (  # noqa: E402
    default_orchestration_transition_visibility,
)
from scripts.report_v4_3_orchestration_diagnostics_and_explainability import (  # noqa: E402
    build_v4_3_orchestration_diagnostics_and_explainability_report,
)


def test_v4_3_diagnostics_aggregation_models_are_immutable_non_executing_and_non_decisioning():
    aggregation = default_orchestration_diagnostics_aggregation()

    with pytest.raises(FrozenInstanceError):
        aggregation.orchestration_decision_enabled = True

    assert aggregation.identity.schema_version == V4_3_ORCHESTRATION_DIAGNOSTICS_SCHEMA_VERSION
    assert aggregation.identity.source_manifest_hash_reference == hash_orchestration_manifest(
        default_orchestration_manifest()
    )
    assert aggregation.identity.source_topology_hash_reference == hash_orchestration_topology(
        default_orchestration_topology()
    )
    assert aggregation.identity.source_capability_hash_reference == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert aggregation.identity.source_policy_hash_reference == hash_orchestration_policy_visibility(
        default_orchestration_policy_visibility()
    )
    assert aggregation.identity.source_transition_hash_reference == hash_orchestration_transition_visibility(
        default_orchestration_transition_visibility()
    )
    assert aggregation.identity.source_coordination_hash_reference == hash_orchestration_coordination_visibility(
        default_orchestration_coordination_visibility()
    )
    assert aggregation.non_executable is True
    assert aggregation.non_decisioning is True
    assert aggregation.descriptive_only is True
    assert aggregation.orchestration_execution_enabled is False
    assert aggregation.orchestration_intelligence_execution_enabled is False
    assert aggregation.orchestration_recommendation_enabled is False
    assert aggregation.orchestration_decision_enabled is False
    assert aggregation.orchestration_dispatch_enabled is False
    assert aggregation.orchestration_activation_enabled is False
    assert aggregation.runtime_coordination_enabled is False
    assert aggregation.routing_execution_enabled is False
    assert aggregation.traversal_execution_enabled is False
    assert aggregation.scheduling_execution_enabled is False
    assert aggregation.dependency_resolution_enabled is False
    assert aggregation.planner_integration_enabled is False
    assert aggregation.production_consumption_enabled is False
    assert enabled_coordination_execution_count(aggregation) == 0
    assert enabled_transition_execution_count(aggregation) == 0
    assert enabled_policy_enforcement_count(aggregation) == 0
    assert enabled_operational_capability_count(aggregation) == 0
    assert enabled_orchestration_decision_count(aggregation) == 0
    assert enabled_orchestration_recommendation_count(aggregation) == 0


def test_v4_3_diagnostics_aggregation_identity_key_is_stable():
    aggregation = default_orchestration_diagnostics_aggregation()

    assert diagnostics_aggregation_identity_key(aggregation) == (
        "v4_3.orchestration_diagnostics_and_explainability.1"
        "|v4_3_orchestration_diagnostics_and_explainability_primary"
        "|v4.3.0-phase-7"
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
        "|v4_3_orchestration_coordination_visibility_primary"
        f"|{hash_orchestration_coordination_visibility(default_orchestration_coordination_visibility())}"
        "|v4_3_diagnostics_aggregation_governance_primary"
    )


def test_v4_3_diagnostics_aggregation_serialization_hashing_and_equality_are_stable():
    first = default_orchestration_diagnostics_aggregation()
    second = default_orchestration_diagnostics_aggregation()

    assert first == second
    assert hash(first) == hash(second)
    assert diagnostics_aggregations_equal(first, second)
    assert serialize_orchestration_diagnostics_aggregation(first) == serialize_orchestration_diagnostics_aggregation(
        second
    )
    assert hash_orchestration_diagnostics_aggregation(first) == hash_orchestration_diagnostics_aggregation(second)


def test_v4_3_diagnostics_aggregation_ordering_survives_reordered_collections():
    aggregation = default_orchestration_diagnostics_aggregation()
    reordered = replace(
        aggregation,
        governance_layer_summaries=tuple(reversed(aggregation.governance_layer_summaries)),
        diagnostics=tuple(reversed(aggregation.diagnostics)),
        explainability_summaries=tuple(reversed(aggregation.explainability_summaries)),
        cross_layer_state_summaries=tuple(reversed(aggregation.cross_layer_state_summaries)),
    )

    assert serialize_orchestration_diagnostics_aggregation(
        aggregation
    ) == serialize_orchestration_diagnostics_aggregation(reordered)
    assert hash_orchestration_diagnostics_aggregation(aggregation) == hash_orchestration_diagnostics_aggregation(
        reordered
    )
    exported = export_orchestration_diagnostics_aggregation(reordered)
    assert [item["layer_id"] for item in exported["governance_layer_summaries"]] == list(GOVERNANCE_LAYER_IDS)
    assert [item["state_type"] for item in exported["cross_layer_state_summaries"]] == [
        CROSS_LAYER_STATE_PROHIBITED,
        CROSS_LAYER_STATE_UNSUPPORTED,
        CROSS_LAYER_STATE_BLOCKED,
        CROSS_LAYER_STATE_STALE,
        CROSS_LAYER_STATE_CONFLICTING,
    ]


def test_v4_3_diagnostics_aggregation_cross_layer_state_visibility_is_fail_visible():
    aggregation = default_orchestration_diagnostics_aggregation()
    visibility = validate_diagnostics_aggregation_state_visibility(aggregation)

    assert visibility["valid"] is True
    assert visibility["prohibited_states_visible"] is True
    assert visibility["unsupported_states_visible"] is True
    assert visibility["blocked_states_visible"] is True
    assert visibility["stale_states_visible"] is True
    assert visibility["conflicting_states_visible"] is True
    assert visibility["prohibited_state_count"] > 0
    assert visibility["unsupported_state_count"] > 0
    assert visibility["blocked_state_count"] > 0
    assert visibility["stale_state_count"] > 0
    assert visibility["conflicting_state_count"] > 0


def test_v4_3_diagnostics_aggregation_layer_validation_is_stable():
    aggregation = default_orchestration_diagnostics_aggregation()
    identity = validate_diagnostics_aggregation_identity(aggregation)
    layers = validate_diagnostics_aggregation_layers(aggregation)

    assert identity["valid"] is True
    assert identity["source_hash_mismatches"] == ()
    assert layers["valid"] is True
    assert layers["layer_ids"] == tuple(sorted(GOVERNANCE_LAYER_IDS))
    assert layers["governance_layer_summary_count"] == len(GOVERNANCE_LAYER_IDS)
    assert layers["continuity_diagnostics_visible"] is True
    assert layers["provenance_diagnostics_visible"] is True
    assert layers["lineage_diagnostics_visible"] is True


def test_v4_3_diagnostics_aggregation_detects_duplicate_layer_ids():
    aggregation = default_orchestration_diagnostics_aggregation()
    duplicate = replace(aggregation.governance_layer_summaries[0], deterministic_order=999)
    contaminated = replace(
        aggregation,
        governance_layer_summaries=aggregation.governance_layer_summaries + (duplicate,),
    )
    layers = validate_diagnostics_aggregation_layers(contaminated)

    assert layers["valid"] is False
    assert layers["duplicate_layer_ids"] == (aggregation.governance_layer_summaries[0].layer_id,)


def test_v4_3_diagnostics_aggregation_explainability_is_complete_and_stable():
    aggregation = default_orchestration_diagnostics_aggregation()
    explainability = validate_diagnostics_aggregation_explainability(aggregation)

    assert explainability["valid"] is True
    assert explainability["missing_explainability_categories"] == ()
    assert "orchestration_non_executable" in explainability["explainability_categories"]
    assert "orchestration_activation_unavailable" in explainability["explainability_categories"]
    assert "orchestration_coordination_unavailable" in explainability["explainability_categories"]
    assert "planner_integration_unavailable" in explainability["explainability_categories"]
    assert "production_consumption_unavailable" in explainability["explainability_categories"]
    assert "operational_orchestration_prohibited" in explainability["explainability_categories"]
    assert "orchestration_decision_making_prohibited" in explainability["explainability_categories"]
    assert "orchestration_recommendations_prohibited" in explainability["explainability_categories"]
    assert explainability["deterministic"] is True
    assert explainability["replay_safe"] is True
    assert explainability["rollback_safe"] is True


def test_v4_3_diagnostics_aggregation_is_descriptive_only():
    aggregation = default_orchestration_diagnostics_aggregation()
    diagnostics = build_orchestration_diagnostics_aggregation_diagnostics(aggregation)

    assert diagnostics["aggregated_diagnostics_count"] == len(aggregation.diagnostics)
    assert diagnostics["aggregated_explainability_count"] == len(aggregation.explainability_summaries)
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["explainability_is_descriptive_only"] is True
    assert diagnostics["enabled_coordination_execution_count"] == 0
    assert diagnostics["enabled_transition_execution_count"] == 0
    assert diagnostics["enabled_policy_enforcement_count"] == 0
    assert diagnostics["enabled_operational_capability_count"] == 0
    assert diagnostics["enabled_orchestration_decision_count"] == 0
    assert diagnostics["enabled_orchestration_recommendation_count"] == 0


def test_v4_3_diagnostics_aggregation_non_execution_and_non_decision_blocks_operational_flags():
    aggregation = default_orchestration_diagnostics_aggregation()
    contaminated_diagnostic = replace(
        aggregation.diagnostics[0],
        decision_enabled=True,
        recommendation_enabled=True,
        ranking_enabled=True,
    )
    contaminated_explanation = replace(
        aggregation.explainability_summaries[0],
        decision_enabled=True,
        recommendation_enabled=True,
    )
    contaminated = replace(
        aggregation,
        diagnostics=(contaminated_diagnostic,) + aggregation.diagnostics[1:],
        explainability_summaries=(contaminated_explanation,) + aggregation.explainability_summaries[1:],
        orchestration_execution_enabled=True,
        orchestration_decision_enabled=True,
        orchestration_recommendation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
    )
    validation = validate_diagnostics_aggregation_non_execution_and_non_decision(contaminated)

    assert validate_diagnostics_aggregation_non_execution_and_non_decision(aggregation)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_operational_capability_count"] == 1
    assert validation["enabled_orchestration_decision_count"] == 1
    assert validation["enabled_orchestration_recommendation_count"] == 1
    assert validation["orchestration_execution_disabled"] is False
    assert validation["orchestration_decision_disabled"] is False
    assert validation["orchestration_recommendation_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False


def test_v4_3_diagnostics_aggregation_report_generation_and_hash_are_stable():
    first = build_v4_3_orchestration_diagnostics_and_explainability_report()
    second = build_v4_3_orchestration_diagnostics_and_explainability_report()

    assert first == second
    assert first["diagnostics_aggregation_status"] == V4_3_ORCHESTRATION_DIAGNOSTICS_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["governance_layer_ordering_verified"] is True
    assert first["summary"]["diagnostics_ordering_verified"] is True
    assert first["summary"]["explainability_ordering_verified"] is True
    assert first["summary"]["state_summary_ordering_verified"] is True
    assert first["summary"]["enabled_coordination_execution_count"] == 0
    assert first["summary"]["enabled_transition_execution_count"] == 0
    assert first["summary"]["enabled_policy_enforcement_count"] == 0
    assert first["summary"]["enabled_operational_capability_count"] == 0
    assert first["summary"]["enabled_orchestration_decision_count"] == 0
    assert first["summary"]["enabled_orchestration_recommendation_count"] == 0
    assert first["summary"]["orchestration_execution_disabled"] is True
    assert first["summary"]["orchestration_recommendation_disabled"] is True
    assert first["summary"]["orchestration_decision_disabled"] is True
    assert first["summary"]["planner_integration_disabled"] is True
    assert first["summary"]["production_consumption_disabled"] is True
    assert "No orchestration decision engine may exist." in EXPLICIT_ORCHESTRATION_DIAGNOSTICS_PROHIBITIONS
    assert "No orchestration decision engine may exist." in first["explicit_prohibitions"]


def test_v4_3_diagnostics_aggregation_component_hashes_are_stable():
    aggregation = default_orchestration_diagnostics_aggregation()

    assert [
        hash_governance_layer_diagnostic_summary(summary)
        for summary in aggregation.governance_layer_summaries
    ] == [
        hash_governance_layer_diagnostic_summary(summary)
        for summary in aggregation.governance_layer_summaries
    ]
    assert [hash_aggregated_diagnostic_finding(diagnostic) for diagnostic in aggregation.diagnostics] == [
        hash_aggregated_diagnostic_finding(diagnostic) for diagnostic in aggregation.diagnostics
    ]
    assert [
        hash_aggregated_explainability_summary(summary)
        for summary in aggregation.explainability_summaries
    ] == [
        hash_aggregated_explainability_summary(summary)
        for summary in aggregation.explainability_summaries
    ]
    assert [
        hash_cross_layer_state_summary(summary) for summary in aggregation.cross_layer_state_summaries
    ] == [
        hash_cross_layer_state_summary(summary) for summary in aggregation.cross_layer_state_summaries
    ]


def test_v4_3_diagnostics_aggregation_is_compatible_with_phase_1_through_6_artifacts():
    aggregation = default_orchestration_diagnostics_aggregation()
    layer_hashes = {
        summary.layer_id: summary.source_hash_reference
        for summary in aggregation.governance_layer_summaries
    }

    assert layer_hashes["manifest"] == hash_orchestration_manifest(default_orchestration_manifest())
    assert layer_hashes["topology"] == hash_orchestration_topology(default_orchestration_topology())
    assert layer_hashes["capability"] == hash_orchestration_capability_visibility(
        default_orchestration_capability_visibility()
    )
    assert layer_hashes["policy"] == hash_orchestration_policy_visibility(
        default_orchestration_policy_visibility()
    )
    assert layer_hashes["transition"] == hash_orchestration_transition_visibility(
        default_orchestration_transition_visibility()
    )
    assert layer_hashes["coordination"] == hash_orchestration_coordination_visibility(
        default_orchestration_coordination_visibility()
    )
