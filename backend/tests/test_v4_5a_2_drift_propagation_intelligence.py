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

from orchestration_governance.v4_5a_2_drift_propagation_audit import (  # noqa: E402
    build_v4_5a_2_drift_propagation_intelligence,
    build_v4_5a_2_drift_propagation_intelligence_report,
    contaminate_v4_5a_2_drift_propagation_for_non_operational_validation,
    drift_propagation_capability_counter_values,
    drift_propagation_equal,
    enabled_drift_propagation_capability_flags,
    validate_descriptive_only_propagation_guarantees,
    validate_fail_visible_unsupported_propagation_visibility,
    validate_propagation_evidence_continuity,
    validate_propagation_identity_integrity,
    validate_propagation_lineage_continuity,
    validate_propagation_ordering_stability,
    validate_propagation_serialization_and_hashing,
    validate_v4_5a_2_drift_propagation_intelligence,
)
from orchestration_governance.v4_5a_2_drift_propagation_hashing import (  # noqa: E402
    hash_drift_propagation_identity,
    hash_propagation_chain,
    hash_propagation_continuity,
    hash_propagation_diagnostic,
    hash_propagation_evidence_chain,
    hash_propagation_explainability,
    hash_v4_5a_2_drift_propagation_intelligence,
)
from orchestration_governance.v4_5a_2_drift_propagation_models import (  # noqa: E402
    CROSS_BOUNDARY_PROPAGATION_TYPES,
    PROPAGATION_ACCUMULATION_TYPES,
    PROPAGATION_CHAIN_TYPES,
    PROPAGATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EVIDENCE_TYPES,
    PROPAGATION_EXPLAINABILITY_TYPES,
    UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES,
    V4_5A_2_DRIFT_PROPAGATION_SCHEMA_VERSION,
    V4_5A_2_DRIFT_PROPAGATION_STATUS_STABLE,
)
from orchestration_governance.v4_5a_2_drift_propagation_serialization import (  # noqa: E402
    serialize_v4_5a_2_drift_propagation_intelligence,
)
from orchestration_governance.v4_5a_2_drift_propagation_visibility import (  # noqa: E402
    cross_boundary_propagation_summary_visibility,
    descriptive_only_propagation_summary,
    fail_visible_propagation_diagnostic_summaries,
    propagation_continuity_summary_visibility,
    propagation_evidence_summary_visibility,
    propagation_explainability_summary_visibility,
    propagation_severity_summary_visibility,
    propagation_summary_visibility,
    unsupported_propagation_visibility_summaries,
    validate_required_propagation_visibility,
)


def test_v4_5a_2_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.propagation_identity.schema_version == V4_5A_2_DRIFT_PROPAGATION_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.planner_integration_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert intelligence.propagation_suppression_enabled is False
    assert enabled_drift_propagation_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in drift_propagation_capability_counter_values(intelligence).values()
    )


