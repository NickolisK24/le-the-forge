"""Generate deterministic v4.2 coordination dependency graph governance evidence."""

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

from refresh_coordination.coordination_dependency_graph_diagnostics import (  # noqa: E402
    build_coordination_dependency_graph_diagnostics,
    coordination_dependency_graphs_equal,
    count_coordination_graph_edge_states,
    count_coordination_graph_node_states,
    validate_coordination_dependency_graph_non_execution,
    validate_coordination_manifest_compatibility,
    validate_dependency_direction_visibility,
    validate_dependency_graph_continuity,
    validate_dependency_graph_lineage_continuity,
    validate_dependency_graph_visibility,
)
from refresh_coordination.coordination_dependency_graph_hashing import (  # noqa: E402
    deterministic_coordination_dependency_graph_hash,
    hash_continuity_aware_dependency_reference,
    hash_coordination_dependency_graph,
    hash_coordination_dependency_graph_identity,
    hash_coordination_direction_visibility,
    hash_coordination_graph_edge,
    hash_coordination_graph_node,
    hash_lineage_aware_dependency_reference,
)
from refresh_coordination.coordination_dependency_graph_models import (  # noqa: E402
    V4_2_COORDINATION_DEPENDENCY_GRAPH_GENERATED_AT,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_PHASE_ID,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_BLOCKED,
    V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_STABLE,
    default_coordination_dependency_graph,
)
from refresh_coordination.coordination_dependency_graph_serialization import (  # noqa: E402
    export_coordination_dependency_graph,
    serialize_coordination_dependency_graph,
)
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_dependency_graph_governance_report.json")


