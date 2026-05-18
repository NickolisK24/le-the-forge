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

from orchestration_governance.v4_4_boundary_conflict_drift_audit import (  # noqa: E402
    boundary_conflict_drift_equal,
    build_v4_4_boundary_conflict_drift,
    build_v4_4_boundary_conflict_drift_report,
    conflict_drift_capability_counter_values,
    contaminate_conflict_drift_for_non_operational_validation,
    enabled_conflict_drift_capability_flags,
    validate_boundary_conflict_drift,
    validate_conflict_drift_non_operational,
    validate_conflict_drift_ordering_stability,
    validate_conflict_drift_serialization_and_hashing,
    validate_conflict_drift_visibility,
    validate_replay_rollback_evidence,
)
from orchestration_governance.v4_4_boundary_conflict_drift_hashing import (  # noqa: E402
    hash_boundary_conflict_drift_identity,
    hash_boundary_conflict_drift_intelligence,
    hash_drift_evidence_metadata,
)
from orchestration_governance.v4_4_boundary_conflict_drift_models import (  # noqa: E402
    CONFLICT_DRIFT_STATE_AMBIGUOUS,
    CONFLICT_DRIFT_STATE_BLOCKED,
    CONFLICT_DRIFT_STATE_COMPATIBLE,
    CONFLICT_DRIFT_STATE_CONFLICTING,
    CONFLICT_DRIFT_STATE_DEGRADED,
    CONFLICT_DRIFT_STATE_DIVERGENT,
    CONFLICT_DRIFT_STATE_DRIFTED,
    CONFLICT_DRIFT_STATE_INCOMPATIBLE,
    CONFLICT_DRIFT_STATE_PROHIBITED,
    CONFLICT_DRIFT_STATE_STALE,
    CONFLICT_DRIFT_STATE_SUPPORTED,
    CONFLICT_DRIFT_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_CONFLICT_DRIFT_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_CONFLICT_DRIFT_SCHEMA_VERSION,
    V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_conflict_drift_serialization import (  # noqa: E402
    serialize_boundary_conflict_drift_intelligence,
)
from orchestration_governance.v4_4_boundary_conflict_drift_visibility import (  # noqa: E402
    aggregate_conflict_diagnostics,
    compatibility_summaries,
    continuity_degradation_summaries,
    fail_visible_ambiguity_summaries,
    governance_drift_summaries,
    governance_safe_conflict_explainability,
    incompatibility_summaries,
    lineage_degradation_visibility,
    provenance_degradation_visibility,
    refinement_divergence_summaries,
)
from orchestration_governance.v4_4_boundary_inheritance_refinement_audit import (  # noqa: E402
    build_v4_4_boundary_inheritance_refinement_report,
)


REPORT_PATH = BACKEND_ROOT.parent / "docs" / "generated" / "v4_4_boundary_conflict_drift_report.json"


def test_v4_4_conflict_drift_models_are_immutable_and_non_operational():
    intelligence = build_v4_4_boundary_conflict_drift()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.identity.schema_version == V4_4_BOUNDARY_CONFLICT_DRIFT_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_authoritative is True
    assert intelligence.non_remediating is True
    assert intelligence.non_resolving is True
    assert intelligence.non_mutating is True
    assert enabled_conflict_drift_capability_flags(intelligence) == {}
    assert all(value == 0 for value in conflict_drift_capability_counter_values(intelligence).values())


def test_v4_4_conflict_drift_visibility_preserves_required_classifications():
    intelligence = build_v4_4_boundary_conflict_drift()
    visibility = validate_conflict_drift_visibility(intelligence)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[CONFLICT_DRIFT_STATE_SUPPORTED] == 1
    assert counts[CONFLICT_DRIFT_STATE_UNSUPPORTED] == 1
    assert counts[CONFLICT_DRIFT_STATE_PROHIBITED] == 1
    assert counts[CONFLICT_DRIFT_STATE_BLOCKED] == 1
    assert counts[CONFLICT_DRIFT_STATE_STALE] == 1
    assert counts[CONFLICT_DRIFT_STATE_CONFLICTING] == 2
    assert counts[CONFLICT_DRIFT_STATE_AMBIGUOUS] == 2
    assert counts[CONFLICT_DRIFT_STATE_DRIFTED] == 1
    assert counts[CONFLICT_DRIFT_STATE_DIVERGENT] == 1
    assert counts[CONFLICT_DRIFT_STATE_COMPATIBLE] == 2
    assert counts[CONFLICT_DRIFT_STATE_INCOMPATIBLE] == 3
    assert counts[CONFLICT_DRIFT_STATE_DEGRADED] == 2
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []


def test_v4_4_conflict_drift_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_conflict_drift()
    second = build_v4_4_boundary_conflict_drift()
    serialization = validate_conflict_drift_serialization_and_hashing(first)

    assert first == second
    assert boundary_conflict_drift_equal(first, second)
    assert serialize_boundary_conflict_drift_intelligence(first) == serialize_boundary_conflict_drift_intelligence(second)
    assert hash_boundary_conflict_drift_intelligence(first) == hash_boundary_conflict_drift_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_boundary_conflict_drift_identity(first.identity)) == 64
    assert len(hash_drift_evidence_metadata(first.drift_evidence_metadata)) == 64


