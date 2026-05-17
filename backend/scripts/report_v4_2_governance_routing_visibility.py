"""Generate deterministic v4.2 governance routing visibility evidence."""

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
from refresh_coordination.coordination_sequencing_models import (  # noqa: E402
    default_coordination_sequencing_intelligence,
)
from refresh_coordination.governance_routing_diagnostics import (  # noqa: E402
    build_governance_routing_diagnostics,
    count_governance_route_states,
    governance_routing_visibility_equal,
    validate_dependency_graph_routing_compatibility,
    validate_governance_route_visibility,
    validate_governance_routing_non_execution,
    validate_lineage_routing_compatibility,
    validate_manifest_routing_compatibility,
    validate_non_executable_route_ordering,
    validate_sequencing_routing_compatibility,
)
from refresh_coordination.governance_routing_hashing import (  # noqa: E402
    deterministic_governance_routing_hash,
    hash_dependency_graph_routing_reference,
    hash_governance_route_record,
    hash_governance_routing_identity,
    hash_governance_routing_visibility,
    hash_lineage_routing_reference,
    hash_manifest_routing_reference,
    hash_non_executable_route_ordering_visibility,
    hash_route_state_visibility,
    hash_routing_source_reference,
    hash_routing_target_reference,
    hash_sequencing_routing_reference,
)
from refresh_coordination.governance_routing_models import (  # noqa: E402
    V4_2_GOVERNANCE_ROUTING_GENERATED_AT,
    V4_2_GOVERNANCE_ROUTING_PHASE_ID,
    V4_2_GOVERNANCE_ROUTING_REPORT_SCHEMA_VERSION,
    V4_2_GOVERNANCE_ROUTING_STATUS_BLOCKED,
    V4_2_GOVERNANCE_ROUTING_STATUS_STABLE,
    default_governance_routing_visibility,
)
from refresh_coordination.governance_routing_serialization import (  # noqa: E402
    export_governance_routing_visibility,
    serialize_governance_routing_visibility,
)


REPORT_PATH = Path("docs/generated/v4_2_governance_routing_visibility_report.json")


