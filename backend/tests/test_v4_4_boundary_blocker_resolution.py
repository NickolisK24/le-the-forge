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

from orchestration_governance.v4_4_boundary_blocker_resolution_audit import (  # noqa: E402
    boundary_blocker_resolution_capability_counter_values,
    boundary_blocker_resolution_equal,
    build_v4_4_boundary_blocker_resolution,
    build_v4_4_boundary_blocker_resolution_report,
    contaminate_boundary_blocker_resolution_for_non_operational_validation,
    enabled_boundary_blocker_resolution_capability_flags,
    validate_blocker_resolution_ordering_stability,
    validate_blocker_resolution_provenance_lineage,
    validate_blocker_resolution_replay_rollback_evidence,
    validate_blocker_resolution_serialization_and_hashing,
    validate_blocker_resolution_visibility,
    validate_boundary_blocker_resolution,
    validate_boundary_blocker_resolution_non_operational,
)
from orchestration_governance.v4_4_boundary_blocker_resolution_hashing import (  # noqa: E402
    hash_blocker_classification_identity,
    hash_blocker_resolution_replay_rollback,
    hash_boundary_blocker_resolution_closeout_preparation,
    hash_warning_classification_identity,
)
from orchestration_governance.v4_4_boundary_blocker_resolution_models import (  # noqa: E402
    BLOCKER_STATE_AMBIGUOUS,
    BLOCKER_STATE_BLOCKED,
    BLOCKER_STATE_CLOSEOUT_BLOCKED,
    BLOCKER_STATE_CLOSEOUT_READY,
    BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS,
    BLOCKER_STATE_CONFLICTING,
    BLOCKER_STATE_DEGRADED,
    BLOCKER_STATE_ESCALATED,
    BLOCKER_STATE_INFORMATIONAL,
    BLOCKER_STATE_INHERITED_CONSTRAINT,
    BLOCKER_STATE_INHERITED_PROHIBITION,
    BLOCKER_STATE_INTENTIONALLY_PRESERVED,
    BLOCKER_STATE_PROHIBITED,
    BLOCKER_STATE_RESOLVED,
    BLOCKER_STATE_STALE,
    BLOCKER_STATE_SUPPORTED,
    BLOCKER_STATE_UNSUPPORTED,
    BLOCKER_STATE_WARNING,
    BOUNDARY_BLOCKER_RESOLUTION_STATES,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_SCHEMA_VERSION,
    V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_blocker_resolution_serialization import (  # noqa: E402
    serialize_boundary_blocker_resolution_closeout_preparation,
)
from orchestration_governance.v4_4_boundary_blocker_resolution_visibility import (  # noqa: E402
    blocker_resolution_summaries,
    closeout_eligibility_summaries,
    escalation_summaries,
    fail_visible_blocker_summaries,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    lineage_continuity_visibility,
    provenance_continuity_visibility,
    unresolved_limitation_summaries,
    v4_5_planning_boundary_summaries,
    warning_classification_summaries,
)
from orchestration_governance.v4_4_boundary_readiness_transition_audit import (  # noqa: E402
    build_v4_4_boundary_readiness_transition_report,
)


REPORT_PATH = (
    BACKEND_ROOT.parent
    / "docs"
    / "generated"
    / "v4_4_boundary_blocker_resolution_report.json"
)


def test_v4_4_blocker_resolution_models_are_immutable_and_non_operational():
    certification = build_v4_4_boundary_blocker_resolution()

    with pytest.raises(FrozenInstanceError):
        certification.runtime_execution_enabled = True

    assert (
        certification.blocker_identity.schema_version
        == V4_4_BOUNDARY_BLOCKER_RESOLUTION_SCHEMA_VERSION
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
    assert enabled_boundary_blocker_resolution_capability_flags(certification) == {}
    assert all(
        value == 0
        for value in boundary_blocker_resolution_capability_counter_values(
            certification
        ).values()
    )


def test_v4_4_blocker_resolution_visibility_preserves_required_classifications():
    certification = build_v4_4_boundary_blocker_resolution()
    visibility = validate_blocker_resolution_visibility(certification)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[BLOCKER_STATE_RESOLVED] == 1
    assert counts[BLOCKER_STATE_INTENTIONALLY_PRESERVED] == 6
    assert counts[BLOCKER_STATE_INHERITED_PROHIBITION] == 11
    assert counts[BLOCKER_STATE_INHERITED_CONSTRAINT] == 8
    assert counts[BLOCKER_STATE_ESCALATED] == 5
    assert counts[BLOCKER_STATE_CLOSEOUT_READY] == 1
    assert counts[BLOCKER_STATE_CLOSEOUT_READY_WITH_LIMITATIONS] == 7
    assert counts[BLOCKER_STATE_CLOSEOUT_BLOCKED] == 5
    assert counts[BLOCKER_STATE_SUPPORTED] == 15
    assert counts[BLOCKER_STATE_UNSUPPORTED] == 1
    assert counts[BLOCKER_STATE_PROHIBITED] == 10
    assert counts[BLOCKER_STATE_BLOCKED] == 7
    assert counts[BLOCKER_STATE_STALE] == 1
    assert counts[BLOCKER_STATE_CONFLICTING] == 1
    assert counts[BLOCKER_STATE_AMBIGUOUS] == 2
    assert counts[BLOCKER_STATE_DEGRADED] == 2
    assert counts[BLOCKER_STATE_WARNING] == 8
    assert counts[BLOCKER_STATE_INFORMATIONAL] == 3
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []
    assert set(counts) == set(BOUNDARY_BLOCKER_RESOLUTION_STATES)


def test_v4_4_blocker_resolution_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_blocker_resolution()
    second = build_v4_4_boundary_blocker_resolution()
    serialization = validate_blocker_resolution_serialization_and_hashing(first)

    assert first == second
    assert boundary_blocker_resolution_equal(first, second)
    assert serialize_boundary_blocker_resolution_closeout_preparation(
        first
    ) == serialize_boundary_blocker_resolution_closeout_preparation(second)
    assert hash_boundary_blocker_resolution_closeout_preparation(
        first
    ) == hash_boundary_blocker_resolution_closeout_preparation(second)
    assert serialization["valid"] is True
    assert len(hash_blocker_classification_identity(first.blocker_identity)) == 64
    assert len(hash_warning_classification_identity(first.warning_identity)) == 64
    assert len(hash_blocker_resolution_replay_rollback(first.replay_rollback_record)) == 64


def test_v4_4_blocker_resolution_ordering_survives_reordered_collections():
    certification = build_v4_4_boundary_blocker_resolution()
    reordered = replace(
        certification,
        phase8_evidence_references=tuple(reversed(certification.phase8_evidence_references)),
        blocker_records=tuple(reversed(certification.blocker_records)),
        warning_records=tuple(reversed(certification.warning_records)),
        inherited_prohibition_records=tuple(
            reversed(certification.inherited_prohibition_records)
        ),
        inherited_constraint_records=tuple(
            reversed(certification.inherited_constraint_records)
        ),
        limitation_records=tuple(reversed(certification.limitation_records)),
        escalation_records=tuple(reversed(certification.escalation_records)),
        closeout_eligibility_records=tuple(
            reversed(certification.closeout_eligibility_records)
        ),
        planning_boundary_records=tuple(reversed(certification.planning_boundary_records)),
        fail_visible_explanations=tuple(reversed(certification.fail_visible_explanations)),
        non_operational_certifications=tuple(
            reversed(certification.non_operational_certifications)
        ),
        closeout_summaries=tuple(reversed(certification.closeout_summaries)),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(certification.explicit_prohibitions)),
    )

    assert validate_blocker_resolution_ordering_stability(certification)["valid"] is True
    assert serialize_boundary_blocker_resolution_closeout_preparation(
        certification
    ) == serialize_boundary_blocker_resolution_closeout_preparation(reordered)
    assert hash_boundary_blocker_resolution_closeout_preparation(
        certification
    ) == hash_boundary_blocker_resolution_closeout_preparation(reordered)


def test_v4_4_blocker_resolution_visibility_helpers_remain_descriptive_only():
    certification = build_v4_4_boundary_blocker_resolution()
    blockers = blocker_resolution_summaries(certification)
    warnings = warning_classification_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    limitations = unresolved_limitation_summaries(certification)
    escalations = escalation_summaries(certification)
    closeout = closeout_eligibility_summaries(certification)
    planning_boundary = v4_5_planning_boundary_summaries(certification)
    fail_visible = fail_visible_blocker_summaries(certification)

    assert blockers["blocker_classification_total"] == 6
    assert blockers["resolved_count"] == 1
    assert blockers["fail_visible_blocker_count"] == 5
    assert blockers["blocker_authorization_enabled_count"] == 0
    assert blockers["blocker_auto_resolution_enabled_count"] == 0
    assert warnings["warning_classification_total"] == 5
    assert warnings["warning_count"] == 4
    assert warnings["informational_count"] == 1
    assert warnings["warning_suppression_enabled_count"] == 0
    assert prohibitions["inherited_prohibition_total"] == 4
    assert prohibitions["is_prohibition_count"] == 4
    assert constraints["inherited_constraint_total"] == 8
    assert constraints["inherited_by_v4_5_count"] == 8
    assert limitations["unresolved_limitation_total"] == 7
    assert limitations["automatic_remediation_enabled_count"] == 0
    assert escalations["escalation_total"] == 4
    assert escalations["non_actioning"] is True
    assert escalations["closeout_activation_enabled_count"] == 0
    assert closeout["closeout_eligibility_total"] == 3
    assert closeout["closeout_ready_count"] == 1
    assert closeout["closeout_ready_with_limitations_count"] == 1
    assert closeout["closeout_blocked_count"] == 1
    assert closeout["runtime_readiness_inferred_count"] == 0
    assert planning_boundary["planning_boundary_total"] == 3
    assert planning_boundary["v4_5_activation_enabled_count"] == 0
    assert planning_boundary["planner_integration_enabled_count"] == 0
    assert planning_boundary["production_consumption_enabled_count"] == 0
    assert fail_visible["fail_visible_explanation_total"] == 5
    assert fail_visible["approval_enabled_count"] == 0
    assert fail_visible["recommendation_enabled_count"] == 0


def test_v4_4_blocker_resolution_fail_visible_evidence_is_preserved():
    certification = build_v4_4_boundary_blocker_resolution()
    blockers = blocker_resolution_summaries(certification)
    warnings = warning_classification_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    limitations = unresolved_limitation_summaries(certification)

    assert blockers["fail_visible_blocker_count"] == 5
    assert warnings["fail_visible_warning_count"] == 4
    assert prohibitions["fail_visible_prohibition_count"] == 4
    assert limitations["fail_visible_limitation_count"] == 7
    assert limitations["inherited_limitation_count"] == 7


def test_v4_4_blocker_resolution_replay_rollback_provenance_and_lineage_are_preserved():
    certification = build_v4_4_boundary_blocker_resolution()
    replay = validate_blocker_resolution_replay_rollback_evidence(certification)
    validation = validate_boundary_blocker_resolution(certification)
    provenance = provenance_continuity_visibility(certification)
    lineage = lineage_continuity_visibility(certification)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 48
    assert replay["replay_safe_evidence_count"] == 48
    assert replay["rollback_safe_evidence_count"] == 48
    assert validation["valid"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_blocker_resolution_non_operational_validation_detects_contamination():
    certification = build_v4_4_boundary_blocker_resolution()
    contaminated = contaminate_boundary_blocker_resolution_for_non_operational_validation(
        certification
    )
    validation = validate_boundary_blocker_resolution_non_operational(contaminated)

    assert validate_boundary_blocker_resolution_non_operational(certification)["valid"] is True
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
    assert validation["counters"]["enabled_blocker_authorization_count"] > 0
    assert validation["counters"]["enabled_closeout_activation_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0
    assert validation["blocker_auto_resolution_disabled"] is False
    assert validation["warning_suppression_disabled"] is False


def test_v4_4_blocker_resolution_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_blocker_resolution_report()
    second = build_v4_4_boundary_blocker_resolution_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_BLOCKER_RESOLUTION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["blocker_serialization_verified"] is True
    assert first["summary"]["warning_serialization_verified"] is True
    assert first["summary"]["escalation_hashing_verified"] is True
    assert first["summary"]["closeout_hashing_verified"] is True
    assert first["summary"]["fail_visible_blocker_preserved"] is True
    assert first["summary"]["inherited_prohibition_preserved"] is True
    assert first["summary"]["inherited_constraint_preserved"] is True
    assert first["summary"]["unresolved_limitation_visibility_preserved"] is True
    assert first["summary"]["escalation_trace_visibility_preserved"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    assert first["summary"]["authorization_behavior_enabled"] is False
    assert first["summary"]["approval_behavior_enabled"] is False
    assert first["summary"]["activation_behavior_enabled"] is False
    assert first["summary"]["recommendation_behavior_enabled"] is False
    assert first["summary"]["decision_behavior_enabled"] is False
    assert first["summary"]["runtime_readiness_inferred"] is False
    for counter_name in V4_4_BOUNDARY_BLOCKER_RESOLUTION_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False


def test_v4_4_blocker_resolution_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_blocker_resolution_report()

    assert generated == built
    assert generated["summary"]["remaining_unclassified_warning_count"] == 0
    assert generated["summary"]["remaining_unclassified_blocker_count"] == 0
    assert generated["summary"]["remaining_fail_visible_warning_count"] == 4
    assert generated["summary"]["remaining_fail_visible_blocker_count"] == 5


def test_v4_4_phase_8_readiness_transition_regression_remains_non_operational():
    report = build_v4_4_boundary_readiness_transition_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["enabled_orchestration_activation_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_scheduling_execution_count"] == 0
    assert report["summary"]["enabled_recommendation_count"] == 0
    assert report["summary"]["enabled_decision_count"] == 0
    assert report["summary"]["planner_integration_enabled"] is False
    assert report["summary"]["production_consumption_enabled"] is False
    assert report["summary"]["runtime_mutation_enabled"] is False
    assert report["summary"]["non_operational_certification_verified"] is True
