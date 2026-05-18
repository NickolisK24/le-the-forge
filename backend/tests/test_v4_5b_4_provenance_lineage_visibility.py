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

from public_trust_visibility.v4_5b_4_provenance_lineage_visibility_audit import (  # noqa: E402
    build_v4_5b_4_provenance_lineage_visibility,
    build_v4_5b_4_provenance_lineage_visibility_report,
    contaminate_v4_5b_4_provenance_lineage_visibility_for_non_operational_validation,
    enabled_provenance_lineage_capability_flags,
    provenance_lineage_capability_counter_values,
    provenance_lineage_visibility_equal,
    validate_descriptive_only_provenance_lineage_guarantees,
    validate_evidence_origin_visibility_preservation,
    validate_explainability_lineage_preservation,
    validate_fail_visible_provenance_lineage_diagnostics,
    validate_lineage_and_provenance_preservation,
    validate_lineage_identity_integrity,
    validate_provenance_identity_integrity,
    validate_provenance_lineage_ordering_stability,
    validate_provenance_lineage_serialization_and_hashing,
    validate_source_to_surface_visibility_stability,
    validate_stale_unknown_provenance_visibility_preservation,
    validate_support_status_lineage_preservation,
    validate_trust_summary_lineage_preservation,
    validate_v4_5b_4_provenance_lineage_visibility,
)
from public_trust_visibility.v4_5b_4_provenance_lineage_visibility_hashing import (  # noqa: E402
    hash_evidence_origin_visibility,
    hash_lineage_visibility_record,
    hash_provenance_lineage_diagnostic_record,
    hash_provenance_lineage_summary_record,
    hash_provenance_lineage_visibility_identity,
    hash_provenance_visibility_record,
    hash_source_to_surface_visibility,
    hash_v4_5b_4_provenance_lineage_visibility,
)
from public_trust_visibility.v4_5b_4_provenance_lineage_visibility_models import (  # noqa: E402
    EVIDENCE_ORIGIN_VISIBILITY_TYPES,
    EXPLAINABILITY_LINEAGE_TYPES,
    PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES,
    PROVENANCE_LINEAGE_SUMMARY_TYPES,
    PROVENANCE_LINEAGE_VISIBILITY_STATEMENT,
    SOURCE_TO_SURFACE_VISIBILITY_TYPES,
    SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT,
    STALE_UNKNOWN_PROVENANCE_TYPES,
    SUPPORT_STATUS_LINEAGE_TYPES,
    TRUST_SUMMARY_LINEAGE_TYPES,
    UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_SCHEMA_VERSION,
    V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_4_provenance_lineage_visibility_serialization import (  # noqa: E402
    serialize_v4_5b_4_provenance_lineage_visibility,
)
from public_trust_visibility.v4_5b_4_provenance_lineage_visibility_visibility import (  # noqa: E402
    descriptive_only_provenance_lineage_summary,
    evidence_origin_summary,
    explainability_lineage_summary,
    lineage_visibility_summary,
    provenance_lineage_diagnostic_summary,
    provenance_lineage_summary_visibility,
    provenance_visibility_summary,
    source_to_surface_summary,
    stale_unknown_provenance_summary,
    support_status_lineage_summary,
    trust_summary_lineage_summary,
    unsupported_operational_state_summary,
    validate_required_provenance_lineage_visibility,
)


def test_v4_5b_4_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()

    with pytest.raises(FrozenInstanceError):
        intelligence.source_authorization_enabled = True

    assert (
        intelligence.visibility_identity.schema_version
        == V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_SCHEMA_VERSION
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
    assert intelligence.source_authorization_enabled is False
    assert intelligence.source_approval_enabled is False
    assert intelligence.provenance_ranking_enabled is False
    assert intelligence.lineage_recommendation_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_provenance_lineage_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in provenance_lineage_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5b_4_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()
    visibility = validate_required_provenance_lineage_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["source_counts"]) == set(SOURCE_TO_SURFACE_VISIBILITY_TYPES)
    assert set(visibility["evidence_counts"]) == set(EVIDENCE_ORIGIN_VISIBILITY_TYPES)
    assert set(visibility["support_counts"]) == set(SUPPORT_STATUS_LINEAGE_TYPES)
    assert set(visibility["explainability_counts"]) == set(
        EXPLAINABILITY_LINEAGE_TYPES
    )
    assert set(visibility["trust_counts"]) == set(TRUST_SUMMARY_LINEAGE_TYPES)
    assert set(visibility["stale_unknown_counts"]) == set(
        STALE_UNKNOWN_PROVENANCE_TYPES
    )
    assert set(visibility["summary_counts"]) == set(PROVENANCE_LINEAGE_SUMMARY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(
        PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES
    )
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES
    )
    assert visibility["missing_source_to_surface"] == []
    assert visibility["missing_evidence_origin"] == []
    assert visibility["missing_support_status_lineage"] == []
    assert visibility["missing_explainability_lineage"] == []
    assert visibility["missing_trust_summary_lineage"] == []
    assert visibility["missing_stale_unknown_provenance"] == []
    assert visibility["missing_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_4_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_4_provenance_lineage_visibility()
    second = build_v4_5b_4_provenance_lineage_visibility()
    serialization = validate_provenance_lineage_serialization_and_hashing(first)

    assert first == second
    assert provenance_lineage_visibility_equal(first, second)
    assert serialize_v4_5b_4_provenance_lineage_visibility(first) == (
        serialize_v4_5b_4_provenance_lineage_visibility(second)
    )
    assert hash_v4_5b_4_provenance_lineage_visibility(first) == (
        hash_v4_5b_4_provenance_lineage_visibility(second)
    )
    assert serialization["valid"] is True
    assert serialization["provenance_serialization_stable"] is True
    assert serialization["lineage_serialization_stable"] is True
    assert serialization["provenance_hashing_stable"] is True
    assert serialization["lineage_hashing_stable"] is True
    assert len(hash_provenance_lineage_visibility_identity(first.visibility_identity)) == 64
    assert len(hash_provenance_visibility_record(first.provenance_visibility_records[0])) == 64
    assert len(hash_lineage_visibility_record(first.lineage_visibility_records[0])) == 64
    assert len(hash_source_to_surface_visibility(first.source_to_surface_visibility[0])) == 64
    assert len(hash_evidence_origin_visibility(first.evidence_origin_visibility[0])) == 64
    assert len(
        hash_provenance_lineage_summary_record(
            first.provenance_lineage_summaries[0]
        )
    ) == 64
    assert len(
        hash_provenance_lineage_diagnostic_record(
            first.provenance_lineage_diagnostics[0]
        )
    ) == 64


def test_v4_5b_4_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()
    reordered = replace(
        intelligence,
        provenance_visibility_records=tuple(
            reversed(intelligence.provenance_visibility_records)
        ),
        lineage_visibility_records=tuple(
            reversed(intelligence.lineage_visibility_records)
        ),
        source_to_surface_visibility=tuple(
            reversed(intelligence.source_to_surface_visibility)
        ),
        evidence_origin_visibility=tuple(
            reversed(intelligence.evidence_origin_visibility)
        ),
        support_status_lineage_visibility=tuple(
            reversed(intelligence.support_status_lineage_visibility)
        ),
        explainability_lineage_visibility=tuple(
            reversed(intelligence.explainability_lineage_visibility)
        ),
        trust_summary_lineage_visibility=tuple(
            reversed(intelligence.trust_summary_lineage_visibility)
        ),
        stale_unknown_provenance_visibility=tuple(
            reversed(intelligence.stale_unknown_provenance_visibility)
        ),
        provenance_lineage_summaries=tuple(
            reversed(intelligence.provenance_lineage_summaries)
        ),
        provenance_lineage_diagnostics=tuple(
            reversed(intelligence.provenance_lineage_diagnostics)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert (
        validate_provenance_lineage_ordering_stability(intelligence)["valid"] is True
    )
    assert serialize_v4_5b_4_provenance_lineage_visibility(
        intelligence
    ) == serialize_v4_5b_4_provenance_lineage_visibility(reordered)
    assert hash_v4_5b_4_provenance_lineage_visibility(
        intelligence
    ) == hash_v4_5b_4_provenance_lineage_visibility(reordered)


def test_v4_5b_4_provenance_and_lineage_layers_are_stable():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()

    assert validate_provenance_identity_integrity(intelligence)["valid"] is True
    assert validate_lineage_identity_integrity(intelligence)["valid"] is True
    assert validate_source_to_surface_visibility_stability(intelligence)["valid"] is True
    assert (
        validate_evidence_origin_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert validate_support_status_lineage_preservation(intelligence)["valid"] is True
    assert validate_explainability_lineage_preservation(intelligence)["valid"] is True
    assert validate_trust_summary_lineage_preservation(intelligence)["valid"] is True
    assert (
        validate_stale_unknown_provenance_visibility_preservation(intelligence)["valid"]
        is True
    )


def test_v4_5b_4_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_provenance_lineage_diagnostics(intelligence)

    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert lineage["evidence_continuity_preserved"] is True
    assert fail_visible["valid"] is True
    assert fail_visible["fail_visible"] is True
    assert fail_visible["silent_fallback_enabled_count"] == 0
    assert fail_visible["hidden_fallback_enabled_count"] == 0
    assert fail_visible["authorization_enabled_count"] == 0
    assert fail_visible["approval_enabled_count"] == 0
    assert fail_visible["ranking_enabled_count"] == 0
    assert fail_visible["recommendation_enabled_count"] == 0
    assert fail_visible["missing_diagnostic_types"] == []
    assert fail_visible["missing_unsupported_states"] == []


def test_v4_5b_4_visibility_helpers_are_non_operational():
    intelligence = build_v4_5b_4_provenance_lineage_visibility()

    assert len(provenance_visibility_summary(intelligence.provenance_visibility_records)) == 1
    assert len(lineage_visibility_summary(intelligence.lineage_visibility_records)) == 1
    assert len(source_to_surface_summary(intelligence.source_to_surface_visibility)) == len(
        SOURCE_TO_SURFACE_VISIBILITY_TYPES
    )
    assert len(evidence_origin_summary(intelligence.evidence_origin_visibility)) == len(
        EVIDENCE_ORIGIN_VISIBILITY_TYPES
    )
    assert len(
        support_status_lineage_summary(intelligence.support_status_lineage_visibility)
    ) == len(SUPPORT_STATUS_LINEAGE_TYPES)
    assert len(
        explainability_lineage_summary(intelligence.explainability_lineage_visibility)
    ) == len(EXPLAINABILITY_LINEAGE_TYPES)
    assert len(
        trust_summary_lineage_summary(intelligence.trust_summary_lineage_visibility)
    ) == len(TRUST_SUMMARY_LINEAGE_TYPES)
    assert len(
        stale_unknown_provenance_summary(
            intelligence.stale_unknown_provenance_visibility
        )
    ) == len(STALE_UNKNOWN_PROVENANCE_TYPES)
    assert len(
        provenance_lineage_summary_visibility(
            intelligence.provenance_lineage_summaries
        )
    ) == len(PROVENANCE_LINEAGE_SUMMARY_TYPES)
    assert len(
        provenance_lineage_diagnostic_summary(
            intelligence.provenance_lineage_diagnostics
        )
    ) == len(PROVENANCE_LINEAGE_DIAGNOSTIC_TYPES)
    assert len(
        unsupported_operational_state_summary(
            intelligence.unsupported_operational_state_visibility
        )
    ) == len(UNSUPPORTED_PROVENANCE_LINEAGE_OPERATIONAL_STATES)
    summary = descriptive_only_provenance_lineage_summary(intelligence)
    assert summary["provenance_lineage_visibility_statement"] == (
        PROVENANCE_LINEAGE_VISIBILITY_STATEMENT
    )
    assert summary["source_visibility_non_authority_statement"] == (
        SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert summary["source_authorization_enabled"] is False
    assert summary["source_approval_enabled"] is False
    assert summary["provenance_ranking_enabled"] is False
    assert summary["lineage_recommendation_enabled"] is False


def test_v4_5b_4_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_4_provenance_lineage_visibility_for_non_operational_validation()
    )
    validation = validate_v4_5b_4_provenance_lineage_visibility(contaminated)
    descriptive = validate_descriptive_only_provenance_lineage_guarantees(contaminated)

    assert validation["valid"] is False
    assert "descriptive_only_guarantees" in validation["failed_validations"]
    assert descriptive["valid"] is False
    assert descriptive["counters"]["enabled_runtime_execution_count"] > 0
    assert descriptive["counters"]["enabled_source_authorization_count"] > 0
    assert descriptive["counters"]["enabled_source_approval_count"] > 0
    assert descriptive["counters"]["enabled_provenance_ranking_count"] > 0
    assert descriptive["counters"]["enabled_lineage_recommendation_count"] > 0
    assert descriptive["counters"]["enabled_remediation_count"] > 0


def test_v4_5b_4_report_is_replay_safe_and_certifies_provenance_boundary():
    first = build_v4_5b_4_provenance_lineage_visibility_report()
    second = build_v4_5b_4_provenance_lineage_visibility_report()
    summary = first["summary"]

    assert first == second
    assert (
        first["foundation_status"]
        == V4_5B_4_PROVENANCE_LINEAGE_VISIBILITY_STATUS_STABLE
    )
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_provenance_serialization_verified"] is True
    assert summary["deterministic_lineage_serialization_verified"] is True
    assert summary["deterministic_provenance_hashing_verified"] is True
    assert summary["deterministic_lineage_hashing_verified"] is True
    assert summary["source_to_surface_visibility_stable"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["provenance_lineage_visibility_statement"] == (
        PROVENANCE_LINEAGE_VISIBILITY_STATEMENT
    )
    assert summary["source_visibility_non_authority_statement"] == (
        SOURCE_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert summary["repository_remains"] == [
        "NON-operational",
        "NON-authorizing",
        "NON-approving",
        "NON-executing",
        "NON-remediating",
        "NON-runtime-mutating",
        "NON-ranking",
        "NON-recommending",
    ]
    assert all(
        value == 0 for key, value in summary.items() if key.startswith("enabled_")
    )
