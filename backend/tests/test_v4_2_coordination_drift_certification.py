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
from refresh_coordination.coordination_drift_diagnostics import (  # noqa: E402
    build_coordination_drift_diagnostics,
    coordination_drift_certifications_equal,
    count_coordination_drift_states,
    validate_coordination_drift_non_execution,
    validate_coordination_drift_visibility,
    validate_cross_layer_drift_visibility,
    validate_dependency_graph_drift_compatibility,
    validate_lineage_drift_compatibility,
    validate_manifest_drift_compatibility,
    validate_routing_drift_compatibility,
    validate_sequencing_drift_compatibility,
)
from refresh_coordination.coordination_drift_hashing import (  # noqa: E402
    hash_coordination_drift_certification,
    hash_coordination_drift_identity,
    hash_coordination_drift_record,
    hash_manifest_drift_reference,
)
from refresh_coordination.coordination_drift_models import (  # noqa: E402
    DRIFT_STATE_CONFLICTING,
    DRIFT_STATE_CROSS_LAYER,
    DRIFT_STATE_MISSING,
    DRIFT_STATE_PROHIBITED_CORRECTION,
    DRIFT_STATE_STABLE,
    DRIFT_STATE_STALE,
    DRIFT_STATE_UNSUPPORTED_TRANSITION,
    V4_2_COORDINATION_DRIFT_SCHEMA_VERSION,
    V4_2_COORDINATION_DRIFT_STATUS_STABLE,
    default_coordination_drift_certification,
)
from refresh_coordination.coordination_drift_serialization import (  # noqa: E402
    export_coordination_drift_certification,
    serialize_coordination_drift_certification,
)
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402
from scripts.report_v4_2_coordination_drift_certification import (  # noqa: E402
    build_v4_2_coordination_drift_certification_report,
)


def test_v4_2_coordination_drift_models_are_immutable_and_non_executable():
    certification = default_coordination_drift_certification()

    with pytest.raises(FrozenInstanceError):
        certification.drift_correction_enabled = True

    assert certification.identity.schema_version == V4_2_COORDINATION_DRIFT_SCHEMA_VERSION
    assert certification.non_executable is True
    assert certification.descriptive_only is True
    assert certification.non_remediating is True
    assert certification.drift_correction_enabled is False
    assert certification.drift_remediation_enabled is False
    assert certification.routing_execution_enabled is False
    assert certification.orchestration_execution_enabled is False
    assert certification.refresh_execution_enabled is False
    assert certification.dependency_resolution_enabled is False
    assert certification.planner_integration_enabled is False
    assert certification.production_consumption_enabled is False
    assert certification.runtime_mutation_enabled is False
    assert all(not record.drift_correction_enabled for record in certification.drift_records)
    assert all(not diagnostic.execution_enabled for diagnostic in certification.diagnostics)


def test_v4_2_coordination_drift_serialization_and_hashing_are_stable():
    first = default_coordination_drift_certification()
    second = default_coordination_drift_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_drift_certifications_equal(first, second)
    assert serialize_coordination_drift_certification(first) == serialize_coordination_drift_certification(second)
    assert hash_coordination_drift_certification(first) == hash_coordination_drift_certification(second)
    assert hash_coordination_drift_identity(first.identity) == hash_coordination_drift_identity(second.identity)
    assert json.loads(serialize_coordination_drift_certification(first))["non_executable"] is True


def test_v4_2_coordination_drift_ordering_is_stable():
    certification = default_coordination_drift_certification()
    reordered = replace(
        certification,
        manifest_drift_references=tuple(reversed(certification.manifest_drift_references)),
        dependency_graph_drift_references=tuple(reversed(certification.dependency_graph_drift_references)),
        lineage_drift_references=tuple(reversed(certification.lineage_drift_references)),
        sequencing_drift_references=tuple(reversed(certification.sequencing_drift_references)),
        routing_drift_references=tuple(reversed(certification.routing_drift_references)),
        drift_records=tuple(reversed(certification.drift_records)),
        diagnostics=tuple(reversed(certification.diagnostics)),
    )

    assert serialize_coordination_drift_certification(certification) == serialize_coordination_drift_certification(reordered)
    assert hash_coordination_drift_certification(certification) == hash_coordination_drift_certification(reordered)
    exported = export_coordination_drift_certification(reordered)
    assert [record["drift_state"] for record in exported["drift_records"]] == [
        DRIFT_STATE_STABLE,
        DRIFT_STATE_STABLE,
        DRIFT_STATE_STABLE,
        DRIFT_STATE_STABLE,
        DRIFT_STATE_STABLE,
        DRIFT_STATE_STALE,
        DRIFT_STATE_MISSING,
        DRIFT_STATE_CONFLICTING,
        DRIFT_STATE_PROHIBITED_CORRECTION,
        DRIFT_STATE_UNSUPPORTED_TRANSITION,
        DRIFT_STATE_CROSS_LAYER,
    ]


