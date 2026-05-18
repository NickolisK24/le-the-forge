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

from orchestration_governance.v4_4_boundary_segmentation_scope_audit import (  # noqa: E402
    boundary_segmentation_scope_equal,
    build_v4_4_boundary_segmentation_scope,
    build_v4_4_boundary_segmentation_scope_report,
    contaminate_segmentation_scope_for_non_operational_validation,
    enabled_segmentation_scope_capability_flags,
    segmentation_scope_capability_counter_values,
    validate_boundary_segmentation_scope,
    validate_segmentation_scope_non_operational,
    validate_segmentation_scope_ordering_stability,
    validate_segmentation_scope_replay_rollback_evidence,
    validate_segmentation_scope_serialization_and_hashing,
    validate_segmentation_scope_visibility,
)
from orchestration_governance.v4_4_boundary_segmentation_scope_hashing import (  # noqa: E402
    hash_boundary_segmentation_scope_identity,
    hash_boundary_segmentation_scope_intelligence,
    hash_segmentation_scope_evidence_metadata,
)
from orchestration_governance.v4_4_boundary_segmentation_scope_models import (  # noqa: E402
    SEGMENTATION_SCOPE_STATE_AMBIGUOUS,
    SEGMENTATION_SCOPE_STATE_BLOCKED,
    SEGMENTATION_SCOPE_STATE_CONFLICTING,
    SEGMENTATION_SCOPE_STATE_CONSISTENT,
    SEGMENTATION_SCOPE_STATE_COUPLED,
    SEGMENTATION_SCOPE_STATE_DEGRADED,
    SEGMENTATION_SCOPE_STATE_INCONSISTENT,
    SEGMENTATION_SCOPE_STATE_ISOLATED,
    SEGMENTATION_SCOPE_STATE_OVERLAPPING,
    SEGMENTATION_SCOPE_STATE_PROHIBITED,
    SEGMENTATION_SCOPE_STATE_SCOPED,
    SEGMENTATION_SCOPE_STATE_SEGMENTED,
    SEGMENTATION_SCOPE_STATE_STALE,
    SEGMENTATION_SCOPE_STATE_UNSCOPED,
    SEGMENTATION_SCOPE_STATE_UNSEGMENTED,
    SEGMENTATION_SCOPE_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_SCHEMA_VERSION,
    V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_segmentation_scope_serialization import (  # noqa: E402
    serialize_boundary_segmentation_scope_intelligence,
)
from orchestration_governance.v4_4_boundary_segmentation_scope_visibility import (  # noqa: E402
    aggregate_scope_diagnostics,
    aggregate_segmentation_diagnostics,
    degraded_scope_visibility,
    fail_visible_segmentation_summaries,
    governance_safe_segmentation_explainability,
    isolation_coupling_visibility,
    overlap_visibility,
    scope_lineage_visibility,
    scope_provenance_visibility,
    scope_summaries,
    scoped_boundary_membership_visibility,
    segmentation_summaries,
)
from orchestration_governance.v4_4_cross_boundary_consistency_audit import (  # noqa: E402
    build_v4_4_cross_boundary_consistency_report,
)


REPORT_PATH = BACKEND_ROOT.parent / "docs" / "generated" / "v4_4_boundary_segmentation_scope_report.json"


def test_v4_4_segmentation_scope_models_are_immutable_and_non_operational():
    intelligence = build_v4_4_boundary_segmentation_scope()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.identity.schema_version == V4_4_BOUNDARY_SEGMENTATION_SCOPE_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_authoritative is True
    assert intelligence.non_routing is True
    assert intelligence.non_dispatching is True
    assert intelligence.non_scheduling is True
    assert intelligence.non_remediating is True
    assert intelligence.non_mutating is True
    assert enabled_segmentation_scope_capability_flags(intelligence) == {}
    assert all(value == 0 for value in segmentation_scope_capability_counter_values(intelligence).values())


def test_v4_4_segmentation_scope_visibility_preserves_required_classifications():
    intelligence = build_v4_4_boundary_segmentation_scope()
    visibility = validate_segmentation_scope_visibility(intelligence)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[SEGMENTATION_SCOPE_STATE_SCOPED] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_UNSCOPED] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_SEGMENTED] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_UNSEGMENTED] == 1
    assert counts[SEGMENTATION_SCOPE_STATE_ISOLATED] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_COUPLED] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_OVERLAPPING] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_AMBIGUOUS] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_CONSISTENT] == 3
    assert counts[SEGMENTATION_SCOPE_STATE_INCONSISTENT] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_UNSUPPORTED] == 1
    assert counts[SEGMENTATION_SCOPE_STATE_PROHIBITED] == 1
    assert counts[SEGMENTATION_SCOPE_STATE_BLOCKED] == 1
    assert counts[SEGMENTATION_SCOPE_STATE_STALE] == 2
    assert counts[SEGMENTATION_SCOPE_STATE_CONFLICTING] == 1
    assert counts[SEGMENTATION_SCOPE_STATE_DEGRADED] == 2
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []


