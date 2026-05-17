"""Generate deterministic v4.2 coordination drift certification evidence."""

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
from refresh_coordination.coordination_drift_diagnostics import (  # noqa: E402
    build_coordination_drift_diagnostics,
    coordination_drift_certifications_equal,
    count_coordination_drift_states,
    validate_coordination_drift_non_execution,
    validate_coordination_drift_visibility,
    validate_cross_layer_drift_visibility,
    validate_dependency_graph_drift_compatibility,
    validate_lineage_drift_compatibility,
    validate_manifest_drift_compatibility,
    validate_routing_drift_compatibility,
    validate_sequencing_drift_compatibility,
)
from refresh_coordination.coordination_drift_hashing import (  # noqa: E402
    deterministic_coordination_drift_hash,
    hash_coordination_drift_certification,
    hash_coordination_drift_identity,
    hash_coordination_drift_record,
    hash_cross_layer_drift_visibility,
    hash_dependency_graph_drift_reference,
    hash_drift_state_visibility,
    hash_lineage_drift_reference,
    hash_manifest_drift_reference,
    hash_routing_drift_reference,
    hash_sequencing_drift_reference,
)
from refresh_coordination.coordination_drift_models import (  # noqa: E402
    V4_2_COORDINATION_DRIFT_GENERATED_AT,
    V4_2_COORDINATION_DRIFT_PHASE_ID,
    V4_2_COORDINATION_DRIFT_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_DRIFT_STATUS_BLOCKED,
    V4_2_COORDINATION_DRIFT_STATUS_STABLE,
    default_coordination_drift_certification,
)
from refresh_coordination.coordination_drift_serialization import (  # noqa: E402
    export_coordination_drift_certification,
    serialize_coordination_drift_certification,
)
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_drift_certification_report.json")


def _sources():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    return manifest, graph, lineage, sequencing, routing


