from __future__ import annotations

import json
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

from operational_refresh.refresh_sequencing_visibility_continuity import (  # noqa: E402
    certify_refresh_sequencing_continuity,
)
from operational_refresh.refresh_sequencing_visibility_diagnostics import (  # noqa: E402
    build_refresh_sequencing_diagnostics,
)
from operational_refresh.refresh_sequencing_visibility_hashing import (  # noqa: E402
    hash_refresh_sequencing_identity,
    hash_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_integrity import (  # noqa: E402
    refresh_sequencing_identities_equal,
    refresh_sequencing_identity_key,
    refresh_sequencing_visibilities_equal,
    validate_refresh_sequencing_integrity,
    validate_refresh_sequencing_non_execution,
)
from operational_refresh.refresh_sequencing_visibility_models import (  # noqa: E402
    PROHIBITED_SEQUENCING_DOMAINS,
    SEQUENCING_STATE_BLOCKED,
    SEQUENCING_STATE_CIRCULAR,
    SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
    SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
    SEQUENCING_STATE_PROHIBITED,
    SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
    SEQUENCING_STATE_READY,
    SEQUENCING_STATE_READY_WITH_WARNINGS,
    SEQUENCING_STATE_REPLAY_DISCONTINUITY,
    SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
    SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
    SEQUENCING_STATE_STALE,
    SEQUENCING_STATE_UNSUPPORTED,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_SCHEMA_VERSION,
    V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE,
    default_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_serialization import (  # noqa: E402
    export_refresh_sequencing_visibility,
    serialize_refresh_sequencing_visibility,
)
from operational_refresh.refresh_sequencing_visibility_visibility import (  # noqa: E402
    count_refresh_ordering_node_states,
    count_refresh_ordering_relationship_states,
    validate_refresh_sequencing_visibility,
)
from scripts.report_v4_1_refresh_sequencing_visibility import (  # noqa: E402
    build_v4_1_refresh_sequencing_continuity_certification_report,
    build_v4_1_refresh_sequencing_diagnostics_report,
    build_v4_1_refresh_sequencing_integrity_certification_report,
    build_v4_1_refresh_sequencing_visibility_report,
)


def test_v4_1_refresh_sequencing_models_are_immutable_non_orchestrating_and_non_executable():
    visibility = default_refresh_sequencing_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.orchestration_enabled = True

    assert visibility.identity.schema_version == V4_1_REFRESH_SEQUENCING_VISIBILITY_SCHEMA_VERSION
    assert visibility.non_executable is True
    assert visibility.descriptive_only is True
    assert visibility.refresh_execution_enabled is False
    assert visibility.orchestration_enabled is False
    assert visibility.automatic_sequencing_enabled is False
    assert visibility.automatic_dependency_resolution_enabled is False
    assert visibility.migration_execution_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.remediation_enabled is False
    assert visibility.runtime_mutation_enabled is False
    assert visibility.hidden_orchestration_behavior_enabled is False
    assert visibility.implicit_execution_pathway_enabled is False
    assert visibility.silent_ordering_correction_enabled is False
    assert all(not node.refresh_execution_enabled for node in visibility.ordering_nodes)
    assert all(not node.automatic_sequencing_enabled for node in visibility.ordering_nodes)
    assert all(not relationship.orchestration_enabled for relationship in visibility.ordering_relationships)
    assert all(not relationship.automatic_dependency_resolution_enabled for relationship in visibility.ordering_relationships)
    assert visibility.governance.production_consumption_enabled is False
    assert visibility.governance.planner_integration_enabled is False


def test_v4_1_refresh_sequencing_identity_key_is_stable():
    visibility = default_refresh_sequencing_visibility()

    assert refresh_sequencing_identity_key(visibility.identity) == (
        "v4_1.refresh_sequencing_visibility.1"
        "|v4_1_phase_5_refresh_sequencing_visibility"
        "|v4_1_refresh_sequencing_visibility_primary|v4.1.0-phase-5"
        "|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary|v4_1_schema_evolution_governance_primary"
        "|v4_1_refresh_sequencing_visibility_provenance_primary"
        "|v4_1_refresh_sequencing_visibility_lineage_primary"
    )


def test_v4_1_refresh_sequencing_serialization_hashing_and_equality_are_stable():
    first = default_refresh_sequencing_visibility()
    second = default_refresh_sequencing_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_sequencing_visibilities_equal(first, second)
    assert refresh_sequencing_identities_equal(first.identity, second.identity)
    assert serialize_refresh_sequencing_visibility(first) == serialize_refresh_sequencing_visibility(second)
    assert hash_refresh_sequencing_visibility(first) == hash_refresh_sequencing_visibility(second)
    assert hash_refresh_sequencing_identity(first.identity) == hash_refresh_sequencing_identity(second.identity)
    assert json.loads(serialize_refresh_sequencing_visibility(first))["non_executable"] is True


def test_v4_1_refresh_sequencing_serialization_preserves_order_and_fail_visible_relationships():
    visibility = default_refresh_sequencing_visibility()
    reordered = replace(
        visibility,
        ordering_nodes=tuple(reversed(visibility.ordering_nodes)),
        ordering_relationships=tuple(reversed(visibility.ordering_relationships)),
    )

    assert serialize_refresh_sequencing_visibility(visibility) == serialize_refresh_sequencing_visibility(reordered)
    assert hash_refresh_sequencing_visibility(visibility) == hash_refresh_sequencing_visibility(reordered)
    exported = export_refresh_sequencing_visibility(reordered)
    assert [item["state"] for item in exported["ordering_relationships"]] == [
        SEQUENCING_STATE_READY,
        SEQUENCING_STATE_READY,
        SEQUENCING_STATE_READY_WITH_WARNINGS,
        SEQUENCING_STATE_UNSUPPORTED,
        SEQUENCING_STATE_STALE,
        SEQUENCING_STATE_SEQUENCING_DISCONTINUITY,
        SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY,
        SEQUENCING_STATE_LINEAGE_DISCONTINUITY,
        SEQUENCING_STATE_PROVENANCE_DISCONTINUITY,
        SEQUENCING_STATE_REPLAY_DISCONTINUITY,
        SEQUENCING_STATE_ROLLBACK_DISCONTINUITY,
        SEQUENCING_STATE_CIRCULAR,
        SEQUENCING_STATE_PROHIBITED,
        SEQUENCING_STATE_BLOCKED,
    ]
    assert exported["blocked_state_visibility"]["blocked_relationship_ids"] == [
        "v4_1_sequence_blocked_ordering_state"
    ]
    assert exported["blocked_state_visibility"]["circular_sequencing_visibility"] == [
        "v4_1_sequence_circular_visibility"
    ]
    assert exported["unsupported_state_visibility"]["unsupported_relationship_ids"] == [
        "v4_1_sequence_future_provider_unsupported",
    ]
    assert exported["unsupported_state_visibility"]["stale_relationship_ids"] == [
        "v4_1_sequence_stale_schema_chain"
    ]
    assert exported["unsupported_state_visibility"]["prohibited_relationship_ids"] == [
        "v4_1_sequence_prohibited_orchestration"
    ]


def test_v4_1_refresh_sequencing_visibility_preserves_blocked_unsupported_circular_and_prohibited_state():
    visibility = default_refresh_sequencing_visibility()
    validation = validate_refresh_sequencing_visibility(visibility)
    node_counts = count_refresh_ordering_node_states(visibility.ordering_nodes)
    relationship_counts = count_refresh_ordering_relationship_states(visibility.ordering_relationships)

    assert node_counts[SEQUENCING_STATE_READY] == 4
    assert node_counts[SEQUENCING_STATE_UNSUPPORTED] == 1
    assert node_counts[SEQUENCING_STATE_PROHIBITED] == 1
    assert relationship_counts[SEQUENCING_STATE_READY] == 2
    assert relationship_counts[SEQUENCING_STATE_READY_WITH_WARNINGS] == 1
    assert relationship_counts[SEQUENCING_STATE_UNSUPPORTED] == 1
    assert relationship_counts[SEQUENCING_STATE_STALE] == 1
    assert relationship_counts[SEQUENCING_STATE_SEQUENCING_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_DEPENDENCY_ORDERING_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_LINEAGE_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_PROVENANCE_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_REPLAY_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_ROLLBACK_DISCONTINUITY] == 1
    assert relationship_counts[SEQUENCING_STATE_CIRCULAR] == 1
    assert relationship_counts[SEQUENCING_STATE_PROHIBITED] == 1
    assert relationship_counts[SEQUENCING_STATE_BLOCKED] == 1
    assert validation["valid"] is True
    assert validation["unsupported_nodes_visible"] is True
    assert validation["unsupported_relationships_visible"] is True
    assert validation["blocked_relationships_visible"] is True
    assert validation["stale_relationships_visible"] is True
    assert validation["prohibited_relationships_visible"] is True
    assert validation["circular_sequencing_visible"] is True
    assert validation["dependency_ordering_discontinuity_visible"] is True
    assert validation["prohibited_sequencing_domain_visibility_count"] == len(PROHIBITED_SEQUENCING_DOMAINS)
    assert validation["node_execution_semantics_count"] == 0
    assert validation["relationship_execution_semantics_count"] == 0


def test_v4_1_refresh_sequencing_continuity_certifies_dependency_lineage_provenance_replay_and_rollback():
    visibility = default_refresh_sequencing_visibility()
    continuity = certify_refresh_sequencing_continuity(visibility)

    with pytest.raises(FrozenInstanceError):
        visibility.continuity_metadata.automatic_sequencing_enabled = True

    assert continuity["valid"] is True
    assert continuity["sequencing_continuity_valid"] is True
    assert continuity["dependency_ordering_continuity_valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["sequencing_continuity"]["sequencing_discontinuity_visibility_count"] == 1
    assert continuity["dependency_ordering_continuity"]["circular_sequencing_visibility_count"] == 1
    assert continuity["lineage_continuity"]["lineage_discontinuity_visibility_count"] == 1
    assert continuity["provenance_continuity"]["provenance_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_safe"] is True
    assert continuity["rollback_continuity"]["rollback_safe"] is True


def test_v4_1_refresh_sequencing_non_execution_validation_blocks_orchestration_production_and_planner_flags():
    visibility = default_refresh_sequencing_visibility()
    contaminated = replace(
        visibility,
        refresh_execution_enabled=True,
        orchestration_enabled=True,
        automatic_sequencing_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_refresh_sequencing_non_execution(contaminated)

    assert validate_refresh_sequencing_non_execution(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 5
    assert validation["refresh_execution_absent"] is False
    assert validation["orchestration_absent"] is False
    assert validation["automatic_sequencing_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_refresh_sequencing_integrity_blocks_hidden_correction_and_execution_semantics():
    visibility = default_refresh_sequencing_visibility()
    hidden_relationship = replace(
        visibility.ordering_relationships[3],
        hidden=True,
        fail_visible=False,
        refresh_execution_enabled=True,
        automatic_sequencing_enabled=True,
    )
    corrective_visibility = replace(
        visibility.blocked_state_visibility,
        remediation_enabled=True,
        silent_ordering_correction_enabled=True,
    )
    contaminated = replace(
        visibility,
        ordering_relationships=(
            visibility.ordering_relationships[0],
            visibility.ordering_relationships[1],
            visibility.ordering_relationships[2],
            hidden_relationship,
            *visibility.ordering_relationships[4:],
        ),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_refresh_sequencing_integrity(contaminated)

    assert validate_refresh_sequencing_integrity(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_relationship_count"] == 1
    assert validation["visibility_validation"]["relationship_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 4


def test_v4_1_refresh_sequencing_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_refresh_sequencing_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_SEQUENCING_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["automatic_sequencing_absent"] is True
    assert diagnostics["automatic_dependency_resolution_absent"] is True
    assert diagnostics["silent_ordering_correction_absent"] is True
    assert diagnostics["circular_sequencing_visibility"] == ["v4_1_sequence_circular_visibility"]


def test_v4_1_refresh_sequencing_reports_contain_required_evidence_and_boundaries():
    report = build_v4_1_refresh_sequencing_visibility_report()
    diagnostics_report = build_v4_1_refresh_sequencing_diagnostics_report()
    continuity_report = build_v4_1_refresh_sequencing_continuity_certification_report()
    integrity_report = build_v4_1_refresh_sequencing_integrity_certification_report()

    assert report["foundation_status"] == V4_1_REFRESH_SEQUENCING_VISIBILITY_STATUS_STABLE
    assert report["sequencing_visibility_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_sequencing_serialization_verified"] is True
    assert report["summary"]["deterministic_sequencing_hashing_verified"] is True
    assert report["summary"]["deterministic_sequencing_equality_verified"] is True
    assert report["summary"]["deterministic_sequencing_visibility_verified"] is True
    assert report["summary"]["sequencing_lineage_continuity_verified"] is True
    assert report["summary"]["sequencing_provenance_continuity_verified"] is True
    assert report["summary"]["sequencing_replay_continuity_verified"] is True
    assert report["summary"]["sequencing_rollback_continuity_verified"] is True
    assert report["summary"]["dependency_ordering_continuity_validated"] is True
    assert report["summary"]["blocked_order_visibility_validated"] is True
    assert report["summary"]["unsupported_state_visibility_validated"] is True
    assert report["summary"]["circular_sequencing_visibility_validated"] is True
    assert report["summary"]["non_orchestration_enforcement_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["production_consumption_disabled_validated"] is True
    assert report["summary"]["planner_integration_disabled_validated"] is True
    assert report["summary"]["integrity_validation_verified"] is True
    assert report["summary"]["certification_validation_verified"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert continuity_report["summary"]["continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No automatic sequencing exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No migration execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
