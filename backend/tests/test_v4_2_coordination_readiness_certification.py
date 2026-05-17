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

from refresh_coordination.coordination_continuity_models import (  # noqa: E402
    default_coordination_continuity_certification,
)
from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_readiness_certification import (  # noqa: E402
    build_coordination_readiness_certification_evidence,
    validate_descriptive_only_coordination_readiness_certification,
)
from refresh_coordination.coordination_readiness_diagnostics import (  # noqa: E402
    build_coordination_readiness_diagnostics,
    coordination_readiness_certifications_equal,
    count_coordination_readiness_states,
    validate_coordination_readiness_non_execution,
    validate_coordination_readiness_visibility,
    validate_descriptive_readiness_classification,
    validate_layer_readiness_compatibility,
    validate_phase_evidence_compatibility,
)
from refresh_coordination.coordination_readiness_hashing import (  # noqa: E402
    hash_coordination_readiness_certification,
    hash_coordination_readiness_identity,
    hash_coordination_readiness_record,
    hash_phase_evidence_reference,
    hash_readiness_state_visibility,
)
from refresh_coordination.coordination_readiness_models import (  # noqa: E402
    READINESS_CLASSIFICATION_DESCRIPTIVE,
    READINESS_STATE_BLOCKED,
    READINESS_STATE_CONFLICTING,
    READINESS_STATE_MISSING,
    READINESS_STATE_PROHIBITED,
    READINESS_STATE_STABLE,
    READINESS_STATE_STALE,
    READINESS_STATE_UNSUPPORTED,
    V4_2_COORDINATION_READINESS_SCHEMA_VERSION,
    V4_2_COORDINATION_READINESS_STATUS_STABLE,
    default_coordination_readiness_certification,
)
from refresh_coordination.coordination_readiness_serialization import (  # noqa: E402
    export_coordination_readiness_certification,
    serialize_coordination_readiness_certification,
)
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402
from scripts.report_v4_2_coordination_readiness_certification import (  # noqa: E402
    build_v4_2_coordination_readiness_certification_report,
)


def test_v4_2_coordination_readiness_models_are_immutable_and_non_executable():
    readiness = default_coordination_readiness_certification()

    with pytest.raises(FrozenInstanceError):
        readiness.readiness_approval_enabled = True

    assert readiness.identity.schema_version == V4_2_COORDINATION_READINESS_SCHEMA_VERSION
    assert readiness.non_executable is True
    assert readiness.descriptive_only is True
    assert readiness.non_authorizing is True
    assert readiness.non_remediating is True
    assert readiness.readiness_approved is False
    assert readiness.operational_authorized is False
    assert readiness.readiness_approval_enabled is False
    assert readiness.operational_authorization_enabled is False
    assert readiness.remediation_enabled is False
    assert readiness.automatic_correction_enabled is False
    assert readiness.drift_correction_enabled is False
    assert readiness.continuity_repair_enabled is False
    assert readiness.routing_execution_enabled is False
    assert readiness.orchestration_execution_enabled is False
    assert readiness.refresh_execution_enabled is False
    assert readiness.dependency_resolution_enabled is False
    assert readiness.planner_integration_enabled is False
    assert readiness.production_consumption_enabled is False
    assert readiness.runtime_mutation_enabled is False
    assert all(not record.readiness_approval_enabled for record in readiness.readiness_records)
    assert all(not diagnostic.operational_authorization_enabled for diagnostic in readiness.diagnostics)


def test_v4_2_coordination_readiness_serialization_and_hashing_are_stable():
    first = default_coordination_readiness_certification()
    second = default_coordination_readiness_certification()

    assert first == second
    assert hash(first) == hash(second)
    assert coordination_readiness_certifications_equal(first, second)
    assert serialize_coordination_readiness_certification(first) == serialize_coordination_readiness_certification(
        second
    )
    assert hash_coordination_readiness_certification(first) == hash_coordination_readiness_certification(second)
    assert hash_coordination_readiness_identity(first.identity) == hash_coordination_readiness_identity(
        second.identity
    )
    assert json.loads(serialize_coordination_readiness_certification(first))["non_executable"] is True


