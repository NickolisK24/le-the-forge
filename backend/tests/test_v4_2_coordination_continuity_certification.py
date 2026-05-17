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

from refresh_coordination.coordination_continuity_certification import (  # noqa: E402
    build_coordination_continuity_certification_evidence,
    validate_descriptive_only_coordination_continuity_certification,
)
from refresh_coordination.coordination_continuity_diagnostics import (  # noqa: E402
    build_coordination_continuity_diagnostics,
    coordination_continuity_certifications_equal,
    count_coordination_continuity_states,
    validate_coordination_continuity_non_execution,
    validate_coordination_continuity_visibility,
    validate_dependency_graph_continuity_compatibility,
    validate_diagnostics_explainability_continuity_compatibility,
    validate_drift_continuity_compatibility,
    validate_lineage_continuity_compatibility,
    validate_manifest_continuity_compatibility,
    validate_routing_continuity_compatibility,
    validate_sequencing_continuity_compatibility,
    validate_cross_layer_continuity_summary,
)
from refresh_coordination.coordination_continuity_hashing import (  # noqa: E402
    hash_continuity_state_visibility,
    hash_coordination_continuity_certification,
    hash_coordination_continuity_identity,
    hash_cross_layer_coordination_continuity_record,
)
from refresh_coordination.coordination_continuity_models import (  # noqa: E402
    CONTINUITY_STATE_CONFLICTING,
    CONTINUITY_STATE_CROSS_LAYER,
    CONTINUITY_STATE_MISSING,
    CONTINUITY_STATE_PROHIBITED_REPAIR,
    CONTINUITY_STATE_STABLE,
    CONTINUITY_STATE_STALE,
    CONTINUITY_STATE_UNSUPPORTED_TRANSITION,
    V4_2_COORDINATION_CONTINUITY_SCHEMA_VERSION,
    V4_2_COORDINATION_CONTINUITY_STATUS_STABLE,
    default_coordination_continuity_certification,
)
from refresh_coordination.coordination_continuity_serialization import (  # noqa: E402
    export_coordination_continuity_certification,
    serialize_coordination_continuity_certification,
)
from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402
from scripts.report_v4_2_coordination_continuity_certification import (  # noqa: E402
    build_v4_2_coordination_continuity_certification_report,
)


def test_v4_2_coordination_continuity_models_are_immutable_and_non_executable():
    certification = default_coordination_continuity_certification()

    with pytest.raises(FrozenInstanceError):
        certification.continuity_repair_enabled = True

    assert certification.identity.schema_version == V4_2_COORDINATION_CONTINUITY_SCHEMA_VERSION
    assert certification.non_executable is True
    assert certification.descriptive_only is True
    assert certification.non_remediating is True
    assert certification.non_repairing is True
    assert certification.non_inferring is True
    assert certification.continuity_repair_enabled is False
    assert certification.continuity_inference_enabled is False
    assert certification.remediation_enabled is False
    assert certification.automatic_correction_enabled is False
    assert certification.drift_correction_enabled is False
    assert certification.routing_execution_enabled is False
    assert certification.orchestration_execution_enabled is False
    assert certification.refresh_execution_enabled is False
    assert certification.dependency_resolution_enabled is False
    assert certification.planner_integration_enabled is False
    assert certification.production_consumption_enabled is False
    assert certification.runtime_mutation_enabled is False
    assert all(not record.continuity_repair_enabled for record in certification.continuity_records)
    assert all(not diagnostic.remediation_enabled for diagnostic in certification.diagnostics)


def test_v4_2_coordination_continuity_serialization_and_hashing_are_stable():
    first = default_coordination_continuity_certification()
    second = default_coordination_continuity_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_continuity_certifications_equal(first, second)
    assert serialize_coordination_continuity_certification(first) == serialize_coordination_continuity_certification(
        second
    )
    assert hash_coordination_continuity_certification(first) == hash_coordination_continuity_certification(second)
    assert hash_coordination_continuity_identity(first.identity) == hash_coordination_continuity_identity(
        second.identity
    )
    assert json.loads(serialize_coordination_continuity_certification(first))["non_executable"] is True


def test_v4_2_coordination_continuity_ordering_is_stable():
    certification = default_coordination_continuity_certification()
    reordered = replace(
        certification,
        manifest_continuity_references=tuple(reversed(certification.manifest_continuity_references)),
        dependency_graph_continuity_references=tuple(
            reversed(certification.dependency_graph_continuity_references)
        ),
        lineage_continuity_references=tuple(reversed(certification.lineage_continuity_references)),
        sequencing_continuity_references=tuple(reversed(certification.sequencing_continuity_references)),
        routing_continuity_references=tuple(reversed(certification.routing_continuity_references)),
        drift_continuity_references=tuple(reversed(certification.drift_continuity_references)),
        diagnostics_continuity_references=tuple(reversed(certification.diagnostics_continuity_references)),
        explainability_continuity_references=tuple(
            reversed(certification.explainability_continuity_references)
        ),
        continuity_records=tuple(reversed(certification.continuity_records)),
        diagnostics=tuple(reversed(certification.diagnostics)),
    )

    assert serialize_coordination_continuity_certification(certification) == serialize_coordination_continuity_certification(
        reordered
    )
    assert hash_coordination_continuity_certification(certification) == hash_coordination_continuity_certification(
        reordered
    )
    exported = export_coordination_continuity_certification(reordered)
    assert [record["continuity_state"] for record in exported["continuity_records"]] == [
        CONTINUITY_STATE_STABLE,
        CONTINUITY_STATE_STALE,
        CONTINUITY_STATE_MISSING,
        CONTINUITY_STATE_CONFLICTING,
        CONTINUITY_STATE_PROHIBITED_REPAIR,
        CONTINUITY_STATE_UNSUPPORTED_TRANSITION,
        CONTINUITY_STATE_CROSS_LAYER,
    ]


