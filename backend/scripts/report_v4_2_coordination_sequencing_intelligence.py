"""Generate deterministic v4.2 coordination sequencing intelligence evidence."""

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
from refresh_coordination.coordination_lineage_chain_models import default_coordination_lineage_chain  # noqa: E402
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402
from refresh_coordination.coordination_sequencing_diagnostics import (  # noqa: E402
    build_coordination_sequencing_diagnostics,
    coordination_sequencing_intelligence_equal,
    count_coordination_sequence_states,
    validate_coordination_dependency_graph_sequence_compatibility,
    validate_coordination_lineage_chain_sequence_compatibility,
    validate_coordination_manifest_sequence_compatibility,
    validate_coordination_sequence_visibility,
    validate_coordination_sequencing_non_execution,
    validate_non_executable_sequence_ordering,
)
from refresh_coordination.coordination_sequencing_hashing import (  # noqa: E402
    deterministic_coordination_sequencing_hash,
    hash_coordination_sequence_record,
    hash_coordination_sequencing_identity,
    hash_coordination_sequencing_intelligence,
    hash_dependency_graph_sequence_reference,
    hash_lineage_sequence_reference,
    hash_manifest_sequence_reference,
    hash_non_executable_sequence_ordering_visibility,
    hash_sequence_state_visibility,
    hash_sequence_step_identity,
)
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    V4_2_COORDINATION_SEQUENCING_GENERATED_AT,
    V4_2_COORDINATION_SEQUENCING_PHASE_ID,
    V4_2_COORDINATION_SEQUENCING_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_SEQUENCING_STATUS_BLOCKED,
    V4_2_COORDINATION_SEQUENCING_STATUS_STABLE,
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.coordination_sequencing_serialization import (  # noqa: E402
    export_coordination_sequencing_intelligence,
    serialize_coordination_sequencing_intelligence,
)


REPORT_PATH = Path("docs/generated/v4_2_coordination_sequencing_intelligence_report.json")


