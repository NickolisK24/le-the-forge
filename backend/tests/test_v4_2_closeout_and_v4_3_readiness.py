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

from refresh_coordination.v4_2_closeout_readiness_audit import (  # noqa: E402
    aggregate_v4_2_disabled_boundaries,
    aggregate_v4_2_prohibited_capabilities,
    aggregate_v4_2_warnings,
    build_v4_2_closeout_and_v4_3_readiness_report,
    build_v4_2_closeout_diagnostics,
    build_v4_2_closeout_readiness,
    count_v4_2_warning_categories,
    enabled_v4_2_closeout_capability_flags,
    hash_v4_2_closeout_readiness,
    serialize_v4_2_closeout_readiness,
    v4_2_closeout_readiness_equal,
    validate_v4_2_closeout_non_execution,
    validate_v4_2_closeout_readiness,
    validate_v4_2_migration_documentation_inventory,
    validate_v4_2_phase_evidence_coverage,
    validate_v4_2_report_inventory,
)
from refresh_coordination.v4_2_closeout_readiness_models import (  # noqa: E402
    V4_2_CLOSEOUT_CLASSIFICATION_BLOCKED,
    V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS,
    V4_2_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
    V4_2_CLOSEOUT_READINESS_SCHEMA_VERSION,
    V4_2_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_2_EVIDENCE_INVALID_JSON,
    V4_2_EVIDENCE_MISSING,
    V4_2_EXPECTED_MIGRATION_DOC_NAMES,
    V4_2_EXPECTED_PHASE_IDS,
    V4_2_EXPECTED_REPORT_NAMES,
    V4_2_EXPECTED_TEST_NAMES,
    V4_2_PROHIBITED_CAPABILITIES,
    V4_2_WARNING_CATEGORIES,
    V4_3_READINESS_CLASSIFICATION_BLOCKED,
    V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS,
    V4_3_RECOMMENDED_DIRECTION,
)


def test_v4_2_closeout_models_are_immutable_descriptive_and_non_executable():
    closeout = build_v4_2_closeout_readiness()

    with pytest.raises(FrozenInstanceError):
        closeout.runtime_mutation_enabled = True

    assert closeout.identity.schema_version == V4_2_CLOSEOUT_READINESS_SCHEMA_VERSION
    assert closeout.non_executable is True
    assert closeout.descriptive_only is True
    assert closeout.closeout_only is True
    assert closeout.planning_readiness_only is True
    assert closeout.readiness_approval_enabled is False
    assert closeout.operational_authorization_enabled is False
    assert closeout.remediation_enabled is False
    assert closeout.automatic_correction_enabled is False
    assert closeout.routing_execution_enabled is False
    assert closeout.orchestration_execution_enabled is False
    assert closeout.refresh_execution_enabled is False
    assert closeout.sequencing_execution_enabled is False
    assert closeout.scheduling_execution_enabled is False
    assert closeout.dependency_resolution_enabled is False
    assert closeout.planner_integration_enabled is False
    assert closeout.production_consumption_enabled is False
    assert closeout.runtime_mutation_enabled is False
    assert enabled_v4_2_closeout_capability_flags(closeout) == {}


def test_v4_2_closeout_covers_phase_1_9_reports_docs_and_tests():
    closeout = build_v4_2_closeout_readiness()
    phase_coverage = validate_v4_2_phase_evidence_coverage(closeout)
    report_inventory = validate_v4_2_report_inventory(closeout)
    doc_inventory = validate_v4_2_migration_documentation_inventory(closeout)

    assert len(V4_2_EXPECTED_PHASE_IDS) == 9
    assert len(V4_2_EXPECTED_REPORT_NAMES) == 9
    assert len(V4_2_EXPECTED_MIGRATION_DOC_NAMES) == 9
    assert len(V4_2_EXPECTED_TEST_NAMES) == 9
    assert phase_coverage["valid"] is True
    assert phase_coverage["phase_evidence_count"] == 9
    assert report_inventory["valid"] is True
    assert report_inventory["present_report_count"] == 9
    assert doc_inventory["valid"] is True
    assert doc_inventory["present_doc_count"] == 9
    assert all(reference.report_hash for reference in closeout.phase_evidence)


