"""Generate deterministic v4.2 coordination lineage chain governance evidence."""

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

from refresh_coordination.coordination_dependency_graph_models import (  # noqa: E402
    default_coordination_dependency_graph,
)
from refresh_coordination.coordination_lineage_chain_diagnostics import (  # noqa: E402
    build_coordination_lineage_chain_diagnostics,
    coordination_lineage_chains_equal,
    count_coordination_lineage_states,
    validate_coordination_dependency_graph_lineage_compatibility,
    validate_coordination_lineage_chain_continuity,
    validate_coordination_lineage_chain_non_execution,
    validate_coordination_lineage_chain_visibility,
    validate_coordination_manifest_lineage_compatibility,
)
from refresh_coordination.coordination_lineage_chain_hashing import (  # noqa: E402
    deterministic_coordination_lineage_chain_hash,
    hash_conflicting_lineage_visibility,
    hash_coordination_lineage_chain,
    hash_coordination_lineage_chain_identity,
    hash_coordination_lineage_chain_record,
    hash_dependency_graph_lineage_chain_reference,
    hash_lineage_predecessor_reference,
    hash_lineage_source_reference,
    hash_lineage_successor_reference,
    hash_manifest_lineage_chain_reference,
    hash_missing_lineage_visibility,
    hash_prohibited_lineage_mutation_visibility,
    hash_stale_lineage_visibility,
    hash_unsupported_lineage_transition_visibility,
)
from refresh_coordination.coordination_lineage_chain_models import (  # noqa: E402
    V4_2_COORDINATION_LINEAGE_CHAIN_GENERATED_AT,
    V4_2_COORDINATION_LINEAGE_CHAIN_PHASE_ID,
    V4_2_COORDINATION_LINEAGE_CHAIN_REPORT_SCHEMA_VERSION,
    V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_BLOCKED,
    V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_STABLE,
    default_coordination_lineage_chain,
)
from refresh_coordination.coordination_lineage_chain_serialization import (  # noqa: E402
    export_coordination_lineage_chain,
    serialize_coordination_lineage_chain,
)
from refresh_coordination.coordination_manifest_models import default_coordination_manifest  # noqa: E402


REPORT_PATH = Path("docs/generated/v4_2_coordination_lineage_chain_governance_report.json")