def test_v4_5a_2_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    visibility = validate_required_propagation_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["propagation_counts"]) == set(PROPAGATION_CHAIN_TYPES)
    assert set(visibility["accumulation_counts"]) == set(PROPAGATION_ACCUMULATION_TYPES)
    assert set(visibility["evidence_counts"]) == set(PROPAGATION_EVIDENCE_TYPES)
    assert set(visibility["explainability_counts"]) == set(PROPAGATION_EXPLAINABILITY_TYPES)
    assert set(visibility["cross_boundary_counts"]) == set(CROSS_BOUNDARY_PROPAGATION_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(PROPAGATION_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_PROPAGATION_OPERATIONAL_STATES
    )
    assert visibility["missing_propagation_types"] == []
    assert visibility["missing_accumulation_types"] == []
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_explainability_types"] == []
    assert visibility["missing_cross_boundary_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_2_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_2_drift_propagation_intelligence()
    second = build_v4_5a_2_drift_propagation_intelligence()
    serialization = validate_propagation_serialization_and_hashing(first)

    assert first == second
    assert drift_propagation_equal(first, second)
    assert serialize_v4_5a_2_drift_propagation_intelligence(first) == serialize_v4_5a_2_drift_propagation_intelligence(second)
    assert hash_v4_5a_2_drift_propagation_intelligence(first) == hash_v4_5a_2_drift_propagation_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_drift_propagation_identity(first.propagation_identity)) == 64
    assert len(hash_propagation_chain(first.propagation_chains[0])) == 64
    assert len(hash_propagation_evidence_chain(first.evidence_chains[0])) == 64
    assert len(hash_propagation_continuity(first.continuity_records[0])) == 64
    assert len(hash_propagation_explainability(first.explainability_visibility[0])) == 64
    assert len(hash_propagation_diagnostic(first.diagnostics[0])) == 64


def test_v4_5a_2_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    reordered = replace(
        intelligence,
        propagation_chains=tuple(reversed(intelligence.propagation_chains)),
        classifications=tuple(reversed(intelligence.classifications)),
        evidence_chains=tuple(reversed(intelligence.evidence_chains)),
        continuity_records=tuple(reversed(intelligence.continuity_records)),
        severity_accumulation=tuple(reversed(intelligence.severity_accumulation)),
        explainability_visibility=tuple(reversed(intelligence.explainability_visibility)),
        cross_boundary_visibility=tuple(reversed(intelligence.cross_boundary_visibility)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        unsupported_propagation_visibility=tuple(
            reversed(intelligence.unsupported_propagation_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_propagation_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_2_drift_propagation_intelligence(
        intelligence
    ) == serialize_v4_5a_2_drift_propagation_intelligence(reordered)
    assert hash_v4_5a_2_drift_propagation_intelligence(
        intelligence
    ) == hash_v4_5a_2_drift_propagation_intelligence(reordered)


def test_v4_5a_2_identity_lineage_provenance_and_evidence_are_preserved():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    identity = validate_propagation_identity_integrity(intelligence)
    lineage = validate_propagation_lineage_continuity(intelligence)
    evidence = validate_propagation_evidence_continuity(intelligence)

    assert identity["valid"] is True
    assert identity["propagation_chain_count"] == 8
    assert lineage["valid"] is True
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["provenance_continuity_preserved"] is True
    assert evidence["valid"] is True
    assert evidence["replay_safe_evidence_count"] == len(intelligence.evidence_chains)
    assert evidence["provenance_safe_evidence_count"] == len(intelligence.evidence_chains)


def test_v4_5a_2_fail_visible_unsupported_propagation_is_explicit():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    unsupported = validate_fail_visible_unsupported_propagation_visibility(intelligence)

    assert unsupported["valid"] is True
    assert unsupported["fail_visible"] is True
    assert unsupported["silent_suppression_enabled_count"] == 0
    assert unsupported["remediation_enabled_count"] == 0
    assert unsupported["missing_diagnostic_types"] == []
    assert unsupported["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_propagation_diagnostic_summaries(
            intelligence.diagnostics
        )
    )
    assert all(
        summary["propagation_suppression_enabled"] is False
        for summary in unsupported_propagation_visibility_summaries(
            intelligence.unsupported_propagation_visibility
        )
    )


def test_v4_5a_2_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()

    assert len(propagation_summary_visibility(intelligence)) == 8
    assert len(propagation_evidence_summary_visibility(intelligence.evidence_chains)) == 9
    assert len(propagation_continuity_summary_visibility(intelligence.continuity_records)) == 8
    assert len(propagation_severity_summary_visibility(intelligence.severity_accumulation)) == 6
    assert len(propagation_explainability_summary_visibility(intelligence.explainability_visibility)) == 7
    assert len(cross_boundary_propagation_summary_visibility(intelligence.cross_boundary_visibility)) == 5
    descriptive = descriptive_only_propagation_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["remediation_enabled"] is False
    assert descriptive["propagation_suppression_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_2_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_2_drift_propagation_intelligence()
    contaminated = contaminate_v4_5a_2_drift_propagation_for_non_operational_validation(
        intelligence
    )

    assert validate_descriptive_only_propagation_guarantees(intelligence)["valid"] is True
    contaminated_validation = validate_descriptive_only_propagation_guarantees(contaminated)
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_propagation_suppression_count"] > 0
    assert enabled_drift_propagation_capability_flags(contaminated) != {}


def test_v4_5a_2_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_2_drift_propagation_intelligence_report()
    second_report = build_v4_5a_2_drift_propagation_intelligence_report()
    validation = validate_v4_5a_2_drift_propagation_intelligence(
        build_v4_5a_2_drift_propagation_intelligence()
    )

    assert first_report == second_report
    assert first_report["foundation_status"] == V4_5A_2_DRIFT_PROPAGATION_STATUS_STABLE
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
