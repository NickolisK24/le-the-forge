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
    build_v4_4_boundary_blocker_resolution_report,
)
from orchestration_governance.v4_4_closeout_readiness_audit import (  # noqa: E402
    build_v4_4_closeout_readiness,
    build_v4_4_closeout_readiness_report,
    closeout_readiness_capability_counter_values,
    closeout_readiness_equal,
    contaminate_v4_4_closeout_readiness_for_non_operational_validation,
    enabled_closeout_readiness_capability_flags,
    validate_closeout_readiness_non_operational,
    validate_closeout_readiness_ordering_stability,
    validate_closeout_readiness_provenance_lineage,
    validate_closeout_readiness_replay_rollback_evidence,
    validate_closeout_readiness_serialization_and_hashing,
    validate_closeout_readiness_visibility,
    validate_v4_4_closeout_readiness,
)
from orchestration_governance.v4_4_closeout_readiness_hashing import (  # noqa: E402
    hash_closeout_identity,
    hash_closeout_readiness_replay_rollback,
    hash_readiness_identity,
    hash_v4_4_closeout_readiness_certification,
)
from orchestration_governance.v4_4_closeout_readiness_models import (  # noqa: E402
    BOUNDARY_CLOSEOUT_READINESS_STATES,
    CLOSEOUT_STATE_AMBIGUOUS,
    CLOSEOUT_STATE_BLOCKED,
    CLOSEOUT_STATE_CERTIFIED,
    CLOSEOUT_STATE_CLOSED_OUT,
    CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS,
    CLOSEOUT_STATE_CLOSED_OUT_WITH_WARNINGS,
    CLOSEOUT_STATE_CLOSEOUT_BLOCKED,
    CLOSEOUT_STATE_CONFLICTING,
    CLOSEOUT_STATE_DEGRADED,
    CLOSEOUT_STATE_INFORMATIONAL,
    CLOSEOUT_STATE_INHERITED,
    CLOSEOUT_STATE_PARTIALLY_CERTIFIED,
    CLOSEOUT_STATE_PRESERVED,
    CLOSEOUT_STATE_PROHIBITED,
    CLOSEOUT_STATE_RESOLVED,
    CLOSEOUT_STATE_STALE,
    CLOSEOUT_STATE_UNCERTIFIED,
    CLOSEOUT_STATE_UNSUPPORTED,
    CLOSEOUT_STATE_V4_5_PLANNING_BLOCKED,
    CLOSEOUT_STATE_V4_5_PLANNING_READY,
    CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS,
    CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_WARNINGS,
    CLOSEOUT_STATE_WARNING,
    V4_4_CLOSEOUT_READINESS_DISABLED_COUNTER_NAMES,
    V4_4_CLOSEOUT_READINESS_SCHEMA_VERSION,
    V4_4_CLOSEOUT_READINESS_STATUS_STABLE,
)
from orchestration_governance.v4_4_closeout_readiness_serialization import (  # noqa: E402
    serialize_v4_4_closeout_readiness_certification,
)
from orchestration_governance.v4_4_closeout_readiness_visibility import (  # noqa: E402
    closeout_readiness_summary_visibility,
    governance_safe_closeout_explainability,
    inherited_constraint_summaries,
    inherited_prohibition_summaries,
    lineage_continuity_visibility,
    phase_chain_evidence_summaries,
    preserved_blocker_summaries,
    preserved_limitation_summaries,
    preserved_warning_summaries,
    provenance_continuity_visibility,
    v4_4_closeout_summaries,
    v4_5_inherited_limitation_summaries,
    v4_5_planning_boundary_summaries,
    v4_5_readiness_summaries,
)


REPORT_PATH = (
    BACKEND_ROOT.parent
    / "docs"
    / "generated"
    / "v4_4_closeout_and_v4_5_readiness_report.json"
)


