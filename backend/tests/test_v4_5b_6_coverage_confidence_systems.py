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

from public_trust_visibility.v4_5b_6_coverage_confidence_audit import (  # noqa: E402
    build_v4_5b_6_coverage_confidence,
    build_v4_5b_6_coverage_confidence_report,
    contaminate_v4_5b_6_coverage_confidence_for_non_operational_validation,
    coverage_confidence_capability_counter_values,
    coverage_confidence_equal,
    enabled_coverage_confidence_capability_flags,
    validate_confidence_visibility_stability,
    validate_coverage_confidence_identity_integrity,
    validate_coverage_confidence_ordering_stability,
    validate_coverage_confidence_serialization_and_hashing,
    validate_coverage_visibility_stability,
    validate_descriptive_only_coverage_confidence_guarantees,
    validate_evidence_coverage_stability,
    validate_explainability_coverage_stability,
    validate_fail_visible_coverage_diagnostics,
    validate_incomplete_unknown_coverage_visibility_preservation,
    validate_lineage_and_provenance_preservation,
    validate_provenance_lineage_coverage_stability,
    validate_support_coverage_stability,
    validate_v4_5b_6_coverage_confidence,
)
from public_trust_visibility.v4_5b_6_coverage_confidence_hashing import (  # noqa: E402
    hash_confidence_visibility_record,
    hash_coverage_confidence_identity,
    hash_coverage_diagnostic_record,
    hash_coverage_visibility_record,
    hash_evidence_coverage_record,
    hash_support_coverage_record,
    hash_v4_5b_6_coverage_confidence,
)
from public_trust_visibility.v4_5b_6_coverage_confidence_models import (  # noqa: E402
    CONFIDENCE_VISIBILITY_TYPES,
    COVERAGE_CONFIDENCE_NON_AUTHORITY_STATEMENT,
    COVERAGE_CONFIDENCE_STATEMENT,
)
from public_trust_visibility.v4_5b_6_coverage_confidence_models import (  # noqa: E402
    COVERAGE_CONFIDENCE_SUMMARY_TYPES,
    COVERAGE_DIAGNOSTIC_TYPES,
    COVERAGE_VISIBILITY_TYPES,
    EVIDENCE_COVERAGE_TYPES,
    EXPLAINABILITY_COVERAGE_TYPES,
    INCOMPLETE_UNKNOWN_COVERAGE_TYPES,
    PROVENANCE_LINEAGE_COVERAGE_TYPES,
    SUPPORT_COVERAGE_TYPES,
    UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES,
    V4_5B_6_COVERAGE_CONFIDENCE_SCHEMA_VERSION,
    V4_5B_6_COVERAGE_CONFIDENCE_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_6_coverage_confidence_serialization import (  # noqa: E402
    serialize_v4_5b_6_coverage_confidence,
)
from public_trust_visibility.v4_5b_6_coverage_confidence_visibility import (  # noqa: E402
    coverage_diagnostic_summary,
    coverage_visibility_summary,
    descriptive_only_coverage_confidence_summary,
    unsupported_operational_state_summary,
    validate_required_coverage_confidence_visibility,
)


def test_v4_5b_6_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_6_coverage_confidence()

    with pytest.raises(FrozenInstanceError):
        intelligence.trust_scoring_enabled = True

    assert intelligence.identity.schema_version == (
        V4_5B_6_COVERAGE_CONFIDENCE_SCHEMA_VERSION
    )
    assert intelligence.descriptive_only is True
    assert intelligence.publicly_transparent is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_approving is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.non_ranking is True
    assert intelligence.non_recommending is True
    assert intelligence.non_scoring is True
    assert intelligence.confidence_authorization_enabled is False
    assert intelligence.confidence_approval_enabled is False
    assert intelligence.coverage_ranking_enabled is False
    assert intelligence.confidence_recommendation_enabled is False
    assert intelligence.trust_scoring_enabled is False
    assert intelligence.evidence_scoring_enabled is False
    assert enabled_coverage_confidence_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in coverage_confidence_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5b_6_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_6_coverage_confidence()
    visibility = validate_required_coverage_confidence_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["coverage_counts"]) == set(COVERAGE_VISIBILITY_TYPES)
    assert set(visibility["support_counts"]) == set(SUPPORT_COVERAGE_TYPES)
    assert set(visibility["evidence_counts"]) == set(EVIDENCE_COVERAGE_TYPES)
    assert set(visibility["explainability_counts"]) == set(
        EXPLAINABILITY_COVERAGE_TYPES
    )
    assert set(visibility["provenance_lineage_counts"]) == set(
        PROVENANCE_LINEAGE_COVERAGE_TYPES
    )
    assert set(visibility["confidence_counts"]) == set(CONFIDENCE_VISIBILITY_TYPES)
    assert set(visibility["incomplete_unknown_counts"]) == set(
        INCOMPLETE_UNKNOWN_COVERAGE_TYPES
    )
    assert set(visibility["summary_counts"]) == set(
        COVERAGE_CONFIDENCE_SUMMARY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(COVERAGE_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_COVERAGE_CONFIDENCE_OPERATIONAL_STATES
    )
    assert visibility["missing_coverage_visibility"] == []
    assert visibility["missing_confidence_visibility"] == []
    assert visibility["missing_incomplete_unknown_coverage"] == []
    assert visibility["missing_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_6_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_6_coverage_confidence()
    second = build_v4_5b_6_coverage_confidence()
    serialization = validate_coverage_confidence_serialization_and_hashing(first)

    assert first == second
    assert coverage_confidence_equal(first, second)
    assert serialize_v4_5b_6_coverage_confidence(first) == (
        serialize_v4_5b_6_coverage_confidence(second)
    )
    assert hash_v4_5b_6_coverage_confidence(first) == (
        hash_v4_5b_6_coverage_confidence(second)
    )
    assert serialization["valid"] is True
    assert serialization["coverage_serialization_stable"] is True
    assert serialization["confidence_serialization_stable"] is True
    assert serialization["coverage_hashing_stable"] is True
    assert serialization["confidence_hashing_stable"] is True
    assert len(hash_coverage_confidence_identity(first.identity)) == 64
    assert len(hash_coverage_visibility_record(first.coverage_visibility_records[0])) == 64
    assert len(hash_support_coverage_record(first.support_coverage_records[0])) == 64
    assert len(hash_evidence_coverage_record(first.evidence_coverage_records[0])) == 64
    assert len(hash_confidence_visibility_record(first.confidence_visibility_records[0])) == 64
    assert len(hash_coverage_diagnostic_record(first.diagnostic_records[0])) == 64


def test_v4_5b_6_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_6_coverage_confidence()
    reordered = replace(
        intelligence,
        coverage_visibility_records=tuple(
            reversed(intelligence.coverage_visibility_records)
        ),
        support_coverage_records=tuple(reversed(intelligence.support_coverage_records)),
        evidence_coverage_records=tuple(reversed(intelligence.evidence_coverage_records)),
        explainability_coverage_records=tuple(
            reversed(intelligence.explainability_coverage_records)
        ),
        provenance_lineage_coverage_records=tuple(
            reversed(intelligence.provenance_lineage_coverage_records)
        ),
        confidence_visibility_records=tuple(
            reversed(intelligence.confidence_visibility_records)
        ),
        incomplete_unknown_coverage_records=tuple(
            reversed(intelligence.incomplete_unknown_coverage_records)
        ),
        summary_records=tuple(reversed(intelligence.summary_records)),
        diagnostic_records=tuple(reversed(intelligence.diagnostic_records)),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_coverage_confidence_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5b_6_coverage_confidence(
        intelligence
    ) == serialize_v4_5b_6_coverage_confidence(reordered)
    assert hash_v4_5b_6_coverage_confidence(intelligence) == (
        hash_v4_5b_6_coverage_confidence(reordered)
    )


def test_v4_5b_6_coverage_and_confidence_layers_are_stable():
    intelligence = build_v4_5b_6_coverage_confidence()

    assert validate_coverage_confidence_identity_integrity(intelligence)["valid"] is True
    assert validate_coverage_visibility_stability(intelligence)["valid"] is True
    assert validate_support_coverage_stability(intelligence)["valid"] is True
    assert validate_evidence_coverage_stability(intelligence)["valid"] is True
    assert validate_explainability_coverage_stability(intelligence)["valid"] is True
    assert validate_provenance_lineage_coverage_stability(intelligence)["valid"] is True
    assert validate_confidence_visibility_stability(intelligence)["valid"] is True
    assert (
        validate_incomplete_unknown_coverage_visibility_preservation(
            intelligence
        )["valid"]
        is True
    )


def test_v4_5b_6_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_6_coverage_confidence()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    diagnostics = validate_fail_visible_coverage_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["evidence_panel_continuity_preserved"] is True
    assert diagnostics["valid"] is True
    assert diagnostics["diagnostic_visibility"]["missing_types"] == []
    assert diagnostics["unsupported_operational_visibility"]["missing_types"] == []
    assert diagnostics["missing_explicit_reasons"] == []


def test_v4_5b_6_visibility_helpers_preserve_descriptive_only_boundaries():
    intelligence = build_v4_5b_6_coverage_confidence()
    coverage = coverage_visibility_summary(intelligence.coverage_visibility_records)
    diagnostics = coverage_diagnostic_summary(intelligence.diagnostic_records)
    unsupported = unsupported_operational_state_summary(
        intelligence.unsupported_operational_state_visibility
    )
    descriptive = descriptive_only_coverage_confidence_summary(intelligence)

    assert coverage[0]["authorization_enabled"] is False
    assert coverage[0]["scoring_enabled"] is False
    assert diagnostics[0]["silent_fallback_enabled"] is False
    assert diagnostics[0]["scoring_enabled"] is False
    assert unsupported[0]["suppression_enabled"] is False
    assert unsupported[0]["scoring_enabled"] is False
    assert descriptive["coverage_confidence_statement"] == COVERAGE_CONFIDENCE_STATEMENT
    assert descriptive["coverage_confidence_non_authority_statement"] == (
        COVERAGE_CONFIDENCE_NON_AUTHORITY_STATEMENT
    )
    assert descriptive["non_scoring"] is True


def test_v4_5b_6_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_6_coverage_confidence_for_non_operational_validation()
    )
    guarantees = validate_descriptive_only_coverage_confidence_guarantees(
        contaminated
    )
    counters = guarantees["counters"]

    assert guarantees["valid"] is False
    assert counters["enabled_runtime_execution_count"] > 0
    assert counters["enabled_confidence_authorization_count"] > 0
    assert counters["enabled_confidence_approval_count"] > 0
    assert counters["enabled_coverage_ranking_count"] > 0
    assert counters["enabled_confidence_recommendation_count"] > 0
    assert counters["enabled_scoring_count"] > 0
    assert counters["enabled_remediation_count"] > 0
    assert counters["enabled_planner_integration_count"] > 0


def test_v4_5b_6_report_is_replay_safe_and_certifies_boundaries():
    report = build_v4_5b_6_coverage_confidence_report()
    second_report = build_v4_5b_6_coverage_confidence_report()
    summary = report["summary"]
    validation = validate_v4_5b_6_coverage_confidence()

    assert report == second_report
    assert report["foundation_status"] == V4_5B_6_COVERAGE_CONFIDENCE_STATUS_STABLE
    assert report["deterministic_report_hash"] == (
        second_report["deterministic_report_hash"]
    )
    assert summary["deterministic_coverage_serialization_verified"] is True
    assert summary["deterministic_confidence_serialization_verified"] is True
    assert summary["deterministic_coverage_hashing_verified"] is True
    assert summary["deterministic_confidence_hashing_verified"] is True
    assert summary["coverage_visibility_stable"] is True
    assert summary["confidence_visibility_stable"] is True
    assert summary["fail_visible_coverage_diagnostics_verified"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["validation_error_count"] == 0
    assert "NON-scoring" in summary["repository_remains"]
    assert summary["coverage_confidence_statement"] == COVERAGE_CONFIDENCE_STATEMENT
    assert summary["coverage_confidence_non_authority_statement"] == (
        COVERAGE_CONFIDENCE_NON_AUTHORITY_STATEMENT
    )
    assert validation["valid"] is True