def test_v4_4_conflict_drift_ordering_survives_reordered_collections():
    intelligence = build_v4_4_boundary_conflict_drift()
    reordered = replace(
        intelligence,
        classifications=tuple(reversed(intelligence.classifications)),
        drift_records=tuple(reversed(intelligence.drift_records)),
        divergence_records=tuple(reversed(intelligence.divergence_records)),
        conflict_diagnostics=tuple(reversed(intelligence.conflict_diagnostics)),
        compatibility_evidence=tuple(reversed(intelligence.compatibility_evidence)),
        degradation_summaries=tuple(reversed(intelligence.degradation_summaries)),
        explainability=tuple(reversed(intelligence.explainability)),
        conflict_lineage_visibility=tuple(reversed(intelligence.conflict_lineage_visibility)),
        conflict_ancestry_visibility=tuple(reversed(intelligence.conflict_ancestry_visibility)),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(intelligence.explicit_prohibitions)),
    )

    assert validate_conflict_drift_ordering_stability(intelligence)["valid"] is True
    assert serialize_boundary_conflict_drift_intelligence(intelligence) == serialize_boundary_conflict_drift_intelligence(reordered)
    assert hash_boundary_conflict_drift_intelligence(intelligence) == hash_boundary_conflict_drift_intelligence(reordered)


def test_v4_4_conflict_drift_visibility_helpers_remain_descriptive_only():
    intelligence = build_v4_4_boundary_conflict_drift()
    drift = governance_drift_summaries(intelligence)
    divergence = refinement_divergence_summaries(intelligence)
    compatibility = compatibility_summaries(intelligence)
    incompatibility = incompatibility_summaries(intelligence)
    degradation = continuity_degradation_summaries(intelligence.degradation_summaries)
    diagnostics = aggregate_conflict_diagnostics(intelligence.conflict_diagnostics)
    explainability = governance_safe_conflict_explainability(intelligence.explainability)

    assert len(drift) == 8
    assert len(divergence) == 6
    assert compatibility["compatibility_evidence_count"] == 4
    assert compatibility["compatible_count"] == 1
    assert compatibility["incompatible_count"] == 1
    assert compatibility["authorization_enabled_count"] == 0
    assert len(incompatibility) == 1
    assert degradation["degradation_count"] == 3
    assert degradation["mutation_enabled_count"] == 0
    assert diagnostics["diagnostic_count"] == 14
    assert diagnostics["conflict_auto_resolution_enabled_count"] == 0
    assert diagnostics["automatic_remediation_enabled_count"] == 0
    assert diagnostics["automatic_repair_enabled_count"] == 0
    assert explainability["explainability_first"] is True
    assert explainability["recommendation_enabled_count"] == 0
    assert explainability["decision_enabled_count"] == 0


def test_v4_4_conflict_drift_ambiguity_and_degradation_are_fail_visible():
    intelligence = build_v4_4_boundary_conflict_drift()
    ambiguity = fail_visible_ambiguity_summaries(intelligence)
    degradation = continuity_degradation_summaries(intelligence.degradation_summaries)

    assert len(ambiguity) == 2
    assert all(item["fail_visible"] is True for item in ambiguity)
    assert degradation["degraded_count"] == 1
    assert degradation["fail_visible"] is True


def test_v4_4_conflict_drift_replay_rollback_provenance_and_lineage_are_preserved():
    intelligence = build_v4_4_boundary_conflict_drift()
    replay = validate_replay_rollback_evidence(intelligence)
    validation = validate_boundary_conflict_drift(intelligence)
    provenance = provenance_degradation_visibility(intelligence)
    lineage = lineage_degradation_visibility(intelligence)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 18
    assert replay["replay_safe_evidence_count"] == 18
    assert replay["rollback_safe_evidence_count"] == 18
    assert validation["valid"] is True
    assert provenance["provenance_continuity_visible"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert lineage["lineage_continuity_visible"] is True
    assert lineage["ambiguous_lineage_inferred"] is False


def test_v4_4_conflict_drift_non_operational_validation_detects_contamination():
    intelligence = build_v4_4_boundary_conflict_drift()
    contaminated = contaminate_conflict_drift_for_non_operational_validation(intelligence)
    validation = validate_conflict_drift_non_operational(contaminated)

    assert validate_conflict_drift_non_operational(intelligence)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_conflict_drift_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_conflict_drift_report()
    second = build_v4_4_boundary_conflict_drift_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_CONFLICT_DRIFT_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["replay_safe_evidence_verified"] is True
    assert first["summary"]["rollback_safe_evidence_verified"] is True
    assert first["summary"]["deterministic_conflict_visibility_verified"] is True
    assert first["summary"]["deterministic_drift_visibility_verified"] is True
    assert first["summary"]["compatibility_visibility_verified"] is True
    assert first["summary"]["provenance_continuity_verified"] is True
    assert first["summary"]["lineage_continuity_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_BOUNDARY_CONFLICT_DRIFT_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_conflict_drift_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_conflict_drift_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_2_inheritance_refinement_regression_remains_non_operational():
    report = build_v4_4_boundary_inheritance_refinement_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_operational_mutation_count"] == 0
    assert report["summary"]["non_operational_certification_verified"] is True
