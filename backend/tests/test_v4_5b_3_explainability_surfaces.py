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

from public_trust_visibility.v4_5b_3_explainability_surface_audit import (  # noqa: E402
    build_v4_5b_3_explainability_surfaces,
    build_v4_5b_3_explainability_surfaces_report,
    contaminate_v4_5b_3_explainability_surfaces_for_non_operational_validation,
    enabled_explainability_surface_capability_flags,
    explainability_surface_capability_counter_values,
    explainability_surface_equal,
    validate_continuity_explanation_visibility,
    validate_descriptive_only_explainability_guarantees,
    validate_evidence_to_explanation_mapping_stability,
    validate_explainability_identity_integrity,
    validate_explainability_surface_ordering_stability,
    validate_explainability_surface_serialization_and_hashing,
    validate_fail_visible_explanation_diagnostics,
    validate_limitation_explanation_preservation,
    validate_lineage_and_provenance_preservation,
    validate_support_state_explanation_visibility,
    validate_trust_explanation_visibility,
    validate_unsupported_state_explanation_preservation,
    validate_v4_5b_3_explainability_surfaces,
)
from public_trust_visibility.v4_5b_3_explainability_surface_hashing import (  # noqa: E402
    hash_evidence_to_explanation_mapping,
    hash_explainability_surface_identity,
    hash_explainability_surface_record,
    hash_explanation_diagnostic_record,
    hash_explanation_summary_record,
    hash_limitation_explanation_visibility,
    hash_support_state_explanation_surface,
    hash_v4_5b_3_explainability_surfaces,
)
from public_trust_visibility.v4_5b_3_explainability_surface_models import (  # noqa: E402
    CONTINUITY_EXPLANATION_TYPES,
    EVIDENCE_TO_EXPLANATION_MAPPING_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    EXPLANATION_SUMMARY_TYPES,
    EXPLAINABILITY_SURFACE_STATEMENT,
    EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT,
    LIMITATION_EXPLANATION_TYPES,
    SUPPORT_STATE_EXPLANATION_TYPES,
    TRUST_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_EXPLANATION_TYPES,
    V4_5B_3_EXPLAINABILITY_SURFACE_SCHEMA_VERSION,
    V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_3_explainability_surface_serialization import (  # noqa: E402
    serialize_v4_5b_3_explainability_surfaces,
)
from public_trust_visibility.v4_5b_3_explainability_surface_visibility import (  # noqa: E402
    continuity_explanation_summary,
    descriptive_only_explainability_surface_summary,
    evidence_to_explanation_mapping_summary,
    explanation_diagnostic_summary,
    explanation_summary_visibility,
    explanation_surface_summary,
    limitation_explanation_summary,
    support_state_explanation_summary,
    trust_explanation_summary,
    unsupported_operational_state_summary,
    unsupported_state_explanation_summary,
    validate_required_explainability_surfaces,
)


def test_v4_5b_3_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_3_explainability_surfaces()

    with pytest.raises(FrozenInstanceError):
        intelligence.explainability_authorization_enabled = True

    assert (
        intelligence.surface_identity.schema_version
        == V4_5B_3_EXPLAINABILITY_SURFACE_SCHEMA_VERSION
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
    assert intelligence.explainability_authorization_enabled is False
    assert intelligence.explainability_approval_enabled is False
    assert intelligence.explainability_ranking_enabled is False
    assert intelligence.explainability_recommendation_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_explainability_surface_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in explainability_surface_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5b_3_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_3_explainability_surfaces()
    visibility = validate_required_explainability_surfaces(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["support_counts"]) == set(SUPPORT_STATE_EXPLANATION_TYPES)
    assert set(visibility["mapping_counts"]) == set(
        EVIDENCE_TO_EXPLANATION_MAPPING_TYPES
    )
    assert set(visibility["limitation_counts"]) == set(LIMITATION_EXPLANATION_TYPES)
    assert set(visibility["trust_counts"]) == set(TRUST_EXPLANATION_TYPES)
    assert set(visibility["continuity_counts"]) == set(CONTINUITY_EXPLANATION_TYPES)
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_STATE_EXPLANATION_TYPES
    )
    assert set(visibility["summary_counts"]) == set(EXPLANATION_SUMMARY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(EXPLANATION_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES
    )
    assert visibility["missing_support_state_explanations"] == []
    assert visibility["missing_evidence_mappings"] == []
    assert visibility["missing_limitation_explanations"] == []
    assert visibility["missing_trust_explanations"] == []
    assert visibility["missing_continuity_explanations"] == []
    assert visibility["missing_unsupported_state_explanations"] == []
    assert visibility["missing_diagnostics"] == []
    assert visibility["missing_unsupported_operational_states"] == []


def test_v4_5b_3_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_3_explainability_surfaces()
    second = build_v4_5b_3_explainability_surfaces()
    serialization = validate_explainability_surface_serialization_and_hashing(first)

    assert first == second
    assert explainability_surface_equal(first, second)
    assert serialize_v4_5b_3_explainability_surfaces(first) == (
        serialize_v4_5b_3_explainability_surfaces(second)
    )
    assert hash_v4_5b_3_explainability_surfaces(first) == (
        hash_v4_5b_3_explainability_surfaces(second)
    )
    assert serialization["valid"] is True
    assert len(hash_explainability_surface_identity(first.surface_identity)) == 64
    assert len(hash_explainability_surface_record(first.surface_records[0])) == 64
    assert len(
        hash_support_state_explanation_surface(first.support_state_explanations[0])
    ) == 64
    assert len(
        hash_evidence_to_explanation_mapping(
            first.evidence_to_explanation_mappings[0]
        )
    ) == 64
    assert len(
        hash_limitation_explanation_visibility(first.limitation_explanations[0])
    ) == 64
    assert len(hash_explanation_summary_record(first.explanation_summaries[0])) == 64
    assert len(
        hash_explanation_diagnostic_record(first.explanation_diagnostics[0])
    ) == 64


def test_v4_5b_3_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_3_explainability_surfaces()
    reordered = replace(
        intelligence,
        surface_records=tuple(reversed(intelligence.surface_records)),
        support_state_explanations=tuple(
            reversed(intelligence.support_state_explanations)
        ),
        evidence_to_explanation_mappings=tuple(
            reversed(intelligence.evidence_to_explanation_mappings)
        ),
        limitation_explanations=tuple(
            reversed(intelligence.limitation_explanations)
        ),
        trust_explanations=tuple(reversed(intelligence.trust_explanations)),
        continuity_explanations=tuple(
            reversed(intelligence.continuity_explanations)
        ),
        unsupported_state_explanations=tuple(
            reversed(intelligence.unsupported_state_explanations)
        ),
        explanation_summaries=tuple(reversed(intelligence.explanation_summaries)),
        explanation_diagnostics=tuple(reversed(intelligence.explanation_diagnostics)),
        unsupported_operational_state_visibility=tuple(
            reversed(intelligence.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert (
        validate_explainability_surface_ordering_stability(intelligence)["valid"]
        is True
    )
    assert serialize_v4_5b_3_explainability_surfaces(
        intelligence
    ) == serialize_v4_5b_3_explainability_surfaces(reordered)
    assert hash_v4_5b_3_explainability_surfaces(
        intelligence
    ) == hash_v4_5b_3_explainability_surfaces(reordered)


def test_v4_5b_3_explainability_layers_are_stable():
    intelligence = build_v4_5b_3_explainability_surfaces()

    assert validate_explainability_identity_integrity(intelligence)["valid"] is True
    assert validate_support_state_explanation_visibility(intelligence)["valid"] is True
    assert (
        validate_evidence_to_explanation_mapping_stability(intelligence)["valid"]
        is True
    )
    assert validate_limitation_explanation_preservation(intelligence)["valid"] is True
    assert validate_trust_explanation_visibility(intelligence)["valid"] is True
    assert validate_continuity_explanation_visibility(intelligence)["valid"] is True
    assert (
        validate_unsupported_state_explanation_preservation(intelligence)["valid"]
        is True
    )


def test_v4_5b_3_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_3_explainability_surfaces()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_explanation_diagnostics(intelligence)

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


def test_v4_5b_3_visibility_helpers_are_non_operational():
    intelligence = build_v4_5b_3_explainability_surfaces()

    assert len(explanation_surface_summary(intelligence.surface_records)) == 1
    assert len(
        support_state_explanation_summary(intelligence.support_state_explanations)
    ) == len(SUPPORT_STATE_EXPLANATION_TYPES)
    assert len(
        evidence_to_explanation_mapping_summary(
            intelligence.evidence_to_explanation_mappings
        )
    ) == len(EVIDENCE_TO_EXPLANATION_MAPPING_TYPES)
    assert len(limitation_explanation_summary(intelligence.limitation_explanations)) == len(
        LIMITATION_EXPLANATION_TYPES
    )
    assert len(trust_explanation_summary(intelligence.trust_explanations)) == len(
        TRUST_EXPLANATION_TYPES
    )
    assert len(
        continuity_explanation_summary(intelligence.continuity_explanations)
    ) == len(CONTINUITY_EXPLANATION_TYPES)
    assert len(
        unsupported_state_explanation_summary(
            intelligence.unsupported_state_explanations
        )
    ) == len(UNSUPPORTED_STATE_EXPLANATION_TYPES)
    assert len(explanation_summary_visibility(intelligence.explanation_summaries)) == len(
        EXPLANATION_SUMMARY_TYPES
    )
    assert len(explanation_diagnostic_summary(intelligence.explanation_diagnostics)) == len(
        EXPLANATION_DIAGNOSTIC_TYPES
    )
    assert len(
        unsupported_operational_state_summary(
            intelligence.unsupported_operational_state_visibility
        )
    ) == len(UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES)
    summary = descriptive_only_explainability_surface_summary(intelligence)
    assert summary["explainability_surface_statement"] == (
        EXPLAINABILITY_SURFACE_STATEMENT
    )
    assert summary["explainability_visibility_non_authority_statement"] == (
        EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert summary["explainability_authorization_enabled"] is False
    assert summary["explainability_approval_enabled"] is False
    assert summary["explainability_ranking_enabled"] is False
    assert summary["explainability_recommendation_enabled"] is False


def test_v4_5b_3_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_3_explainability_surfaces_for_non_operational_validation()
    )
    validation = validate_v4_5b_3_explainability_surfaces(contaminated)
    descriptive = validate_descriptive_only_explainability_guarantees(contaminated)

    assert validation["valid"] is False
    assert "descriptive_only_guarantees" in validation["failed_validations"]
    assert descriptive["valid"] is False
    assert descriptive["counters"]["enabled_runtime_execution_count"] > 0
    assert descriptive["counters"]["enabled_explainability_authorization_count"] > 0
    assert descriptive["counters"]["enabled_explainability_approval_count"] > 0
    assert descriptive["counters"]["enabled_explainability_ranking_count"] > 0
    assert descriptive["counters"]["enabled_explainability_recommendation_count"] > 0
    assert descriptive["counters"]["enabled_remediation_count"] > 0


def test_v4_5b_3_report_is_replay_safe_and_certifies_explainability_boundary():
    first = build_v4_5b_3_explainability_surfaces_report()
    second = build_v4_5b_3_explainability_surfaces_report()
    summary = first["summary"]

    assert first == second
    assert first["foundation_status"] == V4_5B_3_EXPLAINABILITY_SURFACE_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["evidence_to_explanation_mapping_stable"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["explainability_surface_statement"] == (
        EXPLAINABILITY_SURFACE_STATEMENT
    )
    assert summary["explainability_visibility_non_authority_statement"] == (
        EXPLAINABILITY_VISIBILITY_NON_AUTHORITY_STATEMENT
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
