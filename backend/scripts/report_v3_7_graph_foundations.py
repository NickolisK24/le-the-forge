"""Generate the v3.7 deterministic orchestration graph foundations report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration.v3_7_graph_explainability import (  # noqa: E402
    V37_EXPLAINABILITY_STABLE,
    explain_v3_7_graph,
    export_v3_7_graph_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_hashing import (  # noqa: E402
    hash_v3_7_graph,
    validate_v3_7_graph_hash_stability,
)
from app.runtime_orchestration.v3_7_graph_models import (  # noqa: E402
    V3_7_GRAPH_SCHEMA_VERSION,
    default_v3_7_orchestration_planning_graph,
)
from app.runtime_orchestration.v3_7_graph_provenance import (  # noqa: E402
    V37_PROVENANCE_CONTINUITY_PRESERVED,
    audit_v3_7_graph_provenance,
    export_v3_7_graph_provenance_continuity_result,
)
from app.runtime_orchestration.v3_7_graph_serialization import (  # noqa: E402
    export_v3_7_graph,
    export_v3_7_graph_counts,
    validate_v3_7_graph_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_validation import (  # noqa: E402
    V37_GRAPH_VALIDATION_STABLE,
    export_v3_7_graph_validation_result,
    validate_v3_7_graph,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_foundations_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    graph = default_v3_7_orchestration_planning_graph()
    validation = validate_v3_7_graph(graph)
    provenance = audit_v3_7_graph_provenance(graph)
    explainability = explain_v3_7_graph(graph)
    serialization = validate_v3_7_graph_serialization_stability(graph)
    hashing = validate_v3_7_graph_hash_stability(graph)
    counts = export_v3_7_graph_counts(graph)
    validation_export = export_v3_7_graph_validation_result(validation)
    report = {
        "schema_version": "v3_7.graph_foundations_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_deterministic_orchestration_graph_foundations",
        "repo_root": str(root),
        "graph_schema_version": V3_7_GRAPH_SCHEMA_VERSION,
        "architectural_purpose": "deterministic orchestration planning graph foundations",
        "structural_orchestration_reasoning_only": True,
        "planning_only": True,
        "non_executable": True,
        "nodes_do_not_imply_executable_behavior": True,
        "edges_do_not_imply_execution_flow": True,
        "orchestration_execution_enabled": False,
        "graph_execution_enabled": False,
        "graph_traversal_execution_enabled": False,
        "runtime_dispatch_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "mutation_enabled": False,
        "persistent_runtime_writes_enabled": False,
        "background_processing_enabled": False,
        "optimization_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "graph_model_counts": _graph_model_counts(),
        "graph_structure_counts": counts,
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_node_identity_count": validation.duplicate_node_identity_count,
            "duplicate_edge_identity_count": validation.duplicate_edge_identity_count,
            "invalid_edge_reference_count": validation.invalid_edge_reference_count,
            "unsupported_state_visible_count": validation.unsupported_state_visible_count,
            "prohibited_state_visible_count": validation.prohibited_state_visible_count,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_VALIDATION_STABLE,
            "deterministic_serialization_coverage": serialization["stable"],
            "deterministic_hashing_coverage": hashing["stable"],
            "explainability_coverage": explainability.explainability_status == V37_EXPLAINABILITY_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_PROVENANCE_CONTINUITY_PRESERVED,
            "prohibited_state_detection_coverage": validation.prohibited_state_visible_count > 0,
            "unsupported_state_detection_coverage": validation.unsupported_state_visible_count > 0,
            "governance_continuity_coverage": validation.governance_continuity_preserved,
            "replay_continuity_coverage": validation.replay_continuity_preserved,
            "rollback_continuity_coverage": validation.rollback_continuity_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "graph_hash": hash_v3_7_graph(graph),
            "validation_hash": validation.deterministic_validation_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "graph_export": export_v3_7_graph(graph),
        "validation_result": validation_export,
        "provenance_result": export_v3_7_graph_provenance_continuity_result(provenance),
        "explainability_result": export_v3_7_graph_explainability_result(explainability),
        "explicit_limitations": [
            "graphs are non-executable",
            "edges do not imply execution",
            "nodes do not imply executable behavior",
            "no orchestration capability exists in this graph foundation",
            "no runtime routing exists",
            "no scheduling exists",
            "no dispatch exists",
            "no execution flow exists",
            "structural orchestration reasoning only",
        ],
        "summary": {
            "graph_foundations_status": validation.validation_status,
            "structural_orchestration_reasoning_only": True,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "governance_continuity_verified": validation.governance_continuity_preserved,
            "non_execution_guarantee_verified": validation.non_execution_guarantee_preserved,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Foundations",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 establishes deterministic orchestration planning graph foundations for structural orchestration reasoning only.",
        "",
        "Graphs are NON-executable.",
        "",
        "Edges do NOT imply execution.",
        "",
        "Nodes do NOT imply executable behavior.",
        "",
        "No orchestration capability exists.",
        "",
        "No runtime routing exists.",
        "",
        "No scheduling exists.",
        "",
        "No dispatch exists.",
        "",
        "No execution flow exists.",
        "",
        "The graph foundation is structural orchestration reasoning only.",
        "",
        "## Deterministic Scope",
        "",
        f"- Graph schema version: `{report['graph_schema_version']}`",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Graph hash: `{report['deterministic_guarantees']['graph_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Nodes: `{report['graph_structure_counts']['node_count']}`",
        f"- Edges: `{report['graph_structure_counts']['edge_count']}`",
        f"- Governance boundaries: `{report['graph_structure_counts']['governance_boundary_count']}`",
        f"- Compatibility boundaries: `{report['graph_structure_counts']['compatibility_boundary_count']}`",
        f"- Unsupported domains visible: `{report['validation_totals']['unsupported_state_visible_count']}`",
        f"- Prohibited domains visible: `{report['validation_totals']['prohibited_state_visible_count']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic graph structure integrity",
        "- deterministic graph serialization",
        "- deterministic graph hashing",
        "- replay continuity",
        "- rollback continuity",
        "- provenance continuity",
        "- explainability continuity",
        "- governance continuity",
        "- fail-visible unsupported graph states",
        "- fail-visible prohibited graph states",
        "- structural orchestration reasoning only",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add orchestration execution.",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add runtime dispatch.",
        "",
        "This implementation does not add scheduling.",
        "",
        "This implementation does not add routing.",
        "",
        "This implementation does not add autonomous orchestration.",
        "",
        "This implementation does not add optimization or recommendation behavior.",
        "",
        "This implementation does not add mutation engines, persistent runtime writes, background processing, or hidden graph behavior.",
        "",
        "Graph relationships are structural reasoning relationships only.",
        "",
        "Structural orchestration reasoning only remains the controlling interpretation for every node, edge, boundary, and evidence record.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _graph_model_counts() -> dict[str, int]:
    return {
        "graph_identity_models": 1,
        "graph_metadata_models": 1,
        "graph_provenance_models": 1,
        "graph_node_identity_models": 1,
        "graph_edge_identity_models": 1,
        "graph_governance_boundary_models": 1,
        "graph_compatibility_boundary_models": 1,
        "graph_visibility_finding_models": 1,
        "graph_node_models": 1,
        "graph_edge_models": 1,
        "graph_explainability_evidence_models": 1,
        "graph_continuity_evidence_models": 1,
        "graph_validation_models": 2,
        "graph_explainability_result_models": 1,
        "graph_provenance_result_models": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_foundations_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_foundations_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_FOUNDATIONS.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