def test_v4_2_coordination_readiness_ordering_is_stable():
    readiness = default_coordination_readiness_certification()
    reordered = replace(
        readiness,
        phase_evidence_references=tuple(reversed(readiness.phase_evidence_references)),
        manifest_readiness_references=tuple(reversed(readiness.manifest_readiness_references)),
        dependency_graph_readiness_references=tuple(reversed(readiness.dependency_graph_readiness_references)),
        lineage_readiness_references=tuple(reversed(readiness.lineage_readiness_references)),
        sequencing_readiness_references=tuple(reversed(readiness.sequencing_readiness_references)),
        routing_readiness_references=tuple(reversed(readiness.routing_readiness_references)),
        drift_readiness_references=tuple(reversed(readiness.drift_readiness_references)),
        diagnostics_explainability_readiness_references=tuple(
            reversed(readiness.diagnostics_explainability_readiness_references)
        ),
        continuity_readiness_references=tuple(reversed(readiness.continuity_readiness_references)),
        readiness_records=tuple(reversed(readiness.readiness_records)),
        diagnostics=tuple(reversed(readiness.diagnostics)),
    )

    assert serialize_coordination_readiness_certification(readiness) == serialize_coordination_readiness_certification(
        reordered
    )
    assert hash_coordination_readiness_certification(readiness) == hash_coordination_readiness_certification(
        reordered
    )
    exported = export_coordination_readiness_certification(reordered)
    assert [record["readiness_state"] for record in exported["readiness_records"]] == [
        READINESS_STATE_STABLE,
        READINESS_STATE_BLOCKED,
        READINESS_STATE_PROHIBITED,
        READINESS_STATE_UNSUPPORTED,
        READINESS_STATE_STALE,
        READINESS_STATE_MISSING,
        READINESS_STATE_CONFLICTING,
    ]


def test_v4_2_coordination_readiness_hashes_phase_evidence_and_records_deterministically():
    readiness = default_coordination_readiness_certification()

    assert [hash_phase_evidence_reference(reference) for reference in readiness.phase_evidence_references] == [
        hash_phase_evidence_reference(reference) for reference in readiness.phase_evidence_references
    ]
    assert [hash_coordination_readiness_record(record) for record in readiness.readiness_records] == [
        hash_coordination_readiness_record(record) for record in readiness.readiness_records
    ]
    assert hash_readiness_state_visibility(readiness.blocked_readiness_visibility) == hash_readiness_state_visibility(
        readiness.blocked_readiness_visibility
    )


def test_v4_2_coordination_readiness_is_compatible_with_phase_1_to_8_evidence():
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
    continuity = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    readiness = default_coordination_readiness_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )

    phase_compatibility = validate_phase_evidence_compatibility(
        readiness,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )
    layer_compatibility = validate_layer_readiness_compatibility(
        readiness,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )

    assert phase_compatibility["valid"] is True
    assert phase_compatibility["phase_evidence_count"] == 8
    assert layer_compatibility["valid"] is True
    assert all(item["hash_matches"] for item in layer_compatibility["layer_results"].values())


def test_v4_2_coordination_readiness_fail_visible_states_are_aggregated():
    readiness = default_coordination_readiness_certification()
    visibility = validate_coordination_readiness_visibility(readiness)
    counts = count_coordination_readiness_states(readiness.readiness_records)

    assert counts[READINESS_STATE_BLOCKED] == 1
    assert counts[READINESS_STATE_PROHIBITED] == 1
    assert counts[READINESS_STATE_UNSUPPORTED] == 1
    assert counts[READINESS_STATE_STALE] == 1
    assert counts[READINESS_STATE_MISSING] == 1
    assert counts[READINESS_STATE_CONFLICTING] == 1
    assert visibility["valid"] is True
    assert visibility["blocked_readiness_visible"] is True
    assert visibility["prohibited_readiness_visible"] is True
    assert visibility["unsupported_readiness_visible"] is True
    assert visibility["stale_readiness_visible"] is True
    assert visibility["missing_readiness_visible"] is True
    assert visibility["conflicting_readiness_visible"] is True
    assert visibility["hidden_count"] == 0
    assert visibility["corrective_count"] == 0


def test_v4_2_coordination_readiness_classification_is_descriptive_only():
    readiness = default_coordination_readiness_certification()
    classification = validate_descriptive_readiness_classification(readiness)
    evidence = build_coordination_readiness_certification_evidence(readiness)
    diagnostics = build_coordination_readiness_diagnostics(readiness)

    assert classification["valid"] is True
    assert classification["classification"] == READINESS_CLASSIFICATION_DESCRIPTIVE
    assert classification["readiness_approved"] is False
    assert classification["operational_authorized"] is False
    assert evidence["descriptive_only_validation"]["valid"] is True
    assert evidence["fail_visible_record_count"] == 6
    assert diagnostics["enabled_capability_count"] == 0


