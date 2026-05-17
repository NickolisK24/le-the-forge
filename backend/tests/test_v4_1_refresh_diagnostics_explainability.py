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

from operational_refresh.refresh_diagnostics_explainability_continuity import (  # noqa: E402
    certify_diagnostics_explainability_continuity,
)
from operational_refresh.refresh_diagnostics_explainability_diagnostics import (  # noqa: E402
    build_refresh_diagnostics_explainability_diagnostics,
    build_unified_refresh_diagnostics,
    build_unified_refresh_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_hashing import (  # noqa: E402
    hash_diagnostics_explainability_identity,
    hash_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_integrity import (  # noqa: E402
    diagnostics_explainability_identities_equal,
    diagnostics_explainability_identity_key,
    refresh_diagnostics_explainabilities_equal,
    validate_diagnostics_explainability_integrity,
    validate_diagnostics_explainability_non_execution,
)
from operational_refresh.refresh_diagnostics_explainability_models import (  # noqa: E402
    DIAGNOSTIC_STATE_BLOCKED,
    DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT,
    DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY,
    DIAGNOSTIC_STATE_MISSING_COVERAGE,
    DIAGNOSTIC_STATE_PROHIBITED_DOMAIN,
    DIAGNOSTIC_STATE_STALE,
    DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER,
    DIAGNOSTIC_STATE_VISIBLE,
    EXPLANATION_STATE_BLOCKED,
    EXPLANATION_STATE_CROSS_LAYER_CONFLICT,
    EXPLANATION_STATE_INCONSISTENT_CATEGORY,
    EXPLANATION_STATE_MISSING_COVERAGE,
    EXPLANATION_STATE_PROHIBITED_DOMAIN,
    EXPLANATION_STATE_STALE,
    EXPLANATION_STATE_UNSUPPORTED_PROVIDER,
    EXPLANATION_STATE_VISIBLE,
    PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_SCHEMA_VERSION,
    V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_STABLE,
    default_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_serialization import (  # noqa: E402
    export_refresh_diagnostics_explainability,
    serialize_refresh_diagnostics_explainability,
)
from operational_refresh.refresh_diagnostics_explainability_visibility import (  # noqa: E402
    count_diagnostic_states,
    count_explanation_states,
    validate_refresh_diagnostics_explainability_visibility,
)
from scripts.report_v4_1_refresh_diagnostics_explainability import (  # noqa: E402
    build_v4_1_refresh_diagnostics_continuity_certification_report,
    build_v4_1_refresh_diagnostics_explainability_report,
    build_v4_1_refresh_diagnostics_integrity_certification_report,
    build_v4_1_unified_refresh_diagnostics_report,
    build_v4_1_unified_refresh_explainability_report,
)


def test_v4_1_diagnostics_explainability_models_are_immutable_descriptive_and_non_executable():
    payload = default_refresh_diagnostics_explainability()

    with pytest.raises(FrozenInstanceError):
        payload.remediation_enabled = True

    assert payload.identity.schema_version == V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_SCHEMA_VERSION
    assert payload.non_executable is True
    assert payload.descriptive_only is True
    assert payload.remediation_enabled is False
    assert payload.automatic_correction_enabled is False
    assert payload.recommendation_enabled is False
    assert payload.ranking_enabled is False
    assert payload.scoring_enabled is False
    assert payload.selection_enabled is False
    assert payload.approval_enabled is False
    assert payload.authorization_enabled is False
    assert payload.refresh_execution_enabled is False
    assert payload.orchestration_enabled is False
    assert payload.planner_integration_enabled is False
    assert payload.production_consumption_enabled is False
    assert payload.runtime_mutation_enabled is False
    assert all(not summary.remediation_enabled for summary in payload.diagnostic_summaries)
    assert all(not summary.recommendation_enabled for summary in payload.explanation_summaries)


def test_v4_1_diagnostics_explainability_identity_key_is_stable():
    payload = default_refresh_diagnostics_explainability()

    assert diagnostics_explainability_identity_key(payload.identity) == (
        "v4_1.refresh_diagnostics_explainability.1"
        "|v4_1_phase_8_refresh_diagnostics_explainability"
        "|v4_1_refresh_diagnostics_explainability_primary|v4_1_refresh_explainability_primary"
        "|v4.1.0-phase-8|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary|v4_1_schema_evolution_governance_primary"
        "|v4_1_refresh_sequencing_visibility_primary|v4_1_refresh_drift_certification_primary"
        "|v4_1_refresh_replay_rollback_visibility_primary"
        "|v4_1_refresh_diagnostics_explainability_provenance_primary"
        "|v4_1_refresh_diagnostics_explainability_lineage_primary"
    )


def test_v4_1_diagnostics_explainability_serialization_hashing_and_equality_are_stable():
    first = default_refresh_diagnostics_explainability()
    second = default_refresh_diagnostics_explainability()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_diagnostics_explainabilities_equal(first, second)
    assert diagnostics_explainability_identities_equal(first.identity, second.identity)
    assert serialize_refresh_diagnostics_explainability(first) == serialize_refresh_diagnostics_explainability(second)
    assert hash_refresh_diagnostics_explainability(first) == hash_refresh_diagnostics_explainability(second)
    assert hash_diagnostics_explainability_identity(first.identity) == hash_diagnostics_explainability_identity(second.identity)
    assert json.loads(serialize_refresh_diagnostics_explainability(first))["non_executable"] is True


def test_v4_1_diagnostics_explainability_serialization_preserves_order_and_fail_visible_states():
    payload = default_refresh_diagnostics_explainability()
    reordered = replace(
        payload,
        diagnostic_summaries=tuple(reversed(payload.diagnostic_summaries)),
        explanation_summaries=tuple(reversed(payload.explanation_summaries)),
    )

    assert serialize_refresh_diagnostics_explainability(payload) == serialize_refresh_diagnostics_explainability(reordered)
    assert hash_refresh_diagnostics_explainability(payload) == hash_refresh_diagnostics_explainability(reordered)
    exported = export_refresh_diagnostics_explainability(reordered)
    assert [item["state"] for item in exported["diagnostic_summaries"]] == [
        *(DIAGNOSTIC_STATE_VISIBLE for _ in range(8)),
        DIAGNOSTIC_STATE_MISSING_COVERAGE,
        DIAGNOSTIC_STATE_INCONSISTENT_SEVERITY,
        DIAGNOSTIC_STATE_UNSUPPORTED_PROVIDER,
        DIAGNOSTIC_STATE_PROHIBITED_DOMAIN,
        DIAGNOSTIC_STATE_BLOCKED,
        DIAGNOSTIC_STATE_STALE,
        DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT,
    ]
    assert [item["state"] for item in exported["explanation_summaries"]][-7:] == [
        EXPLANATION_STATE_MISSING_COVERAGE,
        EXPLANATION_STATE_INCONSISTENT_CATEGORY,
        EXPLANATION_STATE_UNSUPPORTED_PROVIDER,
        EXPLANATION_STATE_PROHIBITED_DOMAIN,
        EXPLANATION_STATE_BLOCKED,
        EXPLANATION_STATE_STALE,
        EXPLANATION_STATE_CROSS_LAYER_CONFLICT,
    ]


def test_v4_1_diagnostics_explainability_visibility_validates_diagnostics_and_explanations():
    payload = default_refresh_diagnostics_explainability()
    validation = validate_refresh_diagnostics_explainability_visibility(payload)
    diagnostic_counts = count_diagnostic_states(payload.diagnostic_summaries)
    explanation_counts = count_explanation_states(payload.explanation_summaries)

    assert diagnostic_counts[DIAGNOSTIC_STATE_VISIBLE] == 8
    assert diagnostic_counts[DIAGNOSTIC_STATE_MISSING_COVERAGE] == 1
    assert diagnostic_counts[DIAGNOSTIC_STATE_CROSS_LAYER_CONFLICT] == 1
    assert explanation_counts[EXPLANATION_STATE_VISIBLE] == 10
    assert explanation_counts[EXPLANATION_STATE_MISSING_COVERAGE] == 1
    assert explanation_counts[EXPLANATION_STATE_CROSS_LAYER_CONFLICT] == 1
    assert validation["valid"] is True
    assert validation["diagnostic_layer_coverage_complete"] is True
    assert validation["explanation_category_coverage_complete"] is True
    assert validation["unsupported_state_explanations_visible"] is True
    assert validation["blocked_state_explanations_visible"] is True
    assert validation["prohibited_state_explanations_visible"] is True
    assert validation["limitation_explanations_visible"] is True
    assert validation["cross_layer_diagnostic_aggregation_visible"] is True
    assert validation["cross_layer_explanation_aggregation_visible"] is True
    assert validation["prohibited_domain_visibility_count"] == len(PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS)
    assert validation["diagnostic_action_semantics_count"] == 0
    assert validation["explanation_action_semantics_count"] == 0


def test_v4_1_diagnostics_explainability_continuity_certifies_provenance_lineage_replay_and_rollback():
    payload = default_refresh_diagnostics_explainability()
    continuity = certify_diagnostics_explainability_continuity(payload)

    with pytest.raises(FrozenInstanceError):
        payload.continuity_metadata.automatic_correction_enabled = True

    assert continuity["valid"] is True
    assert continuity["diagnostics_continuity_valid"] is True
    assert continuity["provenance_continuity_valid"] is True
    assert continuity["lineage_continuity_valid"] is True
    assert continuity["replay_continuity_valid"] is True
    assert continuity["rollback_continuity_valid"] is True


def test_v4_1_diagnostics_explainability_non_execution_blocks_remediation_recommendation_approval_and_execution():
    payload = default_refresh_diagnostics_explainability()
    contaminated = replace(
        payload,
        remediation_enabled=True,
        automatic_correction_enabled=True,
        recommendation_enabled=True,
        ranking_enabled=True,
        scoring_enabled=True,
        selection_enabled=True,
        approval_enabled=True,
        authorization_enabled=True,
        refresh_execution_enabled=True,
        production_consumption_enabled=True,
        planner_integration_enabled=True,
    )
    validation = validate_diagnostics_explainability_non_execution(contaminated)

    assert validate_diagnostics_explainability_non_execution(payload)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 11
    assert validation["remediation_absent"] is False
    assert validation["automatic_correction_absent"] is False
    assert validation["recommendation_absent"] is False
    assert validation["ranking_absent"] is False
    assert validation["scoring_absent"] is False
    assert validation["selection_absent"] is False
    assert validation["approval_absent"] is False
    assert validation["authorization_absent"] is False
    assert validation["refresh_execution_absent"] is False
    assert validation["production_consumption_absent"] is False
    assert validation["planner_integration_absent"] is False


def test_v4_1_diagnostics_explainability_integrity_blocks_hidden_action_semantics():
    payload = default_refresh_diagnostics_explainability()
    hidden_diagnostic = replace(
        payload.diagnostic_summaries[10],
        hidden=True,
        fail_visible=False,
        remediation_enabled=True,
        automatic_correction_enabled=True,
    )
    hidden_explanation = replace(
        payload.explanation_summaries[12],
        hidden=True,
        fail_visible=False,
        recommendation_enabled=True,
        approval_enabled=True,
    )
    contaminated = replace(
        payload,
        diagnostic_summaries=(*payload.diagnostic_summaries[:10], hidden_diagnostic, *payload.diagnostic_summaries[11:]),
        explanation_summaries=(*payload.explanation_summaries[:12], hidden_explanation, *payload.explanation_summaries[13:]),
    )
    validation = validate_diagnostics_explainability_integrity(contaminated)

    assert validate_diagnostics_explainability_integrity(payload)["valid"] is True
    assert validation["valid"] is False
    assert validation["visibility_validation"]["hidden_diagnostic_count"] == 1
    assert validation["visibility_validation"]["hidden_explanation_count"] == 1
    assert validation["visibility_validation"]["diagnostic_action_semantics_count"] == 1
    assert validation["visibility_validation"]["explanation_action_semantics_count"] == 1
    assert validation["non_execution_validation"]["enabled_capability_count"] == 6


def test_v4_1_diagnostics_explainability_diagnostics_are_fail_visible_and_descriptive_only():
    diagnostics = build_refresh_diagnostics_explainability_diagnostics()
    unified_diagnostics = build_unified_refresh_diagnostics()
    unified_explainability = build_unified_refresh_explainability()

    assert diagnostics["visibility_validation"]["valid"] is True
    assert diagnostics["continuity_certification"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert diagnostics["fail_visible_warning_count"] >= len(PROHIBITED_DIAGNOSTICS_EXPLAINABILITY_DOMAINS)
    assert diagnostics["diagnostics_visible"] is True
    assert diagnostics["explanations_visible"] is True
    assert diagnostics["diagnostics_are_descriptive_only"] is True
    assert diagnostics["explanations_are_descriptive_only"] is True
    assert diagnostics["recommendation_absent"] is True
    assert diagnostics["approval_absent"] is True
    assert diagnostics["authorization_absent"] is True
    assert unified_diagnostics["cross_layer_diagnostic_conflict_ids"] == ["v4_1_cross_layer_diagnostic_conflict"]
    assert unified_explainability["cross_layer_explanation_conflict_ids"] == ["v4_1_cross_layer_explanation_conflict"]


def test_v4_1_diagnostics_explainability_reports_contain_required_boundaries_and_certification():
    report = build_v4_1_refresh_diagnostics_explainability_report()
    diagnostics_report = build_v4_1_unified_refresh_diagnostics_report()
    explainability_report = build_v4_1_unified_refresh_explainability_report()
    continuity_report = build_v4_1_refresh_diagnostics_continuity_certification_report()
    integrity_report = build_v4_1_refresh_diagnostics_integrity_certification_report()

    assert report["foundation_status"] == V4_1_REFRESH_DIAGNOSTICS_EXPLAINABILITY_STATUS_STABLE
    assert report["diagnostics_explainability_mode"] == "descriptive_only"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["enabled_capability_count"] == 0
    assert report["summary"]["deterministic_diagnostics_serialization_verified"] is True
    assert report["summary"]["deterministic_diagnostics_hashing_verified"] is True
    assert report["summary"]["deterministic_diagnostics_equality_verified"] is True
    assert report["summary"]["deterministic_diagnostics_visibility_verified"] is True
    assert report["summary"]["deterministic_explanation_visibility_verified"] is True
    assert report["summary"]["cross_layer_diagnostic_aggregation_validated"] is True
    assert report["summary"]["cross_layer_explanation_aggregation_validated"] is True
    assert report["summary"]["unsupported_state_explanation_validated"] is True
    assert report["summary"]["blocked_state_explanation_validated"] is True
    assert report["summary"]["prohibited_state_explanation_validated"] is True
    assert report["summary"]["limitation_explanation_validated"] is True
    assert report["summary"]["non_recommendation_ranking_scoring_selection_enforcement_validated"] is True
    assert report["summary"]["non_approval_authorization_enforcement_validated"] is True
    assert diagnostics_report["summary"]["enabled_capability_count"] == 0
    assert explainability_report["summary"]["enabled_capability_count"] == 0
    assert continuity_report["summary"]["continuity_certification_verified"] is True
    assert integrity_report["summary"]["integrity_validation_verified"] is True
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No recommendation ranking scoring or selection exists." in report["explicit_prohibitions"]
    assert "No approval or authorization exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No rollback execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
    assert "No mutation behavior exists." in report["explicit_prohibitions"]
