"""Generate the v3.7 graph evaluation reasoning report."""

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
from app.runtime_orchestration.v3_7_graph_continuity_audit import (  # noqa: E402
    V37_GRAPH_CONTINUITY_AUDIT_STABLE,
    audit_v3_7_graph_continuity,
    export_v3_7_graph_continuity_audit_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_explainability import (  # noqa: E402
    V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_evaluation,
    export_v3_7_graph_evaluation_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_findings import (  # noqa: E402
    count_v3_7_graph_evaluation_findings_by_classification,
)
from app.runtime_orchestration.v3_7_graph_evaluation_models import (  # noqa: E402
    export_v3_7_graph_evaluation_chain,
    export_v3_7_graph_evaluation_counts,
    hash_v3_7_graph_evaluation_chain,
    validate_v3_7_graph_evaluation_hash_stability,
    validate_v3_7_graph_evaluation_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_evaluation_provenance import (  # noqa: E402
    V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
    audit_v3_7_graph_evaluation_provenance,
    export_v3_7_graph_evaluation_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_evaluation_replay import (  # noqa: E402
    build_v3_7_graph_evaluation_replay_packets,
    export_v3_7_graph_evaluation_replay_packets,
    validate_v3_7_graph_evaluation_replay_packet_stability,
)
from app.runtime_orchestration.v3_7_graph_evaluation_traces import (  # noqa: E402
    build_v3_7_graph_evaluation_chain,
)
from app.runtime_orchestration.v3_7_graph_evaluation_validation import (  # noqa: E402
    V37_GRAPH_EVALUATION_VALIDATION_STABLE,
    export_v3_7_graph_evaluation_validation_result,
    validate_v3_7_graph_evaluation,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_evaluation_reasoning_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    chain = build_v3_7_graph_evaluation_chain()
    replay_packets = build_v3_7_graph_evaluation_replay_packets(chain)
    validation = validate_v3_7_graph_evaluation(chain, replay_packets)
    continuity = audit_v3_7_graph_continuity(chain, replay_packets)
    provenance = audit_v3_7_graph_evaluation_provenance(chain, replay_packets)
    explainability = explain_v3_7_graph_evaluation(chain)
    serialization = validate_v3_7_graph_evaluation_serialization_stability(chain)
    hashing = validate_v3_7_graph_evaluation_hash_stability(chain)
    replay_stability = [
        validate_v3_7_graph_evaluation_replay_packet_stability(packet)
        for packet in replay_packets
    ]
    summary = chain.summary
    report = {
        "schema_version": "v3_7.graph_evaluation_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_evaluation_reasoning",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph evaluation reasoning",
        "evaluation_reasoning": True,
        "runtime_orchestration_execution": False,
        "planning_only": True,
        "non_executable": True,
        "evaluation_reasoning_is_non_executable": True,
        "replay_packets_are_not_orchestration_packets": True,
        "evaluation_traces_do_not_imply_traversal": True,
        "evaluation_ordering_does_not_imply_execution_ordering": True,
        "evaluation_findings_are_structural_reasoning_evidence_only": True,
        "graph_evaluation_does_not_authorize_orchestration": True,
        "graph_execution_enabled": False,
        "traversal_execution_enabled": False,
        "runtime_orchestration_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "path_selection_enabled": False,
        "graph_optimization_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "graph_runtime_simulation_enabled": False,
        "hidden_evaluation_side_effects_enabled": False,
        "evaluation_chain_counts": export_v3_7_graph_evaluation_counts(chain),
        "evaluation_finding_counts": count_v3_7_graph_evaluation_findings_by_classification(chain.findings),
        "prohibited_finding_totals": {
            "prohibited_finding_count": summary.prohibited_finding_count,
            "validation_prohibited_state_count": validation.prohibited_state_count,
        },
        "unsupported_finding_totals": {
            "unsupported_finding_count": summary.unsupported_finding_count,
            "validation_unsupported_state_count": validation.unsupported_state_count,
        },
        "unknown_finding_totals": {
            "unknown_finding_count": summary.unknown_finding_count,
            "validation_unknown_state_count": validation.unknown_state_count,
        },
        "replay_packet_totals": {
            "replay_packet_count": len(replay_packets),
            "non_executable_replay_packet_count": sum(
                1 for packet in replay_packets if packet.packet_is_non_executable_replay_evidence
            ),
            "orchestration_runtime_packet_count": sum(1 for packet in replay_packets if packet.orchestration_runtime_packet),
            "execution_authorization_count": sum(1 for packet in replay_packets if packet.execution_authorization),
            "serialization_stable": all(item["serialization_stable"] for item in replay_stability),
            "hash_stable": all(item["hash_stable"] for item in replay_stability),
        },
        "continuity_audit_totals": {
            "audit_status": continuity.audit_status,
            "valid": continuity.valid,
            "finding_count": continuity.finding_count,
            "error_count": continuity.error_count,
            "visibility_finding_count": continuity.visibility_finding_count,
            "evaluation_continuity_preserved": continuity.evaluation_continuity_preserved,
            "governance_continuity_preserved": continuity.governance_continuity_preserved,
            "compatibility_continuity_preserved": continuity.compatibility_continuity_preserved,
            "replay_continuity_preserved": continuity.replay_continuity_preserved,
            "rollback_continuity_preserved": continuity.rollback_continuity_preserved,
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "chain_provenance_preserved": provenance.chain_provenance_preserved,
            "step_provenance_preserved": provenance.step_provenance_preserved,
            "finding_provenance_preserved": provenance.finding_provenance_preserved,
            "trace_provenance_preserved": provenance.trace_provenance_preserved,
            "replay_provenance_preserved": provenance.replay_provenance_preserved,
            "replay_continuity_preserved": provenance.replay_continuity_preserved,
            "rollback_continuity_preserved": provenance.rollback_continuity_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "successful_evaluation_explanation_count": explainability.successful_evaluation_explanation_count,
            "unsuccessful_evaluation_explanation_count": explainability.unsuccessful_evaluation_explanation_count,
            "prohibited_explanation_count": explainability.prohibited_explanation_count,
            "unsupported_explanation_count": explainability.unsupported_explanation_count,
            "unknown_explanation_count": explainability.unknown_explanation_count,
            "governance_influenced_explanation_count": explainability.governance_influenced_explanation_count,
            "compatibility_influenced_explanation_count": explainability.compatibility_influenced_explanation_count,
            "continuity_influenced_explanation_count": explainability.continuity_influenced_explanation_count,
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
            "non_execution_guarantee_preserved": validation.non_execution_guarantee_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "replay_packet_serialization_stable": all(item["serialization_stable"] for item in replay_stability),
            "replay_packet_hash_stable": all(item["hash_stable"] for item in replay_stability),
            "evaluation_hash": hash_v3_7_graph_evaluation_chain(chain),
            "validation_hash": validation.deterministic_validation_hash,
            "continuity_audit_hash": continuity.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_EVALUATION_VALIDATION_STABLE,
            "continuity_audit_coverage": continuity.audit_status == V37_GRAPH_CONTINUITY_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_EVALUATION_PROVENANCE_PRESERVED,
            "explainability_coverage": (
                explainability.explainability_status == V37_GRAPH_EVALUATION_EXPLAINABILITY_STABLE
            ),
            "prohibited_visibility_coverage": summary.prohibited_finding_count > 0,
            "unsupported_visibility_coverage": summary.unsupported_finding_count > 0,
            "unknown_visibility_coverage": summary.unknown_finding_count > 0,
            "non_execution_coverage": validation.non_execution_guarantee_preserved,
        },
        "evaluation_chain": export_v3_7_graph_evaluation_chain(chain),
        "replay_packets": export_v3_7_graph_evaluation_replay_packets(replay_packets),
        "validation_result": export_v3_7_graph_evaluation_validation_result(validation),
        "continuity_audit_result": export_v3_7_graph_continuity_audit_result(continuity),
        "provenance_result": export_v3_7_graph_evaluation_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_evaluation_explainability_result(explainability),
        "explicit_limitations": [
            "evaluation reasoning is non-executable",
            "replay packets are not orchestration packets",
            "evaluation traces do not imply traversal",
            "evaluation ordering does not imply execution ordering",
            "evaluation findings are structural reasoning evidence only",
            "graph evaluation does not authorize orchestration",
            "evaluation reasoning is not runtime orchestration execution",
        ],
        "summary": {
            "evaluation_reasoning_status": validation.validation_status,
            "evaluation_reasoning": True,
            "runtime_orchestration_execution": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
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
        "# v3.7 Graph Evaluation Reasoning",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 4 adds deterministic graph evaluation reasoning.",
        "",
        "Evaluation reasoning is NON-executable.",
        "",
        "Replay packets are NOT orchestration packets.",
        "",
        "Evaluation traces do NOT imply traversal.",
        "",
        "Evaluation ordering does NOT imply execution ordering.",
        "",
        "Evaluation findings are structural reasoning evidence only.",
        "",
        "Graph evaluation does NOT authorize orchestration.",
        "",
        "Evaluation reasoning explains why structures were evaluated a certain way. Runtime orchestration execution decides what runs. This phase implements evaluation reasoning only, not runtime orchestration execution.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Continuity audit status: `{report['continuity_audit_totals']['audit_status']}`",
        f"- Evaluation hash: `{report['deterministic_guarantees']['evaluation_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Evaluation chains: `{report['evaluation_chain_counts']['evaluation_chain_count']}`",
        f"- Evaluation steps: `{report['evaluation_chain_counts']['evaluation_step_count']}`",
        f"- Evaluation traces: `{report['evaluation_chain_counts']['evaluation_trace_count']}`",
        f"- Evaluation findings: `{report['evaluation_chain_counts']['evaluation_finding_count']}`",
        f"- Replay packets: `{report['replay_packet_totals']['replay_packet_count']}`",
        f"- Prohibited findings: `{report['prohibited_finding_totals']['prohibited_finding_count']}`",
        f"- Unsupported findings: `{report['unsupported_finding_totals']['unsupported_finding_count']}`",
        f"- Unknown findings: `{report['unknown_finding_totals']['unknown_finding_count']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic evaluation ordering",
        "- deterministic replay continuity",
        "- deterministic rollback continuity",
        "- deterministic trace serialization",
        "- deterministic hash stability",
        "- fail-visible prohibited findings",
        "- fail-visible unsupported findings",
        "- fail-visible unknown findings",
        "- governance-aware evaluation continuity",
        "- compatibility-aware evaluation continuity",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- replay packet stability",
        "- continuity auditing stability",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add traversal execution.",
        "",
        "This implementation does not add runtime orchestration.",
        "",
        "This implementation does not add routing, scheduling, dispatch, path selection, graph optimization, recommendation systems, autonomous orchestration, runtime mutation, graph runtime simulation, orchestration flow engines, or hidden evaluation side effects.",
        "",
        "Evaluation reasoning remains structural reasoning evidence only, not execution authorization.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_evaluation_reasoning_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_evaluation_reasoning_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_EVALUATION_REASONING.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