def test_v4_2_coordination_continuity_hashes_records_and_visibility_deterministically():
    certification = default_coordination_continuity_certification()

    assert [
        hash_cross_layer_coordination_continuity_record(record)
        for record in certification.continuity_records
    ] == [
        hash_cross_layer_coordination_continuity_record(record)
        for record in certification.continuity_records
    ]
    assert hash_continuity_state_visibility(certification.stale_continuity_visibility) == hash_continuity_state_visibility(
        certification.stale_continuity_visibility
    )


def test_v4_2_coordination_continuity_is_compatible_with_all_v4_2_layers():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    drift = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    diagnostics = default_coordination_diagnostics_explainability(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
    )
    certification = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )

    assert validate_manifest_continuity_compatibility(certification, manifest)["valid"] is True
    assert validate_dependency_graph_continuity_compatibility(certification, graph, manifest)["valid"] is True
    assert validate_lineage_continuity_compatibility(certification, lineage, graph, manifest)["valid"] is True
    assert validate_sequencing_continuity_compatibility(
        certification,
        sequencing,
        lineage,
        graph,
        manifest,
    )["valid"] is True
    assert validate_routing_continuity_compatibility(
        certification,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )["valid"] is True
    assert validate_drift_continuity_compatibility(
        certification,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )["valid"] is True
    assert validate_diagnostics_explainability_continuity_compatibility(
        certification,
        diagnostics,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )["valid"] is True


def test_v4_2_coordination_continuity_fail_visible_states_are_aggregated():
    certification = default_coordination_continuity_certification()
    visibility = validate_coordination_continuity_visibility(certification)
    counts = count_coordination_continuity_states(certification.continuity_records)

    assert counts[CONTINUITY_STATE_STALE] == 1
    assert counts[CONTINUITY_STATE_MISSING] == 1
    assert counts[CONTINUITY_STATE_CONFLICTING] == 1
    assert counts[CONTINUITY_STATE_PROHIBITED_REPAIR] == 1
    assert counts[CONTINUITY_STATE_UNSUPPORTED_TRANSITION] == 1
    assert visibility["valid"] is True
    assert visibility["stale_continuity_visible"] is True
    assert visibility["missing_continuity_visible"] is True
    assert visibility["conflicting_continuity_visible"] is True
    assert visibility["prohibited_repair_visible"] is True
    assert visibility["unsupported_transition_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_continuity_cross_layer_summary_is_descriptive_only():
    certification = default_coordination_continuity_certification()
    summary = validate_cross_layer_continuity_summary(certification)
    evidence = build_coordination_continuity_certification_evidence(certification)
    diagnostics = build_coordination_continuity_diagnostics(certification)

    assert summary["valid"] is True
    assert summary["cross_layer_continuity_visible"] is True
    assert evidence["descriptive_only_validation"]["valid"] is True
    assert evidence["fail_visible_record_count"] == 6
    assert diagnostics["cross_layer_summary_validation"]["valid"] is True
    assert diagnostics["enabled_capability_count"] == 0


def test_v4_2_coordination_continuity_non_execution_validation_blocks_forbidden_flags():
    certification = default_coordination_continuity_certification()
    contaminated = replace(
        certification,
        continuity_repair_enabled=True,
        continuity_inference_enabled=True,
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
    validation = validate_coordination_continuity_non_execution(contaminated)

    assert validate_coordination_continuity_non_execution(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 23
    assert validation["continuity_repair_disabled"] is False
    assert validation["continuity_inference_disabled"] is False
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


def test_v4_2_coordination_continuity_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_continuity_diagnostics()
    report = build_v4_2_coordination_continuity_certification_report()

    assert report["continuity_status"] == V4_2_COORDINATION_CONTINUITY_STATUS_STABLE
    assert report["continuity_mode"] == "descriptive_only_non_executable_non_remediating_non_repairing"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_continuity_ordering_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["lineage_chain_compatibility_verified"] is True
    assert report["summary"]["sequencing_compatibility_verified"] is True
    assert report["summary"]["routing_compatibility_verified"] is True
    assert report["summary"]["drift_compatibility_verified"] is True
    assert report["summary"]["diagnostics_explainability_compatibility_verified"] is True
    assert report["summary"]["stale_continuity_verified"] is True
    assert report["summary"]["missing_continuity_verified"] is True
    assert report["summary"]["conflicting_continuity_verified"] is True
    assert report["summary"]["prohibited_repair_verified"] is True
    assert report["summary"]["unsupported_transition_verified"] is True
    assert report["summary"]["cross_layer_summary_verified"] is True
    assert report["summary"]["continuity_repair_disabled"] is True
    assert report["summary"]["continuity_inference_disabled"] is True
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
    assert diagnostics["enabled_capability_count"] == 0
    assert "No continuity repair exists." in report["explicit_prohibitions"]
    assert "No continuity inference exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No drift correction exists." in report["explicit_prohibitions"]
    assert "No routing execution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