def test_v4_4_closeout_readiness_models_are_immutable_and_non_operational():
    certification = build_v4_4_closeout_readiness()

    with pytest.raises(FrozenInstanceError):
        certification.runtime_execution_enabled = True

    assert certification.closeout_identity.schema_version == V4_4_CLOSEOUT_READINESS_SCHEMA_VERSION
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
    assert enabled_closeout_readiness_capability_flags(certification) == {}
    assert all(
        value == 0
        for value in closeout_readiness_capability_counter_values(certification).values()
    )


def test_v4_4_closeout_readiness_visibility_preserves_required_classifications():
    certification = build_v4_4_closeout_readiness()
    visibility = validate_closeout_readiness_visibility(certification)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[CLOSEOUT_STATE_CLOSED_OUT] == 2
    assert counts[CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS] == 4
    assert counts[CLOSEOUT_STATE_CLOSED_OUT_WITH_WARNINGS] == 1
    assert counts[CLOSEOUT_STATE_CLOSEOUT_BLOCKED] == 2
    assert counts[CLOSEOUT_STATE_V4_5_PLANNING_READY] == 2
    assert counts[CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS] == 5
    assert counts[CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_WARNINGS] == 1
    assert counts[CLOSEOUT_STATE_V4_5_PLANNING_BLOCKED] == 3
    assert counts[CLOSEOUT_STATE_CERTIFIED] == 47
    assert counts[CLOSEOUT_STATE_PARTIALLY_CERTIFIED] == 7
    assert counts[CLOSEOUT_STATE_UNCERTIFIED] == 4
    assert counts[CLOSEOUT_STATE_PRESERVED] == 20
    assert counts[CLOSEOUT_STATE_INHERITED] == 6
    assert counts[CLOSEOUT_STATE_RESOLVED] == 3
    assert counts[CLOSEOUT_STATE_UNSUPPORTED] == 1
    assert counts[CLOSEOUT_STATE_PROHIBITED] == 9
    assert counts[CLOSEOUT_STATE_BLOCKED] == 5
    assert counts[CLOSEOUT_STATE_STALE] == 1
    assert counts[CLOSEOUT_STATE_CONFLICTING] == 1
    assert counts[CLOSEOUT_STATE_AMBIGUOUS] == 2
    assert counts[CLOSEOUT_STATE_DEGRADED] == 1
    assert counts[CLOSEOUT_STATE_WARNING] == 5
    assert counts[CLOSEOUT_STATE_INFORMATIONAL] == 3
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []
    assert set(counts) == set(BOUNDARY_CLOSEOUT_READINESS_STATES)


def test_v4_4_closeout_readiness_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_closeout_readiness()
    second = build_v4_4_closeout_readiness()
    serialization = validate_closeout_readiness_serialization_and_hashing(first)

    assert first == second
    assert closeout_readiness_equal(first, second)
    assert serialize_v4_4_closeout_readiness_certification(
        first
    ) == serialize_v4_4_closeout_readiness_certification(second)
    assert hash_v4_4_closeout_readiness_certification(
        first
    ) == hash_v4_4_closeout_readiness_certification(second)
    assert serialization["valid"] is True
    assert len(hash_closeout_identity(first.closeout_identity)) == 64
    assert len(hash_readiness_identity(first.readiness_identity)) == 64
    assert len(hash_closeout_readiness_replay_rollback(first.replay_rollback_record)) == 64


