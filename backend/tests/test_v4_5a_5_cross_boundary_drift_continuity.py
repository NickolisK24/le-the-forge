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

from orchestration_governance.v4_5a_5_cross_boundary_drift_continuity_audit import (  # noqa: E402
    build_v4_5a_5_cross_boundary_drift_continuity,
    build_v4_5a_5_cross_boundary_drift_continuity_report,
    contaminate_v4_5a_5_cross_boundary_drift_continuity_for_non_operational_validation,
    cross_boundary_continuity_capability_counter_values,
    cross_boundary_drift_continuity_equal,
    enabled_cross_boundary_continuity_capability_flags,
    validate_boundary_to_boundary_continuity_preservation,
    validate_cross_boundary_continuity_identity_integrity,
    validate_cross_boundary_evidence_continuity,
    validate_cross_boundary_ordering_stability,
    validate_cross_boundary_serialization_and_hashing,
    validate_degradation_continuity_preservation,
    validate_descriptive_only_cross_boundary_guarantees,
    validate_drift_continuity_preservation,
    validate_explanation_continuity_preservation,
    validate_fail_visible_unsupported_cross_boundary_visibility,
    validate_lineage_and_provenance_preservation,
    validate_propagation_continuity_preservation,
    validate_v4_5a_5_cross_boundary_drift_continuity,
)
from orchestration_governance.v4_5a_5_cross_boundary_drift_continuity_hashing import (  # noqa: E402
    hash_boundary_pair_continuity_record,
    hash_cross_boundary_continuity_diagnostic,
    hash_cross_boundary_continuity_identity,
    hash_cross_boundary_continuity_record,
    hash_cross_boundary_evidence_continuity,
    hash_drift_continuity_preservation,
    hash_v4_5a_5_cross_boundary_drift_continuity,
)
from orchestration_governance.v4_5a_5_cross_boundary_drift_continuity_models import (  # noqa: E402
    BOUNDARY_CONTINUITY_TYPES,
    CROSS_BOUNDARY_DIAGNOSTIC_TYPES,
    CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES,
    DEGRADATION_CONTINUITY_PRESERVATION_TYPES,
    DRIFT_CONTINUITY_PRESERVATION_TYPES,
    EXPLANATION_CONTINUITY_PRESERVATION_TYPES,
    PROPAGATION_CONTINUITY_PRESERVATION_TYPES,
    UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_SCHEMA_VERSION,
    V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_STABLE,
)
from orchestration_governance.v4_5a_5_cross_boundary_drift_continuity_serialization import (  # noqa: E402
    serialize_v4_5a_5_cross_boundary_drift_continuity,
)
from orchestration_governance.v4_5a_5_cross_boundary_drift_continuity_visibility import (  # noqa: E402
    boundary_pair_summary_visibility,
    cross_boundary_continuity_summary_visibility,
    degradation_continuity_summary_visibility,
    descriptive_only_cross_boundary_continuity_summary,
    drift_continuity_summary_visibility,
    evidence_continuity_summary_visibility,
    explanation_continuity_summary_visibility,
    fail_visible_cross_boundary_diagnostic_summaries,
    propagation_continuity_summary_visibility,
    unsupported_cross_boundary_visibility_summaries,
    validate_required_cross_boundary_continuity_visibility,
)


