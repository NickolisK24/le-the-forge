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

from operational_refresh.refresh_replay_rollback_visibility_continuity import (  # noqa: E402
    certify_replay_rollback_visibility_continuity,
)
from operational_refresh.refresh_replay_rollback_visibility_diagnostics import (  # noqa: E402
    build_replay_diagnostics,
    build_replay_rollback_diagnostics,
    build_rollback_diagnostics,
)
from operational_refresh.refresh_replay_rollback_visibility_hashing import (  # noqa: E402
    hash_refresh_replay_rollback_visibility,
    hash_replay_rollback_identity,
)
from operational_refresh.refresh_replay_rollback_visibility_integrity import (  # noqa: E402
    replay_rollback_identities_equal,
    replay_rollback_identity_key,
    refresh_replay_rollback_visibilities_equal,
    validate_replay_rollback_integrity,
    validate_replay_rollback_non_execution,
)
from operational_refresh.refresh_replay_rollback_visibility_models import (  # noqa: E402
    PROHIBITED_REPLAY_DOMAINS,
    PROHIBITED_ROLLBACK_DOMAINS,
    REPLAY_ROLLBACK_STATE_BLOCKED,
    REPLAY_ROLLBACK_STATE_PROHIBITED,
    REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT,
    REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT,
    REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY,
    REPLAY_ROLLBACK_STATE_STALE,
    REPLAY_ROLLBACK_STATE_UNSUPPORTED,
    REPLAY_ROLLBACK_STATE_VISIBLE,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_SCHEMA_VERSION,
    V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_STABLE,
    default_refresh_replay_rollback_visibility,
)
from operational_refresh.refresh_replay_rollback_visibility_serialization import (  # noqa: E402
    export_refresh_replay_rollback_visibility,
    serialize_refresh_replay_rollback_visibility,
)
from operational_refresh.refresh_replay_rollback_visibility_visibility import (  # noqa: E402
    count_replay_rollback_evidence_states,
    validate_refresh_replay_rollback_visibility,
)
from scripts.report_v4_1_refresh_replay_rollback_visibility import (  # noqa: E402
    build_v4_1_refresh_replay_continuity_certification_report,
    build_v4_1_refresh_replay_diagnostics_report,
    build_v4_1_refresh_replay_rollback_integrity_certification_report,
    build_v4_1_refresh_replay_rollback_visibility_report,
    build_v4_1_refresh_rollback_continuity_certification_report,
    build_v4_1_refresh_rollback_diagnostics_report,
)


def test_v4_1_replay_rollback_models_are_immutable_non_recovering_and_non_executable():
    visibility = default_refresh_replay_rollback_visibility()

    with pytest.raises(FrozenInstanceError):
        visibility.replay_execution_enabled = True

    assert visibility.identity.schema_version == V4_1_REPLAY_ROLLBACK_VISIBILITY_SCHEMA_VERSION
    assert visibility.non_executable is True
    assert visibility.descriptive_only is True
    assert visibility.rollback_execution_enabled is False
    assert visibility.replay_execution_enabled is False
    assert visibility.recovery_execution_enabled is False
    assert visibility.automatic_rollback_enabled is False
    assert visibility.automatic_recovery_enabled is False
    assert visibility.remediation_enabled is False
    assert visibility.automatic_correction_enabled is False
    assert visibility.orchestration_enabled is False
    assert visibility.planner_integration_enabled is False
    assert visibility.production_consumption_enabled is False
    assert visibility.runtime_mutation_enabled is False
    assert all(not item.replay_execution_enabled for item in visibility.evidence)
    assert all(not item.rollback_execution_enabled for item in visibility.evidence)
    assert all(not item.recovery_execution_enabled for item in visibility.evidence)
    assert visibility.governance.production_consumption_enabled is False
    assert visibility.governance.planner_integration_enabled is False


def test_v4_1_replay_rollback_identity_key_is_stable():
    visibility = default_refresh_replay_rollback_visibility()

    assert replay_rollback_identity_key(visibility.identity) == (
        "v4_1.refresh_replay_rollback_visibility.1"
        "|v4_1_phase_7_refresh_replay_rollback_visibility"
        "|v4_1_refresh_replay_rollback_visibility_primary|v4.1.0-phase-7"
        "|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary|v4_1_schema_evolution_governance_primary"
        "|v4_1_refresh_sequencing_visibility_primary|v4_1_refresh_drift_certification_primary"
        "|v4_1_replay_visibility_primary|v4_1_rollback_visibility_primary"
        "|v4_1_replay_rollback_provenance_primary|v4_1_replay_rollback_lineage_primary"
    )