def test_v4_4_closeout_readiness_ordering_survives_reordered_collections():
    certification = build_v4_4_closeout_readiness()
    reordered = replace(
        certification,
        phase_chain_evidence_records=tuple(reversed(certification.phase_chain_evidence_records)),
        closeout_records=tuple(reversed(certification.closeout_records)),
        readiness_records=tuple(reversed(certification.readiness_records)),
        preserved_limitation_records=tuple(reversed(certification.preserved_limitation_records)),
        preserved_blocker_records=tuple(reversed(certification.preserved_blocker_records)),
        preserved_warning_records=tuple(reversed(certification.preserved_warning_records)),
        inherited_prohibition_records=tuple(
            reversed(certification.inherited_prohibition_records)
        ),
        inherited_constraint_records=tuple(reversed(certification.inherited_constraint_records)),
        planning_boundary_records=tuple(reversed(certification.planning_boundary_records)),
        inherited_limitation_records=tuple(reversed(certification.inherited_limitation_records)),
        non_operational_certifications=tuple(
            reversed(certification.non_operational_certifications)
        ),
        closeout_readiness_summaries=tuple(
            reversed(certification.closeout_readiness_summaries)
        ),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(certification.explicit_prohibitions)),
    )

    assert validate_closeout_readiness_ordering_stability(certification)["valid"] is True
    assert serialize_v4_4_closeout_readiness_certification(
        certification
    ) == serialize_v4_4_closeout_readiness_certification(reordered)
    assert hash_v4_4_closeout_readiness_certification(
        certification
    ) == hash_v4_4_closeout_readiness_certification(reordered)


def test_v4_4_closeout_readiness_visibility_helpers_remain_descriptive_only():
    certification = build_v4_4_closeout_readiness()
    phase_chain = phase_chain_evidence_summaries(certification)
    closeout = v4_4_closeout_summaries(certification)
    readiness = v4_5_readiness_summaries(certification)
    limitations = preserved_limitation_summaries(certification)
    blockers = preserved_blocker_summaries(certification)
    warnings = preserved_warning_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    constraints = inherited_constraint_summaries(certification)
    planning_boundary = v4_5_planning_boundary_summaries(certification)
    inherited_limitations = v4_5_inherited_limitation_summaries(certification)
    summary = closeout_readiness_summary_visibility(certification)
    explanation = governance_safe_closeout_explainability(certification)

    assert phase_chain["phase_chain_evidence_reference_count"] == 9
    assert phase_chain["phase_evidence_coverage_count"] == 9
    assert phase_chain["generated_report_coverage_count"] == 9
    assert phase_chain["migration_doc_coverage_count"] == 9
    assert closeout["v4_4_closeout_certification_count"] == 4
    assert closeout["closeout_classification"] == CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS
    assert closeout["closeout_authorization_enabled_count"] == 0
    assert readiness["v4_5_readiness_certification_count"] == 4
    assert readiness["v4_5_readiness_classification"] == (
        CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS
    )
    assert readiness["v4_5_runtime_behavior_enabled_count"] == 0
    assert readiness["planner_integration_enabled_count"] == 0
    assert limitations["preserved_limitation_count"] == 7
    assert limitations["automatic_remediation_enabled_count"] == 0
    assert blockers["preserved_blocker_count"] == 6
    assert blockers["blocker_authorization_enabled_count"] == 0
    assert warnings["preserved_warning_count"] == 5
    assert warnings["warning_suppression_enabled_count"] == 0
    assert prohibitions["inherited_prohibition_count"] == 4
    assert prohibitions["v4_5_runtime_behavior_enabled_count"] == 0
    assert constraints["inherited_constraint_count"] == 8
    assert constraints["planner_integration_enabled_count"] == 0
    assert planning_boundary["planning_boundary_count"] == 2
    assert planning_boundary["v4_5_runtime_behavior_enabled_count"] == 0
    assert inherited_limitations["v4_5_inherited_limitation_count"] == 2
    assert inherited_limitations["readiness_activation_enabled_count"] == 0
    assert summary["summary_count"] == 3
    assert summary["readiness_activation_signal_enabled_count"] == 0
    assert explanation["descriptive_only"] is True
    assert explanation["non_operational"] is True
    assert explanation["runtime_readiness_inference_disabled"] is True