def _reordered_coordination_drift_certification():
    manifest, graph, lineage, sequencing, routing = _sources()
    certification = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    return replace(
        certification,
        manifest_drift_references=tuple(reversed(certification.manifest_drift_references)),
        dependency_graph_drift_references=tuple(reversed(certification.dependency_graph_drift_references)),
        lineage_drift_references=tuple(reversed(certification.lineage_drift_references)),
        sequencing_drift_references=tuple(reversed(certification.sequencing_drift_references)),
        routing_drift_references=tuple(reversed(certification.routing_drift_references)),
        drift_records=tuple(reversed(certification.drift_records)),
        diagnostics=tuple(reversed(certification.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_drift_hash(payload)


def build_v4_2_coordination_drift_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest, graph, lineage, sequencing, routing = _sources()
    certification = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    repeated = default_coordination_drift_certification(manifest, graph, lineage, sequencing, routing)
    reordered = _reordered_coordination_drift_certification()
    exported = export_coordination_drift_certification(certification)
    visibility = validate_coordination_drift_visibility(certification)
    cross_layer = validate_cross_layer_drift_visibility(certification)
    manifest_compatibility = validate_manifest_drift_compatibility(certification, manifest)
    graph_compatibility = validate_dependency_graph_drift_compatibility(certification, graph, manifest)
    lineage_compatibility = validate_lineage_drift_compatibility(certification, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_drift_compatibility(
        certification,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    routing_compatibility = validate_routing_drift_compatibility(
        certification,
        routing,
        sequencing,
        lineage,
        graph,
        manifest,
    )
    non_execution = validate_coordination_drift_non_execution(certification)
    diagnostics = build_coordination_drift_diagnostics(certification, manifest, graph, lineage, sequencing, routing)
    serialization_first = serialize_coordination_drift_certification(certification)
    serialization_second = serialize_coordination_drift_certification(repeated)
    serialization_reordered = serialize_coordination_drift_certification(reordered)
    drift_hash = hash_coordination_drift_certification(certification)
    repeated_hash = hash_coordination_drift_certification(repeated)
    reordered_hash = hash_coordination_drift_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if cross_layer["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if lineage_compatibility["valid"] else 1,
            0 if sequencing_compatibility["valid"] else 1,
            0 if routing_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if drift_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_drift_certifications_equal(certification, repeated) else 1,
        ]
    )
    status = V4_2_COORDINATION_DRIFT_STATUS_STABLE if validation_error_count == 0 else V4_2_COORDINATION_DRIFT_STATUS_BLOCKED
    exported_record_order = [item["drift_record_id"] for item in exported["drift_records"]]
    expected_record_order = [
        item["drift_record_id"]
        for item in sorted(exported["drift_records"], key=lambda item: (item["deterministic_order"], item["drift_record_id"]))
    ]
    record_hashes = [hash_coordination_drift_record(record) for record in certification.drift_records]
    report = {
        "schema_version": V4_2_COORDINATION_DRIFT_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_DRIFT_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_DRIFT_PHASE_ID,
        "phase_name": "v4.2_phase_6_coordination_drift_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination drift certification without correction or execution behavior",
        "certification_mode": "descriptive_only_non_executable_non_remediating",
        "certification_status": status,
        "drift_counts": {
            "manifest_drift_reference_count": len(certification.manifest_drift_references),
            "dependency_graph_drift_reference_count": len(certification.dependency_graph_drift_references),
            "lineage_drift_reference_count": len(certification.lineage_drift_references),
            "sequencing_drift_reference_count": len(certification.sequencing_drift_references),
            "routing_drift_reference_count": len(certification.routing_drift_references),
            "drift_record_count": len(certification.drift_records),
            "diagnostic_count": len(certification.diagnostics),
            "drift_state_counts": count_coordination_drift_states(certification.drift_records),
        },
        "manifest_drift_visibility": {
            "manifest_drift_hashes": [
                hash_manifest_drift_reference(reference) for reference in certification.manifest_drift_references
            ],
            "manifest_drift_compatibility": manifest_compatibility,
        },
        "dependency_graph_drift_visibility": {
            "dependency_graph_drift_hashes": [
                hash_dependency_graph_drift_reference(reference)
                for reference in certification.dependency_graph_drift_references
            ],
            "dependency_graph_drift_compatibility": graph_compatibility,
        },
        "lineage_drift_visibility": {
            "lineage_drift_hashes": [
                hash_lineage_drift_reference(reference) for reference in certification.lineage_drift_references
            ],
            "lineage_drift_compatibility": lineage_compatibility,
        },
        "sequencing_drift_visibility": {
            "sequencing_drift_hashes": [
                hash_sequencing_drift_reference(reference) for reference in certification.sequencing_drift_references
            ],
            "sequencing_drift_compatibility": sequencing_compatibility,
        },
        "routing_drift_visibility": {
            "routing_drift_hashes": [
                hash_routing_drift_reference(reference) for reference in certification.routing_drift_references
            ],
            "routing_drift_compatibility": routing_compatibility,
        },
        "stale_drift_visibility": {
            "stale_visibility_hash": hash_drift_state_visibility(certification.stale_drift_visibility),
            "stale_record_ids": visibility["stale_record_ids"],
            "stale_drift_visible": visibility["stale_drift_visible"],
        },
        "missing_drift_visibility": {
            "missing_visibility_hash": hash_drift_state_visibility(certification.missing_drift_visibility),
            "missing_record_ids": visibility["missing_record_ids"],
            "missing_drift_visible": visibility["missing_drift_visible"],
        },
        "conflicting_drift_visibility": {
            "conflicting_visibility_hash": hash_drift_state_visibility(certification.conflicting_drift_visibility),
            "conflicting_record_ids": visibility["conflicting_record_ids"],
            "conflicting_drift_visible": visibility["conflicting_drift_visible"],
        },
        "prohibited_correction_visibility": {
            "prohibited_correction_visibility_hash": hash_drift_state_visibility(
                certification.prohibited_correction_visibility
            ),
            "prohibited_correction_record_ids": visibility["prohibited_correction_record_ids"],
            "prohibited_correction_visible": visibility["prohibited_correction_visible"],
        },
        "unsupported_transition_visibility": {
            "unsupported_transition_visibility_hash": hash_drift_state_visibility(
                certification.unsupported_transition_visibility
            ),
            "unsupported_transition_record_ids": visibility["unsupported_transition_record_ids"],
            "unsupported_transition_visible": visibility["unsupported_transition_visible"],
        },
        "cross_layer_drift_visibility": {
            "cross_layer_visibility_hash": hash_cross_layer_drift_visibility(
                certification.cross_layer_drift_visibility
            ),
            "cross_layer_record_ids": cross_layer["cross_layer_record_ids"],
            "cross_layer_drift_visible": cross_layer["cross_layer_drift_visible"],
            "involved_layers_visible": cross_layer["involved_layers_visible"],
            "layer_pairs": cross_layer["layer_pairs"],
        },
        "drift_diagnostics": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "fail_visible_drift_record_count": diagnostics["fail_visible_drift_record_count"],
        },
        "hashing_stability_evidence": {
            "stable": drift_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_drift_certification",
            "drift_certification_hash": drift_hash,
            "repeated_drift_certification_hash": repeated_hash,
            "reordered_drift_certification_hash": reordered_hash,
            "identity_hash": hash_coordination_drift_identity(certification.identity),
            "drift_record_hashes": record_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_drift_certification",
            "payload_length": len(serialization_first),
            "drift_order_preserved": exported_record_order == expected_record_order,
            "stale_drift_preserved": visibility["stale_drift_visible"],
            "missing_drift_preserved": visibility["missing_drift_visible"],
            "conflicting_drift_preserved": visibility["conflicting_drift_visible"],
            "prohibited_correction_preserved": visibility["prohibited_correction_visible"],
            "unsupported_transition_preserved": visibility["unsupported_transition_visible"],
            "cross_layer_drift_preserved": cross_layer["cross_layer_drift_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "certification_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": drift_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_drift_certifications_equal(certification, repeated),
            "stable_drift_ordering_verified": exported_record_order == expected_record_order,
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "lineage_chain_compatibility_verified": lineage_compatibility["valid"],
            "sequencing_compatibility_verified": sequencing_compatibility["valid"],
            "routing_compatibility_verified": routing_compatibility["valid"],
            "stale_drift_visibility_verified": visibility["stale_drift_visible"],
            "missing_drift_visibility_verified": visibility["missing_drift_visible"],
            "conflicting_drift_visibility_verified": visibility["conflicting_drift_visible"],
            "prohibited_correction_visibility_verified": visibility["prohibited_correction_visible"],
            "unsupported_transition_visibility_verified": visibility["unsupported_transition_visible"],
            "cross_layer_drift_visibility_verified": cross_layer["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "drift_correction_disabled": non_execution["drift_correction_disabled"],
            "drift_remediation_disabled": non_execution["drift_remediation_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_drift_certification": exported,
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
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination drift JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_drift_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"certification_status={report['certification_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
