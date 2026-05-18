from __future__ import annotations

import json
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from orchestration_governance.v4_4_boundary_continuity_integrity_audit import (  # noqa: E402
    build_v4_4_boundary_continuity_integrity_report,
)
from orchestration_governance.v4_4_boundary_readiness_transition_audit import (  # noqa: E402
    boundary_readiness_transition_capability_counter_values,
    boundary_readiness_transition_equal,
    build_v4_4_boundary_readiness_transition,
    build_v4_4_boundary_readiness_transition_report,
    contaminate_boundary_readiness_transition_for_non_operational_validation,
    enabled_boundary_readiness_transition_capability_flags,
    validate_boundary_readiness_transition,
    validate_boundary_readiness_transition_non_operational,
    validate_readiness_transition_ordering_stability,
    validate_readiness_transition_replay_rollback_evidence,
    validate_readiness_transition_serialization_and_hashing,
    validate_readiness_transition_visibility,
)
from orchestration_governance.v4_4_boundary_readiness_transition_hashing import (  # noqa: E402
    hash_boundary_readiness_transition_certification,
    hash_readiness_certification_identity,
    hash_readiness_replay_rollback_evidence,
    hash_transition_certification_identity,
)
from orchestration_governance.v4_4_boundary_readiness_transition_models import (  # noqa: E402
    BOUNDARY_READINESS_TRANSITION_STATES,
    READINESS_STATE_AMBIGUOUS,
    READINESS_STATE_BLOCKED,
    READINESS_STATE_CERTIFIED,
    READINESS_STATE_COMPLETE,
    READINESS_STATE_CONFLICTING,
    READINESS_STATE_DEGRADED,
    READINESS_STATE_INCOMPLETE,
    READINESS_STATE_NOT_READY,
    READINESS_STATE_PARTIALLY_CERTIFIED,
    READINESS_STATE_PROHIBITED,
    READINESS_STATE_READY_FOR_CLOSEOUT,
    READINESS_STATE_READY_WITH_WARNINGS,
    READINESS_STATE_STALE,
    READINESS_STATE_SUPPORTED,
    READINESS_STATE_TRANSITION_BLOCKED,
    READINESS_STATE_TRANSITION_READY,
    READINESS_STATE_TRANSITION_READY_WITH_WARNINGS,
    READINESS_STATE_UNCERTIFIED,
    READINESS_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_READINESS_TRANSITION_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_READINESS_TRANSITION_SCHEMA_VERSION,
    V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_readiness_transition_serialization import (  # noqa: E402
    serialize_boundary_readiness_transition_certification,
)
from orchestration_governance.v4_4_boundary_readiness_transition_visibility import (  # noqa: E402
    blocker_warning_summaries,
    drift_integrity_preparation_summaries,
    governance_safe_readiness_explainability,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    limitation_summaries,
    lineage_continuity_visibility,
    phase_chain_completeness_summaries,
    provenance_continuity_visibility,
    unresolved_diagnostic_summaries,
    v4_4_readiness_summaries,
    v4_5_transition_summaries,
)


REPORT_PATH = (
    BACKEND_ROOT.parent
    / "docs"
    / "generated"
    / "v4_4_boundary_readiness_transition_report.json"
)


def test_v4_4_readiness_transition_models_are_immutable_and_non_operational():
    certification = build_v4_4_boundary_readiness_transition()

    with pytest.raises(FrozenInstanceError):
        certification.runtime_execution_enabled = True

    assert (
        certification.readiness_identity.schema_version
        == V4_4_BOUNDARY_READINESS_TRANSITION_SCHEMA_VERSION
    )
    assert certification.descriptive_only is True
    assert certification.non_operational is True
    assert certification.non_authoritative is True
    assert certification.non_authorizing is True
    assert certification.non_approving is True
    assert certification.non_activating is True
    assert certification.non_recommending is True
    assert certification.non_deciding is True
    assert certification.non_remediating is True
    assert certification.non_mutating is True
    assert certification.runtime_readiness_inference_disabled is True
    assert enabled_boundary_readiness_transition_capability_flags(certification) == {}
    assert all(
        value == 0
        for value in boundary_readiness_transition_capability_counter_values(
            certification
        ).values()
    )


def test_v4_4_readiness_transition_visibility_preserves_required_classifications():
    certification = build_v4_4_boundary_readiness_transition()
    visibility = validate_readiness_transition_visibility(certification)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[READINESS_STATE_READY_FOR_CLOSEOUT] == 6
    assert counts[READINESS_STATE_READY_WITH_WARNINGS] == 15
    assert counts[READINESS_STATE_NOT_READY] == 4
    assert counts[READINESS_STATE_TRANSITION_READY] == 7
    assert counts[READINESS_STATE_TRANSITION_READY_WITH_WARNINGS] == 11
    assert counts[READINESS_STATE_TRANSITION_BLOCKED] == 6
    assert counts[READINESS_STATE_COMPLETE] == 18
    assert counts[READINESS_STATE_INCOMPLETE] == 2
    assert counts[READINESS_STATE_CERTIFIED] == 22
    assert counts[READINESS_STATE_PARTIALLY_CERTIFIED] == 14
    assert counts[READINESS_STATE_UNCERTIFIED] == 3
    assert counts[READINESS_STATE_SUPPORTED] == 3
    assert counts[READINESS_STATE_UNSUPPORTED] == 2
    assert counts[READINESS_STATE_PROHIBITED] == 8
    assert counts[READINESS_STATE_STALE] == 2
    assert counts[READINESS_STATE_CONFLICTING] == 2
    assert counts[READINESS_STATE_AMBIGUOUS] == 2
    assert counts[READINESS_STATE_DEGRADED] == 2
    assert counts[READINESS_STATE_BLOCKED] == 5
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []
    assert set(counts) == set(BOUNDARY_READINESS_TRANSITION_STATES)


def test_v4_4_readiness_transition_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_readiness_transition()
    second = build_v4_4_boundary_readiness_transition()
    serialization = validate_readiness_transition_serialization_and_hashing(first)

    assert first == second
    assert boundary_readiness_transition_equal(first, second)
    assert serialize_boundary_readiness_transition_certification(
        first
    ) == serialize_boundary_readiness_transition_certification(second)
    assert hash_boundary_readiness_transition_certification(
        first
    ) == hash_boundary_readiness_transition_certification(second)
    assert serialization["valid"] is True
    assert len(hash_readiness_certification_identity(first.readiness_identity)) == 64
    assert len(hash_transition_certification_identity(first.transition_identity)) == 64
    assert len(hash_readiness_replay_rollback_evidence(first.replay_rollback_record)) == 64


def test_v4_4_readiness_transition_ordering_survives_reordered_collections():
    certification = build_v4_4_boundary_readiness_transition()
    reordered = replace(
        certification,
        phase_evidence_references=tuple(reversed(certification.phase_evidence_references)),
        readiness_records=tuple(reversed(certification.readiness_records)),
        transition_records=tuple(reversed(certification.transition_records)),
        completeness_records=tuple(reversed(certification.completeness_records)),
        diagnostic_records=tuple(reversed(certification.diagnostic_records)),
        limitation_records=tuple(reversed(certification.limitation_records)),
        blocker_warning_records=tuple(reversed(certification.blocker_warning_records)),
        planning_constraint_records=tuple(reversed(certification.planning_constraint_records)),
        drift_integrity_preparation_records=tuple(
            reversed(certification.drift_integrity_preparation_records)
        ),
        non_operational_certifications=tuple(
            reversed(certification.non_operational_certifications)
        ),
        transition_summaries=tuple(reversed(certification.transition_summaries)),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(certification.explicit_prohibitions)),
    )

    assert validate_readiness_transition_ordering_stability(certification)["valid"] is True
    assert serialize_boundary_readiness_transition_certification(
        certification
    ) == serialize_boundary_readiness_transition_certification(reordered)
    assert hash_boundary_readiness_transition_certification(
        certification
    ) == hash_boundary_readiness_transition_certification(reordered)


