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

from orchestration_governance.v4_5a_7_integrity_certification_audit import (  # noqa: E402
    build_v4_5a_7_integrity_certification,
    build_v4_5a_7_integrity_certification_report,
    contaminate_v4_5a_7_integrity_certification_for_non_operational_validation,
    enabled_integrity_certification_capability_flags,
    integrity_certification_capability_counter_values,
    integrity_certification_equal,
    validate_certification_coverage_stability,
    validate_certification_identity_integrity,
    validate_certification_ordering_stability,
    validate_continuity_certification_stability,
    validate_descriptive_only_integrity_certification_guarantees,
    validate_diagnostics_certification_stability,
    validate_fail_visible_certification_diagnostics,
    validate_hashing_serialization_certification_stability,
    validate_inherited_prohibition_preservation_visibility,
    validate_integrity_certification_serialization_and_hashing,
    validate_lineage_and_provenance_preservation,
    validate_unsupported_state_preservation_visibility,
    validate_v4_5a_7_integrity_certification,
)
from orchestration_governance.v4_5a_7_integrity_certification_hashing import (  # noqa: E402
    hash_certification_diagnostic_record,
    hash_continuity_integrity_certification,
    hash_coverage_certification_visibility,
    hash_integrity_certification_identity,
    hash_integrity_certification_record,
    hash_v4_5a_7_integrity_certification,
)
from orchestration_governance.v4_5a_7_integrity_certification_models import (  # noqa: E402
    CERTIFICATION_DIAGNOSTIC_TYPES,
    CONTINUITY_INTEGRITY_CERTIFICATION_TYPES,
    COVERAGE_CERTIFICATION_TYPES,
    DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES,
    HASH_SERIALIZATION_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    V4_5A_7_INTEGRITY_CERTIFICATION_SCHEMA_VERSION,
    V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_STABLE,
)
from orchestration_governance.v4_5a_7_integrity_certification_serialization import (  # noqa: E402
    serialize_v4_5a_7_integrity_certification,
)
from orchestration_governance.v4_5a_7_integrity_certification_visibility import (  # noqa: E402
    certification_summary_visibility,
    continuity_certification_summary_visibility,
    coverage_certification_summary_visibility,
    descriptive_only_integrity_certification_summary,
    diagnostics_certification_summary_visibility,
    fail_visible_certification_diagnostic_summaries,
    hashing_serialization_certification_summary_visibility,
    inherited_prohibition_certification_summary_visibility,
    unsupported_certification_visibility_summaries,
    unsupported_state_certification_summary_visibility,
    validate_required_integrity_certification_visibility,
)