def test_v4_2_closeout_serialization_hashing_and_ordering_are_stable():
    first = build_v4_2_closeout_readiness()
    second = build_v4_2_closeout_readiness()
    reordered = replace(
        first,
        phase_evidence=tuple(reversed(first.phase_evidence)),
        warning_summaries=tuple(reversed(first.warning_summaries)),
        prohibited_capability_summaries=tuple(reversed(first.prohibited_capability_summaries)),
        disabled_boundary_summaries=tuple(reversed(first.disabled_boundary_summaries)),
        deterministic_guarantees=tuple(reversed(first.deterministic_guarantees)),
    )

    assert first == second
    assert hash(first) == hash(second)
    assert v4_2_closeout_readiness_equal(first, second)
    assert v4_2_closeout_readiness_equal(first, reordered)
    assert serialize_v4_2_closeout_readiness(first) == serialize_v4_2_closeout_readiness(second)
    assert serialize_v4_2_closeout_readiness(first) == serialize_v4_2_closeout_readiness(reordered)
    assert hash_v4_2_closeout_readiness(first) == hash_v4_2_closeout_readiness(second)
    assert hash_v4_2_closeout_readiness(first) == hash_v4_2_closeout_readiness(reordered)
    serialized = json.loads(serialize_v4_2_closeout_readiness(first))
    assert [phase["phase_number"] for phase in serialized["phase_evidence"]] == list(range(1, 10))


def test_v4_2_closeout_missing_evidence_is_fail_visible_without_correction():
    missing_report = V4_2_EXPECTED_REPORT_NAMES[0]
    closeout = build_v4_2_closeout_readiness(report_presence_overrides={missing_report: False})
    validation = validate_v4_2_closeout_readiness(closeout)
    diagnostics = build_v4_2_closeout_diagnostics(closeout)

    assert validation["valid"] is False
    assert closeout.report_inventory.complete is False
    assert missing_report in closeout.report_inventory.missing_names
    assert closeout.phase_evidence[0].evidence_status == V4_2_EVIDENCE_MISSING
    assert diagnostics["missing_evidence_visible"] is True
    assert closeout.closeout_classification.closeout_classification == V4_2_CLOSEOUT_CLASSIFICATION_BLOCKED
    assert closeout.v4_3_planning_readiness.readiness_classification == V4_3_READINESS_CLASSIFICATION_BLOCKED
    assert closeout.remediation_enabled is False
    assert closeout.automatic_correction_enabled is False


def test_v4_2_closeout_invalid_report_json_is_fail_visible():
    invalid_report = V4_2_EXPECTED_REPORT_NAMES[1]
    closeout = build_v4_2_closeout_readiness(report_json_validity_overrides={invalid_report: False})
    report_inventory = validate_v4_2_report_inventory(closeout)
    phase_coverage = validate_v4_2_phase_evidence_coverage(closeout)

    assert report_inventory["valid"] is False
    assert invalid_report in report_inventory["invalid_report_names"]
    assert phase_coverage["valid"] is False
    assert closeout.phase_evidence[1].evidence_status == V4_2_EVIDENCE_INVALID_JSON
    assert closeout.remediation_enabled is False
    assert closeout.automatic_correction_enabled is False


def test_v4_2_closeout_warning_aggregation_is_fail_visible_and_descriptive():
    closeout = build_v4_2_closeout_readiness()
    aggregation = aggregate_v4_2_warnings(closeout)
    counts = count_v4_2_warning_categories(closeout.warning_summaries)

    assert aggregation["valid"] is True
    assert aggregation["warning_count"] == len(V4_2_WARNING_CATEGORIES)
    assert aggregation["unresolved_warning_count"] == len(V4_2_WARNING_CATEGORIES)
    assert aggregation["fail_visible"] is True
    assert aggregation["descriptive_only"] is True
    assert aggregation["remediation_enabled"] is False
    assert aggregation["approval_enabled"] is False
    assert aggregation["authorization_enabled"] is False
    assert aggregation["execution_enabled"] is False
    assert all(counts[category] == 1 for category in V4_2_WARNING_CATEGORIES)
    assert counts["invalid"] == 0


