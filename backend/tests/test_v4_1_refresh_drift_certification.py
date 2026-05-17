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

from operational_refresh.refresh_drift_certification_continuity import certify_refresh_drift_continuity  # noqa: E402
from operational_refresh.refresh_drift_certification_diagnostics import build_refresh_drift_diagnostics  # noqa: E402
from operational_refresh.refresh_drift_certification_hashing import (  # noqa: E402
    hash_refresh_drift_certification,
    hash_refresh_drift_certification_identity,
)
from operational_refresh.refresh_drift_certification_integrity import (  # noqa: E402
    refresh_drift_certifications_equal,
    refresh_drift_identities_equal,
    refresh_drift_identity_key,
    validate_refresh_drift_integrity,
    validate_refresh_drift_non_execution,
)
from operational_refresh.refresh_drift_certification_models import (  # noqa: E402
    DRIFT_STATE_BLOCKED,
    DRIFT_STATE_CROSS_LAYER_CONFLICT,
    DRIFT_STATE_LINEAGE_DISCONTINUITY,
    DRIFT_STATE_PROHIBITED,
    DRIFT_STATE_PROVENANCE_DISCONTINUITY,
    DRIFT_STATE_REPLAY_DISCONTINUITY,
    DRIFT_STATE_ROLLBACK_DISCONTINUITY,
    DRIFT_STATE_STALE,
    DRIFT_STATE_UNSUPPORTED,
    DRIFT_STATE_VISIBLE,
    PROHIBITED_DRIFT_DOMAINS,
    V4_1_REFRESH_DRIFT_CERTIFICATION_SCHEMA_VERSION,
    V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE,
    default_refresh_drift_certification,
)
from operational_refresh.refresh_drift_certification_serialization import (  # noqa: E402
    export_refresh_drift_certification,
    serialize_refresh_drift_certification,
)
from operational_refresh.refresh_drift_certification_visibility import (  # noqa: E402
    count_drift_observation_states,
    validate_refresh_drift_visibility,
)
from scripts.report_v4_1_refresh_drift_certification import (  # noqa: E402
    build_v4_1_cross_layer_drift_certification_report,
    build_v4_1_refresh_drift_certification_report,
    build_v4_1_refresh_drift_continuity_certification_report,
    build_v4_1_refresh_drift_diagnostics_report,
    build_v4_1_refresh_drift_integrity_certification_report,
)


def test_v4_1_drift_models_are_immutable_non_remediating_and_non_executable():
    certification = default_refresh_drift_certification()

    with pytest.raises(FrozenInstanceError):
        certification.drift_remediation_enabled = True

    assert certification.identity.schema_version == V4_1_REFRESH_DRIFT_CERTIFICATION_SCHEMA_VERSION
    assert certification.non_executable is True
    assert certification.descriptive_only is True
    assert certification.drift_remediation_enabled is False
    assert certification.automatic_drift_correction_enabled is False
    assert certification.automatic_repair_enabled is False
    assert certification.refresh_execution_enabled is False
    assert certification.orchestration_enabled is False
    assert certification.automatic_sequencing_enabled is False
    assert certification.schema_migration_execution_enabled is False
    assert certification.planner_integration_enabled is False
    assert certification.production_consumption_enabled is False
    assert certification.runtime_mutation_enabled is False
    assert certification.hidden_remediation_behavior_enabled is False
    assert certification.silent_drift_suppression_enabled is False
    assert all(not observation.drift_remediation_enabled for observation in certification.drift_observations)
    assert all(not observation.automatic_drift_correction_enabled for observation in certification.drift_observations)
    assert all(not observation.refresh_execution_enabled for observation in certification.drift_observations)
    assert certification.governance.production_consumption_enabled is False
    assert certification.governance.planner_integration_enabled is False


def test_v4_1_drift_identity_key_is_stable():
    certification = default_refresh_drift_certification()

    assert refresh_drift_identity_key(certification.identity) == (
        "v4_1.refresh_drift_certification.1"
        "|v4_1_phase_6_refresh_drift_certification"
        "|v4_1_refresh_drift_certification_primary|v4.1.0-phase-6"
        "|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary|v4_1_schema_evolution_governance_primary"
        "|v4_1_refresh_sequencing_visibility_primary"
        "|v4_1_refresh_drift_certification_provenance_primary"
        "|v4_1_refresh_drift_certification_lineage_primary"
    )