def _reordered_governance_routing_visibility():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    return replace(
        routing,
        source_references=tuple(reversed(routing.source_references)),
        target_references=tuple(reversed(routing.target_references)),
        manifest_routing_references=tuple(reversed(routing.manifest_routing_references)),
        dependency_graph_routing_references=tuple(reversed(routing.dependency_graph_routing_references)),
        lineage_routing_references=tuple(reversed(routing.lineage_routing_references)),
        sequencing_routing_references=tuple(reversed(routing.sequencing_routing_references)),
        route_records=tuple(reversed(routing.route_records)),
        diagnostics=tuple(reversed(routing.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_governance_routing_hash(payload)


def build_v4_2_governance_routing_visibility_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    lineage = default_coordination_lineage_chain(manifest, graph)
    sequencing = default_coordination_sequencing_intelligence(manifest, graph, lineage)
    routing = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    repeated = default_governance_routing_visibility(manifest, graph, lineage, sequencing)
    reordered = _reordered_governance_routing_visibility()
    exported = export_governance_routing_visibility(routing)
    visibility = validate_governance_route_visibility(routing)
    ordering = validate_non_executable_route_ordering(routing)
    manifest_compatibility = validate_manifest_routing_compatibility(routing, manifest)
    graph_compatibility = validate_dependency_graph_routing_compatibility(routing, graph, manifest)
    lineage_compatibility = validate_lineage_routing_compatibility(routing, lineage, graph, manifest)
    sequencing_compatibility = validate_sequencing_routing_compatibility(routing, sequencing, lineage, graph, manifest)
    non_execution = validate_governance_routing_non_execution(routing)
    diagnostics = build_governance_routing_diagnostics(routing, manifest, graph, lineage, sequencing)
    serialization_first = serialize_governance_routing_visibility(routing)
    serialization_second = serialize_governance_routing_visibility(repeated)
    serialization_reordered = serialize_governance_routing_visibility(reordered)
    routing_hash = hash_governance_routing_visibility(routing)
    repeated_hash = hash_governance_routing_visibility(repeated)
    reordered_hash = hash_governance_routing_visibility(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if ordering["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if lineage_compatibility["valid"] else 1,
            0 if sequencing_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if routing_hash == repeated_hash == reordered_hash else 1,
            0 if governance_routing_visibility_equal(routing, repeated) else 1,
        ]
    )
    status = V4_2_GOVERNANCE_ROUTING_STATUS_STABLE if validation_error_count == 0 else V4_2_GOVERNANCE_ROUTING_STATUS_BLOCKED
    exported_record_order = [item["route_record_id"] for item in exported["route_records"]]
    expected_record_order = [
        item["route_record_id"]
        for item in sorted(exported["route_records"], key=lambda item: (item["deterministic_order"], item["route_record_id"]))
    ]
    source_hashes = [hash_routing_source_reference(reference) for reference in routing.source_references]
    target_hashes = [hash_routing_target_reference(reference) for reference in routing.target_references]
    record_hashes = [hash_governance_route_record(record) for record in routing.route_records]
    report = {
        "schema_version": V4_2_GOVERNANCE_ROUTING_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_GOVERNANCE_ROUTING_GENERATED_AT,
        "phase_id": V4_2_GOVERNANCE_ROUTING_PHASE_ID,
        "phase_name": "v4.2_phase_5_governance_routing_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination governance routing visibility without execution behavior",
        "routing_mode": "descriptive_only_non_executable_non_routing",
        "foundation_status": status,
        "route_counts": {
            "source_reference_count": len(routing.source_references),
            "target_reference_count": len(routing.target_references),
            "manifest_routing_reference_count": len(routing.manifest_routing_references),
            "dependency_graph_routing_reference_count": len(routing.dependency_graph_routing_references),
            "lineage_routing_reference_count": len(routing.lineage_routing_references),
            "sequencing_routing_reference_count": len(routing.sequencing_routing_references),
            "route_record_count": len(routing.route_records),
            "diagnostic_count": len(routing.diagnostics),
            "route_state_counts": count_governance_route_states(routing.route_records),
        },
        "ordering_visibility": {
            "ordering_visibility_hash": hash_non_executable_route_ordering_visibility(routing.ordering_visibility),
            "ordering_validation": ordering,
        },
        "source_target_visibility": {
            "source_reference_hashes": source_hashes,
            "target_reference_hashes": target_hashes,
        },
        "manifest_routing_visibility": {
            "manifest_routing_hashes": [
                hash_manifest_routing_reference(reference) for reference in routing.manifest_routing_references
            ],
            "manifest_routing_compatibility": manifest_compatibility,
        },
        "dependency_graph_routing_visibility": {
            "dependency_graph_routing_hashes": [
                hash_dependency_graph_routing_reference(reference)
                for reference in routing.dependency_graph_routing_references
            ],
            "dependency_graph_routing_compatibility": graph_compatibility,
        },
        "lineage_routing_visibility": {
            "lineage_routing_hashes": [
                hash_lineage_routing_reference(reference) for reference in routing.lineage_routing_references
            ],
            "lineage_routing_compatibility": lineage_compatibility,
        },
        "sequencing_routing_visibility": {
            "sequencing_routing_hashes": [
                hash_sequencing_routing_reference(reference) for reference in routing.sequencing_routing_references
            ],
            "sequencing_routing_compatibility": sequencing_compatibility,
        },
        "blocked_route_visibility": {
            "blocked_visibility_hash": hash_route_state_visibility(routing.blocked_route_visibility),
            "blocked_record_ids": visibility["blocked_record_ids"],
            "blocked_routes_visible": visibility["blocked_routes_visible"],
        },
        "prohibited_route_visibility": {
            "prohibited_visibility_hash": hash_route_state_visibility(routing.prohibited_route_visibility),
            "prohibited_record_ids": visibility["prohibited_record_ids"],
            "prohibited_routes_visible": visibility["prohibited_routes_visible"],
        },
        "unsupported_route_visibility": {
            "unsupported_visibility_hash": hash_route_state_visibility(routing.unsupported_route_visibility),
            "unsupported_record_ids": visibility["unsupported_record_ids"],
            "unsupported_routes_visible": visibility["unsupported_routes_visible"],
        },
        "stale_route_visibility": {
            "stale_visibility_hash": hash_route_state_visibility(routing.stale_route_visibility),
            "stale_record_ids": visibility["stale_record_ids"],
            "stale_routes_visible": visibility["stale_routes_visible"],
        },
        "missing_route_visibility": {
            "missing_visibility_hash": hash_route_state_visibility(routing.missing_route_visibility),
            "missing_record_ids": visibility["missing_record_ids"],
            "missing_routes_visible": visibility["missing_routes_visible"],
        },
        "conflicting_route_visibility": {
            "conflicting_visibility_hash": hash_route_state_visibility(routing.conflicting_route_visibility),
            "conflicting_record_ids": visibility["conflicting_record_ids"],
            "conflicting_routes_visible": visibility["conflicting_routes_visible"],
        },
        "route_diagnostics": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "fail_visible_route_record_count": diagnostics["fail_visible_route_record_count"],
        },
        "hashing_stability_evidence": {
            "stable": routing_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_governance_routing_visibility",
            "routing_hash": routing_hash,
            "repeated_routing_hash": repeated_hash,
            "reordered_routing_hash": reordered_hash,
            "identity_hash": hash_governance_routing_identity(routing.identity),
            "source_reference_hashes": source_hashes,
            "target_reference_hashes": target_hashes,
            "route_record_hashes": record_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_governance_routing_visibility",
            "payload_length": len(serialization_first),
            "route_order_preserved": exported_record_order == expected_record_order,
            "blocked_routes_preserved": visibility["blocked_routes_visible"],
            "prohibited_routes_preserved": visibility["prohibited_routes_visible"],
            "unsupported_routes_preserved": visibility["unsupported_routes_visible"],
            "stale_routes_preserved": visibility["stale_routes_visible"],
            "missing_routes_preserved": visibility["missing_routes_visible"],
            "conflicting_routes_preserved": visibility["conflicting_routes_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": routing_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": governance_routing_visibility_equal(routing, repeated),
            "stable_route_ordering_verified": exported_record_order == expected_record_order,
            "non_executable_ordering_verified": ordering["valid"],
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "lineage_chain_compatibility_verified": lineage_compatibility["valid"],
            "sequencing_compatibility_verified": sequencing_compatibility["valid"],
            "blocked_route_visibility_verified": visibility["blocked_routes_visible"],
            "prohibited_route_visibility_verified": visibility["prohibited_routes_visible"],
            "unsupported_route_visibility_verified": visibility["unsupported_routes_visible"],
            "stale_route_visibility_verified": visibility["stale_routes_visible"],
            "missing_route_visibility_verified": visibility["missing_routes_visible"],
            "conflicting_route_visibility_verified": visibility["conflicting_routes_visible"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "lineage_repair_disabled": non_execution["lineage_repair_disabled"],
            "lineage_inference_disabled": non_execution["lineage_inference_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "governance_routing_visibility": exported,
        "explicit_limitations": list(routing.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(routing.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Governance routing JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_governance_routing_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
