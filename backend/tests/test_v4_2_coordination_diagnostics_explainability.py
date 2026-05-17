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

from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_aggregation import (  # noqa: E402
    build_coordination_diagnostics_aggregation,
    coordination_diagnostics_equal,
    count_coordination_diagnostic_states,
    validate_coordination_diagnostic_aggregation,
    validate_coordination_diagnostics_non_execution,
    validate_dependency_graph_diagnostics_compatibility,
    validate_diagnostic_severity_visibility,
    validate_drift_diagnostics_compatibility,
    validate_lineage_diagnostics_compatibility,
    validate_manifest_diagnostics_compatibility,
    validate_routing_diagnostics_compatibility,
    validate_sequencing_diagnostics_compatibility,
)
from refresh_coordination.coordination_diagnostics_hashing import (  # noqa: E402
    hash_coordination_diagnostics_explainability,
    hash_coordination_diagnostics_identity,
    hash_cross_layer_coordination_diagnostic_record,
    hash_state_aggregation_visibility,
)
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    DIAGNOSTIC_AGGREGATION_BLOCKED,
    DIAGNOSTIC_AGGREGATION_CONFLICTING,
    DIAGNOSTIC_AGGREGATION_INFO,
    DIAGNOSTIC_AGGREGATION_MISSING,
    DIAGNOSTIC_AGGREGATION_PROHIBITED,
    DIAGNOSTIC_AGGREGATION_STALE,
    DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
    V4_2_COORDINATION_DIAGNOSTICS_SCHEMA_VERSION,
    V4_2_COORDINATION_DIAGNOSTICS_STATUS_STABLE,
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_diagnostics_serialization import (  # noqa: E402
    export_coordination_diagnostics_explainability,
    serialize_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_explainability import (  # noqa: E402
    build_coordination_explainability_evidence,
    validate_fail_visible_explanation_summary,
)
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402
from scripts.report_v4_2_coordination_diagnostics_explainability import (  # noqa: E402
    build_v4_2_coordination_diagnostics_explainability_report,
)


def test_v4_2_coordination_diagnostics_models_are_immutable_and_non_executable():
    diagnostics = default_coordination_diagnostics_explainability()

    with pytest.raises(FrozenInstanceError):
        diagnostics.remediation_enabled = True

    assert diagnostics.identity.schema_version == V4_2_COORDINATION_DIAGNOSTICS_SCHEMA_VERSION
    assert diagnostics.non_executable is True
    assert diagnostics.descriptive_only is True
    assert diagnostics.non_remediating is True
    assert diagnostics.remediation_enabled is False
    assert diagnostics.automatic_correction_enabled is False
    assert diagnostics.drift_correction_enabled is False
    assert diagnostics.routing_execution_enabled is False
    assert diagnostics.orchestration_execution_enabled is False
    assert diagnostics.refresh_execution_enabled is False
    assert diagnostics.dependency_resolution_enabled is False
    assert diagnostics.planner_integration_enabled is False
    assert diagnostics.production_consumption_enabled is False
    assert diagnostics.runtime_mutation_enabled is False
    assert all(not record.remediation_enabled for record in diagnostics.diagnostic_records)
    assert all(not explanation.automatic_correction_enabled for explanation in diagnostics.explanation_records)


def test_v4_2_coordination_diagnostics_serialization_and_hashing_are_stable():
    first = default_coordination_diagnostics_explainability()
    second = default_coordination_diagnostics_explainability()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_diagnostics_equal(first, second)
    assert serialize_coordination_diagnostics_explainability(first) == serialize_coordination_diagnostics_explainability(second)
    assert hash_coordination_diagnostics_explainability(first) == hash_coordination_diagnostics_explainability(second)
    assert hash_coordination_diagnostics_identity(first.identity) == hash_coordination_diagnostics_identity(second.identity)
    assert json.loads(serialize_coordination_diagnostics_explainability(first))["non_executable"] is True


def test_v4_2_coordination_diagnostic_ordering_is_stable():
    diagnostics = default_coordination_diagnostics_explainability()
    reordered = replace(
        diagnostics,
        manifest_diagnostic_references=tuple(reversed(diagnostics.manifest_diagnostic_references)),
        dependency_graph_diagnostic_references=tuple(reversed(diagnostics.dependency_graph_diagnostic_references)),
        lineage_diagnostic_references=tuple(reversed(diagnostics.lineage_diagnostic_references)),
        sequencing_diagnostic_references=tuple(reversed(diagnostics.sequencing_diagnostic_references)),
        routing_diagnostic_references=tuple(reversed(diagnostics.routing_diagnostic_references)),
        drift_diagnostic_references=tuple(reversed(diagnostics.drift_diagnostic_references)),
        diagnostic_records=tuple(reversed(diagnostics.diagnostic_records)),
        severity_visibility=tuple(reversed(diagnostics.severity_visibility)),
        explanation_records=tuple(reversed(diagnostics.explanation_records)),
    )

    assert serialize_coordination_diagnostics_explainability(diagnostics) == serialize_coordination_diagnostics_explainability(reordered)
    assert hash_coordination_diagnostics_explainability(diagnostics) == hash_coordination_diagnostics_explainability(reordered)
    exported = export_coordination_diagnostics_explainability(reordered)
    assert [record["aggregation_state"] for record in exported["diagnostic_records"]] == [
        DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
        DIAGNOSTIC_AGGREGATION_PROHIBITED,
        DIAGNOSTIC_AGGREGATION_BLOCKED,
        DIAGNOSTIC_AGGREGATION_STALE,
        DIAGNOSTIC_AGGREGATION_MISSING,
        DIAGNOSTIC_AGGREGATION_CONFLICTING,
        DIAGNOSTIC_AGGREGATION_INFO,
    ]


def test_v4_2_coordination_diagnostics_hashes_records_and_aggregations_deterministically():
    diagnostics = default_coordination_diagnostics_explainability()

    assert [hash_cross_layer_coordination_diagnostic_record(record) for record in diagnostics.diagnostic_records] == [
        hash_cross_layer_coordination_diagnostic_record(record) for record in diagnostics.diagnostic_records
    ]
    assert hash_state_aggregation_visibility(diagnostics.unsupported_state_aggregation) == hash_state_aggregation_visibility(
        diagnostics.unsupported_state_aggregation
    )


def test_v4_2_coordination_diagnostics_are_compatible_with_all_v4_2_layers():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    drift = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    diagnostics = default_coordination_diagnostics_explainability(manifest, graph, lineage, sequencing, routing, drift)

    manifest_compatibility = validate_manifest_diagnostics_compatibility(diagnostics, manifest)
    graph_compatibility = validate_dependency_graph_diagnostics_compatibility(diagnostics, graph, manifest)
    lineage_compatibility = validate_lineage_diagnostics_compatibility(diagnostics, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_diagnostics_compatibility(
        diagnostics,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    routing_compatibility = validate_routing_diagnostics_compatibility(
        diagnostics,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    drift_compatibility = validate_drift_diagnostics_compatibility(
        diagnostics,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )

    assert manifest_compatibility["valid"] is True
    assert manifest_compatibility["manifest_hash_matches"] is True
    assert graph_compatibility["valid"] is True
    assert graph_compatibility["dependency_graph_hash_matches"] is True
    assert lineage_compatibility["valid"] is True
    assert lineage_compatibility["lineage_chain_hash_matches"] is True
    assert sequencing_compatibility["valid"] is True
    assert sequencing_compatibility["sequencing_hash_matches"] is True
    assert routing_compatibility["valid"] is True
    assert routing_compatibility["routing_hash_matches"] is True
    assert drift_compatibility["valid"] is True
    assert drift_compatibility["drift_hash_matches"] is True


def test_v4_2_coordination_diagnostics_aggregate_fail_visible_states():
    diagnostics = default_coordination_diagnostics_explainability()
    aggregation = validate_coordination_diagnostic_aggregation(diagnostics)
    counts = count_coordination_diagnostic_states(diagnostics.diagnostic_records)

    assert counts[DIAGNOSTIC_AGGREGATION_UNSUPPORTED] == 1
    assert counts[DIAGNOSTIC_AGGREGATION_PROHIBITED] == 1
    assert counts[DIAGNOSTIC_AGGREGATION_BLOCKED] == 1
    assert counts[DIAGNOSTIC_AGGREGATION_STALE] == 1
    assert counts[DIAGNOSTIC_AGGREGATION_MISSING] == 1
    assert counts[DIAGNOSTIC_AGGREGATION_CONFLICTING] == 1
    assert aggregation["valid"] is True
    assert aggregation["unsupported_state_visible"] is True
    assert aggregation["prohibited_state_visible"] is True
    assert aggregation["blocked_state_visible"] is True
    assert aggregation["stale_state_visible"] is True
    assert aggregation["missing_state_visible"] is True
    assert aggregation["conflicting_state_visible"] is True
    assert aggregation["hidden_count"] == 0
    assert aggregation["corrective_count"] == 0


def test_v4_2_coordination_explainability_summarizes_fail_visible_records():
    diagnostics = default_coordination_diagnostics_explainability()
    summary = validate_fail_visible_explanation_summary(diagnostics)
    evidence = build_coordination_explainability_evidence(diagnostics)
    severity = validate_diagnostic_severity_visibility(diagnostics)

    assert summary["valid"] is True
    assert len(summary["fail_visible_record_ids"]) == 6
    assert summary["corrective_count"] == 0
    assert evidence["summary_validation"]["valid"] is True
    assert evidence["fail_visible_explanation_count"] == 6
    assert severity["valid"] is True


def test_v4_2_coordination_diagnostics_non_execution_validation_blocks_forbidden_flags():
    diagnostics = default_coordination_diagnostics_explainability()
    contaminated = replace(
        diagnostics,
        remediation_enabled=True,
        automatic_correction_enabled=True,
        drift_correction_enabled=True,
        drift_remediation_enabled=True,
        routing_execution_enabled=True,
        orchestration_execution_enabled=True,
        refresh_execution_enabled=True,
        sequencing_execution_enabled=True,
        scheduling_execution_enabled=True,
        dependency_resolution_enabled=True,
        lineage_repair_enabled=True,
        lineage_inference_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
        automatic_rollback_enabled=True,
        ranking_enabled=True,
        scoring_enabled=True,
        selection_enabled=True,
        authorization_enabled=True,
        approval_enabled=True,
    )
    validation = validate_coordination_diagnostics_non_execution(contaminated)

    assert validate_coordination_diagnostics_non_execution(diagnostics)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 21
    assert validation["remediation_disabled"] is False
    assert validation["automatic_correction_disabled"] is False
    assert validation["drift_correction_disabled"] is False
    assert validation["routing_execution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_diagnostics_report_contains_required_evidence_and_boundaries():
    aggregation = build_coordination_diagnostics_aggregation()
    report = build_v4_2_coordination_diagnostics_explainability_report()

    assert report["diagnostics_status"] == V4_2_COORDINATION_DIAGNOSTICS_STATUS_STABLE
    assert report["diagnostics_mode"] == "descriptive_only_non_executable_non_remediating"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_diagnostic_ordering_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["lineage_chain_compatibility_verified"] is True
    assert report["summary"]["sequencing_compatibility_verified"] is True
    assert report["summary"]["routing_compatibility_verified"] is True
    assert report["summary"]["drift_compatibility_verified"] is True
    assert report["summary"]["unsupported_aggregation_verified"] is True
    assert report["summary"]["prohibited_aggregation_verified"] is True
    assert report["summary"]["blocked_aggregation_verified"] is True
    assert report["summary"]["stale_aggregation_verified"] is True
    assert report["summary"]["missing_aggregation_verified"] is True
    assert report["summary"]["conflicting_aggregation_verified"] is True
    assert report["summary"]["fail_visible_explanation_summary_verified"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["automatic_correction_disabled"] is True
    assert report["summary"]["drift_correction_disabled"] is True
    assert report["summary"]["routing_execution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert aggregation["enabled_capability_count"] == 0
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No drift correction exists." in report["explicit_prohibitions"]
    assert "No routing execution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
