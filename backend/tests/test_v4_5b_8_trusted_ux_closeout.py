from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from public_trust_visibility.v4_5b_8_trusted_ux_closeout_audit import (  # noqa: E402
    build_v4_5b_8_trusted_ux_closeout,
    build_v4_5b_8_trusted_ux_closeout_report,
    contaminate_v4_5b_8_trusted_ux_closeout_for_non_operational_validation,
    enabled_trusted_ux_capability_flags,
    trusted_ux_capability_counter_values,
    trusted_ux_closeout_equal,
    validate_closeout_record_stability,
    validate_descriptive_only_trusted_ux_guarantees,
    validate_fail_visible_trusted_ux_closeout_diagnostics,
    validate_frontend_readiness_visibility_stability,
    validate_inherited_prohibition_preservation_stability,
    validate_lineage_and_provenance_preservation,
    validate_migration_document_coverage_certification_stability,
    validate_phase_coverage_certification_stability,
    validate_public_trust_continuity_certification,
    validate_readiness_record_stability,
    validate_report_coverage_certification_stability,
    validate_trusted_ux_closeout_identity_integrity,
    validate_trusted_ux_closeout_ordering_stability,
    validate_trusted_ux_closeout_serialization_and_hashing,
    validate_unsupported_state_preservation_stability,
    validate_v4_5b_8_trusted_ux_closeout,
)
from public_trust_visibility.v4_5b_8_trusted_ux_closeout_hashing import (  # noqa: E402
    hash_generated_report_coverage_record,
    hash_phase_coverage_record,
    hash_public_trust_continuity_record,
    hash_trusted_ux_closeout_diagnostic_record,
    hash_trusted_ux_closeout_identity,
    hash_trusted_ux_closeout_record,
    hash_trusted_ux_readiness_record,
    hash_v4_5b_8_trusted_ux_closeout,
)
from public_trust_visibility.v4_5b_8_trusted_ux_closeout_models import (  # noqa: E402
    CLOSEOUT_DIAGNOSTIC_TYPES,
    FRONTEND_READINESS_TYPES,
    FRONTEND_READINESS_VISIBILITY_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    MIGRATION_DOCUMENT_COVERAGE_TYPES,
    PHASE_ARTIFACTS,
    PUBLIC_TRUST_CONTINUITY_TYPES,
    REPORT_COVERAGE_TYPES,
    TRUSTED_UX_CLOSEOUT_TYPES,
    TRUSTED_UX_READINESS_NON_AUTHORITY_STATEMENT,
    TRUSTED_UX_READINESS_STATEMENT,
    UNSUPPORTED_STATE_CERTIFICATION_TYPES,
    UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_SCHEMA_VERSION,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_8_trusted_ux_closeout_serialization import (  # noqa: E402
    serialize_v4_5b_8_trusted_ux_closeout,
)
from public_trust_visibility.v4_5b_8_trusted_ux_closeout_visibility import (  # noqa: E402
    descriptive_only_trusted_ux_summary,
    readiness_classification_summary,
    trusted_ux_closeout_diagnostic_summary,
    trusted_ux_readiness_summary,
    unsupported_operational_state_summary,
    validate_required_trusted_ux_closeout_visibility,
)


def test_v4_5b_8_models_are_immutable_and_descriptive_only():
    certification = build_v4_5b_8_trusted_ux_closeout()

    with pytest.raises(FrozenInstanceError):
        certification.frontend_launch_authorization_enabled = True

    assert certification.identity.schema_version == (
        V4_5B_8_TRUSTED_UX_CLOSEOUT_SCHEMA_VERSION
    )
    assert certification.descriptive_only is True
    assert certification.publicly_transparent is True
    assert certification.non_operational is True
    assert certification.non_executing is True
    assert certification.non_authorizing is True
    assert certification.non_approving is True
    assert certification.non_remediating is True
    assert certification.non_runtime_mutating is True
    assert certification.non_ranking is True
    assert certification.non_recommending is True
    assert certification.non_scoring is True
    assert certification.non_triaging is True
    assert certification.frontend_launch_authorization_enabled is False
    assert certification.production_enablement_enabled is False
    assert certification.ui_authorization_enabled is False
    assert certification.ui_approval_enabled is False
    assert certification.scoring_enabled is False
    assert certification.ranking_enabled is False
    assert certification.recommendation_enabled is False
    assert certification.triage_enabled is False
    assert enabled_trusted_ux_capability_flags(certification) == {}
    assert all(
        value == 0
        for value in trusted_ux_capability_counter_values(certification).values()
    )


def test_v4_5b_8_required_visibility_sets_are_complete():
    certification = build_v4_5b_8_trusted_ux_closeout()
    visibility = validate_required_trusted_ux_closeout_visibility(certification)

    assert visibility["valid"] is True
    assert set(visibility["closeout_counts"]) == set(TRUSTED_UX_CLOSEOUT_TYPES)
    assert set(visibility["readiness_counts"]) == set(FRONTEND_READINESS_TYPES)
    assert set(visibility["phase_counts"]) == {item[0] for item in PHASE_ARTIFACTS}
    assert set(visibility["report_counts"]) == set(REPORT_COVERAGE_TYPES)
    assert set(visibility["migration_counts"]) == set(
        MIGRATION_DOCUMENT_COVERAGE_TYPES
    )
    assert set(visibility["continuity_counts"]) == set(PUBLIC_TRUST_CONTINUITY_TYPES)
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_STATE_CERTIFICATION_TYPES
    )
    assert set(visibility["inherited_counts"]) == set(
        INHERITED_PROHIBITION_CERTIFICATION_TYPES
    )
    assert set(visibility["frontend_counts"]) == set(
        FRONTEND_READINESS_VISIBILITY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(CLOSEOUT_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES
    )
    assert visibility["missing_phase_coverage"] == []
    assert visibility["missing_report_coverage"] == []
    assert visibility["missing_migration_document_coverage"] == []
    assert visibility["missing_closeout_diagnostics"] == []


def test_v4_5b_8_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_8_trusted_ux_closeout()
    second = build_v4_5b_8_trusted_ux_closeout()
    serialization = validate_trusted_ux_closeout_serialization_and_hashing(first)

    assert first == second
    assert trusted_ux_closeout_equal(first, second)
    assert serialize_v4_5b_8_trusted_ux_closeout(first) == (
        serialize_v4_5b_8_trusted_ux_closeout(second)
    )
    assert hash_v4_5b_8_trusted_ux_closeout(first) == (
        hash_v4_5b_8_trusted_ux_closeout(second)
    )
    assert serialization["valid"] is True
    assert serialization["serialization_stable"] is True
    assert serialization["hashing_stable"] is True
    assert len(hash_trusted_ux_closeout_identity(first.identity)) == 64
    assert len(hash_trusted_ux_closeout_record(first.closeout_records[0])) == 64
    assert len(hash_trusted_ux_readiness_record(first.readiness_records[0])) == 64
    assert len(hash_phase_coverage_record(first.phase_coverage_records[0])) == 64
    assert len(
        hash_generated_report_coverage_record(first.report_coverage_records[0])
    ) == 64
    assert len(
        hash_public_trust_continuity_record(
            first.public_trust_continuity_records[0]
        )
    ) == 64
    assert len(
        hash_trusted_ux_closeout_diagnostic_record(
            first.closeout_diagnostic_records[0]
        )
    ) == 64


def test_v4_5b_8_ordering_survives_reordered_collections():
    certification = build_v4_5b_8_trusted_ux_closeout()
    reordered = replace(
        certification,
        closeout_records=tuple(reversed(certification.closeout_records)),
        readiness_records=tuple(reversed(certification.readiness_records)),
        phase_coverage_records=tuple(reversed(certification.phase_coverage_records)),
        report_coverage_records=tuple(reversed(certification.report_coverage_records)),
        migration_document_coverage_records=tuple(
            reversed(certification.migration_document_coverage_records)
        ),
        public_trust_continuity_records=tuple(
            reversed(certification.public_trust_continuity_records)
        ),
        unsupported_state_records=tuple(
            reversed(certification.unsupported_state_records)
        ),
        inherited_prohibition_records=tuple(
            reversed(certification.inherited_prohibition_records)
        ),
        frontend_readiness_records=tuple(
            reversed(certification.frontend_readiness_records)
        ),
        closeout_diagnostic_records=tuple(
            reversed(certification.closeout_diagnostic_records)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(certification.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(certification.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(certification.inherited_constraints)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
    )

    assert validate_trusted_ux_closeout_ordering_stability(certification)[
        "valid"
    ] is True
    assert serialize_v4_5b_8_trusted_ux_closeout(
        certification
    ) == serialize_v4_5b_8_trusted_ux_closeout(reordered)
    assert hash_v4_5b_8_trusted_ux_closeout(certification) == (
        hash_v4_5b_8_trusted_ux_closeout(reordered)
    )


def test_v4_5b_8_closeout_layers_are_stable():
    certification = build_v4_5b_8_trusted_ux_closeout()

    assert validate_trusted_ux_closeout_identity_integrity(certification)["valid"] is True
    assert validate_closeout_record_stability(certification)["valid"] is True
    assert validate_readiness_record_stability(certification)["valid"] is True
    assert validate_phase_coverage_certification_stability(certification)["valid"] is True
    assert validate_report_coverage_certification_stability(certification)["valid"] is True
    assert (
        validate_migration_document_coverage_certification_stability(certification)[
            "valid"
        ]
        is True
    )
    assert validate_public_trust_continuity_certification(certification)["valid"] is True
    assert validate_unsupported_state_preservation_stability(certification)["valid"] is True
    assert (
        validate_inherited_prohibition_preservation_stability(certification)["valid"]
        is True
    )
    assert validate_frontend_readiness_visibility_stability(certification)["valid"] is True


def test_v4_5b_8_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    certification = build_v4_5b_8_trusted_ux_closeout()
    lineage = validate_lineage_and_provenance_preservation(certification)
    diagnostics = validate_fail_visible_trusted_ux_closeout_diagnostics(certification)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["continuity_reference_preserved"] is True
    assert diagnostics["valid"] is True
    assert diagnostics["diagnostic_visibility"]["missing_types"] == []
    assert diagnostics["unsupported_operational_visibility"]["missing_types"] == []
    assert diagnostics["missing_explicit_reasons"] == []


def test_v4_5b_8_visibility_helpers_preserve_descriptive_only_boundaries():
    certification = build_v4_5b_8_trusted_ux_closeout()
    readiness = trusted_ux_readiness_summary(certification.readiness_records)
    diagnostics = trusted_ux_closeout_diagnostic_summary(
        certification.closeout_diagnostic_records
    )
    unsupported = unsupported_operational_state_summary(
        certification.unsupported_operational_state_visibility
    )
    descriptive = descriptive_only_trusted_ux_summary(certification)
    classifications = readiness_classification_summary(certification.readiness_records)

    assert readiness[0]["frontend_launch_enabled"] is False
    assert readiness[0]["production_enablement_enabled"] is False
    assert diagnostics[0]["silent_fallback_enabled"] is False
    assert diagnostics[0]["triage_enabled"] is False
    assert unsupported[0]["suppression_enabled"] is False
    assert unsupported[0]["scoring_enabled"] is False
    assert descriptive["trusted_ux_readiness_statement"] == (
        TRUSTED_UX_READINESS_STATEMENT
    )
    assert descriptive["trusted_ux_readiness_non_authority_statement"] == (
        TRUSTED_UX_READINESS_NON_AUTHORITY_STATEMENT
    )
    assert descriptive["non_scoring"] is True
    assert descriptive["non_triaging"] is True
    assert set(classifications) == set(FRONTEND_READINESS_TYPES)
    assert all(value.endswith("_descriptive_only_ready") for value in classifications.values())


def test_v4_5b_8_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_8_trusted_ux_closeout_for_non_operational_validation()
    )
    guarantees = validate_descriptive_only_trusted_ux_guarantees(contaminated)
    counters = guarantees["counters"]

    assert guarantees["valid"] is False
    assert counters["enabled_runtime_execution_count"] > 0
    assert counters["enabled_frontend_launch_authorization_count"] > 0
    assert counters["enabled_production_enablement_count"] > 0
    assert counters["enabled_ui_authorization_count"] > 0
    assert counters["enabled_ui_approval_count"] > 0
    assert counters["enabled_scoring_count"] > 0
    assert counters["enabled_ranking_count"] > 0
    assert counters["enabled_recommendation_count"] > 0
    assert counters["enabled_triage_count"] > 0
    assert counters["enabled_remediation_count"] > 0
    assert counters["enabled_planner_integration_count"] > 0


def test_v4_5b_8_report_is_replay_safe_and_certifies_boundaries():
    report = build_v4_5b_8_trusted_ux_closeout_report()
    second_report = build_v4_5b_8_trusted_ux_closeout_report()
    summary = report["summary"]
    validation = validate_v4_5b_8_trusted_ux_closeout()

    assert report == second_report
    assert report["foundation_status"] == V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_STABLE
    assert report["deterministic_report_hash"] == (
        second_report["deterministic_report_hash"]
    )
    assert summary["deterministic_closeout_serialization_verified"] is True
    assert summary["deterministic_closeout_hashing_verified"] is True
    assert summary["phase_coverage_stable"] is True
    assert summary["report_coverage_stable"] is True
    assert summary["migration_document_coverage_stable"] is True
    assert summary["public_trust_continuity_preserved"] is True
    assert summary["unsupported_state_preservation_stable"] is True
    assert summary["fail_visible_closeout_diagnostics_preserved"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["validation_error_count"] == 0
    assert "NON-scoring" in summary["repository_remains"]
    assert "NON-triaging" in summary["repository_remains"]
    assert summary["trusted_ux_readiness_statement"] == TRUSTED_UX_READINESS_STATEMENT
    assert summary["trusted_ux_readiness_non_authority_statement"] == (
        TRUSTED_UX_READINESS_NON_AUTHORITY_STATEMENT
    )
    assert set(report["readiness_classifications"]) == set(FRONTEND_READINESS_TYPES)
    assert validation["valid"] is True
