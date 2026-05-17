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

from operational_refresh.v4_1_closeout_readiness_continuity import (  # noqa: E402
    certify_v4_1_closeout_continuity,
)
from operational_refresh.v4_1_closeout_readiness_diagnostics import (  # noqa: E402
    build_v4_1_closeout_diagnostics,
    build_v4_1_final_governance_summary,
    build_v4_2_planning_readiness_certification,
)
from operational_refresh.v4_1_closeout_readiness_hashing import (  # noqa: E402
    hash_v4_1_closeout_identity,
    hash_v4_1_closeout_readiness,
)
from operational_refresh.v4_1_closeout_readiness_integrity import (  # noqa: E402
    v4_1_closeout_identities_equal,
    v4_1_closeout_identity_key,
    v4_1_closeout_readiness_equal,
    validate_v4_1_closeout_integrity,
    validate_v4_1_closeout_non_execution,
)
from operational_refresh.v4_1_closeout_readiness_models import (  # noqa: E402
    PROHIBITED_CLOSEOUT_DOMAINS,
    V4_1_CLOSEOUT_READINESS_SCHEMA_VERSION,
    V4_1_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_1_CLOSEOUT_STATUS_WITH_WARNINGS,
    V4_1_EXPECTED_MIGRATION_DOC_NAMES,
    V4_1_EXPECTED_PHASE_IDS,
    V4_1_EXPECTED_REPORT_NAMES,
    V4_1_EXPECTED_TEST_NAMES,
    V4_2_READINESS_WITH_WARNINGS,
    build_v4_1_closeout_readiness,
    default_v4_1_closeout_readiness,
)
from operational_refresh.v4_1_closeout_readiness_serialization import (  # noqa: E402
    export_v4_1_closeout_readiness,
    serialize_v4_1_closeout_readiness,
)
from operational_refresh.v4_1_closeout_readiness_visibility import (  # noqa: E402
    count_warning_categories,
    validate_v4_1_closeout_visibility,
)
from scripts.report_v4_1_closeout_and_v4_2_readiness import (  # noqa: E402
    build_v4_1_closeout_and_v4_2_readiness_report,
    build_v4_1_closeout_payload,
    build_v4_1_closeout_report,
    build_v4_1_cross_layer_governance_summary_report,
    build_v4_1_cross_layer_integrity_certification_report,
    build_v4_2_readiness_certification_report,
)


def test_v4_1_closeout_models_are_immutable_descriptive_and_non_executable():
    payload = default_v4_1_closeout_readiness()

    with pytest.raises(FrozenInstanceError):
        payload.execution_enabled = True

    assert payload.identity.schema_version == V4_1_CLOSEOUT_READINESS_SCHEMA_VERSION
    assert payload.non_executable is True
    assert payload.descriptive_only is True
    assert payload.remediation_enabled is False
    assert payload.automatic_correction_enabled is False
    assert payload.approval_enabled is False
    assert payload.authorization_enabled is False
    assert payload.refresh_execution_enabled is False
    assert payload.orchestration_enabled is False
    assert payload.planner_integration_enabled is False
    assert payload.production_consumption_enabled is False
    assert payload.runtime_mutation_enabled is False
    assert all(not phase.execution_enabled for phase in payload.phase_coverage)
    assert all(not report.production_consumption_enabled for report in payload.report_coverage)
    assert all(not warning.approval_enabled for warning in payload.warnings)


def test_v4_1_closeout_identity_key_is_stable():
    payload = default_v4_1_closeout_readiness()

    assert v4_1_closeout_identity_key(payload.identity) == (
        "v4_1.closeout_and_v4_2_readiness.1"
        "|v4_1_closeout_and_v4_2_readiness_primary"
        "|v4_1_refresh_governance_stack"
        "|v4.1.0-phase-10|9|38"
        "|v4_1_closeout_provenance_primary"
        "|v4_1_closeout_lineage_primary"
        "|v4_1_closeout_continuity_primary"
        "|v4_2_planning_readiness_primary"
    )


