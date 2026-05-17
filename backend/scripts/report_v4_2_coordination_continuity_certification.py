"""Generate deterministic v4.2 coordination continuity certification evidence."""

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

from refresh_coordination.coordination_continuity_certification import (  # noqa: E402
    build_coordination_continuity_certification_evidence,
    validate_descriptive_only_coordination_continuity_certification,
)
from refresh_coordination.coordination_continuity_diagnostics import (  # noqa: E402
    build_coordination_continuity_diagnostics,
    coordination_continuity_certifications_equal,
    count_coordination_continuity_states,
    validate_coordination_continuity_non_execution,
    validate_coordination_continuity_visibility,
    validate_dependency_graph_continuity_compatibility,
    validate_diagnostics_explainability_continuity_compatibility,
    validate_drift_continuity_compatibility,
    validate_lineage_continuity_compatibility,
    validate_manifest_continuity_compatibility,
    validate_routing_continuity_compatibility,
    validate_sequencing_continuity_compatibility,
    validate_cross_layer_continuity_summary,
)
from refresh_coordination.coordination_continuity_hashing import (  # noqa: E402
    deterministic_coordination_continuity_hash,
    hash_continuity_state_visibility,
    hash_coordination_continuity_certification,
    hash_coordination_continuity_diagnostic,
    hash_coordination_continuity_identity,
    hash_cross_layer_continuity_summary,
    hash_cross_layer_coordination_continuity_record,
)
from refresh_coordination.coordination_continuity_models import (  # noqa: E402
    V4_2_COORDINATION_CONTINUITY_GENERATED_AT,
    V4_2_COORDINATION_CONTINUITY_PHASE_ID,
    V4_2_COORDINATION_CONTINUITY_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_CONTINUITY_STATUS_BLOCKED,
    V4_2_COORDINATION_CONTINUITY_STATUS_STABLE,
    default_coordination_continuity_certification,
)
from refresh_coordination.coordination_continuity_serialization import (  # noqa: E402
    export_coordination_continuity_certification,
    serialize_coordination_continuity_certification,
)
from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_continuity_certification_report.json")


def _sources():
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
    return manifest, graph, lineage, sequencing, routing, drift, diagnostics