def test_v4_4_segmentation_scope_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_segmentation_scope()
    second = build_v4_4_boundary_segmentation_scope()
    serialization = validate_segmentation_scope_serialization_and_hashing(first)

    assert first == second
    assert boundary_segmentation_scope_equal(first, second)
    assert serialize_boundary_segmentation_scope_intelligence(first) == serialize_boundary_segmentation_scope_intelligence(second)
    assert hash_boundary_segmentation_scope_intelligence(first) == hash_boundary_segmentation_scope_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_boundary_segmentation_scope_identity(first.identity)) == 64
    assert len(hash_segmentation_scope_evidence_metadata(first.evidence_metadata)) == 64


def test_v4_4_segmentation_scope_ordering_survives_reordered_collections():
    intelligence = build_v4_4_boundary_segmentation_scope()
    reordered = replace(
        intelligence,
        segmentation_classifications=tuple(reversed(intelligence.segmentation_classifications)),
        scope_classifications=tuple(reversed(intelligence.scope_classifications)),
        segment_records=tuple(reversed(intelligence.segment_records)),
        scope_records=tuple(reversed(intelligence.scope_records)),
        membership_records=tuple(reversed(intelligence.membership_records)),
        relationship_records=tuple(reversed(intelligence.relationship_records)),
        continuity_visibility=tuple(reversed(intelligence.continuity_visibility)),
        scope_diagnostics=tuple(reversed(intelligence.scope_diagnostics)),
        segmentation_diagnostics=tuple(reversed(intelligence.segmentation_diagnostics)),
        explainability=tuple(reversed(intelligence.explainability)),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(intelligence.explicit_prohibitions)),
    )

    assert validate_segmentation_scope_ordering_stability(intelligence)["valid"] is True
    assert serialize_boundary_segmentation_scope_intelligence(intelligence) == serialize_boundary_segmentation_scope_intelligence(reordered)
    assert hash_boundary_segmentation_scope_intelligence(intelligence) == hash_boundary_segmentation_scope_intelligence(reordered)


def test_v4_4_segmentation_scope_visibility_helpers_remain_descriptive_only():
    intelligence = build_v4_4_boundary_segmentation_scope()
    segmentation = segmentation_summaries(intelligence)
    scope = scope_summaries(intelligence)
    membership = scoped_boundary_membership_visibility(intelligence)
    isolation = isolation_coupling_visibility(intelligence)
    overlap = overlap_visibility(intelligence)
    degradation = degraded_scope_visibility(intelligence)
    scope_diagnostics = aggregate_scope_diagnostics(intelligence.scope_diagnostics)
    segmentation_diagnostics = aggregate_segmentation_diagnostics(intelligence.segmentation_diagnostics)
    explainability = governance_safe_segmentation_explainability(intelligence.explainability)

    assert len(segmentation) == 6
    assert len(scope) == 6
    assert membership["membership_count"] == 6
    assert membership["routing_enabled_count"] == 0
    assert membership["dispatch_enabled_count"] == 0
    assert membership["scheduling_enabled_count"] == 0
    assert isolation["relationship_count"] == 6
    assert isolation["isolated_count"] == 1
    assert isolation["coupled_count"] == 1
    assert isolation["overlap_count"] == 1
    assert isolation["routing_enabled_count"] == 0
    assert isolation["dispatch_enabled_count"] == 0
    assert isolation["scheduling_enabled_count"] == 0
    assert len(overlap) == 1
    assert degradation["continuity_count"] == 4
    assert degradation["mutation_enabled_count"] == 0
    assert scope_diagnostics["diagnostic_count"] == 6
    assert scope_diagnostics["scope_based_authorization_enabled_count"] == 0
    assert segmentation_diagnostics["diagnostic_count"] == 12
    assert segmentation_diagnostics["segmentation_based_routing_enabled_count"] == 0
    assert explainability["explainability_count"] == 18
    assert explainability["recommendation_enabled_count"] == 0
    assert explainability["decision_enabled_count"] == 0
    assert explainability["routing_enabled_count"] == 0


