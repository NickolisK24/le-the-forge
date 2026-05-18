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

from orchestration_governance.v4_5a_8_readiness_closeout_audit import (  # noqa: E402
    build_v4_5a_8_readiness_closeout,
    build_v4_5a_8_readiness_closeout_report,
    contaminate_v4_5a_8_readiness_closeout_for_non_operational_validation,
    enabled_readiness_closeout_capability_flags,
    readiness_closeout_capability_counter_values,
    readiness_closeout_equal,
    validate_closeout_identity_integrity,
    validate_closeout_ordering_stability,
    validate_continuity_certification_stability,
    validate_descriptive_only_readiness_closeout_guarantees,
    validate_fail_visible_closeout_diagnostics,
    validate_inherited_prohibition_preservation_stability,
    validate_lineage_and_provenance_preservation,
    validate_migration_documentation_certification_stability,
    validate_phase_coverage_certification_stability,
    validate_readiness_closeout_serialization_and_hashing,
    validate_readiness_visibility_stability,
    validate_report_coverage_certification_stability,
    validate_unsupported_state_preservation_stability,
    validate_v4_5a_8_readiness_closeout,
)
from orchestration_governance.v4_5a_8_readiness_closeout_hashing import (  # noqa: E402
    hash_closeout_diagnostic_record,
    hash_closeout_record,
    hash_phase_coverage_certification,
    hash_readiness_certification_record,
    hash_readiness_closeout_identity,
    hash_v4_5a_8_readiness_closeout,
)
from orchestration_governance.v4_5a_8_readiness_closeout_models import (  # noqa: E402
    CLOSEOUT_DIAGNOSTIC_TYPES,
    CONTINUITY_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_PRESERVATION_TYPES,
    PHASE_COVERAGE_TYPES,
    READINESS_TARGETS,
    READINESS_VISIBILITY_TYPES,
    UNSUPPORTED_READINESS_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    V4_5A_8_READINESS_CLOSEOUT_SCHEMA_VERSION,
    V4_5A_8_READINESS_CLOSEOUT_STATUS_STABLE,
)
from orchestration_governance.v4_5a_8_readiness_closeout_serialization import (  # noqa: E402
    serialize_v4_5a_8_readiness_closeout,
)
from orchestration_governance.v4_5a_8_readiness_closeout_visibility import (  # noqa: E402
    closeout_summary_visibility,
    continuity_certification_summary_visibility,
    descriptive_only_readiness_closeout_summary,
    fail_visible_closeout_diagnostic_summaries,
    inherited_prohibition_summary_visibility,
    migration_document_summary_visibility,
    phase_coverage_summary_visibility,
    readiness_summary_visibility,
    readiness_visibility_summary,
    report_coverage_summary_visibility,
    unsupported_readiness_visibility_summaries,
    unsupported_state_summary_visibility,
    validate_required_readiness_closeout_visibility,
)


def test_v4_5a_8_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_8_readiness_closeout()

    with pytest.raises(FrozenInstanceError):
        intelligence.readiness_authorization_enabled = True

    assert (
        intelligence.closeout_identity.schema_version
        == V4_5A_8_READINESS_CLOSEOUT_SCHEMA_VERSION
    )
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_approving is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.non_ranking is True
    assert intelligence.non_recommending is True
    assert intelligence.readiness_authorization_enabled is False
    assert intelligence.readiness_approval_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_readiness_closeout_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in readiness_closeout_capability_counter_values(intelligence).values()
    )