def test_v4_1_replay_rollback_serialization_hashing_and_equality_are_stable():
    first = default_refresh_replay_rollback_visibility()
    second = default_refresh_replay_rollback_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_replay_rollback_visibilities_equal(first, second)
    assert replay_rollback_identities_equal(first.identity, second.identity)
    assert serialize_refresh_replay_rollback_visibility(first) == serialize_refresh_replay_rollback_visibility(second)
    assert hash_refresh_replay_rollback_visibility(first) == hash_refresh_replay_rollback_visibility(second)
    assert hash_replay_rollback_identity(first.identity) == hash_replay_rollback_identity(second.identity)
    assert json.loads(serialize_refresh_replay_rollback_visibility(first))["non_executable"] is True


def test_v4_1_replay_rollback_serialization_preserves_order_and_fail_visible_evidence():
    visibility = default_refresh_replay_rollback_visibility()
    reordered = replace(visibility, evidence=tuple(reversed(visibility.evidence)))

    assert serialize_refresh_replay_rollback_visibility(visibility) == serialize_refresh_replay_rollback_visibility(reordered)
    assert hash_refresh_replay_rollback_visibility(visibility) == hash_refresh_replay_rollback_visibility(reordered)
    exported = export_refresh_replay_rollback_visibility(reordered)
    assert [item["state"] for item in exported["evidence"]] == [
        *(REPLAY_ROLLBACK_STATE_VISIBLE for _ in range(12)),
        REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT,
        REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT,
        REPLAY_ROLLBACK_STATE_REPLAY_LINEAGE_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_ROLLBACK_LINEAGE_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_REPLAY_PROVENANCE_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_ROLLBACK_PROVENANCE_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_REPLAY_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_ROLLBACK_DISCONTINUITY,
        REPLAY_ROLLBACK_STATE_STALE,
        REPLAY_ROLLBACK_STATE_STALE,
        REPLAY_ROLLBACK_STATE_UNSUPPORTED,
        REPLAY_ROLLBACK_STATE_UNSUPPORTED,
        REPLAY_ROLLBACK_STATE_PROHIBITED,
        REPLAY_ROLLBACK_STATE_PROHIBITED,
        REPLAY_ROLLBACK_STATE_BLOCKED,
        REPLAY_ROLLBACK_STATE_BLOCKED,
    ]
    assert exported["blocked_state_visibility"]["blocked_replay_ids"] == ["v4_1_replay_blocked_state"]
    assert exported["unsupported_state_visibility"]["unsupported_replay_ids"] == ["v4_1_replay_unsupported_provider"]
    assert exported["unsupported_state_visibility"]["prohibited_rollback_ids"] == ["v4_1_rollback_prohibited_execution"]


def test_v4_1_replay_rollback_visibility_validates_stack_blocked_unsupported_and_drift_states():
    visibility = default_refresh_replay_rollback_visibility()
    validation = validate_refresh_replay_rollback_visibility(visibility)
    counts = count_replay_rollback_evidence_states(visibility.evidence)

    assert counts[REPLAY_ROLLBACK_STATE_VISIBLE] == 12
    assert counts[REPLAY_ROLLBACK_STATE_REPLAY_DRIFT_CONFLICT] == 1
    assert counts[REPLAY_ROLLBACK_STATE_ROLLBACK_DRIFT_CONFLICT] == 1
    assert counts[REPLAY_ROLLBACK_STATE_STALE] == 2
    assert counts[REPLAY_ROLLBACK_STATE_UNSUPPORTED] == 2
    assert counts[REPLAY_ROLLBACK_STATE_PROHIBITED] == 2
    assert counts[REPLAY_ROLLBACK_STATE_BLOCKED] == 2
    assert validation["valid"] is True
    assert validation["replay_stack_visible"] is True
    assert validation["rollback_stack_visible"] is True
    assert validation["blocked_replay_visible"] is True
    assert validation["blocked_rollback_visible"] is True
    assert validation["unsupported_replay_visible"] is True
    assert validation["unsupported_rollback_visible"] is True
    assert validation["replay_drift_conflict_visible"] is True
    assert validation["rollback_drift_conflict_visible"] is True
    assert validation["prohibited_replay_domain_visibility_count"] == len(PROHIBITED_REPLAY_DOMAINS)
    assert validation["prohibited_rollback_domain_visibility_count"] == len(PROHIBITED_ROLLBACK_DOMAINS)
    assert validation["evidence_execution_semantics_count"] == 0


