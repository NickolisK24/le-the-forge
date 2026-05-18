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

from orchestration_governance.v4_5a_3_integrity_degradation_audit import (  # noqa: E402
    build_v4_5a_3_integrity_degradation_intelligence,
    build_v4_5a_3_integrity_degradation_intelligence_report,
    contaminate_v4_5a_3_integrity_degradation_for_non_operational_validation,
    enabled_integrity_degradation_capability_flags,
    integrity_degradation_capability_counter_values,
    integrity_degradation_equal,
    validate_degradation_continuity_preservation,
    validate_degradation_evidence_continuity,
    validate_degradation_identity_integrity,
    validate_degradation_ordering_stability,
    validate_degradation_serialization_and_hashing,
    validate_descriptive_only_degradation_guarantees,
    validate_fail_visible_unsupported_degradation_visibility,
    validate_v4_5a_3_integrity_degradation_intelligence,
)
from orchestration_governance.v4_5a_3_integrity_degradation_hashing import (  # noqa: E402
    hash_continuity_degradation,
    hash_degradation_evidence_chain,
    hash_degradation_record,
    hash_explainability_degradation,
    hash_integrity_degradation_diagnostic,
    hash_integrity_degradation_identity,
    hash_v4_5a_3_integrity_degradation_intelligence,
)
from orchestration_governance.v4_5a_3_integrity_degradation_models import (  # noqa: E402
    CONTINUITY_DEGRADATION_TYPES,
    CROSS_BOUNDARY_INTEGRITY_TYPES,
    DEGRADATION_CLASSIFICATION_TYPES,
    DEGRADATION_DIAGNOSTIC_TYPES,
    DEGRADATION_EVIDENCE_TYPES,
    DEGRADATION_SEVERITY_TYPES,
    EXPLAINABILITY_DEGRADATION_TYPES,
    UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES,
    V4_5A_3_INTEGRITY_DEGRADATION_SCHEMA_VERSION,
    V4_5A_3_INTEGRITY_DEGRADATION_STATUS_STABLE,
)
from orchestration_governance.v4_5a_3_integrity_degradation_serialization import (  # noqa: E402
    serialize_v4_5a_3_integrity_degradation_intelligence,
)
from orchestration_governance.v4_5a_3_integrity_degradation_visibility import (  # noqa: E402
    continuity_degradation_summary_visibility,
    cross_boundary_integrity_summary_visibility,
    degradation_evidence_summary_visibility,
    degradation_severity_summary_visibility,
    degradation_summary_visibility,
    descriptive_only_degradation_summary,
    explainability_degradation_summary_visibility,
    fail_visible_degradation_diagnostic_summaries,
    unsupported_degradation_visibility_summaries,
    validate_required_degradation_visibility,
)