def _reordered_coordination_continuity_certification():
    manifest, graph, lineage, sequencing, routing, drift, diagnostics = _sources()
    certification = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    return replace(
        certification,
        manifest_continuity_references=tuple(reversed(certification.manifest_continuity_references)),
        dependency_graph_continuity_references=tuple(
            reversed(certification.dependency_graph_continuity_references)
        ),
        lineage_continuity_references=tuple(reversed(certification.lineage_continuity_references)),
        sequencing_continuity_references=tuple(reversed(certification.sequencing_continuity_references)),
        routing_continuity_references=tuple(reversed(certification.routing_continuity_references)),
        drift_continuity_references=tuple(reversed(certification.drift_continuity_references)),
        diagnostics_continuity_references=tuple(reversed(certification.diagnostics_continuity_references)),
        explainability_continuity_references=tuple(
            reversed(certification.explainability_continuity_references)
        ),
        continuity_records=tuple(reversed(certification.continuity_records)),
        diagnostics=tuple(reversed(certification.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_continuity_hash(payload)


def build_v4_2_coordination_continuity_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest, graph, lineage, sequencing, routing, drift, diagnostics = _sources()
    certification = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    repeated = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    reordered = _reordered_coordination_continuity_certification()
    exported = export_coordination_continuity_certification(certification)
    visibility = validate_coordination_continuity_visibility(certification)
    cross_layer_summary = validate_cross_layer_continuity_summary(certification)
    manifest_compatibility = validate_manifest_continuity_compatibility(certification, manifest)
    graph_compatibility = validate_dependency_graph_continuity_compatibility(certification, graph, manifest)
    lineage_compatibility = validate_lineage_continuity_compatibility(
        certification,
        lineage,
        graph,
        manifest,
    )
    sequencing_compatibility = validate_sequencing_continuity_compatibility(
        certification,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    routing_compatibility = validate_routing_continuity_compatibility(
        certification,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    drift_compatibility = validate_drift_continuity_compatibility(
        certification,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    diagnostics_compatibility = validate_diagnostics_explainability_continuity_compatibility(
        certification,
        diagnostics,
        drift,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    non_execution = validate_coordination_continuity_non_execution(certification)
    descriptive_validation = validate_descriptive_only_coordination_continuity_certification(certification)
    continuity_diagnostics = build_coordination_continuity_diagnostics(
        certification,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    certification_evidence = build_coordination_continuity_certification_evidence(certification)
    serialization_first = serialize_coordination_continuity_certification(certification)
    serialization_second = serialize_coordination_continuity_certification(repeated)
    serialization_reordered = serialize_coordination_continuity_certification(reordered)
    continuity_hash = hash_coordination_continuity_certification(certification)
    repeated_hash = hash_coordination_continuity_certification(repeated)
    reordered_hash = hash_coordination_continuity_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if cross_layer_summary["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if lineage_compatibility["valid"] else 1,
            0 if sequencing_compatibility["valid"] else 1,
            0 if routing_compatibility["valid"] else 1,
            0 if drift_compatibility["valid"] else 1,
            0 if diagnostics_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if descriptive_validation["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if continuity_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_continuity_certifications_equal(certification, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_CONTINUITY_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_CONTINUITY_STATUS_BLOCKED
    )
    exported_record_order = [item["continuity_record_id"] for item in exported["continuity_records"]]
    expected_record_order = [
        item["continuity_record_id"]
        for item in sorted(
            exported["continuity_records"],
            key=lambda item: (item["deterministic_order"], item["continuity_record_id"]),
        )
    ]
    report = {
        "schema_version": V4_2_COORDINATION_CONTINUITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_CONTINUITY_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_CONTINUITY_PHASE_ID,
        "phase_name": "v4.2_phase_8_coordination_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination continuity certification without repair inference remediation or execution behavior",
        "continuity_mode": "descriptive_only_non_executable_non_remediating_non_repairing",
        "continuity_status": status,
        "continuity_counts": {
            "manifest_continuity_reference_count": len(certification.manifest_continuity_references),
            "dependency_graph_continuity_reference_count": len(
                certification.dependency_graph_continuity_references
            ),
            "lineage_continuity_reference_count": len(certification.lineage_continuity_references),
            "sequencing_continuity_reference_count": len(certification.sequencing_continuity_references),
            "routing_continuity_reference_count": len(certification.routing_continuity_references),
            "drift_continuity_reference_count": len(certification.drift_continuity_references),
            "diagnostics_continuity_reference_count": len(certification.diagnostics_continuity_references),
            "explainability_continuity_reference_count": len(
                certification.explainability_continuity_references
            ),
            "continuity_record_count": len(certification.continuity_records),
            "continuity_diagnostic_count": len(certification.diagnostics),
            "continuity_state_counts": count_coordination_continuity_states(
                certification.continuity_records
            ),
        },
        "compatibility_visibility": {
            "manifest": manifest_compatibility,
            "dependency_graph": graph_compatibility,
            "lineage": lineage_compatibility,
            "sequencing": sequencing_compatibility,
            "routing": routing_compatibility,
            "drift": drift_compatibility,
            "diagnostics_explainability": diagnostics_compatibility,
        },
        "continuity_visibility": {
            "visibility_validation": visibility,
            "stale_continuity_hash": hash_continuity_state_visibility(
                certification.stale_continuity_visibility
            ),
            "missing_continuity_hash": hash_continuity_state_visibility(
                certification.missing_continuity_visibility
            ),
            "conflicting_continuity_hash": hash_continuity_state_visibility(
                certification.conflicting_continuity_visibility
            ),
            "prohibited_repair_hash": hash_continuity_state_visibility(
                certification.prohibited_repair_visibility
            ),
            "unsupported_transition_hash": hash_continuity_state_visibility(
                certification.unsupported_transition_visibility
            ),
        },
        "cross_layer_continuity_summary": {
            "summary_validation": cross_layer_summary,
            "summary_hash": hash_cross_layer_continuity_summary(
                certification.cross_layer_continuity_summary
            ),
        },
        "continuity_diagnostics": continuity_diagnostics,
        "continuity_certification_evidence": certification_evidence,
        "hashing_stability_evidence": {
            "stable": continuity_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_continuity_certification",
            "continuity_hash": continuity_hash,
            "repeated_continuity_hash": repeated_hash,
            "reordered_continuity_hash": reordered_hash,
            "identity_hash": hash_coordination_continuity_identity(certification.identity),
            "continuity_record_hashes": [
                hash_cross_layer_coordination_continuity_record(record)
                for record in certification.continuity_records
            ],
            "diagnostic_hashes": [
                hash_coordination_continuity_diagnostic(diagnostic)
                for diagnostic in certification.diagnostics
            ],
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_continuity_certification",
            "payload_length": len(serialization_first),
            "continuity_order_preserved": exported_record_order == expected_record_order,
            "stale_continuity_preserved": visibility["stale_continuity_visible"],
            "missing_continuity_preserved": visibility["missing_continuity_visible"],
            "conflicting_continuity_preserved": visibility["conflicting_continuity_visible"],
            "prohibited_repair_preserved": visibility["prohibited_repair_visible"],
            "unsupported_transition_preserved": visibility["unsupported_transition_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "continuity_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": continuity_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_continuity_certifications_equal(
                certification,
                repeated,
            ),
            "stable_continuity_ordering_verified": exported_record_order == expected_record_order,
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "lineage_chain_compatibility_verified": lineage_compatibility["valid"],
            "sequencing_compatibility_verified": sequencing_compatibility["valid"],
            "routing_compatibility_verified": routing_compatibility["valid"],
            "drift_compatibility_verified": drift_compatibility["valid"],
            "diagnostics_explainability_compatibility_verified": diagnostics_compatibility["valid"],
            "stale_continuity_verified": visibility["stale_continuity_visible"],
            "missing_continuity_verified": visibility["missing_continuity_visible"],
            "conflicting_continuity_verified": visibility["conflicting_continuity_visible"],
            "prohibited_repair_verified": visibility["prohibited_repair_visible"],
            "unsupported_transition_verified": visibility["unsupported_transition_visible"],
            "cross_layer_summary_verified": cross_layer_summary["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "continuity_repair_disabled": non_execution["continuity_repair_disabled"],
            "continuity_inference_disabled": non_execution["continuity_inference_disabled"],
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
        "coordination_continuity_certification": exported,
        "explicit_limitations": list(certification.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(certification.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination continuity JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_continuity_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"continuity_status={report['continuity_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
