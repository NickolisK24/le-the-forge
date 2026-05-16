"""Generate the v3.7 graph governance boundary intelligence report."""

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
from app.runtime_orchestration.v3_7_graph_governance_explainability import (  # noqa: E402
    V37_GOVERNANCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_governance,
    export_v3_7_graph_governance_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_governance_models import (  # noqa: E402
    export_v3_7_governance_counts,
    export_v3_7_governance_map,
    hash_v3_7_governance_map,
    validate_v3_7_governance_hash_stability,
    validate_v3_7_governance_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_governance_provenance import (  # noqa: E402
    V37_GOVERNANCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_governance_provenance,
    export_v3_7_graph_governance_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_governance_rules import (  # noqa: E402
    build_v3_7_graph_governance_map,
)
from app.runtime_orchestration.v3_7_graph_governance_validation import (  # noqa: E402
    V37_GOVERNANCE_VALIDATION_STABLE,
    export_v3_7_graph_governance_validation_result,
    validate_v3_7_graph_governance,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_governance_boundaries_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    governance_map = build_v3_7_graph_governance_map()
    validation = validate_v3_7_graph_governance(governance_map)
    provenance = audit_v3_7_graph_governance_provenance(governance_map)
    explainability = explain_v3_7_graph_governance(governance_map)
    serialization = validate_v3_7_governance_serialization_stability(governance_map)
    hashing = validate_v3_7_governance_hash_stability(governance_map)
    report = {
        "schema_version": "v3_7.graph_governance_boundaries_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_governance_boundary_intelligence",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph governance boundary intelligence",
        "governance_intelligence": True,
        "execution_intelligence": False,
        "planning_only": True,
        "non_executable": True,
        "governance_metadata_does_not_enable_orchestration": True,
        "node_relationships_are_structural_only": True,
        "edges_do_not_imply_runtime_traversal": True,
        "governance_reasoning_is_not_orchestration_execution": True,
        "graph_execution_enabled": False,
        "node_execution_enabled": False,
        "edge_traversal_execution_enabled": False,
        "runtime_orchestration_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "optimization_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "graph_evaluation_execution_enabled": False,
        "governance_counts": export_v3_7_governance_counts(governance_map),
        "domain_classification_counts": _count_by(
            (domain.domain_classification for domain in governance_map.domains)
        ),
        "node_classification_counts": _count_by(
            (classification.governance_classification for classification in governance_map.node_classifications)
        ),
        "edge_classification_counts": _count_by(
            (classification.governance_classification for classification in governance_map.edge_classifications)
        ),
        "relationship_finding_counts": _count_by(
            (finding.finding_kind for finding in governance_map.findings)
        ),
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "prohibited_relationship_visible_count": validation.prohibited_relationship_visible_count,
            "unsupported_relationship_visible_count": validation.unsupported_relationship_visible_count,
            "prohibited_edge_relationship_count": validation.prohibited_edge_relationship_count,
            "unsupported_edge_relationship_count": validation.unsupported_edge_relationship_count,
            "missing_metadata_count": validation.missing_metadata_count,
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "domain_provenance_preserved": provenance.domain_provenance_preserved,
            "rule_provenance_preserved": provenance.rule_provenance_preserved,
            "node_classification_provenance_preserved": provenance.node_classification_provenance_preserved,
            "edge_classification_provenance_preserved": provenance.edge_classification_provenance_preserved,
            "replay_continuity_preserved": provenance.replay_continuity_preserved,
            "rollback_continuity_preserved": provenance.rollback_continuity_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "node_explanation_count": explainability.node_explanation_count,
            "edge_explanation_count": explainability.edge_explanation_count,
            "prohibited_relationship_explanation_count": (
                explainability.prohibited_relationship_explanation_count
            ),
            "unsupported_relationship_explanation_count": (
                explainability.unsupported_relationship_explanation_count
            ),
        },
        "governance_continuity_totals": {
            "governance_continuity_preserved": validation.governance_continuity_preserved,
            "provenance_continuity_preserved": validation.provenance_continuity_preserved,
            "explainability_continuity_preserved": validation.explainability_continuity_preserved,
            "replay_continuity_preserved": validation.replay_continuity_preserved,
            "rollback_continuity_preserved": validation.rollback_continuity_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "governance_hash": hash_v3_7_governance_map(governance_map),
            "validation_hash": validation.deterministic_validation_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GOVERNANCE_VALIDATION_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GOVERNANCE_PROVENANCE_PRESERVED,
            "explainability_coverage": (
                explainability.explainability_status == V37_GOVERNANCE_EXPLAINABILITY_STABLE
            ),
            "prohibited_relationship_visibility_coverage": (
                validation.prohibited_relationship_visible_count > 0
            ),
            "unsupported_relationship_visibility_coverage": (
                validation.unsupported_relationship_visible_count > 0
            ),
            "governance_metadata_non_execution_coverage": validation.non_execution_guarantee_preserved,
        },
        "governance_map": export_v3_7_governance_map(governance_map),
        "validation_result": export_v3_7_graph_governance_validation_result(validation),
        "provenance_result": export_v3_7_graph_governance_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_governance_explainability_result(explainability),
        "explicit_limitations": [
            "graphs remain non-executable",
            "governance metadata does not enable orchestration",
            "node relationships are structural only",
            "edges do not imply runtime traversal",
            "governance reasoning is not orchestration execution",
            "governance intelligence is not execution intelligence",
            "routing, scheduling, and dispatch remain prohibited",
        ],
        "summary": {
            "governance_boundary_status": validation.validation_status,
            "governance_intelligence": True,
            "execution_intelligence": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "governance_continuity_verified": validation.governance_continuity_preserved,
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "non_execution_guarantee_verified": validation.non_execution_guarantee_preserved,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Governance Boundaries",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 2 adds deterministic graph governance boundary intelligence.",
        "",
        "Graphs remain NON-executable.",
        "",
        "Governance metadata does NOT enable orchestration.",
        "",
        "Node relationships are structural only.",
        "",
        "Edges do NOT imply runtime traversal.",
        "",
        "Governance reasoning is NOT orchestration execution.",
        "",
        "Governance intelligence is metadata classification, visibility, provenance, and explainability.",
        "",
        "Execution intelligence would imply runtime flow, dispatch, scheduling, routing, traversal, mutation, or autonomous orchestration. This phase includes none of those capabilities.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Governance hash: `{report['deterministic_guarantees']['governance_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Governance domains: `{report['governance_counts']['domain_count']}`",
        f"- Governance rules: `{report['governance_counts']['rule_count']}`",
        f"- Node classifications: `{report['governance_counts']['node_classification_count']}`",
        f"- Edge classifications: `{report['governance_counts']['edge_classification_count']}`",
        f"- Prohibited relationship findings: `{report['relationship_finding_counts']['prohibited_relationship']}`",
        f"- Unsupported relationship findings: `{report['relationship_finding_counts']['unsupported_relationship']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic governance classification stability",
        "- prohibited relationship visibility",
        "- unsupported relationship visibility",
        "- governance continuity preservation",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- deterministic serialization compatibility",
        "- deterministic hashing compatibility",
        "- replay-safe governance evidence",
        "- rollback-safe governance evidence",
        "- fail-visible prohibited states",
        "- fail-visible unsupported states",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add node execution.",
        "",
        "This implementation does not add edge traversal execution.",
        "",
        "This implementation does not add runtime orchestration.",
        "",
        "This implementation does not add routing, scheduling, or dispatch.",
        "",
        "This implementation does not add optimization, recommendation, autonomous orchestration, runtime mutation, graph evaluation execution, execution-capable traversal chains, implicit graph semantics, or dynamic orchestration flow.",
        "",
        "Graph governance intelligence remains deterministic structural governance metadata only.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _count_by(values: object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_governance_boundaries_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_governance_boundaries_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_GOVERNANCE_BOUNDARIES.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