def test_v4_2_coordination_readiness_non_execution_validation_blocks_forbidden_flags():
    readiness = default_coordination_readiness_certification()
    contaminated = replace(
        readiness,
        readiness_approved=True,
        operational_authorized=True,
        readiness_approval_enabled=True,
        operational_authorization_enabled=True,
        remediation_enabled=True,
        automatic_correction_enabled=True,
        drift_correction_enabled=True,
        drift_remediation_enabled=True,
        continuity_repair_enabled=True,
        continuity_inference_enabled=True,
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
    validation = validate_coordination_readiness_non_execution(contaminated)

    assert validate_coordination_readiness_non_execution(readiness)["valid"] is True
    assert validation["valid"] is False
    assert validation["enabled_capability_count"] == 27
    assert validation["readiness_approval_disabled"] is False
    assert validation["operational_authorization_disabled"] is False
    assert validation["remediation_disabled"] is False
    assert validation["automatic_correction_disabled"] is False
    assert validation["drift_correction_disabled"] is False
    assert validation["continuity_repair_disabled"] is False
    assert validation["routing_execution_disabled"] is False
    assert validation["orchestration_execution_disabled"] is False
    assert validation["refresh_execution_disabled"] is False
    assert validation["dependency_resolution_disabled"] is False
    assert validation["planner_integration_disabled"] is False
    assert validation["production_consumption_disabled"] is False
    assert validation["runtime_mutation_disabled"] is False


def test_v4_2_coordination_readiness_report_contains_required_evidence_and_boundaries():
    diagnostics = build_coordination_readiness_diagnostics()
    report = build_v4_2_coordination_readiness_certification_report()

    assert report["readiness_status"] == V4_2_COORDINATION_READINESS_STATUS_STABLE
    assert report["readiness_mode"] == "descriptive_only_non_executable_non_authorizing_non_remediating"
    assert report["summary"]["validation_error_count"] == 0
    assert report["summary"]["deterministic_serialization_verified"] is True
    assert report["summary"]["deterministic_hashing_verified"] is True
    assert report["summary"]["stable_readiness_ordering_verified"] is True
    assert report["summary"]["phase_evidence_compatibility_verified"] is True
    assert report["summary"]["layer_readiness_compatibility_verified"] is True
    assert report["summary"]["blocked_readiness_verified"] is True
    assert report["summary"]["prohibited_readiness_verified"] is True
    assert report["summary"]["unsupported_readiness_verified"] is True
    assert report["summary"]["stale_readiness_verified"] is True
    assert report["summary"]["missing_readiness_verified"] is True
    assert report["summary"]["conflicting_readiness_verified"] is True
    assert report["summary"]["descriptive_readiness_classification_verified"] is True
    assert report["summary"]["readiness_approval_disabled"] is True
    assert report["summary"]["operational_authorization_disabled"] is True
    assert report["summary"]["remediation_disabled"] is True
    assert report["summary"]["automatic_correction_disabled"] is True
    assert report["summary"]["drift_correction_disabled"] is True
    assert report["summary"]["continuity_repair_disabled"] is True
    assert report["summary"]["routing_execution_disabled"] is True
    assert report["summary"]["orchestration_execution_disabled"] is True
    assert report["summary"]["refresh_execution_disabled"] is True
    assert report["summary"]["dependency_resolution_disabled"] is True
    assert report["summary"]["planner_integration_disabled"] is True
    assert report["summary"]["production_consumption_disabled"] is True
    assert report["summary"]["runtime_mutation_disabled"] is True
    assert diagnostics["enabled_capability_count"] == 0
    assert "No readiness approval exists." in report["explicit_prohibitions"]
    assert "No operational authorization exists." in report["explicit_prohibitions"]
    assert "No remediation exists." in report["explicit_prohibitions"]
    assert "No automatic correction exists." in report["explicit_prohibitions"]
    assert "No drift correction exists." in report["explicit_prohibitions"]
    assert "No continuity repair exists." in report["explicit_prohibitions"]
    assert "No routing execution exists." in report["explicit_prohibitions"]
    assert "No orchestration execution exists." in report["explicit_prohibitions"]
    assert "No refresh execution exists." in report["explicit_prohibitions"]
    assert "No dependency resolution exists." in report["explicit_prohibitions"]
    assert "No planner integration exists." in report["explicit_prohibitions"]
    assert "No production consumption exists." in report["explicit_prohibitions"]
