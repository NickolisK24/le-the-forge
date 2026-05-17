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

from operational_refresh.refresh_lineage_certification_continuity import (  # noqa: E402
    certify_refresh_lineage_continuity,
)
from operational_refresh.refresh_lineage_certification_diagnostics import (  # noqa: E402
    build_lineage_certification_diagnostics,
)
from operational_refresh.refresh_lineage_certification_hashing import (  # noqa: E402
    hash_lineage_identity,
    hash_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_integrity import (  # noqa: E402
    lineage_identities_equal,
    lineage_identity_key,
    refresh_lineage_certifications_equal,
    validate_lineage_integrity,
    validate_lineage_non_execution,
)
from operational_refresh.refresh_lineage_certification_models import (  # noqa: E402
    LINEAGE_STATE_BLOCKED,
    LINEAGE_STATE_CIRCULAR_ANCESTRY,
    LINEAGE_STATE_LINEAGE_DISCONTINUITY,
    LINEAGE_STATE_PROHIBITED,
    LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
    LINEAGE_STATE_SCHEMA_DISCONTINUITY,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_SUPPORTED,
    LINEAGE_STATE_UNSUPPORTED,
    PROHIBITED_LINEAGE_DOMAINS,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_SCHEMA_VERSION,
    V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE,
    default_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_serialization import (  # noqa: E402
    export_refresh_lineage_certification,
    serialize_refresh_lineage_certification,
)
from operational_refresh.refresh_lineage_certification_visibility import (  # noqa: E402
    count_ancestry_link_states,
    count_ancestry_node_states,
    validate_refresh_lineage_visibility,
)
from scripts.report_v4_1_refresh_lineage_certification import (  # noqa: E402
    build_v4_1_refresh_lineage_certification_diagnostics_report,
    build_v4_1_refresh_lineage_certification_report,
    build_v4_1_refresh_lineage_continuity_certification_report,
    build_v4_1_refresh_lineage_integrity_certification_report,
)


def test_v4_1_lineage_certification_models_are_immutable_and_non_executable():
    certification = default_refresh_lineage_certification()

    with pytest.raises(FrozenInstanceError):
        certification.refresh_execution_enabled = True

    assert certification.identity.schema_version == V4_1_REFRESH_LINEAGE_CERTIFICATION_SCHEMA_VERSION
    assert certification.non_executable is True
    assert certification.descriptive_only is True
    assert certification.refresh_execution_enabled is False
    assert certification.orchestration_enabled is False
    assert certification.migration_execution_enabled is False
    assert certification.automatic_lineage_repair_enabled is False
    assert certification.automatic_continuity_correction_enabled is False
    assert certification.automatic_schema_migration_enabled is False
    assert certification.automatic_rollback_enabled is False
    assert certification.automatic_recovery_enabled is False
    assert certification.planner_integration_enabled is False
    assert certification.production_consumption_enabled is False
    assert certification.remediation_enabled is False
    assert certification.runtime_mutation_enabled is False
    assert certification.hidden_orchestration_behavior_enabled is False
    assert certification.implicit_execution_pathway_enabled is False
    assert certification.silent_continuity_correction_enabled is False
    assert all(not node.refresh_execution_enabled for node in certification.ancestry_nodes)
    assert all(not node.automatic_lineage_repair_enabled for node in certification.ancestry_nodes)
    assert all(not link.refresh_execution_enabled for link in certification.ancestry_links)
    assert all(not link.automatic_lineage_repair_enabled for link in certification.ancestry_links)
    assert all(not link.automatic_schema_migration_enabled for link in certification.ancestry_links)
    assert certification.governance.production_consumption_enabled is False
    assert certification.governance.planner_integration_enabled is False


def test_v4_1_lineage_certification_identity_key_is_stable():
    certification = default_refresh_lineage_certification()

    assert lineage_identity_key(certification.identity) == (
        "v4_1.refresh_lineage_certification.1"
        "|v4_1_phase_3_refresh_lineage_certification"
        "|v4_1_refresh_lineage_certification_primary|v4.1.0-phase-3"
        "|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_provenance_primary"
        "|v4_1_refresh_lineage_certification_lineage_primary"
    )


def test_v4_1_lineage_certification_serialization_hashing_and_equality_are_stable():
    first = default_refresh_lineage_certification()
    second = default_refresh_lineage_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_lineage_certifications_equal(first, second)
    assert lineage_identities_equal(first.identity, second.identity)
    assert serialize_refresh_lineage_certification(first) == serialize_refresh_lineage_certification(second)
    assert hash_refresh_lineage_certification(first) == hash_refresh_lineage_certification(second)
    assert hash_lineage_identity(first.identity) == hash_lineage_identity(second.identity)
    assert json.loads(serialize_refresh_lineage_certification(first))["non_executable"] is True


def test_v4_1_lineage_serialization_preserves_order_and_fail_visible_relationships():
    certification = default_refresh_lineage_certification()
    reordered = replace(
        certification,
        ancestry_nodes=tuple(reversed(certification.ancestry_nodes)),
        ancestry_links=tuple(reversed(certification.ancestry_links)),
        provenance_inheritance=tuple(reversed(certification.provenance_inheritance)),
    )

    assert serialize_refresh_lineage_certification(certification) == serialize_refresh_lineage_certification(reordered)
    assert hash_refresh_lineage_certification(certification) == hash_refresh_lineage_certification(reordered)
    exported = export_refresh_lineage_certification(reordered)
    assert [item["relationship_state"] for item in exported["ancestry_links"]] == [
        LINEAGE_STATE_SUPPORTED,
        LINEAGE_STATE_SUPPORTED,
        LINEAGE_STATE_UNSUPPORTED,
        LINEAGE_STATE_CIRCULAR_ANCESTRY,
        LINEAGE_STATE_STALE,
        LINEAGE_STATE_LINEAGE_DISCONTINUITY,
        LINEAGE_STATE_PROVENANCE_DISCONTINUITY,
        LINEAGE_STATE_SCHEMA_DISCONTINUITY,
        LINEAGE_STATE_PROHIBITED,
        LINEAGE_STATE_BLOCKED,
    ]
    assert exported["blocked_state_visibility"]["blocked_lineage_links"] == [
        "v4_1_lineage_link_blocked_continuity_gap"
    ]
    assert exported["blocked_state_visibility"]["circular_ancestry_links"] == [
        "v4_1_lineage_link_future_generation_circular_visibility"
    ]
    assert exported["unsupported_state_visibility"]["unsupported_lineage_links"] == [
        "v4_1_lineage_link_future_generation_unsupported"
    ]
    assert exported["unsupported_state_visibility"]["stale_lineage_links"] == [
        "v4_1_lineage_link_stale_schema_transition"
    ]
    assert exported["unsupported_state_visibility"]["prohibited_lineage_links"] == [
        "v4_1_lineage_link_prohibited_migration"
    ]


def test_v4_1_lineage_visibility_preserves_blocked_unsupported_circular_schema_and_prohibited_state():
    certification = default_refresh_lineage_certification()
    visibility = validate_refresh_lineage_visibility(certification)
    node_counts = count_ancestry_node_states(certification.ancestry_nodes)
    link_counts = count_ancestry_link_states(certification.ancestry_links)

    assert node_counts[LINEAGE_STATE_SUPPORTED] == 3
    assert node_counts[LINEAGE_STATE_UNSUPPORTED] == 1
    assert node_counts[LINEAGE_STATE_PROHIBITED] == 1
    assert link_counts[LINEAGE_STATE_SUPPORTED] == 2
    assert link_counts[LINEAGE_STATE_UNSUPPORTED] == 1
    assert link_counts[LINEAGE_STATE_CIRCULAR_ANCESTRY] == 1
    assert link_counts[LINEAGE_STATE_STALE] == 1
    assert link_counts[LINEAGE_STATE_LINEAGE_DISCONTINUITY] == 1
    assert link_counts[LINEAGE_STATE_PROVENANCE_DISCONTINUITY] == 1
    assert link_counts[LINEAGE_STATE_SCHEMA_DISCONTINUITY] == 1
    assert link_counts[LINEAGE_STATE_PROHIBITED] == 1
    assert link_counts[LINEAGE_STATE_BLOCKED] == 1
    assert visibility["valid"] is True
    assert visibility["unsupported_nodes_visible"] is True
    assert visibility["unsupported_links_visible"] is True
    assert visibility["blocked_links_visible"] is True
    assert visibility["stale_links_visible"] is True
    assert visibility["prohibited_links_visible"] is True
    assert visibility["circular_ancestry_visible"] is True
    assert visibility["schema_discontinuity_visible"] is True
    assert visibility["prohibited_lineage_domains_visible"] is True
    assert visibility["prohibited_lineage_domain_visibility_count"] == len(PROHIBITED_LINEAGE_DOMAINS)
    assert visibility["node_execution_semantics_count"] == 0
    assert visibility["link_execution_semantics_count"] == 0


def test_v4_1_lineage_continuity_certifies_ancestry_provenance_replay_rollback_and_schema():
    certification = default_refresh_lineage_certification()
    continuity = certify_refresh_lineage_continuity(certification)

    with pytest.raises(FrozenInstanceError):
        certification.continuity_metadata.automatic_continuity_correction_enabled = True

    assert continuity["valid"] is True
    assert continuity["ancestry_continuity_valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["schema_continuity_valid"] is True
    assert continuity["ancestry_continuity"]["circular_ancestry_visibility_count"] == 1
    assert continuity["provenance_continuity"]["provenance_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_safe"] is True
    assert continuity["rollback_continuity"]["rollback_safe"] is True
    assert continuity["schema_continuity"]["schema_transition_continuity_preserved"] is True


def test_v4_1_lineage_non_execution_validation_blocks_refresh_migration_production_and_planner_flags():
    certification = default_refresh_lineage_certification()
    contaminated = replace(
        certification,
        refresh_execution_enabled=True,
        migration_execution_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_lineage_non_execution(contaminated)

    assert validate_lineage_non_execution(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 4
    assert validation["refresh_execution_absent"] is False
    assert validation["migration_execution_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_lineage_integrity_blocks_hidden_correction_and_execution_semantics():
    certification = default_refresh_lineage_certification()
    hidden_link = replace(
        certification.ancestry_links[2],
        hidden=True,
        fail_visible=False,
        refresh_execution_enabled=True,
        automatic_lineage_repair_enabled=True,
    )
    corrective_visibility = replace(
        certification.blocked_state_visibility,
        remediation_enabled=True,
        silent_correction_enabled=True,
    )
    contaminated = replace(
        certification,
        ancestry_links=(certification.ancestry_links[0], certification.ancestry_links[1], hidden_link, *certification.ancestry_links[3:]),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_lineage_integrity(contaminated)

    assert validate_lineage_integrity(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_link_count"] == 1
    assert validation["visibility_validation"]["link_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 4


def test_v4_1_lineage_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_lineage_certification_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_LINEAGE_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["silent_correction_absent"] is True
    assert diagnostics["automatic_recovery_absent"] is True
    assert diagnostics["circular_ancestry_links"] == [
        "v4_1_lineage_link_future_generation_circular_visibility"
    ]


def test_v4_1_lineage_reports_contain_required_evidence_and_boundaries():
    report = build_v4_1_refresh_lineage_certification_report()
    diagnostics_report = build_v4_1_refresh_lineage_certification_diagnostics_report()
    continuity_report = build_v4_1_refresh_lineage_continuity_certification_report()
    integrity_report = build_v4_1_refresh_lineage_integrity_certification_report()

    assert report["foundation_status"] == V4_1_REFRESH_LINEAGE_CERTIFICATION_STATUS_STABLE
    assert report["lineage_certification_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_certification_serialization_verified"] is True
    assert report["summary"]["deterministic_certification_hashing_verified"] is True
    assert report["summary"]["deterministic_lineage_equality_verified"] is True
    assert report["summary"]["deterministic_lineage_visibility_verified"] is True
    assert report["summary"]["ancestry_continuity_verified"] is True
    assert report["summary"]["provenance_continuity_verified"] is True
    assert report["summary"]["replay_continuity_verified"] is True
    assert report["summary"]["rollback_continuity_verified"] is True
    assert report["summary"]["schema_continuity_validated"] is True
    assert report["summary"]["blocked_state_visibility_validated"] is True
    assert report["summary"]["unsupported_state_visibility_validated"] is True
    assert report["summary"]["circular_ancestry_visibility_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["production_consumption_disabled_validated"] is True
    assert report["summary"]["planner_integration_disabled_validated"] is True
    assert report["summary"]["integrity_validation_verified"] is True
    assert report["summary"]["certification_validation_verified"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert continuity_report["summary"]["continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No orchestration exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No migration execution exists." in report["explicit_prohibitions"]
    assert "No automatic repair exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