def test_v4_5a_7_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_7_integrity_certification()

    with pytest.raises(FrozenInstanceError):
        intelligence.authorization_semantics_enabled = True

    assert (
        intelligence.certification_identity.schema_version
        == V4_5A_7_INTEGRITY_CERTIFICATION_SCHEMA_VERSION
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
    assert intelligence.authorization_semantics_enabled is False
    assert intelligence.approval_semantics_enabled is False
    assert intelligence.ranking_enabled is False
    assert intelligence.recommendation_enabled is False
    assert enabled_integrity_certification_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in integrity_certification_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5a_7_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_7_integrity_certification()
    visibility = validate_required_integrity_certification_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["coverage_counts"]) == set(COVERAGE_CERTIFICATION_TYPES)
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_STATE_PRESERVATION_TYPES
    )
    assert set(visibility["prohibition_counts"]) == set(
        INHERITED_PROHIBITION_CERTIFICATION_TYPES
    )
    assert set(visibility["hash_serialization_counts"]) == set(
        HASH_SERIALIZATION_CERTIFICATION_TYPES
    )
    assert set(visibility["continuity_counts"]) == set(
        CONTINUITY_INTEGRITY_CERTIFICATION_TYPES
    )
    assert set(visibility["diagnostics_counts"]) == set(
        DIAGNOSTICS_INTEGRITY_CERTIFICATION_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(CERTIFICATION_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_CERTIFICATION_OPERATIONAL_STATES
    )
    assert visibility["missing_coverage_types"] == []
    assert visibility["missing_unsupported_types"] == []
    assert visibility["missing_prohibition_types"] == []
    assert visibility["missing_hash_serialization_types"] == []
    assert visibility["missing_continuity_types"] == []
    assert visibility["missing_diagnostics_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_7_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_7_integrity_certification()
    second = build_v4_5a_7_integrity_certification()
    serialization = validate_integrity_certification_serialization_and_hashing(first)

    assert first == second
    assert integrity_certification_equal(first, second)
    assert serialize_v4_5a_7_integrity_certification(first) == (
        serialize_v4_5a_7_integrity_certification(second)
    )
    assert hash_v4_5a_7_integrity_certification(first) == (
        hash_v4_5a_7_integrity_certification(second)
    )
    assert serialization["valid"] is True
    assert len(hash_integrity_certification_identity(first.certification_identity)) == 64
    assert len(hash_integrity_certification_record(first.certification_records[0])) == 64
    assert len(hash_coverage_certification_visibility(first.coverage_certifications[0])) == 64
    assert len(hash_continuity_integrity_certification(first.continuity_certifications[0])) == 64
    assert len(hash_certification_diagnostic_record(first.certification_diagnostics[0])) == 64


def test_v4_5a_7_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_7_integrity_certification()
    reordered = replace(
        intelligence,
        certification_records=tuple(reversed(intelligence.certification_records)),
        coverage_certifications=tuple(reversed(intelligence.coverage_certifications)),
        unsupported_state_certifications=tuple(
            reversed(intelligence.unsupported_state_certifications)
        ),
        inherited_prohibition_certifications=tuple(
            reversed(intelligence.inherited_prohibition_certifications)
        ),
        hashing_serialization_certifications=tuple(
            reversed(intelligence.hashing_serialization_certifications)
        ),
        continuity_certifications=tuple(
            reversed(intelligence.continuity_certifications)
        ),
        diagnostics_certifications=tuple(
            reversed(intelligence.diagnostics_certifications)
        ),
        certification_diagnostics=tuple(
            reversed(intelligence.certification_diagnostics)
        ),
        unsupported_certification_visibility=tuple(
            reversed(intelligence.unsupported_certification_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_certification_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_7_integrity_certification(
        intelligence
    ) == serialize_v4_5a_7_integrity_certification(reordered)
    assert hash_v4_5a_7_integrity_certification(
        intelligence
    ) == hash_v4_5a_7_integrity_certification(reordered)


def test_v4_5a_7_certification_stability_layers_are_preserved():
    intelligence = build_v4_5a_7_integrity_certification()

    assert validate_certification_identity_integrity(intelligence)["valid"] is True
    assert validate_certification_coverage_stability(intelligence)["valid"] is True
    assert (
        validate_unsupported_state_preservation_visibility(intelligence)["valid"]
        is True
    )
    assert (
        validate_inherited_prohibition_preservation_visibility(intelligence)["valid"]
        is True
    )
    assert (
        validate_hashing_serialization_certification_stability(intelligence)["valid"]
        is True
    )
    assert validate_continuity_certification_stability(intelligence)["valid"] is True
    assert validate_diagnostics_certification_stability(intelligence)["valid"] is True


def test_v4_5a_7_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5a_7_integrity_certification()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_certification_diagnostics(intelligence)

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
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_certification_diagnostic_summaries(
            intelligence.certification_diagnostics
        )
    )
    assert all(
        summary["authorization_enabled"] is False
        for summary in unsupported_certification_visibility_summaries(
            intelligence.unsupported_certification_visibility
        )
    )


def test_v4_5a_7_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_7_integrity_certification()

    assert len(certification_summary_visibility(intelligence.certification_records)) == 1
    assert len(coverage_certification_summary_visibility(intelligence.coverage_certifications)) == 9
    assert len(unsupported_state_certification_summary_visibility(intelligence.unsupported_state_certifications)) == 6
    assert len(inherited_prohibition_certification_summary_visibility(intelligence.inherited_prohibition_certifications)) == 6
    assert len(hashing_serialization_certification_summary_visibility(intelligence.hashing_serialization_certifications)) == 6
    assert len(continuity_certification_summary_visibility(intelligence.continuity_certifications)) == 6
    assert len(diagnostics_certification_summary_visibility(intelligence.diagnostics_certifications)) == 6
    assert len(fail_visible_certification_diagnostic_summaries(intelligence.certification_diagnostics)) == 9
    assert len(unsupported_certification_visibility_summaries(intelligence.unsupported_certification_visibility)) == 26
    descriptive = descriptive_only_integrity_certification_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["non_authorizing"] is True
    assert descriptive["non_approving"] is True
    assert descriptive["non_ranking"] is True
    assert descriptive["non_recommending"] is True
    assert descriptive["authorization_semantics_enabled"] is False
    assert descriptive["approval_semantics_enabled"] is False
    assert descriptive["ranking_enabled"] is False
    assert descriptive["recommendation_enabled"] is False
    assert descriptive["remediation_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_7_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_7_integrity_certification()
    contaminated = (
        contaminate_v4_5a_7_integrity_certification_for_non_operational_validation(
            intelligence
        )
    )

    assert validate_descriptive_only_integrity_certification_guarantees(
        intelligence
    )["valid"] is True
    contaminated_validation = (
        validate_descriptive_only_integrity_certification_guarantees(contaminated)
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert (
        contaminated_validation["counters"][
            "enabled_orchestration_authorization_count"
        ]
        > 0
    )
    assert (
        contaminated_validation["counters"]["enabled_orchestration_approval_count"] > 0
    )
    assert (
        contaminated_validation["counters"]["enabled_authorization_semantics_count"] > 0
    )
    assert contaminated_validation["counters"]["enabled_approval_semantics_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_ranking_count"] > 0
    assert contaminated_validation["counters"]["enabled_recommendation_count"] > 0
    assert enabled_integrity_certification_capability_flags(contaminated) != {}


def test_v4_5a_7_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_7_integrity_certification_report()
    second_report = build_v4_5a_7_integrity_certification_report()
    validation = validate_v4_5a_7_integrity_certification(
        build_v4_5a_7_integrity_certification()
    )

    assert first_report == second_report
    assert (
        first_report["foundation_status"]
        == V4_5A_7_INTEGRITY_CERTIFICATION_STATUS_STABLE
    )
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
