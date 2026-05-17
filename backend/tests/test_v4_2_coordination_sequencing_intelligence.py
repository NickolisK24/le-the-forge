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
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_diagnostics import (  # noqa: E402
    build_coordination_sequencing_diagnostics,
    coordination_sequencing_intelligence_equal,
    count_coordination_sequence_states,
    validate_coordination_dependency_graph_sequence_compatibility,
    validate_coordination_lineage_chain_sequence_compatibility,
    validate_coordination_manifest_sequence_compatibility,
    validate_coordination_sequence_visibility,
    validate_coordination_sequencing_non_execution,
    validate_non_executable_sequence_ordering,
)
from refresh_coordination.coordination_sequencing_hashing import (  # noqa: E402
    hash_coordination_sequence_record,
    hash_coordination_sequencing_identity,
    hash_coordination_sequencing_intelligence,
    hash_sequence_step_identity,
)
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    SEQUENCE_STATE_BLOCKED,
    SEQUENCE_STATE_CONFLICTING,
    SEQUENCE_STATE_MISSING,
    SEQUENCE_STATE_PROHIBITED,
    SEQUENCE_STATE_STABLE,
    SEQUENCE_STATE_STALE,
    SEQUENCE_STATE_UNSUPPORTED,
    V4_2_COORDINATION_SEQUENCING_SCHEMA_VERSION,
    V4_2_COORDINATION_SEQUENCING_STATUS_STABLE,
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.coordination_sequencing_serialization import (  # noqa: E402
    export_coordination_sequencing_intelligence,
    serialize_coordination_sequencing_intelligence,
)
from scripts.report_v4_2_coordination_sequencing_intelligence import (  # noqa: E402
    build_v4_2_coordination_sequencing_intelligence_report,
)


def test_v4_2_coordination_sequencing_models_are_immutable_and_non_executable():
    sequencing = default_coordination_sequencing_intelligence()

    with pytest.raises(FrozenInstanceError):
        sequencing.scheduling_execution_enabled = True

    assert sequencing.identity.schema_version == V4_2_COORDINATION_SEQUENCING_SCHEMA_VERSION
    assert sequencing.non_executable is True
    assert sequencing.descriptive_only is True
    assert sequencing.sequencing_execution_enabled is False
    assert sequencing.scheduling_execution_enabled is False
    assert sequencing.dependency_resolution_enabled is False
    assert sequencing.lineage_repair_enabled is False
    assert sequencing.lineage_inference_enabled is False
    assert sequencing.orchestration_execution_enabled is False
    assert sequencing.refresh_execution_enabled is False
    assert sequencing.planner_integration_enabled is False
    assert sequencing.production_consumption_enabled is False
    assert sequencing.production_bundle_consumption_enabled is False
    assert sequencing.runtime_mutation_enabled is False
    assert sequencing.remediation_enabled is False
    assert all(not record.sequencing_execution_enabled for record in sequencing.sequence_records)
    assert all(not record.scheduling_execution_enabled for record in sequencing.sequence_records)
    assert all(not diagnostic.execution_enabled for diagnostic in sequencing.diagnostics)


def test_v4_2_coordination_sequencing_serialization_and_hashing_are_stable():
    first = default_coordination_sequencing_intelligence()
    second = default_coordination_sequencing_intelligence()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_sequencing_intelligence_equal(first, second)
    assert serialize_coordination_sequencing_intelligence(first) == serialize_coordination_sequencing_intelligence(
        second
    )
    assert hash_coordination_sequencing_intelligence(first) == hash_coordination_sequencing_intelligence(second)
    assert hash_coordination_sequencing_identity(first.identity) == hash_coordination_sequencing_identity(
        second.identity
    )
    assert json.loads(serialize_coordination_sequencing_intelligence(first))["non_executable"] is True


def test_v4_2_coordination_sequencing_ordering_is_stable():
    sequencing = default_coordination_sequencing_intelligence()
    reordered = replace(
        sequencing,
        step_identities=tuple(reversed(sequencing.step_identities)),
        manifest_sequence_references=tuple(reversed(sequencing.manifest_sequence_references)),
        dependency_graph_sequence_references=tuple(reversed(sequencing.dependency_graph_sequence_references)),
        lineage_sequence_references=tuple(reversed(sequencing.lineage_sequence_references)),
        sequence_records=tuple(reversed(sequencing.sequence_records)),
        diagnostics=tuple(reversed(sequencing.diagnostics)),
    )

    assert serialize_coordination_sequencing_intelligence(sequencing) == serialize_coordination_sequencing_intelligence(
        reordered
    )
    assert hash_coordination_sequencing_intelligence(sequencing) == hash_coordination_sequencing_intelligence(reordered)
    exported = export_coordination_sequencing_intelligence(reordered)
    assert [record["sequence_state"] for record in exported["sequence_records"]] == [
        SEQUENCE_STATE_STABLE,
        SEQUENCE_STATE_STABLE,
        SEQUENCE_STATE_STABLE,
        SEQUENCE_STATE_BLOCKED,
        SEQUENCE_STATE_PROHIBITED,
        SEQUENCE_STATE_UNSUPPORTED,
        SEQUENCE_STATE_STALE,
        SEQUENCE_STATE_MISSING,
        SEQUENCE_STATE_CONFLICTING,
    ]


