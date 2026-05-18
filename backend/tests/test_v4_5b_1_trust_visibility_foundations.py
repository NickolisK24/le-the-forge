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

from public_trust_visibility.v4_5b_1_trust_visibility_foundation_audit import (  # noqa: E402
    build_v4_5b_1_trust_visibility_foundation,
    build_v4_5b_1_trust_visibility_foundation_report,
    contaminate_v4_5b_1_trust_visibility_foundation_for_non_operational_validation,
    enabled_trust_visibility_capability_flags,
    trust_visibility_capability_counter_values,
    trust_visibility_foundation_equal,
    validate_descriptive_only_public_trust_guarantees,
    validate_fail_visible_public_trust_diagnostics,
    validate_governance_transparency_visibility_preservation,
    validate_lineage_and_provenance_preservation,
    validate_public_explainability_visibility,
    validate_public_integrity_visibility,
    validate_public_trust_evidence_visibility,
    validate_trust_summary_stability,
    validate_trust_visibility_identity_integrity,
    validate_trust_visibility_ordering_stability,
    validate_trust_visibility_serialization_and_hashing,
    validate_unsupported_state_visibility_preservation,
    validate_v4_5b_1_trust_visibility_foundation,
)
from public_trust_visibility.v4_5b_1_trust_visibility_foundation_hashing import (  # noqa: E402
    hash_governance_transparency_visibility,
    hash_public_trust_diagnostic_record,
    hash_public_trust_evidence_visibility,
    hash_trust_summary_record,
    hash_trust_visibility_identity,
    hash_trust_visibility_record,
    hash_v4_5b_1_trust_visibility_foundation,
)
from public_trust_visibility.v4_5b_1_trust_visibility_foundation_models import (  # noqa: E402
    GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES,
    PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES,
    PUBLIC_INTEGRITY_VISIBILITY_TYPES,
    PUBLIC_TRUST_DIAGNOSTIC_TYPES,
    PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES,
    PUBLIC_TRUST_VISIBILITY_NON_AUTHORITY_STATEMENT,
    PUBLIC_TRUST_VISIBILITY_STATEMENT,
    TRUST_SUMMARY_TYPES,
    UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_VISIBILITY_TYPES,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_SCHEMA_VERSION,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_STABLE,
)
from public_trust_visibility.v4_5b_1_trust_visibility_foundation_serialization import (  # noqa: E402
    serialize_v4_5b_1_trust_visibility_foundation,
)
from public_trust_visibility.v4_5b_1_trust_visibility_foundation_visibility import (  # noqa: E402
    descriptive_only_public_trust_summary,
    diagnostics_summary,
    evidence_visibility_summary,
    explainability_summary,
    governance_transparency_summary,
    integrity_summary,
    trust_summary_visibility,
    trust_visibility_summary,
    unsupported_public_trust_summary,
    unsupported_state_summary,
    validate_required_trust_visibility_foundation,
)


def test_v4_5b_1_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5b_1_trust_visibility_foundation()

    with pytest.raises(FrozenInstanceError):
        intelligence.trust_authorization_enabled = True

    assert (
        intelligence.trust_identity.schema_version
        == V4_5B_1_TRUST_VISIBILITY_FOUNDATION_SCHEMA_VERSION
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
    assert intelligence.trust_authorization_enabled is False
    assert intelligence.trust_approval_enabled is False
    assert intelligence.trust_ranking_enabled is False
    assert intelligence.trust_recommendation_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_trust_visibility_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in trust_visibility_capability_counter_values(intelligence).values()
    )


