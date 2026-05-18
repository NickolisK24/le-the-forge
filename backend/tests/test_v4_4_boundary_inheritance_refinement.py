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

from orchestration_governance.v4_4_boundary_inheritance_refinement_audit import (  # noqa: E402
    boundary_inheritance_refinement_equal,
    build_v4_4_boundary_inheritance_refinement,
    build_v4_4_boundary_inheritance_refinement_report,
    contaminate_inheritance_for_non_operational_validation,
    enabled_inheritance_capability_flags,
    inheritance_capability_counter_values,
    validate_boundary_inheritance_refinement,
    validate_inheritance_non_operational,
    validate_inheritance_ordering_stability,
    validate_inheritance_serialization_and_hashing,
    validate_inheritance_state_visibility,
    validate_replay_rollback_evidence,
)
from orchestration_governance.v4_4_boundary_inheritance_refinement_hashing import (  # noqa: E402
    hash_boundary_inheritance_identity,
    hash_boundary_inheritance_refinement_intelligence,
    hash_continuity_propagation_metadata,
)
from orchestration_governance.v4_4_boundary_inheritance_refinement_models import (  # noqa: E402
    INHERITANCE_STATE_AMBIGUOUS,
    INHERITANCE_STATE_BLOCKED,
    INHERITANCE_STATE_CONFLICTING,
    INHERITANCE_STATE_INHERITED,
    INHERITANCE_STATE_PROHIBITED,
    INHERITANCE_STATE_REFINED,
    INHERITANCE_STATE_STALE,
    INHERITANCE_STATE_SUPPORTED,
    INHERITANCE_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_INHERITANCE_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_INHERITANCE_SCHEMA_VERSION,
    V4_4_BOUNDARY_INHERITANCE_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_inheritance_refinement_serialization import (  # noqa: E402
    serialize_boundary_inheritance_refinement_intelligence,
)
from orchestration_governance.v4_4_boundary_inheritance_refinement_visibility import (  # noqa: E402
    aggregate_refinement_diagnostics,
    ancestry_depth_visibility,
    fail_visible_ambiguity_summaries,
    fail_visible_inheritance_summary,
    governance_safe_refinement_explainability,
    inheritance_chain_summaries,
    inheritance_conflict_visibility,
    lineage_propagation_visibility,
    provenance_propagation_visibility,
    refinement_ancestry_summaries,
    refinement_drift_visibility,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_audit import (  # noqa: E402
    build_v4_4_boundary_intelligence_foundations_report,
)


REPORT_PATH = BACKEND_ROOT.parent / "docs" / "generated" / "v4_4_boundary_inheritance_refinement_report.json"


def test_v4_4_inheritance_models_are_immutable_and_non_operational():
    intelligence = build_v4_4_boundary_inheritance_refinement()

    with pytest.raises(FrozenInstanceError):
        intelligence.runtime_execution_enabled = True

    assert intelligence.identity.schema_version == V4_4_BOUNDARY_INHERITANCE_SCHEMA_VERSION
    assert intelligence.descriptive_only is True
    assert intelligence.non_operational is True
    assert intelligence.non_authoritative is True
    assert intelligence.non_executing is True
    assert intelligence.non_authorizing is True
    assert intelligence.non_approving is True
    assert intelligence.non_dispatching is True
    assert intelligence.non_routing is True
    assert intelligence.non_mutating is True
    assert enabled_inheritance_capability_flags(intelligence) == {}
    assert all(value == 0 for value in inheritance_capability_counter_values(intelligence).values())


def test_v4_4_inheritance_and_refinement_state_visibility_is_complete():
    intelligence = build_v4_4_boundary_inheritance_refinement()
    visibility = validate_inheritance_state_visibility(intelligence)

    assert visibility["valid"] is True
    counts = visibility["combined_counts"]
    assert counts[INHERITANCE_STATE_SUPPORTED] == 2
    assert counts[INHERITANCE_STATE_UNSUPPORTED] == 2
    assert counts[INHERITANCE_STATE_PROHIBITED] == 2
    assert counts[INHERITANCE_STATE_BLOCKED] == 1
    assert counts[INHERITANCE_STATE_STALE] == 1
    assert counts[INHERITANCE_STATE_CONFLICTING] == 2
    assert counts[INHERITANCE_STATE_AMBIGUOUS] == 2
    assert counts[INHERITANCE_STATE_INHERITED] == 2
    assert counts[INHERITANCE_STATE_REFINED] == 2
    assert visibility["missing_states"] == []
    assert visibility["missing_fail_visible_states"] == []


def test_v4_4_inheritance_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_inheritance_refinement()
    second = build_v4_4_boundary_inheritance_refinement()
    serialization = validate_inheritance_serialization_and_hashing(first)

    assert first == second
    assert boundary_inheritance_refinement_equal(first, second)
    assert serialize_boundary_inheritance_refinement_intelligence(first) == serialize_boundary_inheritance_refinement_intelligence(second)
    assert hash_boundary_inheritance_refinement_intelligence(first) == hash_boundary_inheritance_refinement_intelligence(second)
    assert serialization["valid"] is True
    assert len(hash_boundary_inheritance_identity(first.identity)) == 64
    assert len(hash_continuity_propagation_metadata(first.continuity_propagation_metadata)) == 64


def test_v4_4_inheritance_ordering_survives_reordered_collections():
    intelligence = build_v4_4_boundary_inheritance_refinement()
    reordered = replace(
        intelligence,
        inheritance_relationships=tuple(reversed(intelligence.inheritance_relationships)),
        refinement_relationships=tuple(reversed(intelligence.refinement_relationships)),
        ancestry_visibility=tuple(reversed(intelligence.ancestry_visibility)),
        parent_child_refinement_visibility=tuple(
            reversed(intelligence.parent_child_refinement_visibility)
        ),
        refinement_lineage_continuity=tuple(reversed(intelligence.refinement_lineage_continuity)),
        diagnostics=tuple(reversed(intelligence.diagnostics)),
        explainability=tuple(reversed(intelligence.explainability)),
        fail_visible_findings=tuple(reversed(intelligence.fail_visible_findings)),
        deterministic_guarantees=tuple(reversed(intelligence.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(intelligence.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(intelligence.explicit_prohibitions)),
    )

    assert validate_inheritance_ordering_stability(intelligence)["valid"] is True
    assert serialize_boundary_inheritance_refinement_intelligence(intelligence) == serialize_boundary_inheritance_refinement_intelligence(reordered)
    assert hash_boundary_inheritance_refinement_intelligence(intelligence) == hash_boundary_inheritance_refinement_intelligence(reordered)


def test_v4_4_inheritance_visibility_helpers_remain_descriptive_only():
    intelligence = build_v4_4_boundary_inheritance_refinement()
    inheritance = inheritance_chain_summaries(intelligence)
    refinement = refinement_ancestry_summaries(intelligence)
    ancestry = ancestry_depth_visibility(intelligence.ancestry_visibility)
    diagnostics = aggregate_refinement_diagnostics(intelligence.diagnostics)
    explainability = governance_safe_refinement_explainability(intelligence.explainability)
    fail_visible = fail_visible_inheritance_summary(intelligence.fail_visible_findings)

    assert len(inheritance) == 8
    assert len(refinement) == 8
    assert ancestry["max_ancestry_depth"] == 3
    assert ancestry["multi_level_ancestry_count"] == 5
    assert ancestry["operational_authority_count"] == 0
    assert diagnostics["diagnostic_count"] == 16
    assert diagnostics["automatic_repair_enabled_count"] == 0
    assert diagnostics["automatic_remediation_enabled_count"] == 0
    assert explainability["explainability_first"] is True
    assert explainability["recommendation_enabled_count"] == 0
    assert explainability["decision_enabled_count"] == 0
    assert fail_visible["finding_count"] == 10
    assert fail_visible["hidden_inference_used_count"] == 0


def test_v4_4_inheritance_ambiguity_conflict_and_drift_are_fail_visible():
    intelligence = build_v4_4_boundary_inheritance_refinement()

    assert len(fail_visible_ambiguity_summaries(intelligence)) == 2
    assert len(inheritance_conflict_visibility(intelligence)) == 2
    assert len(refinement_drift_visibility(intelligence)) == 1
    assert all(
        finding["fail_visible"] is True
        for finding in fail_visible_ambiguity_summaries(intelligence)
        + inheritance_conflict_visibility(intelligence)
        + refinement_drift_visibility(intelligence)
    )


def test_v4_4_inheritance_replay_rollback_provenance_and_lineage_are_preserved():
    intelligence = build_v4_4_boundary_inheritance_refinement()
    replay = validate_replay_rollback_evidence(intelligence)
    validation = validate_boundary_inheritance_refinement(intelligence)
    provenance = provenance_propagation_visibility(intelligence)
    lineage = lineage_propagation_visibility(intelligence)

    assert replay["valid"] is True
    assert replay["relationship_count"] == 16
    assert replay["replay_safe_evidence_count"] == 16
    assert replay["rollback_safe_evidence_count"] == 16
    assert validation["valid"] is True
    assert provenance["provenance_continuity_preserved"] is True
    assert provenance["hidden_source_inference_used"] is False
    assert lineage["lineage_continuity_preserved"] is True
    assert lineage["ambiguous_lineage_inferred"] is False


def test_v4_4_inheritance_non_operational_validation_detects_contamination():
    intelligence = build_v4_4_boundary_inheritance_refinement()
    contaminated = contaminate_inheritance_for_non_operational_validation(intelligence)
    validation = validate_inheritance_non_operational(contaminated)

    assert validate_inheritance_non_operational(intelligence)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_inheritance_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_inheritance_refinement_report()
    second = build_v4_4_boundary_inheritance_refinement_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_INHERITANCE_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["replay_safe_evidence_verified"] is True
    assert first["summary"]["rollback_safe_evidence_verified"] is True
    assert first["summary"]["inheritance_continuity_verified"] is True
    assert first["summary"]["provenance_continuity_verified"] is True
    assert first["summary"]["lineage_continuity_verified"] is True
    assert first["summary"]["fail_visible_ambiguity_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_BOUNDARY_INHERITANCE_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_inheritance_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_inheritance_refinement_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_4_phase_1_foundation_regression_remains_non_operational():
    report = build_v4_4_boundary_intelligence_foundations_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_runtime_execution_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["enabled_dispatch_execution_count"] == 0
    assert report["summary"]["enabled_routing_execution_count"] == 0
    assert report["summary"]["enabled_operational_mutation_count"] == 0
    assert report["summary"]["non_operational_certification_verified"] is True
