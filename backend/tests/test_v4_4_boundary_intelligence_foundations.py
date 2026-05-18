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

from orchestration_governance.v4_3_closeout_readiness_audit import (  # noqa: E402
    build_v4_3_closeout_and_v4_4_readiness_report,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_audit import (  # noqa: E402
    boundary_capability_counter_values,
    boundary_intelligence_foundations_equal,
    build_v4_4_boundary_intelligence_foundations,
    build_v4_4_boundary_intelligence_foundations_report,
    contaminate_foundations_for_non_operational_validation,
    enabled_boundary_capability_flags,
    validate_boundary_intelligence_foundations,
    validate_boundary_non_operational,
    validate_boundary_ordering_stability,
    validate_boundary_replay_rollback_evidence,
    validate_boundary_serialization_and_hashing,
    validate_boundary_state_visibility,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_hashing import (  # noqa: E402
    hash_boundary_continuity_metadata,
    hash_boundary_intelligence_foundations,
    hash_boundary_intelligence_identity,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_models import (  # noqa: E402
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_STATE_CONFLICTING,
    BOUNDARY_STATE_PROHIBITED,
    BOUNDARY_STATE_STALE,
    BOUNDARY_STATE_SUPPORTED,
    BOUNDARY_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION,
    V4_4_BOUNDARY_INTELLIGENCE_STATUS_STABLE,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_serialization import (  # noqa: E402
    serialize_boundary_intelligence_foundations,
)
from orchestration_governance.v4_4_boundary_intelligence_foundations_visibility import (  # noqa: E402
    aggregate_boundary_diagnostics,
    aggregate_explainability_visibility,
    fail_visible_summary,
    governance_safe_boundary_summaries,
)


REPORT_PATH = BACKEND_ROOT.parent / "docs" / "generated" / "v4_4_boundary_intelligence_foundations_report.json"


def test_v4_4_boundary_models_are_immutable_and_non_operational():
    foundations = build_v4_4_boundary_intelligence_foundations()

    with pytest.raises(FrozenInstanceError):
        foundations.runtime_execution_enabled = True

    assert foundations.identity.schema_version == V4_4_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION
    assert foundations.descriptive_only is True
    assert foundations.non_operational is True
    assert foundations.non_executing is True
    assert foundations.non_authorizing is True
    assert foundations.non_approving is True
    assert foundations.non_dispatching is True
    assert foundations.non_routing is True
    assert foundations.non_mutating is True
    assert enabled_boundary_capability_flags(foundations) == {}
    assert all(value == 0 for value in boundary_capability_counter_values(foundations).values())


def test_v4_4_boundary_state_visibility_preserves_required_classifications():
    foundations = build_v4_4_boundary_intelligence_foundations()
    visibility = validate_boundary_state_visibility(foundations)

    assert visibility["valid"] is True
    assert visibility["record_counts"][BOUNDARY_STATE_SUPPORTED] == 2
    assert visibility["record_counts"][BOUNDARY_STATE_UNSUPPORTED] == 2
    assert visibility["record_counts"][BOUNDARY_STATE_PROHIBITED] == 4
    assert visibility["record_counts"][BOUNDARY_STATE_BLOCKED] == 1
    assert visibility["record_counts"][BOUNDARY_STATE_STALE] == 1
    assert visibility["record_counts"][BOUNDARY_STATE_CONFLICTING] == 1
    assert visibility["prohibited_visibility_count"] == 4
    assert visibility["unsupported_visibility_count"] == 2
    assert visibility["stale_visibility_count"] == 1
    assert visibility["conflicting_visibility_count"] == 1
    assert visibility["required_state_gaps"] == []
    assert visibility["fail_visible_state_gaps"] == []


def test_v4_4_boundary_serialization_hashing_and_equality_are_stable():
    first = build_v4_4_boundary_intelligence_foundations()
    second = build_v4_4_boundary_intelligence_foundations()
    serialization = validate_boundary_serialization_and_hashing(first)

    assert first == second
    assert boundary_intelligence_foundations_equal(first, second)
    assert serialize_boundary_intelligence_foundations(first) == serialize_boundary_intelligence_foundations(second)
    assert hash_boundary_intelligence_foundations(first) == hash_boundary_intelligence_foundations(second)
    assert serialization["valid"] is True
    assert len(hash_boundary_intelligence_identity(first.identity)) == 64
    assert len(hash_boundary_continuity_metadata(first.continuity_metadata)) == 64


def test_v4_4_boundary_ordering_survives_reordered_collections():
    foundations = build_v4_4_boundary_intelligence_foundations()
    reordered = replace(
        foundations,
        classifications=tuple(reversed(foundations.classifications)),
        boundary_records=tuple(reversed(foundations.boundary_records)),
        scope_visibility=tuple(reversed(foundations.scope_visibility)),
        segmentation_visibility=tuple(reversed(foundations.segmentation_visibility)),
        diagnostics=tuple(reversed(foundations.diagnostics)),
        explainability=tuple(reversed(foundations.explainability)),
        integrity_visibility=tuple(reversed(foundations.integrity_visibility)),
        governance_visibility_summaries=tuple(reversed(foundations.governance_visibility_summaries)),
        fail_visible_findings=tuple(reversed(foundations.fail_visible_findings)),
        deterministic_guarantees=tuple(reversed(foundations.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(foundations.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(foundations.explicit_prohibitions)),
    )

    assert validate_boundary_ordering_stability(foundations)["valid"] is True
    assert serialize_boundary_intelligence_foundations(foundations) == serialize_boundary_intelligence_foundations(reordered)
    assert hash_boundary_intelligence_foundations(foundations) == hash_boundary_intelligence_foundations(reordered)


def test_v4_4_boundary_visibility_helpers_are_descriptive_only():
    foundations = build_v4_4_boundary_intelligence_foundations()
    summaries = governance_safe_boundary_summaries(foundations)
    diagnostics = aggregate_boundary_diagnostics(foundations.diagnostics)
    explainability = aggregate_explainability_visibility(foundations.explainability)
    fail_visible = fail_visible_summary(foundations)

    assert len(summaries) == 6
    assert diagnostics["diagnostic_count"] == 11
    assert diagnostics["descriptive_only"] is True
    assert diagnostics["auto_remediation_enabled_count"] == 0
    assert diagnostics["repair_enabled_count"] == 0
    assert explainability["explainability_count"] == 11
    assert explainability["explainability_first"] is True
    assert explainability["recommendation_enabled_count"] == 0
    assert explainability["decision_enabled_count"] == 0
    assert fail_visible["fail_visible_finding_count"] == 9
    assert fail_visible["hidden_inference_used_count"] == 0
    assert fail_visible["remediation_enabled_count"] == 0


def test_v4_4_boundary_replay_rollback_provenance_and_lineage_are_preserved():
    foundations = build_v4_4_boundary_intelligence_foundations()
    evidence = validate_boundary_replay_rollback_evidence(foundations)
    validation = validate_boundary_intelligence_foundations(foundations)

    assert evidence["valid"] is True
    assert evidence["deterministic_evidence_count"] == 11
    assert evidence["replay_safe_evidence_count"] == 11
    assert evidence["rollback_safe_evidence_count"] == 11
    assert validation["valid"] is True
    assert validation["validations"]["continuity"]["provenance_continuity_preserved"] is True
    assert validation["validations"]["continuity"]["lineage_continuity_preserved"] is True


def test_v4_4_boundary_non_operational_validation_detects_contamination():
    foundations = build_v4_4_boundary_intelligence_foundations()
    contaminated = contaminate_foundations_for_non_operational_validation(foundations)
    validation = validate_boundary_non_operational(contaminated)

    assert validate_boundary_non_operational(foundations)["valid"] is True
    assert validation["valid"] is False
    assert validation["counters"]["enabled_runtime_execution_count"] > 0
    assert validation["counters"]["enabled_orchestration_authorization_count"] > 0
    assert validation["counters"]["enabled_orchestration_approval_count"] > 0
    assert validation["counters"]["enabled_dispatch_execution_count"] > 0
    assert validation["counters"]["enabled_routing_execution_count"] > 0
    assert validation["counters"]["enabled_operational_mutation_count"] > 0


def test_v4_4_boundary_report_generation_and_hash_are_stable():
    first = build_v4_4_boundary_intelligence_foundations_report()
    second = build_v4_4_boundary_intelligence_foundations_report()

    assert first == second
    assert first["foundation_status"] == V4_4_BOUNDARY_INTELLIGENCE_STATUS_STABLE
    assert first["deterministic_report_hash"] == second["deterministic_report_hash"]
    assert len(first["deterministic_report_hash"]) == 64
    assert first["summary"]["validation_error_count"] == 0
    assert first["summary"]["deterministic_ordering_verified"] is True
    assert first["summary"]["deterministic_serialization_verified"] is True
    assert first["summary"]["deterministic_hashing_verified"] is True
    assert first["summary"]["replay_safe_evidence_verified"] is True
    assert first["summary"]["rollback_safe_evidence_verified"] is True
    assert first["summary"]["provenance_continuity_verified"] is True
    assert first["summary"]["lineage_continuity_verified"] is True
    assert first["summary"]["governance_safe_certification_verified"] is True
    assert first["summary"]["non_operational_certification_verified"] is True
    for counter_name in V4_4_BOUNDARY_DISABLED_COUNTER_NAMES:
        assert first["summary"][counter_name] == 0
    assert first["summary"]["planner_integration_enabled"] is False
    assert first["summary"]["production_consumption_enabled"] is False
    assert first["summary"]["runtime_mutation_enabled"] is False
    assert first["summary"]["operational_mutation_enabled"] is False


def test_v4_4_generated_report_matches_builder_output():
    assert REPORT_PATH.exists()
    generated = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    built = build_v4_4_boundary_intelligence_foundations_report()

    assert generated == built
    assert generated["summary"]["remaining_warning_count"] == 0
    assert generated["summary"]["remaining_blocker_count"] == 0


def test_v4_3_governance_closeout_regression_remains_non_operational():
    report = build_v4_3_closeout_and_v4_4_readiness_report()

    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_coordination_execution_count"] == 0
    assert report["summary"]["enabled_transition_execution_count"] == 0
    assert report["summary"]["enabled_policy_enforcement_count"] == 0
    assert report["summary"]["enabled_operational_capability_count"] == 0
    assert report["summary"]["enabled_orchestration_authorization_count"] == 0
    assert report["summary"]["enabled_orchestration_approval_count"] == 0
    assert report["summary"]["non_execution_guarantees_validated"] is True
    assert report["summary"]["non_authorization_guarantees_validated"] is True
    assert report["summary"]["non_approval_guarantees_validated"] is True
