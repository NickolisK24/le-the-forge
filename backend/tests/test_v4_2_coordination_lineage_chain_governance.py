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

from refresh_coordination.coordination_dependency_graph_models import (  # noqa: E402
    default_coordination_dependency_graph,
)
from refresh_coordination.coordination_lineage_chain_diagnostics import (  # noqa: E402
    build_coordination_lineage_chain_diagnostics,
    coordination_lineage_chains_equal,
    count_coordination_lineage_states,
    validate_coordination_dependency_graph_lineage_compatibility,
    validate_coordination_lineage_chain_continuity,
    validate_coordination_lineage_chain_non_execution,
    validate_coordination_lineage_chain_visibility,
    validate_coordination_manifest_lineage_compatibility,
)
from refresh_coordination.coordination_lineage_chain_hashing import (  # noqa: E402
    hash_coordination_lineage_chain,
    hash_coordination_lineage_chain_identity,
    hash_coordination_lineage_chain_record,
    hash_lineage_source_reference,
)
from refresh_coordination.coordination_lineage_chain_models import (  # noqa: E402
    LINEAGE_STATE_CONFLICTING,
    LINEAGE_STATE_MISSING,
    LINEAGE_STATE_PROHIBITED_MUTATION,
    LINEAGE_STATE_STABLE,
    LINEAGE_STATE_STALE,
    LINEAGE_STATE_UNSUPPORTED_TRANSITION,
    V4_2_COORDINATION_LINEAGE_CHAIN_SCHEMA_VERSION,
    V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_STABLE,
    default_coordination_lineage_chain,
)
from refresh_coordination.coordination_lineage_chain_serialization import (  # noqa: E402
    export_coordination_lineage_chain,
    serialize_coordination_lineage_chain,
)
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from scripts.report_v4_2_coordination_lineage_chain_governance import (  # noqa: E402
    build_v4_2_coordination_lineage_chain_governance_report,
)


def test_v4_2_coordination_lineage_chain_models_are_immutable_and_non_executable():
    chain = default_coordination_lineage_chain()

    with pytest.raises(FrozenInstanceError):
        chain.lineage_repair_enabled = True

    assert chain.identity.schema_version == V4_2_COORDINATION_LINEAGE_CHAIN_SCHEMA_VERSION
    assert chain.non_executable is True
    assert chain.descriptive_only is True
    assert chain.lineage_repair_enabled is False
    assert chain.lineage_inference_enabled is False
    assert chain.lineage_mutation_enabled is False
    assert chain.dependency_resolution_enabled is False
    assert chain.orchestration_execution_enabled is False
    assert chain.refresh_execution_enabled is False
    assert chain.planner_integration_enabled is False
    assert chain.production_consumption_enabled is False
    assert chain.production_bundle_consumption_enabled is False
    assert chain.runtime_mutation_enabled is False
    assert chain.remediation_enabled is False
    assert chain.automatic_correction_enabled is False
    assert chain.automatic_rollback_enabled is False
    assert chain.authorization_enabled is False
    assert chain.approval_enabled is False
    assert all(not record.lineage_repair_enabled for record in chain.records)
    assert all(not record.lineage_inference_enabled for record in chain.records)
    assert all(not diagnostic.execution_enabled for diagnostic in chain.diagnostics)


def test_v4_2_coordination_lineage_chain_serialization_and_hashing_are_stable():
    first = default_coordination_lineage_chain()
    second = default_coordination_lineage_chain()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_lineage_chains_equal(first, second)
    assert serialize_coordination_lineage_chain(first) == serialize_coordination_lineage_chain(second)
    assert hash_coordination_lineage_chain(first) == hash_coordination_lineage_chain(second)
    assert hash_coordination_lineage_chain_identity(first.identity) == hash_coordination_lineage_chain_identity(
        second.identity
    )
    assert json.loads(serialize_coordination_lineage_chain(first))["non_executable"] is True


def test_v4_2_coordination_lineage_chain_ordering_is_stable():
    chain = default_coordination_lineage_chain()
    reordered = replace(
        chain,
        source_references=tuple(reversed(chain.source_references)),
        predecessor_references=tuple(reversed(chain.predecessor_references)),
        successor_references=tuple(reversed(chain.successor_references)),
        manifest_lineage_references=tuple(reversed(chain.manifest_lineage_references)),
        dependency_graph_lineage_references=tuple(reversed(chain.dependency_graph_lineage_references)),
        records=tuple(reversed(chain.records)),
        diagnostics=tuple(reversed(chain.diagnostics)),
    )

    assert serialize_coordination_lineage_chain(chain) == serialize_coordination_lineage_chain(reordered)
    assert hash_coordination_lineage_chain(chain) == hash_coordination_lineage_chain(reordered)
    exported = export_coordination_lineage_chain(reordered)
    assert [record["lineage_state"] for record in exported["records"]] == [
        LINEAGE_STATE_STABLE,
        LINEAGE_STATE_STABLE,
        LINEAGE_STATE_STALE,
        LINEAGE_STATE_MISSING,
        LINEAGE_STATE_CONFLICTING,
        LINEAGE_STATE_PROHIBITED_MUTATION,
        LINEAGE_STATE_UNSUPPORTED_TRANSITION,
    ]