def test_v4_1_replay_rollback_continuity_certifies_replay_rollback_lineage_provenance_and_drift():
    visibility = default_refresh_replay_rollback_visibility()
    continuity = certify_replay_rollback_visibility_continuity(visibility)

    with pytest.raises(FrozenInstanceError):
        visibility.continuity_metadata.recovery_execution_enabled = True

    assert continuity["valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True
    assert continuity["replay_lineage_continuity_valid"] is True
    assert continuity["rollback_lineage_continuity_valid"] is True
    assert continuity["replay_provenance_continuity_valid"] is True
    assert continuity["rollback_provenance_continuity_valid"] is True
    assert continuity["replay_drift_valid"] is True
    assert continuity["rollback_drift_valid"] is True


def test_v4_1_replay_rollback_non_execution_validation_blocks_recovery_remediation_production_and_planner_flags():
    visibility = default_refresh_replay_rollback_visibility()
    contaminated = replace(
        visibility,
        replay_execution_enabled=True,
        rollback_execution_enabled=True,
        recovery_execution_enabled=True,
        remediation_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_replay_rollback_non_execution(contaminated)

    assert validate_replay_rollback_non_execution(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 6
    assert validation["replay_execution_absent"] is False
    assert validation["rollback_execution_absent"] is False
    assert validation["recovery_execution_absent"] is False
    assert validation["remediation_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_replay_rollback_integrity_blocks_hidden_correction_and_execution_semantics():
    visibility = default_refresh_replay_rollback_visibility()
    hidden_evidence = replace(
        visibility.evidence[22],
        hidden=True,
        fail_visible=False,
        replay_execution_enabled=True,
        remediation_enabled=True,
        automatic_correction_enabled=True,
    )
    corrective_visibility = replace(
        visibility.blocked_state_visibility,
        recovery_execution_enabled=True,
        automatic_correction_enabled=True,
    )
    contaminated = replace(
        visibility,
        evidence=(*visibility.evidence[:22], hidden_evidence, *visibility.evidence[23:]),
        blocked_state_visibility=corrective_visibility,
    )
    validation = validate_replay_rollback_integrity(contaminated)

    assert validate_replay_rollback_integrity(visibility)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_evidence_count"] == 1
    assert validation["visibility_validation"]["evidence_execution_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 6


def test_v4_1_replay_rollback_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_replay_rollback_diagnostics()
    replay_diagnostics = build_replay_diagnostics()
    rollback_diagnostics = build_rollback_diagnostics()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_REPLAY_DOMAINS) + len(PROHIBITED_ROLLBACK_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["replay_execution_absent"] is True
    assert diagnostics["rollback_execution_absent"] is True
    assert diagnostics["recovery_execution_absent"] is True
    assert diagnostics["remediation_absent"] is True
    assert diagnostics["automatic_correction_absent"] is True
    assert replay_diagnostics["replay_execution_absent"] is True
    assert rollback_diagnostics["rollback_execution_absent"] is True


def test_v4_1_replay_rollback_reports_contain_required_evidence_boundaries_and_certification():
    report = build_v4_1_refresh_replay_rollback_visibility_report()
    replay_diagnostics_report = build_v4_1_refresh_replay_diagnostics_report()
    rollback_diagnostics_report = build_v4_1_refresh_rollback_diagnostics_report()
    replay_continuity_report = build_v4_1_refresh_replay_continuity_certification_report()
    rollback_continuity_report = build_v4_1_refresh_rollback_continuity_certification_report()
    integrity_report = build_v4_1_refresh_replay_rollback_integrity_certification_report()

    assert report["foundation_status"] == V4_1_REPLAY_ROLLBACK_VISIBILITY_STATUS_STABLE
    assert report["replay_rollback_visibility_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_replay_rollback_serialization_verified"] is True
    assert report["summary"]["deterministic_replay_rollback_hashing_verified"] is True
    assert report["summary"]["deterministic_replay_rollback_equality_verified"] is True
    assert report["summary"]["deterministic_replay_rollback_visibility_verified"] is True
    assert report["summary"]["replay_continuity_validated"] is True
    assert report["summary"]["rollback_continuity_validated"] is True
    assert report["summary"]["blocked_replay_visibility_validated"] is True
    assert report["summary"]["blocked_rollback_visibility_validated"] is True
    assert report["summary"]["unsupported_state_visibility_validated"] is True
    assert report["summary"]["replay_drift_validated"] is True
    assert report["summary"]["rollback_drift_validated"] is True
    assert report["summary"]["non_recovery_enforcement_validated"] is True
    assert report["summary"]["non_remediation_enforcement_validated"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert replay_diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert rollback_diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert replay_continuity_report["summary"]["replay_continuity_certification_verified"] is True
    assert rollback_continuity_report["summary"]["rollback_continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No rollback execution exists." in report["explicit_prohibitions"]
    assert "No replay execution exists." in report["explicit_prohibitions"]
    assert "No recovery execution exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No automatic sequencing exists." in report["explicit_prohibitions"]
    assert "No migration execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