def test_v4_5a_8_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_8_readiness_closeout()
    visibility = validate_required_readiness_closeout_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["phase_counts"]) == set(PHASE_COVERAGE_TYPES)
    assert set(visibility["report_counts"]) == set(PHASE_COVERAGE_TYPES)
    assert set(visibility["document_counts"]) == set(PHASE_COVERAGE_TYPES)
    assert set(visibility["continuity_counts"]) == set(CONTINUITY_CERTIFICATION_TYPES)
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_STATE_PRESERVATION_TYPES
    )
    assert set(visibility["prohibition_counts"]) == set(
        INHERITED_PROHIBITION_PRESERVATION_TYPES
    )
    assert set(visibility["readiness_counts"]) == set(READINESS_TARGETS)
    assert set(visibility["readiness_visibility_counts"]) == set(
        READINESS_VISIBILITY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(CLOSEOUT_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_READINESS_OPERATIONAL_STATES
    )
    assert visibility["missing_phase_types"] == []
    assert visibility["missing_report_types"] == []
    assert visibility["missing_document_types"] == []
    assert visibility["missing_readiness_targets"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_8_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_8_readiness_closeout()
    second = build_v4_5a_8_readiness_closeout()
    serialization = validate_readiness_closeout_serialization_and_hashing(first)

    assert first == second
    assert readiness_closeout_equal(first, second)
    assert serialize_v4_5a_8_readiness_closeout(first) == (
        serialize_v4_5a_8_readiness_closeout(second)
    )
    assert hash_v4_5a_8_readiness_closeout(first) == (
        hash_v4_5a_8_readiness_closeout(second)
    )
    assert serialization["valid"] is True
    assert len(hash_readiness_closeout_identity(first.closeout_identity)) == 64
    assert len(hash_closeout_record(first.closeout_records[0])) == 64
    assert len(hash_readiness_certification_record(first.readiness_certifications[0])) == 64
    assert len(hash_phase_coverage_certification(first.phase_coverage_certifications[0])) == 64
    assert len(hash_closeout_diagnostic_record(first.closeout_diagnostics[0])) == 64


def test_v4_5a_8_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_8_readiness_closeout()
    reordered = replace(
        intelligence,
        closeout_records=tuple(reversed(intelligence.closeout_records)),
        readiness_certifications=tuple(reversed(intelligence.readiness_certifications)),
        phase_coverage_certifications=tuple(
            reversed(intelligence.phase_coverage_certifications)
        ),
        report_coverage_certifications=tuple(
            reversed(intelligence.report_coverage_certifications)
        ),
        migration_document_certifications=tuple(
            reversed(intelligence.migration_document_certifications)
        ),
        continuity_certifications=tuple(
            reversed(intelligence.continuity_certifications)
        ),
        unsupported_state_certifications=tuple(
            reversed(intelligence.unsupported_state_certifications)
        ),
        inherited_prohibition_certifications=tuple(
            reversed(intelligence.inherited_prohibition_certifications)
        ),
        readiness_visibility=tuple(reversed(intelligence.readiness_visibility)),
        closeout_diagnostics=tuple(reversed(intelligence.closeout_diagnostics)),
        unsupported_readiness_visibility=tuple(
            reversed(intelligence.unsupported_readiness_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        inherited_limitations=tuple(reversed(intelligence.inherited_limitations)),
        inherited_blockers=tuple(reversed(intelligence.inherited_blockers)),
        inherited_warnings=tuple(reversed(intelligence.inherited_warnings)),
    )

    assert validate_closeout_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_8_readiness_closeout(
        intelligence
    ) == serialize_v4_5a_8_readiness_closeout(reordered)
    assert hash_v4_5a_8_readiness_closeout(
        intelligence
    ) == hash_v4_5a_8_readiness_closeout(reordered)


def test_v4_5a_8_closeout_certification_layers_are_stable():
    intelligence = build_v4_5a_8_readiness_closeout()

    assert validate_closeout_identity_integrity(intelligence)["valid"] is True
    assert validate_phase_coverage_certification_stability(intelligence)["valid"] is True
    assert validate_report_coverage_certification_stability(intelligence)["valid"] is True
    assert (
        validate_migration_documentation_certification_stability(intelligence)["valid"]
        is True
    )
    assert validate_continuity_certification_stability(intelligence)["valid"] is True
    assert validate_unsupported_state_preservation_stability(intelligence)["valid"] is True
    assert (
        validate_inherited_prohibition_preservation_stability(intelligence)["valid"]
        is True
    )
    assert validate_readiness_visibility_stability(intelligence)["valid"] is True


def test_v4_5a_8_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5a_8_readiness_closeout()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_closeout_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["evidence_continuity_preserved"] is True
    assert fail_visible["valid"] is True
    assert fail_visible["fail_visible"] is True
    assert fail_visible["silent_fallback_enabled_count"] == 0
    assert fail_visible["authorization_enabled_count"] == 0
    assert fail_visible["approval_enabled_count"] == 0
    assert fail_visible["ranking_enabled_count"] == 0
    assert fail_visible["recommendation_enabled_count"] == 0
    assert fail_visible["missing_diagnostic_types"] == []
    assert fail_visible["missing_unsupported_states"] == []


def test_v4_5a_8_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_8_readiness_closeout()

    assert len(closeout_summary_visibility(intelligence.closeout_records)) == 1
    assert len(readiness_summary_visibility(intelligence.readiness_certifications)) == 2
    assert len(phase_coverage_summary_visibility(intelligence.phase_coverage_certifications)) == 7
    assert len(report_coverage_summary_visibility(intelligence.report_coverage_certifications)) == 7
    assert len(migration_document_summary_visibility(intelligence.migration_document_certifications)) == 7
    assert len(continuity_certification_summary_visibility(intelligence.continuity_certifications)) == 7
    assert len(unsupported_state_summary_visibility(intelligence.unsupported_state_certifications)) == 6
    assert len(inherited_prohibition_summary_visibility(intelligence.inherited_prohibition_certifications)) == 5
    assert len(readiness_visibility_summary(intelligence.readiness_visibility)) == 6
    assert len(fail_visible_closeout_diagnostic_summaries(intelligence.closeout_diagnostics)) == 10
    assert len(unsupported_readiness_visibility_summaries(intelligence.unsupported_readiness_visibility)) == 23
    descriptive = descriptive_only_readiness_closeout_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["non_authorizing"] is True
    assert descriptive["non_approving"] is True
    assert descriptive["non_ranking"] is True
    assert descriptive["non_recommending"] is True
    assert descriptive["readiness_authorization_enabled"] is False
    assert descriptive["readiness_approval_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False
    assert descriptive["production_consumption_enabled"] is False


def test_v4_5a_8_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_8_readiness_closeout()
    contaminated = (
        contaminate_v4_5a_8_readiness_closeout_for_non_operational_validation(
            intelligence
        )
    )

    assert validate_descriptive_only_readiness_closeout_guarantees(
        intelligence
    )["valid"] is True
    contaminated_validation = validate_descriptive_only_readiness_closeout_guarantees(
        contaminated
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert (
        contaminated_validation["counters"][
            "enabled_orchestration_authorization_count"
        ]
        > 0
    )
    assert contaminated_validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert contaminated_validation["counters"]["enabled_readiness_authorization_count"] > 0
    assert contaminated_validation["counters"]["enabled_readiness_approval_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_ranking_count"] > 0
    assert contaminated_validation["counters"]["enabled_recommendation_count"] > 0
    assert enabled_readiness_closeout_capability_flags(contaminated) != {}


def test_v4_5a_8_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_8_readiness_closeout_report()
    second_report = build_v4_5a_8_readiness_closeout_report()
    validation = validate_v4_5a_8_readiness_closeout(
        build_v4_5a_8_readiness_closeout()
    )

    assert first_report == second_report
    assert first_report["foundation_status"] == V4_5A_8_READINESS_CLOSEOUT_STATUS_STABLE
    assert first_report["deterministic_report_hash"] == second_report[
        "deterministic_report_hash"
    ]
    assert len(first_report["deterministic_report_hash"]) == 64
    assert validation["valid"] is True
    assert first_report["summary"]["validation_error_count"] == 0
    assert first_report["summary"]["repository_remains"] == [
        "NON-operational",
        "NON-authorizing",
        "NON-approving",
        "NON-executing",
        "NON-remediating",
        "NON-runtime-mutating",
        "NON-ranking",
        "NON-recommending",
    ]
    assert first_report["summary"]["readiness_classifications"] == {
        "v4.5B public trust visibility readiness": (
            "v4_5b_public_trust_visibility_readiness_descriptive_only"
        ),
        "v4.6 governance aggregation readiness": (
            "v4_6_governance_aggregation_readiness_descriptive_only"
        ),
    }