def test_v4_2_coordination_lineage_chain_hashes_records_and_sources_deterministically():
    chain = default_coordination_lineage_chain()

    assert [hash_coordination_lineage_chain_record(record) for record in chain.records] == [
        hash_coordination_lineage_chain_record(record) for record in chain.records
    ]
    assert [hash_lineage_source_reference(reference) for reference in chain.source_references] == [
        hash_lineage_source_reference(reference) for reference in chain.source_references
    ]


def test_v4_2_coordination_lineage_visibility_preserves_stale_missing_conflicting_prohibited_and_unsupported_states():
    chain = default_coordination_lineage_chain()
    visibility = validate_coordination_lineage_chain_visibility(chain)
    counts = count_coordination_lineage_states(chain.records)

    assert counts[LINEAGE_STATE_STALE] == 1
    assert counts[LINEAGE_STATE_MISSING] == 1
    assert counts[LINEAGE_STATE_CONFLICTING] == 1
    assert counts[LINEAGE_STATE_PROHIBITED_MUTATION] == 1
    assert counts[LINEAGE_STATE_UNSUPPORTED_TRANSITION] == 1
    assert visibility["valid"] is True
    assert visibility["stale_lineage_visible"] is True
    assert visibility["missing_lineage_visible"] is True
    assert visibility["conflicting_lineage_visible"] is True
    assert visibility["prohibited_lineage_mutation_visible"] is True
    assert visibility["unsupported_lineage_transition_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_lineage_chain_continuity_visibility_is_preserved():
    chain = default_coordination_lineage_chain()
    continuity = validate_coordination_lineage_chain_continuity(chain)

    with pytest.raises(FrozenInstanceError):
        chain.records[0].lineage_inference_enabled = True

    assert continuity["valid"] is True
    assert continuity["record_count"] == len(chain.records)
    assert continuity["lineage_continuity_preserved"] is True
    assert continuity["provenance_continuity_preserved"] is True
    assert continuity["dependency_graph_compatibility_preserved"] is True
    assert continuity["replay_safe"] is True
    assert continuity["rollback_safe"] is True
    assert continuity["corrective_lineage_count"] == 0


def test_v4_2_coordination_lineage_chain_is_manifest_and_dependency_graph_compatible():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    chain = default_coordination_lineage_chain(manifest, graph)
    manifest_compatibility = validate_coordination_manifest_lineage_compatibility(chain, manifest)
    graph_compatibility = validate_coordination_dependency_graph_lineage_compatibility(chain, graph, manifest)

    assert manifest_compatibility["valid"] is True
    assert manifest_compatibility["chain_source_manifest_reference"] == manifest.identity.manifest_id
    assert manifest_compatibility["manifest_hash_matches"] is True
    assert graph_compatibility["valid"] is True
    assert graph_compatibility["chain_source_dependency_graph_reference"] == graph.identity.graph_id
    assert graph_compatibility["dependency_graph_hash_matches"] is True


def test_v4_2_coordination_lineage_chain_non_execution_validation_blocks_forbidden_flags():
    chain = default_coordination_lineage_chain()
    contaminated = replace(
        chain,
        lineage_repair_enabled=True,
        lineage_inference_enabled=True,
        lineage_mutation_enabled=True,
        dependency_resolution_enabled=True,
        orchestration_execution_enabled=True,
        refresh_execution_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        remediation_enabled=True,
        runtime_mutation_enabled=True,
    )
    validation = validate_coordination_lineage_chain_non_execution(contaminated)

    assert validate_coordination_lineage_chain_non_execution(chain)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 10
    assert validation["lineage_repair_disabled"] is False
    assert validation["lineage_inference_disabled"] is False
    assert validation["lineage_mutation_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_lineage_chain_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_lineage_chain_diagnostics()
    report = build_v4_2_coordination_lineage_chain_governance_report()

    assert report["foundation_status"] == V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_STABLE
    assert report["lineage_chain_mode"] == "descriptive_only_non_executable"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_lineage_ordering_verified"] is True
    assert report["summary"]["stale_lineage_visibility_verified"] is True
    assert report["summary"]["missing_lineage_visibility_verified"] is True
    assert report["summary"]["conflicting_lineage_visibility_verified"] is True
    assert report["summary"]["prohibited_lineage_mutation_visibility_verified"] is True
    assert report["summary"]["unsupported_lineage_transition_visibility_verified"] is True
    assert report["summary"]["lineage_continuity_verified"] is True
    assert report["summary"]["manifest_compatibility_verified"] is True
    assert report["summary"]["dependency_graph_compatibility_verified"] is True
    assert report["summary"]["non_execution_enforcement_validated"] is True
    assert report["summary"]["lineage_repair_disabled"] is True
    assert report["summary"]["lineage_inference_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No lineage repair exists." in report["explicit_prohibitions"]
    assert "No lineage inference exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
