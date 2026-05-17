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

from operational_refresh.schema_evolution_governance_continuity import (  # noqa: E402
    certify_schema_evolution_continuity,
)
from operational_refresh.schema_evolution_governance_diagnostics import (  # noqa: E402
    build_schema_evolution_diagnostics,
)
from operational_refresh.schema_evolution_governance_hashing import (  # noqa: E402
    hash_schema_evolution_governance,
    hash_schema_evolution_identity,
)
from operational_refresh.schema_evolution_governance_integrity import (  # noqa: E402
    schema_evolution_governances_equal,
    schema_evolution_identities_equal,
    schema_evolution_identity_key,
    validate_schema_evolution_integrity,
    validate_schema_evolution_non_execution,
)
from operational_refresh.schema_evolution_governance_models import (  # noqa: E402
    PROHIBITED_SCHEMA_DOMAINS,
    SCHEMA_STATE_BLOCKED,
    SCHEMA_STATE_CIRCULAR_ANCESTRY,
    SCHEMA_STATE_COMPATIBLE,
    SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS,
    SCHEMA_STATE_LINEAGE_DISCONTINUITY,
    SCHEMA_STATE_PROHIBITED,
    SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
    SCHEMA_STATE_REPLAY_DISCONTINUITY,
    SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
    SCHEMA_STATE_STALE,
    SCHEMA_STATE_UNSUPPORTED,
    SCHEMA_STATE_VERSION_DISCONTINUITY,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION,
    V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE,
    default_schema_evolution_governance,
)
from operational_refresh.schema_evolution_governance_serialization import (  # noqa: E402
    export_schema_evolution_governance,
    serialize_schema_evolution_governance,
)
from operational_refresh.schema_evolution_governance_visibility import (  # noqa: E402
    count_schema_node_states,
    count_schema_transition_states,
    validate_schema_evolution_visibility,
)
from scripts.report_v4_1_schema_evolution_governance import (  # noqa: E402
    build_v4_1_schema_continuity_certification_report,
    build_v4_1_schema_evolution_diagnostics_report,
    build_v4_1_schema_evolution_governance_report,
    build_v4_1_schema_integrity_certification_report,
)


def test_v4_1_schema_evolution_models_are_immutable_and_non_migrating():
    governance = default_schema_evolution_governance()

    with pytest.raises(FrozenInstanceError):
        governance.schema_migration_execution_enabled = True

    assert governance.identity.schema_version == V4_1_SCHEMA_EVOLUTION_GOVERNANCE_SCHEMA_VERSION
    assert governance.non_executable is True
    assert governance.descriptive_only is True
    assert governance.schema_migration_execution_enabled is False
    assert governance.automatic_schema_migration_enabled is False
    assert governance.automatic_schema_repair_enabled is False
    assert governance.automatic_compatibility_correction_enabled is False
    assert governance.refresh_execution_enabled is False
    assert governance.orchestration_enabled is False
    assert governance.planner_integration_enabled is False
    assert governance.production_consumption_enabled is False
    assert governance.remediation_enabled is False
    assert governance.runtime_mutation_enabled is False
    assert governance.hidden_migration_behavior_enabled is False
    assert governance.implicit_execution_pathway_enabled is False
    assert governance.silent_compatibility_fallback_enabled is False
    assert all(not node.schema_migration_execution_enabled for node in governance.version_nodes)
    assert all(not node.automatic_schema_migration_enabled for node in governance.version_nodes)
    assert all(not transition.schema_migration_execution_enabled for transition in governance.version_transitions)
    assert all(not transition.automatic_compatibility_correction_enabled for transition in governance.version_transitions)
    assert governance.governance.production_consumption_enabled is False
    assert governance.governance.planner_integration_enabled is False


def test_v4_1_schema_evolution_identity_key_is_stable():
    governance = default_schema_evolution_governance()

    assert schema_evolution_identity_key(governance.identity) == (
        "v4_1.schema_evolution_governance.1"
        "|v4_1_phase_4_schema_evolution_governance"
        "|v4_1_schema_evolution_governance_primary|v4.1.0-phase-4"
        "|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary"
        "|v4_1_schema_evolution_governance_provenance_primary"
        "|v4_1_schema_evolution_governance_lineage_primary"
    )


def test_v4_1_schema_serialization_hashing_and_equality_are_stable():
    first = default_schema_evolution_governance()
    second = default_schema_evolution_governance()

    assert first == second
    assert hash(first) == hash(second)
    assert schema_evolution_governances_equal(first, second)
    assert schema_evolution_identities_equal(first.identity, second.identity)
    assert serialize_schema_evolution_governance(first) == serialize_schema_evolution_governance(second)
    assert hash_schema_evolution_governance(first) == hash_schema_evolution_governance(second)
    assert hash_schema_evolution_identity(first.identity) == hash_schema_evolution_identity(second.identity)
    assert json.loads(serialize_schema_evolution_governance(first))["non_executable"] is True


