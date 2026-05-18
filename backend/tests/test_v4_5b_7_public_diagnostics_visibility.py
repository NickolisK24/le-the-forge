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

from public_trust_visibility.v4_5b_7_public_diagnostics_audit import (  # noqa: E402
    build_v4_5b_7_public_diagnostics,
    build_v4_5b_7_public_diagnostics_report,
    contaminate_v4_5b_7_public_diagnostics_for_non_operational_validation,
    enabled_public_diagnostics_capability_flags,
    public_diagnostics_capability_counter_values,
    public_diagnostics_equal,
    validate_blocker_warning_visibility_preservation,
    validate_coverage_confidence_diagnostics_visibility_stability,
    validate_descriptive_only_public_diagnostics_guarantees,
    validate_diagnostics_summary_stability,
    validate_evidence_panel_diagnostics_visibility_stability,
    validate_explainability_diagnostics_visibility_stability,
    validate_fail_visible_public_diagnostics,
    validate_inherited_limitation_visibility_preservation,
    validate_lineage_and_provenance_preservation,
    validate_provenance_lineage_diagnostics_visibility_stability,
    validate_public_diagnostics_identity_integrity,
    validate_public_diagnostics_ordering_stability,
    validate_public_diagnostics_serialization_and_hashing,
    validate_public_diagnostics_visibility_stability,
    validate_support_diagnostics_visibility_stability,
    validate_v4_5b_7_public_diagnostics,
)
from public_trust_visibility.v4_5b_7_public_diagnostics_hashing import (  # noqa: E402
    hash_coverage_confidence_diagnostics_record,
    hash_evidence_panel_diagnostics_record,
    hash_fail_visible_public_diagnostic_record,
    hash_public_diagnostics_identity,
    hash_public_diagnostics_visibility_record,
    hash_support_diagnostics_record,
    hash_v4_5b_7_public_diagnostics,
)
from public_trust_visibility.v4_5b_7_public_diagnostics_models import (  # noqa: E402
    BLOCKER_WARNING_SUMMARY_TYPES,
    COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES,
    DIAGNOSTICS_SUMMARY_TYPES,
    DIAGNOSTICS_VISIBILITY_NON_AUTHORITY_STATEMENT,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EXPLAINABILITY_DIAGNOSTIC_TYPES,
    FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES,
    INHERITED_LIMITATION_VISIBILITY_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PUBLIC_DIAGNOSTICS_STATEMENT,
    PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES,
    V4_5B_7_PUBLIC_DIAGNOSTICS_SCHEMA_VERSION,
    V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_7_public_diagnostics_serialization import (  # noqa: E402
    serialize_v4_5b_7_public_diagnostics,
)
from public_trust_visibility.v4_5b_7_public_diagnostics_visibility import (  # noqa: E402
    descriptive_only_public_diagnostics_summary,
    fail_visible_public_diagnostics_summary,
    public_diagnostics_summary,
    unsupported_operational_state_summary,
    validate_required_public_diagnostics_visibility,
)


def test_v4_5b_7_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_7_public_diagnostics()

    with pytest.raises(FrozenInstanceError):
        intelligence.diagnostics_triage_enabled = True

    assert intelligence.identity.schema_version == (
        V4_5B_7_PUBLIC_DIAGNOSTICS_SCHEMA_VERSION
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
    assert intelligence.non_triaging is True
    assert intelligence.diagnostics_authorization_enabled is False
    assert intelligence.diagnostics_approval_enabled is False
    assert intelligence.diagnostics_ranking_enabled is False
    assert intelligence.diagnostics_recommendation_enabled is False
    assert intelligence.diagnostics_triage_enabled is False
    assert intelligence.scoring_enabled is False
    assert enabled_public_diagnostics_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in public_diagnostics_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5b_7_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_7_public_diagnostics()
    visibility = validate_required_public_diagnostics_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["public_counts"]) == set(PUBLIC_DIAGNOSTICS_VISIBILITY_TYPES)
    assert set(visibility["support_counts"]) == set(SUPPORT_DIAGNOSTIC_TYPES)
    assert set(visibility["explainability_counts"]) == set(
        EXPLAINABILITY_DIAGNOSTIC_TYPES
    )
    assert set(visibility["provenance_lineage_counts"]) == set(
        PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES
    )
    assert set(visibility["evidence_counts"]) == set(EVIDENCE_PANEL_DIAGNOSTIC_TYPES)
    assert set(visibility["coverage_confidence_counts"]) == set(
        COVERAGE_CONFIDENCE_DIAGNOSTIC_TYPES
    )
    assert set(visibility["inherited_counts"]) == set(
        INHERITED_LIMITATION_VISIBILITY_TYPES
    )
    assert set(visibility["blocker_warning_counts"]) == set(
        BLOCKER_WARNING_SUMMARY_TYPES
    )
    assert set(visibility["summary_counts"]) == set(DIAGNOSTICS_SUMMARY_TYPES)
    assert set(visibility["fail_visible_counts"]) == set(
        FAIL_VISIBLE_PUBLIC_DIAGNOSTIC_TYPES
    )
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_PUBLIC_DIAGNOSTICS_OPERATIONAL_STATES
    )
    assert visibility["missing_public_diagnostics"] == []
    assert visibility["missing_support_diagnostics"] == []
    assert visibility["missing_fail_visible_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_7_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_7_public_diagnostics()
    second = build_v4_5b_7_public_diagnostics()
    serialization = validate_public_diagnostics_serialization_and_hashing(first)

    assert first == second
    assert public_diagnostics_equal(first, second)
    assert serialize_v4_5b_7_public_diagnostics(first) == (
        serialize_v4_5b_7_public_diagnostics(second)
    )
    assert hash_v4_5b_7_public_diagnostics(first) == (
        hash_v4_5b_7_public_diagnostics(second)
    )
    assert serialization["valid"] is True
    assert serialization["serialization_stable"] is True
    assert serialization["hashing_stable"] is True
    assert len(hash_public_diagnostics_identity(first.identity)) == 64
    assert len(
        hash_public_diagnostics_visibility_record(first.public_diagnostics_records[0])
    ) == 64
    assert len(hash_support_diagnostics_record(first.support_diagnostics_records[0])) == 64
    assert len(
        hash_evidence_panel_diagnostics_record(
            first.evidence_panel_diagnostics_records[0]
        )
    ) == 64
    assert len(
        hash_coverage_confidence_diagnostics_record(
            first.coverage_confidence_diagnostics_records[0]
        )
    ) == 64
    assert len(
        hash_fail_visible_public_diagnostic_record(
            first.fail_visible_diagnostic_records[0]
        )
    ) == 64


def test_v4_5b_7_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_7_public_diagnostics()
    reordered = replace(
        intelligence,
        public_diagnostics_records=tuple(
            reversed(intelligence.public_diagnostics_records)
        ),
        support_diagnostics_records=tuple(
            reversed(intelligence.support_diagnostics_records)
        ),
        explainability_diagnostics_records=tuple(
            reversed(intelligence.explainability_diagnostics_records)
        ),
        provenance_lineage_diagnostics_records=tuple(
            reversed(intelligence.provenance_lineage_diagnostics_records)
        ),
        evidence_panel_diagnostics_records=tuple(
            reversed(intelligence.evidence_panel_diagnostics_records)
        ),
        coverage_confidence_diagnostics_records=tuple(
            reversed(intelligence.coverage_confidence_diagnostics_records)
        ),
        inherited_limitation_records=tuple(
            reversed(intelligence.inherited_limitation_records)
        ),
        blocker_warning_records=tuple(reversed(intelligence.blocker_warning_records)),
        summary_records=tuple(reversed(intelligence.summary_records)),
        fail_visible_diagnostic_records=tuple(
            reversed(intelligence.fail_visible_diagnostic_records)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_public_diagnostics_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5b_7_public_diagnostics(
        intelligence
    ) == serialize_v4_5b_7_public_diagnostics(reordered)
    assert hash_v4_5b_7_public_diagnostics(intelligence) == (
        hash_v4_5b_7_public_diagnostics(reordered)
    )


def test_v4_5b_7_public_diagnostics_layers_are_stable():
    intelligence = build_v4_5b_7_public_diagnostics()

    assert validate_public_diagnostics_identity_integrity(intelligence)["valid"] is True
    assert validate_public_diagnostics_visibility_stability(intelligence)["valid"] is True
    assert validate_support_diagnostics_visibility_stability(intelligence)["valid"] is True
    assert (
        validate_explainability_diagnostics_visibility_stability(intelligence)["valid"]
        is True
    )
    assert (
        validate_provenance_lineage_diagnostics_visibility_stability(intelligence)[
            "valid"
        ]
        is True
    )
    assert (
        validate_evidence_panel_diagnostics_visibility_stability(intelligence)["valid"]
        is True
    )
    assert (
        validate_coverage_confidence_diagnostics_visibility_stability(intelligence)[
            "valid"
        ]
        is True
    )
    assert (
        validate_inherited_limitation_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert validate_blocker_warning_visibility_preservation(intelligence)["valid"] is True
    assert validate_diagnostics_summary_stability(intelligence)["valid"] is True


def test_v4_5b_7_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_7_public_diagnostics()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    diagnostics = validate_fail_visible_public_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["diagnostics_reference_continuity_preserved"] is True
    assert diagnostics["valid"] is True
    assert diagnostics["diagnostic_visibility"]["missing_types"] == []
    assert diagnostics["unsupported_operational_visibility"]["missing_types"] == []
    assert diagnostics["missing_explicit_reasons"] == []


def test_v4_5b_7_visibility_helpers_preserve_descriptive_only_boundaries():
    intelligence = build_v4_5b_7_public_diagnostics()
    public = public_diagnostics_summary(intelligence.public_diagnostics_records)
    diagnostics = fail_visible_public_diagnostics_summary(
        intelligence.fail_visible_diagnostic_records
    )
    unsupported = unsupported_operational_state_summary(
        intelligence.unsupported_operational_state_visibility
    )
    descriptive = descriptive_only_public_diagnostics_summary(intelligence)

    assert public[0]["authorization_enabled"] is False
    assert public[0]["triage_enabled"] is False
    assert diagnostics[0]["silent_fallback_enabled"] is False
    assert diagnostics[0]["triage_enabled"] is False
    assert unsupported[0]["suppression_enabled"] is False
    assert unsupported[0]["scoring_enabled"] is False
    assert descriptive["public_diagnostics_statement"] == PUBLIC_DIAGNOSTICS_STATEMENT
    assert descriptive["diagnostics_visibility_non_authority_statement"] == (
        DIAGNOSTICS_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert descriptive["non_scoring"] is True
    assert descriptive["non_triaging"] is True


def test_v4_5b_7_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_7_public_diagnostics_for_non_operational_validation()
    )
    guarantees = validate_descriptive_only_public_diagnostics_guarantees(contaminated)
    counters = guarantees["counters"]

    assert guarantees["valid"] is False
    assert counters["enabled_runtime_execution_count"] > 0
    assert counters["enabled_diagnostics_authorization_count"] > 0
    assert counters["enabled_diagnostics_approval_count"] > 0
    assert counters["enabled_diagnostics_ranking_count"] > 0
    assert counters["enabled_diagnostics_recommendation_count"] > 0
    assert counters["enabled_triage_count"] > 0
    assert counters["enabled_scoring_count"] > 0
    assert counters["enabled_remediation_count"] > 0
    assert counters["enabled_planner_integration_count"] > 0


def test_v4_5b_7_report_is_replay_safe_and_certifies_boundaries():
    report = build_v4_5b_7_public_diagnostics_report()
    second_report = build_v4_5b_7_public_diagnostics_report()
    summary = report["summary"]
    validation = validate_v4_5b_7_public_diagnostics()

    assert report == second_report
    assert report["foundation_status"] == V4_5B_7_PUBLIC_DIAGNOSTICS_STATUS_STABLE
    assert report["deterministic_report_hash"] == (
        second_report["deterministic_report_hash"]
    )
    assert summary["deterministic_diagnostics_serialization_verified"] is True
    assert summary["deterministic_diagnostics_hashing_verified"] is True
    assert summary["diagnostics_visibility_stable"] is True
    assert summary["support_diagnostics_stable"] is True
    assert summary["evidence_diagnostics_stable"] is True
    assert summary["coverage_confidence_diagnostics_stable"] is True
    assert summary["blocker_warning_visibility_preserved"] is True
    assert summary["fail_visible_diagnostics_preserved"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["validation_error_count"] == 0
    assert "NON-scoring" in summary["repository_remains"]
    assert "NON-triaging" in summary["repository_remains"]
    assert summary["public_diagnostics_statement"] == PUBLIC_DIAGNOSTICS_STATEMENT
    assert summary["diagnostics_visibility_non_authority_statement"] == (
        DIAGNOSTICS_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert validation["valid"] is True