def test_v4_4_readiness_transition_visibility_helpers_remain_descriptive_only():
    certification = build_v4_4_boundary_readiness_transition()
    readiness = v4_4_readiness_summaries(certification)
    transition = v4_5_transition_summaries(certification)
    completeness = phase_chain_completeness_summaries(certification)
    diagnostics = unresolved_diagnostic_summaries(certification)
    limitations = limitation_summaries(certification)
    blocker_warning = blocker_warning_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    preparation = drift_integrity_preparation_summaries(certification)
    explanation = governance_safe_readiness_explainability(certification)

    assert readiness["v4_4_readiness_certification_count"] == 9
    assert readiness["ready_for_closeout_count"] == 3
    assert readiness["ready_with_warnings_count"] == 5
    assert readiness["not_ready_count"] == 1
    assert readiness["readiness_authorization_enabled_count"] == 0
    assert readiness["runtime_readiness_inferred_count"] == 0
    assert transition["v4_5_transition_certification_count"] == 7
    assert transition["transition_ready_count"] == 2
    assert transition["transition_ready_with_warnings_count"] == 2
    assert transition["transition_blocked_count"] == 3
    assert transition["transition_approval_enabled_count"] == 0
    assert transition["v4_5_activation_enabled_count"] == 0
    assert transition["production_consumption_enabled_count"] == 0
    assert transition["planner_integration_enabled_count"] == 0
    assert completeness["phase_evidence_reference_count"] == 7
    assert completeness["phase_chain_completeness_count"] == 9
    assert completeness["runtime_activation_enabled_count"] == 0
    assert diagnostics["unresolved_diagnostic_count"] == 9
    assert diagnostics["automatic_remediation_enabled_count"] == 0
    assert limitations["limitation_count"] == 7
    assert limitations["inherited_limitation_count"] == 7
    assert blocker_warning["warning_count"] == 4
    assert blocker_warning["blocker_count"] == 3
    assert blocker_warning["approval_enabled_count"] == 0
    assert blocker_warning["activation_enabled_count"] == 0
    assert constraints["inherited_v4_5_constraint_count"] == 8
    assert constraints["inherited_v4_5_prohibition_count"] == 4
    assert constraints["planner_integration_enabled_count"] == 0
    assert constraints["production_consumption_enabled_count"] == 0
    assert preparation["drift_integrity_preparation_count"] == 4
    assert preparation["runtime_activation_enabled_count"] == 0
    assert explanation["descriptive_only"] is True
    assert explanation["non_operational"] is True
    assert explanation["runtime_readiness_inference_disabled"] is True


