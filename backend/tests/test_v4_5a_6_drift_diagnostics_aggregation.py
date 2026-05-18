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

from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_audit import (  # noqa: E402
    build_v4_5a_6_drift_diagnostics_aggregation,
    build_v4_5a_6_drift_diagnostics_aggregation_report,
    contaminate_v4_5a_6_drift_diagnostics_aggregation_for_non_operational_validation,
    drift_diagnostics_aggregation_capability_counter_values,
    drift_diagnostics_aggregation_equal,
    enabled_drift_diagnostics_aggregation_capability_flags,
    validate_blocker_warning_summary_determinism,
    validate_continuity_gap_visibility_preservation,
    validate_descriptive_only_diagnostics_aggregation_guarantees,
    validate_diagnostic_source_aggregation_stability,
    validate_diagnostics_aggregation_identity_integrity,
    validate_diagnostics_aggregation_ordering_stability,
    validate_diagnostics_aggregation_serialization_and_hashing,
    validate_evidence_gap_visibility_preservation,
    validate_fail_visible_aggregation_diagnostics,
    validate_lineage_and_provenance_preservation,
    validate_severity_summary_determinism,
    validate_unsupported_state_summary_visibility,
    validate_v4_5a_6_drift_diagnostics_aggregation,
)
from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_hashing import (  # noqa: E402
    hash_aggregated_diagnostic_record,
    hash_diagnostic_aggregation_record,
    hash_diagnostic_source_aggregation,
    hash_drift_diagnostics_aggregation_identity,
    hash_evidence_gap_summary_visibility,
    hash_v4_5a_6_drift_diagnostics_aggregation,
)
from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_models import (  # noqa: E402
    AGGREGATED_DIAGNOSTIC_TYPES,
    BLOCKER_WARNING_SUMMARY_TYPES,
    CONTINUITY_GAP_SUMMARY_TYPES,
    DIAGNOSTIC_SEVERITY_SUMMARY_TYPES,
    DIAGNOSTIC_SOURCE_TYPES,
    EVIDENCE_GAP_SUMMARY_TYPES,
    UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_SUMMARY_TYPES,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_SCHEMA_VERSION,
    V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_STABLE,
)
from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_serialization import (  # noqa: E402
    serialize_v4_5a_6_drift_diagnostics_aggregation,
)
from orchestration_governance.v4_5a_6_drift_diagnostics_aggregation_visibility import (  # noqa: E402
    aggregation_summary_visibility,
    blocker_warning_summary_visibility,
    continuity_gap_summary_visibility,
    descriptive_only_diagnostics_aggregation_summary,
    diagnostic_source_summary_visibility,
    evidence_gap_summary_visibility,
    fail_visible_aggregated_diagnostic_summaries,
    severity_summary_visibility,
    unsupported_aggregation_visibility_summaries,
    unsupported_state_summary_visibility,
    validate_required_diagnostics_aggregation_visibility,
)