def _reordered_coordination_sequencing_intelligence():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    return replace(
        sequencing,
        step_identities=tuple(reversed(sequencing.step_identities)),
        manifest_sequence_references=tuple(reversed(sequencing.manifest_sequence_references)),
        dependency_graph_sequence_references=tuple(reversed(sequencing.dependency_graph_sequence_references)),
        lineage_sequence_references=tuple(reversed(sequencing.lineage_sequence_references)),
        sequence_records=tuple(reversed(sequencing.sequence_records)),
        diagnostics=tuple(reversed(sequencing.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_sequencing_hash(payload)


def build_v4_2_coordination_sequencing_intelligence_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    repeated = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    reordered = _reordered_coordination_sequencing_intelligence()
    exported = export_coordination_sequencing_intelligence(sequencing)
    visibility = validate_coordination_sequence_visibility(sequencing)
    ordering = validate_non_executable_sequence_ordering(sequencing)
    manifest_compatibility = validate_coordination_manifest_sequence_compatibility(sequencing, manifest)
    graph_compatibility = validate_coordination_dependency_graph_sequence_compatibility(sequencing, graph, manifest)
    lineage_compatibility = validate_coordination_lineage_chain_sequence_compatibility(
        sequencing,
        lineage,
        graph,
        manifest,
    )
    non_execution = validate_coordination_sequencing_non_execution(sequencing)
    diagnostics = build_coordination_sequencing_diagnostics(sequencing, manifest, graph, lineage)
    serialization_first = serialize_coordination_sequencing_intelligence(sequencing)
    serialization_second = serialize_coordination_sequencing_intelligence(repeated)
    serialization_reordered = serialize_coordination_sequencing_intelligence(reordered)
    sequencing_hash = hash_coordination_sequencing_intelligence(sequencing)
    repeated_hash = hash_coordination_sequencing_intelligence(repeated)
    reordered_hash = hash_coordination_sequencing_intelligence(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if ordering["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if lineage_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if sequencing_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_sequencing_intelligence_equal(sequencing, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_SEQUENCING_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_SEQUENCING_STATUS_BLOCKED
    )
    exported_record_order = [item["sequence_record_id"] for item in exported["sequence_records"]]
    expected_record_order = [
        item["sequence_record_id"]
        for item in sorted(
            exported["sequence_records"],
            key=lambda item: (item["deterministic_order"], item["sequence_record_id"]),
        )
    ]
    step_hashes = [hash_sequence_step_identity(step) for step in sequencing.step_identities]
    record_hashes = [hash_coordination_sequence_record(record) for record in sequencing.sequence_records]
    report = {
        "schema_version": V4_2_COORDINATION_SEQUENCING_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_SEQUENCING_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_SEQUENCING_PHASE_ID,
        "phase_name": "v4.2_phase_4_coordination_sequencing_intelligence",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination sequencing intelligence without execution behavior",
        "sequencing_mode": "descriptive_only_non_executable_non_scheduling",
        "foundation_status": status,
        "sequence_counts": {
            "step_identity_count": len(sequencing.step_identities),
            "manifest_sequence_reference_count": len(sequencing.manifest_sequence_references),
            "dependency_graph_sequence_reference_count": len(sequencing.dependency_graph_sequence_references),
            "lineage_sequence_reference_count": len(sequencing.lineage_sequence_references),
            "sequence_record_count": len(sequencing.sequence_records),
            "diagnostic_count": len(sequencing.diagnostics),
            "sequence_state_counts": count_coordination_sequence_states(sequencing.sequence_records),
        },
        "ordering_visibility": {
            "ordering_visibility_hash": hash_non_executable_sequence_ordering_visibility(
                sequencing.ordering_visibility
            ),
            "ordering_validation": ordering,
        },
        "manifest_sequence_visibility": {
            "manifest_sequence_hashes": [
                hash_manifest_sequence_reference(reference)
                for reference in sequencing.manifest_sequence_references
            ],
            "manifest_sequence_compatibility": manifest_compatibility,
        },
        "dependency_graph_sequence_visibility": {
            "dependency_graph_sequence_hashes": [
                hash_dependency_graph_sequence_reference(reference)
                for reference in sequencing.dependency_graph_sequence_references
            ],
            "dependency_graph_sequence_compatibility": graph_compatibility,
        },
        "lineage_sequence_visibility": {
            "lineage_sequence_hashes": [
                hash_lineage_sequence_reference(reference) for reference in sequencing.lineage_sequence_references
            ],
            "lineage_chain_sequence_compatibility": lineage_compatibility,
        },
        "blocked_sequence_visibility": {
            "blocked_visibility_hash": hash_sequence_state_visibility(sequencing.blocked_sequence_visibility),
            "blocked_record_ids": visibility["blocked_record_ids"],
            "blocked_sequences_visible": visibility["blocked_sequences_visible"],
        },
        "prohibited_sequence_visibility": {
            "prohibited_visibility_hash": hash_sequence_state_visibility(sequencing.prohibited_sequence_visibility),
            "prohibited_record_ids": visibility["prohibited_record_ids"],
            "prohibited_sequences_visible": visibility["prohibited_sequences_visible"],
        },
        "unsupported_sequence_visibility": {
            "unsupported_visibility_hash": hash_sequence_state_visibility(sequencing.unsupported_sequence_visibility),
            "unsupported_record_ids": visibility["unsupported_record_ids"],
            "unsupported_sequences_visible": visibility["unsupported_sequences_visible"],
        },
        "stale_sequence_visibility": {
            "stale_visibility_hash": hash_sequence_state_visibility(sequencing.stale_sequence_visibility),
            "stale_record_ids": visibility["stale_record_ids"],
            "stale_sequences_visible": visibility["stale_sequences_visible"],
        },
        "missing_sequence_visibility": {
            "missing_visibility_hash": hash_sequence_state_visibility(sequencing.missing_sequence_visibility),
            "missing_record_ids": visibility["missing_record_ids"],
            "missing_sequences_visible": visibility["missing_sequences_visible"],
        },
        "conflicting_sequence_visibility": {
            "conflicting_visibility_hash": hash_sequence_state_visibility(sequencing.conflicting_sequence_visibility),
            "conflicting_record_ids": visibility["conflicting_record_ids"],
            "conflicting_sequences_visible": visibility["conflicting_sequences_visible"],
        },
        "sequence_diagnostics": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "fail_visible_sequence_record_count": diagnostics["fail_visible_sequence_record_count"],
        },
        "hashing_stability_evidence": {
            "stable": sequencing_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_sequencing_intelligence",
            "sequencing_hash": sequencing_hash,
            "repeated_sequencing_hash": repeated_hash,
            "reordered_sequencing_hash": reordered_hash,
            "identity_hash": hash_coordination_sequencing_identity(sequencing.identity),
            "step_hashes": step_hashes,
            "sequence_record_hashes": record_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_sequencing_intelligence",
            "payload_length": len(serialization_first),
            "sequence_order_preserved": exported_record_order == expected_record_order,
            "blocked_sequences_preserved": visibility["blocked_sequences_visible"],
            "prohibited_sequences_preserved": visibility["prohibited_sequences_visible"],
            "unsupported_sequences_preserved": visibility["unsupported_sequences_visible"],
            "stale_sequences_preserved": visibility["stale_sequences_visible"],
            "missing_sequences_preserved": visibility["missing_sequences_visible"],
            "conflicting_sequences_preserved": visibility["conflicting_sequences_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": sequencing_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_sequencing_intelligence_equal(sequencing, repeated),
            "stable_sequence_ordering_verified": exported_record_order == expected_record_order,
            "non_executable_ordering_verified": ordering["valid"],
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "lineage_chain_compatibility_verified": lineage_compatibility["valid"],
            "blocked_sequence_visibility_verified": visibility["blocked_sequences_visible"],
            "prohibited_sequence_visibility_verified": visibility["prohibited_sequences_visible"],
            "unsupported_sequence_visibility_verified": visibility["unsupported_sequences_visible"],
            "stale_sequence_visibility_verified": visibility["stale_sequences_visible"],
            "missing_sequence_visibility_verified": visibility["missing_sequences_visible"],
            "conflicting_sequence_visibility_verified": visibility["conflicting_sequences_visible"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "lineage_repair_disabled": non_execution["lineage_repair_disabled"],
            "lineage_inference_disabled": non_execution["lineage_inference_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_sequencing_intelligence": exported,
        "explicit_limitations": list(sequencing.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(sequencing.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination sequencing JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_sequencing_intelligence_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