def _reordered_coordination_lineage_chain():
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    chain = default_coordination_lineage_chain(manifest, graph)
    return replace(
        chain,
        source_references=tuple(reversed(chain.source_references)),
        predecessor_references=tuple(reversed(chain.predecessor_references)),
        successor_references=tuple(reversed(chain.successor_references)),
        manifest_lineage_references=tuple(reversed(chain.manifest_lineage_references)),
        dependency_graph_lineage_references=tuple(reversed(chain.dependency_graph_lineage_references)),
        records=tuple(reversed(chain.records)),
        diagnostics=tuple(reversed(chain.diagnostics)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_coordination_lineage_chain_hash(payload)


def build_v4_2_coordination_lineage_chain_governance_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    manifest = default_coordination_manifest()
    graph = default_coordination_dependency_graph(manifest)
    chain = default_coordination_lineage_chain(manifest, graph)
    repeated = default_coordination_lineage_chain(manifest, graph)
    reordered = _reordered_coordination_lineage_chain()
    exported = export_coordination_lineage_chain(chain)
    visibility = validate_coordination_lineage_chain_visibility(chain)
    continuity = validate_coordination_lineage_chain_continuity(chain)
    manifest_compatibility = validate_coordination_manifest_lineage_compatibility(chain, manifest)
    graph_compatibility = validate_coordination_dependency_graph_lineage_compatibility(chain, graph, manifest)
    non_execution = validate_coordination_lineage_chain_non_execution(chain)
    diagnostics = build_coordination_lineage_chain_diagnostics(chain, manifest, graph)
    serialization_first = serialize_coordination_lineage_chain(chain)
    serialization_second = serialize_coordination_lineage_chain(repeated)
    serialization_reordered = serialize_coordination_lineage_chain(reordered)
    chain_hash = hash_coordination_lineage_chain(chain)
    repeated_hash = hash_coordination_lineage_chain(repeated)
    reordered_hash = hash_coordination_lineage_chain(reordered)
    validation_error_count = sum(
        [
            0 if visibility["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if manifest_compatibility["valid"] else 1,
            0 if graph_compatibility["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if chain_hash == repeated_hash == reordered_hash else 1,
            0 if coordination_lineage_chains_equal(chain, repeated) else 1,
        ]
    )
    status = (
        V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_COORDINATION_LINEAGE_CHAIN_STATUS_BLOCKED
    )
    exported_record_order = [item["record_id"] for item in exported["records"]]
    expected_record_order = [
        item["record_id"]
        for item in sorted(exported["records"], key=lambda item: (item["deterministic_order"], item["record_id"]))
    ]
    source_hashes = [hash_lineage_source_reference(reference) for reference in chain.source_references]
    predecessor_hashes = [
        hash_lineage_predecessor_reference(reference) for reference in chain.predecessor_references
    ]
    successor_hashes = [hash_lineage_successor_reference(reference) for reference in chain.successor_references]
    manifest_lineage_hashes = [
        hash_manifest_lineage_chain_reference(reference) for reference in chain.manifest_lineage_references
    ]
    dependency_graph_lineage_hashes = [
        hash_dependency_graph_lineage_chain_reference(reference)
        for reference in chain.dependency_graph_lineage_references
    ]
    record_hashes = [hash_coordination_lineage_chain_record(record) for record in chain.records]
    report = {
        "schema_version": V4_2_COORDINATION_LINEAGE_CHAIN_REPORT_SCHEMA_VERSION,
        "generated_at": V4_2_COORDINATION_LINEAGE_CHAIN_GENERATED_AT,
        "phase_id": V4_2_COORDINATION_LINEAGE_CHAIN_PHASE_ID,
        "phase_name": "v4.2_phase_3_coordination_lineage_chain_governance",
        "repo_root": str(root),
        "architectural_purpose": "deterministic refresh coordination lineage chain governance without execution behavior",
        "lineage_chain_mode": "descriptive_only_non_executable",
        "foundation_status": status,
        "lineage_counts": {
            "source_reference_count": len(chain.source_references),
            "predecessor_reference_count": len(chain.predecessor_references),
            "successor_reference_count": len(chain.successor_references),
            "manifest_lineage_reference_count": len(chain.manifest_lineage_references),
            "dependency_graph_lineage_reference_count": len(chain.dependency_graph_lineage_references),
            "record_count": len(chain.records),
            "diagnostic_count": len(chain.diagnostics),
            "lineage_state_counts": count_coordination_lineage_states(chain.records),
        },
        "lineage_source_visibility": {
            "source_reference_hashes": source_hashes,
            "source_reference_ids": tuple(reference.source_reference_id for reference in chain.source_references),
            "predecessor_reference_hashes": predecessor_hashes,
            "successor_reference_hashes": successor_hashes,
        },
        "manifest_lineage_visibility": {
            "manifest_lineage_hashes": manifest_lineage_hashes,
            "manifest_lineage_compatibility": manifest_compatibility,
        },
        "dependency_graph_lineage_visibility": {
            "dependency_graph_lineage_hashes": dependency_graph_lineage_hashes,
            "dependency_graph_lineage_compatibility": graph_compatibility,
        },
        "stale_lineage_visibility": {
            "stale_visibility_hash": hash_stale_lineage_visibility(chain.stale_lineage_visibility),
            "stale_record_ids": visibility["stale_record_ids"],
            "stale_lineage_visible": visibility["stale_lineage_visible"],
        },
        "missing_lineage_visibility": {
            "missing_visibility_hash": hash_missing_lineage_visibility(chain.missing_lineage_visibility),
            "missing_record_ids": visibility["missing_record_ids"],
            "missing_lineage_visible": visibility["missing_lineage_visible"],
        },
        "conflicting_lineage_visibility": {
            "conflicting_visibility_hash": hash_conflicting_lineage_visibility(chain.conflicting_lineage_visibility),
            "conflicting_record_ids": visibility["conflicting_record_ids"],
            "conflicting_lineage_visible": visibility["conflicting_lineage_visible"],
        },
        "prohibited_lineage_mutation_visibility": {
            "prohibited_mutation_visibility_hash": hash_prohibited_lineage_mutation_visibility(
                chain.prohibited_lineage_mutation_visibility
            ),
            "prohibited_record_ids": visibility["prohibited_record_ids"],
            "prohibited_lineage_mutation_visible": visibility["prohibited_lineage_mutation_visible"],
            "prohibited_capability_count": len(
                chain.prohibited_lineage_mutation_visibility.prohibited_capabilities
            ),
        },
        "unsupported_lineage_transition_visibility": {
            "unsupported_transition_visibility_hash": hash_unsupported_lineage_transition_visibility(
                chain.unsupported_lineage_transition_visibility
            ),
            "unsupported_record_ids": visibility["unsupported_record_ids"],
            "unsupported_transition_ids": chain.unsupported_lineage_transition_visibility.unsupported_transition_ids,
            "unsupported_lineage_transition_visible": visibility["unsupported_lineage_transition_visible"],
        },
        "lineage_continuity_visibility": {
            "lineage_continuity_validation": continuity,
            "replay_safe": continuity["replay_safe"],
            "rollback_safe": continuity["rollback_safe"],
            "provenance_safe": continuity["provenance_safe"],
            "lineage_safe": continuity["lineage_safe"],
        },
        "lineage_diagnostics": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "fail_visible_lineage_record_count": diagnostics["fail_visible_lineage_record_count"],
        },
        "hashing_stability_evidence": {
            "stable": chain_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_2_coordination_lineage_chain_governance",
            "chain_hash": chain_hash,
            "repeated_chain_hash": repeated_hash,
            "reordered_chain_hash": reordered_hash,
            "identity_hash": hash_coordination_lineage_chain_identity(chain.identity),
            "source_reference_hashes": source_hashes,
            "predecessor_reference_hashes": predecessor_hashes,
            "successor_reference_hashes": successor_hashes,
            "manifest_lineage_hashes": manifest_lineage_hashes,
            "dependency_graph_lineage_hashes": dependency_graph_lineage_hashes,
            "record_hashes": record_hashes,
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_2_coordination_lineage_chain_governance",
            "payload_length": len(serialization_first),
            "record_order_preserved": exported_record_order == expected_record_order,
            "stale_lineage_preserved": visibility["stale_lineage_visible"],
            "missing_lineage_preserved": visibility["missing_lineage_visible"],
            "conflicting_lineage_preserved": visibility["conflicting_lineage_visible"],
            "prohibited_lineage_mutation_preserved": visibility["prohibited_lineage_mutation_visible"],
            "unsupported_lineage_transition_preserved": visibility["unsupported_lineage_transition_visible"],
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "foundation_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": chain_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": coordination_lineage_chains_equal(chain, repeated),
            "stable_lineage_ordering_verified": exported_record_order == expected_record_order,
            "stale_lineage_visibility_verified": visibility["stale_lineage_visible"],
            "missing_lineage_visibility_verified": visibility["missing_lineage_visible"],
            "conflicting_lineage_visibility_verified": visibility["conflicting_lineage_visible"],
            "prohibited_lineage_mutation_visibility_verified": visibility[
                "prohibited_lineage_mutation_visible"
            ],
            "unsupported_lineage_transition_visibility_verified": visibility[
                "unsupported_lineage_transition_visible"
            ],
            "lineage_continuity_verified": continuity["valid"],
            "manifest_compatibility_verified": manifest_compatibility["valid"],
            "dependency_graph_compatibility_verified": graph_compatibility["valid"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "lineage_repair_disabled": non_execution["lineage_repair_disabled"],
            "lineage_inference_disabled": non_execution["lineage_inference_disabled"],
            "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "remediation_disabled": non_execution["remediation_disabled"],
            "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
        },
        "coordination_lineage_chain": exported,
        "explicit_limitations": list(chain.governance_visibility.explicit_limitations),
        "explicit_prohibitions": list(chain.governance_visibility.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Coordination lineage chain JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_2_coordination_lineage_chain_governance_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"foundation_status={report['foundation_status']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
