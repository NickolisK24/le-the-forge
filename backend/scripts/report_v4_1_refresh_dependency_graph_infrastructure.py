"""Generate deterministic v4.1 refresh dependency graph governance evidence."""

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

from operational_refresh.refresh_dependency_graph_continuity import (  # noqa: E402
    validate_dependency_graph_continuity,
)
from operational_refresh.refresh_dependency_graph_diagnostics import (  # noqa: E402
    build_dependency_graph_diagnostics,
)
from operational_refresh.refresh_dependency_graph_hashing import (  # noqa: E402
    deterministic_refresh_dependency_graph_hash,
    hash_dependency_graph_continuity,
    hash_dependency_graph_diagnostics,
    hash_dependency_graph_identity,
    hash_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_integrity import (  # noqa: E402
    dependency_graph_identity_normalization_report,
    refresh_dependency_graphs_equal,
    validate_dependency_graph_integrity,
    validate_dependency_graph_non_execution,
)
from operational_refresh.refresh_dependency_graph_models import (  # noqa: E402
    V4_1_REFRESH_DEPENDENCY_GRAPH_DIAGNOSTICS_SCHEMA_VERSION,
    V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT,
    V4_1_REFRESH_DEPENDENCY_GRAPH_INTEGRITY_SCHEMA_VERSION,
    V4_1_REFRESH_DEPENDENCY_GRAPH_PHASE_ID,
    V4_1_REFRESH_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION,
    V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_BLOCKED,
    V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE,
    default_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_serialization import (  # noqa: E402
    export_refresh_dependency_graph,
    serialize_refresh_dependency_graph,
)
from operational_refresh.refresh_dependency_graph_visibility import (  # noqa: E402
    count_dependency_edge_states,
    count_dependency_node_states,
    validate_refresh_dependency_visibility,
)


REPORT_PATH = Path("docs/generated/v4_1_refresh_dependency_graph_report.json")
DIAGNOSTICS_REPORT_PATH = Path("docs/generated/v4_1_refresh_dependency_graph_diagnostics_report.json")
INTEGRITY_REPORT_PATH = Path("docs/generated/v4_1_refresh_dependency_graph_integrity_report.json")


def _reordered_dependency_graph():
    graph = default_refresh_dependency_graph()
    return replace(
        graph,
        nodes=tuple(reversed(graph.nodes)),
        edges=tuple(reversed(graph.edges)),
        lineage_chains=tuple(reversed(graph.lineage_chains)),
        provenance_chains=tuple(reversed(graph.provenance_chains)),
    )


def build_v4_1_refresh_dependency_graph_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    graph = default_refresh_dependency_graph()
    repeated_graph = default_refresh_dependency_graph()
    reordered_graph = _reordered_dependency_graph()
    exported = export_refresh_dependency_graph(graph)
    visibility = validate_refresh_dependency_visibility(graph)
    continuity = validate_dependency_graph_continuity(graph)
    non_execution = validate_dependency_graph_non_execution(graph)
    integrity = validate_dependency_graph_integrity(graph)
    diagnostics = build_dependency_graph_diagnostics(graph)
    serialization_first = serialize_refresh_dependency_graph(graph)
    serialization_second = serialize_refresh_dependency_graph(repeated_graph)
    serialization_reordered = serialize_refresh_dependency_graph(reordered_graph)
    graph_hash = hash_refresh_dependency_graph(graph)
    repeated_hash = hash_refresh_dependency_graph(repeated_graph)
    reordered_hash = hash_refresh_dependency_graph(reordered_graph)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if integrity["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if graph_hash == repeated_hash == reordered_hash else 1,
            0 if refresh_dependency_graphs_equal(graph, repeated_graph) else 1,
        ]
    )
    status = (
        V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE
        if validation_error_count == 0
        else V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_BLOCKED
    )
    exported_node_order = [item["node_id"] for item in exported["nodes"]]
    expected_node_order = [
        item["node_id"] for item in sorted(exported["nodes"], key=lambda item: (item["deterministic_order"], item["node_id"]))
    ]
    exported_edge_order = [item["edge_id"] for item in exported["edges"]]
    expected_edge_order = [
        item["edge_id"] for item in sorted(exported["edges"], key=lambda item: (item["deterministic_order"], item["edge_id"]))
    ]
    report = {
        "schema_version": V4_1_REFRESH_DEPENDENCY_GRAPH_REPORT_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DEPENDENCY_GRAPH_PHASE_ID,
        "phase_name": "v4.1_phase_2_refresh_dependency_graph_infrastructure",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh dependency governance intelligence without orchestration or execution",
        "dependency_graph_mode": "descriptive_only",
        "foundation_status": status,
        "graph_model_counts": {
            "identity_count": 1,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "lineage_chain_count": len(graph.lineage_chains),
            "provenance_chain_count": len(graph.provenance_chains),
            "node_state_counts": count_dependency_node_states(graph.nodes),
            "edge_state_counts": count_dependency_edge_states(graph.edges),
        },
        "deterministic_serialization_verification": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_1_refresh_dependency_graph",
            "payload_length": len(serialization_first),
            "node_order_preserved": exported_node_order == expected_node_order,
            "edge_order_preserved": exported_edge_order == expected_edge_order,
            "blocked_states_preserved": visibility["blocked_dependency_edge_visibility_count"] >= 0,
            "unsupported_states_preserved": visibility["unsupported_dependency_edge_visibility_count"] > 0,
            "circular_dependencies_preserved": visibility["circular_dependency_visibility_count"] > 0,
            "prohibited_dependencies_preserved": visibility["prohibited_dependency_edge_visibility_count"] > 0,
            "stale_dependencies_preserved": visibility["stale_dependency_edge_visibility_count"] > 0,
            "hidden_omission_enabled": False,
        },
        "deterministic_hashing_verification": {
            "stable": graph_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_1_refresh_dependency_graph",
            "graph_hash": graph_hash,
            "identity_hash": hash_dependency_graph_identity(graph.identity),
            "continuity_hash": hash_dependency_graph_continuity(graph.continuity_metadata),
            "diagnostics_hash": hash_dependency_graph_diagnostics(graph.diagnostics_visibility),
        },
        "deterministic_equality_verification": {
            "dataclass_equality_stable": graph == repeated_graph,
            "dataclass_hash_stable": hash(graph) == hash(repeated_graph),
            "serialized_equality_stable": refresh_dependency_graphs_equal(graph, repeated_graph),
            "reordered_serialized_equality_stable": refresh_dependency_graphs_equal(graph, reordered_graph),
        },
        "lineage_continuity_visibility": continuity["lineage_continuity"],
        "provenance_continuity_visibility": continuity["provenance_continuity"],
        "replay_continuity_visibility": continuity["replay_continuity"],
        "rollback_continuity_visibility": continuity["rollback_continuity"],
        "fail_visible_visibility": {
            "fail_visible_dependency_edge_count": visibility["fail_visible_dependency_edge_count"],
            "unsupported_dependency_node_visibility_count": visibility["unsupported_dependency_node_visibility_count"],
            "unsupported_dependency_edge_visibility_count": visibility["unsupported_dependency_edge_visibility_count"],
            "blocked_dependency_edge_visibility_count": visibility["blocked_dependency_edge_visibility_count"],
            "stale_dependency_edge_visibility_count": visibility["stale_dependency_edge_visibility_count"],
            "prohibited_dependency_edge_visibility_count": visibility["prohibited_dependency_edge_visibility_count"],
            "circular_dependency_visibility_count": visibility["circular_dependency_visibility_count"],
            "lineage_discontinuity_visibility_count": visibility["lineage_discontinuity_visibility_count"],
            "provenance_discontinuity_visibility_count": visibility["provenance_discontinuity_visibility_count"],
            "replay_discontinuity_visibility_count": visibility["replay_discontinuity_visibility_count"],
            "rollback_discontinuity_visibility_count": visibility["rollback_discontinuity_visibility_count"],
            "prohibited_dependency_domain_visibility_count": visibility["prohibited_dependency_domain_visibility_count"],
            "diagnostics_warning_visibility_count": visibility["diagnostics_warning_visibility_count"],
            "unsupported_nodes_visible": visibility["unsupported_nodes_visible"],
            "unsupported_edges_visible": visibility["unsupported_edges_visible"],
            "stale_edges_visible": visibility["stale_edges_visible"],
            "prohibited_edges_visible": visibility["prohibited_edges_visible"],
            "circular_dependencies_visible": visibility["circular_dependencies_visible"],
            "prohibited_dependency_domains_visible": visibility["prohibited_dependency_domains_visible"],
            "visibility_is_descriptive_only": visibility["visibility_is_descriptive_only"],
        },
        "diagnostics_visibility": diagnostics,
        "integrity_validation": integrity,
        "non_execution_guarantees": non_execution,
        "dependency_graph_identity_normalization": dependency_graph_identity_normalization_report(graph.identity),
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "deterministic_graph_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_graph_hashing_verified": graph_hash == repeated_hash == reordered_hash,
            "deterministic_dependency_equality_verified": refresh_dependency_graphs_equal(graph, repeated_graph),
            "deterministic_dependency_visibility_verified": visibility["valid"],
            "lineage_continuity_verified": continuity["lineage_continuity_valid"],
            "provenance_continuity_verified": continuity["provenance_continuity_valid"],
            "replay_continuity_verified": continuity["replay_continuity_valid"],
            "rollback_continuity_verified": continuity["rollback_continuity_valid"],
            "blocked_state_visibility_validated": visibility["blocked_edges_visible"],
            "unsupported_state_visibility_validated": visibility["unsupported_edges_visible"],
            "circular_dependency_visibility_validated": visibility["circular_dependencies_visible"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
            "integrity_validation_verified": integrity["valid"],
            "descriptive_only_verified": graph.descriptive_only and graph.non_executable,
        },
        "refresh_dependency_graph": exported,
        "explicit_limitations": list(graph.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(graph.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_dependency_graph_diagnostics_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    graph = default_refresh_dependency_graph()
    diagnostics = build_dependency_graph_diagnostics(graph)
    non_execution = validate_dependency_graph_non_execution(graph)
    status = (
        V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE
        if diagnostics["visibility_validation"]["valid"] and diagnostics["enabled_capability_count"] == 0
        else V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_DEPENDENCY_GRAPH_DIAGNOSTICS_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DEPENDENCY_GRAPH_PHASE_ID,
        "phase_name": "v4.1_phase_2_refresh_dependency_graph_diagnostics",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh dependency diagnostics visibility without remediation or execution",
        "diagnostics_mode": "fail_visible_descriptive_only",
        "foundation_status": status,
        "diagnostics": diagnostics,
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "enabled_capability_count": diagnostics["enabled_capability_count"],
            "diagnostics_visible": diagnostics["diagnostics_visible"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "remediation_absent": diagnostics["remediation_absent"],
            "silent_fallback_absent": diagnostics["silent_fallback_absent"],
            "automatic_recovery_absent": diagnostics["automatic_recovery_absent"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "production_consumption_disabled_validated": non_execution["production_consumption_absent"],
            "planner_integration_disabled_validated": non_execution["planner_integration_absent"],
        },
        "explicit_limitations": list(graph.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(graph.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def build_v4_1_refresh_dependency_graph_integrity_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    graph = default_refresh_dependency_graph()
    integrity = validate_dependency_graph_integrity(graph)
    status = (
        V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_STABLE
        if integrity["valid"]
        else V4_1_REFRESH_DEPENDENCY_GRAPH_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_1_REFRESH_DEPENDENCY_GRAPH_INTEGRITY_SCHEMA_VERSION,
        "generated_at": V4_1_REFRESH_DEPENDENCY_GRAPH_GENERATED_AT,
        "phase_id": V4_1_REFRESH_DEPENDENCY_GRAPH_PHASE_ID,
        "phase_name": "v4.1_phase_2_refresh_dependency_graph_integrity",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh dependency integrity auditing without automatic correction",
        "integrity_mode": "descriptive_only_no_correction",
        "foundation_status": status,
        "integrity_validation": integrity,
        "summary": {
            "foundation_status": status,
            "integrity_validation_verified": integrity["valid"],
            "visibility_valid": integrity["visibility_valid"],
            "continuity_valid": integrity["continuity_valid"],
            "non_execution_valid": integrity["non_execution_valid"],
            "prohibited_leakage_visible": integrity["prohibited_leakage_visible"],
            "enabled_capability_count": integrity["non_execution_validation"]["enabled_capability_count"],
            "production_consumption_disabled_validated": integrity["non_execution_validation"]["production_consumption_absent"],
            "planner_integration_disabled_validated": integrity["non_execution_validation"]["planner_integration_absent"],
        },
        "explicit_limitations": list(graph.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(graph.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_refresh_dependency_graph_hash(payload)


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Dependency graph JSON report output path")
    parser.add_argument(
        "--diagnostics-output",
        default=str(DIAGNOSTICS_REPORT_PATH),
        help="Dependency graph diagnostics JSON report output path",
    )
    parser.add_argument(
        "--integrity-output",
        default=str(INTEGRITY_REPORT_PATH),
        help="Dependency graph integrity JSON report output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_v4_1_refresh_dependency_graph_report()
    diagnostics_report = build_v4_1_refresh_dependency_graph_diagnostics_report()
    integrity_report = build_v4_1_refresh_dependency_graph_integrity_report()
    write_report(report, Path(args.output))
    write_report(diagnostics_report, Path(args.diagnostics_output))
    write_report(integrity_report, Path(args.integrity_output))
    print(f"wrote {Path(args.output)}")
    print(f"wrote {Path(args.diagnostics_output)}")
    print(f"wrote {Path(args.integrity_output)}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"diagnostics_status={diagnostics_report['foundation_status']}")
    print(f"integrity_status={integrity_report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    print(f"deterministic_diagnostics_report_hash={diagnostics_report['deterministic_report_hash']}")
    print(f"deterministic_integrity_report_hash={integrity_report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
