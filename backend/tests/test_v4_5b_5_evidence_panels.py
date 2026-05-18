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

from public_trust_visibility.v4_5b_5_evidence_panel_audit import (  # noqa: E402
    build_v4_5b_5_evidence_panels,
    build_v4_5b_5_evidence_panels_report,
    contaminate_v4_5b_5_evidence_panels_for_non_operational_validation,
    enabled_evidence_panel_capability_flags,
    evidence_panel_capability_counter_values,
    evidence_panels_equal,
    validate_descriptive_only_evidence_panel_guarantees,
    validate_evidence_freshness_visibility_preservation,
    validate_evidence_grouping_stability,
    validate_evidence_item_stability,
    validate_evidence_panel_identity_integrity,
    validate_evidence_panel_ordering_stability,
    validate_evidence_panel_serialization_and_hashing,
    validate_evidence_panel_summary_stability,
    validate_evidence_source_visibility_stability,
    validate_explainability_evidence_panel_stability,
    validate_fail_visible_evidence_panel_diagnostics,
    validate_lineage_and_provenance_preservation,
    validate_provenance_lineage_evidence_panel_stability,
    validate_support_status_evidence_panel_stability,
    validate_unsupported_missing_evidence_visibility_preservation,
    validate_v4_5b_5_evidence_panels,
)
from public_trust_visibility.v4_5b_5_evidence_panel_hashing import (  # noqa: E402
    hash_evidence_freshness_visibility,
    hash_evidence_group_record,
    hash_evidence_item_record,
    hash_evidence_panel_diagnostic_record,
    hash_evidence_panel_identity,
    hash_evidence_panel_record,
    hash_evidence_panel_summary_record,
    hash_evidence_source_visibility,
    hash_v4_5b_5_evidence_panels,
)
from public_trust_visibility.v4_5b_5_evidence_panel_models import (  # noqa: E402
    EVIDENCE_FRESHNESS_VISIBILITY_TYPES,
    EVIDENCE_GROUPING_TYPES,
    EVIDENCE_PANEL_DIAGNOSTIC_TYPES,
    EVIDENCE_PANEL_STATEMENT,
    EVIDENCE_PANEL_SUMMARY_TYPES,
    EVIDENCE_SOURCE_VISIBILITY_TYPES,
    EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT,
    EXPLAINABILITY_EVIDENCE_PANEL_TYPES,
    PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES,
    SUPPORT_STATUS_EVIDENCE_PANEL_TYPES,
    UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES,
    UNSUPPORTED_MISSING_EVIDENCE_TYPES,
    V4_5B_5_EVIDENCE_PANEL_SCHEMA_VERSION,
    V4_5B_5_EVIDENCE_PANEL_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_5_evidence_panel_serialization import (  # noqa: E402
    serialize_v4_5b_5_evidence_panels,
)
from public_trust_visibility.v4_5b_5_evidence_panel_visibility import (  # noqa: E402
    descriptive_only_evidence_panel_summary,
    evidence_panel_diagnostic_summary,
    evidence_panel_summary,
    unsupported_operational_state_summary,
    validate_required_evidence_panel_visibility,
)


def test_v4_5b_5_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_5_evidence_panels()

    with pytest.raises(FrozenInstanceError):
        intelligence.evidence_scoring_enabled = True

    assert intelligence.evidence_identity.schema_version == (
        V4_5B_5_EVIDENCE_PANEL_SCHEMA_VERSION
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
    assert intelligence.evidence_authorization_enabled is False
    assert intelligence.evidence_approval_enabled is False
    assert intelligence.evidence_ranking_enabled is False
    assert intelligence.evidence_recommendation_enabled is False
    assert intelligence.evidence_scoring_enabled is False
    assert intelligence.trust_scoring_enabled is False
    assert enabled_evidence_panel_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in evidence_panel_capability_counter_values(intelligence).values()
    )


def test_v4_5b_5_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_5_evidence_panels()
    visibility = validate_required_evidence_panel_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["grouping_counts"]) == set(EVIDENCE_GROUPING_TYPES)
    assert set(visibility["source_counts"]) == set(EVIDENCE_SOURCE_VISIBILITY_TYPES)
    assert set(visibility["freshness_counts"]) == set(
        EVIDENCE_FRESHNESS_VISIBILITY_TYPES
    )
    assert set(visibility["support_counts"]) == set(
        SUPPORT_STATUS_EVIDENCE_PANEL_TYPES
    )
    assert set(visibility["explainability_counts"]) == set(
        EXPLAINABILITY_EVIDENCE_PANEL_TYPES
    )
    assert set(visibility["provenance_lineage_counts"]) == set(
        PROVENANCE_LINEAGE_EVIDENCE_PANEL_TYPES
    )
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_MISSING_EVIDENCE_TYPES
    )
    assert set(visibility["summary_counts"]) == set(EVIDENCE_PANEL_SUMMARY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(EVIDENCE_PANEL_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_EVIDENCE_PANEL_OPERATIONAL_STATES
    )
    assert visibility["missing_groupings"] == []
    assert visibility["missing_sources"] == []
    assert visibility["missing_freshness"] == []
    assert visibility["missing_support_panels"] == []
    assert visibility["missing_explainability_panels"] == []
    assert visibility["missing_provenance_lineage_panels"] == []
    assert visibility["missing_unsupported_missing_evidence"] == []
    assert visibility["missing_summaries"] == []
    assert visibility["missing_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_5_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_5_evidence_panels()
    second = build_v4_5b_5_evidence_panels()
    serialization = validate_evidence_panel_serialization_and_hashing(first)

    assert first == second
    assert evidence_panels_equal(first, second)
    assert serialize_v4_5b_5_evidence_panels(first) == (
        serialize_v4_5b_5_evidence_panels(second)
    )
    assert hash_v4_5b_5_evidence_panels(first) == (
        hash_v4_5b_5_evidence_panels(second)
    )
    assert serialization["valid"] is True
    assert serialization["serialization_stable"] is True
    assert serialization["hashing_stable"] is True
    assert len(hash_evidence_panel_identity(first.evidence_identity)) == 64
    assert len(hash_evidence_panel_record(first.evidence_panel_records[0])) == 64
    assert len(hash_evidence_group_record(first.evidence_group_records[0])) == 64
    assert len(hash_evidence_item_record(first.evidence_item_records[0])) == 64
    assert len(hash_evidence_source_visibility(first.evidence_source_visibility[0])) == 64
    assert len(
        hash_evidence_freshness_visibility(first.evidence_freshness_visibility[0])
    ) == 64
    assert len(hash_evidence_panel_summary_record(first.evidence_panel_summaries[0])) == 64
    assert len(
        hash_evidence_panel_diagnostic_record(first.evidence_panel_diagnostics[0])
    ) == 64


def test_v4_5b_5_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_5_evidence_panels()
    reordered = replace(
        intelligence,
        evidence_panel_records=tuple(reversed(intelligence.evidence_panel_records)),
        evidence_group_records=tuple(reversed(intelligence.evidence_group_records)),
        evidence_item_records=tuple(reversed(intelligence.evidence_item_records)),
        evidence_source_visibility=tuple(
            reversed(intelligence.evidence_source_visibility)
        ),
        evidence_freshness_visibility=tuple(
            reversed(intelligence.evidence_freshness_visibility)
        ),
        support_status_evidence_panels=tuple(
            reversed(intelligence.support_status_evidence_panels)
        ),
        explainability_evidence_panels=tuple(
            reversed(intelligence.explainability_evidence_panels)
        ),
        provenance_lineage_evidence_panels=tuple(
            reversed(intelligence.provenance_lineage_evidence_panels)
        ),
        unsupported_missing_evidence_visibility=tuple(
            reversed(intelligence.unsupported_missing_evidence_visibility)
        ),
        evidence_panel_summaries=tuple(
            reversed(intelligence.evidence_panel_summaries)
        ),
        evidence_panel_diagnostics=tuple(
            reversed(intelligence.evidence_panel_diagnostics)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_evidence_panel_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5b_5_evidence_panels(
        intelligence
    ) == serialize_v4_5b_5_evidence_panels(reordered)
    assert hash_v4_5b_5_evidence_panels(intelligence) == (
        hash_v4_5b_5_evidence_panels(reordered)
    )


def test_v4_5b_5_evidence_panel_layers_are_stable():
    intelligence = build_v4_5b_5_evidence_panels()

    assert validate_evidence_panel_identity_integrity(intelligence)["valid"] is True
    assert validate_evidence_grouping_stability(intelligence)["valid"] is True
    assert validate_evidence_item_stability(intelligence)["valid"] is True
    assert validate_evidence_source_visibility_stability(intelligence)["valid"] is True
    assert (
        validate_evidence_freshness_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert validate_support_status_evidence_panel_stability(intelligence)["valid"] is True
    assert validate_explainability_evidence_panel_stability(intelligence)["valid"] is True
    assert (
        validate_provenance_lineage_evidence_panel_stability(intelligence)["valid"]
        is True
    )
    assert (
        validate_unsupported_missing_evidence_visibility_preservation(
            intelligence
        )["valid"]
        is True
    )
    assert validate_evidence_panel_summary_stability(intelligence)["valid"] is True


def test_v4_5b_5_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_5_evidence_panels()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    diagnostics = validate_fail_visible_evidence_panel_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["evidence_continuity_preserved"] is True
    assert lineage["source_visibility_preserved"] is True
    assert diagnostics["valid"] is True
    assert diagnostics["diagnostic_visibility"]["missing_types"] == []
    assert diagnostics["unsupported_operational_visibility"]["missing_types"] == []
    assert diagnostics["missing_explicit_reasons"] == []


def test_v4_5b_5_visibility_helpers_preserve_descriptive_only_boundaries():
    intelligence = build_v4_5b_5_evidence_panels()
    panels = evidence_panel_summary(intelligence.evidence_panel_records)
    diagnostics = evidence_panel_diagnostic_summary(
        intelligence.evidence_panel_diagnostics
    )
    unsupported = unsupported_operational_state_summary(
        intelligence.unsupported_operational_state_visibility
    )
    descriptive = descriptive_only_evidence_panel_summary(intelligence)

    assert panels[0]["evidence_authorization_enabled"] is False
    assert panels[0]["evidence_scoring_enabled"] is False
    assert diagnostics[0]["silent_fallback_enabled"] is False
    assert diagnostics[0]["scoring_enabled"] is False
    assert unsupported[0]["suppression_enabled"] is False
    assert unsupported[0]["scoring_enabled"] is False
    assert descriptive["evidence_panel_statement"] == EVIDENCE_PANEL_STATEMENT
    assert descriptive["evidence_visibility_non_authority_statement"] == (
        EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert descriptive["non_scoring"] is True


def test_v4_5b_5_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_5_evidence_panels_for_non_operational_validation()
    )
    guarantees = validate_descriptive_only_evidence_panel_guarantees(contaminated)
    counters = guarantees["counters"]

    assert guarantees["valid"] is False
    assert counters["enabled_runtime_execution_count"] > 0
    assert counters["enabled_evidence_authorization_count"] > 0
    assert counters["enabled_evidence_approval_count"] > 0
    assert counters["enabled_evidence_ranking_count"] > 0
    assert counters["enabled_evidence_recommendation_count"] > 0
    assert counters["enabled_scoring_count"] > 0
    assert counters["enabled_remediation_count"] > 0
    assert counters["enabled_planner_integration_count"] > 0


def test_v4_5b_5_report_is_replay_safe_and_certifies_boundaries():
    report = build_v4_5b_5_evidence_panels_report()
    second_report = build_v4_5b_5_evidence_panels_report()
    summary = report["summary"]
    validation = validate_v4_5b_5_evidence_panels()

    assert report == second_report
    assert report["foundation_status"] == V4_5B_5_EVIDENCE_PANEL_STATUS_STABLE
    assert report["deterministic_report_hash"] == (
        second_report["deterministic_report_hash"]
    )
    assert summary["deterministic_evidence_panel_serialization_verified"] is True
    assert summary["deterministic_evidence_panel_hashing_verified"] is True
    assert summary["evidence_grouping_stable"] is True
    assert summary["evidence_source_visibility_stable"] is True
    assert summary["evidence_freshness_visibility_preserved"] is True
    assert summary["fail_visible_evidence_panel_diagnostics_verified"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["validation_error_count"] == 0
    assert "NON-scoring" in summary["repository_remains"]
    assert summary["evidence_panel_statement"] == EVIDENCE_PANEL_STATEMENT
    assert summary["evidence_visibility_non_authority_statement"] == (
        EVIDENCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert validation["valid"] is True