def test_v4_1_schema_serialization_preserves_order_and_fail_visible_transitions():
    governance = default_schema_evolution_governance()
    reordered = replace(
        governance,
        version_nodes=tuple(reversed(governance.version_nodes)),
        version_transitions=tuple(reversed(governance.version_transitions)),
    )

    assert serialize_schema_evolution_governance(governance) == serialize_schema_evolution_governance(reordered)
    assert hash_schema_evolution_governance(governance) == hash_schema_evolution_governance(reordered)
    exported = export_schema_evolution_governance(reordered)
    assert [item["state"] for item in exported["version_transitions"]] == [
        SCHEMA_STATE_COMPATIBLE,
        SCHEMA_STATE_COMPATIBLE,
        SCHEMA_STATE_COMPATIBLE,
        SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS,
        SCHEMA_STATE_UNSUPPORTED,
        SCHEMA_STATE_STALE,
        SCHEMA_STATE_VERSION_DISCONTINUITY,
        SCHEMA_STATE_LINEAGE_DISCONTINUITY,
        SCHEMA_STATE_PROVENANCE_DISCONTINUITY,
        SCHEMA_STATE_REPLAY_DISCONTINUITY,
        SCHEMA_STATE_ROLLBACK_DISCONTINUITY,
        SCHEMA_STATE_CIRCULAR_ANCESTRY,
        SCHEMA_STATE_PROHIBITED,
        SCHEMA_STATE_BLOCKED,
    ]
    assert exported["blocked_state_visibility"]["blocked_transition_ids"] == [
        "v4_1_schema_transition_blocked_compatibility"
    ]
    assert exported["blocked_state_visibility"]["circular_schema_ancestry_visibility"] == [
        "v4_1_schema_transition_circular_ancestry"
    ]
    assert exported["unsupported_state_visibility"]["unsupported_transition_ids"] == [
        "v4_1_schema_transition_future_provider_unsupported"
    ]
    assert exported["unsupported_state_visibility"]["stale_transition_ids"] == [
        "v4_1_schema_transition_stale_manifest_version"
    ]
    assert exported["unsupported_state_visibility"]["prohibited_transition_ids"] == [
        "v4_1_schema_transition_prohibited_migration"
    ]


def test_v4_1_schema_visibility_preserves_blocked_unsupported_circular_and_prohibited_state():
    governance = default_schema_evolution_governance()
    visibility = validate_schema_evolution_visibility(governance)
    node_counts = count_schema_node_states(governance.version_nodes)
    transition_counts = count_schema_transition_states(governance.version_transitions)

    assert node_counts[SCHEMA_STATE_COMPATIBLE] == 4
    assert node_counts[SCHEMA_STATE_UNSUPPORTED] == 1
    assert node_counts[SCHEMA_STATE_PROHIBITED] == 1
    assert transition_counts[SCHEMA_STATE_COMPATIBLE] == 3
    assert transition_counts[SCHEMA_STATE_COMPATIBLE_WITH_WARNINGS] == 1
    assert transition_counts[SCHEMA_STATE_UNSUPPORTED] == 1
    assert transition_counts[SCHEMA_STATE_STALE] == 1
    assert transition_counts[SCHEMA_STATE_VERSION_DISCONTINUITY] == 1
    assert transition_counts[SCHEMA_STATE_LINEAGE_DISCONTINUITY] == 1
    assert transition_counts[SCHEMA_STATE_PROVENANCE_DISCONTINUITY] == 1
    assert transition_counts[SCHEMA_STATE_REPLAY_DISCONTINUITY] == 1
    assert transition_counts[SCHEMA_STATE_ROLLBACK_DISCONTINUITY] == 1
    assert transition_counts[SCHEMA_STATE_CIRCULAR_ANCESTRY] == 1
    assert transition_counts[SCHEMA_STATE_PROHIBITED] == 1
    assert transition_counts[SCHEMA_STATE_BLOCKED] == 1
    assert visibility["valid"] is True
    assert visibility["unsupported_nodes_visible"] is True
    assert visibility["unsupported_transitions_visible"] is True
    assert visibility["blocked_transitions_visible"] is True
    assert visibility["stale_transitions_visible"] is True
    assert visibility["prohibited_transitions_visible"] is True
    assert visibility["circular_schema_ancestry_visible"] is True
    assert visibility["schema_version_discontinuity_visible"] is True
    assert visibility["schema_lineage_discontinuity_visible"] is True
    assert visibility["schema_provenance_discontinuity_visible"] is True
    assert visibility["schema_replay_discontinuity_visible"] is True
    assert visibility["schema_rollback_discontinuity_visible"] is True
    assert visibility["compatibility_classifications_visible"] is True
    assert visibility["prohibited_schema_domain_visibility_count"] == len(PROHIBITED_SCHEMA_DOMAINS)
    assert visibility["node_execution_semantics_count"] == 0
    assert visibility["transition_execution_semantics_count"] == 0


