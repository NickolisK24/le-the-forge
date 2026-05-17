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

from operational_refresh.refresh_continuity_certification_continuity import (  # noqa: E402
    certify_refresh_continuity,
)
from operational_refresh.refresh_continuity_certification_diagnostics import (  # noqa: E402
    build_cross_layer_continuity_diagnostics,
    build_cross_layer_continuity_explainability,
    build_refresh_continuity_certification_diagnostics,
    build_unified_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_hashing import (  # noqa: E402
    hash_continuity_certification_identity,
    hash_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_integrity import (  # noqa: E402
    continuity_certification_identities_equal,
    continuity_certification_identity_key,
    refresh_continuity_certifications_equal,
    validate_continuity_certification_integrity,
    validate_continuity_certification_non_execution,
)
from operational_refresh.refresh_continuity_certification_models import (  # noqa: E402
    CONTINUITY_STATE_BLOCKED,
    CONTINUITY_STATE_CROSS_LAYER_CONFLICT,
    CONTINUITY_STATE_FAILURE,
    CONTINUITY_STATE_PRESERVED,
    CONTINUITY_STATE_PROHIBITED,
    CONTINUITY_STATE_STALE,
    CONTINUITY_STATE_UNSUPPORTED,
    PROHIBITED_CONTINUITY_DOMAINS,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_SCHEMA_VERSION,
    V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_STABLE,
    default_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_serialization import (  # noqa: E402
    export_refresh_continuity_certification,
    serialize_refresh_continuity_certification,
)
from operational_refresh.refresh_continuity_certification_visibility import (  # noqa: E402
    count_continuity_states,
    validate_refresh_continuity_certification_visibility,
)
from scripts.report_v4_1_refresh_continuity_certification import (  # noqa: E402
    build_v4_1_cross_layer_continuity_diagnostics_report,
    build_v4_1_cross_layer_continuity_explainability_report,
    build_v4_1_cross_layer_continuity_integrity_certification_report,
    build_v4_1_refresh_continuity_certification_report,
    build_v4_1_unified_refresh_continuity_certification_report,
)


def test_v4_1_continuity_models_are_immutable_descriptive_and_non_executable():
    payload = default_refresh_continuity_certification()

    with pytest.raises(FrozenInstanceError):
        payload.remediation_enabled = True

    assert payload.identity.schema_version == V4_1_REFRESH_CONTINUITY_CERTIFICATION_SCHEMA_VERSION
    assert payload.non_executable is True
    assert payload.descriptive_only is True
    assert payload.remediation_enabled is False
    assert payload.automatic_correction_enabled is False
    assert payload.automatic_repair_enabled is False
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
    assert all(not entry.remediation_enabled for entry in payload.certifications)
    assert all(not entry.approval_enabled for entry in payload.certifications)


def test_v4_1_continuity_identity_key_is_stable():
    payload = default_refresh_continuity_certification()

    assert continuity_certification_identity_key(payload.identity) == (
        "v4_1.refresh_continuity_certification.1"
        "|v4_1_phase_9_refresh_continuity_certification"
        "|v4_1_refresh_continuity_certification_primary"
        "|v4.1.0-phase-9|v4_1_refresh_manifest_primary|v4_1_refresh_dependency_graph_primary"
        "|v4_1_refresh_lineage_certification_primary|v4_1_schema_evolution_governance_primary"
        "|v4_1_refresh_sequencing_visibility_primary|v4_1_refresh_drift_certification_primary"
        "|v4_1_refresh_replay_rollback_visibility_primary"
        "|v4_1_refresh_diagnostics_explainability_primary"
        "|v4_1_refresh_continuity_provenance_primary"
        "|v4_1_refresh_continuity_lineage_primary"
    )


def test_v4_1_continuity_serialization_hashing_and_equality_are_stable():
    first = default_refresh_continuity_certification()
    second = default_refresh_continuity_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert refresh_continuity_certifications_equal(first, second)
    assert continuity_certification_identities_equal(first.identity, second.identity)
    assert serialize_refresh_continuity_certification(first) == serialize_refresh_continuity_certification(second)
    assert hash_refresh_continuity_certification(first) == hash_refresh_continuity_certification(second)
    assert hash_continuity_certification_identity(first.identity) == hash_continuity_certification_identity(second.identity)
    assert json.loads(serialize_refresh_continuity_certification(first))["non_executable"] is True


def test_v4_1_continuity_serialization_preserves_order_and_fail_visible_states():
    payload = default_refresh_continuity_certification()
    reordered = replace(payload, certifications=tuple(reversed(payload.certifications)))

    assert serialize_refresh_continuity_certification(payload) == serialize_refresh_continuity_certification(reordered)
    assert hash_refresh_continuity_certification(payload) == hash_refresh_continuity_certification(reordered)
    exported = export_refresh_continuity_certification(reordered)
    states = [item["state"] for item in exported["certifications"]]
    assert states[:10] == [CONTINUITY_STATE_PRESERVED for _ in range(10)]
    assert states[10:20] == [CONTINUITY_STATE_FAILURE for _ in range(10)]
    assert states[-5:] == [
        CONTINUITY_STATE_UNSUPPORTED,
        CONTINUITY_STATE_BLOCKED,
        CONTINUITY_STATE_PROHIBITED,
        CONTINUITY_STATE_STALE,
        CONTINUITY_STATE_CROSS_LAYER_CONFLICT,
    ]
    assert sum(1 for item in exported["certifications"] if item["fail_visible"]) == 15


def test_v4_1_continuity_visibility_validates_all_layers_and_fail_visible_states():
    payload = default_refresh_continuity_certification()
    validation = validate_refresh_continuity_certification_visibility(payload)
    counts = count_continuity_states(payload.certifications)

    assert counts[CONTINUITY_STATE_PRESERVED] == 10
    assert counts[CONTINUITY_STATE_FAILURE] == 10
    assert counts[CONTINUITY_STATE_CROSS_LAYER_CONFLICT] == 1
    assert validation["valid"] is True
    assert validation["continuity_layer_coverage_complete"] is True
    assert validation["cross_layer_continuity_aggregation_visible"] is True
    assert validation["continuity_failure_visibility_count"] == 10
    assert validation["unsupported_continuity_state_visible"] is True
    assert validation["blocked_continuity_state_visible"] is True
    assert validation["prohibited_continuity_state_visible"] is True
    assert validation["stale_continuity_evidence_visible"] is True
    assert validation["cross_layer_continuity_conflict_visible"] is True
    assert set(payload.integrity_boundary.prohibited_continuity_domains) == set(PROHIBITED_CONTINUITY_DOMAINS)


def test_v4_1_continuity_certification_validates_all_required_continuity_dimensions():
    certification = certify_refresh_continuity()

    assert certification["valid"] is True
    assert certification["manifest_continuity_valid"] is True
    assert certification["dependency_continuity_valid"] is True
    assert certification["lineage_continuity_valid"] is True
    assert certification["schema_continuity_valid"] is True
    assert certification["sequencing_continuity_valid"] is True
    assert certification["drift_continuity_valid"] is True
    assert certification["replay_continuity_valid"] is True
    assert certification["rollback_continuity_valid"] is True
    assert certification["diagnostics_continuity_valid"] is True
    assert certification["explainability_continuity_valid"] is True
    assert certification["cross_layer_continuity_valid"] is True
    assert certification["provenance_continuity_valid"] is True
    assert certification["lineage_continuity_valid"] is True
    assert certification["replay_continuity_valid"] is True
    assert certification["rollback_continuity_valid"] is True


def test_v4_1_continuity_integrity_enforces_no_remediation_approval_or_execution():
    payload = default_refresh_continuity_certification()
    non_execution = validate_continuity_certification_non_execution(payload)
    integrity = validate_continuity_certification_integrity(payload)

    assert non_execution["valid"] is True
    assert non_execution["remediation_absent"] is True
    assert non_execution["automatic_correction_absent"] is True
    assert non_execution["approval_absent"] is True
    assert non_execution["authorization_absent"] is True
    assert non_execution["refresh_execution_absent"] is True
    assert non_execution["orchestration_absent"] is True
    assert non_execution["planner_integration_absent"] is True
    assert non_execution["production_consumption_absent"] is True
    assert integrity["valid"] is True
    assert integrity["prohibited_leakage_visible"] is True
    assert integrity["non_execution_valid"] is True


def test_v4_1_continuity_diagnostics_and_explainability_are_fail_visible_only():
    payload = default_refresh_continuity_certification()
    diagnostics = build_refresh_continuity_certification_diagnostics(payload)
    unified = build_unified_refresh_continuity_certification(payload)
    cross_layer = build_cross_layer_continuity_diagnostics(payload)
    explainability = build_cross_layer_continuity_explainability(payload)

    assert diagnostics["diagnostics_mode"] == "descriptive_only"
    assert diagnostics["enabled_capability_count"] == 0
    assert unified["certification_mode"] == "descriptive_only_non_authorizing"
    assert cross_layer["diagnostics_mode"] == "fail_visible_descriptive_only"
    assert cross_layer["continuity_failure_visibility_count"] == 10
    assert explainability["explainability_mode"] == "descriptive_only_non_recommending_non_authorizing"
    assert explainability["failure_explanation_count"] == 10
    assert "does not approve operations" in explainability["explanation_texts"][0]


def test_v4_1_continuity_reports_include_required_validation_and_boundary_sections():
    report = build_v4_1_refresh_continuity_certification_report()
    unified = build_v4_1_unified_refresh_continuity_certification_report()
    diagnostics = build_v4_1_cross_layer_continuity_diagnostics_report()
    integrity = build_v4_1_cross_layer_continuity_integrity_certification_report()
    explainability = build_v4_1_cross_layer_continuity_explainability_report()
    summary = report["summary"]

    assert report["foundation_status"] == V4_1_REFRESH_CONTINUITY_CERTIFICATION_STATUS_STABLE
    assert summary["validation_error_count"] == 0
    assert summary["deterministic_continuity_serialization_verified"] is True
    assert summary["deterministic_continuity_hashing_verified"] is True
    assert summary["deterministic_continuity_equality_verified"] is True
    assert summary["deterministic_continuity_visibility_verified"] is True
    assert summary["manifest_continuity_validated"] is True
    assert summary["dependency_continuity_validated"] is True
    assert summary["lineage_continuity_validated"] is True
    assert summary["schema_continuity_validated"] is True
    assert summary["sequencing_continuity_validated"] is True
    assert summary["drift_continuity_validated"] is True
    assert summary["replay_continuity_validated"] is True
    assert summary["rollback_continuity_validated"] is True
    assert summary["diagnostics_continuity_validated"] is True
    assert summary["explainability_continuity_validated"] is True
    assert summary["cross_layer_continuity_aggregation_validated"] is True
    assert summary["unsupported_continuity_state_validated"] is True
    assert summary["blocked_continuity_state_validated"] is True
    assert summary["prohibited_continuity_state_validated"] is True
    assert summary["non_remediation_enforcement_validated"] is True
    assert summary["non_correction_enforcement_validated"] is True
    assert summary["non_approval_authorization_enforcement_validated"] is True
    assert summary["non_execution_enforcement_validated"] is True
    assert summary["production_consumption_disabled_validated"] is True
    assert summary["planner_integration_disabled_validated"] is True
    assert summary["integrity_validation_verified"] is True
    assert summary["certification_validation_verified"] is True
    assert summary["cross_layer_continuity_validation_verified"] is True
    assert "No continuity certification becomes operational authorization." in report["explicit_prohibitions"]
    assert unified["unified_refresh_continuity_certification"]["cross_layer_continuity_valid"] is True
    assert diagnostics["cross_layer_continuity_diagnostics"]["blocked_continuity_state_visible"] is True
    assert integrity["cross_layer_continuity_integrity_certification"]["valid"] is True
    assert "No approval or authorization exists." in explainability["explicit_prohibitions"]


def test_v4_1_continuity_rejects_hidden_execution_semantics():
    payload = default_refresh_continuity_certification()
    compromised = replace(payload, refresh_execution_enabled=True)

    non_execution = validate_continuity_certification_non_execution(compromised)
    integrity = validate_continuity_certification_integrity(compromised)

    assert non_execution["valid"] is False
    assert non_execution["refresh_execution_absent"] is False
    assert integrity["valid"] is False