def test_v4_5a_5_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert (
        intelligence.continuity_identity.schema_version
        == V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_SCHEMA_VERSION
    )
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.non_routing is True
    assert intelligence.non_traversing is True
    assert intelligence.non_restoring is True
    assert intelligence.boundary_traversal_enabled is False
    assert intelligence.continuity_restoration_enabled is False
    assert intelligence.planner_integration_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert enabled_cross_boundary_continuity_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in cross_boundary_continuity_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5a_5_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()
    visibility = validate_required_cross_boundary_continuity_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["boundary_counts"]) == set(BOUNDARY_CONTINUITY_TYPES)
    assert set(visibility["boundary_pair_counts"]) == set(BOUNDARY_CONTINUITY_TYPES)
    assert set(visibility["drift_counts"]) == set(DRIFT_CONTINUITY_PRESERVATION_TYPES)
    assert set(visibility["propagation_counts"]) == set(
        PROPAGATION_CONTINUITY_PRESERVATION_TYPES
    )
    assert set(visibility["degradation_counts"]) == set(
        DEGRADATION_CONTINUITY_PRESERVATION_TYPES
    )
    assert set(visibility["explanation_counts"]) == set(
        EXPLANATION_CONTINUITY_PRESERVATION_TYPES
    )
    assert set(visibility["evidence_counts"]) == set(
        CROSS_BOUNDARY_EVIDENCE_CONTINUITY_TYPES
    )
    assert set(visibility["diagnostic_counts"]) == set(CROSS_BOUNDARY_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_CROSS_BOUNDARY_OPERATIONAL_STATES
    )
    assert visibility["missing_boundary_types"] == []
    assert visibility["missing_boundary_pair_types"] == []
    assert visibility["missing_drift_types"] == []
    assert visibility["missing_propagation_types"] == []
    assert visibility["missing_degradation_types"] == []
    assert visibility["missing_explanation_types"] == []
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_5_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_5_cross_boundary_drift_continuity()
    second = build_v4_5a_5_cross_boundary_drift_continuity()
    serialization = validate_cross_boundary_serialization_and_hashing(first)

    assert first == second
    assert cross_boundary_drift_continuity_equal(first, second)
    assert serialize_v4_5a_5_cross_boundary_drift_continuity(first) == (
        serialize_v4_5a_5_cross_boundary_drift_continuity(second)
    )
    assert hash_v4_5a_5_cross_boundary_drift_continuity(first) == (
        hash_v4_5a_5_cross_boundary_drift_continuity(second)
    )
    assert serialization["valid"] is True
    assert len(hash_cross_boundary_continuity_identity(first.continuity_identity)) == 64
    assert len(hash_cross_boundary_continuity_record(first.cross_boundary_continuity[0])) == 64
    assert len(hash_boundary_pair_continuity_record(first.boundary_pair_continuity[0])) == 64
    assert len(hash_drift_continuity_preservation(first.drift_continuity[0])) == 64
    assert len(hash_cross_boundary_evidence_continuity(first.evidence_continuity[0])) == 64
    assert len(hash_cross_boundary_continuity_diagnostic(first.diagnostics[0])) == 64