def test_v4_1_closeout_serialization_hashing_and_equality_are_stable():
    first = default_v4_1_closeout_readiness()
    second = default_v4_1_closeout_readiness()

    assert first == second
    assert hash(first) == hash(second)
    assert v4_1_closeout_readiness_equal(first, second)
    assert v4_1_closeout_identities_equal(first.identity, second.identity)
    assert serialize_v4_1_closeout_readiness(first) == serialize_v4_1_closeout_readiness(second)
    assert hash_v4_1_closeout_readiness(first) == hash_v4_1_closeout_readiness(second)
    assert hash_v4_1_closeout_identity(first.identity) == hash_v4_1_closeout_identity(second.identity)
    assert json.loads(serialize_v4_1_closeout_readiness(first))["non_executable"] is True


def test_v4_1_closeout_serialization_normalizes_ordering():
    payload = default_v4_1_closeout_readiness()
    reordered = replace(
        payload,
        phase_coverage=tuple(reversed(payload.phase_coverage)),
        report_coverage=tuple(reversed(payload.report_coverage)),
        warnings=tuple(reversed(payload.warnings)),
    )

    assert serialize_v4_1_closeout_readiness(payload) == serialize_v4_1_closeout_readiness(reordered)
    assert hash_v4_1_closeout_readiness(payload) == hash_v4_1_closeout_readiness(reordered)
    exported = export_v4_1_closeout_readiness(reordered)
    assert [phase["phase_number"] for phase in exported["phase_coverage"]] == list(range(1, 10))
    assert [warning["deterministic_order"] for warning in exported["warnings"]] == [10, 20, 30, 40, 50, 60]


def test_v4_1_closeout_visibility_validates_phase_report_doc_and_test_coverage():
    payload = default_v4_1_closeout_readiness()
    validation = validate_v4_1_closeout_visibility(payload)

    assert len(V4_1_EXPECTED_PHASE_IDS) == 9
    assert len(V4_1_EXPECTED_REPORT_NAMES) == 38
    assert len(V4_1_EXPECTED_MIGRATION_DOC_NAMES) == 9
    assert len(V4_1_EXPECTED_TEST_NAMES) == 9
    assert validation["valid"] is True
    assert validation["phase_coverage_complete"] is True
    assert validation["report_coverage_complete"] is True
    assert validation["migration_doc_coverage_complete"] is True
    assert validation["focused_test_coverage_complete"] is True
    assert validation["deterministic_hash_coverage_complete"] is True
    assert validation["prohibited_domains_visible"] is True
    assert set(payload.integrity_boundary.prohibited_domains) == set(PROHIBITED_CLOSEOUT_DOMAINS)


def test_v4_1_closeout_continuity_certifies_required_dimensions():
    certification = certify_v4_1_closeout_continuity(default_v4_1_closeout_readiness())

    assert certification["valid"] is True
    assert certification["phase_coverage_valid"] is True
    assert certification["report_coverage_valid"] is True
    assert certification["integrity_coverage_valid"] is True
    assert certification["continuity_coverage_valid"] is True
    assert certification["governance_verification_valid"] is True
    assert certification["replay_verification_valid"] is True
    assert certification["rollback_verification_valid"] is True
    assert certification["provenance_verification_valid"] is True
    assert certification["lineage_verification_valid"] is True
    assert certification["readiness_visibility_valid"] is True
    assert certification["warning_aggregation_valid"] is True
    assert certification["unsupported_prohibited_blocked_aggregation_valid"] is True


def test_v4_1_closeout_integrity_enforces_no_remediation_approval_or_execution():
    payload = default_v4_1_closeout_readiness()
    non_execution = validate_v4_1_closeout_non_execution(payload)
    integrity = validate_v4_1_closeout_integrity(payload)

    assert non_execution["valid"] is True
    assert non_execution["remediation_absent"] is True
    assert non_execution["automatic_correction_absent"] is True
    assert non_execution["approval_absent"] is True
    assert non_execution["authorization_absent"] is True
    assert non_execution["refresh_execution_absent"] is True
    assert non_execution["orchestration_absent"] is True
    assert non_execution["planner_integration_absent"] is True
    assert non_execution["production_consumption_absent"] is True
    assert integrity["valid"] is True
    assert integrity["prohibited_leakage_visible"] is True