def test_v4_1_drift_serialization_hashing_and_equality_are_stable():
    first = default_refresh_drift_certification()
    second = default_refresh_drift_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_drift_certifications_equal(first, second)
    assert refresh_drift_identities_equal(first.identity, second.identity)
    assert serialize_refresh_drift_certification(first) == serialize_refresh_drift_certification(second)
    assert hash_refresh_drift_certification(first) == hash_refresh_drift_certification(second)
    assert hash_refresh_drift_certification_identity(first.identity) == hash_refresh_drift_certification_identity(second.identity)
    assert json.loads(serialize_refresh_drift_certification(first))["non_executable"] is True


def test_v4_1_drift_serialization_preserves_order_and_fail_visible_observations():
    certification = default_refresh_drift_certification()
    reordered = replace(certification, drift_observations=tuple(reversed(certification.drift_observations)))

    assert serialize_refresh_drift_certification(certification) == serialize_refresh_drift_certification(reordered)
    assert hash_refresh_drift_certification(certification) == hash_refresh_drift_certification(reordered)
    exported = export_refresh_drift_certification(reordered)
    assert [item["state"] for item in exported["drift_observations"]] == [
        DRIFT_STATE_VISIBLE,
        DRIFT_STATE_VISIBLE,
        DRIFT_STATE_VISIBLE,
        DRIFT_STATE_VISIBLE,
        DRIFT_STATE_VISIBLE,
        DRIFT_STATE_CROSS_LAYER_CONFLICT,
        DRIFT_STATE_STALE,
        DRIFT_STATE_UNSUPPORTED,
        DRIFT_STATE_PROHIBITED,
        DRIFT_STATE_BLOCKED,
        DRIFT_STATE_LINEAGE_DISCONTINUITY,
        DRIFT_STATE_PROVENANCE_DISCONTINUITY,
        DRIFT_STATE_REPLAY_DISCONTINUITY,
        DRIFT_STATE_ROLLBACK_DISCONTINUITY,
    ]
    assert exported["blocked_state_visibility"]["blocked_drift_ids"] == ["v4_1_drift_blocked_unresolved"]
    assert exported["unsupported_state_visibility"]["unsupported_drift_ids"] == ["v4_1_drift_unsupported_provider"]
    assert exported["unsupported_state_visibility"]["prohibited_drift_ids"] == ["v4_1_drift_prohibited_remediation"]


def test_v4_1_drift_visibility_validates_cross_layer_drift_classification():
    certification = default_refresh_drift_certification()
    visibility = validate_refresh_drift_visibility(certification)
    counts = count_drift_observation_states(certification.drift_observations)

    assert counts[DRIFT_STATE_VISIBLE] == 5
    assert counts[DRIFT_STATE_CROSS_LAYER_CONFLICT] == 1
    assert counts[DRIFT_STATE_STALE] == 1
    assert counts[DRIFT_STATE_UNSUPPORTED] == 1
    assert counts[DRIFT_STATE_PROHIBITED] == 1
    assert counts[DRIFT_STATE_BLOCKED] == 1
    assert counts[DRIFT_STATE_LINEAGE_DISCONTINUITY] == 1
    assert counts[DRIFT_STATE_PROVENANCE_DISCONTINUITY] == 1
    assert counts[DRIFT_STATE_REPLAY_DISCONTINUITY] == 1
    assert counts[DRIFT_STATE_ROLLBACK_DISCONTINUITY] == 1
    assert visibility["valid"] is True
    assert visibility["manifest_drift_visible"] is True
    assert visibility["dependency_drift_visible"] is True
    assert visibility["lineage_drift_visible"] is True
    assert visibility["schema_drift_visible"] is True
    assert visibility["sequencing_drift_visible"] is True
    assert visibility["cross_layer_conflict_visible"] is True
    assert visibility["blocked_drift_visible"] is True
    assert visibility["unsupported_drift_visible"] is True
    assert visibility["prohibited_drift_domain_visibility_count"] == len(PROHIBITED_DRIFT_DOMAINS)
    assert visibility["observation_execution_semantics_count"] == 0


