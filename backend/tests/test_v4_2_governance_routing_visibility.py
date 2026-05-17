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
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_diagnostics import (  # noqa: E402
    build_governance_routing_diagnostics,
    count_governance_route_states,
    governance_routing_visibility_equal,
    validate_dependency_graph_routing_compatibility,
    validate_governance_route_visibility,
    validate_governance_routing_non_execution,
    validate_lineage_routing_compatibility,
    validate_manifest_routing_compatibility,
    validate_non_executable_route_ordering,
    validate_sequencing_routing_compatibility,
)
from refresh_coordination.governance_routing_hashing import (  # noqa: E402
    hash_governance_route_record,
    hash_governance_routing_identity,
    hash_governance_routing_visibility,
    hash_routing_source_reference,
)
from refresh_coordination.governance_routing_models import (  # noqa: E402
    ROUTE_STATE_BLOCKED,
    ROUTE_STATE_CONFLICTING,
    ROUTE_STATE_MISSING,
    ROUTE_STATE_PROHIBITED,
    ROUTE_STATE_STABLE,
    ROUTE_STATE_STALE,
    ROUTE_STATE_UNSUPPORTED,
    V4_2_GOVERNANCE_ROUTING_SCHEMA_VERSION,
    V4_2_GOVERNANCE_ROUTING_STATUS_STABLE,
    default_governance_routing_visibility,
)
from refresh_coordination.governance_routing_serialization import (  # noqa: E402
    export_governance_routing_visibility,
    serialize_governance_routing_visibility,
)
from scripts.report_v4_2_governance_routing_visibility import (  # noqa: E402
    build_v4_2_governance_routing_visibility_report,
)


def test_v4_2_governance_routing_models_are_immutable_and_non_executable():
    routing = default_governance_routing_visibility()

    with pytest.raises(FrozenInstanceError):
        routing.routing_execution_enabled = True

    assert routing.identity.schema_version == V4_2_GOVERNANCE_ROUTING_SCHEMA_VERSION
    assert routing.non_executable is True
    assert routing.descriptive_only is True
    assert routing.routing_execution_enabled is False
    assert routing.orchestration_execution_enabled is False
    assert routing.refresh_execution_enabled is False
    assert routing.sequencing_execution_enabled is False
    assert routing.scheduling_execution_enabled is False
    assert routing.dependency_resolution_enabled is False
    assert routing.planner_integration_enabled is False
    assert routing.production_consumption_enabled is False
    assert routing.runtime_mutation_enabled is False
    assert routing.remediation_enabled is False
    assert all(not record.routing_execution_enabled for record in routing.route_records)
    assert all(not diagnostic.execution_enabled for diagnostic in routing.diagnostics)


def test_v4_2_governance_routing_serialization_and_hashing_are_stable():
    first = default_governance_routing_visibility()
    second = default_governance_routing_visibility()

    assert first == second
    assert hash(first) == hash(second)
    assert governance_routing_visibility_equal(first, second)
    assert serialize_governance_routing_visibility(first) == serialize_governance_routing_visibility(second)
    assert hash_governance_routing_visibility(first) == hash_governance_routing_visibility(second)
    assert hash_governance_routing_identity(first.identity) == hash_governance_routing_identity(second.identity)
    assert json.loads(serialize_governance_routing_visibility(first))["non_executable"] is True


def test_v4_2_governance_route_ordering_is_stable():
    routing = default_governance_routing_visibility()
    reordered = replace(
        routing,
        source_references=tuple(reversed(routing.source_references)),
        target_references=tuple(reversed(routing.target_references)),
        manifest_routing_references=tuple(reversed(routing.manifest_routing_references)),
        dependency_graph_routing_references=tuple(reversed(routing.dependency_graph_routing_references)),
        lineage_routing_references=tuple(reversed(routing.lineage_routing_references)),
        sequencing_routing_references=tuple(reversed(routing.sequencing_routing_references)),
        route_records=tuple(reversed(routing.route_records)),
        diagnostics=tuple(reversed(routing.diagnostics)),
    )

    assert serialize_governance_routing_visibility(routing) == serialize_governance_routing_visibility(reordered)
    assert hash_governance_routing_visibility(routing) == hash_governance_routing_visibility(reordered)
    exported = export_governance_routing_visibility(reordered)
    assert [record["route_state"] for record in exported["route_records"]] == [
        ROUTE_STATE_STABLE,
        ROUTE_STATE_STABLE,
        ROUTE_STATE_STABLE,
        ROUTE_STATE_STABLE,
        ROUTE_STATE_BLOCKED,
        ROUTE_STATE_PROHIBITED,
        ROUTE_STATE_UNSUPPORTED,
        ROUTE_STATE_STALE,
        ROUTE_STATE_MISSING,
        ROUTE_STATE_CONFLICTING,
    ]


