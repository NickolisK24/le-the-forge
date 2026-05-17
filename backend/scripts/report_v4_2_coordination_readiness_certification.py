"""Generate deterministic v4.2 coordination readiness certification evidence."""

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

from refresh_coordination.coordination_continuity_models import (  # noqa: E402
    default_coordination_continuity_certification,
)
from refresh_coordination.coordination_dependency_graph_models import default_coordination_dependency_graph  # noqa: E402
from refresh_coordination.coordination_diagnostics_models import (  # noqa: E402
    default_coordination_diagnostics_explainability,
)
from refresh_coordination.coordination_drift_models import default_coordination_drift_certification  # noqa: E402
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_readiness_certification import (  # noqa: E402
    build_coordination_readiness_certification_evidence,
    validate_descriptive_only_coordination_readiness_certification,
)
from refresh_coordination.coordination_readiness_diagnostics import (  # noqa: E402
    build_coordination_readiness_diagnostics,
    coordination_readiness_certifications_equal,
    count_coordination_readiness_states,
    validate_coordination_readiness_non_execution,
    validate_coordination_readiness_visibility,
    validate_descriptive_readiness_classification,
    validate_layer_readiness_compatibility,
    validate_phase_evidence_compatibility,
)
from refresh_coordination.coordination_readiness_hashing import (  # noqa: E402
    deterministic_coordination_readiness_hash,
    hash_coordination_readiness_certification,
    hash_coordination_readiness_diagnostic,
    hash_coordination_readiness_identity,
    hash_coordination_readiness_record,
    hash_descriptive_readiness_classification,
    hash_phase_evidence_reference,
    hash_readiness_state_visibility,
)
from refresh_coordination.coordination_readiness_models import (  # noqa: E402
    V4_2_COORDINATION_READINESS_GENERATED_AT,
    V4_2_COORDINATION_READINESS_PHASE_ID,
    V4_2_COORDINATION_READINESS_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_READINESS_STATUS_BLOCKED,
    V4_2_COORDINATION_READINESS_STATUS_STABLE,
    default_coordination_readiness_certification,
)
from refresh_coordination.coordination_readiness_serialization import (  # noqa: E402
    export_coordination_readiness_certification,
    serialize_coordination_readiness_certification,
)
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_models import default_governance_routing_visibility  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_readiness_certification_report.json")


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
    continuity = default_coordination_continuity_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
    )
    return manifest, graph, lineage, sequencing, routing, drift, diagnostics, continuity


def _readiness_from_sources():
    manifest, graph, lineage, sequencing, routing, drift, diagnostics, continuity = _sources()
    return default_coordination_readiness_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )


def _reordered_coordination_readiness_certification():
    certification = _readiness_from_sources()
    return replace(
        certification,
        phase_evidence_references=tuple(reversed(certification.phase_evidence_references)),
        manifest_readiness_references=tuple(reversed(certification.manifest_readiness_references)),
        dependency_graph_readiness_references=tuple(
            reversed(certification.dependency_graph_readiness_references)
        ),
        lineage_readiness_references=tuple(reversed(certification.lineage_readiness_references)),
        sequencing_readiness_references=tuple(reversed(certification.sequencing_readiness_references)),
        routing_readiness_references=tuple(reversed(certification.routing_readiness_references)),
        drift_readiness_references=tuple(reversed(certification.drift_readiness_references)),
        diagnostics_explainability_readiness_references=tuple(
            reversed(certification.diagnostics_explainability_readiness_references)
        ),
        continuity_readiness_references=tuple(reversed(certification.continuity_readiness_references)),
        readiness_records=tuple(reversed(certification.readiness_records)),
        diagnostics=tuple(reversed(certification.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_readiness_hash(payload)


def build_v4_2_coordination_readiness_certification_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest, graph, lineage, sequencing, routing, drift, diagnostics, continuity = _sources()
    readiness = default_coordination_readiness_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )
    repeated = default_coordination_readiness_certification(
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )
    reordered = _reordered_coordination_readiness_certification()
    exported = export_coordination_readiness_certification(readiness)
    visibility = validate_coordination_readiness_visibility(readiness)
    classification = validate_descriptive_readiness_classification(readiness)
    phase_compatibility = validate_phase_evidence_compatibility(
        readiness,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )
    layer_compatibility = validate_layer_readiness_compatibility(
        readiness,
        manifest,
        graph,
        lineage,
        sequencing,
        routing,
        drift,
        diagnostics,
        continuity,
    )
    non_execution = validate_coordination_readiness_non_execution(readiness)
    descriptive_validation = validate_descriptive_only_coordination_readiness_certification(readiness)
    readiness_diagnostics = build_coordination_readiness_diagnostics(readiness)
    readiness_evidence = build_coordination_readiness_certification_evidence(readiness)
    serialization_first = serialize_coordination_readiness_certification(readiness)
    serialization_second = serialize_coordination_readiness_certification(repeated)
    serialization_reordered = serialize_coordination_readiness_certification(reordered)
    readiness_hash = hash_coordination_readiness_certification(readiness)
    repeated_hash = hash_coordination_readiness_certification(repeated)
    reordered_hash = hash_coordination_readiness_certification(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if classification["valid"] else 1,
            0 if phase_compatibility["valid"] else 1,
            0 if layer_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if descriptive_validation["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if readiness_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_readiness_certifications_equal(readiness, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_READINESS_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_READINESS_STATUS_BLOCKED
    )
    exported_record_order = [item["readiness_record_id"] for item in exported["readiness_records"]]
    expected_record_order = [
        item["readiness_record_id"]
        for item in sorted(
            exported["readiness_records"],
            key=lambda item: (item["deterministic_order"], item["readiness_record_id"]),
        )
    ]
    report = {
        "schema_version": V4_2_COORDINATION_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_READINESS_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_READINESS_PHASE_ID,
        "phase_name": "v4.2_phase_9_coordination_readiness_certification",
        "repo_root": str(root),
        "architectural_purpose": "deterministic v4.2 refresh coordination readiness certification without approval authorization remediation or execution behavior",
        "readiness_mode": "descriptive_only_non_executable_non_authorizing_non_remediating",
        "readiness_status": status,
        "readiness_counts": {
            "phase_evidence_reference_count": len(readiness.phase_evidence_references),
            "manifest_readiness_reference_count": len(readiness.manifest_readiness_references),
            "dependency_graph_readiness_reference_count": len(
                readiness.dependency_graph_readiness_references
            ),
            "lineage_readiness_reference_count": len(readiness.lineage_readiness_references),
            "sequencing_readiness_reference_count": len(readiness.sequencing_readiness_references),
            "routing_readiness_reference_count": len(readiness.routing_readiness_references),
            "drift_readiness_reference_count": len(readiness.drift_readiness_references),
            "diagnostics_explainability_readiness_reference_count": len(
                readiness.diagnostics_explainability_readiness_references
            ),
            "continuity_readiness_reference_count": len(readiness.continuity_readiness_references),
            "readiness_record_count": len(readiness.readiness_records),
            "readiness_diagnostic_count": len(readiness.diagnostics),
            "readiness_state_counts": count_coordination_readiness_states(readiness.readiness_records),
        },
        "compatibility_visibility": {
            "phase_evidence": phase_compatibility,
            "layer_readiness": layer_compatibility,
        },
        "readiness_visibility": {
            "visibility_validation": visibility,
            "blocked_readiness_hash": hash_readiness_state_visibility(readiness.blocked_readiness_visibility),
            "prohibited_readiness_hash": hash_readiness_state_visibility(
                readiness.prohibited_readiness_visibility
            ),
            "unsupported_readiness_hash": hash_readiness_state_visibility(
                readiness.unsupported_readiness_visibility
            ),
            "stale_readiness_hash": hash_readiness_state_visibility(readiness.stale_readiness_visibility),
            "missing_readiness_hash": hash_readiness_state_visibility(readiness.missing_readiness_visibility),
            "conflicting_readiness_hash": hash_readiness_state_visibility(
                readiness.conflicting_readiness_visibility
            ),
        },
        "descriptive_readiness_classification": {
            "classification_validation": classification,
            "classification_hash": hash_descriptive_readiness_classification(
                readiness.descriptive_readiness_classification
            ),
        },
        "readiness_diagnostics": readiness_diagnostics,
        "readiness_certification_evidence": readiness_evidence,
        "hashing_stability_evidence": {
            "stable": readiness_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_readiness_certification",
            "readiness_hash": readiness_hash,
            "repeated_readiness_hash": repeated_hash,
            "reordered_readiness_hash": reordered_hash,
            "identity_hash": hash_coordination_readiness_identity(readiness.identity),
            "phase_evidence_hashes": [
                hash_phase_evidence_reference(reference)
                for reference in readiness.phase_evidence_references
            ],
            "readiness_record_hashes": [
                hash_coordination_readiness_record(record) for record in readiness.readiness_records
            ],
            "diagnostic_hashes": [
                hash_coordination_readiness_diagnostic(diagnostic) for diagnostic in readiness.diagnostics
            ],
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_readiness_certification",
            "payload_length": len(serialization_first),
            "readiness_order_preserved": exported_record_order == expected_record_order,
            "blocked_readiness_preserved": visibility["blocked_readiness_visible"],
            "prohibited_readiness_preserved": visibility["prohibited_readiness_visible"],
            "unsupported_readiness_preserved": visibility["unsupported_readiness_visible"],
            "stale_readiness_preserved": visibility["stale_readiness_visible"],
            "missing_readiness_preserved": visibility["missing_readiness_visible"],
            "conflicting_readiness_preserved": visibility["conflicting_readiness_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "readiness_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first
            == serialization_second
            == serialization_reordered,
            "deterministic_hashing_verified": readiness_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_readiness_certifications_equal(
                readiness,
                repeated,
            ),
            "stable_readiness_ordering_verified": exported_record_order == expected_record_order,
            "phase_evidence_compatibility_verified": phase_compatibility["valid"],
            "layer_readiness_compatibility_verified": layer_compatibility["valid"],
            "blocked_readiness_verified": visibility["blocked_readiness_visible"],
            "prohibited_readiness_verified": visibility["prohibited_readiness_visible"],
            "unsupported_readiness_verified": visibility["unsupported_readiness_visible"],
            "stale_readiness_verified": visibility["stale_readiness_visible"],
            "missing_readiness_verified": visibility["missing_readiness_visible"],
            "conflicting_readiness_verified": visibility["conflicting_readiness_visible"],
            "descriptive_readiness_classification_verified": classification["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
            "operational_authorization_disabled": non_execution["operational_authorization_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "automatic_correction_disabled": non_execution["automatic_correction_disabled"],
            "drift_correction_disabled": non_execution["drift_correction_disabled"],
            "continuity_repair_disabled": non_execution["continuity_repair_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_readiness_certification": exported,
        "explicit_limitations": list(readiness.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(readiness.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination readiness JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_readiness_certification_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"readiness_status={report['readiness_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