def test_v4_1_closeout_warning_aggregation_is_fail_visible_and_descriptive():
    payload = default_v4_1_closeout_readiness()
    diagnostics = build_v4_1_closeout_diagnostics(payload)
    summary = build_v4_1_final_governance_summary(payload)
    readiness = build_v4_2_planning_readiness_certification(payload)
    warning_counts = count_warning_categories(payload.warnings)

    assert diagnostics["diagnostics_mode"] == "descriptive_closeout_only"
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["warning_count"] == 6
    assert all(warning_counts[category] == 1 for category in warning_counts if category != "invalid")
    assert summary["closeout_status"] == V4_1_CLOSEOUT_STATUS_WITH_WARNINGS
    assert summary["v4_2_readiness_status"] == V4_2_READINESS_WITH_WARNINGS
    assert readiness["readiness_certification_does_not_authorize_operations"] is True
    assert readiness["approval_enabled"] is False
    assert readiness["execution_enabled"] is False


def test_v4_1_closeout_detects_missing_report_coverage_without_correction():
    missing_report = V4_1_EXPECTED_REPORT_NAMES[0]
    payload = build_v4_1_closeout_readiness(report_presence={missing_report: False})
    visibility = validate_v4_1_closeout_visibility(payload)
    continuity = certify_v4_1_closeout_continuity(payload)

    assert visibility["valid"] is False
    assert missing_report in visibility["missing_report_names"]
    assert continuity["valid"] is False
    assert payload.readiness.closeout_status != V4_1_CLOSEOUT_STATUS_WITH_WARNINGS
    assert payload.remediation_enabled is False
    assert payload.automatic_correction_enabled is False


def test_v4_1_closeout_reports_include_required_readiness_and_boundary_sections():
    payload = build_v4_1_closeout_payload()
    report = build_v4_1_closeout_and_v4_2_readiness_report()
    closeout = build_v4_1_closeout_report()
    readiness = build_v4_2_readiness_certification_report()
    governance = build_v4_1_cross_layer_governance_summary_report()
    integrity = build_v4_1_cross_layer_integrity_certification_report()
    summary = report["summary"]

    assert payload.readiness.closeout_status == V4_1_CLOSEOUT_STATUS_WITH_WARNINGS
    assert report["foundation_status"] == V4_1_CLOSEOUT_READINESS_STATUS_STABLE
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_closeout_serialization_verified"] is True
    assert summary["deterministic_closeout_hashing_verified"] is True
    assert summary["deterministic_closeout_equality_verified"] is True
    assert summary["deterministic_closeout_visibility_verified"] is True
    assert summary["phase_coverage_validated"] is True
    assert summary["report_coverage_validated"] is True
    assert summary["integrity_coverage_validated"] is True
    assert summary["continuity_coverage_validated"] is True
    assert summary["replay_verification_validated"] is True
    assert summary["rollback_verification_validated"] is True
    assert summary["provenance_verification_validated"] is True
    assert summary["lineage_verification_validated"] is True
    assert summary["readiness_visibility_validated"] is True
    assert summary["warning_aggregation_validated"] is True
    assert summary["unsupported_prohibited_blocked_aggregation_validated"] is True
    assert summary["non_remediation_enforcement_validated"] is True
    assert summary["non_correction_enforcement_validated"] is True
    assert summary["non_approval_authorization_enforcement_validated"] is True
    assert summary["non_execution_enforcement_validated"] is True
    assert summary["production_consumption_disabled_validated"] is True
    assert summary["planner_integration_disabled_validated"] is True
    assert summary["integrity_validation_verified"] is True
    assert summary["certification_validation_verified"] is True
    assert summary["closeout_readiness_validation_verified"] is True
    assert "No readiness certification becomes operational authorization." in report["explicit_prohibitions"]
    assert closeout["v4_1_closeout"]["readiness_mode"] == "planning_ready_with_warnings_descriptive_only"
    assert readiness["v4_2_readiness_certification"]["execution_enabled"] is False
    assert governance["cross_layer_governance_summary"]["non_execution_valid"] is True
    assert integrity["cross_layer_integrity_certification"]["valid"] is True
