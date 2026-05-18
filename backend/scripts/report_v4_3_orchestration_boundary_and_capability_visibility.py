"""Generate deterministic v4.3 orchestration boundary and capability visibility evidence."""

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

from orchestration_governance.orchestration_capability_diagnostics import (  # noqa: E402
    build_capability_visibility_diagnostics,
    capability_visibilities_equal,
    capability_visibility_identity_key,
    count_capability_states,
    validate_capability_continuity,
    validate_capability_explainability,
    validate_capability_identity,
    validate_capability_metadata,
    validate_capability_non_execution,
    validate_capability_relationships,
    validate_capability_support_visibility,
)
from orchestration_governance.orchestration_capability_hashing import (  # noqa: E402
    deterministic_capability_hash,
    hash_capability_boundary,
    hash_capability_diagnostic,
    hash_capability_explainability,
    hash_capability_record,
    hash_capability_relationship,
    hash_capability_visibility_identity,
    hash_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_models import (  # noqa: E402
    EXPLICIT_ORCHESTRATION_CAPABILITY_LIMITATIONS,
    EXPLICIT_ORCHESTRATION_CAPABILITY_PROHIBITIONS,
    V4_3_ORCHESTRATION_CAPABILITY_GENERATED_AT,
    V4_3_ORCHESTRATION_CAPABILITY_PHASE_ID,
    V4_3_ORCHESTRATION_CAPABILITY_REPORT_SCHEMA_VERSION,
    V4_3_ORCHESTRATION_CAPABILITY_STATUS_BLOCKED,
    V4_3_ORCHESTRATION_CAPABILITY_STATUS_STABLE,
    default_orchestration_capability_visibility,
)
from orchestration_governance.orchestration_capability_serialization import (  # noqa: E402
    export_orchestration_capability_visibility,
    serialize_orchestration_capability_visibility,
)


REPORT_PATH = Path("docs/generated/v4_3_orchestration_boundary_and_capability_visibility_report.json")


def _reordered_capability_visibility():
    visibility = default_orchestration_capability_visibility()
    return replace(
        visibility,
        capabilities=tuple(reversed(visibility.capabilities)),
        boundaries=tuple(reversed(visibility.boundaries)),
        relationships=tuple(reversed(visibility.relationships)),
        continuity_metadata=tuple(reversed(visibility.continuity_metadata)),
        diagnostics=tuple(reversed(visibility.diagnostics)),
        explainability_summaries=tuple(reversed(visibility.explainability_summaries)),
    )


def _hash_report(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_capability_hash(payload)


def build_v4_3_orchestration_boundary_and_capability_visibility_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    visibility = default_orchestration_capability_visibility()
    repeated = default_orchestration_capability_visibility()
    reordered = _reordered_capability_visibility()
    exported = export_orchestration_capability_visibility(visibility)
    identity = validate_capability_identity(visibility)
    support = validate_capability_support_visibility(visibility)
    metadata = validate_capability_metadata(visibility)
    relationships = validate_capability_relationships(visibility)
    continuity = validate_capability_continuity(visibility)
    explainability = validate_capability_explainability(visibility)
    non_execution = validate_capability_non_execution(visibility)
    diagnostics = build_capability_visibility_diagnostics(visibility)
    serialization_first = serialize_orchestration_capability_visibility(visibility)
    serialization_second = serialize_orchestration_capability_visibility(repeated)
    serialization_reordered = serialize_orchestration_capability_visibility(reordered)
    visibility_hash = hash_orchestration_capability_visibility(visibility)
    repeated_hash = hash_orchestration_capability_visibility(repeated)
    reordered_hash = hash_orchestration_capability_visibility(reordered)
    capability_hashes = [hash_capability_record(capability) for capability in visibility.capabilities]
    boundary_hashes = [hash_capability_boundary(boundary) for boundary in visibility.boundaries]
    relationship_hashes = [
        hash_capability_relationship(relationship) for relationship in visibility.relationships
    ]
    diagnostic_hashes = [hash_capability_diagnostic(diagnostic) for diagnostic in visibility.diagnostics]
    explainability_hashes = [
        hash_capability_explainability(summary) for summary in visibility.explainability_summaries
    ]
    exported_capability_order = [item["capability_id"] for item in exported["capabilities"]]
    expected_capability_order = [
        item["capability_id"]
        for item in sorted(
            exported["capabilities"],
            key=lambda item: (item["deterministic_order"], item["capability_id"]),
        )
    ]
    exported_boundary_order = [item["boundary_id"] for item in exported["boundaries"]]
    expected_boundary_order = [
        item["boundary_id"]
        for item in sorted(exported["boundaries"], key=lambda item: (item["deterministic_order"], item["boundary_id"]))
    ]
    exported_relationship_order = [item["relationship_id"] for item in exported["relationships"]]
    expected_relationship_order = [
        item["relationship_id"]
        for item in sorted(
            exported["relationships"],
            key=lambda item: (item["deterministic_order"], item["relationship_id"]),
        )
    ]
    validation_error_count = sum(
        [
            0 if identity["valid"] else 1,
            0 if support["valid"] else 1,
            0 if metadata["valid"] else 1,
            0 if relationships["valid"] else 1,
            0 if continuity["valid"] else 1,
            0 if explainability["valid"] else 1,
            0 if non_execution["valid"] else 1,
            0 if serialization_first == serialization_second == serialization_reordered else 1,
            0 if visibility_hash == repeated_hash == reordered_hash else 1,
            0 if capability_visibilities_equal(visibility, repeated) else 1,
            0 if exported_capability_order == expected_capability_order else 1,
            0 if exported_boundary_order == expected_boundary_order else 1,
            0 if exported_relationship_order == expected_relationship_order else 1,
        ]
    )
    status = (
        V4_3_ORCHESTRATION_CAPABILITY_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_ORCHESTRATION_CAPABILITY_STATUS_BLOCKED
    )
    report = {
        "schema_version": V4_3_ORCHESTRATION_CAPABILITY_REPORT_SCHEMA_VERSION,
        "generated_at": V4_3_ORCHESTRATION_CAPABILITY_GENERATED_AT,
        "phase_id": V4_3_ORCHESTRATION_CAPABILITY_PHASE_ID,
        "phase_name": "v4.3_phase_3_orchestration_boundary_and_capability_visibility",
        "repo_root": str(root),
        "architectural_purpose": "deterministic orchestration boundary and capability visibility without activation",
        "capability_mode": "descriptive_only_non_executable_capability_governance",
        "capability_visibility_status": status,
        "capability_counts": {
            "capability_count": len(visibility.capabilities),
            "prohibited_capability_count": len(diagnostics["prohibited_capability_ids"]),
            "unsupported_capability_count": len(diagnostics["unsupported_capability_ids"]),
            "blocked_capability_count": len(diagnostics["blocked_capability_ids"]),
            "stale_capability_count": len(diagnostics["stale_capability_ids"]),
            "conflicting_capability_count": len(diagnostics["conflicting_capability_ids"]),
            "governance_boundary_count": len(visibility.boundaries),
            "relationship_count": len(visibility.relationships),
            "invalid_relationship_count": diagnostics["invalid_relationship_count"],
            "diagnostic_count": len(visibility.diagnostics),
            "explainability_summary_count": len(visibility.explainability_summaries),
            "capability_state_counts": count_capability_states(visibility.capabilities),
        },
        "identity_visibility": {
            "identity_key": capability_visibility_identity_key(visibility),
            "identity_validation": identity,
            "identity_hash": hash_capability_visibility_identity(visibility.identity),
        },
        "support_state_visibility": {
            "support_visibility_validation": support,
            "prohibited_capability_ids": diagnostics["prohibited_capability_ids"],
            "unsupported_capability_ids": diagnostics["unsupported_capability_ids"],
            "blocked_capability_ids": diagnostics["blocked_capability_ids"],
            "stale_capability_ids": diagnostics["stale_capability_ids"],
            "conflicting_capability_ids": diagnostics["conflicting_capability_ids"],
            "unknown_capability_ids": diagnostics["unknown_capability_ids"],
            "prohibited_capabilities_visible": support["prohibited_capabilities_visible"],
            "unsupported_capabilities_visible": support["unsupported_capabilities_visible"],
            "blocked_capabilities_visible": support["blocked_capabilities_visible"],
            "stale_capabilities_visible": support["stale_capabilities_visible"],
            "conflicting_capabilities_visible": support["conflicting_capabilities_visible"],
            "enabled_operational_capability_count": diagnostics["enabled_operational_capability_count"],
        },
        "governance_boundary_visibility": {
            "boundary_hashes": boundary_hashes,
            "boundary_count": len(visibility.boundaries),
            "metadata_validation": metadata,
            "governance_boundary_metadata_present": metadata["governance_boundary_metadata_present"],
            "operational_boundary_metadata_present": metadata["operational_boundary_metadata_present"],
            "continuity_metadata_present": metadata["continuity_metadata_present"],
            "provenance_metadata_present": metadata["provenance_metadata_present"],
            "lineage_metadata_present": metadata["lineage_metadata_present"],
            "diagnostics_metadata_present": metadata["diagnostics_metadata_present"],
            "explainability_metadata_present": metadata["explainability_metadata_present"],
        },
        "relationship_visibility": {
            "relationship_validation": relationships,
            "relationship_hashes": relationship_hashes,
            "invalid_relationship_count": relationships["invalid_relationship_count"],
            "invalid_boundary_relationship_ids": relationships["invalid_boundary_relationship_ids"],
            "invalid_policy_relationship_ids": relationships["invalid_policy_relationship_ids"],
            "operational_relationship_ids": relationships["operational_relationship_ids"],
        },
        "continuity_visibility": {
            "continuity_validation": continuity,
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "provenance_continuity_preserved": continuity["provenance_continuity_preserved"],
            "lineage_continuity_preserved": continuity["lineage_continuity_preserved"],
            "capability_continuity_visible": continuity["capability_continuity_visible"],
        },
        "diagnostic_aggregation": {
            "diagnostic_categories": diagnostics["diagnostic_categories"],
            "diagnostic_hashes": diagnostic_hashes,
            "diagnostic_count": diagnostics["diagnostic_count"],
            "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
            "fail_visible_warning_count": diagnostics["fail_visible_warning_count"],
            "diagnostics_are_descriptive_only": diagnostics["diagnostics_are_descriptive_only"],
            "correction_absent": diagnostics["correction_absent"],
            "inference_absent": diagnostics["inference_absent"],
            "authorization_absent": diagnostics["authorization_absent"],
            "operational_mutation_absent": diagnostics["operational_mutation_absent"],
            "execution_absent": diagnostics["execution_absent"],
            "selection_systems_absent": diagnostics["selection_systems_absent"],
        },
        "explainability_findings": {
            "explainability_validation": explainability,
            "explainability_hashes": explainability_hashes,
            "prohibited_capability_visible": "prohibited_capability" in explainability["explainability_categories"],
            "unsupported_capability_visible": "unsupported_capability" in explainability["explainability_categories"],
            "blocked_capability_visible": "blocked_capability" in explainability["explainability_categories"],
            "stale_capability_visible": "stale_capability" in explainability["explainability_categories"],
            "conflicting_capability_visible": "conflicting_capability" in explainability["explainability_categories"],
            "activation_unavailable_visible": "activation_unavailable" in explainability["explainability_categories"],
            "execution_unavailable_visible": "execution_unavailable" in explainability["explainability_categories"],
            "planner_integration_unavailable_visible": (
                "planner_integration_unavailable" in explainability["explainability_categories"]
            ),
            "operational_orchestration_prohibited_visible": (
                "operational_orchestration_prohibited" in explainability["explainability_categories"]
            ),
            "governance_boundary_visible": "governance_boundary" in explainability["explainability_categories"],
        },
        "serialization_stability_evidence": {
            "stable": serialization_first == serialization_second == serialization_reordered,
            "serializer": "json_sort_keys_stable_v4_3_orchestration_capability_visibility",
            "payload_length": len(serialization_first),
            "capability_ordering_stable": exported_capability_order == expected_capability_order,
            "boundary_ordering_stable": exported_boundary_order == expected_boundary_order,
            "relationship_ordering_stable": exported_relationship_order == expected_relationship_order,
            "diagnostics_ordering_stable": [item["diagnostic_id"] for item in exported["diagnostics"]]
            == [
                item["diagnostic_id"]
                for item in sorted(
                    exported["diagnostics"],
                    key=lambda item: (item["deterministic_order"], item["diagnostic_id"]),
                )
            ],
            "explainability_ordering_stable": [
                item["explanation_id"] for item in exported["explainability_summaries"]
            ]
            == [
                item["explanation_id"]
                for item in sorted(
                    exported["explainability_summaries"],
                    key=lambda item: (item["deterministic_order"], item["explanation_id"]),
                )
            ],
            "prohibited_states_preserved": len(diagnostics["prohibited_capability_ids"]) > 0,
            "unsupported_states_preserved": len(diagnostics["unsupported_capability_ids"]) > 0,
            "blocked_states_preserved": len(diagnostics["blocked_capability_ids"]) > 0,
            "stale_states_preserved": len(diagnostics["stale_capability_ids"]) > 0,
            "conflicting_states_preserved": len(diagnostics["conflicting_capability_ids"]) > 0,
        },
        "hashing_stability_evidence": {
            "stable": visibility_hash == repeated_hash == reordered_hash,
            "hash_algorithm": "sha256_stable_json_v4_3_orchestration_capability_visibility",
            "capability_visibility_hash": visibility_hash,
            "repeated_capability_visibility_hash": repeated_hash,
            "reordered_capability_visibility_hash": reordered_hash,
            "identity_hash": hash_capability_visibility_identity(visibility.identity),
            "capability_hashes": capability_hashes,
            "boundary_hashes": boundary_hashes,
            "relationship_hashes": relationship_hashes,
            "diagnostic_hashes": diagnostic_hashes,
            "explainability_hashes": explainability_hashes,
        },
        "non_execution_guarantees": non_execution,
        "summary": {
            "capability_visibility_status": status,
            "validation_error_count": validation_error_count,
            "deterministic_serialization_verified": serialization_first == serialization_second == serialization_reordered,
            "deterministic_hashing_verified": visibility_hash == repeated_hash == reordered_hash,
            "deterministic_equality_verified": capability_visibilities_equal(visibility, repeated),
            "capability_ordering_verified": exported_capability_order == expected_capability_order,
            "boundary_ordering_verified": exported_boundary_order == expected_boundary_order,
            "relationship_ordering_verified": exported_relationship_order == expected_relationship_order,
            "identity_visibility_verified": identity["valid"],
            "support_state_visibility_verified": support["valid"],
            "metadata_visibility_verified": metadata["valid"],
            "relationship_visibility_verified": relationships["valid"],
            "continuity_visibility_verified": continuity["valid"],
            "explainability_visibility_verified": explainability["valid"],
            "replay_safe_status": continuity["replay_safe"],
            "rollback_safe_status": continuity["rollback_safe"],
            "non_execution_enforcement_validated": non_execution["valid"],
            "enabled_operational_capability_count": non_execution["enabled_operational_capability_count"],
            "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
            "orchestration_activation_disabled": non_execution["orchestration_activation_disabled"],
            "runtime_execution_disabled": non_execution["runtime_execution_disabled"],
            "capability_execution_disabled": non_execution["capability_execution_disabled"],
            "routing_execution_disabled": non_execution["routing_execution_disabled"],
            "traversal_execution_disabled": non_execution["traversal_execution_disabled"],
            "dependency_execution_disabled": non_execution["dependency_execution_disabled"],
            "sequencing_execution_disabled": non_execution["sequencing_execution_disabled"],
            "scheduling_execution_disabled": non_execution["scheduling_execution_disabled"],
            "planner_integration_disabled": non_execution["planner_integration_disabled"],
            "production_consumption_disabled": non_execution["production_consumption_disabled"],
            "orchestration_dispatch_disabled": non_execution["orchestration_dispatch_disabled"],
            "runtime_coordination_disabled": non_execution["runtime_coordination_disabled"],
            "operational_orchestration_engine_absent": non_execution["operational_orchestration_engine_absent"],
            "orchestration_decision_engine_absent": non_execution["orchestration_decision_engine_absent"],
        },
        "capability_visibility": exported,
        "explicit_limitations": list(EXPLICIT_ORCHESTRATION_CAPABILITY_LIMITATIONS),
        "explicit_prohibitions": list(EXPLICIT_ORCHESTRATION_CAPABILITY_PROHIBITIONS),
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(REPORT_PATH), help="Capability visibility JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    report = build_v4_3_orchestration_boundary_and_capability_visibility_report()
    write_report(report, output_path)
    print(f"wrote {output_path}")
    print(f"capability_visibility_status={report['capability_visibility_status']}")
    print(f"enabled_operational_capability_count={report['summary']['enabled_operational_capability_count']}")
    print(f"deterministic_report_hash={report['deterministic_report_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