def test_v4_2_governance_routing_hashes_records_and_sources_deterministically():
    routing = default_governance_routing_visibility()

    assert [hash_governance_route_record(record) for record in routing.route_records] == [
        hash_governance_route_record(record) for record in routing.route_records
    ]
    assert [hash_routing_source_reference(reference) for reference in routing.source_references] == [
        hash_routing_source_reference(reference) for reference in routing.source_references
    ]


def test_v4_2_governance_route_visibility_preserves_all_fail_visible_states():
    routing = default_governance_routing_visibility()
    visibility = validate_governance_route_visibility(routing)
    counts = count_governance_route_states(routing.route_records)

    assert counts[ROUTE_STATE_BLOCKED] == 1
    assert counts[ROUTE_STATE_PROHIBITED] == 1
    assert counts[ROUTE_STATE_UNSUPPORTED] == 1
    assert counts[ROUTE_STATE_STALE] == 1
    assert counts[ROUTE_STATE_MISSING] == 1
    assert counts[ROUTE_STATE_CONFLICTING] == 1
    assert visibility["valid"] is True
    assert visibility["blocked_routes_visible"] is True
    assert visibility["prohibited_routes_visible"] is True
    assert visibility["unsupported_routes_visible"] is True
    assert visibility["stale_routes_visible"] is True
    assert visibility["missing_routes_visible"] is True
    assert visibility["conflicting_routes_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_governance_route_ordering_is_non_executable_and_non_routing():
    routing = default_governance_routing_visibility()
    ordering = validate_non_executable_route_ordering(routing)

    with pytest.raises(FrozenInstanceError):
        routing.ordering_visibility.routing_execution_enabled = True

    assert ordering["valid"] is True
    assert ordering["non_executable_ordering_only"] is True
    assert ordering["routing_execution_disabled"] is True
    assert ordering["corrective_ordering_count"] == 0
    assert ordering["missing_ordered_records"] == ()


def test_v4_2_governance_routing_is_manifest_graph_lineage_and_sequencing_compatible():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)

    manifest_compatibility = validate_manifest_routing_compatibility(routing, manifest)
    graph_compatibility = validate_dependency_graph_routing_compatibility(routing, graph, manifest)
    lineage_compatibility = validate_lineage_routing_compatibility(routing, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_routing_compatibility(
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


def test_v4_2_governance_routing_non_execution_validation_blocks_forbidden_flags():
    routing = default_governance_routing_visibility()
    contaminated = replace(
        routing,
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
    )
    validation = validate_governance_routing_non_execution(contaminated)

    assert validate_governance_routing_non_execution(routing)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 12
    assert validation["routing_execution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["sequencing_execution_disabled"] is False
    assert validation["scheduling_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["lineage_repair_disabled"] is False
    assert validation["lineage_inference_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_governance_routing_report_contains_required_evidence_and_boundaries():
    diagnostics = build_governance_routing_diagnostics()
    report = build_v4_2_governance_routing_visibility_report()

    assert report["foundation_status"] == V4_2_GOVERNANCE_ROUTING_STATUS_STABLE
    assert report["routing_mode"] == "descriptive_only_non_executable_non_routing"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_route_ordering_verified"] is True
    assert report["summary"]["non_executable_ordering_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["lineage_chain_compatibility_verified"] is True
    assert report["summary"]["sequencing_compatibility_verified"] is True
    assert report["summary"]["blocked_route_visibility_verified"] is True
    assert report["summary"]["prohibited_route_visibility_verified"] is True
    assert report["summary"]["unsupported_route_visibility_verified"] is True
    assert report["summary"]["stale_route_visibility_verified"] is True
    assert report["summary"]["missing_route_visibility_verified"] is True
    assert report["summary"]["conflicting_route_visibility_verified"] is True
    assert report["summary"]["routing_execution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["sequencing_execution_disabled"] is True
    assert report["summary"]["scheduling_execution_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["lineage_repair_disabled"] is True
    assert report["summary"]["lineage_inference_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No routing execution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No sequencing execution exists." in report["explicit_prohibitions"]
    assert "No scheduling execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No lineage repair exists." in report["explicit_prohibitions"]
    assert "No lineage inference exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