def test_v4_5a_5_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()
    reordered = replace(
        intelligence,
        cross_boundary_continuity=tuple(reversed(intelligence.cross_boundary_continuity)),
        boundary_pair_continuity=tuple(reversed(intelligence.boundary_pair_continuity)),
        drift_continuity=tuple(reversed(intelligence.drift_continuity)),
        propagation_continuity=tuple(reversed(intelligence.propagation_continuity)),
        degradation_continuity=tuple(reversed(intelligence.degradation_continuity)),
        explanation_continuity=tuple(reversed(intelligence.explanation_continuity)),
        evidence_continuity=tuple(reversed(intelligence.evidence_continuity)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        unsupported_cross_boundary_visibility=tuple(
            reversed(intelligence.unsupported_cross_boundary_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_cross_boundary_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_5_cross_boundary_drift_continuity(
        intelligence
    ) == serialize_v4_5a_5_cross_boundary_drift_continuity(reordered)
    assert hash_v4_5a_5_cross_boundary_drift_continuity(
        intelligence
    ) == hash_v4_5a_5_cross_boundary_drift_continuity(reordered)


def test_v4_5a_5_continuity_lineage_provenance_and_evidence_are_preserved():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()

    assert validate_cross_boundary_continuity_identity_integrity(intelligence)["valid"] is True
    assert validate_boundary_to_boundary_continuity_preservation(intelligence)["valid"] is True
    assert validate_drift_continuity_preservation(intelligence)["valid"] is True
    assert validate_propagation_continuity_preservation(intelligence)["valid"] is True
    assert validate_degradation_continuity_preservation(intelligence)["valid"] is True
    assert validate_explanation_continuity_preservation(intelligence)["valid"] is True

    evidence = validate_cross_boundary_evidence_continuity(intelligence)
    lineage = validate_lineage_and_provenance_preservation(intelligence)
    assert evidence["valid"] is True
    assert evidence["replay_safe_evidence_count"] == len(intelligence.evidence_continuity)
    assert evidence["provenance_safe_evidence_count"] == len(
        intelligence.evidence_continuity
    )
    assert evidence["lineage_safe_evidence_count"] == len(intelligence.evidence_continuity)
    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True


def test_v4_5a_5_fail_visible_unsupported_cross_boundary_is_explicit():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()
    unsupported = validate_fail_visible_unsupported_cross_boundary_visibility(
        intelligence
    )

    assert unsupported["valid"] is True
    assert unsupported["fail_visible"] is True
    assert unsupported["silent_fallback_enabled_count"] == 0
    assert unsupported["routing_enabled_count"] == 0
    assert unsupported["traversal_enabled_count"] == 0
    assert unsupported["continuity_restoration_enabled_count"] == 0
    assert unsupported["remediation_enabled_count"] == 0
    assert unsupported["missing_diagnostic_types"] == []
    assert unsupported["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_cross_boundary_diagnostic_summaries(
            intelligence.diagnostics
        )
    )
    assert all(
        summary["continuity_restoration_enabled"] is False
        for summary in unsupported_cross_boundary_visibility_summaries(
            intelligence.unsupported_cross_boundary_visibility
        )
    )


def test_v4_5a_5_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()

    assert len(cross_boundary_continuity_summary_visibility(intelligence.cross_boundary_continuity)) == 7
    assert len(boundary_pair_summary_visibility(intelligence.boundary_pair_continuity)) == 7
    assert len(drift_continuity_summary_visibility(intelligence.drift_continuity)) == 6
    assert len(propagation_continuity_summary_visibility(intelligence.propagation_continuity)) == 6
    assert len(degradation_continuity_summary_visibility(intelligence.degradation_continuity)) == 6
    assert len(explanation_continuity_summary_visibility(intelligence.explanation_continuity)) == 6
    assert len(evidence_continuity_summary_visibility(intelligence.evidence_continuity)) == 8
    descriptive = descriptive_only_cross_boundary_continuity_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["non_routing"] is True
    assert descriptive["non_traversing"] is True
    assert descriptive["non_restoring"] is True
    assert descriptive["orchestration_routing_enabled"] is False
    assert descriptive["orchestration_traversal_enabled"] is False
    assert descriptive["boundary_traversal_enabled"] is False
    assert descriptive["continuity_restoration_enabled"] is False
    assert descriptive["remediation_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_5_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_5_cross_boundary_drift_continuity()
    contaminated = (
        contaminate_v4_5a_5_cross_boundary_drift_continuity_for_non_operational_validation(
            intelligence
        )
    )

    assert validate_descriptive_only_cross_boundary_guarantees(intelligence)["valid"] is True
    contaminated_validation = validate_descriptive_only_cross_boundary_guarantees(
        contaminated
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_orchestration_routing_count"] > 0
    assert contaminated_validation["counters"]["enabled_boundary_traversal_count"] > 0
    assert contaminated_validation["counters"]["enabled_continuity_restoration_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert enabled_cross_boundary_continuity_capability_flags(contaminated) != {}


def test_v4_5a_5_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_5_cross_boundary_drift_continuity_report()
    second_report = build_v4_5a_5_cross_boundary_drift_continuity_report()
    validation = validate_v4_5a_5_cross_boundary_drift_continuity(
        build_v4_5a_5_cross_boundary_drift_continuity()
    )

    assert first_report == second_report
    assert (
        first_report["foundation_status"]
        == V4_5A_5_CROSS_BOUNDARY_DRIFT_CONTINUITY_STATUS_STABLE
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
    ]