def test_v4_5b_1_required_visibility_sets_are_complete():
    intelligence = build_v4_5b_1_trust_visibility_foundation()
    visibility = validate_required_trust_visibility_foundation(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["evidence_counts"]) == set(
        PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES
    )
    assert set(visibility["unsupported_counts"]) == set(
        UNSUPPORTED_STATE_VISIBILITY_TYPES
    )
    assert set(visibility["transparency_counts"]) == set(
        GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES
    )
    assert set(visibility["summary_counts"]) == set(TRUST_SUMMARY_TYPES)
    assert set(visibility["explainability_counts"]) == set(
        PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES
    )
    assert set(visibility["integrity_counts"]) == set(
        PUBLIC_INTEGRITY_VISIBILITY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(PUBLIC_TRUST_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_operational_counts"]) == set(
        UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES
    )
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_unsupported_types"] == []
    assert visibility["missing_transparency_types"] == []
    assert visibility["missing_summary_types"] == []
    assert visibility["missing_explainability_types"] == []
    assert visibility["missing_integrity_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5b_1_serialization_hashing_and_equality_are_stable():
    first = build_v4_5b_1_trust_visibility_foundation()
    second = build_v4_5b_1_trust_visibility_foundation()
    serialization = validate_trust_visibility_serialization_and_hashing(first)

    assert first == second
    assert trust_visibility_foundation_equal(first, second)
    assert serialize_v4_5b_1_trust_visibility_foundation(first) == (
        serialize_v4_5b_1_trust_visibility_foundation(second)
    )
    assert hash_v4_5b_1_trust_visibility_foundation(first) == (
        hash_v4_5b_1_trust_visibility_foundation(second)
    )
    assert serialization["valid"] is True
    assert len(hash_trust_visibility_identity(first.trust_identity)) == 64
    assert len(hash_trust_visibility_record(first.trust_visibility_records[0])) == 64
    assert len(hash_public_trust_evidence_visibility(first.evidence_visibility[0])) == 64
    assert len(
        hash_governance_transparency_visibility(
            first.governance_transparency_visibility[0]
        )
    ) == 64
    assert len(hash_trust_summary_record(first.trust_summaries[0])) == 64
    assert len(hash_public_trust_diagnostic_record(first.public_trust_diagnostics[0])) == 64


def test_v4_5b_1_ordering_survives_reordered_collections():
    intelligence = build_v4_5b_1_trust_visibility_foundation()
    reordered = replace(
        intelligence,
        trust_visibility_records=tuple(reversed(intelligence.trust_visibility_records)),
        evidence_visibility=tuple(reversed(intelligence.evidence_visibility)),
        unsupported_state_visibility=tuple(
            reversed(intelligence.unsupported_state_visibility)
        ),
        governance_transparency_visibility=tuple(
            reversed(intelligence.governance_transparency_visibility)
        ),
        trust_summaries=tuple(reversed(intelligence.trust_summaries)),
        explainability_visibility=tuple(
            reversed(intelligence.explainability_visibility)
        ),
        integrity_visibility=tuple(reversed(intelligence.integrity_visibility)),
        public_trust_diagnostics=tuple(
            reversed(intelligence.public_trust_diagnostics)
        ),
        unsupported_public_trust_visibility=tuple(
            reversed(intelligence.unsupported_public_trust_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_trust_visibility_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5b_1_trust_visibility_foundation(
        intelligence
    ) == serialize_v4_5b_1_trust_visibility_foundation(reordered)
    assert hash_v4_5b_1_trust_visibility_foundation(
        intelligence
    ) == hash_v4_5b_1_trust_visibility_foundation(reordered)


def test_v4_5b_1_trust_visibility_layers_are_stable():
    intelligence = build_v4_5b_1_trust_visibility_foundation()

    assert validate_trust_visibility_identity_integrity(intelligence)["valid"] is True
    assert validate_public_trust_evidence_visibility(intelligence)["valid"] is True
    assert (
        validate_unsupported_state_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert (
        validate_governance_transparency_visibility_preservation(intelligence)["valid"]
        is True
    )
    assert validate_trust_summary_stability(intelligence)["valid"] is True
    assert validate_public_explainability_visibility(intelligence)["valid"] is True
    assert validate_public_integrity_visibility(intelligence)["valid"] is True


def test_v4_5b_1_lineage_provenance_and_fail_visible_diagnostics_are_preserved():
    intelligence = build_v4_5b_1_trust_visibility_foundation()
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    fail_visible = validate_fail_visible_public_trust_diagnostics(intelligence)

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


def test_v4_5b_1_visibility_helpers_are_non_operational():
    intelligence = build_v4_5b_1_trust_visibility_foundation()

    assert len(trust_visibility_summary(intelligence.trust_visibility_records)) == 1
    assert len(evidence_visibility_summary(intelligence.evidence_visibility)) == len(
        PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES
    )
    assert len(
        unsupported_state_summary(intelligence.unsupported_state_visibility)
    ) == len(UNSUPPORTED_STATE_VISIBILITY_TYPES)
    assert len(
        governance_transparency_summary(intelligence.governance_transparency_visibility)
    ) == len(GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES)
    assert len(trust_summary_visibility(intelligence.trust_summaries)) == len(
        TRUST_SUMMARY_TYPES
    )
    assert len(explainability_summary(intelligence.explainability_visibility)) == len(
        PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES
    )
    assert len(integrity_summary(intelligence.integrity_visibility)) == len(
        PUBLIC_INTEGRITY_VISIBILITY_TYPES
    )
    assert len(diagnostics_summary(intelligence.public_trust_diagnostics)) == len(
        PUBLIC_TRUST_DIAGNOSTIC_TYPES
    )
    assert len(
        unsupported_public_trust_summary(
            intelligence.unsupported_public_trust_visibility
        )
    ) == len(UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES)
    summary = descriptive_only_public_trust_summary(intelligence)
    assert summary["public_trust_visibility_statement"] == (
        PUBLIC_TRUST_VISIBILITY_STATEMENT
    )
    assert summary["trust_visibility_non_authority_statement"] == (
        PUBLIC_TRUST_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    assert summary["trust_authorization_enabled"] is False
    assert summary["trust_approval_enabled"] is False
    assert summary["trust_ranking_enabled"] is False
    assert summary["trust_recommendation_enabled"] is False


def test_v4_5b_1_contamination_is_fail_visible():
    contaminated = (
        contaminate_v4_5b_1_trust_visibility_foundation_for_non_operational_validation()
    )
    validation = validate_v4_5b_1_trust_visibility_foundation(contaminated)
    descriptive = validate_descriptive_only_public_trust_guarantees(contaminated)

    assert validation["valid"] is False
    assert "descriptive_only_guarantees" in validation["failed_validations"]
    assert descriptive["valid"] is False
    assert descriptive["counters"]["enabled_runtime_execution_count"] > 0
    assert descriptive["counters"]["enabled_trust_authorization_count"] > 0
    assert descriptive["counters"]["enabled_trust_approval_count"] > 0
    assert descriptive["counters"]["enabled_trust_ranking_count"] > 0
    assert descriptive["counters"]["enabled_trust_recommendation_count"] > 0
    assert descriptive["counters"]["enabled_remediation_count"] > 0


def test_v4_5b_1_report_is_replay_safe_and_certifies_public_trust_boundary():
    first = build_v4_5b_1_trust_visibility_foundation_report()
    second = build_v4_5b_1_trust_visibility_foundation_report()
    summary = first["summary"]

    assert first == second
    assert first["foundation_status"] == V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_serialization_verified"] is True
    assert summary["deterministic_hashing_verified"] is True
    assert summary["descriptive_only_guarantees_verified"] is True
    assert summary["public_trust_visibility_statement"] == (
        PUBLIC_TRUST_VISIBILITY_STATEMENT
    )
    assert summary["trust_visibility_non_authority_statement"] == (
        PUBLIC_TRUST_VISIBILITY_NON_AUTHORITY_STATEMENT
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