def test_v4_2_closeout_prohibited_capabilities_and_disabled_boundaries_are_aggregated():
    closeout = build_v4_2_closeout_readiness()
    prohibited = aggregate_v4_2_prohibited_capabilities(closeout)
    disabled = aggregate_v4_2_disabled_boundaries(closeout)
    non_execution = validate_v4_2_closeout_non_execution(closeout)

    assert prohibited["valid"] is True
    assert prohibited["prohibited_capability_count"] == len(V4_2_PROHIBITED_CAPABILITIES)
    assert prohibited["enabled_capabilities"] == []
    assert disabled["valid"] is True
    assert disabled["enabled_boundaries"] == []
    assert non_execution["valid"] is True
    assert non_execution["readiness_approval_disabled"] is True
    assert non_execution["operational_authorization_disabled"] is True
    assert non_execution["remediation_disabled"] is True
    assert non_execution["orchestration_execution_disabled"] is True
    assert non_execution["refresh_execution_disabled"] is True
    assert non_execution["routing_execution_disabled"] is True
    assert non_execution["sequencing_execution_disabled"] is True
    assert non_execution["scheduling_execution_disabled"] is True
    assert non_execution["dependency_resolution_disabled"] is True
    assert non_execution["planner_integration_disabled"] is True
    assert non_execution["production_consumption_disabled"] is True
    assert non_execution["runtime_mutation_disabled"] is True


def test_v4_2_closeout_and_v4_3_readiness_classifications_are_descriptive_only():
    closeout = build_v4_2_closeout_readiness()
    validation = validate_v4_2_closeout_readiness(closeout)

    assert validation["valid"] is True
    assert validation["foundation_status"] == V4_2_CLOSEOUT_READINESS_STATUS_STABLE
    assert closeout.closeout_classification.closeout_classification == (
        V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS
    )
    assert closeout.v4_3_planning_readiness.readiness_classification == (
        V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS
    )
    assert closeout.v4_3_planning_readiness.recommended_direction == V4_3_RECOMMENDED_DIRECTION
    assert closeout.closeout_classification.operational_authorization_enabled is False
    assert closeout.closeout_classification.readiness_approval_enabled is False
    assert closeout.v4_3_planning_readiness.orchestration_execution_enabled is False
    assert closeout.v4_3_planning_readiness.production_consumption_enabled is False


def test_v4_2_closeout_report_contains_required_sections_and_boundaries():
    report = build_v4_2_closeout_and_v4_3_readiness_report()
    summary = report["summary"]

    assert report["schema_version"] == V4_2_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION
    assert report["foundation_status"] == V4_2_CLOSEOUT_READINESS_STATUS_STABLE
    assert report["recommended_v4_3_direction"] == V4_3_RECOMMENDED_DIRECTION
    assert report["deterministic_serialization_verification"]["stable"] is True
    assert report["deterministic_hashing_verification"]["stable"] is True
    assert report["inventory_validation"]["generated_reports"]["valid"] is True
    assert report["inventory_validation"]["migration_documentation"]["valid"] is True
    assert report["inventory_validation"]["focused_tests"]["valid"] is True
    assert report["warning_aggregation"]["unresolved_warning_count"] == len(V4_2_WARNING_CATEGORIES)
    assert report["non_execution_and_non_authorization_guarantees"]["valid"] is True
    assert summary["v4_2_closeout_classification"] == V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS
    assert summary["v4_3_readiness_classification"] == V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS
    assert summary["phase_1_9_evidence_coverage_validated"] is True
    assert summary["prohibited_capability_aggregation_validated"] is True
    assert summary["disabled_boundary_aggregation_validated"] is True
    assert summary["readiness_approval_disabled"] is True
    assert summary["operational_authorization_disabled"] is True
    assert summary["remediation_disabled"] is True
    assert summary["orchestration_execution_disabled"] is True
    assert summary["refresh_execution_disabled"] is True
    assert summary["routing_execution_disabled"] is True
    assert summary["sequencing_execution_disabled"] is True
    assert summary["scheduling_execution_disabled"] is True
    assert summary["dependency_resolution_disabled"] is True
    assert summary["planner_integration_disabled"] is True
    assert summary["production_consumption_disabled"] is True
    assert summary["runtime_mutation_disabled"] is True
    assert "No readiness approval exists." in report["explicit_prohibitions"]
