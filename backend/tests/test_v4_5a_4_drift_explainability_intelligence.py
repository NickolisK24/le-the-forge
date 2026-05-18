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

from orchestration_governance.v4_5a_4_drift_explainability_audit import (  # noqa: E402
    build_v4_5a_4_drift_explainability_intelligence,
    build_v4_5a_4_drift_explainability_intelligence_report,
    contaminate_v4_5a_4_drift_explainability_for_non_operational_validation,
    drift_explainability_capability_counter_values,
    drift_explainability_equal,
    enabled_drift_explainability_capability_flags,
    validate_descriptive_only_explanation_guarantees,
    validate_evidence_to_explanation_continuity,
    validate_explanation_chain_continuity,
    validate_explanation_identity_integrity,
    validate_explanation_ordering_stability,
    validate_explanation_serialization_and_hashing,
    validate_fail_visible_unsupported_explanation_visibility,
    validate_v4_5a_4_drift_explainability_intelligence,
)
from orchestration_governance.v4_5a_4_drift_explainability_hashing import (  # noqa: E402
    hash_drift_cause_visibility,
    hash_drift_explainability_identity,
    hash_evidence_explanation_mapping,
    hash_explanation_diagnostic,
    hash_explanation_record,
    hash_propagation_explanation_chain,
    hash_v4_5a_4_drift_explainability_intelligence,
)
from orchestration_governance.v4_5a_4_drift_explainability_models import (  # noqa: E402
    DEGRADATION_EXPLANATION_TYPES,
    DRIFT_CAUSE_TYPES,
    EVIDENCE_MAPPING_TYPES,
    EXPLANATION_COMPLETENESS_TYPES,
    EXPLANATION_CONFIDENCE_TYPES,
    EXPLANATION_DIAGNOSTIC_TYPES,
    PROPAGATION_EXPLANATION_TYPES,
    UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES,
    V4_5A_4_DRIFT_EXPLAINABILITY_SCHEMA_VERSION,
    V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_STABLE,
)
from orchestration_governance.v4_5a_4_drift_explainability_serialization import (  # noqa: E402
    serialize_v4_5a_4_drift_explainability_intelligence,
)
from orchestration_governance.v4_5a_4_drift_explainability_visibility import (  # noqa: E402
    cause_summary_visibility,
    completeness_summary_visibility,
    confidence_summary_visibility,
    degradation_explanation_summary_visibility,
    descriptive_only_explanation_summary,
    evidence_mapping_summary_visibility,
    explanation_summary_visibility,
    fail_visible_explanation_diagnostic_summaries,
    propagation_explanation_summary_visibility,
    unsupported_explanation_visibility_summaries,
    validate_required_explanation_visibility,
)


def test_v4_5a_4_models_are_immutable_and_descriptive_only():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.explainability_identity.schema_version == V4_5A_4_DRIFT_EXPLAINABILITY_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_runtime_mutating is True
    assert intelligence.non_ranking is True
    assert intelligence.planner_integration_enabled is False
    assert intelligence.production_consumption_enabled is False
    assert intelligence.explanation_action_enabled is False
    assert intelligence.explanation_ranking_enabled is False
    assert enabled_drift_explainability_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in drift_explainability_capability_counter_values(
            intelligence
        ).values()
    )


def test_v4_5a_4_required_visibility_sets_are_complete():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    visibility = validate_required_explanation_visibility(intelligence)

    assert visibility["valid"] is True
    assert set(visibility["cause_counts"]) == set(DRIFT_CAUSE_TYPES)
    assert set(visibility["propagation_counts"]) == set(PROPAGATION_EXPLANATION_TYPES)
    assert set(visibility["degradation_counts"]) == set(DEGRADATION_EXPLANATION_TYPES)
    assert set(visibility["evidence_counts"]) == set(EVIDENCE_MAPPING_TYPES)
    assert set(visibility["completeness_counts"]) == set(EXPLANATION_COMPLETENESS_TYPES)
    assert set(visibility["confidence_counts"]) == set(EXPLANATION_CONFIDENCE_TYPES)
    assert set(visibility["diagnostic_counts"]) == set(EXPLANATION_DIAGNOSTIC_TYPES)
    assert set(visibility["unsupported_state_counts"]) == set(
        UNSUPPORTED_EXPLANATION_OPERATIONAL_STATES
    )
    assert visibility["missing_cause_types"] == []
    assert visibility["missing_propagation_types"] == []
    assert visibility["missing_degradation_types"] == []
    assert visibility["missing_evidence_types"] == []
    assert visibility["missing_completeness_types"] == []
    assert visibility["missing_confidence_types"] == []
    assert visibility["missing_diagnostic_types"] == []
    assert visibility["missing_unsupported_states"] == []


def test_v4_5a_4_serialization_hashing_and_equality_are_stable():
    first = build_v4_5a_4_drift_explainability_intelligence()
    second = build_v4_5a_4_drift_explainability_intelligence()
    serialization = validate_explanation_serialization_and_hashing(first)

    assert first == second
    assert drift_explainability_equal(first, second)
    assert serialize_v4_5a_4_drift_explainability_intelligence(first) == serialize_v4_5a_4_drift_explainability_intelligence(second)
    assert hash_v4_5a_4_drift_explainability_intelligence(first) == hash_v4_5a_4_drift_explainability_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_drift_explainability_identity(first.explainability_identity)) == 64
    assert len(hash_explanation_record(first.explanation_records[0])) == 64
    assert len(hash_drift_cause_visibility(first.cause_visibility[0])) == 64
    assert len(hash_propagation_explanation_chain(first.propagation_explanations[0])) == 64
    assert len(hash_evidence_explanation_mapping(first.evidence_mappings[0])) == 64
    assert len(hash_explanation_diagnostic(first.diagnostics[0])) == 64