def test_v4_1_drift_continuity_certifies_provenance_lineage_replay_and_rollback():
    certification = default_refresh_drift_certification()
    continuity = certify_refresh_drift_continuity(certification)

    with pytest.raises(FrozenInstanceError):
        certification.continuity_metadata.automatic_drift_correction_enabled = True

    assert continuity["valid"] is True
    assert continuity["drift_continuity_valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["drift_continuity"]["cross_layer_conflict_visibility_count"] == 1
    assert continuity["lineage_continuity"]["lineage_discontinuity_visibility_count"] == 1
    assert continuity["provenance_continuity"]["provenance_discontinuity_visibility_count"] == 1
    assert continuity["replay_continuity"]["replay_safe"] is True
    assert continuity["rollback_continuity"]["rollback_safe"] is True


def test_v4_1_drift_non_execution_validation_blocks_remediation_correction_production_and_planner_flags():
    certification = default_refresh_drift_certification()
    contaminated = replace(
        certification,
        drift_remediation_enabled=True,
        automatic_drift_correction_enabled=True,
        refresh_execution_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_refresh_drift_non_execution(contaminated)

    assert validate_refresh_drift_non_execution(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 5
    assert validation["drift_remediation_absent"] is False
    assert validation["automatic_drift_correction_absent"] is False
    assert validation["refresh_execution_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_drift_integrity_blocks_hidden_suppression_and_remediation_semantics():
    certification = default_refresh_drift_certification()
    hidden_observation = replace(
        certification.drift_observations[7],
        hidden=True,
        fail_visible=False,
        drift_remediation_enabled=True,
        automatic_drift_correction_enabled=True,
    )
    corrective_visibility = replace(
        certification.blocked_state_visibility,
        remediation_enabled=True,
        silent_drift_suppression_enabled=True,
    )
    contaminated = replace(
        certification,
        drift_observations=(
            *certification.drift_observations[:7],
            hidden_observation,
            *certification.drift_observations[8:],
        ),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_refresh_drift_integrity(contaminated)

    assert validate_refresh_drift_integrity(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_observation_count"] == 1
    assert validation["visibility_validation"]["observation_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 4


def test_v4_1_drift_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_refresh_drift_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_DRIFT_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["drift_remediation_absent"] is True
    assert diagnostics["automatic_drift_correction_absent"] is True
    assert diagnostics["automatic_repair_absent"] is True
    assert diagnostics["silent_drift_suppression_absent"] is True
    assert diagnostics["cross_layer_conflict_ids"] == ["v4_1_drift_cross_layer_conflict"]


def test_v4_1_drift_reports_contain_required_evidence_boundaries_and_cross_layer_certification():
    report = build_v4_1_refresh_drift_certification_report()
    diagnostics_report = build_v4_1_refresh_drift_diagnostics_report()
    continuity_report = build_v4_1_refresh_drift_continuity_certification_report()
    integrity_report = build_v4_1_refresh_drift_integrity_certification_report()
    cross_layer_report = build_v4_1_cross_layer_drift_certification_report()

    assert report["foundation_status"] == V4_1_REFRESH_DRIFT_CERTIFICATION_STATUS_STABLE
    assert report["drift_certification_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_drift_serialization_verified"] is True
    assert report["summary"]["deterministic_drift_hashing_verified"] is True
    assert report["summary"]["deterministic_drift_equality_verified"] is True
    assert report["summary"]["deterministic_drift_visibility_verified"] is True
    assert report["summary"]["cross_layer_drift_classification_validated"] is True
    assert report["summary"]["manifest_drift_visibility_validated"] is True
    assert report["summary"]["dependency_drift_visibility_validated"] is True
    assert report["summary"]["lineage_drift_visibility_validated"] is True
    assert report["summary"]["schema_drift_visibility_validated"] is True
    assert report["summary"]["sequencing_drift_visibility_validated"] is True
    assert report["summary"]["non_remediation_enforcement_validated"] is True
    assert report["summary"]["non_correction_enforcement_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert continuity_report["summary"]["continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert cross_layer_report["summary"]["cross_layer_drift_certification_verified"] is True
    assert "No drift remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No automatic sequencing exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No migration execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