def test_v4_5a_3_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.degradation_identity.schema_version == V4_5A_3_INTEGRITY_DEGRADATION_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.planner_integration_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert intelligence.degradation_suppression_enabled is False
    assert enabled_integrity_degradation_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in integrity_degradation_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5a_3_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    visibility = validate_required_degradation_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["classification_counts"]) == set(DEGRADATION_CLASSIFICATION_TYPES)
    assert set(visibility["severity_counts"]) == set(DEGRADATION_SEVERITY_TYPES)
    assert set(visibility["evidence_counts"]) == set(DEGRADATION_EVIDENCE_TYPES)
    assert set(visibility["continuity_counts"]) == set(CONTINUITY_DEGRADATION_TYPES)
    assert set(visibility["explainability_counts"]) == set(EXPLAINABILITY_DEGRADATION_TYPES)
    assert set(visibility["cross_boundary_counts"]) == set(CROSS_BOUNDARY_INTEGRITY_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(DEGRADATION_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_DEGRADATION_OPERATIONAL_STATES
    )
    assert visibility["missing_classification_types"] == []
    assert visibility["missing_severity_types"] == []
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_continuity_types"] == []
    assert visibility["missing_explainability_types"] == []
    assert visibility["missing_cross_boundary_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_3_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_3_integrity_degradation_intelligence()
    second = build_v4_5a_3_integrity_degradation_intelligence()
    serialization = validate_degradation_serialization_and_hashing(first)

    assert first == second
    assert integrity_degradation_equal(first, second)
    assert serialize_v4_5a_3_integrity_degradation_intelligence(first) == serialize_v4_5a_3_integrity_degradation_intelligence(second)
    assert hash_v4_5a_3_integrity_degradation_intelligence(first) == hash_v4_5a_3_integrity_degradation_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_integrity_degradation_identity(first.degradation_identity)) == 64
    assert len(hash_degradation_record(first.degradation_records[0])) == 64
    assert len(hash_degradation_evidence_chain(first.evidence_chains[0])) == 64
    assert len(hash_continuity_degradation(first.continuity_degradation[0])) == 64
    assert len(hash_explainability_degradation(first.explainability_degradation[0])) == 64
    assert len(hash_integrity_degradation_diagnostic(first.diagnostics[0])) == 64


def test_v4_5a_3_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    reordered = replace(
        intelligence,
        degradation_records=tuple(reversed(intelligence.degradation_records)),
        classifications=tuple(reversed(intelligence.classifications)),
        evidence_chains=tuple(reversed(intelligence.evidence_chains)),
        continuity_degradation=tuple(reversed(intelligence.continuity_degradation)),
        severity_accumulation=tuple(reversed(intelligence.severity_accumulation)),
        explainability_degradation=tuple(reversed(intelligence.explainability_degradation)),
        cross_boundary_integrity=tuple(reversed(intelligence.cross_boundary_integrity)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        unsupported_degradation_visibility=tuple(
            reversed(intelligence.unsupported_degradation_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_degradation_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_3_integrity_degradation_intelligence(
        intelligence
    ) == serialize_v4_5a_3_integrity_degradation_intelligence(reordered)
    assert hash_v4_5a_3_integrity_degradation_intelligence(
        intelligence
    ) == hash_v4_5a_3_integrity_degradation_intelligence(reordered)


def test_v4_5a_3_identity_continuity_provenance_and_evidence_are_preserved():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    identity = validate_degradation_identity_integrity(intelligence)
    continuity = validate_degradation_continuity_preservation(intelligence)
    evidence = validate_degradation_evidence_continuity(intelligence)

    assert identity["valid"] is True
    assert identity["degradation_record_count"] == 9
    assert continuity["valid"] is True
    assert continuity["lineage_continuity_preserved"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["integrity_continuity_preserved"] is True
    assert evidence["valid"] is True
    assert evidence["replay_safe_evidence_count"] == len(intelligence.evidence_chains)
    assert evidence["provenance_safe_evidence_count"] == len(intelligence.evidence_chains)
    assert evidence["lineage_safe_evidence_count"] == len(intelligence.evidence_chains)


def test_v4_5a_3_fail_visible_unsupported_degradation_is_explicit():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    unsupported = validate_fail_visible_unsupported_degradation_visibility(intelligence)

    assert unsupported["valid"] is True
    assert unsupported["fail_visible"] is True
    assert unsupported["silent_suppression_enabled_count"] == 0
    assert unsupported["remediation_enabled_count"] == 0
    assert unsupported["degradation_suppression_enabled_count"] == 0
    assert unsupported["missing_diagnostic_types"] == []
    assert unsupported["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_degradation_diagnostic_summaries(
            intelligence.diagnostics
        )
    )
    assert all(
        summary["degradation_suppression_enabled"] is False
        for summary in unsupported_degradation_visibility_summaries(
            intelligence.unsupported_degradation_visibility
        )
    )


def test_v4_5a_3_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()

    assert len(degradation_summary_visibility(intelligence)) == 9
    assert len(degradation_evidence_summary_visibility(intelligence.evidence_chains)) == 9
    assert len(continuity_degradation_summary_visibility(intelligence.continuity_degradation)) == 5
    assert len(degradation_severity_summary_visibility(intelligence.severity_accumulation)) == 7
    assert len(explainability_degradation_summary_visibility(intelligence.explainability_degradation)) == 6
    assert len(cross_boundary_integrity_summary_visibility(intelligence.cross_boundary_integrity)) == 6
    descriptive = descriptive_only_degradation_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["remediation_enabled"] is False
    assert descriptive["degradation_suppression_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_3_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_3_integrity_degradation_intelligence()
    contaminated = contaminate_v4_5a_3_integrity_degradation_for_non_operational_validation(
        intelligence
    )

    assert validate_descriptive_only_degradation_guarantees(intelligence)["valid"] is True
    contaminated_validation = validate_descriptive_only_degradation_guarantees(
        contaminated
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_degradation_suppression_count"] > 0
    assert enabled_integrity_degradation_capability_flags(contaminated) != {}


def test_v4_5a_3_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_3_integrity_degradation_intelligence_report()
    second_report = build_v4_5a_3_integrity_degradation_intelligence_report()
    validation = validate_v4_5a_3_integrity_degradation_intelligence(
        build_v4_5a_3_integrity_degradation_intelligence()
    )

    assert first_report == second_report
    assert first_report["foundation_status"] == V4_5A_3_INTEGRITY_DEGRADATION_STATUS_STABLE
    assert first_report["deterministic_report_hash"] == second_report["deterministic_report_hash"]
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
