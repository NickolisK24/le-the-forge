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
    build_v4_4_boundary_conflict_drift_report,
)
from orchestration_governance.v4_4_cross_boundary_consistency_audit import (  # noqa: E402
    build_v4_4_cross_boundary_consistency,
    build_v4_4_cross_boundary_consistency_report,
    contaminate_cross_boundary_consistency_for_non_operational_validation,
    cross_boundary_consistency_capability_counter_values,
    cross_boundary_consistency_equal,
    enabled_cross_boundary_consistency_capability_flags,
    validate_cross_boundary_consistency,
    validate_cross_boundary_consistency_non_operational,
    validate_cross_boundary_consistency_ordering_stability,
    validate_cross_boundary_consistency_serialization_and_hashing,
    validate_cross_boundary_consistency_visibility,
    validate_cross_boundary_replay_rollback_evidence,
)
from orchestration_governance.v4_4_cross_boundary_consistency_hashing import (  # noqa: E402
    hash_consistency_evidence_metadata,
    hash_cross_boundary_consistency_identity,
    hash_cross_boundary_consistency_intelligence,
)
from orchestration_governance.v4_4_cross_boundary_consistency_models import (  # noqa: E402
    CONSISTENCY_STATE_AMBIGUOUS,
    CONSISTENCY_STATE_BLOCKED,
    CONSISTENCY_STATE_COMPATIBLE,
    CONSISTENCY_STATE_CONFLICTING,
    CONSISTENCY_STATE_CONSISTENT,
    CONSISTENCY_STATE_DEGRADED,
    CONSISTENCY_STATE_INCOMPATIBLE,
    CONSISTENCY_STATE_INCONSISTENT,
    CONSISTENCY_STATE_PARTIALLY_CONSISTENT,
    CONSISTENCY_STATE_PROHIBITED,
    CONSISTENCY_STATE_STALE,
    CONSISTENCY_STATE_UNSUPPORTED,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_DISABLED_COUNTER_NAMES,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_SCHEMA_VERSION,
    V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_STABLE,
)
from orchestration_governance.v4_4_cross_boundary_consistency_serialization import (  # noqa: E402
    serialize_cross_boundary_consistency_intelligence,
)
from orchestration_governance.v4_4_cross_boundary_consistency_visibility import (  # noqa: E402
    aggregate_cross_boundary_diagnostics,
    compatibility_consistency_visibility,
    cross_boundary_consistency_summaries,
    degraded_consistency_visibility,
    fail_visible_consistency_ambiguity_summaries,
    governance_safe_consistency_explainability,
    incompatibility_visibility,
    lineage_consistency_visibility,
    provenance_consistency_visibility,
    relationship_consistency_visibility,
)


REPORT_PATH = BACKEND_ROOT.parent / "docs" / "generated" / "v4_4_cross_boundary_consistency_report.json"


def test_v4_4_cross_boundary_models_are_immutable_and_non_operational():
    intelligence = build_v4_4_cross_boundary_consistency()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.identity.schema_version == V4_4_CROSS_BOUNDARY_CONSISTENCY_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_authoritative is True
    assert intelligence.non_enforcing is True
    assert intelligence.non_remediating is True
    assert intelligence.non_resolving is True
    assert intelligence.non_normalizing is True
    assert intelligence.non_mutating is True
    assert enabled_cross_boundary_consistency_capability_flags(intelligence) == {}
    assert all(
        value == 0 for value in cross_boundary_consistency_capability_counter_values(intelligence).values()
    )


def test_v4_4_cross_boundary_visibility_preserves_required_classifications():
    intelligence = build_v4_4_cross_boundary_consistency()
    visibility = validate_cross_boundary_consistency_visibility(intelligence)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[CONSISTENCY_STATE_CONSISTENT] == 3
    assert counts[CONSISTENCY_STATE_INCONSISTENT] == 1
    assert counts[CONSISTENCY_STATE_PARTIALLY_CONSISTENT] == 4
    assert counts[CONSISTENCY_STATE_UNSUPPORTED] == 1
    assert counts[CONSISTENCY_STATE_PROHIBITED] == 1
    assert counts[CONSISTENCY_STATE_BLOCKED] == 1
    assert counts[CONSISTENCY_STATE_STALE] == 3
    assert counts[CONSISTENCY_STATE_CONFLICTING] == 2
    assert counts[CONSISTENCY_STATE_AMBIGUOUS] == 2
    assert counts[CONSISTENCY_STATE_DEGRADED] == 4
    assert counts[CONSISTENCY_STATE_COMPATIBLE] == 3
    assert counts[CONSISTENCY_STATE_INCOMPATIBLE] == 3
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []


def test_v4_4_cross_boundary_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_cross_boundary_consistency()
    second = build_v4_4_cross_boundary_consistency()
    serialization = validate_cross_boundary_consistency_serialization_and_hashing(first)

    assert first == second
    assert cross_boundary_consistency_equal(first, second)
    assert serialize_cross_boundary_consistency_intelligence(first) == serialize_cross_boundary_consistency_intelligence(second)
    assert hash_cross_boundary_consistency_intelligence(first) == hash_cross_boundary_consistency_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_cross_boundary_consistency_identity(first.identity)) == 64
    assert len(hash_consistency_evidence_metadata(first.evidence_metadata)) == 64


