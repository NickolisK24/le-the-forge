"""Generate deterministic v4.2 coordination diagnostics explainability evidence."""

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

from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_aggregation import (  # noqa: E402
    build_coordination_diagnostics_aggregation,
    coordination_diagnostics_equal,
    count_coordination_diagnostic_states,
    validate_coordination_diagnostic_aggregation,
    validate_coordination_diagnostics_non_execution,
    validate_dependency_graph_diagnostics_compatibility,
    validate_diagnostic_severity_visibility,
    validate_drift_diagnostics_compatibility,
    validate_lineage_diagnostics_compatibility,
    validate_manifest_diagnostics_compatibility,
    validate_routing_diagnostics_compatibility,
    validate_sequencing_diagnostics_compatibility,
)
from refresh_coordination.coordination_diagnostics_hashing import (  # noqa: E402
    deterministic_coordination_diagnostics_hash,
    hash_coordination_diagnostics_explainability,
    hash_coordination_diagnostics_identity,
    hash_cross_layer_coordination_diagnostic_record,
    hash_diagnostic_severity_visibility,
    hash_fail_visible_explanation_summary,
    hash_state_aggregation_visibility,
)
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    V4_2_COORDINATION_DIAGNOSTICS_GENERATED_AT,
    V4_2_COORDINATION_DIAGNOSTICS_PHASE_ID,
    V4_2_COORDINATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_DIAGNOSTICS_STATUS_BLOCKED,
    V4_2_COORDINATION_DIAGNOSTICS_STATUS_STABLE,
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_diagnostics_serialization import (  # noqa: E402
    export_coordination_diagnostics_explainability,
    serialize_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_explainability import (  # noqa: E402
    build_coordination_explainability_evidence,
    validate_fail_visible_explanation_summary,
)
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_diagnostics_explainability_report.json")


def _sources():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    drift = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    return manifest, graph, lineage, sequencing, routing, drift


def _reordered_coordination_diagnostics_explainability():
    manifest, graph, lineage, sequencing, routing, drift = _sources()
    diagnostics = default_coordination_diagnostics_explainability(manifest, graph, lineage, sequencing, routing, drift)
    return replace(
        diagnostics,
        manifest_diagnostic_references=tuple(reversed(diagnostics.manifest_diagnostic_references)),
        dependency_graph_diagnostic_references=tuple(reversed(diagnostics.dependency_graph_diagnostic_references)),
        lineage_diagnostic_references=tuple(reversed(diagnostics.lineage_diagnostic_references)),
        sequencing_diagnostic_references=tuple(reversed(diagnostics.sequencing_diagnostic_references)),
        routing_diagnostic_references=tuple(reversed(diagnostics.routing_diagnostic_references)),
        drift_diagnostic_references=tuple(reversed(diagnostics.drift_diagnostic_references)),
        diagnostic_records=tuple(reversed(diagnostics.diagnostic_records)),
        severity_visibility=tuple(reversed(diagnostics.severity_visibility)),
        explanation_records=tuple(reversed(diagnostics.explanation_records)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_diagnostics_hash(payload)


def build_v4_2_coordination_diagnostics_explainability_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest, graph, lineage, sequencing, routing, drift = _sources()
    diagnostics = default_coordination_diagnostics_explainability(manifest, graph, lineage, sequencing, routing, drift)
    repeated = default_coordination_diagnostics_explainability(manifest, graph, lineage, sequencing, routing, drift)
    reordered = _reordered_coordination_diagnostics_explainability()
    exported = export_coordination_diagnostics_explainability(diagnostics)
    aggregation = validate_coordination_diagnostic_aggregation(diagnostics)
    severity = validate_diagnostic_severity_visibility(diagnostics)
    explainability = validate_fail_visible_explanation_summary(diagnostics)
    explainability_evidence = build_coordination_explainability_evidence(diagnostics)
    manifest_compatibility = validate_manifest_diagnostics_compatibility(diagnostics, manifest)
    graph_compatibility = validate_dependency_graph_diagnostics_compatibility(diagnostics, graph, manifest)
    lineage_compatibility = validate_lineage_diagnostics_compatibility(diagnostics, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_diagnostics_compatibility(
        diagnostics,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    routing_compatibility = validate_routing_diagnostics_compatibility(
        diagnostics,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    drift_compatibility = validate_drift_diagnostics_compatibility(
        diagnostics,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    non_execution = validate_coordination_diagnostics_non_execution(diagnostics)
    aggregation_evidence = build_coordination_diagnostics_aggregation(
        diagnostics,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
    )
    serialization_first = serialize_coordination_diagnostics_explainability(diagnostics)
    serialization_second = serialize_coordination_diagnostics_explainability(repeated)
    serialization_reordered = serialize_coordination_diagnostics_explainability(reordered)
    diagnostics_hash = hash_coordination_diagnostics_explainability(diagnostics)
    repeated_hash = hash_coordination_diagnostics_explainability(repeated)
    reordered_hash = hash_coordination_diagnostics_explainability(reordered)
    validation_error_count = sum(
        [
            0 if aggregation["valid"] else 1,
            0 if severity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if lineage_compatibility["valid"] else 1,
            0 if sequencing_compatibility["valid"] else 1,
            0 if routing_compatibility["valid"] else 1,
            0 if drift_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if diagnostics_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_diagnostics_equal(diagnostics, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_DIAGNOSTICS_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_DIAGNOSTICS_STATUS_BLOCKED
    )
    exported_record_order = [item["diagnostic_record_id"] for item in exported["diagnostic_records"]]
    expected_record_order = [
        item["diagnostic_record_id"]
        for item in sorted(
            exported["diagnostic_records"],
            key=lambda item: (item["deterministic_order"], item["diagnostic_record_id"]),
        )
    ]
    record_hashes = [
        hash_cross_layer_coordination_diagnostic_record(record) for record in diagnostics.diagnostic_records
    ]
    report = {
        "schema_version": V4_2_COORDINATION_DIAGNOSTICS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_DIAGNOSTICS_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_DIAGNOSTICS_PHASE_ID,
        "phase_name": "v4.2_phase_7_coordination_diagnostics_explainability",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination diagnostics and explainability aggregation without remediation or execution behavior",
        "diagnostics_mode": "descriptive_only_non_executable_non_remediating",
        "diagnostics_status": status,
        "diagnostic_counts": {
            "manifest_diagnostic_reference_count": len(diagnostics.manifest_diagnostic_references),
            "dependency_graph_diagnostic_reference_count": len(diagnostics.dependency_graph_diagnostic_references),
            "lineage_diagnostic_reference_count": len(diagnostics.lineage_diagnostic_references),
            "sequencing_diagnostic_reference_count": len(diagnostics.sequencing_diagnostic_references),
            "routing_diagnostic_reference_count": len(diagnostics.routing_diagnostic_references),
            "drift_diagnostic_reference_count": len(diagnostics.drift_diagnostic_references),
            "diagnostic_record_count": len(diagnostics.diagnostic_records),
            "explanation_record_count": len(diagnostics.explanation_records),
            "diagnostic_state_counts": count_coordination_diagnostic_states(diagnostics.diagnostic_records),
        },
        "compatibility_visibility": {
            "manifest": manifest_compatibility,
            "dependency_graph": graph_compatibility,
            "lineage": lineage_compatibility,
            "sequencing": sequencing_compatibility,
            "routing": routing_compatibility,
            "drift": drift_compatibility,
        },
        "state_aggregation_visibility": {
            "aggregation_validation": aggregation,
            "unsupported_aggregation_hash": hash_state_aggregation_visibility(
                diagnostics.unsupported_state_aggregation
            ),
            "prohibited_aggregation_hash": hash_state_aggregation_visibility(
                diagnostics.prohibited_state_aggregation
            ),
            "blocked_aggregation_hash": hash_state_aggregation_visibility(diagnostics.blocked_state_aggregation),
            "stale_aggregation_hash": hash_state_aggregation_visibility(diagnostics.stale_state_aggregation),
            "missing_aggregation_hash": hash_state_aggregation_visibility(diagnostics.missing_state_aggregation),
            "conflicting_aggregation_hash": hash_state_aggregation_visibility(
                diagnostics.conflicting_state_aggregation
            ),
        },
        "severity_visibility": {
            "severity_validation": severity,
            "severity_hashes": [
                hash_diagnostic_severity_visibility(visibility)
                for visibility in diagnostics.severity_visibility
            ],
        },
        "explainability_visibility": {
            "summary_validation": explainability,
            "explainability_evidence": explainability_evidence,
            "fail_visible_summary_hash": hash_fail_visible_explanation_summary(
                diagnostics.fail_visible_explanation_summary
            ),
        },
        "diagnostic_aggregation_evidence": aggregation_evidence,
        "hashing_stability_evidence": {
            "stable": diagnostics_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_diagnostics_explainability",
            "diagnostics_hash": diagnostics_hash,
            "repeated_diagnostics_hash": repeated_hash,
            "reordered_diagnostics_hash": reordered_hash,
            "identity_hash": hash_coordination_diagnostics_identity(diagnostics.identity),
            "diagnostic_record_hashes": record_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_diagnostics_explainability",
            "payload_length": len(serialization_first),
            "diagnostic_order_preserved": exported_record_order == expected_record_order,
            "unsupported_aggregation_preserved": aggregation["unsupported_state_visible"],
            "prohibited_aggregation_preserved": aggregation["prohibited_state_visible"],
            "blocked_aggregation_preserved": aggregation["blocked_state_visible"],
            "stale_aggregation_preserved": aggregation["stale_state_visible"],
            "missing_aggregation_preserved": aggregation["missing_state_visible"],
            "conflicting_aggregation_preserved": aggregation["conflicting_state_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "diagnostics_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": diagnostics_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_diagnostics_equal(diagnostics, repeated),
            "stable_diagnostic_ordering_verified": exported_record_order == expected_record_order,
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "lineage_chain_compatibility_verified": lineage_compatibility["valid"],
            "sequencing_compatibility_verified": sequencing_compatibility["valid"],
            "routing_compatibility_verified": routing_compatibility["valid"],
            "drift_compatibility_verified": drift_compatibility["valid"],
            "unsupported_aggregation_verified": aggregation["unsupported_state_visible"],
            "prohibited_aggregation_verified": aggregation["prohibited_state_visible"],
            "blocked_aggregation_verified": aggregation["blocked_state_visible"],
            "stale_aggregation_verified": aggregation["stale_state_visible"],
            "missing_aggregation_verified": aggregation["missing_state_visible"],
            "conflicting_aggregation_verified": aggregation["conflicting_state_visible"],
            "severity_visibility_verified": severity["valid"],
            "fail_visible_explanation_summary_verified": explainability["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "automatic_correction_disabled": non_execution["automatic_correction_disabled"],
            "drift_correction_disabled": non_execution["drift_correction_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_diagnostics_explainability": exported,
        "explicit_limitations": list(diagnostics.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(diagnostics.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination diagnostics JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_diagnostics_explainability_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"diagnostics_status={report['diagnostics_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