def test_v4_1_schema_continuity_certifies_lineage_provenance_replay_rollback_and_compatibility():
    governance = default_schema_evolution_governance()
    continuity = certify_schema_evolution_continuity(governance)

    with pytest.raises(FrozenInstanceError):
        governance.continuity_metadata.automatic_schema_migration_enabled = True

    assert continuity["valid"] is True
    assert continuity["schema_continuity_valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["compatibility_continuity_valid"] is True
    assert continuity["schema_continuity"]["schema_version_discontinuity_visibility_count"] == 1
    assert continuity["lineage_continuity"]["circular_schema_ancestry_visibility_count"] == 1
    assert continuity["provenance_continuity"]["provenance_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_safe"] is True
    assert continuity["rollback_continuity"]["rollback_safe"] is True
    assert continuity["compatibility_continuity"]["blocked_transition_visibility_count"] == 1


def test_v4_1_schema_non_execution_validation_blocks_migration_production_and_planner_flags():
    governance = default_schema_evolution_governance()
    contaminated = replace(
        governance,
        schema_migration_execution_enabled=True,
        automatic_schema_migration_enabled=True,
        automatic_compatibility_correction_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_schema_evolution_non_execution(contaminated)

    assert validate_schema_evolution_non_execution(governance)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 5
    assert validation["schema_migration_execution_absent"] is False
    assert validation["automatic_schema_migration_absent"] is False
    assert validation["automatic_compatibility_correction_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_schema_integrity_blocks_hidden_correction_and_execution_semantics():
    governance = default_schema_evolution_governance()
    hidden_transition = replace(
        governance.version_transitions[4],
        hidden=True,
        fail_visible=False,
        schema_migration_execution_enabled=True,
        automatic_compatibility_correction_enabled=True,
    )
    corrective_visibility = replace(
        governance.blocked_state_visibility,
        remediation_enabled=True,
        silent_compatibility_fallback_enabled=True,
    )
    contaminated = replace(
        governance,
        version_transitions=(
            governance.version_transitions[0],
            governance.version_transitions[1],
            governance.version_transitions[2],
            governance.version_transitions[3],
            hidden_transition,
            *governance.version_transitions[5:],
        ),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_schema_evolution_integrity(contaminated)

    assert validate_schema_evolution_integrity(governance)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_transition_count"] == 1
    assert validation["visibility_validation"]["transition_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 4


def test_v4_1_schema_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_schema_evolution_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_SCHEMA_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["automatic_schema_migration_absent"] is True
    assert diagnostics["automatic_compatibility_correction_absent"] is True
    assert diagnostics["silent_compatibility_fallback_absent"] is True
    assert diagnostics["circular_schema_ancestry_visibility"] == [
        "v4_1_schema_transition_circular_ancestry"
    ]


def test_v4_1_schema_reports_contain_required_evidence_and_boundaries():
    report = build_v4_1_schema_evolution_governance_report()
    diagnostics_report = build_v4_1_schema_evolution_diagnostics_report()
    continuity_report = build_v4_1_schema_continuity_certification_report()
    integrity_report = build_v4_1_schema_integrity_certification_report()

    assert report["foundation_status"] == V4_1_SCHEMA_EVOLUTION_GOVERNANCE_STATUS_STABLE
    assert report["schema_governance_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_schema_serialization_verified"] is True
    assert report["summary"]["deterministic_schema_hashing_verified"] is True
    assert report["summary"]["deterministic_schema_equality_verified"] is True
    assert report["summary"]["deterministic_schema_visibility_verified"] is True
    assert report["summary"]["schema_lineage_continuity_verified"] is True
    assert report["summary"]["schema_provenance_continuity_verified"] is True
    assert report["summary"]["schema_replay_continuity_verified"] is True
    assert report["summary"]["schema_rollback_continuity_verified"] is True
    assert report["summary"]["compatibility_visibility_validated"] is True
    assert report["summary"]["blocked_transition_visibility_validated"] is True
    assert report["summary"]["unsupported_state_visibility_validated"] is True
    assert report["summary"]["circular_schema_ancestry_visibility_validated"] is True
    assert report["summary"]["non_migration_enforcement_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["production_consumption_disabled_validated"] is True
    assert report["summary"]["planner_integration_disabled_validated"] is True
    assert report["summary"]["integrity_validation_verified"] is True
    assert report["summary"]["certification_validation_verified"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert continuity_report["summary"]["continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No schema migration execution exists." in report["explicit_prohibitions"]
    assert "No automatic compatibility correction exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No orchestration exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