def test_v4_4_readiness_transition_fail_visible_diagnostics_and_constraints_are_preserved():
    certification = build_v4_4_boundary_readiness_transition()
    diagnostics = unresolved_diagnostic_summaries(certification)
    limitations = limitation_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)

    assert diagnostics["unresolved_diagnostic_count"] == 9
    assert diagnostics["fail_visible_diagnostic_count"] == 9
    assert limitations["fail_visible_limitation_count"] == 7
    assert len(prohibitions) == 4
    assert all(item["is_prohibition"] is True for item in prohibitions)
    assert all(item["v4_5_activation_enabled"] is False for item in prohibitions)


def test_v4_4_readiness_transition_replay_rollback_provenance_and_lineage_are_preserved():
    certification = build_v4_4_boundary_readiness_transition()
    replay = validate_readiness_transition_replay_rollback_evidence(certification)
    validation = validate_boundary_readiness_transition(certification)
    provenance = provenance_continuity_visibility(certification)
    lineage = lineage_continuity_visibility(certification)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 39
    assert replay["replay_safe_evidence_count"] == 39
    assert replay["rollback_safe_evidence_count"] == 39
    assert validation["valid"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_readiness_transition_non_operational_validation_detects_contamination():
    certification = build_v4_4_boundary_readiness_transition()
    contaminated = contaminate_boundary_readiness_transition_for_non_operational_validation(
        certification
    )
    validation = validate_boundary_readiness_transition_non_operational(contaminated)

    assert validate_boundary_readiness_transition_non_operational(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_orchestration_activation_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_scheduling_execution_count"] > 0
    assert validation["counters"]["enabled_recommendation_count"] > 0
    assert validation["counters"]["enabled_decision_count"] > 0
    assert validation["counters"]["enabled_readiness_authorization_count"] > 0
    assert validation["counters"]["enabled_transition_approval_count"] > 0
    assert validation["counters"]["enabled_v4_5_activation_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_readiness_transition_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_readiness_transition_report()
    second = build_v4_4_boundary_readiness_transition_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_READINESS_TRANSITION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["readiness_serialization_verified"] is True
    assert first["summary"]["transition_serialization_verified"] is True
    assert first["summary"]["readiness_hashing_verified"] is True
    assert first["summary"]["transition_hashing_verified"] is True
    assert first["summary"]["phase_evidence_reference_stability_verified"] is True
    assert first["summary"]["phase_chain_completeness_visibility_preserved"] is True
    assert first["summary"]["unresolved_diagnostic_visibility_preserved"] is True
    assert first["summary"]["limitation_visibility_preserved"] is True
    assert first["summary"]["v4_5_inherited_constraint_visibility_preserved"] is True
    assert first["summary"]["v4_5_inherited_prohibition_visibility_preserved"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    assert first["summary"]["authorization_behavior_enabled"] is False
    assert first["summary"]["approval_behavior_enabled"] is False
    assert first["summary"]["activation_behavior_enabled"] is False
    assert first["summary"]["recommendation_behavior_enabled"] is False
    assert first["summary"]["decision_behavior_enabled"] is False
    assert first["summary"]["runtime_readiness_inferred"] is False
    for counter_name in V4_4_BOUNDARY_READINESS_TRANSITION_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False


def test_v4_4_readiness_transition_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_readiness_transition_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 4
    assert generated["summary"]["remaining_blocker_count"] == 3


def test_v4_4_phase_7_continuity_integrity_regression_remains_non_operational():
    report = build_v4_4_boundary_continuity_integrity_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_scheduling_execution_count"] == 0
    assert report["summary"]["enabled_recommendation_count"] == 0
    assert report["summary"]["enabled_decision_count"] == 0
    assert report["summary"]["planner_integration_enabled"] is False
    assert report["summary"]["production_consumption_enabled"] is False
    assert report["summary"]["runtime_mutation_enabled"] is False
    assert report["summary"]["non_operational_certification_verified"] is True