def test_v4_4_cross_boundary_ordering_survives_reordered_collections():
    intelligence = build_v4_4_cross_boundary_consistency()
    reordered = replace(
        intelligence,
        classifications=tuple(reversed(intelligence.classifications)),
        consistency_records=tuple(reversed(intelligence.consistency_records)),
        relationship_records=tuple(reversed(intelligence.relationship_records)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        compatibility_consistency=tuple(reversed(intelligence.compatibility_consistency)),
        continuity_consistency=tuple(reversed(intelligence.continuity_consistency)),
        explainability=tuple(reversed(intelligence.explainability)),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(intelligence.explicit_prohibitions)),
    )

    assert validate_cross_boundary_consistency_ordering_stability(intelligence)["valid"] is True
    assert serialize_cross_boundary_consistency_intelligence(intelligence) == serialize_cross_boundary_consistency_intelligence(reordered)
    assert hash_cross_boundary_consistency_intelligence(intelligence) == hash_cross_boundary_consistency_intelligence(reordered)


def test_v4_4_cross_boundary_visibility_helpers_remain_descriptive_only():
    intelligence = build_v4_4_cross_boundary_consistency()
    consistency = cross_boundary_consistency_summaries(intelligence)
    relationships = relationship_consistency_visibility(intelligence)
    compatibility = compatibility_consistency_visibility(intelligence)
    incompatibility = incompatibility_visibility(intelligence)
    degradation = degraded_consistency_visibility(intelligence)
    diagnostics = aggregate_cross_boundary_diagnostics(intelligence.diagnostics)
    explainability = governance_safe_consistency_explainability(intelligence.explainability)

    assert len(consistency) == 12
    assert relationships["relationship_count"] == 8
    assert relationships["recommendation_enabled_count"] == 0
    assert relationships["decision_enabled_count"] == 0
    assert compatibility["compatibility_consistency_count"] == 4
    assert compatibility["compatible_count"] == 1
    assert compatibility["incompatible_count"] == 1
    assert compatibility["authorization_enabled_count"] == 0
    assert compatibility["approval_enabled_count"] == 0
    assert len(incompatibility) == 1
    assert degradation["continuity_consistency_count"] == 4
    assert degradation["degraded_count"] == 1
    assert degradation["mutation_enabled_count"] == 0
    assert diagnostics["diagnostic_count"] == 12
    assert diagnostics["consistency_auto_resolution_enabled_count"] == 0
    assert diagnostics["automatic_normalization_enabled_count"] == 0
    assert diagnostics["automatic_remediation_enabled_count"] == 0
    assert diagnostics["automatic_repair_enabled_count"] == 0
    assert explainability["explainability_first"] is True
    assert explainability["recommendation_enabled_count"] == 0
    assert explainability["decision_enabled_count"] == 0
    assert explainability["scoring_enabled_count"] == 0


def test_v4_4_cross_boundary_ambiguity_and_degradation_are_fail_visible():
    intelligence = build_v4_4_cross_boundary_consistency()
    ambiguity = fail_visible_consistency_ambiguity_summaries(intelligence)
    degradation = degraded_consistency_visibility(intelligence)

    assert len(ambiguity) == 2
    assert all(item["fail_visible"] is True for item in ambiguity)
    assert degradation["degraded_count"] == 1
    assert degradation["fail_visible"] is True


def test_v4_4_cross_boundary_replay_rollback_provenance_and_lineage_are_preserved():
    intelligence = build_v4_4_cross_boundary_consistency()
    replay = validate_cross_boundary_replay_rollback_evidence(intelligence)
    validation = validate_cross_boundary_consistency(intelligence)
    provenance = provenance_consistency_visibility(intelligence)
    lineage = lineage_consistency_visibility(intelligence)

    assert replay["valid"] is True
    assert replay["expected_evidence_count"] == 32
    assert replay["replay_safe_evidence_count"] == 32
    assert replay["rollback_safe_evidence_count"] == 32
    assert validation["valid"] is True
    assert provenance["provenance_consistency_visible"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert provenance["production_consumption_enabled"] is False
    assert lineage["lineage_consistency_visible"] is True
    assert lineage["ambiguous_lineage_inferred"] is False
    assert lineage["operational_mutation_enabled"] is False


def test_v4_4_cross_boundary_non_operational_validation_detects_contamination():
    intelligence = build_v4_4_cross_boundary_consistency()
    contaminated = contaminate_cross_boundary_consistency_for_non_operational_validation(intelligence)
    validation = validate_cross_boundary_consistency_non_operational(contaminated)

    assert validate_cross_boundary_consistency_non_operational(intelligence)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_cross_boundary_report_generation_and_hash_are_stable():
    first = build_v4_4_cross_boundary_consistency_report()
    second = build_v4_4_cross_boundary_consistency_report()

    assert first == second
    assert first["foundation_status"] == V4_4_CROSS_BOUNDARY_CONSISTENCY_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["replay_safe_evidence_verified"] is True
    assert first["summary"]["rollback_safe_evidence_verified"] is True
    assert first["summary"]["cross_boundary_consistency_visibility_verified"] is True
    assert first["summary"]["inconsistency_visibility_verified"] is True
    assert first["summary"]["partial_consistency_visibility_verified"] is True
    assert first["summary"]["compatibility_consistency_verified"] is True
    assert first["summary"]["provenance_consistency_verified"] is True
    assert first["summary"]["lineage_consistency_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_CROSS_BOUNDARY_CONSISTENCY_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_cross_boundary_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_cross_boundary_consistency_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_3_conflict_drift_regression_remains_non_operational():
    report = build_v4_4_boundary_conflict_drift_report()

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
