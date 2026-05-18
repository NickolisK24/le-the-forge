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

from public_trust_visibility.v4_5b_2_support_status_visibility_audit import (  # noqa: E402
    build_v4_5b_2_support_status_visibility,
    build_v4_5b_2_support_status_visibility_report,
    contaminate_v4_5b_2_support_status_visibility_for_non_operational_validation,
    enabled_support_status_capability_flags,
    support_status_capability_counter_values,
    support_status_visibility_equal,
    validate_descriptive_only_support_guarantees,
    validate_evidence_based_support_visibility,
    validate_experimental_deprecated_visibility_preservation,
    validate_explainability_support_visibility,
    validate_fail_visible_support_diagnostics,
    validate_lineage_and_provenance_preservation,
    validate_public_support_surface_visibility,
    validate_support_classification_stability,
    validate_support_identity_integrity,
    validate_support_status_ordering_stability,
    validate_support_status_serialization_and_hashing,
    validate_support_summary_stability,
    validate_unsupported_state_visibility_preservation,
    validate_v4_5b_2_support_status_visibility,
)
from public_trust_visibility.v4_5b_2_support_status_visibility_hashing import (  # noqa: E402
    hash_evidence_based_support_visibility,
    hash_experimental_deprecated_visibility,
    hash_public_support_surface_visibility,
    hash_support_classification_visibility,
    hash_support_diagnostic_record,
    hash_support_status_identity,
    hash_support_summary_record,
    hash_support_visibility_record,
    hash_v4_5b_2_support_status_visibility,
)
from public_trust_visibility.v4_5b_2_support_status_visibility_models import (  # noqa: E402
    EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES,
    EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES,
    EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES,
    PUBLIC_SUPPORT_SURFACE_TYPES,
    SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT,
    SUPPORT_CLASSIFICATION_TYPES,
    SUPPORT_DIAGNOSTIC_TYPES,
    SUPPORT_STATUS_VISIBILITY_STATEMENT,
    SUPPORT_SUMMARY_TYPES,
    UNSUPPORTED_SUPPORT_OPERATIONAL_STATES,
    UNSUPPORTED_SUPPORT_STATE_TYPES,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_SCHEMA_VERSION,
    V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_2_support_status_visibility_serialization import (  # noqa: E402
    serialize_v4_5b_2_support_status_visibility,
)
from public_trust_visibility.v4_5b_2_support_status_visibility_visibility import (  # noqa: E402
    continuity_support_summary,
    descriptive_only_support_status_summary,
    evidence_based_support_summary,
    experimental_deprecated_summary,
    explainability_support_summary,
    support_classification_summary,
    support_diagnostic_summary,
    support_summary_visibility,
    support_surface_summary,
    support_visibility_summary,
    unsupported_operational_state_summary,
    unsupported_state_summary,
    validate_required_support_status_visibility,
)


def test_v4_5b_2_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_2_support_status_visibility()

    with pytest.raises(FrozenInstanceError):
        intelligence.support_authorization_enabled = True

    assert (
        intelligence.support_identity.schema_version
        == V4_5B_2_SUPPORT_STATUS_VISIBILITY_SCHEMA_VERSION
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
    assert intelligence.support_authorization_enabled is False
    assert intelligence.support_approval_enabled is False
    assert intelligence.support_ranking_enabled is False
    assert intelligence.support_recommendation_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_support_status_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in support_status_capability_counter_values(intelligence).values()
    )


def test_v4_5b_2_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_2_support_status_visibility()
    visibility = validate_required_support_status_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["classification_counts"]) == set(SUPPORT_CLASSIFICATION_TYPES)
    assert set(visibility["surface_counts"]) == set(PUBLIC_SUPPORT_SURFACE_TYPES)
    assert set(visibility["unsupported_counts"]) == set(UNSUPPORTED_SUPPORT_STATE_TYPES)
    assert set(visibility["experimental_counts"]) == set(
        EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES
    )
    assert set(visibility["evidence_counts"]) == set(
        EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES
    )
    assert set(visibility["explainability_counts"]) == set(
        EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES
    )
    assert set(visibility["summary_counts"]) == set(SUPPORT_SUMMARY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(SUPPORT_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_SUPPORT_OPERATIONAL_STATES
    )
    assert visibility["missing_classifications"] == []
    assert visibility["missing_surfaces"] == []
    assert visibility["missing_unsupported_states"] == []
    assert visibility["missing_experimental_deprecated"] == []
    assert visibility["missing_evidence_support"] == []
    assert visibility["missing_explainability_support"] == []
    assert visibility["missing_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_2_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_2_support_status_visibility()
    second = build_v4_5b_2_support_status_visibility()
    serialization = validate_support_status_serialization_and_hashing(first)

    assert first == second
    assert support_status_visibility_equal(first, second)
    assert serialize_v4_5b_2_support_status_visibility(first) == (
        serialize_v4_5b_2_support_status_visibility(second)
    )
    assert hash_v4_5b_2_support_status_visibility(first) == (
        hash_v4_5b_2_support_status_visibility(second)
    )
    assert serialization["valid"] is True
    assert len(hash_support_status_identity(first.support_identity)) == 64
    assert len(hash_support_visibility_record(first.support_visibility_records[0])) == 64
    assert len(hash_support_classification_visibility(first.support_classifications[0])) == 64
    assert len(hash_public_support_surface_visibility(first.support_surfaces[0])) == 64
    assert len(
        hash_experimental_deprecated_visibility(
            first.experimental_deprecated_visibility[0]
        )
    ) == 64
    assert len(
        hash_evidence_based_support_visibility(
            first.evidence_based_support_visibility[0]
        )
    ) == 64
    assert len(hash_support_summary_record(first.support_summaries[0])) == 64
    assert len(hash_support_diagnostic_record(first.support_diagnostics[0])) == 64


def test_v4_5b_2_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_2_support_status_visibility()
    reordered = replace(
        intelligence,
        support_visibility_records=tuple(
            reversed(intelligence.support_visibility_records)
        ),
        support_classifications=tuple(reversed(intelligence.support_classifications)),
        support_surfaces=tuple(reversed(intelligence.support_surfaces)),
        unsupported_state_visibility=tuple(
            reversed(intelligence.unsupported_state_visibility)
        ),
        experimental_deprecated_visibility=tuple(
            reversed(intelligence.experimental_deprecated_visibility)
        ),
        evidence_based_support_visibility=tuple(
            reversed(intelligence.evidence_based_support_visibility)
        ),
        explainability_support_visibility=tuple(
            reversed(intelligence.explainability_support_visibility)
        ),
        continuity_support_visibility=tuple(
            reversed(intelligence.continuity_support_visibility)
        ),
        support_summaries=tuple(reversed(intelligence.support_summaries)),
        support_diagnostics=tuple(reversed(intelligence.support_diagnostics)),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_support_status_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5b_2_support_status_visibility(
        intelligence
    ) == serialize_v4_5b_2_support_status_visibility(reordered)
    assert hash_v4_5b_2_support_status_visibility(
        intelligence
    ) == hash_v4_5b_2_support_status_visibility(reordered)


def test_v4_5b_2_support_visibility_layers_are_stable():
    intelligence = build_v4_5b_2_support_status_visibility()

    assert validate_support_identity_integrity(intelligence)["valid"] is True
    assert validate_support_classification_stability(intelligence)["valid"] is True
    assert validate_public_support_surface_visibility(intelligence)["valid"] is True
    assert (
        validate_unsupported_state_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert (
        validate_experimental_deprecated_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert validate_evidence_based_support_visibility(intelligence)["valid"] is True
    assert validate_explainability_support_visibility(intelligence)["valid"] is True
    assert validate_support_summary_stability(intelligence)["valid"] is True


def test_v4_5b_2_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_2_support_status_visibility()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_support_diagnostics(intelligence)

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


def test_v4_5b_2_visibility_helpers_are_non_operational():
    intelligence = build_v4_5b_2_support_status_visibility()

    assert len(support_visibility_summary(intelligence.support_visibility_records)) == 1
    assert len(
        support_classification_summary(intelligence.support_classifications)
    ) == len(SUPPORT_CLASSIFICATION_TYPES)
    assert len(support_surface_summary(intelligence.support_surfaces)) == len(
        PUBLIC_SUPPORT_SURFACE_TYPES
    )
    assert len(unsupported_state_summary(intelligence.unsupported_state_visibility)) == len(
        UNSUPPORTED_SUPPORT_STATE_TYPES
    )
    assert len(
        experimental_deprecated_summary(intelligence.experimental_deprecated_visibility)
    ) == len(EXPERIMENTAL_DEPRECATED_VISIBILITY_TYPES)
    assert len(
        evidence_based_support_summary(intelligence.evidence_based_support_visibility)
    ) == len(EVIDENCE_BASED_SUPPORT_VISIBILITY_TYPES)
    assert len(
        explainability_support_summary(intelligence.explainability_support_visibility)
    ) == len(EXPLAINABILITY_SUPPORT_VISIBILITY_TYPES)
    assert len(
        continuity_support_summary(intelligence.continuity_support_visibility)
    ) > 0
    assert len(support_summary_visibility(intelligence.support_summaries)) == len(
        SUPPORT_SUMMARY_TYPES
    )
    assert len(support_diagnostic_summary(intelligence.support_diagnostics)) == len(
        SUPPORT_DIAGNOSTIC_TYPES
    )
    assert len(
        unsupported_operational_state_summary(
            intelligence.unsupported_operational_state_visibility
        )
    ) == len(UNSUPPORTED_SUPPORT_OPERATIONAL_STATES)
    summary = descriptive_only_support_status_summary(intelligence)
    assert summary["support_status_visibility_statement"] == (
        SUPPORT_STATUS_VISIBILITY_STATEMENT
    )
    assert summary["support_classification_non_authority_statement"] == (
        SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT
    )
    assert summary["support_authorization_enabled"] is False
    assert summary["support_approval_enabled"] is False
    assert summary["support_ranking_enabled"] is False
    assert summary["support_recommendation_enabled"] is False


def test_v4_5b_2_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_2_support_status_visibility_for_non_operational_validation()
    )
    validation = validate_v4_5b_2_support_status_visibility(contaminated)
    descriptive = validate_descriptive_only_support_guarantees(contaminated)

    assert validation["valid"] is False
    assert "descriptive_only_guarantees" in validation["failed_validations"]
    assert descriptive["valid"] is False
    assert descriptive["counters"]["enabled_runtime_execution_count"] > 0
    assert descriptive["counters"]["enabled_support_authorization_count"] > 0
    assert descriptive["counters"]["enabled_support_approval_count"] > 0
    assert descriptive["counters"]["enabled_support_ranking_count"] > 0
    assert descriptive["counters"]["enabled_support_recommendation_count"] > 0
    assert descriptive["counters"]["enabled_remediation_count"] > 0


def test_v4_5b_2_report_is_replay_safe_and_certifies_support_boundary():
    first = build_v4_5b_2_support_status_visibility_report()
    second = build_v4_5b_2_support_status_visibility_report()
    summary = first["summary"]

    assert first == second
    assert first["foundation_status"] == V4_5B_2_SUPPORT_STATUS_VISIBILITY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["support_classification_stable"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["support_status_visibility_statement"] == (
        SUPPORT_STATUS_VISIBILITY_STATEMENT
    )
    assert summary["support_classification_non_authority_statement"] == (
        SUPPORT_CLASSIFICATION_NON_AUTHORITY_STATEMENT
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