def _reordered_coordination_dependency_graph():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    return replace(
        graph,
        nodes=tuple(reversed(graph.nodes)),
        edges=tuple(reversed(graph.edges)),
        lineage_references=tuple(reversed(graph.lineage_references)),
        continuity_references=tuple(reversed(graph.continuity_references)),
        diagnostics=tuple(reversed(graph.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_dependency_graph_hash(payload)


def build_v4_2_coordination_dependency_graph_governance_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    repeated = default_coordination_dependency_graph(manifest)
    reordered = _reordered_coordination_dependency_graph()
    exported = export_coordination_dependency_graph(graph)
    direction = validate_dependency_direction_visibility(graph)
    visibility = validate_dependency_graph_visibility(graph)
    lineage = validate_dependency_graph_lineage_continuity(graph)
    continuity = validate_dependency_graph_continuity(graph)
    compatibility = validate_coordination_manifest_compatibility(graph, manifest)
    non_execution = validate_coordination_dependency_graph_non_execution(graph)
    diagnostics = build_coordination_dependency_graph_diagnostics(graph, manifest)
    serialization_first = serialize_coordination_dependency_graph(graph)
    serialization_second = serialize_coordination_dependency_graph(repeated)
    serialization_reordered = serialize_coordination_dependency_graph(reordered)
    graph_hash = hash_coordination_dependency_graph(graph)
    repeated_hash = hash_coordination_dependency_graph(repeated)
    reordered_hash = hash_coordination_dependency_graph(reordered)
    validation_error_count = sum(
        [
            0 if direction["valid"] else 1,
            0 if visibility["valid"] else 1,
            0 if lineage["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if graph_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_dependency_graphs_equal(graph, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_DEPENDENCY_GRAPH_STATUS_BLOCKED
    )
    exported_node_order = [item["node_id"] for item in exported["nodes"]]
    expected_node_order = [
        item["node_id"] for item in sorted(exported["nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_edge_order = [item["edge_id"] for item in exported["edges"]]
    expected_edge_order = [
        item["edge_id"] for item in sorted(exported["edges"], key=lambda item: (item["deterministic_order"], item["edge_id"]))
    ]
    node_hashes = [hash_coordination_graph_node(node) for node in graph.nodes]
    edge_hashes = [hash_coordination_graph_edge(edge) for edge in graph.edges]
    lineage_hashes = [
        hash_lineage_aware_dependency_reference(reference) for reference in graph.lineage_references
    ]
    continuity_hashes = [
        hash_continuity_aware_dependency_reference(reference) for reference in graph.continuity_references
    ]
    report = {
        "schema_version": V4_2_COORDINATION_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_DEPENDENCY_GRAPH_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_DEPENDENCY_GRAPH_PHASE_ID,
        "phase_name": "v4.2_phase_2_coordination_dependency_graph_governance",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination dependency graph governance without execution behavior",
        "graph_mode": "descriptive_only_non_executable",
        "foundation_status": status,
        "graph_counts": {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "lineage_reference_count": len(graph.lineage_references),
            "continuity_reference_count": len(graph.continuity_references),
            "diagnostic_count": len(graph.diagnostics),
            "node_state_counts": count_coordination_graph_node_states(graph.nodes),
            "edge_state_counts": count_coordination_graph_edge_states(graph.edges),
        },
        "dependency_direction_visibility": {
            "direction_visibility_hash": hash_coordination_direction_visibility(graph.direction_visibility),
            "direction_validation": direction,
            "directional_edge_ids": graph.direction_visibility.directional_edge_ids,
            "reverse_dependency_visibility": graph.direction_visibility.reverse_dependency_visibility,
            "ambiguous_direction_visibility": graph.direction_visibility.ambiguous_direction_visibility,
        },
        "blocked_dependency_visibility": {
            "blocked_node_ids": visibility["blocked_node_ids"],
            "blocked_edge_ids": visibility["blocked_edge_ids"],
            "blocked_dependencies_visible": visibility["blocked_dependencies_visible"],
        },
        "prohibited_dependency_visibility": {
            "prohibited_node_ids": visibility["prohibited_node_ids"],
            "prohibited_edge_ids": visibility["prohibited_edge_ids"],
            "prohibited_dependencies_visible": visibility["prohibited_dependencies_visible"],
            "prohibited_capability_count": len(graph.prohibited_dependency_visibility.prohibited_capabilities),
        },
        "unsupported_dependency_visibility": {
            "unsupported_node_ids": visibility["unsupported_node_ids"],
            "unsupported_edge_ids": visibility["unsupported_edge_ids"],
            "stale_node_ids": visibility["stale_node_ids"],
            "stale_edge_ids": visibility["stale_edge_ids"],
            "unsupported_dependencies_visible": visibility["unsupported_dependencies_visible"],
            "stale_dependencies_visible": visibility["stale_dependencies_visible"],
        },
        "lineage_visibility": {
            "lineage_hashes": lineage_hashes,
            "lineage_validation": lineage,
        },
        "continuity_visibility": {
            "continuity_hashes": continuity_hashes,
            "continuity_validation": continuity,
        },
        "coordination_manifest_compatibility": compatibility,
        "graph_diagnostics": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "fail_visible_dependency_count": diagnostics["fail_visible_dependency_count"],
        },
        "hashing_stability_evidence": {
            "stable": graph_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_dependency_graph_governance",
            "graph_hash": graph_hash,
            "repeated_graph_hash": repeated_hash,
            "reordered_graph_hash": reordered_hash,
            "identity_hash": hash_coordination_dependency_graph_identity(graph.identity),
            "node_hashes": node_hashes,
            "edge_hashes": edge_hashes,
            "lineage_hashes": lineage_hashes,
            "continuity_hashes": continuity_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_dependency_graph_governance",
            "payload_length": len(serialization_first),
            "node_order_preserved": exported_node_order == expected_node_order,
            "edge_order_preserved": exported_edge_order == expected_edge_order,
            "blocked_dependencies_preserved": visibility["blocked_dependencies_visible"],
            "prohibited_dependencies_preserved": visibility["prohibited_dependencies_visible"],
            "unsupported_dependencies_preserved": visibility["unsupported_dependencies_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": graph_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_dependency_graphs_equal(graph, repeated),
            "stable_node_ordering_verified": exported_node_order == expected_node_order,
            "stable_edge_ordering_verified": exported_edge_order == expected_edge_order,
            "dependency_direction_visibility_verified": direction["valid"],
            "blocked_dependency_visibility_verified": visibility["blocked_dependencies_visible"],
            "prohibited_dependency_visibility_verified": visibility["prohibited_dependencies_visible"],
            "unsupported_dependency_visibility_verified": visibility["unsupported_dependencies_visible"],
            "lineage_continuity_verified": lineage["valid"],
            "continuity_verified": continuity["valid"],
            "coordination_manifest_compatibility_verified": compatibility["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_dependency_graph": exported,
        "explicit_limitations": list(graph.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(graph.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination dependency graph JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_dependency_graph_governance_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