def test_v4_4_closeout_readiness_preserves_fail_visible_evidence():
    certification = build_v4_4_closeout_readiness()
    limitations = preserved_limitation_summaries(certification)
    blockers = preserved_blocker_summaries(certification)
    warnings = preserved_warning_summaries(certification)
    prohibitions = inherited_prohibition_summaries(certification)
    constraints = inherited_constraint_summaries(certification)

    assert limitations["fail_visible_limitation_count"] == 7
    assert blockers["fail_visible_blocker_count"] == 5
    assert warnings["fail_visible_warning_count"] == 4
    assert prohibitions["fail_visible_prohibition_count"] == 4
    assert constraints["inherited_by_v4_5_count"] == 8


def test_v4_4_closeout_readiness_replay_rollback_provenance_and_lineage_are_preserved():
    certification = build_v4_4_closeout_readiness()
    replay = validate_closeout_readiness_replay_rollback_evidence(certification)
    validation = validate_v4_4_closeout_readiness(certification)
    provenance = provenance_continuity_visibility(certification)
    lineage = lineage_continuity_visibility(certification)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 51
    assert replay["replay_safe_evidence_count"] == 51
    assert replay["rollback_safe_evidence_count"] == 51
    assert validation["valid"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_closeout_readiness_non_operational_validation_detects_contamination():
    certification = build_v4_4_closeout_readiness()
    contaminated = contaminate_v4_4_closeout_readiness_for_non_operational_validation(
        certification
    )
    validation = validate_closeout_readiness_non_operational(contaminated)

    assert validate_closeout_readiness_non_operational(certification)["valid"] is True
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
    assert validation["counters"]["enabled_closeout_authorization_count"] > 0
    assert validation["counters"]["enabled_readiness_activation_count"] > 0
    assert validation["counters"]["enabled_v4_5_runtime_behavior_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_closeout_readiness_report_generation_and_hash_are_stable():
    first = build_v4_4_closeout_readiness_report()
    second = build_v4_4_closeout_readiness_report()

    assert first == second
    assert first["foundation_status"] == V4_4_CLOSEOUT_READINESS_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["closeout_serialization_verified"] is True
    assert first["summary"]["readiness_serialization_verified"] is True
    assert first["summary"]["closeout_hashing_verified"] is True
    assert first["summary"]["readiness_hashing_verified"] is True
    assert first["summary"]["phase_chain_evidence_reference_stability_verified"] is True
    assert first["summary"]["preserved_limitation_visibility_preserved"] is True
    assert first["summary"]["preserved_blocker_visibility_preserved"] is True
    assert first["summary"]["preserved_warning_visibility_preserved"] is True
    assert first["summary"]["inherited_prohibition_preserved"] is True
    assert first["summary"]["inherited_constraint_preserved"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    assert first["summary"]["authorization_behavior_enabled"] is False
    assert first["summary"]["approval_behavior_enabled"] is False
    assert first["summary"]["activation_behavior_enabled"] is False
    assert first["summary"]["recommendation_behavior_enabled"] is False
    assert first["summary"]["decision_behavior_enabled"] is False
    assert first["summary"]["v4_5_runtime_behavior_enabled"] is False
    for counter_name in V4_4_CLOSEOUT_READINESS_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False


def test_v4_4_closeout_readiness_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_closeout_readiness_report()

    assert generated == built
    assert generated["summary"]["closeout_classification"] == (
        CLOSEOUT_STATE_CLOSED_OUT_WITH_LIMITATIONS
    )
    assert generated["summary"]["v4_5_readiness_classification"] == (
        CLOSEOUT_STATE_V4_5_PLANNING_READY_WITH_LIMITATIONS
    )
    assert generated["summary"]["remaining_unclassified_warning_count"] == 0
    assert generated["summary"]["remaining_unclassified_blocker_count"] == 0


def test_v4_4_phase_9_blocker_resolution_regression_remains_non_operational():
    report = build_v4_4_boundary_blocker_resolution_report()

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