def test_v4_2_coordination_sequencing_hashes_steps_and_records_deterministically():
    sequencing = default_coordination_sequencing_intelligence()

    assert [hash_sequence_step_identity(step) for step in sequencing.step_identities] == [
        hash_sequence_step_identity(step) for step in sequencing.step_identities
    ]
    assert [hash_coordination_sequence_record(record) for record in sequencing.sequence_records] == [
        hash_coordination_sequence_record(record) for record in sequencing.sequence_records
    ]


def test_v4_2_coordination_sequence_visibility_preserves_all_fail_visible_states():
    sequencing = default_coordination_sequencing_intelligence()
    visibility = validate_coordination_sequence_visibility(sequencing)
    counts = count_coordination_sequence_states(sequencing.sequence_records)

    assert counts[SEQUENCE_STATE_BLOCKED] == 1
    assert counts[SEQUENCE_STATE_PROHIBITED] == 1
    assert counts[SEQUENCE_STATE_UNSUPPORTED] == 1
    assert counts[SEQUENCE_STATE_STALE] == 1
    assert counts[SEQUENCE_STATE_MISSING] == 1
    assert counts[SEQUENCE_STATE_CONFLICTING] == 1
    assert visibility["valid"] is True
    assert visibility["blocked_sequences_visible"] is True
    assert visibility["prohibited_sequences_visible"] is True
    assert visibility["unsupported_sequences_visible"] is True
    assert visibility["stale_sequences_visible"] is True
    assert visibility["missing_sequences_visible"] is True
    assert visibility["conflicting_sequences_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_sequence_ordering_is_non_executable_and_non_scheduling():
    sequencing = default_coordination_sequencing_intelligence()
    ordering = validate_non_executable_sequence_ordering(sequencing)

    with pytest.raises(FrozenInstanceError):
        sequencing.ordering_visibility.scheduling_execution_enabled = True

    assert ordering["valid"] is True
    assert ordering["non_executable_ordering_only"] is True
    assert ordering["sequencing_execution_disabled"] is True
    assert ordering["scheduling_execution_disabled"] is True
    assert ordering["corrective_ordering_count"] == 0
    assert ordering["missing_ordered_records"] == ()
    assert ordering["missing_ordered_steps"] == ()


def test_v4_2_coordination_sequencing_is_manifest_dependency_graph_and_lineage_compatible():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    manifest_compatibility = validate_coordination_manifest_sequence_compatibility(sequencing, manifest)
    graph_compatibility = validate_coordination_dependency_graph_sequence_compatibility(sequencing, graph, manifest)
    lineage_compatibility = validate_coordination_lineage_chain_sequence_compatibility(
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


def test_v4_2_coordination_sequencing_non_execution_validation_blocks_forbidden_flags():
    sequencing = default_coordination_sequencing_intelligence()
    contaminated = replace(
        sequencing,
        sequencing_execution_enabled=True,
        scheduling_execution_enabled=True,
        dependency_resolution_enabled=True,
        lineage_repair_enabled=True,
        lineage_inference_enabled=True,
        orchestration_execution_enabled=True,
        refresh_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_coordination_sequencing_non_execution(contaminated)

    assert validate_coordination_sequencing_non_execution(sequencing)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 11
    assert validation["sequencing_execution_disabled"] is False
    assert validation["scheduling_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["lineage_repair_disabled"] is False
    assert validation["lineage_inference_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_sequencing_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_sequencing_diagnostics()
    report = build_v4_2_coordination_sequencing_intelligence_report()

    assert report["foundation_status"] == V4_2_COORDINATION_SEQUENCING_STATUS_STABLE
    assert report["sequencing_mode"] == "descriptive_only_non_executable_non_scheduling"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_sequence_ordering_verified"] is True
    assert report["summary"]["non_executable_ordering_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["lineage_chain_compatibility_verified"] is True
    assert report["summary"]["blocked_sequence_visibility_verified"] is True
    assert report["summary"]["prohibited_sequence_visibility_verified"] is True
    assert report["summary"]["unsupported_sequence_visibility_verified"] is True
    assert report["summary"]["stale_sequence_visibility_verified"] is True
    assert report["summary"]["missing_sequence_visibility_verified"] is True
    assert report["summary"]["conflicting_sequence_visibility_verified"] is True
    assert report["summary"]["sequencing_execution_disabled"] is True
    assert report["summary"]["scheduling_execution_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["lineage_repair_disabled"] is True
    assert report["summary"]["lineage_inference_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No sequencing execution exists." in report["explicit_prohibitions"]
    assert "No scheduling execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