def test_v4_4_segmentation_scope_fail_visible_ambiguity_overlap_and_degradation_are_preserved():
    intelligence = build_v4_4_boundary_segmentation_scope()
    fail_visible = fail_visible_segmentation_summaries(intelligence)
    overlap = overlap_visibility(intelligence)
    degradation = degraded_scope_visibility(intelligence)

    assert len(fail_visible) == 8
    assert all(item["fail_visible"] is True for item in fail_visible)
    assert len(overlap) == 1
    assert overlap[0]["fail_visible"] is True
    assert degradation["degraded_count"] == 1
    assert degradation["fail_visible"] is True


def test_v4_4_segmentation_scope_replay_rollback_provenance_and_lineage_are_preserved():
    intelligence = build_v4_4_boundary_segmentation_scope()
    replay = validate_segmentation_scope_replay_rollback_evidence(intelligence)
    validation = validate_boundary_segmentation_scope(intelligence)
    provenance = scope_provenance_visibility(intelligence)
    lineage = scope_lineage_visibility(intelligence)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 24
    assert replay["replay_safe_evidence_count"] == 24
    assert replay["rollback_safe_evidence_count"] == 24
    assert validation["valid"] is True
    assert provenance["provenance_visible"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_visible"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_segmentation_scope_non_operational_validation_detects_contamination():
    intelligence = build_v4_4_boundary_segmentation_scope()
    contaminated = contaminate_segmentation_scope_for_non_operational_validation(intelligence)
    validation = validate_segmentation_scope_non_operational(contaminated)

    assert validate_segmentation_scope_non_operational(intelligence)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_scheduling_execution_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_segmentation_scope_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_segmentation_scope_report()
    second = build_v4_4_boundary_segmentation_scope_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_SEGMENTATION_SCOPE_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["segmentation_serialization_verified"] is True
    assert first["summary"]["scope_serialization_verified"] is True
    assert first["summary"]["segmentation_hashing_verified"] is True
    assert first["summary"]["scope_hashing_verified"] is True
    assert first["summary"]["replay_safe_evidence_verified"] is True
    assert first["summary"]["rollback_safe_evidence_verified"] is True
    assert first["summary"]["segment_membership_visibility_verified"] is True
    assert first["summary"]["scope_ambiguity_visibility_verified"] is True
    assert first["summary"]["overlap_visibility_verified"] is True
    assert first["summary"]["isolation_coupling_visibility_verified"] is True
    assert first["summary"]["provenance_visibility_verified"] is True
    assert first["summary"]["lineage_visibility_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_BOUNDARY_SEGMENTATION_SCOPE_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_segmentation_scope_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_segmentation_scope_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_4_cross_boundary_consistency_regression_remains_non_operational():
    report = build_v4_4_cross_boundary_consistency_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_operational_mutation_count"] == 0
    assert report["summary"]["planner_integration_enabled"] is False
    assert report["summary"]["production_consumption_enabled"] is False
    assert report["summary"]["runtime_mutation_enabled"] is False
    assert report["summary"]["non_operational_certification_verified"] is True
