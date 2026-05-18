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

from orchestration_governance.v4_4_boundary_explainability_aggregation_audit import (  # noqa: E402
    boundary_explainability_aggregation_equal,
    build_v4_4_boundary_explainability_aggregation,
    build_v4_4_boundary_explainability_aggregation_report,
    contaminate_explainability_aggregation_for_non_operational_validation,
    enabled_explainability_aggregation_capability_flags,
    explainability_aggregation_capability_counter_values,
    validate_boundary_explainability_aggregation,
    validate_explainability_aggregation_non_operational,
    validate_explainability_aggregation_ordering_stability,
    validate_explainability_aggregation_serialization_and_hashing,
    validate_explainability_aggregation_visibility,
    validate_explainability_replay_rollback_evidence,
)
from orchestration_governance.v4_4_boundary_explainability_aggregation_hashing import (  # noqa: E402
    hash_boundary_explainability_aggregation_identity,
    hash_boundary_explainability_aggregation_intelligence,
    hash_replay_rollback_aggregation_summary,
)
from orchestration_governance.v4_4_boundary_explainability_aggregation_models import (  # noqa: E402
    EXPLAINABILITY_STATE_AMBIGUOUS,
    EXPLAINABILITY_STATE_BLOCKED,
    EXPLAINABILITY_STATE_CONFLICTING,
    EXPLAINABILITY_STATE_CONSISTENT,
    EXPLAINABILITY_STATE_DEGRADED,
    EXPLAINABILITY_STATE_DIAGNOSTIC,
    EXPLAINABILITY_STATE_EXPLAINED,
    EXPLAINABILITY_STATE_INFORMATIONAL,
    EXPLAINABILITY_STATE_INCONSISTENT,
    EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED,
    EXPLAINABILITY_STATE_PROHIBITED,
    EXPLAINABILITY_STATE_STALE,
    EXPLAINABILITY_STATE_UNEXPLAINED,
    EXPLAINABILITY_STATE_UNSUPPORTED,
    EXPLAINABILITY_STATE_WARNING,
    V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_SCHEMA_VERSION,
    V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_explainability_aggregation_serialization import (  # noqa: E402
    serialize_boundary_explainability_aggregation_intelligence,
)
from orchestration_governance.v4_4_boundary_explainability_aggregation_visibility import (  # noqa: E402
    diagnostic_aggregation_summaries,
    explainability_coverage_summaries,
    fail_visible_diagnostic_summaries,
    governance_safe_explanation_traces,
    lineage_visibility,
    provenance_visibility,
    source_evidence_coverage_totals,
    unresolved_diagnostic_totals,
)
from orchestration_governance.v4_4_boundary_segmentation_scope_audit import (  # noqa: E402
    build_v4_4_boundary_segmentation_scope_report,
)


REPORT_PATH = (
    BACKEND_ROOT.parent
    / "docs"
    / "generated"
    / "v4_4_boundary_explainability_aggregation_report.json"
)


def test_v4_4_explainability_aggregation_models_are_immutable_and_non_operational():
    intelligence = build_v4_4_boundary_explainability_aggregation()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.identity.schema_version == V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_authoritative is True
    assert intelligence.non_recommending is True
    assert intelligence.non_deciding is True
    assert intelligence.non_remediating is True
    assert intelligence.non_mutating is True
    assert intelligence.runtime_readiness_inference_disabled is True
    assert enabled_explainability_aggregation_capability_flags(intelligence) == {}
    assert all(
        value == 0
        for value in explainability_aggregation_capability_counter_values(intelligence).values()
    )


def test_v4_4_explainability_aggregation_visibility_preserves_required_classifications():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    visibility = validate_explainability_aggregation_visibility(intelligence)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[EXPLAINABILITY_STATE_EXPLAINED] == 3
    assert counts[EXPLAINABILITY_STATE_PARTIALLY_EXPLAINED] == 3
    assert counts[EXPLAINABILITY_STATE_UNEXPLAINED] == 1
    assert counts[EXPLAINABILITY_STATE_DIAGNOSTIC] == 3
    assert counts[EXPLAINABILITY_STATE_INFORMATIONAL] == 2
    assert counts[EXPLAINABILITY_STATE_WARNING] == 2
    assert counts[EXPLAINABILITY_STATE_BLOCKED] == 1
    assert counts[EXPLAINABILITY_STATE_UNSUPPORTED] == 1
    assert counts[EXPLAINABILITY_STATE_PROHIBITED] == 1
    assert counts[EXPLAINABILITY_STATE_STALE] == 1
    assert counts[EXPLAINABILITY_STATE_CONFLICTING] == 2
    assert counts[EXPLAINABILITY_STATE_AMBIGUOUS] == 2
    assert counts[EXPLAINABILITY_STATE_DEGRADED] == 1
    assert counts[EXPLAINABILITY_STATE_CONSISTENT] == 1
    assert counts[EXPLAINABILITY_STATE_INCONSISTENT] == 2
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []


def test_v4_4_explainability_aggregation_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_explainability_aggregation()
    second = build_v4_4_boundary_explainability_aggregation()
    serialization = validate_explainability_aggregation_serialization_and_hashing(first)

    assert first == second
    assert boundary_explainability_aggregation_equal(first, second)
    assert serialize_boundary_explainability_aggregation_intelligence(first) == serialize_boundary_explainability_aggregation_intelligence(second)
    assert hash_boundary_explainability_aggregation_intelligence(first) == hash_boundary_explainability_aggregation_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_boundary_explainability_aggregation_identity(first.identity)) == 64
    assert len(hash_replay_rollback_aggregation_summary(first.replay_rollback_summary)) == 64