def test_v4_2_coordination_drift_hashes_records_and_references_deterministically():
    certification = default_coordination_drift_certification()

    assert [hash_coordination_drift_record(record) for record in certification.drift_records] == [
        hash_coordination_drift_record(record) for record in certification.drift_records
    ]
    assert [hash_manifest_drift_reference(reference) for reference in certification.manifest_drift_references] == [
        hash_manifest_drift_reference(reference) for reference in certification.manifest_drift_references
    ]


def test_v4_2_coordination_drift_visibility_preserves_fail_visible_states():
    certification = default_coordination_drift_certification()
    visibility = validate_coordination_drift_visibility(certification)
    counts = count_coordination_drift_states(certification.drift_records)

    assert counts[DRIFT_STATE_STALE] == 1
    assert counts[DRIFT_STATE_MISSING] == 1
    assert counts[DRIFT_STATE_CONFLICTING] == 1
    assert counts[DRIFT_STATE_PROHIBITED_CORRECTION] == 1
    assert counts[DRIFT_STATE_UNSUPPORTED_TRANSITION] == 1
    assert counts[DRIFT_STATE_CROSS_LAYER] == 1
    assert visibility["valid"] is True
    assert visibility["stale_drift_visible"] is True
    assert visibility["missing_drift_visible"] is True
    assert visibility["conflicting_drift_visible"] is True
    assert visibility["prohibited_correction_visible"] is True
    assert visibility["unsupported_transition_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_drift_cross_layer_visibility_is_descriptive_only():
    certification = default_coordination_drift_certification()
    cross_layer = validate_cross_layer_drift_visibility(certification)

    with pytest.raises(FrozenInstanceError):
        certification.cross_layer_drift_visibility.drift_correction_enabled = True

    assert cross_layer["valid"] is True
    assert cross_layer["cross_layer_drift_visible"] is True
    assert cross_layer["involved_layers_visible"] is True
    assert cross_layer["corrective_count"] == 0
    assert "sequencing->governance_routing" in cross_layer["layer_pairs"]


def test_v4_2_coordination_drift_is_compatible_with_manifest_graph_lineage_sequence_and_routing():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    certification = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)

    manifest_compatibility = validate_manifest_drift_compatibility(certification, manifest)
    graph_compatibility = validate_dependency_graph_drift_compatibility(certification, graph, manifest)
    lineage_compatibility = validate_lineage_drift_compatibility(certification, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_drift_compatibility(
        certification,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    routing_compatibility = validate_routing_drift_compatibility(
        certification,
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


def test_v4_2_coordination_drift_non_execution_validation_blocks_forbidden_flags():
    certification = default_coordination_drift_certification()
    contaminated = replace(
        certification,
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
        remediation_enabled=True,
        runtime_mutation_enabled=True,
        automatic_correction_enabled=True,
        automatic_rollback_enabled=True,
    )
    validation = validate_coordination_drift_non_execution(contaminated)

    assert validate_coordination_drift_non_execution(certification)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 16
    assert validation["drift_correction_disabled"] is False
    assert validation["drift_remediation_disabled"] is False
    assert validation["routing_execution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_drift_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_drift_diagnostics()
    report = build_v4_2_coordination_drift_certification_report()

    assert report["certification_status"] == V4_2_COORDINATION_DRIFT_STATUS_STABLE
    assert report["certification_mode"] == "descriptive_only_non_executable_non_remediating"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_drift_ordering_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["lineage_chain_compatibility_verified"] is True
    assert report["summary"]["sequencing_compatibility_verified"] is True
    assert report["summary"]["routing_compatibility_verified"] is True
    assert report["summary"]["stale_drift_visibility_verified"] is True
    assert report["summary"]["missing_drift_visibility_verified"] is True
    assert report["summary"]["conflicting_drift_visibility_verified"] is True
    assert report["summary"]["prohibited_correction_visibility_verified"] is True
    assert report["summary"]["unsupported_transition_visibility_verified"] is True
    assert report["summary"]["cross_layer_drift_visibility_verified"] is True
    assert report["summary"]["drift_correction_disabled"] is True
    assert report["summary"]["drift_remediation_disabled"] is True
    assert report["summary"]["routing_execution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No drift correction exists." in report["explicit_prohibitions"]
    assert "No drift remediation exists." in report["explicit_prohibitions"]
    assert "No routing execution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