def test_v4_5a_4_ordering_survives_reordered_collections():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    reordered = replace(
        intelligence,
        explanation_records=tuple(reversed(intelligence.explanation_records)),
        cause_visibility=tuple(reversed(intelligence.cause_visibility)),
        propagation_explanations=tuple(reversed(intelligence.propagation_explanations)),
        degradation_explanations=tuple(reversed(intelligence.degradation_explanations)),
        evidence_mappings=tuple(reversed(intelligence.evidence_mappings)),
        completeness_visibility=tuple(reversed(intelligence.completeness_visibility)),
        confidence_visibility=tuple(reversed(intelligence.confidence_visibility)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        unsupported_explanation_visibility=tuple(
            reversed(intelligence.unsupported_explanation_visibility)
        ),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(intelligence.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(intelligence.inherited_constraints)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
    )

    assert validate_explanation_ordering_stability(intelligence)["valid"] is True
    assert serialize_v4_5a_4_drift_explainability_intelligence(
        intelligence
    ) == serialize_v4_5a_4_drift_explainability_intelligence(reordered)
    assert hash_v4_5a_4_drift_explainability_intelligence(
        intelligence
    ) == hash_v4_5a_4_drift_explainability_intelligence(reordered)


def test_v4_5a_4_identity_chain_provenance_and_mapping_are_preserved():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    identity = validate_explanation_identity_integrity(intelligence)
    chain = validate_explanation_chain_continuity(intelligence)
    mapping = validate_evidence_to_explanation_continuity(intelligence)

    assert identity["valid"] is True
    assert identity["explanation_record_count"] == 8
    assert chain["valid"] is True
    assert chain["lineage_continuity_preserved"] is True
    assert chain["provenance_continuity_preserved"] is True
    assert mapping["valid"] is True
    assert mapping["replay_safe_mapping_count"] == len(intelligence.evidence_mappings)
    assert mapping["provenance_safe_mapping_count"] == len(intelligence.evidence_mappings)
    assert mapping["lineage_safe_mapping_count"] == len(intelligence.evidence_mappings)


def test_v4_5a_4_fail_visible_unsupported_explanation_is_explicit():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    unsupported = validate_fail_visible_unsupported_explanation_visibility(intelligence)

    assert unsupported["valid"] is True
    assert unsupported["fail_visible"] is True
    assert unsupported["silent_fallback_enabled_count"] == 0
    assert unsupported["remediation_enabled_count"] == 0
    assert unsupported["explanation_action_enabled_count"] == 0
    assert unsupported["missing_diagnostic_types"] == []
    assert unsupported["missing_unsupported_states"] == []
    assert all(
        summary["fail_visible"]
        for summary in fail_visible_explanation_diagnostic_summaries(
            intelligence.diagnostics
        )
    )
    assert all(
        summary["explanation_action_enabled"] is False
        for summary in unsupported_explanation_visibility_summaries(
            intelligence.unsupported_explanation_visibility
        )
    )


def test_v4_5a_4_visibility_helpers_remain_non_operational():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()

    assert len(explanation_summary_visibility(intelligence)) == 8
    assert len(cause_summary_visibility(intelligence.cause_visibility)) == 8
    assert len(propagation_explanation_summary_visibility(intelligence.propagation_explanations)) == 7
    assert len(degradation_explanation_summary_visibility(intelligence.degradation_explanations)) == 7
    assert len(evidence_mapping_summary_visibility(intelligence.evidence_mappings)) == 8
    assert len(completeness_summary_visibility(intelligence.completeness_visibility)) == 6
    assert len(confidence_summary_visibility(intelligence.confidence_visibility)) == 6
    descriptive = descriptive_only_explanation_summary(intelligence)
    assert descriptive["descriptive_only"] is True
    assert descriptive["non_operational"] is True
    assert descriptive["remediation_enabled"] is False
    assert descriptive["explanation_action_enabled"] is False
    assert descriptive["explanation_ranking_enabled"] is False
    assert descriptive["planner_integration_enabled"] is False


def test_v4_5a_4_descriptive_only_guarantees_detect_contamination():
    intelligence = build_v4_5a_4_drift_explainability_intelligence()
    contaminated = contaminate_v4_5a_4_drift_explainability_for_non_operational_validation(
        intelligence
    )

    assert validate_descriptive_only_explanation_guarantees(intelligence)["valid"] is True
    contaminated_validation = validate_descriptive_only_explanation_guarantees(
        contaminated
    )
    assert contaminated_validation["valid"] is False
    assert contaminated_validation["counters"]["enabled_runtime_execution_count"] > 0
    assert contaminated_validation["counters"]["enabled_remediation_count"] > 0
    assert contaminated_validation["counters"]["enabled_explanation_ranking_count"] > 0
    assert enabled_drift_explainability_capability_flags(contaminated) != {}


def test_v4_5a_4_report_generation_is_replay_safe_and_certifies_repository_state():
    first_report = build_v4_5a_4_drift_explainability_intelligence_report()
    second_report = build_v4_5a_4_drift_explainability_intelligence_report()
    validation = validate_v4_5a_4_drift_explainability_intelligence(
        build_v4_5a_4_drift_explainability_intelligence()
    )

    assert first_report == second_report
    assert first_report["foundation_status"] == V4_5A_4_DRIFT_EXPLAINABILITY_STATUS_STABLE
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
