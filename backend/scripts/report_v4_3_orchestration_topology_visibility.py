"""Generate deterministic v4.3 orchestration topology visibility evidence."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from orchestration_governance.orchestration_topology_diagnostics import (  # noqa: E402
    build_orchestration_topology_diagnostics,
    count_topology_edge_states,
    count_topology_node_states,
    count_topology_relationship_states,
    topologies_equal,
    topology_identity_key,
    validate_topology_continuity,
    validate_topology_explainability,
    validate_topology_identity,
    validate_topology_metadata,
    validate_topology_non_execution,
    validate_topology_relationship_visibility,
    validate_topology_structure,
)
from orchestration_governance.orchestration_topology_hashing import (  # noqa: E402
    deterministic_orchestration_topology_hash,
    hash_orchestration_topology,
    hash_orchestration_topology_diagnostic,
    hash_orchestration_topology_edge,
    hash_orchestration_topology_identity,
    hash_orchestration_topology_node,
    hash_orchestration_topology_relationship,
)
from orchestration_governance.orchestration_topology_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_TOPOLOGY_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_TOPOLOGY_PROHIBITIONS,
    V4_3_ORCHESTRATION_TOPOLOGY_GENERATED_AT,
    V4_3_ORCHESTRATION_TOPOLOGY_PHASE_ID,
    V4_3_ORCHESTRATION_TOPOLOGY_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_TOPOLOGY_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_TOPOLOGY_STATUS_STABLE,
    default_orchestration_topology,
)
from orchestration_governance.orchestration_topology_serialization import (  # noqa: E402
    export_orchestration_topology,
    serialize_orchestration_topology,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_topology_visibility_report.json")


def _reordered_orchestration_topology():
    topology = default_orchestration_topology()
    return replace(
        topology,
        nodes=tuple(reversed(topology.nodes)),
        edges=tuple(reversed(topology.edges)),
        relationships=tuple(reversed(topology.relationships)),
        continuity_metadata=tuple(reversed(topology.continuity_metadata)),
        diagnostics=tuple(reversed(topology.diagnostics)),
        explainability_summaries=tuple(reversed(topology.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_orchestration_topology_hash(payload)


def build_v4_3_orchestration_topology_visibility_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    topology = default_orchestration_topology()
    repeated = default_orchestration_topology()
    reordered = _reordered_orchestration_topology()
    exported = export_orchestration_topology(topology)
    identity = validate_topology_identity(topology)
    structure = validate_topology_structure(topology)
    visibility = validate_topology_relationship_visibility(topology)
    metadata = validate_topology_metadata(topology)
    continuity = validate_topology_continuity(topology)
    explainability = validate_topology_explainability(topology)
    non_execution = validate_topology_non_execution(topology)
    diagnostics = build_orchestration_topology_diagnostics(topology)
    serialization_first = serialize_orchestration_topology(topology)
    serialization_second = serialize_orchestration_topology(repeated)
    serialization_reordered = serialize_orchestration_topology(reordered)
    topology_hash = hash_orchestration_topology(topology)
    repeated_hash = hash_orchestration_topology(repeated)
    reordered_hash = hash_orchestration_topology(reordered)
    node_hashes = [hash_orchestration_topology_node(node) for node in topology.nodes]
    edge_hashes = [hash_orchestration_topology_edge(edge) for edge in topology.edges]
    relationship_hashes = [
        hash_orchestration_topology_relationship(relationship) for relationship in topology.relationships
    ]
    diagnostic_hashes = [hash_orchestration_topology_diagnostic(diagnostic) for diagnostic in topology.diagnostics]
    exported_node_order = [item["node_id"] for item in exported["nodes"]]
    expected_node_order = [
        item["node_id"]
        for item in sorted(exported["nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_edge_order = [item["edge_id"] for item in exported["edges"]]
    expected_edge_order = [
        item["edge_id"]
        for item in sorted(exported["edges"], key=lambda item: (item["deterministic_order"], item["edge_id"]))
    ]
    exported_relationship_order = [item["relationship_id"] for item in exported["relationships"]]
    expected_relationship_order = [
        item["relationship_id"]
        for item in sorted(
            exported["relationships"],
            key=lambda item: (item["deterministic_order"], item["relationship_id"]),
        )
    ]
    validation_error_count = sum(
        [
            0 if identity["valid"] else 1,
            0 if structure["valid"] else 1,
            0 if visibility["valid"] else 1,
            0 if metadata["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if topology_hash == repeated_hash == reordered_hash else 1,
            0 if topologies_equal(topology, repeated) else 1,
            0 if exported_node_order == expected_node_order else 1,
            0 if exported_edge_order == expected_edge_order else 1,
            0 if exported_relationship_order == expected_relationship_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_TOPOLOGY_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_TOPOLOGY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_3_ORCHESTRATION_TOPOLOGY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_TOPOLOGY_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_TOPOLOGY_PHASE_ID,
        "phase_name": "v4.3_phase_2_orchestration_topology_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration topology visibility without graph execution",
        "topology_mode": "descriptive_only_non_executable_topology_visibility",
        "topology_visibility_status": status,
        "topology_counts": {
            "topology_count": 1,
            "node_count": len(topology.nodes),
            "edge_count": len(topology.edges),
            "relationship_count": len(topology.relationships),
            "diagnostic_count": len(topology.diagnostics),
            "explainability_summary_count": len(topology.explainability_summaries),
            "node_state_counts": count_topology_node_states(topology.nodes),
            "edge_state_counts": count_topology_edge_states(topology.edges),
            "relationship_state_counts": count_topology_relationship_states(topology.relationships),
            "unsupported_relationship_count": len(diagnostics["unsupported_relationship_ids"]),
            "prohibited_relationship_count": len(diagnostics["prohibited_relationship_ids"]),
            "blocked_relationship_count": len(diagnostics["blocked_relationship_ids"]),
            "stale_relationship_count": len(diagnostics["stale_relationship_ids"]),
            "conflicting_relationship_count": len(diagnostics["conflicting_relationship_ids"]),
            "missing_metadata_count": len(diagnostics["missing_metadata_relationship_ids"]),
        },
        "topology_structure": {
            "identity_key": topology_identity_key(topology),
            "identity_validation": identity,
            "structure_validation": structure,
            "duplicate_node_ids": structure["duplicate_node_ids"],
            "duplicate_edge_ids": structure["duplicate_edge_ids"],
            "unknown_source_edge_ids": structure["unknown_source_edge_ids"],
            "unknown_target_edge_ids": structure["unknown_target_edge_ids"],
            "self_referential_edge_ids": structure["self_referential_edge_ids"],
            "topology_structure_valid": structure["valid"],
        },
        "relationship_visibility": {
            "relationship_visibility_validation": visibility,
            "unsupported_relationship_ids": diagnostics["unsupported_relationship_ids"],
            "prohibited_relationship_ids": diagnostics["prohibited_relationship_ids"],
            "blocked_relationship_ids": diagnostics["blocked_relationship_ids"],
            "stale_relationship_ids": diagnostics["stale_relationship_ids"],
            "conflicting_relationship_ids": diagnostics["conflicting_relationship_ids"],
            "missing_metadata_relationship_ids": diagnostics["missing_metadata_relationship_ids"],
            "unknown_relationship_ids": diagnostics["unknown_relationship_ids"],
            "unsupported_relationships_visible": visibility["unsupported_relationships_visible"],
            "prohibited_relationships_visible": visibility["prohibited_relationships_visible"],
            "blocked_relationships_visible": visibility["blocked_relationships_visible"],
            "stale_relationships_visible": visibility["stale_relationships_visible"],
            "conflicting_relationships_visible": visibility["conflicting_relationships_visible"],
            "missing_metadata_relationships_visible": visibility["missing_metadata_relationships_visible"],
            "boundary_relationships_visible": visibility["boundary_relationships_visible"],
            "executable_relationship_ids": visibility["executable_relationship_ids"],
        },
        "metadata_visibility": {
            "metadata_validation": metadata,
            "governance_metadata_present": metadata["governance_metadata_present"],
            "lineage_metadata_present": metadata["lineage_metadata_present"],
            "provenance_metadata_present": metadata["provenance_metadata_present"],
            "continuity_metadata_present": metadata["continuity_metadata_present"],
            "diagnostics_metadata_present": metadata["diagnostics_metadata_present"],
            "explainability_metadata_present": metadata["explainability_metadata_present"],
            "non_execution_metadata_present": metadata["non_execution_metadata_present"],
        },
        "continuity_visibility": {
            "continuity_validation": continuity,
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "topology_continuity_visible": continuity["topology_continuity_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "diagnostic_hashes": diagnostic_hashes,
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "repair_absent": diagnostics["repair_absent"],
            "inference_absent": diagnostics["inference_absent"],
            "auto_correction_absent": diagnostics["auto_correction_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "execution_absent": diagnostics["execution_absent"],
            "selection_systems_absent": diagnostics["selection_systems_absent"],
        },
        "explainability_summaries": {
            "explainability_validation": explainability,
            "blocked_topology_visible": "blocked_topology" in explainability["explainability_categories"],
            "prohibited_relationship_visible": "prohibited_relationship" in explainability["explainability_categories"],
            "unsupported_relationship_visible": "unsupported_relationship" in explainability["explainability_categories"],
            "stale_relationship_visible": "stale_relationship" in explainability["explainability_categories"],
            "conflicting_relationship_visible": "conflicting_relationship" in explainability["explainability_categories"],
            "traversal_unavailable_visible": "traversal_unavailable" in explainability["explainability_categories"],
            "routing_unavailable_visible": "routing_unavailable" in explainability["explainability_categories"],
            "dependency_resolution_unavailable_visible": (
                "dependency_resolution_unavailable" in explainability["explainability_categories"]
            ),
            "execution_disabled_visible": "execution_disabled" in explainability["explainability_categories"],
        },
        "hashing_stability_evidence": {
            "stable": topology_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_topology_visibility",
            "topology_hash": topology_hash,
            "repeated_topology_hash": repeated_hash,
            "reordered_topology_hash": reordered_hash,
            "identity_hash": hash_orchestration_topology_identity(topology.identity),
            "node_hashes": node_hashes,
            "edge_hashes": edge_hashes,
            "relationship_hashes": relationship_hashes,
            "diagnostic_hashes": diagnostic_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_topology_visibility",
            "payload_length": len(serialization_first),
            "node_ordering_stable": exported_node_order == expected_node_order,
            "edge_ordering_stable": exported_edge_order == expected_edge_order,
            "relationship_ordering_stable": exported_relationship_order == expected_relationship_order,
            "diagnostics_ordering_stable": [item["diagnostic_id"] for item in exported["diagnostics"]]
            == [
                item["diagnostic_id"]
                for item in sorted(
                    exported["diagnostics"],
                    key=lambda item: (item["deterministic_order"], item["diagnostic_id"]),
                )
            ],
            "unsupported_relationships_preserved": len(diagnostics["unsupported_relationship_ids"]) > 0,
            "prohibited_relationships_preserved": len(diagnostics["prohibited_relationship_ids"]) > 0,
            "blocked_relationships_preserved": len(diagnostics["blocked_relationship_ids"]) > 0,
            "stale_relationships_preserved": len(diagnostics["stale_relationship_ids"]) > 0,
            "conflicting_relationships_preserved": len(diagnostics["conflicting_relationship_ids"]) > 0,
            "missing_metadata_relationships_preserved": len(diagnostics["missing_metadata_relationship_ids"]) > 0,
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "topology_visibility_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": topology_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": topologies_equal(topology, repeated),
            "node_ordering_verified": exported_node_order == expected_node_order,
            "edge_ordering_verified": exported_edge_order == expected_edge_order,
            "relationship_ordering_verified": exported_relationship_order == expected_relationship_order,
            "identity_visibility_verified": identity["valid"],
            "structure_visibility_verified": structure["valid"],
            "relationship_visibility_verified": visibility["valid"],
            "metadata_visibility_verified": metadata["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "traversal_disabled": non_execution["traversal_disabled"],
            "graph_execution_disabled": non_execution["graph_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "route_selection_disabled": non_execution["route_selection_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
            "operational_state_mutation_disabled": non_execution["operational_state_mutation_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "graph_engine_absent": non_execution["graph_engine_absent"],
            "traversal_engine_absent": non_execution["traversal_engine_absent"],
            "routing_engine_absent": non_execution["routing_engine_absent"],
            "dependency_resolver_absent": non_execution["dependency_resolver_absent"],
        },
        "topology": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_TOPOLOGY_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_TOPOLOGY_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Topology visibility JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_topology_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"topology_visibility_status={report['topology_visibility_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