def test_v4_4_explainability_aggregation_ordering_survives_reordered_collections():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    reordered = replace(
        intelligence,
        source_evidence_references=tuple(reversed(intelligence.source_evidence_references)),
        phase_evidence_summaries=tuple(reversed(intelligence.phase_evidence_summaries)),
        explainability_records=tuple(reversed(intelligence.explainability_records)),
        diagnostic_records=tuple(reversed(intelligence.diagnostic_records)),
        coverage_summaries=tuple(reversed(intelligence.coverage_summaries)),
        explanation_traces=tuple(reversed(intelligence.explanation_traces)),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(intelligence.explicit_prohibitions)),
    )

    assert validate_explainability_aggregation_ordering_stability(intelligence)["valid"] is True
    assert serialize_boundary_explainability_aggregation_intelligence(intelligence) == serialize_boundary_explainability_aggregation_intelligence(reordered)
    assert hash_boundary_explainability_aggregation_intelligence(intelligence) == hash_boundary_explainability_aggregation_intelligence(reordered)


def test_v4_4_explainability_aggregation_visibility_helpers_remain_descriptive_only():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    source = source_evidence_coverage_totals(intelligence)
    coverage = explainability_coverage_summaries(intelligence)
    diagnostics = diagnostic_aggregation_summaries(intelligence)
    unresolved = unresolved_diagnostic_totals(intelligence)
    traces = governance_safe_explanation_traces(intelligence.explanation_traces)

    assert source["source_evidence_reference_count"] == 5
    assert source["all_sources_available"] is True
    assert source["production_consumption_enabled_count"] == 0
    assert coverage["explainability_record_count"] == 5
    assert coverage["explained_count"] == 2
    assert coverage["partially_explained_count"] == 1
    assert coverage["unexplained_count"] == 1
    assert coverage["recommendation_enabled_count"] == 0
    assert coverage["decision_enabled_count"] == 0
    assert coverage["runtime_readiness_inferred_count"] == 0
    assert diagnostics["diagnostic_record_count"] == 11
    assert diagnostics["unresolved_diagnostic_count"] == 9
    assert diagnostics["fail_visible_diagnostic_count"] == 9
    assert diagnostics["diagnostic_auto_resolution_enabled_count"] == 0
    assert diagnostics["automatic_remediation_enabled_count"] == 0
    assert diagnostics["automatic_repair_enabled_count"] == 0
    assert diagnostics["recommendation_enabled_count"] == 0
    assert diagnostics["decision_enabled_count"] == 0
    assert diagnostics["authorization_enabled_count"] == 0
    assert unresolved["unresolved_diagnostic_count"] == 9
    assert traces["trace_count"] == 5
    assert traces["recommendation_enabled_count"] == 0
    assert traces["decision_enabled_count"] == 0
    assert traces["runtime_readiness_inferred_count"] == 0


def test_v4_4_explainability_aggregation_fail_visible_and_unresolved_diagnostics_are_preserved():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    fail_visible = fail_visible_diagnostic_summaries(intelligence)
    unresolved = unresolved_diagnostic_totals(intelligence)

    assert len(fail_visible) == 9
    assert all(item["fail_visible"] is True for item in fail_visible)
    assert unresolved["unresolved_diagnostic_count"] == 9
    assert unresolved["fail_visible_unresolved_count"] == 9


def test_v4_4_explainability_aggregation_replay_rollback_provenance_and_lineage_are_preserved():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    replay = validate_explainability_replay_rollback_evidence(intelligence)
    validation = validate_boundary_explainability_aggregation(intelligence)
    provenance = provenance_visibility(intelligence)
    lineage = lineage_visibility(intelligence)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 21
    assert replay["replay_safe_evidence_count"] == 21
    assert replay["rollback_safe_evidence_count"] == 21
    assert validation["valid"] is True
    assert provenance["provenance_visible"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_visible"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_explainability_aggregation_non_operational_validation_detects_contamination():
    intelligence = build_v4_4_boundary_explainability_aggregation()
    contaminated = contaminate_explainability_aggregation_for_non_operational_validation(
        intelligence
    )
    validation = validate_explainability_aggregation_non_operational(contaminated)

    assert validate_explainability_aggregation_non_operational(intelligence)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_scheduling_execution_count"] > 0
    assert validation["counters"]["enabled_recommendation_count"] > 0
    assert validation["counters"]["enabled_decision_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_explainability_aggregation_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_explainability_aggregation_report()
    second = build_v4_4_boundary_explainability_aggregation_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["explainability_serialization_verified"] is True
    assert first["summary"]["diagnostic_serialization_verified"] is True
    assert first["summary"]["explainability_hashing_verified"] is True
    assert first["summary"]["diagnostic_hashing_verified"] is True
    assert first["summary"]["source_evidence_reference_stability_verified"] is True
    assert first["summary"]["explainability_coverage_preserved"] is True
    assert first["summary"]["diagnostic_visibility_preserved"] is True
    assert first["summary"]["unresolved_diagnostic_preserved"] is True
    assert first["summary"]["provenance_visibility_verified"] is True
    assert first["summary"]["lineage_visibility_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_BOUNDARY_EXPLAINABILITY_AGGREGATION_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_explainability_aggregation_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_explainability_aggregation_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_5_segmentation_scope_regression_remains_non_operational():
    report = build_v4_4_boundary_segmentation_scope_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_scheduling_execution_count"] == 0
    assert report["summary"]["planner_integration_enabled"] is False
    assert report["summary"]["production_consumption_enabled"] is False
    assert report["summary"]["runtime_mutation_enabled"] is False
    assert report["summary"]["non_operational_certification_verified"] is True
