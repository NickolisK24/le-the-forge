"""Generate the v3.7 graph compatibility reasoning report."""

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
from app.runtime_orchestration.v3_7_graph_compatibility_explainability import (  # noqa: E402
    V37_COMPATIBILITY_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_compatibility,
    export_v3_7_graph_compatibility_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_compatibility_models import (  # noqa: E402
    V37_COMPATIBILITY_CLASSIFICATIONS,
    export_v3_7_compatibility_counts,
    export_v3_7_compatibility_map,
    hash_v3_7_compatibility_map,
    validate_v3_7_compatibility_hash_stability,
    validate_v3_7_compatibility_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_compatibility_provenance import (  # noqa: E402
    V37_COMPATIBILITY_PROVENANCE_PRESERVED,
    audit_v3_7_graph_compatibility_provenance,
    export_v3_7_graph_compatibility_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_compatibility_rules import (  # noqa: E402
    build_v3_7_graph_compatibility_map,
)
from app.runtime_orchestration.v3_7_graph_compatibility_validation import (  # noqa: E402
    V37_COMPATIBILITY_VALIDATION_STABLE,
    export_v3_7_graph_compatibility_validation_result,
    validate_v3_7_graph_compatibility,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_compatibility_reasoning_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    compatibility_map = build_v3_7_graph_compatibility_map()
    validation = validate_v3_7_graph_compatibility(compatibility_map)
    provenance = audit_v3_7_graph_compatibility_provenance(compatibility_map)
    explainability = explain_v3_7_graph_compatibility(compatibility_map)
    serialization = validate_v3_7_compatibility_serialization_stability(compatibility_map)
    hashing = validate_v3_7_compatibility_hash_stability(compatibility_map)
    aggregation = compatibility_map.aggregation
    report = {
        "schema_version": "v3_7.graph_compatibility_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_compatibility_reasoning",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph compatibility reasoning",
        "compatibility_reasoning": True,
        "execution_routing": False,
        "planning_only": True,
        "non_executable": True,
        "compatibility_reasoning_is_non_executable": True,
        "compatibility_does_not_authorize_execution": True,
        "edge_compatibility_does_not_imply_traversal": True,
        "node_compatibility_does_not_imply_runtime_ordering": True,
        "compatibility_findings_are_structural_planning_evidence_only": True,
        "prohibited_unsupported_unknown_states_remain_visible": True,
        "graph_execution_enabled": False,
        "node_execution_enabled": False,
        "edge_traversal_execution_enabled": False,
        "runtime_orchestration_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "graph_optimization_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "background_graph_processing_enabled": False,
        "graph_path_selection_enabled": False,
        "compatibility_counts": export_v3_7_compatibility_counts(compatibility_map),
        "compatibility_classification_counts": _count_by(
            (
                item.compatibility_classification
                for item in (
                    compatibility_map.domains
                    + compatibility_map.rules
                    + compatibility_map.node_results
                    + compatibility_map.edge_results
                    + compatibility_map.findings
                )
            ),
            expected_values=V37_COMPATIBILITY_CLASSIFICATIONS,
        ),
        "node_compatibility_counts": _count_by(
            (result.compatibility_classification for result in compatibility_map.node_results)
        ),
        "edge_compatibility_counts": _count_by(
            (result.compatibility_classification for result in compatibility_map.edge_results)
        ),
        "graph_level_compatibility_totals": {
            "compatible_relationship_count": aggregation.compatible_relationship_count,
            "incompatible_relationship_count": aggregation.incompatible_relationship_count,
            "unsupported_relationship_count": aggregation.unsupported_relationship_count,
            "prohibited_relationship_count": aggregation.prohibited_relationship_count,
            "experimental_relationship_count": aggregation.experimental_relationship_count,
            "unknown_relationship_count": aggregation.unknown_relationship_count,
            "governance_restricted_count": aggregation.governance_restricted_count,
            "compatibility_restricted_count": aggregation.compatibility_restricted_count,
            "fail_visible_finding_count": aggregation.fail_visible_finding_count,
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "prohibited_state_count": validation.prohibited_state_count,
            "unsupported_state_count": validation.unsupported_state_count,
            "unknown_state_count": validation.unknown_state_count,
            "missing_metadata_count": validation.missing_metadata_count,
            "governance_aware_outcome_count": validation.governance_aware_outcome_count,
        },
        "prohibited_compatibility_findings": _findings_for(compatibility_map, "prohibited"),
        "unsupported_compatibility_findings": _findings_for(compatibility_map, "unsupported"),
        "unknown_compatibility_findings": _findings_for(compatibility_map, "unknown"),
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "domain_provenance_preserved": provenance.domain_provenance_preserved,
            "rule_provenance_preserved": provenance.rule_provenance_preserved,
            "node_result_provenance_preserved": provenance.node_result_provenance_preserved,
            "edge_result_provenance_preserved": provenance.edge_result_provenance_preserved,
            "finding_provenance_preserved": provenance.finding_provenance_preserved,
            "replay_continuity_preserved": provenance.replay_continuity_preserved,
            "rollback_continuity_preserved": provenance.rollback_continuity_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "node_explanation_count": explainability.node_explanation_count,
            "edge_explanation_count": explainability.edge_explanation_count,
            "compatible_explanation_count": explainability.compatible_explanation_count,
            "incompatible_explanation_count": explainability.incompatible_explanation_count,
            "unsupported_explanation_count": explainability.unsupported_explanation_count,
            "prohibited_explanation_count": explainability.prohibited_explanation_count,
            "unknown_explanation_count": explainability.unknown_explanation_count,
        },
        "governance_aware_compatibility_totals": {
            "governance_aware_outcome_count": validation.governance_aware_outcome_count,
            "governance_restricted_count": aggregation.governance_restricted_count,
            "compatibility_restricted_count": aggregation.compatibility_restricted_count,
            "governance_influenced_explanation_count": explainability.governance_influenced_explanation_count,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "compatibility_hash": hash_v3_7_compatibility_map(compatibility_map),
            "validation_hash": validation.deterministic_validation_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_COMPATIBILITY_VALIDATION_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_COMPATIBILITY_PROVENANCE_PRESERVED,
            "explainability_coverage": (
                explainability.explainability_status == V37_COMPATIBILITY_EXPLAINABILITY_STABLE
            ),
            "deterministic_hash_stability": hashing["stable"],
            "prohibited_visibility_coverage": bool(_findings_for(compatibility_map, "prohibited")),
            "unsupported_visibility_coverage": bool(_findings_for(compatibility_map, "unsupported")),
            "unknown_visibility_coverage": bool(_findings_for(compatibility_map, "unknown")),
            "non_execution_coverage": validation.non_execution_guarantee_preserved,
        },
        "compatibility_map": export_v3_7_compatibility_map(compatibility_map),
        "validation_result": export_v3_7_graph_compatibility_validation_result(validation),
        "provenance_result": export_v3_7_graph_compatibility_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_compatibility_explainability_result(explainability),
        "explicit_limitations": [
            "compatibility reasoning is non-executable",
            "compatibility does not authorize graph execution",
            "edge compatibility does not imply traversal",
            "node compatibility does not imply runtime ordering",
            "compatibility findings are structural planning evidence only",
            "prohibited, unsupported, and unknown states remain visible",
            "compatibility reasoning is not execution routing",
        ],
        "summary": {
            "compatibility_reasoning_status": validation.validation_status,
            "compatibility_reasoning": True,
            "execution_routing": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
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
        "# v3.7 Graph Compatibility Reasoning",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 3 adds deterministic graph compatibility reasoning.",
        "",
        "Compatibility reasoning is NON-executable.",
        "",
        "Compatibility does NOT authorize graph execution.",
        "",
        "Edge compatibility does NOT imply traversal.",
        "",
        "Node compatibility does NOT imply runtime ordering.",
        "",
        "Compatibility findings are structural planning evidence only.",
        "",
        "Prohibited, unsupported, and unknown states remain visible.",
        "",
        "Compatibility reasoning answers whether structures are compatible. Execution routing would choose what path runs. This phase implements compatibility reasoning only, not execution routing.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Compatibility hash: `{report['deterministic_guarantees']['compatibility_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Compatibility domains: `{report['compatibility_counts']['domain_count']}`",
        f"- Compatibility rules: `{report['compatibility_counts']['rule_count']}`",
        f"- Node compatibility results: `{report['compatibility_counts']['node_result_count']}`",
        f"- Edge compatibility results: `{report['compatibility_counts']['edge_result_count']}`",
        f"- Prohibited findings: `{len(report['prohibited_compatibility_findings'])}`",
        f"- Unsupported findings: `{len(report['unsupported_compatibility_findings'])}`",
        f"- Unknown findings: `{len(report['unknown_compatibility_findings'])}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic compatibility classification stability",
        "- compatible relationship visibility",
        "- incompatible relationship visibility",
        "- unsupported relationship visibility",
        "- prohibited relationship visibility",
        "- unknown relationship visibility",
        "- governance-aware compatibility outcomes",
        "- deterministic graph-level aggregation",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- replay-safe compatibility evidence",
        "- rollback-safe compatibility evidence",
        "- deterministic serialization compatibility",
        "- deterministic hashing compatibility",
        "- fail-visible compatibility failures",
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
        "This implementation does not add routing, scheduling, dispatch, graph optimization, recommendation behavior, autonomous orchestration, runtime mutation, background graph processing, implied execution semantics, or graph path selection.",
        "",
        "Compatibility remains planning intelligence, not execution authorization.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _count_by(values: object, expected_values: tuple[str, ...] = ()) -> dict[str, int]:
    counts: dict[str, int] = {value: 0 for value in expected_values}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _findings_for(compatibility_map, classification: str) -> list[dict[str, str]]:
    return [
        {
            "finding_id": finding.finding_id,
            "reason": finding.reason,
            "rule_id": finding.rule_id,
        }
        for finding in sorted(compatibility_map.findings, key=lambda item: item.finding_id)
        if finding.compatibility_classification == classification
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_compatibility_reasoning_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_compatibility_reasoning_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_COMPATIBILITY_REASONING.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