def test_v4_5a_6_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()

    with pytest.raises(FrozenInstanceError):
        intelligence.ranking_enabled = True

    assert (
        intelligence.aggregation_identity.schema_version
        == V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_SCHEMA_VERSION
    )
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.non_ranking is True
    assert intelligence.non_recommending is True
    assert intelligence.non_triaging is True
    assert intelligence.automated_prioritization_enabled is False
    assert intelligence.automated_triage_enabled is False
    assert intelligence.ranking_enabled is False
    assert intelligence.recommendation_enabled is False
    assert enabled_drift_diagnostics_aggregation_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in drift_diagnostics_aggregation_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5a_6_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()
    visibility = validate_required_diagnostics_aggregation_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["source_counts"]) == set(DIAGNOSTIC_SOURCE_TYPES)
    assert set(visibility["unsupported_summary_counts"]) == set(
        UNSUPPORTED_STATE_SUMMARY_TYPES
    )
    assert set(visibility["evidence_gap_counts"]) == set(EVIDENCE_GAP_SUMMARY_TYPES)
    assert set(visibility["continuity_gap_counts"]) == set(
        CONTINUITY_GAP_SUMMARY_TYPES
    )
    assert set(visibility["severity_counts"]) == set(
        DIAGNOSTIC_SEVERITY_SUMMARY_TYPES
    )
    assert set(visibility["blocker_warning_counts"]) == set(
        BLOCKER_WARNING_SUMMARY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(AGGREGATED_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_AGGREGATION_OPERATIONAL_STATES
    )
    assert visibility["missing_source_types"] == []
    assert visibility["missing_unsupported_summary_types"] == []
    assert visibility["missing_evidence_gap_types"] == []
    assert visibility["missing_continuity_gap_types"] == []
    assert visibility["missing_severity_types"] == []
    assert visibility["missing_blocker_warning_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5a_6_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_6_drift_diagnostics_aggregation()
    second = build_v4_5a_6_drift_diagnostics_aggregation()
    serialization = validate_diagnostics_aggregation_serialization_and_hashing(first)

    assert first == second
    assert drift_diagnostics_aggregation_equal(first, second)
    assert serialize_v4_5a_6_drift_diagnostics_aggregation(first) == (
        serialize_v4_5a_6_drift_diagnostics_aggregation(second)
    )
    assert hash_v4_5a_6_drift_diagnostics_aggregation(first) == (
        hash_v4_5a_6_drift_diagnostics_aggregation(second)
    )
    assert serialization["valid"] is True
    assert len(hash_drift_diagnostics_aggregation_identity(first.aggregation_identity)) == 64
    assert len(hash_diagnostic_aggregation_record(first.diagnostic_aggregation_records[0])) == 64
    assert len(hash_diagnostic_source_aggregation(first.diagnostic_source_aggregation[0])) == 64
    assert len(hash_evidence_gap_summary_visibility(first.evidence_gap_summaries[0])) == 64
    assert len(hash_aggregated_diagnostic_record(first.aggregated_diagnostics[0])) == 64


def test_v4_5a_6_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()
    reordered = replace(
        intelligence,
        diagnostic_aggregation_records=tuple(
            reversed(intelligence.diagnostic_aggregation_records)
        ),
        diagnostic_source_aggregation=tuple(
            reversed(intelligence.diagnostic_source_aggregation)
        ),
        unsupported_state_summaries=tuple(
            reversed(intelligence.unsupported_state_summaries)
        ),
        evidence_gap_summaries=tuple(reversed(intelligence.evidence_gap_summaries)),
        continuity_gap_summaries=tuple(
            reversed(intelligence.continuity_gap_summaries)
        ),
        severity_summaries=tuple(reversed(intelligence.severity_summaries)),
        blocker_warning_summaries=tuple(
            reversed(intelligence.blocker_warning_summaries)
        ),
        aggregated_diagnostics=tuple(reversed(intelligence.aggregated_diagnostics)),
        unsupported_aggregation_visibility=tuple(
            reversed(intelligence.unsupported_aggregation_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_diagnostics_aggregation_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_6_drift_diagnostics_aggregation(
        intelligence
    ) == serialize_v4_5a_6_drift_diagnostics_aggregation(reordered)
    assert hash_v4_5a_6_drift_diagnostics_aggregation(
        intelligence
    ) == hash_v4_5a_6_drift_diagnostics_aggregation(reordered)


def test_v4_5a_6_source_gap_severity_and_blocker_visibility_are_preserved():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()

    assert validate_diagnostics_aggregation_identity_integrity(intelligence)["valid"] is True
    assert validate_diagnostic_source_aggregation_stability(intelligence)["valid"] is True
    assert validate_unsupported_state_summary_visibility(intelligence)["valid"] is True
    assert validate_evidence_gap_visibility_preservation(intelligence)["valid"] is True
    assert validate_continuity_gap_visibility_preservation(intelligence)["valid"] is True
    assert validate_severity_summary_determinism(intelligence)["valid"] is True
    assert validate_blocker_warning_summary_determinism(intelligence)["valid"] is True


def test_v4_5a_6_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_aggregation_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert fail_visible["valid"] is True
    assert fail_visible["fail_visible"] is True
    assert fail_visible["silent_fallback_enabled_count"] == 0
    assert fail_visible["ranking_enabled_count"] == 0
    assert fail_visible["recommendation_enabled_count"] == 0
    assert fail_visible["automated_triage_enabled_count"] == 0
    assert fail_visible["missing_diagnostic_types"] == []
    assert fail_visible["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_aggregated_diagnostic_summaries(
            intelligence.aggregated_diagnostics
        )
    )
    assert all(
        summary["ranking_enabled"] is False
        for summary in unsupported_aggregation_visibility_summaries(
            intelligence.unsupported_aggregation_visibility
        )
    )


def test_v4_5a_6_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()

    assert len(aggregation_summary_visibility(intelligence.diagnostic_aggregation_records)) == 8
    assert len(diagnostic_source_summary_visibility(intelligence.diagnostic_source_aggregation)) == 8
    assert len(unsupported_state_summary_visibility(intelligence.unsupported_state_summaries)) == 8
    assert len(evidence_gap_summary_visibility(intelligence.evidence_gap_summaries)) == 9
    assert len(continuity_gap_summary_visibility(intelligence.continuity_gap_summaries)) == 8
    assert len(severity_summary_visibility(intelligence.severity_summaries)) == 5
    assert len(blocker_warning_summary_visibility(intelligence.blocker_warning_summaries)) == 10
    descriptive = descriptive_only_diagnostics_aggregation_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["non_ranking"] is True
    assert descriptive["non_recommending"] is True
    assert descriptive["non_triaging"] is True
    assert descriptive["automated_prioritization_enabled"] is False
    assert descriptive["automated_triage_enabled"] is False
    assert descriptive["ranking_enabled"] is False
    assert descriptive["recommendation_enabled"] is False
    assert descriptive["remediation_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_6_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_6_drift_diagnostics_aggregation()
    contaminated = (
        contaminate_v4_5a_6_drift_diagnostics_aggregation_for_non_operational_validation(
            intelligence
        )
    )

    assert validate_descriptive_only_diagnostics_aggregation_guarantees(
        intelligence
    )["valid"] is True
    contaminated_validation = validate_descriptive_only_diagnostics_aggregation_guarantees(
        contaminated
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_automated_prioritization_count"] > 0
    assert contaminated_validation["counters"]["enabled_automated_triage_count"] > 0
    assert contaminated_validation["counters"]["enabled_ranking_count"] > 0
    assert contaminated_validation["counters"]["enabled_recommendation_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert enabled_drift_diagnostics_aggregation_capability_flags(contaminated) != {}


def test_v4_5a_6_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_6_drift_diagnostics_aggregation_report()
    second_report = build_v4_5a_6_drift_diagnostics_aggregation_report()
    validation = validate_v4_5a_6_drift_diagnostics_aggregation(
        build_v4_5a_6_drift_diagnostics_aggregation()
    )

    assert first_report == second_report
    assert (
        first_report["foundation_status"]
        == V4_5A_6_DRIFT_DIAGNOSTICS_AGGREGATION_STATUS_STABLE
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
        "NON-executing",
        "NON-remediating",
        "NON-runtime-mutating",
        "NON-ranking",
        "NON-recommending",
    ]
